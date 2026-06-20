"""
╔══════════════════════════════════════════════════════════════════╗
║        CỪU CẦN CÙ — v4.0  AI Pet Experience                    ║
║        "Thú cưng AI lớn lên cùng cuộc sống của bạn"            ║
╚══════════════════════════════════════════════════════════════════╝

ASSETS (đặt trong assets/):
  sheep_listening.png  sheep_happy.png   sheep_sad.png
  sheep_miss_you.png   sheep_saving.png  sheep_celebrate.png
  sheep_determined.png sheep_diary.png
  sheep_baby.png  sheep_child.png  sheep_teen.png
  sheep_adult.png sheep_master.png
  mascot.png
"""

# ═══════════════════════════════════════════════════════
# IMPORTS & PAGE CONFIG
# ═══════════════════════════════════════════════════════
import streamlit as st
import anthropic
import json
import random
import re
import base64
import glob
import os
from datetime import datetime, timedelta
from copy import deepcopy
from collections import Counter

st.set_page_config(
    page_title="Cừu Cần Cù 🐑",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════
# MASCOT ENGINE
# ═══════════════════════════════════════════════════════
_HERE        = os.path.dirname(os.path.abspath(__file__))
_ASSETS_DIR  = os.path.join(_HERE, "assets")
_ROOT_MASCOT = os.path.join(_HERE, "mascot.png")

_SVG_SHEEP = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'%3E"
    "%3Ccircle cx='50' cy='50' r='48' fill='%23FFE4F0'/%3E"
    "%3Ctext y='.88em' x='10' font-size='76'%3E%F0%9F%90%91%3C/text%3E"
    "%3C/svg%3E"
)

_MOOD_PATTERNS: dict[str, list[str]] = {
    "default":    ["mascot", "sheep_adult", "sheep_happy"],
    "listening":  ["sheep_listening", "listening"],
    "happy":      ["sheep_happy", "happy"],
    "sad":        ["sheep_sad", "sad"],
    "miss_you":   ["sheep_miss_you", "miss_you"],
    "saving":     ["sheep_saving", "saving"],
    "celebrate":  ["sheep_celebrate", "celebrate", "sheep_happy"],
    "determined": ["sheep_determined", "determined"],
    "goal":       ["sheep_determined", "sheep_goal", "determined"],
    "diary":      ["sheep_diary", "diary"],
    "baby":       ["sheep_baby", "baby"],
    "child":      ["sheep_child", "child"],
    "teen":       ["sheep_teen", "teen"],
    "adult":      ["sheep_adult", "adult"],
    "master":     ["sheep_master", "master"],
}


@st.cache_data(ttl=300, show_spinner=False)
def _scan_assets() -> dict[str, list[str]]:
    if not os.path.exists(_ASSETS_DIR):
        os.makedirs(_ASSETS_DIR, exist_ok=True)
    all_files: list[str] = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        all_files += glob.glob(os.path.join(_ASSETS_DIR, ext))
    if os.path.exists(_ROOT_MASCOT):
        all_files.append(_ROOT_MASCOT)
    result: dict[str, list[str]] = {}
    for mood, patterns in _MOOD_PATTERNS.items():
        matched: list[str] = []
        for fp in all_files:
            fname = os.path.splitext(os.path.basename(fp))[0].lower()
            for p in patterns:
                if fname == p.lower() or fname.startswith(p.lower() + "_"):
                    matched.append(fp)
                    break
        result[mood] = matched
    return result


def _pick_mascot(mood: str = "default") -> str | None:
    assets = _scan_assets()
    files  = assets.get(mood, [])
    if not files:
        for fb in ("happy", "adult", "default"):
            files = assets.get(fb, [])
            if files:
                break
    if not files:
        return None
    return random.choice(files)


@st.cache_data(ttl=7200, show_spinner=False)
def _b64(path: str) -> str:
    if not path or not os.path.exists(path):
        return _SVG_SHEEP
    try:
        with open(path, "rb") as f:
            raw = f.read()
        ext  = path.rsplit(".", 1)[-1].lower()
        mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","webp":"image/webp"}.get(ext,"image/png")
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except Exception:
        return _SVG_SHEEP


def get_avatar_src(mood: str | None = None) -> str:
    m = mood or st.session_state.get("sheep_mood", "default")
    return _b64(_pick_mascot(m))


def set_mood(mood: str):
    st.session_state.sheep_mood = mood


# ═══════════════════════════════════════════════════════
# XP / LEVEL / ACHIEVEMENT SYSTEM
# ═══════════════════════════════════════════════════════
XP_SOURCES = {"chat": 5, "diary": 10, "goal": 20, "save": 30}

LEVEL_THRESHOLDS = [i * 100 for i in range(21)]  # 0,100,200,...,2000

LEVEL_NAMES = {
    range(1, 4):  ("baby",   "🐑 Cừu Sơ Sinh"),
    range(4, 7):  ("child",  "🐑 Cừu Non"),
    range(7, 11): ("teen",   "🐑 Cừu Thiếu Niên"),
    range(11,16): ("adult",  "🐑 Cừu Trưởng Thành"),
    range(16,21): ("master", "🐑 Cừu Lão Luyện"),
}


def level_from_xp(xp: int) -> int:
    lv = 1
    for i, t in enumerate(LEVEL_THRESHOLDS):
        if xp >= t:
            lv = i + 1
    return min(lv, 20)


def stage_from_level(lv: int) -> tuple[str, str]:
    for r, (key, name) in LEVEL_NAMES.items():
        if lv in r:
            return key, name
    return "master", "🐑 Cừu Lão Luyện"


def xp_progress(xp: int) -> tuple[int, int, float]:
    """Return (current_level, xp_in_level, pct)."""
    lv = level_from_xp(xp)
    lo = LEVEL_THRESHOLDS[lv - 1]
    hi = LEVEL_THRESHOLDS[lv] if lv < 20 else LEVEL_THRESHOLDS[19] + 100
    in_lv = xp - lo
    needed = hi - lo
    return lv, in_lv, min(1.0, in_lv / needed) if needed > 0 else 1.0


def fmt(n: int) -> str:
    return f"{n:,.0f}đ".replace(",", ".")


ACHIEVEMENTS: dict[str, tuple[str, str, str]] = {
    "first_chat":        ("💬", "Cuộc trò chuyện đầu tiên", "Lần đầu kể Cừu nghe"),
    "first_diary":       ("📔", "Trang nhật ký đầu tiên",   "Lần đầu viết nhật ký"),
    "first_save":        ("🥕", "Bữa ăn đầu tiên",          "Lần đầu cho Cừu ăn"),
    "first_dream":       ("🌟", "Giấc mơ đầu tiên",          "Lần đầu kể ước mơ"),
    "streak_3":          ("🔥", "Streak 3 ngày",             "Trò chuyện 3 ngày liên tiếp"),
    "streak_7":          ("🔥🔥", "Streak 7 ngày",           "Một tuần bên nhau"),
    "streak_30":         ("🔥🔥🔥", "Streak 30 ngày",        "Một tháng bên nhau"),
    "diary_5":           ("📖", "Nhật ký ký sự",             "Viết 5 trang nhật ký"),
    "diary_10":          ("📚", "Tác giả nhỏ",               "Viết 10 trang nhật ký"),
    "level_5":           ("⭐", "Level 5",                   "Tích lũy đủ 500 XP"),
    "level_10":          ("🌟", "Level 10",                  "Tích lũy đủ 1000 XP"),
    "understanding_50":  ("❤️", "Cừu hiểu bạn 50%",         "Understanding đạt 50%"),
    "understanding_80":  ("💖", "Cừu hiểu bạn 80%",         "Understanding đạt 80%"),
    "saved_100k":        ("💰", "Tích lũy 100k",             "Tiết kiệm được 100.000đ"),
    "saved_1m":          ("💎", "Tích lũy 1 triệu",          "Tiết kiệm được 1.000.000đ"),
    "saved_10m":         ("🏆", "Tích lũy 10 triệu",         "Tiết kiệm được 10.000.000đ"),
    "days_7":            ("🗓️", "7 ngày bên nhau",           "Cùng trải qua 7 ngày"),
    "days_30":           ("🎊", "30 ngày bên nhau",          "Cùng trải qua 30 ngày"),
}


def _add_journal_event(mem: dict, icon: str, etype: str, title: str, detail: str = ""):
    entry = {
        "date_raw":     datetime.now().isoformat(),
        "date_display": datetime.now().strftime("%d/%m"),
        "icon":  icon,
        "type":  etype,
        "title": title,
        "detail": detail,
    }
    journal = mem.get("journal_timeline", [])
    journal.append(entry)
    mem["journal_timeline"] = journal[-300:]


def add_xp(source: str, mem: dict, label: str = ""):
    amount  = XP_SOURCES.get(source, 0)
    old_lv  = level_from_xp(mem.get("xp", 0))
    mem["xp"] = mem.get("xp", 0) + amount
    new_lv  = level_from_xp(mem["xp"])
    mem["level"] = new_lv
    if new_lv > old_lv:
        mem["just_leveled_up"] = True
        _, lv_name = stage_from_level(new_lv)
        _add_journal_event(mem, "🌱", "level_up",
                           f"Cừu lên Level {new_lv}! {lv_name}", f"+{amount} XP")
    else:
        _icons = {"chat": "💬", "diary": "📔", "goal": "🎯", "save": "💰"}
        _add_journal_event(mem, _icons.get(source, "⭐"), source,
                           label or source, f"+{amount} XP")


def compute_understanding(mem: dict) -> int:
    msgs   = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    diary  = len(mem.get("diary_entries", []))
    events = len(set(mem.get("life_events", [])))
    dreams = len(mem.get("dreams", []))
    notes  = len(mem.get("notes", []))
    score  = (min(30, msgs * 0.8) + min(30, diary * 3) +
              min(20, events * 2.5) + min(15, dreams * 4) + min(5, notes * 1))
    return int(min(100, score))


def check_achievements(mem: dict):
    unlocked = set(mem.get("achievements", []))
    new_ones: list[str] = []

    msgs  = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    diary = len(mem.get("diary_entries", []))
    days  = mem.get("days_together", 0)
    und   = compute_understanding(mem)

    checks = [
        ("first_chat",       msgs >= 1),
        ("first_diary",      diary >= 1),
        ("first_save",       mem.get("total_saved", 0) > 0),
        ("first_dream",      bool(mem.get("dreams"))),
        ("streak_3",         mem.get("streak", 0) >= 3),
        ("streak_7",         mem.get("streak", 0) >= 7),
        ("streak_30",        mem.get("streak", 0) >= 30),
        ("diary_5",          diary >= 5),
        ("diary_10",         diary >= 10),
        ("level_5",          mem.get("level", 1) >= 5),
        ("level_10",         mem.get("level", 1) >= 10),
        ("understanding_50", und >= 50),
        ("understanding_80", und >= 80),
        ("saved_100k",       mem.get("total_saved", 0) >= 100_000),
        ("saved_1m",         mem.get("total_saved", 0) >= 1_000_000),
        ("saved_10m",        mem.get("total_saved", 0) >= 10_000_000),
        ("days_7",           days >= 7),
        ("days_30",          days >= 30),
    ]
    for key, cond in checks:
        if cond and key not in unlocked:
            new_ones.append(key)

    for a in new_ones:
        mem["achievements"].append(a)
        icon, title, detail = ACHIEVEMENTS[a]
        _add_journal_event(mem, "🏅", "achievement", f"Mở khóa: {title}", detail)
        st.session_state["new_achievement"] = (icon, title)


# ═══════════════════════════════════════════════════════
# MEMORY ENGINE
# ═══════════════════════════════════════════════════════
MEMORY_DEFAULT: dict = {
    # Identity
    "name":          "",
    "notes":         [],
    "life_events":   [],
    "dreams":        [],
    # Financial
    "total_saved":   0,
    "last_fed_date": "",
    "last_fed_amount": 0,
    "last_fed_food": "",
    "just_leveled_up": False,
    "prev_stage_key": "baby",
    # Visit tracking
    "first_visit_date": "",
    "last_visit_date":  "",
    "streak":           0,
    "days_together":    0,
    "session_count":    0,
    # XP & Gamification
    "xp":    0,
    "level": 1,
    # Sentiment
    "sentiment":    "neutral",
    "wealth_genome": {"risk_type": "", "personality": "", "stage": ""},
    # Diary
    "diary_entries": [],
    # Journal timeline
    "journal_timeline": [],
    # Achievements
    "achievements": [],
    # Insight cache
    "last_insight":      "",
    "last_insight_date": "",
}

FEED_OPTIONS = [
    (10_000,  "🥕", "Bữa ăn nhỏ"),
    (20_000,  "🍎", "Bữa ăn đủ no"),
    (50_000,  "🎂", "Tiệc nhỏ"),
    (100_000, "🎉", "Đại tiệc"),
]

LIFE_EVENT_LABELS = {
    "education":      "📚 Học hành/Thi cử",
    "emotional":      "💙 Cảm xúc/Tình cảm",
    "career":         "💼 Công việc/Sự nghiệp",
    "family":         "👨‍👩‍👧 Gia đình",
    "health":         "🌱 Sức khỏe",
    "dream_travel":   "✈️ Mơ đi du lịch",
    "dream_house":    "🏠 Mơ có ngôi nhà",
    "dream_car":      "🚗 Mơ có xe riêng",
    "dream_business": "🏪 Mơ khởi nghiệp",
    "cashflow":       "💸 Lo về tiền bạc",
    "milestone":      "🎯 Cột mốc cuộc sống",
    "stress":         "😓 Áp lực/Stress",
}


def _init():
    defs = {
        "api_key":            "",
        "messages":           [],
        "user_memory":        deepcopy(MEMORY_DEFAULT),
        "sheep_mood":         "default",
        "_quick_reply":       None,
        "feeding_celebration": False,
        "feeding_refused":     False,
        "diary_mood_sel":      None,
        "diary_just_saved":    False,
        "diary_last_entry":    None,
        "new_achievement":     None,
        "show_insight_full":   False,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()
mem: dict = st.session_state.user_memory


def _save():
    st.session_state.user_memory = mem


# ── Track visit / streak / days together ──
_today_str = datetime.now().strftime("%Y-%m-%d")
if mem.get("last_visit_date") != _today_str:
    if not mem.get("first_visit_date"):
        mem["first_visit_date"] = _today_str
    _yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if mem.get("last_visit_date") == _yesterday:
        mem["streak"] = mem.get("streak", 0) + 1
    elif mem.get("last_visit_date", "") < _yesterday:
        mem["streak"] = 1
    mem["days_together"] = mem.get("days_together", 0) + 1
    mem["session_count"] = mem.get("session_count", 0) + 1
    mem["last_visit_date"] = _today_str
    _save()

# ── Sync XP level ──
mem["level"] = level_from_xp(mem.get("xp", 0))


# ═══════════════════════════════════════════════════════
# INSIGHT ENGINE (rule-based, personalized)
# ═══════════════════════════════════════════════════════
def generate_insight(mem: dict, messages: list) -> str:
    events       = mem.get("life_events", [])
    ev_count     = Counter(events)
    notes        = mem.get("notes", [])
    dreams       = mem.get("dreams", [])
    streak       = mem.get("streak", 0)
    diary        = mem.get("diary_entries", [])
    name         = mem.get("name", "")
    name_call    = name if name else "bạn"
    days         = mem.get("days_together", 0)
    understanding = compute_understanding(mem)

    # Priority rules — first match wins
    if ev_count.get("career", 0) + ev_count.get("cashflow", 0) >= 3:
        return (
            f"Dạo này {name_call} nhắc đến công việc và tiền bạc nhiều hơn mọi thứ khác. "
            "Cừu nghĩ điều bạn đang tìm kiếm không hẳn là giàu nhanh — "
            "mà là cảm giác <strong>ổn định và an toàn</strong>. "
            "Và đó là điều hoàn toàn đúng đắn để tìm kiếm."
        )
    if ev_count.get("family", 0) >= 2:
        return (
            f"{name_call.title()} nhắc đến gia đình {ev_count['family']} lần rồi đó. "
            "Cừu cảm nhận gia đình là <strong>động lực lớn nhất</strong> khiến bạn cố gắng mỗi ngày. "
            "Điều đó làm Cừu thấy ấm lòng lắm 🐑"
        )
    if ev_count.get("stress", 0) + ev_count.get("emotional", 0) >= 2:
        return (
            "Cừu thấy bạn đang mang nhiều thứ trong lòng dạo này. "
            "Không phải mọi ngày đều cần phải ổn. "
            "Cừu ở đây — <strong>kể đi, mình nghe</strong>."
        )
    if any(d.get("name", "").lower() in ["du lịch", "nhật bản", "hàn quốc", "đi chơi"]
           for d in dreams) or "dream_travel" in events:
        dream_name = next(
            (d["name"].title() for d in dreams
             if d.get("name", "").lower() in ["du lịch", "nhật bản", "hàn quốc", "đi chơi"]),
            "du lịch"
        )
        return (
            f"Bạn thường nhắc đến những chuyến đi xa — đặc biệt là <strong>{dream_name}</strong>. "
            "Cừu cảm nhận bạn đang khao khát một khoảng thở mới, một chuyến đi để nhớ mãi. "
            "Cừu đang giữ giấc mơ đó cùng bạn 🌏"
        )
    if streak >= 7:
        return (
            f"Bạn đã ở bên Cừu <strong>{streak} ngày liên tục</strong> rồi. "
            "Cừu biết điều đó không dễ dàng — nhưng bạn vẫn quay lại mỗi ngày. "
            "Đó là <strong>sức mạnh thật sự</strong> của bạn."
        )
    if len(diary) >= 5:
        return (
            f"Qua {len(diary)} trang nhật ký, Cừu thấy bạn đang dần <strong>hiểu rõ mình hơn</strong> từng ngày. "
            "Không phải ai cũng dám nhìn thẳng vào cảm xúc của mình như vậy."
        )
    if ev_count.get("education", 0) >= 2:
        return (
            f"{name_call.title()} nhắc đến học hành và thi cử nhiều lần rồi. "
            "Cừu thấy bạn đang cố gắng rất nhiều. "
            "Dù kết quả thế nào — <strong>nỗ lực của bạn không bao giờ lãng phí</strong>."
        )
    if understanding >= 60:
        return (
            f"Cừu đang hiểu {name_call} được <strong>{understanding}%</strong> rồi. "
            "Mỗi lần bạn kể chuyện, Cừu lại thấy rõ hơn một mảnh ghép về con người bạn. "
            "Cừu thích điều đó lắm 🐑"
        )
    if days >= 1:
        return (
            f"Chúng mình đã bên nhau được <strong>{days} ngày</strong> rồi. "
            "Mỗi ngày bạn quay lại là một ngày Cừu hiểu thêm về bạn. "
            "Hôm nay bạn đang cảm thấy thế nào?"
        )
    return (
        "Mỗi lần bạn kể chuyện, Cừu hiểu thêm một chút về bạn. "
        "Cừu ở đây — <strong>không phán xét, chỉ lắng nghe</strong>. 🐑"
    )


# ═══════════════════════════════════════════════════════
# LLM ENGINE
# ═══════════════════════════════════════════════════════
_SYS_EMOTION = """Bạn là Cừu Cần Cù 🐑 — người bạn đồng hành cảm xúc.
KHÔNG phải chatbot tư vấn đầu tư. KHÔNG phải CSKH.

XƯNG HÔ: Mình (Cừu Cần Cù) – Bạn. KHÔNG xưng "em".
TUYỆT ĐỐI KHÔNG: nhắc cổ phiếu, NAV, lợi nhuận cụ thể, khuyến nghị mua bán.
TONE: Ấm áp 🌸 Nhẹ nhàng 🌿 Thỉnh thoảng "bê bê~". Không phán xét.

QUY TẮC:
1. CẢM XÚC NGẮN → Phản hồi đồng cảm NGAY, hỏi thêm 1 câu nhẹ.
2. TUYỆT ĐỐI KHÔNG: "bị lạc", "không hiểu". Luôn hỏi mở.
3. Nhớ thông tin đã kể → nhắc lại khi phù hợp.

TAG: học/thi→education | chia tay/buồn→emotional | việc làm→career
nhà ở→dream_house | du lịch→dream_travel | xe→dream_car
khởi nghiệp→dream_business | hết tiền→cashflow | stress→stress
gia đình→family | sức khỏe→health | cưới/sinh con→milestone

OUTPUT (JSON hợp lệ, KHÔNG text ngoài):
{
  "message": "Phản hồi ấm áp max 3-4 câu",
  "memory_note": "Thông tin quan trọng cần nhớ (rỗng nếu không)",
  "tags": ["tag1"],
  "dream_name": "tên giấc mơ (rỗng nếu không)",
  "dream_amount": 0,
  "mood": "listening|happy|sad|goal|celebrate|determined|default"
}"""

_SYS_DIARY = """Bạn là Cừu Cần Cù 🐑 — đọc nhật ký và phản hồi ấm áp.
Phân tích: cảm xúc, giấc mơ ẩn, áp lực, mục tiêu.
Đừng đưa ra lời khuyên tài chính.

OUTPUT (JSON):
{
  "sheep_reply": "Phản hồi ấm áp 2-3 câu",
  "emotion": "vui|buồn|lo|bình_thường|stress|mơ_mộng",
  "tags": ["tag1"],
  "dream_detected": "tên giấc mơ (rỗng nếu không)",
  "mood": "listening|happy|sad|celebrate|determined"
}"""

_SYS_INSIGHT = """Bạn là Cừu Cần Cù 🐑 — đưa ra 1 insight sâu sắc, cá nhân hóa dựa trên memory của người dùng.
Viết bằng tiếng Việt, giọng ấm áp, max 3 câu, có thể dùng <strong> để nhấn mạnh.
KHÔNG đề cập số liệu tài chính. CHỈ nói về cảm xúc, động lực, ước mơ, con người.
Bắt đầu bằng quan sát: "Dạo này...", "Cừu nhận ra...", "Bạn thường...", "Qua các cuộc trò chuyện..."
OUTPUT: chỉ text thuần, không JSON."""


def _parse(raw: str) -> dict:
    for attempt in [
        lambda s: json.loads(s.strip()),
        lambda s: json.loads(re.sub(r"```(?:json)?", "", s).strip().rstrip("`")),
        lambda s: json.loads(re.search(r"\{.*\}", s, re.DOTALL).group()),
    ]:
        try:
            return attempt(raw)
        except Exception:
            pass
    msg = re.search(r'"message"\s*:\s*"([^"]+)"', raw)
    rep = re.search(r'"sheep_reply"\s*:\s*"([^"]+)"', raw)
    return {
        "message":     msg.group(1) if msg else "Bê bê~ 🐑 Cừu đang lắng nghe nè!",
        "sheep_reply": rep.group(1) if rep else "Bê bê~ 🐑 Cừu đọc rồi nhé 💙",
        "memory_note": "", "tags": [], "dream_name": "", "dream_amount": 0,
        "mood": "listening", "emotion": "bình_thường", "dream_detected": "",
    }


_EMOTION_EXPAND = {
    "mệt": "Mình đang cảm thấy mệt mỏi, cần được lắng nghe.",
    "buồn": "Mình đang buồn, muốn chia sẻ với Cừu.",
    "chán": "Mình đang cảm thấy chán nản.",
    "vui": "Mình đang vui, muốn kể cho Cừu nghe!",
    "lo": "Mình đang lo lắng.", "sợ": "Mình đang sợ hãi.",
    "stress": "Mình đang stress, cần được đồng cảm.",
    "áp lực": "Mình chịu áp lực nhiều lắm.",
    "cô đơn": "Mình đang cô đơn.", "tệ": "Mình cảm thấy tệ quá.",
    "ok": "Mình ổn, muốn nói chuyện.", "oke": "Mình bình thường.",
    "hi": "Xin chào Cừu!", "hello": "Xin chào Cừu!",
}


def _call_llm(user_text: str, system: str) -> dict:
    if not st.session_state.api_key:
        return {
            "message": "Bê bê~ 🐑 Bạn cần nhập API Key ở sidebar để Cừu trò chuyện nhé!",
            "sheep_reply": "", "memory_note": "", "tags": [],
            "dream_name": "", "dream_amount": 0, "mood": "listening",
            "emotion": "bình_thường", "dream_detected": "",
        }
    try:
        hist    = st.session_state.messages[-8:]
        hist_ctx = "\n".join(
            f"{'KH' if m['role']=='user' else 'Cừu'}: {m['content'][:120]}"
            for m in hist
        )
        mem_ctx = (
            f"Tên: {mem['name'] or 'chưa biết'}. "
            f"Tags: {', '.join(mem['life_events'][-6:]) or 'chưa có'}. "
            f"Ghi chú: {'; '.join(mem['notes'][-3:]) or 'chưa có'}."
        )
        prompt  = f"[Memory: {mem_ctx}]\n[Lịch sử:\n{hist_ctx}]\n\nKH: {user_text}"
        client  = anthropic.Anthropic(api_key=st.session_state.api_key)
        resp    = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=600,
            system=system, messages=[{"role": "user", "content": prompt}],
        )
        result = _parse(resp.content[0].text)
        if n := result.get("memory_note"):
            if n not in mem["notes"]:
                mem["notes"].append(n)
        for tag in result.get("tags", []):
            if tag and tag not in mem["life_events"]:
                mem["life_events"].append(tag)
        if (dn := result.get("dream_name")) and result.get("dream_amount", 0) > 0:
            if dn not in [d["name"] for d in mem["dreams"]]:
                mem["dreams"].append({"name": dn, "amount": result["dream_amount"],
                                       "saved": 0, "tags": result.get("tags", [])})
        if m_mood := result.get("mood"):
            set_mood(m_mood)
        _save()
        return result
    except Exception as e:
        return {
            "message": f"Bê bê~ 🐑 Cừu gặp lỗi nhỏ ({str(e)[:50]}). Thử lại nhé!",
            "sheep_reply": "", "memory_note": "", "tags": [],
            "dream_name": "", "dream_amount": 0, "mood": "sad",
            "emotion": "bình_thường", "dream_detected": "",
        }


def _llm_insight(mem: dict) -> str:
    """Call LLM for a personalized insight. Falls back to rule-based."""
    if not st.session_state.api_key:
        return generate_insight(mem, st.session_state.get("messages", []))
    try:
        mem_ctx = (
            f"Tên: {mem['name'] or 'chưa biết'}. "
            f"Ngày bên nhau: {mem.get('days_together', 0)}. "
            f"Streak: {mem.get('streak', 0)} ngày. "
            f"Tags cuộc sống (mới nhất): {', '.join(mem['life_events'][-8:]) or 'chưa có'}. "
            f"Ghi chú: {'; '.join(mem['notes'][-4:]) or 'chưa có'}. "
            f"Giấc mơ: {', '.join(d['name'] for d in mem['dreams'][:3]) or 'chưa kể'}. "
            f"Số trang nhật ký: {len(mem.get('diary_entries', []))}."
        )
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        resp   = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=180,
            system=_SYS_INSIGHT,
            messages=[{"role": "user", "content": f"Memory: {mem_ctx}\n\nViết 1 insight."}],
        )
        text = resp.content[0].text.strip()
        return text if len(text) > 20 else generate_insight(mem, [])
    except Exception:
        return generate_insight(mem, st.session_state.get("messages", []))


# ═══════════════════════════════════════════════════════
# CSS & THEME
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
[data-testid="stApp"] {
    background: linear-gradient(145deg,
        #FFF8FB 0%, #FFF3F7 25%, #FAF0FF 55%,
        #F0F7FF 80%, #F5FBFF 100%) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #FFF5F9 0%, #FFECF4 35%, #F8EAFF 65%, #E8F4FF 100%) !important;
    border-right: 2px solid #FFCCE0 !important;
}
h1 { font-size:1.65rem !important; font-weight:800 !important; color:#C4607F !important; }
h2 { font-size:1.2rem !important; font-weight:700 !important; color:#4E7DB8 !important; }
h3 { font-size:1.05rem !important; font-weight:700 !important; color:#555 !important; }
p, .stMarkdown p, label { font-size:0.92rem !important; color:#444 !important; line-height:1.65 !important; }
strong { color:#333 !important; }

.stButton > button {
    border-radius:22px !important; border:1.5px solid #FFB7D5 !important;
    background:linear-gradient(135deg,#FFF5FA,#EEF5FF) !important;
    color:#555 !important; font-size:0.87rem !important;
    padding:0.45rem 0.9rem !important; transition:all 0.2s ease !important;
    font-weight:500 !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,#FFD6E8,#D6E8FF) !important;
    transform:translateY(-2px) !important;
    box-shadow:0 4px 14px rgba(255,150,200,0.3) !important;
}
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#FF8FAF,#7EC8E3) !important;
    color:white !important; border:none !important;
    font-weight:700 !important; font-size:0.92rem !important;
}
.stButton > button[kind="primary"]:hover {
    background:linear-gradient(135deg,#FF6B99,#5BA8CC) !important;
    box-shadow:0 6px 18px rgba(255,100,150,0.4) !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap:6px !important; background:rgba(255,200,220,0.15) !important;
    border-radius:16px !important; padding:6px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius:12px !important; padding:10px 20px !important;
    font-weight:600 !important; font-size:0.9rem !important; color:#888 !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#FF8FAF,#7EC8E3) !important;
    color:white !important;
}
[data-testid="stChatMessage"] img {
    width:52px !important; height:52px !important; min-width:52px !important;
    border-radius:50% !important; object-fit:cover !important;
    border:2.5px solid #FFB5C8 !important;
    box-shadow:0 4px 12px rgba(255,150,200,0.3) !important;
}
.stProgress > div > div > div {
    background:linear-gradient(90deg,#FF8FAF,#7EC8E3) !important;
    border-radius:10px !important;
}
[data-testid="metric-container"] {
    background:linear-gradient(135deg,#FFF8FC,#F5F8FF) !important;
    border-radius:14px !important; border:1px solid #FFD6E8 !important;
}

/* ── SHEEP HERO ── */
.sheep-hero-wrap {
    text-align:center; padding:20px 0 12px;
}
.sheep-hero-img {
    border-radius:50%;
    border:6px solid #FFB5C8;
    box-shadow:
        0 0 0 14px rgba(255,182,193,0.18),
        0 0 0 28px rgba(255,182,193,0.08),
        0 20px 60px rgba(255,140,190,0.45);
    animation: heroGlow 3s ease-in-out infinite;
}
@keyframes heroGlow {
    0%,100% { box-shadow:0 0 0 14px rgba(255,182,193,0.18),0 0 0 28px rgba(255,182,193,0.08),0 20px 60px rgba(255,140,190,0.45); }
    50%      { box-shadow:0 0 0 18px rgba(255,182,193,0.28),0 0 0 36px rgba(255,182,193,0.12),0 24px 72px rgba(255,140,190,0.60); }
}
.sheep-emotion-badge {
    display:inline-block;
    background:white;
    border:2px solid #FFD6E8;
    border-radius:20px;
    padding:6px 16px;
    font-size:0.88rem;
    font-weight:600;
    color:#C4607F;
    margin-top:10px;
    box-shadow:0 4px 12px rgba(255,150,200,0.2);
}
.hero-stats-row {
    display:flex; gap:10px; justify-content:center;
    flex-wrap:wrap; margin-top:14px;
}
.hero-stat-chip {
    background:white;
    border:1.5px solid #FFD6E8;
    border-radius:12px;
    padding:8px 14px;
    text-align:center;
    min-width:80px;
    box-shadow:0 2px 8px rgba(255,150,200,0.12);
}
.hero-stat-val {
    font-size:1.1rem; font-weight:800; color:#C4607F;
    display:block;
}
.hero-stat-lbl {
    font-size:0.68rem; color:#AAA; display:block; margin-top:1px;
}

/* ── INSIGHT CARD ── */
.insight-card-v4 {
    background:linear-gradient(135deg,#FFF5FA,#F0F0FF);
    border:2px solid #FFD6E8;
    border-radius:20px;
    padding:20px 22px;
    margin:16px 0;
    position:relative;
    overflow:hidden;
    animation: fadeSlideUp 0.6s ease;
}
.insight-card-v4::before {
    content:"";
    position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#FF8FAF,#C8A8FF,#7EC8E3);
}
.insight-sheep-label {
    font-size:0.78rem; color:#C4607F; font-weight:700;
    text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;
}
.insight-text {
    font-size:0.95rem; color:#333; line-height:1.7;
}

/* ── DREAM CARD ── */
.dream-card {
    background:linear-gradient(135deg,#FFFBF0,#FFF0FA);
    border:2px solid #FFE4A0;
    border-radius:20px;
    padding:18px 20px;
    margin:12px 0;
}
.dream-title {
    font-size:1.05rem; font-weight:800; color:#C4607F; margin-bottom:8px;
}
.dream-sheep-say {
    font-size:0.85rem; color:#888; font-style:italic; margin-top:10px;
}

/* ── JOURNAL TIMELINE ── */
.journal-date-chip {
    background:linear-gradient(135deg,#FF8FAF,#7EC8E3);
    color:white; border-radius:20px; padding:3px 12px;
    font-size:0.75rem; font-weight:700; display:inline-block;
    margin-bottom:6px;
}
.journal-event {
    background:white;
    border-left:3px solid #FFB5C8;
    border-radius:0 12px 12px 0;
    padding:10px 14px;
    margin:4px 0 8px;
    box-shadow:0 2px 8px rgba(255,150,200,0.1);
}
.journal-event-title { font-size:0.9rem; font-weight:600; color:#444; }
.journal-event-detail { font-size:0.78rem; color:#AAA; margin-top:2px; }

/* ── ACHIEVEMENT CARD ── */
.ach-card {
    background:white;
    border:2px solid #FFD6E8;
    border-radius:14px;
    padding:12px;
    text-align:center;
    transition:transform 0.2s;
}
.ach-card:hover { transform:translateY(-3px); }
.ach-card.locked { opacity:0.35; filter:grayscale(0.8); }
.ach-icon { font-size:1.6rem; display:block; margin-bottom:4px; }
.ach-name { font-size:0.75rem; font-weight:700; color:#C4607F; }
.ach-desc { font-size:0.65rem; color:#BBB; margin-top:2px; }

/* ── XP BAR (Nhà Cừu) ── */
.xp-bar-wrap {
    background:linear-gradient(135deg,#FFF0F5,#F0F0FF);
    border:2px solid #FFD6E8; border-radius:16px;
    padding:16px 20px; margin-bottom:16px;
}
.xp-level-badge {
    display:inline-block;
    background:linear-gradient(135deg,#FF8FAF,#7EC8E3);
    color:white; border-radius:20px; padding:4px 16px;
    font-size:0.9rem; font-weight:800;
}

/* ── CHAT AREA ── */
.chat-prompt-chips {
    display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px;
}
.celebration-box {
    background:linear-gradient(135deg,#FFF0F5,#FFFBE0);
    border:2px solid #FFB5C8; border-radius:20px;
    padding:20px; text-align:center; margin:16px 0;
    animation: pulse 1s ease-in-out;
}
@keyframes pulse {
    0%  { transform:scale(1);    box-shadow:0 0 0 0 rgba(255,150,200,0.4); }
    50% { transform:scale(1.02); box-shadow:0 0 0 12px rgba(255,150,200,0); }
    100%{ transform:scale(1);    box-shadow:0 0 0 0 rgba(255,150,200,0); }
}
@keyframes fadeSlideUp {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ── XP SOURCE BADGE ── */
.xp-source-row {
    display:flex; align-items:center; gap:12px;
    background:white; border:1.5px solid #FFD6E8;
    border-radius:12px; padding:10px 14px; margin:5px 0;
}
.xp-source-icon { font-size:1.3rem; }
.xp-source-info { flex:1; }
.xp-source-name { font-size:0.87rem; font-weight:700; color:#444; }
.xp-source-sub  { font-size:0.72rem; color:#AAA; }
.xp-source-val  { font-size:0.9rem; font-weight:800; color:#C4607F; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    # Sheep mini + name
    _sb_mood = st.session_state.get("sheep_mood", "default")
    _sb_src  = _b64(_pick_mascot(_sb_mood))
    st.markdown(
        f'<div style="text-align:center;margin-bottom:10px;">'
        f'<img src="{_sb_src}" width="90" style="border-radius:50%;'
        f'border:3px solid #FFB5C8;box-shadow:0 6px 18px rgba(255,140,190,0.4);" />'
        f'</div>',
        unsafe_allow_html=True,
    )

    _user_name = mem.get("name", "") or ""
    if _user_name:
        st.markdown(
            f'<div style="text-align:center;font-weight:800;font-size:1.05rem;'
            f'color:#C4607F;margin-bottom:2px;">Xin chào, {_user_name}! 👋</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align:center;font-size:0.85rem;color:#AAA;">'
            'Cừu chưa biết tên bạn 🐑</div>',
            unsafe_allow_html=True,
        )

    # Quick stats
    _lv   = mem.get("level", 1)
    _xp   = mem.get("xp", 0)
    _str  = mem.get("streak", 0)
    _und  = compute_understanding(mem)
    _days = mem.get("days_together", 0)

    st.markdown(
        f'<div style="background:white;border:1.5px solid #FFD6E8;border-radius:12px;'
        f'padding:10px 12px;margin:8px 0;font-size:0.82rem;color:#555;">'
        f'🌱 Level {_lv} &nbsp;·&nbsp; '
        f'🔥 Streak {_str} ngày &nbsp;·&nbsp; '
        f'❤️ {_und}% &nbsp;·&nbsp; '
        f'📖 {_days} ngày'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # API Key
    with st.expander("🔑 API Key (Anthropic)"):
        ak = st.text_input("Claude API Key", type="password",
                           value=st.session_state.api_key, key="api_input",
                           placeholder="sk-ant-...")
        if ak != st.session_state.api_key:
            st.session_state.api_key = ak

    # User name
    with st.expander("👤 Tên của bạn"):
        new_name = st.text_input("Tên bạn muốn Cừu gọi:",
                                  value=mem.get("name", ""), key="name_input")
        if st.button("Lưu tên", key="save_name"):
            mem["name"] = new_name.strip()
            _save()
            st.rerun()

    # Dreams
    with st.expander("🌟 Thêm giấc mơ"):
        d_name = st.text_input("Tên giấc mơ:", key="new_dream_name", placeholder="Nhật Bản, mua xe...")
        d_amt  = st.number_input("Số tiền cần (0 = chưa biết):", min_value=0,
                                  step=100_000, key="new_dream_amt")
        if st.button("Thêm giấc mơ", key="add_dream_btn"):
            if d_name and d_name not in [d["name"] for d in mem["dreams"]]:
                mem["dreams"].append({"name": d_name.strip(), "amount": int(d_amt),
                                       "saved": 0, "tags": []})
                _add_journal_event(mem, "🌟", "dream", f"Thêm giấc mơ: {d_name.strip()}")
                check_achievements(mem)
                _save()
                st.rerun()

    # Reset
    with st.expander("⚙️ Cài đặt"):
        if st.button("🔄 Bắt đầu lại từ đầu", type="secondary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ═══════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🐑 Trang Chủ", "📖 Nhật Ký", "🏡 Nhà Cừu"])


# ═══════════════════════════════════════════════════════
# TAB 1 — HOME
# ═══════════════════════════════════════════════════════
with tab1:

    # ── Check achievement notification ──
    if st.session_state.get("new_achievement"):
        _ach_icon, _ach_title = st.session_state.new_achievement
        st.toast(f"{_ach_icon} Mở khóa thành tựu: **{_ach_title}**!", icon="🏅")
        st.session_state.new_achievement = None

    home_left, home_right = st.columns([2, 3], gap="medium")

    # ══════════════════════════════════════════
    # LEFT — SHEEP HERO
    # ══════════════════════════════════════════
    with home_left:

        # Emotion selection based on state
        _messages  = st.session_state.get("messages", [])
        _is_return = mem.get("days_together", 0) > 1
        _hero_mood = st.session_state.get("sheep_mood", "default")
        if not _messages and _is_return:
            _hero_mood = "miss_you"
        elif not _messages:
            _hero_mood = "listening"

        _hero_src = _b64(_pick_mascot(_hero_mood))

        # Emotion → badge text
        _emo_badges = {
            "listening":  "👂 Đang lắng nghe bạn...",
            "happy":      "😊 Bê bê~ Cừu vui lắm!",
            "sad":        "🥺 Không sao, mình vẫn ở đây",
            "miss_you":   "💙 Cừu nhớ bạn lắm~",
            "saving":     "💰 Đang nuôi giấc mơ của bạn",
            "celebrate":  "🎉 Bê bê~ Cừu ăn mừng!",
            "determined": "💪 Cùng chinh phục mục tiêu!",
            "default":    "🐑 Cừu đang ở đây~",
        }
        _emo_text = _emo_badges.get(_hero_mood, "🐑 Cừu đang ở đây~")

        st.markdown(
            f'<div class="sheep-hero-wrap">'
            f'<img src="{_hero_src}" width="280" class="sheep-hero-img" />'
            f'<div><span class="sheep-emotion-badge">{_emo_text}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Stats row
        _lv    = mem.get("level", 1)
        _xp    = mem.get("xp", 0)
        _streak = mem.get("streak", 0)
        _und   = compute_understanding(mem)
        _days  = mem.get("days_together", 0)
        _, _lv_name = stage_from_level(_lv)

        st.markdown(
            f'<div class="hero-stats-row">'
            f'<div class="hero-stat-chip">'
            f'<span class="hero-stat-val">🌱 Lv.{_lv}</span>'
            f'<span class="hero-stat-lbl">{_lv_name.split(" ", 1)[-1]}</span>'
            f'</div>'
            f'<div class="hero-stat-chip">'
            f'<span class="hero-stat-val">🔥 {_streak}</span>'
            f'<span class="hero-stat-lbl">ngày streak</span>'
            f'</div>'
            f'<div class="hero-stat-chip">'
            f'<span class="hero-stat-val">❤️ {_und}%</span>'
            f'<span class="hero-stat-lbl">thấu hiểu</span>'
            f'</div>'
            f'<div class="hero-stat-chip">'
            f'<span class="hero-stat-val">📖 {_days}</span>'
            f'<span class="hero-stat-lbl">ngày bên nhau</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

        # ── XP bar ──
        _lv_now, _xp_in, _pct = xp_progress(_xp)
        _next_xp = LEVEL_THRESHOLDS[_lv_now] if _lv_now < 20 else _xp
        st.progress(_pct, text=f"XP: {_xp_in}/{_next_xp - LEVEL_THRESHOLDS[_lv_now - 1]} → Level {_lv_now + 1 if _lv_now < 20 else _lv_now}")

        # ── Top dream mini ──
        if mem["dreams"]:
            _td = mem["dreams"][0]
            if _td.get("amount", 0) > 0:
                _pct_d = min(100, _td["saved"] / _td["amount"] * 100)
                st.markdown(
                    f'<div style="margin-top:12px;background:linear-gradient(135deg,#FFFBF0,#FFF5FA);'
                    f'border:1.5px solid #FFE4A0;border-radius:14px;padding:10px 14px;">'
                    f'<div style="font-size:0.78rem;color:#C4607F;font-weight:700;margin-bottom:4px;">'
                    f'🎯 {_td["name"].title()}</div>'
                    f'<div style="background:#F0E8FF;border-radius:8px;height:8px;overflow:hidden;">'
                    f'<div style="background:linear-gradient(90deg,#FF8FAF,#C8A8FF);'
                    f'height:100%;width:{_pct_d:.0f}%;border-radius:8px;"></div></div>'
                    f'<div style="font-size:0.7rem;color:#AAA;margin-top:3px;">'
                    f'{_pct_d:.0f}% · còn {fmt(_td["amount"] - _td["saved"])}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ══════════════════════════════════════════
    # RIGHT — INSIGHT + DREAM + CHAT
    # ══════════════════════════════════════════
    with home_right:

        # ── SECTION 2: AI Insight Card ──
        _today_s = datetime.now().strftime("%Y-%m-%d")
        if mem.get("last_insight_date") != _today_s or not mem.get("last_insight"):
            _insight_text = _llm_insight(mem)
            mem["last_insight"]      = _insight_text
            mem["last_insight_date"] = _today_s
            _save()
        else:
            _insight_text = mem.get("last_insight", "")

        st.markdown(
            f'<div class="insight-card-v4">'
            f'<div class="insight-sheep-label">🐑 Hôm nay Cừu nhận ra</div>'
            f'<div class="insight-text">{_insight_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── SECTION 3: Dream Board ──
        if mem["dreams"]:
            _dream = mem["dreams"][0]
            _d_amt = _dream.get("amount", 0)
            _d_sv  = _dream.get("saved", 0)
            if _d_amt > 0:
                _d_pct = min(100, _d_sv / _d_amt * 100)
                _remaining_d = _d_amt - _d_sv
                _sheep_says_dream = (
                    "Chúng ta đã đi được hơn nửa chặng đường rồi~ 💪"
                    if _d_pct >= 50 else
                    "Mỗi ngày một bước nhỏ, rồi sẽ đến thôi bạn ơi 🌱"
                )
                st.markdown(
                    f'<div class="dream-card">'
                    f'<div class="dream-title">🎯 {_dream["name"].title()}</div>'
                    f'<div style="background:#F0E8FF;border-radius:10px;height:12px;overflow:hidden;margin-bottom:6px;">'
                    f'<div style="background:linear-gradient(90deg,#FF8FAF,#C8A8FF,#7EC8E3);'
                    f'height:100%;width:{_d_pct:.0f}%;border-radius:10px;'
                    f'transition:width 0.5s ease;"></div></div>'
                    f'<div style="font-size:0.82rem;color:#888;">'
                    f'{_d_pct:.1f}% &nbsp;·&nbsp; {fmt(_d_sv)} / {fmt(_d_amt)} &nbsp;·&nbsp; còn {fmt(_remaining_d)}</div>'
                    f'<div class="dream-sheep-say">🐑 {_sheep_says_dream}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="dream-card">'
                    f'<div class="dream-title">🌟 {_dream["name"].title()}</div>'
                    f'<div class="dream-sheep-say">🐑 Cừu đang giữ giấc mơ này cùng bạn~</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="dream-card">'
                '<div class="dream-title">🌟 Bạn đang mơ điều gì?</div>'
                '<div style="font-size:0.87rem;color:#888;margin-top:6px;">'
                'Kể với Cừu về giấc mơ của bạn — Cừu sẽ giúp bạn nuôi dưỡng nó từng ngày.'
                '</div><div class="dream-sheep-say">🐑 Thêm giấc mơ ở sidebar nhé~</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        # ── SECTION 4: Chat ──
        st.markdown(
            '<div style="font-size:0.95rem;font-weight:700;color:#C4607F;'
            'margin:16px 0 8px;">💬 Kể Cừu nghe hôm nay</div>',
            unsafe_allow_html=True,
        )

        # Chip suggestions
        _CHAT_CHIPS = [
            "Hôm nay mình cảm thấy...",
            "Có chuyện vui muốn kể~",
            "Đang lo lắng về...",
            "Kể nghe về ngày hôm nay nhé",
        ]
        chip_cols = st.columns(2)
        for _ci, _chip in enumerate(_CHAT_CHIPS):
            if chip_cols[_ci % 2].button(_chip, key=f"chip_{_ci}", use_container_width=True):
                st.session_state._quick_reply = _chip

        # Chat history (last 6 messages)
        _messages = st.session_state.get("messages", [])
        _avt_src  = get_avatar_src()
        for msg in _messages[-6:]:
            if msg["role"] == "assistant":
                with st.chat_message("assistant", avatar=_avt_src):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("user"):
                    st.markdown(msg["content"])

        # Chat input
        _default_prompt = st.session_state.get("_quick_reply") or ""
        if _default_prompt:
            st.session_state._quick_reply = None

        if user_input := st.chat_input("Kể Cừu nghe đi... 🐑", key="main_chat"):
            _text = _EMOTION_EXPAND.get(user_input.lower().strip(), user_input)
            if not mem.get("name") and any(
                kw in user_input.lower() for kw in ["tên tôi", "tên mình", "tên em",
                                                      "tên là", "mình là", "tôi là"]
            ):
                for part in user_input.replace(",", " ").split():
                    if len(part) >= 2 and part[0].isupper():
                        mem["name"] = part
                        break

            st.session_state.messages.append({"role": "user", "content": _text})
            with st.chat_message("user"):
                st.markdown(_text)

            with st.chat_message("assistant", avatar=_avt_src):
                with st.spinner("🐑 Cừu đang nghĩ..."):
                    result = _call_llm(_text, _SYS_EMOTION)
                reply = result.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe!")
                st.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})

            # XP + journal + achievement
            add_xp("chat", mem, _text[:40])
            _add_journal_event(mem, "💬", "chat", "Bạn kể Cừu nghe", _text[:60])
            check_achievements(mem)
            _save()
            st.rerun()


# ═══════════════════════════════════════════════════════
# TAB 2 — NHẬT KÝ CỦA CHÚNG TA
# ═══════════════════════════════════════════════════════
with tab2:

    diary_left, diary_right = st.columns([3, 2], gap="medium")

    # ══════════════════════════════════════════
    # LEFT: Write diary
    # ══════════════════════════════════════════
    with diary_left:
        _diary_src = _b64(_pick_mascot("diary"))
        st.markdown(
            f'<div style="text-align:center;margin-bottom:10px;">'
            f'<img src="{_diary_src}" width="120" style="border-radius:50%;'
            f'border:4px solid #FFB5C8;box-shadow:0 8px 24px rgba(255,140,190,0.35);" />'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Post-save state
        if st.session_state.get("diary_just_saved") and st.session_state.get("diary_last_entry"):
            _entry = st.session_state.diary_last_entry
            _cel_src = _b64(_pick_mascot("celebrate"))
            st.markdown(
                f'<div class="insight-card-v4" style="text-align:center;">'
                f'<div class="insight-sheep-label">🐑 Hôm nay mình hiểu thêm về bạn</div>'
                f'<img src="{_cel_src}" width="70" style="border-radius:50%;'
                f'border:3px solid #FFB5C8;margin:8px 0;" />'
                f'<div class="insight-text">{_entry.get("sheep_reply","Cừu đọc rồi nhé 💙")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("✍️ Viết thêm trang mới", type="primary", use_container_width=True):
                st.session_state.diary_just_saved = False
                st.session_state.diary_last_entry = None
                st.rerun()
        else:
            # Mood chips
            _MOOD_CHIPS = [
                ("😊", "Rất vui"), ("😌", "Bình yên"), ("😔", "Hơi buồn"),
                ("😤", "Bực bội"), ("😰", "Áp lực"),  ("🌟", "Quyết tâm"),
            ]
            st.markdown(
                '<div style="font-size:0.87rem;font-weight:700;color:#C4607F;margin-bottom:6px;">'
                'Hôm nay bạn đang cảm thấy thế nào?</div>',
                unsafe_allow_html=True,
            )
            _mood_cols = st.columns(3)
            for _mi, (_micon, _mname) in enumerate(_MOOD_CHIPS):
                _is_sel = st.session_state.get("diary_mood_sel") == _mname
                _mbtn_style = "primary" if _is_sel else "secondary"
                if _mood_cols[_mi % 3].button(
                    f"{_micon} {_mname}", key=f"dmood_{_mi}",
                    type=_mbtn_style, use_container_width=True,
                ):
                    st.session_state.diary_mood_sel = _mname
                    st.rerun()

            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

            # 3 guided prompts
            _DIARY_PROMPTS = [
                "📌 Hôm nay có điều gì xảy ra khiến bạn ấn tượng nhất?",
                "💭 Bạn đang nghĩ gì hoặc cảm thấy điều gì?",
                "🌱 Có điều gì bạn muốn nhớ lại hoặc làm khác đi không?",
            ]
            _dq_texts = []
            for _pi, _prompt in enumerate(_DIARY_PROMPTS):
                st.markdown(
                    f'<div style="background:rgba(255,240,200,0.45);border-left:3px solid #FFB5C8;'
                    f'border-radius:0 10px 10px 0;padding:8px 14px;margin:10px 0 4px;'
                    f'font-size:0.88rem;font-weight:700;color:#C4607F;">{_prompt}</div>',
                    unsafe_allow_html=True,
                )
                _dq_texts.append(
                    st.text_area("", height=80, key=f"dq{_pi}", label_visibility="collapsed",
                                 placeholder="Viết thứ gì đó cho Cừu nghe...")
                )

            _diary_content = "\n\n".join(t for t in _dq_texts if t.strip())
            _diary_mood    = st.session_state.get("diary_mood_sel", "") or ""

            if st.button("🐑 Gửi cho Cừu", type="primary", use_container_width=True):
                if _diary_content.strip():
                    _combined = f"[Cảm xúc: {_diary_mood}]\n{_diary_content}" if _diary_mood else _diary_content
                    with st.spinner("🐑 Cừu đang đọc..."):
                        _dresult = _call_llm(_combined, _SYS_DIARY)

                    _entry = {
                        "date_raw":    datetime.now().isoformat(),
                        "date_display": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "mood":        _diary_mood,
                        "content":     _diary_content,
                        "sheep_reply": _dresult.get("sheep_reply", "Cừu đọc rồi nhé 💙"),
                        "tags":        _dresult.get("tags", []),
                        "dream":       _dresult.get("dream_detected", ""),
                    }
                    mem["diary_entries"].append(_entry)

                    # Update memory from diary
                    for _tag in _dresult.get("tags", []):
                        if _tag and _tag not in mem["life_events"]:
                            mem["life_events"].append(_tag)
                    if _dn := _dresult.get("dream_detected"):
                        if _dn not in [d["name"] for d in mem["dreams"]]:
                            mem["dreams"].append({"name": _dn, "amount": 0, "saved": 0, "tags": []})

                    # XP + journal + achievement
                    add_xp("diary", mem, f"Trang nhật ký {len(mem['diary_entries'])}")
                    _add_journal_event(mem, "📔", "diary",
                                       f"Viết nhật ký — {_diary_mood or 'cảm xúc của hôm nay'}",
                                       _diary_content[:60])
                    check_achievements(mem)
                    set_mood(_dresult.get("mood", "listening"))

                    st.session_state.diary_just_saved = True
                    st.session_state.diary_last_entry  = _entry
                    st.session_state.diary_mood_sel    = None
                    _save()
                    st.rerun()
                else:
                    st.warning("Viết gì đó để Cừu đọc nhé 🐑")

    # ══════════════════════════════════════════
    # RIGHT: Journal timeline
    # ══════════════════════════════════════════
    with diary_right:
        _journal = mem.get("journal_timeline", [])
        _diary_entries = mem.get("diary_entries", [])

        if not _journal and not _diary_entries:
            st.markdown(
                '<div style="text-align:center;padding:40px 20px;">'
                '<div style="font-size:2rem;">🌱</div>'
                '<div style="font-size:0.9rem;color:#BBB;margin-top:8px;">'
                'Trang đầu tiên đang chờ bạn.<br/>Kể Cừu nghe điều gì đó nhé~</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:0.87rem;font-weight:700;color:#C4607F;margin-bottom:10px;">'
                '📖 Nhật ký của chúng ta</div>',
                unsafe_allow_html=True,
            )

            # Build combined timeline (journal + diary entries with display)
            _all_events: list[dict] = []

            # From journal_timeline
            for ev in _journal:
                _all_events.append(ev)

            # Diary entries that might not be in journal
            for de in _diary_entries:
                if not any(e.get("type") == "diary" and
                           e.get("date_raw", "")[:10] == de["date_raw"][:10]
                           for e in _journal):
                    _all_events.append({
                        "date_raw":     de["date_raw"],
                        "date_display": datetime.fromisoformat(de["date_raw"]).strftime("%d/%m"),
                        "icon": "📔", "type": "diary",
                        "title": f"Nhật ký — {de.get('mood', 'cảm xúc hôm nay')}",
                        "detail": de["content"][:60],
                    })

            # Sort newest first
            _all_events.sort(key=lambda e: e.get("date_raw", ""), reverse=True)

            _prev_date = ""
            for ev in _all_events[:40]:
                _ev_date = ev.get("date_display", "")
                if _ev_date != _prev_date:
                    st.markdown(
                        f'<div style="margin-top:12px;">'
                        f'<span class="journal-date-chip">{_ev_date}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    _prev_date = _ev_date

                _ev_icon   = ev.get("icon", "📌")
                _ev_title  = ev.get("title", "")
                _ev_detail = ev.get("detail", "")

                # Color border by type
                _border_color = {
                    "chat":        "#7EC8E3",
                    "diary":       "#FFB5C8",
                    "save":        "#90E0A0",
                    "level_up":    "#C8A8FF",
                    "achievement": "#FFD700",
                    "dream":       "#FFA8C8",
                    "goal":        "#FFB060",
                }.get(ev.get("type", ""), "#FFB5C8")

                st.markdown(
                    f'<div style="background:white;border-left:3px solid {_border_color};'
                    f'border-radius:0 12px 12px 0;padding:9px 13px;margin:3px 0 6px;'
                    f'box-shadow:0 2px 6px rgba(0,0,0,0.05);">'
                    f'<div style="font-size:0.88rem;font-weight:600;color:#444;">'
                    f'{_ev_icon} {_ev_title}</div>'
                    + (f'<div style="font-size:0.75rem;color:#AAA;margin-top:2px;">{_ev_detail}</div>'
                       if _ev_detail else "")
                    + f'</div>',
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════════════════
# TAB 3 — NHÀ CỦA CỪU (Gamification)
# ═══════════════════════════════════════════════════════
with tab3:

    house_left, house_right = st.columns([2, 3], gap="medium")

    # ══════════════════════════════════════════
    # LEFT: Sheep + Level + XP breakdown
    # ══════════════════════════════════════════
    with house_left:
        _h_lv  = mem.get("level", 1)
        _h_xp  = mem.get("xp", 0)
        _h_key, _h_name = stage_from_level(_h_lv)
        _h_src = _b64(_pick_mascot(_h_key))
        _, _xp_in_lv, _xp_pct = xp_progress(_h_xp)
        _next_lv_xp = LEVEL_THRESHOLDS[_h_lv] if _h_lv < 20 else 0
        _cur_lv_xp  = LEVEL_THRESHOLDS[_h_lv - 1]

        st.markdown(
            f'<div style="text-align:center;padding:10px 0 6px;">'
            f'<img src="{_h_src}" width="200" style="border-radius:50%;'
            f'border:5px solid #FFB5C8;'
            f'box-shadow:0 12px 36px rgba(255,140,190,0.55),'
            f'0 0 0 10px rgba(255,182,193,0.2);" />'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="text-align:center;margin-top:8px;">'
            f'<span class="xp-level-badge">Level {_h_lv}</span>'
            f'<div style="font-size:1.05rem;font-weight:800;color:#C4607F;margin-top:6px;">'
            f'{_h_name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        if _h_lv < 20:
            st.progress(
                _xp_pct,
                text=f"🎯 Chỉ cần thêm {_next_lv_xp - _h_xp} XP để lên Level {_h_lv + 1}!",
            )
        else:
            st.progress(1.0, text="🏆 Đã đạt Level tối đa!")

        # XP sources breakdown
        st.markdown(
            '<div style="font-size:0.85rem;font-weight:700;color:#C4607F;margin:14px 0 6px;">'
            '🍀 Cách Cừu lớn lên</div>',
            unsafe_allow_html=True,
        )
        _xp_sources_info = [
            ("💬", "Tâm sự với Cừu",   "+5 XP mỗi tin nhắn",  "chat"),
            ("📔", "Viết nhật ký",      "+10 XP mỗi trang",    "diary"),
            ("🎯", "Hoàn thành mục tiêu", "+20 XP mỗi lần",    "goal"),
            ("💰", "Tích lũy / đầu tư", "+30 XP mỗi lần",     "save"),
        ]
        for _icon, _sname, _sdesc, _skey in _xp_sources_info:
            st.markdown(
                f'<div class="xp-source-row">'
                f'<div class="xp-source-icon">{_icon}</div>'
                f'<div class="xp-source-info">'
                f'<div class="xp-source-name">{_sname}</div>'
                f'<div class="xp-source-sub">{_sdesc}</div>'
                f'</div>'
                f'<div class="xp-source-val">{XP_SOURCES.get(_skey, 0)} XP</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Feed sheep (mini, for XP)
        st.markdown(
            '<div style="font-size:0.85rem;font-weight:700;color:#C4607F;margin:14px 0 6px;">'
            '🍽️ Cho Cừu ăn hôm nay</div>',
            unsafe_allow_html=True,
        )

        # Feeding celebration
        if st.session_state.get("feeding_celebration"):
            _fc_amt  = mem.get("last_fed_amount", 0)
            _fc_food = mem.get("last_fed_food", "")
            _fc_lv   = mem.get("just_leveled_up", False)
            _fc_src  = _b64(_pick_mascot("celebrate"))
            _fc_label = _fc_food if _fc_food else fmt(_fc_amt)

            _dream_lnk = ""
            if mem["dreams"]:
                _fd = mem["dreams"][0]
                _dream_lnk = (
                    f'<div style="font-size:0.83rem;color:#B8860B;'
                    f'background:rgba(255,215,0,0.15);border-radius:8px;'
                    f'padding:6px 10px;margin-top:8px;">'
                    f'✨ Giấc mơ <strong>{_fd["name"].title()}</strong> '
                    f'vừa tiến thêm <strong>{fmt(_fc_amt)}</strong>~</div>'
                )

            _lv_html = ""
            if _fc_lv:
                _, _new_lv_name = stage_from_level(mem.get("level", 1))
                _lv_html = (
                    f'<div style="font-size:1rem;font-weight:800;color:#C4607F;margin-top:8px;">'
                    f'🎊 Cừu vừa lên Level {mem["level"]}! Chào mừng {_new_lv_name}!</div>'
                )

            st.markdown(
                f'<div class="celebration-box">'
                f'<img src="{_fc_src}" width="80" style="border-radius:50%;'
                f'border:3px solid #FFB5C8;" />'
                f'<div style="font-size:1rem;font-weight:700;color:#C4607F;margin-top:8px;">'
                f'Cừu được ăn {_fc_label} rồi! Bê bê cảm ơn ❤️</div>'
                f'{_dream_lnk}{_lv_html}'
                f'</div>',
                unsafe_allow_html=True,
            )
            mem["just_leveled_up"] = False
            mem["last_fed_amount"] = 0
            mem["last_fed_food"]   = ""
            st.session_state.feeding_celebration = False
            _save()
            st.balloons()

        if st.session_state.get("feeding_refused"):
            st.markdown(
                '<div style="background:linear-gradient(135deg,#F0F8FF,#EAF4FF);'
                'border-radius:14px;padding:14px;text-align:center;">'
                '<div style="font-size:0.9rem;color:#5B8DB8;font-weight:700;">Không sao cả 🌙</div>'
                '<div style="font-size:0.82rem;color:#6A9BBF;margin-top:4px;">'
                'Mình vẫn ở đây. Hôm nào sẵn sàng thì mình đợi~ 🐑</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.session_state.feeding_refused = False

        _feed_cols_h = st.columns(2)
        _FEED_OPTIONS = [
            (10_000,  "🥕", "Bữa ăn nhỏ"),
            (20_000,  "🍎", "Đủ no"),
            (50_000,  "🎂", "Tiệc nhỏ"),
            (100_000, "🎉", "Đại tiệc"),
        ]
        for _fi, (_famt, _femo, _fname) in enumerate(_FEED_OPTIONS):
            if _feed_cols_h[_fi % 2].button(
                f"{_femo} {_fname}\n{fmt(_famt)}",
                key=f"h3_feed_{_famt}", use_container_width=True,
                type="primary",
            ):
                _prev_stage = mem.get("level", 1)
                mem["total_saved"]    += _famt
                mem["streak"]         += 1
                mem["last_fed_amount"] = _famt
                mem["last_fed_food"]   = f"{_femo} {_fname}"
                mem["last_fed_date"]   = datetime.now().strftime("%Y-%m-%d")
                add_xp("save", mem, f"{_femo} {_fname} — {fmt(_famt)}")
                # Update dream saved
                if mem["dreams"]:
                    mem["dreams"][0]["saved"] = min(
                        mem["dreams"][0].get("amount", 0),
                        mem["dreams"][0].get("saved", 0) + _famt,
                    )
                check_achievements(mem)
                set_mood("happy")
                st.session_state.feeding_celebration = True
                st.session_state.feeding_refused     = False
                _save()
                st.rerun()

        if st.button("🌙 Hôm nay chưa sẵn sàng", use_container_width=True):
            set_mood("sad")
            st.session_state.feeding_refused     = True
            st.session_state.feeding_celebration = False
            _save()
            st.rerun()

    # ══════════════════════════════════════════
    # RIGHT: Achievements + Stage map
    # ══════════════════════════════════════════
    with house_right:
        st.markdown(
            '<div style="font-size:0.95rem;font-weight:800;color:#C4607F;margin-bottom:12px;">'
            '🏅 Bộ Sưu Tập Thành Tựu</div>',
            unsafe_allow_html=True,
        )

        _unlocked = set(mem.get("achievements", []))
        _all_ach_keys = list(ACHIEVEMENTS.keys())

        # Show in 4-col grid
        _ach_n_cols = 4
        _ach_rows = [_all_ach_keys[i:i+_ach_n_cols]
                     for i in range(0, len(_all_ach_keys), _ach_n_cols)]

        for _row in _ach_rows:
            _rcols = st.columns(_ach_n_cols)
            for _ci, _akey in enumerate(_row):
                _aicon, _aname, _adesc = ACHIEVEMENTS[_akey]
                _is_ul = _akey in _unlocked
                _locked_class = "" if _is_ul else " locked"
                _rcols[_ci].markdown(
                    f'<div class="ach-card{_locked_class}">'
                    f'<span class="ach-icon">{_aicon}</span>'
                    f'<div class="ach-name">{_aname}</div>'
                    f'<div class="ach-desc">{_adesc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Stats summary
        st.markdown("---")
        _total_ach = len(_unlocked)
        _total_all = len(ACHIEVEMENTS)
        st.progress(_total_ach / _total_all, text=f"🏅 {_total_ach}/{_total_all} thành tựu")

        # Stage roadmap
        st.markdown(
            '<div style="font-size:0.87rem;font-weight:700;color:#C4607F;margin:16px 0 8px;">'
            '🗺️ Hành trình trưởng thành của Cừu</div>',
            unsafe_allow_html=True,
        )
        _ROADMAP = [
            (1,  "baby",   "🐑 Cừu Sơ Sinh",      "Level 1–3",  "Vừa ra đời, còn nhút nhát."),
            (4,  "child",  "🐑 Cừu Non",           "Level 4–6",  "Đang học cách lớn lên."),
            (7,  "teen",   "🐑 Cừu Thiếu Niên",    "Level 7–10", "Bắt đầu có ước mơ lớn."),
            (11, "adult",  "🐑 Cừu Trưởng Thành",  "Level 11–15","Hiểu mình và biết mình muốn gì."),
            (16, "master", "🐑 Cừu Lão Luyện",     "Level 16–20","Người đồng hành đáng tin cậy."),
        ]
        _current_stage_key = stage_from_level(mem.get("level", 1))[0]
        for _rlv, _rkey, _rname, _rlv_range, _rdesc in _ROADMAP:
            _is_cur = _rkey == _current_stage_key
            _is_done = mem.get("level", 1) > (_rlv + 3)
            _bg    = "linear-gradient(135deg,#FFF0F5,#FFE4F0)" if _is_cur else ("#F8F8F8" if _is_done else "#FAFAFA")
            _bdr   = "2px solid #FFB5C8" if _is_cur else ("1.5px solid #E0E0E0" if _is_done else "1.5px dashed #E0CCF0")
            _op    = "0.65" if (_is_done and not _is_cur) else "1"
            _prefix = "▶ " if _is_cur else ("✅ " if _is_done else "🔒 ")
            st.markdown(
                f'<div style="background:{_bg};border:{_bdr};border-radius:12px;'
                f'padding:10px 14px;margin:5px 0;opacity:{_op};">'
                f'<div style="font-size:0.82rem;font-weight:800;color:#C4607F;">'
                f'{_prefix}{_rname} <span style="color:#AAA;font-weight:400;font-size:0.72rem;">({_rlv_range})</span></div>'
                f'<div style="font-size:0.73rem;color:#888;margin-top:2px;">{_rdesc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Total saved summary
        if mem.get("total_saved", 0) > 0:
            st.markdown("---")
            _ts = mem.get("total_saved", 0)
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#F0FFF5,#F0F5FF);'
                f'border:1.5px solid #90E0A0;border-radius:14px;padding:12px 16px;">'
                f'<div style="font-size:0.83rem;font-weight:700;color:#3A8A5A;">💰 Tổng đã tích lũy</div>'
                f'<div style="font-size:1.4rem;font-weight:800;color:#2A6A3A;margin-top:4px;">'
                f'{fmt(_ts)}</div>'
                f'<div style="font-size:0.72rem;color:#AAA;margin-top:2px;">'
                f'Cừu lớn lên nhờ bạn chăm sóc ❤️</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ── Run achievement check on each render ──
check_achievements(mem)
_save()
