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
# 3 TABS NAVIGATION
# Vision: Finch × Duolingo × Character AI × TCBS
# 💬 Tâm sự · 🐑 Cừu của tôi · 🌾 Trang trại
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "💬 Tâm sự",
    "🐑 Cừu của tôi",
    "🌾 Trang trại",
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
with tab2:
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
            st.info("💭 Kể với Cừu về giấc mơ của bạn ở tab **💬 Tâm sự** nhé!")

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



    # ══════════════════════════════════════════════════
    # PHẦN PROFILE — Cừu hiểu bạn hơn
    # (Hấp thụ Hồ sơ tài chính → ngôn ngữ Cừu)
    # ══════════════════════════════════════════════════
    st.markdown("---")
    with st.expander("🧬 Cừu hiểu gì về bạn?", expanded=False):
        genome = mem.get("wealth_genome", {})
        has_data_p = any([mem["dreams"], mem["life_events"], mem["notes"], mem.get("total_saved", 0) > 0])

        if not has_data_p:
            st.info("🌿 Kể chuyện với Cừu ở tab **💬 Tâm sự** — Cừu sẽ nhớ dần về bạn!")
        else:
            _stage_key_p, _stage_name_p, _, _stage_desc_p, _ = get_growth_stage(mem.get("total_saved", 0))
            _p1c, _p2c, _p3c = st.columns(3)

            with _p1c:
                st.markdown(
                    f'''<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);
                    border-radius:14px;padding:14px;text-align:center;border:1.5px solid #FFD6E8;">
                    <div style="font-size:0.78rem;color:#aaa;margin-bottom:4px;">🐑 Cừu đang ở</div>
                    <div style="font-size:1.05rem;font-weight:800;color:#C4607F;">{_stage_name_p}</div>
                    <div style="font-size:0.75rem;color:#888;margin-top:4px;">{_stage_desc_p}</div>
                    </div>''',
                    unsafe_allow_html=True,
                )
            with _p2c:
                st.markdown(
                    f'''<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);
                    border-radius:14px;padding:14px;text-align:center;border:1.5px solid #FFD6E8;">
                    <div style="font-size:0.78rem;color:#aaa;margin-bottom:4px;">💰 Cừu đã ăn</div>
                    <div style="font-size:1.05rem;font-weight:800;color:#C4607F;">{fmt(mem.get("total_saved",0))}</div>
                    <div style="font-size:0.75rem;color:#888;margin-top:4px;">🔥 {mem.get("streak",0)} ngày liên tiếp</div>
                    </div>''',
                    unsafe_allow_html=True,
                )
            with _p3c:
                _p3_dream = mem["dreams"][0]["name"].title() if mem.get("dreams") else "Chưa có"
                st.markdown(
                    f'''<div style="background:linear-gradient(135deg,#FFF5FA,#F5F0FF);
                    border-radius:14px;padding:14px;text-align:center;border:1.5px solid #FFD6E8;">
                    <div style="font-size:0.78rem;color:#aaa;margin-bottom:4px;">✨ Đang mơ đến</div>
                    <div style="font-size:1.0rem;font-weight:800;color:#C4607F;">{_p3_dream[:18]}</div>
                    <div style="font-size:0.75rem;color:#888;margin-top:4px;">giấc mơ của bạn</div>
                    </div>''',
                    unsafe_allow_html=True,
                )

            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
            _pk1, _pk2 = st.columns(2)
            with _pk1:
                _risk_ans = st.radio(
                    "🛡️ Nếu Cừu ăn 10tr mà còn 8tr:",
                    ["😰 Lo lắm, muốn lấy lại",
                     "🤔 Chờ xem thêm",
                     "😎 Mua thêm cho Cừu ăn!"],
                    key="profile_risk2",
                )
                _risk_map2 = {
                    "😰 Lo lắm, muốn lấy lại":     ("low",    "🌿 Cừu thích ăn nhẹ", "TCBF"),
                    "🤔 Chờ xem thêm":               ("medium", "🌊 Cừu ăn cân bằng", "TCFF"),
                    "😎 Mua thêm cho Cừu ăn!":       ("high",   "⚡ Cừu thích mạo hiểm","TCEF"),
                }
                _r2_val, _r2_label, _r2_fund = _risk_map2[_risk_ans]
                genome["risk_type"] = _r2_label
                _save()
                st.caption(f"**{_r2_label}** · Quỹ tham khảo: **{_r2_fund}**")
            with _pk2:
                _motive2 = st.selectbox("💭 Cừu ăn vì lý do gì?", [
                    "Để bạn an tâm về tương lai",
                    "Cùng bạn thực hiện giấc mơ",
                    "Vì gia đình của bạn",
                    "Để bạn tự do tài chính",
                    "Đang thử nghiệm cùng nhau",
                ], key="profile_motive2")
                genome["personality"] = _motive2
                _save()

            if mem.get("life_events"):
                st.markdown("**🏷️ Cừu nhớ chuyện của bạn:**")
                _ev_cols = st.columns(3)
                for _ei, _etag in enumerate(list(dict.fromkeys(mem["life_events"]))[:6]):
                    _ev_cols[_ei % 3].caption(f"• {LIFE_EVENT_LABELS.get(_etag, _etag)}")

        st.caption("⚠️ Thông tin chỉ mang tính tham khảo, không phải tư vấn đầu tư chuyên nghiệp.")


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

