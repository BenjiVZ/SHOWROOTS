"""
Anti-desintermediación scanner.

Detecta intentos de compartir contactos directos (teléfono, email, redes,
WhatsApp, etc.) en textos generados por usuarios. Se usa en:
  - Mensajes del chat in-app
  - Descripción / notas de bookings
  - Bio / descripciones de talentos (opcional)

Devuelve una tupla (clean_text, matches) donde matches es la lista de patrones
detectados. Para frontend, los mismos patrones se replican como regex JS en
`frontend/src/utils/antiDisinter.js`.
"""
import re

# Patrones — separados por categoría para poder mostrar warning específico
PATTERNS = {
    'phone': re.compile(
        r'(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}'
    ),
    'email': re.compile(
        r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}'
    ),
    'username_at': re.compile(r'@[A-Za-z0-9_.]{3,}'),
    'whatsapp': re.compile(r'\b(?:whats?app|wsp|wpp|wa\.me)\b', re.IGNORECASE),
    'call_me': re.compile(
        r'\b(?:ll[aá]mame|c[oó]ntactame|escr[ií]beme|tel(?:[eé]fono)?|movil|celular|m[oó]vil)\b',
        re.IGNORECASE
    ),
    'social': re.compile(
        r'\b(?:instagram|insta|facebook|fb|tiktok|telegram|signal|twitter|x\.com)\b',
        re.IGNORECASE
    ),
    'url': re.compile(
        r'(?:https?://|www\.)\S+',
        re.IGNORECASE
    ),
}

MASK = '***'


def scan(text):
    """
    Run all patterns over `text`. Returns list of (category, match_string) tuples.
    """
    if not text:
        return []
    findings = []
    for category, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            findings.append((category, m.group(0)))
    return findings


def sanitize(text):
    """
    Replace every detected pattern with MASK. Returns (clean_text, findings).
    """
    if not text:
        return text, []
    findings = scan(text)
    clean = text
    for category, pattern in PATTERNS.items():
        clean = pattern.sub(MASK, clean)
    return clean, findings


def has_violations(text):
    """Quick boolean check — useful for form validators."""
    return len(scan(text)) > 0
