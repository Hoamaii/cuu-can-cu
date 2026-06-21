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
    "prev_stage_key": "baby",
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
# 5 TABS NAVIGATION
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chia sẻ cảm xúc",
    "📔 Nhật ký tâm sự",
    "❤️ Hành trình nuôi cừu",
    "🧬 Hồ sơ tài chính",
    "🎨 Xem Thiết Kế",
])


# ═══════════════════════════════════════════════════════
# TAB 1 — CHIA SẺ CẢM XÚC  v3.2
# UX: "Người bạn đồng hành — mở app vì muốn gặp Cừu"
# Hierarchy: Mascot → Mình đang nghe → Nhớ về bạn → Tiến bộ → Chips → Chat
# ═══════════════════════════════════════════════════════
with tab1:

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


# ═══════════════════════════════════════════════════════
# TAB 2 — NHẬT KÝ TÂM SỰ  v3.1
# UX: "Mình đang viết cho Cừu" — KHÔNG phải "điền form"
# ═══════════════════════════════════════════════════════
with tab2:
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
# TAB 3 — HÀNH TRÌNH NUÔI CỪU
# UX: Food metaphors, unlock rewards, Moment of Joy/Kindness, dream linkage
# ═══════════════════════════════════════════════════════
with tab3:
    total_saved = mem.get("total_saved", 0)
    stage_key, stage_name, lv_num, stage_desc, stage_msg = get_growth_stage(total_saved)

    _STAGE_REWARDS = {
        "baby":   "🌱 Được gặp bạn lần đầu",
        "child":  "💌 Cừu nhớ tên bạn rồi",
        "teen":   "🌙 Cừu kể chuyện buổi tối",
        "adult":  "✨ Cừu đặt tên theo giấc mơ",
        "master": "🏆 Cừu Lão Luyện — đồng hành mãi mãi",
    }

    col_left, col_right = st.columns([2, 3])

    # ── LEFT: Sheep + unlock roadmap ──
    with col_left:
        show_growth_sheep(total_saved, width=200)

        st.markdown(
            '<p style="font-size:0.85rem;font-weight:700;color:#C4607F;margin:14px 0 6px;">'
            '🗺️ Hành trình của Cừu</p>',
            unsafe_allow_html=True,
        )
        for i, (thresh, skey, sname, slv, sdesc, _) in enumerate(GROWTH_STAGES):
            is_current  = skey == stage_key
            is_unlocked = total_saved >= thresh
            _reward     = _STAGE_REWARDS.get(skey, "")
            if is_current:
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#FFF0F5,#FFE4F0);'
                    f'border:2px solid #FFB5C8;border-radius:12px;padding:10px 12px;margin:4px 0;">'
                    f'<div style="font-size:0.8rem;font-weight:800;color:#C4607F;">▶ {sname}</div>'
                    f'<div style="font-size:0.72rem;color:#999;margin-top:2px;">{_reward}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            elif is_unlocked:
                st.markdown(
                    f'<div style="background:#F8F8F8;border:1.5px solid #E0E0E0;'
                    f'border-radius:12px;padding:8px 12px;margin:4px 0;opacity:0.72;">'
                    f'<div style="font-size:0.78rem;font-weight:700;color:#AAA;text-decoration:line-through;">{sname}</div>'
                    f'<div style="font-size:0.7rem;color:#CCC;">✅ Đã mở khóa · {_reward}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:#FAFAFA;border:1.5px dashed #E0CCF0;'
                    f'border-radius:12px;padding:8px 12px;margin:4px 0;">'
                    f'<div style="font-size:0.78rem;font-weight:700;color:#C0A8D8;">🔒 {sname}</div>'
                    f'<div style="font-size:0.7rem;color:#CCC;margin-top:2px;">'
                    f'Cần {fmt(thresh)} · {_reward}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ── RIGHT: Main interaction ──
    with col_right:

        # PHẦN 1: Hero in Cừu's first-person voice
        _hero_lines = {
            "baby":   ("🥕", f"\"Mình vừa ra đời... còn bé lắm 🐑<br/>Cho mình ăn bữa đầu tiên nhé?\""),
            "child":  ("🍎", f"\"Mình lớn hơn rồi nhờ {mem.get('name','bạn')} đấy!<br/>Hôm nay cho mình ăn tiếp không?\""),
            "teen":   ("🎂", f"\"Mình đang lớn nhanh lắm~<br/>Cùng nhau đến đích thôi {mem.get('name','bạn')} ơi!\""),
            "adult":  ("🎉", f"\"Chúng mình đã đi được nửa đường rồi.<br/>Mình tự hào về {mem.get('name','bạn')} lắm ❤️\""),
            "master": ("🌟", f"\"Nhìn chúng mình đến đây...<br/>Cảm ơn {mem.get('name','bạn')} đã không bỏ cuộc 🏆\""),
        }
        _hfood, _htxt = _hero_lines.get(stage_key, _hero_lines["baby"])
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
            f'border-radius:16px;padding:16px 20px;text-align:center;margin-bottom:14px;">'
            f'<div style="font-size:2.2rem;">{_hfood}</div>'
            f'<div style="font-size:0.97rem;color:#C4607F;font-style:italic;margin-top:8px;line-height:1.6;">'
            f'{_htxt}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # PHẦN 5: Moment of Joy (celebration after feeding)
        if st.session_state.get("feeding_celebration"):
            fed_amt   = mem.get("last_fed_amount", 0)
            fed_food  = mem.get("last_fed_food", "")
            leveled   = mem.get("just_leveled_up", False)
            cur_key, cur_name, *_ = get_growth_stage(total_saved)
            cel_src   = _b64(_pick_mascot("celebrate"))

            _dream_link_html = ""
            if mem["dreams"]:
                _top_d      = mem["dreams"][0]
                _top_d_name = _top_d.get("name", "").title()
                _dream_link_html = (
                    f'<div style="background:rgba(255,215,0,0.15);border-radius:10px;'
                    f'padding:8px 14px;margin-top:10px;font-size:0.87rem;color:#B8860B;">'
                    f'✨ Giấc mơ <strong>{_top_d_name}</strong> vừa tiến thêm '
                    f'<strong>{fmt(fed_amt)}</strong>~</div>'
                )

            _leveled_html = ""
            if leveled:
                _leveled_html = (
                    f'<div style="font-size:1.1rem;font-weight:800;color:#C4607F;margin-top:12px;">'
                    f'🎊 Cừu vừa lớn thêm một giai đoạn! Chào mừng đến với {cur_name}!</div>'
                )

            _food_label = fed_food if fed_food else fmt(fed_amt)
            st.markdown(
                f'<div class="celebration-box" style="text-align:center;">'
                f'<img src="{cel_src}" width="100" style="border-radius:50%;border:4px solid #FFB5C8;" />'
                f'<div style="font-size:1.4rem;margin:6px 0;">🎉</div>'
                f'<strong style="font-size:1.05rem;color:#C4607F;">'
                f'Cừu được ăn {_food_label} rồi — bê bê cảm ơn bạn ❤️</strong>'
                f'{_dream_link_html}'
                f'{_leveled_html}'
                f'</div>',
                unsafe_allow_html=True,
            )
            mem["just_leveled_up"] = False
            mem["last_fed_amount"] = 0
            mem["last_fed_food"]   = ""
            st.session_state.feeding_celebration = False
            _save()
            st.balloons()

        # PHẦN 6: Moment of Kindness (skip — zero guilt)
        if st.session_state.get("feeding_refused"):
            kind_src = _b64(_pick_mascot("listening"))
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#F0F8FF,#EAF4FF);'
                f'border-radius:16px;padding:16px 20px;text-align:center;margin-bottom:12px;">'
                f'<img src="{kind_src}" width="76" style="border-radius:50%;border:3px solid #B5D8FF;" />'
                f'<div style="font-size:1rem;font-weight:700;color:#5B8DB8;margin-top:8px;">'
                f'Không sao cả 🌙</div>'
                f'<div style="font-size:0.88rem;color:#6A9BBF;margin-top:5px;">'
                f'Mình vẫn ở đây. Hôm nào sẵn sàng thì mình vẫn đợi~ 🐑</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.session_state.feeding_refused = False

        # PHẦN 2: Feed buttons — food metaphors
        st.markdown(
            '<p style="font-size:0.97rem;font-weight:700;color:#C4607F;margin:10px 0 6px;">'
            '🍽️ Hôm nay cho Cừu ăn gì?</p>',
            unsafe_allow_html=True,
        )
        _feed_cols = st.columns(4)
        for i, (amt, food_emoji, food_name) in enumerate(FEED_OPTIONS):
            if _feed_cols[i].button(
                f"{food_emoji} {food_name}\n{fmt(amt)}",
                use_container_width=True,
                key=f"feed_{amt}",
                type="primary",
            ):
                _prev_key = stage_key
                mem["total_saved"]     += amt
                mem["streak"]          += 1
                mem["last_fed_amount"]  = amt
                mem["last_fed_food"]    = f"{food_emoji} {food_name}"
                mem["last_fed_date"]    = datetime.now().strftime("%Y-%m-%d")
                _new_key, *_ = get_growth_stage(mem["total_saved"])
                if _new_key != _prev_key:
                    mem["just_leveled_up"] = True
                set_mood("happy")
                st.session_state.feeding_celebration = True
                st.session_state.feeding_refused     = False
                _save()
                st.rerun()

        with st.expander("🔢 Nhập số tiền khác"):
            custom = st.number_input(
                "Số tiền:", min_value=1_000, max_value=100_000_000,
                step=10_000, value=30_000, key="custom_amt",
            )
            if st.button(f"🐑 Đầu tư {fmt(int(custom))}", type="primary", use_container_width=True):
                _prev_key = stage_key
                mem["total_saved"]    += int(custom)
                mem["streak"]         += 1
                mem["last_fed_amount"] = int(custom)
                mem["last_fed_food"]   = fmt(int(custom))
                _new_key, *_ = get_growth_stage(mem["total_saved"])
                if _new_key != _prev_key:
                    mem["just_leveled_up"] = True
                set_mood("happy")
                st.session_state.feeding_celebration = True
                _save()
                st.rerun()

        # PHẦN 9: Dream linkage cards
        if mem["dreams"]:
            st.markdown("---")
            st.markdown(
                '<p style="font-size:0.97rem;font-weight:700;color:#C4607F;margin-bottom:8px;">'
                '🎯 Giấc mơ đang được nuôi</p>',
                unsafe_allow_html=True,
            )
            for d in mem["dreams"][:3]:
                with st.container(border=True):
                    da, db = st.columns([3, 2])
                    with da:
                        st.markdown(f"**✨ {d['name'].title()}**")
                        if d["amount"] > 0:
                            pct = min(100, d["saved"] / d["amount"] * 100)
                            st.progress(pct / 100, text=f"{pct:.1f}% — còn {fmt(d['amount'] - d['saved'])}")
                    with db:
                        if d["amount"] > 0 and d["saved"] < d["amount"]:
                            if st.button("❤️ +50k", key=f"dream_{d['name']}", type="primary"):
                                d["saved"]             = min(d["amount"], d["saved"] + 50_000)
                                mem["total_saved"]    += 50_000
                                mem["last_fed_amount"] = 50_000
                                mem["last_fed_food"]   = f"❤️ cho {d['name'].title()}"
                                set_mood("celebrate" if d["saved"] >= d["amount"] else "happy")
                                st.session_state.feeding_celebration = True
                                _save()
                                st.rerun()
                        elif d["amount"] > 0:
                            st.success("🎉 Hoàn thành!")
        else:
            st.markdown("---")
            st.info("💭 Kể với Cừu về giấc mơ của bạn ở tab **💬 Chia sẻ cảm xúc** nhé!")

        # Skip for today
        st.markdown("---")
        if st.button("🌙 Hôm nay chưa sẵn sàng", use_container_width=True):
            set_mood("sad")
            st.session_state.feeding_refused     = True
            st.session_state.feeding_celebration = False
            _save()
            st.rerun()

    # ── PHẦN 7+8: Plain-language fund cards + Cừu's voice recommender ──
    st.markdown("---")
    st.markdown(
        '<p style="font-size:1.05rem;font-weight:800;color:#C4607F;margin-bottom:2px;">'
        '🐑 Cừu Giải Thích Quỹ Đầu Tư</p>'
        '<p style="font-size:0.8rem;color:#AAA;margin-bottom:14px;">'
        'Kiến thức đơn giản · Không hứa lợi nhuận · Không khuyến nghị mua bán</p>',
        unsafe_allow_html=True,
    )

    _FUND_ANALOGIES = {
        "TCEF": (
            "🌳 Trồng cây ăn quả",
            "Cần kiên nhẫn 3–5 năm, nhưng khi cây ra trái thì ngọt lắm. "
            "Giá trị lên xuống theo thị trường — nhưng dài hạn thường đi lên.",
        ),
        "TCBF": (
            "🪣 Bình nước dự phòng",
            "Không sinh lời nhanh, nhưng ổn định và ít biến động. "
            "Phù hợp khi bạn cần dùng tiền trong 1–3 năm tới.",
        ),
        "TCFF": (
            "🎒 Balo cân bằng",
            "Vừa cổ phiếu vừa trái phiếu — không quá cay, không quá nhạt. "
            "Lý tưởng cho ai chưa chắc về khẩu vị rủi ro của mình.",
        ),
    }

    _fc1, _fc2, _fc3 = st.columns(3)
    for _fcol, _fkey in zip([_fc1, _fc2, _fc3], ["TCEF", "TCBF", "TCFF"]):
        _f = FUNDS[_fkey]
        _a_title, _a_desc = _FUND_ANALOGIES[_fkey]
        with _fcol:
            st.markdown(
                f'<div style="background:white;border:2px solid #FFD6E8;border-radius:16px;'
                f'padding:16px;min-height:190px;">'
                f'<div style="font-size:1.5rem;text-align:center;">{_f["emoji"]}</div>'
                f'<div style="font-size:0.83rem;font-weight:800;color:#C4607F;'
                f'text-align:center;margin-top:6px;">{_a_title}</div>'
                f'<div style="font-size:0.77rem;color:#555;margin-top:8px;line-height:1.55;">'
                f'{_a_desc}</div>'
                f'<div style="font-size:0.68rem;color:#CCC;margin-top:10px;">'
                f'{_f["tên"]} · {_f["rủi_ro"]} · {_f["phù_hợp"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Cừu's voice recommender (uses user memory)
    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.95rem;font-weight:700;color:#C4607F;margin-bottom:8px;">'
        '🤔 Hỏi Cừu — Quỹ nào phù hợp với mình?</p>',
        unsafe_allow_html=True,
    )
    _ry1, _ry2 = st.columns(2)
    with _ry1:
        y_opt = st.selectbox(
            "Mục tiêu bao lâu?", [1, 2, 3, 5],
            format_func=lambda x: f"{x} năm", key="rec_y",
        )
    with _ry2:
        r_opt = st.selectbox(
            "Khẩu vị rủi ro?",
            ["low", "medium", "high"],
            format_func=lambda x: {
                "low":    "🌿 Thấp — hay lo lắng",
                "medium": "🌊 Trung bình — cân bằng",
                "high":   "⚡ Cao — chấp nhận biến động",
            }[x],
            key="rec_r",
        )

    rf_key = recommend_fund(y_opt, r_opt)
    rf     = FUNDS[rf_key]
    _rf_a_title, _rf_a_desc = _FUND_ANALOGIES[rf_key]

    _user_name_rec = mem.get("name", "bạn")
    _risk_label    = {"low": "thấp", "medium": "trung bình", "high": "cao"}[r_opt]
    _dream_ctx_rec = ""
    if mem["dreams"]:
        _dream_ctx_rec = (
            f'Mình biết {_user_name_rec} đang mơ đến '
            f'<strong>{mem["dreams"][0]["name"].title()}</strong> — '
        )

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);'
        f'border-radius:16px;padding:18px 20px;margin-top:8px;">'
        f'<div style="font-size:0.88rem;color:#C4607F;font-style:italic;margin-bottom:8px;">'
        f'🐑 Cừu nói với {_user_name_rec}:</div>'
        f'<div style="font-size:0.93rem;color:#444;line-height:1.7;">'
        f'{_dream_ctx_rec}với mục tiêu <strong>{y_opt} năm</strong> và khẩu vị '
        f'<strong>{_risk_label}</strong>, mình nghĩ <strong>{rf["emoji"]} {_rf_a_title}</strong> '
        f'hợp với {_user_name_rec} nhất.<br/><br/>'
        f'<span style="font-size:0.84rem;color:#777;">{_rf_a_desc}</span><br/><br/>'
        f'<span style="font-size:0.73rem;color:#BBB;">'
        f'⚠️ Đây chỉ là gợi ý tham khảo, không phải tư vấn đầu tư chuyên nghiệp.</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    with st.expander("📚 Kiến thức đầu tư cơ bản"):
        for _pk, _pp in INVESTMENT_PRINCIPLES.items():
            st.markdown(f"**{_pp['tên']}**")
            st.markdown(_pp["nội_dung"])
            st.markdown("---")


# ═══════════════════════════════════════════════════════
# TAB 4 — HỒ SƠ TÀI CHÍNH
# ═══════════════════════════════════════════════════════
with tab4:
    col_p1, col_p2 = st.columns([1, 4])
    with col_p1:
        show_sheep("determined", width=160)
    with col_p2:
        st.title("🧬 Hồ Sơ Tài Chính")
        st.markdown("*Cừu xây dựng hồ sơ dựa trên câu chuyện của bạn* 🌟")

    st.markdown("---")

    genome   = mem.get("wealth_genome", {})
    has_data = any([mem["dreams"], mem["life_events"], mem["notes"], mem["total_saved"] > 0])

    if not has_data:
        show_sheep("miss_you", width=130)
        st.info(
            "**Hồ sơ tài chính đang trống** 🌿\n\n"
            "Hãy chia sẻ chuyện ở tab **💬 Chia sẻ cảm xúc** "
            "hoặc viết **📔 Nhật ký tâm sự** — Cừu sẽ tự xây dựng hồ sơ cho bạn!"
        )
    else:
        stage_key_p, stage_name_p, lv_num_p, stage_desc_p, _ = get_growth_stage(mem["total_saved"])
        stage_src_p = _b64(_pick_mascot(stage_key_p))

        # ── Profile card ──
        st.markdown(
            f'<div style="background:white;border-radius:20px;'
            f'border:2px solid #FFD6E8;padding:24px;'
            f'box-shadow:0 4px 24px rgba(255,150,200,0.15);margin-bottom:20px;">'
            f'<div style="text-align:center;margin-bottom:16px;">'
            f'<img src="{stage_src_p}" width="120" style="border-radius:50%;border:4px solid #FFB5C8;" /><br/>'
            f'<strong style="font-size:1.2rem;color:#C4607F;">{stage_name_p}</strong><br/>'
            f'<span style="color:#888;">{stage_desc_p}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 💭 Giấc mơ")
            if mem["dreams"]:
                for d in mem["dreams"][:3]:
                    st.markdown(f"**✨ {d['name'].title()}**")
                    if d["amount"] > 0:
                        pct = min(100, d["saved"] / d["amount"] * 100)
                        st.progress(pct / 100, text=f"{pct:.0f}%")
            else:
                st.caption("Chưa xác định")

            st.markdown("#### 🏷️ Sự kiện cuộc sống")
            if mem["life_events"]:
                for t in list(dict.fromkeys(mem["life_events"]))[:6]:
                    st.markdown(f"• {LIFE_EVENT_LABELS.get(t, t)}")
            else:
                st.caption("Chưa có")

            st.markdown("#### 💰 Tích lũy")
            st.markdown(
                f'<span style="background:linear-gradient(135deg,#FF8FAF,#7EC8E3);'
                f'color:white;border-radius:20px;padding:4px 14px;'
                f'font-weight:700;">{stage_name_p}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"Đã tích lũy: **{fmt(mem['total_saved'])}** · Streak: **{mem['streak']} ngày**")

        with c2:
            st.markdown("#### 🛡️ Khẩu vị rủi ro")
            risk_ans = st.radio(
                "Nếu đầu tư 10 triệu và còn 8 triệu:",
                ["😰 Bán ngay, không dám chờ",
                 "🤔 Chờ xem, cân nhắc thêm",
                 "😎 Không lo, thậm chí mua thêm"],
                key="profile_risk",
            )
            risk_map = {
                "😰 Bán ngay, không dám chờ":  ("low",    "🌿 Ưa ổn định",  "TCBF"),
                "🤔 Chờ xem, cân nhắc thêm":    ("medium", "🌊 Cân bằng",    "TCFF"),
                "😎 Không lo, thậm chí mua thêm":("high",  "⚡ Dám rủi ro",  "TCEF"),
            }
            r_val, r_label, r_fund = risk_map[risk_ans]
            genome["risk_type"] = r_label
            _save()
            st.markdown(f"**{r_label}** · Quỹ tham khảo: **{r_fund}**")

            st.markdown("#### 🔥 Động lực")
            motive = st.selectbox("Bạn tích lũy vì:", [
                "Muốn an tâm về tương lai",
                "Có giấc mơ muốn thực hiện",
                "Trách nhiệm với gia đình",
                "Muốn tự do tài chính",
                "Đang thử nghiệm, chưa chắc",
            ], key="profile_motive")
            genome["personality"] = motive
            _save()

            st.markdown("#### 📈 Giai đoạn")
            stage_p = st.selectbox("Bạn đang ở:", [
                "🌱 Mới bắt đầu tích lũy",
                "🌿 Đang hình thành thói quen",
                "🌳 Đã có nền tảng vững",
                "🌴 Tối ưu hóa danh mục",
            ], key="profile_stage")
            genome["stage"] = stage_p
            _save()

        st.markdown("---")
        st.subheader("💡 Gợi ý từ Cừu Coach")
        rf_key2 = recommend_fund(3, r_val)
        rf2     = FUNDS[rf_key2]
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            with st.container(border=True):
                st.markdown(f"**{rf2['emoji']} {rf_key2}**")
                st.caption(rf2["mô_tả"])
        with cc2:
            with st.container(border=True):
                st.markdown("**🔄 Đầu tư đều đặn**")
                st.caption("Cố định mỗi tháng, không cần chọn thời điểm.")
        with cc3:
            with st.container(border=True):
                st.markdown("**📅 Kiên nhẫn dài hạn**")
                st.caption("Nhìn vào 3-5 năm, đừng lo biến động ngắn hạn.")

        st.warning(
            "⚠️ **Lưu ý:** Tất cả thông tin chỉ mang tính tham khảo và giáo dục tài chính cơ bản. "
            "Cừu Cần Cù KHÔNG phải công ty tư vấn đầu tư được cấp phép. "
            "Hãy tự nghiên cứu và/hoặc tham khảo chuyên gia trước khi ra quyết định đầu tư."
        )

    # ── TAB 5: Interactive Design Demo ──────────────────────────────────
    with tab5:
        _PROTO_HTML = """
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:100%;height:100%;overflow:hidden;}
.root{
  width:860px;height:820px;position:relative;overflow:hidden;
  font-family:-apple-system,'SF Pro Display','Segoe UI',sans-serif;
}

/* ── SKY & SCENE ── */
.sky{
  position:absolute;inset:0;
  background:linear-gradient(180deg,#5BBCF8 0%,#A8DCFF 38%,#C8EFA0 55%,#7DC95E 68%,#5AAD3C 100%);
}
.sun{position:absolute;top:20px;right:200px;width:52px;height:52px;
  background:radial-gradient(circle,#FFE45E,#FFB800);border-radius:50%;
  box-shadow:0 0 30px 10px rgba(255,220,60,0.45);}
.cloud{position:absolute;animation:cloud-drift linear infinite;}
.cloud-shape{background:#fff;border-radius:50px;box-shadow:inset 0 -2px 4px rgba(0,0,0,0.05);}
@keyframes cloud-drift{from{transform:translateX(-120px)}to{transform:translateX(920px)}}

/* ── HILLS ── */
.hill{position:absolute;border-radius:50%;}
.h1{width:580px;height:240px;background:#6EC446;bottom:192px;left:-100px;}
.h2{width:480px;height:200px;background:#5DBB36;bottom:182px;right:-80px;}
.h3{width:360px;height:160px;background:#7DD458;bottom:208px;left:160px;}

/* ── GROUND ── */
.ground{
  position:absolute;bottom:0;left:0;right:0;height:240px;
  background:linear-gradient(180deg,#6EC446 0%,#4E9A2A 50%,#3D7A20 100%);
}

/* ── FENCE ── */
.fence{position:absolute;bottom:168px;left:0;right:0;height:36px;pointer-events:none;}
.fence svg{width:100%;height:100%;}

/* ── FARMHOUSE ── */
.farmhouse{position:absolute;bottom:215px;right:155px;width:130px;text-align:center;}
.fh-roof{width:0;height:0;border-left:65px solid transparent;border-right:65px solid transparent;border-bottom:50px solid #C0522A;margin:0 auto;}
.fh-chimney{width:14px;height:24px;background:#9A3D1A;position:absolute;top:-24px;right:28px;border-radius:2px 2px 0 0;}
.fh-body{background:#8B6340;height:70px;border-radius:0 0 4px 4px;position:relative;display:flex;align-items:center;justify-content:center;gap:8px;}
.fh-window{width:22px;height:22px;background:rgba(255,220,100,0.85);border:3px solid #6A4820;border-radius:4px;box-shadow:0 0 8px rgba(255,200,50,0.6);}
.fh-door{width:20px;height:32px;background:#5A3010;border:2px solid #3A1A00;border-radius:10px 10px 0 0;position:absolute;bottom:0;}

/* ── WINDMILL ── */
.windmill{position:absolute;bottom:220px;right:300px;}
.wm-tower{width:20px;height:60px;background:linear-gradient(180deg,#C8A870,#A07840);margin:0 auto;border-radius:2px;}
.wm-hub{width:14px;height:14px;background:#8B6010;border-radius:50%;position:absolute;top:-7px;left:3px;}
.wm-blades{position:absolute;top:-40px;left:-20px;width:54px;height:54px;animation:spin-blade 5s linear infinite;}
@keyframes spin-blade{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
.wm-blade{position:absolute;width:22px;height:7px;background:#D4A050;border-radius:4px;transform-origin:right center;}

/* ── POND ── */
.pond{
  position:absolute;bottom:148px;right:108px;width:110px;height:52px;
  background:radial-gradient(ellipse,#64C8F8 0%,#3A9ED8 100%);
  border-radius:50%;border:3px solid #2A80C0;
  box-shadow:0 2px 12px rgba(58,158,216,0.5);
}
.pond-bridge{
  position:absolute;bottom:155px;right:142px;
  width:36px;height:14px;
  background:linear-gradient(180deg,#C8A870,#A07840);
  border-radius:0 0 18px 18px;border:2px solid #8B6010;
}

/* ── PATCHES ── */
.patch{position:absolute;font-size:14px;}

/* ── TREES ── */
.tree{position:absolute;}
.tree-trunk{width:12px;height:28px;background:linear-gradient(180deg,#8B6040,#6A4020);border-radius:2px;margin:0 auto;}
.tree-foliage{border-radius:50%;position:absolute;top:0;}

/* ── BABY SHEEP ── */
.bsheep{position:absolute;font-size:28px;text-align:center;}
.zzz{position:absolute;font-size:10px;color:#8888aa;font-weight:700;top:-18px;right:-6px;animation:zzz-float 2s ease-in-out infinite;}
@keyframes zzz-float{0%,100%{opacity:0.6;transform:translateY(0)}50%{opacity:1;transform:translateY(-6px)}}

/* ── MASCOT ── */
.mascot{
  position:absolute;bottom:195px;left:50%;transform:translateX(-50%);
  width:140px;z-index:12;cursor:pointer;
  animation:mascot-idle 2.8s ease-in-out infinite;
  filter:drop-shadow(0 12px 24px rgba(0,0,0,0.3));
  transition:filter 0.3s;
}
@keyframes mascot-idle{0%,100%{transform:translateX(-50%) translateY(0)}50%{transform:translateX(-50%) translateY(-12px)}}
.mascot:hover{filter:drop-shadow(0 16px 32px rgba(255,215,0,0.5));}

/* ── KNOTTED CRATE ── */
.kho-thoc{
  position:absolute;bottom:82px;right:20px;
  background:linear-gradient(135deg,#C8A040,#A07828);
  border:3px solid #8B6010;border-radius:10px;
  padding:8px 12px;z-index:90;text-align:center;
  box-shadow:2px 4px 12px rgba(0,0,0,0.25);
}
.kho-label{font-size:9px;font-weight:700;color:#FFF0C0;}
.kho-count{font-size:16px;font-weight:800;color:#FFE050;}

/* ── TOP BAR ── */
.top-bar{
  position:absolute;top:10px;left:10px;right:10px;height:62px;
  background:rgba(255,255,255,0.92);backdrop-filter:blur(20px);
  border-radius:22px;border:1.5px solid rgba(255,255,255,0.8);
  box-shadow:0 4px 24px rgba(0,0,0,0.14);
  display:flex;align-items:center;padding:0 14px;gap:10px;z-index:100;
}
.tb-avatar{
  width:42px;height:42px;border-radius:50%;
  background:linear-gradient(135deg,#FFD700,#FF8C00);
  border:2.5px solid #FFD700;
  display:flex;align-items:center;justify-content:center;
  font-size:22px;flex-shrink:0;
  box-shadow:0 0 0 2px rgba(255,215,0,0.5);
}
.tb-info{flex:1;min-width:0;}
.tb-name{font-size:11px;font-weight:800;color:#1A1A2E;letter-spacing:0.1px;}
.tb-sub{font-size:9px;color:#888;margin:1px 0;}
.tb-xp{display:flex;align-items:center;gap:5px;margin-top:3px;}
.tb-xp-track{height:6px;background:#E8E0F0;border-radius:3px;width:110px;overflow:hidden;}
.tb-xp-fill{height:100%;width:65%;background:linear-gradient(90deg,#FFD700,#FFA500);border-radius:3px;}
.tb-xp-label{font-size:8px;color:#AAA;}
.tb-star{font-size:14px;margin-left:2px;}
.tb-currencies{display:flex;align-items:center;gap:6px;}
.tb-coin{
  display:flex;align-items:center;gap:4px;
  background:#FFF8E0;border:1.5px solid #FFD700;
  border-radius:16px;padding:4px 10px;
  font-size:11px;font-weight:800;color:#7B4F00;
}
.tb-gem{
  display:flex;align-items:center;gap:4px;
  background:#EEF4FF;border:1.5px solid #6096FF;
  border-radius:16px;padding:4px 10px;
  font-size:11px;font-weight:800;color:#2050C0;
}
.tb-plus{
  width:24px;height:24px;background:linear-gradient(135deg,#48BB78,#2F9E56);
  border-radius:50%;border:none;color:#fff;font-size:16px;
  cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;
}
.tb-bell{
  width:36px;height:36px;background:rgba(0,0,0,0.06);border-radius:50%;
  border:none;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;
  position:relative;
}
.tb-bell-dot{position:absolute;top:5px;right:5px;width:8px;height:8px;background:#FC8181;border-radius:50%;border:1.5px solid #fff;}

/* ── SPEECH BUBBLE ── */
.speech-bubble{
  position:absolute;top:82px;right:178px;z-index:88;
  background:rgba(255,255,255,0.97);backdrop-filter:blur(16px);
  border-radius:16px;padding:11px 13px;max-width:188px;
  border:1.5px solid rgba(255,255,255,0.9);
  box-shadow:0 4px 20px rgba(0,0,0,0.13);
}
.speech-bubble::after{
  content:"";position:absolute;right:-10px;top:18px;
  border:6px solid transparent;border-left:10px solid rgba(255,255,255,0.97);
}
.sb-msg{font-size:10.5px;color:#2D3748;line-height:1.55;font-weight:500;}
.sb-react{font-size:13px;margin-top:5px;}

/* ── LEFT NAV ── */
.left-nav{
  position:absolute;left:10px;top:84px;
  display:flex;flex-direction:column;gap:7px;z-index:90;
}
.nav-btn{
  width:64px;background:rgba(255,255,255,0.94);
  border-radius:16px;padding:10px 4px 8px;
  display:flex;flex-direction:column;align-items:center;gap:3px;
  cursor:pointer;border:1.5px solid rgba(255,255,255,0.8);
  box-shadow:0 3px 12px rgba(0,0,0,0.12);
  transition:transform 0.15s,box-shadow 0.15s;position:relative;
}
.nav-btn:hover{transform:scale(1.06) translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,0.18);}
.nav-btn-icon{font-size:24px;}
.nav-btn-label{font-size:8.5px;font-weight:700;color:#4A5568;text-align:center;}
.nav-badge{
  position:absolute;top:4px;right:4px;
  background:#FF4444;color:#fff;font-size:9px;font-weight:800;
  border-radius:10px;padding:1px 5px;border:1.5px solid #fff;
}

/* ── LEVEL SIGNBOARD ── */
.signboard{
  position:absolute;right:10px;top:84px;
  width:150px;z-index:90;
}
.sign-top{
  background:linear-gradient(180deg,#C8A040,#A07828);
  border:3px solid #8B6010;border-radius:12px 12px 0 0;
  padding:12px 12px 10px;text-align:center;
  box-shadow:3px 3px 0 #6A4810;
}
.sign-lv{font-size:20px;font-weight:900;color:#FFF0A0;text-shadow:0 2px 4px rgba(0,0,0,0.3);}
.sign-name{font-size:10px;font-weight:700;color:#FFE080;margin:2px 0;}
.sign-bar-wrap{height:8px;background:rgba(0,0,0,0.25);border-radius:4px;overflow:hidden;margin-top:6px;}
.sign-bar-fill{height:100%;width:65%;background:linear-gradient(90deg,#FFD700,#FFA500);border-radius:4px;}
.sign-pct{font-size:8px;color:#FFD090;margin-top:3px;}
.sign-post{width:10px;height:22px;background:#A07828;margin:0 auto;border:2px solid #8B6010;}

/* ── FRIENDS CARD ── */
.friends-card{
  position:absolute;right:10px;z-index:90;width:150px;
  background:rgba(255,255,255,0.95);backdrop-filter:blur(12px);
  border-radius:14px;padding:11px;border:1.5px solid rgba(255,255,255,0.8);
  box-shadow:0 3px 16px rgba(0,0,0,0.11);
}
.fc-title{font-size:10px;font-weight:700;color:#2D3748;margin-bottom:8px;}
.fc-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;}
.fc-item{display:flex;flex-direction:column;align-items:center;gap:2px;cursor:pointer;}
.fc-avatar{
  width:34px;height:34px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:16px;border:2px solid #fff;
  box-shadow:0 2px 6px rgba(0,0,0,0.15);
  transition:transform 0.15s;
}
.fc-avatar:hover{transform:scale(1.12);}
.fc-name{font-size:6.5px;color:#4A5568;font-weight:600;text-align:center;max-width:40px;}

/* ── MISSIONS ── */
.missions-card{
  position:absolute;bottom:82px;left:86px;z-index:90;width:244px;
  background:rgba(255,255,255,0.97);backdrop-filter:blur(16px);
  border-radius:18px;padding:13px 14px;
  border:1.5px solid rgba(255,255,255,0.85);
  box-shadow:0 4px 22px rgba(0,0,0,0.13);
}
.mc-title{font-size:11.5px;font-weight:800;color:#1A1A2E;margin-bottom:9px;}
.mc-sub{font-size:9px;color:#888;margin-bottom:8px;font-weight:600;}
.mc-row{display:flex;align-items:center;gap:7px;padding:4px 2px;border-bottom:1px solid rgba(0,0,0,0.05);cursor:pointer;border-radius:6px;transition:background 0.1s;}
.mc-row:last-child{border-bottom:none;}
.mc-row:hover{background:rgba(0,0,0,0.025);}
.mc-icon{font-size:14px;width:18px;text-align:center;flex-shrink:0;}
.mc-info{flex:1;}
.mc-name{font-size:9.5px;font-weight:700;color:#2D3748;}
.mc-prog-wrap{height:3px;background:#EEE;border-radius:2px;margin-top:2px;overflow:hidden;}
.mc-prog-fill{height:100%;background:linear-gradient(90deg,#68D391,#38A169);border-radius:2px;transition:width 0.5s;}
.mc-check{font-size:14px;flex-shrink:0;}
.mc-row.done .mc-name{color:#38A169;text-decoration:line-through;opacity:0.6;}

/* ── FEED BUTTON ── */
.feed-btn{
  position:absolute;bottom:84px;left:50%;transform:translateX(-50%);
  background:linear-gradient(135deg,#FF9500,#FF6D00);
  border:none;border-radius:36px;padding:16px 38px;
  font-size:15px;font-weight:900;color:#fff;
  letter-spacing:0.2px;cursor:pointer;white-space:nowrap;z-index:95;
  text-shadow:0 1px 3px rgba(0,0,0,0.25);
  box-shadow:0 4px 0 #CC5500,0 6px 20px rgba(255,109,0,0.5);
  animation:feed-pulse 2.2s ease-in-out infinite;
}
@keyframes feed-pulse{0%,100%{box-shadow:0 4px 0 #CC5500,0 6px 22px rgba(255,109,0,0.5)}50%{box-shadow:0 4px 0 #CC5500,0 8px 36px rgba(255,149,0,0.8),0 0 60px rgba(255,200,0,0.4)}}
.feed-btn:active{transform:translateX(-50%) translateY(3px);box-shadow:0 1px 0 #CC5500,0 2px 10px rgba(255,109,0,0.4);}

/* ── BOTTOM TAB BAR ── */
.tab-bar{
  position:absolute;bottom:0;left:0;right:0;height:70px;
  background:rgba(255,255,255,0.97);backdrop-filter:blur(20px);
  border-top:1.5px solid rgba(0,0,0,0.07);
  display:flex;align-items:center;padding:0 12px;z-index:100;
}
.tab-item{
  flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;
  cursor:pointer;padding:8px 4px;border-radius:12px;transition:background 0.15s;
}
.tab-item:hover{background:rgba(0,0,0,0.04);}
.tab-icon{font-size:20px;}
.tab-label{font-size:9.5px;font-weight:600;color:#B0B8C8;}
.tab-item.active .tab-label{color:#FF8C00;font-weight:800;}
.tab-item.active .tab-icon{filter:saturate(2);}
.tab-dot{width:5px;height:5px;border-radius:3px;background:#FF8C00;margin-top:-1px;}

/* ── TOAST ── */
.toast{
  position:absolute;top:82px;left:50%;
  transform:translateX(-50%) translateY(-16px);
  background:linear-gradient(135deg,#38A169,#2F855A);
  color:#fff;padding:9px 20px;border-radius:28px;
  font-size:12px;font-weight:700;opacity:0;pointer-events:none;z-index:200;
  transition:opacity 0.3s,transform 0.3s;white-space:nowrap;
  box-shadow:0 4px 20px rgba(0,0,0,0.2);
}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
.confetti-p{position:absolute;pointer-events:none;z-index:200;animation:c-fall 1.3s ease-out forwards;}
@keyframes c-fall{0%{opacity:1;transform:translateY(0) rotate(0deg) scale(1)}100%{opacity:0;transform:translateY(200px) rotate(720deg) scale(0.4)}}
</style>

<div class="root" id="root">
  <!-- SKY -->
  <div class="sky">
    <div class="sun"></div>
    <!-- Clouds -->
    <div class="cloud" style="top:22px;left:-90px;animation-duration:28s;">
      <div class="cloud-shape" style="width:80px;height:22px;position:relative;">
        <div class="cloud-shape" style="width:40px;height:36px;position:absolute;top:-18px;left:12px;"></div>
        <div class="cloud-shape" style="width:30px;height:28px;position:absolute;top:-12px;left:36px;"></div>
      </div>
    </div>
    <div class="cloud" style="top:40px;left:150px;animation-duration:20s;animation-delay:-10s;opacity:0.85;">
      <div class="cloud-shape" style="width:60px;height:18px;position:relative;">
        <div class="cloud-shape" style="width:30px;height:28px;position:absolute;top:-14px;left:8px;"></div>
        <div class="cloud-shape" style="width:24px;height:22px;position:absolute;top:-10px;left:28px;"></div>
      </div>
    </div>
    <div class="cloud" style="top:14px;left:480px;animation-duration:35s;animation-delay:-18s;opacity:0.75;">
      <div class="cloud-shape" style="width:50px;height:16px;position:relative;">
        <div class="cloud-shape" style="width:26px;height:24px;position:absolute;top:-12px;left:8px;"></div>
      </div>
    </div>
  </div>

  <!-- HILLS -->
  <div class="hill h1"></div>
  <div class="hill h2"></div>
  <div class="hill h3"></div>
  <div class="ground"></div>

  <!-- TREES -->
  <div class="tree" style="position:absolute;bottom:226px;left:96px;">
    <div style="position:relative;width:56px;text-align:center;">
      <div style="width:48px;height:52px;background:#3C8A1E;border-radius:50% 50% 40% 40%;margin:0 auto;box-shadow:inset -4px -4px 8px rgba(0,0,0,0.2);position:relative;z-index:2;"></div>
      <div style="width:38px;height:40px;background:#4EA828;border-radius:50%;margin:-16px auto 0;position:relative;z-index:1;"></div>
      <div class="tree-trunk" style="margin-top:2px;"></div>
    </div>
  </div>
  <div class="tree" style="position:absolute;bottom:220px;left:152px;">
    <div style="position:relative;width:44px;text-align:center;">
      <div style="width:38px;height:44px;background:#347A1A;border-radius:50% 50% 40% 40%;margin:0 auto;box-shadow:inset -3px -3px 6px rgba(0,0,0,0.2);"></div>
      <div class="tree-trunk"></div>
    </div>
  </div>
  <div class="tree" style="position:absolute;bottom:232px;right:308px;">
    <div style="position:relative;width:54px;text-align:center;">
      <div style="width:46px;height:50px;background:#3C8A1E;border-radius:50% 50% 40% 40%;margin:0 auto;box-shadow:inset -4px -4px 8px rgba(0,0,0,0.2);position:relative;z-index:2;"></div>
      <div style="width:36px;height:38px;background:#4EA828;border-radius:50%;margin:-14px auto 0;position:relative;z-index:1;"></div>
      <div class="tree-trunk" style="margin-top:2px;"></div>
    </div>
  </div>
  <div class="tree" style="position:absolute;bottom:220px;right:250px;">
    <div style="position:relative;width:40px;text-align:center;">
      <div style="width:34px;height:40px;background:#347A1A;border-radius:50% 50% 40% 40%;margin:0 auto;"></div>
      <div class="tree-trunk"></div>
    </div>
  </div>

  <!-- FENCE -->
  <div style="position:absolute;bottom:168px;left:78px;right:0;display:flex;gap:0;z-index:3;">
    <div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:22px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div><div style="display:flex;align-items:flex-end;gap:0;margin-right:16px;"><div style="width:8px;height:18px;background:#E8D8B0;border:1.5px solid #C8A870;border-radius:3px 3px 0 0;"></div></div>
  </div>

  <!-- WINDMILL -->
  <div class="windmill">
    <div style="position:relative;width:60px;text-align:center;">
      <div class="wm-blades" style="position:relative;left:3px;">
        <div class="wm-blade" style="top:24px;left:0;transform:rotate(0deg) translateX(-22px);"></div>
        <div class="wm-blade" style="top:24px;left:0;transform:rotate(90deg) translateX(-22px);"></div>
        <div class="wm-blade" style="top:24px;left:0;transform:rotate(180deg) translateX(-22px);"></div>
        <div class="wm-blade" style="top:24px;left:0;transform:rotate(270deg) translateX(-22px);"></div>
      </div>
      <div class="wm-hub"></div>
      <div class="wm-tower"></div>
      <div style="width:30px;height:10px;background:#A07840;margin:0 auto;border-radius:2px;border:2px solid #8B6010;"></div>
    </div>
  </div>

  <!-- FARMHOUSE -->
  <div class="farmhouse">
    <div style="position:relative;">
      <div class="fh-chimney"></div>
      <div class="fh-roof"></div>
    </div>
    <div class="fh-body">
      <div class="fh-window"></div>
      <div class="fh-door"></div>
      <div class="fh-window"></div>
    </div>
    <div style="width:100%;height:8px;background:#6A4020;border-radius:0 0 4px 4px;"></div>
  </div>

  <!-- POND & BRIDGE -->
  <div class="pond"></div>
  <div class="pond-bridge"></div>
  <div style="position:absolute;bottom:170px;right:148px;font-size:12px;">🦆</div>

  <!-- PATCHES -->
  <div class="patch" style="bottom:158px;left:210px;">🥕🥕</div>
  <div class="patch" style="bottom:154px;left:265px;">🎃</div>
  <div class="patch" style="bottom:158px;right:180px;">🥕🎃</div>
  <div style="position:absolute;bottom:158px;left:320px;font-size:12px;">🌸🌼🌸</div>
  <div style="position:absolute;bottom:154px;left:190px;font-size:12px;">🌷🌸</div>

  <!-- BABY SHEEP -->
  <div class="bsheep" style="bottom:165px;left:330px;">🐑</div>
  <div class="bsheep" style="bottom:162px;left:400px;font-size:24px;">
    🐑<span class="zzz">z z z</span>
  </div>
  <div class="bsheep" style="bottom:165px;right:260px;font-size:26px;animation:float-sheep 3s ease-in-out infinite;">🐑</div>
  <style>@keyframes float-sheep{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}</style>

  <!-- KHO THOC CRATE -->
  <div class="kho-thoc">
    <div style="font-size:20px;margin-bottom:2px;">🧺</div>
    <div class="kho-label">Kho thóc</div>
    <div class="kho-count">12</div>
  </div>

  <!-- MASCOT -->
  <img class="mascot" id="mascotImg" src="data:image/png;base64,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" alt="Bông Cần Cù" onclick="feedSheep()"/>

  <!-- TOP BAR -->
  <div class="top-bar">
    <div class="tb-avatar">🐑</div>
    <div class="tb-info">
      <div class="tb-name">Bông Cần Cù</div>
      <div class="tb-sub">Cừu Kiên Trì · Cấp 5</div>
      <div class="tb-xp">
        <div class="tb-xp-track"><div class="tb-xp-fill"></div></div>
        <div class="tb-xp-label">65%</div>
        <div class="tb-star">⭐</div>
      </div>
    </div>
    <div class="tb-currencies">
      <div class="tb-coin">🪙 <span id="coinCount">128.450</span></div>
      <div class="tb-gem">💎 <span>320</span></div>
      <button class="tb-plus">+</button>
    </div>
    <button class="tb-bell">🔔<div class="tb-bell-dot"></div></button>
  </div>

  <!-- SPEECH BUBBLE -->
  <div class="speech-bubble">
    <div class="sb-msg">Chúc bạn một ngày tuyệt vời! ☀️<br><br>Cừu nhớ bạn đang tích lũy để mua xe máy nhé!</div>
    <div class="sb-react">❤️</div>
  </div>

  <!-- LEFT NAV -->
  <div class="left-nav">
    <div class="nav-btn" onclick="navClick(this)">
      <span class="nav-btn-icon">📋</span><span class="nav-btn-label">Nhiệm vụ</span>
      <span class="nav-badge">3</span>
    </div>
    <div class="nav-btn" onclick="navClick(this)"><span class="nav-btn-icon">🛍️</span><span class="nav-btn-label">Cửa hàng</span></div>
    <div class="nav-btn" onclick="navClick(this)"><span class="nav-btn-icon">🎨</span><span class="nav-btn-label">Trang trí</span></div>
    <div class="nav-btn" onclick="navClick(this)"><span class="nav-btn-icon">👥</span><span class="nav-btn-label">Bạn bè</span></div>
    <div class="nav-btn" onclick="navClick(this)"><span class="nav-btn-icon">🏘️</span><span class="nav-btn-label">Hội nhóm</span></div>
  </div>

  <!-- SIGNBOARD -->
  <div class="signboard">
    <div class="sign-top">
      <div class="sign-lv">Lv.5 ⭐</div>
      <div class="sign-name">Cừu Kiên Trì</div>
      <div class="sign-bar-wrap"><div class="sign-bar-fill"></div></div>
      <div class="sign-pct">65% → Cấp 6</div>
    </div>
    <div class="sign-post"></div>
  </div>

  <!-- FRIENDS CARD -->
  <div class="friends-card" style="top:228px;">
    <div class="fc-title">🟢 Bạn bè online (6)</div>
    <div class="fc-grid">
      <div class="fc-item"><div class="fc-avatar" style="background:linear-gradient(135deg,#FFB3D9,#FF88BB)">🐑</div><span class="fc-name">Bông Mập</span></div>
      <div class="fc-item"><div class="fc-avatar" style="background:linear-gradient(135deg,#81E6D9,#4FD1C5)">🐏</div><span class="fc-name">Cừu Nhanh</span></div>
      <div class="fc-item"><div class="fc-avatar" style="background:linear-gradient(135deg,#FBD38D,#F6AD55)">🐑</div><span class="fc-name">Máy Tích</span></div>
      <div class="fc-item"><div class="fc-avatar" style="background:linear-gradient(135deg,#9AE6B4,#68D391)">🐑</div><span class="fc-name">Lúa Vàng</span></div>
      <div class="fc-item"><div class="fc-avatar" style="background:linear-gradient(135deg,#FEB2B2,#FC8181)">🐑</div><span class="fc-name">Bé Bông</span></div>
      <div class="fc-item"><div class="fc-avatar" style="background:linear-gradient(135deg,#B794F4,#9F7AEA)">🐏</div><span class="fc-name">Thịnh Vượng</span></div>
    </div>
  </div>

  <!-- MISSIONS CARD -->
  <div class="missions-card">
    <div class="mc-title">📋 Nhiệm vụ hôm nay</div>
    <div class="mc-sub" id="mcSub">3/5 hoàn thành</div>
    <div class="mc-row done" onclick="toggleTask(this)">
      <span class="mc-icon">🥕</span>
      <div class="mc-info"><div class="mc-name">Cho cừu ăn 100.000đ</div></div>
      <span class="mc-check">✅</span>
    </div>
    <div class="mc-row done" onclick="toggleTask(this)">
      <span class="mc-icon">📖</span>
      <div class="mc-info"><div class="mc-name">Đọc tin tài chính</div></div>
      <span class="mc-check">✅</span>
    </div>
    <div class="mc-row done" onclick="toggleTask(this)">
      <span class="mc-icon">💰</span>
      <div class="mc-info"><div class="mc-name">Tích lũy 50.000đ</div></div>
      <span class="mc-check">✅</span>
    </div>
    <div class="mc-row" onclick="toggleTask(this)">
      <span class="mc-icon">👥</span>
      <div class="mc-info">
        <div class="mc-name">Mời 1 người bạn</div>
        <div class="mc-prog-wrap"><div class="mc-prog-fill" style="width:0%"></div></div>
      </div>
      <span class="mc-check" style="color:#CCC;font-size:13px">⭕</span>
    </div>
    <div class="mc-row" onclick="toggleTask(this)">
      <span class="mc-icon">💬</span>
      <div class="mc-info">
        <div class="mc-name">Tham gia hội nhóm</div>
        <div class="mc-prog-wrap"><div class="mc-prog-fill" style="width:0%"></div></div>
      </div>
      <span class="mc-check" style="color:#CCC;font-size:13px">⭕</span>
    </div>
  </div>

  <!-- FEED BUTTON -->
  <button class="feed-btn" onclick="feedSheep()">🥕 Cho cừu ăn 100.000đ</button>

  <!-- TAB BAR -->
  <div class="tab-bar">
    <div class="tab-item active" id="tab-0" onclick="switchTab(0)">
      <div class="tab-icon">🏠</div><div class="tab-label">Trang trại</div><div class="tab-dot"></div>
    </div>
    <div class="tab-item" id="tab-1" onclick="switchTab(1)"><div class="tab-icon">📔</div><div class="tab-label">Nhật ký</div></div>
    <div class="tab-item" id="tab-2" onclick="switchTab(2)"><div class="tab-icon">✨</div><div class="tab-label">Giấc mơ</div></div>
    <div class="tab-item" id="tab-3" onclick="switchTab(3)"><div class="tab-icon">🏆</div><div class="tab-label">Thành tựu</div></div>
    <div class="tab-item" id="tab-4" onclick="switchTab(4)"><div class="tab-icon">👤</div><div class="tab-label">Cá nhân</div></div>
  </div>

  <div class="toast" id="toast">🎉 +100.000đ tích lũy! Cừu vui lắm!</div>
</div>

<script>
  function switchTab(idx) {
    for(var i=0;i<5;i++){
      var t=document.getElementById("tab-"+i);
      t.classList.remove("active");
      var d=t.querySelector(".tab-dot");
      if(d) d.remove();
    }
    var a=document.getElementById("tab-"+idx);
    a.classList.add("active");
    var dot=document.createElement("div");
    dot.className="tab-dot";
    a.appendChild(dot);
  }
  function feedSheep(){
    var m=document.getElementById("mascotImg");
    m.style.transform="translateX(-50%) scale(1.12) translateY(-16px)";
    m.style.filter="drop-shadow(0 16px 36px rgba(255,215,0,0.8))";
    setTimeout(function(){
      m.style.transform="";
      m.style.filter="";
    },500);
    showToast();
    spawnConfetti();
    var el=document.getElementById("coinCount");
    var v=parseInt(el.textContent.replace(/\./g,""))+100000;
    el.textContent=v.toLocaleString("vi-VN").replace(/,/g,".");
  }
  function showToast(){
    var t=document.getElementById("toast");
    t.classList.add("show");
    setTimeout(function(){t.classList.remove("show");},2600);
  }
  function spawnConfetti(){
    var root=document.getElementById("root");
    var colors=["#FFD700","#FF6B6B","#4ECDC4","#96E6A1","#DDA0DD","#FFB347","#FF8C94","#45B7D1"];
    var cx=root.offsetWidth/2;
    for(var i=0;i<30;i++){
      (function(){
        var c=document.createElement("div");
        c.className="confetti-p";
        c.style.width=(6+Math.random()*8)+"px";
        c.style.height=(6+Math.random()*8)+"px";
        c.style.left=(cx+(Math.random()-0.5)*260)+"px";
        c.style.top=(root.offsetHeight*0.28)+"px";
        c.style.background=colors[Math.floor(Math.random()*colors.length)];
        c.style.animationDelay=(Math.random()*0.5)+"s";
        c.style.borderRadius=Math.random()>0.5?"50%":"3px";
        root.appendChild(c);
        setTimeout(function(){if(c.parentNode)c.parentNode.removeChild(c);},1900);
      })();
    }
  }
  function toggleTask(row){
    if(row.classList.contains("done")) return;
    row.classList.add("done");
    var ch=row.querySelector(".mc-check");
    ch.textContent="✅"; ch.style.fontSize="14px"; ch.style.color="";
    var p=row.querySelector(".mc-prog-fill");
    if(p) p.style.width="100%";
    var done=document.querySelectorAll(".mc-row.done").length;
    var total=document.querySelectorAll(".mc-row").length;
    document.getElementById("mcSub").textContent=done+"/"+total+" hoàn thành";
  }
  function navClick(card){
    card.style.background="rgba(255,240,180,0.98)";
    card.style.borderColor="#FFD700";
    setTimeout(function(){card.style.background="";card.style.borderColor="";},700);
  }
</script>
"""
        import streamlit.components.v1 as components
        components.html(_PROTO_HTML, height=830, scrolling=False)

