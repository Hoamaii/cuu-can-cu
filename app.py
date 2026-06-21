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
  * { margin: 0; padding: 0; box-sizing: border-box; }
  .farm-root { width: 860px; height: 820px; position: relative; overflow: hidden; font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif; background: linear-gradient(180deg, #87CEEB 0%, #B0E0FF 40%, #98FB98 60%, #5DBB63 100%); }
  .cloud { position: absolute; font-size: 28px; opacity: 0.8; animation: float-cloud 20s linear infinite; }
  @keyframes float-cloud { 0%{transform:translateX(-80px)} 100%{transform:translateX(920px)} }
  .hill { position: absolute; border-radius: 50%; }
  .hill-1 { width: 500px; height: 200px; background: #5DBB63; bottom: 180px; left: -80px; }
  .hill-2 { width: 400px; height: 160px; background: #4CAF50; bottom: 170px; right: -60px; }
  .hill-3 { width: 300px; height: 120px; background: #66BB6A; bottom: 200px; left: 200px; }
  .ground { position: absolute; bottom: 0; left: 0; right: 0; height: 230px; background: linear-gradient(180deg, #5DBB63 0%, #43A047 100%); }
  .pond { position: absolute; bottom: 100px; right: 130px; width: 120px; height: 60px; background: linear-gradient(135deg, #64B5F6, #42A5F5); border-radius: 50%; border: 3px solid #29B6F6; box-shadow: 0 2px 12px rgba(66,165,245,0.4); }
  .windmill-wrap { position: absolute; bottom: 232px; right: 252px; }
  .windmill { font-size: 30px; display: block; animation: spin-slow 8s linear infinite; transform-origin: center; }
  @keyframes spin-slow { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
  .farmhouse { position: absolute; font-size: 44px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2)); bottom: 228px; right: 168px; }
  .tree { position: absolute; }
  .flower { position: absolute; font-size: 16px; animation: sway 3s ease-in-out infinite; }
  @keyframes sway { 0%,100%{transform:rotate(-5deg)} 50%{transform:rotate(5deg)} }
  .sheep-small { position: absolute; font-size: 22px; animation: float-sheep 4s ease-in-out infinite; }
  @keyframes float-sheep { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
  .sheep-mascot { position: absolute; font-size: 90px; bottom: 215px; left: 50%; transform: translateX(-50%); animation: bounce-idle 2s ease-in-out infinite; filter: drop-shadow(0 8px 20px rgba(0,0,0,0.25)); z-index: 10; cursor: pointer; user-select: none; transition: font-size 0.2s, filter 0.2s; }
  @keyframes bounce-idle { 0%,100%{transform:translateX(-50%) translateY(0)} 50%{transform:translateX(-50%) translateY(-14px)} }
  .top-bar { position: absolute; top: 12px; left: 12px; right: 12px; height: 64px; background: rgba(255,255,255,0.88); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(255,255,255,0.6); box-shadow: 0 4px 24px rgba(0,0,0,0.12); display: flex; align-items: center; padding: 0 16px; gap: 12px; z-index: 100; }
  .avatar-circle { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #FFD700, #FF8C00); display: flex; align-items: center; justify-content: center; font-size: 24px; border: 2.5px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.15); flex-shrink: 0; }
  .profile-info { flex: 1; min-width: 0; }
  .profile-name { font-size: 12px; font-weight: 700; color: #2D3748; white-space: nowrap; }
  .xp-bar-wrap { height: 6px; background: #E2E8F0; border-radius: 3px; width: 130px; overflow: hidden; margin-top: 4px; }
  .xp-bar-fill { height: 100%; width: 65%; background: linear-gradient(90deg, #48BB78, #38A169); border-radius: 3px; }
  .top-currencies { display: flex; align-items: center; gap: 8px; }
  .currency-pill { display: flex; align-items: center; gap: 5px; background: rgba(0,0,0,0.06); border-radius: 20px; padding: 5px 12px; font-size: 12px; font-weight: 700; color: #2D3748; }
  .plus-btn { width: 26px; height: 26px; background: linear-gradient(135deg, #48BB78, #38A169); border-radius: 50%; color: #fff; font-size: 18px; cursor: pointer; border: none; display: flex; align-items: center; justify-content: center; line-height: 1; }
  .bell-btn { width: 38px; height: 38px; background: rgba(0,0,0,0.06); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; border: none; position: relative; }
  .bell-dot { position: absolute; top: 6px; right: 6px; width: 8px; height: 8px; background: #FC8181; border-radius: 50%; border: 1.5px solid #fff; }
  .left-nav { position: absolute; left: 12px; top: 90px; display: flex; flex-direction: column; gap: 8px; z-index: 90; }
  .nav-card { width: 66px; background: rgba(255,255,255,0.93); backdrop-filter: blur(12px); border-radius: 18px; padding: 12px 4px 9px; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; border: 1.5px solid rgba(255,255,255,0.75); box-shadow: 0 3px 14px rgba(0,0,0,0.1); transition: transform 0.15s, box-shadow 0.15s, background 0.2s; position: relative; }
  .nav-card:hover { transform: translateY(-2px) scale(1.06); box-shadow: 0 6px 22px rgba(0,0,0,0.16); background: rgba(255,248,230,0.98); }
  .nav-icon { font-size: 26px; }
  .nav-label { font-size: 9px; font-weight: 700; color: #4A5568; text-align: center; line-height: 1.2; }
  .nav-badge { position: absolute; top: 5px; right: 5px; background: #FC8181; color: #fff; font-size: 9px; font-weight: 700; border-radius: 10px; padding: 1px 5px; border: 1.5px solid #fff; }
  .right-panel { position: absolute; right: 12px; top: 90px; display: flex; flex-direction: column; gap: 10px; z-index: 90; width: 154px; }
  .level-card { background: linear-gradient(135deg, #8B5E3C, #A0694A); border-radius: 18px; padding: 14px; border: 2px solid #DAA520; box-shadow: 0 4px 18px rgba(139,94,60,0.4); }
  .lc-title { font-size: 13px; font-weight: 800; color: #FFE8B0; }
  .lc-name { font-size: 10px; color: #F6D79B; margin: 3px 0; }
  .lc-bar-wrap { height: 8px; background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; margin: 7px 0 5px; }
  .lc-bar-fill { height: 100%; width: 65%; background: linear-gradient(90deg, #FFD700, #FFA500); border-radius: 4px; }
  .friends-card { background: rgba(255,255,255,0.93); backdrop-filter: blur(12px); border-radius: 18px; padding: 12px; border: 1.5px solid rgba(255,255,255,0.75); box-shadow: 0 3px 16px rgba(0,0,0,0.1); }
  .friends-title { font-size: 10px; font-weight: 700; color: #2D3748; margin-bottom: 9px; }
  .friends-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 7px; }
  .friend-avatar { display: flex; flex-direction: column; align-items: center; gap: 2px; cursor: pointer; }
  .friend-circle { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #FFB3D9, #C084FC); display: flex; align-items: center; justify-content: center; font-size: 18px; border: 2px solid #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.15); transition: transform 0.15s; }
  .friend-circle:hover { transform: scale(1.12); }
  .friend-name { font-size: 7px; color: #4A5568; font-weight: 600; text-align: center; max-width: 42px; overflow: hidden; line-height: 1.3; }
  .speech-bubble { position: absolute; top: 90px; right: 178px; background: rgba(255,255,255,0.96); backdrop-filter: blur(16px); border-radius: 18px; padding: 13px 15px; border: 1px solid rgba(255,255,255,0.85); box-shadow: 0 4px 20px rgba(0,0,0,0.12); max-width: 196px; z-index: 88; }
  .speech-bubble::after { content: ""; position: absolute; right: -10px; top: 22px; border: 6px solid transparent; border-left: 10px solid rgba(255,255,255,0.96); }
  .sb-text { font-size: 11px; color: #2D3748; line-height: 1.6; font-weight: 500; }
  .sb-heart { font-size: 16px; margin-top: 5px; display: block; }
  .missions-card { position: absolute; bottom: 80px; left: 90px; background: rgba(255,255,255,0.95); backdrop-filter: blur(16px); border-radius: 20px; padding: 14px 16px; border: 1.5px solid rgba(255,255,255,0.8); box-shadow: 0 4px 22px rgba(0,0,0,0.12); width: 250px; z-index: 90; }
  .missions-title { font-size: 12px; font-weight: 800; color: #2D3748; margin-bottom: 10px; }
  .mission-row { display: flex; align-items: center; gap: 8px; padding: 5px 4px; border-bottom: 1px solid rgba(0,0,0,0.05); cursor: pointer; border-radius: 6px; transition: background 0.1s; }
  .mission-row:last-child { border-bottom: none; }
  .mission-row:hover { background: rgba(0,0,0,0.03); }
  .mission-icon { font-size: 15px; flex-shrink: 0; width: 20px; text-align: center; }
  .mission-info { flex: 1; }
  .mission-name { font-size: 10px; font-weight: 700; color: #2D3748; }
  .mission-sub { font-size: 9px; color: #718096; margin-top: 1px; }
  .mission-prog { height: 4px; background: #E2E8F0; border-radius: 2px; margin-top: 3px; overflow: hidden; }
  .mission-prog-fill { height: 100%; background: linear-gradient(90deg, #68D391, #38A169); border-radius: 2px; transition: width 0.5s ease; }
  .mission-check { font-size: 16px; flex-shrink: 0; }
  .mission-done .mission-name { color: #38A169; text-decoration: line-through; opacity: 0.65; }
  .feed-btn { position: absolute; bottom: 84px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #FFD700, #FFA500); border: none; border-radius: 40px; padding: 17px 42px; font-size: 16px; font-weight: 800; color: #7B3F00; cursor: pointer; white-space: nowrap; animation: pulse-glow 2s ease-in-out infinite; z-index: 95; text-shadow: 0 1px 2px rgba(255,255,255,0.4); letter-spacing: 0.2px; }
  @keyframes pulse-glow { 0%,100%{box-shadow:0 4px 22px rgba(255,165,0,0.55),0 0 42px rgba(255,215,0,0.28)} 50%{box-shadow:0 8px 38px rgba(255,165,0,0.88),0 0 72px rgba(255,215,0,0.6)} }
  .feed-btn:active { transform: translateX(-50%) scale(0.96); }
  .tab-bar { position: absolute; bottom: 0; left: 0; right: 0; height: 72px; background: rgba(255,255,255,0.97); backdrop-filter: blur(20px); border-top: 1px solid rgba(0,0,0,0.07); display: flex; align-items: center; justify-content: space-around; padding: 0 8px; z-index: 100; }
  .tab-item { display: flex; flex-direction: column; align-items: center; gap: 3px; cursor: pointer; padding: 8px 14px; border-radius: 14px; transition: background 0.15s; flex: 1; }
  .tab-item:hover { background: rgba(0,0,0,0.04); }
  .tab-icon { font-size: 22px; }
  .tab-label { font-size: 10px; font-weight: 600; color: #A0AEC0; }
  .tab-item.active .tab-label { color: #ED8936; font-weight: 800; }
  .tab-dot { width: 6px; height: 6px; border-radius: 3px; background: #ED8936; margin-top: -1px; }
  .toast { position: absolute; top: 88px; left: 50%; transform: translateX(-50%) translateY(-20px); background: rgba(56,161,105,0.95); color: #fff; padding: 10px 22px; border-radius: 30px; font-size: 13px; font-weight: 700; opacity: 0; pointer-events: none; z-index: 200; transition: opacity 0.3s, transform 0.3s; white-space: nowrap; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
  .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
  .confetti-piece { position: absolute; width: 8px; height: 8px; border-radius: 2px; pointer-events: none; z-index: 200; animation: confetti-fall 1.3s ease-out forwards; }
  @keyframes confetti-fall { 0%{opacity:1;transform:translateY(0) rotate(0deg)} 100%{opacity:0;transform:translateY(200px) rotate(720deg)} }
</style>

<div class="farm-root" id="farmRoot">
  <div class="cloud" style="top:18px;left:-60px;animation-duration:25s">&#x2601;&#xFE0F;</div>
  <div class="cloud" style="top:34px;left:180px;animation-duration:18s;animation-delay:-9s;font-size:22px">&#x2601;&#xFE0F;</div>
  <div class="cloud" style="top:12px;left:510px;animation-duration:32s;animation-delay:-15s;font-size:18px">&#x2601;&#xFE0F;</div>
  <div class="hill hill-1"></div><div class="hill hill-2"></div><div class="hill hill-3"></div>
  <div class="ground"></div>
  <div class="pond"></div>
  <div class="farmhouse">&#x1F3E1;</div>
  <div class="windmill-wrap"><span class="windmill">&#x1F3A1;</span></div>
  <div class="tree" style="bottom:222px;left:114px;font-size:34px">&#x1F333;</div>
  <div class="tree" style="bottom:217px;left:164px;font-size:28px">&#x1F332;</div>
  <div class="tree" style="bottom:240px;right:308px;font-size:30px">&#x1F333;</div>
  <div class="tree" style="bottom:226px;left:298px;font-size:22px">&#x1F332;</div>
  <div class="flower" style="bottom:211px;left:207px">&#x1F338;</div>
  <div class="flower" style="bottom:206px;left:248px;animation-delay:-1s">&#x1F33C;</div>
  <div class="flower" style="bottom:201px;left:342px;animation-delay:-2s">&#x1F338;</div>
  <div class="flower" style="bottom:208px;right:224px;animation-delay:-0.5s">&#x1F337;</div>
  <div class="flower" style="bottom:203px;right:262px;animation-delay:-1.5s">&#x1F33B;</div>
  <div class="sheep-small" style="bottom:200px;left:357px">&#x1F411;</div>
  <div class="sheep-small" style="bottom:214px;left:426px;animation-delay:-1.5s">&#x1F411;</div>
  <div class="sheep-small" style="bottom:196px;right:285px;animation-delay:-0.8s">&#x1F411;</div>
  <div class="sheep-small" style="bottom:209px;left:280px;animation-delay:-2.2s">&#x1F411;</div>
  <div class="sheep-mascot" id="sheepMascot" onclick="feedSheep()">&#x1F411;</div>

  <div class="top-bar">
    <div class="avatar-circle">&#x1F411;</div>
    <div class="profile-info">
      <div class="profile-name">B&#xF4;ng C&#x1EA7;n C&#xF9; &middot; C&#x1EEB;u Ki&#xEA;n Tr&igrave; &middot; C&#x1EA5;p 5</div>
      <div class="xp-bar-wrap"><div class="xp-bar-fill"></div></div>
      <div style="font-size:9px;color:#A0AEC0;margin-top:2px">65% &#x2192; C&#x1EA5;p 6</div>
    </div>
    <div class="top-currencies">
      <div class="currency-pill">&#x1FA99; <span id="coinCount">128.450</span></div>
      <div class="currency-pill">&#x1F48E; <span>320</span></div>
      <button class="plus-btn">+</button>
    </div>
    <button class="bell-btn">&#x1F514;<div class="bell-dot"></div></button>
  </div>

  <div class="left-nav">
    <div class="nav-card" onclick="navClick(this)"><span class="nav-icon">&#x1F4CB;</span><span class="nav-label">Nhi&#x1EC7;m v&#x1EE5;</span><span class="nav-badge">3</span></div>
    <div class="nav-card" onclick="navClick(this)"><span class="nav-icon">&#x1F6CD;&#xFE0F;</span><span class="nav-label">C&#x1EED;a h&#xE0;ng</span></div>
    <div class="nav-card" onclick="navClick(this)"><span class="nav-icon">&#x1F3A8;</span><span class="nav-label">Trang tr&iacute;</span></div>
    <div class="nav-card" onclick="navClick(this)"><span class="nav-icon">&#x1F465;</span><span class="nav-label">B&#x1EA1;n b&#xE8;</span></div>
    <div class="nav-card" onclick="navClick(this)"><span class="nav-icon">&#x1F3D8;&#xFE0F;</span><span class="nav-label">H&#x1ED9;i nh&#xF3;m</span></div>
  </div>

  <div class="right-panel">
    <div class="level-card">
      <div class="lc-title">Lv.5 &middot; C&#x1EEB;u Ki&#xEA;n Tr&igrave;</div>
      <div class="lc-name">N&#xF4;ng tr&#x1EA1;i c&#x1EE7;a B&#xF4;ng</div>
      <div class="lc-bar-wrap"><div class="lc-bar-fill"></div></div>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:9px;color:#F6D79B">65% &#x2192; C&#x1EA5;p 6</span>
        <span style="font-size:13px">&#x2B50;&#x2B50;&#x2B50;</span>
      </div>
    </div>
    <div class="friends-card">
      <div class="friends-title">&#x1F7E2; B&#x1EA1;n b&#xE8; online (6)</div>
      <div class="friends-grid">
        <div class="friend-avatar"><div class="friend-circle">&#x1F411;</div><span class="friend-name">B&#xF4;ng M&#x1EAD;p</span></div>
        <div class="friend-avatar"><div class="friend-circle" style="background:linear-gradient(135deg,#81E6D9,#4FD1C5)">&#x1F40F;</div><span class="friend-name">C&#x1EEB;u Nhanh</span></div>
        <div class="friend-avatar"><div class="friend-circle" style="background:linear-gradient(135deg,#FBD38D,#F6AD55)">&#x1F411;</div><span class="friend-name">M&#xE1;y T&iacute;ch</span></div>
        <div class="friend-avatar"><div class="friend-circle" style="background:linear-gradient(135deg,#9AE6B4,#68D391)">&#x1F411;</div><span class="friend-name">L&#xFA;a V&#xE0;ng</span></div>
        <div class="friend-avatar"><div class="friend-circle" style="background:linear-gradient(135deg,#FEB2B2,#FC8181)">&#x1F411;</div><span class="friend-name">B&#xE9; B&#xF4;ng</span></div>
        <div class="friend-avatar"><div class="friend-circle" style="background:linear-gradient(135deg,#B794F4,#9F7AEA)">&#x1F40F;</div><span class="friend-name">Th&#x1ECB;nh V&#x01B0;&#x1EE3;ng</span></div>
      </div>
    </div>
  </div>

  <div class="speech-bubble">
    <div class="sb-text">Ch&#xFA;c b&#x1EA1;n m&#x1ED9;t ng&#xE0;y tuy&#x1EC7;t v&#x1EDD;i! &#x2600;&#xFE0F;<br><br>C&#x1EEB;u nh&#x1EDB; b&#x1EA1;n &#x111;ang t&iacute;ch l&#x0169;y &#x111;&#x1EC3; mua xe m&#xE1;y nh&#xE9;!</div>
    <span class="sb-heart">&#x2764;&#xFE0F;</span>
  </div>

  <div class="missions-card">
    <div class="missions-title" id="missionTitle">&#x1F4CB; Nhi&#x1EC7;m v&#x1EE5; h&#xF4;m nay (3/5)</div>
    <div class="mission-row mission-done" onclick="toggleMission(this)">
      <span class="mission-icon">&#x1F955;</span>
      <div class="mission-info"><div class="mission-name">Cho c&#x1EEB;u &#x103;n 100.000&#x111;</div><div class="mission-sub">Ho&#xE0;n th&#xE0;nh 08:30</div></div>
      <span class="mission-check">&#x2705;</span>
    </div>
    <div class="mission-row mission-done" onclick="toggleMission(this)">
      <span class="mission-icon">&#x1F4D6;</span>
      <div class="mission-info"><div class="mission-name">&#x110;&#x1ECD;c tin t&#xE0;i ch&iacute;nh</div><div class="mission-sub">Ho&#xE0;n th&#xE0;nh</div></div>
      <span class="mission-check">&#x2705;</span>
    </div>
    <div class="mission-row mission-done" onclick="toggleMission(this)">
      <span class="mission-icon">&#x1F4B0;</span>
      <div class="mission-info"><div class="mission-name">T&iacute;ch l&#x0169;y 50.000&#x111;</div><div class="mission-sub">Ho&#xE0;n th&#xE0;nh</div></div>
      <span class="mission-check">&#x2705;</span>
    </div>
    <div class="mission-row" onclick="toggleMission(this)">
      <span class="mission-icon">&#x1F465;</span>
      <div class="mission-info">
        <div class="mission-name">M&#x1EDD;i 1 ng&#x01B0;&#x1EDD;i b&#x1EA1;n</div><div class="mission-sub">0/1</div>
        <div class="mission-prog"><div class="mission-prog-fill" style="width:0%"></div></div>
      </div>
      <span class="mission-check" style="font-size:13px;color:#CBD5E0">&#x2B55;</span>
    </div>
    <div class="mission-row" onclick="toggleMission(this)">
      <span class="mission-icon">&#x1F4AC;</span>
      <div class="mission-info">
        <div class="mission-name">Tham gia h&#x1ED9;i nh&#xF3;m</div><div class="mission-sub">0/1</div>
        <div class="mission-prog"><div class="mission-prog-fill" style="width:0%"></div></div>
      </div>
      <span class="mission-check" style="font-size:13px;color:#CBD5E0">&#x2B55;</span>
    </div>
  </div>

  <button class="feed-btn" onclick="feedSheep()">&#x1F955; Cho c&#x1EEB;u &#x103;n 100.000&#x111;</button>

  <div class="tab-bar">
    <div class="tab-item active" id="tab-0" onclick="switchTab(0)"><div class="tab-icon">&#x1F3E0;</div><div class="tab-label">Trang tr&#x1EA1;i</div><div class="tab-dot"></div></div>
    <div class="tab-item" id="tab-1" onclick="switchTab(1)"><div class="tab-icon">&#x1F4D4;</div><div class="tab-label">Nh&#x1EAD;t k&yacute;</div></div>
    <div class="tab-item" id="tab-2" onclick="switchTab(2)"><div class="tab-icon">&#x2728;</div><div class="tab-label">Gi&#x1EA5;c m&#x01A1;</div></div>
    <div class="tab-item" id="tab-3" onclick="switchTab(3)"><div class="tab-icon">&#x1F3C6;</div><div class="tab-label">Th&#xE0;nh t&#x1EF1;u</div></div>
    <div class="tab-item" id="tab-4" onclick="switchTab(4)"><div class="tab-icon">&#x1F464;</div><div class="tab-label">C&#xE1; nh&#xE2;n</div></div>
  </div>

  <div class="toast" id="toast">&#x1F389; +100.000&#x111; t&iacute;ch l&#x0169;y!</div>
</div>

<script>
  function switchTab(idx) {
    for (var i = 0; i < 5; i++) {
      var t = document.getElementById("tab-" + i);
      t.classList.remove("active");
      var d = t.querySelector(".tab-dot");
      if (d) d.remove();
    }
    var a = document.getElementById("tab-" + idx);
    a.classList.add("active");
    var dot = document.createElement("div");
    dot.className = "tab-dot";
    a.appendChild(dot);
  }
  function feedSheep() {
    var m = document.getElementById("sheepMascot");
    m.style.fontSize = "114px";
    m.style.filter = "drop-shadow(0 10px 32px rgba(255,215,0,0.75))";
    setTimeout(function() {
      m.style.fontSize = "90px";
      m.style.filter = "drop-shadow(0 8px 20px rgba(0,0,0,0.25))";
    }, 380);
    showToast();
    spawnConfetti();
    var el = document.getElementById("coinCount");
    var v = parseInt(el.textContent.replace(/\./g, "")) + 100000;
    el.textContent = v.toLocaleString("vi-VN").replace(/,/g, ".");
  }
  function showToast() {
    var t = document.getElementById("toast");
    t.classList.add("show");
    setTimeout(function() { t.classList.remove("show"); }, 2500);
  }
  function spawnConfetti() {
    var root = document.getElementById("farmRoot");
    var colors = ["#FFD700","#FF6B6B","#4ECDC4","#45B7D1","#96E6A1","#DDA0DD","#FFB347","#FF8C94"];
    var cx = root.offsetWidth / 2;
    for (var i = 0; i < 28; i++) {
      (function() {
        var c = document.createElement("div");
        c.className = "confetti-piece";
        c.style.left = (cx + (Math.random() - 0.5) * 240) + "px";
        c.style.top = (root.offsetHeight * 0.3) + "px";
        c.style.background = colors[Math.floor(Math.random() * colors.length)];
        c.style.animationDelay = (Math.random() * 0.5) + "s";
        c.style.borderRadius = Math.random() > 0.5 ? "50%" : "2px";
        root.appendChild(c);
        setTimeout(function() { if (c.parentNode) c.parentNode.removeChild(c); }, 1800);
      })();
    }
  }
  function toggleMission(row) {
    if (row.classList.contains("mission-done")) return;
    row.classList.add("mission-done");
    var check = row.querySelector(".mission-check");
    check.textContent = "✅"; check.style.fontSize = "16px"; check.style.color = "";
    var prog = row.querySelector(".mission-prog-fill");
    if (prog) prog.style.width = "100%";
    var sub = row.querySelector(".mission-sub");
    if (sub) sub.textContent = "Hoàn thành!";
    var done = document.querySelectorAll(".mission-done").length;
    var total = document.querySelectorAll(".mission-row").length;
    document.getElementById("missionTitle").textContent =
      "📋 Nhiệm vụ hôm nay (" + done + "/" + total + ")";
  }
  function navClick(card) {
    card.style.background = "rgba(255,240,180,0.98)"; card.style.borderColor = "#FFD700";
    setTimeout(function() { card.style.background = ""; card.style.borderColor = ""; }, 700);
  }
</script>
"""
        import streamlit.components.v1 as components
        components.html(_PROTO_HTML, height=830, scrolling=False)

