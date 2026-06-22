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

MEMORY_DEFAULT: dict = {
    "name":          "",
    "notes":         [],
    "life_events":   [],
    "dreams":        [],
    "total_saved":   0,
    "streak":        0,
    "last_fed_date":   "",
    "last_visit_date": "",
    "sentiment":       "neutral",
    "wealth_genome": {
        "risk_type":   "",
        "personality": "",
        "stage":       "",
    },
    "diary_entries": [],
    "last_fed_amount": 0,
    "last_fed_food":   "",
    "just_leveled_up": False,
    "prev_stage_key":  "baby",
    # ── Behavioral Finance Engine ──
    "user_exp":         0,
    "current_level":    1,
    "ilucky_tickets":   0,
    "achievements":     [],
    "daily_quests":     {},
    "last_visit_date":  "",
    "hunger":           100,
    "market_mood":      "normal",
    "new_level_name":   "",
    "new_level_tickets": 0,
}

MICRO_AMOUNTS = [10_000, 20_000, 50_000, 100_000]

FEED_OPTIONS = [
    (10_000,  "🥬", "Bó Cỏ"),
    (20_000,  "🥕", "Cà Rốt"),
    (50_000,  "🍎", "Táo"),
    (100_000, "🎂", "Tiệc Sinh Nhật"),
    (500_000, "🎉", "Đại Tiệc"),
]


def _init():
    defs = {
        "api_key":      "",
        "messages":     [],
        "user_memory":  deepcopy(MEMORY_DEFAULT),
        "sheep_mood":   "default",
        "_quick_reply": None,
        "feeding_celebration": False,
        "feeding_refused":     False,
        "diary_mood_sel":      None,
        "diary_just_saved":    False,
        "diary_last_entry":    None,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()
mem: dict = st.session_state.user_memory


def _save():
    st.session_state.user_memory = mem


# ═══════════════════════════════════════════════════════
# EXP + LEVEL SYSTEM
# ═══════════════════════════════════════════════════════
EXP_LEVELS  = {1: 0, 2: 500, 3: 1_500, 4: 3_000, 5: 6_000, 6: 12_000}
LEVEL_NAMES = {
    1: "🐑 Cừu Sơ Sinh",  2: "🐑 Cừu Non",
    3: "🐑 Cừu Thiếu Niên", 4: "🐑 Cừu Trưởng Thành",
    5: "🐑 Cừu Lão Luyện",  6: "🐑 Cừu Huyền Thoại",
}
LEVEL_ILUCKY = {2: 1, 3: 2, 4: 3, 5: 5, 6: 10}
LEVEL_ITEMS  = {
    2: ["🎩 Mũ Sinh Viên"],
    3: ["👔 Vest Xanh TCBS", "🎒 Balo"],
    4: ["⌚ Đồng Hồ", "🏠 Nhà Gỗ"],
    5: ["🚗 Xe Mini", "🏡 Nhà Cao Cấp"],
    6: ["👑 Vương Miện", "🏰 Lâu Đài Cừu"],
}
ACHIEVEMENTS_DEF = [
    ("first_chat",   "🌱 Bắt đầu hành trình",  "Lần đầu nói chuyện với Cừu"),
    ("streak_7",     "🔥 Bảy ngày liên tiếp",   "Streak 7 ngày không gián đoạn"),
    ("streak_30",    "💎 Ba mươi ngày bền bỉ",  "Streak 30 ngày"),
    ("quest_50",     "🎯 Hoàn thành 50 nhiệm vụ","Hoàn thành 50 Daily Quest"),
    ("level_4",      "🏠 Nhà đầu tư kiên trì",  "Đạt Level 4"),
    ("level_max",    "👑 Cừu trưởng thành",      "Đạt Level 6 Huyền Thoại"),
    ("invite_1",     "👯 Bạn cừu đầu tiên",     "Mời 1 người bạn thành công"),
]

def get_exp_level(exp: int) -> int:
    lv = 1
    for l, th in sorted(EXP_LEVELS.items()):
        if exp >= th:
            lv = l
    return min(lv, 6)

def exp_progress(exp: int) -> tuple:
    lv = get_exp_level(exp)
    if lv >= 6:
        return exp - EXP_LEVELS[6], EXP_LEVELS[6], 100.0
    cur_th  = EXP_LEVELS[lv]
    next_th = EXP_LEVELS[lv + 1]
    in_lv   = exp - cur_th
    needed  = next_th - cur_th
    return in_lv, needed, min(100.0, in_lv / needed * 100)

def _add_exp(amount: int, _mem: dict) -> bool:
    """Add EXP. Returns True if level-up occurred."""
    old_lv = get_exp_level(_mem.get("user_exp", 0))
    _mem["user_exp"] = _mem.get("user_exp", 0) + amount
    new_lv = get_exp_level(_mem["user_exp"])
    if new_lv > old_lv:
        _mem["current_level"]    = new_lv
        tickets = LEVEL_ILUCKY.get(new_lv, 0)
        _mem["ilucky_tickets"]   = _mem.get("ilucky_tickets", 0) + tickets
        _mem["just_leveled_up"]  = True
        _mem["new_level_name"]   = LEVEL_NAMES[new_lv]
        _mem["new_level_tickets"] = tickets
        return True
    return False

def _get_today_q(_mem: dict) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    qs = _mem.get("daily_quests", {})
    if today not in qs:
        qs[today] = {"visit": False, "chat": False, "diary": False, "feed": False, "bonus_claimed": False}
        _mem["daily_quests"] = qs
    return qs[today], today

def _complete_quest(_mem: dict, key: str, exp: int):
    q, today = _get_today_q(_mem)
    if q.get(key): return
    q[key] = True
    _mem["daily_quests"][today] = q
    _add_exp(exp, _mem)
    q2 = _mem["daily_quests"][today]
    if (q2["visit"] and q2["chat"] and q2["diary"] and q2["feed"]
            and not q2.get("bonus_claimed")):
        _add_exp(50, _mem)
        _mem["daily_quests"][today]["bonus_claimed"] = True
    # achievements
    _check_achievements(_mem)

def _check_achievements(_mem: dict):
    earned = set(_mem.get("achievements", []))
    streak = _mem.get("streak", 0)
    if _mem.get("messages") or True:
        earned.add("first_chat")   # mark when chat tab visited
    if streak >= 7:  earned.add("streak_7")
    if streak >= 30: earned.add("streak_30")
    if get_exp_level(_mem.get("user_exp", 0)) >= 4: earned.add("level_4")
    if get_exp_level(_mem.get("user_exp", 0)) >= 6: earned.add("level_max")
    total_q = sum(1 for dq in _mem.get("daily_quests", {}).values()
                  for k, v in dq.items() if k not in ("bonus_claimed",) and v)
    if total_q >= 50: earned.add("quest_50")
    _mem["achievements"] = list(earned)

def _get_hunger(_mem: dict) -> tuple:
    """Return (pct, state, msg)."""
    last = _mem.get("last_fed_date", "")
    if not last: return 70, "normal", ""
    try:
        days = (datetime.now().date() - datetime.strptime(last, "%Y-%m-%d").date()).days
    except: return 70, "normal", ""
    if days == 0: return 100, "fed", "🐑 Cừu vừa được cho ăn hôm nay!"
    if days == 1: return 80, "ok",  ""
    if days <= 3: return 50, "hungry",   "🐑 Mình hơi đói rồi... bữa nay cho mình ăn nhé?"
    if days <= 7: return 25, "miss_you", f"🐑 Mình nhớ bạn lắm... đã {days} ngày rồi."
    return 8, "lonely", f"🌱 Không sao cả. Mình vẫn ở đây chờ bạn sau {days} ngày."

def _return_msg(_mem: dict, today_str: str) -> tuple:
    """(days_away, emoji, title, body) — None if same day."""
    last = _mem.get("last_visit_date", "")
    if last == today_str or not last: return 0, None, None, None
    try:
        days = (datetime.now().date() - datetime.strptime(last, "%Y-%m-%d").date()).days
    except: return 0, None, None, None
    if days <= 0: return 0, None, None, None
    if days == 1: return days, "💙", "Bạn quay lại rồi!", "Mình vui lắm khi thấy bạn hôm nay~"
    if days <= 3: return days, "🐑", "Mình vẫn đợi bạn.", f"Đã {days} ngày — hôm nay cho mình ăn nhé?"
    if days <= 7: return days, "🥺", "Mình nhớ bạn lắm.", f"Xa nhau {days} ngày... nhưng mình vẫn ở đây."
    return days, "🌱", "Không sao cả.", f"Đã {days} ngày rồi... Mình biết cuộc sống bận rộn. Mình vẫn ở đây đồng hành với bạn."


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
# 💬 Tâm sự · 🐑 Cừu của tôi · 👥 Cộng đồng
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "💬 Tâm sự",
    "🐑 Cừu của tôi",
    "👥 Cộng đồng",
])

# ═══════════════════════════════════════════════════════
# TAB 1 — TÂM SỰ  (Chat + Diary merged)
# Sub-views: 💬 Trò chuyện | 📔 Nhật ký
# ═══════════════════════════════════════════════════════
with tab1:

    # ── Sub-view toggle ──
    st.markdown(
        '<div style="display:flex;justify-content:center;margin-bottom:8px;"></div>',
        unsafe_allow_html=True,
    )
    _tamsự_view = st.radio(
        "",
        ["💬 Trò chuyện với Cừu", "📔 Nhật ký tâm sự"],
        horizontal=True,
        label_visibility="collapsed",
        key="tamsự_view",
    )
    st.markdown('<div style="margin-bottom:4px;"></div>', unsafe_allow_html=True)

    if _tamsự_view == "💬 Trò chuyện với Cừu":
        # ══════════════════════════════════════════════
        # CHAT VIEW — Cừu lắng nghe
        # ══════════════════════════════════════════════

            # ── Detect returning user ──
            _today_str   = datetime.now().strftime("%Y-%m-%d")
            _last_visit  = mem.get("last_visit_date", "")
            _is_returning = bool(_last_visit) and _last_visit != _today_str
            if mem.get("last_visit_date") != _today_str:
                mem["last_visit_date"] = _today_str
                _save()

            # ──────────────────────────────────────────────────
            # LEVEL 1: MASCOT — trung tâm màn hình, 300px
            # ──────────────────────────────────────────────────
            # Emotion Engine: chọn mood dựa trên context
            _hero_mood = st.session_state.get("sheep_mood", "default")
            if _is_returning and not st.session_state.messages:
                _hero_mood = "miss_you"       # Cừu nhớ bạn
            elif not st.session_state.messages:
                _hero_mood = "listening"      # Cừu đang sẵn sàng

            _hero_src = _b64(_pick_mascot(_hero_mood))
            st.markdown(
                f'<div style="text-align:center;padding:28px 0 10px;">'
                f'<img src="{_hero_src}" width="300" '
                f'style="border-radius:50%;'
                f'border:6px solid #FFB5C8;'
                f'box-shadow:0 20px 60px rgba(255,140,190,0.45),'
                f'0 0 0 16px rgba(255,182,193,0.13);" />'
                f'</div>',
                unsafe_allow_html=True,
            )

            # ──────────────────────────────────────────────────
            # LEVEL 2: TAGLINE — "Mình đang nghe đây"
            # ──────────────────────────────────────────────────
            _name_str  = mem.get("name", "").strip()
            _return_line = ""
            if _is_returning and _name_str:
                _return_line = (
                    f'<div style="color:#FF8FAF;font-size:0.92rem;font-weight:600;'
                    f'margin-bottom:6px;">💙 {_name_str} ơi, mình nhớ bạn lắm!</div>'
                )
            elif _is_returning:
                _return_line = (
                    '<div style="color:#FF8FAF;font-size:0.92rem;font-weight:600;'
                    'margin-bottom:6px;">💙 Bạn quay lại rồi! Mình nhớ bạn lắm!</div>'
                )

            st.markdown(
                f'<div style="text-align:center;padding:4px 0 18px;">'
                f'{_return_line}'
                f'<div style="font-size:1.65rem;font-weight:800;color:#C4607F;margin-bottom:7px;">'
                f'🐑 Mình đang nghe đây</div>'
                f'<div style="font-size:0.97rem;color:#666;margin-bottom:4px;">'
                f'Có chuyện gì đang diễn ra với bạn hôm nay?</div>'
                f'<div style="font-size:0.88rem;color:#bbb;">'
                f'Bạn có thể kể cho mình bất cứ điều gì.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # ──────────────────────────────────────────────────
            # PHẦN 6: HÀNH TRÌNH QUAY LẠI — streak card
            # ──────────────────────────────────────────────────
            if mem.get("streak", 0) > 1:
                _, _t1_sname, _, _, _ = get_growth_stage(mem["total_saved"])
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,'
                    f'rgba(255,245,250,0.95),rgba(238,245,255,0.95));'
                    f'border:1.5px solid #FFD6E8;border-radius:16px;'
                    f'padding:11px 22px;text-align:center;margin:0 0 14px;">'
                    f'🐑 Hôm nay là ngày thứ '
                    f'<strong style="color:#C4607F;">{mem["streak"]}</strong>'
                    f' bạn gặp mình &nbsp;·&nbsp; '
                    f'🔥 Streak <strong>{mem["streak"]} ngày</strong>'
                    f' &nbsp;·&nbsp; {_t1_sname}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # ──────────────────────────────────────────────────
            # PHẦN 2: MEMORY CARD — "Điều mình đang nhớ về bạn"
            # ──────────────────────────────────────────────────
            _mem_items = _build_memory_card(mem)
            if _mem_items:
                _mem_chips = "".join(
                    f'<span style="display:inline-flex;align-items:center;gap:4px;'
                    f'background:white;border:1.5px solid #FFD6E8;border-radius:20px;'
                    f'padding:5px 13px;font-size:0.87rem;color:#444;'
                    f'margin:3px 2px;white-space:nowrap;">{_e} {_t}</span>'
                    for _e, _t in _mem_items
                )
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,'
                    f'rgba(255,220,235,0.25),rgba(210,230,255,0.25));'
                    f'border:1.5px solid #FFD6E8;border-radius:18px;'
                    f'padding:16px 20px;margin:0 0 14px;">'
                    f'<div style="font-size:0.88rem;font-weight:700;color:#C4607F;'
                    f'margin-bottom:11px;">🐑 Điều mình đang nhớ về bạn</div>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:0;">{_mem_chips}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="background:rgba(255,220,235,0.1);'
                    'border:1.5px solid #FFD6E8;border-radius:18px;'
                    'padding:13px 20px;margin:0 0 12px;text-align:center;">'
                    '<span style="color:#bbb;font-size:0.88rem;">'
                    '🐑 Mình vẫn đang tìm hiểu thêm về bạn...</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            # ──────────────────────────────────────────────────
            # PHẦN 4: PROGRESS STRIP — chỉ khi có dữ liệu
            # ──────────────────────────────────────────────────
            _has_prog = (
                mem.get("streak", 0) > 0
                or mem.get("total_saved", 0) > 0
                or mem.get("dreams")
                or len(st.session_state.messages) >= 2
            )
            if _has_prog:
                _, _ps_name, _, _, _ = get_growth_stage(mem["total_saved"])
                _pd_dream = mem["dreams"][0]["name"].title() if mem.get("dreams") else "—"
                _pt_tag   = (
                    LIFE_EVENT_LABELS.get(mem["life_events"][-1], "—")
                    if mem.get("life_events") else "—"
                )
                _p_chats  = len(st.session_state.messages) // 2
                _pc1, _pc2, _pc3, _pc4 = st.columns(4)
                for _pcol, _pval, _plbl in [
                    (_pc1, str(mem.get("streak", 0)), "🔥 Streak"),
                    (_pc2, _ps_name,                  "🐑 Cừu lớn"),
                    (_pc3, _pd_dream[:14],            "🎯 Giấc mơ"),
                    (_pc4, str(_p_chats),             "💬 Lần chat"),
                ]:
                    _pcol.markdown(
                        f'<div class="diary-stat-mini">'
                        f'<div style="font-size:0.88rem;font-weight:800;'
                        f'color:#C4607F;line-height:1.3;">{_pval}</div>'
                        f'<div style="font-size:0.73rem;color:#888;margin-top:2px;">{_plbl}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    '<div style="margin-bottom:14px;"></div>', unsafe_allow_html=True
                )

            # ──────────────────────────────────────────────────
            # PHẦN 3: CHIPS — ngắn, hội thoại, chỉ khi chưa chat
            # ──────────────────────────────────────────────────
            if not st.session_state.messages:
                _chips_v2 = [
                    "📚 Em đang áp lực chuyện học",
                    "💸 Em đang lo về tiền bạc",
                    "💔 Hôm nay em không vui",
                    "✨ Em có một giấc mơ",
                    "🌱 Em muốn thay đổi cuộc sống",
                    "💼 Em đang suy nghĩ về công việc",
                ]
                _chip_prompts_v2 = {
                    "📚 Em đang áp lực chuyện học":
                        "Cừu ơi, em đang rất áp lực về việc học và kỳ thi. Lắng nghe em với nhé?",
                    "💸 Em đang lo về tiền bạc":
                        "Cừu ơi, em đang lo lắng về tài chính và tiền bạc, áp lực lắm.",
                    "💔 Hôm nay em không vui":
                        "Cừu ơi, hôm nay em không vui, muốn chia sẻ với Cừu.",
                    "✨ Em có một giấc mơ":
                        "Cừu ơi, em có một ước mơ muốn kể! Em cần được động viên.",
                    "🌱 Em muốn thay đổi cuộc sống":
                        "Cừu ơi, em muốn thay đổi cuộc sống nhưng chưa biết bắt đầu từ đâu.",
                    "💼 Em đang suy nghĩ về công việc":
                        "Cừu ơi, em đang cân nhắc thay đổi hướng đi sự nghiệp, cần được lắng nghe.",
                }
                _qcols = st.columns(3)
                for _ci, _chip in enumerate(_chips_v2):
                    if _qcols[_ci % 3].button(_chip, use_container_width=True, key=f"chip_{_ci}"):
                        st.session_state._quick_reply = _chip_prompts_v2[_chip]
                        st.session_state.messages.append({"role": "user", "content": _chip})
                        st.rerun()

            # ── Handle quick reply ──
            if st.session_state._quick_reply:
                _qr = st.session_state._quick_reply
                st.session_state._quick_reply = None
                with st.spinner("Cừu đang nghĩ... 🐑"):
                    _result_qr = _call_llm(_qr, _SYS_EMOTION)
                _reply_qr = _result_qr.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe!")
                st.session_state.messages.append({"role": "assistant", "content": _reply_qr})
                st.rerun()

            # ── Smart suggestion (contextual only) ──
            _suggestion = get_smart_suggestion(st.session_state.messages, mem)
            if _suggestion:
                st.markdown(
                    f'<div class="suggestion-box">{_suggestion}</div>',
                    unsafe_allow_html=True,
                )

            # ── LEVEL 5: Chat history ──
            if st.session_state.messages:
                st.markdown("---")
                for _m in st.session_state.messages[-12:]:
                    _av = get_avatar_src("listening") if _m["role"] == "assistant" else "🧑"
                    with st.chat_message(_m["role"], avatar=_av):
                        st.markdown(_m["content"])

            # ── Chat input ──
            _user_msg = st.chat_input("Nhắn tin với Cừu Cần Cù... 🐑")
            if _user_msg:
                _expanded = _EMOTION_EXPAND.get(_user_msg.strip().lower(), _user_msg)
                st.session_state.messages.append({"role": "user", "content": _user_msg})
                with st.spinner("Cừu đang lắng nghe... 🐑"):
                    _result_msg = _call_llm(_expanded, _SYS_EMOTION)
                _reply_msg = _result_msg.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe nè!")
                st.session_state.messages.append({"role": "assistant", "content": _reply_msg})
                st.rerun()




    else:
        # ══════════════════════════════════════════════
        # DIARY VIEW — Nhật ký tâm sự
        # ══════════════════════════════════════════════
            diary_entries: list[dict] = mem.get("diary_entries", [])

            # ── PHẦN 1: HERO — sheep_diary + tagline ──
            col_dimg, col_dhdr = st.columns([1, 4])
            with col_dimg:
                show_sheep("diary", width=180, show_badge=False)
            with col_dhdr:
                st.title("🐑 Nhật Ký Tâm Sự")
                st.markdown(
                    '<div class="diary-framing">'
                    '<strong style="color:#5A7A4A;font-size:1rem;">'
                    '📖 Cừu sẽ giữ giúp bạn những điều của hôm nay.</strong><br/>'
                    '<span style="color:#777;font-size:0.88rem;">'
                    'Để sau này nhìn lại, bạn sẽ thấy mình đã trưởng thành như thế nào.<br/>'
                    '<em>Không phải chat realtime — đây là không gian riêng tư của bạn.</em>'
                    '</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            # ── PHẦN 6: PROGRESS STATS — chỉ hiện khi có entries ──
            if diary_entries:
                d_streak  = _diary_streak(diary_entries)
                d_theme   = _top_diary_theme(diary_entries)
                d_dream   = _top_diary_dream(diary_entries)
                d_last_r  = diary_entries[0].get("reply", "") if diary_entries else ""
                top_lbl   = LIFE_EVENT_LABELS.get(d_theme, d_theme) if d_theme else "—"
                dream_lbl = d_dream.title() if d_dream else "—"

                st.markdown("---")
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                sc1.markdown(
                    f'<div class="diary-stat-mini">'
                    f'<div style="font-size:1.3rem;font-weight:800;color:#C4607F;">{len(diary_entries)}</div>'
                    f'<div style="font-size:0.76rem;color:#888;">📖 Tổng trang</div>'
                    f'</div>', unsafe_allow_html=True,
                )
                sc2.markdown(
                    f'<div class="diary-stat-mini">'
                    f'<div style="font-size:1.3rem;font-weight:800;color:#C4607F;">{d_streak}</div>'
                    f'<div style="font-size:0.76rem;color:#888;">🔥 Streak</div>'
                    f'</div>', unsafe_allow_html=True,
                )
                sc3.markdown(
                    f'<div class="diary-stat-mini">'
                    f'<div style="font-size:0.85rem;font-weight:700;color:#4E7DB8;">{top_lbl[:16]}</div>'
                    f'<div style="font-size:0.76rem;color:#888;">💙 Hay tâm sự</div>'
                    f'</div>', unsafe_allow_html=True,
                )
                sc4.markdown(
                    f'<div class="diary-stat-mini">'
                    f'<div style="font-size:0.85rem;font-weight:700;color:#4E7DB8;">{dream_lbl[:16]}</div>'
                    f'<div style="font-size:0.76rem;color:#888;">🎯 Giấc mơ thường</div>'
                    f'</div>', unsafe_allow_html=True,
                )
                preview_r = f'"{d_last_r[:36]}..."' if len(d_last_r) > 36 else f'"{d_last_r}"'
                sc5.markdown(
                    f'<div class="diary-stat-mini">'
                    f'<div style="font-size:0.78rem;color:#666;font-style:italic;">{preview_r}</div>'
                    f'<div style="font-size:0.76rem;color:#888;">🐑 Cừu nhớ nhất</div>'
                    f'</div>', unsafe_allow_html=True,
                )

            st.markdown("---")

            DIARY_MOODS_V2 = [
                ("😊", "Mình rất vui"),
                ("😔", "Có chút áp lực"),
                ("😴", "Hơi mệt"),
                ("😡", "Bực một chuyện"),
                ("💪", "Đang quyết tâm"),
                ("🥹", "Muốn được lắng nghe"),
            ]

            col_write, col_history = st.columns([3, 2])

            # ─────────────────────────────────────────────────────
            # LEFT: WRITING SECTION
            # ─────────────────────────────────────────────────────
            with col_write:

                # ── PHẦN 4: INSIGHT CARD — hiển thị sau khi lưu ──
                if st.session_state.get("diary_just_saved") and st.session_state.get("diary_last_entry"):
                    last_e   = st.session_state.diary_last_entry
                    insights = _build_diary_insights(
                        last_e.get("mood", ""),
                        last_e.get("tags", []),
                        last_e.get("dream", ""),
                        last_e.get("content", ""),
                    )
                    diary_src = _b64(_pick_mascot("diary"))

                    insight_html = "".join(
                        f'<div style="display:flex;align-items:flex-start;gap:8px;margin:5px 0;text-align:left;">'
                        f'<span style="color:#FF8FAF;font-weight:700;flex-shrink:0;">•</span>'
                        f'<span style="font-size:0.9rem;color:#444;line-height:1.5;">{ins}</span>'
                        f'</div>'
                        for ins in insights
                    )
                    st.markdown(
                        f'<div class="insight-card">'
                        f'<img src="{diary_src}" width="88" '
                        f'style="border-radius:50%;border:4px solid #FFB5C8;margin-bottom:12px;" /><br/>'
                        f'<strong style="color:#C4607F;font-size:1.08rem;">'
                        f'🐑 Hôm nay mình hiểu thêm về bạn</strong>'
                        f'<div style="margin:14px 0 10px;padding:0 4px;">{insight_html}</div>'
                        f'<div style="color:#4E7DB8;font-size:0.92rem;font-style:italic;">'
                        f'💙 Mình sẽ nhớ điều này giúp bạn.</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if last_e.get("reply"):
                        st.markdown(
                            f'<div style="background:rgba(255,182,210,0.15);border-radius:14px;'
                            f'padding:12px 16px;margin:6px 0 14px;font-style:italic;color:#C4607F;">'
                            f'🐑 Cừu nhắn: <strong>{last_e["reply"]}</strong>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    if last_e.get("dream"):
                        st.markdown(
                            f'<div style="background:rgba(200,240,200,0.3);border-radius:12px;'
                            f'padding:10px 14px;margin:6px 0;">'
                            f'✨ Cừu phát hiện giấc mơ: <strong>{last_e["dream"]}</strong>!'
                            f'</div>',
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
                    # ── PHẦN 2: CHỌN CẢM XÚC — mood chips ──
                    st.markdown(
                        '<div style="font-size:1rem;font-weight:700;color:#C4607F;margin-bottom:10px;">'
                        '🐑 Hôm nay bạn thế nào?</div>',
                        unsafe_allow_html=True,
                    )
                    mood_cols = st.columns(3)
                    for i, (emoji, label) in enumerate(DIARY_MOODS_V2):
                        full_label = f"{emoji} {label}"
                        is_sel     = (st.session_state.get("diary_mood_sel") == full_label)
                        if mood_cols[i % 3].button(
                            full_label,
                            key=f"dmood_{i}",
                            use_container_width=True,
                            type="primary" if is_sel else "secondary",
                        ):
                            st.session_state.diary_mood_sel = full_label
                            st.rerun()

                    current_mood = st.session_state.get("diary_mood_sel") or ""

                    # ── PHẦN 3: 3 KHUNG VIẾT CÓ GỢI MỞ ──
                    st.markdown(
                        '<div class="diary-prompt">🐑 Hôm nay điều gì khiến bạn nhớ nhất?</div>',
                        unsafe_allow_html=True,
                    )
                    q1 = st.text_area(
                        "",
                        placeholder="Kể cho mình nghe... (không cần viết nhiều)",
                        height=100, key="dq1", label_visibility="collapsed",
                    )

                    st.markdown(
                        '<div class="diary-prompt">🐑 Có điều gì khiến bạn vui, buồn hoặc lo lắng không?</div>',
                        unsafe_allow_html=True,
                    )
                    q2 = st.text_area(
                        "",
                        placeholder="Vài dòng thôi cũng được...",
                        height=100, key="dq2", label_visibility="collapsed",
                    )

                    st.markdown(
                        '<div class="diary-prompt">🐑 Có điều gì bạn muốn nhắn cho chính mình trong tương lai?</div>',
                        unsafe_allow_html=True,
                    )
                    q3 = st.text_area(
                        "",
                        placeholder="Ghi lại điều bạn muốn nhớ...",
                        height=100, key="dq3", label_visibility="collapsed",
                    )

                    # ── PHẦN 4: SAVE CTA ──
                    has_content = any([q1.strip(), q2.strip(), q3.strip()])
                    if st.button(
                        "💾 Lưu vào nhật ký của Cừu",
                        type="primary",
                        use_container_width=True,
                        disabled=not has_content,
                    ):
                        combined = "\n\n".join(filter(None, [
                            f"Điều nhớ nhất: {q1.strip()}"       if q1.strip() else "",
                            f"Cảm xúc hôm nay: {q2.strip()}"     if q2.strip() else "",
                            f"Nhắn cho tương lai: {q3.strip()}"   if q3.strip() else "",
                        ]))
                        sheep_reply  = "Bê bê~ 🐑 Cừu đã đọc rồi! Cảm ơn bạn đã tin tưởng 💙"
                        emotion_tag  = "bình_thường"
                        dream_det    = ""
                        entry_tags: list[str] = []

                        if st.session_state.api_key:
                            with st.spinner("Cừu đang đọc nhật ký... 📖"):
                                r = _call_llm(
                                    f"Nhật ký hôm nay:\nTâm trạng: {current_mood}\n{combined[:600]}",
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
                        _save()

                        st.session_state.diary_just_saved = True
                        st.session_state.diary_last_entry = entry
                        st.rerun()

                    if not has_content:
                        st.caption("Viết ít nhất một điều để Cừu có thể lưu giúp bạn 🌿")

                    if diary_entries:
                        dl = json.dumps(diary_entries, ensure_ascii=False, indent=2)
                        st.download_button(
                            "⬇️ Tải nhật ký về máy", dl,
                            "nhat_ky_tam_su.json", "application/json",
                        )

            # ─────────────────────────────────────────────────────
            # RIGHT: TIMELINE — PHẦN 5 & 7
            # ─────────────────────────────────────────────────────
            with col_history:
                if not diary_entries:
                    # Empty state: emotional hook
                    st.markdown(
                        '<div style="text-align:center;padding:40px 16px 20px;">'
                        '<div style="font-size:2.4rem;margin-bottom:8px;">🌱</div>'
                        '<div style="font-weight:800;color:#5A7A4A;font-size:1.05rem;margin-bottom:10px;">'
                        'Trang đầu tiên đang chờ bạn.</div>'
                        '<div style="color:#888;font-size:0.88rem;line-height:1.7;font-style:italic;">'
                        '"Mọi giấc mơ lớn đều bắt đầu<br/>từ một dòng nhật ký nhỏ."'
                        '</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<div style="font-weight:800;color:#4E7DB8;font-size:1.05rem;margin-bottom:6px;">'
                        '📖 Hành trình trưởng thành</div>',
                        unsafe_allow_html=True,
                    )
                    now = datetime.now()
                    filter_opt = st.radio(
                        "Xem:",
                        ["Hôm nay", "Tuần này", "Tháng này", "Tất cả"],
                        horizontal=True,
                        label_visibility="collapsed",
                        key="d_filter",
                    )
                    filtered = diary_entries
                    if filter_opt == "Hôm nay":
                        filtered = [e for e in diary_entries
                                    if e["date_raw"][:10] == now.strftime("%Y-%m-%d")]
                    elif filter_opt == "Tuần này":
                        ago = (now - timedelta(days=7)).isoformat()
                        filtered = [e for e in diary_entries if e["date_raw"] >= ago]
                    elif filter_opt == "Tháng này":
                        ms = now.strftime("%Y-%m")
                        filtered = [e for e in diary_entries if e["date_raw"][:7] == ms]

                    search = st.text_input(
                        "🔍", placeholder="Tìm kiếm...", key="d_search",
                        label_visibility="collapsed",
                    )
                    if search:
                        sl = search.lower()
                        filtered = [e for e in filtered
                                    if sl in e["content"].lower() or sl in e["title"].lower()]

                    st.caption(f"{len(filtered)} trang nhật ký")

                    for entry in filtered:
                        preview = entry["content"][:110] + ("..." if len(entry["content"]) > 110 else "")
                        dream_line = (
                            f'<div style="color:#5A7A4A;font-size:0.82rem;margin-top:4px;">✨ {entry["dream"]}</div>'
                            if entry.get("dream") else ""
                        )
                        tags_line = " ".join(
                            LIFE_EVENT_LABELS.get(t, t)
                            for t in entry.get("tags", [])[:2]
                        )
                        reply_preview = ""
                        if entry.get("reply"):
                            rp = entry["reply"]
                            reply_preview = (
                                f'<div style="color:#C4607F;font-size:0.82rem;'
                                f'margin-top:6px;font-style:italic;">'
                                f'🐑 {rp[:55]}{"..." if len(rp)>55 else ""}</div>'
                            )

                        tags_div = (
                            f'<div style="font-size:0.76rem;color:#aaa;margin-top:3px;">{tags_line}</div>'
                            if tags_line else ""
                        )
                        st.markdown(
                            f'<div class="diary-entry-card">'
                            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                            f'<span style="font-weight:700;color:#444;font-size:0.88rem;">{entry["mood"]}</span>'
                            f'<span style="font-size:0.76rem;color:#bbb;">{entry["date"][:8]}</span>'
                            f'</div>'
                            f'<div style="font-size:0.85rem;color:#666;margin:6px 0 2px;line-height:1.55;">'
                            f'{preview}</div>'
                            f'{dream_line}'
                            f'{tags_div}'
                            f'{reply_preview}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        if st.button("🗑️", key=f"del_{entry['id']}", help="Xoá trang này"):
                            mem["diary_entries"] = [e for e in diary_entries if e["id"] != entry["id"]]
                            _save()
                            st.rerun()


        # ═══════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════
# TAB 2 — CỪU CỦA TÔI  (Feeding + condensed Profile)
# Vision: Giấc mơ và tiết kiệm qua ngôn ngữ Cừu
# ═══════════════════════════════════════════════════════
# ══ TAB 2: 🐑 CỪU CỦA TÔI — Behavioral Finance Platform ════════════════════
with tab2:
    import random as _rand2

    # ── 0. Init ──────────────────────────────────────────────────────────────
    _today_str    = datetime.now().strftime("%Y-%m-%d")
    _today_q, _today_key = _get_today_q(mem)
    if not _today_q.get("visit"):
        _complete_quest(mem, "visit", 10)
        _save()

    _days_away, _ret_emoji, _ret_title, _ret_body = _return_msg(mem, _today_str)
    if _days_away >= 1:
        mem["last_visit_date"] = _today_str
        _save()

    total_saved      = mem.get("total_saved", 0)
    stage_key, stage_name, lv_num, stage_desc, stage_msg = get_growth_stage(total_saved)
    _exp             = mem.get("user_exp", 0)
    _lv              = get_exp_level(_exp)
    _in_lv, _needed, _pct = exp_progress(_exp)
    _tickets         = mem.get("ilucky_tickets", 0)
    _hunger_pct, _hunger_state, _hunger_msg = _get_hunger(mem)
    _today_q_data    = mem.get("daily_quests", {}).get(_today_str, {})
    _q_done_count    = sum(1 for k in ("visit","chat","diary","feed") if _today_q_data.get(k))
    _all_q_done      = _q_done_count == 4
    _bonus_claimed   = _today_q_data.get("bonus_claimed", False)
    _user_name       = mem.get("name", "bạn")
    _next_lv         = min(_lv + 1, 6)
    _next_lv_tickets = LEVEL_ILUCKY.get(_next_lv, 0)
    _next_lv_items   = LEVEL_ITEMS.get(_next_lv, [])
    _earned_ach      = set(mem.get("achievements", []))

    # ── GLOBAL CSS ────────────────────────────────────────────────────────────
    st.markdown("""<style>
    .sec-header{font-size:.78rem;font-weight:800;color:#7B5EA7;text-transform:uppercase;
                letter-spacing:.08em;margin:22px 0 10px;display:flex;align-items:center;gap:8px;}
    .sec-header::before{content:'';display:block;width:3px;height:16px;
                        background:linear-gradient(180deg,#7B5EA7,#C4607F);border-radius:3px;}
    .card-base{background:#fff;border:1.5px solid #f0e8ff;border-radius:20px;
               padding:16px 18px;margin-bottom:12px;}
    .exp-bar-wrap{background:#f0f0f7;border-radius:12px;height:14px;overflow:hidden;margin:6px 0;}
    .exp-bar-fill{height:100%;border-radius:12px;
                  background:linear-gradient(90deg,#7B5EA7,#C4607F,#FFD700);}
    .hunger-wrap{background:#f0f0f7;border-radius:8px;height:9px;overflow:hidden;margin:4px 0;}
    .hunger-fill{height:100%;border-radius:8px;}
    .quest-row{display:flex;align-items:center;gap:12px;padding:11px 14px;
               border-radius:14px;margin-bottom:7px;border:1.5px solid;}
    .quest-done{background:#f0fff4;border-color:#b8f0c8;}
    .quest-todo{background:#fafafa;border-color:#ede8ff;}
    .lv-pill{display:inline-flex;align-items:center;gap:6px;
             background:linear-gradient(135deg,#7B5EA7,#C4607F);
             color:#fff;border-radius:24px;padding:6px 18px;
             font-size:.82rem;font-weight:800;}
    .ticket-pill{display:inline-flex;align-items:center;gap:6px;
                 background:linear-gradient(135deg,#FFD700,#FFA500);
                 color:#1a1a2e;border-radius:24px;padding:6px 18px;
                 font-size:.82rem;font-weight:800;}
    .item-chip{display:inline-flex;align-items:center;gap:5px;border-radius:20px;
               padding:5px 12px;font-size:.72rem;font-weight:700;margin:3px;}
    .item-unlocked{background:#f4eeff;border:1.5px solid #d4b8ff;color:#5a3d9a;}
    .item-locked{background:#f5f5f5;border:1.5px dashed #ddd;color:#aaa;}
    .ach-card{border-radius:16px;padding:13px 10px;text-align:center;margin-bottom:8px;
              border:1.5px solid;}
    .ach-got{background:#f4eeff;border-color:#d4b8ff;}
    .ach-miss{background:#f8f8f8;border-color:#e8e8e8;opacity:.5;}
    .feed-translate{font-size:.68rem;color:#7B5EA7;font-style:italic;margin-top:2px;text-align:center;}
    .timeline-dot{width:10px;height:10px;border-radius:50%;background:#C4607F;
                  flex-shrink:0;margin-top:4px;}
    .research-card{background:linear-gradient(135deg,#fff8f0,#fff0f8);
                   border:1.5px solid #ffd6c8;border-radius:16px;padding:13px 15px;margin-bottom:8px;}
    </style>""", unsafe_allow_html=True)

    # ── 1. RETURNING USER BANNER ──────────────────────────────────────────────
    if _days_away >= 1 and _ret_title:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1A1A2E,#2D1B69);'
            f'border-radius:20px;padding:18px 20px;margin-bottom:14px;text-align:center;">'
            f'<div style="font-size:2rem;margin-bottom:6px;">{_ret_emoji}</div>'
            f'<div style="font-size:1.05rem;font-weight:800;color:#fff;margin-bottom:4px;">{_ret_title}</div>'
            f'<div style="font-size:.84rem;color:rgba(255,255,255,.78);line-height:1.6;">{_ret_body}</div>'
            f'</div>', unsafe_allow_html=True)

    # ── 2. LEVEL-UP POPUP ─────────────────────────────────────────────────────
    if mem.get("just_leveled_up"):
        _nl_name    = mem.get("new_level_name", LEVEL_NAMES.get(_lv, ""))
        _nl_tickets = mem.get("new_level_tickets", 0)
        st.balloons()
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFD700,#FFA500,#FF6B35);'
            f'border-radius:22px;padding:22px 20px;text-align:center;margin-bottom:14px;">'
            f'<div style="font-size:2.4rem;">🎉</div>'
            f'<div style="font-size:1.3rem;font-weight:800;color:#1a1a2e;margin:6px 0 3px;">LEVEL UP!</div>'
            f'<div style="font-size:.92rem;color:#1a1a2e;margin-bottom:10px;">{_nl_name}</div>'
            f'<div style="background:rgba(0,0,0,.14);border-radius:14px;'
            f'padding:10px 16px;display:inline-block;">'
            f'<span style="font-size:.9rem;font-weight:800;color:#1a1a2e;">'
            f'🎟️ Nhận được {_nl_tickets} Vé Quay iLucky!</span>'
            f'</div></div>', unsafe_allow_html=True)
        mem["just_leveled_up"]   = False
        mem["new_level_name"]    = ""
        mem["new_level_tickets"] = 0
        _save()

    # ── 3. MARKET DOWN EXPERIENCE ─────────────────────────────────────────────
    if mem.get("market_mood", "normal") == "down":
        st.markdown(
            '<div style="background:linear-gradient(135deg,#e8f0ff,#f0f8ff);'
            'border-radius:18px;padding:14px 18px;margin-bottom:12px;'
            'border-left:4px solid #7B9ED9;">'
            '<div style="font-size:.88rem;font-weight:700;color:#3a5f9a;margin-bottom:4px;">'
            '🌧️ Hôm nay đồng cỏ hơi có mưa.</div>'
            '<div style="font-size:.82rem;color:#5a7aaa;line-height:1.6;">'
            '🐑 Nhưng mình vẫn đang lớn lên cùng bạn. '
            'Có những ngày cỏ không xanh — nhưng hành trình vẫn tiếp tục.</div>'
            '</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1: 🐑 CỪU CỦA TÔI
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">🐑 Cừu của tôi</div>', unsafe_allow_html=True)

    _s1_left, _s1_right = st.columns([1, 1.4])
    with _s1_left:
        show_growth_sheep(total_saved, width=200)

        # Hunger meter
        _h_color = {"ok":"#7B5EA7","hungry":"#FFA500","miss_you":"#FF6B35","lonely":"#E53935"}.get(_hunger_state,"#7B5EA7")
        _h_label = {"ok":"🌿 No bụng","hungry":"🥺 Hơi đói","miss_you":"😢 Đói lắm","lonely":"💔 Nhớ bạn ghê"}.get(_hunger_state,"🌿 No bụng")
        st.markdown(
            f'<div style="margin:10px 0 4px;">'
            f'<div style="display:flex;justify-content:space-between;font-size:.7rem;color:#888;margin-bottom:3px;">'
            f'<span>🍽️ Độ no</span><span style="color:{_h_color};font-weight:700;">{_h_label}</span></div>'
            f'<div class="hunger-wrap"><div class="hunger-fill" style="width:{_hunger_pct}%;background:{_h_color};"></div></div>'
            f'<div style="font-size:.68rem;color:{_h_color};margin-top:2px;">{_hunger_msg}</div>'
            f'</div>',
            unsafe_allow_html=True)

        # Mood bar
        _mood_now = mem.get("mood", "happy")
        _mood_map = {"happy":("❤️","100","#FF6B9D"),"sad":("💙","40","#7B9ED9"),
                     "celebrate":("🌟","100","#FFD700"),"listening":("💜","75","#9B5EA7")}
        _m_ico, _m_pct, _m_col = _mood_map.get(_mood_now, ("❤️","80","#FF6B9D"))
        st.markdown(
            f'<div style="margin:4px 0;">'
            f'<div style="display:flex;justify-content:space-between;font-size:.7rem;color:#888;margin-bottom:3px;">'
            f'<span>{_m_ico} Tâm trạng</span></div>'
            f'<div class="hunger-wrap"><div class="hunger-fill" style="width:{_m_pct}%;background:{_m_col};"></div></div>'
            f'</div>', unsafe_allow_html=True)

    with _s1_right:
        # Hero voice
        _hero_lines = {
            "baby":   f'"Mình vừa ra đời... cho mình ăn bữa đầu tiên nhé? 🥺"',
            "child":  f'"Lớn hơn rồi nhờ {_user_name} đấy! Hôm nay cho mình ăn tiếp không?"',
            "teen":   f'"Mình đang lớn nhanh lắm~ Cùng nhau đến đích thôi {_user_name} ơi!"',
            "adult":  f'"Chúng mình đã đi được nửa đường. Mình tự hào về {_user_name} lắm ❤️"',
            "master": f'"Cảm ơn {_user_name} đã không bỏ cuộc. Mình sẽ ở bên mãi mãi 🏆"',
        }
        _hstage_food = {"baby":"🥬","child":"🥕","teen":"🍎","adult":"🎂","master":"🎉"}
        _htxt = _hero_lines.get(stage_key, _hero_lines["baby"])
        _hfood = _hstage_food.get(stage_key, "🌿")
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
            f'border-radius:16px;padding:14px 16px;margin-bottom:10px;">'
            f'<div style="font-size:2rem;text-align:center;">{_hfood}</div>'
            f'<div style="font-size:.88rem;color:#C4607F;font-style:italic;'
            f'margin-top:7px;line-height:1.6;text-align:center;">{_htxt}</div>'
            f'</div>', unsafe_allow_html=True)

        # Celebration feedback
        if st.session_state.get("feeding_celebration"):
            _fed_food = mem.get("last_fed_food", "")
            _translate_msg = {
                "🥬 Bó Cỏ":          "🐑 Cừu vừa được ăn một bó cỏ!",
                "🥕 Cà Rốt":         "🐑 Cừu vừa ăn cà rốt — ngon lắm!",
                "🍎 Táo":            "🐑 Cừu vừa ăn táo — bê bê thích quá!",
                "🎂 Tiệc Sinh Nhật": "🐑 Tiệc sinh nhật cho Cừu! 🎂",
                "🎉 Đại Tiệc":       "🐑 Đại tiệc! Cừu hạnh phúc nhất đàn! 🎉",
            }.get(_fed_food, "🐑 Cừu vừa được cho ăn!")
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#FFF5FA,#FFF8E8);'
                f'border-radius:14px;padding:12px 14px;text-align:center;margin-bottom:8px;">'
                f'<div style="font-size:1.6rem;">🎉</div>'
                f'<div style="font-size:.88rem;font-weight:700;color:#C4607F;margin-top:4px;">{_translate_msg}</div>'
                f'<div style="font-size:.72rem;color:#7B5EA7;margin-top:3px;">+30 EXP đã được cộng!</div>'
                f'</div>', unsafe_allow_html=True)
            st.session_state.feeding_celebration = False
            st.balloons()

        if st.session_state.get("feeding_refused"):
            st.markdown(
                '<div style="background:#F0F8FF;border-radius:14px;padding:12px 14px;'
                'text-align:center;margin-bottom:8px;">'
                '<div style="font-size:.88rem;font-weight:700;color:#5B8DB8;">Không sao cả 🌙</div>'
                '<div style="font-size:.82rem;color:#6A9BBF;margin-top:4px;">'
                'Mình vẫn ở đây, hôm nào sẵn sàng thì mình vẫn đợi~ 🐑</div>'
                '</div>', unsafe_allow_html=True)
            st.session_state.feeding_refused = False

        # Feed buttons
        st.markdown(
            '<div style="font-size:.85rem;font-weight:700;color:#C4607F;margin:6px 0 6px;">'
            '🍽️ Hôm nay cho Cừu ăn gì?</div>', unsafe_allow_html=True)
        _FOOD_TRANS = {
            "🥬 Bó Cỏ":"Đầu tư 10.000đ", "🥕 Cà Rốt":"Đầu tư 20.000đ",
            "🍎 Táo":"Đầu tư 50.000đ","🎂 Tiệc Sinh Nhật":"Đầu tư 100.000đ",
            "🎉 Đại Tiệc":"Đầu tư 500.000đ",
        }
        _fcols = st.columns(len(FEED_OPTIONS))
        for _fi, (_famt, _femo, _fnm) in enumerate(FEED_OPTIONS):
            _flbl = f"{_femo} {_fnm}"
            if _fcols[_fi].button(f"{_femo}\n{_fnm}", use_container_width=True, key=f"feed2_{_famt}", type="primary"):
                _prev_key = stage_key
                mem["total_saved"]    += _famt
                mem["streak"]         += 1
                mem["last_fed_amount"] = _famt
                mem["last_fed_food"]   = _flbl
                mem["last_fed_date"]   = _today_str
                _new_key, *_ = get_growth_stage(mem["total_saved"])
                if _new_key != _prev_key:
                    mem["just_leveled_up"] = True
                _complete_quest(mem, "feed", 30)
                _add_exp(30, mem)
                _check_achievements(mem)
                set_mood("happy")
                st.session_state.feeding_celebration = True
                st.session_state.feeding_refused = False
                _save()
                st.rerun()
            _fcols[_fi].markdown(
                f'<div class="feed-translate">{_FOOD_TRANS.get(_flbl,"")}</div>',
                unsafe_allow_html=True)

        with st.expander("🔢 Nhập số tiền khác"):
            _custom = st.number_input("Số tiền:", min_value=1_000, max_value=100_000_000,
                                       step=10_000, value=30_000, key="custom_amt2")
            if st.button(f"🐑 Cho Cừu ăn {fmt(int(_custom))}", type="primary",
                         use_container_width=True, key="custom_feed2"):
                mem["total_saved"]    += int(_custom)
                mem["streak"]         += 1
                mem["last_fed_amount"] = int(_custom)
                mem["last_fed_food"]   = fmt(int(_custom))
                mem["last_fed_date"]   = _today_str
                _new_key2, *_ = get_growth_stage(mem["total_saved"])
                if _new_key2 != stage_key:
                    mem["just_leveled_up"] = True
                _complete_quest(mem, "feed", 30)
                _add_exp(30, mem)
                _check_achievements(mem)
                set_mood("happy")
                st.session_state.feeding_celebration = True
                _save()
                st.rerun()

        if st.button("🌙 Hôm nay chưa sẵn sàng", use_container_width=True, key="skip_feed2"):
            set_mood("sad")
            st.session_state.feeding_refused = True
            st.session_state.feeding_celebration = False
            _save()
            st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2: 🎯 NHIỆM VỤ HÔM NAY
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">🎯 Nhiệm vụ hôm nay</div>', unsafe_allow_html=True)

    _QUESTS2 = [
        ("visit", "👁️ Ghé thăm Cừu",       10, "Đã ghé thăm ✓"),
        ("chat",  "💬 Trò chuyện với Cừu",  10, "Đã trò chuyện ✓"),
        ("diary", "📔 Viết nhật ký",         20, "Đã viết nhật ký ✓"),
        ("feed",  "🍽️ Cho Cừu ăn",          30, "Đã cho ăn ✓"),
    ]
    _q_html2 = ""
    for _qk2, _ql2, _qe2, _qd2 in _QUESTS2:
        _done2 = _today_q_data.get(_qk2, False)
        _cls2  = "quest-done" if _done2 else "quest-todo"
        _ico2  = "✅" if _done2 else "⬜"
        _lbl2  = _qd2 if _done2 else _ql2
        _exp2  = "" if _done2 else f'<span style="margin-left:auto;font-size:.65rem;font-weight:800;color:#7B5EA7;background:#f0eaff;border-radius:10px;padding:2px 8px;">+{_qe2} EXP</span>'
        _q_html2 += (f'<div class="quest-row {_cls2}">'
                     f'<span style="font-size:1.1rem;">{_ico2}</span>'
                     f'<span style="font-size:.84rem;font-weight:{"700" if _done2 else "500"};'
                     f'color:{"#2a9d5c" if _done2 else "#333"};">{_lbl2}</span>'
                     f'{_exp2}</div>')

    # Progress bar
    _q_prog_pct = int(_q_done_count / 4 * 100)
    _q_prog_color = "#2a9d5c" if _all_q_done else "#7B5EA7"
    st.markdown(
        f'<div class="card-base">'
        f'{_q_html2}'
        f'<div style="margin-top:12px;">'
        f'<div style="display:flex;justify-content:space-between;font-size:.7rem;color:#888;margin-bottom:4px;">'
        f'<span>Tiến độ hôm nay</span><span style="font-weight:700;color:{_q_prog_color};">'
        f'{_q_done_count}/4 nhiệm vụ · {_q_prog_pct}%</span></div>'
        f'<div style="background:#f0f0f7;border-radius:8px;height:8px;overflow:hidden;">'
        f'<div style="width:{_q_prog_pct}%;height:100%;border-radius:8px;background:{_q_prog_color};'
        f'transition:width .4s ease;"></div></div>'
        f'</div></div>',
        unsafe_allow_html=True)

    if _all_q_done and not _bonus_claimed:
        if st.button("🎁 Nhận thưởng hoàn thành tất cả! (+50 EXP)", type="primary",
                     use_container_width=True, key="claim_bonus2"):
            _complete_quest(mem, "bonus_claimed", 50)
            mem["daily_quests"][_today_str]["bonus_claimed"] = True
            _save()
            st.rerun()
    elif _all_q_done and _bonus_claimed:
        st.markdown(
            '<div style="text-align:center;background:#f0fff4;border-radius:14px;'
            'padding:12px;border:1.5px solid #b8f0c8;margin-top:-8px;">'
            '<span style="font-size:1.1rem;">🎉</span> '
            '<strong style="font-size:.85rem;color:#2a9d5c;">Hoàn thành xuất sắc hôm nay! +50 EXP đã nhận</strong>'
            '</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3: ⭐ LEVEL + EXP
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">⭐ Level & EXP</div>', unsafe_allow_html=True)

    _lv_name_disp = LEVEL_NAMES.get(_lv, f"Level {_lv}")
    _nxt_items_txt = " · ".join(_next_lv_items[:2]) if _next_lv_items else "Đã đạt cấp cao nhất"
    st.markdown(
        f'<div class="card-base" style="padding:20px 22px;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">'
        f'<span class="lv-pill">Lv.{_lv} · {_lv_name_disp}</span>'
        f'<span style="font-size:.75rem;color:#888;font-weight:600;">{_in_lv:,} / {_needed:,} EXP</span>'
        f'</div>'
        f'<div class="exp-bar-wrap"><div class="exp-bar-fill" style="width:{_pct:.1f}%;"></div></div>'
        f'<div style="display:flex;justify-content:space-between;margin-top:8px;">'
        f'<span style="font-size:.7rem;color:#aaa;">Còn {max(0,_needed-_in_lv):,} EXP → Lv.{_next_lv}</span>'
        f'<span style="font-size:.7rem;color:#C4607F;font-weight:700;">{_pct:.0f}%</span>'
        f'</div>'
        f'<div style="margin-top:12px;background:#faf6ff;border-radius:12px;padding:9px 12px;">'
        f'<div style="font-size:.7rem;color:#9b7ed9;font-weight:700;">🎁 Thăng lên Lv.{_next_lv} sẽ nhận:</div>'
        f'<div style="font-size:.78rem;color:#5a3d9a;margin-top:4px;font-weight:600;">'
        f'🎟️ {_next_lv_tickets} Vé iLucky · {_nxt_items_txt}</div>'
        f'</div></div>',
        unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4: 🎟️ ILUCKY REWARD CENTER
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">🎟️ Vé iLucky</div>', unsafe_allow_html=True)

    _il_left, _il_right = st.columns([1.2, 1])
    with _il_left:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1A1A2E,#2D1B69);'
            f'border-radius:20px;padding:18px 20px;">'
            f'<div style="font-size:.72rem;color:#c4a8ff;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Hiện có</div>'
            f'<div style="display:flex;align-items:baseline;gap:8px;">'
            f'<span style="font-size:2.8rem;font-weight:800;color:#FFD700;">{_tickets}</span>'
            f'<span style="font-size:1rem;color:rgba(255,255,255,.7);">vé</span>'
            f'</div>'
            f'<span class="ticket-pill" style="margin-top:12px;display:inline-flex;">🎟️ iLucky Tickets</span>'
            f'</div>',
            unsafe_allow_html=True)
    with _il_right:
        # Items unlocked so far
        _all_items_unlocked = []
        for _li in range(2, _lv + 1):
            _all_items_unlocked += LEVEL_ITEMS.get(_li, [])
        st.markdown(
            f'<div style="background:#fff8f0;border:1.5px solid #FFD6C8;border-radius:20px;padding:14px 16px;height:100%;">'
            f'<div style="font-size:.72rem;color:#C4607F;font-weight:700;margin-bottom:8px;">🎁 Đã mở khóa</div>',
            unsafe_allow_html=True)
        if _all_items_unlocked:
            for _it in _all_items_unlocked:
                st.markdown(f'<span class="item-chip item-unlocked">{_it}</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="font-size:.78rem;color:#aaa;">Lên Lv.2 để mở khóa</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:.72rem;color:#888;margin-top:8px;border-top:1px solid #ffe8d8;padding-top:8px;">'
            f'🔒 Tiếp theo: {" · ".join(_next_lv_items) if _next_lv_items else "Đã đủ tất cả"}'
            f'</div></div>',
            unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 5: 🏆 THÀNH TÍCH
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">🏆 Thành tích</div>', unsafe_allow_html=True)

    _ach_cols2 = st.columns(4)
    for _ai2, (_akey2, _aname2, _adesc2) in enumerate(ACHIEVEMENTS_DEF):
        _got2  = _akey2 in _earned_ach
        _cls2a = "ach-got" if _got2 else "ach-miss"
        _aparts2 = _aname2.split()
        _abadge2 = '<div style="font-size:.6rem;color:#2a9d5c;margin-top:5px;font-weight:700;">✅ Đạt được</div>' if _got2 else ''
        with _ach_cols2[_ai2 % 4]:
            st.markdown(
                f'<div class="ach-card {_cls2a}">'
                f'<div style="font-size:1.5rem;">{_aparts2[0]}</div>'
                f'<div style="font-size:.72rem;font-weight:700;color:{"#5a3d9a" if _got2 else "#aaa"};margin-top:4px;">'
                f'{" ".join(_aparts2[1:])}</div>'
                f'<div style="font-size:.62rem;color:{"#888" if _got2 else "#ccc"};margin-top:3px;">{_adesc2}</div>'
                f'{_abadge2}</div>',
                unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 6: 🐑 SHEEP SHOP — Wardrobe by Level
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">🐑 Tủ Đồ Cừu</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:.78rem;color:#aaa;margin-top:-8px;margin-bottom:10px;">'
        'Cừu thay đổi theo cấp độ của bạn. Đầu tư đều → Cừu ngày càng chất!</div>',
        unsafe_allow_html=True)

    _SHOP_ITEMS = [
        (1, "🐑", "Cừu Sơ Sinh",     "Mặc định"),
        (2, "🎩", "Mũ Sinh Viên",    "Lv.2 · Cừu Non"),
        (3, "👔", "Vest Xanh TCBS",  "Lv.3 · Cừu Thiếu Niên"),
        (3, "🎒", "Balo",            "Lv.3"),
        (4, "⌚", "Đồng Hồ",        "Lv.4 · Cừu Trưởng Thành"),
        (4, "🏠", "Nhà Gỗ",         "Lv.4"),
        (5, "🚗", "Xe Mini",        "Lv.5 · Cừu Lão Luyện"),
        (5, "🏡", "Nhà Cao Cấp",    "Lv.5"),
        (6, "👑", "Vương Miện",     "Lv.6 · Huyền Thoại"),
        (6, "🏰", "Lâu Đài Cừu",    "Lv.6"),
    ]
    _shop_cols = st.columns(5)
    for _si, (_slv, _sico, _snm, _ssub) in enumerate(_SHOP_ITEMS):
        _sunlocked = _lv >= _slv
        _s_border  = "2px solid #d4b8ff" if _sunlocked else "2px dashed #e0e0e0"
        _s_bg      = "#f4eeff" if _sunlocked else "#f8f8f8"
        _s_opacity = "1"       if _sunlocked else ".45"
        _s_namecolor = "#5a3d9a" if _sunlocked else "#aaa"
        _s_subcolor  = "#9b7ed9" if _sunlocked else "#ccc"
        _s_badge = '<div style="font-size:.58rem;color:#2a9d5c;font-weight:700;margin-top:3px;">✅ Đã có</div>' if _sunlocked else ''
        with _shop_cols[_si % 5]:
            st.markdown(
                f'<div style="border:{_s_border};border-radius:16px;padding:10px 6px;'
                f'text-align:center;background:{_s_bg};opacity:{_s_opacity};">'
                f'<div style="font-size:1.6rem;">{_sico}</div>'
                f'<div style="font-size:.68rem;font-weight:700;color:{_s_namecolor};margin-top:4px;">{_snm}</div>'
                f'<div style="font-size:.58rem;color:{_s_subcolor};margin-top:2px;">{_ssub}</div>'
                f'{_s_badge}</div>',
                unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 7: 👨‍👩‍👧 FAMILY MODE + 🧠 AI MEMORY TIMELINE
    # ════════════════════════════════════════════════════════════════════════
    _fam_col, _mem_col = st.columns(2)

    with _fam_col:
        st.markdown('<div class="sec-header" style="margin-top:14px;">👨‍👩‍👧 Family Mode</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-base" style="padding:16px 16px;">'
            '<div style="text-align:center;font-size:.8rem;color:#555;margin-bottom:12px;line-height:1.6;">'
            '🐑 Gia đình bạn có thể cùng nuôi Cừu!<br/>'
            '<span style="font-size:.72rem;color:#aaa;">Bố mẹ, con cái — mỗi người một cừu riêng</span>'
            '</div>'
            '<div style="display:flex;justify-content:center;gap:12px;">'
            '<div style="text-align:center;">'
            '<div style="font-size:2rem;">👨</div>'
            '<div style="font-size:.68rem;font-weight:700;color:#5a3d9a;margin-top:3px;">Cừu Bố</div>'
            '<div style="font-size:.6rem;color:#aaa;">Đang nuôi</div>'
            '</div>'
            '<div style="text-align:center;">'
            '<div style="font-size:2rem;">👩</div>'
            '<div style="font-size:.68rem;font-weight:700;color:#5a3d9a;margin-top:3px;">Cừu Mẹ</div>'
            '<div style="font-size:.6rem;color:#aaa;">Đang nuôi</div>'
            '</div>'
            '<div style="text-align:center;">'
            '<div style="font-size:2rem;">👶</div>'
            '<div style="font-size:.68rem;font-weight:700;color:#C4607F;margin-top:3px;">Cừu Con</div>'
            '<div style="font-size:.6rem;color:#2a9d5c;font-weight:600;">+10k → Cừu lớn</div>'
            '</div>'
            '</div>'
            '<div style="margin-top:12px;background:#f8f6ff;border-radius:12px;'
            'padding:9px 12px;font-size:.73rem;color:#7B5EA7;text-align:center;">'
            '💌 Mời gia đình tham gia → Cả nhà cùng lớn!'
            '</div></div>',
            unsafe_allow_html=True)
        if st.button("💌 Mời gia đình", use_container_width=True, key="invite_fam2"):
            st.info("🔗 Sao chép link mời: tcbs.vn/invite/sheep-family (sắp ra mắt!)")

    with _mem_col:
        st.markdown('<div class="sec-header" style="margin-top:14px;">🧠 AI Nhớ Hành Trình</div>', unsafe_allow_html=True)
        _mem_events  = mem.get("life_events", [])
        _mem_dreams  = mem.get("dreams", [])
        _mem_notes   = mem.get("notes", [])
        _mem_start   = mem.get("created_at", "")[:7] or "2025-01"

        _timeline_items = []
        if _mem_start:
            _timeline_items.append(("🌱", f"Tháng {_mem_start[5:7]}/{_mem_start[2:4]}", "Bắt đầu hành trình"))
        for _ev in _mem_events[:2]:
            _ev_lbl = LIFE_EVENT_LABELS.get(_ev, _ev)
            _timeline_items.append(("📌", "Gần đây", _ev_lbl))
        for _dr in _mem_dreams[:2]:
            _timeline_items.append(("✨", "Đang mơ", _dr.get("name","").title()[:20]))
        if mem.get("streak", 0) >= 7:
            _timeline_items.append(("🔥", "Streak", f'{mem["streak"]} ngày liên tiếp'))
        if not _timeline_items:
            _timeline_items = [
                ("🌱", "Hôm nay", "Bắt đầu hành trình"),
                ("💭", "Sắp tới", "Kể ước mơ cho Cừu nghe..."),
            ]

        _tl_html = '<div class="card-base" style="padding:14px 16px;">'
        _tl_html += '<div style="font-size:.76rem;font-weight:700;color:#C4607F;margin-bottom:10px;">🐑 Điều mình nhớ về bạn</div>'
        for _tl_ico, _tl_date, _tl_txt in _timeline_items[:5]:
            _tl_html += (
                f'<div style="display:flex;gap:10px;margin-bottom:9px;align-items:flex-start;">'
                f'<div class="timeline-dot" style="margin-top:6px;"></div>'
                f'<div><div style="font-size:.66rem;color:#aaa;font-weight:600;">{_tl_date}</div>'
                f'<div style="font-size:.78rem;color:#333;font-weight:600;">{_tl_ico} {_tl_txt}</div>'
                f'</div></div>')
        _tl_html += '</div>'
        st.markdown(_tl_html, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 8: 🔍 DEEP RESEARCH — AI Trend Insights
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">🔍 AI Đang Theo Dõi Cho Bạn</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:.76rem;color:#aaa;margin-top:-8px;margin-bottom:10px;">'
        'Cừu theo dõi TikTok, Reddit, Google Trends — để tạo động lực cho bạn đúng lúc</div>',
        unsafe_allow_html=True)

    _first_dream = mem["dreams"][0].get("name","").lower() if mem.get("dreams") else ""
    _TREND_MAP = {
        "nhật": ("🗾", "Nhiều bạn đang săn vé Nhật mùa lá đỏ tháng 11",
                 "Vé rẻ nhất ~5.8tr. Nếu bạn bắt đầu từ tuần trước, hôm nay đã có 200k rồi!"),
        "xe":   ("🚗", "Xe điện VinFast đang trending mạnh trên TikTok",
                 "Nhiều bạn 9x đang chuyển từ xe máy sang xe điện — trend mới 2025"),
        "nhà":  ("🏠", "Giá chung cư tại TP.HCM đang được tìm kiếm nhiều nhất",
                 "Reddit r/VietNam: 'Mua hay thuê?' là câu hỏi hot nhất tháng này"),
        "đám":  ("💒", "Xu hướng đám cưới mini 2025 đang tăng trên TikTok",
                 "Chi phí đám cưới trung bình giảm 40% so với 2023"),
        "du":   ("✈️", "Google Trends: Tìm kiếm 'vé máy bay' tăng 2.3x so với tháng trước",
                 "Mùa hè tới — nhiều bạn đang lên kế hoạch cho chuyến đi đầu tiên"),
    }
    _matched_trends = []
    for _tk, _tv in _TREND_MAP.items():
        if _tk in _first_dream:
            _matched_trends.append(_tv)
    if not _matched_trends:
        _matched_trends = [
            ("📈", "Thị trường chứng khoán VN đang phục hồi mạnh",
             "VN-Index tuần này tăng 1.4%. Thời điểm tốt để kiên trì tích lũy!"),
            ("💰", "Lạm phát tháng 6/2025 được kiểm soát tốt",
             "Sức mua tăng — mỗi đồng bạn tích lũy hôm nay có giá trị thực hơn."),
            ("🌱", "Đầu tư đều đặn (DCA) đang được nhiều bạn trẻ áp dụng",
             "Reddit: 'Tôi không cần timing thị trường, tôi chỉ cần nuôi Cừu đều'"),
        ]
    _tr_cols = st.columns(len(_matched_trends[:3]))
    for _tri, (_tr_ico, _tr_title, _tr_body) in enumerate(_matched_trends[:3]):
        with _tr_cols[_tri]:
            st.markdown(
                f'<div class="research-card">'
                f'<div style="font-size:1.4rem;margin-bottom:6px;">{_tr_ico}</div>'
                f'<div style="font-size:.76rem;font-weight:700;color:#C4607F;margin-bottom:5px;">{_tr_title}</div>'
                f'<div style="font-size:.71rem;color:#666;line-height:1.55;">{_tr_body}</div>'
                f'<div style="font-size:.62rem;color:#aaa;margin-top:7px;border-top:1px solid #ffe0d0;padding-top:5px;">'
                f'🐑 Cừu nhớ bạn đang mơ đến điều này~</div>'
                f'</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # DREAM CARDS
    # ════════════════════════════════════════════════════════════════════════
    if mem.get("dreams"):
        st.markdown('<div class="sec-header">🎯 Giấc Mơ Đang Được Nuôi</div>', unsafe_allow_html=True)
        for _d2 in mem["dreams"][:3]:
            with st.container(border=True):
                _da2, _db2 = st.columns([3, 2])
                with _da2:
                    st.markdown(f"**✨ {_d2['name'].title()}**")
                    if _d2["amount"] > 0:
                        _d_pct2 = min(100, _d2["saved"] / _d2["amount"] * 100)
                        st.progress(_d_pct2 / 100, text=f"{_d_pct2:.1f}% — còn {fmt(_d2['amount'] - _d2['saved'])}")
                with _db2:
                    if _d2["amount"] > 0 and _d2["saved"] < _d2["amount"]:
                        if st.button("❤️ +50k", key=f"dream2_{_d2['name']}", type="primary"):
                            _d2["saved"] = min(_d2["amount"], _d2["saved"] + 50_000)
                            mem["total_saved"] += 50_000
                            mem["last_fed_amount"] = 50_000
                            mem["last_fed_food"]   = f"❤️ cho {_d2['name'].title()}"
                            mem["last_fed_date"]   = _today_str
                            _complete_quest(mem, "feed", 30)
                            _add_exp(30, mem)
                            set_mood("celebrate" if _d2["saved"] >= _d2["amount"] else "happy")
                            st.session_state.feeding_celebration = True
                            _save()
                            st.rerun()
                    elif _d2.get("amount", 0) > 0:
                        st.success("🎉 Hoàn thành!")
    else:
        st.info("💭 Kể với Cừu về giấc mơ của bạn ở phần bên dưới nhé!")

    # ════════════════════════════════════════════════════════════════════════
    # FUND EXPLAINER (kept, in expander)
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    with st.expander("📚 Cừu Giải Thích Quỹ Đầu Tư", expanded=False):
        st.markdown(
            '<p style="font-size:.78rem;color:#AAA;margin-bottom:12px;">'
            'Kiến thức đơn giản · Không hứa lợi nhuận · Không khuyến nghị mua bán</p>',
            unsafe_allow_html=True)
        _FUND_ANALOGIES2 = {
            "TCEF": ("🌳 Trồng cây ăn quả",
                     "Cần kiên nhẫn 3–5 năm, nhưng khi cây ra trái thì ngọt lắm."),
            "TCBF": ("🪣 Bình nước dự phòng",
                     "Không sinh lời nhanh, nhưng ổn định và ít biến động."),
            "TCFF": ("🎒 Balo cân bằng",
                     "Vừa cổ phiếu vừa trái phiếu — không quá cay, không quá nhạt."),
        }
        _fc2a, _fc2b, _fc2c = st.columns(3)
        for _fcol2, _fkey2 in zip([_fc2a, _fc2b, _fc2c], ["TCEF", "TCBF", "TCFF"]):
            _f2 = FUNDS[_fkey2]
            _at2, _ad2 = _FUND_ANALOGIES2[_fkey2]
            with _fcol2:
                st.markdown(
                    f'<div style="background:white;border:2px solid #FFD6E8;border-radius:16px;'
                    f'padding:14px;min-height:160px;">'
                    f'<div style="font-size:1.5rem;text-align:center;">{_f2["emoji"]}</div>'
                    f'<div style="font-size:.8rem;font-weight:800;color:#C4607F;text-align:center;margin-top:5px;">{_at2}</div>'
                    f'<div style="font-size:.74rem;color:#555;margin-top:7px;line-height:1.5;">{_ad2}</div>'
                    f'<div style="font-size:.65rem;color:#CCC;margin-top:6px;">{_f2["tên"]} · {_f2["rủi_ro"]}</div>'
                    f'</div>', unsafe_allow_html=True)
        st.markdown("---")
        _rfy1, _rfy2 = st.columns(2)
        with _rfy1:
            _y_opt2 = st.selectbox("Mục tiêu bao lâu?", [1,2,3,5], format_func=lambda x: f"{x} năm", key="rec_y2")
        with _rfy2:
            _r_opt2 = st.selectbox("Khẩu vị rủi ro?", ["low","medium","high"],
                                   format_func=lambda x: {"low":"🌿 Thấp","medium":"🌊 Trung bình","high":"⚡ Cao"}[x], key="rec_r2")
        _rf_key2 = recommend_fund(_y_opt2, _r_opt2)
        _rf2     = FUNDS[_rf_key2]
        _rfa_t2, _rfa_d2 = _FUND_ANALOGIES2[_rf_key2]
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
            f'border-radius:16px;padding:14px 16px;margin-top:8px;">'
            f'<div style="font-size:.84rem;color:#C4607F;font-style:italic;margin-bottom:6px;">🐑 Cừu nói:</div>'
            f'<div style="font-size:.88rem;color:#444;line-height:1.7;">'
            f'Với mục tiêu <strong>{_y_opt2} năm</strong>, mình nghĩ '
            f'<strong>{_rf2["emoji"]} {_rfa_t2}</strong> hợp nhất.<br/>'
            f'<span style="font-size:.8rem;color:#777;">{_rfa_d2}</span><br/>'
            f'<span style="font-size:.68rem;color:#BBB;">⚠️ Chỉ là gợi ý tham khảo, không phải tư vấn đầu tư.</span>'
            f'</div></div>', unsafe_allow_html=True)
        with st.expander("📚 Kiến thức đầu tư cơ bản"):
            for _pk2, _pp2 in INVESTMENT_PRINCIPLES.items():
                st.markdown(f"**{_pp2['tên']}**")
                st.markdown(_pp2["nội_dung"])
                st.markdown("---")

    # Profile
    with st.expander("🧬 Cừu hiểu gì về bạn?", expanded=False):
        _has_data = any([mem["dreams"], mem["life_events"], mem["notes"], mem.get("total_saved",0) > 0])
        if not _has_data:
            st.info("🌿 Kể chuyện với Cừu ở phần Tâm sự bên dưới — Cừu sẽ nhớ dần về bạn!")
        else:
            _pc1, _pc2, _pc3 = st.columns(3)
            _sk_p, _sn_p, _, _sd_p, _ = get_growth_stage(mem.get("total_saved",0))
            for _cc, _ll, _vv, _ss in [
                (_pc1, "🐑 Cừu đang ở", _sn_p, _sd_p),
                (_pc2, "💰 Đã tích lũy", fmt(mem.get("total_saved",0)), f"🔥 {mem.get('streak',0)} ngày streak"),
                (_pc3, "✨ Đang mơ đến", (mem["dreams"][0]["name"].title()[:18] if mem.get("dreams") else "Chưa có"), "giấc mơ"),
            ]:
                _cc.markdown(
                    f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
                    f'border-radius:14px;padding:12px;text-align:center;border:1.5px solid #FFD6E8;">'
                    f'<div style="font-size:.74rem;color:#aaa;margin-bottom:2px;">{_ll}</div>'
                    f'<div style="font-size:.95rem;font-weight:800;color:#C4607F;">{_vv}</div>'
                    f'<div style="font-size:.7rem;color:#888;margin-top:2px;">{_ss}</div>'
                    f'</div>', unsafe_allow_html=True)
            _pk1, _pk2 = st.columns(2)
            with _pk1:
                _risk_ans2 = st.radio("🛡️ Nếu Cừu ăn 10tr mà còn 8tr:",
                    ["😰 Lo lắm, muốn lấy lại","🤔 Chờ xem thêm","😎 Mua thêm!"], key="profile_risk3")
                _risk_map3 = {
                    "😰 Lo lắm, muốn lấy lại":("low","🌿 Cừu thích ăn nhẹ","TCBF"),
                    "🤔 Chờ xem thêm":         ("medium","🌊 Cừu ăn cân bằng","TCFF"),
                    "😎 Mua thêm!":             ("high","⚡ Cừu thích mạo hiểm","TCEF"),
                }
                _r3_val, _r3_label, _r3_fund = _risk_map3[_risk_ans2]
                mem.setdefault("wealth_genome",{})["risk_type"] = _r3_label
                _save()
                st.caption(f"**{_r3_label}** · Quỹ: **{_r3_fund}**")
            with _pk2:
                mem.setdefault("wealth_genome",{})["personality"] = st.selectbox("💭 Cừu ăn vì lý do gì?", [
                    "Để bạn an tâm về tương lai","Cùng bạn thực hiện giấc mơ",
                    "Vì gia đình của bạn","Để bạn tự do tài chính","Đang thử nghiệm",
                ], key="profile_motive3")
                _save()
            if mem.get("life_events"):
                st.markdown("**🏷️ Cừu nhớ chuyện của bạn:**")
                _ev3c = st.columns(3)
                for _ei3, _et3 in enumerate(list(dict.fromkeys(mem["life_events"]))[:6]):
                    _ev3c[_ei3 % 3].caption(f"• {LIFE_EVENT_LABELS.get(_et3, _et3)}")
        st.caption("⚠️ Thông tin chỉ mang tính tham khảo, không phải tư vấn đầu tư chuyên nghiệp.")

    # ════════════════════════════════════════════════════════════════════════
    # SECTION LAST: 💬 TÂM SỰ VỚI CỪU
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(
        '<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
        'border-radius:20px;padding:16px 18px;margin-bottom:12px;">'
        '<div style="font-size:.9rem;font-weight:800;color:#C4607F;margin-bottom:4px;">💬 Tâm sự với Cừu</div>'
        '<div style="font-size:.78rem;color:#888;">Kể với Cừu về ngày hôm nay, ước mơ, hay bất cứ điều gì...</div>'
        '</div>', unsafe_allow_html=True)

    # Show recent chat context
    _recent_msgs = [m for m in st.session_state.get("messages",[]) if m.get("role")!="system"][-4:]
    if _recent_msgs:
        for _rm in _recent_msgs:
            _rm_is_user = _rm.get("role") == "user"
            _rm_bg = "#f0e8ff" if _rm_is_user else "#fff5fa"
            _rm_color = "#5a3d9a" if _rm_is_user else "#C4607F"
            _rm_prefix = f"🧑 {_user_name}" if _rm_is_user else "🐑 Cừu"
            _rm_content = str(_rm.get("content",""))[:300]
            st.markdown(
                f'<div style="background:{_rm_bg};border-radius:12px;padding:9px 12px;'
                f'margin-bottom:6px;font-size:.8rem;">'
                f'<div style="font-size:.65rem;font-weight:700;color:{_rm_color};margin-bottom:3px;">{_rm_prefix}</div>'
                f'{_rm_content}</div>', unsafe_allow_html=True)

    _quick_input = st.text_area("Nói với Cừu...", placeholder="Cừu ơi, hôm nay mình...",
                                height=80, key="tab2_chat_input", label_visibility="collapsed")
    _chat_col1, _chat_col2 = st.columns([3, 1])
    with _chat_col1:
        if st.button("💬 Gửi cho Cừu 🐑", type="primary", use_container_width=True, key="tab2_send"):
            if _quick_input.strip():
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": _quick_input.strip()})
                _complete_quest(mem, "chat", 10)
                _add_exp(10, mem)
                _check_achievements(mem)
                # Quick sheep response
                _sheep_responses = [
                    f"🐑 Bê bê~ Cừu nghe rồi, {_user_name}! Mình luôn ở đây lắng nghe bạn 💜",
                    f"🐑 Ôi {_user_name}~ Kể tiếp đi, mình muốn nghe thêm!",
                    f"🐑 Cừu hiểu rồi... {_user_name} thật là tuyệt vời khi chia sẻ điều này 🌸",
                    f"🐑 Mình nhớ chuyện này của {_user_name} rồi nhé! Bê bê~",
                    f"🐑 Cảm ơn {_user_name} đã tâm sự với mình 💛 Mình cũng nhớ {_user_name} lắm!",
                ]
                _reply = _rand2.choice(_sheep_responses)
                st.session_state.messages.append({"role": "assistant", "content": _reply})
                mem.setdefault("notes", [])
                if len(mem["notes"]) < 20:
                    mem["notes"].append(_quick_input.strip()[:100])
                _save()
                st.rerun()
    with _chat_col2:
        if st.button("📔 Viết nhật ký", use_container_width=True, key="tab2_diary"):
            st.info("💡 Tab 1 có đầy đủ tính năng nhật ký + AI Cừu nhé!")

# ══ TAB 3: 👥 CỘNG ĐỒNG — Animal Crossing × Duolingo × Finch ══════════════════
with tab3:
    import os as _os3
    import streamlit.components.v1 as _comp3

    _GH3    = "https://raw.githubusercontent.com/Hoamaii/cuu-can-cu/main/assets"
    _uname3 = mem.get("name", "") or "Bạn"
    _streak3 = mem.get("streak", 0)
    _saved3  = mem.get("total_saved", 0)
    _dreams3 = mem.get("dreams", [])
    _dream3  = _dreams3[0]["name"].title() if _dreams3 else "Giấc mơ của tôi"
    _key3, _sname3, _lv3, *_ = get_growth_stage(_saved3)

    import hashlib as _hl3
    _ref3 = "CUU-" + _hl3.md5(_uname3.encode()).hexdigest()[:4].upper()

    # ── AI SUMMARY sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1A1A2E,#2D1B69);
             border-radius:16px;padding:16px 14px;margin-bottom:4px;">
          <div style="color:#c4a8ff;font-size:.64rem;font-weight:700;
               text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;">
               🐑 AI thấy hôm nay
          </div>
          <div style="color:rgba(255,255,255,.88);font-size:.77rem;line-height:1.9;">
              &bull; <strong style="color:#fff;">42</strong> cừu đang tiết kiệm MBA<br>
              &bull; <strong style="color:#fff;">Du lịch Nhật</strong> trend hot nhất<br>
              &bull; <strong style="color:#fff;">15</strong> giấc mơ vừa hoàn thành<br>
              &bull; <strong style="color:#fff;">321</strong> lời động viên đã gửi
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Community banner ──────────────────────────────────────────────────────
    st.markdown("""<style>
    section[data-testid="stMain"] div[data-testid="stImage"] img {
        border-radius:20px !important; max-height:280px;
        object-fit:cover; box-shadow:0 6px 24px rgba(0,0,0,.1);
    }</style>""", unsafe_allow_html=True)
    _ban3 = _os3.path.join(_os3.path.dirname(__file__), "assets", "community_banner.png")
    if _os3.path.exists(_ban3):
        st.image(_ban3, use_container_width=True)
    else:
        try:
            st.image(_GH3 + "/community_banner.png", use_container_width=True)
        except Exception:
            pass

    # Hero pill
    st.markdown("""
    <div style="text-align:center;margin:10px 0 16px;">
      <span style="background:linear-gradient(135deg,#f0e8ff,#ffe8f8);
           border-radius:30px;padding:8px 20px;display:inline-block;
           font-size:.8rem;font-weight:800;color:#7B5EA7;
           border:1.5px solid rgba(123,94,167,.18);">
        🐑 12.847 chú cừu đang cùng nhau theo đuổi giấc mơ ✨
      </span>
    </div>""", unsafe_allow_html=True)

    # ══ 4 SUB-TABS ══
    _ct1, _ct2, _ct3, _ct4 = st.tabs(["📰 Bảng Tin", "👯 Bạn Bè Cừu", "👨‍👩‍👧 Gia Đình", "👗 Thời Trang"])

    # ─────────────────────────────────────────────────────────────────────────
    # SUB-TAB 1: BẢNG TIN
    # ─────────────────────────────────────────────────────────────────────────
    with _ct1:
        _HTML_T1 = """<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:transparent;color:#1a1a2e;padding:0 0 20px;}

/* ── HIGHLIGHTS glass ── */
.hl{background:linear-gradient(135deg,#f0e8ff 0%,#e8f0ff 50%,#fff8f0 100%);
    border:1.5px solid rgba(123,94,167,.15);border-radius:22px;
    padding:18px 16px;margin-bottom:22px;position:relative;overflow:hidden;}
.hl::before{content:'';position:absolute;inset:0;
    background:rgba(255,255,255,.45);backdrop-filter:blur(12px);
    -webkit-backdrop-filter:blur(12px);border-radius:22px;pointer-events:none;}
.hl-in{position:relative;z-index:1;}
.hl-hd{font-size:.88rem;font-weight:800;color:#1a1a2e;
       margin-bottom:14px;display:flex;align-items:center;gap:8px;}
.dot{width:8px;height:8px;border-radius:50%;background:#7B5EA7;
     animation:pulse 1.8s infinite;}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(123,94,167,.4);}
 70%{box-shadow:0 0 0 8px rgba(123,94,167,0);}
 100%{box-shadow:0 0 0 0 rgba(123,94,167,0);}}
.hl-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.hl-item{background:rgba(255,255,255,.72);border-radius:16px;
         padding:12px 14px;display:flex;align-items:center;gap:10px;}
.hl-ico{font-size:1.4rem;flex-shrink:0;}
.hl-num{font-size:1.15rem;font-weight:800;color:#1a1a2e;line-height:1;}
.hl-lbl{font-size:.63rem;color:#8b94a8;margin-top:2px;line-height:1.3;}

/* ── STORY CARD ── */
.story{background:#fff;border:1.5px solid #f0f0f5;border-radius:22px;
       overflow:hidden;margin-bottom:22px;cursor:pointer;transition:all .2s;}
.story:hover{box-shadow:0 8px 28px rgba(0,0,0,.08);transform:translateY(-2px);}
.story-top{background:linear-gradient(135deg,#1A1A2E,#2D1B69,#0d2040);
           padding:18px 18px;display:flex;align-items:center;gap:14px;}
.story-av{width:58px;height:58px;border-radius:50%;
          background:rgba(255,255,255,.15);display:flex;align-items:center;
          justify-content:center;font-size:2rem;flex-shrink:0;
          border:2px solid rgba(255,255,255,.2);}
.story-name{font-size:1rem;font-weight:800;color:#fff;}
.story-tag{display:inline-flex;align-items:center;gap:4px;
           background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);
           border-radius:20px;padding:3px 10px;font-size:.63rem;
           color:rgba(255,255,255,.8);font-weight:600;margin-top:5px;}
.story-body{padding:16px 18px 18px;}
.story-q{font-size:.83rem;color:#7B5EA7;font-weight:700;
         font-style:italic;margin-bottom:8px;}
.story-txt{font-size:.82rem;color:#444;line-height:1.65;margin-bottom:14px;}
.story-btn{display:inline-flex;align-items:center;gap:6px;
           background:linear-gradient(135deg,#7B5EA7,#5a3d9a);
           color:#fff;border:none;border-radius:10px;
           padding:9px 18px;font-size:.77rem;font-weight:700;cursor:pointer;}

/* ── GUILDS ── */
.sec-hd{font-size:.9rem;font-weight:800;color:#1a1a2e;
        margin-bottom:12px;display:flex;align-items:center;
        justify-content:space-between;}
.sec-hd a{font-size:.68rem;font-weight:600;color:#7B5EA7;
          background:#f4eeff;border-radius:20px;padding:3px 10px;cursor:pointer;}
.g-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;
        margin-bottom:22px;}
.g-card{background:#fff;border:1.5px solid #f0f0f5;border-radius:18px;
        padding:14px 12px;cursor:pointer;transition:all .2s;text-align:left;}
.g-card:hover{box-shadow:0 4px 16px rgba(0,0,0,.08);transform:translateY(-2px);
              border-color:#d4b8ff;}
.g-ico{font-size:1.9rem;margin-bottom:6px;}
.g-name{font-size:.79rem;font-weight:800;color:#1a1a2e;line-height:1.3;margin-bottom:3px;}
.g-cnt{font-size:.63rem;color:#8b94a8;margin-bottom:5px;}
.g-hot{font-size:.6rem;color:#e8773d;background:#fff3ee;
       border-radius:6px;padding:3px 7px;display:inline-block;margin-bottom:8px;}
.g-btn{width:100%;padding:7px 0;border:1.5px solid #d4b8ff;border-radius:9px;
       background:#fff;font-size:.71rem;font-weight:700;color:#7B5EA7;cursor:pointer;}
.g-btn:hover{background:#f0e6ff;}
.g-btn.on{background:linear-gradient(135deg,#7B5EA7,#5a3d9a);color:#fff;border:none;}

/* ── FEED POSTS ── */
.fc{background:#fff;border:1.5px solid #f0f0f5;border-radius:18px;
    padding:14px 16px 12px;margin-bottom:10px;transition:all .18s;}
.fc:hover{box-shadow:0 4px 14px rgba(0,0,0,.06);transform:translateY(-1px);}
.fc-top{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
.fc-av{width:44px;height:44px;border-radius:50%;
       display:flex;align-items:center;justify-content:center;font-size:1.4rem;
       flex-shrink:0;}
.fc-name{font-size:.87rem;font-weight:700;color:#1a1a2e;}
.fc-time{font-size:.63rem;color:#bbb;margin-top:1px;}
.badge{border-radius:20px;padding:4px 10px;font-size:.63rem;
       font-weight:700;white-space:nowrap;display:inline-flex;
       align-items:center;gap:3px;flex-shrink:0;}
.b-streak{background:#fff3e0;color:#e65100;}
.b-goal  {background:#e8f5e9;color:#2e7d32;}
.b-motiv {background:#f3e5f5;color:#7b1fa2;}
.b-achiev{background:#e3f2fd;color:#1565c0;}
.b-lvlup {background:#fffde7;color:#f57f17;}
.fc-msg{font-size:.82rem;color:#444;line-height:1.55;
        padding:10px 12px;background:#f8f7fc;border-radius:12px;
        margin-bottom:10px;border-left:3px solid #d4b8ff;}
.fc-row{display:flex;gap:7px;align-items:center;}
.fc-lk{font-size:.7rem;color:#aaa;margin-right:auto;}
.fc-btn{padding:7px 10px;border:1.5px solid #ede8f8;border-radius:10px;
        background:#fff;font-size:.72rem;font-weight:600;color:#5a4a9a;
        cursor:pointer;transition:all .15s;white-space:nowrap;}
.fc-btn:hover{background:#f0e6ff;}
.fc-btn.hi{background:linear-gradient(135deg,#7B5EA7,#5a3d9a);color:#fff;border:none;}

/* TOAST */
#toast{position:fixed;bottom:16px;left:50%;
       transform:translateX(-50%) translateY(60px);
       background:#1a1a2e;color:#fff;padding:8px 18px;
       border-radius:22px;font-size:.77rem;font-weight:600;
       opacity:0;transition:all .28s cubic-bezier(.4,0,.2,1);
       z-index:9999;white-space:nowrap;
       box-shadow:0 6px 18px rgba(0,0,0,.25);pointer-events:none;}
#toast.on{opacity:1;transform:translateX(-50%) translateY(0);}
</style></head><body>
<div id="toast"></div>

<!-- HIGHLIGHTS -->
<div class="hl">
  <div class="hl-in">
    <div class="hl-hd"><div class="dot"></div>🐑 Hôm nay trong đàn cừu</div>
    <div class="hl-grid">
      <div class="hl-item"><div class="hl-ico">🔥</div>
        <div><div class="hl-num" id="n1">0</div><div class="hl-lbl">cừu được cho ăn</div></div></div>
      <div class="hl-item"><div class="hl-ico">🎓</div>
        <div><div class="hl-num" id="n2">0</div><div class="hl-lbl">giấc mơ hoàn thành</div></div></div>
      <div class="hl-item"><div class="hl-ico">💜</div>
        <div><div class="hl-num" id="n3">0</div><div class="hl-lbl">lời động viên gửi đi</div></div></div>
      <div class="hl-item"><div class="hl-ico">⭐</div>
        <div><div class="hl-num" id="n4">0</div><div class="hl-lbl">streak trên 30 ngày</div></div></div>
    </div>
  </div>
</div>

<!-- STORY OF THE DAY -->
<div class="story" onclick="toast('Đang mở câu chuyện đầy đủ...')">
  <div class="story-top">
    <div class="story-av">🐑</div>
    <div>
      <div class="story-name">Bông Mập · Câu chuyện hôm nay</div>
      <span class="story-tag">✨ AI Story Engine chọn lọc</span>
    </div>
  </div>
  <div class="story-body">
    <div class="story-q">"Từ 10.000đ/ngày đến học phí MBA — mất 730 ngày không bỏ lỡ."</div>
    <div class="story-txt">Hai năm trước Bông Mập chỉ bắt đầu bằng <strong>một ly trà sữa nhỏ mỗi sáng.</strong>
    Không ai tin điều đó thay đổi cuộc đời. Nhưng hôm nay cô ấy hoàn thành học phí MBA —
    không phải vì có nhiều tiền, mà vì <strong>không bao giờ bỏ cuộc.</strong></div>
    <button class="story-btn" onclick="event.stopPropagation();toast('Đang mở câu chuyện...')">📖 Đọc tiếp</button>
  </div>
</div>

<!-- GUILDS -->
<div class="sec-hd">🏡 Hội quán nổi bật <a onclick="toast('Tải thêm hội quán...')">Tất cả →</a></div>
<div class="g-grid">
  <div class="g-card">
    <div class="g-ico">✈️</div>
    <div class="g-name">Du lịch Nhật 2027</div>
    <div class="g-cnt">👥 4.112 cừu</div>
    <div class="g-hot">🔥 Đang hot</div>
    <button class="g-btn" onclick="toggleG(this,'Du lịch Nhật')">Tham gia</button>
  </div>
  <div class="g-card">
    <div class="g-ico">🎓</div>
    <div class="g-name">MBA Gang</div>
    <div class="g-cnt">👥 3.241 cừu</div>
    <div class="g-hot">✨ Mới: Mây Tích vừa tốt nghiệp!</div>
    <button class="g-btn" onclick="toggleG(this,'MBA')">Tham gia</button>
  </div>
  <div class="g-card">
    <div class="g-ico">🚗</div>
    <div class="g-name">Chiếc xe đầu tiên</div>
    <div class="g-cnt">👥 2.876 cừu</div>
    <div class="g-hot">🎉 Hùng vừa nhận chìa khoá</div>
    <button class="g-btn" onclick="toggleG(this,'Xe')">Tham gia</button>
  </div>
  <div class="g-card">
    <div class="g-ico">💰</div>
    <div class="g-name">Quỹ khẩn cấp</div>
    <div class="g-cnt">👥 1.540 cừu</div>
    <div class="g-hot">🛡️ An toàn tài chính</div>
    <button class="g-btn" onclick="toggleG(this,'Quỹ khẩn cấp')">Tham gia</button>
  </div>
</div>

<!-- COMMUNITY FEED -->
<div class="sec-hd">🐑 Bạn cừu hôm nay <a onclick="toast('Đang tải thêm...')">Xem tất cả →</a></div>

<div class="fc">
  <div class="fc-top">
    <div class="fc-av" style="background:linear-gradient(135deg,#f0e8ff,#e8f0ff);">🐑</div>
    <div style="flex:1;"><div class="fc-name">Bông Mập</div><div class="fc-time">2 phút · Hà Nội</div></div>
    <span class="badge b-streak">🔥 Streak 30</span>
  </div>
  <div class="fc-msg">Hoàn thành chuỗi <strong>30 ngày liên tiếp</strong> — không bỏ một ngày nào! 🎉</div>
  <div class="fc-row">
    <span class="fc-lk">❤️ 24 · 💬 5</span>
    <button class="fc-btn" onclick="likePost(this,'Bông Mập')">❤️ Chúc mừng</button>
    <button class="fc-btn hi" onclick="toast('🎁 Đã tặng quà!')">🎁 Tặng quà</button>
    <button class="fc-btn" onclick="toast('💬 Nhắn tin...')">💬 Nhắn</button>
  </div>
</div>

<div class="fc">
  <div class="fc-top">
    <div class="fc-av" style="background:linear-gradient(135deg,#e8f5ff,#f0fff8);">🐑</div>
    <div style="flex:1;"><div class="fc-name">Mây Tích</div><div class="fc-time">15 phút · TP.HCM</div></div>
    <span class="badge b-achiev">🎓 Thành tích</span>
  </div>
  <div class="fc-msg">Hoàn thành giấc mơ <strong>MBA</strong> hôm nay 🎓 Mất 2 năm. Cảm ơn đàn cừu! 🐑</div>
  <div class="fc-row">
    <span class="fc-lk">❤️ 87 · 💬 31</span>
    <button class="fc-btn" onclick="likePost(this,'Mây Tích')">🎉 Ăn mừng</button>
    <button class="fc-btn hi" onclick="toast('🎁 Đã tặng quà!')">🎁 Tặng quà</button>
    <button class="fc-btn" onclick="toast('💬 Nhắn tin...')">💬 Nhắn</button>
  </div>
</div>

<div class="fc">
  <div class="fc-top">
    <div class="fc-av" style="background:linear-gradient(135deg,#fff8e8,#fff0f8);">🐑</div>
    <div style="flex:1;"><div class="fc-name">Thu Hiền</div><div class="fc-time">2 giờ · Hà Nội</div></div>
    <span class="badge b-motiv">💜 Động viên</span>
  </div>
  <div class="fc-msg">Hôm nay khó khăn nhưng vẫn <strong>cho cừu ăn</strong>. Nhỏ thôi, nhưng không bỏ. 🐑</div>
  <div class="fc-row">
    <span class="fc-lk">❤️ 156 · 💬 42</span>
    <button class="fc-btn" onclick="likePost(this,'Thu Hiền')">💜 Ủng hộ</button>
    <button class="fc-btn hi" onclick="toast('🎁 Đã tặng quà!')">🎁 Tặng quà</button>
    <button class="fc-btn" onclick="toast('💬 Nhắn tin...')">💬 Nhắn</button>
  </div>
</div>

<script>
function toast(msg){
  var t=document.getElementById('toast');
  t.textContent=msg;t.classList.add('on');
  clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},2600);
}
function likePost(btn,name){
  if(btn.dataset.liked)return;
  btn.dataset.liked='1';btn.textContent='✅ Đã gửi';btn.disabled=true;btn.style.opacity='.6';
  toast('❤️ Đã gửi lời chúc đến '+name+'!');
}
function toggleG(btn,name){
  if(btn.classList.contains('on')){btn.classList.remove('on');btn.textContent='Tham gia';}
  else{btn.classList.add('on');btn.textContent='✓ Đã vào';toast('✅ Đã vào hội quán '+name+'!');}
}
function animCount(id,target){
  var el=document.getElementById(id),cur=0,step=Math.ceil(target/28);
  var iv=setInterval(function(){cur=Math.min(cur+step,target);el.textContent=cur;
    if(cur>=target)clearInterval(iv);},38);
}
window.addEventListener('load',function(){
  animCount('n1',247);animCount('n2',12);animCount('n3',321);animCount('n4',89);
});
</script></body></html>"""
        _comp3.html(_HTML_T1, height=2200, scrolling=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SUB-TAB 2: BẠN BÈ CỪU
    # ─────────────────────────────────────────────────────────────────────────
    with _ct2:
        _HTML_T2 = """<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:transparent;color:#1a1a2e;padding:0 0 20px;}

/* ── BUDDY HERO ── */
.buddy-hero{background:linear-gradient(135deg,#f0e8ff 0%,#ffe8f8 50%,#e8f8ff 100%);
    border-radius:24px;padding:22px 18px;margin-bottom:18px;text-align:center;
    border:1.5px solid rgba(123,94,167,.15);}
.buddy-avatars{display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:14px;}
.av-wrap{text-align:center;}
.av-circle{width:72px;height:72px;border-radius:50%;display:flex;align-items:center;
           justify-content:center;font-size:2.2rem;margin:0 auto 6px;
           border:3px solid #fff;box-shadow:0 4px 14px rgba(0,0,0,.1);}
.av-name{font-size:.7rem;font-weight:700;color:#666;}
.av-lv{font-size:.6rem;color:#7B5EA7;background:#f4eeff;
       border-radius:8px;padding:2px 7px;display:inline-block;margin-top:3px;}
.heart-mid{font-size:1.8rem;}
.buddy-title{font-size:1.05rem;font-weight:800;color:#1a1a2e;margin-bottom:5px;}
.buddy-sub{font-size:.78rem;color:#666;line-height:1.5;margin-bottom:16px;}

/* ── BUDDY STREAK BAR ── */
.streak-bar{background:#fff;border-radius:14px;padding:12px 16px;
            display:flex;align-items:center;gap:12px;margin-bottom:16px;
            border:1.5px solid #f0e8ff;}
.streak-bar .ico{font-size:1.5rem;}
.streak-lbl{font-size:.72rem;color:#888;}
.streak-val{font-size:1.05rem;font-weight:800;color:#7B5EA7;}
.streak-prog{flex:1;background:#f0f0f7;border-radius:8px;height:7px;overflow:hidden;}
.streak-fill{height:100%;border-radius:8px;
             background:linear-gradient(90deg,#7B5EA7,#e879b0);}

/* ── REWARD CHIPS ── */
.rewards{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px;justify-content:center;}
.reward{background:#fff;border:1.5px solid #f0e8ff;border-radius:14px;
        padding:10px 14px;display:flex;align-items:center;gap:8px;min-width:130px;}
.reward-ico{font-size:1.4rem;}
.reward-name{font-size:.74rem;font-weight:700;color:#1a1a2e;}
.reward-sub{font-size:.62rem;color:#8b94a8;margin-top:1px;}
.reward.locked{opacity:.5;}
.reward.locked .reward-ico::after{content:'🔒';font-size:.7rem;}

/* ── FRIEND SUGGESTIONS ── */
.sec-hd{font-size:.9rem;font-weight:800;color:#1a1a2e;
        margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;}
.sec-hd a{font-size:.68rem;font-weight:600;color:#7B5EA7;background:#f4eeff;
          border-radius:20px;padding:3px 10px;cursor:pointer;}
.ai-chip{display:inline-flex;align-items:center;gap:4px;
         background:#f0fff4;border:1px solid #b8f0c8;border-radius:20px;
         padding:3px 9px;font-size:.62rem;font-weight:700;color:#2a9d5c;
         margin-bottom:12px;}
.f-scroll{display:flex;gap:12px;overflow-x:auto;padding-bottom:8px;
          -webkit-overflow-scrolling:touch;scrollbar-width:none;}
.f-scroll::-webkit-scrollbar{display:none;}
.f-card{background:#fff;border:1.5px solid #f0f0f5;border-radius:20px;
        padding:16px 14px;min-width:150px;flex-shrink:0;
        transition:all .2s;cursor:pointer;text-align:center;}
.f-card:hover{box-shadow:0 5px 18px rgba(0,0,0,.08);transform:translateY(-2px);border-color:#d4b8ff;}
.f-av{width:52px;height:52px;border-radius:50%;
      background:linear-gradient(135deg,#f0e8ff,#ffe8f8);
      display:flex;align-items:center;justify-content:center;
      font-size:1.6rem;margin:0 auto 8px;border:2px solid #f0e8ff;}
.f-name{font-size:.82rem;font-weight:700;color:#1a1a2e;margin-bottom:5px;}
.f-goal{font-size:.7rem;color:#7B5EA7;font-weight:600;
        background:#f4eeff;border-radius:8px;padding:3px 8px;
        display:inline-block;margin-bottom:5px;}
.f-stats{font-size:.63rem;color:#8b94a8;line-height:1.7;margin-bottom:9px;}
.f-btn{width:100%;padding:7px 0;border:1.5px solid #d4b8ff;border-radius:9px;
       background:#fff;font-size:.72rem;font-weight:700;color:#7B5EA7;cursor:pointer;}
.f-btn:hover{background:#f0e6ff;}
.f-btn.on{background:linear-gradient(135deg,#7B5EA7,#5a3d9a);color:#fff;border:none;}

/* ── INVITE REWARD BOX ── */
.inv-box{background:linear-gradient(135deg,#1A1A2E,#2D1B69);
         border-radius:22px;padding:20px 18px;margin-bottom:16px;}
.inv-title{color:#fff;font-size:.88rem;font-weight:800;margin-bottom:14px;
           display:flex;align-items:center;gap:8px;}
.inv-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px;}
.inv-tier{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);
          border-radius:14px;padding:12px 8px;text-align:center;}
.inv-lbl{font-size:.54rem;color:rgba(255,255,255,.4);
         text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px;}
.inv-val{font-size:1rem;font-weight:800;color:#fff;}
.inv-desc{font-size:.62rem;color:#d4b8ff;font-weight:600;margin-top:4px;}
.inv-code{display:flex;align-items:center;gap:10px;
          background:rgba(255,255,255,.07);border:1.5px solid rgba(255,255,255,.12);
          border-radius:12px;padding:10px 14px;}
.inv-code-lbl{font-size:.62rem;color:rgba(255,255,255,.4);}
.inv-code-val{font-size:.95rem;font-weight:800;color:#fff;letter-spacing:.12em;flex:1;}

/* ── BUTTONS ── */
.big-btn{width:100%;padding:14px;border-radius:14px;font-size:.85rem;
         font-weight:800;cursor:pointer;border:none;transition:all .18s;}
.big-btn:hover{opacity:.92;transform:translateY(-1px);}
.btn-primary{background:linear-gradient(135deg,#7B5EA7,#5a3d9a);color:#fff;margin-bottom:10px;}
.btn-outline{background:#fff;border:1.5px solid #d4b8ff!important;border:none;
             color:#7B5EA7;}

/* TOAST */
#toast{position:fixed;bottom:16px;left:50%;
       transform:translateX(-50%) translateY(60px);
       background:#1a1a2e;color:#fff;padding:8px 18px;border-radius:22px;
       font-size:.77rem;font-weight:600;opacity:0;
       transition:all .28s cubic-bezier(.4,0,.2,1);z-index:9999;
       white-space:nowrap;box-shadow:0 6px 18px rgba(0,0,0,.25);pointer-events:none;}
#toast.on{opacity:1;transform:translateX(-50%) translateY(0);}
</style></head><body>
<div id="toast"></div>

<!-- BUDDY HERO -->
<div class="buddy-hero">
  <div class="buddy-avatars">
    <div class="av-wrap">
      <div class="av-circle" style="background:linear-gradient(135deg,#f0e8ff,#d4b8ff);">🐑</div>
      <div class="av-name">Bạn</div>
      <div class="av-lv">Lv.3 · 42🔥</div>
    </div>
    <div class="heart-mid">💛</div>
    <div class="av-wrap">
      <div class="av-circle" style="background:linear-gradient(135deg,#ffe8f8,#ffb8d8);">🐑</div>
      <div class="av-name">Hoa Nhỏ</div>
      <div class="av-lv">Lv.3 · 38🔥</div>
    </div>
  </div>
  <div class="buddy-title">👯 Bạn Thân Cừu</div>
  <div class="buddy-sub">Bạn và Hoa Nhỏ đang cùng nuôi cừu được <strong>12 ngày</strong> rồi!<br>
    Duy trì streak đôi để mở khóa skin và quà đặc biệt.</div>
  <div class="streak-bar">
    <div class="ico">🔥</div>
    <div><div class="streak-val">Streak đôi: 12 ngày</div>
    <div class="streak-lbl">Còn 3 ngày nữa để mở skin đôi!</div></div>
    <div class="streak-prog"><div class="streak-fill" style="width:80%;"></div></div>
  </div>
</div>

<!-- REWARDS -->
<div class="sec-hd" style="margin-bottom:10px;">🎁 Phần thưởng khi có bạn thân</div>
<div class="rewards">
  <div class="reward">
    <div class="reward-ico">🐑</div>
    <div><div class="reward-name">Skin đôi</div>
    <div class="reward-sub">Mở lúc streak 15 ngày</div></div>
  </div>
  <div class="reward">
    <div class="reward-ico">💛</div>
    <div><div class="reward-name">+100 iXu</div>
    <div class="reward-sub">Mỗi bạn mời thành công</div></div>
  </div>
  <div class="reward locked">
    <div class="reward-ico">👑</div>
    <div><div class="reward-name">Khung avatar đôi</div>
    <div class="reward-sub">Khi cả hai lên Lv.5</div></div>
  </div>
</div>

<!-- AI FRIEND MATCHING -->
<div class="sec-hd">🐑 Cừu giống bạn nhất
  <a onclick="toast('AI đang tìm thêm bạn cừu...')">Tìm thêm →</a>
</div>
<span class="ai-chip">✨ AI khớp theo mục tiêu &amp; hành vi</span>
<div class="f-scroll">
  <div class="f-card">
    <div class="f-av">🐑</div>
    <div class="f-name">Hoa Nhỏ</div>
    <div class="f-goal">✈️ Du lịch Nhật</div>
    <div class="f-stats">🔥 Streak 42 ngày<br>📍 Hà Nội · Lv.3</div>
    <button class="f-btn on">✓ Bạn thân</button>
  </div>
  <div class="f-card">
    <div class="f-av">🐑</div>
    <div class="f-name">Lan Thảo</div>
    <div class="f-goal">🎓 MBA</div>
    <div class="f-stats">🔥 Streak 65 ngày<br>📍 Đà Nẵng · Lv.4</div>
    <button class="f-btn" onclick="followFriend(this,'Lan Thảo')">Kết bạn</button>
  </div>
  <div class="f-card">
    <div class="f-av">🐑</div>
    <div class="f-name">Tuấn Béo</div>
    <div class="f-goal">🏠 Mua nhà</div>
    <div class="f-stats">🔥 Streak 28 ngày<br>📍 TP.HCM · Lv.2</div>
    <button class="f-btn" onclick="followFriend(this,'Tuấn Béo')">Kết bạn</button>
  </div>
  <div class="f-card">
    <div class="f-av">🐑</div>
    <div class="f-name">Ngọc Mập</div>
    <div class="f-goal">💰 Tự do TC</div>
    <div class="f-stats">🔥 Streak 112 ngày<br>📍 Hải Phòng · Lv.5</div>
    <button class="f-btn" onclick="followFriend(this,'Ngọc Mập')">Kết bạn</button>
  </div>
  <div class="f-card">
    <div class="f-av">🐑</div>
    <div class="f-name">Minh Lùn</div>
    <div class="f-goal">🚗 Mua xe</div>
    <div class="f-stats">🔥 Streak 17 ngày<br>📍 Hà Nội · Lv.2</div>
    <button class="f-btn" onclick="followFriend(this,'Minh Lùn')">Kết bạn</button>
  </div>
</div>

<!-- INVITE BOX -->
<div style="height:18px;"></div>
<div class="inv-box">
  <div class="inv-title">🎁 Mời bạn — cả hai cùng thắng</div>
  <div class="inv-grid">
    <div class="inv-tier">
      <div class="inv-lbl">Mời 1 bạn</div>
      <div class="inv-val">+100</div>
      <div class="inv-desc">iXu cho cả hai</div>
    </div>
    <div class="inv-tier">
      <div class="inv-lbl">Mời 5 bạn</div>
      <div class="inv-val">🎨</div>
      <div class="inv-desc">Skin độc quyền</div>
    </div>
    <div class="inv-tier">
      <div class="inv-lbl">Mời 10 bạn</div>
      <div class="inv-val">👑</div>
      <div class="inv-desc">Trưởng Đàn</div>
    </div>
  </div>
  <div class="inv-code">
    <span class="inv-code-lbl">Mã của bạn</span>
    <span class="inv-code-val">__REF__</span>
  </div>
</div>
<div style="height:12px;"></div>
<button class="big-btn btn-primary" onclick="toast('🐑 Đã sao chép link mời!')">
  🐑 Rủ bạn cùng nuôi cừu
</button>
<button class="big-btn btn-outline" onclick="toast('🎁 Đã tạo quà tặng cừu!')">
  🎁 Tặng bạn một chú cừu
</button>

<script>
function toast(msg){
  var t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');
  clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},2600);
}
function followFriend(btn,name){
  if(btn.classList.contains('on')){btn.classList.remove('on');btn.textContent='Kết bạn';}
  else{btn.classList.add('on');btn.textContent='✓ Đã kết bạn';toast('✅ Đã kết bạn với '+name+'!');}
}
</script></body></html>""".replace("__REF__", _ref3)
        # ── buddy_sheep.png (native Streamlit — PIL-safe, no iframe CSP) ──────
        st.markdown("""<style>
        div[data-testid="stImage"] img {
            border-radius:20px !important;
            object-fit:contain !important;
            max-height:none !important;
            width:100%;
            box-shadow:0 5px 18px rgba(0,0,0,.08);
            background:#f8f6ff;
        }</style>""", unsafe_allow_html=True)
        _buddy_local = _os3.path.join(_os3.path.dirname(__file__), "assets", "buddy_sheep.png")
        _buddy_gh    = _GH3 + "/buddy_sheep.png"
        try:
            from PIL import Image as _PIL_B
            if _os3.path.exists(_buddy_local):
                _PIL_B.open(_buddy_local).verify()
                st.image(_buddy_local, use_container_width=True)
            else:
                raise FileNotFoundError
        except Exception:
            try:
                import urllib.request as _ur_b
                _req_b = _ur_b.Request(_buddy_gh, headers={"User-Agent": "Mozilla/5.0"})
                with _ur_b.urlopen(_req_b, timeout=8) as _r_b:
                    _buddy_bytes = _r_b.read()
                st.image(_buddy_bytes, use_container_width=True)
            except Exception:
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#f0e8ff,#e8f8ff);'
                    'border-radius:20px;padding:40px;text-align:center;font-size:3rem;">🐑💛🐑</div>',
                    unsafe_allow_html=True)
        _comp3.html(_HTML_T2, height=2000, scrolling=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SUB-TAB 3: GIA ĐÌNH CỪU
    # ─────────────────────────────────────────────────────────────────────────
    with _ct3:
        _HTML_T3 = """<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:transparent;color:#1a1a2e;padding:0 0 20px;}

/* ── FAMILY HERO ── */
.fam-hero{background:linear-gradient(135deg,#fff8e8 0%,#f0e8ff 50%,#e8f8ff 100%);
    border-radius:24px;padding:22px 16px 18px;margin-bottom:18px;text-align:center;
    border:1.5px solid rgba(255,200,100,.25);}
.fam-title{font-size:1.05rem;font-weight:800;color:#1a1a2e;margin-bottom:5px;}
.fam-sub{font-size:.78rem;color:#888;line-height:1.5;margin-bottom:18px;}
.fam-tree{display:flex;align-items:flex-end;justify-content:center;gap:8px;margin-bottom:14px;}
.fam-member{text-align:center;flex-shrink:0;}
.fam-av{border-radius:50%;display:flex;align-items:center;justify-content:center;
        font-size:1.8rem;margin:0 auto 5px;border:3px solid #fff;
        box-shadow:0 3px 10px rgba(0,0,0,.1);}
.fam-role{font-size:.68rem;font-weight:700;color:#666;}
.fam-streak{font-size:.6rem;color:#7B5EA7;background:#f4eeff;
            border-radius:8px;padding:2px 6px;display:inline-block;margin-top:2px;}
.conn-line{width:20px;height:2px;background:linear-gradient(90deg,#f0e8ff,#d4b8ff);
           border-radius:2px;margin-bottom:32px;}

/* ── INVITE PARENT/CHILD CARD ── */
.inv-card{background:#fff;border:1.5px solid #f0f0f5;border-radius:20px;
          padding:16px 18px;margin-bottom:12px;display:flex;align-items:center;gap:14px;}
.inv-card-ico{width:52px;height:52px;border-radius:16px;display:flex;
              align-items:center;justify-content:center;font-size:1.6rem;flex-shrink:0;}
.inv-card-name{font-size:.88rem;font-weight:800;color:#1a1a2e;}
.inv-card-sub{font-size:.73rem;color:#888;margin-top:2px;line-height:1.4;}
.inv-card-btn{margin-left:auto;flex-shrink:0;padding:8px 14px;
              border-radius:10px;font-size:.72rem;font-weight:700;
              background:linear-gradient(135deg,#7B5EA7,#5a3d9a);
              color:#fff;border:none;cursor:pointer;white-space:nowrap;}

/* ── FAMILY FEED ── */
.sec-hd{font-size:.9rem;font-weight:800;color:#1a1a2e;margin-bottom:12px;
        display:flex;align-items:center;justify-content:space-between;}
.ff{background:#fff;border:1.5px solid #f0f0f5;border-radius:18px;
    padding:14px 16px;margin-bottom:10px;}
.ff-top{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
.ff-av{width:40px;height:40px;border-radius:50%;display:flex;
       align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0;}
.ff-name{font-size:.85rem;font-weight:700;color:#1a1a2e;}
.ff-time{font-size:.62rem;color:#bbb;margin-top:1px;}
.ff-badge{border-radius:20px;padding:3px 9px;font-size:.62rem;font-weight:700;
          white-space:nowrap;flex-shrink:0;}
.ff-msg{font-size:.82rem;color:#444;line-height:1.55;padding:10px 12px;
        background:#fffbf0;border-radius:12px;border-left:3px solid #FFD700;}
.ff-row{display:flex;gap:7px;margin-top:9px;}
.ff-btn{padding:7px 10px;border:1.5px solid #f0e8d0;border-radius:10px;
        background:#fff;font-size:.72rem;font-weight:600;color:#b07a20;
        cursor:pointer;}
.ff-btn:hover{background:#fffbf0;}
.ff-btn.hi{background:linear-gradient(135deg,#FFD700,#FFA500);color:#1a1a2e;border:none;}

/* ── FAMILY ACTIONS ── */
.fam-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:18px;}
.fam-act{background:#fff;border:1.5px solid #f0f0f5;border-radius:18px;
         padding:16px 14px;text-align:center;cursor:pointer;transition:all .2s;}
.fam-act:hover{box-shadow:0 4px 14px rgba(0,0,0,.07);transform:translateY(-2px);border-color:#d4b8ff;}
.fam-act-ico{font-size:1.8rem;margin-bottom:7px;}
.fam-act-name{font-size:.79rem;font-weight:700;color:#1a1a2e;margin-bottom:3px;}
.fam-act-sub{font-size:.63rem;color:#8b94a8;line-height:1.35;}

/* TOAST */
#toast{position:fixed;bottom:16px;left:50%;
       transform:translateX(-50%) translateY(60px);
       background:#1a1a2e;color:#fff;padding:8px 18px;border-radius:22px;
       font-size:.77rem;font-weight:600;opacity:0;
       transition:all .28s cubic-bezier(.4,0,.2,1);z-index:9999;
       white-space:nowrap;box-shadow:0 6px 18px rgba(0,0,0,.25);pointer-events:none;}
#toast.on{opacity:1;transform:translateX(-50%) translateY(0);}
</style></head><body>
<div id="toast"></div>

<!-- FAMILY HERO -->
<div class="fam-hero">
  <div class="fam-title">👨‍👩‍👧 Gia đình cừu của bạn</div>
  <div class="fam-sub">Tiết kiệm cùng gia đình — vui hơn, bền hơn.</div>
  <div class="fam-tree">
    <div class="fam-member">
      <div class="fam-av" style="width:64px;height:64px;background:linear-gradient(135deg,#e8f0ff,#d4e8ff);">🐏</div>
      <div class="fam-role">Cừu Bố</div>
      <div class="fam-streak">🔥 21 ngày</div>
    </div>
    <div class="conn-line"></div>
    <div class="fam-member">
      <div class="fam-av" style="width:72px;height:72px;background:linear-gradient(135deg,#f0e8ff,#ffe8f8);">🐑</div>
      <div class="fam-role">Bạn</div>
      <div class="fam-streak">🔥 42 ngày</div>
    </div>
    <div class="conn-line"></div>
    <div class="fam-member">
      <div class="fam-av" style="width:56px;height:56px;background:linear-gradient(135deg,#f0fff8,#d4f5e8);">🐑</div>
      <div class="fam-role">Cừu Em</div>
      <div class="fam-streak">🔥 7 ngày</div>
    </div>
  </div>
  <div style="background:rgba(255,255,255,.7);border-radius:14px;padding:10px 14px;
              text-align:left;display:flex;align-items:center;gap:10px;">
    <span style="font-size:1.3rem;">🏆</span>
    <div>
      <div style="font-size:.8rem;font-weight:800;color:#1a1a2e;">Gia đình cừu · Lv.2</div>
      <div style="font-size:.65rem;color:#888;">Tổng streak đàn cừu: 70 ngày · Xếp hạng #128</div>
    </div>
  </div>
</div>

<!-- INVITE -->
<div class="inv-card">
  <div class="inv-card-ico" style="background:#e8f0ff;">👨</div>
  <div>
    <div class="inv-card-name">Thêm Cừu Bố</div>
    <div class="inv-card-sub">Mời bố tham gia — nhận 200 iXu cho gia đình</div>
  </div>
  <button class="inv-card-btn" onclick="toast('📲 Đã gửi lời mời cho Bố!')">Mời Bố</button>
</div>
<div class="inv-card">
  <div class="inv-card-ico" style="background:#fff0f8;">👩</div>
  <div>
    <div class="inv-card-name">Thêm Cừu Mẹ</div>
    <div class="inv-card-sub">Mời mẹ tham gia — cùng theo dõi tiến độ</div>
  </div>
  <button class="inv-card-btn" onclick="toast('📲 Đã gửi lời mời cho Mẹ!')">Mời Mẹ</button>
</div>
<div class="inv-card">
  <div class="inv-card-ico" style="background:#f0fff8;">🧒</div>
  <div>
    <div class="inv-card-name">Thêm Cừu Con / Em</div>
    <div class="inv-card-sub">Dạy con tiết kiệm từ nhỏ · Tài khoản thiếu nhi</div>
  </div>
  <button class="inv-card-btn" onclick="toast('📲 Đã tạo tài khoản Cừu Con!')">Tạo cho Con</button>
</div>

<div style="height:16px;"></div>

<!-- FAMILY ACTIONS -->
<div class="sec-hd">🎁 Hành động gia đình</div>
<div class="fam-actions">
  <div class="fam-act" onclick="toast('🎁 Đã gửi iXu cho Cừu Em!')">
    <div class="fam-act-ico">💛</div>
    <div class="fam-act-name">Tặng iXu</div>
    <div class="fam-act-sub">Gửi iXu cho thành viên</div>
  </div>
  <div class="fam-act" onclick="toast('🎁 Đang chọn quà...')">
    <div class="fam-act-ico">🎁</div>
    <div class="fam-act-name">Tặng quà</div>
    <div class="fam-act-sub">Skin, mũ, phụ kiện</div>
  </div>
  <div class="fam-act" onclick="toast('🎓 Đã khen thưởng Cừu Em!')">
    <div class="fam-act-ico">🏅</div>
    <div class="fam-act-name">Khen thưởng</div>
    <div class="fam-act-sub">Trao huy hiệu cho con</div>
  </div>
  <div class="fam-act" onclick="toast('📊 Đang xem tiến độ...')">
    <div class="fam-act-ico">📊</div>
    <div class="fam-act-name">Theo dõi tiến độ</div>
    <div class="fam-act-sub">AI gợi ý động viên con</div>
  </div>
</div>

<!-- FAMILY FEED -->
<div class="sec-hd">📰 Bản tin gia đình cừu</div>

<div class="ff">
  <div class="ff-top">
    <div class="ff-av" style="background:linear-gradient(135deg,#e8f0ff,#d4e8ff);">🐏</div>
    <div style="flex:1;"><div class="ff-name">Cừu Bố</div><div class="ff-time">3 phút trước</div></div>
    <span class="ff-badge" style="background:#e8f5ff;color:#1565c0;">💛 Gửi quà</span>
  </div>
  <div class="ff-msg">Bố vừa gửi <strong>50 iXu</strong> cho Cừu Em — "Giỏi lắm con! Giữ streak nhé." 🐑</div>
  <div class="ff-row">
    <button class="ff-btn hi" onclick="toast('❤️ Đã cảm ơn Bố!')">❤️ Cảm ơn Bố</button>
    <button class="ff-btn" onclick="toast('💬 Nhắn tin Bố...')">💬 Nhắn</button>
  </div>
</div>

<div class="ff">
  <div class="ff-top">
    <div class="ff-av" style="background:linear-gradient(135deg,#f0fff8,#d4f5e8);">🐑</div>
    <div style="flex:1;"><div class="ff-name">Cừu Em</div><div class="ff-time">1 giờ trước</div></div>
    <span class="ff-badge" style="background:#e8f5e9;color:#2e7d32;">⭐ Streak 7 ngày</span>
  </div>
  <div class="ff-msg">Cừu Em vừa đạt <strong>streak 7 ngày liên tiếp</strong>! Lần đầu tiên không bỏ lỡ 🌟</div>
  <div class="ff-row">
    <button class="ff-btn hi" onclick="toast('🏅 Đã khen thưởng Cừu Em!')">🏅 Khen thưởng</button>
    <button class="ff-btn" onclick="toast('🎁 Tặng quà cho Em!')">🎁 Tặng quà</button>
  </div>
</div>

<div class="ff">
  <div class="ff-top">
    <div class="ff-av" style="background:linear-gradient(135deg,#fff0f8,#ffd4e8);">👩</div>
    <div style="flex:1;"><div class="ff-name">Cừu Mẹ</div><div class="ff-time">Hôm qua</div></div>
    <span class="ff-badge" style="background:#f3e5f5;color:#7b1fa2;">💜 Động viên</span>
  </div>
  <div class="ff-msg">Mẹ nhắn: <strong>"Con đang làm rất tốt! Cả nhà tự hào về con."</strong> 💜🐑</div>
  <div class="ff-row">
    <button class="ff-btn hi" onclick="toast('❤️ Đã cảm ơn Mẹ!')">❤️ Cảm ơn Mẹ</button>
  </div>
</div>

<script>
function toast(msg){
  var t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');
  clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},2600);
}
</script></body></html>"""
        # ── family_sheep.png (native Streamlit — PIL-safe, no iframe CSP) ──────
        st.markdown("""<style>
        div[data-testid="stImage"] img {
            border-radius:20px !important;
            object-fit:contain !important;
            max-height:none !important;
            width:100%;
            box-shadow:0 5px 18px rgba(0,0,0,.08);
            background:#fdf8ff;
        }</style>""", unsafe_allow_html=True)
        # ── family_sheep.png load ─────────────────────────────────────────────
        _fam_local = _os3.path.join(_os3.path.dirname(__file__), "assets", "family_sheep.png")
        _fam_gh    = _GH3 + "/family_sheep.png"
        try:
            from PIL import Image as _PIL_F
            if _os3.path.exists(_fam_local):
                _PIL_F.open(_fam_local).verify()
                st.image(_fam_local, use_container_width=True)
            else:
                raise FileNotFoundError
        except Exception:
            try:
                import urllib.request as _ur_f
                _req_f = _ur_f.Request(_fam_gh, headers={"User-Agent": "Mozilla/5.0"})
                with _ur_f.urlopen(_req_f, timeout=8) as _r_f:
                    _fam_bytes = _r_f.read()
                st.image(_fam_bytes, use_container_width=True)
            except Exception:
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#fff8e8,#f0e8ff);'
                    'border-radius:20px;padding:40px;text-align:center;font-size:3rem;">🐏👩🐑🐑</div>',
                    unsafe_allow_html=True)
        _comp3.html(_HTML_T3, height=2200, scrolling=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SUB-TAB 4: THỜI TRANG CỪU
    # ─────────────────────────────────────────────────────────────────────────
    with _ct4:
        _HTML_T4 = """<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
     background:transparent;color:#1a1a2e;padding:0 0 20px;}

/* ── WARDROBE HERO ── */
.ward-hero{background:linear-gradient(135deg,#f0e8ff 0%,#ffe8f8 60%,#fff8e8 100%);
    border-radius:24px;padding:18px 16px;margin-bottom:18px;text-align:center;
    border:1.5px solid rgba(123,94,167,.12);}
.sheep-display{font-size:5rem;margin-bottom:8px;filter:drop-shadow(0 4px 10px rgba(123,94,167,.25));}
.ward-name{font-size:1rem;font-weight:800;color:#1a1a2e;margin-bottom:4px;}
.ward-set{font-size:.75rem;color:#7B5EA7;font-weight:600;margin-bottom:10px;}
.ward-stats{display:flex;justify-content:center;gap:16px;}
.ws{text-align:center;}
.ws-val{font-size:.95rem;font-weight:800;color:#1a1a2e;}
.ws-lbl{font-size:.6rem;color:#8b94a8;margin-top:1px;}

/* ── CATEGORY TABS ── */
.cat-row{display:flex;gap:8px;overflow-x:auto;padding-bottom:6px;
         margin-bottom:16px;scrollbar-width:none;}
.cat-row::-webkit-scrollbar{display:none;}
.cat{padding:8px 14px;border-radius:20px;font-size:.75rem;font-weight:700;
     border:1.5px solid #f0f0f5;background:#fff;cursor:pointer;
     white-space:nowrap;transition:all .15s;}
.cat.on{background:linear-gradient(135deg,#7B5EA7,#5a3d9a);color:#fff;border:none;}
.cat:hover:not(.on){background:#f4eeff;border-color:#d4b8ff;}

/* ── SETS ── */
.sec-hd{font-size:.9rem;font-weight:800;color:#1a1a2e;
        margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;}
.sets-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(152px,1fr));
           gap:12px;margin-bottom:20px;}
.set-card{background:#fff;border:1.5px solid #f0f0f5;border-radius:20px;
          padding:16px 12px;text-align:center;cursor:pointer;transition:all .2s;position:relative;}
.set-card:hover{box-shadow:0 5px 18px rgba(0,0,0,.08);transform:translateY(-2px);border-color:#d4b8ff;}
.set-card.active{border-color:#7B5EA7;box-shadow:0 0 0 3px rgba(123,94,167,.15);}
.set-ico{font-size:2.4rem;margin-bottom:8px;}
.set-name{font-size:.8rem;font-weight:800;color:#1a1a2e;margin-bottom:3px;}
.set-desc{font-size:.63rem;color:#8b94a8;line-height:1.4;margin-bottom:10px;}
.set-cost{font-size:.7rem;font-weight:700;margin-bottom:9px;}
.cost-free{color:#2a9d5c;background:#e8f5e9;border-radius:6px;padding:2px 7px;}
.cost-ix{color:#7B5EA7;background:#f4eeff;border-radius:6px;padding:2px 7px;}
.cost-lock{color:#888;background:#f5f5f5;border-radius:6px;padding:2px 7px;}
.set-btn{width:100%;padding:8px 0;border-radius:10px;font-size:.74rem;
         font-weight:700;cursor:pointer;border:none;transition:all .15s;}
.set-btn:hover{opacity:.9;}
.set-wearing{background:linear-gradient(135deg,#7B5EA7,#5a3d9a);color:#fff;}
.set-equip  {background:linear-gradient(135deg,#f0e8ff,#e8d8ff);color:#7B5EA7;border:1.5px solid #d4b8ff!important;}
.set-buy    {background:linear-gradient(135deg,#FFD700,#FFA500);color:#1a1a2e;}
.set-locked {background:#f5f5f5;color:#888;}
.badge-new{position:absolute;top:10px;right:10px;
           background:linear-gradient(135deg,#FF3B30,#FF6B35);
           color:#fff;border-radius:8px;padding:2px 7px;
           font-size:.58rem;font-weight:800;}
.badge-pop{position:absolute;top:10px;right:10px;
           background:linear-gradient(135deg,#7B5EA7,#5a3d9a);
           color:#fff;border-radius:8px;padding:2px 7px;
           font-size:.58rem;font-weight:800;}

/* ── ITEMS ── */
.items-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:20px;}
.item{background:#fff;border:1.5px solid #f0f0f5;border-radius:14px;
      padding:10px 8px;text-align:center;cursor:pointer;transition:all .18s;position:relative;}
.item:hover{box-shadow:0 3px 10px rgba(0,0,0,.07);border-color:#d4b8ff;}
.item.on{border-color:#7B5EA7;box-shadow:0 0 0 2px rgba(123,94,167,.15);}
.item-ico{font-size:1.6rem;margin-bottom:4px;}
.item-name{font-size:.62rem;font-weight:600;color:#444;line-height:1.3;}
.item-lock{position:absolute;top:4px;right:4px;font-size:.6rem;}

/* ── IXU BAR ── */
.ixu-bar{background:linear-gradient(135deg,#1A1A2E,#2D1B69);
         border-radius:18px;padding:14px 16px;
         display:flex;align-items:center;gap:14px;margin-bottom:16px;}
.ixu-ico{font-size:1.8rem;}
.ixu-val{font-size:1.2rem;font-weight:800;color:#fff;}
.ixu-lbl{font-size:.65rem;color:rgba(255,255,255,.55);}
.ixu-earn{margin-left:auto;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);
          border-radius:10px;padding:7px 12px;font-size:.7rem;font-weight:700;
          color:#d4b8ff;cursor:pointer;}

/* TOAST */
#toast{position:fixed;bottom:16px;left:50%;
       transform:translateX(-50%) translateY(60px);
       background:#1a1a2e;color:#fff;padding:8px 18px;border-radius:22px;
       font-size:.77rem;font-weight:600;opacity:0;
       transition:all .28s cubic-bezier(.4,0,.2,1);z-index:9999;
       white-space:nowrap;box-shadow:0 6px 18px rgba(0,0,0,.25);pointer-events:none;}
#toast.on{opacity:1;transform:translateX(-50%) translateY(0);}
</style></head><body>
<div id="toast"></div>

<!-- WARDROBE HERO -->
<div class="ward-hero">
  <div class="sheep-display" id="sheepDisplay">🐑</div>
  <div class="ward-name">Cừu của bạn</div>
  <div class="ward-set" id="activeSet">🌱 Đang mặc: Bộ Nông dân</div>
  <div class="ward-stats">
    <div class="ws"><div class="ws-val">💛 480</div><div class="ws-lbl">iXu hiện có</div></div>
    <div class="ws"><div class="ws-val">👗 6</div><div class="ws-lbl">trang phục đã mở</div></div>
    <div class="ws"><div class="ws-val">✨ 12</div><div class="ws-lbl">vật phẩm sở hữu</div></div>
  </div>
</div>

<!-- IXU BAR -->
<div class="ixu-bar">
  <div class="ixu-ico">💛</div>
  <div><div class="ixu-val">480 iXu</div><div class="ixu-lbl">Số dư hiện tại</div></div>
  <button class="ixu-earn" onclick="toast('🔥 Tiết kiệm mỗi ngày để kiếm thêm iXu!')">+ Kiếm thêm</button>
</div>

<!-- CATEGORY TABS -->
<div class="cat-row">
  <button class="cat on" onclick="setCat(this,'all')">Tất cả</button>
  <button class="cat" onclick="setCat(this,'hat')">🎩 Mũ</button>
  <button class="cat" onclick="setCat(this,'outfit')">👗 Trang phục</button>
  <button class="cat" onclick="setCat(this,'bag')">🎒 Balo</button>
  <button class="cat" onclick="setCat(this,'glasses')">👓 Kính</button>
  <button class="cat" onclick="setCat(this,'special')">✨ Đặc biệt</button>
</div>

<!-- SETS -->
<div class="sec-hd">🌟 Bộ trang phục</div>
<div class="sets-grid">

  <div class="set-card active" onclick="wearSet(this,'🌱 Bộ Nông dân','🐑')">
    <div class="set-ico">🌱</div>
    <div class="set-name">Nông dân</div>
    <div class="set-desc">Bộ gốc — thoải mái, thân thiện</div>
    <div class="set-cost"><span class="cost-free">Miễn phí</span></div>
    <button class="set-btn set-wearing">✓ Đang mặc</button>
  </div>

  <div class="set-card" onclick="wearSet(this,'🎓 Bộ Học sinh','🐑')">
    <span class="badge-pop">HOT</span>
    <div class="set-ico">🎓</div>
    <div class="set-name">Học sinh</div>
    <div class="set-desc">Cừu học giỏi, streak 30 ngày</div>
    <div class="set-cost"><span class="cost-free">Đã mở khóa</span></div>
    <button class="set-btn set-equip">Mặc ngay</button>
  </div>

  <div class="set-card" onclick="wearSet(this,'✈️ Bộ Du lịch','🐑')">
    <span class="badge-new">MỚI</span>
    <div class="set-ico">✈️</div>
    <div class="set-name">Du lịch</div>
    <div class="set-desc">Cho hội mê phượt và khám phá</div>
    <div class="set-cost"><span class="cost-ix">💛 200 iXu</span></div>
    <button class="set-btn set-buy" onclick="event.stopPropagation();buySet('Du lịch',200)">Mua ngay</button>
  </div>

  <div class="set-card">
    <div class="set-ico">🚀</div>
    <div class="set-name">Phi hành gia</div>
    <div class="set-desc">Giấc mơ bay cao không giới hạn</div>
    <div class="set-cost"><span class="cost-ix">💛 350 iXu</span></div>
    <button class="set-btn set-buy" onclick="buySet('Phi hành gia',350)">Mua ngay</button>
  </div>

  <div class="set-card">
    <div class="set-ico">👑</div>
    <div class="set-name">Hoàng gia</div>
    <div class="set-desc">Chỉ dành cho Lv.5 trở lên</div>
    <div class="set-cost"><span class="cost-lock">🔒 Lv.5</span></div>
    <button class="set-btn set-locked" disabled>Chưa mở được</button>
  </div>

  <div class="set-card">
    <div class="set-ico">💎</div>
    <div class="set-name">Diamond</div>
    <div class="set-desc">Hiếm nhất — mời 10 bạn để mở</div>
    <div class="set-cost"><span class="cost-lock">🔒 Mời 10 bạn</span></div>
    <button class="set-btn set-locked" disabled>Chưa mở được</button>
  </div>

</div>

<!-- INDIVIDUAL ITEMS -->
<div class="sec-hd">🎩 Vật phẩm đơn lẻ</div>
<div class="items-grid">
  <div class="item on" onclick="toggleItem(this,'Mũ rơm')">
    <div class="item-ico">👒</div>
    <div class="item-name">Mũ rơm</div>
  </div>
  <div class="item on" onclick="toggleItem(this,'Balo Xuân')">
    <div class="item-ico">🎒</div>
    <div class="item-name">Balo Xuân</div>
  </div>
  <div class="item" onclick="toggleItem(this,'Kính râm')">
    <div class="item-ico">😎</div>
    <div class="item-name">Kính râm</div>
  </div>
  <div class="item" onclick="toggleItem(this,'Vương miện')">
    <div class="item-ico">👑</div>
    <div class="item-name">Vương miện</div>
    <span class="item-lock">🔒</span>
  </div>
  <div class="item" onclick="toggleItem(this,'Nơ hồng')">
    <div class="item-ico">🎀</div>
    <div class="item-name">Nơ hồng</div>
  </div>
  <div class="item" onclick="toggleItem(this,'Mũ sinh nhật')">
    <div class="item-ico">🎂</div>
    <div class="item-name">Sinh nhật</div>
  </div>
  <div class="item" onclick="toggleItem(this,'Kính phi công')">
    <div class="item-ico">🥽</div>
    <div class="item-name">Kính phi công</div>
    <span class="item-lock">🔒</span>
  </div>
  <div class="item" onclick="toggleItem(this,'Khăn quàng')">
    <div class="item-ico">🧣</div>
    <div class="item-name">Khăn quàng</div>
  </div>
</div>

<script>
var currentSet='🌱 Bộ Nông dân';
function toast(msg){
  var t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');
  clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('on');},2600);
}
function setCat(btn,cat){
  document.querySelectorAll('.cat').forEach(function(b){b.classList.remove('on');});
  btn.classList.add('on');
  toast('Đang lọc: '+btn.textContent.trim());
}
function wearSet(card,name,sheep){
  if(card.querySelector('.set-btn.set-locked')) return;
  document.querySelectorAll('.set-card').forEach(function(c){c.classList.remove('active');});
  document.querySelectorAll('.set-btn.set-wearing').forEach(function(b){
    b.className='set-btn set-equip';b.textContent='Mặc ngay';
  });
  card.classList.add('active');
  var btn=card.querySelector('.set-btn');
  btn.className='set-btn set-wearing';btn.textContent='✓ Đang mặc';
  document.getElementById('activeSet').textContent='Đang mặc: '+name;
  toast('✨ Đã mặc '+name+'!');
}
function buySet(name,cost){
  toast('💛 Đã mua bộ '+name+' (–'+cost+' iXu)!');
}
function toggleItem(el,name){
  if(el.querySelector('.item-lock')){toast('🔒 Chưa mở khóa vật phẩm này!');return;}
  el.classList.toggle('on');
  toast(el.classList.contains('on')?'✓ Đã trang bị '+name:'Đã bỏ '+name);
}
</script></body></html>"""
        _comp3.html(_HTML_T4, height=2100, scrolling=True)
