"""Journal comptable signé — FICHIER PROTÉGÉ.

Règle n°1 : à 0 € tu meurs.

Le journal est un fichier texte « append-only » (une ligne JSON par écriture).
Chaque ligne contient :
  - le hash SHA-256 de la ligne précédente (chaîne : on ne peut pas retirer ou
    modifier une ligne au milieu sans casser la chaîne) ;
  - une signature HMAC-SHA256 calculée avec LEDGER_KEY (on ne peut pas fabriquer
    une ligne valide sans la clé).

Le solde, les positions, les gains réalisés sont TOUJOURS recalculés depuis le
journal. Aucune autre source de vérité. Les gains latents ne sont jamais des fonds
disponibles : le solde disponible ne bouge qu'avec des flux réalisés (achat,
vente, règlement).

Faillite : dès que le solde disponible est <= 0, une écriture BANKRUPT signée est
ajoutée et un fichier verrou signé est écrit. Ensuite plus aucune opération n'est
acceptée. Seule une écriture RESET, qui exige le code RESET_CODE, peut repartir.

Toute anomalie (ligne illisible, chaîne cassée, signature invalide, incohérence
comptable) lève LedgerCorrupt. Jamais de réparation ni de réinitialisation
automatique.

Tous les montants sont des Decimal (calcul exact), sérialisés en texte.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import hmac
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

GENESIS_PREV = "0" * 64
MIN_KEY_BYTES = 32
MONEY_TYPES = ("BUY", "SELL", "SETTLE")
ENTRY_TYPES = ("GENESIS", "BUY", "SELL", "SETTLE", "HEARTBEAT", "BANKRUPT", "RESET",
               "MILESTONE", "PROMOTION", "ELIMINATION")
# Cliquet (décision d'Etienne, 15/10/2026) : l'objectif suivant vaut toujours 1,5 × le
# palier précédent (premier objectif : 1,5 × le capital initial). Il ne redescend jamais.
RATCHET = Decimal("1.5")
ZERO = Decimal("0")
ONE = Decimal("1")


class LedgerError(Exception):
    """Erreur de base du journal."""


class LedgerCorrupt(LedgerError):
    """Le journal ou le verrou est invalide : arrêt « CORROMPU »."""


class LedgerLocked(LedgerError):
    """Faillite : aucune opération n'est plus acceptée."""


class DuplicateOperation(LedgerError):
    """Cet identifiant d'opération a déjà été comptabilisé."""


class InsufficientFunds(LedgerError):
    """L'opération rendrait le solde disponible négatif."""


class InvalidEntry(LedgerError):
    """Écriture mal formée ou incohérente."""


class ResetRefused(LedgerError):
    """Réinitialisation refusée (code absent ou faux)."""


class NotInitialized(LedgerError):
    """Le journal n'existe pas : seule l'initialisation explicite peut le créer."""


# --------------------------------------------------------------------------- outils


def to_decimal(value: Any, name: str = "valeur") -> Decimal:
    """Convertit en Decimal fini. Refuse NaN, infini, booléens et types bizarres."""
    if isinstance(value, bool) or value is None:
        raise InvalidEntry(f"{name} invalide : {value!r}")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise InvalidEntry(f"{name} invalide : {value!r}") from exc
    if not result.is_finite():
        raise InvalidEntry(f"{name} non fini : {value!r}")
    return result


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_ts(ts: datetime) -> str:
    if ts.tzinfo is None:
        raise InvalidEntry("horodatage sans fuseau horaire")
    return ts.astimezone(timezone.utc).isoformat(timespec="microseconds")


def parse_ts(text: str) -> datetime:
    try:
        ts = datetime.fromisoformat(text)
    except (TypeError, ValueError) as exc:
        raise InvalidEntry(f"horodatage invalide : {text!r}") from exc
    if ts.tzinfo is None:
        raise InvalidEntry(f"horodatage sans fuseau : {text!r}")
    return ts.astimezone(timezone.utc)


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def entry_hash(seq: int, ts: str, entry_type: str, data: dict, prev: str) -> str:
    payload = canonical({"seq": seq, "ts": ts, "type": entry_type, "data": data, "prev": prev})
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sign(key: bytes, message: str) -> str:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).hexdigest()


def load_key_from_env(var: str = "LEDGER_KEY") -> bytes:
    """Lit la clé depuis l'environnement. Ne l'affiche jamais."""
    raw = os.environ.get(var, "")
    key = raw.encode("utf-8")
    if len(key) < MIN_KEY_BYTES:
        raise LedgerError(
            f"La variable d'environnement {var} est absente ou trop courte "
            f"(minimum {MIN_KEY_BYTES} caractères)."
        )
    return key


# --------------------------------------------------------------------------- état


@dataclass
class Position:
    token_id: str
    market_id: str
    event_id: str
    outcome: str
    shares: Decimal
    cost_basis: Decimal  # prix payé + frais, pour les parts encore détenues
    opened_at: str
    strategy_id: str
    strategy_version: str
    group: str = ""  # groupe de corrélation (ex. « crypto:btc »), par défaut l'événement

    @property
    def avg_cost(self) -> Decimal:
        return self.cost_basis / self.shares if self.shares > 0 else ZERO


@dataclass
class LedgerState:
    initialized: bool = False
    initial_capital: Decimal = ZERO
    cash: Decimal = ZERO  # solde disponible : uniquement des flux réalisés
    realized_pnl: Decimal = ZERO  # net de frais
    fees_paid: Decimal = ZERO
    positions: dict[str, Position] = field(default_factory=dict)
    op_ids: set[str] = field(default_factory=set)
    realized_by_day: dict[str, Decimal] = field(default_factory=dict)
    bankrupt: bool = False
    bankrupt_reason: str = ""
    epoch: int = 0  # nombre de réinitialisations
    epoch_started_at: datetime | None = None
    # Paliers atteints (capital RÉALISÉ = solde + coût des positions, hors gains latents).
    milestones: list[dict] = field(default_factory=list)
    next_target: Decimal = ZERO
    # Compétition : stratégie qui pilote le capital principal ("" = ne rien faire).
    champion: str = ""
    eliminated: set[str] = field(default_factory=set)
    last_elimination_at: datetime | None = None
    last_seq: int = -1
    last_hash: str = GENESIS_PREV
    last_ts: datetime | None = None
    last_heartbeat_at: datetime | None = None

    def clone(self) -> "LedgerState":
        """Copie indépendante, équivalente à copy.deepcopy mais bien plus rapide.

        Les Decimal, str et datetime sont immuables : seuls les conteneurs et les
        positions sont recopiés. Tout nouveau champ mutable doit être ajouté ici
        (test_ledger.py vérifie l'équivalence avec deepcopy).
        """
        new = copy.copy(self)
        new.positions = {k: dataclasses.replace(v) for k, v in self.positions.items()}
        new.op_ids = set(self.op_ids)
        new.realized_by_day = dict(self.realized_by_day)
        new.milestones = [dict(m) for m in self.milestones]
        new.eliminated = set(self.eliminated)
        return new

    def realized_capital(self) -> Decimal:
        """Capital réalisé : solde + coût des positions ouvertes (aucun gain latent)."""
        return self.cash + self.immobilized()

    # Capital immobilisé : coût d'acquisition des positions ouvertes.
    def immobilized(self) -> Decimal:
        return sum((p.cost_basis for p in self.positions.values()), ZERO)

    def position_value(self, marks: dict[str, Decimal] | None = None) -> Decimal:
        """Valeur estimée des positions. Sans prix de marque : coût d'acquisition."""
        marks = marks or {}
        total = ZERO
        for token_id, pos in self.positions.items():
            mark = marks.get(token_id)
            total += pos.shares * mark if mark is not None else pos.cost_basis
        return total

    def unrealized_pnl(self, marks: dict[str, Decimal] | None = None) -> Decimal:
        return self.position_value(marks) - self.immobilized()

    def total_estimated(self, marks: dict[str, Decimal] | None = None) -> Decimal:
        """Capital total ESTIMÉ (informatif). Jamais utilisé comme fonds disponibles."""
        return self.cash + self.position_value(marks)

    def realized_today(self, now: datetime) -> Decimal:
        return self.realized_by_day.get(now.astimezone(timezone.utc).date().isoformat(), ZERO)

    def summary(self, marks: dict[str, Decimal] | None = None) -> dict[str, str]:
        """Résumé lisible (arrondi à 4 décimales pour l'affichage uniquement)."""
        def fmt(value: Decimal) -> str:
            return str(value.quantize(Decimal("0.0001")))
        return {
            "solde_disponible": fmt(self.cash),
            "capital_immobilise": fmt(self.immobilized()),
            "gains_realises_nets": fmt(self.realized_pnl),
            "gains_latents": fmt(self.unrealized_pnl(marks)),
            "frais_payes": fmt(self.fees_paid),
            "capital_total_estime": fmt(self.total_estimated(marks)),
            "positions_ouvertes": str(len(self.positions)),
            "faillite": "oui" if self.bankrupt else "non",
        }


def _require(data: dict, keys: tuple[str, ...], entry_type: str) -> None:
    missing = [k for k in keys if k not in data]
    if missing:
        raise InvalidEntry(f"{entry_type} : champs manquants {missing}")


def _book_realized(state: LedgerState, ts: datetime, amount: Decimal) -> None:
    state.realized_pnl += amount
    day = ts.date().isoformat()
    state.realized_by_day[day] = state.realized_by_day.get(day, ZERO) + amount


def apply_entry(state: LedgerState, entry_type: str, data: dict, ts: datetime) -> None:
    """Applique une écriture à l'état. Lève InvalidEntry / LedgerLocked / ... si refusée.

    Fonction pure et déterministe : utilisée à l'identique pour vérifier une
    nouvelle écriture et pour rejouer le journal au chargement.
    """
    if entry_type not in ENTRY_TYPES:
        raise InvalidEntry(f"type d'écriture inconnu : {entry_type!r}")

    if entry_type == "GENESIS":
        if state.initialized:
            raise InvalidEntry("GENESIS en double")
        _require(data, ("initial_capital",), entry_type)
        capital = to_decimal(data["initial_capital"], "initial_capital")
        if capital <= 0:
            raise InvalidEntry("capital initial <= 0")
        state.initialized = True
        state.initial_capital = capital
        state.cash = capital
        state.epoch_started_at = ts
        state.next_target = capital * RATCHET
        return

    if not state.initialized:
        raise InvalidEntry("écriture avant GENESIS")

    if entry_type == "HEARTBEAT":
        state.last_heartbeat_at = ts
        return

    if entry_type == "BANKRUPT":
        if state.bankrupt:
            raise InvalidEntry("BANKRUPT en double")
        _require(data, ("reason",), entry_type)
        state.bankrupt = True
        state.bankrupt_reason = str(data["reason"])
        return

    if entry_type == "RESET":
        _require(data, ("reason", "initial_capital"), entry_type)
        capital = to_decimal(data["initial_capital"], "initial_capital")
        if capital <= 0:
            raise InvalidEntry("capital de réinitialisation <= 0")
        state.initial_capital = capital
        state.cash = capital
        state.realized_pnl = ZERO
        state.fees_paid = ZERO
        state.positions = {}
        state.realized_by_day = {}
        state.bankrupt = False
        state.bankrupt_reason = ""
        state.epoch += 1
        state.epoch_started_at = ts
        state.milestones = []
        state.next_target = capital * RATCHET
        return

    if entry_type == "MILESTONE":
        _require(data, ("target",), entry_type)
        target = to_decimal(data["target"], "target")
        if state.bankrupt:
            raise LedgerLocked("faillite : aucun palier possible")
        if target != state.next_target:
            raise InvalidEntry(f"palier {target} différent de l'objectif courant {state.next_target}")
        if state.realized_capital() < target:
            raise InvalidEntry(f"palier {target} non atteint (capital réalisé {state.realized_capital()})")
        started = state.milestones[-1]["reached_at"] if state.milestones else format_ts(state.epoch_started_at)
        state.milestones.append({"target": str(target), "reached_at": format_ts(ts),
                                 "seconds": int((ts - parse_ts(started)).total_seconds())})
        state.next_target = target * RATCHET
        return

    if entry_type == "PROMOTION":
        _require(data, ("champion", "reason"), entry_type)
        champion = str(data["champion"])
        if champion and champion in state.eliminated:
            raise InvalidEntry(f"stratégie éliminée : {champion}")
        state.champion = champion
        return

    if entry_type == "ELIMINATION":
        _require(data, ("strategy", "reason"), entry_type)
        strategy = str(data["strategy"])
        if not strategy or strategy == state.champion:
            raise InvalidEntry("on n'élimine pas le champion en titre")
        state.eliminated.add(strategy)
        state.last_elimination_at = ts
        return

    # ----- écritures monétaires
    if state.bankrupt:
        raise LedgerLocked(f"faillite : {state.bankrupt_reason}")
    _require(data, ("op_id", "token_id"), entry_type)
    op_id = str(data["op_id"])
    if not op_id:
        raise InvalidEntry("op_id vide")
    if op_id in state.op_ids:
        raise DuplicateOperation(f"opération déjà comptabilisée : {op_id}")
    token_id = str(data["token_id"])

    if entry_type == "BUY":
        _require(data, ("market_id", "event_id", "outcome", "shares", "price", "fee",
                        "strategy_id", "strategy_version"), entry_type)
        shares = to_decimal(data["shares"], "shares")
        price = to_decimal(data["price"], "price")
        fee = to_decimal(data["fee"], "fee")
        if shares <= 0:
            raise InvalidEntry("BUY : nombre de parts <= 0")
        if not (ZERO < price < ONE):
            raise InvalidEntry("BUY : prix hors de ]0, 1[")
        if fee < 0:
            raise InvalidEntry("BUY : frais négatifs")
        outlay = shares * price + fee
        if outlay > state.cash:
            raise InsufficientFunds(f"BUY : coût {outlay} > solde disponible {state.cash}")
        state.cash -= outlay
        state.fees_paid += fee
        pos = state.positions.get(token_id)
        if pos is None:
            state.positions[token_id] = Position(
                token_id=token_id,
                market_id=str(data["market_id"]),
                event_id=str(data["event_id"]),
                outcome=str(data["outcome"]),
                shares=shares,
                cost_basis=outlay,
                opened_at=format_ts(ts),
                strategy_id=str(data["strategy_id"]),
                strategy_version=str(data["strategy_version"]),
                group=str(data.get("group") or data["event_id"]),
            )
        else:
            pos.shares += shares
            pos.cost_basis += outlay
        state.op_ids.add(op_id)
        return

    if entry_type == "SELL":
        _require(data, ("shares", "price", "fee"), entry_type)
        pos = state.positions.get(token_id)
        if pos is None:
            raise InvalidEntry("SELL : aucune position sur ce jeton")
        shares = to_decimal(data["shares"], "shares")
        price = to_decimal(data["price"], "price")
        fee = to_decimal(data["fee"], "fee")
        if shares <= 0 or shares > pos.shares:
            raise InvalidEntry("SELL : nombre de parts invalide")
        if not (ZERO < price < ONE):
            raise InvalidEntry("SELL : prix hors de ]0, 1[")
        if fee < 0:
            raise InvalidEntry("SELL : frais négatifs")
        proceeds = shares * price - fee
        if state.cash + proceeds < 0:
            raise InsufficientFunds("SELL : les frais dépassent le solde")
        cost_part = pos.cost_basis * shares / pos.shares
        state.cash += proceeds
        state.fees_paid += fee
        _book_realized(state, ts, proceeds - cost_part)
        pos.shares -= shares
        pos.cost_basis -= cost_part
        if pos.shares == 0:
            del state.positions[token_id]
        state.op_ids.add(op_id)
        return

    if entry_type == "SETTLE":
        _require(data, ("payout_per_share", "resolution"), entry_type)
        pos = state.positions.get(token_id)
        if pos is None:
            raise InvalidEntry("SETTLE : aucune position sur ce jeton")
        payout = to_decimal(data["payout_per_share"], "payout_per_share")
        if not (ZERO <= payout <= ONE):
            raise InvalidEntry("SETTLE : paiement par part hors de [0, 1]")
        amount = pos.shares * payout
        state.cash += amount
        _book_realized(state, ts, amount - pos.cost_basis)
        del state.positions[token_id]
        state.op_ids.add(op_id)
        return


# --------------------------------------------------------------------------- journal


class Ledger:
    """Accès au journal. Toujours ouvrir via Ledger.open() (vérification complète)."""

    def __init__(self, path: Path, key: bytes, lock_path: Path):
        if len(key) < MIN_KEY_BYTES:
            raise LedgerError(f"clé trop courte (minimum {MIN_KEY_BYTES} octets)")
        self.path = Path(path)
        self.lock_path = Path(lock_path)
        self._key = key
        self.state = LedgerState()
        self.hashes: list[str] = []  # hash de chaque écriture, par numéro de séquence

    def __repr__(self) -> str:  # ne jamais exposer la clé
        return f"Ledger(path={str(self.path)!r})"

    # ---------------------------------------------------------------- ouverture

    @classmethod
    def open(cls, path: Path, key: bytes, lock_path: Path) -> "Ledger":
        """Ouvre et vérifie un journal EXISTANT. Ne crée jamais de capital."""
        ledger = cls(path, key, lock_path)
        if not ledger.path.exists():
            raise NotInitialized(
                f"journal absent ({ledger.path}). Seul scripts/initialize.py peut le créer."
            )
        ledger._replay()
        ledger._check_lock_file()
        return ledger

    @classmethod
    def create(cls, path: Path, key: bytes, lock_path: Path, initial_capital: Any,
               now: datetime | None = None) -> "Ledger":
        """Crée un nouveau journal (GENESIS). Refuse s'il existe déjà un journal ou un verrou."""
        ledger = cls(path, key, lock_path)
        if ledger.path.exists():
            raise LedgerError(f"un journal existe déjà : {ledger.path}")
        if ledger.lock_path.exists():
            raise LedgerLocked("un verrou de faillite existe : réinitialisation manuelle requise")
        ledger.path.parent.mkdir(parents=True, exist_ok=True)
        ledger._append("GENESIS", {"initial_capital": str(to_decimal(initial_capital))}, now)
        return ledger

    def _replay(self) -> None:
        state = LedgerState()
        hashes: list[str] = []
        prev = GENESIS_PREV
        with self.path.open("r", encoding="utf-8") as handle:
            lines = handle.read().split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        if not lines:
            raise LedgerCorrupt("journal vide")
        for number, line in enumerate(lines, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LedgerCorrupt(f"ligne {number} illisible") from exc
            if not isinstance(record, dict) or set(record) != {"seq", "ts", "type", "data", "prev", "hash", "sig"}:
                raise LedgerCorrupt(f"ligne {number} : structure invalide")
            seq, ts_text, etype, data = record["seq"], record["ts"], record["type"], record["data"]
            if seq != number - 1 or not isinstance(data, dict):
                raise LedgerCorrupt(f"ligne {number} : numéro de séquence invalide")
            if record["prev"] != prev:
                raise LedgerCorrupt(f"ligne {number} : chaîne de hash cassée")
            expected_hash = entry_hash(seq, ts_text, etype, data, prev)
            if not hmac.compare_digest(str(record["hash"]), expected_hash):
                raise LedgerCorrupt(f"ligne {number} : hash invalide")
            if not hmac.compare_digest(str(record["sig"]), sign(self._key, expected_hash)):
                raise LedgerCorrupt(f"ligne {number} : signature invalide")
            if number == 1 and etype != "GENESIS":
                raise LedgerCorrupt("la première écriture n'est pas GENESIS")
            try:
                ts = parse_ts(ts_text)
                if state.last_ts is not None and ts < state.last_ts:
                    raise InvalidEntry("horodatage antérieur à l'écriture précédente")
                apply_entry(state, etype, data, ts)
            except LedgerError as exc:
                raise LedgerCorrupt(f"ligne {number} : {exc}") from exc
            state.last_seq, state.last_hash, state.last_ts = seq, expected_hash, ts
            hashes.append(expected_hash)
            prev = expected_hash
        # Deuxième niveau : même sans écriture BANKRUPT, un solde <= 0 est une faillite.
        if not state.bankrupt and state.cash <= 0:
            state.bankrupt = True
            state.bankrupt_reason = f"solde disponible {state.cash} <= 0 détecté au rechargement"
        self.state = state
        self.hashes = hashes

    def hash_at(self, seq: int) -> str | None:
        return self.hashes[seq] if 0 <= seq < len(self.hashes) else None

    def _check_lock_file(self) -> None:
        if not self.lock_path.exists():
            if self.state.bankrupt:
                # Faillite dans le journal mais verrou absent : on le réécrit.
                self._write_lock_file(self.state.bankrupt_reason)
            return
        try:
            lock = json.loads(self.lock_path.read_text(encoding="utf-8"))
            body = {k: lock[k] for k in ("reason", "seq", "ledger_hash", "written_at")}
            valid = hmac.compare_digest(str(lock["sig"]), sign(self._key, canonical(body)))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise LedgerCorrupt("verrou de faillite illisible") from exc
        if not valid:
            raise LedgerCorrupt("verrou de faillite : signature invalide")
        if isinstance(body["seq"], int) and body["seq"] > self.state.last_seq:
            raise LedgerCorrupt("verrou postérieur à la fin du journal : journal tronqué")
        # Un verrou valide impose la faillite, même si le journal ne la contient pas.
        if not self.state.bankrupt:
            self.state.bankrupt = True
            self.state.bankrupt_reason = f"verrou de faillite présent : {body['reason']}"

    def _write_lock_file(self, reason: str) -> None:
        body = {
            "reason": reason,
            "seq": self.state.last_seq,
            "ledger_hash": self.state.last_hash,
            "written_at": format_ts(utc_now()),
        }
        content = dict(body, sig=sign(self._key, canonical(body)))
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.lock_path.with_suffix(".tmp")
        tmp.write_text(canonical(content) + "\n", encoding="utf-8")
        os.replace(tmp, self.lock_path)

    # ---------------------------------------------------------------- écriture

    def _append(self, entry_type: str, data: dict, now: datetime | None = None) -> dict:
        ts = (now or utc_now()).astimezone(timezone.utc)
        if self.state.last_ts is not None and ts < self.state.last_ts:
            ts = self.state.last_ts  # jamais d'horodatage qui recule
        ts_text = format_ts(ts)
        # Vérification sur une copie : si l'écriture est refusée, rien n'est modifié.
        trial = self.state.clone()
        apply_entry(trial, entry_type, data, ts)
        seq = self.state.last_seq + 1
        digest = entry_hash(seq, ts_text, entry_type, data, self.state.last_hash)
        record = {"seq": seq, "ts": ts_text, "type": entry_type, "data": data,
                  "prev": self.state.last_hash, "hash": digest, "sig": sign(self._key, digest)}
        line = canonical(record) + "\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        trial.last_seq, trial.last_hash, trial.last_ts = seq, digest, ts
        self.state = trial
        self.hashes.append(digest)
        return record

    def _after_money_entry(self, now: datetime | None) -> None:
        """Vérification APRÈS chaque opération comptabilisée."""
        if not self.state.bankrupt and self.state.cash <= 0:
            self.declare_bankruptcy(
                f"solde disponible {self.state.cash} <= 0 après l'opération n°{self.state.last_seq}", now
            )

    def _guard_money(self) -> None:
        """Vérification AVANT chaque opération."""
        if self.state.bankrupt:
            raise LedgerLocked(f"faillite : {self.state.bankrupt_reason}")
        if self.state.cash <= 0:
            self.declare_bankruptcy(f"solde disponible {self.state.cash} <= 0 avant opération")
            raise LedgerLocked(f"faillite : {self.state.bankrupt_reason}")

    def record_buy(self, *, op_id: str, token_id: str, market_id: str, event_id: str,
                   outcome: str, shares: Any, price: Any, fee: Any, strategy_id: str,
                   strategy_version: str, now: datetime | None = None,
                   extra: dict | None = None, group: str | None = None) -> dict:
        self._guard_money()
        data = {"op_id": op_id, "token_id": token_id, "market_id": market_id,
                "event_id": event_id, "outcome": outcome, "shares": str(to_decimal(shares)),
                "price": str(to_decimal(price)), "fee": str(to_decimal(fee)),
                "strategy_id": strategy_id, "strategy_version": strategy_version}
        if group:
            data["group"] = group
        if extra:
            data["extra"] = extra
        record = self._append("BUY", data, now)
        self._after_money_entry(now)
        return record

    def record_sell(self, *, op_id: str, token_id: str, shares: Any, price: Any, fee: Any,
                    now: datetime | None = None, extra: dict | None = None) -> dict:
        self._guard_money()
        data = {"op_id": op_id, "token_id": token_id, "shares": str(to_decimal(shares)),
                "price": str(to_decimal(price)), "fee": str(to_decimal(fee))}
        if extra:
            data["extra"] = extra
        record = self._append("SELL", data, now)
        self._after_money_entry(now)
        return record

    def record_settlement(self, *, op_id: str, token_id: str, payout_per_share: Any,
                          resolution: str, now: datetime | None = None) -> dict:
        self._guard_money()
        data = {"op_id": op_id, "token_id": token_id,
                "payout_per_share": str(to_decimal(payout_per_share)), "resolution": resolution}
        record = self._append("SETTLE", data, now)
        self._after_money_entry(now)
        return record

    def record_milestones(self, now: datetime | None = None) -> list[dict]:
        """Inscrit chaque palier franchi par le capital réalisé (plusieurs d'un coup si besoin)."""
        reached = []
        while (not self.state.bankrupt and self.state.next_target > 0
               and self.state.realized_capital() >= self.state.next_target):
            self._append("MILESTONE", {"target": str(self.state.next_target),
                                       "capital": str(self.state.realized_capital())}, now)
            reached.append(dict(self.state.milestones[-1]))
        return reached

    def record_promotion(self, champion: str, reason: str, metrics: dict | None = None,
                         now: datetime | None = None) -> dict:
        return self._append("PROMOTION", {"champion": champion, "reason": reason,
                                          "metrics": metrics or {}}, now)

    def record_elimination(self, strategy: str, reason: str, metrics: dict | None = None,
                           now: datetime | None = None) -> dict:
        return self._append("ELIMINATION", {"strategy": strategy, "reason": reason,
                                            "metrics": metrics or {}}, now)

    def heartbeat(self, cycle_id: str, status: str, now: datetime | None = None,
                  total_estimated: Any = None) -> dict:
        """Battement de cœur signé. Le capital total estimé est informatif (courbe, drawdown)."""
        data = {"cycle_id": cycle_id, "status": status, "cash": str(self.state.cash)}
        if total_estimated is not None:
            data["total_estimated"] = str(to_decimal(total_estimated))
        return self._append("HEARTBEAT", data, now)

    def declare_bankruptcy(self, reason: str, now: datetime | None = None) -> None:
        if not self.state.bankrupt:
            self._append("BANKRUPT", {"reason": reason, "cash": str(self.state.cash)}, now)
        self._write_lock_file(self.state.bankrupt_reason)

    def reset(self, *, provided_code: str, expected_code: str, reason: str,
              initial_capital: Any, now: datetime | None = None) -> dict:
        """Réinitialisation manuelle. Exige le code RESET_CODE (comparaison à temps constant)."""
        if not expected_code or len(expected_code) < 8:
            raise ResetRefused("RESET_CODE non configuré")
        if not hmac.compare_digest(provided_code.encode("utf-8"), expected_code.encode("utf-8")):
            raise ResetRefused("code de réinitialisation incorrect")
        if not reason.strip():
            raise ResetRefused("une raison écrite est obligatoire")
        record = self._append("RESET", {"reason": reason,
                                        "initial_capital": str(to_decimal(initial_capital))}, now)
        if self.lock_path.exists():
            self.lock_path.unlink()
        return record
