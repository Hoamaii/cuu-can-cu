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
    # ── v4 Architecture Fields ──────────────────────────
    "goals":              [],       # [{name, target_date, done}]
    "journey_timeline":   [],       # [{date, icon, title, body}]
    "knowledge_graph":    {},       # {entity: [related_entity,...]}
    "research_cache":     {},       # {dream_key: [insight_dict,...]}
    "last_research_date": "",
    "behavior_metrics":   {
        "feed_days":      [],       # list of YYYY-MM-DD
        "chat_days":      [],
        "diary_days":     [],
        "engagement":     0,
        "churn_risk":     0,
        "attachment":     0,
    },
    "family_members":     [],       # [{role, name, exp, level, saved}]
    "family_code":        "",
    "wardrobe":           [],       # list of unlocked item strings
    "house":              "",
    "energy":             100,
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
# AI LAYER 2 — KNOWLEDGE GRAPH
# ═══════════════════════════════════════════════════════
def _build_knowledge_graph(_mem: dict) -> dict:
    """Build entity→connections map from mem (dreams, events, notes)."""
    graph: dict = {}

    def _add(src: str, *targets):
        graph.setdefault(src, [])
        for t in targets:
            if t not in graph[src]:
                graph[src].append(t)

    for d in _mem.get("dreams", []):
        n = d.get("name","").lower().strip()
        if n:
            _add(n, "tích_lũy", "đầu_tư")
            _add("tích_lũy", n)

    tag_conn = {
        "dream_travel":   ["du_lịch","tích_lũy"],
        "dream_house":    ["bất_động_sản","tích_lũy"],
        "dream_car":      ["xe_hơi","tích_lũy"],
        "dream_business": ["khởi_nghiệp","tích_lũy"],
        "career":         ["sự_nghiệp","thu_nhập"],
        "cashflow":       ["tiết_kiệm","tích_lũy"],
        "family":         ["gia_đình","bảo_vệ"],
    }
    for tag in _mem.get("life_events", []):
        for conn in tag_conn.get(tag, []):
            _add(tag, conn)

    _mem["knowledge_graph"] = graph
    return graph


# ═══════════════════════════════════════════════════════
# AI LAYER 3 — DEEP RESEARCH ENGINE
# ═══════════════════════════════════════════════════════
_RESEARCH_DB: dict = {
    "nhật": [
        {"icon":"🗾","title":"Nhật Bản đang gần hơn",
         "body":"Vé mùa lá đỏ (tháng 11) đang được săn nhiều trên TikTok. Giá round-trip từ HN ~6.2tr.",
         "cta":"Tích lũy thêm 50k/ngày = đủ vé sau 4 tháng 🐑"},
        {"icon":"🍜","title":"Chi phí sống ở Nhật 2025",
         "body":"Reddit r/VietNam: 7-10 ngày Nhật tốn khoảng 25-35tr. DCA đều đặn là cách nhiều bạn đang làm.",
         "cta":"Cừu giúp bạn tính kế hoạch tích lũy nhé!"},
    ],
    "xe": [
        {"icon":"🚗","title":"Xu hướng xe điện 2025",
         "body":"VinFast VF3 giá từ 235tr — nhiều bạn trẻ đang chuyển dần. TikTok trend #muaxelan1.",
         "cta":"DCA 1tr/tháng = 20 tháng đủ cọc 🐑"},
        {"icon":"🔋","title":"Chi phí vận hành xe điện",
         "body":"Tiết kiệm 60-70% so với xe xăng. Google Trends: 'xe điện giá rẻ' tăng 3x trong 6 tháng.",
         "cta":"Cừu tính giúp: cần tích lũy bao lâu?"},
    ],
    "nhà": [
        {"icon":"🏠","title":"Xu hướng chung cư 2025",
         "body":"Hà Nội: chung cư tầm 2-3 tỷ đang được săn. Lãi suất vay đang ở mức tốt.",
         "cta":"Tích lũy đều đặn = vốn tự có + điều kiện vay tốt 🐑"},
        {"icon":"🏡","title":"Thuê hay mua?",
         "body":"Reddit VN hot thread: 'Mua nhà hay tiếp tục thuê?' — 68% chọn tích lũy DCA trước.",
         "cta":"Cừu giúp bạn lên kế hoạch vốn tự có!"},
    ],
    "du_lịch": [
        {"icon":"✈️","title":"Mùa du lịch hè 2025",
         "body":"Google Trends: tìm kiếm 'vé máy bay' tăng 2.3x. Đặt sớm rẻ hơn 35%.",
         "cta":"Tích lũy ngay hôm nay để có chuyến đi trong mơ 🐑"},
    ],
    "tự_do": [
        {"icon":"💰","title":"FIRE movement ở Việt Nam",
         "body":"TikTok #tự_do_tài_chính đạt 45M views. Nhiều bạn 9x đang mục tiêu FIRE trước 45 tuổi.",
         "cta":"Mỗi ngày cho Cừu ăn = một bước gần tự do hơn 🐑"},
    ],
    "học": [
        {"icon":"🎓","title":"Chi phí học thêm 2025",
         "body":"Khóa online chất lượng từ 500k-3tr. Đầu tư vào bản thân = ROI cao nhất.",
         "cta":"Tích lũy cho giáo dục — Cừu giúp bạn lên kế hoạch!"},
    ],
    "default": [
        {"icon":"📈","title":"Thói quen DCA của người thành công",
         "body":"Nghiên cứu: đầu tư đều đặn mỗi tháng hiệu quả hơn 73% so với chờ 'thời điểm vàng'.",
         "cta":"Cho Cừu ăn hôm nay — dù chỉ 10k cũng có ý nghĩa 🐑"},
        {"icon":"🌱","title":"Quy tắc 1% mỗi ngày",
         "body":"Cải thiện 1% mỗi ngày = 37 lần tốt hơn sau 1 năm. Tích lũy nhỏ → thay đổi lớn.",
         "cta":"Bắt đầu từ bó cỏ 10k hôm nay nhé!"},
        {"icon":"💡","title":"Lạm phát và sức mua",
         "body":"Lạm phát VN ~3.5%/năm. Tiền để yên = mất giá. Đầu tư đều = bảo vệ sức mua.",
         "cta":"Cừu giúp bạn hiểu đơn giản hơn 🐑"},
    ],
}


def _get_research_insights(_mem: dict) -> list:
    """Return list of (icon, title, body, cta) tuples personalized to user's dreams."""
    results = []
    seen_keys: set = set()

    for d in _mem.get("dreams", [])[:3]:
        name = d.get("name","").lower()
        for kw, items in _RESEARCH_DB.items():
            if kw == "default":
                continue
            if kw in name and kw not in seen_keys:
                seen_keys.add(kw)
                results += items[:2]

    if not results:
        results = _RESEARCH_DB["default"]

    return results[:6]


# ═══════════════════════════════════════════════════════
# AI LAYER 4 — BEHAVIOR PREDICTION
# ═══════════════════════════════════════════════════════
def _update_behavior_metrics(_mem: dict) -> dict:
    """Recompute engagement, churn_risk, attachment from mem data."""
    import datetime as _dt2
    bm = _mem.setdefault("behavior_metrics", {
        "feed_days":[], "chat_days":[], "diary_days":[],
        "engagement":0, "churn_risk":0, "attachment":0
    })

    today_str = _dt2.date.today().isoformat()
    last_visit = _mem.get("last_visit_date","")
    try:
        days_absent = (_dt2.date.today() -
                       _dt2.date.fromisoformat(last_visit)).days if last_visit else 999
    except Exception:
        days_absent = 30

    # Count active days (last 30)
    q = _mem.get("daily_quests", {})
    recent_days = 0
    feed_count  = 0
    for dstr, dq in q.items():
        try:
            age = (_dt2.date.today() - _dt2.date.fromisoformat(dstr)).days
            if age <= 30:
                recent_days += 1
                if dq.get("feed"): feed_count += 1
        except Exception:
            pass

    streak = _mem.get("streak", 0)
    n_dreams   = len(_mem.get("dreams", []))
    n_events   = len(_mem.get("life_events", []))
    n_diary    = len(_mem.get("diary_entries", []))
    n_notes    = len(_mem.get("notes", []))
    n_msgs     = len(st.session_state.get("messages", []))

    # Engagement: 0-100
    eng = min(100, int(
        recent_days * 2 +
        streak * 1.5 +
        feed_count * 1 +
        min(n_diary, 10) * 2 +
        min(n_msgs, 30) * 0.5
    ))

    # Churn risk: 0-100 (higher = more likely to churn)
    churn = max(0, min(100, int(
        days_absent * 8 +
        (30 - min(recent_days, 30)) * 1.5 -
        eng * 0.5
    )))

    # Attachment: 0-100 (emotional investment)
    att = min(100, int(
        n_dreams * 10 +
        n_events * 3 +
        n_diary * 4 +
        n_notes * 2 +
        min(streak, 30) * 2
    ))

    bm["engagement"]  = eng
    bm["churn_risk"]  = churn
    bm["attachment"]  = att
    _mem["behavior_metrics"] = bm
    return bm


# ═══════════════════════════════════════════════════════
# HOUSE PROGRESSION
# ═══════════════════════════════════════════════════════
def _get_house(level: int) -> tuple:
    """Return (emoji, name, desc) for current level house."""
    houses = {
        1: ("🏕️", "Lều Nhỏ",     "Cừu đang nằm dưới trời sao..."),
        2: ("🛖", "Chòi Gỗ",     "Có mái che rồi! Ấm hơn rồi~"),
        3: ("🏠", "Nhà Gỗ",      "Nhà xinh xắn giữa đồng cỏ xanh"),
        4: ("🏡", "Biệt Thự Nhỏ","Sân vườn có hoa, Cừu rất thích!"),
        5: ("🏰", "Lâu Đài Cừu", "Vương quốc của Cừu — hoành tráng!"),
        6: ("✨🏰","Lâu Đài Huyền Thoại","Đỉnh cao của hành trình!"),
    }
    return houses.get(level, houses[1])


def _get_energy(_mem: dict) -> tuple:
    """Return (pct, state, msg) for energy bar."""
    streak = _mem.get("streak", 0)
    n_quests = sum(1 for dq in _mem.get("daily_quests",{}).values()
                   for k,v in dq.items() if k!="bonus_claimed" and v)
    pct = min(100, 20 + streak * 5 + n_quests * 2)
    if pct >= 80: return pct, "high",   "⚡ Năng lượng dồi dào!"
    if pct >= 50: return pct, "medium", "🌿 Năng lượng ổn định"
    if pct >= 20: return pct, "low",    "😴 Hơi mệt, cho Cừu ăn thêm nhé"
    return pct,   "empty",  "😪 Cừu cần bạn..."


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
tab1, tab2, tab3, tab4 = st.tabs([
    "🐑 Cừu của tôi",
    "💬 Hành Trình",
    "🧠 Nghiên Cứu",
    "👨\u200d👩\u200d👧 Gia Đình",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — 🐑 CỪU CỦA TÔI  (Pure Tamagotchi / Finch / Duolingo experience)
# NO chat. NO research. NO news.
# = Avatar · Mood · Hunger · Energy · Quest · Level · iLucky · Ach · Wardrobe · House
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    import random as _r1

    # ── 0. Init state ────────────────────────────────────────────────────────
    _t1_today = datetime.now().strftime("%Y-%m-%d")
    _t1_q, _t1_key = _get_today_q(mem)
    if not _t1_q.get("visit"):
        _complete_quest(mem, "visit", 10)
        _save()

    _t1_days, _t1_re, _t1_rt, _t1_rb = _return_msg(mem, _t1_today)
    if _t1_days >= 1:
        mem["last_visit_date"] = _t1_today
        _save()

    total_saved   = mem.get("total_saved", 0)
    _t1_sk, _t1_sn, _t1_slv, _t1_sd, _ = get_growth_stage(total_saved)
    _t1_exp       = mem.get("user_exp", 0)
    _t1_lv        = get_exp_level(_t1_exp)
    _t1_in, _t1_nd, _t1_pct = exp_progress(_t1_exp)
    _t1_tix       = mem.get("ilucky_tickets", 0)
    _t1_hpct, _t1_hs, _t1_hm = _get_hunger(mem)
    _t1_epct, _t1_es, _t1_em = _get_energy(mem)
    _t1_qdata     = mem.get("daily_quests",{}).get(_t1_today,{})
    _t1_qdone     = sum(1 for k in ("visit","chat","diary","feed") if _t1_qdata.get(k))
    _t1_qall      = _t1_qdone == 4
    _t1_qbonus    = _t1_qdata.get("bonus_claimed", False)
    _t1_earned    = set(mem.get("achievements",[]))
    _t1_uname     = mem.get("name","bạn")
    _t1_nlv       = min(_t1_lv + 1, 6)
    _t1_nlv_tix   = LEVEL_ILUCKY.get(_t1_nlv, 0)
    _t1_nlv_items = LEVEL_ITEMS.get(_t1_nlv, [])
    _t1_house_ico, _t1_house_name, _t1_house_desc = _get_house(_t1_lv)

    # ── CSS ──────────────────────────────────────────────────────────────────
    st.markdown("""<style>
    .t1-sec{font-size:.76rem;font-weight:800;color:#7B5EA7;text-transform:uppercase;
            letter-spacing:.08em;margin:20px 0 10px;display:flex;align-items:center;gap:8px;}
    .t1-sec::before{content:'';display:block;width:3px;height:14px;
                    background:linear-gradient(180deg,#7B5EA7,#C4607F);border-radius:3px;}
    .t1-card{background:#fff;border:1.5px solid #f0e8ff;border-radius:20px;
             padding:16px 18px;margin-bottom:12px;}
    .t1-bar-bg{background:#f0f0f7;border-radius:10px;height:11px;overflow:hidden;margin:4px 0;}
    .t1-bar-fill{height:100%;border-radius:10px;}
    .t1-lv-pill{display:inline-flex;align-items:center;gap:5px;
                background:linear-gradient(135deg,#7B5EA7,#C4607F);
                color:#fff;border-radius:22px;padding:5px 16px;
                font-size:.8rem;font-weight:800;}
    .t1-gold{display:inline-flex;align-items:center;gap:5px;
             background:linear-gradient(135deg,#FFD700,#FFA500);
             color:#1a1a2e;border-radius:22px;padding:5px 16px;font-size:.8rem;font-weight:800;}
    .t1-quest-row{display:flex;align-items:center;gap:10px;padding:10px 14px;
                  border-radius:13px;margin-bottom:6px;border:1.5px solid;}
    .t1-q-done{background:#f0fff4;border-color:#b8f0c8;}
    .t1-q-todo{background:#fafafa;border-color:#ede8ff;}
    .t1-ach{border-radius:15px;padding:12px 8px;text-align:center;border:1.5px solid;}
    .t1-ach-got{background:#f4eeff;border-color:#d4b8ff;}
    .t1-ach-no{background:#f8f8f8;border-color:#e8e8e8;opacity:.48;}
    .t1-shop-item{border-radius:14px;padding:10px 6px;text-align:center;
                  border:2px solid;margin-bottom:6px;}
    .t1-item-on{background:#f4eeff;border-color:#d4b8ff;}
    .t1-item-off{background:#f8f8f8;border-color:#e0e0e0;opacity:.45;}
    .t1-feed-sub{font-size:.67rem;color:#7B5EA7;font-style:italic;text-align:center;margin-top:2px;}
    </style>""", unsafe_allow_html=True)

    # ── 1. Return banner + level-up ─────────────────────────────────────────
    if _t1_days >= 1 and _t1_rt:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1A1A2E,#2D1B69);'
            f'border-radius:18px;padding:16px 20px;margin-bottom:12px;text-align:center;">'
            f'<div style="font-size:1.8rem;">{_t1_re}</div>'
            f'<div style="font-size:1rem;font-weight:800;color:#fff;margin:5px 0 3px;">{_t1_rt}</div>'
            f'<div style="font-size:.82rem;color:rgba(255,255,255,.75);">{_t1_rb}</div>'
            f'</div>', unsafe_allow_html=True)

    if mem.get("just_leveled_up"):
        _nl = mem.get("new_level_name", LEVEL_NAMES.get(_t1_lv,""))
        _nt = mem.get("new_level_tickets", 0)
        st.balloons()
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFD700,#FFA500,#FF6B35);'
            f'border-radius:20px;padding:20px;text-align:center;margin-bottom:12px;">'
            f'<div style="font-size:2rem;">🎉</div>'
            f'<div style="font-size:1.2rem;font-weight:800;color:#1a1a2e;">LEVEL UP! {_nl}</div>'
            f'<div style="background:rgba(0,0,0,.12);border-radius:12px;'
            f'padding:8px 14px;display:inline-block;margin-top:10px;">'
            f'🎟️ <strong style="color:#1a1a2e;">+{_nt} Vé iLucky</strong></div>'
            f'</div>', unsafe_allow_html=True)
        mem["just_leveled_up"] = False
        mem["new_level_name"]  = ""
        mem["new_level_tickets"] = 0
        _save()

    if mem.get("market_mood","normal") == "down":
        st.markdown(
            '<div style="background:linear-gradient(135deg,#e8f0ff,#f0f8ff);'
            'border-left:4px solid #7B9ED9;border-radius:14px;padding:12px 16px;margin-bottom:10px;">'
            '<div style="font-size:.86rem;font-weight:700;color:#3a5f9a;">🌧️ Đồng cỏ hơi có mưa hôm nay.</div>'
            '<div style="font-size:.8rem;color:#5a7aaa;margin-top:3px;">'
            '🐑 Nhưng mình vẫn ở đây — hành trình không dừng lại vì mưa đâu nhé.</div>'
            '</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION A: 🐑 AVATAR + BARS + FEED
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="t1-sec">🐑 Cừu của tôi</div>', unsafe_allow_html=True)

    _col_av, _col_stats = st.columns([1, 1.5])

    with _col_av:
        show_growth_sheep(total_saved, width=180)

        # House
        st.markdown(
            f'<div style="text-align:center;margin:10px 0;">'
            f'<div style="font-size:2rem;">{_t1_house_ico}</div>'
            f'<div style="font-size:.72rem;font-weight:700;color:#5a3d9a;">{_t1_house_name}</div>'
            f'<div style="font-size:.62rem;color:#aaa;">{_t1_house_desc}</div>'
            f'</div>', unsafe_allow_html=True)

    with _col_stats:
        # Sheep voice
        _voices = {
            "baby":  f'"Bê bê~ Cho mình ăn để lớn nhanh nhé {_t1_uname}!"',
            "child": f'"Mình lớn hơn rồi! Hôm nay cho mình ăn tiếp không?"',
            "teen":  f'"Mình đang lớn nhanh lắm~ Cùng nhau đến đích thôi!"',
            "adult": f'"Cảm ơn {_t1_uname} đã kiên trì đến đây ❤️"',
            "master":f'"Chúng mình đã đi một chặng đường dài! 🏆"',
        }
        _food_ico = {"baby":"🥬","child":"🥕","teen":"🍎","adult":"🎂","master":"🎉"}.get(_t1_sk,"🌿")
        st.markdown(
            f'<div class="t1-card" style="padding:12px 14px;margin-bottom:8px;">'
            f'<div style="font-size:1.5rem;text-align:center;">{_food_ico}</div>'
            f'<div style="font-size:.86rem;color:#C4607F;font-style:italic;'
            f'text-align:center;margin-top:5px;line-height:1.55;">'
            f'{_voices.get(_t1_sk,_voices["baby"])}</div>'
            f'</div>', unsafe_allow_html=True)

        # Bars: Hunger / Mood / Energy
        _hcol = {"ok":"#7B5EA7","hungry":"#FFA500","miss_you":"#FF6B35","lonely":"#E53935","fed":"#2a9d5c"}.get(_t1_hs,"#7B5EA7")
        _ecol = {"high":"#2a9d5c","medium":"#7B5EA7","low":"#FFA500","empty":"#E53935"}.get(_t1_es,"#7B5EA7")
        _mood_now = mem.get("mood","happy")
        _mmap  = {"happy":("#FF6B9D","100"),"sad":("#7B9ED9","40"),
                  "celebrate":("#FFD700","100"),"listening":("#9B5EA7","75"),
                  "default":("#FF8FAF","80")}
        _mcol, _mpct = _mmap.get(_mood_now, _mmap["default"])

        _bars_html = (
            f'<div class="t1-card" style="padding:12px 14px;">'
            f'<div style="margin-bottom:10px;">'
            f'<div style="display:flex;justify-content:space-between;font-size:.69rem;color:#888;">'
            f'<span>🍽️ Độ no</span>'
            f'<span style="color:{_hcol};font-weight:700;">{_t1_hpct}%</span></div>'
            f'<div class="t1-bar-bg"><div class="t1-bar-fill" style="width:{_t1_hpct}%;background:{_hcol};"></div></div>'
            f'<div style="font-size:.63rem;color:{_hcol};margin-top:1px;">{_t1_hm}</div>'
            f'</div>'
            f'<div style="margin-bottom:10px;">'
            f'<div style="display:flex;justify-content:space-between;font-size:.69rem;color:#888;">'
            f'<span>❤️ Tâm trạng</span></div>'
            f'<div class="t1-bar-bg"><div class="t1-bar-fill" style="width:{_mpct}%;background:{_mcol};"></div></div>'
            f'</div>'
            f'<div>'
            f'<div style="display:flex;justify-content:space-between;font-size:.69rem;color:#888;">'
            f'<span>⚡ Năng lượng</span>'
            f'<span style="color:{_ecol};font-weight:700;">{_t1_epct}%</span></div>'
            f'<div class="t1-bar-bg"><div class="t1-bar-fill" style="width:{_t1_epct}%;background:{_ecol};"></div></div>'
            f'<div style="font-size:.63rem;color:{_ecol};margin-top:1px;">{_t1_em}</div>'
            f'</div></div>'
        )
        st.markdown(_bars_html, unsafe_allow_html=True)

        # Feed buttons
        st.markdown(
            '<div style="font-size:.83rem;font-weight:700;color:#C4607F;margin:8px 0 5px;">'
            '🍽️ Cho Cừu ăn</div>', unsafe_allow_html=True)
        _FOOD_T = {
            "🥬 Bó Cỏ":"10k","🥕 Cà Rốt":"20k","🍎 Táo":"50k",
            "🎂 Tiệc Sinh Nhật":"100k","🎉 Đại Tiệc":"500k"
        }
        _fcols = st.columns(len(FEED_OPTIONS))
        for _fi, (_fa, _fe, _fn) in enumerate(FEED_OPTIONS):
            _fl = f"{_fe} {_fn}"
            if _fcols[_fi].button(f"{_fe}\n{_fn}", use_container_width=True, key=f"t1f_{_fa}", type="primary"):
                _pk = _t1_sk
                mem["total_saved"]    += _fa
                mem["streak"]         += 1
                mem["last_fed_amount"] = _fa
                mem["last_fed_food"]   = _fl
                mem["last_fed_date"]   = _t1_today
                _nk, *_ = get_growth_stage(mem["total_saved"])
                if _nk != _pk:
                    mem["just_leveled_up"] = True
                _complete_quest(mem, "feed", 30)
                _add_exp(30, mem)
                _check_achievements(mem)
                _update_behavior_metrics(mem)
                set_mood("happy")
                st.session_state.feeding_celebration = True
                st.session_state.feeding_refused     = False
                # Add to journey timeline
                mem.setdefault("journey_timeline",[]).append({
                    "date": _t1_today, "icon": _fe,
                    "title": f"Cho Cừu ăn {_fl}",
                    "body":  f"Tích lũy {fmt(_fa)} hôm nay"
                })
                _save()
                st.rerun()
            _fcols[_fi].markdown(f'<div class="t1-feed-sub">{_FOOD_T.get(_fl,"")}</div>', unsafe_allow_html=True)

        if st.session_state.get("feeding_celebration"):
            _food_msg = {
                "🥬 Bó Cỏ":"🐑 Cừu vừa được ăn bó cỏ!",
                "🥕 Cà Rốt":"🐑 Ngon lắm! Cà rốt tươi~",
                "🍎 Táo":"🐑 Cừu thích táo lắm!",
                "🎂 Tiệc Sinh Nhật":"🐑 Tiệc cho Cừu! Bê bê~",
                "🎉 Đại Tiệc":"🐑 Đại tiệc! Hạnh phúc nhất đàn!",
            }.get(mem.get("last_fed_food",""), "🐑 Cừu cảm ơn bạn!")
            st.success(f"{_food_msg} +30 EXP 🎊")
            st.session_state.feeding_celebration = False
            st.balloons()

        if st.session_state.get("feeding_refused"):
            st.info("🌙 Không sao. Mình vẫn ở đây khi bạn sẵn sàng~")
            st.session_state.feeding_refused = False

        if st.button("🌙 Hôm nay chưa sẵn sàng", use_container_width=True, key="t1_skip"):
            set_mood("sad")
            st.session_state.feeding_refused = True
            st.session_state.feeding_celebration = False
            _save()
            st.rerun()

    # ══════════════════════════════════════════════════════
    # SECTION B: 🎯 DAILY QUEST
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="t1-sec">🎯 Nhiệm vụ hôm nay</div>', unsafe_allow_html=True)

    _T1_QUESTS = [
        ("visit","👁️ Ghé thăm Cừu",       10,"Đã ghé thăm ✓"),
        ("chat", "💬 Trò chuyện với Cừu",  10,"Đã trò chuyện ✓"),
        ("diary","📔 Viết nhật ký",         20,"Đã viết nhật ký ✓"),
        ("feed", "🍽️ Cho Cừu ăn",          30,"Đã cho ăn ✓"),
    ]
    _qrows = ""
    for _qk, _ql, _qe, _qd in _T1_QUESTS:
        _done = _t1_qdata.get(_qk, False)
        _cls  = "t1-q-done" if _done else "t1-q-todo"
        _ico  = "✅" if _done else "⬜"
        _lbl  = _qd if _done else _ql
        _exp_span = "" if _done else f'<span style="margin-left:auto;font-size:.63rem;font-weight:800;color:#7B5EA7;background:#f0eaff;border-radius:8px;padding:2px 7px;">+{_qe} EXP</span>'
        _qrows += (
            f'<div class="t1-quest-row {_cls}">'
            f'<span style="font-size:1.05rem;">{_ico}</span>'
            f'<span style="font-size:.82rem;font-weight:{"700" if _done else "500"};'
            f'color:{"#2a9d5c" if _done else "#333"};">{_lbl}</span>'
            f'{_exp_span}</div>'
        )
    _qprog   = int(_t1_qdone / 4 * 100)
    _qpcol   = "#2a9d5c" if _t1_qall else "#7B5EA7"
    st.markdown(
        f'<div class="t1-card">{_qrows}'
        f'<div style="margin-top:10px;">'
        f'<div style="display:flex;justify-content:space-between;font-size:.68rem;color:#888;margin-bottom:3px;">'
        f'<span>Hôm nay</span>'
        f'<span style="color:{_qpcol};font-weight:700;">{_t1_qdone}/4 · {_qprog}%</span></div>'
        f'<div style="background:#f0f0f7;border-radius:8px;height:8px;overflow:hidden;">'
        f'<div style="width:{_qprog}%;height:100%;border-radius:8px;background:{_qpcol};"></div></div>'
        f'</div></div>', unsafe_allow_html=True)

    if _t1_qall and not _t1_qbonus:
        if st.button("🎁 Nhận +50 EXP thưởng hoàn thành tất cả!", type="primary",
                     use_container_width=True, key="t1_bonus"):
            _complete_quest(mem, "bonus_claimed", 50)
            mem["daily_quests"][_t1_today]["bonus_claimed"] = True
            _save()
            st.rerun()
    elif _t1_qall and _t1_qbonus:
        st.markdown(
            '<div style="background:#f0fff4;border:1.5px solid #b8f0c8;border-radius:14px;'
            'padding:10px;text-align:center;margin-top:-6px;">'
            '<strong style="font-size:.84rem;color:#2a9d5c;">🎉 Hoàn thành xuất sắc! +50 EXP đã nhận</strong>'
            '</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION C: ⭐ LEVEL + EXP
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="t1-sec">⭐ Level & EXP</div>', unsafe_allow_html=True)

    _lv_name = LEVEL_NAMES.get(_t1_lv, f"Level {_t1_lv}")
    _nxt_txt = " · ".join(_t1_nlv_items[:2]) if _t1_nlv_items else "Đã max level!"
    st.markdown(
        f'<div class="t1-card" style="padding:18px 20px;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<span class="t1-lv-pill">Lv.{_t1_lv} · {_lv_name}</span>'
        f'<span style="font-size:.72rem;color:#888;">{_t1_in:,} / {_t1_nd:,} EXP</span>'
        f'</div>'
        f'<div class="t1-bar-bg" style="height:14px;">'
        f'<div class="t1-bar-fill" style="width:{_t1_pct:.1f}%;'
        f'background:linear-gradient(90deg,#7B5EA7,#C4607F,#FFD700);"></div></div>'
        f'<div style="display:flex;justify-content:space-between;margin-top:7px;">'
        f'<span style="font-size:.68rem;color:#aaa;">Còn {max(0,_t1_nd-_t1_in):,} EXP → Lv.{_t1_nlv}</span>'
        f'<span style="font-size:.68rem;color:#C4607F;font-weight:700;">{_t1_pct:.0f}%</span></div>'
        f'<div style="margin-top:10px;background:#faf6ff;border-radius:10px;padding:8px 12px;">'
        f'<span style="font-size:.7rem;color:#9b7ed9;font-weight:700;">🎁 Lv.{_t1_nlv}: </span>'
        f'<span style="font-size:.74rem;color:#5a3d9a;font-weight:600;">'
        f'🎟️ {_t1_nlv_tix} vé · {_nxt_txt}</span>'
        f'</div></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION D: 🎟️ ILUCKY TICKETS
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="t1-sec">🎟️ Vé iLucky</div>', unsafe_allow_html=True)

    _il1, _il2 = st.columns([1.2, 1])
    with _il1:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1A1A2E,#2D1B69);'
            f'border-radius:18px;padding:16px 20px;">'
            f'<div style="font-size:.68rem;color:#c4a8ff;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;">Hiện có</div>'
            f'<div style="display:flex;align-items:baseline;gap:8px;">'
            f'<span style="font-size:2.6rem;font-weight:800;color:#FFD700;">{_t1_tix}</span>'
            f'<span style="font-size:.9rem;color:rgba(255,255,255,.65);">vé</span></div>'
            f'<span class="t1-gold" style="margin-top:10px;display:inline-flex;">🎟️ iLucky</span>'
            f'</div>', unsafe_allow_html=True)
    with _il2:
        _unlocked = []
        for _li in range(2, _t1_lv + 1):
            _unlocked += LEVEL_ITEMS.get(_li,[])
        st.markdown(
            f'<div style="background:#fff8f0;border:1.5px solid #FFD6C8;'
            f'border-radius:18px;padding:14px 15px;">'
            f'<div style="font-size:.68rem;color:#C4607F;font-weight:700;margin-bottom:7px;">🎁 Đã mở khóa</div>',
            unsafe_allow_html=True)
        if _unlocked:
            for _it in _unlocked[:4]:
                st.markdown(
                    f'<span style="display:inline-flex;align-items:center;gap:4px;'
                    f'background:#f4eeff;border:1.5px solid #d4b8ff;border-radius:18px;'
                    f'padding:3px 10px;font-size:.7rem;font-weight:700;color:#5a3d9a;margin:2px;">{_it}</span>',
                    unsafe_allow_html=True)
        else:
            st.markdown('<span style="font-size:.76rem;color:#aaa;">Lên Lv.2 để mở khóa</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION E: 🏆 THÀNH TÍCH
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="t1-sec">🏆 Thành tích</div>', unsafe_allow_html=True)

    _ach_cls = st.columns(4)
    for _ai, (_ak, _an, _ad) in enumerate(ACHIEVEMENTS_DEF):
        _got  = _ak in _t1_earned
        _cls  = "t1-ach t1-ach-got" if _got else "t1-ach t1-ach-no"
        _apts = _an.split()
        _abg  = '<div style="font-size:.58rem;color:#2a9d5c;font-weight:700;margin-top:4px;">✅ Đạt</div>' if _got else ''
        with _ach_cls[_ai % 4]:
            st.markdown(
                f'<div class="{_cls}">'
                f'<div style="font-size:1.4rem;">{_apts[0]}</div>'
                f'<div style="font-size:.7rem;font-weight:700;'
                f'color:{"#5a3d9a" if _got else "#aaa"};margin-top:3px;">{" ".join(_apts[1:])}</div>'
                f'<div style="font-size:.6rem;color:{"#888" if _got else "#ccc"};margin-top:2px;">{_ad}</div>'
                f'{_abg}</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION F: 🐑 TỦ ĐỒ + NHÀ
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="t1-sec">🎪 Tủ Đồ & Nhà Cừu</div>', unsafe_allow_html=True)

    _WARDROBE = [
        (1,"🐑","Lông Tự Nhiên","Mặc định"),
        (2,"🎩","Mũ Sinh Viên","Lv.2"),
        (3,"👔","Vest Xanh TCBS","Lv.3"),
        (3,"🎒","Balo","Lv.3"),
        (4,"⌚","Đồng Hồ","Lv.4"),
        (5,"🚗","Xe Mini","Lv.5"),
        (6,"👑","Vương Miện","Lv.6"),
    ]
    _HOUSES = [
        (1,"🏕️","Lều Nhỏ"),(2,"🛖","Chòi Gỗ"),(3,"🏠","Nhà Gỗ"),
        (4,"🏡","Biệt Thự"),(5,"🏰","Lâu Đài"),(6,"✨🏰","Huyền Thoại"),
    ]
    _wd_col, _h_col = st.columns(2)
    with _wd_col:
        st.markdown(
            '<div style="font-size:.72rem;font-weight:700;color:#C4607F;margin-bottom:7px;">👗 Trang phục</div>',
            unsafe_allow_html=True)
        _wdcols = st.columns(4)
        for _wi, (_wlv, _wico, _wnm, _wsub) in enumerate(_WARDROBE):
            _won = _t1_lv >= _wlv
            _wcls = "t1-shop-item t1-item-on" if _won else "t1-shop-item t1-item-off"
            _wbg  = '<div style="font-size:.55rem;color:#2a9d5c;font-weight:700;">✅</div>' if _won else ''
            with _wdcols[_wi % 4]:
                st.markdown(
                    f'<div class="{_wcls}">'
                    f'<div style="font-size:1.3rem;">{_wico}</div>'
                    f'<div style="font-size:.62rem;font-weight:700;'
                    f'color:{"#5a3d9a" if _won else "#aaa"};margin-top:3px;">{_wnm}</div>'
                    f'<div style="font-size:.55rem;color:{"#9b7ed9" if _won else "#ccc"};">{_wsub}</div>'
                    f'{_wbg}</div>', unsafe_allow_html=True)
    with _h_col:
        st.markdown(
            '<div style="font-size:.72rem;font-weight:700;color:#C4607F;margin-bottom:7px;">🏠 Ngôi nhà</div>',
            unsafe_allow_html=True)
        _hcols2 = st.columns(3)
        for _hi, (_hlv, _hico, _hnm) in enumerate(_HOUSES):
            _hon = _t1_lv >= _hlv
            _hcls = "t1-shop-item t1-item-on" if _hon else "t1-shop-item t1-item-off"
            _hbg  = '<div style="font-size:.55rem;color:#2a9d5c;font-weight:700;">✅</div>' if _hon else ''
            with _hcols2[_hi % 3]:
                st.markdown(
                    f'<div class="{_hcls}">'
                    f'<div style="font-size:1.3rem;">{_hico}</div>'
                    f'<div style="font-size:.62rem;font-weight:700;'
                    f'color:{"#5a3d9a" if _hon else "#aaa"};margin-top:3px;">{_hnm}</div>'
                    f'</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # SECTION G: INVESTMENT ROAD (Growth stages)
    # ══════════════════════════════════════════════════════
    with st.expander("🗺️ Hành trình tích lũy", expanded=False):
        _STAGE_REWARDS = {
            "baby":"🌱 Được gặp bạn lần đầu",
            "child":"💌 Cừu nhớ tên bạn",
            "teen":"🌙 Cừu kể chuyện buổi tối",
            "adult":"✨ Cừu đặt tên theo giấc mơ",
            "master":"🏆 Cừu Lão Luyện — mãi mãi",
        }
        for thresh, skey, sname, slv, sdesc, _ in GROWTH_STAGES:
            _is_cur  = skey == _t1_sk
            _is_done = total_saved >= thresh
            _sr      = _STAGE_REWARDS.get(skey,"")
            if _is_cur:
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#FFF0F5,#FFE4F0);'
                    f'border:2px solid #FFB5C8;border-radius:12px;padding:10px 12px;margin:4px 0;">'
                    f'<div style="font-size:.82rem;font-weight:800;color:#C4607F;">▶ {sname}</div>'
                    f'<div style="font-size:.7rem;color:#999;margin-top:2px;">{_sr}</div>'
                    f'</div>', unsafe_allow_html=True)
            elif _is_done:
                st.markdown(
                    f'<div style="background:#F8F8F8;border:1.5px solid #E0E0E0;'
                    f'border-radius:12px;padding:8px 12px;margin:4px 0;opacity:.7;">'
                    f'<div style="font-size:.78rem;font-weight:700;color:#AAA;text-decoration:line-through;">{sname}</div>'
                    f'<div style="font-size:.7rem;color:#CCC;">✅ {_sr}</div>'
                    f'</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="background:#FAFAFA;border:1.5px dashed #E0CCF0;'
                    f'border-radius:12px;padding:8px 12px;margin:4px 0;">'
                    f'<div style="font-size:.78rem;font-weight:700;color:#C0A8D8;">🔒 {sname}</div>'
                    f'<div style="font-size:.7rem;color:#CCC;margin-top:2px;">Cần {fmt(thresh)} · {_sr}</div>'
                    f'</div>', unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — 💬 HÀNH TRÌNH CỦA TÔI
# Journey Timeline · Dreams · Goals · Life Events · Diary · Chat
# AI Memory Engine: hiển thị những gì AI nhớ về bạn
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    import random as _r2

    # ── Init ─────────────────────────────────────────────────────────────────
    _t2_today = datetime.now().strftime("%Y-%m-%d")
    _t2_uname = mem.get("name","bạn")
    _t2_msgs  = st.session_state.get("messages", [])
    _build_knowledge_graph(mem)
    _update_behavior_metrics(mem)
    _save()

    # ── CSS ──────────────────────────────────────────────────────────────────
    st.markdown("""<style>
    .t2-sec{font-size:.76rem;font-weight:800;color:#C4607F;text-transform:uppercase;
            letter-spacing:.08em;margin:20px 0 10px;display:flex;align-items:center;gap:8px;}
    .t2-sec::before{content:'';display:block;width:3px;height:14px;
                    background:linear-gradient(180deg,#C4607F,#FFD700);border-radius:3px;}
    .t2-card{background:#fff;border:1.5px solid #ffe0ec;border-radius:18px;
             padding:14px 16px;margin-bottom:10px;}
    .t2-tl-dot{width:10px;height:10px;border-radius:50%;
               background:linear-gradient(135deg,#C4607F,#FFD700);flex-shrink:0;margin-top:5px;}
    .t2-mem-chip{display:inline-flex;align-items:center;gap:5px;
                 background:#fff5fa;border:1.5px solid #ffd6e8;border-radius:18px;
                 padding:4px 11px;font-size:.72rem;font-weight:600;color:#C4607F;margin:3px;}
    .t2-subview-label{font-size:.82rem;font-weight:700;color:#555;margin-bottom:6px;}
    </style>""", unsafe_allow_html=True)

    # ── Sub-view toggle ───────────────────────────────────────────────────────
    _t2_view = st.radio("", ["🗓️ Hành Trình", "💭 Tâm Sự", "📔 Nhật Ký", "🎯 Ước Mơ & Mục Tiêu"],
                        horizontal=True, key="t2_view", label_visibility="collapsed")

    # ══════════════════════════════════════════════════════
    # VIEW 1: JOURNEY TIMELINE + MEMORY
    # ══════════════════════════════════════════════════════
    if _t2_view == "🗓️ Hành Trình":
        st.markdown('<div class="t2-sec">🧠 AI nhớ gì về bạn</div>', unsafe_allow_html=True)

        _mem_items = _build_memory_card(mem)
        if _mem_items:
            _chips = ""
            for _mi_ico, _mi_txt in _mem_items:
                _chips += f'<span class="t2-mem-chip">{_mi_ico} {_mi_txt}</span>'
            st.markdown(
                f'<div class="t2-card">'
                f'<div style="font-size:.76rem;color:#aaa;margin-bottom:7px;">Cừu nhớ những điều này về bạn~</div>'
                f'{_chips}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="t2-card" style="text-align:center;color:#aaa;">'
                '💭 Kể chuyện cho Cừu nghe — mình sẽ nhớ mọi điều về bạn!</div>',
                unsafe_allow_html=True)

        # Knowledge graph visualization (simple)
        _kg = mem.get("knowledge_graph", {})
        if _kg:
            st.markdown('<div class="t2-sec">🔗 Bản đồ hành trình</div>', unsafe_allow_html=True)
            _kg_html = '<div class="t2-card"><div style="display:flex;flex-wrap:wrap;gap:8px;">'
            for _ent, _conns in list(_kg.items())[:8]:
                _conns_txt = " · ".join(_conns[:2])
                _kg_html += (
                    f'<div style="background:#f4eeff;border:1.5px solid #d4b8ff;'
                    f'border-radius:14px;padding:8px 12px;">'
                    f'<div style="font-size:.72rem;font-weight:700;color:#5a3d9a;">{_ent.replace("_"," ").title()}</div>'
                    f'<div style="font-size:.63rem;color:#9b7ed9;margin-top:3px;">→ {_conns_txt}</div>'
                    f'</div>'
                )
            _kg_html += '</div></div>'
            st.markdown(_kg_html, unsafe_allow_html=True)

        # Journey Timeline
        st.markdown('<div class="t2-sec">📅 Hành trình của bạn</div>', unsafe_allow_html=True)

        # Build timeline from various sources
        _timeline = []
        _created = mem.get("created_at","")
        if _created:
            _timeline.append({"date": _created[:10], "icon":"🌱", "title":"Bắt đầu hành trình",
                               "body":"Ngày đầu tiên gặp Cừu~"})
        # From diary
        for _de in mem.get("diary_entries",[])[-3:]:
            _timeline.append({"date":_de.get("date_raw","")[:10], "icon":"📔",
                               "title":f"Nhật ký: {_de.get('mood','hôm nay')}",
                               "body": _de.get("content","")[:60] + "..."})
        # From life events
        _ev_map = {"dream_travel":"✈️","dream_house":"🏠","dream_car":"🚗","career":"💼",
                   "cashflow":"💸","family":"❤️","stress":"😓","milestone":"🎊"}
        for _ev in mem.get("life_events",[])[-3:]:
            _ico = _ev_map.get(_ev, "📌")
            _timeline.append({"date":"Gần đây","icon":_ico,
                               "title": LIFE_EVENT_LABELS.get(_ev, _ev),"body":""})
        # From journey_timeline (user actions)
        for _jt in mem.get("journey_timeline",[])[-5:]:
            _timeline.append(_jt)
        # Level milestones
        _lv_cur = get_exp_level(mem.get("user_exp",0))
        if _lv_cur >= 2:
            _timeline.append({"date":"","icon":"⭐","title":f"Đạt Level {_lv_cur}",
                               "body":LEVEL_NAMES.get(_lv_cur,"")})
        # Dreams achieved
        for _dr in mem.get("dreams",[]):
            if _dr.get("amount",0) > 0 and _dr.get("saved",0) >= _dr["amount"]:
                _timeline.append({"date":"","icon":"🎉","title":f"Hoàn thành giấc mơ!",
                                   "body": _dr.get("name","").title()})

        if not _timeline:
            _timeline = [
                {"date":_t2_today,"icon":"🌱","title":"Hành trình bắt đầu hôm nay","body":"Kể chuyện cho Cừu nghe nhé!"},
            ]

        _tl_html = '<div class="t2-card"><div style="position:relative;padding-left:22px;">'
        _tl_html += '<div style="position:absolute;left:4px;top:0;bottom:0;width:2px;background:linear-gradient(180deg,#C4607F,#FFD700,#7B5EA7);border-radius:2px;"></div>'
        for _tl in _timeline[-8:]:
            _body_div = f'<div style="font-size:.72rem;color:#888;margin-top:2px;">{_tl["body"]}</div>' if _tl.get("body") else ""
            _tl_html += (
                f'<div style="display:flex;gap:10px;margin-bottom:12px;">'
                f'<div class="t2-tl-dot" style="margin-left:-18px;"></div>'
                f'<div>'
                f'<div style="font-size:.63rem;color:#bbb;">{_tl.get("date","")}</div>'
                f'<div style="font-size:.8rem;font-weight:700;color:#333;">{_tl["icon"]} {_tl["title"]}</div>'
                f'{_body_div}</div></div>'
            )
        _tl_html += '</div></div>'
        st.markdown(_tl_html, unsafe_allow_html=True)

        # Behavior metrics dashboard
        _bm = mem.get("behavior_metrics",{})
        if any(_bm.get(k,0) > 0 for k in ("engagement","churn_risk","attachment")):
            st.markdown('<div class="t2-sec">📊 Chỉ số hành vi của bạn</div>', unsafe_allow_html=True)
            _b1, _b2, _b3 = st.columns(3)
            for _bc, _bl, _bv, _bcolor in [
                (_b1,"💚 Engagement", _bm.get("engagement",0),"#2a9d5c"),
                (_b2,"❤️ Gắn bó",    _bm.get("attachment",0),"#C4607F"),
                (_b3,"⚡ Churn Risk", _bm.get("churn_risk",0), "#FFA500" if _bm.get("churn_risk",0)<50 else "#E53935"),
            ]:
                _bc.markdown(
                    f'<div class="t2-card" style="text-align:center;padding:12px 10px;">'
                    f'<div style="font-size:.68rem;color:#aaa;">{_bl}</div>'
                    f'<div style="font-size:1.6rem;font-weight:800;color:{_bcolor};">{_bv}</div>'
                    f'<div style="background:#f0f0f7;border-radius:6px;height:5px;margin-top:5px;overflow:hidden;">'
                    f'<div style="width:{min(100,_bv)}%;height:100%;background:{_bcolor};border-radius:6px;"></div></div>'
                    f'</div>', unsafe_allow_html=True)

            # Churn warning
            if _bm.get("churn_risk",0) > 60:
                st.markdown(
                    '<div style="background:linear-gradient(135deg,#1A1A2E,#2D1B69);'
                    'border-radius:14px;padding:12px 16px;margin-top:6px;">'
                    '<div style="font-size:.82rem;font-weight:700;color:#c4a8ff;">🐑 Cừu đang nhớ bạn...</div>'
                    '<div style="font-size:.76rem;color:rgba(255,255,255,.7);margin-top:3px;">'
                    'Lâu rồi chưa gặp — hôm nay cho Cừu ăn một chút nhé? Dù chỉ 10k thôi cũng ý nghĩa lắm!</div>'
                    '</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # VIEW 2: TÂM SỰ (AI Chat)
    # ══════════════════════════════════════════════════════
    elif _t2_view == "💭 Tâm Sự":
        st.markdown('<div class="t2-sec">💬 Tâm sự với Cừu</div>', unsafe_allow_html=True)

        # API key input in expander
        with st.expander("⚙️ API Key", expanded=not st.session_state.get("api_key","")):
            _ak = st.text_input("Anthropic API Key:", value=st.session_state.get("api_key",""),
                                type="password", key="t2_apikey")
            if _ak:
                st.session_state.api_key = _ak
                if st.button("✅ Lưu", key="t2_save_api"):
                    st.rerun()

        # Quick suggestion
        _sugg = get_smart_suggestion(_t2_msgs, mem)
        if _sugg:
            st.markdown(
                f'<div class="suggestion-box">{_sugg}</div>', unsafe_allow_html=True)

        # Quick reply chips
        _quick_replies = [
            "Hôm nay mình mệt quá...", "Cho mình hỏi về quỹ đầu tư",
            "Mình muốn kể về giấc mơ", "Thị trường đang xuống, mình lo",
            "Mình vừa nhận lương rồi!",
        ]
        _qr_cols = st.columns(len(_quick_replies))
        for _qi, _qr in enumerate(_quick_replies):
            if _qr_cols[_qi % len(_quick_replies)].button(_qr, key=f"t2_qr_{_qi}", use_container_width=True):
                st.session_state["_t2_quick_send"] = _qr

        # Chat history
        _avatar_src = get_avatar_src()
        for msg in _t2_msgs:
            if msg["role"] == "system":
                continue
            with st.chat_message(msg["role"], avatar=_avatar_src if msg["role"]=="assistant" else None):
                st.markdown(msg["content"])

        # Input
        _user_in = st.chat_input("Nói với Cừu...", key="t2_chat_input")
        _auto_send = st.session_state.pop("_t2_quick_send", None)
        _to_send   = _auto_send or _user_in

        if _to_send:
            _exp_text = _EMOTION_EXPAND.get(_to_send.strip().lower(), _to_send)
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append({"role":"user","content":_to_send})
            with st.chat_message("user"):
                st.markdown(_to_send)
            with st.chat_message("assistant", avatar=_avatar_src):
                with st.spinner("🐑 Cừu đang nghĩ..."):
                    _res = _call_llm(_exp_text, _SYS_EMOTION)
                _reply = _res.get("message","Bê bê~ 🐑 Mình đang lắng nghe!")
                st.markdown(_reply)
            st.session_state.messages.append({"role":"assistant","content":_reply})
            _complete_quest(mem,"chat",10)
            _add_exp(10,mem)
            _check_achievements(mem)
            # Add to journey timeline
            mem.setdefault("journey_timeline",[]).append({
                "date":_t2_today,"icon":"💬","title":"Tâm sự với Cừu","body":_to_send[:50]
            })
            _build_knowledge_graph(mem)
            _save()
            st.rerun()

    # ══════════════════════════════════════════════════════
    # VIEW 3: NHẬT KÝ
    # ══════════════════════════════════════════════════════
    elif _t2_view == "📔 Nhật Ký":
        st.markdown('<div class="t2-sec">📔 Nhật ký hôm nay</div>', unsafe_allow_html=True)

        _diary_entries = mem.get("diary_entries", [])
        _dstreak       = _diary_streak(_diary_entries)
        _avatar_diary  = get_avatar_src("diary")

        _d1, _d2, _d3 = st.columns(3)
        for _dc, _dl, _dv in [
            (_d1,"📅 Tổng trang nhật ký", str(len(_diary_entries))),
            (_d2,"🔥 Streak nhật ký",     f"{_dstreak} ngày"),
            (_d3,"✨ Giấc mơ hay nhắc",  (_top_diary_dream(_diary_entries) or "Chưa có").title()[:16]),
        ]:
            _dc.markdown(
                f'<div class="diary-stat-mini">'
                f'<div style="font-size:.66rem;color:#aaa;">{_dl}</div>'
                f'<div style="font-size:1.1rem;font-weight:800;color:#C4607F;">{_dv}</div>'
                f'</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        # Diary prompts rotation
        _DIARY_PROMPTS = [
            "Hôm nay bạn cảm thấy thế nào về hành trình tài chính của mình?",
            "Điều gì khiến bạn tự hào nhất trong tuần này?",
            "Bạn đang lo lắng về điều gì? Kể cho Cừu nghe nhé.",
            "Nếu được nói một điều với tương lai, bạn muốn nói gì?",
            "Giấc mơ của bạn hôm nay trông như thế nào?",
        ]
        _dprompt = _DIARY_PROMPTS[len(_diary_entries) % len(_DIARY_PROMPTS)]
        st.markdown(
            f'<div class="diary-prompt">📝 Cừu hỏi: {_dprompt}</div>', unsafe_allow_html=True)

        with st.form("t2_diary_form", clear_on_submit=True):
            _mood_sel = st.select_slider("Tâm trạng hôm nay",
                options=["rất vui 🌟","vui 😊","bình thường 🌤️","hơi mệt 😴","áp lực 😓","bực 😤","quyết tâm 💪"],
                value="bình thường 🌤️", key="t2_mood_sel")
            _diary_text = st.text_area("Kể cho Cừu nghe...", height=130, placeholder="Hôm nay mình...", key="t2_diary_text")
            _dream_diary = st.text_input("✨ Giấc mơ muốn nhắc đến (để trống nếu không)", key="t2_dream_diary")
            _tag_opts    = list(LIFE_EVENT_LABELS.keys())
            _tag_labels  = [LIFE_EVENT_LABELS[t] for t in _tag_opts]
            _tag_sel_idx = st.multiselect("🏷️ Chủ đề", options=_tag_labels, key="t2_tags_sel")
            _tag_sel     = [_tag_opts[_tag_labels.index(t)] for t in _tag_sel_idx if t in _tag_labels]
            _submitted = st.form_submit_button("🐑 Lưu nhật ký hôm nay", type="primary", use_container_width=True)

        if _submitted and _diary_text.strip():
            with st.spinner("🐑 Cừu đang đọc nhật ký..."):
                _dresp = _call_llm(
                    f"Nhật ký: {_diary_text}\nTâm trạng: {_mood_sel}\nTags: {_tag_sel}",
                    _SYS_DIARY,
                )
            _sheep_reply = _dresp.get("sheep_reply","Bê bê~ Cừu đọc rồi nhé 💙")
            _new_entry   = {
                "id":         f"d_{len(_diary_entries)}",
                "date":       datetime.now().strftime("%d/%m/%Y · %H:%M"),
                "date_raw":   datetime.now().isoformat(),
                "mood":       _mood_sel, "content": _diary_text,
                "dream":      _dream_diary.strip() or _dresp.get("dream_detected",""),
                "tags":       list(set(_tag_sel + _dresp.get("tags",[]))),
                "reply":      _sheep_reply,
            }
            mem.setdefault("diary_entries",[]).append(_new_entry)
            set_mood(_dresp.get("mood","listening"))
            _complete_quest(mem,"diary",20)
            _add_exp(20,mem)
            _check_achievements(mem)
            # Update life events
            for _xt in _dresp.get("tags",[]):
                if _xt and _xt not in mem.get("life_events",[]):
                    mem.setdefault("life_events",[]).append(_xt)
            # Dream detection
            _dd = _dream_diary.strip() or _dresp.get("dream_detected","")
            if _dd and _dd not in [d["name"] for d in mem.get("dreams",[])]:
                mem.setdefault("dreams",[]).append({"name":_dd,"amount":0,"saved":0,"tags":_tag_sel})
            # Journey timeline
            mem.setdefault("journey_timeline",[]).append({
                "date":_t2_today,"icon":"📔","title":"Viết nhật ký","body":_diary_text[:50]
            })
            _build_knowledge_graph(mem)
            _save()
            # Show sheep reply
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
                f'border-radius:16px;padding:14px 18px;border:1.5px solid #FFD6E8;">'
                f'<img src="{_avatar_diary}" width="50" style="border-radius:50%;float:left;margin-right:12px;border:3px solid #FFB5C8;" />'
                f'<div style="font-size:.88rem;color:#C4607F;font-style:italic;line-height:1.65;">'
                f'🐑 {_sheep_reply}</div><div style="clear:both;"></div>'
                f'</div>', unsafe_allow_html=True)
            st.rerun()

        # Past diary entries
        if _diary_entries:
            st.markdown('<div class="t2-sec" style="margin-top:16px;">📚 Nhật ký cũ</div>', unsafe_allow_html=True)
            for _de in reversed(_diary_entries[-5:]):
                _preview  = _de.get("content","")[:100] + "..."
                _tags_lbl = " ".join(LIFE_EVENT_LABELS.get(t,t) for t in _de.get("tags",[])[:2])
                _reply_pr = _de.get("reply","")[:60]
                st.markdown(
                    f'<div class="diary-entry-card">'
                    f'<div style="display:flex;justify-content:space-between;">'
                    f'<span style="font-size:.8rem;font-weight:700;color:#444;">{_de.get("mood","")}</span>'
                    f'<span style="font-size:.72rem;color:#bbb;">{_de.get("date","")[:10]}</span>'
                    f'</div>'
                    f'<div style="font-size:.82rem;color:#666;margin:5px 0 3px;">{_preview}</div>'
                    f'<div style="font-size:.72rem;color:#aaa;">{_tags_lbl}</div>'
                    + (f'<div style="font-size:.78rem;color:#C4607F;font-style:italic;margin-top:5px;">🐑 {_reply_pr}...</div>' if _reply_pr else "")
                    + f'</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # VIEW 4: ƯỚC MƠ & MỤC TIÊU
    # ══════════════════════════════════════════════════════
    elif _t2_view == "🎯 Ước Mơ & Mục Tiêu":
        st.markdown('<div class="t2-sec">✨ Giấc mơ đang được nuôi</div>', unsafe_allow_html=True)

        # Add dream
        with st.expander("➕ Thêm giấc mơ mới", expanded=not mem.get("dreams",[])):
            _dn = st.text_input("Tên giấc mơ (VD: Đi Nhật, Mua xe, Tự do tài chính)", key="t2_dream_name")
            _da = st.number_input("Số tiền cần (0 = chưa biết)", min_value=0, step=100_000, key="t2_dream_amt")
            if st.button("🐑 Thêm giấc mơ!", type="primary", key="t2_add_dream") and _dn.strip():
                _existing = [d["name"].lower() for d in mem.get("dreams",[])]
                if _dn.strip().lower() not in _existing:
                    mem.setdefault("dreams",[]).append({
                        "name": _dn.strip(), "amount": int(_da), "saved": 0, "tags": []
                    })
                    mem.setdefault("journey_timeline",[]).append({
                        "date":_t2_today,"icon":"✨","title":f"Thêm giấc mơ: {_dn.strip()}","body":""
                    })
                    _build_knowledge_graph(mem)
                    _save()
                    st.rerun()

        for _i, _d in enumerate(mem.get("dreams",[])):
            _dpct = min(100, _d["saved"] / _d["amount"] * 100) if _d.get("amount",0) > 0 else 0
            with st.container(border=True):
                _dc1, _dc2 = st.columns([3,1])
                with _dc1:
                    st.markdown(f"**✨ {_d['name'].title()}**")
                    if _d.get("amount",0) > 0:
                        st.progress(_dpct/100, text=f"{_dpct:.1f}% · đã có {fmt(_d['saved'])} / cần {fmt(_d['amount'])}")
                    else:
                        st.caption("Chưa đặt mục tiêu số tiền")
                with _dc2:
                    if _d.get("amount",0) > 0 and _d["saved"] < _d["amount"]:
                        if st.button("❤️ +50k", key=f"t2_dream_{_i}", type="primary"):
                            _d["saved"] = min(_d["amount"], _d["saved"] + 50_000)
                            mem["total_saved"] += 50_000
                            mem["last_fed_date"] = _t2_today
                            _complete_quest(mem,"feed",30)
                            _add_exp(30,mem)
                            set_mood("celebrate" if _d["saved"]>=_d["amount"] else "happy")
                            _save()
                            st.rerun()
                    elif _d.get("amount",0) > 0 and _d["saved"] >= _d["amount"]:
                        st.success("🎉 Đạt rồi!")

        # Goals
        st.markdown('<div class="t2-sec" style="margin-top:14px;">🎯 Mục tiêu</div>', unsafe_allow_html=True)

        with st.expander("➕ Thêm mục tiêu", expanded=False):
            _gn = st.text_input("Tên mục tiêu", key="t2_goal_name")
            _gd = st.date_input("Deadline (tuỳ chọn)", key="t2_goal_date")
            if st.button("🐑 Thêm mục tiêu!", type="primary", key="t2_add_goal") and _gn.strip():
                mem.setdefault("goals",[]).append({
                    "name": _gn.strip(), "target_date": str(_gd), "done": False
                })
                _save()
                st.rerun()

        _goals = mem.get("goals",[])
        if _goals:
            for _gi, _g in enumerate(_goals):
                _gc1, _gc2 = st.columns([5,1])
                with _gc1:
                    _done_ico = "✅" if _g.get("done") else "⬜"
                    _date_txt = f' · {_g["target_date"]}' if _g.get("target_date") else ""
                    st.markdown(
                        f'<div class="t2-card" style="padding:10px 14px;display:flex;align-items:center;gap:8px;">'
                        f'<span style="font-size:1.1rem;">{_done_ico}</span>'
                        f'<div>'
                        f'<div style="font-size:.84rem;font-weight:700;color:#333;'
                        f'text-decoration:{"line-through" if _g.get("done") else "none"};">{_g["name"]}</div>'
                        f'<div style="font-size:.68rem;color:#aaa;">{_date_txt}</div>'
                        f'</div></div>', unsafe_allow_html=True)
                with _gc2:
                    if not _g.get("done"):
                        if st.button("✅", key=f"t2_gdone_{_gi}"):
                            _g["done"] = True
                            _add_exp(50, mem)
                            mem.setdefault("journey_timeline",[]).append({
                                "date":_t2_today,"icon":"🎯","title":f"Hoàn thành: {_g['name']}","body":""
                            })
                            _save()
                            st.rerun()
        else:
            st.info("💭 Đặt mục tiêu — Cừu sẽ giúp bạn theo dõi!")

        # Life Events quick log
        st.markdown('<div class="t2-sec" style="margin-top:14px;">📌 Sự kiện cuộc sống</div>', unsafe_allow_html=True)
        _ev_cols = st.columns(4)
        for _ei, (_ek, _ev_lbl) in enumerate(LIFE_EVENT_LABELS.items()):
            _active = _ek in mem.get("life_events",[])
            if _ev_cols[_ei % 4].button(
                _ev_lbl + (" ✓" if _active else ""),
                key=f"t2_ev_{_ek}",
                type="primary" if _active else "secondary",
                use_container_width=True,
            ):
                if _active:
                    mem["life_events"] = [e for e in mem.get("life_events",[]) if e != _ek]
                else:
                    mem.setdefault("life_events",[]).append(_ek)
                _build_knowledge_graph(mem)
                _save()
                st.rerun()

# ════════════════════════════════════════════════════════════════
# TAB 3 — 🧠 PHÒNG NGHIÊN CỨU CỦA CỪU
# Personalized AI Research + Fund Explainer + CEO Demo + Behavior
# ════════════════════════════════════════════════════════════════
with tab3:
    mem = st.session_state.user_memory

    # ── sub-tabs ─────────────────────────────────────────────────
    t3a, t3b, t3c, t3d = st.tabs([
        "🔍 Nghiên Cứu Cho Tôi",
        "🌳 Quỹ Là Gì?",
        "📊 CEO Demo Mode",
        "🧠 Phân Tích Hành Vi",
    ])

    # ─────────────────────────────────────────────────────────────
    # T3A — PERSONALIZED DEEP RESEARCH
    # ─────────────────────────────────────────────────────────────
    with t3a:
        st.markdown("""
<div style='background:linear-gradient(135deg,#f0e6ff,#e6f0ff);
            border-radius:16px;padding:20px 24px;margin-bottom:16px'>
  <div style='font-size:22px;font-weight:700;color:#5b21b6'>🔍 Nghiên Cứu Cá Nhân Hóa</div>
  <div style='font-size:14px;color:#6b7280;margin-top:4px'>
    Cừu tổng hợp từ TikTok · Reddit · YouTube · Google Trends · News<br>
    — chỉ những gì liên quan tới ước mơ của bạn 💜
  </div>
</div>
""", unsafe_allow_html=True)

        dreams = mem.get("dreams", [])
        insights = _get_research_insights(mem)

        if not dreams:
            st.info("🐑 Thêm ước mơ ở Tab **Hành Trình → Ước Mơ** để Cừu nghiên cứu cho bạn nhé!")
        else:
            dream_tags = [d.get("name","") for d in dreams[:3]]
            tags_html = "".join(
                f'<span style="background:#ede9fe;color:#6d28d9;padding:3px 10px;'
                f'border-radius:20px;font-size:12px;margin-right:6px">{t}</span>'
                for t in dream_tags
            )
            st.markdown(
                f'<div style="margin-bottom:12px">Đang nghiên cứu theo ước mơ: {tags_html}</div>',
                unsafe_allow_html=True,
            )

        # Insight cards — 2 columns
        if insights:
            cols = st.columns(2)
            for i, ins in enumerate(insights):
                _icon  = ins.get("icon","📌")
                _title = ins.get("title","")
                _body  = ins.get("body","")
                _cta   = ins.get("cta","")
                with cols[i % 2]:
                    st.markdown(f"""
<div style='background:#fff;border:1px solid #e9d5ff;border-radius:14px;
            padding:16px;margin-bottom:14px;box-shadow:0 2px 8px rgba(109,40,217,.07)'>
  <div style='font-size:28px;margin-bottom:6px'>{_icon}</div>
  <div style='font-size:15px;font-weight:700;color:#3730a3;margin-bottom:6px'>{_title}</div>
  <div style='font-size:13px;color:#374151;line-height:1.55;margin-bottom:10px'>{_body}</div>
  <div style='background:#f5f3ff;border-radius:8px;padding:8px 12px;
              font-size:12px;color:#6d28d9;font-weight:600'>{_cta}</div>
</div>
""", unsafe_allow_html=True)

        # Refresh research button
        st.markdown("---")
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            st.caption("🔄 Cừu cập nhật nghiên cứu mỗi ngày dựa trên ước mơ của bạn")
        with col_r2:
            if st.button("🔍 Nghiên Cứu Lại", key="t3_refresh_research"):
                mem["last_research_date"] = ""
                _save()
                st.rerun()

    # ─────────────────────────────────────────────────────────────
    # T3B — FUND EXPLAINER (food metaphors)
    # ─────────────────────────────────────────────────────────────
    with t3b:
        st.markdown("""
<div style='background:linear-gradient(135deg,#ecfdf5,#d1fae5);
            border-radius:16px;padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:700;color:#065f46'>🌳 Quỹ Đầu Tư Là Gì?</div>
  <div style='font-size:14px;color:#374151;margin-top:4px'>
    Giải thích đơn giản — không dùng từ chuyên môn 🐑
  </div>
</div>
""", unsafe_allow_html=True)

        fund_cards = [
            {
                "icon": "🌳",
                "title": "Trồng Cây",
                "subtitle": "Quỹ Cổ Phiếu (Equity Fund)",
                "desc": (
                    "Bạn góp tiền → Cừu trồng cây cho bạn → cây lớn dần → bán được giá cao hơn. "
                    "Nhưng có mùa mưa, có mùa hạn — cây lên xuống theo thị trường."
                ),
                "risk": "⚡ Rủi ro cao · Lợi nhuận kỳ vọng cao",
                "color_bg": "#f0fdf4",
                "color_border": "#86efac",
                "color_title": "#15803d",
            },
            {
                "icon": "🪣",
                "title": "Bình Nước",
                "subtitle": "Quỹ Trái Phiếu (Bond Fund)",
                "desc": (
                    "Bạn cho người khác mượn nước → họ trả lại kèm thêm một ít mỗi tháng. "
                    "Ổn định hơn cây, nhưng không tăng nhanh bằng."
                ),
                "risk": "🌿 Rủi ro vừa · Lợi nhuận đều đặn",
                "color_bg": "#eff6ff",
                "color_border": "#93c5fd",
                "color_title": "#1d4ed8",
            },
            {
                "icon": "🎒",
                "title": "Balo Hỗn Hợp",
                "subtitle": "Quỹ Cân Bằng (Balanced Fund)",
                "desc": (
                    "Cừu bỏ vào balo: 60% cây + 40% bình nước. "
                    "Khi cây gặp hạn, bình nước vẫn nhỏ giọt. Cân bằng giữa tăng trưởng và ổn định."
                ),
                "risk": "⚖️ Rủi ro cân bằng · Phổ biến nhất",
                "color_bg": "#fdf4ff",
                "color_border": "#d8b4fe",
                "color_title": "#7e22ce",
            },
            {
                "icon": "🧸",
                "title": "Hũ Tiết Kiệm",
                "subtitle": "Quỹ Tiền Tệ (Money Market)",
                "desc": (
                    "Tiền để trong hũ, Cừu giữ an toàn tuyệt đối. "
                    "Lãi suất thấp nhưng rút ra bất cứ lúc nào. Phù hợp tiền ngắn hạn."
                ),
                "risk": "🛡️ Rủi ro rất thấp · Linh hoạt",
                "color_bg": "#fffbeb",
                "color_border": "#fcd34d",
                "color_title": "#b45309",
            },
        ]

        for fc in fund_cards:
            st.markdown(f"""
<div style='background:{fc["color_bg"]};border:2px solid {fc["color_border"]};
            border-radius:16px;padding:18px 20px;margin-bottom:14px'>
  <div style='display:flex;align-items:center;gap:12px;margin-bottom:8px'>
    <div style='font-size:32px'>{fc["icon"]}</div>
    <div>
      <div style='font-size:17px;font-weight:700;color:{fc["color_title"]}'>{fc["title"]}</div>
      <div style='font-size:12px;color:#6b7280'>{fc["subtitle"]}</div>
    </div>
  </div>
  <div style='font-size:13px;color:#374151;line-height:1.6;margin-bottom:10px'>{fc["desc"]}</div>
  <div style='font-size:12px;font-weight:600;color:{fc["color_title"]}'>{fc["risk"]}</div>
</div>
""", unsafe_allow_html=True)

        # DCA explanation
        st.markdown("""
<div style='background:#fefce8;border:2px solid #fde047;border-radius:16px;
            padding:18px 20px;margin-top:8px'>
  <div style='font-size:17px;font-weight:700;color:#854d0e;margin-bottom:8px'>
    🔁 DCA — Cho Cừu Ăn Đều Đặn
  </div>
  <div style='font-size:13px;color:#374151;line-height:1.65'>
    <b>Dollar Cost Averaging</b> = đầu tư cùng một số tiền mỗi tháng, bất kể thị trường lên hay xuống.<br><br>
    Ví dụ: Thay vì chờ "thời điểm hoàn hảo", bạn cho Cừu ăn 500k mỗi tháng.<br>
    → Tháng cây đắt: mua ít cây hơn. Tháng cây rẻ: mua được nhiều cây hơn.<br>
    → Trung bình giá mua luôn tốt hơn người chờ đợi 🐑
  </div>
</div>
""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────
    # T3C — CEO DEMO MODE (6-month simulation)
    # ─────────────────────────────────────────────────────────────
    with t3c:
        st.markdown("""
<div style='background:linear-gradient(135deg,#1e1b4b,#312e81);
            border-radius:16px;padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:700;color:#c7d2fe'>📊 CEO Demo Mode</div>
  <div style='font-size:14px;color:#a5b4fc;margin-top:4px'>
    Mô phỏng 6 tháng tích lũy đều đặn — xem tiền của bạn lớn lên thế nào 🚀
  </div>
</div>
""", unsafe_allow_html=True)

        # Inputs
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            demo_monthly = st.number_input(
                "💰 Tích lũy mỗi tháng (VNĐ)",
                min_value=50_000,
                max_value=50_000_000,
                value=500_000,
                step=50_000,
                key="t3_demo_monthly",
                format="%d",
            )
        with col_d2:
            demo_rate_pct = st.slider(
                "📈 Lãi suất kỳ vọng / năm (%)",
                min_value=4,
                max_value=20,
                value=10,
                step=1,
                key="t3_demo_rate",
            )

        demo_initial = st.number_input(
            "🌱 Số tiền đã có sẵn (tùy chọn)",
            min_value=0,
            max_value=1_000_000_000,
            value=int(mem.get("total_saved", 0)),
            step=100_000,
            key="t3_demo_initial",
            format="%d",
        )

        # Simulate 6 months
        monthly_rate = (demo_rate_pct / 100) / 12
        months = 6
        balance = demo_initial
        timeline_rows = []
        for m in range(1, months + 1):
            balance = balance * (1 + monthly_rate) + demo_monthly
            interest = balance - (demo_initial + demo_monthly * m)
            timeline_rows.append({
                "month": m,
                "balance": int(balance),
                "contributed": demo_initial + demo_monthly * m,
                "interest": max(0, int(interest)),
            })

        total_contributed = demo_initial + demo_monthly * months
        total_final = timeline_rows[-1]["balance"]
        total_gain = total_final - total_contributed

        # Summary cards
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"""
<div style='background:#1e1b4b;border-radius:12px;padding:14px;text-align:center'>
  <div style='font-size:12px;color:#a5b4fc'>Tổng đã bỏ vào</div>
  <div style='font-size:18px;font-weight:700;color:#c7d2fe'>
    {total_contributed/1_000_000:.1f}tr
  </div>
</div>""", unsafe_allow_html=True)
        with sc2:
            st.markdown(f"""
<div style='background:#14532d;border-radius:12px;padding:14px;text-align:center'>
  <div style='font-size:12px;color:#86efac'>Sau 6 tháng</div>
  <div style='font-size:18px;font-weight:700;color:#4ade80'>
    {total_final/1_000_000:.2f}tr
  </div>
</div>""", unsafe_allow_html=True)
        with sc3:
            st.markdown(f"""
<div style='background:#713f12;border-radius:12px;padding:14px;text-align:center'>
  <div style='font-size:12px;color:#fde68a'>Tiền lãi kiếm thêm</div>
  <div style='font-size:18px;font-weight:700;color:#fbbf24'>
    +{total_gain/1_000_000:.2f}tr
  </div>
</div>""", unsafe_allow_html=True)

        # Month-by-month timeline
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("#### 📅 Lịch Trình 6 Tháng")

        month_labels = ["T.1","T.2","T.3","T.4","T.5","T.6"]
        max_bal = timeline_rows[-1]["balance"]

        for row in timeline_rows:
            bar_pct = int(row["balance"] / max_bal * 100)
            m_label = month_labels[row["month"] - 1]
            bal_str = f'{row["balance"]/1_000_000:.2f}tr'
            gain_str = f'+{row["interest"]/1000:.0f}k lãi' if row["interest"] > 0 else ""
            st.markdown(f"""
<div style='display:flex;align-items:center;gap:12px;margin-bottom:8px'>
  <div style='width:32px;font-size:12px;color:#a5b4fc;font-weight:600'>{m_label}</div>
  <div style='flex:1;background:#1e1b4b;border-radius:6px;height:22px;overflow:hidden'>
    <div style='width:{bar_pct}%;background:linear-gradient(90deg,#6366f1,#8b5cf6);
                height:100%;border-radius:6px;transition:width .4s'></div>
  </div>
  <div style='width:70px;font-size:13px;color:#c7d2fe;font-weight:700'>{bal_str}</div>
  <div style='width:80px;font-size:11px;color:#86efac'>{gain_str}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style='background:#1e1b4b;border-radius:12px;padding:14px;margin-top:12px;
            font-size:13px;color:#a5b4fc;line-height:1.6'>
  💡 <b style="color:#c7d2fe">Đây là mô phỏng tham khảo</b> — lãi suất thực tế phụ thuộc vào
  loại quỹ và thị trường. Tích lũy đều đặn (DCA) là cách hiệu quả nhất dù thị trường lên xuống.
</div>
""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────
    # T3D — BEHAVIOR PREDICTION DASHBOARD
    # ─────────────────────────────────────────────────────────────
    with t3d:
        st.markdown("""
<div style='background:linear-gradient(135deg,#fff7ed,#fed7aa);
            border-radius:16px;padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:700;color:#c2410c'>🧠 Phân Tích Hành Vi</div>
  <div style='font-size:14px;color:#78350f;margin-top:4px'>
    Cừu hiểu bạn — theo dõi mức độ gắn kết và đưa ra gợi ý cá nhân 💜
  </div>
</div>
""", unsafe_allow_html=True)

        bm = _update_behavior_metrics(mem)
        _save()

        eng   = bm.get("engagement", 0)
        churn = bm.get("churn_risk", 0)
        att   = bm.get("attachment", 0)

        # Three metric bars
        def _metric_bar(label, value, color_high, color_low, invert=False):
            pct = value
            bar_color = color_high if (value >= 50) != invert else color_low
            return f"""
<div style='margin-bottom:16px'>
  <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
    <span style='font-size:13px;font-weight:600;color:#374151'>{label}</span>
    <span style='font-size:13px;font-weight:700;color:{bar_color}'>{value}/100</span>
  </div>
  <div style='background:#f3f4f6;border-radius:8px;height:12px'>
    <div style='width:{pct}%;background:{bar_color};border-radius:8px;height:100%'></div>
  </div>
</div>"""

        st.markdown(
            _metric_bar("⚡ Engagement — Mức độ tương tác", eng,   "#10b981", "#d1d5db") +
            _metric_bar("💔 Churn Risk — Nguy cơ rời bỏ",  churn, "#ef4444", "#10b981", invert=True) +
            _metric_bar("❤️ Attachment — Gắn kết cảm xúc", att,   "#8b5cf6", "#d1d5db"),
            unsafe_allow_html=True,
        )

        # Churn warning
        if churn >= 60:
            st.warning("⚠️ Bạn đã vắng mặt khá lâu. Cừu nhớ bạn lắm — cho Cừu ăn một bó cỏ nhé 🐑")

        # Personalized suggestions
        st.markdown("#### 💡 Gợi Ý Cho Bạn")

        suggestions = []
        if eng < 40:
            suggestions.append(("🎯", "Hôm nay hoàn thành 1 nhiệm vụ để tăng điểm tương tác nhé!"))
        if att < 30:
            suggestions.append(("✍️", "Viết một entry nhật ký để Cừu hiểu bạn hơn."))
        if len(mem.get("dreams", [])) == 0:
            suggestions.append(("⭐", "Thêm ước mơ đầu tiên để Cừu nghiên cứu riêng cho bạn!"))
        if len(mem.get("diary_entries", [])) < 3:
            suggestions.append(("📔", "Viết thêm nhật ký — Cừu sẽ đưa ra gợi ý tài chính cá nhân hóa hơn."))
        if mem.get("streak", 0) == 0:
            suggestions.append(("🔥", "Cho Cừu ăn hôm nay để bắt đầu chuỗi streak nhé!"))

        if not suggestions:
            suggestions = [
                ("🌟", "Bạn đang dùng tốt lắm! Tiếp tục duy trì thói quen tích lũy mỗi ngày."),
                ("🐑", "Cừu tự hào vì bạn kiên trì đến vậy!"),
            ]

        for s_icon, s_text in suggestions[:4]:
            st.markdown(f"""
<div style='display:flex;align-items:flex-start;gap:12px;
            background:#fff7ed;border-radius:10px;padding:12px 14px;margin-bottom:8px'>
  <div style='font-size:20px'>{s_icon}</div>
  <div style='font-size:13px;color:#374151;line-height:1.5'>{s_text}</div>
</div>
""", unsafe_allow_html=True)

        # Stats summary
        st.markdown("---")
        st.markdown("#### 📊 Thống Kê Tổng Hợp")
        n_dreams  = len(mem.get("dreams", []))
        n_diary   = len(mem.get("diary_entries", []))
        n_quests_total = sum(
            sum(1 for k, v in dq.items() if k != "bonus_claimed" and v)
            for dq in mem.get("daily_quests", {}).values()
        )
        streak    = mem.get("streak", 0)

        stat_cols = st.columns(4)
        for col_s, (lbl, val, icon) in zip(stat_cols, [
            ("Ước Mơ",   n_dreams,      "⭐"),
            ("Nhật Ký",  n_diary,       "📔"),
            ("Nhiệm Vụ", n_quests_total,"✅"),
            ("Streak",   streak,        "🔥"),
        ]):
            with col_s:
                st.markdown(f"""
<div style='background:#fff7ed;border-radius:10px;padding:12px;text-align:center'>
  <div style='font-size:22px'>{icon}</div>
  <div style='font-size:20px;font-weight:700;color:#c2410c'>{val}</div>
  <div style='font-size:11px;color:#78350f'>{lbl}</div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — 👨‍👩‍👧 GIA ĐÌNH CỪU
# Family Mode: each member has their own sheep, level, progress
# ════════════════════════════════════════════════════════════════
with tab4:
    mem = st.session_state.user_memory

    family_members = mem.get("family_members", [])
    family_code    = mem.get("family_code", "")

    st.markdown("""
<div style='background:linear-gradient(135deg,#fdf2f8,#fce7f3);
            border-radius:16px;padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:700;color:#9d174d'>
    👨‍👩‍👧 Gia Đình Cừu
  </div>
  <div style='font-size:14px;color:#6b7280;margin-top:4px'>
    Cùng gia đình tích lũy — mỗi người một con Cừu riêng 🐑💕
  </div>
</div>
""", unsafe_allow_html=True)

    # ─── ROLE DEFINITIONS ────────────────────────────────────────
    FAMILY_ROLES = {
        "👨 Ba":    {"emoji": "👨", "sheep": "🐏", "color": "#1d4ed8", "bg": "#eff6ff"},
        "👩 Mẹ":    {"emoji": "👩", "sheep": "🐑", "color": "#9d174d", "bg": "#fdf2f8"},
        "🧒 Con":   {"emoji": "🧒", "sheep": "🐣", "color": "#065f46", "bg": "#ecfdf5"},
        "👴 Ông":   {"emoji": "👴", "sheep": "🦙", "color": "#78350f", "bg": "#fffbeb"},
        "👵 Bà":    {"emoji": "👵", "sheep": "🦌", "color": "#5b21b6", "bg": "#f5f3ff"},
        "👫 Bạn đời":{"emoji":"👫", "sheep": "🐑", "color": "#047857", "bg": "#ecfdf5"},
    }

    # ─── FAMILY CODE SECTION ─────────────────────────────────────
    with st.expander("🔑 Mã Gia Đình", expanded=(not family_code)):
        if family_code:
            st.markdown(f"""
<div style='background:#f0fdf4;border:2px solid #86efac;border-radius:12px;
            padding:14px;text-align:center'>
  <div style='font-size:12px;color:#15803d;margin-bottom:4px'>Mã gia đình của bạn</div>
  <div style='font-size:28px;font-weight:800;color:#166534;letter-spacing:4px'>{family_code}</div>
  <div style='font-size:12px;color:#6b7280;margin-top:6px'>
    Chia sẻ mã này để thêm thành viên
  </div>
</div>
""", unsafe_allow_html=True)
            if st.button("🔄 Tạo Mã Mới", key="t4_regen_code"):
                import random, string
                mem["family_code"] = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
                _save()
                st.rerun()
        else:
            st.info("Tạo mã gia đình để mời các thành viên cùng tích lũy nhé!")
            if st.button("✨ Tạo Mã Gia Đình", key="t4_create_code"):
                import random, string
                mem["family_code"] = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
                _save()
                st.rerun()
            st.markdown("---")
            st.caption("Hoặc nhập mã gia đình để tham gia:")
            join_col1, join_col2 = st.columns([3, 1])
            with join_col1:
                join_code = st.text_input("Nhập mã gia đình", key="t4_join_code", label_visibility="collapsed", placeholder="Nhập mã 6 ký tự...")
            with join_col2:
                if st.button("Tham gia", key="t4_join_btn"):
                    if join_code and len(join_code) == 6:
                        mem["family_code"] = join_code.upper()
                        _save()
                        st.success("Đã tham gia gia đình!")
                        st.rerun()
                    else:
                        st.error("Mã không hợp lệ")

    # ─── ADD MEMBER ──────────────────────────────────────────────
    with st.expander("➕ Thêm Thành Viên", expanded=(len(family_members) == 0)):
        add_col1, add_col2 = st.columns(2)
        with add_col1:
            new_role = st.selectbox(
                "Vai trò",
                list(FAMILY_ROLES.keys()),
                key="t4_new_role",
            )
        with add_col2:
            new_name = st.text_input("Tên", key="t4_new_name", placeholder="Tên thành viên...")

        new_goal = st.number_input(
            "🎯 Mục tiêu tích lũy (VNĐ)",
            min_value=0,
            max_value=1_000_000_000,
            value=5_000_000,
            step=500_000,
            key="t4_new_goal",
            format="%d",
        )

        if st.button("✅ Thêm Thành Viên", key="t4_add_member"):
            if new_name.strip():
                existing_roles = [m["role"] for m in family_members]
                if new_role in existing_roles:
                    st.warning(f"{new_role} đã có trong gia đình rồi!")
                else:
                    family_members.append({
                        "role":    new_role,
                        "name":    new_name.strip(),
                        "exp":     0,
                        "level":   1,
                        "saved":   0,
                        "goal":    new_goal,
                        "hearts":  0,
                        "streak":  0,
                    })
                    mem["family_members"] = family_members
                    _save()
                    st.success(f"Đã thêm {new_role} {new_name.strip()} vào gia đình! 🎉")
                    st.rerun()
            else:
                st.error("Vui lòng nhập tên thành viên")

    # ─── FAMILY LEADERBOARD ──────────────────────────────────────
    if family_members:
        # Sort by saved desc
        sorted_members = sorted(family_members, key=lambda m: m.get("saved", 0), reverse=True)

        st.markdown("#### 🏆 Bảng Xếp Hạng Gia Đình")

        for rank, member in enumerate(sorted_members, 1):
            _role   = member.get("role", "👤")
            _name   = member.get("name", "")
            _exp    = member.get("exp", 0)
            _lv     = member.get("level", 1)
            _saved  = member.get("saved", 0)
            _goal   = member.get("goal", 5_000_000)
            _hearts = member.get("hearts", 0)
            _streak = member.get("streak", 0)

            _rinfo  = FAMILY_ROLES.get(_role, {"sheep":"🐑","color":"#6b7280","bg":"#f9fafb"})
            _sheep  = _rinfo["sheep"]
            _color  = _rinfo["color"]
            _bg     = _rinfo["bg"]

            # Progress toward goal
            _goal_safe = max(_goal, 1)
            _prog_pct  = min(100, int(_saved / _goal_safe * 100))

            # EXP to next level
            _next_exp  = EXP_LEVELS.get(_lv + 1, EXP_LEVELS.get(_lv, 1))
            _lv_pct    = min(100, int(_exp / max(_next_exp, 1) * 100)) if _lv < 6 else 100

            # Rank badge
            _rank_badge = ["🥇","🥈","🥉"][rank - 1] if rank <= 3 else f"#{rank}"

            # Saved & goal formatted
            _saved_str  = f'{_saved/1_000_000:.1f}tr' if _saved >= 1_000_000 else f'{_saved//1000}k'
            _goal_str   = f'{_goal/1_000_000:.1f}tr'  if _goal  >= 1_000_000 else f'{_goal//1000}k'

            st.markdown(f"""
<div style='background:{_bg};border:2px solid {_color}33;border-radius:16px;
            padding:16px 20px;margin-bottom:12px'>
  <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px'>
    <div style='font-size:26px'>{_rank_badge}</div>
    <div style='font-size:28px'>{_sheep}</div>
    <div style='flex:1'>
      <div style='font-size:15px;font-weight:700;color:{_color}'>{_name}</div>
      <div style='font-size:12px;color:#6b7280'>{_role} · Lv.{_lv} · ❤️ {_hearts} · 🔥 {_streak} ngày</div>
    </div>
    <div style='text-align:right'>
      <div style='font-size:16px;font-weight:800;color:{_color}'>{_saved_str}</div>
      <div style='font-size:11px;color:#6b7280'>/ {_goal_str}</div>
    </div>
  </div>

  <div style='margin-bottom:6px'>
    <div style='display:flex;justify-content:space-between;
                font-size:11px;color:#6b7280;margin-bottom:3px'>
      <span>🎯 Mục tiêu</span>
      <span>{_prog_pct}%</span>
    </div>
    <div style='background:#e5e7eb;border-radius:6px;height:8px'>
      <div style='width:{_prog_pct}%;background:{_color};border-radius:6px;height:100%'></div>
    </div>
  </div>

  <div>
    <div style='display:flex;justify-content:space-between;
                font-size:11px;color:#6b7280;margin-bottom:3px'>
      <span>⭐ EXP Lv.{_lv}</span>
      <span>{_lv_pct}%</span>
    </div>
    <div style='background:#e5e7eb;border-radius:6px;height:6px'>
      <div style='width:{_lv_pct}%;background:linear-gradient(90deg,#f59e0b,#f97316);
                  border-radius:6px;height:100%'></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ─── MEMBER MANAGEMENT ───────────────────────────────────
        st.markdown("#### 💝 Cập Nhật & Tặng Quà")

        selected_member_name = st.selectbox(
            "Chọn thành viên",
            [f'{m["role"]} {m["name"]}' for m in family_members],
            key="t4_select_member",
        )

        sel_idx = next(
            (i for i, m in enumerate(family_members)
             if f'{m["role"]} {m["name"]}' == selected_member_name),
            0,
        )
        sel = family_members[sel_idx]

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            st.markdown("**💰 Ghi nhận tích lũy**")
            add_amount = st.number_input(
                "Số tiền (VNĐ)",
                min_value=10_000,
                max_value=100_000_000,
                value=500_000,
                step=50_000,
                key="t4_add_amount",
                format="%d",
                label_visibility="collapsed",
            )
            if st.button("✅ Ghi Nhận", key="t4_record_btn"):
                family_members[sel_idx]["saved"]  = sel.get("saved", 0) + add_amount
                family_members[sel_idx]["exp"]    = sel.get("exp", 0) + max(1, add_amount // 10_000)
                # Level up check
                new_exp = family_members[sel_idx]["exp"]
                new_lv  = sel.get("level", 1)
                for lv_check in range(new_lv + 1, 7):
                    if new_exp >= EXP_LEVELS.get(lv_check, 999999):
                        new_lv = lv_check
                family_members[sel_idx]["level"] = new_lv
                mem["family_members"] = family_members
                _save()
                st.success(f"✅ Đã ghi nhận {add_amount//1000}k cho {sel['name']}!")
                st.rerun()

        with action_col2:
            st.markdown("**❤️ Tặng Tim Yêu Thương**")
            heart_msg = st.text_input(
                "Lời nhắn",
                key="t4_heart_msg",
                placeholder="Viết lời động viên...",
                label_visibility="collapsed",
            )
            if st.button("❤️ Tặng Tim", key="t4_heart_btn"):
                family_members[sel_idx]["hearts"] = sel.get("hearts", 0) + 1
                mem["family_members"] = family_members
                # Add to journey timeline
                import datetime as _dt4
                mem.setdefault("journey_timeline", []).append({
                    "date":  _dt4.date.today().isoformat(),
                    "icon":  "❤️",
                    "title": f"Tặng tim cho {sel['name']}",
                    "body":  heart_msg or f"Yêu {sel['name']} nhiều lắm! 💕",
                })
                _save()
                st.success(f"❤️ Đã tặng tim cho {sel['name']}!")
                st.rerun()

        # ─── REMOVE MEMBER ───────────────────────────────────────
        with st.expander("🗑️ Xóa thành viên"):
            remove_name = st.selectbox(
                "Chọn thành viên muốn xóa",
                [f'{m["role"]} {m["name"]}' for m in family_members],
                key="t4_remove_select",
            )
            if st.button("🗑️ Xóa", key="t4_remove_btn"):
                mem["family_members"] = [
                    m for m in family_members
                    if f'{m["role"]} {m["name"]}' != remove_name
                ]
                _save()
                st.success(f"Đã xóa {remove_name}")
                st.rerun()

    else:
        # Empty state
        st.markdown("""
<div style='text-align:center;padding:40px 20px;background:#fdf2f8;
            border-radius:16px;border:2px dashed #f9a8d4'>
  <div style='font-size:48px;margin-bottom:12px'>👨‍👩‍👧</div>
  <div style='font-size:16px;font-weight:700;color:#9d174d;margin-bottom:8px'>
    Chưa có thành viên nào
  </div>
  <div style='font-size:13px;color:#6b7280'>
    Thêm thành viên gia đình để cùng nhau tích lũy nhé!<br>
    Mỗi người sẽ có con Cừu riêng, cấp độ riêng, và mục tiêu riêng 🐑💕
  </div>
</div>
""", unsafe_allow_html=True)

    # ─── FAMILY MILESTONE ────────────────────────────────────────
    if family_members:
        total_family_saved = sum(m.get("saved", 0) for m in family_members)
        st.markdown("---")
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#fdf2f8,#f3e8ff);
            border-radius:16px;padding:16px 20px;text-align:center'>
  <div style='font-size:13px;color:#6b7280;margin-bottom:4px'>💰 Tổng tích lũy gia đình</div>
  <div style='font-size:28px;font-weight:800;color:#9d174d'>
    {total_family_saved/1_000_000:.1f} triệu đồng
  </div>
  <div style='font-size:13px;color:#6b7280;margin-top:4px'>
    {len(family_members)} thành viên · Cùng nhau tiến đến ước mơ 🐑
  </div>
</div>
""", unsafe_allow_html=True)
