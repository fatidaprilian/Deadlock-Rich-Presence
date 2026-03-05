"""
Fetches hero data from assets.deadlock-api.com and caches it locally.

The API returns hero objects with:
  - class_name: e.g. "hero_inferno"  (strip "hero_" prefix -> codename key)
  - name:       e.g. "Infernus"      (display name for Discord)
  - hideout_rich_presence: e.g. "Mixing Drinks in the Hideout"

Cache is stored in <exe_dir>/cache/heroes.json and refreshed every 24 h.
Falls back to an embedded minimal dataset when the API is unreachable.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)

# ── types ──────────────────────────────────────────────────────────────────────

class HeroInfo(TypedDict):
    name: str
    hideout_text: str   # maps to API field "hideout_rich_presence"
    asset_key: str      # Discord named-asset key, e.g. "hero_inferno"
    icon_image: str     # External URL to the hero's small icon
    card_image: str     # External URL to the hero's portrait card


# ── embedded fallback (keeps the app working when offline) ─────────────────────
# Only the playable + common heroes are listed here;
# the full list is fetched from the API at runtime.

_FALLBACK: dict[str, HeroInfo] = {
    "inferno":    {"name": "Infernus",   "hideout_text": "In the Hideout", "asset_key": "hero_inferno", "icon_image": "", "card_image": ""},
    "gigawatt":   {"name": "Seven",      "hideout_text": "In the Hideout", "asset_key": "hero_gigawatt", "icon_image": "", "card_image": ""},
    "hornet":     {"name": "Vindicta",   "hideout_text": "In the Hideout", "asset_key": "hero_hornet", "icon_image": "", "card_image": ""},
    "ghost":      {"name": "Lady Geist", "hideout_text": "In the Hideout", "asset_key": "hero_ghost", "icon_image": "", "card_image": ""},
    "atlas":      {"name": "Abrams",     "hideout_text": "In the Hideout", "asset_key": "hero_atlas", "icon_image": "", "card_image": ""},
    "wraith":     {"name": "Wraith",     "hideout_text": "In the Hideout", "asset_key": "hero_wraith", "icon_image": "", "card_image": ""},
    "forge":      {"name": "McGinnis",   "hideout_text": "In the Hideout", "asset_key": "hero_forge", "icon_image": "", "card_image": ""},
    "dynamo":     {"name": "Dynamo",     "hideout_text": "In the Hideout", "asset_key": "hero_dynamo", "icon_image": "", "card_image": ""},
    "haze":       {"name": "Haze",       "hideout_text": "In the Hideout", "asset_key": "hero_haze", "icon_image": "", "card_image": ""},
    "kelvin":     {"name": "Kelvin",     "hideout_text": "In the Hideout", "asset_key": "hero_kelvin", "icon_image": "", "card_image": ""},
    "lash":       {"name": "Lash",       "hideout_text": "In the Hideout", "asset_key": "hero_lash", "icon_image": "", "card_image": ""},
    "pocket":     {"name": "Pocket",     "hideout_text": "In the Hideout", "asset_key": "hero_pocket", "icon_image": "", "card_image": ""},
    "bebop":      {"name": "Bebop",      "hideout_text": "In the Hideout", "asset_key": "hero_bebop", "icon_image": "", "card_image": ""},
    "shiv":       {"name": "Shiv",       "hideout_text": "In the Hideout", "asset_key": "hero_shiv", "icon_image": "", "card_image": ""},
    "viscous":    {"name": "Viscous",    "hideout_text": "In the Hideout", "asset_key": "hero_viscous", "icon_image": "", "card_image": ""},
    "warden":     {"name": "Warden",     "hideout_text": "In the Hideout", "asset_key": "hero_warden", "icon_image": "", "card_image": ""},
    "yamato":     {"name": "Yamato",     "hideout_text": "In the Hideout", "asset_key": "hero_yamato", "icon_image": "", "card_image": ""},
    "tengu":      {"name": "Ivy",        "hideout_text": "In the Hideout", "asset_key": "hero_tengu", "icon_image": "", "card_image": ""},
    "orion":      {"name": "Grey Talon", "hideout_text": "In the Hideout", "asset_key": "hero_orion", "icon_image": "", "card_image": ""},
    "krill":      {"name": "Mo & Krill", "hideout_text": "In the Hideout", "asset_key": "hero_krill", "icon_image": "", "card_image": ""},
    "synth":      {"name": "Pocket",     "hideout_text": "In the Hideout", "asset_key": "hero_synth", "icon_image": "", "card_image": ""},
    "chrono":     {"name": "Paradox",    "hideout_text": "In the Hideout", "asset_key": "hero_chrono", "icon_image": "", "card_image": ""},
    "astro":      {"name": "Holliday",   "hideout_text": "In the Hideout", "asset_key": "hero_astro", "icon_image": "", "card_image": ""},
    "cadence":    {"name": "Calico",     "hideout_text": "In the Hideout", "asset_key": "hero_cadence", "icon_image": "", "card_image": ""},
    "werewolf":   {"name": "Silver",     "hideout_text": "In the Hideout", "asset_key": "hero_werewolf", "icon_image": "", "card_image": ""},
    "magician":   {"name": "Sinclair",   "hideout_text": "In the Hideout", "asset_key": "hero_magician", "icon_image": "", "card_image": ""},
    "archer":     {"name": "Grey Talon", "hideout_text": "In the Hideout", "asset_key": "hero_orion", "icon_image": "", "card_image": ""},
    "abrams":     {"name": "Abrams",     "hideout_text": "In the Hideout", "asset_key": "hero_atlas", "icon_image": "", "card_image": ""},
    "digger":     {"name": "Mo & Krill", "hideout_text": "In the Hideout", "asset_key": "hero_krill", "icon_image": "", "card_image": ""},
    "ivy":        {"name": "Ivy",        "hideout_text": "In the Hideout", "asset_key": "hero_tengu", "icon_image": "", "card_image": ""},
}

# ── asset key overrides (old internal name -> correct Discord asset) ───────────
# These handle heroes whose internal codename differs from the Discord asset name.
_ASSET_OVERRIDES: dict[str, str] = {
    "abrams":  "hero_atlas",
    "archer":  "hero_orion",
    "digger":  "hero_krill",
    "ivy":     "hero_tengu",
    "pocket":  "hero_synth",
}

_CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours
_API_URL = "https://assets.deadlock-api.com/v2/heroes?language=english"
_TIMEOUT_SECONDS = 8


class HeroDataStore:
    """
    Thread-safe singleton that provides hero metadata.
    Load once at startup; data is read-only thereafter.
    """

    _instance: "HeroDataStore | None" = None
    _data: dict[str, HeroInfo] = {}

    def __init__(self, cache_dir: Path) -> None:
        self._cache_path = cache_dir / "heroes.json"
        self._data = dict(_FALLBACK)  # always start with fallback

    # ── public API ─────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Fetch from API or load from cache. Silently falls back if unavailable."""
        if self._try_load_cache():
            return
        self._fetch_from_api()

    def get(self, codename: str) -> HeroInfo | None:
        """Return HeroInfo for a codename (e.g. "inferno"), or None if unknown."""
        return self._data.get(codename.lower())

    def display_name(self, codename: str) -> str:
        """Return display name, falling back to a title-cased version of the key."""
        info = self.get(codename)
        if info:
            return info["name"]
        return codename.replace("_", " ").title()

    def hideout_text(self, codename: str) -> str:
        """Return the hideout presence text (e.g. "Mixing Drinks in the Hideout")."""
        info = self.get(codename)
        if info and info.get("hideout_text") and info["hideout_text"] != "In the Hideout":
            return info["hideout_text"]
        return "In the Hideout"

    def asset_key(self, codename: str) -> str:
        """Return Discord named-asset key for the hero, e.g. "hero_inferno"."""
        # Check explicit overrides first
        if codename in _ASSET_OVERRIDES:
            return _ASSET_OVERRIDES[codename]
        info = self.get(codename)
        if info:
            return info["asset_key"]
        return f"hero_{codename}"

    def icon_url(self, codename: str) -> str | None:
        """Return the URL for the hero's small icon or None if unavailable/offline."""
        info = self.get(codename)
        if info and info.get("icon_image"):
            return info["icon_image"]
        return None

    def card_url(self, codename: str) -> str | None:
        """Return the URL for the hero's large portrait card or None if unavailable/offline."""
        info = self.get(codename)
        if info and info.get("card_image"):
            return info["card_image"]
        return None

    # ── private ────────────────────────────────────────────────────────────────

    def _try_load_cache(self) -> bool:
        """Return True if cache exists and is fresh."""
        if not self._cache_path.exists():
            return False
        try:
            stat = self._cache_path.stat()
            age = time.time() - stat.st_mtime
            if age > _CACHE_TTL_SECONDS:
                logger.debug("Hero cache is stale (%.0f h old), refreshing.", age / 3600)
                return False
            with open(self._cache_path, encoding="utf-8") as f:
                cached = json.load(f)
            if not isinstance(cached, dict) or not cached:
                return False
            self._data = {**_FALLBACK, **cached}
            logger.info("Loaded hero data from cache (%d heroes).", len(self._data))
            return True
        except Exception as e:
            logger.warning("Failed to read hero cache: %s", e)
            return False

    def _fetch_from_api(self) -> None:
        """Fetch hero list from API and merge into _data. Save to cache on success."""
        try:
            import requests  # lazy import so startup isn't slowed when offline
            logger.info("Fetching hero data from API...")
            resp = requests.get(_API_URL, timeout=_TIMEOUT_SECONDS)
            resp.raise_for_status()
            heroes: list[dict] = resp.json()
        except Exception as e:
            logger.warning("Hero API unavailable, using fallback data: %s", e)
            return

        parsed: dict[str, HeroInfo] = {}
        for hero in heroes:
            class_name: str = hero.get("class_name", "")
            name: str = hero.get("name", "")
            hideout_text: str = hero.get("hideout_rich_presence", "In the Hideout")

            if not class_name or not name:
                continue

            # class_name looks like "hero_inferno" → strip "hero_" prefix
            codename = class_name.removeprefix("hero_")

            # Determine Discord asset key:
            # Use override if exists, otherwise use the full class_name from the API.
            asset_key = _ASSET_OVERRIDES.get(codename, class_name)

            images = hero.get("images", {})
            icon_image = images.get("icon_hero_card", "") if isinstance(images, dict) else ""
            card_image = images.get("portrait", "") if isinstance(images, dict) else ""

            parsed[codename] = HeroInfo(
                name=name,
                hideout_text=hideout_text,
                asset_key=asset_key,
                icon_image=icon_image,
                card_image=card_image,
            )

        if parsed:
            self._data = {**_FALLBACK, **parsed}
            logger.info("Loaded %d heroes from API.", len(parsed))
            self._save_cache(parsed)
        else:
            logger.warning("API returned empty hero list, using fallback.")

    def _save_cache(self, data: dict[str, HeroInfo]) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("Hero cache saved to %s", self._cache_path)
        except Exception as e:
            logger.warning("Could not save hero cache: %s", e)
