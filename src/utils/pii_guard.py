"""
Personal-data gate for WF1.

Detects French social security numbers (NIR), IBANs, payslip/tax vocabulary
and card numbers so a card carrying real PII is never written to the
(public) repo. `detect_pii` returns reason CODES only — callers must never
log or notify with the matched text itself, only the codes it returns.
"""
import re
import unicodedata

_NIR_RE = re.compile(
    r"\b([1234789])[ .]?(\d{2})[ .]?(\d{2})[ .]?(\d{2}|2[AaBb])[ .]?(\d{3})[ .]?(\d{3})[ .]?(\d{2})\b"
)
_CORSICA_DEPT = {"2A": "19", "2B": "18"}

_IBAN_RE = re.compile(r"\b([A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}[ ]?[A-Z0-9]{1,4})\b", re.IGNORECASE)

_CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?<!\D)")

# Knowledge cards embed fenced/inline code (hex addresses, array dumps,
# long float literals) that trips the card-number heuristic on digit count
# alone; code content can't carry a real card number worth flagging.
_CODE_SPAN_RE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)

# Academic references link ScienceDirect articles by their Elsevier "PII"
# (Publisher Item Identifier, unrelated to personal data) — a 17-char code
# that satisfies Luhn about 1 in 10 times; GitHub camo proxy URLs also embed
# long hex digit runs. URLs can't carry a card number worth flagging either.
_URL_RE = re.compile(r"https?://\S+")

_HR_FISCAL_KEYWORDS = [
    "bulletin de paie",
    "bulletin de salaire",
    "payslip",
    "salaire net",
    "net a payer",
    "avis d imposition",
]


def _fold(text: str) -> str:
    """Lowercase, strip accents and apostrophes so keyword matching ignores
    'à' vs 'a' and "d'imposition" vs "d imposition"."""
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"['’]", " ", stripped).lower()


def _nir_valid(match: re.Match) -> bool:
    sex, year, month, dept, commune, order, key = match.groups()
    dept = _CORSICA_DEPT.get(dept.upper(), dept)
    digits13 = sex + year + month + dept + commune + order
    expected_key = 97 - (int(digits13) % 97)
    return int(key) == expected_key


def _has_nir(text: str) -> bool:
    return any(_nir_valid(m) for m in _NIR_RE.finditer(text))


def _iban_valid(candidate: str) -> bool:
    iban = candidate.replace(" ", "").upper()
    if not (15 <= len(iban) <= 34):
        return False
    rearranged = iban[4:] + iban[:4]
    try:
        converted = "".join(str(int(c, 36)) for c in rearranged)
    except ValueError:
        return False
    return int(converted) % 97 == 1


def _has_iban(text: str) -> bool:
    return any(_iban_valid(m.group(0)) for m in _IBAN_RE.finditer(text))


def _luhn_valid(candidate: str) -> bool:
    digits = [int(d) for d in candidate if d.isdigit()]
    if not (13 <= len(digits) <= 19):
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _has_card_number(text: str) -> bool:
    clean = _URL_RE.sub(" ", _CODE_SPAN_RE.sub(" ", text))
    return any(_luhn_valid(m.group(0)) for m in _CARD_RE.finditer(clean))


def _has_hr_fiscal_keyword(text: str) -> bool:
    folded = _fold(text)
    return any(kw in folded for kw in _HR_FISCAL_KEYWORDS)


def detect_pii(text: str | None) -> list[str]:
    """
    Scan `text` for personal data. Returns a list of reason codes
    (a subset of "nir", "iban", "credit_card", "hr_fiscal_keyword"),
    empty if nothing was found. Never returns or logs the matched text.
    """
    if not text or not text.strip():
        return []
    reasons = []
    if _has_nir(text):
        reasons.append("nir")
    if _has_iban(text):
        reasons.append("iban")
    if _has_card_number(text):
        reasons.append("credit_card")
    if _has_hr_fiscal_keyword(text):
        reasons.append("hr_fiscal_keyword")
    return reasons
