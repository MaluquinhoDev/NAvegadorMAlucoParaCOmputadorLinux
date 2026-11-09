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
HIGH_PRESSURE_SUSPEND_AFTER_SECONDS = 120
CRITICAL_PRESSURE_SUSPEND_AFTER_SECONDS = 90


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



def memory_pressure_level(meminfo_text: str, psi_text: str) -> str:
    """Classifica pressão de memória com MemAvailable + PSI; falha fechada em normal."""
    available_kb = None
    some_avg10 = 0.0
    full_avg10 = 0.0
    try:
        for line in (meminfo_text or "").splitlines():
            if line.startswith("MemAvailable:"):
                available_kb = int(line.split()[1])
                break
        for line in (psi_text or "").splitlines():
            fields = line.split()
            if not fields:
                continue
            values = {item.split("=", 1)[0]: item.split("=", 1)[1]
                      for item in fields[1:] if "=" in item}
            if fields[0] == "some":
                some_avg10 = float(values.get("avg10", 0))
            elif fields[0] == "full":
                full_avg10 = float(values.get("avg10", 0))
    except (ValueError, IndexError, TypeError):
        return "normal"

    if available_kb is None:
        return "normal"
    if available_kb < 384 * 1024 and full_avg10 >= 1.0:
        return "critical"
    if available_kb < 512 * 1024 and some_avg10 >= 2.0:
        return "high"
    return "normal"


def can_create_tab(count: int) -> bool:
    return count < MAX_TABS


def is_youtube_shorts(url: str) -> bool:
    parsed = urlparse(url or "")
    return parsed.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"} and parsed.path.startswith("/shorts/")
