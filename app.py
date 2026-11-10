import streamlit as st
import numpy as np
import pickle
import pandas as pd
import requests
import time
import json
import os
import re
import difflib
import random
import threading
import urllib.parse
import hashlib
import hmac
import secrets
from datetime import datetime
from html import escape, unescape
from concurrent.futures import ThreadPoolExecutor, as_completed

# All project files are resolved relative to this app.py file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------
# Page config
# ---------------------------------------------------------------
st.set_page_config(
    page_title="AnimeViewer - Discover Anime",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------
# CSS: dark theme + 3D hover cards
# ---------------------------------------------------------------
st.markdown("""
<style>
/* ---------- theme the Streamlit widgets (menu, search, settings, sign in...) ---------- */
[data-testid="stPopover"] button,
button[data-testid="stBaseButton-secondary"], button[kind="secondary"],
[data-testid="stBaseLinkButton-secondary"], [data-testid="stDownloadButton"] button {
    background: #1a1829 !important; color: #ffffff !important;
    border: 1px solid #2b2840 !important; border-radius: 8px !important;
}
[data-testid="stPopover"] button p, button[data-testid="stBaseButton-secondary"] p,
button[kind="secondary"] p, [data-testid="stBaseLinkButton-secondary"] p { color: #ffffff !important; }
[data-testid="stPopover"] button svg { fill: #ffffff !important; color: #ffffff !important; }
[data-testid="stPopover"] button:hover,
button[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover,
[data-testid="stBaseLinkButton-secondary"]:hover {
    border-color: #ff2a75 !important; background: #241f3a !important; color: #ffffff !important;
}
[data-testid="stPopoverBody"] {
    background: #12101b !important; border: 1px solid #2b2840 !important; color: #ffffff !important;
}
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] {
    background: #1a1829 !important; border-color: #2b2840 !important;
}
[data-baseweb="input"] input, [data-baseweb="base-input"] input { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
[data-baseweb="tab"] { color: #cfcde6 !important; }
[data-baseweb="tab"][aria-selected="true"] { color: #ffffff !important; }
[data-baseweb="popover"] ul, [role="listbox"] { background: #1a1829 !important; }
[role="option"] { color: #ffffff !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: #2b2840 !important; }
.stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #ffffff; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: #9a97b8 !important; }
[data-testid="stExpander"] { border: 1px solid #2b2840 !important; border-radius: 10px; background: rgba(26,24,41,.55); }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color: #ffffff !important; }

.stApp { background-color: #0b0a12; color: #ffffff; }
[data-testid="stSidebar"] { background-color: #12101b; border-right: 1px solid #1a1829; }
.sidebar-brand { font-size: 20px; font-weight: bold; color: #ffffff; margin-bottom: 25px; }
div[data-baseweb="select"] > div {
    background-color: #1a1829 !important; border-color: #2b2840 !important;
    color: #ffffff !important; border-radius: 8px !important;
}

/* ---------- 3D card ---------- */
.card3d { perspective: 900px; margin-bottom: 22px; }
.card-inner {
    position: relative; border-radius: 12px; overflow: hidden;
    transform-style: preserve-3d; background: #1a1829;
    box-shadow: 0 6px 18px rgba(0,0,0,.45);
    transition: transform .4s ease, box-shadow .4s ease;
}
.card3d:hover .card-inner {
    transform: rotateY(-12deg) rotateX(6deg) translateZ(18px) scale(1.04);
    box-shadow: -14px 18px 34px rgba(255,42,117,.30);
}
.pwrap { position: relative; width: 100%; padding-top: 150%; background: #1a1829; }
.pwrap .poster { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
.badge {
    position: absolute; top: 8px; left: 8px; padding: 2px 8px; border-radius: 999px;
    font-size: 10px; font-weight: 700; background: rgba(11,10,18,.85); color: #fff;
    border: 1px solid #ff2a75;
}
.badge.airing { border-color: #2ee59d; color: #2ee59d; }
.badge.upcoming { border-color: #ffb703; color: #ffb703; }
.overlay {
    position: absolute; inset: 0; padding: 10px; display: flex; align-items: flex-end;
    background: linear-gradient(to bottom, rgba(11,10,18,0) 25%, rgba(11,10,18,.96));
    opacity: 0; transition: opacity .3s ease;
    font-size: 11px; line-height: 1.4; color: #dcdcec;
}
.card3d:hover .overlay { opacity: 1; }

.info {
    height: 104px; display: flex; flex-direction: column; align-items: center;
    gap: 3px; margin-top: 8px; overflow: hidden;
}
.anime-name {
    font-size: 13px; font-weight: 700; color: #ffffff; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; text-align: center;
    width: 100%; height: 18px; line-height: 18px;
}
.anime-rating { font-size: 12px; font-weight: bold; color: #ffb703; text-align: center; height: 16px; line-height: 16px; }
.meta {
    font-size: 10.5px; color: #9a97b8; text-align: center; width: 100%;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; height: 15px; line-height: 15px;
}
.next-ep {
    font-size: 10.5px; color: #2ee59d; text-align: center; font-weight: 600; width: 100%;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; height: 15px; line-height: 15px;
}
.watch {
    display: flex; flex-wrap: nowrap; gap: 4px; justify-content: center;
    width: 100%; height: 24px; margin-top: 4px; overflow: hidden;
}
.wbtn {
    font-size: 10px; font-weight: 700; padding: 3px 7px; border-radius: 6px; white-space: nowrap;
    max-width: 78px; overflow: hidden; text-overflow: ellipsis; line-height: 16px;
    background: #ff2a75; color: #ffffff !important; text-decoration: none !important;
    transition: transform .2s ease, background .2s ease;
}
.wbtn:hover { background: #ff5c97; transform: translateY(-2px); }
.wbtn.alt { background: #2b2840; }
.wbtn.alt:hover { background: #3a3658; }
/* small round favorite button, drawn on top of the poster (top-right) */
[class*="st-key-fav_"] {
    position: relative; z-index: 20; height: 0 !important; min-height: 0 !important;
    width: 100% !important; display: flex !important; justify-content: flex-end;
}
[class*="st-key-fav_"] > div { width: auto !important; }
[class*="st-key-fav_"] button {
    width: 30px !important; height: 30px !important; min-height: 30px !important;
    padding: 0 !important; margin: 7px 8px 0 0 !important; border-radius: 50% !important;
    background: rgba(11,10,18,.72) !important; border: 1px solid rgba(255,255,255,.35) !important;
    backdrop-filter: blur(3px); font-size: 14px !important; line-height: 1 !important;
    display: flex; align-items: center; justify-content: center;
    transition: transform .2s ease, border-color .2s ease, background .2s ease;
}
[class*="st-key-fav_"] button p { font-size: 14px !important; margin: 0 !important; line-height: 1 !important; }
[class*="st-key-fav_"] button:hover {
    transform: scale(1.18); border-color: #ff2a75 !important; background: rgba(255,42,117,.30) !important;
}
/* no sidebar: navigation lives in the top bar */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] { display: none !important; }
.brand { font-size: 20px; font-weight: 800; color: #ffffff; white-space: nowrap; }
/* background picker: the whole colour tile is the (invisible) button */
[class*="st-key-bg_"] {
    position: relative; z-index: 5; height: 84px !important; min-height: 84px !important;
    margin-top: calc(-84px - 1rem) !important; width: 100% !important;
}
[class*="st-key-bg_"] > div, [class*="st-key-bg_"] .stButton { width: 100% !important; }
[class*="st-key-bg_"] button {
    width: 100% !important; height: 84px !important; min-height: 84px !important;
    background: transparent !important; border: 0 !important; color: transparent !important;
    border-radius: 12px !important; padding: 0 !important; cursor: pointer;
    transition: background .2s ease, box-shadow .2s ease;
}
[class*="st-key-bg_"] button p { color: transparent !important; }
[class*="st-key-bg_"] button:hover {
    background: rgba(255,255,255,.07) !important; box-shadow: inset 0 0 0 2px rgba(255,255,255,.55) !important;
}
/* hidden helper buttons: the heart inside the HTML cards clicks these */
[class*="st-key-favrow_"] { display: none !important; }
/* pull the card up so the poster starts exactly where the heart container is */
.stElementContainer:has(.card3d) { margin-top: -1rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Load models
# ---------------------------------------------------------------
@st.cache_resource
def load_data():
    data_path = os.path.join(BASE_DIR, "anime_dict.pkl")
    similarity_path = os.path.join(BASE_DIR, "anime_similarity_topk.npz")

    with open(data_path, "rb") as f:
        anime_dict = pickle.load(f)

    data = np.load(similarity_path)
    anime_frame = pd.DataFrame(anime_dict)

    if len(anime_frame) != data["idx"].shape[0]:
        st.error("Anime dataset and model size mismatch.")
        st.stop()

    return anime_frame.reset_index(drop=True), data["idx"], data["val"]



# ---------------------------------------------------------------
# Info store: disk cache + rate limiter
# ---------------------------------------------------------------
CACHE_FILE = os.path.join(BASE_DIR, "poster_cache_v4.json")   # v4 = includes episodes / links / next episode / trailer

_PH_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='450'>"
    "<rect width='100%' height='100%' fill='#1a1829'/>"
    "<text x='50%' y='50%' fill='#6c698d' font-size='22' "
    "text-anchor='middle' font-family='sans-serif'>No Poster</text></svg>"
)
PLACEHOLDER = "data:image/svg+xml;utf8," + urllib.parse.quote(_PH_SVG)

anime_df, topk_idx, topk_val = load_data()
@st.cache_resource
def get_store():
    data = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    return {
        "data": data,
        "lock": threading.Lock(),
        "rate_lock": threading.Lock(),
        "last_call": [0.0],
        "session": requests.Session(),
    }


store = get_store()


def _save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(store["data"], f)
    except Exception:
        pass


def _wait_for_slot(min_gap=0.4):
    with store["rate_lock"]:
        wait = min_gap - (time.time() - store["last_call"][0])
        if wait > 0:
            time.sleep(wait)
        store["last_call"][0] = time.time()


def blank_info(**kw):
    info = {
        "poster": PLACEHOLDER, "score": "N/A", "synopsis": "Details not available.",
        "episodes": None, "status": None, "season": None, "year": None, "format": None,
        "next_ep": None, "next_at": None, "links": [], "trailer": None, "seasons": None,
        "url": None, "source": None, "fetched_at": time.time(),
    }
    info.update(kw)
    return info


# ---------------------------------------------------------------
# Source 1: AniList (free, no key)
# ---------------------------------------------------------------
ANILIST_QUERY = """
query ($search: String) {
  Page(perPage: 6) {
    media(search: $search, type: ANIME, sort: SEARCH_MATCH) {
      siteUrl format status episodes season seasonYear popularity
      title { romaji english native }
      coverImage { extraLarge large }
      averageScore
      description(asHtml: false)
      trailer { id site }
      nextAiringEpisode { episode airingAt }
      externalLinks { site url type }
      relations { edges { relationType node { id type format } } }
    }
  }
}
"""


def _pick_best(query, items):
    q = query.lower().strip()

    def rank(m):
        t = m.get("title") or {}
        titles = [x for x in (t.get("romaji"), t.get("english"), t.get("native")) if x]
        sim = max((difflib.SequenceMatcher(None, q, x.lower()).ratio() for x in titles), default=0)
        bonus = 0.15 if m.get("format") in ("TV", "MOVIE", "OVA") else 0
        pop = min((m.get("popularity") or 0) / 200000, 0.1)
        return sim + bonus + pop

    return max(items, key=rank)


def _query_anilist(query):
    for attempt in range(3):
        _wait_for_slot(0.7)
        try:
            r = store["session"].post(
                "https://graphql.anilist.co",
                json={"query": ANILIST_QUERY, "variables": {"search": query}},
                timeout=8,
            )
        except requests.RequestException:
            time.sleep(0.6)
            continue
        if r.status_code == 429:
            try:
                wait = int(r.headers.get("Retry-After", 2 * (attempt + 1)))
            except ValueError:
                wait = 2 * (attempt + 1)
            if wait > 8:
                return None
            time.sleep(wait + 0.5)
            continue
        if r.status_code != 200:
            return None

        items = ((r.json().get("data") or {}).get("Page") or {}).get("media") or []
        items = [m for m in items if (m.get("coverImage") or {}).get("large")]
        if not items:
            return None
        m = _pick_best(query, items)

        cover = m.get("coverImage") or {}
        score = m.get("averageScore")
        desc = re.sub(r"<[^>]+>", " ", m.get("description") or "No description available.")
        nxt = m.get("nextAiringEpisode") or {}
        tr = m.get("trailer") or {}
        trailer = (f"https://www.youtube.com/watch?v={tr['id']}"
                   if (tr.get("site") or "").lower() == "youtube" and tr.get("id") else None)

        links = []
        for l in (m.get("externalLinks") or []):
            if l.get("type") == "STREAMING" and (l.get("url") or "").startswith("http"):
                links.append({"site": l.get("site") or "Watch", "url": l["url"]})

        linked = 0
        for e in ((m.get("relations") or {}).get("edges") or []):
            n = e.get("node") or {}
            if e.get("relationType") in ("PREQUEL", "SEQUEL") and n.get("type") == "ANIME" \
                    and n.get("format") in ("TV", "TV_SHORT"):
                linked += 1

        return blank_info(
            poster=cover.get("extraLarge") or cover.get("large"),
            score=round(score / 10, 1) if score else "N/A",
            synopsis=re.sub(r"\s+", " ", desc).strip(),
            episodes=m.get("episodes"),
            status=m.get("status"),
            season=m.get("season"),
            year=m.get("seasonYear"),
            format=m.get("format"),
            next_ep=nxt.get("episode"),
            next_at=nxt.get("airingAt"),
            links=links,
            seasons=(linked + 1) if m.get("format") in ("TV", "TV_SHORT") else None,
            url=m.get("siteUrl"),
            trailer=trailer,
            source="anilist",
        )
    return None


# ---------------------------------------------------------------
# Source 2: Kitsu (backup, poster only)
# ---------------------------------------------------------------
def _query_kitsu(query):
    try:
        r = store["session"].get(
            "https://kitsu.io/api/edge/anime",
            params={"filter[text]": query, "page[limit]": 3},
            headers={"Accept": "application/vnd.api+json"},
            timeout=8,
        )
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    for it in (r.json().get("data") or []):
        a = it.get("attributes") or {}
        pi = a.get("posterImage") or {}
        img = pi.get("large") or pi.get("medium") or pi.get("original")
        if img:
            try:
                score = round(float(a.get("averageRating")) / 10, 1)
            except (TypeError, ValueError):
                score = "N/A"
            return blank_info(
                poster=img, score=score,
                synopsis=a.get("synopsis") or "No description available.",
                episodes=a.get("episodeCount"), source="kitsu",
            )
    return None


# ---------------------------------------------------------------
# Source 3: Jikan (last resort)
# ---------------------------------------------------------------
def _query_jikan(query):
    url = f"https://api.jikan.moe/v4/anime?q={urllib.parse.quote(query)}&limit=1"
    for attempt in range(2):
        _wait_for_slot()
        try:
            r = store["session"].get(url, timeout=5)
        except requests.RequestException:
            time.sleep(0.8)
            continue
        if r.status_code == 429:
            time.sleep(1.2 * (attempt + 1))
            continue
        if r.status_code != 200:
            return None
        data = r.json().get("data") or []
        if not data:
            return None
        item = data[0]
        jpg = item.get("images", {}).get("jpg", {})
        img = jpg.get("large_image_url") or jpg.get("image_url")
        if not img:
            return None
        return blank_info(
            poster=img, score=item.get("score") or "N/A",
            synopsis=item.get("synopsis") or "No description available.",
            episodes=item.get("episodes"), source="jikan",
        )
    return None


def _title_variants(name):
    name = unescape(name)
    variants = [name]
    cleaned = "".join(c for c in name if c.isalnum() or c.isspace()).strip()
    short = re.split(r"[:\-–(]", name)[0]
    short = "".join(c for c in short if c.isalnum() or c.isspace()).strip()
    for v in (cleaned, short):
        if v and v not in variants:
            variants.append(v)
    return variants


def _is_stale(e):
    age = time.time() - e.get("fetched_at", 0)
    if e.get("source") != "anilist":
        return age > 3600                       # retry AniList for backup results
    if e.get("status") in ("RELEASING", "NOT_YET_RELEASED"):
        return age > 6 * 3600                   # airing shows: refresh every 6h
    return age > 30 * 86400


def _fetch_info_raw(name):
    with store["lock"]:
        old = store["data"].get(name)
        if old and not _is_stale(old):
            return old

    result = None
    variants = _title_variants(name)
    for v in variants:
        result = _query_anilist(v)
        if result:
            break
    if result is None:
        for v in variants:
            result = _query_kitsu(v)
            if result:
                break
    if result is None:
        result = _query_jikan(name)

    if result:
        with store["lock"]:
            store["data"][name] = result
            _save_cache()
        return result
    return old or blank_info(fetched_at=0)


# ---------------------------------------------------------------
# Cartoons (Doraemon, Pokemon, Shin-chan...): own list, YouTube search links
# ---------------------------------------------------------------
CARTOONS = [
    {"name": "Doraemon", "q": "Doraemon", "group": "Japanese", "fetch": "Doraemon"},
    {"name": "Pokémon", "q": "Pokemon", "group": "Japanese", "fetch": "Pokemon"},
    {"name": "Shin-chan", "q": "Shinchan", "group": "Japanese", "fetch": "Crayon Shin-chan"},
    {"name": "Ninja Hattori", "q": "Ninja Hattori", "group": "Japanese", "fetch": "Ninja Hattori-kun"},
    {"name": "Kiteretsu", "q": "Kiteretsu", "group": "Japanese", "fetch": "Kiteretsu Daihyakka"},
    {"name": "Perman", "q": "Perman", "group": "Japanese", "fetch": "Perman"},
    {"name": "Beyblade", "q": "Beyblade", "group": "Japanese", "fetch": "Beyblade"},
    {"name": "Dragon Ball Z", "q": "Dragon Ball Z", "group": "Japanese", "fetch": "Dragon Ball Z"},
    {"name": "Chhota Bheem", "q": "Chhota Bheem", "group": "Indian", "alts": ["Chota Bheem"],
     "desc": "Indian animated adventure series about Bheem, a brave boy from the village of Dholakpur."},
    {"name": "Motu Patlu", "q": "Motu Patlu", "group": "Indian",
     "desc": "Indian comedy series about the friends Motu and Patlu and their adventures in Furfuri Nagar."},
    {"name": "Little Singham", "q": "Little Singham", "group": "Indian",
     "desc": "Indian action-comedy animated series about a young hero inspired by a fearless police officer."},
    {"name": "Mighty Raju", "q": "Mighty Raju", "group": "Indian",
     "desc": "Indian animated series about Raju, a young boy with superpowers."},
    {"name": "Oggy and the Cockroaches", "q": "Oggy and the Cockroaches", "group": "Western",
     "desc": "Comedy cartoon about a lazy cat and three cockroaches who keep making trouble."},
    {"name": "Tom and Jerry", "q": "Tom and Jerry", "group": "Western",
     "desc": "The classic cat-and-mouse chase comedy."},
    {"name": "Ben 10", "q": "Ben 10", "group": "Western",
     "desc": "Ben Tennyson finds the Omnitrix, a watch that lets him turn into different aliens."},
]
CARTOON_MAP = {c["name"]: c for c in CARTOONS}


def _text_poster(title):
    import textwrap
    hue = sum(ord(ch) for ch in title) % 360
    lines = textwrap.wrap(title, 14)[:3]
    text = "".join(
        f"<text x='50%' y='{300 + i * 34}' fill='#ffffff' font-size='28' font-weight='bold' "
        f"text-anchor='middle' font-family='sans-serif'>{escape(l)}</text>"
        for i, l in enumerate(lines))
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='450'>"
        "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
        f"<stop offset='0' stop-color='hsl({hue},65%,42%)'/>"
        f"<stop offset='1' stop-color='hsl({(hue + 50) % 360},60%,18%)'/></linearGradient></defs>"
        "<rect width='100%' height='100%' fill='url(#g)'/>"
        "<text x='50%' y='210' font-size='96' text-anchor='middle'>🧸</text>"
        + text + "</svg>")
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
       "Accept-Language": "en-US,en;q=0.9"}


def _sim(a, b):
    return difflib.SequenceMatcher(None, a.lower(), (b or "").lower()).ratio()


def _tvmaze_lookup(sess, names):
    best, best_s = None, 0.0
    for q in names:
        try:
            _wait_for_slot(0.3)
            r = sess.get("https://api.tvmaze.com/search/shows", params={"q": q}, timeout=8)
            if r.status_code != 200:
                continue
            for it in r.json():
                sh = it.get("show") or {}
                img = sh.get("image") or {}
                sim = _sim(q, sh.get("name")) + (0.05 if img else 0)
                if sim > best_s:
                    best, best_s = sh, sim
        except Exception:
            continue
        if best_s >= 0.85:
            break
    if not best or best_s < 0.6:
        return None
    img = best.get("image") or {}
    url = img.get("original") or img.get("medium")
    avg = (best.get("rating") or {}).get("average")
    syn = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", best.get("summary") or "")).strip()
    year = str(best.get("premiered") or "")[:4]
    return {
        "poster": url.replace("http://", "https://") if url else None,
        "score": round(float(avg), 1) if avg else None,
        "synopsis": syn,
        "year": int(year) if year.isdigit() else None,
        "status": {"Ended": "FINISHED", "Running": "RELEASING"}.get(best.get("status")),
    }


def _imdb_lookup(sess, names):
    best, best_s = None, 0.0
    for q in names:
        key = q.lower().strip()
        if not key:
            continue
        first = key[0] if key[0].isalnum() else "_"
        try:
            r = sess.get(f"https://v2.sg.media-imdb.com/suggestion/{first}/{urllib.parse.quote(key)}.json",
                         headers=_UA, timeout=8)
            if r.status_code != 200:
                continue
            for d in (r.json().get("d") or []):
                img = (d.get("i") or {}).get("imageUrl")
                if not img or not str(d.get("id", "")).startswith("tt"):
                    continue
                if d.get("qid") not in ("tvSeries", "tvMiniSeries", "movie", "tvMovie", "video"):
                    continue
                sim = _sim(q, d.get("l"))
                if sim > best_s:
                    best, best_s = {"poster": img, "id": d["id"], "year": d.get("y")}, sim
        except Exception:
            continue
        if best_s >= 0.85:
            break
    return best if best and best_s >= 0.6 else None


def _imdb_rating(sess, tt):
    try:                                                   # 1) imdbapi.dev
        r = sess.get(f"https://api.imdbapi.dev/titles/{tt}", timeout=6)
        if r.status_code == 200:
            v = (r.json().get("rating") or {}).get("aggregateRating")
            if v:
                return round(float(v), 1)
    except Exception:
        pass
    try:                                                   # 2) IMDb GraphQL
        q = 'query{title(id:"%s"){ratingsSummary{aggregateRating}}}' % tt
        r = sess.post("https://caching.graphql.imdb.com/", json={"query": q},
                      headers=dict(_UA, **{"Content-Type": "application/json"}), timeout=6)
        if r.status_code == 200:
            v = ((((r.json().get("data") or {}).get("title") or {}).get("ratingsSummary") or {})
                 .get("aggregateRating"))
            if v:
                return round(float(v), 1)
    except Exception:
        pass
    try:                                                   # 3) title page
        r = sess.get(f"https://www.imdb.com/title/{tt}/", headers=_UA, timeout=6)
        if r.status_code == 200:
            m = re.search(r'"ratingValue"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)', r.text)
            if m:
                return round(float(m.group(1)), 1)
    except Exception:
        pass
    return None


def _itunes_lookup(sess, names):
    for q in names:
        try:
            r = sess.get("https://itunes.apple.com/search",
                         params={"term": q, "media": "tvShow", "entity": "tvSeason", "country": "IN", "limit": 6},
                         timeout=8)
            if r.status_code != 200:
                continue
            for it in (r.json().get("results") or []):
                nm = re.split(r",\s*Season", it.get("collectionName") or it.get("artistName") or "")[0]
                art = it.get("artworkUrl100")
                if art and _sim(q, nm) >= 0.7:
                    return art.replace("100x100bb", "600x600bb")
        except Exception:
            continue
    return None


def _wiki_lookup(sess, q):
    try:
        r = sess.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "generator": "search", "gsrsearch": q + " animated series",
                    "gsrlimit": 4, "prop": "pageimages", "piprop": "thumbnail", "pithumbsize": 500,
                    "format": "json"},
            headers={"User-Agent": "AnimeViewer/1.0 (personal project)"}, timeout=8)
        if r.status_code == 200:
            pages = ((r.json().get("query") or {}).get("pages") or {}).values()
            first = q.lower().split()[0]
            for pg in sorted(pages, key=lambda x: x.get("index", 99)):
                thumb = (pg.get("thumbnail") or {}).get("source")
                if thumb and first in (pg.get("title") or "").lower():
                    return thumb
    except Exception:
        pass
    return None


def _fetch_cartoon_external(c):
    """Poster + rating for non-anime cartoons: TVmaze, IMDb, iTunes, Wikipedia (first that has them)."""
    names = [c.get("tv") or c["name"]] + list(c.get("alts", []))
    sess = store["session"]
    tv = _tvmaze_lookup(sess, names) or {}
    poster, src, score = tv.get("poster"), ("tvmaze" if tv.get("poster") else None), tv.get("score")
    imdb = None
    if not poster or not score:
        imdb = _imdb_lookup(sess, names)
        if imdb:
            if not poster:
                poster, src = imdb["poster"], "imdb"
            if not score:
                score = _imdb_rating(sess, imdb["id"])
    if not poster:
        poster = _itunes_lookup(sess, names)
        src = "itunes" if poster else src
    if not poster:
        poster = _wiki_lookup(sess, names[0])
        src = "wikipedia" if poster else src
    if not poster and not tv and not imdb:
        return None
    return blank_info(
        poster=poster or PLACEHOLDER,
        score=score or "N/A",
        synopsis=tv.get("synopsis") or c.get("desc", ""),
        year=tv.get("year") or (imdb or {}).get("year"),
        status=tv.get("status"),
        source=src or "no-picture",
    )


def cartoon_info(c):
    if c.get("fetch"):
        info = dict(_fetch_info_raw(c["fetch"]))
    else:
        key = "cartoon2:" + c["name"]
        with store["lock"]:
            e = store["data"].get(key)
        age = time.time() - (e or {}).get("fetched_at", 0)
        _has_score = bool(e) and (e.get("info") or {}).get("score") not in (None, "N/A")
        if e and age < (30 * 86400 if (e.get("ok") and _has_score) else (86400 if e.get("ok") else 3600)):
            info = dict(e["info"])
        else:
            res = _fetch_cartoon_external(c)
            info = res or blank_info(score="N/A", synopsis=c.get("desc", ""), source="none")
            ok = bool(res) and res.get("poster") not in (None, PLACEHOLDER)
            with store["lock"]:
                store["data"][key] = {"ok": ok, "fetched_at": time.time(), "info": info}
                _save_cache()
            info = dict(info)
        if not info.get("synopsis") or "not available" in info["synopsis"]:
            info["synopsis"] = c.get("desc", "")
    if not info.get("poster") or info["poster"] == PLACEHOLDER:
        info["poster"] = _text_poster(c["name"])
    return info


def fetch_info(name):
    c = CARTOON_MAP.get(unescape(name))
    if c:
        return cartoon_info(c)
    return _fetch_info_raw(name)


# ---------------------------------------------------------------
# Card HTML
# ---------------------------------------------------------------
STATUS_LABEL = {
    "FINISHED": ("Finished", ""),
    "RELEASING": ("Airing", "airing"),
    "NOT_YET_RELEASED": ("Upcoming", "upcoming"),
    "CANCELLED": ("Cancelled", ""),
    "HIATUS": ("Hiatus", ""),
}


def _countdown(ts):
    delta = int(ts - time.time())
    if delta <= 0:
        return "airing now"
    d, rem = divmod(delta, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


SITE_ORDER = ["Crunchyroll", "Netflix", "Amazon Prime Video", "Hulu", "Disney Plus",
              "HIDIVE", "Bilibili TV", "YouTube"]
SITE_SHORT = {"Amazon Prime Video": "Prime Video", "Disney Plus": "Disney+", "Bilibili TV": "Bilibili"}


def _site_rank(l):
    try:
        return SITE_ORDER.index(l.get("site"))
    except ValueError:
        return 99


def card_html(name, info, loading=False, fav=False):
    name = unescape(name)                       # dataset has names like Gintama&#039;
    poster = escape(info.get("poster") or PLACEHOLDER, quote=True)
    n = escape(name, quote=True)
    score = "..." if loading else info.get("score", "N/A")

    heart = ""                                  # state is shown by the round button
    badge = ""
    label = STATUS_LABEL.get(info.get("status"))
    if label:
        badge = f"<div class='badge {label[1]}'>{label[0]}</div>"

    full_syn = info.get("synopsis") or ""
    syn = escape(full_syn[:230]) + ("..." if len(full_syn) > 230 else "")

    # one-line meta: "24 eps · 2011 · 3 seasons"
    meta = []
    eps = info.get("episodes")
    if eps:
        meta.append(f"{eps} ep" if eps == 1 else f"{eps} eps")
    elif info.get("status") == "RELEASING":
        meta.append("ongoing")
    if info.get("year"):
        meta.append(str(info["year"]))
    if info.get("seasons") and info["seasons"] > 1:
        meta.append(f"{info['seasons']} seasons")
    meta_tip = ""
    if info.get("season") and info.get("year"):
        meta_tip = f"{str(info['season']).title()} {info['year']}"
    meta_html = f"<div class='meta' title='{escape(meta_tip, quote=True)}'>{escape(' · '.join(meta)) or '&nbsp;'}</div>"

    # one-line next episode (always reserves its row so cards stay aligned)
    next_html = "<div class='next-ep'>&nbsp;</div>"
    if info.get("next_ep") and info.get("next_at"):
        when = datetime.fromtimestamp(info["next_at"]).strftime("%a %d %b, %I:%M %p")
        next_html = (f"<div class='next-ep' title='{escape(when, quote=True)}'>"
                     f"⏳ Ep {info['next_ep']} in {_countdown(info['next_at'])}</div>")

    # one-line watch row: up to 2 platforms + Info (1 platform + Trailer + Info when a trailer exists)
    buttons = ""
    if not loading:
        q = urllib.parse.quote(name)
        links = sorted(info.get("links") or [], key=_site_rank)[:1 if info.get("trailer") else 2]
        for l in links:
            site = SITE_SHORT.get(l["site"], l["site"])
            buttons += (f"<a class='wbtn' href='{escape(l['url'], quote=True)}' target='_blank' "
                        f"rel='noopener noreferrer' title='{escape(l['site'], quote=True)}'>▶ {escape(site)}</a>")
        if not buttons:
            buttons = (f"<a class='wbtn' href='https://www.crunchyroll.com/search?q={q}' "
                       f"target='_blank' rel='noopener noreferrer'>▶ Crunchyroll</a>")
        if info.get("trailer"):
            buttons += (f"<a class='wbtn alt' href='{escape(info['trailer'], quote=True)}' "
                        "target='_blank' rel='noopener noreferrer'>🎞 Trailer</a>")
        if info.get("url"):
            buttons += (f"<a class='wbtn alt' href='{escape(info['url'], quote=True)}' "
                        f"target='_blank' rel='noopener noreferrer'>Info</a>")

    # language pages (Hindi / Tamil / Telugu / Hindi Sub): buttons search that language
    lang = st.session_state.get("card_lang")
    if lang and not loading:
        qq = urllib.parse.quote(f"{name} {lang}")
        buttons = (
            f"<a class='wbtn' href='https://www.youtube.com/results?search_query={qq}' "
            "target='_blank' rel='noopener noreferrer'>▶ YouTube</a>"
            f"<a class='wbtn alt' href='https://www.google.com/search?q={qq}+watch+online' "
            "target='_blank' rel='noopener noreferrer'>Google</a>"
        )

    cart = CARTOON_MAP.get(name)
    if cart and not loading:
        cq = urllib.parse.quote(cart["q"])
        buttons = (
            f"<a class='wbtn' href='https://www.youtube.com/results?search_query={cq}+full+episodes' "
            "target='_blank' rel='noopener noreferrer'>▶ Episodes</a>"
            f"<a class='wbtn' href='https://www.youtube.com/results?search_query={cq}+full+movie' "
            "target='_blank' rel='noopener noreferrer'>🎬 Movies</a>"
            f"<a class='wbtn alt' href='https://en.wikipedia.org/wiki/Special:Search?search={cq}' "
            "target='_blank' rel='noopener noreferrer'>Info</a>"
        )

    return (
        "<div class='card3d'><div class='card-inner'>"
        f"<div class='pwrap'><img class='poster' src='{poster}' alt='{n}'></div>{badge}{heart}"
        f"<div class='overlay'>{syn}</div></div>"
        "<div class='info'>"
        f"<div class='anime-name' title='{n}'>{escape(name)}</div>"
        f"<div class='anime-rating'>★ {score}</div>"
        f"{meta_html}{next_html}<div class='watch'>{buttons}</div>"
        "</div></div>"
    )


# ---------------------------------------------------------------
# Settings: background theme (saved in settings.json)
# (settings are loaded first, because favorites depend on who is signed in)
# ---------------------------------------------------------------
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
BACKGROUNDS = {
    'Midnight': '#0b0a12',
    'Sakura night': 'radial-gradient(circle at 15% 10%, rgba(255,42,117,.28), transparent 45%), radial-gradient(circle at 90% 85%, rgba(120,60,200,.30), transparent 50%), #0d0a16',
    'Neon Tokyo': 'radial-gradient(circle at 10% 90%, rgba(0,229,255,.22), transparent 42%), radial-gradient(circle at 85% 10%, rgba(255,0,153,.30), transparent 45%), linear-gradient(160deg, #0a0f24, #120a2a)',
    'Aurora': 'radial-gradient(ellipse at 20% 0%, rgba(46,229,157,.28), transparent 50%), radial-gradient(ellipse at 85% 20%, rgba(127,119,221,.32), transparent 50%), linear-gradient(180deg, #070b18, #0b1224)',
    'Sunset': 'linear-gradient(170deg, #1a0b2e 0%, #4a1456 40%, #b3375a 75%, #ff8a4c 120%)',
    'Deep ocean': 'radial-gradient(circle at 80% 0%, rgba(24,160,200,.30), transparent 50%), linear-gradient(180deg, #04101f, #06233a 70%, #052c40)',
}


VIDEO_DIR = os.path.join(BASE_DIR, "static")


def list_videos():
    try:
        return sorted(f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".webm")))
    except Exception:
        return []


def _load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "bg": st.session_state["bg"],
                "video": st.session_state["video"],
                "dim": st.session_state["dim"],
                "user": st.session_state.get("user", ""),
            }, f, ensure_ascii=False)
    except Exception:
        pass


if "bg" not in st.session_state:
    _s = _load_settings()
    st.session_state["user"] = str(_s.get("user", ""))[:30]
    st.session_state["bg"] = _s.get("bg") if _s.get("bg") in BACKGROUNDS else "Midnight"
    st.session_state["video"] = _s.get("video") if _s.get("video") in list_videos() else "None"
    try:
        st.session_state["dim"] = min(max(float(_s.get("dim", 0.45)), 0.0), 0.85)
    except (TypeError, ValueError):
        st.session_state["dim"] = 0.45

# ---------------------------------------------------------------
# Favorites (per user: favorites_<username>.json, guest: favorites.json)
# ---------------------------------------------------------------
def _fav_file():
    u = st.session_state.get("user", "")
    return os.path.join(BASE_DIR, f"favorites_{u.lower()}.json") if u else os.path.join(BASE_DIR, "favorites.json")


def _load_favs():
    try:
        with open(_fav_file(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return [x for x in data if isinstance(x, str)]
    except Exception:
        return []


def _save_favs():
    try:
        with open(_fav_file(), "w", encoding="utf-8") as f:
            json.dump(st.session_state["favs"], f, ensure_ascii=False)
    except Exception:
        pass


if "favs" not in st.session_state:
    st.session_state["favs"] = _load_favs()

# ---------------------------------------------------------------
# Watching history (history.json): anime you searched / opened in TV mode
# ---------------------------------------------------------------
HIST_FILE = os.path.join(BASE_DIR, "history.json")


def _hist_file():
    username = st.session_state.get("user", "")
    return os.path.join(BASE_DIR, f"history_{username.lower()}.json") if username else HIST_FILE


def _load_hist():
    try:
        with open(_hist_file(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return [x for x in data if isinstance(x, str)] if isinstance(data, list) else []
    except Exception:
        return []


def record_history(name):
    if not isinstance(name, str) or not name.strip():
        return
    h = st.session_state.setdefault("hist", _load_hist())
    if h and h[0] == name:
        return
    if name in h:
        h.remove(name)
    h.insert(0, name)
    del h[30:]
    try:
        with open(_hist_file(), "w", encoding="utf-8") as f:
            json.dump(h, f, ensure_ascii=False)
    except OSError:
        pass


def clear_history():
    st.session_state["hist"] = []
    try:
        with open(_hist_file(), "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
    except OSError:
        pass


if "hist" not in st.session_state:
    st.session_state["hist"] = _load_hist()


def set_bg(name):
    st.session_state["bg"] = name
    _save_settings()


def set_video():
    st.session_state["video"] = st.session_state["video_pick"]
    _save_settings()


def set_dim():
    st.session_state["dim"] = float(st.session_state["dim_pick"])
    _save_settings()


def apply_background():
    bg = BACKGROUNDS.get(st.session_state["bg"], BACKGROUNDS["Midnight"])
    video = st.session_state.get("video", "None")
    if video != "None" and video in list_videos():
        dim = st.session_state.get("dim", 0.45)
        url = "app/static/" + urllib.parse.quote(video)
        st.markdown(
            "<style>"
            "html, body, .stApp { background: #0b0a12 !important; }"
            "[data-testid='stAppViewContainer'] { position: relative; isolation: isolate; background: transparent !important; }"
            "[data-testid='stMain'], [data-testid='stHeader'] { background: transparent !important; }"
            "[data-testid='stSidebar'] { background: rgba(18,16,27,.62) !important; backdrop-filter: blur(8px); }"
            ".bgvid { position: fixed; inset: 0; width: 100vw; height: 100vh; object-fit: cover; z-index: -1;"
            " pointer-events: none; transform-origin: 50% 50%; animation: bgdepth 28s ease-in-out infinite alternate; }"
            "@keyframes bgdepth { from { transform: scale(1.03) translate3d(0,0,0); }"
            " to { transform: scale(1.14) translate3d(-1.2%, -1%, 0); } }"
            ".bgshade { position: fixed; inset: 0; z-index: -1; pointer-events: none;"
            f" background: radial-gradient(ellipse at 50% 40%, rgba(11,10,18,0) 30%, rgba(11,10,18,.78) 100%),"
            f" rgba(11,10,18,{dim}); }}"
            "</style>"
            f"<video class='bgvid' src='{url}' autoplay loop muted playsinline></video>"
            "<div class='bgshade'></div>",
            unsafe_allow_html=True,
        )
        return
    st.markdown(
        "<style>"
        f".stApp {{ background: {bg} !important; background-attachment: fixed !important; }}"
        "[data-testid='stHeader'] { background: transparent !important; }"
        "[data-testid='stSidebar'] { background: rgba(18,16,27,.82) !important; backdrop-filter: blur(6px); }"
        "</style>",
        unsafe_allow_html=True,
    )


def toggle_fav(name):
    favs = st.session_state["favs"]
    if name in favs:
        favs.remove(name)
    else:
        favs.append(name)
    _save_favs()


# ---------------------------------------------------------------
# My List + Episode tracker (per user: tracker_<username>.json, guest: tracker.json)
# Online jaate waqt sirf _tr_load() aur _tr_save() ko database se badalna hoga.
# ---------------------------------------------------------------
ML_STATUSES = ["Watching", "Plan to watch", "Completed", "Dropped"]
ML_ICON = {"Watching": "▶️", "Plan to watch": "🕒", "Completed": "✅", "Dropped": "🛑"}


def _tr_file():
    u = st.session_state.get("user", "")
    return os.path.join(BASE_DIR, f"tracker_{u.lower()}.json") if u else os.path.join(BASE_DIR, "tracker.json")


def _tr_load():
    try:
        with open(_tr_file(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _tr_save(data):
    try:
        with open(_tr_file(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def get_tracker():
    """Cached in session; reloads when the signed-in user changes."""
    ss = st.session_state
    owner = ss.get("user", "")
    if ss.get("_tr_owner") != owner or "_tr" not in ss:
        ss["_tr"] = _tr_load()
        ss["_tr_owner"] = owner
    return ss["_tr"]


def ml_set_status(name, status):
    tr = get_tracker()
    entry = tr.setdefault(name, {"status": status, "watched": 0})
    entry["status"] = status
    _tr_save(tr)


def _ml_on_status(name, key):
    ml_set_status(name, st.session_state[key])


def _ml_on_watched(name, key, total):
    tr = get_tracker()
    entry = tr.setdefault(name, {"status": "Watching", "watched": 0})
    n = int(st.session_state[key])
    entry["watched"] = n
    if total and n >= total:
        entry["status"] = "Completed"
    elif n > 0 and entry["status"] == "Plan to watch":
        entry["status"] = "Watching"
    _tr_save(tr)


def _ml_plus_one(name, total):
    tr = get_tracker()
    entry = tr.setdefault(name, {"status": "Watching", "watched": 0})
    entry["watched"] = entry.get("watched", 0) + 1
    if total and entry["watched"] >= total:
        entry["watched"] = total
        entry["status"] = "Completed"
    elif entry["status"] == "Plan to watch":
        entry["status"] = "Watching"
    _tr_save(tr)


def _ml_remove(name):
    tr = get_tracker()
    tr.pop(name, None)
    _tr_save(tr)


def _ml_apply_choice(name, key):
    choice = st.session_state[key]
    if choice == "Not in list":
        _ml_remove(name)
    else:
        ml_set_status(name, choice)


def list_controls(name):
    """Small dropdown: add any anime to My List (used on the recommendations page)."""
    tr = get_tracker()
    cur = (tr.get(name) or {}).get("status")
    opts = ["Not in list"] + ML_STATUSES
    key = "lc_" + hashlib.md5(name.encode("utf-8")).hexdigest()[:10]
    st.selectbox(
        "📋 My List", opts,
        index=opts.index(cur) if cur in opts else 0,
        key=key, on_change=_ml_apply_choice, args=(name, key))


def _ml_row(name, entry, status, i):
    info = fetch_info(name)
    total = info.get("episodes")
    watched = int(entry.get("watched", 0))
    base = f"ml_{status}_{i}"

    c_img, c_main, c_st, c_ep, c_btn = st.columns([1, 4, 2, 2.3, 1.4], vertical_alignment="center")

    poster = escape(info.get("poster") or PLACEHOLDER, quote=True)
    c_img.markdown(
        f"<img src='{poster}' style='width:60px;height:88px;object-fit:cover;border-radius:8px'>",
        unsafe_allow_html=True)

    with c_main:
        st.markdown(f"**{unescape(name)}**")
        if total:
            st.progress(min(watched / total, 1.0), text=f"{watched} / {total} episodes")
            if watched < total:
                st.caption(f"Next to watch: Ep {watched + 1}")
        else:
            st.caption(f"{watched} episodes dekhe (total unknown)")
            if info.get("next_ep"):
                st.caption(f"Latest aired: Ep {info['next_ep'] - 1}")

    c_st.selectbox(
        "Status", ML_STATUSES, index=ML_STATUSES.index(status),
        key=base + "_st", label_visibility="collapsed",
        on_change=_ml_on_status, args=(name, base + "_st"))

    with c_ep:
        e1, e2 = st.columns([2, 1], vertical_alignment="center")
        e1.number_input(
            "Watched", min_value=0, max_value=int(total) if total else 5000,
            value=min(watched, int(total)) if total else watched,
            step=1, key=base + "_ep", label_visibility="collapsed",
            on_change=_ml_on_watched, args=(name, base + "_ep", total))
        e2.button("+1", key=base + "_p1", on_click=_ml_plus_one, args=(name, total),
                  help="Ek episode aur dekha")

    c_btn.button("Remove", key=base + "_rm", on_click=_ml_remove, args=(name,))
    st.markdown("<hr style='margin:6px 0;border-color:#1a1829'>", unsafe_allow_html=True)


def page_mylist():
    tr = get_tracker()
    if not tr:
        st.info("List abhi khali hai. Kisi anime ko search karo, phir 'My List' dropdown se status chuno. "
                "Ya neeche favorites mein se add karo.")
    favs = [f for f in st.session_state.get("favs", []) if f not in tr]
    if favs:
        with st.expander(f"❤️ Favorites ko list mein add karo ({len(favs)})"):
            for i, f in enumerate(favs):
                c1, c2 = st.columns([4, 1], vertical_alignment="center")
                c1.write(unescape(f))
                c2.button("+ Plan", key=f"addfav_{i}", on_click=ml_set_status, args=(f, "Plan to watch"))

    counts = {s: sum(1 for v in tr.values() if v.get("status") == s) for s in ML_STATUSES}
    tabs = st.tabs([f"{ML_ICON[s]} {s} ({counts[s]})" for s in ML_STATUSES])
    for tab, status in zip(tabs, ML_STATUSES):
        with tab:
            names = [n for n, v in tr.items() if v.get("status") == status]
            if not names:
                st.caption("Yahan abhi kuch nahi hai.")
                continue
            for i, name in enumerate(names):
                _ml_row(name, tr[name], status, i)


def because_you_liked(how_many=5):
    """Home row: anime similar to your last favorites + Completed anime."""
    favs = list(st.session_state.get("favs", []))
    tr = get_tracker()
    liked = favs[-3:] + [n for n, v in tr.items() if v.get("status") == "Completed"][-3:]
    seen = set(favs) | set(tr.keys())

    name_to_idx = {nm: idx for idx, nm in enumerate(anime_df["name"].values)}
    base_idx = [name_to_idx[n] for n in dict.fromkeys(liked) if n in name_to_idx]
    if not base_idx:
        return

        scores = {}
    for bi in base_idx:
        for j, score in zip(topk_idx[bi], topk_val[bi]):
            try:
                j = int(j)
                scores[j] = scores.get(j, 0.0) + float(score)
            except (TypeError, ValueError):
                continue

    picks = []
    for j, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        nm = anime_df.iloc[j]["name"]
        if j in base_idx or nm in seen:
            continue
        picks.append(nm)
        if len(picks) >= how_many:
            break
    if not picks:
        return

    shown = ", ".join(unescape(anime_df.iloc[b]["name"]) for b in base_idx[:2])
    st.markdown(f"##### 💡 Because you liked {escape(shown)}")
    render_grid(picks, how_many, prefix="byl")


# ---------------------------------------------------------------
# Grid: cards show instantly, details fill in as they arrive
# ---------------------------------------------------------------
def render_grid(names, ncols, prefix="grid"):
    favs = st.session_state["favs"]
    loading = blank_info(synopsis="Loading...")
    slots, cols = [], None
    for i, name in enumerate(names):
        if i % ncols == 0:
            cols = st.columns(ncols)
        cell = cols[i % ncols]
        is_fav = name in favs
        cell.button(
            "❤️" if is_fav else "🤍",
            key=f"fav_{prefix}_{name}",
            help="Remove from favorites" if is_fav else "Add to favorites",
            on_click=toggle_fav,
            args=(name,),
        )
        slot = cell.empty()
        slot.markdown(card_html(name, loading, loading=True, fav=is_fav), unsafe_allow_html=True)
        slots.append(slot)

    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(fetch_info, n): k for k, n in enumerate(names)}
        for fut in as_completed(futures):
            k = futures[fut]
            try:
                info = fut.result()
            except Exception:
                info = blank_info()
            slots[k].markdown(card_html(names[k], info, fav=names[k] in favs), unsafe_allow_html=True)


# ---------------------------------------------------------------
# Explore pages (data from anime.csv)
# ---------------------------------------------------------------
BLOCKED_GENRES = {"hentai"}            # adult titles are hidden from these pages


@st.cache_resource
def load_catalog():
    try:
        df = pd.read_csv(os.path.join(BASE_DIR, "anime.csv"))
    except Exception:
        return None
    df.columns = [str(c).strip().lower() for c in df.columns]
    if not {"name", "genre", "type", "rating", "members"}.issubset(df.columns):
        return None
    df = df[["name", "genre", "type", "rating", "members"]].copy()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["members"] = pd.to_numeric(df["members"], errors="coerce").fillna(0)
    df["genres"] = df["genre"].fillna("").apply(
        lambda s: [g.strip() for g in str(s).split(",") if g.strip()])
    df = df[df["rating"].notna()]
    df = df[~df["genres"].apply(lambda gs: any(g.lower() in BLOCKED_GENRES for g in gs))]
    df = df[df["name"].isin(set(anime_df["name"].values))]
    return df.drop_duplicates("name").reset_index(drop=True)


def filter_catalog(cat, genres=(), match_all=True, typ="All", min_rating=0.0,
                   sort="Rating", min_members=5000):
    d = cat
    if genres:
        gs = set(genres)
        d = d[d["genres"].apply(lambda x: gs.issubset(x) if match_all else bool(gs & set(x)))]
    if typ != "All":
        d = d[d["type"] == typ]
    d = d[(d["rating"] >= min_rating) & (d["members"] >= min_members)]
    cols = ["rating", "members"] if sort == "Rating" else ["members", "rating"]
    return list(d.sort_values(cols, ascending=False)["name"])


def _more(step):
    st.session_state["pg_n"] = st.session_state.get("pg_n", step) + step


def paged_grid(names, sig, prefix, ncols=5, step=10):
    if st.session_state.get("pg_sig") != sig:
        st.session_state["pg_sig"] = sig
        st.session_state["pg_n"] = step
    n = st.session_state.get("pg_n", step)
    st.caption(f"{len(names)} anime mile")
    if not names:
        st.info("Is filter se kuch nahi mila. Rating kam karo ya genre badlo.")
        return
    render_grid(names[:n], ncols, prefix=prefix)
    if n < len(names):
        st.button("Show more ⬇️", key=f"more_{prefix}", on_click=_more, args=(step,))


def _pick_random(cat):
    g = st.session_state.get("r_genre", "Any")
    pool = filter_catalog(cat, [] if g == "Any" else [g], min_rating=6.5, min_members=10000)
    st.session_state["rand_names"] = random.sample(pool, min(5, len(pool)))


def page_surprise(cat):
    genres = ["Any"] + sorted({g for gs in cat["genres"] for g in gs})
    st.selectbox("Genre", genres, key="r_genre")
    st.button("🎲 Surprise me!", key="rand_go", on_click=_pick_random, args=(cat,))
    names = st.session_state.get("rand_names")
    if names:
        render_grid(names, 5, prefix="rand")
    else:
        st.info("Button dabao, app tumhare liye 5 achhe anime chun dega.")


# ---------------------------------------------------------------
# New pages: Series, Movies, languages, Anime TV mode
# ---------------------------------------------------------------
LANG_TERMS = {
    "🇮🇳 Hindi": "Hindi dubbed",
    "🇮🇳 Tamil": "Tamil dubbed",
    "🇮🇳 Telugu": "Telugu dubbed",
    "💬 Hindi Sub": "Hindi subbed",
    "🇬🇧 English": "English dubbed",
    "🇯🇵 Japanese": "Japanese original",
}


def page_type(cat, typ, kind):
    genres = sorted({g for gs in cat["genres"] for g in gs})
    c1, c2 = st.columns([3, 2])
    pick = c1.multiselect("Genre", genres, key=f"{kind}_genres")
    min_r = c2.slider("Min rating", 0.0, 9.0, 0.0, 0.5, key=f"{kind}_minr")
    sort = st.radio("Sort by", ["Rating", "Popularity"], horizontal=True, key=f"{kind}_sort")
    names = filter_catalog(cat, genres=pick, typ=typ, min_rating=min_r,
                           sort=sort, min_members=5000)
    paged_grid(names, (kind, sort, tuple(pick), min_r), kind)


def page_lang(cat, nav):
    term = LANG_TERMS[nav]
    st.caption(f"Card ke buttons '{term}' search karenge")
    st.session_state["card_lang"] = term
    names = filter_catalog(cat, min_rating=6.5, sort="Popularity", min_members=20000)
    paged_grid(names, ("lang", term), "lang_" + term.replace(" ", "_"))
    st.session_state["card_lang"] = None


def _tv_shuffle(cat):
    pool = filter_catalog(cat, min_rating=7.0, sort="Popularity", min_members=50000)
    random.shuffle(pool)
    st.session_state["tv_list"] = pool
    st.session_state["tv_i"] = 0


def _tv_step(step):
    n = len(st.session_state.get("tv_list", [])) or 1
    st.session_state["tv_i"] = (st.session_state.get("tv_i", 0) + step) % n


def page_tv(cat):
    if "tv_list" not in st.session_state:
        _tv_shuffle(cat)
    names = st.session_state["tv_list"]
    if not names:
        st.info("TV mode ke liye koi anime nahi mila.")
        return
    name = names[st.session_state["tv_i"] % len(names)]
    record_history(name)
    info = fetch_info(name)

    left, right = st.columns([1, 2], vertical_alignment="center")
    with left:
        st.markdown(card_html(name, info), unsafe_allow_html=True)
    with right:
        st.markdown(f"### {unescape(name)}")
        st.caption(f"Now playing {st.session_state['tv_i'] + 1} / {len(names)}")
        st.write((info.get("synopsis") or "")[:600])
        b1, b2, b3 = st.columns(3)
        b1.button("⏮ Prev", key="tv_prev", on_click=_tv_step, args=(-1,))
        b2.button("⏭ Skip", key="tv_skip", on_click=_tv_step, args=(1,))
        b3.button("🔀 Shuffle", key="tv_shuf", on_click=_tv_shuffle, args=(cat,))
        auto = st.checkbox("Auto-play (apne aap agla anime)", key="tv_auto")
        secs = st.slider("Seconds", 5, 60, 15, key="tv_secs")
    if auto:
        # Let the browser schedule the next click; never block Streamlit with time.sleep().
        import streamlit.components.v1 as components
        components.html(
            f"""<script>
            (function () {{
                const delay = {int(secs) * 1000};
                window.setTimeout(function () {{
                    try {{
                        const doc = window.parent.document;
                        const wrapper = doc.querySelector('.st-key-tv_skip');
                        const button = wrapper ? wrapper.querySelector('button') : null;
                        if (button) button.click();
                    }} catch (e) {{ /* Auto-play is optional; keep the app usable. */ }}
                }}, delay);
            }})();
            </script>""",
            height=0,
        )


def page_cartoons():
    st.caption("Episodes aur Movies ke buttons YouTube par search kholte hain. "
               "Jo official channel ya service par available hoga wahi dikhega.")
    names = [c["name"] for c in CARTOONS]
    st.caption(f"{len(names)} cartoons")
    render_grid(names, 5, prefix="cartoon_all")

    with st.expander("Poster sources (debug)"):
        for _n in names:
            _c = CARTOON_MAP[_n]
            if _c.get("fetch"):
                st.write(f"{_n}: AniList")
            else:
                _e = store["data"].get("cartoon2:" + _n)
                _src = (_e or {}).get("info", {}).get("source", "loading...")
                _ok = "picture ✅" if (_e or {}).get("ok") else "no picture ❌"
                st.write(f"{_n}: {_src} — {_ok}")


# ---------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------
if "nav" not in st.session_state:
    st.session_state["nav"] = "🏠 Home"


def zigzag(text, color):
    """Letters alternate up / down (zig-zag) in one colour."""
    out = []
    for i, ch in enumerate(text):
        c = "&nbsp;" if ch == " " else escape(ch)
        dy, rot = (-4, -5) if i % 2 == 0 else (4, 5)
        out.append(f"<span style='display:inline-block;transform:translateY({dy}px) rotate({rot}deg);'>{c}</span>")
    return (f"<span style='color:{color};font-weight:800;letter-spacing:1px;"
            f"text-shadow:0 0 12px {color}66;'>{''.join(out)}</span>")


def go(page):
    st.session_state["nav"] = page
    st.session_state["close_pop"] = True


# ---------------------------------------------------------------
# Accounts (stored only on this computer, passwords are hashed)
# ---------------------------------------------------------------
USERS_FILE = os.path.join(BASE_DIR, "users.json")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False)
        return True
    except Exception:
        return False


def _hash_pw(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 200_000).hex()


def _hash_recovery(code, salt):
    return hashlib.pbkdf2_hmac("sha256", code.strip().upper().encode("utf-8"),
                               bytes.fromhex(salt), 200_000).hex()


def _auth_msg(kind, text):
    st.session_state["auth_msg"] = (kind, text)


def create_account():
    ss = st.session_state
    username = ss.get("ca_user", "").strip()
    email = ss.get("ca_email", "").strip().lower()
    pw = ss.get("ca_pw", "")
    pw2 = ss.get("ca_pw2", "")
    if not USERNAME_RE.match(username):
        return _auth_msg("error", "Username 3-20 characters ka ho (letters, numbers, _ ya . hi).")
    if not EMAIL_RE.match(email):
        return _auth_msg("error", "Sahi email daalo.")
    if len(pw) < 6:
        return _auth_msg("error", "Password kam se kam 6 characters ka ho.")
    if pw != pw2:
        return _auth_msg("error", "Dono password match nahi karte.")
    users = _load_users()
    if username.lower() in users:
        return _auth_msg("error", "Ye username pehle se liya hua hai.")
    if any(u.get("email") == email for u in users.values()):
        return _auth_msg("error", "Is email se account pehle se bana hai.")
    salt = secrets.token_hex(16)
    recovery_salt = secrets.token_hex(16)
    recovery_code = secrets.token_urlsafe(9).upper()
    users[username.lower()] = {
        "username": username, "email": email,
        "salt": salt, "hash": _hash_pw(pw, salt),
        "recovery_salt": recovery_salt,
        "recovery_hash": _hash_recovery(recovery_code, recovery_salt),
    }
    if not _save_users(users):
        return _auth_msg("error", "Account save nahi ho paya. Folder ki permission check karo.")
    ss["recovery_notice"] = recovery_code
    ss["user"] = username
    ss["favs"] = _load_favs()
    ss["hist"] = _load_hist()
    ss.pop("_tr", None)
    ss.pop("_tr_owner", None)
    _save_settings()
    _auth_msg("success", f"Account ban gaya. Welcome, {username}!")


def sign_in():
    ss = st.session_state
    ident = ss.get("si_id", "").strip()
    pw = ss.get("si_pw", "")
    users = _load_users()
    rec = None
    if "@" in ident:
        rec = next((u for u in users.values() if u.get("email") == ident.lower()), None)
    else:
        rec = users.get(ident.lower())
    ok = False
    if rec:
        try:
            ok = hmac.compare_digest(_hash_pw(pw, rec["salt"]), rec["hash"])
        except Exception:
            ok = False
    if not ok:
        return _auth_msg("error", "Username/email ya password galat hai.")
    ss["user"] = rec["username"]
    ss["favs"] = _load_favs()
    ss["hist"] = _load_hist()
    ss.pop("_tr", None)
    ss.pop("_tr_owner", None)
    _save_settings()
    _auth_msg("success", f"Welcome back, {rec['username']}!")


def reset_password():
    ss = st.session_state
    if time.time() < ss.get("fp_lock", 0):
        return _auth_msg("error", "Bahut zyada galat koshish. Thodi der baad dobara try karo.")
    username = ss.get("fp_user", "").strip()
    email = ss.get("fp_email", "").strip().lower()
    pw = ss.get("fp_pw", "")
    pw2 = ss.get("fp_pw2", "")
    recovery_code = ss.get("fp_recovery", "").strip()
    if len(pw) < 6:
        return _auth_msg("error", "Naya password kam se kam 6 characters ka ho.")
    if pw != pw2:
        return _auth_msg("error", "Dono password match nahi karte.")
    users = _load_users()
    rec = users.get(username.lower())
    valid_identity = bool(rec and rec.get("email") == email)
    recovery_salt = (rec or {}).get("recovery_salt")
    recovery_hash = (rec or {}).get("recovery_hash")
    valid_recovery = False
    if valid_identity and recovery_salt and recovery_hash and recovery_code:
        valid_recovery = hmac.compare_digest(_hash_recovery(recovery_code, recovery_salt), recovery_hash)
    if not valid_identity or not valid_recovery:
        ss["fp_fails"] = ss.get("fp_fails", 0) + 1
        if ss["fp_fails"] >= 5:
            ss["fp_lock"] = time.time() + 60
            ss["fp_fails"] = 0
        if valid_identity and not recovery_hash:
            return _auth_msg("error", "Is purane account ka recovery key set nahi hai. Account owner ko local admin se contact karna hoga.")
        return _auth_msg("error", "Username, email ya recovery key galat hai.")
    salt = secrets.token_hex(16)
    rec["salt"] = salt
    rec["hash"] = _hash_pw(pw, salt)
    users[username.lower()] = rec
    if not _save_users(users):
        return _auth_msg("error", "Password save nahi ho paya. Folder ki permission check karo.")
    ss["fp_fails"] = 0
    _auth_msg("success", "Password badal gaya. Ab naye password se Sign in karo.")


def sign_out():
    st.session_state["user"] = ""
    st.session_state["favs"] = _load_favs()
    st.session_state["hist"] = _load_hist()
    st.session_state.pop("_tr", None)
    st.session_state.pop("_tr_owner", None)
    _save_settings()


def search_go():
    st.session_state["nav"] = "🏠 Home"
    st.session_state["close_pop"] = True
    record_history(st.session_state.get("search_pick"))


def go_home():
    st.session_state["nav"] = "🏠 Home"
    st.session_state["search_pick"] = None
    st.session_state["close_pop"] = True


# ---------------------------------------------------------------
# Upcoming anime: release schedule (AniList) shown in Settings
# ---------------------------------------------------------------
SCHEDULE_QUERY = """
query ($from: Int, $to: Int, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    airingSchedules(airingAt_greater: $from, airingAt_lesser: $to, sort: TIME) {
      airingAt episode
      media {
        siteUrl format isAdult countryOfOrigin popularity
        title { romaji english }
      }
    }
  }
}
"""

UPCOMING_QUERY = """
query ($page: Int) {
  Page(page: $page, perPage: 30) {
    media(type: ANIME, status: NOT_YET_RELEASED, isAdult: false, sort: POPULARITY_DESC) {
      siteUrl format season seasonYear
      startDate { year month day }
      title { romaji english }
      coverImage { medium }
      nextAiringEpisode { airingAt episode }
    }
  }
}
"""


def _anilist_post(query, variables, timeout=10, tries=2):
    for _ in range(tries):
        try:
            r = requests.post("https://graphql.anilist.co",
                              json={"query": query, "variables": variables}, timeout=timeout)
        except requests.RequestException:
            continue
        if r.status_code == 429:
            time.sleep(2)
            continue
        if r.status_code != 200:
            return None
        return r.json().get("data")
    return None


@st.cache_data(ttl=1800, show_spinner="Release schedule load ho raha hai...")
def load_schedule():
    now = int(time.time())
    end = now + 7 * 86400
    out = []
    for page in range(1, 5):
        data = _anilist_post(SCHEDULE_QUERY, {"from": now, "to": end, "page": page})
        if not data:
            return out or None
        pg = data.get("Page") or {}
        for it in pg.get("airingSchedules") or []:
            m = it.get("media") or {}
            if m.get("isAdult") or m.get("countryOfOrigin") != "JP":
                continue
            if (m.get("popularity") or 0) < 3000:
                continue
            t = m.get("title") or {}
            out.append({
                "at": it["airingAt"], "ep": it["episode"],
                "title": t.get("english") or t.get("romaji") or "Unknown",
                "url": m.get("siteUrl"),
            })
        if not (pg.get("pageInfo") or {}).get("hasNextPage"):
            break
    return out


@st.cache_data(ttl=3600, show_spinner="Upcoming anime load ho rahe hain...")
def load_upcoming():
    data = _anilist_post(UPCOMING_QUERY, {"page": 1})
    if not data:
        return None
    out = []
    for m in (data.get("Page") or {}).get("media") or []:
        t = m.get("title") or {}
        sd = m.get("startDate") or {}
        nxt = m.get("nextAiringEpisode") or {}
        out.append({
            "title": t.get("english") or t.get("romaji") or "Unknown",
            "url": m.get("siteUrl"),
            "poster": (m.get("coverImage") or {}).get("medium"),
            "format": m.get("format"),
            "season": m.get("season"), "season_year": m.get("seasonYear"),
            "y": sd.get("year"), "m": sd.get("month"), "d": sd.get("day"),
            "next_at": nxt.get("airingAt"), "next_ep": nxt.get("episode"),
        })
    return out


def _date_label(ts):
    d = datetime.fromtimestamp(ts).date()
    today = datetime.now().date()
    diff = (d - today).days
    if diff == 0:
        return "Today · " + d.strftime("%a %d %b")
    if diff == 1:
        return "Tomorrow · " + d.strftime("%a %d %b")
    return d.strftime("%A · %d %b")


def _upcoming_when(a):
    """(sort key, 'date time' text) for an upcoming anime"""
    if a.get("next_at"):
        dt = datetime.fromtimestamp(a["next_at"])
        return (a["next_at"], dt.strftime("%d %b %Y, %I:%M %p") + f" · Ep {a['next_ep']}")
    y, m, d = a.get("y"), a.get("m"), a.get("d")
    if y and m and d:
        return (datetime(y, m, d).timestamp(), datetime(y, m, d).strftime("%d %b %Y") + " · time TBA")
    if y and m:
        return (datetime(y, m, 28).timestamp(), datetime(y, m, 1).strftime("%b %Y") + " · date TBA")
    if a.get("season") and a.get("season_year"):
        return (9e9 - 1, f"{str(a['season']).title()} {a['season_year']} · date TBA")
    if y:
        return (9e9 - 1, f"{y} · date TBA")
    return (9e9, "TBA")


def _row_title(title, url):
    t = escape(title)
    if url:
        return (f"<a href='{escape(url, quote=True)}' target='_blank' rel='noopener noreferrer' "
                f"style='color:#ffffff;text-decoration:none;font-weight:600'>{t}</a>")
    return f"<span style='font-weight:600'>{t}</span>"


def page_upcoming():
    st.markdown("##### 📅 Upcoming anime")
    st.caption("Release date aur time tumhare computer ke time (local time) mein dikhte hain. "
               "Data AniList se aata hai aur har 30 minute mein refresh hota hai.")
    st.button("🔄 Refresh", key="up_refresh", on_click=lambda: st.cache_data.clear())

    tab1, tab2 = st.tabs(["Is hafte ke episodes", "Aane wale naye anime"])

    with tab1:
        sched = load_schedule()
        if sched is None:
            st.warning("Schedule load nahi ho paya. Internet check karo aur Refresh dabao.")
        else:
            now = time.time()
            sched = [x for x in sched if x["at"] >= now - 60]
            if not sched:
                st.info("Agle 7 din ke liye koi episode nahi mila.")
            days = {}
            for x in sorted(sched, key=lambda z: z["at"]):
                days.setdefault(datetime.fromtimestamp(x["at"]).date(), []).append(x)
            for i, (day, items) in enumerate(days.items()):
                with st.expander(f"{_date_label(items[0]['at'])}  ({len(items)})", expanded=(i == 0)):
                    rows = ""
                    for x in items:
                        when = datetime.fromtimestamp(x["at"]).strftime("%I:%M %p")
                        rows += (
                            "<div style='display:flex;gap:12px;align-items:center;padding:6px 0;"
                            "border-bottom:1px solid rgba(255,255,255,.08);font-size:13px;'>"
                            f"<span style='min-width:78px;font-weight:700;color:#2ee59d'>{when}</span>"
                            f"<span style='flex:1;min-width:0'>{_row_title(x['title'], x['url'])}</span>"
                            f"<span style='color:#9a97b8;white-space:nowrap'>Ep {x['ep']} · in {_countdown(x['at'])}</span>"
                            "</div>"
                        )
                    st.markdown(rows, unsafe_allow_html=True)

    with tab2:
        ups = load_upcoming()
        if ups is None:
            st.warning("Upcoming list load nahi ho payi. Internet check karo aur Refresh dabao.")
        elif not ups:
            st.info("Abhi koi upcoming anime nahi mila.")
        else:
            st.caption("Exact time tabhi dikhta hai jab episode ka schedule publish ho chuka ho. "
                       "Warna sirf date ya season dikhta hai.")
            rows = ""
            for a in sorted(ups, key=lambda z: _upcoming_when(z)[0]):
                _, text = _upcoming_when(a)
                img = (f"<img src='{escape(a['poster'], quote=True)}' "
                       "style='width:38px;height:54px;object-fit:cover;border-radius:6px'>"
                       if a.get("poster") else "")
                fmt = f" · {escape(str(a['format']).replace('_', ' '))}" if a.get("format") else ""
                rows += (
                    "<div style='display:flex;gap:12px;align-items:center;padding:6px 0;"
                    "border-bottom:1px solid rgba(255,255,255,.08);font-size:13px;'>"
                    f"{img}<div style='flex:1;min-width:0'>{_row_title(a['title'], a['url'])}"
                    f"<div style='color:#9a97b8;font-size:11.5px'>{escape(text)}{fmt}</div></div></div>"
                )
            st.markdown(rows, unsafe_allow_html=True)


# ---------------------------------------------------------------
# Home hero: 5 currently airing anime, auto-advancing every 3 seconds
# ---------------------------------------------------------------
CAROUSEL_QUERY = """
query {
  Page(page: 1, perPage: 15) {
    media(type: ANIME, status: RELEASING, sort: TRENDING_DESC, isAdult: false, countryOfOrigin: JP) {
      siteUrl format episodes averageScore genres bannerImage
      description(asHtml: false)
      title { romaji english }
      coverImage { extraLarge large }
      nextAiringEpisode { episode airingAt }
    }
  }
}
"""

CAROUSEL_HTML = """
<style>
  html, body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', Arial, sans-serif; }
  #car { position: relative; height: 280px; border-radius: 14px; overflow: hidden; background: #1a1829;
         box-shadow: 0 6px 22px rgba(0,0,0,.5); }
  #track { display: flex; height: 100%; overflow-x: auto; scroll-snap-type: x mandatory;
           scrollbar-width: none; cursor: grab; }
  #track::-webkit-scrollbar { display: none; }
  .slide { position: relative; flex: 0 0 100%; height: 100%; scroll-snap-align: start; overflow: hidden; }
  .bg { position: absolute; inset: 0; background-size: cover; background-position: center; }
  .bg.plain { background: linear-gradient(135deg, #1a1829, #0b0a12); }
  .shade { position: absolute; inset: 0;
           background: linear-gradient(90deg, rgba(11,10,18,.95) 0%, rgba(11,10,18,.78) 45%, rgba(11,10,18,.15) 100%); }
  .content { position: absolute; inset: 0; display: flex; align-items: center; gap: 22px; padding: 0 64px; }
  .poster { height: 210px; aspect-ratio: 2 / 3; object-fit: cover; border-radius: 10px;
            box-shadow: 0 6px 18px rgba(0,0,0,.6); flex: 0 0 auto; user-select: none; -webkit-user-drag: none; }
  .pw { position: relative; flex: 0 0 auto; }
  .hb { position:absolute; top:6px; right:6px; width:28px; height:28px; padding:0; border-radius:50%; border:1px solid rgba(255,255,255,.4); background:rgba(11,10,18,.72); color:#fff; font-size:14px; line-height:1; cursor:pointer; z-index:6; display:flex; align-items:center; justify-content:center; transition:transform .2s,background .2s }
  .hb:hover { transform:scale(1.15); background:rgba(255,42,117,.55) }
  
  .txt { min-width: 0; max-width: 640px; color: #fff; }
  .tag { display: inline-block; font-size: 11px; font-weight: 700; color: #2ee59d; border: 1px solid #2ee59d;
         border-radius: 999px; padding: 2px 10px; margin-bottom: 8px; }
  .title { font-size: 26px; font-weight: 800; line-height: 1.15; margin-bottom: 6px;
           display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .meta { font-size: 12.5px; color: #ffb703; font-weight: 600; margin-bottom: 4px; }
  .next { font-size: 12.5px; color: #2ee59d; font-weight: 700; margin-bottom: 8px; min-height: 16px; }
  .syn { font-size: 12.5px; line-height: 1.45; color: #d6d4ea; margin-bottom: 12px;
         display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
  .b { display: inline-block; font-size: 12px; font-weight: 700; padding: 6px 14px; border-radius: 8px;
       background: #ff2a75; color: #fff; text-decoration: none; margin-right: 8px; }
  .b.alt { background: rgba(255,255,255,.16); }
  .b:hover { filter: brightness(1.15); }
  .nav { position: absolute; top: 50%; transform: translateY(-50%); width: 38px; height: 38px; border-radius: 50%;
         border: 1px solid rgba(255,255,255,.5); background: rgba(11,10,18,.8); padding: 0; cursor: pointer; z-index: 5;
         display: flex; align-items: center; justify-content: center; }
  .nav svg { width: 18px; height: 18px; stroke: #ffffff; fill: none; stroke-width: 3;
             stroke-linecap: round; stroke-linejoin: round; pointer-events: none; }
  .nav:hover { background: rgba(255,42,117,.45); }
  .nav.prev { left: 12px; } .nav.next { right: 12px; }
  #dots { position: absolute; bottom: 10px; left: 0; right: 0; display: flex; justify-content: center; gap: 7px; z-index: 5; }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,.35); cursor: pointer; transition: all .25s; }
  .dot.on { background: #ff2a75; width: 22px; border-radius: 999px; }
  .fade { animation: fadein .6s ease; }
  @keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
  @media (max-width: 640px) { .pw, .poster { display: none; } .content { padding: 0 52px; } .title { font-size: 21px; } }
</style>
<div id="car">
  <div id="track">__SLIDES__</div>
  <button class="nav prev" id="prev" aria-label="Previous"><svg viewBox="0 0 24 24"><polyline points="15 5 8 12 15 19"/></svg></button>
  <button class="nav next" id="next" aria-label="Next"><svg viewBox="0 0 24 24"><polyline points="9 5 16 12 9 19"/></svg></button>
  <div id="dots"></div>
</div>
<script>
function favToggle(p,i,ev){ev.preventDefault();ev.stopPropagation();try{var b=window.parent.document.querySelector('.st-key-favrow_'+p+'_'+i+' button');if(b)b.click();}catch(e){}return false;}
</script>
<script>
(function () {
  var track = document.getElementById('track');
  var slides = Array.prototype.slice.call(track.children);
  var n = slides.length;
  var dotsEl = document.getElementById('dots');
  var i = 0, timer = null, autoMove = false, dragging = false;
  var DELAY = 3000;

  slides.forEach(function (_, k) {
    var d = document.createElement('div');
    d.className = 'dot';
    d.onclick = function () { go(k); restart(); };
    dotsEl.appendChild(d);
  });

  function setDots() {
    Array.prototype.forEach.call(dotsEl.children, function (d, k) {
      d.className = 'dot' + (k === i ? ' on' : '');
    });
  }

  function go(k, instant) {
    var wrapped = (k >= n) || (k < 0);
    i = (k + n) % n;
    autoMove = true;
    track.style.scrollSnapType = 'none';
    track.scrollTo({ left: i * track.clientWidth, behavior: (instant || wrapped) ? 'auto' : 'smooth' });
    if (wrapped) { slides[i].classList.remove('fade'); void slides[i].offsetWidth; slides[i].classList.add('fade'); }
    setTimeout(function () { autoMove = false; track.style.scrollSnapType = 'x mandatory'; }, 700);
    setDots();
  }

  function restart() {
    clearInterval(timer);
    timer = setInterval(function () { go(i + 1); }, DELAY);
  }

  // user scrolling / swiping: show the slide they landed on, then keep auto-playing 3s later
  var settle = null;
  track.addEventListener('scroll', function () {
    if (autoMove) return;
    var k = Math.round(track.scrollLeft / track.clientWidth);
    if (k !== i && k >= 0 && k < n) { i = k; setDots(); }
    clearInterval(timer);
    clearTimeout(settle);
    settle = setTimeout(restart, 400);
  });

  // mouse drag (touch uses native swipe)
  var startX = 0, startLeft = 0;
  track.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'mouse' || e.target.closest('a, button')) return;
    dragging = true; startX = e.clientX; startLeft = track.scrollLeft;
    track.style.scrollSnapType = 'none'; track.style.cursor = 'grabbing'; clearInterval(timer);
  });
  window.addEventListener('pointermove', function (e) {
    if (dragging) track.scrollLeft = startLeft - (e.clientX - startX);
  });
  window.addEventListener('pointerup', function (e) {
    if (!dragging) return;
    dragging = false; track.style.cursor = 'grab';
    var dx = e.clientX - startX;
    var k = i;
    if (dx < -50) k = Math.min(i + 1, n - 1); else if (dx > 50) k = Math.max(i - 1, 0);
    go(k); restart();
  });

  document.getElementById('prev').onclick = function () { go(i - 1); restart(); };
  document.getElementById('next').onclick = function () { go(i + 1); restart(); };
  window.addEventListener('resize', function () { go(i, true); });

  // live countdown to the next episode
  function tick() {
    document.querySelectorAll('.next').forEach(function (el) {
      var ts = parseInt(el.getAttribute('data-ts'), 10);
      if (!ts) { el.textContent = ''; return; }
      var s = ts - Math.floor(Date.now() / 1000);
      var ep = el.getAttribute('data-ep');
      if (s <= 0) { el.textContent = 'Ep ' + ep + ' airing now'; return; }
      var d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60);
      el.textContent = '\\u23F3 Ep ' + ep + ' in ' + (d ? d + 'd ' + h + 'h' : (h ? h + 'h ' + m + 'm' : m + 'm'));
    });
  }
  tick(); setInterval(tick, 30000);

  setDots();
  restart();
})();
</script>
"""


@st.cache_data(ttl=1800, show_spinner=False)
def load_current_anime():
    data = _anilist_post(CAROUSEL_QUERY, {}, timeout=5, tries=1)
    if not data:
        raise RuntimeError("AniList unavailable")          # errors are not cached
    items = []
    for m in (data.get("Page") or {}).get("media") or []:
        cov = m.get("coverImage") or {}
        cover = cov.get("extraLarge") or cov.get("large")
        if not cover:
            continue
        t = m.get("title") or {}
        nxt = m.get("nextAiringEpisode") or {}
        desc = re.sub(r"<[^>]+>", " ", m.get("description") or "")
        desc = re.sub(r"\s+", " ", unescape(desc)).strip()
        items.append({
            "title": t.get("english") or t.get("romaji") or "Unknown",
            "url": m.get("siteUrl"),
            "cover": cover,
            "banner": m.get("bannerImage"),
            "score": round(m["averageScore"] / 10, 1) if m.get("averageScore") else None,
            "format": m.get("format"),
            "episodes": m.get("episodes"),
            "genres": (m.get("genres") or [])[:3],
            "syn": desc[:190] + ("..." if len(desc) > 190 else ""),
            "next_ep": nxt.get("episode"),
            "next_at": nxt.get("airingAt"),
        })
    # real banner pictures first, then ones with a next episode (stable sort)
    items.sort(key=lambda a: (0 if a["banner"] else 1, 0 if a["next_at"] else 1))
    return items[:5]


def current_carousel():
    import streamlit.components.v1 as components
    if time.time() < store.get("car_fail_until", 0):
        return                                    # AniList failed recently: skip for 2 minutes
    try:
        items = load_current_anime()
    except Exception:
        store["car_fail_until"] = time.time() + 120
        return
    if not items:
        return
    favs = st.session_state["favs"]
    fav_buttons("car", [a["title"] for a in items])
    slides = ""
    for rank, a in enumerate(items, 1):
        if a["banner"]:
            bg_html = (f"<div class='bg' style=\"background-image:url('{escape(a['banner'], quote=True)}')\"></div>")
        else:
            bg_html = "<div class='bg plain'></div>"
        meta = []
        if a["score"]:
            meta.append(f"★ {a['score']}")
        if a["format"]:
            meta.append(str(a["format"]).replace("_", " "))
        meta.append(f"{a['episodes']} eps" if a["episodes"] else "ongoing")
        meta.extend(a["genres"])
        q = urllib.parse.quote(a["title"])
        info = (f"<a class='b' href='{escape(a['url'], quote=True)}' target='_blank' rel='noopener noreferrer'>Info</a>"
                if a["url"] else "")
        slides += (
            "<div class='slide'>"
            f"{bg_html}"
            "<div class='shade'></div><div class='content'>"
            f"<div class='pw'><img class='poster' src='{escape(a['cover'], quote=True)}' alt=''>"
            f"{_heart_btn('car', rank - 1, a['title'] in favs)}</div>"
            "<div class='txt'>"
            f"<div class='tag'>🔥 Airing now · {rank}/{len(items)}</div>"
            f"<div class='title'>{escape(a['title'])}</div>"
            f"<div class='meta'>{escape(' · '.join(meta))}</div>"
            f"<div class='next' data-ts='{a['next_at'] or ''}' data-ep='{a['next_ep'] or ''}'></div>"
            f"<div class='syn'>{escape(a['syn'])}</div>"
            f"{info}<a class='b alt' href='https://www.crunchyroll.com/search?q={q}' "
            "target='_blank' rel='noopener noreferrer'>▶ Watch</a>"
            "</div></div></div>"
        )
    components.html(CAROUSEL_HTML.replace("__SLIDES__", slides), height=296)


# ---------------------------------------------------------------
# Home rows: sliding lists (history, top 10, new, top rated) + "View all"
# ---------------------------------------------------------------
SECTIONS = {
    "top_series_today": {"title": "🔥 Top 10 Series Today", "ranked": True, "n": 10,
                         "args": 'sort: TRENDING_DESC, format: TV, status_not: NOT_YET_RELEASED'},
    "new_series": {"title": "🆕 New Series", "ranked": False, "n": 15,
                   "args": 'sort: START_DATE_DESC, format: TV, status: RELEASING, popularity_greater: 3000'},
    "new_movies": {"title": "🎬 New Movies", "ranked": False, "n": 15,
                   "args": 'sort: START_DATE_DESC, format: MOVIE, status_not: NOT_YET_RELEASED, popularity_greater: 1500'},
    "top_movies_today": {"title": "🔥 Top 10 Movies Today", "ranked": True, "n": 10,
                         "args": 'sort: TRENDING_DESC, format: MOVIE, status_not: NOT_YET_RELEASED'},
    "top_series_all": {"title": "🏆 Top 10 Series Of All Time", "ranked": True, "n": 10,
                       "args": 'sort: SCORE_DESC, format: TV, popularity_greater: 100000'},
    "top_rated": {"title": "⭐ Top Rated", "ranked": False, "n": 15,
                  "args": 'sort: SCORE_DESC, popularity_greater: 100000'},
}
HISTORY_TITLE = "🕘 Watching History"

SECTION_QUERY = """
query {
  Page(page: 1, perPage: 50) {
    media(type: ANIME, isAdult: false, countryOfOrigin: JP, %s) {
      siteUrl format episodes averageScore status seasonYear
      title { romaji english }
      coverImage { extraLarge large }
      nextAiringEpisode { episode airingAt }
    }
  }
}
"""


def _latest_line(episodes, next_ep, fmt, nxt_at=None):
    if next_ep:
        txt = f"Latest: Ep {next_ep - 1}" if next_ep > 1 else "Starts soon"
        if nxt_at:
            txt += f" · next {_countdown(nxt_at)}"
        return txt
    if fmt == "MOVIE":
        return "Movie"
    if episodes:
        return f"{episodes} eps"
    return ""


@st.cache_data(ttl=1800, show_spinner=False)
def load_section(key):
    data = _anilist_post(SECTION_QUERY % SECTIONS[key]["args"], {}, timeout=8, tries=2)
    if not data:
        raise RuntimeError("AniList unavailable")          # errors are not cached
    items = []
    for m in (data.get("Page") or {}).get("media") or []:
        cov = m.get("coverImage") or {}
        poster = cov.get("extraLarge") or cov.get("large")
        if not poster:
            continue
        t = m.get("title") or {}
        nxt = m.get("nextAiringEpisode") or {}
        sc = m.get("averageScore")
        items.append({
            "title": t.get("english") or t.get("romaji") or "Unknown",
            "url": m.get("siteUrl"), "poster": poster,
            "score": round(sc / 10, 1) if sc else None,
            "line": _latest_line(m.get("episodes"), nxt.get("episode"), m.get("format"), nxt.get("airingAt")),
        })
    if not items:
        raise RuntimeError("empty")
    return items


def history_items():
    out = []
    for name in st.session_state.get("hist", []):
        info = fetch_info(name)
        nm = unescape(name)
        sc = info.get("score")
        out.append({
            "title": nm,
            "url": info.get("url") or ("https://www.crunchyroll.com/search?q=" + urllib.parse.quote(nm)),
            "poster": info.get("poster") or PLACEHOLDER,
            "score": sc if isinstance(sc, (int, float)) else None,
            "line": _latest_line(info.get("episodes"), info.get("next_ep"), info.get("format"), info.get("next_at")),
        })
    return out


def safe_section(key):
    if time.time() < store.get("sec_fail_until", 0):
        return None
    try:
        return load_section(key)
    except Exception:
        store["sec_fail_until"] = time.time() + 60
        return None


SLIDER_HTML = """
<style>
html,body{margin:0;background:transparent;font-family:'Source Sans Pro',system-ui,sans-serif;color:#fff}
.wrap{position:relative}
.track{display:flex;gap:14px;overflow-x:auto;scroll-behavior:smooth;scroll-snap-type:x proximity;padding:4px 2px 10px;scrollbar-width:thin;scrollbar-color:#3a3658 transparent}
.it{flex:0 0 150px;width:150px;min-width:0;scroll-snap-align:start;text-decoration:none;color:#fff;display:block}
.p{position:relative;width:150px;height:225px;border-radius:10px;overflow:hidden;background:#1a1829;box-shadow:0 6px 16px rgba(0,0,0,.45);transition:transform .25s ease,box-shadow .25s ease}
.p img{width:100%;height:100%;object-fit:cover;display:block}
.it:hover .p{transform:translateY(-4px) scale(1.03);box-shadow:0 12px 24px rgba(255,42,117,.30)}
.rk{position:absolute;left:6px;top:6px;background:#ff2a75;color:#fff;font-weight:800;font-size:12px;padding:2px 8px;border-radius:999px}
.t{font-size:12.5px;font-weight:700;margin-top:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.s{font-size:12px;font-weight:700;color:#ffb703;height:16px}
.l{font-size:11px;color:#2ee59d;font-weight:600;height:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ar{position:absolute;top:92px;width:34px;height:34px;border-radius:50%;border:1px solid rgba(255,255,255,.4);background:rgba(11,10,18,.85);color:#fff;font-size:18px;cursor:pointer;z-index:5;display:flex;align-items:center;justify-content:center}
.ar:hover{background:#ff2a75;border-color:#ff2a75}
.ar.l1{left:-4px}.ar.r1{right:-4px}
.hb{position:absolute;top:6px;right:6px;width:28px;height:28px;padding:0;border-radius:50%;border:1px solid rgba(255,255,255,.4);background:rgba(11,10,18,.72);color:#fff;font-size:14px;line-height:1;cursor:pointer;z-index:6;display:flex;align-items:center;justify-content:center;transition:transform .2s,background .2s}.hb:hover{transform:scale(1.15);background:rgba(255,42,117,.55)}
</style>
<div class="wrap">
<button class="ar l1" onclick="go(-1)">&#8249;</button>
<div class="track" id="tr">__ITEMS__</div>
<button class="ar r1" onclick="go(1)">&#8250;</button>
</div>
<script>
function go(d){var t=document.getElementById('tr');t.scrollBy({left:d*t.clientWidth*0.8,behavior:'smooth'});}
function favToggle(p,i,ev){ev.preventDefault();ev.stopPropagation();try{var b=window.parent.document.querySelector('.st-key-favrow_'+p+'_'+i+' button');if(b)b.click();}catch(e){}return false;}
</script>
"""


def fav_buttons(prefix, titles):
    """Hidden Streamlit buttons; the heart inside the HTML cards clicks them (see favToggle)."""
    for i, t in enumerate(titles):
        st.button("fav", key=f"favrow_{prefix}_{i}", on_click=toggle_fav, args=(t,))


def _heart_btn(prefix, idx, is_fav):
    return (f"<button class='hb' type='button' title='Favorite' "
            f"onclick=\"favToggle('{prefix}',{idx},event)\">{'❤️' if is_fav else '🤍'}</button>")


def _item_html(it, rank=None, prefix="", idx=0, fav=False):
    badge = f"<span class='rk'>#{rank}</span>" if rank else ""
    heart = _heart_btn(prefix, idx, fav)
    score = f"★ {it['score']}" if it.get("score") else "&nbsp;"
    return (f"<a class='it' href='{escape(it['url'] or '#', quote=True)}' target='_blank' rel='noopener noreferrer'>"
            f"<div class='p'><img src='{escape(it['poster'], quote=True)}' alt='' loading='lazy'>{badge}{heart}</div>"
            f"<div class='t' title='{escape(it['title'], quote=True)}'>{escape(it['title'])}</div>"
            f"<div class='s'>{score}</div><div class='l'>{escape(it.get('line') or '')}</div></a>")


def open_viewall(key):
    st.session_state["viewall"] = key
    st.session_state["nav"] = "📚 View all"
    st.session_state["close_pop"] = True


def render_row(key, title, items, ranked=False, n=10, extra_button=None):
    import streamlit.components.v1 as components
    c1, c2, c3 = st.columns([6, 1.3, 1.3], vertical_alignment="center")
    c1.markdown(f"##### {title}")
    if extra_button:
        extra_button(c2)
    c3.button("View all ›", key=f"va_{key}", on_click=open_viewall, args=(key,))
    shown = items[:n]
    favs = st.session_state["favs"]
    fav_buttons(key, [it["title"] for it in shown])
    html = "".join(_item_html(it, (i + 1) if ranked else None, key, i, it["title"] in favs)
                   for i, it in enumerate(shown))
    components.html(SLIDER_HTML.replace("__ITEMS__", html), height=340)


def render_history_row():
    items = history_items()[:10]
    if not items:
        st.markdown(f"##### {HISTORY_TITLE}")
        st.caption("Abhi history khali hai. Koi anime search karo ya TV mode kholo, yahan latest episode ke saath dikhega.")
        return
    render_row("history", HISTORY_TITLE, items, n=10,
               extra_button=lambda col: col.button("Clear", key="hist_clear", on_click=clear_history))


HB_CSS = ".hb{position:absolute;top:6px;right:6px;width:28px;height:28px;padding:0;border-radius:50%;border:1px solid rgba(255,255,255,.4);background:rgba(11,10,18,.72);color:#fff;font-size:14px;line-height:1;cursor:pointer;z-index:6;display:flex;align-items:center;justify-content:center;transition:transform .2s,background .2s}.hb:hover{transform:scale(1.15);background:rgba(255,42,117,.55)}"
HB_JS = "function favToggle(p,i,ev){ev.preventDefault();ev.stopPropagation();try{var b=window.parent.document.querySelector('.st-key-favrow_'+p+'_'+i+' button');if(b)b.click();}catch(e){}return false;}"


def page_view_all():
    key = st.session_state.get("viewall")
    _b1, _b2, _ = st.columns([1, 1, 6])
    _b1.button("← Back", key="va_back", on_click=go_home)
    if key == "history":
        _b2.button("Clear", key="hist_clear", on_click=clear_history)
        title, items, ranked = HISTORY_TITLE, history_items(), False
    elif key in SECTIONS:
        title, ranked = SECTIONS[key]["title"], SECTIONS[key]["ranked"]
        items = safe_section(key)
    else:
        go_home()
        st.rerun()
        return
    st.markdown(f"##### {title}")
    if not items:
        if key == "history":
            st.info("Abhi history khali hai. Koi anime search karo ya TV mode kholo, yahan latest episode ke saath dikhega.")
        else:
            st.info("List abhi nahi mili. Thodi der baad dobara try karo.")
        return
    if ranked:
        items = items[:50]
    import streamlit.components.v1 as components
    favs = st.session_state["favs"]
    prefix = "va_" + str(key)
    fav_buttons(prefix, [it["title"] for it in items])
    cards = "".join(
        f"<a class='vc' href='{escape(it['url'] or '#', quote=True)}' target='_blank' rel='noopener noreferrer'>"
        f"<div class='vp'><img src='{escape(it['poster'], quote=True)}' alt='' loading='lazy'>"
        + (f"<span class='vr'>#{i + 1}</span>" if ranked else "")
        + _heart_btn(prefix, i, it["title"] in favs) + "</div>"
        f"<div class='vt' title='{escape(it['title'], quote=True)}'>{escape(it['title'])}</div>"
        f"<div class='vs'>{'★ ' + str(it['score']) if it.get('score') else '&nbsp;'}</div>"
        f"<div class='vl'>{escape(it.get('line') or '')}</div></a>"
        for i, it in enumerate(items))
    page = (
        "<style>html,body{margin:0;background:transparent;font-family:'Source Sans Pro',system-ui,sans-serif;color:#fff}"
        ".vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:18px;padding:4px 2px}"
        ".vc{text-decoration:none;color:#fff!important;display:block;min-width:0}"
        ".vp{position:relative;aspect-ratio:2/3;border-radius:10px;overflow:hidden;background:#1a1829;"
        "box-shadow:0 6px 16px rgba(0,0,0,.45);transition:transform .25s ease}"
        ".vp img{width:100%;height:100%;object-fit:cover;display:block}.vc:hover .vp{transform:translateY(-4px) scale(1.03)}"
        ".vr{position:absolute;left:6px;top:6px;background:#ff2a75;color:#fff;font-weight:800;font-size:12px;"
        "padding:2px 8px;border-radius:999px}"
        ".vt{font-size:12.5px;font-weight:700;margin-top:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".vs{font-size:12px;font-weight:700;color:#ffb703;min-height:16px}"
        ".vl{font-size:11px;color:#2ee59d;font-weight:600;min-height:15px}"
        + HB_CSS + "</style>"
        f"<div class='vgrid'>{cards}</div>"
        "<script>" + HB_JS +
        "function fit(){try{window.frameElement.style.height=(document.documentElement.scrollHeight+6)+'px';}catch(e){}}"
        "window.addEventListener('load',fit);window.addEventListener('resize',fit);setTimeout(fit,300);setTimeout(fit,1200);"
        "</script>")
    components.html(page, height=900)


# ---------------------------------------------------------------
# Footer: Other updates (news, server status, festivals, season)
# ---------------------------------------------------------------
STATUS_SITES = [
    ("AniList", "https://graphql.anilist.co", "post"),
    ("Kitsu", "https://kitsu.io/api/edge/anime?page[limit]=1", "get"),
    ("Jikan (MyAnimeList)", "https://api.jikan.moe/v4/anime/1", "get"),
    ("TVmaze", "https://api.tvmaze.com/shows/1", "get"),
    ("Anime News Network", "https://www.animenewsnetwork.com/all/rss.xml", "get"),
]


def _ping(item):
    name, url, method = item
    t0 = time.time()
    try:
        if method == "post":
            r = requests.post(url, json={"query": "{ Page(perPage:1){ media{ id } } }"}, timeout=5)
        else:
            r = requests.get(url, headers=_UA, timeout=5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 429:
            return (name, "busy", ms)
        return (name, "up" if r.status_code < 400 else "down", ms)
    except requests.RequestException:
        return (name, "down", None)


@st.cache_data(ttl=300, show_spinner=False)
def load_server_status():
    with ThreadPoolExecutor(max_workers=5) as ex:
        return list(ex.map(_ping, STATUS_SITES))


@st.cache_data(ttl=1800, show_spinner=False)
def load_news():
    import xml.etree.ElementTree as ET
    r = requests.get("https://www.animenewsnetwork.com/all/rss.xml", headers=_UA, timeout=8)
    if r.status_code != 200:
        raise RuntimeError("news unavailable")           # errors are not cached
    root = ET.fromstring(r.content)
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        when = (it.findtext("pubDate") or "").strip()[:16]
        if title and link.startswith("http"):
            out.append({"title": unescape(title), "url": link, "when": when})
        if len(out) >= 8:
            break
    if not out:
        raise RuntimeError("empty")
    return out


def safe_news():
    if time.time() < store.get("news_fail_until", 0):
        return None
    try:
        return load_news()
    except Exception:
        store["news_fail_until"] = time.time() + 120
        return None


# months are the usual ones; exact dates change every year
FESTIVALS = [
    {"name": "AnimeJapan", "where": "Tokyo, Japan", "months": [3], "url": "https://anime-japan.jp"},
    {"name": "MCM Comic Con", "where": "London, UK", "months": [5, 10], "url": "https://www.mcmcomiccon.com"},
    {"name": "Anime Expo", "where": "Los Angeles, USA", "months": [7], "url": "https://www.anime-expo.org"},
    {"name": "Japan Expo", "where": "Paris, France", "months": [7], "url": "https://www.japan-expo-paris.com"},
    {"name": "Comiket", "where": "Tokyo, Japan", "months": [8, 12], "url": "https://www.comiket.co.jp"},
    {"name": "Anime NYC", "where": "New York, USA", "months": [11], "url": "https://animenyc.com"},
    {"name": "Comic Con India", "where": "India (Delhi, Bengaluru and more)", "months": [10, 11, 12, 1, 2],
     "url": "https://www.comicconindia.com"},
]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _season_now():
    m = datetime.now().month
    return ["Winter", "Winter", "Winter", "Spring", "Spring", "Spring",
            "Summer", "Summer", "Summer", "Fall", "Fall", "Fall"][m - 1]


def _footer_refresh():
    load_server_status.clear()
    load_news.clear()
    load_week_schedule.clear()
    load_upcoming_shows.clear()
    store["news_fail_until"] = 0


OU_CSS = """
<style>
.ou-hero{border-radius:16px;padding:18px 20px;margin:4px 0 14px;
 background:linear-gradient(120deg,rgba(255,42,117,.28),rgba(124,58,237,.28) 50%,rgba(34,211,238,.24));
 border:1px solid rgba(255,255,255,.14);box-shadow:0 8px 28px rgba(124,58,237,.18)}
.ou-title{font-size:22px;font-weight:800;background:linear-gradient(90deg,#ff2a75,#ffb703,#2ee59d,#22d3ee);
 -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;display:inline-block}
.ou-sub{color:#cfcde6;font-size:12.5px;margin:2px 0 12px}
.ou-chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{font-size:12px;font-weight:700;padding:4px 12px;border-radius:999px;border:1px solid}
.ou-card{border-radius:14px;padding:6px 14px 8px;background:rgba(26,24,41,.72);border:1px solid #2b2840;
 border-top:3px solid var(--c);margin-top:8px}
.ou-row{display:flex;gap:12px;align-items:center;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.07);font-size:13px}
.ou-row:last-child{border-bottom:0}
.ou-idx{min-width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;
 font-weight:800;font-size:12px;color:#0b0a12;background:var(--c)}
.ou-link{color:#fff;text-decoration:none;font-weight:600}
.ou-link:hover{color:var(--c)}
.ou-meta{color:#9a97b8;font-size:11.5px}
.ou-bar{height:6px;border-radius:999px;background:rgba(255,255,255,.10);overflow:hidden;width:90px}
.ou-bar>span{display:block;height:100%;border-radius:999px}
.ou-season{display:flex;align-items:center;gap:16px;padding:14px 4px}
.ou-big{font-size:46px;line-height:1}
.ou-stitle{font-size:20px;font-weight:800;color:#fb923c}
</style>
"""

SEASON_EMOJI = {"Winter": "❄️", "Spring": "🌸", "Summer": "☀️", "Fall": "🍂"}
FEST_COLORS = ["#f472b6", "#a78bfa", "#22d3ee", "#fb923c", "#2ee59d", "#facc15", "#ff2a75"]


def _chip(text, color):
    return f"<span class='chip' style='color:{color};border-color:{color};background:{color}1a'>{text}</span>"


def render_footer():
    from datetime import timedelta  # noqa: F401  (kept for symmetry with render_schedule)
    st.markdown(OU_CSS, unsafe_allow_html=True)
    st.markdown("<hr style='margin:34px 0 14px;border-color:#1a1829;'>", unsafe_allow_html=True)

    status = load_server_status()
    up = sum(1 for _, st_, _ in status if st_ == "up")
    news = safe_news()
    cur = datetime.now().month
    n_fest = sum(1 for e in FESTIVALS if cur in e["months"])
    season = _season_now()
    chips = (
        _chip(f"🌐 {up}/{len(status)} servers online",
              "#2ee59d" if up == len(status) else ("#ffb703" if up else "#ff4d4d"))
        + _chip(f"📰 {len(news) if news else 0} news", "#22d3ee")
        + _chip(f"🎉 {n_fest} events this month", "#f472b6")
        + _chip(f"{SEASON_EMOJI[season]} {season} {datetime.now().year}", "#fb923c"))
    st.markdown(
        "<div class='ou-hero'><div class='ou-title'>📢 Other updates</div>"
        "<div class='ou-sub'>News, server status, festivals aur season, sab ek jagah</div>"
        f"<div class='ou-chips'>{chips}</div></div>", unsafe_allow_html=True)

    _, h2 = st.columns([6, 1.3], vertical_alignment="center")
    h2.button("🔄 Refresh", key="ft_refresh", on_click=_footer_refresh)

    t_news, t_srv, t_fest, t_season = st.tabs(
        ["📰 Anime news", "🌐 Server status", "🎉 Festivals", "📅 This season"])

    with t_news:
        if not news:
            st.caption("News abhi nahi mil rahi. Thodi der baad Refresh dabao.")
        else:
            rows = ""
            for i, n in enumerate(news, 1):
                rows += (
                    f"<div class='ou-row'><span class='ou-idx'>{i}</span><div style='min-width:0'>"
                    f"<a class='ou-link' href='{escape(n['url'], quote=True)}' target='_blank' "
                    f"rel='noopener noreferrer'>{escape(n['title'])}</a>"
                    f"<div class='ou-meta'>{escape(n['when'])}</div></div></div>")
            st.markdown(f"<div class='ou-card' style='--c:#22d3ee'>{rows}</div>", unsafe_allow_html=True)
            st.caption("Source: Anime News Network")

    with t_srv:
        colors = {"up": "#2ee59d", "busy": "#ffb703", "down": "#ff4d4d"}
        labels = {"up": "Online", "busy": "Busy", "down": "Down"}
        rows = ""
        for name, state, ms in status:
            c = colors[state]
            fill = 8 if ms is None else max(8, min(100, int(100 - ms / 15)))
            speed = f"{ms} ms" if ms is not None else "no reply"
            rows += (
                "<div class='ou-row'>"
                f"<span style='width:10px;height:10px;border-radius:50%;background:{c};box-shadow:0 0 8px {c}'></span>"
                f"<span style='flex:1;font-weight:600'>{escape(name)}</span>"
                f"<div class='ou-bar'><span style='width:{fill}%;background:{c}'></span></div>"
                f"<span style='color:{c};font-weight:700;min-width:58px;text-align:right'>{labels[state]}</span>"
                f"<span class='ou-meta' style='min-width:64px;text-align:right'>{speed}</span></div>")
        st.markdown(f"<div class='ou-card' style='--c:#2ee59d'>{rows}</div>", unsafe_allow_html=True)
        st.caption("Agar koi server Down ho to posters ya details kam aa sakte hain. Har 5 minute mein check hota hai.")

    with t_fest:
        evs = sorted(FESTIVALS, key=lambda e: min((m - cur) % 12 for m in e["months"]))
        rows = ""
        for i, e in enumerate(evs):
            c = FEST_COLORS[i % len(FEST_COLORS)]
            months = "".join(
                _chip(MONTH_NAMES[m - 1], "#ff2a75" if m == cur else c) for m in e["months"])
            now_tag = (_chip("THIS MONTH", "#ff2a75") if cur in e["months"] else "")
            rows += (
                f"<div class='ou-row' style='--c:{c}'><span class='ou-idx'>🎉</span>"
                f"<div style='flex:1;min-width:0'><a class='ou-link' href='{escape(e['url'], quote=True)}' "
                f"target='_blank' rel='noopener noreferrer'>{escape(e['name'])}</a> {now_tag}"
                f"<div class='ou-meta'>{escape(e['where'])}</div></div>"
                f"<div style='display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end'>{months}</div></div>")
        st.markdown(f"<div class='ou-card' style='--c:#f472b6'>{rows}</div>", unsafe_allow_html=True)
        st.caption("Months andaza hain. Exact dates har saal badalti hain, official site par check karo.")

    with t_season:
        nxt = {"Winter": "Spring", "Spring": "Summer", "Summer": "Fall", "Fall": "Winter"}[season]
        st.markdown(
            "<div class='ou-card' style='--c:#fb923c'><div class='ou-season'>"
            f"<div class='ou-big'>{SEASON_EMOJI[season]}</div><div>"
            f"<div class='ou-stitle'>{season} {datetime.now().year}</div>"
            f"<div class='ou-meta'>Abhi ye anime season chal raha hai. Agla season: "
            f"{SEASON_EMOJI[nxt]} {nxt}</div></div></div></div>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        b1.link_button("This season (AniList)", "https://anilist.co/search/anime/this-season")
        b2.link_button("Next season (AniList)", "https://anilist.co/search/anime/next-season")
        b3.link_button("Season chart (MAL)", "https://myanimelist.net/anime/season")


# ---------------------------------------------------------------
# Release schedule: weekday pills + timeline (AniList, local time)
# ---------------------------------------------------------------
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SCHED_COLORS = ["#22d3ee", "#a78bfa", "#f472b6", "#fb923c", "#2ee59d", "#facc15"]

WEEK_QUERY = """
query ($from: Int, $to: Int, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    airingSchedules(airingAt_greater: $from, airingAt_lesser: $to, sort: TIME) {
      airingAt episode
      media {
        siteUrl format isAdult countryOfOrigin popularity averageScore
        coverImage { medium }
        title { romaji english }
      }
    }
  }
}
"""


@st.cache_data(ttl=1800, show_spinner="Release schedule load ho raha hai...")
def load_week_schedule(day_key):
    start = datetime.combine(datetime.now().date(), datetime.min.time())
    t0 = int(start.timestamp())
    t1 = t0 + 7 * 86400
    out = []
    for page in range(1, 9):
        data = _anilist_post(WEEK_QUERY, {"from": t0, "to": t1, "page": page})
        if not data:
            if out:
                break
            raise RuntimeError("AniList unavailable")          # errors are not cached
        pg = data.get("Page") or {}
        for it in pg.get("airingSchedules") or []:
            m = it.get("media") or {}
            if m.get("isAdult") or m.get("countryOfOrigin") != "JP":
                continue
            if (m.get("popularity") or 0) < 3000:
                continue
            t = m.get("title") or {}
            sc = m.get("averageScore")
            out.append({
                "at": it["airingAt"], "ep": it["episode"],
                "title": t.get("english") or t.get("romaji") or "Unknown",
                "url": m.get("siteUrl"),
                "poster": (m.get("coverImage") or {}).get("medium"),
                "format": m.get("format"),
                "score": round(sc / 10, 1) if sc else None,
            })
        if not (pg.get("pageInfo") or {}).get("hasNextPage"):
            break
    return out


def _set_sched_day(i):
    st.session_state["sched_day"] = i


SCHED_CSS = """
<style>
.sc-head{font-size:22px;font-weight:800;margin:30px 0 10px;
 background:linear-gradient(90deg,#ef4444,#fb923c,#facc15);-webkit-background-clip:text;background-clip:text;
 -webkit-text-fill-color:transparent;display:inline-block}
.sc-note{display:flex;gap:14px;align-items:center;border-radius:14px;padding:14px 16px;margin-bottom:14px;
 background:rgba(120,80,10,.28);border:1px solid rgba(250,170,30,.55);color:#fde68a;font-size:13px;line-height:1.5}
.sc-i{flex:0 0 26px;height:26px;border-radius:50%;background:#f59e0b;color:#1a1200;font-weight:900;
 display:flex;align-items:center;justify-content:center}
.sc-next{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;border-radius:12px;padding:10px 14px;margin:10px 0 4px;
 background:linear-gradient(90deg,rgba(34,211,238,.16),rgba(167,139,250,.14));border:1px solid rgba(34,211,238,.35);
 font-size:13px}
.sc-day{font-size:15px;font-weight:800;margin:14px 0 4px;color:#fff}
.tl{position:relative;padding-left:34px;margin-top:10px}
.tl:before{content:"";position:absolute;left:11px;top:8px;bottom:8px;width:3px;border-radius:3px;
 background:linear-gradient(#22d3ee,#a78bfa,#f472b6,#fb923c)}
.tl-item{position:relative;margin-bottom:12px}
.tl-dot{position:absolute;left:-29px;top:22px;width:14px;height:14px;border-radius:50%;border:2px solid #12101b}
a.tl-card, div.tl-card{display:block;border-radius:16px;padding:14px 16px;background:#23263a;border:1px solid #33374d;
 text-decoration:none;color:#fff;transition:transform .2s ease,border-color .2s ease}
a.tl-card:hover{transform:translateX(4px);border-color:#ff7a8a}
.tl-card.past{opacity:.5}
.tl-card.next{border-color:#ff2a75;box-shadow:0 0 22px rgba(255,42,117,.35)}
.tl-top{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:8px}
.tl-time{font-size:18px;font-weight:800;color:#ff7a8a}
.tl-in{font-size:13px;color:#a3a6bd;font-weight:600}
.tl-tag{background:#ff2a75;color:#fff;font-size:10px;font-weight:800;padding:2px 8px;border-radius:999px;margin-right:8px}
.tl-body{display:flex;gap:12px;align-items:center}
.tl-body img{width:44px;height:62px;object-fit:cover;border-radius:8px;flex:0 0 auto}
.tl-title{font-size:15px;font-weight:700;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;
 -webkit-box-orient:vertical;overflow:hidden}
.tl-meta{font-size:11.5px;color:#9a97b8;margin-top:4px}
.sc-stay{border-radius:14px;padding:16px 18px;margin-top:14px;background:rgba(120,30,40,.35);
 border:1px solid rgba(239,68,68,.25);color:#e7e5f5;font-size:13.5px;line-height:1.6}
[class*="st-key-wd_"], [class*="st-key-wd_"] .stButton { width:100% !important; }
[class*="st-key-wd_"] button { width:100% !important; border-radius:999px !important; padding:10px 0 !important;
 background:#1f2230 !important; border:1px solid #343848 !important; transition:transform .15s ease, box-shadow .15s ease; }
[class*="st-key-wd_"] button p { font-size:12.5px !important; font-weight:800 !important; letter-spacing:.5px;
 text-transform:uppercase; color:#c9cbe0 !important; }
[class*="st-key-wd_"] button:hover { transform:translateY(-2px); border-color:#ef4444 !important; }
[class*="st-key-wd_"] button[kind="primary"], [class*="st-key-wd_"] button[data-testid="stBaseButton-primary"] {
 background:linear-gradient(135deg,#ef4444,#b91c1c) !important; border-color:#ff6b6b !important;
 box-shadow:0 0 18px rgba(239,68,68,.5) !important; }
[class*="st-key-wd_"] button[kind="primary"] p, [class*="st-key-wd_"] button[data-testid="stBaseButton-primary"] p { color:#fff !important; }
@media (max-width: 800px) {
 div[data-testid="stHorizontalBlock"]:has([class*="st-key-wd_"]) { flex-wrap:wrap !important; gap:8px !important; }
 div[data-testid="stHorizontalBlock"]:has([class*="st-key-wd_"]) > div { flex:1 1 30% !important; min-width:30% !important; }
}
</style>
"""


SCHED_NAV_JS = """
<script>
(function () {
  var P, D;
  try { P = window.parent; D = P.document; } catch (e) { return; }
  var ID = 'av-sched-fab', SID = 'av-sched-fab-style';

  var oldB = D.getElementById(ID);
  if (oldB) oldB.remove();
  if (P.__avTick) {
    try { P.removeEventListener('scroll', P.__avTick, true); P.removeEventListener('resize', P.__avTick); } catch (e) {}
  }

  if (!D.getElementById(SID)) {
    var st = D.createElement('style');
    st.id = SID;
    st.textContent =
      "#av-sched-fab{position:fixed;right:22px;bottom:26px;z-index:999999;display:flex;align-items:center;height:56px;" +
      "padding:0 6px;border:0;border-radius:999px;cursor:pointer;color:#fff;font:700 13px 'Source Sans Pro',system-ui,sans-serif;" +
      "background:linear-gradient(135deg,#ef4444,#fb923c);box-shadow:0 10px 28px rgba(239,68,68,.55);" +
      "opacity:0;transform:translateY(24px) scale(.8);pointer-events:none;" +
      "transition:opacity .3s ease,transform .3s ease}" +
      "#av-sched-fab.on{opacity:1;transform:none;pointer-events:auto;animation:avfpulse 2.2s ease-in-out infinite}" +
      "#av-sched-fab:hover{transform:scale(1.06)}" +
      "#av-sched-fab .avf-logo{width:44px;height:44px;display:flex;align-items:center;justify-content:center}" +
      "#av-sched-fab .avf-label{max-width:0;overflow:hidden;white-space:nowrap;transition:max-width .3s ease,margin .3s ease}" +
      "#av-sched-fab:hover .avf-label{max-width:150px;margin:0 10px 0 2px}" +
      "#av-sched-fab .avf-arrow{position:absolute;top:-6px;right:-4px;width:22px;height:22px;border-radius:50%;" +
      "background:#0b0a12;border:2px solid #ff7a8a;display:flex;align-items:center;justify-content:center;" +
      "font-size:13px;font-weight:900;line-height:1}" +
      "@keyframes avfpulse{0%,100%{box-shadow:0 10px 28px rgba(239,68,68,.55),0 0 0 0 rgba(239,68,68,.45)}" +
      "50%{box-shadow:0 10px 28px rgba(239,68,68,.55),0 0 0 14px rgba(239,68,68,0)}}";
    D.head.appendChild(st);
  }

  var b = D.createElement('button');
  b.id = ID;
  b.type = 'button';
  b.setAttribute('aria-label', 'Go to release schedule');
  b.title = 'Release schedule';
  b.innerHTML =
    '<span class="avf-logo"><svg viewBox="0 0 48 48" width="32" height="32">' +
    '<rect x="6" y="9" width="36" height="34" rx="7" fill="#fff"/>' +
    '<path d="M6 16a7 7 0 0 1 7-7h22a7 7 0 0 1 7 7v4H6z" fill="#ef4444" stroke="#fff" stroke-width="1"/>' +
    '<rect x="14" y="4" width="4.5" height="11" rx="2.2" fill="#fff"/><rect x="29.5" y="4" width="4.5" height="11" rx="2.2" fill="#fff"/>' +
    '<path d="M20 26l13 7-13 7z" fill="#ef4444"/></svg></span>' +
    '<span class="avf-label">Release schedule</span><span class="avf-arrow" id="avf-arrow">&#8595;</span>';
  D.body.appendChild(b);

  function head() { return D.querySelector('.sc-head'); }
  function tail() { return D.querySelector('.sc-stay'); }

  b.addEventListener('click', function () {
    var h = head();
    if (!h) return;
    h.style.scrollMarginTop = '80px';
    h.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  function tick() {
    var h = head();
    if (!h) { b.classList.remove('on'); return; }
    var vh = P.innerHeight || 800;
    var hr = h.getBoundingClientRect();
    var t = tail();
    var bottom = t ? t.getBoundingClientRect().bottom : hr.top + 400;
    var below = hr.top >= vh - 120;          // schedule is below the screen
    var above = bottom <= 70;                // schedule is above the screen
    if (!below && !above) { b.classList.remove('on'); return; }
    var a = D.getElementById('avf-arrow');
    if (a) a.innerHTML = below ? '&#8595;' : '&#8593;';
    b.classList.add('on');
  }

  P.__avTick = tick;
  P.addEventListener('scroll', tick, true);
  P.addEventListener('resize', tick);
  setInterval(tick, 400);
  tick();

  // iframe removed (page changed): clean up the button
  window.addEventListener('pagehide', function () {
    try { b.remove(); P.removeEventListener('scroll', tick, true); P.removeEventListener('resize', tick); } catch (e) {}
  });
})();
</script>
"""


def render_schedule():
    from datetime import timedelta
    st.markdown(SCHED_CSS, unsafe_allow_html=True)
    import streamlit.components.v1 as _fab
    _fab.html(SCHED_NAV_JS, height=0)
    st.markdown("<div class='sc-head'>🗓️ Release schedule</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sc-note'><span class='sc-i'>!</span><div>Timings AniList se liye gaye hain aur tumhare "
        "computer ke local time mein dikhte hain. Ye Japan ke original broadcast time par based hain, "
        "kisi streaming site ke upload time ki guarantee nahi.</div></div>", unsafe_allow_html=True)

    try:
        sched = load_week_schedule(str(datetime.now().date()))
    except Exception:
        sched = None

    today = datetime.now().date()
    wd_date = {}
    for k in range(7):
        d = today + timedelta(days=k)
        wd_date[d.weekday()] = d
    if "sched_day" not in st.session_state:
        st.session_state["sched_day"] = today.weekday()
    sel = st.session_state["sched_day"]

    cols = st.columns(7)
    for i, c in enumerate(cols):
        c.button(WEEKDAYS[i], key=f"wd_{i}", on_click=_set_sched_day, args=(i,),
                 type="primary" if i == sel else "secondary")

    f1, f2 = st.columns([3, 1.3], vertical_alignment="center")
    q = f1.text_input("Search in schedule", key="sched_q", placeholder="🔍 Is din ke anime mein search karo...",
                      label_visibility="collapsed")
    only_fav = f2.checkbox("❤️ Only favorites", key="sched_fav")

    if sched is None:
        st.warning("Schedule load nahi ho paya. Internet check karo aur Refresh dabao.")
        return

    now = time.time()
    upcoming = [x for x in sched if x["at"] > now]
    if upcoming:
        nx = min(upcoming, key=lambda x: x["at"])
        st.markdown(
            "<div class='sc-next'><span class='tl-tag'>NEXT EPISODE</span>"
            f"<b>{escape(nx['title'])}</b><span style='color:#9a97b8'>Ep {nx['ep']} · "
            f"{datetime.fromtimestamp(nx['at']).strftime('%a %I:%M %p')} · in {_countdown(nx['at'])}</span></div>",
            unsafe_allow_html=True)

    day = wd_date[sel]
    favs_l = {f.lower() for f in st.session_state["favs"]}
    items = [x for x in sched if datetime.fromtimestamp(x["at"]).date() == day]
    total = len(items)
    if q.strip():
        items = [x for x in items if q.strip().lower() in x["title"].lower()]
    if only_fav:
        items = [x for x in items if x["title"].lower() in favs_l]
    items.sort(key=lambda x: x["at"])

    suffix = " · Today" if day == today else (" · Tomorrow" if day == today + timedelta(days=1) else "")
    st.markdown(f"<div class='sc-day'>{WEEKDAYS[sel]} · {day.strftime('%d %b')}{suffix} "
                f"<span style='color:#9a97b8;font-weight:600;font-size:12.5px'>({len(items)} of {total} episodes)</span></div>",
                unsafe_allow_html=True)

    if not items:
        st.info("Is din ke liye koi episode nahi mila. Doosra din ya filter badal ke dekho.")
    else:
        first_next = next((x for x in items if x["at"] > now), None)
        rows = ""
        for k, x in enumerate(items):
            c = SCHED_COLORS[k % len(SCHED_COLORS)]
            past = x["at"] <= now
            when = datetime.fromtimestamp(x["at"]).strftime("%I:%M %p").lower()
            left = "Aired" if past else f"in {_countdown(x['at'])}"
            cls = "tl-card" + (" past" if past else "") + (" next" if x is first_next else "")
            tag = "<span class='tl-tag'>NEXT UP</span>" if x is first_next else ""
            img = (f"<img src='{escape(x['poster'], quote=True)}' alt='' loading='lazy'>" if x.get("poster") else "")
            meta = [f"Ep {x['ep']}"]
            if x.get("format"):
                meta.append(str(x["format"]).replace("_", " "))
            if x.get("score"):
                meta.append(f"★ {x['score']}")
            if x["title"].lower() in favs_l:
                meta.append("❤️ Favorite")
            inner = (
                f"<div class='tl-top'><span class='tl-time'>{tag}{when}</span><span class='tl-in'>{left}</span></div>"
                f"<div class='tl-body'>{img}<div style='min-width:0'>"
                f"<div class='tl-title'>{escape(x['title'])}</div>"
                f"<div class='tl-meta'>{escape(' · '.join(meta))}</div></div></div>")
            dot = f"<span class='tl-dot' style='background:{c};box-shadow:0 0 10px {c}'></span>"
            if x.get("url"):
                card = (f"<a class='{cls}' href='{escape(x['url'], quote=True)}' target='_blank' "
                        f"rel='noopener noreferrer'>{inner}</a>")
            else:
                card = f"<div class='{cls}'>{inner}</div>"
            rows += f"<div class='tl-item'>{dot}{card}</div>"
        st.markdown(f"<div class='tl'>{rows}</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='sc-stay'><b>Stay updated!</b> Naye episodes ka time AniList se aata hai aur har 30 minute "
        "mein refresh hota hai. Kabhi kabhi time thoda badal jata hai, isliye visit karte raho.</div>",
        unsafe_allow_html=True)


def render_credit():
    st.markdown(
        "<div style='text-align:center;color:#7a7893;font-size:11.5px;margin:26px 0 6px;'>"
        "AnimeViewer · data from AniList, Kitsu, Jikan, TVmaze and Anime News Network · "
        "streaming links open the official services</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Upcoming shows: cards grouped by month (AniList, not yet released)
# ---------------------------------------------------------------
UP_QUERY = """
query ($page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    media(type: ANIME, status: NOT_YET_RELEASED, isAdult: false, countryOfOrigin: JP, sort: POPULARITY_DESC) {
      siteUrl format season seasonYear episodes popularity genres
      startDate { year month day }
      title { romaji english }
      coverImage { large }
      trailer { id site }
      nextAiringEpisode { airingAt episode }
      description(asHtml: false)
    }
  }
}
"""

UP_FILTERS = ["All", "TV", "Movie", "ONA / OVA"]
UP_FORMATS = {
    "TV": {"TV", "TV_SHORT"},
    "Movie": {"MOVIE"},
    "ONA / OVA": {"ONA", "OVA", "SPECIAL", "MUSIC"},
}


@st.cache_data(ttl=3600, show_spinner="Upcoming shows load ho rahe hain...")
def load_upcoming_shows(day_key):
    out = []
    for page in (1, 2):
        data = _anilist_post(UP_QUERY, {"page": page})
        if not data:
            if out:
                break
            raise RuntimeError("AniList unavailable")          # errors are not cached
        pg = data.get("Page") or {}
        for m in pg.get("media") or []:
            t = m.get("title") or {}
            sd = m.get("startDate") or {}
            nxt = m.get("nextAiringEpisode") or {}
            tr = m.get("trailer") or {}
            desc = re.sub(r"<[^>]+>", " ", m.get("description") or "")
            desc = re.sub(r"\s+", " ", unescape(desc)).strip()
            out.append({
                "title": t.get("english") or t.get("romaji") or "Unknown",
                "url": m.get("siteUrl"),
                "poster": (m.get("coverImage") or {}).get("large"),
                "format": m.get("format"), "episodes": m.get("episodes"),
                "genres": (m.get("genres") or [])[:3],
                "pop": m.get("popularity") or 0,
                "syn": desc[:150] + ("..." if len(desc) > 150 else ""),
                "trailer": (f"https://www.youtube.com/watch?v={tr['id']}"
                            if (tr.get("site") or "").lower() == "youtube" and tr.get("id") else None),
                "season": m.get("season"), "season_year": m.get("seasonYear"),
                "y": sd.get("year"), "m": sd.get("month"), "d": sd.get("day"),
                "next_at": nxt.get("airingAt"), "next_ep": nxt.get("episode"),
            })
        if not (pg.get("pageInfo") or {}).get("hasNextPage"):
            break
    return out


def _days_left(ts):
    d = (datetime.fromtimestamp(ts).date() - datetime.now().date()).days
    if d < 0:
        return "Any day now"
    if d == 0:
        return "Today"
    if d == 1:
        return "Tomorrow"
    if d < 60:
        return f"in {d} days"
    return f"in {d // 30} months"


def _set_up_filter(i):
    st.session_state["up_filter"] = i
    st.session_state["up_n"] = 24


def _up_more():
    st.session_state["up_n"] = st.session_state.get("up_n", 24) + 24


UP_CSS = """
<style>
.up-head{font-size:22px;font-weight:800;margin:34px 0 4px;
 background:linear-gradient(90deg,#a78bfa,#f472b6,#22d3ee);-webkit-background-clip:text;background-clip:text;
 -webkit-text-fill-color:transparent;display:inline-block}
.up-sub{color:#cfcde6;font-size:12.5px;margin-bottom:10px}
.up-chips{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 12px}
.up-chip{font-size:12px;font-weight:700;padding:4px 12px;border-radius:999px;border:1px solid}
.up-grp{display:flex;align-items:center;gap:10px;margin:20px 0 10px;font-size:15px;font-weight:800;color:#fff;
 letter-spacing:.5px;text-transform:uppercase}
.up-grp:after{content:"";flex:1;height:2px;border-radius:2px;background:linear-gradient(90deg,rgba(255,255,255,.25),transparent)}
.up-grp span{color:#9a97b8;font-size:12px;font-weight:600}
.up-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.up-card{display:flex;gap:14px;border-radius:16px;padding:12px;background:#23263a;border:1px solid #33374d;
 border-left:4px solid var(--c);transition:transform .2s ease,box-shadow .2s ease;min-width:0}
.up-card:hover{transform:translateY(-3px);box-shadow:0 10px 26px rgba(0,0,0,.45)}
.up-poster{position:relative;flex:0 0 88px;height:128px;border-radius:10px;overflow:hidden;background:#1a1829}
.up-poster img{width:100%;height:100%;object-fit:cover;display:block}
.up-fmt{position:absolute;left:5px;top:5px;background:rgba(11,10,18,.85);color:#fff;font-size:9.5px;font-weight:800;
 padding:2px 7px;border-radius:999px;border:1px solid var(--c)}
.up-body{min-width:0;flex:1;display:flex;flex-direction:column;gap:5px}
.up-title{font-size:14.5px;font-weight:700;color:#fff;line-height:1.25;display:-webkit-box;-webkit-line-clamp:2;
 -webkit-box-orient:vertical;overflow:hidden}
.up-date{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.up-badge{font-size:11px;font-weight:800;padding:2px 9px;border-radius:999px;color:#0b0a12;background:var(--c)}
.up-left{font-size:11.5px;font-weight:700;color:#ff7a8a}
.up-genres{display:flex;flex-wrap:wrap;gap:5px}
.up-genres span{font-size:10.5px;color:#cfcde6;background:rgba(255,255,255,.08);padding:1px 8px;border-radius:999px}
.up-syn{font-size:11.5px;line-height:1.4;color:#a9a7c4;display:-webkit-box;-webkit-line-clamp:2;
 -webkit-box-orient:vertical;overflow:hidden}
.up-hype{display:flex;align-items:center;gap:8px;font-size:10.5px;color:#9a97b8;font-weight:700}
.up-bar{flex:1;height:5px;border-radius:999px;background:rgba(255,255,255,.10);overflow:hidden}
.up-bar span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#fb923c,#ff2a75)}
.up-actions{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto}
.up-actions a{font-size:10.5px;font-weight:700;padding:3px 10px;border-radius:7px;background:#2b2e45;color:#fff!important;
 text-decoration:none!important;transition:background .2s ease}
.up-actions a:hover{background:var(--c);color:#0b0a12!important}
</style>
"""


def render_upcoming():
    st.markdown(UP_CSS, unsafe_allow_html=True)
    st.markdown("<div class='up-head'>🚀 Upcoming shows</div>"
                "<div class='up-sub'>Jo anime abhi release nahi hue. Date, countdown, trailer aur hype ek jagah.</div>",
                unsafe_allow_html=True)
    try:
        data = load_upcoming_shows(str(datetime.now().date()))
    except Exception:
        data = None
    if data is None:
        st.warning("Upcoming shows load nahi ho paye. Internet check karo aur thodi der baad dobara try karo.")
        return

    now = time.time()
    rows = []
    for a in data:
        key, text = _upcoming_when(a)
        a = dict(a, key=key, text=text.split(" · Ep")[0],
                 exact=bool(a.get("next_at") or (a.get("y") and a.get("m") and a.get("d"))))
        rows.append(a)

    soon = sum(1 for a in rows if a["exact"] and 0 <= a["key"] - now <= 30 * 86400)
    movies = sum(1 for a in rows if a.get("format") == "MOVIE")
    top = max(rows, key=lambda a: a["pop"], default=None)
    chips = (
        f"<span class='up-chip' style='color:#a78bfa;border-color:#a78bfa;background:#a78bfa1a'>🚀 {len(rows)} upcoming</span>"
        f"<span class='up-chip' style='color:#ff7a8a;border-color:#ff7a8a;background:#ff7a8a1a'>⏳ {soon} in next 30 days</span>"
        f"<span class='up-chip' style='color:#22d3ee;border-color:#22d3ee;background:#22d3ee1a'>🎬 {movies} movies</span>")
    if top:
        chips += (f"<span class='up-chip' style='color:#fb923c;border-color:#fb923c;background:#fb923c1a'>"
                  f"🔥 Most hyped: {escape(top['title'][:32])}</span>")
    st.markdown(f"<div class='up-chips'>{chips}</div>", unsafe_allow_html=True)

    if "up_filter" not in st.session_state:
        st.session_state["up_filter"] = 0
    sel = st.session_state["up_filter"]
    pc = st.columns(len(UP_FILTERS))
    for i, c in enumerate(pc):
        c.button(UP_FILTERS[i], key=f"wd_up_{i}", on_click=_set_up_filter, args=(i,),
                 type="primary" if i == sel else "secondary")

    f1, f2 = st.columns([3, 2], vertical_alignment="center")
    q = f1.text_input("Search upcoming", key="up_q", placeholder="🔍 Naam ya genre se search karo...",
                      label_visibility="collapsed")
    sort = f2.radio("Sort", ["Soonest", "Most hyped"], horizontal=True, key="up_sort", label_visibility="collapsed")

    items = rows
    if UP_FILTERS[sel] != "All":
        items = [a for a in items if a.get("format") in UP_FORMATS[UP_FILTERS[sel]]]
    if q.strip():
        ql = q.strip().lower()
        items = [a for a in items if ql in a["title"].lower() or any(ql in g.lower() for g in a["genres"])]
    items = sorted(items, key=lambda a: a["key"]) if sort == "Soonest" else sorted(items, key=lambda a: -a["pop"])

    if not items:
        st.info("Is filter se koi upcoming anime nahi mila.")
        return

    maxpop = max((a["pop"] for a in rows), default=1) or 1
    shown_n = st.session_state.get("up_n", 24)
    shown = items[:shown_n]

    def card(a, idx):
        c = SCHED_COLORS[idx % len(SCHED_COLORS)]
        img = f"<img src='{escape(a['poster'], quote=True)}' alt='' loading='lazy'>" if a.get("poster") else ""
        fmt = escape(str(a.get("format") or "").replace("_", " "))
        fmt_html = f"<span class='up-fmt'>{fmt}</span>" if fmt else ""
        left = f"<span class='up-left'>{_days_left(a['key'])}</span>" if a["exact"] else ""
        genres = "".join(f"<span>{escape(g)}</span>" for g in a["genres"])
        if a.get("episodes"):
            genres += f"<span>{a['episodes']} eps</span>"
        pct = max(6, int(a["pop"] / maxpop * 100))
        links = ""
        if a.get("url"):
            links += f"<a href='{escape(a['url'], quote=True)}' target='_blank' rel='noopener noreferrer'>Info</a>"
        if a.get("trailer"):
            links += f"<a href='{escape(a['trailer'], quote=True)}' target='_blank' rel='noopener noreferrer'>🎞 Trailer</a>"
        links += (f"<a href='https://www.crunchyroll.com/search?q={urllib.parse.quote(a['title'])}' "
                  "target='_blank' rel='noopener noreferrer'>▶ Watch</a>")
        return (
            f"<div class='up-card' style='--c:{c}'>"
            f"<div class='up-poster'>{img}{fmt_html}</div><div class='up-body'>"
            f"<div class='up-title' title='{escape(a['title'], quote=True)}'>{escape(a['title'])}</div>"
            f"<div class='up-date'><span class='up-badge'>📅 {escape(a['text'])}</span>{left}</div>"
            f"<div class='up-genres'>{genres}</div>"
            f"<div class='up-syn'>{escape(a['syn'])}</div>"
            f"<div class='up-hype'>🔥 Hype<div class='up-bar'><span style='width:{pct}%'></span></div></div>"
            f"<div class='up-actions'>{links}</div></div></div>")

    html = ""
    if sort == "Soonest":
        groups = {}
        for a in shown:
            label = (datetime.fromtimestamp(a["key"]).strftime("%B %Y") if a["key"] < 9e9 - 1 else "Date TBA")
            groups.setdefault(label, []).append(a)
        n = 0
        for label, g in groups.items():
            cards = ""
            for a in g:
                cards += card(a, n)
                n += 1
            html += f"<div class='up-grp'>{escape(label)} <span>({len(g)})</span></div><div class='up-grid'>{cards}</div>"
    else:
        cards = "".join(card(a, i) for i, a in enumerate(shown))
        html = f"<div class='up-grp'>Most hyped <span>({len(shown)})</span></div><div class='up-grid'>{cards}</div>"
    st.markdown(html, unsafe_allow_html=True)

    if shown_n < len(items):
        st.button(f"Show more ⬇️ ({len(items) - shown_n} baaki)", key="up_more", on_click=_up_more)


# ---------------------------------------------------------------
# Comments (comments.json): per anime, shows the signed-in account name
# ---------------------------------------------------------------
COMMENTS_FILE = os.path.join(BASE_DIR, "comments.json")
COMMENT_MAX = 500
_cm_lock = threading.Lock()


def _cm_load():
    try:
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _cm_save(data):
    try:
        with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except Exception:
        return False


def _cm_key(name):
    return "cm_" + hashlib.md5(name.encode("utf-8")).hexdigest()[:10]


def _cm_post(name, key):
    user = st.session_state.get("user", "")
    text = (st.session_state.get(key) or "").strip()
    if not user:
        st.toast("Comment karne ke liye pehle Sign in karo.", icon="⚠️")
        return
    if not text:
        return
    with _cm_lock:
        data = _cm_load()
        data.setdefault(name, []).append({
            "id": secrets.token_hex(4),
            "user": user,
            "text": text[:COMMENT_MAX],
            "at": time.time(),
        })
        if not _cm_save(data):
            st.toast("Comment save nahi ho paya. Folder ki permission check karo.", icon="⚠️")
            return
    st.session_state[key] = ""          # clear the box after posting


def _cm_delete(name, cid):
    user = st.session_state.get("user", "")
    with _cm_lock:
        data = _cm_load()
        data[name] = [c for c in data.get(name, [])
                      if not (c.get("id") == cid and str(c.get("user", "")).lower() == user.lower())]
        _cm_save(data)


def page_comments(name):
    """Comment box + list of comments for one anime."""
    user = st.session_state.get("user", "")
    key = _cm_key(name)
    st.markdown("<hr style='margin:26px 0 14px;border-color:#1a1829;'>", unsafe_allow_html=True)
    st.markdown("##### 💬 Comments")

    if user:
        st.text_area(
            "Write a comment", key=key, max_chars=COMMENT_MAX, height=90,
            placeholder=f"{user} ke naam se comment likho...",
            label_visibility="collapsed")
        st.button("Post comment", key="cmpost_" + key, on_click=_cm_post, args=(name, key))
    else:
        st.info("Comment karne ke liye upar 'Sign in' se login karo. Tumhara account ka naam comment ke saath dikhega.")

    comments = _cm_load().get(name, [])
    if not comments:
        st.caption("Abhi koi comment nahi hai. Pehla comment tum karo!")
        return
    st.caption(f"{len(comments)} comment{'s' if len(comments) != 1 else ''}")

    for c in reversed(comments):                # newest first
        who = str(c.get("user", "Unknown"))
        when = datetime.fromtimestamp(c.get("at", 0)).strftime("%d %b %Y, %I:%M %p")
        initial = escape(who[:1].upper() or "?")
        body = escape(str(c.get("text", ""))).replace("\n", "<br>")
        st.markdown(
            "<div style='display:flex;gap:12px;padding:12px 14px;margin:8px 0 2px;border-radius:12px;"
            "background:rgba(26,24,41,.72);border:1px solid #2b2840;'>"
            "<div style='flex:0 0 36px;height:36px;border-radius:50%;background:#ff2a75;color:#fff;"
            f"font-weight:800;display:flex;align-items:center;justify-content:center'>{initial}</div>"
            "<div style='min-width:0;flex:1'>"
            f"<div><b style='color:#2ee59d'>{escape(who)}</b> "
            f"<span style='color:#9a97b8;font-size:11.5px'>· {when}</span></div>"
            f"<div style='font-size:13.5px;line-height:1.5;color:#e7e5f5;word-break:break-word'>{body}</div>"
            "</div></div>", unsafe_allow_html=True)
        if user and who.lower() == user.lower():
            st.button("🗑 Delete", key=f"cmdel_{c.get('id')}", on_click=_cm_delete, args=(name, c.get("id")))


apply_background()

# ---------------------------------------------------------------
# Top bar:  [⋮ menu] [AnimeViewer] ............ [🔍] [⚙️] [Sign in]
# ---------------------------------------------------------------
_c_menu, _c_brand, _c_gap, _c_home, _c_search, _c_set, _c_user = st.columns(
    [0.7, 2.6, 4.4, 0.8, 0.8, 0.8, 1.8], vertical_alignment="center")

with _c_menu:
    with st.popover("⋮", help="Menu"):
        st.button("🎌 Anime", key="nav_anime", on_click=go_home)
        st.button(
            f"❤️ Favorites ({len(st.session_state['favs'])})",
            key="nav_favs",
            on_click=go,
            args=("🤍 Favorites",),
        )
        st.button("📋 My List", key="nav_mylist", on_click=go, args=("📋 My List",))
        st.button("📺 Series", key="nav_series", on_click=go, args=("📺 Series",))
        st.button("🎬 Movies", key="nav_movies", on_click=go, args=("🎬 Movies",))
        st.button("🕘 Watching History", key="nav_history", on_click=open_viewall, args=("history",))
        st.button("🧸 Cartoon", key="nav_cartoon", on_click=go, args=("🧸 Cartoon",))
        st.button("🇮🇳 Hindi", key="nav_hindi", on_click=go, args=("🇮🇳 Hindi",))
        st.button("🇮🇳 Tamil", key="nav_tamil", on_click=go, args=("🇮🇳 Tamil",))
        st.button("🇮🇳 Telugu", key="nav_telugu", on_click=go, args=("🇮🇳 Telugu",))
        st.button("🇬🇧 English", key="nav_english", on_click=go, args=("🇬🇧 English",))
        st.button("🇯🇵 Japanese", key="nav_japanese", on_click=go, args=("🇯🇵 Japanese",))
        st.button("💬 Hindi Sub", key="nav_hsub", on_click=go, args=("💬 Hindi Sub",))
        st.button("📡 Anime TV mode", key="nav_tv", on_click=go, args=("📡 Anime TV mode",))
        st.divider()
        st.caption("Links")
        st.link_button("Crunchyroll", "https://www.crunchyroll.com")
        st.link_button("HIDIVE", "https://www.hidive.com")
        st.link_button("YouTube", "https://www.youtube.com")
        st.link_button("AniList", "https://anilist.co")
        st.link_button("MyAnimeList", "https://myanimelist.net")

with _c_brand:
    st.markdown("<div class='brand' style='padding:6px 0;'>🎬 " + zigzag("AnimeViewer", "#2ee59d") + "</div>", unsafe_allow_html=True)

with _c_home:
    st.button(
        "🏠",
        key="top_home",
        help="Home",
        on_click=go_home,
        type="primary" if st.session_state["nav"] == "🏠 Home" else "secondary",
    )

with _c_search:
    with st.popover("🔍", help="Search anime"):
        st.selectbox(
            "search",
            anime_df['name'].values,
            index=None,
            placeholder="Search anime title...",
            label_visibility="collapsed",
            key="search_pick",
            on_change=search_go,
        )

with _c_set:
    st.button(
        "⚙️",
        key="top_settings",
        help="Settings",
        on_click=go,
        args=("⚙️ Settings",),
        type="primary" if st.session_state["nav"] == "⚙️ Settings" else "secondary",
    )

with _c_user:
    _user = st.session_state.get("user", "")
    with st.popover(f"👤 {_user}" if _user else "Sign in", help="Account"):
        if _user:
            st.markdown(f"Signed in as **{_user}**")
            st.button("Sign out", key="signout", on_click=sign_out)
        else:
            _tab_in, _tab_new, _tab_fp = st.tabs(["Sign in", "Create account", "Forgot password"])
            with _tab_in:
                st.text_input("Username or email", key="si_id", placeholder="username or email")
                st.text_input("Password", key="si_pw", type="password", placeholder="Password")
                st.button("Sign in", key="signin_go", on_click=sign_in)
            with _tab_new:
                st.text_input("Username", key="ca_user", placeholder="3-20 letters, numbers, _ or .")
                st.text_input("Email", key="ca_email", placeholder="you@example.com")
                st.text_input("Password", key="ca_pw", type="password", placeholder="At least 6 characters")
                st.text_input("Confirm password", key="ca_pw2", type="password", placeholder="Repeat password")
                st.button("Create account", key="create_go", on_click=create_account)
            with _tab_fp:
                st.caption("Account banate waqt mila recovery key bhi zaroori hai.")
                st.text_input("Username", key="fp_user", placeholder="Your username")
                st.text_input("Email", key="fp_email", placeholder="Email used for the account")
                st.text_input("Recovery key", key="fp_recovery", type="password", placeholder="Your saved recovery key")
                st.text_input("New password", key="fp_pw", type="password", placeholder="At least 6 characters")
                st.text_input("Confirm new password", key="fp_pw2", type="password", placeholder="Repeat new password")
                st.button("Reset password", key="fp_go", on_click=reset_password)
            st.caption("Account sirf is computer par save hota hai. Password hashed rehta hai, kahin bheja nahi jata.")

# close any open popover (menu / search) after a menu click
if st.session_state.pop("close_pop", False):
    import streamlit.components.v1 as _comp
    _comp.html("""<script>
    (function(){
      var d = window.parent.document;
      function close(){
        ['keydown','keyup'].forEach(function(t){
          var e = new KeyboardEvent(t, {key:'Escape', code:'Escape', keyCode:27, which:27, bubbles:true});
          d.dispatchEvent(e);
          if (d.activeElement) d.activeElement.dispatchEvent(e);
        });
        var pop = d.querySelector('[data-testid="stPopoverBody"]');
        if (pop) { d.body.click(); }
      }
      setTimeout(close, 50); setTimeout(close, 300);
    })();
    </script>""", height=0)

_am = st.session_state.pop("auth_msg", None)
if _am:
    st.toast(_am[1], icon="✅" if _am[0] == "success" else "⚠️")
if st.session_state.get("recovery_notice"):
    st.warning("Account recovery key — ise abhi copy karke safe jagah save karo. Ye dobara show nahi hoga.")
    st.code(st.session_state["recovery_notice"])
    if st.button("I saved my recovery key", key="recovery_saved"):
        st.session_state.pop("recovery_notice", None)
        st.rerun()

nav = st.session_state["nav"]

# ---------------------------------------------------------------
# Top layout
# ---------------------------------------------------------------
_titles = {
    "🏠 Home": ("Browse Anime", ""),
    "🤍 Favorites": ("My Favorites", "Anime you saved with the heart button"),
    "📋 My List": ("My List", "Watching, completed, plan to watch aur episode progress"),
    "⚙️ Settings": ("Settings", "App preferences"),
    "🎭 Genres": ("Browse by genre", "Romance, adventure, action and more. Mix genres, type and rating"),
    "🏆 Top rated": ("Top rated", "Highest rated anime that lots of people have watched"),
    "🔥 Most popular": ("Most popular", "What most people are watching"),
    "🎲 Surprise me": ("Surprise me", "Can't decide? Let the app pick for you"),
    "📺 Series": ("Series", "TV anime series"),
    "🎬 Movies": ("Movies", "Anime movies"),
    "🧸 Cartoon": ("Cartoon", "Doraemon, Pokémon, Shin-chan and more. Full episodes and movies"),
    "🇮🇳 Hindi": ("Hindi", "Hindi dubbed anime search"),
    "🇮🇳 Tamil": ("Tamil", "Tamil dubbed anime search"),
    "🇮🇳 Telugu": ("Telugu", "Telugu dubbed anime search"),
    "💬 Hindi Sub": ("Hindi Sub", "Hindi subtitle anime search"),
    "🇬🇧 English": ("English", "English dubbed anime search"),
    "📚 View all": ("View all", "Everything in this list"),
    "🇯🇵 Japanese": ("Japanese", "Original Japanese audio anime search"),
    "📡 Anime TV mode": ("Anime TV mode", "Lean back, skip to the next anime"),
}
_title, _sub = _titles[nav]

st.markdown(f"""
    <div style="font-size: 22px; margin-top: 8px; margin-bottom: 4px; padding: 6px 0;">{zigzag(_title, "#ff2a4d")}</div>
    {f'<div style="font-size: 11px; color: #7a7893; margin-bottom: 10px;">{_sub}</div>' if _sub else ''}
""", unsafe_allow_html=True)

selected_anime = st.session_state.get("search_pick") if nav == "🏠 Home" else None

st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px; border-color: #1a1829;'>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Main content
# ---------------------------------------------------------------
if nav == "🤍 Favorites":
    fav_names = list(st.session_state["favs"])
    if not fav_names:
        st.info("Abhi koi favorite nahi hai. Home par kisi anime ke neeche gol 🤍 (poster ke upar) dabao.")
    else:
        st.markdown(f"##### ❤️ {len(fav_names)} saved")
        render_grid(fav_names, 5, prefix="favtab")
elif nav == "📋 My List":
    page_mylist()
elif nav == "🧸 Cartoon":
    page_cartoons()
elif nav == "📚 View all":
    page_view_all()
elif nav in ("📺 Series", "🎬 Movies", "🇮🇳 Hindi", "🇮🇳 Tamil", "🇮🇳 Telugu",
             "💬 Hindi Sub", "🇬🇧 English", "🇯🇵 Japanese", "📡 Anime TV mode"):
    _cat = load_catalog()
    if _cat is None:
        st.warning("anime.csv mein name, genre, type, rating, members columns nahi mile.")
    elif nav == "📺 Series":
        page_type(_cat, "TV", "series")
    elif nav == "🎬 Movies":
        page_type(_cat, "Movie", "movies")
    elif nav == "📡 Anime TV mode":
        page_tv(_cat)
    else:
        page_lang(_cat, nav)
elif nav in ("🎭 Genres", "🏆 Top rated", "🔥 Most popular", "🎲 Surprise me"):
    _cat = load_catalog()
    if _cat is None:
        st.warning("anime.csv mein name, genre, type, rating, members columns nahi mile.")
    elif nav == "🎲 Surprise me":
        page_surprise(_cat)
    else:
        # old explore pages are no longer in the menu; fall back to Home
        st.session_state["nav"] = "🏠 Home"
        st.rerun()
elif nav == "⚙️ Settings":
    st.markdown("##### 🎨 Background")
    _names = list(BACKGROUNDS.keys())
    for _row in range(0, len(_names), 3):
        _cols = st.columns(3)
        for _c, _n in zip(_cols, _names[_row:_row + 3]):
            _active = _n == st.session_state["bg"]
            _c.markdown(
                f"<div style='height:84px;border-radius:12px;background:{BACKGROUNDS[_n]};"
                f"border:2px solid {'#ff2a75' if _active else 'rgba(255,255,255,.15)'};"
                "display:flex;align-items:flex-end;padding:8px;box-sizing:border-box;'>"
                "<span style='font-size:12px;font-weight:700;color:#fff;background:rgba(0,0,0,.5);"
                f"padding:2px 10px;border-radius:999px;'>{'✓ ' if _active else ''}{_n}</span></div>",
                unsafe_allow_html=True,
            )
            _c.button(
                _n,
                key=f"bg_{_n}",
                on_click=set_bg,
                args=(_n,),
                help=f"Use {_n}",
            )

    st.markdown("##### 🎬 Video background (anime clip)")
    _vids = list_videos()
    try:
        _static_on = bool(st.get_option("server.enableStaticServing"))
    except Exception:
        _static_on = True
    if not _static_on:
        st.warning(
            "Video chalne ke liye `.streamlit/config.toml` file banao (app.py wale folder mein) "
            "jisme ye 2 line ho:\n\n[server]\n\nenableStaticServing = true\n\nphir app restart karo."
        )
    if not _vids:
        st.info("`static` naam ka folder banao (app.py ke saath) aur usme apni anime clip `.mp4` file daalo. "
                "Phir yahan page refresh karo.")
    else:
        _opts = ["None"] + _vids
        _cur = st.session_state["video"] if st.session_state["video"] in _opts else "None"
        st.selectbox("Clip", _opts, index=_opts.index(_cur), key="video_pick", on_change=set_video)
        st.slider("Dimness (text saaf dikhne ke liye)", 0.0, 0.85, float(st.session_state["dim"]),
                  step=0.05, key="dim_pick", on_change=set_dim)

    st.divider()
    page_upcoming()
elif selected_anime:
    st.markdown(
        f"##### 🎯 Recommendations based on: <span style='color: #ff2a75;'>{escape(str(selected_anime))}</span>",
        unsafe_allow_html=True
    )
    list_controls(selected_anime)
    matches = anime_df.index[anime_df["name"].astype(str) == str(selected_anime)].tolist()
    if not matches:
        st.warning("Selected anime dataset mein nahi mila. Dobara search karo.")
    else:
        idx = matches[0]

        ranked = sorted(
            (
                (int(i), float(score))
                for i, score in zip(topk_idx[idx], topk_val[idx])
                if int(i) != idx
            ),
            key=lambda item: item[1],
            reverse=True,
        )

        rec_names = [anime_df.iloc[i]["name"] for i, _score in ranked[:8]]

        if rec_names:
            render_grid(rec_names, 4, prefix="rec")
        else:
            st.info("Is anime ke liye recommendations available nahi hain.")

    page_comments(selected_anime)
else:
    _car_slot = st.container()                   # airing slider goes here, filled after the page has loaded
    for _k, _sec in SECTIONS.items():
        _items = safe_section(_k)
        if _items:
            render_row(_k, _sec["title"], _items, ranked=_sec["ranked"], n=_sec["n"])
        else:
            st.markdown(f"##### {_sec['title']}")
            st.caption("AniList abhi nahi mil raha. Thodi der baad page refresh karo.")
    because_you_liked()
    with _car_slot:
        current_carousel()
    render_schedule()
    render_upcoming()


render_footer()
render_credit()