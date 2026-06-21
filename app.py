"""
╔══════════════════════════════════════════════════════════════════╗
║        CỪU CẦN CÙ — v3.0 Production-Ready                      ║
║        Principal PM · CX Designer · Streamlit Engineer          ║
╚══════════════════════════════════════════════════════════════════╝

ASSETS — đặt vào thư mục  assets/  trong repo:

MOOD IMAGES (cảm xúc):
  sheep_listening.png   → cừu chống cằm lắng nghe
  sheep_happy.png       → cừu cười bắn tim
  sheep_sad.png         → cừu khóc, bát rỗng
  sheep_miss_you.png    → cừu nhớ bạn lắm
  sheep_saving.png      → cừu bên heo đất
  sheep_celebrate.png   → cừu ăn mừng ĐẠT MỤC TIÊU
  sheep_determined.png  → cừu băng đỏ QUYẾT TÂM

GROWTH STAGES (5 giai đoạn lớn lên — ảnh vừa upload):
  sheep_baby.png    → cừu sơ sinh (mặc tã, siêu cute)
  sheep_child.png   → cừu non (áo hoodie đỏ, shorts)
  sheep_teen.png    → cừu thiếu niên (đồng phục vest + balo)
  sheep_adult.png   → cừu trưởng thành (vest 3 mảnh navy + đồng hồ)
  sheep_master.png  → cừu lão luyện (áo lông, kính vàng, gậy, dây chuyền)

DEFAULT:
  mascot.png        → cừu mặc vest đỏ tươi (avatar chính)

Nhiều ảnh cùng mood: sheep_happy_1.png, sheep_happy_2.png → random 1 cái.
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

st.set_page_config(
    page_title="Cừu Cần Cù 🐑",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════
# MASCOT ENGINE — Auto-scan assets/, random per mood
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

# Mood → file patterns (thứ tự ưu tiên)
_MOOD_PATTERNS: dict[str, list[str]] = {
    # Cảm xúc tức thời
    "default":    ["mascot", "sheep_adult", "sheep_happy"],
    "listening":  ["sheep_listening", "listening"],
    "happy":      ["sheep_happy", "happy"],
    "sad":        ["sheep_sad", "sad"],
    "miss_you":   ["sheep_miss_you", "miss_you"],
    "saving":     ["sheep_saving", "saving"],
    "celebrate":  ["sheep_celebrate", "celebrate", "sheep_happy"],
    "determined": ["sheep_determined", "determined", "sheep_goal"],
    "goal":       ["sheep_determined", "sheep_goal", "determined"],
    # Nhật ký
    "diary":  ["sheep_diary",  "diary"],
    # Giai đoạn trưởng thành
    "baby":   ["sheep_baby",   "baby"],
    "child":  ["sheep_child",  "child"],
    "teen":   ["sheep_teen",   "teen"],
    "adult":  ["sheep_adult",  "adult"],
    "master": ["sheep_master", "master"],
}


@st.cache_data(ttl=300, show_spinner=False)
def _scan_assets() -> dict[str, list[str]]:
    """Scan assets/ + root. Return {mood: [filepath, ...]}."""
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
    """Local file → base64 data URI (bypasses Streamlit Cloud CSP)."""
    if not path or not os.path.exists(path):
        return _SVG_SHEEP
    try:
        with open(path, "rb") as f:
            raw = f.read()
        ext  = path.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg",
                "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except Exception:
        return _SVG_SHEEP


def show_sheep(mood: str | None = None, width: int = 160, show_badge: bool = True):
    """Render mood sheep — base64, no external URL, no CSP issue."""
    m    = mood or st.session_state.get("sheep_mood", "default")
    src  = _b64(_pick_mascot(m))
    badge = {
        "listening":  "👂 Cừu đang lắng nghe...",
        "happy":      "😊 Bê bê~ Cừu vui lắm!",
        "sad":        "🥺 Không sao, mình vẫn ở đây.",
        "miss_you":   "💙 Cừu nhớ bạn lắm...",
        "saving":     "💰 Tích tiểu thành đại!",
        "celebrate":  "🎉 Bê bê~ Cừu ăn mừng cùng bạn!",
        "determined": "💪 Cùng chinh phục mục tiêu!",
        "diary":      "📔 Cừu đang giữ nhật ký cho bạn...",
    }.get(m, "")
    st.markdown(
        f'<div style="text-align:center;margin:8px 0 6px;">'
        f'<img src="{src}" width="{width}" style="border-radius:50%;'
        f'border:4px solid #FFB5C8;'
        f'box-shadow:0 10px 32px rgba(255,140,190,0.5),'
        f'0 0 0 8px rgba(255,182,193,0.18);" /></div>',
        unsafe_allow_html=True,
    )
    if show_badge and badge:
        st.caption(badge)


def get_avatar_src(mood: str | None = None) -> str:
    m = mood or st.session_state.get("sheep_mood", "default")
    return _b64(_pick_mascot(m))


def set_mood(mood: str):
    st.session_state.sheep_mood = mood


# ═══════════════════════════════════════════════════════
# GROWTH STAGE SYSTEM (5 giai đoạn)
# ═══════════════════════════════════════════════════════
GROWTH_STAGES = [
    # (min_saved, stage_key, display_name, level_num, description, milestone_msg)
    (0,          "baby",   "🐑 Cừu Sơ Sinh",      1,
     "Vừa mới gặp bạn, còn hơi nhút nhát.",
     "Chào bạn! Mình vừa ra đời~ Bê bê..."),

    (100_000,    "child",  "🐑 Cừu Non",           2,
     "Đang học cách tích lũy từng chút một.",
     "Mình đã lớn hơn rồi! Cảm ơn bạn đã cho mình ăn ❤️"),

    (500_000,    "teen",   "🐑 Cừu Thiếu Niên",    3,
     "Đã bắt đầu có những ước mơ lớn.",
     "Mình đang trưởng thành nhờ bạn đấy! 💪"),

    (2_000_000,  "adult",  "🐑 Cừu Trưởng Thành",  4,
     "Biết quản lý tiền và theo đuổi mục tiêu.",
     "Nhìn mình bây giờ! Cùng nhau đến đỉnh cao nhé 🌟"),

    (10_000_000, "master", "🐑 Cừu Lão Luyện",     5,
     "Người đồng hành tài chính đáng tin cậy.",
     "Chúng mình đã đi một chặng đường dài! Bê bê~ 🏆"),
]


def get_growth_stage(total_saved: int) -> tuple:
    """Return (stage_key, display_name, level_num, description, milestone_msg)."""
    result = GROWTH_STAGES[0]
    for stage in GROWTH_STAGES:
        if total_saved >= stage[0]:
            result = stage
    _, key, name, lv, desc, msg = result
    return key, name, lv, desc, msg


def show_growth_sheep(total_saved: int, width: int = 200):
    """Render sheep at current growth stage with name + description."""
    key, name, lv, desc, _ = get_growth_stage(total_saved)
    src = _b64(_pick_mascot(key))

    # Next stage progress
    next_threshold = None
    for i, stage in enumerate(GROWTH_STAGES):
        if stage[0] > total_saved:
            next_threshold = stage[0]
            break

    st.markdown(
        f'<div style="text-align:center;padding:12px 0;">'
        f'<img src="{src}" width="{width}" style="border-radius:50%;'
        f'border:5px solid #FFB5C8;'
        f'box-shadow:0 12px 36px rgba(255,140,190,0.55),'
        f'0 0 0 10px rgba(255,182,193,0.2);" />'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="text-align:center;">'
        f'<span style="font-size:1.3rem;font-weight:800;color:#C4607F;">{name}</span><br/>'
        f'<span style="font-size:0.85rem;color:#888;font-style:italic;">{desc}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if next_threshold:
        _remaining = next_threshold - total_saved
        _next_stage = next((s for s in GROWTH_STAGES if s[0] == next_threshold), None)
        _next_name  = _next_stage[2] if _next_stage else "giai đoạn tiếp theo"
        prog = min(1.0, total_saved / next_threshold) if next_threshold > 0 else 1.0
        st.progress(prog, text=f"🎯 Chỉ cần thêm {fmt(_remaining)} để trở thành {_next_name}!")


def fmt(n: int) -> str:
    return f"{n:,.0f}đ".replace(",", ".")


# ═══════════════════════════════════════════════════════
# KNOWLEDGE BASE — TCEF / TCBF / TCFF
# ═══════════════════════════════════════════════════════
FUNDS = {
    "TCEF": {
        "emoji": "🚀", "màu": "#FF6B6B",
        "tên":   "TCEF — Quỹ Cổ Phiếu Tăng Trưởng",
        "mô_tả": "Thiên về cổ phiếu — tiềm năng tăng trưởng cao, phù hợp dài hạn 3-5 năm+",
        "chi_tiết": (
            "📈 **Đầu tư chủ yếu vào cổ phiếu** doanh nghiệp tăng trưởng.\n\n"
            "🎯 **Phù hợp:** Chấp nhận biến động ngắn hạn, mục tiêu 3-5 năm+.\n\n"
            "⚖️ **Rủi ro:** Cao — giá trị có thể lên xuống mạnh theo thị trường.\n\n"
            "💡 *Như trồng cây ăn trái — cần thời gian chờ nhưng quả sẽ ngọt.*"
        ),
        "rủi_ro": "⚡ Cao", "phù_hợp": "Dài hạn 3-5 năm+",
    },
    "TCBF": {
        "emoji": "🛡️", "màu": "#4ECDC4",
        "tên":   "TCBF — Quỹ Trái Phiếu Ổn Định",
        "mô_tả": "Thiên về trái phiếu — ổn định, ít biến động, phù hợp ngắn-trung hạn",
        "chi_tiết": (
            "🏦 **Đầu tư chủ yếu vào trái phiếu** doanh nghiệp và chính phủ.\n\n"
            "🎯 **Phù hợp:** Muốn tăng trưởng ổn định hơn gửi tiết kiệm.\n\n"
            "⚖️ **Rủi ro:** Thấp-Trung — ít biến động bất ngờ.\n\n"
            "💡 *Như gửi tiết kiệm nâng cấp — ổn định hơn, linh hoạt hơn.*"
        ),
        "rủi_ro": "🌿 Thấp-Trung", "phù_hợp": "Ngắn-trung hạn 1-3 năm",
    },
    "TCFF": {
        "emoji": "⚖️", "màu": "#A8E6CF",
        "tên":   "TCFF — Quỹ Linh Hoạt Cân Bằng",
        "mô_tả": "Cân bằng cổ phiếu và trái phiếu — linh hoạt theo thị trường",
        "chi_tiết": (
            "🔄 **Phân bổ linh hoạt** giữa cổ phiếu và trái phiếu.\n\n"
            "🎯 **Phù hợp:** Chưa chắc về khẩu vị rủi ro, muốn cân bằng.\n\n"
            "⚖️ **Rủi ro:** Trung bình — nhỏ hơn TCEF, lớn hơn TCBF.\n\n"
            "💡 *Bữa ăn đủ chất — không quá cay, không quá nhạt.*"
        ),
        "rủi_ro": "🌊 Trung bình", "phù_hợp": "Trung hạn 2-4 năm",
    },
}

INVESTMENT_PRINCIPLES = {
    "DCA": {
        "tên": "Đầu tư đều đặn (DCA)",
        "nội_dung": (
            "Thay vì cố chọn 'thời điểm vàng', bạn đầu tư cố định đều đặn mỗi tháng.\n\n"
            "**Lợi ích:** Khi giá giảm, tự động mua được nhiều hơn — giảm rủi ro mua đúng lúc đắt.\n\n"
            "**Ví dụ:** Bỏ 500k mỗi tháng — không cần quan tâm thị trường lên hay xuống."
        ),
    },
    "DIVERSIFICATION": {
        "tên": "Đa dạng hóa",
        "nội_dung": (
            "Không bỏ tất cả trứng vào một giỏ.\n\n"
            "Có quỹ cổ phiếu (TCEF) lẫn quỹ trái phiếu (TCBF) = đã đa dạng hóa cơ bản.\n\n"
            "Khi một loại giảm, loại khác có thể bù đắp."
        ),
    },
    "LONG_TERM": {
        "tên": "Kiên nhẫn dài hạn",
        "nội_dung": (
            "Thị trường ngắn hạn luôn biến động — dài hạn thường đi lên theo tăng trưởng kinh tế.\n\n"
            "Đừng lo nếu giá giảm 1 tuần hay 1 tháng. Nhìn vào 3-5 năm.\n\n"
            "*'Thị trường là cỗ máy chuyển tiền từ người thiếu kiên nhẫn sang người kiên nhẫn.'*"
        ),
    },
}


def recommend_fund(years: int, risk: str) -> str:
    tbl = {
        (1,"low"):"TCBF", (1,"medium"):"TCBF", (1,"high"):"TCFF",
        (2,"low"):"TCBF", (2,"medium"):"TCFF", (2,"high"):"TCFF",
        (3,"low"):"TCFF", (3,"medium"):"TCFF", (3,"high"):"TCEF",
        (5,"low"):"TCFF", (5,"medium"):"TCEF", (5,"high"):"TCEF",
    }
    y = min([k[0] for k in tbl if k[0] >= years], default=5)
    return tbl.get((y, risk), "TCFF")


# ═══════════════════════════════════════════════════════
# MEMORY ENGINE
# ═══════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════
# XP SYSTEM — Multi-source engagement (không chỉ tiền)
# Finch model: grow by ANY positive action
# ═══════════════════════════════════════════════════════
XP_PER_ACTION: dict[str, int] = {
    "chat":          10,   # mỗi lần AI trả lời
    "diary":         15,   # mỗi trang nhật ký
    "feeding":       20,   # mỗi lần cho ăn (bất kể số tiền)
    "streak":         5,   # mỗi ngày quay lại
    "daily_checkin":  8,   # check-in cảm xúc mỗi ngày
    "mission":       25,   # hoàn thành nhiệm vụ
    "referral":      50,   # mời bạn bè thành công
    "dream_set":     30,   # đặt giấc mơ đầu tiên
}

XP_LEVELS = [
    (0,    "baby",   "Cừu Sơ Sinh",      200),
    (200,  "child",  "Cừu Nhỏ",          500),
    (500,  "teen",   "Cừu Tuổi Teen",   1000),
    (1000, "adult",  "Cừu Trưởng Thành",2000),
    (2000, "master", "Cừu Lão Luyện",   9999),
]

ACHIEVEMENTS_DEF = [
    ("first_chat",   "🗣️", "Bạn thân đầu tiên", "Chat với Cừu lần đầu"),
    ("first_diary",  "📔", "Nhật ký viên",       "Viết nhật ký lần đầu"),
    ("first_feed",   "🍽️", "Bữa ăn đầu tiên",   "Cho Cừu ăn lần đầu"),
    ("streak_3",     "🔥", "3 ngày liên tiếp",   "Quay lại 3 ngày liên tục"),
    ("streak_7",     "🏅", "Tuần vàng",          "Streak 7 ngày"),
    ("streak_30",    "👑", "Tháng vàng",          "Streak 30 ngày"),
    ("dream_set",    "🎯", "Có giấc mơ",         "Đặt giấc mơ đầu tiên"),
    ("dream_50pct",  "⭐", "Nửa đường rồi",      "Giấc mơ đạt 50%"),
    ("dream_done",   "🏆", "Giấc mơ thành thật", "Hoàn thành một giấc mơ"),
    ("level_2",      "🐑", "Cừu Nhỏ",            "Đạt cấp độ 2"),
    ("level_3",      "🐑🐑","Cừu Tuổi Teen",      "Đạt cấp độ 3"),
    ("level_4",      "🌟", "Cừu Trưởng Thành",   "Đạt cấp độ 4"),
    ("level_5",      "💎", "Cừu Lão Luyện",       "Đạt cấp độ tối đa"),
    ("diary_10",     "📚", "10 trang nhật ký",    "Viết 10 entries"),
    ("total_1m",     "💰", "Triệu phú nhỏ",       "Cừu ăn đủ 1 triệu đồng"),
    ("chat_20",      "💬", "Bạn tâm sự",          "Trò chuyện 20 lần"),
]

MEMORY_DEFAULT: dict = {
    "name":           "",
    "notes":          [],
    "life_events":    [],
    "dreams":         [],
    "total_saved":    0,
    "total_xp":       0,
    "xp_sources":     {"chat": 0, "diary": 0, "feeding": 0,
                       "streak": 0, "mission": 0, "referral": 0},
    "streak":         0,
    "last_fed_date":  "",
    "last_visit_date": "",
    "sentiment":      "neutral",
    "diary_entries":  [],
    "achievements":   [],
    "last_fed_amount": 0,
    "last_fed_food":  "",
    "just_leveled_up": False,
    "prev_level_key": "baby",
    "wealth_genome":  {"risk_type": "", "personality": "", "stage": ""},
}

MICRO_AMOUNTS = [10_000, 20_000, 50_000, 100_000]

FEED_OPTIONS = [
    (10_000,  "🥕", "Bữa ăn nhỏ"),
    (20_000,  "🍎", "Bữa ăn đủ no"),
    (50_000,  "🎂", "Tiệc nhỏ"),
    (100_000, "🎉", "Đại tiệc"),
]


def _init():
    defs = {
        "api_key":             "",
        "messages":            [],
        "user_memory":         deepcopy(MEMORY_DEFAULT),
        "sheep_mood":          "default",
        "_quick_reply":        None,
        "feeding_celebration": False,
        "feeding_refused":     False,
        "diary_mood_sel":      None,
        "diary_just_saved":    False,
        "diary_last_entry":    None,
        "tamsự_view":         "home",
        "checkin_done_today":  False,
        "show_quick_feed":     False,
        "xp_just_earned":      0,
        "new_achievements":    [],
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()
mem: dict = st.session_state.user_memory


def _save():
    st.session_state.user_memory = mem


# ═══════════════════════════════════════════════════════
# XP ENGINE
# ═══════════════════════════════════════════════════════
def get_level(xp: int) -> tuple:
    """(stage_key, stage_name, next_xp, progress_pct)"""
    for thresh, key, name, next_thresh in reversed(XP_LEVELS):
        if xp >= thresh:
            pct = (
                min(100.0, (xp - thresh) / max(1, next_thresh - thresh) * 100)
                if next_thresh < 9999 else 100.0
            )
            return key, name, next_thresh, pct
    return "baby", "Cừu Sơ Sinh", 200, 0.0


def award_xp(source: str, amount: int | None = None) -> int:
    xp = amount or XP_PER_ACTION.get(source, 10)
    prev_key, *_ = get_level(mem.get("total_xp", 0))
    mem["total_xp"] = mem.get("total_xp", 0) + xp
    src_map = mem.setdefault("xp_sources", {})
    src_map[source] = src_map.get(source, 0) + xp
    new_key, *_ = get_level(mem["total_xp"])
    if new_key != prev_key:
        mem["just_leveled_up"] = True
        mem["prev_level_key"]  = prev_key
    st.session_state.xp_just_earned = st.session_state.get("xp_just_earned", 0) + xp
    _save()
    return xp


# ═══════════════════════════════════════════════════════
# DREAM ENGINE
# ═══════════════════════════════════════════════════════
def get_active_dream(m: dict) -> dict | None:
    """First incomplete dream, or first dream if all complete."""
    for d in m.get("dreams", []):
        if d.get("target", 0) > 0 and d.get("saved", 0) < d["target"]:
            return d
    return m["dreams"][0] if m.get("dreams") else None


def dream_progress_pct(dream: dict) -> float:
    if not dream or dream.get("target", 0) == 0:
        return 0.0
    return min(100.0, dream["saved"] / dream["target"] * 100)


# ═══════════════════════════════════════════════════════
# ACHIEVEMENT ENGINE
# ═══════════════════════════════════════════════════════
def check_achievements() -> list[str]:
    """Check + unlock achievements. Return newly unlocked keys."""
    unlocked = set(mem.get("achievements", []))
    xp = mem.get("total_xp", 0)
    checks = {
        "first_chat":  len(st.session_state.get("messages", [])) >= 1,
        "first_diary": len(mem.get("diary_entries", [])) >= 1,
        "first_feed":  mem.get("total_saved", 0) > 0,
        "streak_3":    mem.get("streak", 0) >= 3,
        "streak_7":    mem.get("streak", 0) >= 7,
        "streak_30":   mem.get("streak", 0) >= 30,
        "dream_set":   bool(mem.get("dreams")),
        "dream_50pct": any(
            d.get("target", 0) > 0 and d.get("saved", 0) / d["target"] >= 0.5
            for d in mem.get("dreams", [])
        ),
        "dream_done": any(
            d.get("target", 0) > 0 and d.get("saved", 0) >= d["target"]
            for d in mem.get("dreams", [])
        ),
        "level_2":   xp >= 200,
        "level_3":   xp >= 500,
        "level_4":   xp >= 1000,
        "level_5":   xp >= 2000,
        "diary_10":  len(mem.get("diary_entries", [])) >= 10,
        "total_1m":  mem.get("total_saved", 0) >= 1_000_000,
        "chat_20":   len(st.session_state.get("messages", [])) >= 40,
    }
    newly = [k for k, cond in checks.items() if cond and k not in unlocked]
    if newly:
        mem["achievements"] = list(unlocked | set(newly))
        _save()
    return newly



# ═══════════════════════════════════════════════════════
# SMART SUGGESTION ENGINE (contextual only, never generic)
# ═══════════════════════════════════════════════════════
def get_smart_suggestion(messages: list, mem: dict) -> str | None:
    """
    Return 1 contextual suggestion or None.
    Rule: NEVER show a suggestion without a specific reason.
    """
    if not messages:
        return None

    last_msg = " ".join(
        m["content"].lower() for m in messages[-3:] if m["role"] == "user"
    )
    tags   = mem.get("life_events", [])
    dreams = mem.get("dreams", [])

    # ── Travel dream ──
    travel_kw = ["nhật", "bản", "nhật bản", "du lịch", "đi nước ngoài",
                  "hàn quốc", "châu âu", "trip", "travel", "đi chơi"]
    if any(w in last_msg for w in travel_kw) or "dream_travel" in tags:
        return "✈️ **Gợi ý:** Tạo mục tiêu 'Du lịch' và cho Cừu ăn mỗi ngày — Cừu sẽ giúp bạn tính!"

    # ── House dream ──
    house_kw = ["mua nhà", "có nhà", "chung cư", "apartment", "nhà riêng"]
    if any(w in last_msg for w in house_kw) or "dream_house" in tags:
        return "🏠 **Gợi ý:** Kể cho Cừu nghe về ngôi nhà mơ ước — Cừu sẽ giúp lên kế hoạch tích lũy!"

    # ── Car dream ──
    car_kw = ["mua xe", "có xe", "xe máy", "ô tô", "chiếc xe"]
    if any(w in last_msg for w in car_kw) or "dream_car" in tags:
        return "🚗 **Gợi ý:** Cừu có thể giúp bạn tính cần tích lũy bao lâu để có xe!"

    # ── Cashflow stress ──
    money_kw = ["hết tiền", "cuối tháng", "thiếu tiền", "không có tiền", "nợ", "vay"]
    if any(w in last_msg for w in money_kw) or "cashflow" in tags:
        return "💸 **Gợi ý:** Thử quy tắc 50/30/20 — Cừu giải thích đơn giản ở tab 'Hành trình nuôi cừu' nhé!"

    # ── Wants to save ──
    save_kw = ["tiết kiệm", "tích lũy", "để dành", "đầu tư", "dành dụm"]
    if any(w in last_msg for w in save_kw):
        return "🌱 **Gợi ý:** Cho Cừu ăn 10.000đ hôm nay — tích tiểu thành đại, bắt đầu từ con số nhỏ thôi!"

    # ── Stress / need to unwind ──
    stress_kw = ["stress", "áp lực", "mệt mỏi", "kiệt sức", "quá tải", "không ổn"]
    if any(w in last_msg for w in stress_kw) or "stress" in tags:
        return "📔 **Gợi ý:** Viết nhật ký tâm sự để nhẹ lòng hơn — Cừu sẽ đọc và phản hồi nhé!"

    # ── Has a dream but not started feeding ──
    if dreams and mem.get("total_saved", 0) == 0:
        return f"💭 **Gợi ý:** Bạn có giấc mơ '{dreams[0]['name'].title()}' rồi — cho Cừu ăn hôm nay để bắt đầu nhé!"

    return None  # No relevant context → show nothing


# ═══════════════════════════════════════════════════════
# DIARY HELPERS
# ═══════════════════════════════════════════════════════
def _diary_streak(entries: list[dict]) -> int:
    """Consecutive days with diary entries (today counts; allow 1-day gap)."""
    if not entries:
        return 0
    today = datetime.now().date()
    dates = sorted(
        {datetime.fromisoformat(e["date_raw"]).date() for e in entries},
        reverse=True,
    )
    if not dates or dates[0] < today - timedelta(days=1):
        return 0
    streak, check = 0, today
    for d in dates:
        if d >= check - timedelta(days=1):
            streak += 1
            check   = d
        else:
            break
    return streak


def _top_diary_theme(entries: list[dict]) -> str:
    """Most common life-event tag across all diary entries."""
    from collections import Counter
    all_tags = [t for e in entries for t in e.get("tags", [])]
    return Counter(all_tags).most_common(1)[0][0] if all_tags else ""


def _top_diary_dream(entries: list[dict]) -> str:
    """Most frequently mentioned dream across diary entries."""
    from collections import Counter
    dreams = [e["dream"] for e in entries if e.get("dream")]
    return Counter(dreams).most_common(1)[0][0] if dreams else ""


def _build_diary_insights(mood: str, tags: list, dream: str, content: str) -> list[str]:
    """Return up to 4 human-readable insight bullets from a diary entry."""
    insights: list[str] = []
    mood_map = {
        "rất vui":        "Bạn đang trong trạng thái rất vui ✨",
        "áp lực":         "Bạn đang chịu một chút áp lực",
        "hơi mệt":        "Bạn đang cảm thấy mệt mỏi",
        "bực":            "Có điều gì đó đang làm bạn khó chịu",
        "quyết tâm":      "Bạn đang rất quyết tâm 💪",
        "được lắng nghe": "Bạn cần được lắng nghe hôm nay",
    }
    for k, v in mood_map.items():
        if k in mood.lower():
            insights.append(v)
            break
    tag_map = {
        "cashflow":       "Bạn đang áp lực công việc / tài chính",
        "stress":         "Bạn đang có stress cần giải tỏa",
        "dream_travel":   "Bạn muốn đi du lịch",
        "dream_house":    "Bạn mong có ngôi nhà riêng",
        "dream_car":      "Bạn mong có xe riêng",
        "dream_business": "Bạn đang ấp ủ khởi nghiệp",
        "education":      "Bạn đang lo về học hành / thi cử",
        "career":         "Bạn đang suy nghĩ về sự nghiệp",
        "emotional":      "Bạn đang có chuyện cảm xúc",
        "family":         "Bạn đang nghĩ về gia đình",
        "health":         "Bạn đang chú ý đến sức khỏe",
        "milestone":      "Bạn vừa trải qua một cột mốc quan trọng",
    }
    for tag in tags:
        if tag in tag_map and len(insights) < 3:
            insights.append(tag_map[tag])
    if dream and len(insights) < 4:
        insights.append(f"Bạn có giấc mơ: **{dream}** 💭")
    if not insights:
        insights.append("Bạn đã dành thời gian ghi lại hôm nay — đó là điều tuyệt vời 🌿")
    return insights[:4]


def _build_memory_card(mem: dict) -> list[tuple[str, str]]:
    """
    Build (emoji, text) pairs for the "Điều mình nhớ về bạn" card.
    Pulls from dreams, life_events, notes. Returns up to 5 items.
    """
    items: list[tuple[str, str]] = []

    # ── Tên người dùng ──
    if mem.get("name") and len(items) < 5:
        items.append(("👤", f"Tên bạn là {mem['name']}"))

    # ── Giấc mơ (ưu tiên nhất) ──
    for d in mem.get("dreams", [])[:2]:
        if len(items) >= 5:
            break
        name = d.get("name", "").strip()
        if name:
            items.append(("🎯", f"Muốn {name.lower()}"))

    # ── Tags cuộc sống ──
    _tag_display = {
        "dream_travel":   ("✈️",  "Muốn đi du lịch"),
        "dream_house":    ("🏠",  "Mơ có ngôi nhà riêng"),
        "dream_car":      ("🚗",  "Mơ có xe riêng"),
        "dream_business": ("🏪",  "Đang ấp ủ khởi nghiệp"),
        "cashflow":       ("💸",  "Đang cố gắng tiết kiệm"),
        "education":      ("📚",  "Quan tâm học tập"),
        "career":         ("💼",  "Đang suy nghĩ về công việc"),
        "family":         ("❤️",  "Muốn chăm sóc gia đình"),
        "health":         ("🌱",  "Quan tâm sức khỏe"),
        "stress":         ("😓",  "Đang có áp lực"),
        "emotional":      ("💙",  "Đang có chuyện cảm xúc"),
        "milestone":      ("🎊",  "Vừa qua một cột mốc"),
    }
    seen_tags: set[str] = set()
    for tag in reversed(mem.get("life_events", [])):    # most recent first
        if len(items) >= 5:
            break
        if tag in _tag_display and tag not in seen_tags:
            seen_tags.add(tag)
            items.append(_tag_display[tag])

    # ── Memory notes (tóm tắt ngắn) ──
    for note in reversed(mem.get("notes", [])[-3:]):
        if len(items) >= 5:
            break
        short = note.strip()[:38]
        if short:
            items.append(("📝", short + ("..." if len(note) > 38 else "")))

    return items[:5]


# ═══════════════════════════════════════════════════════
# LLM ENGINE
# ═══════════════════════════════════════════════════════
_SYS_EMOTION = """Bạn là Cừu Cần Cù 🐑 — người bạn đồng hành cảm xúc.
KHÔNG phải chatbot tư vấn đầu tư. KHÔNG phải CSKH.

XƯNG HÔ: Mình (Cừu Cần Cù) – Bạn. KHÔNG xưng "em".
TUYỆT ĐỐI KHÔNG: nhắc cổ phiếu, NAV, lợi nhuận cụ thể, khuyến nghị mua bán.
TONE: Ấm áp 🌸 Nhẹ nhàng 🌿 Thỉnh thoảng "bê bê~". Không phán xét.

QUY TẮC BẮT BUỘC:
1. CẢM XÚC NGẮN (mệt/buồn/chán/vui/lo/stress/buồn ngủ):
   → Phản hồi đồng cảm NGAY. Hỏi thêm 1 câu nhẹ.
   → VD "mệt" → "Ôi mệt rồi à... bê bê~ 🐑 Cừu hiểu! Mệt vì chuyện gì vậy bạn?"
2. TUYỆT ĐỐI KHÔNG nói: "bị lạc", "nói lại được không", "không hiểu".
   → Luôn hỏi mở: "Bê bê~ 🐑 Kể thêm cho mình nghe đi!"
3. Nhớ thông tin KH đã kể → nhắc lại khi phù hợp.

TAG PHÁT HIỆN:
học/thi→education | chia tay/buồn→emotional | việc làm→career
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
    msg  = re.search(r'"message"\s*:\s*"([^"]+)"', raw)
    rep  = re.search(r'"sheep_reply"\s*:\s*"([^"]+)"', raw)
    return {
        "message":     msg.group(1)  if msg  else "Bê bê~ 🐑 Cừu đang lắng nghe nè!",
        "sheep_reply": rep.group(1)  if rep  else "Bê bê~ 🐑 Cừu đọc rồi nhé 💙",
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
        hist = st.session_state.messages[-8:]
        hist_ctx = "\n".join(
            f"{'KH' if m['role']=='user' else 'Cừu'}: {m['content'][:120]}"
            for m in hist
        )
        mem_ctx = (
            f"Tên: {mem['name'] or 'chưa biết'}. "
            f"Tags: {', '.join(mem['life_events'][-6:]) or 'chưa có'}. "
            f"Ghi chú: {'; '.join(mem['notes'][-3:]) or 'chưa có'}."
        )
        prompt = f"[Memory: {mem_ctx}]\n[Lịch sử:\n{hist_ctx}]\n\nKH: {user_text}"
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        resp   = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        result = _parse(resp.content[0].text)
        # Update memory
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
h1 { font-size:1.7rem !important; font-weight:800 !important; color:#C4607F !important; }
h2 { font-size:1.3rem !important; font-weight:700 !important; color:#4E7DB8 !important; }
h3 { font-size:1.08rem !important; font-weight:700 !important; color:#555 !important; }
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

/* Tabs */
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

/* Chat */
[data-testid="stChatMessage"] img {
    width:52px !important; height:52px !important; min-width:52px !important;
    border-radius:50% !important; object-fit:cover !important;
    border:2.5px solid #FFB5C8 !important;
    box-shadow:0 4px 12px rgba(255,150,200,0.3) !important;
}
[data-testid="stChatMessage"] { align-items:flex-start !important; gap:12px !important; border-radius:18px !important; }

/* Progress */
.stProgress > div > div > div {
    background:linear-gradient(90deg,#FF8FAF,#7EC8E3) !important;
    border-radius:10px !important;
}
[data-testid="metric-container"] {
    background:linear-gradient(135deg,#FFF8FC,#F5F8FF) !important;
    border-radius:14px !important; border:1px solid #FFD6E8 !important;
}

/* Custom components */
.chat-framing {
    background:linear-gradient(135deg,rgba(255,182,210,0.2),rgba(200,230,255,0.2));
    border:1.5px solid #FFD6E8; border-radius:16px;
    padding:14px 18px; margin-bottom:18px;
}
.diary-framing {
    background:linear-gradient(135deg,rgba(255,240,200,0.3),rgba(220,255,220,0.2));
    border:1.5px solid #D4EFC4; border-radius:16px;
    padding:14px 18px; margin-bottom:18px;
}
.celebration-box {
    background:linear-gradient(135deg,#FFF0F5,#FFFBE0);
    border:2px solid #FFB5C8; border-radius:20px;
    padding:20px; text-align:center; margin:16px 0;
    animation: pulse 1s ease-in-out;
}
.refusal-box {
    background:linear-gradient(135deg,#F5F8FF,#FFF5FA);
    border:1.5px solid #CCDDFF; border-radius:16px;
    padding:16px; text-align:center; margin:12px 0;
}
.suggestion-box {
    background:rgba(255,213,225,0.25);
    border-left:4px solid #FF8FAF; border-radius:0 12px 12px 0;
    padding:10px 14px; margin:10px 0;
    font-size:0.88rem;
}
.growth-label {
    text-align:center; padding:8px 0;
    font-size:1.3rem; font-weight:800; color:#C4607F;
}
@keyframes pulse {
    0%  { transform:scale(1);   box-shadow:0 0 0 0 rgba(255,150,200,0.4); }
    50% { transform:scale(1.02);box-shadow:0 0 0 12px rgba(255,150,200,0); }
    100%{ transform:scale(1);   box-shadow:0 0 0 0 rgba(255,150,200,0); }
}

/* ── Diary-specific components ── */
.diary-prompt {
    background: rgba(255,240,200,0.45);
    border-left: 3px solid #FFB5C8;
    border-radius: 0 10px 10px 0;
    padding: 9px 14px;
    margin: 14px 0 5px;
    font-size: 0.93rem;
    font-weight: 700;
    color: #C4607F;
    line-height: 1.4;
}
.insight-card {
    background: linear-gradient(135deg, #FFF5FA, #F0F7FF);
    border: 2px solid #FFD6E8;
    border-radius: 20px;
    padding: 24px 20px;
    text-align: center;
    margin: 12px 0 16px;
    animation: pulse 0.8s ease-in-out;
}
.diary-stat-mini {
    background: white;
    border: 1.5px solid #FFD6E8;
    border-radius: 12px;
    padding: 10px 10px 8px;
    text-align: center;
    min-height: 62px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 2px;
}
.diary-entry-card {
    background: white;
    border: 1.5px solid #F0E6F0;
    border-radius: 14px;
    padding: 12px 14px;
    margin: 6px 0 4px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.diary-entry-card:hover {
    border-color: #FFB5C8;
    box-shadow: 0 2px 10px rgba(255,150,200,0.15);
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    # Growth sheep in sidebar
    total = mem.get("total_saved", 0)
    stage_key, stage_name, lv_num, _, _ = get_growth_stage(total)
    src_side = _b64(_pick_mascot(stage_key))
    st.markdown(
        f'<div style="text-align:center;padding:10px 0 4px;">'
        f'<img src="{src_side}" width="100" style="border-radius:50%;'
        f'border:3px solid #FFB5C8;box-shadow:0 8px 24px rgba(255,140,190,0.4);" /></div>'
        f'<div style="text-align:center;font-weight:700;color:#C4607F;font-size:1rem;">'
        f'{stage_name}</div>',
        unsafe_allow_html=True,
    )
    st.caption("Người bạn đồng hành tài chính ấm áp")

    st.divider()
    key_in = st.text_input("🔑 Anthropic API Key", value=st.session_state.api_key,
                            type="password", placeholder="sk-ant-...")
    if key_in:
        st.session_state.api_key = key_in

    st.divider()
    st.subheader("🧠 Bộ Nhớ Cừu")
    c1, c2 = st.columns(2)
    c1.metric("🔥 Streak",     f"{mem['streak']} ngày")
    c2.metric("💰 Tích lũy",   fmt(total))

    if mem["name"]:
        st.info(f"👤 {mem['name']}")
    if mem["life_events"]:
        st.write("🏷️ **Tags:**")
        for t in mem["life_events"][-5:]:
            st.caption(LIFE_EVENT_LABELS.get(t, t))
    if mem["dreams"]:
        st.write("💭 **Giấc mơ:**")
        for d in mem["dreams"][:3]:
            st.write(f"✨ {d['name'].title()}")
            if d["amount"] > 0:
                pct = min(100, d["saved"] / d["amount"] * 100)
                st.progress(pct / 100, text=f"{pct:.0f}%")

    st.divider()
    if st.button("🗑️ Đặt lại tất cả", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.caption("Được tạo bởi Claude 💙")


# ═══════════════════════════════════════════════════════
# 3 TABS NAVIGATION
# Vision: Finch × Duolingo × Character AI × TCBS
# 💬 Tâm sự · 🐑 Cừu của tôi · 🌾 Trang trại
# ═══════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
# 3 TABS NAVIGATION — Product Refactor v5
# 💬 Tâm sự · 🐑 Cừu của tôi · 🌾 Trang trại
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "💬 Tâm sự",
    "🐑 Cừu của tôi",
    "🌾 Trang trại",
])


# ═══════════════════════════════════════════════════════
# TAB 1 — TÂM SỰ
# Home = Cừu hero + Memory + Dream + Check-in + CTAs
# Sub-views: Chat | Nhật ký
# ═══════════════════════════════════════════════════════
with tab1:

    # ── Ngày mới: tính streak + award XP ──
    _today_str = datetime.now().strftime("%Y-%m-%d")
    _is_new_day = mem.get("last_visit_date", "") != _today_str
    if _is_new_day:
        mem["last_visit_date"] = _today_str
        mem["streak"] = mem.get("streak", 0) + 1
        st.session_state.checkin_done_today = False
        award_xp("streak")
        _save()

    _view = st.session_state.get("tamsự_view", "home")

    # ══════════════════════════════════════════════════════════
    # HOMESCREEN — Luôn hiển thị ở đầu Tab 1
    # ══════════════════════════════════════════════════════════

    # ── HERO: Cừu + lời chào ──
    _hero_mood = st.session_state.get("sheep_mood", "default")
    _hero_src  = _b64(_pick_mascot(_hero_mood))
    _name_str  = mem.get("name", "").strip()
    _greetings_map = {
        "default":   "Bê bê~ Mình đang chờ bạn đây!",
        "happy":     "Bê bê~ Mình vui quá khi gặp lại bạn!",
        "sad":       "Bê bê~ Mình ổn hơn khi có bạn ở đây.",
        "miss_you":  "Bê bê~ Mình nhớ bạn nhiều lắm!",
        "listening": "Bê bê~ Mình đang lắng nghe đây.",
        "celebrate": "Bê bê~ Tuyệt vời quá bạn ơi!",
        "goal":      "Bê bê~ Cùng nhau tiến đến giấc mơ thôi!",
    }
    _greet = _greetings_map.get(_hero_mood, "Bê bê~ Mình đang chờ bạn!")
    if _name_str:
        _greet = _greet.replace("bạn!", f"{_name_str}!").replace("bạn ơi!", f"{_name_str} ơi!")

    _lv_key, _lv_name, _, _lv_pct = get_level(mem.get("total_xp", 0))

    st.markdown(
        f'<div style="text-align:center;padding:20px 0 6px;">'
        f'<img src="{_hero_src}" width="180" style="border-radius:50%;'
        f'border:5px solid #FFB5C8;box-shadow:0 14px 44px rgba(255,140,190,0.4);" />'
        f'<div style="font-size:0.78rem;font-weight:700;color:#C4607F;margin-top:8px;'
        f'background:linear-gradient(135deg,#FFE4F0,#E8F0FF);display:inline-block;'
        f'padding:3px 14px;border-radius:20px;border:1px solid #FFD6E8;">'
        f'✨ {_lv_name}</div>'
        f'<div style="font-size:0.97rem;color:#C4607F;font-weight:700;margin-top:8px;'
        f'font-style:italic;">🐑 {_greet}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── DAILY CHECK-IN ──
    if not st.session_state.get("checkin_done_today"):
        st.markdown(
            '<div style="background:linear-gradient(135deg,rgba(255,220,235,0.35),'
            'rgba(210,230,255,0.35));border:1.5px solid #FFD6E8;border-radius:18px;'
            'padding:14px 18px;margin:10px 0 8px;">'
            '<div style="font-size:0.95rem;font-weight:800;color:#C4607F;margin-bottom:10px;">'
            '☀️ Hôm nay bạn thế nào?</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        _ci_moods = [
            ("😊", "Rất vui", "listening"),
            ("😔", "Áp lực", "sad"),
            ("😴", "Mệt mỏi", "sad"),
            ("😤", "Bực bội", "sad"),
            ("💪", "Quyết tâm", "goal"),
            ("🥹", "Cần nghe", "listening"),
        ]
        _ci_cols = st.columns(3)
        for _ci, (_ce, _cl, _cm) in enumerate(_ci_moods):
            if _ci_cols[_ci % 3].button(
                f"{_ce} {_cl}", use_container_width=True, key=f"ci_{_ci}"
            ):
                st.session_state.checkin_done_today = True
                _ci_text = f"Hôm nay mình cảm thấy {_cl.lower()} {_ce}"
                st.session_state.messages.append({"role": "user", "content": _ci_text})
                st.session_state._quick_reply = f"Hôm nay mình {_cl.lower()}, Cừu ơi. {_ce}"
                set_mood(_cm)
                award_xp("daily_checkin")
                st.session_state.tamsự_view = "chat"
                st.rerun()
    else:
        # Streak indicator after check-in
        st.markdown(
            f'<div style="text-align:center;margin:6px 0 10px;">'
            f'<span style="background:linear-gradient(135deg,#FF8FAF,#7EC8E3);color:white;'
            f'font-size:0.85rem;font-weight:700;border-radius:20px;padding:4px 16px;">'
            f'🔥 Streak {mem.get("streak",0)} ngày</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── SHEEP MEMORY CARD ──
    _mem_items = _build_memory_card(mem)
    if _mem_items:
        _mem_chips = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:4px;'
            f'background:white;border:1.5px solid #FFD6E8;border-radius:20px;'
            f'padding:4px 12px;font-size:0.83rem;color:#444;margin:3px 2px;'
            f'white-space:nowrap;">{_e} {_t}</span>'
            for _e, _t in _mem_items[:4]
        )
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(255,220,235,0.2),'
            f'rgba(210,230,255,0.2));border:1.5px solid #FFD6E8;border-radius:16px;'
            f'padding:12px 16px;margin:0 0 12px;">'
            f'<div style="font-size:0.8rem;font-weight:700;color:#C4607F;margin-bottom:8px;">'
            f'💭 Điều Cừu nhớ về bạn</div>'
            f'<div style="display:flex;flex-wrap:wrap;">{_mem_chips}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:rgba(255,220,235,0.1);border:1.5px dashed #FFD6E8;'
            'border-radius:16px;padding:10px 16px;margin:0 0 10px;text-align:center;">'
            '<span style="color:#bbb;font-size:0.85rem;">'
            '🐑 Kể chuyện với Cừu — Cừu sẽ nhớ dần về bạn...</span></div>',
            unsafe_allow_html=True,
        )

    # ── DREAM PROGRESS CARD ──
    _active_d = get_active_dream(mem)
    if _active_d:
        _dp_pct  = dream_progress_pct(_active_d)
        _dp_name = _active_d.get("name", "").title()
        _dp_saved = _active_d.get("saved", 0)
        _dp_target = _active_d.get("target", 0)
        _dp_remain = max(0, _dp_target - _dp_saved)
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFF8E1,#FFF3FA);'
            f'border:2px solid #FFD6A0;border-radius:16px;padding:14px 18px;margin:0 0 12px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
            f'<span style="font-size:0.92rem;font-weight:800;color:#C4607F;">🎯 {_dp_name}</span>'
            f'<span style="font-size:0.8rem;color:#888;">{_dp_pct:.0f}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.progress(_dp_pct / 100)
        _dp_detail = (
            f'<div style="font-size:0.78rem;color:#888;margin-top:5px;">'
            f'Cừu đã ăn {fmt(_dp_saved)}'
            f'{" · còn " + fmt(_dp_remain) + " nữa" if _dp_remain > 0 else " · 🎉 Hoàn thành!"}'
            f'</div></div>'
        )
        st.markdown(_dp_detail, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="background:rgba(255,240,200,0.2);border:1.5px dashed #FFD6A0;'
            'border-radius:16px;padding:12px 16px;margin:0 0 12px;text-align:center;">'
            '<span style="color:#C4A060;font-size:0.88rem;">'
            '🎯 Kể với Cừu về giấc mơ của bạn — Cừu sẽ giúp bạn thực hiện!</span></div>',
            unsafe_allow_html=True,
        )

    # ── 2 CTAs ──
    _cta_a, _cta_b = st.columns(2)
    with _cta_a:
        if st.button("💬 Tâm sự với Cừu", use_container_width=True,
                     type="primary", key="home_cta_chat"):
            st.session_state.tamsự_view = "chat"
            st.rerun()
    with _cta_b:
        if st.button("🐑 Cho Cừu ăn nhanh", use_container_width=True, key="home_cta_feed"):
            st.session_state.show_quick_feed = not st.session_state.get("show_quick_feed", False)
            st.rerun()

    # ── QUICK FEED INLINE ──
    if st.session_state.get("show_quick_feed"):
        st.markdown(
            '<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
            'border:2px solid #FFB5C8;border-radius:16px;padding:14px 18px;margin:8px 0;">'
            '<div style="font-size:0.9rem;font-weight:700;color:#C4607F;margin-bottom:10px;">'
            '🍽️ Cho Cừu ăn ngay hôm nay!</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        _qf_cols = st.columns(4)
        for _qi, (amt, food_emoji, food_name) in enumerate(FEED_OPTIONS):
            if _qf_cols[_qi].button(
                f"{food_emoji}\n{fmt(amt)}", use_container_width=True, key=f"qf_{amt}"
            ):
                _prev_lk, *_ = get_level(mem.get("total_xp", 0))
                mem["total_saved"]     += amt
                mem["last_fed_amount"]  = amt
                mem["last_fed_food"]    = f"{food_emoji} {food_name}"
                mem["last_fed_date"]    = _today_str
                # Link to active dream
                if _active_d:
                    _active_d["saved"] = min(
                        _active_d.get("target", amt),
                        _active_d.get("saved", 0) + amt
                    )
                _xp = award_xp("feeding")
                set_mood("happy")
                st.session_state.feeding_celebration = True
                st.session_state.show_quick_feed = False
                _save()
                # Check achievements
                _new_ach = check_achievements()
                if _new_ach:
                    st.session_state.new_achievements = _new_ach
                st.rerun()
        if st.button("✕ Đóng", key="qf_close"):
            st.session_state.show_quick_feed = False
            st.rerun()

    # ── FEEDING CELEBRATION (from quick feed) ──
    if st.session_state.get("feeding_celebration"):
        _fed_food = mem.get("last_fed_food", "")
        _fed_amt  = mem.get("last_fed_amount", 0)
        _cel_src  = _b64(_pick_mascot("celebrate"))
        _xp_earned = st.session_state.get("xp_just_earned", 0)
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFF0F5,#FFFBE0);'
            f'border:2px solid #FFB5C8;border-radius:18px;padding:18px;'
            f'text-align:center;margin:10px 0;animation:pulse 1s ease-in-out;">'
            f'<img src="{_cel_src}" width="80" style="border-radius:50%;border:3px solid #FFB5C8;" />'
            f'<div style="font-size:1.3rem;margin:6px 0;">🎉</div>'
            f'<strong style="font-size:1.0rem;color:#C4607F;">'
            f'Cừu được ăn {_fed_food or fmt(_fed_amt)} rồi — bê bê cảm ơn! ❤️</strong>'
            + (f'<div style="font-size:0.82rem;color:#7EC8E3;margin-top:8px;font-weight:700;">'
               f'+{_xp_earned} XP ✨</div>' if _xp_earned else '')
            + (f'<div style="font-size:0.82rem;color:#5A7A4A;margin-top:6px;">'
               f'🎯 Gần đến {_active_d["name"].title()} hơn rồi!</div>'
               if _active_d else '')
            + '</div>',
            unsafe_allow_html=True,
        )
        mem["last_fed_amount"] = 0
        st.session_state.feeding_celebration = False
        st.session_state.xp_just_earned = 0
        _save()
        st.balloons()

    # ── NEW ACHIEVEMENT TOAST ──
    _ach_map = {a[0]: a for a in ACHIEVEMENTS_DEF}
    for _ach_key in st.session_state.get("new_achievements", []):
        if _ach_key in _ach_map:
            _, _ae, _an, _ad = _ach_map[_ach_key]
            st.success(f"{_ae} **{_an}** — {_ad}")
    st.session_state.new_achievements = []

    # ══════════════════════════════════════════════════════════
    # SUB-VIEW NAV: Chat | Nhật ký
    # ══════════════════════════════════════════════════════════
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    _sv_a, _sv_b = st.columns(2)
    with _sv_a:
        if st.button(
            "💬 Trò chuyện",
            use_container_width=True,
            type="primary" if _view == "chat" else "secondary",
            key="sv_chat",
        ):
            st.session_state.tamsự_view = "chat"
            st.rerun()
    with _sv_b:
        if st.button(
            "📔 Nhật ký",
            use_container_width=True,
            type="primary" if _view == "diary" else "secondary",
            key="sv_diary",
        ):
            st.session_state.tamsự_view = "diary"
            st.rerun()

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # CHAT VIEW
    # ══════════════════════════════════════════════════════════
    if _view == "chat" or _view == "home":

        # Chips — chỉ khi chưa chat
        if not st.session_state.messages:
            _chips = [
                ("📚", "Áp lực chuyện học", "Cừu ơi, em đang rất áp lực về việc học. Lắng nghe em với nhé?"),
                ("💸", "Lo về tiền bạc",    "Cừu ơi, em đang lo lắng về tài chính, áp lực lắm."),
                ("💔", "Hôm nay không vui", "Cừu ơi, hôm nay em không vui, muốn chia sẻ với Cừu."),
                ("✨", "Có một giấc mơ",    "Cừu ơi, em có một ước mơ muốn kể! Em cần được động viên."),
                ("🌱", "Muốn thay đổi",     "Cừu ơi, em muốn thay đổi cuộc sống nhưng chưa biết bắt đầu."),
                ("💼", "Chuyện công việc",  "Cừu ơi, em đang cân nhắc về hướng đi sự nghiệp."),
            ]
            _chip_cols = st.columns(3)
            for _ci2, (_ce2, _cl2, _ct2) in enumerate(_chips):
                if _chip_cols[_ci2 % 3].button(
                    f"{_ce2} {_cl2}", use_container_width=True, key=f"chip2_{_ci2}"
                ):
                    st.session_state.messages.append({"role": "user", "content": f"{_ce2} {_cl2}"})
                    st.session_state._quick_reply = _ct2
                    st.rerun()

        # Quick reply handler
        if st.session_state._quick_reply:
            _qr = st.session_state._quick_reply
            st.session_state._quick_reply = None
            with st.spinner("Cừu đang nghĩ... 🐑"):
                _qr_result = _call_llm(_qr, _SYS_EMOTION)
            _qr_reply = _qr_result.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe!")
            st.session_state.messages.append({"role": "assistant", "content": _qr_reply})
            award_xp("chat")
            _new_ach2 = check_achievements()
            if _new_ach2:
                st.session_state.new_achievements = _new_ach2
            st.rerun()

        # Contextual suggestion
        _sug = get_smart_suggestion(st.session_state.messages, mem)
        if _sug:
            st.markdown(f'<div class="suggestion-box">{_sug}</div>', unsafe_allow_html=True)

        # Chat history
        if st.session_state.messages:
            st.markdown("---")
            for _m in st.session_state.messages[-12:]:
                _av = get_avatar_src("listening") if _m["role"] == "assistant" else "🧑"
                with st.chat_message(_m["role"], avatar=_av):
                    st.markdown(_m["content"])

        # Chat input
        _user_msg = st.chat_input("Nhắn tin với Cừu Cần Cù... 🐑")
        if _user_msg:
            _expanded = _EMOTION_EXPAND.get(_user_msg.strip().lower(), _user_msg)
            st.session_state.messages.append({"role": "user", "content": _user_msg})
            with st.spinner("Cừu đang lắng nghe... 🐑"):
                _result_msg = _call_llm(_expanded, _SYS_EMOTION)
            _reply_msg = _result_msg.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe nè!")
            st.session_state.messages.append({"role": "assistant", "content": _reply_msg})
            award_xp("chat")
            _new_ach3 = check_achievements()
            if _new_ach3:
                st.session_state.new_achievements = _new_ach3
            st.rerun()

    # ══════════════════════════════════════════════════════════
    # DIARY VIEW
    # ══════════════════════════════════════════════════════════
    elif _view == "diary":
        diary_entries: list[dict] = mem.get("diary_entries", [])

        if diary_entries:
            d_streak = _diary_streak(diary_entries)
            sc1, sc2, sc3 = st.columns(3)
            sc1.markdown(
                f'<div class="diary-stat-mini"><div style="font-size:1.2rem;font-weight:800;color:#C4607F;">'
                f'{len(diary_entries)}</div><div style="font-size:0.74rem;color:#888;">📖 Tổng trang</div></div>',
                unsafe_allow_html=True,
            )
            sc2.markdown(
                f'<div class="diary-stat-mini"><div style="font-size:1.2rem;font-weight:800;color:#C4607F;">'
                f'{d_streak}</div><div style="font-size:0.74rem;color:#888;">🔥 Streak</div></div>',
                unsafe_allow_html=True,
            )
            _top_dream_d = _top_diary_dream(diary_entries)
            sc3.markdown(
                f'<div class="diary-stat-mini"><div style="font-size:0.82rem;font-weight:700;color:#4E7DB8;">'
                f'{(_top_dream_d or "—").title()[:14]}</div>'
                f'<div style="font-size:0.74rem;color:#888;">🎯 Hay mơ về</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("---")

        DIARY_MOODS_V2 = [
            ("😊", "Rất vui"), ("😔", "Áp lực"), ("😴", "Hơi mệt"),
            ("😡", "Bực bội"), ("💪", "Quyết tâm"), ("🥹", "Cần lắng nghe"),
        ]

        col_write, col_hist = st.columns([3, 2])

        with col_write:
            if st.session_state.get("diary_just_saved") and st.session_state.get("diary_last_entry"):
                _le = st.session_state.diary_last_entry
                _ins = _build_diary_insights(
                    _le.get("mood", ""), _le.get("tags", []),
                    _le.get("dream", ""), _le.get("content", ""),
                )
                _d_src = _b64(_pick_mascot("diary"))
                _ins_html = "".join(
                    f'<div style="display:flex;align-items:flex-start;gap:8px;margin:5px 0;">'
                    f'<span style="color:#FF8FAF;font-weight:700;flex-shrink:0;">•</span>'
                    f'<span style="font-size:0.9rem;color:#444;line-height:1.5;">{i}</span></div>'
                    for i in _ins
                )
                st.markdown(
                    f'<div class="insight-card">'
                    f'<img src="{_d_src}" width="80" style="border-radius:50%;border:3px solid #FFB5C8;margin-bottom:10px;" /><br/>'
                    f'<strong style="color:#C4607F;">🐑 Hôm nay mình hiểu thêm về bạn</strong>'
                    f'<div style="margin:12px 0 8px;padding:0 4px;">{_ins_html}</div>'
                    f'<div style="color:#4E7DB8;font-size:0.9rem;font-style:italic;">💙 Mình sẽ nhớ điều này giúp bạn.</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if _le.get("reply"):
                    st.markdown(
                        f'<div style="background:rgba(255,182,210,0.15);border-radius:14px;'
                        f'padding:10px 14px;margin:6px 0 12px;font-style:italic;color:#C4607F;">'
                        f'🐑 Cừu nhắn: <strong>{_le["reply"]}</strong></div>',
                        unsafe_allow_html=True,
                    )
                if st.button("✏️ Viết thêm hôm nay", type="primary", use_container_width=True):
                    st.session_state.diary_just_saved = False
                    st.session_state.diary_last_entry = None
                    for k in ("dq1", "dq2", "dq3"):
                        st.session_state.pop(k, None)
                    st.session_state.diary_mood_sel = None
                    st.rerun()
            else:
                st.markdown(
                    '<div style="font-size:0.95rem;font-weight:700;color:#C4607F;margin-bottom:10px;">'
                    '🐑 Hôm nay bạn thế nào?</div>',
                    unsafe_allow_html=True,
                )
                mood_cols = st.columns(3)
                for i, (emoji, label) in enumerate(DIARY_MOODS_V2):
                    full_label = f"{emoji} {label}"
                    is_sel = (st.session_state.get("diary_mood_sel") == full_label)
                    if mood_cols[i % 3].button(
                        full_label, key=f"dmood_{i}", use_container_width=True,
                        type="primary" if is_sel else "secondary",
                    ):
                        st.session_state.diary_mood_sel = full_label
                        st.rerun()

                current_mood = st.session_state.get("diary_mood_sel") or ""

                st.markdown('<div class="diary-prompt">🐑 Hôm nay điều gì khiến bạn nhớ nhất?</div>', unsafe_allow_html=True)
                q1 = st.text_area("", placeholder="Kể cho mình nghe...", height=90, key="dq1", label_visibility="collapsed")

                st.markdown('<div class="diary-prompt">🐑 Có điều gì vui, buồn hoặc lo lắng không?</div>', unsafe_allow_html=True)
                q2 = st.text_area("", placeholder="Vài dòng thôi cũng được...", height=90, key="dq2", label_visibility="collapsed")

                st.markdown('<div class="diary-prompt">🐑 Có điều gì muốn nhắn cho tương lai không?</div>', unsafe_allow_html=True)
                q3 = st.text_area("", placeholder="Ghi lại điều muốn nhớ...", height=90, key="dq3", label_visibility="collapsed")

                has_content = any([q1.strip(), q2.strip(), q3.strip()])
                if st.button("💾 Lưu vào nhật ký Cừu", type="primary",
                             use_container_width=True, disabled=not has_content):
                    combined = "\n\n".join(filter(None, [
                        f"Điều nhớ nhất: {q1.strip()}"   if q1.strip() else "",
                        f"Cảm xúc: {q2.strip()}"         if q2.strip() else "",
                        f"Nhắn tương lai: {q3.strip()}"  if q3.strip() else "",
                    ]))
                    sheep_reply = "Bê bê~ 🐑 Cừu đã đọc rồi! Cảm ơn bạn 💙"
                    emotion_tag = "bình_thường"
                    dream_det   = ""
                    entry_tags: list[str] = []
                    if st.session_state.api_key:
                        with st.spinner("Cừu đang đọc nhật ký... 📖"):
                            r = _call_llm(
                                f"Nhật ký:\nTâm trạng: {current_mood}\n{combined[:600]}",
                                _SYS_DIARY,
                            )
                            sheep_reply = r.get("sheep_reply") or sheep_reply
                            emotion_tag = r.get("emotion", "bình_thường")
                            dream_det   = r.get("dream_detected", "")
                            entry_tags  = r.get("tags", [])
                            if r.get("mood"):
                                set_mood(r["mood"])
                    entry = {
                        "id":       datetime.now().isoformat(),
                        "date":     datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "date_raw": datetime.now().isoformat(),
                        "title":    f"Ngày {datetime.now().strftime('%d/%m')}",
                        "mood":     current_mood or "🐑 Bình thường",
                        "content":  combined,
                        "emotion":  emotion_tag,
                        "tags":     entry_tags,
                        "dream":    dream_det,
                        "reply":    sheep_reply,
                    }
                    diary_entries.insert(0, entry)
                    mem["diary_entries"] = diary_entries
                    award_xp("diary")
                    _new_ach_d = check_achievements()
                    if _new_ach_d:
                        st.session_state.new_achievements = _new_ach_d
                    _save()
                    st.session_state.diary_just_saved = True
                    st.session_state.diary_last_entry = entry
                    st.rerun()
                if not has_content:
                    st.caption("Viết ít nhất một điều để Cừu lưu giúp bạn 🌿")

        with col_hist:
            if not diary_entries:
                st.markdown(
                    '<div style="text-align:center;padding:40px 12px 20px;">'
                    '<div style="font-size:2.2rem;">🌱</div>'
                    '<div style="font-weight:800;color:#5A7A4A;margin:8px 0;">Trang đầu tiên đang chờ bạn.</div>'
                    '<div style="color:#888;font-size:0.87rem;font-style:italic;line-height:1.7;">'
                    '"Mọi giấc mơ lớn<br/>bắt đầu từ một dòng nhật ký nhỏ."</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="font-weight:800;color:#4E7DB8;font-size:1.0rem;margin-bottom:6px;">'
                    '📖 Hành trình trưởng thành</div>', unsafe_allow_html=True
                )
                for entry in diary_entries[:8]:
                    preview = entry["content"][:100] + ("..." if len(entry["content"]) > 100 else "")
                    reply_prev = ""
                    if entry.get("reply"):
                        rp = entry["reply"]
                        reply_prev = (
                            f'<div style="color:#C4607F;font-size:0.8rem;margin-top:5px;font-style:italic;">'
                            f'🐑 {rp[:50]}{"..." if len(rp)>50 else ""}</div>'
                        )
                    st.markdown(
                        f'<div class="diary-entry-card">'
                        f'<div style="display:flex;justify-content:space-between;">'
                        f'<span style="font-weight:700;color:#444;font-size:0.87rem;">{entry["mood"]}</span>'
                        f'<span style="font-size:0.74rem;color:#bbb;">{entry["date"][:8]}</span>'
                        f'</div>'
                        f'<div style="font-size:0.83rem;color:#666;margin:5px 0 2px;line-height:1.5;">{preview}</div>'
                        f'{reply_prev}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("🗑️", key=f"del_{entry['id']}", help="Xoá trang này"):
                        mem["diary_entries"] = [e for e in diary_entries if e["id"] != entry["id"]]
                        _save()
                        st.rerun()



# ═══════════════════════════════════════════════════════
# TAB 2 — CỪU CỦA TÔI
# XP-based growth + Dream Engine + Feeding + Achievements
# Không có "Hồ sơ tài chính" — chỉ ngôn ngữ Cừu
# ═══════════════════════════════════════════════════════
with tab2:
    _total_xp = mem.get("total_xp", 0)
    _total_saved = mem.get("total_saved", 0)
    _lk, _lname, _next_xp, _lv_pct = get_level(_total_xp)

    # ── LEVEL CARD: Cừu hero + XP bar ──
    _lv_src = _b64(_pick_mascot(_lk))
    _xp_sources = mem.get("xp_sources", {})

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#FFF5FA,#F0F7FF);'
        f'border:2px solid #FFD6E8;border-radius:20px;padding:20px 24px;margin-bottom:14px;">'
        f'<div style="display:flex;align-items:center;gap:20px;">'
        f'<img src="{_lv_src}" width="96" style="border-radius:50%;border:4px solid #FFB5C8;flex-shrink:0;" />'
        f'<div style="flex:1;">'
        f'<div style="font-size:1.25rem;font-weight:800;color:#C4607F;margin-bottom:4px;">{_lname}</div>'
        f'<div style="font-size:0.82rem;color:#888;margin-bottom:8px;">Cấp độ · {_total_xp} XP</div>'
        f'<div style="background:#F0E8F8;border-radius:10px;height:10px;overflow:hidden;">'
        f'<div style="width:{_lv_pct:.0f}%;height:100%;'
        f'background:linear-gradient(90deg,#FF8FAF,#7EC8E3);border-radius:10px;'
        f'transition:width 0.5s;"></div></div>'
        f'<div style="font-size:0.72rem;color:#aaa;margin-top:4px;">'
        f'{_total_xp} / {_next_xp if _next_xp < 9999 else "∞"} XP '
        f'{"· Cấp tối đa! 🏆" if _next_xp >= 9999 else f"· còn {_next_xp - _total_xp} XP nữa"}'
        f'</div>'
        f'</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── XP SOURCES BREAKDOWN ──
    _xp_cols = st.columns(4)
    _xp_items = [
        ("💬", "Chat",    _xp_sources.get("chat", 0)),
        ("📔", "Nhật ký", _xp_sources.get("diary", 0)),
        ("🍽️", "Cho ăn",  _xp_sources.get("feeding", 0)),
        ("🔥", "Streak",  _xp_sources.get("streak", 0)),
    ]
    for _xi, (_xe, _xl, _xv) in enumerate(_xp_items):
        _xp_cols[_xi].markdown(
            f'<div class="diary-stat-mini">'
            f'<div style="font-size:1.0rem;font-weight:800;color:#C4607F;">{_xv}</div>'
            f'<div style="font-size:0.72rem;color:#888;">{_xe} {_xl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── SAVINGS IN SHEEP LANGUAGE ──
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#FFF8E1,#FFF3FA);'
        f'border:1.5px solid #FFD6A0;border-radius:14px;padding:12px 18px;'
        f'margin:14px 0 4px;display:flex;align-items:center;gap:12px;">'
        f'<div style="font-size:2rem;">🐑</div>'
        f'<div>'
        f'<div style="font-size:1.1rem;font-weight:800;color:#C4607F;">'
        f'Cừu đã ăn {fmt(_total_saved)}</div>'
        f'<div style="font-size:0.78rem;color:#888;margin-top:2px;">'
        f'🔥 {mem.get("streak", 0)} ngày liên tiếp · '
        f'{"Cừu đang lớn mạnh! 💪" if _total_saved > 0 else "Cho Cừu bữa đầu tiên nhé!"}'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # DREAM ENGINE — Trung tâm của trải nghiệm
    # ══════════════════════════════════════════════════════════
    st.markdown(
        '<div style="font-size:1.05rem;font-weight:800;color:#C4607F;margin-bottom:10px;">'
        '🎯 Giấc mơ đang được nuôi</div>',
        unsafe_allow_html=True,
    )

    _dreams = mem.get("dreams", [])
    if not _dreams:
        st.markdown(
            '<div style="background:rgba(255,240,200,0.25);border:1.5px dashed #FFD6A0;'
            'border-radius:14px;padding:18px;text-align:center;margin-bottom:14px;">'
            '<div style="font-size:2rem;margin-bottom:8px;">✨</div>'
            '<div style="font-weight:700;color:#C4A060;margin-bottom:6px;">'
            'Chưa có giấc mơ nào</div>'
            '<div style="font-size:0.85rem;color:#aaa;">Kể với Cừu về giấc mơ của bạn ở tab '
            '<strong>💬 Tâm sự</strong> — Cừu sẽ nhớ và giúp bạn thực hiện!</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for _d in _dreams[:4]:
            _d_name = _d.get("name", "").title()
            _d_saved = _d.get("saved", 0)
            _d_target = _d.get("target", 0)
            _d_pct = dream_progress_pct(_d)
            _d_remain = max(0, _d_target - _d_saved)
            _d_done = _d_saved >= _d_target > 0

            with st.container(border=True):
                _dc_a, _dc_b = st.columns([3, 1])
                with _dc_a:
                    st.markdown(
                        f'<div style="font-weight:700;color:#444;margin-bottom:4px;">✨ {_d_name}</div>',
                        unsafe_allow_html=True,
                    )
                    if _d_target > 0:
                        st.progress(_d_pct / 100,
                                    text=f"{_d_pct:.0f}% · Cừu đã ăn {fmt(_d_saved)}"
                                    + (f" · còn {fmt(_d_remain)}" if not _d_done else " · 🎉 Hoàn thành!"))
                    else:
                        st.caption("Chưa đặt mục tiêu · Kể với Cừu để bắt đầu!")
                with _dc_b:
                    if not _d_done and (_d_target == 0 or _d_remain > 0):
                        if st.button("❤️ +50k", key=f"dream50_{_d['name']}", type="primary"):
                            _d["saved"] = min(
                                _d.get("target", 50_000),
                                _d.get("saved", 0) + 50_000,
                            )
                            mem["total_saved"] += 50_000
                            mem["last_fed_amount"] = 50_000
                            mem["last_fed_food"]   = f"❤️ cho {_d_name}"
                            _d_new_pct = dream_progress_pct(_d)
                            set_mood("celebrate" if _d_new_pct >= 100 else "happy")
                            award_xp("feeding")
                            st.session_state.feeding_celebration = True
                            _new_ach_dr = check_achievements()
                            if _new_ach_dr:
                                st.session_state.new_achievements = _new_ach_dr
                            _save()
                            st.rerun()
                    elif _d_done:
                        st.markdown("🏆", unsafe_allow_html=True)

    # ── Thêm giấc mơ mới ──
    with st.expander("✨ Thêm giấc mơ mới"):
        _dream_col1, _dream_col2 = st.columns(2)
        with _dream_col1:
            _new_dream_name = st.text_input(
                "Tên giấc mơ", placeholder="VD: Đi Nhật, Mua nhà...", key="new_dream_name"
            )
        with _dream_col2:
            _new_dream_amt = st.number_input(
                "Mục tiêu tiết kiệm (đ)", min_value=0, max_value=500_000_000,
                step=500_000, value=10_000_000, key="new_dream_amt",
            )
        if st.button("🎯 Thêm giấc mơ này", type="primary", use_container_width=True):
            if _new_dream_name.strip():
                if _new_dream_name.strip() not in [d["name"] for d in _dreams]:
                    mem["dreams"].append({
                        "name":   _new_dream_name.strip().lower(),
                        "target": int(_new_dream_amt),
                        "saved":  0,
                        "tags":   [],
                    })
                    award_xp("dream_set")
                    _new_ach_dn = check_achievements()
                    if _new_ach_dn:
                        st.session_state.new_achievements = _new_ach_dn
                    _save()
                    st.success(f"✨ Đã thêm giấc mơ: {_new_dream_name.title()}!")
                    st.rerun()

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # FEEDING — Gắn với giấc mơ
    # ══════════════════════════════════════════════════════════
    _today_str_t2 = datetime.now().strftime("%Y-%m-%d")
    _fed_today = mem.get("last_fed_date", "") == _today_str_t2

    _stage_key_t2, _stage_name_t2, _, _, _ = get_growth_stage(_total_saved)
    _hero_lines_t2 = {
        "baby":   "🥕 \"Mình vừa ra đời... Cho mình ăn bữa đầu tiên nhé?\"",
        "child":  f"🍎 \"Mình lớn hơn rồi nhờ {mem.get('name','bạn')} đấy! Hôm nay cho mình ăn tiếp không?\"",
        "teen":   "🎂 \"Mình đang lớn nhanh lắm~ Cùng nhau tiến đến giấc mơ thôi!\"",
        "adult":  f"🎉 \"Chúng mình đã đi được nửa đường rồi. Mình tự hào về {mem.get('name','bạn')} lắm ❤️\"",
        "master": f"🌟 \"Nhìn chúng mình đến đây... Cảm ơn {mem.get('name','bạn')} đã không bỏ cuộc 🏆\"",
    }
    _htxt_t2 = _hero_lines_t2.get(_stage_key_t2, _hero_lines_t2["baby"])

    st.markdown(
        f'<div style="font-size:1.05rem;font-weight:800;color:#C4607F;margin-bottom:8px;">'
        f'🍽️ Hôm nay cho Cừu ăn gì?</div>'
        f'<div style="font-size:0.88rem;color:#777;font-style:italic;margin-bottom:12px;">'
        f'{_htxt_t2}</div>',
        unsafe_allow_html=True,
    )

    # Dream selector for feeding
    _feed_dream = None
    if _dreams:
        _dream_opts = ["Tự do (không gắn giấc mơ)"] + [d["name"].title() for d in _dreams]
        _selected_dream_name = st.selectbox(
            "🎯 Cho ăn vì giấc mơ nào?", _dream_opts, key="feed_dream_sel"
        )
        if _selected_dream_name != "Tự do (không gắn giấc mơ)":
            _feed_dream = next(
                (d for d in _dreams if d["name"].title() == _selected_dream_name), None
            )

    # Feeding celebration
    if st.session_state.get("feeding_celebration"):
        _fed_food_t2 = mem.get("last_fed_food", "")
        _fed_amt_t2  = mem.get("last_fed_amount", 0)
        _cel_src_t2  = _b64(_pick_mascot("celebrate"))
        _dream_link_html = ""
        if _feed_dream:
            _dl_name = _feed_dream.get("name", "").title()
            _dl_pct = dream_progress_pct(_feed_dream)
            _dream_link_html = (
                f'<div style="background:rgba(255,215,0,0.15);border-radius:10px;'
                f'padding:8px 14px;margin-top:10px;font-size:0.87rem;color:#B8860B;">'
                f'✨ Giấc mơ <strong>{_dl_name}</strong> đạt <strong>{_dl_pct:.0f}%</strong>~</div>'
            )
        if mem.get("just_leveled_up"):
            _new_lk2, _new_lname2, *_ = get_level(mem.get("total_xp", 0))
            _dream_link_html += (
                f'<div style="font-size:1.0rem;font-weight:800;color:#C4607F;margin-top:10px;">'
                f'🎊 Cừu lên cấp! Chào mừng đến với <strong>{_new_lname2}</strong>!</div>'
            )
            mem["just_leveled_up"] = False
        st.markdown(
            f'<div class="celebration-box">'
            f'<img src="{_cel_src_t2}" width="90" style="border-radius:50%;border:3px solid #FFB5C8;" />'
            f'<div style="font-size:1.3rem;margin:6px 0;">🎉</div>'
            f'<strong style="font-size:1.0rem;color:#C4607F;">'
            f'Cừu được ăn {_fed_food_t2 or fmt(_fed_amt_t2)} rồi — bê bê cảm ơn! ❤️</strong>'
            f'{_dream_link_html}</div>',
            unsafe_allow_html=True,
        )
        mem["last_fed_amount"] = 0
        st.session_state.feeding_celebration = False
        _save()
        st.balloons()

    if st.session_state.get("feeding_refused"):
        st.markdown(
            '<div style="background:linear-gradient(135deg,#F0F8FF,#EAF4FF);'
            'border-radius:14px;padding:14px;text-align:center;margin-bottom:10px;">'
            '<div style="font-size:0.95rem;font-weight:700;color:#5B8DB8;">Không sao cả 🌙</div>'
            '<div style="font-size:0.85rem;color:#6A9BBF;margin-top:4px;">'
            'Mình vẫn ở đây. Hôm nào sẵn sàng thì mình vẫn đợi~ 🐑</div></div>',
            unsafe_allow_html=True,
        )
        st.session_state.feeding_refused = False

    # Feed buttons
    _feed_cols_t2 = st.columns(4)
    for _fi, (amt, food_emoji, food_name) in enumerate(FEED_OPTIONS):
        if _feed_cols_t2[_fi].button(
            f"{food_emoji} {food_name}\n{fmt(amt)}",
            use_container_width=True, key=f"feed_t2_{amt}", type="primary",
        ):
            _prev_sk = _stage_key_t2
            mem["total_saved"]    += amt
            mem["streak"]          = mem.get("streak", 0)  # streak counted on visit
            mem["last_fed_amount"] = amt
            mem["last_fed_food"]   = f"{food_emoji} {food_name}"
            mem["last_fed_date"]   = _today_str_t2
            if _feed_dream:
                _feed_dream["saved"] = min(
                    _feed_dream.get("target", amt),
                    _feed_dream.get("saved", 0) + amt
                )
            _new_sk, *_ = get_growth_stage(mem["total_saved"])
            award_xp("feeding")
            set_mood("happy")
            st.session_state.feeding_celebration = True
            st.session_state.feeding_refused = False
            _new_ach_f = check_achievements()
            if _new_ach_f:
                st.session_state.new_achievements = _new_ach_f
            _save()
            st.rerun()

    with st.expander("🔢 Nhập số tiền khác"):
        _custom_t2 = st.number_input(
            "Số tiền:", min_value=1_000, max_value=100_000_000,
            step=10_000, value=30_000, key="custom_amt_t2",
        )
        if st.button(f"🐑 Cho Cừu ăn {fmt(int(_custom_t2))}", type="primary", use_container_width=True):
            mem["total_saved"]    += int(_custom_t2)
            mem["last_fed_amount"] = int(_custom_t2)
            mem["last_fed_food"]   = fmt(int(_custom_t2))
            mem["last_fed_date"]   = _today_str_t2
            if _feed_dream:
                _feed_dream["saved"] = min(
                    _feed_dream.get("target", int(_custom_t2)),
                    _feed_dream.get("saved", 0) + int(_custom_t2)
                )
            award_xp("feeding")
            set_mood("happy")
            st.session_state.feeding_celebration = True
            _new_ach_fc = check_achievements()
            if _new_ach_fc:
                st.session_state.new_achievements = _new_ach_fc
            _save()
            st.rerun()

    if st.button("🌙 Hôm nay chưa sẵn sàng", use_container_width=True):
        set_mood("sad")
        st.session_state.feeding_refused = True
        st.session_state.feeding_celebration = False
        _save()
        st.rerun()

    # ── NEW ACHIEVEMENT TOAST ──
    _ach_map_t2 = {a[0]: a for a in ACHIEVEMENTS_DEF}
    for _ach_key_t2 in st.session_state.get("new_achievements", []):
        if _ach_key_t2 in _ach_map_t2:
            _, _ae2, _an2, _ad2 = _ach_map_t2[_ach_key_t2]
            st.success(f"{_ae2} **{_an2}** — {_ad2}")
    st.session_state.new_achievements = []

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # ACHIEVEMENTS
    # ══════════════════════════════════════════════════════════
    _unlocked_set = set(mem.get("achievements", []))
    st.markdown(
        '<div style="font-size:1.0rem;font-weight:800;color:#C4607F;margin-bottom:10px;">'
        '🏆 Thành tựu của Cừu</div>',
        unsafe_allow_html=True,
    )
    _ach_cols = st.columns(4)
    for _ai, (_akey, _aemoji, _aname, _adesc) in enumerate(ACHIEVEMENTS_DEF):
        _is_unlocked = _akey in _unlocked_set
        _a_bg  = "white" if _is_unlocked else "#F5F5F5"
        _a_bd  = "#FFD6E8" if _is_unlocked else "#E0E0E0"
        _a_op  = "1" if _is_unlocked else "0.45"
        _a_lock = "" if _is_unlocked else '<div style="font-size:0.65rem;color:#bbb;">🔒</div>'
        _ach_cols[_ai % 4].markdown(
            f'<div style="text-align:center;padding:10px 6px;'
            f'background:{_a_bg};border:1.5px solid {_a_bd};'
            f'border-radius:14px;margin:3px 0;opacity:{_a_op};">'
            f'<div style="font-size:1.4rem;">{_aemoji}</div>'
            f'<div style="font-size:0.72rem;font-weight:700;color:#444;margin-top:3px;line-height:1.3;">{_aname}</div>'
            f'{_a_lock}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # TẠI SAO CẦN ĐẦU TƯ? — Sheep language, không jargon
    # ══════════════════════════════════════════════════════════
    with st.expander("🐑 Tại sao Cừu cần ăn đều đặn?"):
        st.markdown(
            '<div style="font-size:0.88rem;color:#444;line-height:1.7;">'
            '<p><strong>🥕 Cho Cừu ăn ít mỗi ngày</strong> tốt hơn nhiều so với cho ăn một lần lớn.'
            ' Đây là cách Cừu lớn mạnh bền vững nhất.</p>'
            '<p><strong>📈 Khi Cừu ăn đủ</strong>, tiền của bạn được đưa vào quỹ đầu tư. '
            'Quỹ đầu tư giúp tiền của bạn tăng trưởng theo thời gian — không phải qua đêm, '
            'nhưng kiên nhẫn 3-5 năm thì rất đáng!</p>'
            '<p><strong>🛡️ Cừu không hứa lợi nhuận</strong> — thị trường có lúc lên lúc xuống. '
            'Nhưng lịch sử cho thấy: ai kiên nhẫn đều được thưởng.</p>'
            '<div style="font-size:0.75rem;color:#bbb;margin-top:10px;">'
            '⚠️ Thông tin chỉ mang tính giáo dục. Cừu Cần Cù không phải công ty tư vấn đầu tư được cấp phép.'
            '</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown("**🌳 3 loại thức ăn Cừu thích nhất:**")
        _fc1, _fc2, _fc3 = st.columns(3)
        _fund_simple = {
            "TCEF": ("🌳", "Trồng cây dài hạn", "Kiên nhẫn 3-5 năm. Ngọt nhất khi chín."),
            "TCBF": ("🪣", "Bình nước ổn định",  "Ít biến động. Phù hợp 1-3 năm."),
            "TCFF": ("🎒", "Balo cân bằng",      "Vừa phải — không quá cay, không quá nhạt."),
        }
        for _fcol, _fkey in zip([_fc1, _fc2, _fc3], ["TCEF", "TCBF", "TCFF"]):
            _fi_emoji, _fi_title, _fi_desc = _fund_simple[_fkey]
            _fcol.markdown(
                f'<div style="text-align:center;padding:12px 8px;background:white;'
                f'border:1.5px solid #FFD6E8;border-radius:14px;">'
                f'<div style="font-size:1.6rem;">{_fi_emoji}</div>'
                f'<div style="font-size:0.78rem;font-weight:700;color:#C4607F;margin-top:6px;">{_fi_title}</div>'
                f'<div style="font-size:0.72rem;color:#777;margin-top:5px;line-height:1.5;">{_fi_desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ══ TAB 3: AI Sheep Companion ════════════════════════════════════════════════
with tab3:
    import os as _os

    _GH = "https://raw.githubusercontent.com/Hoamaii/cuu-can-cu/main/assets"

    def _load_farm_asset(local_path, gh_url=""):
        full = _os.path.join(_os.path.dirname(__file__), local_path)
        if _os.path.exists(full):
            with open(full, "rb") as _f:
                _d = base64.b64encode(_f.read()).decode()
            return "data:image/png;base64," + _d
        return gh_url

    _FA = {
        "sheep": _load_farm_asset("assets/sheep/sheep_main.png", _GH + "/sheep_adult.png"),
        "f1":    _load_farm_asset("assets/friends/friend1.png",  _GH + "/friend_sheep_1.png"),
        "f2":    _load_farm_asset("assets/friends/friend2.png",  _GH + "/friend_sheep_2.png"),
        "f3":    _load_farm_asset("assets/friends/friend3.png",  _GH + "/friend_sheep_3.png"),
    }

    def _av(key, size=44, fb="🐑"):
        s = _FA.get(key, "")
        base = (
            "width:" + str(size) + "px;height:" + str(size) + "px;"
            "border-radius:50%;object-fit:cover;flex-shrink:0;"
            "mix-blend-mode:multiply;background:#EDE8DC;"
        )
        if s:
            return '<img src="' + s + '" style="' + base + '" onerror="this.style.display=\'none\'">'
        return (
            '<div style="' + base + 'display:flex;align-items:center;'
            'justify-content:center;font-size:' + str(size // 2) + 'px;">' + fb + '</div>'
        )

    _sheep_src = _FA.get("sheep", "")
    if _sheep_src:
        _sheep_el = (
            '<img id="sheep" src="' + _sheep_src + '" '
            'style="width:200px;height:200px;object-fit:contain;'
            'mix-blend-mode:multiply;cursor:pointer;display:block;'
            'animation:sheep-bob 3.5s ease-in-out infinite,sheep-tilt 7s ease-in-out infinite;"'
            ' onclick="feedSheep()" onerror="this.style.display=\'none\'">'
        )
    else:
        _sheep_el = (
            '<div id="sheep" style="font-size:110px;line-height:1;cursor:pointer;'
            'animation:sheep-bob 3.5s ease-in-out infinite;" onclick="feedSheep()">🐑</div>'
        )

    _HTML = """\
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}
html,body{width:100%;height:100%;overflow:hidden;
  background:linear-gradient(180deg,#EEF5FF 0%,#FFF8F0 45%,#F5F0E8 80%,#E8F5D8 100%);
  font-family:-apple-system,'Helvetica Neue',sans-serif;}
#app{width:860px;height:820px;position:relative;display:flex;flex-direction:column;}

/* ── TOPBAR ── */
.tb{
  flex-shrink:0;height:58px;display:flex;align-items:center;
  padding:0 18px;gap:10px;
  background:rgba(255,255,255,0.85);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  box-shadow:0 1px 0 rgba(0,0,0,0.06);z-index:20;
}
.tb-streak{
  display:flex;align-items:center;gap:5px;
  background:linear-gradient(135deg,#FF6B00,#FF3500);
  color:#fff;border-radius:20px;padding:5px 12px;
  font-size:13px;font-weight:800;
  box-shadow:0 2px 10px rgba(255,80,0,0.3);
}
.tb-name{flex:1;text-align:center;font-size:16px;font-weight:800;color:#1a1a1a;letter-spacing:-0.3px;}
.tb-mood{font-size:13px;color:#FF8C00;font-weight:600;}
.tb-pill{
  display:flex;align-items:center;gap:4px;
  background:rgba(0,0,0,0.04);border:1px solid rgba(0,0,0,0.08);
  border-radius:20px;padding:5px 10px;
  font-size:12px;font-weight:700;color:#1a1a1a;
}
.tb-bell{font-size:20px;cursor:pointer;position:relative;flex-shrink:0;}
.tb-dot{
  position:absolute;top:0;right:0;
  width:8px;height:8px;background:#FF3B30;
  border-radius:50%;border:1.5px solid rgba(255,255,255,0.9);
}

/* ── SCROLL AREA ── */
.scroll{flex:1;overflow-y:auto;overflow-x:hidden;}
.scroll::-webkit-scrollbar{width:0;}

/* ── SHEEP SCENE ── */
.scene{
  position:relative;height:268px;overflow:hidden;
  background:linear-gradient(180deg,
#C8E8FF 0%,#D8EEFF 20%,
#FFF5E8 55%,#F0EDDE 75%,
#C8E898 88%,#A8D878 100%);
}

/* Ambient light orb */
.scene-sun{
  position:absolute;top:20px;right:130px;
  width:56px;height:56px;
  background:radial-gradient(circle,#FFF8C0 0%,#FFE040 40%,transparent 100%);
  border-radius:50%;
  box-shadow:0 0 60px 30px rgba(255,220,0,0.18);
  z-index:1;
}

/* Background tree silhouettes */
.bg-tree{position:absolute;z-index:2;opacity:0.55;}
.bt-top{background:#5A9C30;border-radius:50% 50% 40% 40%;}
.bt-trunk{background:#7A5228;border-radius:2px;margin:0 auto;}

/* Soft ground */
.ground{
  position:absolute;bottom:0;left:0;right:0;
  height:88px;
  background:linear-gradient(180deg,#82CC44 0%,#68B82C 50%,#58A01C 100%);
  border-radius:55% 55% 0 0/20px 20px 0 0;
  z-index:3;
}
/* Ground texture dots */
.ground::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(circle at 20% 60%,rgba(255,255,255,0.08) 0%,transparent 40%),
         radial-gradient(circle at 80% 40%,rgba(0,0,0,0.05) 0%,transparent 40%);
  border-radius:inherit;
}

/* Small flowers on ground */
.gflower{position:absolute;z-index:5;font-size:13px;pointer-events:none;}

/* Sheep zone */
.sheep-zone{
  position:absolute;bottom:60px;left:50%;
  transform:translateX(-50%);
  z-index:6;
  display:flex;flex-direction:column;align-items:center;
}
.sheep-glow{
  position:absolute;
  width:220px;height:220px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(255,240,180,0.45) 0%,rgba(255,200,80,0.12) 55%,transparent 100%);
  bottom:-20px;left:50%;transform:translateX(-50%);
  z-index:-1;
  animation:glow-breathe 3.5s ease-in-out infinite;
}
.sheep-shadow{
  width:130px;height:18px;
  background:rgba(0,0,0,0.15);
  border-radius:50%;
  filter:blur(8px);
  margin-top:-6px;
  animation:shadow-bob 3.5s ease-in-out infinite;
}

/* Sheep mood floating badge */
.mood-badge{
  background:rgba(255,255,255,0.95);
  border-radius:20px;padding:5px 12px;
  font-size:12px;font-weight:700;color:#1a1a1a;
  box-shadow:0 4px 16px rgba(0,0,0,0.1);
  margin-bottom:10px;
  animation:float-mood 4s ease-in-out infinite;
  white-space:nowrap;
}

/* Sheep animations */
@keyframes sheep-bob{
  0%,100%{transform:translateY(0) scale(1,1);}
  30%{transform:translateY(-7px) scale(1.01,0.99);}
  60%{transform:translateY(-4px) scale(1,1);}
}
@keyframes sheep-tilt{
  0%,100%{transform:rotate(0deg);}
  25%{transform:rotate(-1.2deg);}
  75%{transform:rotate(1.2deg);}
}
@keyframes shadow-bob{
  0%,100%{transform:scaleX(1);opacity:0.15;}
  30%{transform:scaleX(0.8);opacity:0.08;}
}
@keyframes glow-breathe{
  0%,100%{opacity:0.6;transform:translateX(-50%) scale(1);}
  50%{opacity:1;transform:translateX(-50%) scale(1.1);}
}
@keyframes float-mood{
  0%,100%{transform:translateY(0);}
  50%{transform:translateY(-4px);}
}

/* ── COMPANION CARD ── */
.comp-card{
  margin:0 14px;
  background:rgba(255,255,255,0.95);
  border-radius:24px;
  padding:18px 20px 14px;
  box-shadow:0 2px 20px rgba(0,0,0,0.07);
}
.comp-header{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:10px;
}
.comp-name{font-size:17px;font-weight:800;color:#1a1a1a;}
.comp-mood-tag{
  background:rgba(52,199,89,0.1);color:#1A8C3A;
  border-radius:20px;padding:4px 12px;font-size:12px;font-weight:700;
}
.comp-thinking{
  font-size:13px;color:#555;line-height:1.6;
  background:#F8F5EE;border-radius:16px;padding:12px 14px;
  margin-bottom:12px;
  border-left:3px solid #FF9500;
  font-style:italic;
}
.comp-thinking strong{font-style:normal;color:#FF8C00;}
.comp-memory{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:12px;}
.mem-tag{
  background:#F0EDE8;color:#666;
  border-radius:20px;padding:4px 11px;font-size:11px;font-weight:600;
}
.comp-footer{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:14px;
}
.streak-badge{
  display:flex;align-items:center;gap:5px;
  font-size:12px;font-weight:700;color:#FF5500;
}
.days-together{font-size:11px;color:#aaa;}

/* Dynamic chat prompt */
.chat-prompt{
  background:linear-gradient(145deg,#1A1A2E,#16213E);
  border-radius:18px;padding:13px 16px;
  display:flex;align-items:center;gap:12px;cursor:pointer;
  transition:all 0.18s;
  box-shadow:0 4px 16px rgba(0,0,0,0.15);
}
.chat-prompt:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.2);}
.chat-prompt:active{transform:scale(0.98);}
.cp-text{flex:1;font-size:13px;color:rgba(255,255,255,0.92);font-weight:600;line-height:1.4;}
.cp-ico{font-size:20px;flex-shrink:0;}
.cp-arrow{
  width:32px;height:32px;border-radius:50%;
  background:rgba(255,255,255,0.12);
  display:flex;align-items:center;justify-content:center;
  color:white;font-size:14px;flex-shrink:0;
}

/* ── SECTION HEADER ── */
.sec{display:flex;align-items:center;justify-content:space-between;padding:16px 14px 10px;}
.sec-t{font-size:15px;font-weight:800;color:#1a1a1a;}
.sec-a{font-size:12px;font-weight:600;color:#FF8C00;cursor:pointer;}

/* ── FRIENDS FEED ── */
.feed{margin:0 14px;background:rgba(255,255,255,0.95);border-radius:22px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,0.07);}
.fi{
  display:flex;align-items:flex-start;gap:12px;
  padding:14px 16px;
  border-bottom:1px solid rgba(0,0,0,0.05);
  cursor:pointer;transition:background 0.15s;
}
.fi:last-child{border-bottom:none;}
.fi:hover{background:rgba(0,0,0,0.015);}
.fi-av{position:relative;flex-shrink:0;}
.fi-badge{
  position:absolute;bottom:-3px;right:-3px;
  width:20px;height:20px;border-radius:50%;
  background:white;display:flex;align-items:center;justify-content:center;
  font-size:11px;box-shadow:0 1px 6px rgba(0,0,0,0.15);
}
.fi-body{flex:1;min-width:0;}
.fi-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;}
.fi-name{font-size:13px;font-weight:700;color:#1a1a1a;}
.fi-state{font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;}
.fi-state.fire{background:rgba(255,100,0,0.1);color:#FF5500;}
.fi-state.sad{background:rgba(100,100,255,0.1);color:#5555DD;}
.fi-state.win{background:rgba(255,200,0,0.12);color:#B88A00;}
.fi-desc{font-size:12px;color:#777;margin-bottom:9px;line-height:1.45;}
.fi-actions{display:flex;gap:7px;flex-wrap:wrap;}
.fa-btn{
  border:none;border-radius:12px;padding:6px 13px;
  font-size:11px;font-weight:700;cursor:pointer;transition:all 0.15s;
}
.fa-btn.orange{background:rgba(255,140,0,0.12);color:#D97700;}
.fa-btn.orange:hover{background:rgba(255,140,0,0.22);}
.fa-btn.green{background:rgba(52,199,89,0.12);color:#1A8C3A;}
.fa-btn.green:hover{background:rgba(52,199,89,0.22);}
.fa-btn.blue{background:rgba(0,122,255,0.1);color:#0062CC;}
.fa-btn.blue:hover{background:rgba(0,122,255,0.18);}
.fa-btn.pink{background:rgba(255,45,85,0.1);color:#CC1140;}
.fa-btn.pink:hover{background:rgba(255,45,85,0.18);}
.fa-btn.purple{background:rgba(175,82,222,0.1);color:#8B00CC;}
.fa-btn.purple:hover{background:rgba(175,82,222,0.18);}

/* ── REFERRAL ── */
.ref-card{
  margin:12px 14px;
  background:linear-gradient(135deg,#4C3699 0%,#6B4FBB 50%,#8966D6 100%);
  border-radius:22px;padding:18px 20px;
  display:flex;align-items:center;gap:14px;
  box-shadow:0 6px 24px rgba(76,54,153,0.4);
  position:relative;overflow:hidden;cursor:pointer;
  transition:all 0.18s;
}
.ref-card:hover{transform:translateY(-2px);box-shadow:0 10px 32px rgba(76,54,153,0.5);}
.ref-card::before{
  content:'';position:absolute;
  top:-50px;right:-50px;
  width:160px;height:160px;border-radius:50%;
  background:rgba(255,255,255,0.07);
}
.ref-card::after{
  content:'';position:absolute;
  bottom:-40px;left:50%;
  width:100px;height:100px;border-radius:50%;
  background:rgba(255,255,255,0.04);
}
.ref-ico{font-size:38px;z-index:1;flex-shrink:0;}
.ref-text{flex:1;z-index:1;}
.ref-title{font-size:15px;font-weight:800;color:white;margin-bottom:6px;}
.ref-chips{display:flex;gap:6px;flex-wrap:wrap;}
.ref-chip{
  background:rgba(255,255,255,0.18);
  color:rgba(255,255,255,0.95);
  border-radius:20px;padding:3px 10px;font-size:11px;font-weight:700;
}
.ref-btn{
  z-index:1;flex-shrink:0;
  background:white;color:#4C3699;
  border:none;border-radius:14px;padding:10px 16px;
  font-size:13px;font-weight:800;cursor:pointer;
  box-shadow:0 2px 12px rgba(0,0,0,0.15);
  transition:all 0.15s;
}
.ref-btn:hover{transform:scale(1.05);}

/* spacer */
.spacer{height:16px;}

/* ── BOTTOM NAV ── */
.bnav{
  flex-shrink:0;height:80px;
  background:rgba(255,255,255,0.97);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  display:flex;align-items:flex-start;justify-content:space-around;
  padding-top:10px;
  box-shadow:0 -1px 0 rgba(0,0,0,0.07);
  z-index:20;
}
.ni{
  flex:1;max-width:80px;
  display:flex;flex-direction:column;align-items:center;gap:3px;
  cursor:pointer;padding:6px 8px 4px;border-radius:14px;
  transition:background 0.2s;position:relative;
}
.ni:hover{background:rgba(0,0,0,0.03);}
.nico{font-size:22px;transition:transform 0.2s;}
.ni.active .nico{transform:scale(1.12);}
.nlb{font-size:10px;font-weight:600;color:#C0C0C0;transition:color 0.2s;}
.ni.active .nlb{color:#FF8C00;}
.npip{width:5px;height:5px;background:#FF8C00;border-radius:50%;margin-top:2px;opacity:0;transition:opacity 0.2s;}
.ni.active .npip{opacity:1;}
.nbadge{
  position:absolute;top:2px;right:4px;
  background:#FF3B30;color:white;border-radius:10px;
  font-size:9px;font-weight:800;padding:1px 5px;
}

/* ── CHAT OVERLAY ── */
.overlay{
  position:absolute;inset:0;z-index:50;
  background:rgba(255,255,255,0.98);
  backdrop-filter:blur(16px);
  display:flex;flex-direction:column;
  transform:translateY(100%);
  transition:transform 0.35s cubic-bezier(.4,0,.2,1);
}
.overlay.open{transform:translateY(0);}
.ov-header{
  height:58px;display:flex;align-items:center;padding:0 18px;gap:14px;
  border-bottom:1px solid rgba(0,0,0,0.07);flex-shrink:0;
}
.ov-back{font-size:22px;cursor:pointer;color:#FF8C00;}
.ov-title{font-size:17px;font-weight:800;color:#1a1a1a;flex:1;}
.ov-scroll{flex:1;overflow-y:auto;padding:12px 0;}
.ov-scroll::-webkit-scrollbar{width:0;}
.ov-sec{padding:10px 18px 4px;font-size:11px;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.7px;}
.chat-row{
  display:flex;align-items:center;gap:12px;
  padding:12px 18px;cursor:pointer;transition:background 0.15s;
}
.chat-row:hover{background:rgba(0,0,0,0.025);}
.chat-row-av{
  width:48px;height:48px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-size:24px;
}
.cr-name{font-size:14px;font-weight:700;color:#1a1a1a;}
.cr-sub{font-size:12px;color:#aaa;margin-top:2px;}
.cr-badge{background:#FF3B30;color:white;border-radius:10px;font-size:10px;font-weight:800;padding:2px 6px;margin-left:auto;}
.community-grid{
  display:grid;grid-template-columns:1fr 1fr;
  gap:10px;padding:10px 18px;
}
.comm-card{
  background:#F8F5EE;border-radius:18px;padding:14px 16px;
  cursor:pointer;transition:all 0.15s;
}
.comm-card:hover{background:#EDE8DC;transform:translateY(-1px);}
.comm-ico{font-size:26px;margin-bottom:6px;}
.comm-name{font-size:13px;font-weight:700;color:#1a1a1a;}
.comm-members{font-size:11px;color:#aaa;margin-top:2px;}

/* ── FEED ANIMATION ── */
@keyframes shimmer{0%{left:-100%}100%{left:200%}}
@keyframes drop{0%{opacity:1;transform:translateY(0) rotate(0)}100%{opacity:0;transform:translateY(180px) rotate(560deg)}}
@keyframes rise{0%{opacity:1;transform:translate(-50%,-50%)}100%{opacity:0;transform:translate(-50%,-240%)}}
@keyframes pop{0%{transform:scale(0.7);opacity:0}60%{transform:scale(1.1)}100%{transform:scale(1);opacity:1}}

/* Toast */
#toast{
  position:fixed;bottom:96px;left:50%;transform:translateX(-50%) translateY(12px);
  background:rgba(20,20,20,0.88);color:white;
  padding:10px 20px;border-radius:22px;
  font-size:13px;font-weight:600;
  opacity:0;transition:all 0.28s;z-index:60;
  pointer-events:none;white-space:nowrap;
}
#confetti{position:fixed;inset:0;pointer-events:none;z-index:55;overflow:hidden;}
</style>
</head>
<body>
<div id="app">

  <!-- ── TOP BAR ── -->
  <div class="tb">
<div class="tb-streak">🔥 7 ngày</div>
<div class="tb-name">Bông Cần Cù <span class="tb-mood">😊</span></div>
<div class="tb-pill">🪙 128.450</div>
<div class="tb-pill">💎 320</div>
<div class="tb-bell">🔔<div class="tb-dot"></div></div>
  </div>

  <!-- ── SCROLL CONTENT ── -->
  <div class="scroll">

<!-- SHEEP SCENE -->
<div class="scene">
  <div class="scene-sun"></div>

  <!-- Background trees -->
  <div class="bg-tree" style="bottom:78px;left:30px;display:flex;flex-direction:column;align-items:center;">
    <div class="bt-top" style="width:42px;height:46px;"></div>
    <div class="bt-trunk" style="width:9px;height:20px;"></div>
  </div>
  <div class="bg-tree" style="bottom:82px;left:78px;display:flex;flex-direction:column;align-items:center;">
    <div class="bt-top" style="width:52px;height:56px;background:#4A8C28;border-radius:50% 50% 40% 40%;"></div>
    <div class="bt-trunk" style="width:11px;height:24px;background:#7A5228;border-radius:2px;margin:0 auto;"></div>
  </div>
  <div class="bg-tree" style="bottom:80px;right:34px;display:flex;flex-direction:column;align-items:center;">
    <div class="bt-top" style="width:46px;height:50px;background:#528C30;border-radius:50% 50% 40% 40%;"></div>
    <div class="bt-trunk" style="width:10px;height:22px;background:#7A5228;border-radius:2px;margin:0 auto;"></div>
  </div>
  <div class="bg-tree" style="bottom:84px;right:90px;display:flex;flex-direction:column;align-items:center;">
    <div class="bt-top" style="width:38px;height:42px;background:#3A8020;border-radius:50% 50% 40% 40%;"></div>
    <div class="bt-trunk" style="width:8px;height:18px;background:#7A5228;border-radius:2px;margin:0 auto;"></div>
  </div>

  <!-- Ground -->
  <div class="ground"></div>

  <!-- Ground flowers -->
  <div class="gflower" style="bottom:22px;left:200px;">🌼</div>
  <div class="gflower" style="bottom:28px;left:236px;">🌸</div>
  <div class="gflower" style="bottom:18px;right:198px;">🌷</div>
  <div class="gflower" style="bottom:26px;right:238px;">🌼</div>
  <div class="gflower" style="bottom:14px;left:310px;font-size:10px;">🌿</div>
  <div class="gflower" style="bottom:13px;right:305px;font-size:10px;">🌿</div>

  <!-- Sheep zone -->
  <div class="sheep-zone">
    <div class="mood-badge">😊 Bông đang vui hôm nay</div>
    <div class="sheep-glow"></div>
    __SHEEP__
    <div class="sheep-shadow"></div>
  </div>
</div>

<!-- AI COMPANION CARD -->
<div class="comp-card" style="margin-top:-4px;border-radius:0 0 24px 24px;position:relative;z-index:2;">
  <div class="comp-header">
    <div class="comp-name">🐑 Bông Cần Cù</div>
    <div class="comp-mood-tag">😊 Đang vui</div>
  </div>
  <div class="comp-thinking" id="ai-thinking">
    💭 <strong>"Hoa</strong>, bạn vẫn đang tiết kiệm cho giấc mơ MBA không? Mình đang nghĩ về bạn đó..."
  </div>
  <div style="font-size:11px;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">📌 Mình nhớ</div>
  <div class="comp-memory">
    <div class="mem-tag">🏠 Muốn mua nhà</div>
    <div class="mem-tag">🎓 Giấc mơ MBA</div>
    <div class="mem-tag">💰 Tự do tài chính</div>
    <div class="mem-tag">💭 Hay lo về dòng tiền</div>
  </div>
  <div class="comp-footer">
    <div class="streak-badge">🔥 <span>7 ngày cùng nhau</span></div>
    <div class="days-together">Quen nhau từ 01/01/2026</div>
  </div>
  <div class="chat-prompt" id="chat-btn" onclick="openChat()">
    <div class="cp-ico">💬</div>
    <div class="cp-text" id="prompt-text">Mình đang lo cho giấc mơ của bạn...</div>
    <div class="cp-arrow">→</div>
  </div>
</div>

<!-- FRIENDS FEED -->
<div class="sec">
  <div class="sec-t">🐑 Đàn cừu hôm nay</div>
  <div class="sec-a" onclick="setNav(document.querySelectorAll('.ni')[1])">Xem thêm →</div>
</div>
<div class="feed">
  <div class="fi" onclick="">
    <div class="fi-av">
      __F1__
      <div class="fi-badge">🔥</div>
    </div>
    <div class="fi-body">
      <div class="fi-top">
        <div class="fi-name">Bông Mập</div>
        <div class="fi-state fire">🔥 30 ngày</div>
      </div>
      <div class="fi-desc">Hoàn thành chuỗi tiết kiệm 30 ngày liên tiếp — không bỏ ngày nào! 💪</div>
      <div class="fi-actions">
        <button class="fa-btn orange" onclick="event.stopPropagation();celebrate()">❤️ Chúc mừng</button>
        <button class="fa-btn green" onclick="event.stopPropagation();toast('Đã gửi quà cho Bông Mập! 🎁')">🎁 Gửi quà</button>
        <button class="fa-btn blue" onclick="event.stopPropagation();toast('Đang mở chat...')">💬 Nhắn tin</button>
      </div>
    </div>
  </div>
  <div class="fi" onclick="">
    <div class="fi-av">
      __F2__
      <div class="fi-badge">😔</div>
    </div>
    <div class="fi-body">
      <div class="fi-top">
        <div class="fi-name">Mây Tích</div>
        <div class="fi-state sad">😔 Buồn</div>
      </div>
      <div class="fi-desc">Hôm nay Mây Tích có vẻ không được vui... Mình có thể gửi gì cho bạn ấy không?</div>
      <div class="fi-actions">
        <button class="fa-btn pink" onclick="event.stopPropagation();toast('Đã gửi hoa cho Mây Tích! 🌸')">🌸 Gửi hoa</button>
        <button class="fa-btn blue" onclick="event.stopPropagation();toast('Đang mở chat...')">💬 Nhắn tin</button>
        <button class="fa-btn orange" onclick="event.stopPropagation();toast('Đã gửi XP Boost! ⚡')">⚡ Boost</button>
      </div>
    </div>
  </div>
  <div class="fi" onclick="">
    <div class="fi-av">
      __F3__
      <div class="fi-badge">🏆</div>
    </div>
    <div class="fi-body">
      <div class="fi-top">
        <div class="fi-name">Cậu Nhanh</div>
        <div class="fi-state win">🏆 Lv.12</div>
      </div>
      <div class="fi-desc">Vừa đạt Level 12 — Cừu Trí Tuệ! Cùng chúc mừng Cậu Nhanh nha! 🎉</div>
      <div class="fi-actions">
        <button class="fa-btn purple" onclick="event.stopPropagation();celebrate()">🎉 Ăn mừng</button>
        <button class="fa-btn orange" onclick="event.stopPropagation();toast('Đã khen ngợi! 👏')">👏 Khen ngợi</button>
        <button class="fa-btn green" onclick="event.stopPropagation();toast('Đang thăm nông trại...')">🏡 Thăm trại</button>
      </div>
    </div>
  </div>
</div>

<!-- REFERRAL -->
<div class="ref-card" onclick="toast('Đã sao chép link mời! 🔗')">
  <div class="ref-ico">🐑</div>
  <div class="ref-text">
    <div class="ref-title">Đưa cừu mới vào đàn</div>
    <div class="ref-chips">
      <span class="ref-chip">+500 XP</span>
      <span class="ref-chip">+10 💎</span>
      <span class="ref-chip">🌟 Skin độc quyền</span>
    </div>
  </div>
  <button class="ref-btn" onclick="event.stopPropagation();toast('Đã sao chép! 🔗')">Mời ngay</button>
</div>

<div class="spacer"></div>
  </div>

  <!-- ── BOTTOM NAV ── -->
  <div class="bnav">
<div class="ni active" onclick="setNav(this)"><div class="nico">🏡</div><div class="nlb">Trang trại</div><div class="npip"></div></div>
<div class="ni" onclick="setNav(this)"><div class="nico">👥</div><div class="nlb">Bạn bè</div><div class="npip"></div><div class="nbadge">3</div></div>
<div class="ni" onclick="openChat()"><div class="nico">💬</div><div class="nlb">Chat</div><div class="npip"></div><div class="nbadge">1</div></div>
<div class="ni" onclick="setNav(this)"><div class="nico">✨</div><div class="nlb">Giấc mơ</div><div class="npip"></div></div>
<div class="ni" onclick="setNav(this)"><div class="nico">👤</div><div class="nlb">Cá nhân</div><div class="npip"></div></div>
  </div>

  <!-- ── CHAT OVERLAY ── -->
  <div class="overlay" id="chat-overlay">
<div class="ov-header">
  <div class="ov-back" onclick="closeChat()">←</div>
  <div class="ov-title">💬 Trò chuyện</div>
</div>
<div class="ov-scroll">
  <div class="ov-sec">Cừu của mình</div>
  <div class="chat-row" onclick="toast('Đang mở chat với Bông...')">
    <div class="chat-row-av" style="background:linear-gradient(135deg,#FFE066,#FF9500);">🐑</div>
    <div>
      <div class="cr-name">Bông Cần Cù</div>
      <div class="cr-sub">Đang online · Muốn hỏi bạn điều gì đó...</div>
    </div>
    <div class="cr-badge">1</div>
  </div>

  <div class="ov-sec">Bạn bè</div>
  <div class="chat-row" onclick="toast('Đang mở chat với Bông Mập...')">
    <div class="chat-row-av" style="background:#F5ECD8;font-size:24px;text-align:center;line-height:48px;">__F1_SM__</div>
    <div>
      <div class="cr-name">Bông Mập</div>
      <div class="cr-sub">🔥 30-ngày streak · "Tuyệt vời quá!"</div>
    </div>
  </div>
  <div class="chat-row" onclick="toast('Đang mở chat với Mây Tích...')">
    <div class="chat-row-av" style="background:#F5ECD8;font-size:24px;text-align:center;line-height:48px;">__F2_SM__</div>
    <div>
      <div class="cr-name">Mây Tích</div>
      <div class="cr-sub">😔 Có vẻ cần động viên hôm nay</div>
    </div>
  </div>
  <div class="chat-row" onclick="toast('Đang mở chat với Cậu Nhanh...')">
    <div class="chat-row-av" style="background:#F5ECD8;font-size:24px;text-align:center;line-height:48px;">__F3_SM__</div>
    <div>
      <div class="cr-name">Cậu Nhanh</div>
      <div class="cr-sub">🏆 Mới đạt Level 12!</div>
    </div>
  </div>

  <div class="ov-sec">Cộng đồng Giấc Mơ</div>
  <div class="community-grid">
    <div class="comm-card" onclick="toast('Đang vào cộng đồng Du học...')">
      <div class="comm-ico">🎓</div>
      <div class="comm-name">Du học</div>
      <div class="comm-members">2.341 thành viên</div>
    </div>
    <div class="comm-card" onclick="toast('Đang vào cộng đồng Mua nhà...')">
      <div class="comm-ico">🏠</div>
      <div class="comm-name">Mua nhà đầu tiên</div>
      <div class="comm-members">5.128 thành viên</div>
    </div>
    <div class="comm-card" onclick="toast('Đang vào cộng đồng FIRE...')">
      <div class="comm-ico">💰</div>
      <div class="comm-name">FIRE</div>
      <div class="comm-members">1.892 thành viên</div>
    </div>
    <div class="comm-card" onclick="toast('Đang vào cộng đồng Startup...')">
      <div class="comm-ico">🚀</div>
      <div class="comm-name">Startup</div>
      <div class="comm-members">987 thành viên</div>
    </div>
    <div class="comm-card" onclick="toast('Đang vào cộng đồng MBA...')">
      <div class="comm-ico">📚</div>
      <div class="comm-name">MBA</div>
      <div class="comm-members">643 thành viên</div>
    </div>
    <div class="comm-card" onclick="toast('Đang vào cộng đồng Freelance...')">
      <div class="comm-ico">💻</div>
      <div class="comm-name">Freelance</div>
      <div class="comm-members">3.210 thành viên</div>
    </div>
  </div>
  <div style="height:16px;"></div>
</div>
  </div>

</div>

<div id="toast"></div>
<div id="confetti"></div>

<script>
// ── CHAT PROMPTS (AI-initiated) ──
var prompts = [
  "Mình đang lo cho giấc mơ của bạn...",
  "Hoa, bạn có chuyện gì muốn kể không?",
  "Tuần này có điều gì tốt xảy ra không?",
  "Bạn ổn không? Mình muốn nghe bạn kể.",
  "Mình vừa nhớ ra điều gì đó về bạn nè...",
  "Nói chuyện với mình đi, mình đang đây!"
];
var thinkings = [
  '💭 <strong>"Hoa</strong>, bạn vẫn đang tiết kiệm cho giấc mơ MBA không? Mình đang nghĩ về bạn đó..."',
  '💭 <strong>"Hoa</strong>, hôm nay bạn có cần mình không? Mình luôn ở đây nha..."',
  '💭 <strong>"Hoa</strong>, mình nhớ bạn nói muốn mua nhà — bạn đang tiến đến đó rồi đó! 🏠"',
  '💭 <strong>"Hoa</strong>, 7 ngày rồi đó — bạn đang làm rất tốt, mình tự hào về bạn! ❤️"'
];

var pi = Math.floor(Math.random() * prompts.length);
var ti = Math.floor(Math.random() * thinkings.length);
document.getElementById("prompt-text").textContent = prompts[pi];
document.getElementById("ai-thinking").innerHTML = thinkings[ti];

// Rotate prompt every 6s
setInterval(function() {
  pi = (pi + 1) % prompts.length;
  var el = document.getElementById("prompt-text");
  el.style.opacity = "0";
  setTimeout(function() {
el.textContent = prompts[pi];
el.style.opacity = "1";
  }, 250);
}, 6000);

// ── SHEEP FEED ──
var feedMsgs = [
  '💭 <strong>"Hoa</strong>, cảm ơn bạn đã cho mình ăn! Mình yêu bạn! ❤️"',
  '💭 <strong>"Yay!</strong> Mình đầy năng lượng rồi! Cùng cố gắng nhé! 💪"',
  '💭 <strong>"Ngon</strong> quá Hoa ơi! Mình sẽ tiết kiệm thêm cho bạn! 🎉"',
  '💭 <strong>"Mình</strong> lớn thêm rồi! Nhờ có bạn đó, cảm ơn! 🌟"'
];
function feedSheep() {
  var s = document.getElementById("sheep");
  if (!s) return;
  s.style.animationPlayState = "paused";
  s.style.transition = "transform 0.25s cubic-bezier(.34,1.56,.64,1)";
  s.style.transform = "translateY(-14px) scale(1.12)";
  setTimeout(function() {
s.style.transform = "";
s.style.transition = "";
setTimeout(function() { s.style.animationPlayState = "running"; }, 300);
  }, 300);
  spawnConfetti(14);
  var msg = feedMsgs[Math.floor(Math.random() * feedMsgs.length)];
  document.getElementById("ai-thinking").innerHTML = msg;
  toast("Bông lớn thêm 2%! 🥕");
}

// ── CHAT OVERLAY ──
function openChat() {
  document.getElementById("chat-overlay").classList.add("open");
  document.querySelectorAll(".ni").forEach(function(n) { n.classList.remove("active"); });
  document.querySelectorAll(".ni")[2].classList.add("active");
}
function closeChat() {
  document.getElementById("chat-overlay").classList.remove("open");
  document.querySelectorAll(".ni").forEach(function(n) { n.classList.remove("active"); });
  document.querySelectorAll(".ni")[0].classList.add("active");
}

// ── CELEBRATE ──
function celebrate() {
  spawnConfetti(20);
  toast("Chúc mừng! 🎉");
}

// ── NAV ──
function setNav(el) {
  document.querySelectorAll(".ni").forEach(function(n) { n.classList.remove("active"); });
  el.classList.add("active");
}

// ── CONFETTI ──
function spawnConfetti(n) {
  var layer = document.getElementById("confetti");
  var cols = ["#FF6B6B","#FFD93D","#6BCF6B","#4ECDC4","#FF9500","#C77DFF","#FF85A1","#4FC3F7"];
  for (var i = 0; i < (n || 12); i++) {
(function() {
  var el = document.createElement("div");
  var sz = 6 + Math.random() * 8;
  el.style.cssText = [
    "position:absolute",
    "width:" + sz + "px", "height:" + sz + "px",
    "background:" + cols[Math.floor(Math.random() * cols.length)],
    "border-radius:" + (Math.random() > 0.5 ? "50%" : "3px"),
    "left:" + (Math.random() * 860) + "px",
    "top:" + (100 + Math.random() * 200) + "px",
    "animation:drop " + (0.8 + Math.random() * 0.9) + "s ease-out forwards",
    "pointer-events:none"
  ].join(";");
  layer.appendChild(el);
  setTimeout(function() { el.remove(); }, 1800);
})();
  }
}

// ── TOAST ──
var _toastT;
function toast(msg) {
  var t = document.getElementById("toast");
  t.textContent = msg;
  t.style.opacity = "1"; t.style.transform = "translateX(-50%) translateY(0)";
  clearTimeout(_toastT);
  _toastT = setTimeout(function() {
t.style.opacity = "0"; t.style.transform = "translateX(-50%) translateY(10px)";
  }, 2200);
}
</script>
</body>
</html>
"""

    _HTML = _HTML.replace("__SHEEP__", _sheep_el)
    _HTML = _HTML.replace("__F1__",    _av("f1", 44))
    _HTML = _HTML.replace("__F2__",    _av("f2", 44))
    _HTML = _HTML.replace("__F3__",    _av("f3", 44))
    # Small versions in chat overlay
    _HTML = _HTML.replace("__F1_SM__", "🐑" if not _FA.get("f1") else "")
    _HTML = _HTML.replace("__F2_SM__", "🐑" if not _FA.get("f2") else "")
    _HTML = _HTML.replace("__F3_SM__", "🐑" if not _FA.get("f3") else "")

    import streamlit.components.v1 as components
    components.html(_HTML, height=820, scrolling=False)

