"""Input safety helpers for public MicroBiz agent conversations.

The Coordinator must never accept shop credentials through ASI:One chat. This
best-effort detector blocks common credential formats, but is not a substitute
for a secure OAuth connection flow: users should never paste secrets in chat.
"""

import re

_SECRET_PATTERNS = (
    # Shopify custom app/Admin API tokens and common platform tokens.
    re.compile(r"\bshpat_[A-Za-z0-9_-]{12,}", re.IGNORECASE),
    re.compile(r"\bshpca_[A-Za-z0-9_-]{12,}", re.IGNORECASE),
    re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{12,}", re.IGNORECASE),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # Bearer/JWT credentials.
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    # Explicit key/token/password assignments with a non-placeholder value.
    re.compile(
        r"\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|password)"
        r"\s*[:=]\s*['\"]?([A-Za-z0-9_./+-]{16,})",
        re.IGNORECASE,
    ),
)


def contains_credential(text: str) -> bool:
    """Return whether text appears to contain a credential; never return the match."""
    for pattern in _SECRET_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        if match.lastindex:
            value = match.group(1).strip().upper()
            if value in {"YOUR_API_KEY_HERE", "REPLACE_ME", "CHANGEME", "PLACEHOLDER"}:
                continue
        return True
    return False


def requests_live_store_connection(text: str) -> bool:
    """Detect requests that should get the honest, secure-connector explanation."""
    normalized = text.casefold()
    return any(
        phrase in normalized
        for phrase in (
            "shopify",
            "connect my store",
            "connect store",
            "api key",
            "access token",
        )
    )
