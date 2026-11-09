"""Lógica independente da interface do Navegador Maluco."""
from urllib.parse import quote_plus, urlparse

HOME_URL = "https://www.wikipedia.org"
MAX_TABS = 30
MAX_RESIDENT_TABS = 6


def normalize_input(value: str) -> str:
    """Converte texto da barra em URL HTTP(S) ou pesquisa DuckDuckGo."""
    value = (value or "").strip()
    if not value:
        return HOME_URL
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        raise ValueError("Somente endereços HTTP e HTTPS são aceitos.")
    if " " not in value and "." in value:
        candidate = "https://" + value
        parsed = urlparse(candidate)
        if parsed.netloc and "." in parsed.netloc:
            return candidate
    return "https://duckduckgo.com/?q=" + quote_plus(value)


def can_create_tab(count: int) -> bool:
    return count < MAX_TABS


def is_youtube_shorts(url: str) -> bool:
    parsed = urlparse(url or "")
    return parsed.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"} and parsed.path.startswith("/shorts/")
