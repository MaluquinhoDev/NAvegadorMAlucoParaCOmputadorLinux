"""Lógica independente da interface do Navegador Maluco."""
from urllib.parse import quote_plus, urlparse

HOME_URL = "https://www.wikipedia.org"
SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com/?q={query}",
    "Startpage": "https://www.startpage.com/sp/search?query={query}",
    "Google": "https://www.google.com/search?q={query}",
}
MAX_TABS = 12
MAX_RESIDENT_TABS = 3
SUSPEND_AFTER_SECONDS = 180


def search_url(value: str, search_engine: str = "DuckDuckGo") -> str:
    """Monta uma URL de pesquisa usando um mecanismo conhecido."""
    template = SEARCH_ENGINES.get(search_engine, SEARCH_ENGINES["DuckDuckGo"])
    return template.format(query=quote_plus((value or "").strip()))


def normalize_input(value: str, search_engine: str = "DuckDuckGo") -> str:
    """Converte texto da barra em URL HTTP(S) ou pesquisa no mecanismo escolhido."""
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
    return search_url(value, search_engine)


def can_create_tab(count: int) -> bool:
    return count < MAX_TABS


def is_youtube_shorts(url: str) -> bool:
    parsed = urlparse(url or "")
    return parsed.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"} and parsed.path.startswith("/shorts/")
