"""
Localisation helper for OurWay bot.

Usage:
    from locales import t
    text = t("auth.welcome_back", locale, name="Anton")
"""
from locales.en import STRINGS as _EN
from locales.uk import STRINGS as _UK

_LOCALES: dict[str, dict[str, str]] = {"en": _EN, "uk": _UK}


def t(key: str, locale: str = "en", **kwargs: str) -> str:
    """Return localised string for *key*, formatted with *kwargs*.

    Falls back to English if key is missing in the requested locale.
    Falls back to the raw key string if missing in English too.
    """
    strings = _LOCALES.get(locale, _EN)
    template: str = strings.get(key) or _EN.get(key) or key
    if kwargs:
        return template.format(**kwargs)
    return template
