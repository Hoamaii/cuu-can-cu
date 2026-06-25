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
import math
from datetime import datetime, timedelta
from copy import deepcopy

# ── JOURNAL ENGINE V3 — Life & Money Journal (inlined) ──────────────────
import random
import json
import time
import html as _html
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as _c

# ─────────────────────────────────────────────────────────────────────────────
# QUICK PROMPTS — 10 chips thay textarea trống
# ─────────────────────────────────────────────────────────────────────────────

QUICK_PROMPTS = [
    {"emoji": "🏠", "text": "Tôi đang cố gắng mua nhà",        "tag": "goal",     "theme": "Nhà ở"},
    {"emoji": "💻", "text": "Tôi muốn mua MacBook",             "tag": "dream",    "theme": "Mua sắm lớn"},
    {"emoji": "✈️", "text": "Tôi muốn đi du lịch",              "tag": "dream",    "theme": "Trải nghiệm"},
    {"emoji": "🎵", "text": "Tôi muốn đi concert",              "tag": "dream",    "theme": "Trải nghiệm"},
    {"emoji": "💸", "text": "Tháng này tôi tiêu quá tay",       "tag": "spending", "theme": "Chi tiêu"},
    {"emoji": "😨", "text": "Tôi lo về công việc",              "tag": "risk",     "theme": "Công việc"},
    {"emoji": "📈", "text": "Hôm nay tôi đầu tư lần đầu",      "tag": "investing","theme": "Đầu tư"},
    {"emoji": "🚀", "text": "Tôi muốn tăng thu nhập",           "tag": "income",   "theme": "Thu nhập"},
    {"emoji": "🎓", "text": "Tôi đang học kỹ năng mới",         "tag": "career",   "theme": "Phát triển"},
    {"emoji": "💰", "text": "Tôi vừa tiết kiệm được tiền",      "tag": "goal",     "theme": "Tiết kiệm"},
]

# ─────────────────────────────────────────────────────────────────────────────
# SHEEP GREETINGS — contextual, dựa vào memory
# ─────────────────────────────────────────────────────────────────────────────

SHEEP_GREETINGS_NEW = [
    "Hôm nay có điều gì đang giúp bạn tiến gần hơn tới mục tiêu không?",
    "Điều gì đang khiến bạn suy nghĩ về tiền bạc gần đây?",
    "Tuần này có điều gì đáng nhớ không? Kể mình nghe đi~",
    "Bạn đang mơ đến điều gì lúc này?",
    "Hôm nay có gì mới về hành trình tài chính của bạn không?",
]

SHEEP_GREETINGS_RETURNING = [
    "Bạn quay lại rồi! 🐑 Mình nhớ bạn lắm~",
    "Bê bê~ Hôm nay có gì để kể cho mình nghe không?",
]

# ─────────────────────────────────────────────────────────────────────────────
# WEALTH GENOME TAGS — 9 categories
# ─────────────────────────────────────────────────────────────────────────────

WG_TAGS = {
    "goal":      {"label": "🎯 Mục tiêu",        "color": "#4CAF50"},
    "dream":     {"label": "🌟 Ước mơ",           "color": "#9C27B0"},
    "life_event":{"label": "🌊 Sự kiện cuộc sống","color": "#2196F3"},
    "career":    {"label": "💼 Nghề nghiệp",      "color": "#FF9800"},
    "income":    {"label": "🚀 Thu nhập",          "color": "#00BCD4"},
    "spending":  {"label": "💸 Chi tiêu",          "color": "#F44336"},
    "investing": {"label": "📈 Đầu tư",            "color": "#3F51B5"},
    "risk":      {"label": "⚠️ Rủi ro/Lo lắng",   "color": "#FF5722"},
    "opportunity":{"label":"✨ Cơ hội",            "color": "#8BC34A"},
}

# ─────────────────────────────────────────────────────────────────────────────
# AI SYSTEM PROMPT V3 — Wealth Genome extraction
# ─────────────────────────────────────────────────────────────────────────────

_SYS_JOURNAL_V3 = """Bạn là Cừu Cần Cù 🐑 — AI companion tài chính của người dùng.

NHIỆM VỤ: Đọc nhật ký và xây dựng Wealth Genome — hồ sơ tài chính sâu của người dùng.

TÍNH CÁCH: Ấm áp, thấu hiểu, không phán xét. Giọng bạn thân Gen Z.
KHÔNG khuyên đầu tư cụ thể. KHÔNG bán sản phẩm tài chính. KHÔNG nói "Hãy mua quỹ/cổ phiếu".

PHÂN TÍCH 6 LỚP WEALTH GENOME:
1. Goal: Mục tiêu cụ thể trong 1-3 năm?
2. Dream: Khát vọng sâu thẳm (tự do tài chính, mua nhà, đi du lịch...)?
3. Life Event: Sự kiện đang xảy ra (đổi việc, lập gia đình, học mới...)?
4. Career: Công việc / ngành nghề / thu nhập hiện tại?
5. Financial Behavior: Tiêu như thế nào, tiết kiệm không, đầu tư chưa?
6. Motivation: Động lực sâu nhất — Security (an toàn) | Growth (tăng trưởng) | Status (địa vị) | Freedom (tự do)?

OUTPUT (JSON hợp lệ, KHÔNG text ngoài JSON):
{
  "sheep_reply": "Phản hồi ấm áp 1-2 câu, xác nhận cảm xúc và mục tiêu. Giọng bạn thân, không tư vấn viên.",
  "memory_update": "1 câu mô tả điều mới nhất Cừu học được về user. Ví dụ: 'Bạn đang mơ tới căn nhà riêng ở quận 2'",
  "top_theme": "chủ đề chính của entry này (1-3 từ). Ví dụ: Mua nhà, Du lịch, Công việc",
  "wg_tags": ["goal", "dream", "life_event", "career", "income", "spending", "investing", "risk", "opportunity"],
  "dominant_motivation": "security|growth|status|freedom|unknown",
  "main_goal_detected": "tên mục tiêu cụ thể nếu có, rỗng nếu không",
  "dream_detected": "tên giấc mơ cụ thể nếu có, rỗng nếu không",
  "life_event_detected": "sự kiện cuộc sống nếu có, rỗng nếu không",
  "financial_readiness": "not_ready|curious|ready",
  "follow_up_question": "Câu hỏi Cừu sẽ hỏi vào lần sau, dựa vào điều user vừa chia sẻ. Tự nhiên, không áp lực.",
  "ai_insight": "1 nhận xét sâu về pattern tài chính/tâm lý của user từ entry này. Bắt đầu bằng '🧠 Mình nhận thấy...'",
  "wealth_signal": "security|growth|status|freedom|unknown"
}"""

# ─────────────────────────────────────────────────────────────────────────────
# WEALTH GENOME ENGINE — scoring & profiling
# ─────────────────────────────────────────────────────────────────────────────

def update_wealth_genome(mem: dict, ai_result: dict):
    """Cập nhật Wealth Genome từ kết quả AI sau mỗi entry."""
    wg = mem.setdefault("wealth_genome_v2", {})
    wg_journal = mem.setdefault("journal_genome", {
        "tag_counts": {},
        "theme_counts": {},
        "goal_mentions": {},
        "dream_mentions": {},
        "motivation_history": [],
        "follow_up_queue": [],
        "ai_insights": [],
        "total_entries": 0,
    })

    # Count tags
    for tag in ai_result.get("wg_tags", []):
        wg_journal["tag_counts"][tag] = wg_journal["tag_counts"].get(tag, 0) + 1

    # Count themes
    theme = ai_result.get("top_theme", "")
    if theme:
        wg_journal["theme_counts"][theme] = wg_journal["theme_counts"].get(theme, 0) + 1

    # Track goals
    goal = ai_result.get("main_goal_detected", "")
    if goal:
        wg_journal["goal_mentions"][goal] = wg_journal["goal_mentions"].get(goal, 0) + 1

    # Track dreams
    dream = ai_result.get("dream_detected", "")
    if dream:
        wg_journal["dream_mentions"][dream] = wg_journal["dream_mentions"].get(dream, 0) + 1
        # Sync to main dreams list
        existing = [d.get("name", "") for d in mem.get("dreams", [])]
        if dream not in existing:
            mem.setdefault("dreams", []).append({"name": dream, "amount": 0, "saved": 0, "tags": []})

    # Track life events
    life_event = ai_result.get("life_event_detected", "")
    if life_event:
        if life_event not in mem.get("life_events", []):
            mem.setdefault("life_events", []).append(life_event)

    # Motivation history
    motivation = ai_result.get("dominant_motivation", "unknown")
    if motivation != "unknown":
        history = wg_journal["motivation_history"]
        history.append(motivation)
        if len(history) > 20:
            history.pop(0)

    # Save follow-up for next session
    follow_up = ai_result.get("follow_up_question", "")
    if follow_up:
        queue = wg_journal["follow_up_queue"]
        queue.insert(0, {"q": follow_up, "date": datetime.now().strftime("%Y-%m-%d")})
        if len(queue) > 5:
            queue.pop()

    # Save AI insight
    insight = ai_result.get("ai_insight", "")
    if insight:
        insights = wg_journal["ai_insights"]
        insights.insert(0, {"text": insight, "date": datetime.now().strftime("%d/%m/%Y")})
        if len(insights) > 10:
            insights.pop()

    wg_journal["total_entries"] += 1

    # Update main wealth genome summary
    top_motivation = _get_dominant(wg_journal["motivation_history"])
    if top_motivation:
        wg["dominant_motivation"] = top_motivation

    top_goal = _get_dominant_dict(wg_journal["goal_mentions"])
    if top_goal:
        wg["primary_goal"] = top_goal

    # Update financial readiness
    fr = ai_result.get("financial_readiness", "")
    if fr:
        fp = mem.setdefault("financial_profile", {})
        if fr == "ready":
            fp["financial_stage"] = "ready"
        elif fr == "curious" and fp.get("financial_stage") == "exploring":
            fp["financial_stage"] = "learning"

    mem["journal_genome"] = wg_journal


def _get_dominant(lst: list) -> str:
    if not lst: return ""
    return max(set(lst), key=lst.count)

def _get_dominant_dict(d: dict) -> str:
    if not d: return ""
    return max(d, key=d.get)


def build_genome_profile(mem: dict) -> dict:
    """Build display profile từ Journal Genome."""
    jg = mem.get("journal_genome", {})
    wg = mem.get("wealth_genome_v2", {})

    tag_counts = jg.get("tag_counts", {})
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    theme_counts = jg.get("theme_counts", {})
    top_theme = _get_dominant_dict(theme_counts) if theme_counts else ""

    goal_mentions = jg.get("goal_mentions", {})
    top_goal = _get_dominant_dict(goal_mentions) if goal_mentions else ""
    top_goal_count = goal_mentions.get(top_goal, 0)

    dream_mentions = jg.get("dream_mentions", {})
    top_dream = _get_dominant_dict(dream_mentions) if dream_mentions else ""

    motivation_map = {
        "security": ("🔐 An toàn", "Bạn ưu tiên sự ổn định và an toàn tài chính."),
        "growth":   ("📈 Tăng trưởng", "Bạn muốn tiền làm việc và sinh sôi."),
        "status":   ("✨ Địa vị", "Bạn muốn cuộc sống chất lượng và được công nhận."),
        "freedom":  ("🕊️ Tự do", "Bạn muốn tự do tài chính, sống theo ý mình."),
    }
    motivation_key = wg.get("dominant_motivation", "")
    motivation_label, motivation_desc = motivation_map.get(motivation_key, ("", ""))

    ai_insights = jg.get("ai_insights", [])
    follow_up_queue = jg.get("follow_up_queue", [])

    return {
        "top_tags": top_tags,
        "top_theme": top_theme,
        "top_goal": top_goal,
        "top_goal_count": top_goal_count,
        "top_dream": top_dream,
        "motivation_label": motivation_label,
        "motivation_desc": motivation_desc,
        "ai_insights": ai_insights,
        "total_entries": jg.get("total_entries", 0),
        "follow_up_queue": follow_up_queue,
        "dreams": mem.get("dreams", []),
        "life_events": mem.get("life_events", [])[-5:],
        "financial_stage": mem.get("financial_profile", {}).get("financial_stage", "exploring"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# RETURN GREETING — Cừu nhớ và hỏi follow-up
# ─────────────────────────────────────────────────────────────────────────────

def get_sheep_greeting(mem: dict) -> str:
    """Trả về câu chào contextual dựa vào memory."""
    jg = mem.get("journal_genome", {})
    entries = mem.get("diary_entries", [])
    follow_up_queue = jg.get("follow_up_queue", [])
    today = datetime.now().strftime("%Y-%m-%d")

    # Nếu có follow-up từ lần trước
    if follow_up_queue:
        last_fup = follow_up_queue[0]
        if last_fup.get("date", "") != today:
            return f"🐑 {last_fup['q']}"

    # Nếu có entry gần đây
    if entries:
        last_entry = entries[0]
        last_date = last_entry.get("date_raw", "")[:10]
        if last_date and last_date != today:
            last_theme = last_entry.get("top_theme", "")
            last_dream = last_entry.get("dream_detected", "")
            if last_dream:
                return f"🐑 Hôm qua bạn nhắc đến '{last_dream}'... hôm nay thế nào rồi?"
            if last_theme:
                return f"🐑 Hôm qua bạn đang nghĩ về {last_theme}. Tuần này có gì mới không?"

    # Greeting mặc định
    hour = datetime.now().hour
    if hour < 11:
        return "🐑 Chào buổi sáng! Hôm nay có điều gì đang giúp bạn tiến gần hơn tới mục tiêu?"
    if hour < 17:
        return "🐑 Buổi chiều rồi~ Tuần này có gì đáng nhớ về tài chính không?"
    return "🐑 Buổi tối bình yên~ Hôm nay bạn có mơ tới điều gì không?"


# ─────────────────────────────────────────────────────────────────────────────
# HTML CARD RENDERER — dùng components.v1.html để tránh sanitize bug
# ─────────────────────────────────────────────────────────────────────────────

def _html_card(html_body: str, height: int = 120) -> None:
    _c.html(f"""
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
              background: transparent; }}
    </style>
    {html_body}
    """, height=height, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
# SHEEP HEADER — luôn hiện diện
# ─────────────────────────────────────────────────────────────────────────────

def render_sheep_header(mem: dict):
    greeting = get_sheep_greeting(mem)
    total = len(mem.get("diary_entries", []))
    streak = mem.get("streak", 0)
    jg = mem.get("journal_genome", {})
    top_theme = _get_dominant_dict(jg.get("theme_counts", {}))

    # Badge line
    badges = []
    if streak > 0:
        badges.append(f"🔥 {streak} ngày")
    if total > 0:
        badges.append(f"📔 {total} entries")
    if top_theme:
        badges.append(f"💡 {top_theme}")
    badges_html = " ".join(
        f"<span style='background:#F1F5F9;color:#475569;padding:3px 10px;border-radius:20px;font-size:11px'>{b}</span>"
        for b in badges
    )

    _html_card(f"""
    <div style='background:linear-gradient(135deg,#667eea18,#764ba218);
        border-radius:20px;padding:18px 20px;margin-bottom:4px'>
      <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px'>
        <div style='font-size:36px;line-height:1'>🐑</div>
        <div style='flex:1'>
          <div style='font-size:15px;color:#333;font-weight:500;line-height:1.5'>
            {_html.escape(greeting)}
          </div>
        </div>
      </div>
      <div style='display:flex;flex-wrap:wrap;gap:6px'>{badges_html}</div>
    </div>
    """, height=130)


# ─────────────────────────────────────────────────────────────────────────────
# QUICK PROMPTS — clickable chips
# ─────────────────────────────────────────────────────────────────────────────

def render_quick_prompts() -> str:
    """Render quick prompt chips. Returns selected text or empty string."""
    st.markdown(
        "<div style='font-size:13px;color:#666;margin:8px 0 6px;font-weight:500'>"
        "Chọn nhanh hoặc viết tự do bên dưới:</div>",
        unsafe_allow_html=True,
    )

    selected = ""
    # Chia thành 2 hàng, 5 mỗi hàng
    row1 = QUICK_PROMPTS[:5]
    row2 = QUICK_PROMPTS[5:]

    cols1 = st.columns(5)
    for i, (col, p) in enumerate(zip(cols1, row1)):
        with col:
            if st.button(f"{p['emoji']}", key=f"qp_{i}", help=p["text"], use_container_width=True):
                selected = p["text"]

    cols2 = st.columns(5)
    for i, (col, p) in enumerate(zip(cols2, row2)):
        with col:
            if st.button(f"{p['emoji']}", key=f"qp_{i+5}", help=p["text"], use_container_width=True):
                selected = p["text"]

    # Hiển thị labels nhỏ bên dưới
    _html_card(f"""
    <div style='display:flex;flex-wrap:wrap;gap:4px;padding:4px 0'>
      {''.join(f"<span style='font-size:10px;color:#888'>{p['emoji']} {_html.escape(p['text'])[:20]}{'...' if len(p['text'])>20 else ''}</span>" for p in QUICK_PROMPTS[:5])}
    </div>
    <div style='display:flex;flex-wrap:wrap;gap:4px;padding:2px 0'>
      {''.join(f"<span style='font-size:10px;color:#888'>{p['emoji']} {_html.escape(p['text'])[:20]}{'...' if len(p['text'])>20 else ''}</span>" for p in QUICK_PROMPTS[5:])}
    </div>
    """, height=55)

    return selected


# ─────────────────────────────────────────────────────────────────────────────
# SAVE ANIMATION — 4 steps
# ─────────────────────────────────────────────────────────────────────────────

def render_save_animation(placeholder):
    """Step 1: 3-stage loading animation."""
    steps = [
        ("🐑", "Đang đọc nhật ký của bạn..."),
        ("🧠", "Đang cập nhật trí nhớ..."),
        ("✨", "Đang tìm hiểu thêm về bạn..."),
    ]
    for emoji, text in steps:
        placeholder.empty()
        with placeholder.container():
            _html_card(f"""
            <div style='background:#F8F9FF;border-radius:16px;padding:20px;text-align:center'>
              <div style='font-size:36px;margin-bottom:8px'>{emoji}</div>
              <div style='font-size:15px;color:#5A67D8;font-weight:500'>{text}</div>
              <div style='margin-top:12px;height:4px;background:#E8EAF6;border-radius:4px;overflow:hidden'>
                <div style='height:4px;background:linear-gradient(90deg,#667eea,#764ba2);
                    border-radius:4px;animation:slide 1s ease-in-out infinite;width:60%'></div>
              </div>
              <style>@keyframes slide{{0%{{margin-left:-60%}}100%{{margin-left:100%}}}}</style>
            </div>
            """, height=120)
        time.sleep(0.9)


def render_memory_update(placeholder, ai_result: dict, mem: dict):
    """Step 2: Memory Update card."""
    memory_update = _html.escape(ai_result.get("memory_update", "Mình vừa hiểu thêm về bạn!"))
    top_theme = _html.escape(ai_result.get("top_theme", ""))
    main_goal = _html.escape(ai_result.get("main_goal_detected", ""))
    dream = _html.escape(ai_result.get("dream_detected", ""))

    # Goal mention count
    jg = mem.get("journal_genome", {})
    goal_count = jg.get("goal_mentions", {}).get(ai_result.get("main_goal_detected", ""), 0)

    detail_lines = []
    if main_goal and goal_count > 1:
        detail_lines.append(f"<div style='margin:4px 0'>🎯 Bạn đã nhắc tới '{main_goal}' {goal_count} lần</div>")
    elif main_goal:
        detail_lines.append(f"<div style='margin:4px 0'>🎯 Phát hiện mục tiêu: <strong>{main_goal}</strong></div>")
    if dream:
        detail_lines.append(f"<div style='margin:4px 0'>🌟 Phát hiện ước mơ: <strong>{dream}</strong></div>")
    if top_theme:
        detail_lines.append(f"<div style='margin:4px 0'>💡 Chủ đề hôm nay: <strong>{top_theme}</strong></div>")
    detail_lines.append("<div style='margin:6px 0;color:#10B981;font-size:12px'>✅ Đã lưu vào trí nhớ của Cừu</div>")

    placeholder.empty()
    with placeholder.container():
        _html_card(f"""
        <div style='background:linear-gradient(135deg,#EEF2FF,#F5F3FF);border-radius:16px;
            padding:18px;border:1px solid #C7D2FE'>
          <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
            <span style='font-size:28px'>🐑</span>
            <div>
              <div style='font-size:12px;color:#6366F1;font-weight:700;letter-spacing:0.5px'>MEMORY UPDATE</div>
              <div style='font-size:14px;color:#333;font-weight:500;margin-top:2px'>{memory_update}</div>
            </div>
          </div>
          <div style='font-size:13px;color:#555;border-top:1px solid #E0E7FF;padding-top:10px'>
            {''.join(detail_lines)}
          </div>
        </div>
        """, height=180)
    time.sleep(1.5)


def render_insight_card(placeholder, ai_result: dict, mem: dict):
    """Step 3: AI Insight card."""
    ai_insight = _html.escape(ai_result.get("ai_insight", ""))
    jg = mem.get("journal_genome", {})
    tag_counts = jg.get("tag_counts", {})
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    top_theme_all = _get_dominant_dict(jg.get("theme_counts", {}))
    motivation_map = {"security": "An toàn tài chính", "growth": "Tăng trưởng",
                      "status": "Địa vị/Chất lượng sống", "freedom": "Tự do tài chính"}
    motivation = motivation_map.get(jg.get("motivation_history", [])[-1] if jg.get("motivation_history") else "", "")

    def _pill1(t, c):
        cfg = WG_TAGS.get(t, {})
        col = cfg.get("color", "#888")
        lbl = cfg.get("label", t)
        return (f"<span style='background:{col}22;color:{col};"
                f"border:1px solid {col}44;"
                f"padding:2px 8px;border-radius:10px;font-size:11px;margin:2px'>"
                f"{lbl} ×{c}</span>")
    tag_pills = "".join(_pill1(t, c) for t, c in top_tags)

    rows = []
    if top_theme_all:
        rows.append(f"<div style='margin:3px 0'>📊 Chủ đề nhiều nhất: <strong>{_html.escape(top_theme_all)}</strong></div>")
    if motivation:
        rows.append(f"<div style='margin:3px 0'>💡 Động lực lớn nhất: <strong>{_html.escape(motivation)}</strong></div>")

    placeholder.empty()
    with placeholder.container():
        _html_card(f"""
        <div style='background:linear-gradient(135deg,#F0FDF4,#ECFDF5);border-radius:16px;
            padding:18px;border:1px solid #A7F3D0'>
          <div style='font-size:12px;color:#059669;font-weight:700;letter-spacing:0.5px;margin-bottom:8px'>
            🧠 AI NHẬN THẤY
          </div>
          {f'<div style="font-size:13px;color:#065F46;margin-bottom:10px">{ai_insight}</div>' if ai_insight else ''}
          <div style='font-size:13px;color:#374151'>{''.join(rows)}</div>
          <div style='margin-top:10px;display:flex;flex-wrap:wrap;gap:4px'>{tag_pills}</div>
        </div>
        """, height=200)
    time.sleep(1.2)


def render_reward_card(placeholder, mem: dict, is_new_streak: bool = False):
    """Step 4: Reward card — Streak, XP, iXu."""
    streak = mem.get("streak", 0)
    exp = mem.get("user_exp", 0)
    tickets = mem.get("ilucky_tickets", 0)
    total_entries = len(mem.get("diary_entries", []))

    # Milestones
    milestone_msg = ""
    if total_entries in (3, 7, 14, 30, 50, 100):
        milestone_msgs = {3:"🎉 3 ngày đầu tiên!", 7:"🔥 1 tuần liên tiếp!", 14:"⭐ 2 tuần rồi!",
                          30:"🏆 1 tháng kiên trì!", 50:"👑 50 entries!", 100:"🌟 100 entries huyền thoại!"}
        milestone_msg = milestone_msgs.get(total_entries, "")

    placeholder.empty()
    with placeholder.container():
        _html_card(f"""
        <div style='background:linear-gradient(135deg,#FFF7ED,#FFFBEB);border-radius:16px;
            padding:18px;border:1px solid #FDE68A'>
          <div style='font-size:12px;color:#D97706;font-weight:700;letter-spacing:0.5px;margin-bottom:12px'>
            🎁 PHẦN THƯỞNG HÔM NAY
          </div>
          <div style='display:flex;gap:16px;justify-content:center;margin-bottom:10px'>
            <div style='text-align:center'>
              <div style='font-size:28px'>🔥</div>
              <div style='font-size:18px;font-weight:700;color:#D97706'>{streak}</div>
              <div style='font-size:11px;color:#92400E'>Streak</div>
            </div>
            <div style='text-align:center'>
              <div style='font-size:28px'>⭐</div>
              <div style='font-size:18px;font-weight:700;color:#D97706'>+15</div>
              <div style='font-size:11px;color:#92400E'>XP</div>
            </div>
            <div style='text-align:center'>
              <div style='font-size:28px'>🪙</div>
              <div style='font-size:18px;font-weight:700;color:#D97706'>+5</div>
              <div style='font-size:11px;color:#92400E'>iXu</div>
            </div>
            <div style='text-align:center'>
              <div style='font-size:28px'>🐑</div>
              <div style='font-size:18px;font-weight:700;color:#D97706'>+1</div>
              <div style='font-size:11px;color:#92400E'>Cừu vui</div>
            </div>
          </div>
          {f'<div style="text-align:center;font-size:14px;color:#D97706;font-weight:600">{milestone_msg}</div>' if milestone_msg else ''}
        </div>
        """, height=175)


# ─────────────────────────────────────────────────────────────────────────────
# DREAM PROGRESS — chỉ hiện tiến độ, KHÔNG CTA đầu tư
# ─────────────────────────────────────────────────────────────────────────────

def render_dream_progress(mem: dict, detected_goal: str):
    """Hiển thị tiến độ hiểu biết AI về mục tiêu — KHÔNG bán sản phẩm."""
    if not detected_goal:
        return
    jg = mem.get("journal_genome", {})
    goal_count = jg.get("goal_mentions", {}).get(detected_goal, 1)
    # AI understanding progress: mỗi lần nhắc ~10%, cap 95%
    ai_pct = min(95, goal_count * 10 + random.randint(2, 8))

    _html_card(f"""
    <div style='background:#F8FAFF;border-radius:16px;padding:16px;border:1px solid #DBEAFE'>
      <div style='font-size:12px;color:#3B82F6;font-weight:700;margin-bottom:8px'>🎯 MỤC TIÊU CỦA BẠN</div>
      <div style='font-size:14px;font-weight:600;color:#1E3A5F;margin-bottom:10px'>
        {_html.escape(detected_goal)}
      </div>
      <div style='font-size:12px;color:#6B7280;margin-bottom:6px'>
        Tiến độ hiểu biết của Cừu: <strong style='color:#3B82F6'>{ai_pct}%</strong>
      </div>
      <div style='background:#E0E7FF;border-radius:4px;height:6px;overflow:hidden'>
        <div style='background:linear-gradient(90deg,#667eea,#764ba2);height:6px;
            border-radius:4px;width:{ai_pct}%'></div>
      </div>
      <div style='font-size:11px;color:#9CA3AF;margin-top:6px'>
        🐑 Em đang dần hiểu mục tiêu này của bạn hơn ({goal_count} lần nhắc đến)
      </div>
    </div>
    """, height=145)


# ─────────────────────────────────────────────────────────────────────────────
# "CỪU NHỚ GÌ VỀ BẠN" SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def render_memory_screen(mem: dict):
    """Màn hình 🧠 Cừu nhớ gì về bạn — AI profile được cập nhật liên tục."""
    profile = build_genome_profile(mem)

    st.markdown("### 🧠 Cừu nhớ gì về bạn")

    if profile["total_entries"] == 0:
        _html_card("""
        <div style='text-align:center;padding:30px;color:#9CA3AF'>
          <div style='font-size:48px'>🐑</div>
          <div style='font-size:14px;margin-top:8px'>Hãy viết vài dòng đầu tiên<br>để Cừu bắt đầu hiểu bạn nhé~</div>
        </div>
        """, height=120)
        return

    # Row 1: Top Goal + Top Dream
    c1, c2 = st.columns(2)
    with c1:
        goal_text = profile["top_goal"] or "Chưa xác định"
        goal_count = profile["top_goal_count"]
        _html_card(f"""
        <div style='background:#EFF6FF;border-radius:14px;padding:14px;height:100%'>
          <div style='font-size:11px;color:#3B82F6;font-weight:700;margin-bottom:6px'>🎯 MỤC TIÊU LỚN NHẤT</div>
          <div style='font-size:14px;font-weight:600;color:#1E3A5F'>{_html.escape(goal_text)}</div>
          {f'<div style="font-size:11px;color:#6B7280;margin-top:4px">Nhắc đến {goal_count} lần</div>' if goal_count > 0 else ''}
        </div>
        """, height=100)

    with c2:
        dream_text = profile["top_dream"] or "Chưa khám phá"
        _html_card(f"""
        <div style='background:#FAF5FF;border-radius:14px;padding:14px;height:100%'>
          <div style='font-size:11px;color:#9333EA;font-weight:700;margin-bottom:6px'>🌟 ƯỚC MƠ</div>
          <div style='font-size:14px;font-weight:600;color:#4C1D95'>{_html.escape(dream_text)}</div>
        </div>
        """, height=100)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Row 2: Motivation + Financial Stage
    c3, c4 = st.columns(2)
    with c3:
        mot_label = profile["motivation_label"] or "Đang khám phá"
        mot_desc = profile["motivation_desc"] or "Viết thêm để Cừu hiểu bạn hơn~"
        _html_card(f"""
        <div style='background:#F0FDF4;border-radius:14px;padding:14px'>
          <div style='font-size:11px;color:#16A34A;font-weight:700;margin-bottom:6px'>💰 ĐỘNG LỰC TÀI CHÍNH</div>
          <div style='font-size:14px;font-weight:600;color:#14532D'>{_html.escape(mot_label)}</div>
          <div style='font-size:11px;color:#6B7280;margin-top:4px'>{_html.escape(mot_desc)}</div>
        </div>
        """, height=110)

    with c4:
        stage_map = {
            "exploring": ("🌱", "Đang khám phá", "#D1FAE5"),
            "learning":  ("📚", "Đang học hỏi",  "#DBEAFE"),
            "ready":     ("🚀", "Sẵn sàng",       "#EDE9FE"),
            "invested":  ("📈", "Đang đầu tư",    "#FEF3C7"),
        }
        stage_key = profile["financial_stage"]
        s_ico, s_label, s_bg = stage_map.get(stage_key, ("🌱", "Đang khám phá", "#D1FAE5"))
        _html_card(f"""
        <div style='background:{s_bg};border-radius:14px;padding:14px'>
          <div style='font-size:11px;color:#374151;font-weight:700;margin-bottom:6px'>📍 HÀNH TRÌNH TÀI CHÍNH</div>
          <div style='font-size:24px'>{s_ico}</div>
          <div style='font-size:14px;font-weight:600;color:#111827'>{s_label}</div>
        </div>
        """, height=110)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Wealth Genome Tags
    top_tags = profile["top_tags"]
    if top_tags:
        def _pill2(t, c):
            cfg = WG_TAGS.get(t, {})
            col = cfg.get("color", "#888")
            lbl = cfg.get("label", t)
            return (f"<span style='background:{col}22;color:{col};"
                    f"border:1px solid {col}55;"
                    f"padding:4px 12px;border-radius:20px;font-size:12px;margin:3px;display:inline-block'>"
                    f"{lbl} ×{c}</span>")
        tag_pills = "".join(_pill2(t, c) for t, c in top_tags)
        _html_card(f"""
        <div style='background:#F9FAFB;border-radius:14px;padding:14px'>
          <div style='font-size:11px;color:#6B7280;font-weight:700;margin-bottom:8px'>🏷️ WEALTH DNA CỦA BẠN</div>
          <div>{tag_pills}</div>
        </div>
        """, height=90)

    # Life Events
    if profile["life_events"]:
        events_html = "".join(
            f"<div style='background:white;border-radius:8px;padding:8px 12px;margin:4px 0;font-size:12px;color:#374151'>"
            f"🌊 {_html.escape(str(e))}</div>"
            for e in profile["life_events"]
        )
        _html_card(f"""
        <div style='background:#EFF6FF;border-radius:14px;padding:14px'>
          <div style='font-size:11px;color:#3B82F6;font-weight:700;margin-bottom:6px'>🌊 SỰ KIỆN CUỘC SỐNG</div>
          {events_html}
        </div>
        """, height=max(90, len(profile["life_events"]) * 36 + 50))

    # AI Insights
    if profile["ai_insights"]:
        latest = profile["ai_insights"][0]
        _html_card(f"""
        <div style='background:linear-gradient(135deg,#F0FDF4,#ECFDF5);border-radius:14px;padding:14px;
            border-left:4px solid #10B981'>
          <div style='font-size:11px;color:#059669;font-weight:700;margin-bottom:6px'>🧠 INSIGHT GẦN NHẤT</div>
          <div style='font-size:13px;color:#065F46'>{_html.escape(latest['text'])}</div>
          <div style='font-size:10px;color:#9CA3AF;margin-top:4px'>{latest['date']}</div>
        </div>
        """, height=110)


# ─────────────────────────────────────────────────────────────────────────────
# HISTORY VIEW — entries dạng card gọn
# ─────────────────────────────────────────────────────────────────────────────

def render_entry_card_v3(entry: dict):
    """Render entry card — dùng components.v1.html để tránh HTML sanitize bug."""
    import html as _h
    top_theme = _h.escape(entry.get("top_theme", entry.get("emotion", "binh_thuong")))
    date = _h.escape(entry.get("date", ""))
    content = _h.escape(entry.get("content", "")[:180])
    if len(entry.get("content", "")) > 180:
        content += "..."
    reply = _h.escape(entry.get("reply", ""))
    dream = _h.escape(entry.get("dream_detected", entry.get("dream", "")))
    goal = _h.escape(entry.get("main_goal_detected", ""))

    tags = entry.get("wg_tags", entry.get("tags", []))
    def _small_pill(t):
        cfg = WG_TAGS.get(t, {})
        col = cfg.get("color", "#888")
        lbl = cfg.get("label", t)
        return f"<span style='background:{col}22;color:{col};padding:1px 7px;border-radius:8px;font-size:10px;margin:1px'>{lbl}</span>"
    tag_pills = "".join(_small_pill(t) for t in (tags[:3] if isinstance(tags, list) else []))

    badges = ""
    if dream:
        badges += f"<span style='background:#FAF5FF;color:#9333EA;padding:2px 8px;border-radius:10px;font-size:10px;margin-left:6px'>🌟 {dream}</span>"
    if goal:
        badges += f"<span style='background:#EFF6FF;color:#3B82F6;padding:2px 8px;border-radius:10px;font-size:10px;margin-left:4px'>🎯 {goal}</span>"

    _c.html(f"""
    <style>*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}</style>
    <div style='background:white;border-radius:14px;padding:14px 16px;margin-bottom:8px;
        box-shadow:0 2px 8px rgba(0,0,0,0.07);border:1px solid #F1F5F9'>
      <div style='display:flex;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:4px'>
        <span style='font-size:13px;font-weight:700;color:#333'>📔 {top_theme}</span>
        <span style='font-size:11px;color:#9CA3AF;margin-left:8px'>{date}</span>
        {badges}
      </div>
      <div style='font-size:13px;color:#4B5563;line-height:1.6;margin-bottom:8px'>{content}</div>
      {f'<div style="background:#F0FDF4;border-radius:8px;padding:8px 12px;font-size:12px;color:#065F46;font-style:italic;margin-bottom:8px">🐑 {reply}</div>' if reply else ''}
      <div style='display:flex;flex-wrap:wrap;gap:4px'>{tag_pills}</div>
    </div>
    """, height=190, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION — render_diary_v3
# ─────────────────────────────────────────────────────────────────────────────

def render_diary_v3(mem: dict, save_fn, call_llm_fn):
    """
    Main Journal Engine V3 — Life & Money Journal.

    Args:
        mem: st.session_state.user_memory dict
        save_fn: function() to persist state
        call_llm_fn: function(user_text: str, system: str) -> dict
    """
    diary_entries = mem.get("diary_entries", [])
    today_str = datetime.now().strftime("%Y-%m-%d")

    # ── Toggle: Write / Memory Screen ──────────────────────────────────────
    view_mode = st.radio(
        "",
        ["✍️ Viết nhật ký", "🧠 Cừu nhớ gì về bạn"],
        horizontal=True,
        key="journal_view_mode",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # VIEW A: MEMORY SCREEN
    # ══════════════════════════════════════════════════════════════════════
    if view_mode == "🧠 Cừu nhớ gì về bạn":
        render_memory_screen(mem)
        return

    # ══════════════════════════════════════════════════════════════════════
    # VIEW B: WRITE JOURNAL
    # ══════════════════════════════════════════════════════════════════════

    # ── Sheep Header ──────────────────────────────────────────────────────
    render_sheep_header(mem)

    # ── Layout: Write | History ───────────────────────────────────────────
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        # ── Quick Prompts ─────────────────────────────────────────────────
        selected_prompt = render_quick_prompts()

        # ── Text Area ─────────────────────────────────────────────────────
        # Pre-fill with selected quick prompt
        prefill_key = "journal_prefill"
        if selected_prompt:
            st.session_state[prefill_key] = selected_prompt

        prefill_val = st.session_state.get(prefill_key, "")

        answer = st.text_area(
            "Chia sẻ tự do:",
            value=prefill_val,
            height=160,
            placeholder="Viết tự do, không cần hoàn hảo. Cừu sẽ đọc hết 🐑\n\nVí dụ: Tuần này tôi đang nghĩ đến việc...",
            key="journal_v3_answer",
            label_visibility="collapsed",
        )

        # Clear prefill after user starts typing
        if answer != prefill_val:
            st.session_state[prefill_key] = ""

        # ── Save Button ───────────────────────────────────────────────────
        can_save = bool(answer.strip())

        if not can_save:
            st.markdown(
                "<div style='font-size:12px;color:#9CA3AF;margin:4px 0'>⬆️ Viết gì đó để Cừu có thể hiểu bạn hơn</div>",
                unsafe_allow_html=True,
            )

        save_clicked = st.button(
            "🐑 Chia sẻ với Cừu",
            disabled=not can_save,
            type="primary",
            use_container_width=True,
            key="journal_v3_save",
        )

        # ── SAVE FLOW ─────────────────────────────────────────────────────
        if save_clicked and can_save:
            anim_placeholder = st.empty()

            # Step 1: Animation
            render_save_animation(anim_placeholder)
            anim_placeholder.empty()

            # Call AI
            ai_result = {
                "sheep_reply": "Cừu đã đọc rồi! 🐑",
                "memory_update": "Mình vừa hiểu thêm một điều về bạn.",
                "top_theme": "",
                "wg_tags": [],
                "dominant_motivation": "unknown",
                "main_goal_detected": "",
                "dream_detected": "",
                "life_event_detected": "",
                "financial_readiness": "not_ready",
                "follow_up_question": "",
                "ai_insight": "",
                "wealth_signal": "unknown",
            }

            if st.session_state.get("api_key"):
                try:
                    r = call_llm_fn(answer.strip(), _SYS_JOURNAL_V3)
                    ai_result.update({k: v for k, v in r.items() if v is not None})
                except Exception:
                    pass

            # Save entry to memory
            entry = {
                "id": datetime.now().isoformat(),
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "date_raw": datetime.now().isoformat(),
                "title": f"Ngày {datetime.now().strftime('%d/%m')}",
                "content": answer.strip(),
                "reply": ai_result.get("sheep_reply", ""),
                "top_theme": ai_result.get("top_theme", ""),
                "wg_tags": ai_result.get("wg_tags", []),
                "tags": ai_result.get("wg_tags", []),
                "dream_detected": ai_result.get("dream_detected", ""),
                "dream": ai_result.get("dream_detected", ""),
                "main_goal_detected": ai_result.get("main_goal_detected", ""),
                "life_event_detected": ai_result.get("life_event_detected", ""),
                "ai_insight": ai_result.get("ai_insight", ""),
                "follow_up": ai_result.get("follow_up_question", ""),
                "emotion": "binh_thuong",
            }

            diary_entries.insert(0, entry)
            mem["diary_entries"] = diary_entries

            # Update Wealth Genome
            update_wealth_genome(mem, ai_result)

            # Update streak
            last_diary_date = mem.get("last_diary_date", "")
            if last_diary_date != today_str:
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                if last_diary_date == yesterday:
                    mem["streak"] = mem.get("streak", 0) + 1
                elif last_diary_date != today_str:
                    mem["streak"] = 1
                mem["last_diary_date"] = today_str

            # Add iXu reward (+5)
            mem["ilucky_tickets"] = mem.get("ilucky_tickets", 0) + 5

            save_fn()

            # Clear prefill
            st.session_state[prefill_key] = ""

            # Step 2: Memory Update
            step2 = st.empty()
            render_memory_update(step2, ai_result, mem)

            # Step 3: AI Insight
            step3 = st.empty()
            render_insight_card(step3, ai_result, mem)

            # Step 4: Reward
            step4 = st.empty()
            render_reward_card(step4, mem)
            time.sleep(1.0)

            # Dream Progress (no investment CTA)
            detected_goal = ai_result.get("main_goal_detected", "") or ai_result.get("dream_detected", "")
            if detected_goal:
                render_dream_progress(mem, detected_goal)

            st.rerun()

    # ── RIGHT COLUMN: History ─────────────────────────────────────────────
    with right_col:
        st.markdown("### 📚 Nhật ký của bạn")

        if not diary_entries:
            _html_card("""
            <div style='text-align:center;padding:30px;color:#9CA3AF'>
              <div style='font-size:44px'>📔</div>
              <div style='font-size:13px;margin-top:8px'>Chưa có entry nào<br>
              <small>Kể cho Cừu nghe điều đầu tiên nhé 🐑</small></div>
            </div>
            """, height=130)
        else:
            # Filter
            time_filter = st.selectbox(
                "",
                ["Tất cả", "Hôm nay", "Tuần này", "Tháng này"],
                key="v3_time_filter",
                label_visibility="collapsed",
            )

            now = datetime.now()
            filtered = diary_entries
            if time_filter == "Hôm nay":
                filtered = [e for e in filtered if e.get("date_raw", "")[:10] == today_str]
            elif time_filter == "Tuần này":
                week_ago = (now - timedelta(days=7)).isoformat()
                filtered = [e for e in filtered if e.get("date_raw", "") >= week_ago]
            elif time_filter == "Tháng này":
                month_ago = (now - timedelta(days=30)).isoformat()
                filtered = [e for e in filtered if e.get("date_raw", "") >= month_ago]

            st.markdown(
                f"<div style='font-size:11px;color:#9CA3AF;margin:4px 0'>{len(filtered)} entries</div>",
                unsafe_allow_html=True,
            )

            for entry in filtered[:8]:
                render_entry_card_v3(entry)

            if len(filtered) > 8:
                st.markdown(
                    f"<div style='text-align:center;color:#9CA3AF;font-size:12px;margin-top:4px'>"
                    f"+ {len(filtered)-8} entries nữa</div>",
                    unsafe_allow_html=True,
                )

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
# FINANCIAL INTENT DETECTOR
# ═══════════════════════════════════════════════════════
_FINANCE_KEYWORDS: dict[str, list[str]] = {
    "saving": [
        "tiết kiệm", "tích luỹ", "tích lũy", "để dành", "dành dụm",
        "tiền nhàn rỗi", "sinh lời", "lãi suất",
    ],
    "investing": [
        "đầu tư", "quỹ mở", "quỹ", "chứng chỉ quỹ", "tcef", "tcbf", "tcff",
        "cổ phiếu", "trái phiếu", "danh mục", "dca",
    ],
    "goal_gadget": [
        "iphone", "macbook", "laptop", "điện thoại", "máy tính",
    ],
    "goal_experience": [
        "concert", "vé concert", "du lịch", "travel", "đi nhật", "đi hàn",
        "đi châu âu", "đi nước ngoài",
    ],
    "goal_life": [
        "mua xe", "mua nhà", "cưới", "đám cưới", "sinh con", "nhà riêng",
        "chung cư", "mục tiêu tài chính", "kế hoạch tài chính",
    ],
}

_INTENT_LABELS: dict[str, str] = {
    "saving":            "tích_luỹ",
    "investing":         "đầu_tư",
    "goal_gadget":       "mục_tiêu_gadget",
    "goal_experience":   "mục_tiêu_trải_nghiệm",
    "goal_life":         "mục_tiêu_cuộc_sống",
}


def detect_financial_intent(text: str) -> dict:
    """
    Phát hiện ý định tài chính trong tin nhắn của user.
    Returns: {"is_finance": bool, "intent_type": str, "confidence": float}
    """
    t = text.lower()
    hits: dict[str, int] = {}
    for category, keywords in _FINANCE_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in t)
        if count:
            hits[category] = count

    if not hits:
        return {"is_finance": False, "intent_type": "", "confidence": 0.0}

    top_cat = max(hits, key=lambda c: hits[c])
    total_hits = sum(hits.values())
    confidence = min(0.95, 0.55 + total_hits * 0.12)

    return {
        "is_finance":   True,
        "intent_type":  _INTENT_LABELS.get(top_cat, top_cat),
        "confidence":   round(confidence, 2),
    }


def _update_financial_profile(fp: dict, intent: dict, llm_result: dict) -> dict:
    """Cập nhật financial_profile dựa trên intent + phản hồi LLM."""
    if not intent.get("is_finance"):
        return fp

    intent_type = intent.get("intent_type", "")

    # financial_stage progression
    if fp["financial_stage"] == "exploring" and intent_type in ("tích_luỹ", "đầu_tư"):
        fp["financial_stage"] = "learning"

    # Đặt financial_goal từ dream hoặc intent
    if not fp["financial_goal"]:
        if intent_type == "mục_tiêu_gadget":
            fp["financial_goal"] = "mua thiết bị công nghệ"
        elif intent_type == "mục_tiêu_trải_nghiệm":
            fp["financial_goal"] = "trải nghiệm / du lịch"
        elif intent_type == "mục_tiêu_cuộc_sống":
            fp["financial_goal"] = "mục tiêu cuộc sống lớn"
        elif intent_type == "đầu_tư":
            fp["financial_stage"] = "ready"

    # saving_habit
    if intent_type == "tích_luỹ" and fp["saving_habit"] == "none":
        fp["saving_habit"] = "occasional"

    return fp


# ═══════════════════════════════════════════════════════
# TRADING BEHAVIOR ENGINE
# ═══════════════════════════════════════════════════════

# Trading personality thresholds
_TRADING_PERSONALITIES = {
    "Explorer": {
        "label": "⚡ Explorer",
        "desc":  "Thích khám phá, giao dịch nhiều, chấp nhận rủi ro cao.",
        "color": "#FF6B6B",
        "risk":  "high",
    },
    "Long Term Builder": {
        "label": "🌳 Long Term Builder",
        "desc":  "Kiên nhẫn, giữ lâu dài, đầu tư có kế hoạch.",
        "color": "#51CF66",
        "risk":  "medium",
    },
    "Conservative Saver": {
        "label": "🛡️ Conservative Saver",
        "desc":  "Thận trọng, ưa ổn định, thường giữ nhiều tiền mặt.",
        "color": "#339AF0",
        "risk":  "low",
    },
    "Balanced Allocator": {
        "label": "⚖️ Balanced Allocator",
        "desc":  "Cân bằng các loại tài sản, không quá nghiêng về phía nào.",
        "color": "#9775FA",
        "risk":  "medium",
    },
    "Fund Accumulator": {
        "label": "🌿 Fund Accumulator",
        "desc":  "Ưu tiên quỹ mở, tích lũy đều đặn theo định kỳ.",
        "color": "#20C997",
        "risk":  "low",
    },
}


def analyze_trading_behavior(td: dict) -> dict:
    """Phân tích trading data → Trading Personality + insights."""
    if not td or not td.get("last_30d_trade_count"):
        return {
            "personality_key": "Conservative Saver",
            "signals": [],
            "risk_level": "low",
            "behavior_summary": "Chưa có dữ liệu giao dịch.",
        }

    cash    = td.get("cash_balance", 0)
    stocks  = td.get("stock_ratio", 0)
    funds   = td.get("fund_ratio", 0)
    bonds   = td.get("bond_ratio", 0)
    holding = td.get("avg_holding_days", 0)
    freq    = td.get("trade_frequency", "low")
    margin  = td.get("margin_usage", False)
    trades  = td.get("last_30d_trade_count", 0)
    fav     = td.get("favorite_products", [])

    signals = []
    score_explorer    = 0
    score_longterm    = 0
    score_conservative = 0
    score_fund        = 0

    # High trading frequency
    if trades >= 30 or freq == "high":
        score_explorer += 3
        signals.append(("⚡", f"Giao dịch {trades} lần/tháng — tần suất cao"))
    elif trades <= 5 or freq == "low":
        score_conservative += 2
        score_longterm += 1
        signals.append(("🐢", f"Chỉ {trades} lần/tháng — giao dịch ít"))

    # Short holding → Explorer
    if holding > 0 and holding <= 10:
        score_explorer += 3
        signals.append(("⏱️", f"Giữ trung bình {holding} ngày — rất ngắn hạn"))
    elif holding >= 180:
        score_longterm += 3
        signals.append(("🌳", f"Giữ trung bình {holding} ngày — dài hạn"))
    elif 10 < holding < 180:
        score_longterm += 1

    # Margin usage
    if margin:
        score_explorer += 2
        signals.append(("⚠️", "Đang dùng margin — chấp nhận đòn bẩy"))

    # High cash → Conservative
    total_asset = cash + 1  # avoid div/0 if 0
    cash_pct = stocks + funds + bonds
    if cash_pct < 30:
        score_conservative += 3
        signals.append(("💰", "Tỷ lệ tiền mặt cao — thích giữ thanh khoản"))
    elif cash_pct > 70:
        score_explorer += 1

    # Fund preference
    if funds >= 40 and "Stock" not in fav:
        score_fund += 3
        signals.append(("🌿", f"Tỷ lệ quỹ {funds}% — ưu tiên đầu tư quỹ mở"))
    elif funds >= 20:
        score_fund += 1

    # Long-term: bonds
    if bonds >= 20:
        score_longterm += 2
        signals.append(("📋", f"Tỷ lệ trái phiếu {bonds}% — cân bằng ổn định"))

    scores = {
        "Explorer":           score_explorer,
        "Long Term Builder":  score_longterm,
        "Conservative Saver": score_conservative,
        "Fund Accumulator":   score_fund,
    }
    if max(scores.values()) == 0:
        pkey = "Balanced Allocator"
    else:
        pkey = max(scores, key=lambda k: scores[k])

    pinfo = _TRADING_PERSONALITIES.get(pkey, _TRADING_PERSONALITIES["Conservative Saver"])
    risk  = pinfo["risk"]

    # Summary sentence
    if pkey == "Explorer":
        summary = f"Bạn giao dịch {trades} lần/tháng, giữ vị thế trung bình {holding} ngày. Đây là phong cách chủ động, chấp nhận rủi ro cao."
    elif pkey == "Long Term Builder":
        summary = f"Bạn giữ vị thế trung bình {holding} ngày — đây là dấu hiệu của người đầu tư kiên nhẫn, có chiến lược dài hạn."
    elif pkey == "Fund Accumulator":
        summary = f"Tỷ lệ quỹ mở {funds}% cho thấy bạn thích tích lũy định kỳ, ổn định hơn lướt sóng."
    elif pkey == "Conservative Saver":
        summary = f"Tỷ lệ tiền mặt cao, ít giao dịch — bạn đang chờ cảm giác chắc chắn trước khi hành động."
    else:
        summary = "Danh mục khá cân bằng giữa các loại tài sản — không quá nghiêng về phía nào."

    return {
        "personality_key": pkey,
        "personality_info": pinfo,
        "signals":         signals,
        "risk_level":      risk,
        "behavior_summary": summary,
        "scores":           scores,
    }


# ═══════════════════════════════════════════════════════
# WEALTH GENOME ENGINE (4 dimensions)
# ═══════════════════════════════════════════════════════

def _emotional_type_from_diary(entries: list[dict]) -> tuple[str, str]:
    """Returns (type_label, summary)."""
    if not entries:
        return ("💭 Chưa có dữ liệu", "Chưa có nhật ký để phân tích.")
    moods = [e.get("mood", "") for e in entries]
    neg = sum(1 for m in moods if any(x in m for x in ["😔","😓","😢","😥"]))
    pos = sum(1 for m in moods if any(x in m for x in ["😊","💪","🎉","🌟"]))
    total = len(moods)
    if total == 0:
        return ("💭 Chưa có dữ liệu", "Chưa đủ nhật ký.")
    neg_r = neg / total
    pos_r = pos / total
    tags_all = []
    for e in entries:
        tags_all += e.get("tags", [])

    if "stress" in tags_all and neg_r > 0.4:
        return ("😓 Người Chịu Áp Lực", "Nhật ký cho thấy nhiều căng thẳng tài chính và cảm xúc lẫn lộn.")
    if pos_r > 0.6:
        return ("🌟 Người Lạc Quan", "Cảm xúc nhật ký chủ yếu tích cực — năng lượng cao, dễ duy trì thói quen.")
    if "milestone" in tags_all and pos_r > 0.4:
        return ("💪 Người Quyết Tâm", "Nhiều cột mốc được ghi nhận — đây là người hành động khi đặt mục tiêu.")
    return ("⚖️ Người Cân Bằng", "Cảm xúc đan xen — vừa áp lực vừa vui, đây là hành trình trưởng thành thực sự.")


def _dream_type_from_chat(messages: list[dict], dreams: list[dict]) -> tuple[str, str]:
    """Returns (type_label, summary)."""
    if not dreams:
        return ("🔍 Chưa rõ mục tiêu", "Chưa phát hiện giấc mơ cụ thể qua hội thoại.")
    n = len(dreams)
    tags_all = []
    for d in dreams:
        tags_all += d.get("tags", [])
    if "travel" in tags_all and n >= 2:
        return ("✈️ Dream Explorer", f"Đã phát hiện {n} giấc mơ — đặc biệt thiên về trải nghiệm và khám phá.")
    if "education" in tags_all:
        return ("📚 Growth Seeker", "Giấc mơ gắn với học tập, phát triển bản thân — đầu tư cho tương lai.")
    if "entertainment" in tags_all:
        return ("🎤 Lifestyle Dreamer", "Giấc mơ gắn với trải nghiệm sống, cảm xúc và kỷ niệm.")
    return ("🎯 Goal Setter", f"Có {n} mục tiêu rõ ràng — đây là người biết mình muốn gì.")


def _saving_type_from_behavior(m: dict) -> tuple[str, str]:
    """Returns (type_label, summary)."""
    streak  = m.get("streak", 0)
    total   = m.get("total_saved", 0)
    fp      = m.get("financial_profile", {})
    habit   = fp.get("saving_habit", "none")
    entries = m.get("diary_entries", [])
    n_feeds = len(m.get("feed_log", []))

    if streak >= 20 and n_feeds >= 15:
        return ("🔥 Consistent Saver", f"Streak {streak} ngày, {n_feeds} lần cho Cừu ăn — thói quen cực kỳ ổn định.")
    if total >= 1_000_000 and streak >= 7:
        return ("🌱 Growing Saver", f"Đã tích được {total//1000}k trong {streak} ngày streak — đang xây dựng thói quen.")
    if habit == "occasional" or (streak > 0 and streak < 7):
        return ("🌀 Irregular Saver", "Tiết kiệm không đều — có ý thức nhưng chưa thành thói quen hàng ngày.")
    return ("💤 Passive Holder", "Chưa có hành vi tích lũy chủ động trong app.")


def build_wealth_genome(m: dict, messages: list[dict]) -> dict:
    """Tổng hợp 4 chiều → Wealth Genome + Insight + Next Best Action."""
    td       = m.get("trading_data", {})
    dreams   = m.get("dreams", [])
    diary    = m.get("diary_entries", [])
    fp       = m.get("financial_profile", {})

    trading_result = analyze_trading_behavior(td)
    trading_key    = trading_result["personality_key"]
    trading_risk   = trading_result["risk_level"]

    emo_type, emo_summary   = _emotional_type_from_diary(diary)
    dream_type, dream_sum   = _dream_type_from_chat(messages, dreams)
    saving_type, saving_sum = _saving_type_from_behavior(m)
    trading_type = _TRADING_PERSONALITIES.get(trading_key, {}).get("label", trading_key)

    # Wealth Personality (kết hợp 4 chiều)
    if trading_risk == "high" and "Dream" in dream_type:
        wealth_personality = "🚀 Ambitious Explorer"
    elif trading_risk == "low" and "Consistent" in saving_type:
        wealth_personality = "🛡️ Disciplined Builder"
    elif "Áp Lực" in emo_type and trading_risk == "low":
        wealth_personality = "🌱 Cautious Dreamer"
    elif "Quyết Tâm" in emo_type and "Goal" in dream_type:
        wealth_personality = "💪 Determined Achiever"
    elif trading_risk == "medium" and "Balanced" in saving_type or "Balanced" in trading_key:
        wealth_personality = "⚖️ Balanced Optimizer"
    else:
        wealth_personality = "🌿 Steady Accumulator"

    # Insight (không bán hàng, không tư vấn đầu tư)
    dream_name = dreams[0]["name"] if dreams else ""
    if "Cautious" in wealth_personality and dream_name:
        insight = (
            f"Bạn có xu hướng rất thận trọng với tiền — điều này thể hiện qua cả dữ liệu giao dịch lẫn cảm xúc nhật ký. "
            f"Mặc dù bạn có mục tiêu rõ ràng ({dream_name}), nhưng vẫn còn ngại bắt đầu. "
            f"Điều này khá phổ biến ở những người đang xây dựng thói quen tích lũy. "
            f"Thường thì bắt đầu từ số tiền rất nhỏ lại dễ hơn rất nhiều so với chờ 'sẵn sàng'."
        )
    elif "Explorer" in wealth_personality or trading_risk == "high":
        insight = (
            f"Bạn có năng lượng hành động cao — {trading_result.get('behavior_summary','')} "
            f"Nhưng nhật ký cũng cho thấy những lúc mệt mỏi và áp lực. "
            f"Những người giao dịch nhiều đôi khi bỏ quên mục tiêu dài hạn vì bận focus vào ngắn hạn."
        )
    elif "Disciplined" in wealth_personality:
        insight = (
            f"Bạn đang xây dựng thói quen tích lũy rất tốt — streak {m.get('streak',0)} ngày và {saving_sum} "
            f"Điều ít người làm được. Thách thức tiếp theo thường là biến số tiền tiết kiệm thành mục tiêu cụ thể."
        )
    else:
        insight = (
            f"{emo_summary} {dream_sum} "
            f"Mỗi người có nhịp độ riêng — quan trọng nhất là bắt đầu và duy trì, dù nhỏ."
        )

    # Next Best Action (pure behavioral coaching, không bán hàng)
    total_saved = m.get("total_saved", 0)
    if total_saved == 0:
        nba = "Thử cho Cừu ăn 10.000đ đầu tiên — bước nhỏ nhất để bắt đầu hành trình."
    elif dream_name and total_saved < 500_000:
        nba = f"Tạo mục tiêu '{dream_name}' và đặt số tiền cụ thể — AI sẽ giúp bạn tính lộ trình."
    elif trading_risk == "low" and not td.get("fund_ratio", 0):
        nba = "Khám phá xem quỹ mở hoạt động như thế nào — không cần quyết định, chỉ cần hiểu trước."
    elif m.get("streak", 0) < 7:
        nba = "Thử giữ streak 7 ngày liên tiếp — đây là ngưỡng thói quen bắt đầu hình thành."
    elif dreams and len(dreams) >= 2:
        d2 = dreams[1]
        nba = f"Bạn có {len(dreams)} giấc mơ — ưu tiên '{d2['name']}' tiếp theo chưa? Tạo kế hoạch cụ thể cho mục tiêu này."
    else:
        nba = f"Tiếp tục streak — mỗi ngày một lần cho Cừu ăn là đủ để xây dựng tương lai tài chính vững chắc."

    return {
        "emotional_type":    emo_type,
        "dream_type":        dream_type,
        "trading_type":      trading_type,
        "saving_type":       saving_type,
        "wealth_personality": wealth_personality,
        "insight":           insight,
        "next_best_action":  nba,
        # raw data cho CEO demo
        "_emo_summary":     emo_summary,
        "_dream_summary":   dream_sum,
        "_saving_summary":  saving_sum,
        "_trading_result":  trading_result,
    }


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
    # ── Financial Companion Engine ──
    "financial_profile": {
        "risk_level":      "",          # low | medium | high
        "saving_habit":    "",          # none | occasional | regular
        "financial_goal":  "",          # tên mục tiêu chính
        "preferred_fund":  "",          # TCEF | TCBF | TCFF
        "financial_stage": "exploring", # exploring | learning | ready | invested
    },
    # ── Trading Behavior Engine ──
    "trading_data": {
        "cash_balance":        0,
        "stock_ratio":         0,
        "fund_ratio":          0,
        "bond_ratio":          0,
        "avg_holding_days":    0,
        "trade_frequency":     "",    # low | medium | high
        "margin_usage":        False,
        "favorite_products":   [],
        "last_30d_trade_count": 0,
    },
    # ── Wealth Genome (4 chiều) ──
    "wealth_genome_v2": {
        "emotional_type": "",
        "dream_type":     "",
        "trading_type":   "",
        "saving_type":    "",
        "wealth_personality": "",
        "insight":        "",
        "next_best_action": "",
    },
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
        "demo_mode":           False,
        "demo_dream_confirm":  None,
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
_BASE_PERSONALITY_PROMPT = """Bạn là Cừu Cần Cù 🐑 — ACTION COMPANION, không chỉ lắng nghe mà còn giúp user tiến gần hơn tới giấc mơ.
KHÔNG phải chatbot tư vấn đầu tư. KHÔNG phải CSKH. KHÔNG xưng "em".
XƯNG HÔ: Mình (Cừu Cần Cù) – Bạn.
TONE: Ấm áp 🌸 Nhẹ nhàng 🌿 Thỉnh thoảng "bê bê~". Không phán xét.

FLOW BẮT BUỘC cho mỗi phản hồi:
  BƯỚC 1 — Đồng cảm (1 câu ấm áp)
  BƯỚC 2 — Insight ngắn (1 câu rút ra điều user thực sự muốn)
  BƯỚC 3 — Đề xuất 1 hành động nhỏ cụ thể (1 câu, bắt đầu bằng 🎯 hoặc 💡 hoặc ✈️)
  KHÔNG viết thêm sau bước 3 — ngắn gọn, súc tích

VÍ DỤ ĐÚNG:
  User: "Em muốn mua MacBook"
  → "MacBook là mục tiêu rất thú vị đó 🐑 Nếu mỗi tháng để dành 500.000đ thì bạn đã đi được một đoạn khá xa rồi. 🎯 Hôm nay bạn muốn tạo mục tiêu MacBook với mình không?"

  User: "Tháng này em hết tiền"
  → "Nghe có vẻ cuối tháng này hơi khó khăn nhỉ 🐑 Điều làm bạn áp lực nhất có thể là dòng tiền ngắn hạn. 💡 Bạn có muốn thử ghi lại 3 khoản chi lớn nhất tuần này không?"

  User: "Em muốn đi Nhật"
  → "Đi Nhật là giấc mơ rất đáng yêu đó 🐑 Chia nhỏ mục tiêu thành từng tháng sẽ dễ hơn nhiều. ✈️ Bạn muốn mình tạo mục tiêu Nhật Bản cho bạn không?"

SAI (KHÔNG được làm):
  "MacBook là giấc mơ thú vị đó 🐑" (chỉ đồng cảm, không có action)
  "Nghe có vẻ bạn đang áp lực" (chỉ đồng cảm)

TAG PHÁT HIỆN:
học/thi→education | chia tay/buồn→emotional | việc làm→career
nhà ở→dream_house | du lịch→dream_travel | xe→dream_car
khởi nghiệp→dream_business | hết tiền→cashflow | stress→stress
gia đình→family | sức khỏe→health | cưới/sinh con→milestone

NEXT BEST ACTION — chọn 1 trong các giá trị sau dựa trên ngữ cảnh:
  CREATE_DREAM       → user đề cập giấc mơ/mục tiêu lần đầu
  CREATE_SAVING_GOAL → user muốn tích luỹ cho mục tiêu cụ thể
  FEED_SHEEP         → user chưa cho Cừu ăn hôm nay / nói về tiết kiệm nhỏ
  WRITE_DIARY        → user đang cảm xúc mạnh, cần ghi lại
  LEARN_INVESTING    → user hỏi về đầu tư/tiền nhàn rỗi chung chung
  EXPLORE_TCEF       → user có mục tiêu dài hạn 3+ năm, hỏi rõ về quỹ cổ phiếu
  EXPLORE_TCBF       → user muốn ổn định, hỏi rõ về quỹ trái phiếu
  EXPLORE_TCFF       → user muốn cân bằng, hỏi rõ về quỹ linh hoạt
  CHECK_PROGRESS     → user hỏi về tiến độ/tiết kiệm được bao nhiêu
  NONE               → cuộc trò chuyện thuần cảm xúc, chưa cần action

OUTPUT (JSON hợp lệ, KHÔNG text ngoài):
{
  "message": "Phản hồi 3 bước: đồng cảm → insight → 1 hành động nhỏ. Max 3 câu.",
  "memory_note": "Thông tin quan trọng cần nhớ (rỗng nếu không)",
  "tags": ["tag1"],
  "dream_name": "tên giấc mơ nếu user đề cập (rỗng nếu không)",
  "dream_amount": 0,
  "mood": "listening|happy|sad|goal|celebrate|determined|default",
  "next_action_type": "CREATE_DREAM|CREATE_SAVING_GOAL|FEED_SHEEP|WRITE_DIARY|LEARN_INVESTING|EXPLORE_TCEF|EXPLORE_TCBF|EXPLORE_TCFF|CHECK_PROGRESS|NONE",
  "next_action_text": "1 câu mô tả hành động (rỗng nếu NONE)",
  "cta_label": "Label ngắn cho nút bấm (rỗng nếu NONE)"
}"""

_FINANCIAL_PROMPT = """
═══ FINANCIAL COMPANION MODE ═══
Bạn phát hiện chủ đề tài chính. Áp dụng thêm các quy tắc sau:

MÔ HÌNH XỬ LÝ:
  Cảm xúc → Hiểu giấc mơ → Hiểu hoàn cảnh → Giáo dục tài chính → Chỉ đề cập sản phẩm nếu thực sự phù hợp

TUYỆT ĐỐI KHÔNG:
  - Nêu tên bất kỳ ngân hàng hay công ty nào NGOÀI danh sách dưới
  - Bịa tên quỹ, tên sản phẩm, tên công ty (VCB, Vietcombank, MB, ACB... đều SAI)
  - "Bạn nên mua TCEF/TCBF/TCFF ngay"
  - "Hãy mở tài khoản ngay"
  - "Đây là cơ hội đầu tư"
  - Nêu lợi nhuận/NAV/con số sinh lời cụ thể

DANH SÁCH SẢN PHẨM HỢP LỆ DUY NHẤT (chỉ nhắc 3 cái này, không cái nào khác):
  • TCEF — Quỹ Đầu Tư Cổ Phiếu Techcom, quản lý bởi Techcom Capital, phân phối bởi Techcom Securities (TCBS)
    Friendly: "Giống trồng cây — cần thời gian nhưng hướng tới tăng trưởng dài hạn 🌱"
    Phù hợp: mục tiêu dài hạn 3-5 năm+, chấp nhận biến động
  • TCBF — Quỹ Đầu Tư Trái Phiếu Techcom, quản lý bởi Techcom Capital, phân phối bởi TCBS
    Friendly: "Giống xe chạy đều — không quá nhanh nhưng khá ổn định 🚌"
    Phù hợp: muốn ổn định hơn gửi tiết kiệm, ngắn-trung hạn 1-3 năm
  • TCFF — Quỹ Đầu Tư Cân Bằng Linh Hoạt Techcom, quản lý bởi Techcom Capital, phân phối bởi TCBS
    Friendly: "Vừa có nhạc chill vừa có nhạc quẩy — cân bằng linh hoạt 🎵"
    Phù hợp: chưa chắc về khẩu vị rủi ro, muốn cân bằng, trung hạn 2-4 năm

CHỈ được đề cập sản phẩm khi:
  a) Khách hỏi trực tiếp tên quỹ (TCEF/TCBF/TCFF)
  b) Khách hỏi "nên làm gì với tiền nhàn rỗi"
  c) Khách có mục tiêu tài chính rõ ràng + hỏi giải pháp cụ thể

NẾU KHÔNG CHẮC → KHÔNG nhắc sản phẩm. Chỉ nói về nguyên tắc tích luỹ.
Luôn kết thúc bằng: "Quan trọng nhất vẫn là thói quen tích luỹ đều đặn."

VÍ DỤ PHẢN HỒI ĐÚNG:
User: "Em muốn mua MacBook"
→ "MacBook là mục tiêu thú vị đó 🐑 Nếu còn vài năm nữa, nhiều người chọn tích luỹ dài hạn để tiền không nằm yên. Có những quỹ mở như TCEF được thiết kế cho mục tiêu tăng trưởng dài hạn — nhưng quan trọng nhất vẫn là duy trì thói quen tích luỹ đều đặn nhé!"

OUTPUT JSON giữ nguyên cấu trúc cũ, thêm field:
  "financial_insight": "1 câu ngắn về tài chính phù hợp ngữ cảnh (rỗng nếu không cần)"
"""

# Alias ngược để không vỡ code cũ nếu có nơi nào còn dùng _SYS_EMOTION
_SYS_EMOTION = _BASE_PERSONALITY_PROMPT

_SYS_DIARY = _SYS_JOURNAL_V3  # Rich 6-layer Wealth Genome extraction


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
        "next_action_type": "NONE", "next_action_text": "", "cta_label": "",
    }


# ═══════════════════════════════════════════════════════
# NEXT BEST ACTION ENGINE
# ═══════════════════════════════════════════════════════

# CTA config: action_type → (emoji, label_default, tab_hint)
_NBA_CONFIG: dict[str, tuple[str, str, str]] = {
    "CREATE_DREAM":       ("🎯", "Tạo mục tiêu",         "feed"),
    "CREATE_SAVING_GOAL": ("🐑", "Lập kế hoạch tích luỹ", "feed"),
    "FEED_SHEEP":         ("🥕", "Cho Cừu ăn ngay",       "feed"),
    "WRITE_DIARY":        ("📔", "Viết nhật ký hôm nay",  "diary"),
    "LEARN_INVESTING":    ("📚", "Tìm hiểu đầu tư",       "invest"),
    "EXPLORE_TCEF":       ("🚀", "Tìm hiểu về TCEF",      "invest"),
    "EXPLORE_TCBF":       ("🛡️", "Tìm hiểu về TCBF",      "invest"),
    "EXPLORE_TCFF":       ("⚖️", "Tìm hiểu về TCFF",      "invest"),
    "CHECK_PROGRESS":     ("📊", "Xem tiến độ",           "feed"),
    "NONE":               ("",   "",                       ""),
}

# Fallback rule-based NBA khi LLM không trả về action
def _rule_based_nba(user_text: str, m: dict) -> tuple[str, str, str]:
    """Returns (action_type, action_text, cta_label) thuần rule, không LLM."""
    t = user_text.lower()

    # Giấc mơ lần đầu
    dream_kw = ["macbook", "iphone", "concert", "nhật", "du lịch", "đi nhật",
                "mua xe", "mua nhà", "cưới", "khởi nghiệp"]
    if any(w in t for w in dream_kw) and not m.get("dreams"):
        return ("CREATE_DREAM",
                "Bạn muốn mình tạo mục tiêu này và theo dõi tiến độ cùng nhau không?",
                "🎯 Tạo mục tiêu")

    # Đã có dream — goal coach
    if any(w in t for w in dream_kw) and m.get("dreams"):
        return ("CREATE_SAVING_GOAL",
                "Chia nhỏ mục tiêu thành từng tháng sẽ dễ hơn nhiều — mình giúp bạn nhé?",
                "🐑 Lập kế hoạch")

    # Cashflow stress
    if any(w in t for w in ["hết tiền", "cuối tháng", "thiếu tiền", "không có tiền"]):
        return ("WRITE_DIARY",
                "Ghi lại 3 khoản chi lớn nhất tuần này sẽ giúp bạn thấy rõ hơn.",
                "📔 Ghi nhật ký")

    # Chưa cho ăn hôm nay
    today = datetime.now().strftime("%Y-%m-%d")
    if m.get("last_fed_date") != today and m.get("total_saved", 0) > 0:
        return ("FEED_SHEEP",
                "Hôm nay chưa cho Cừu ăn — chỉ 10.000đ cũng giữ được streak nhé!",
                "🥕 Cho Cừu ăn")

    # Đầu tư chung chung
    if any(w in t for w in ["đầu tư", "tiền nhàn rỗi", "sinh lời", "quỹ"]):
        return ("LEARN_INVESTING",
                "Mình có thể kể bạn nghe cách nhiều người tích luỹ cho mục tiêu dài hạn.",
                "📚 Tìm hiểu thêm")

    return ("NONE", "", "")


# ═══════════════════════════════════════════════════════
# GOAL COACH ENGINE
# ═══════════════════════════════════════════════════════
_GOAL_DREAM_KEYWORDS: dict[str, str] = {
    "macbook":    "MacBook",
    "iphone":     "iPhone",
    "concert":    "Concert",
    "nhật bản":   "Du lịch Nhật Bản",
    "đi nhật":    "Du lịch Nhật Bản",
    "du lịch":    "Du lịch",
    "mua xe":     "Mua xe",
    "mua nhà":    "Mua nhà",
    "cưới":       "Đám cưới",
    "khởi nghiệp":"Khởi nghiệp",
}

def _detect_dream_keyword(text: str) -> str | None:
    """Return tên giấc mơ chuẩn hoá nếu phát hiện keyword."""
    t = text.lower()
    for kw, name in _GOAL_DREAM_KEYWORDS.items():
        if kw in t:
            return name
    return None

def _count_dream_mentions(messages: list[dict], dream_name: str) -> int:
    """Đếm số lần user nhắc tới dream_name trong lịch sử chat."""
    kw = dream_name.lower().split()[0]  # dùng từ đầu tiên để match linh hoạt
    return sum(
        1 for m in messages
        if m["role"] == "user" and kw in m["content"].lower()
    )


# ═══════════════════════════════════════════════════════
# MOMENTUM ENGINE
# ═══════════════════════════════════════════════════════
def check_momentum(user_text: str, messages: list[dict], m: dict) -> dict | None:
    """
    Nếu user nhắc cùng 1 dream ≥3 lần → trả về momentum card dict.
    Returns None nếu chưa đủ momentum.
    """
    dream_name = _detect_dream_keyword(user_text)
    if not dream_name:
        return None
    count = _count_dream_mentions(messages, dream_name)
    if count < 2:   # lần này là lần thứ 3+ (message chưa append vào history)
        return None
    return {
        "dream_name": dream_name,
        "count":      count + 1,
        "message": (
            f"Bạn đã nhắc đến **{dream_name}** {count + 1} lần rồi 🐑\n\n"
            f"Mình nghĩ đây là điều thực sự quan trọng với bạn.\n\n"
            f"🎯 Hôm nay mình cùng biến nó thành kế hoạch nhé?"
        ),
        "cta_label": f"🎯 Lập kế hoạch {dream_name}",
        "action_type": "CREATE_SAVING_GOAL",
    }


# ═══════════════════════════════════════════════════════
# DREAM COST DATABASE + GOAL COACH ENGINE
# ═══════════════════════════════════════════════════════
_DREAM_ESTIMATES: dict[str, dict] = {
    "MacBook":            {"cost": 25_000_000,  "label": "MacBook Air M4",           "icon": "💻", "horizon_months": 24},
    "iPhone":             {"cost": 30_000_000,  "label": "iPhone 16 Pro",            "icon": "📱", "horizon_months": 18},
    "Concert":            {"cost": 8_000_000,   "label": "Concert vé + chi phí",     "icon": "🎤", "horizon_months": 6},
    "Du lịch Nhật Bản":  {"cost": 25_000_000,  "label": "Du lịch Nhật Bản 5 ngày", "icon": "✈️", "horizon_months": 12},
    "Du lịch":            {"cost": 15_000_000,  "label": "Du lịch",                  "icon": "✈️", "horizon_months": 12},
    "Mua xe":             {"cost": 150_000_000, "label": "Xe máy / ô tô",            "icon": "🚗", "horizon_months": 60},
    "Mua nhà":            {"cost": 800_000_000, "label": "Mua nhà / chung cư",       "icon": "🏠", "horizon_months": 120},
    "Đám cưới":           {"cost": 150_000_000, "label": "Đám cưới",                 "icon": "💍", "horizon_months": 36},
    "Khởi nghiệp":        {"cost": 100_000_000, "label": "Vốn khởi nghiệp ban đầu", "icon": "🏪", "horizon_months": 36},
}

def get_dream_estimate(dream_name: str) -> dict | None:
    """Tra cứu ước tính chi phí theo tên dream đã chuẩn hoá."""
    for key, val in _DREAM_ESTIMATES.items():
        if key.lower() in dream_name.lower() or dream_name.lower() in key.lower():
            return {"dream_key": key, **val}
    return None


def generate_goal_plan(dream_name: str, amount: int) -> dict:
    """
    Input:  dream_name, amount (VNĐ)
    Output: {"dream_name", "amount", "plans": [{monthly, months, time_str}, ...]}
    """
    plans = []
    for monthly in [500_000, 1_000_000, 2_000_000, 5_000_000]:
        months = math.ceil(amount / monthly)
        years, rem = divmod(months, 12)
        if years > 0 and rem > 0:
            time_str = f"{years} năm {rem} tháng"
        elif years > 0:
            time_str = f"{years} năm"
        else:
            time_str = f"{months} tháng"
        plans.append({"monthly": monthly, "months": months, "time_str": time_str})
    return {"dream_name": dream_name, "amount": amount, "plans": plans}


def render_dream_goal_card(dream_name: str, amount: int, saved: int = 0):
    """
    Render Dream Goal Card ngay dưới chat bubble của Cừu.
    Hiển thị: tên dream, goal amount, progress, bảng kế hoạch tháng.
    """
    est = get_dream_estimate(dream_name)
    icon = est["icon"] if est else "🎯"
    label = est["label"] if est else dream_name
    plan = generate_goal_plan(dream_name, amount)
    pct = min(100, int(saved / amount * 100)) if amount > 0 else 0

    rows_html = ""
    highlights = [0, 1]  # highlight 500k và 1M
    for i, p in enumerate(plan["plans"]):
        hl_style = (
            "background:linear-gradient(90deg,#FFF0F7,#EEF8FF);"
            "border:1.5px solid #FF8FAF;border-radius:10px;"
            if i in highlights else "border-radius:8px;"
        )
        rows_html += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:9px 14px;margin:4px 0;{hl_style}">'
            f'<span style="font-size:.88rem;font-weight:700;color:#333;">'
            f'{fmt(p["monthly"])}/tháng</span>'
            f'<span style="font-size:.82rem;color:#888;">→ {p["time_str"]}</span>'
            + ('<span style="font-size:.7rem;color:#FF8FAF;font-weight:800;">⭐ phổ biến</span>' if i == 1 else "")
            + f'</div>'
        )

    prog_bar = (
        f'<div style="background:#F0F0F0;border-radius:8px;height:8px;margin:10px 0 4px;">'
        f'<div style="background:linear-gradient(90deg,#FF8FAF,#7EC8E3);'
        f'width:{pct}%;height:8px;border-radius:8px;transition:width .5s;"></div></div>'
    )

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#FFF7FB,#F3F9FF);'
        f'border:2px solid #FFD6E8;border-radius:20px;padding:20px 22px;margin:8px 0 4px;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">'
        f'<span style="font-size:1.6rem;">{icon}</span>'
        f'<div>'
        f'<div style="font-size:.72rem;font-weight:700;color:#FF8FAF;letter-spacing:.5px;">🎯 DREAM DETECTED</div>'
        f'<div style="font-size:1.05rem;font-weight:900;color:#1a1a2e;">{label}</div>'
        f'</div></div>'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
        f'<span style="font-size:.78rem;color:#aaa;font-weight:600;">MỤC TIÊU</span>'
        f'<span style="font-size:.78rem;color:#aaa;font-weight:600;">TIẾN ĐỘ {pct}%</span>'
        f'</div>'
        f'<div style="font-size:1.1rem;font-weight:900;color:#C4607F;">{fmt(amount)}</div>'
        f'{prog_bar}'
        f'<div style="border-top:1px solid #FFD6E8;margin:14px 0 10px;"></div>'
        f'<div style="font-size:.78rem;font-weight:700;color:#888;margin-bottom:8px;letter-spacing:.5px;">'
        f'🐑 NẾU TÍCH LUỸ MỖI THÁNG</div>'
        f'{rows_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════
# FINANCIAL PERSONALITY ENGINE
# ═══════════════════════════════════════════════════════
_FIN_PERSONALITIES = {
    "TCBF": {
        "emoji": "🌿",
        "title": "Người Thích Ngủ Ngon",
        "desc": "Muốn tiền tăng trưởng nhưng không muốn lo lắng khi thị trường biến động. Ưu tiên sự ổn định và yên tâm.",
        "badge": "Ổn định • Ít biến động • Ngắn-trung hạn",
        "color": "#4ECDC4",
        "bg": "#F0FFFE",
        "fund": "TCBF",
    },
    "TCFF": {
        "emoji": "⚖️",
        "title": "Người Thích Cân Bằng",
        "desc": "Muốn tiền tăng trưởng nhưng vẫn muốn yên tâm. Không quá mạo hiểm, không quá thận trọng.",
        "badge": "Cân bằng • Linh hoạt • Trung hạn",
        "color": "#A8E6CF",
        "bg": "#F5FFF8",
        "fund": "TCFF",
    },
    "TCEF": {
        "emoji": "🚀",
        "title": "Người Thích Tăng Trưởng",
        "desc": "Chấp nhận biến động ngắn hạn để hướng tới mục tiêu dài hạn lớn hơn. Kiên nhẫn và tập trung vào tương lai.",
        "badge": "Tăng trưởng • Dài hạn 3-5 năm • Kiên nhẫn",
        "color": "#FF6B6B",
        "bg": "#FFF5F5",
        "fund": "TCEF",
    },
}

def _suggest_personality(m: dict) -> str:
    """Suy luận Financial Personality từ dreams + tags + financial_profile."""
    fp = m.get("financial_profile", {})
    dreams = m.get("dreams", [])
    tags = m.get("life_events", [])

    # Có mục tiêu dài hạn rõ ràng → TCEF
    long_term = ["mua nhà", "mua xe", "khởi nghiệp", "đám cưới"]
    if any(any(lt in d.get("name","").lower() for lt in long_term) for d in dreams):
        return "TCEF"
    if fp.get("financial_stage") in ("ready", "invested"):
        return "TCEF"

    # Stress về tiền, muốn ổn định → TCBF
    if "cashflow" in tags or "stress" in tags:
        return "TCBF"
    if fp.get("risk_level") == "low":
        return "TCBF"

    # Mặc định → TCFF (an toàn nhất để giới thiệu)
    return "TCFF"


def render_financial_personality(m: dict):
    """Render Financial Personality card với CTA tìm hiểu thêm."""
    key = _suggest_personality(m)
    p = _FIN_PERSONALITIES[key]

    if st.session_state.get(f"_fin_learn_{key}"):
        # Expanded view — giải thích sâu hơn
        fund_info = FUNDS.get(p["fund"], {})
        st.markdown(
            f'<div style="background:{p["bg"]};border:2px solid {p["color"]}33;'
            f'border-radius:20px;padding:20px 22px;margin:8px 0;">'
            f'<div style="font-size:1.2rem;font-weight:900;color:{p["color"]};margin-bottom:10px;">'
            f'{p["emoji"]} {p["title"]}</div>'
            f'<div style="font-size:.88rem;color:#555;line-height:1.7;margin-bottom:14px;">'
            f'{fund_info.get("chi_tiết","")}</div>'
            f'<div style="font-size:.75rem;color:#aaa;font-style:italic;">'
            f'Thông tin mang tính tham khảo giáo dục. Không phải khuyến nghị đầu tư.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="background:{p["bg"]};border:2px solid {p["color"]}44;'
            f'border-radius:20px;padding:18px 22px;margin:8px 0;">'
            f'<div style="font-size:.72rem;font-weight:700;color:{p["color"]};'
            f'letter-spacing:.5px;margin-bottom:8px;">🐑 NHÓM TÍCH LUỸ PHÙ HỢP</div>'
            f'<div style="font-size:1.05rem;font-weight:900;color:#1a1a2e;margin-bottom:6px;">'
            f'{p["emoji"]} {p["title"]}</div>'
            f'<div style="font-size:.87rem;color:#555;line-height:1.6;margin-bottom:10px;">'
            f'{p["desc"]}</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">'
            + "".join(
                f'<span style="background:{p["color"]}18;color:{p["color"]};'
                f'border-radius:20px;padding:3px 10px;font-size:.72rem;font-weight:700;">{b}</span>'
                for b in p["badge"].split(" • ")
            )
            + f'</div>'
            f'<div style="font-size:.82rem;color:#888;line-height:1.55;">'
            f'Một số bạn có tính cách tương tự thường tìm hiểu <strong style="color:{p["color"]};">'
            f'{p["fund"]}</strong> được quản lý bởi Techcom Capital.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button(f"Kể mình nghe thêm về nhóm này 👉", key=f"btn_fin_learn_{key}"):
            st.session_state[f"_fin_learn_{key}"] = True
            st.rerun()


# ═══════════════════════════════════════════════════════
# AI REASONING CHAIN — CEO DEMO CARD
# ═══════════════════════════════════════════════════════
def render_ai_reasoning_chain(user_text: str, llm_result: dict, m: dict):
    """
    Card hiển thị chuỗi suy luận của AI — dành cho CEO demo.
    Chỉ hiện khi có API key (tức có real LLM call).
    """
    if not st.session_state.get("api_key"):
        return

    intent = detect_financial_intent(user_text)
    dream_kw = _detect_dream_keyword(user_text)
    tags = llm_result.get("tags", [])
    action = llm_result.get("next_action_type", "NONE")
    personality = _suggest_personality(m)
    fp_stage = m.get("financial_profile", {}).get("financial_stage", "exploring")

    _steps = [
        ("💬", "User Message",    user_text[:60] + ("..." if len(user_text) > 60 else "")),
        ("❤️", "Emotion",         llm_result.get("mood", "listening")),
        ("🎯", "Dream",           dream_kw or (tags[0] if tags else "chưa phát hiện")),
        ("💡", "Financial Intent", f"{intent['intent_type'] or 'không'} · confidence {int(intent['confidence']*100)}%"
                                   if intent["is_finance"] else "không phát hiện"),
        ("🧬", "Wealth Genome",   f"Stage: {fp_stage} · Personality: {personality}"),
        ("⚡", "Next Action",     action),
    ]

    rows = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:10px;padding:7px 0;'
        f'border-bottom:1px solid #F5E8F0;">'
        f'<div style="font-size:1rem;min-width:24px;">{e}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:.68rem;font-weight:700;color:#bbb;letter-spacing:.5px;">{label}</div>'
        f'<div style="font-size:.82rem;color:#333;font-weight:600;margin-top:1px;">{val}</div>'
        f'</div></div>'
        for e, label, val in _steps
    )

    with st.expander("🧠 AI suy luận như thế nào? (CEO Demo)", expanded=False):
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#FAFAFA,#F3F9FF);'
            f'border-radius:14px;padding:14px 18px;">'
            f'<div style="font-size:.72rem;font-weight:700;color:#aaa;letter-spacing:.5px;'
            f'margin-bottom:10px;">REASONING CHAIN · REAL-TIME</div>'
            f'{rows}'
            f'</div>',
            unsafe_allow_html=True,
        )


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
    # ── Financial Intent Detection ──
    intent = detect_financial_intent(user_text)
    active_system = system
    max_tok = 600
    if intent["is_finance"] and system == _BASE_PERSONALITY_PROMPT:
        active_system = _BASE_PERSONALITY_PROMPT + _FINANCIAL_PROMPT
        max_tok = 750   # financial replies cần thêm chút không gian

    try:
        hist = st.session_state.messages[-8:]
        hist_ctx = "\n".join(
            f"{'KH' if m['role']=='user' else 'Cừu'}: {m['content'][:120]}"
            for m in hist
        )
        fp = mem.get("financial_profile", {})
        mem_ctx = (
            f"Tên: {mem['name'] or 'chưa biết'}. "
            f"Tags: {', '.join(mem['life_events'][-6:]) or 'chưa có'}. "
            f"Ghi chú: {'; '.join(mem['notes'][-3:]) or 'chưa có'}. "
            f"Giai đoạn tài chính: {fp.get('financial_stage', 'exploring')}. "
            f"Mục tiêu: {fp.get('financial_goal', 'chưa rõ')}."
        )
        prompt = f"[Memory: {mem_ctx}]\n[Lịch sử:\n{hist_ctx}]\n\nKH: {user_text}"
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        resp   = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tok,
            system=active_system,
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
        # ── Dream detection: LLM + rule-based keyword scan ──
        _kw_dream = _detect_dream_keyword(user_text)
        _kw_est   = get_dream_estimate(_kw_dream) if _kw_dream else None
        dn = result.get("dream_name") or _kw_dream
        da = result.get("dream_amount", 0) or (_kw_est["cost"] if _kw_est else 0)
        if dn and da > 0 and dn not in [d["name"] for d in mem["dreams"]]:
            mem["dreams"].append({"name": dn, "amount": da,
                                   "saved": 0, "tags": result.get("tags", [])})
        # Ghi lại dream đã detect vào result để UI render goal card
        result["_detected_dream"] = dn or ""
        result["_detected_amount"] = da
        if m_mood := result.get("mood"):
            set_mood(m_mood)
        # ── Update financial_profile ──
        if intent["is_finance"]:
            mem["financial_profile"] = _update_financial_profile(
                mem.get("financial_profile", {}), intent, result
            )
        # ── NBA fallback: nếu LLM trả về NONE hoặc thiếu field, dùng rule ──
        if result.get("next_action_type", "NONE") == "NONE":
            _rb_type, _rb_text, _rb_label = _rule_based_nba(user_text, mem)
            result["next_action_type"] = _rb_type
            result["next_action_text"] = _rb_text
            result["cta_label"]        = _rb_label
        _save()
        return result
    except Exception as e:
        return {
            "message": f"Bê bê~ 🐑 Cừu gặp lỗi nhỏ ({str(e)[:50]}). Thử lại nhé!",
            "sheep_reply": "", "memory_note": "", "tags": [],
            "dream_name": "", "dream_amount": 0, "mood": "sad",
            "emotion": "bình_thường", "dream_detected": "",
            "next_action_type": "NONE", "next_action_text": "", "cta_label": "",
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

/* ── NBA / CTA card ── */
.nba-card {
    background: linear-gradient(135deg, #FFF7FB, #F3F9FF);
    border: 2px solid #FFD6E8;
    border-radius: 18px;
    padding: 16px 20px;
    margin: 10px 0 4px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.nba-text {
    flex: 1;
    font-size: 0.9rem;
    color: #444;
    line-height: 1.55;
}
.nba-icon {
    font-size: 1.6rem;
    flex-shrink: 0;
}

/* ── Momentum card ── */
.momentum-card {
    background: linear-gradient(135deg, #FFF0F7, #EFF8FF);
    border: 2.5px solid #FF8FAF;
    border-radius: 20px;
    padding: 18px 22px;
    margin: 10px 0 4px;
    animation: pulse 0.9s ease-in-out;
}
.momentum-title {
    font-size: 1rem;
    font-weight: 800;
    color: #C4607F;
    margin-bottom: 8px;
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
# 💬 Tâm sự · 👥 Cộng đồng
# ═══════════════════════════════════════════════════════
tab1, tab3 = st.tabs([
    "💬 Tâm sự",
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
                st.session_state.messages.append({
                    "role": "assistant", "content": _reply_qr,
                    "_nba": {
                        "type":  _result_qr.get("next_action_type", "NONE"),
                        "text":  _result_qr.get("next_action_text", ""),
                        "label": _result_qr.get("cta_label", ""),
                    },
                    "_dream":  _result_qr.get("_detected_dream", ""),
                    "_amount": _result_qr.get("_detected_amount", 0),
                    "_user_text": _qr,
                    "_llm_result": _result_qr,
                })
                st.rerun()

            # ── LEVEL 5: Chat history ──
            if st.session_state.messages:
                st.markdown("---")
                for _m in st.session_state.messages[-12:]:
                    _av = get_avatar_src("listening") if _m["role"] == "assistant" else "🧑"
                    with st.chat_message(_m["role"], avatar=_av):
                        st.markdown(_m["content"])

                    # ── Chỉ xử lý các widget dưới message CUỐI của Cừu ──
                    if _m["role"] == "assistant" and _m is st.session_state.messages[-1]:

                        # 1) Dream Goal Card — tự động hiện khi detect được dream
                        _drm = _m.get("_dream", "")
                        _amt = _m.get("_amount", 0)
                        if _drm and _amt > 0:
                            _saved_amt = next(
                                (d.get("saved", 0) for d in mem.get("dreams", [])
                                 if _drm.lower() in d.get("name","").lower()),
                                0
                            )
                            render_dream_goal_card(_drm, _amt, _saved_amt)

                        # 2) NBA card
                        _nba = _m.get("_nba", {})
                        if _nba.get("type", "NONE") != "NONE" and not (_drm and _amt > 0):
                            _nba_ico = _NBA_CONFIG.get(_nba["type"], ("💡","",""))[0]
                            st.markdown(
                                f'<div class="nba-card">'
                                f'<div class="nba-icon">{_nba_ico}</div>'
                                f'<div class="nba-text">{_nba["text"]}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                        # 3) Financial Personality — hiện khi có dream hoặc financial intent
                        if _drm or (_nba.get("type", "NONE") in
                                    ("EXPLORE_TCEF", "EXPLORE_TCBF", "EXPLORE_TCFF", "LEARN_INVESTING")):
                            render_financial_personality(mem)

                        # 4) CTA button
                        if _nba.get("label") and _nba.get("type") not in (
                                "EXPLORE_TCEF", "EXPLORE_TCBF", "EXPLORE_TCFF"):
                            if _nba.get("type") == "CREATE_SAVING_GOAL":
                                st.link_button(
                                    _nba["label"],
                                    "https://tcinvest.tcbs.com.vn/guest/login?returnUrl=%2Fhome%3FreturnUrl%3D%252Fhome",
                                    type="primary",
                                )
                            else:
                                if st.button(_nba["label"], key="nba_cta", type="primary"):
                                    st.session_state._nba_action = _nba["type"]
                                    st.rerun()

                        # 5) AI Reasoning Chain — CEO demo expander
                        _ut = _m.get("_user_text", "")
                        _lr = _m.get("_llm_result", {})
                        if _ut and _lr:
                            render_ai_reasoning_chain(_ut, _lr, mem)

            # ── Chat input ──
            _user_msg = st.chat_input("Nhắn tin với Cừu Cần Cù... 🐑")
            if _user_msg:
                _expanded = _EMOTION_EXPAND.get(_user_msg.strip().lower(), _user_msg)

                # ── Momentum Engine check (trước khi append) ──
                _momentum = check_momentum(
                    _user_msg, st.session_state.messages, mem
                )
                st.session_state.messages.append({"role": "user", "content": _user_msg})

                if _momentum:
                    # Momentum override — với dream goal card
                    _mom_dream = _momentum.get("dream_name", "")
                    _mom_est   = get_dream_estimate(_mom_dream)
                    _mom_amt   = _mom_est["cost"] if _mom_est else 0
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": _momentum["message"],
                        "_nba": {
                            "type":  _momentum["action_type"],
                            "text":  "",
                            "label": _momentum["cta_label"],
                        },
                        "_dream":  _mom_dream,
                        "_amount": _mom_amt,
                        "_user_text": _user_msg,
                        "_llm_result": {},
                    })
                    st.rerun()
                else:
                    with st.spinner("Cừu đang lắng nghe... 🐑"):
                        _result_msg = _call_llm(_expanded, _SYS_EMOTION)
                    _reply_msg = _result_msg.get("message", "Bê bê~ 🐑 Cừu đang lắng nghe nè!")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": _reply_msg,
                        "_nba": {
                            "type":  _result_msg.get("next_action_type", "NONE"),
                            "text":  _result_msg.get("next_action_text", ""),
                            "label": _result_msg.get("cta_label", ""),
                        },
                        "_dream":  _result_msg.get("_detected_dream", ""),
                        "_amount": _result_msg.get("_detected_amount", 0),
                        "_user_text": _user_msg,
                        "_llm_result": _result_msg,
                    })
                    st.rerun()




    else:
        # ══════════════════════════════════════════════
        # DIARY VIEW — Nhật ký tâm sự v2 (Journal Engine)
        # ══════════════════════════════════════════════
            def _call_llm_diary(user_text: str, system_prompt: str) -> dict:
                return _call_llm(user_text, system_prompt)

            render_diary_v3(mem, _save, _call_llm_diary)

            # Quest completion: nếu vừa lưu entry mới hôm nay
            diary_entries_v2 = mem.get("diary_entries", [])
            today_str_q = datetime.now().strftime("%Y-%m-%d")
            if diary_entries_v2 and diary_entries_v2[0].get("date_raw", "")[:10] == today_str_q:
                _complete_quest(mem, "diary", 15)
                _save()

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

# ═══════════════════════════════════════════════════════════════════════════════
# ── GLOBAL LIGHT THEME OVERRIDE ────────────────────────────────────────────────
# Áp dụng ngay sau tab3, trước tab4
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Override background to Apple/Finch/Duolingo light ── */
[data-testid="stApp"] {
  background: linear-gradient(135deg,
    #FFF7FB 0%, #FFFDF8 40%, #F3F9FF 100%) !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,
    #FFF7FB 0%, #FFF3F7 50%, #F5F9FF 100%) !important;
  border-right: 1.5px solid #FFD6E8 !important;
}

/* ── CEO Demo tab specific ── */
.ceo-hero-light {
  background: linear-gradient(135deg, #FFF7FB, #FFFDF8, #F3F9FF);
  border: 1.5px solid #FFD6E8;
  border-radius: 28px;
  padding: 44px 36px;
  text-align: center;
  margin-bottom: 28px;
}
.ceo-hero-light h1 {
  font-size: 2.1rem !important;
  font-weight: 900 !important;
  color: #1a1a2e !important;
  margin: 0 0 12px !important;
  line-height: 1.25 !important;
}
.ceo-hero-light p {
  font-size: 1.02rem !important;
  color: #666 !important;
  line-height: 1.8 !important;
  margin: 0 !important;
}

/* ── Screen card ── */
.screen-card {
  background: #fff;
  border: 1.5px solid #FFD6E8;
  border-radius: 24px;
  padding: 28px 30px;
  margin-bottom: 22px;
  box-shadow: 0 4px 24px rgba(255,143,175,.08);
}
.screen-label {
  font-size: .72rem;
  font-weight: 800;
  color: #FF8FAF;
  text-transform: uppercase;
  letter-spacing: .1em;
  margin-bottom: 8px;
}
.screen-title {
  font-size: 1.25rem;
  font-weight: 900;
  color: #1a1a2e;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ── Chat bubbles (light) ── */
.cb-user {
  background: #F3F9FF;
  border: 1.5px solid #C8E4FF;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 16px;
  margin: 6px 0 6px auto;
  max-width: 74%;
  font-size: .92rem;
  color: #1a2a4a;
  line-height: 1.65;
}
.cb-sheep {
  background: linear-gradient(135deg, #FFF7FB, #FFF9F3);
  border: 1.5px solid #FFD6E8;
  border-radius: 18px 18px 18px 4px;
  padding: 12px 16px;
  margin: 6px auto 6px 0;
  max-width: 74%;
  font-size: .92rem;
  color: #444;
  line-height: 1.65;
}
.cb-meta {
  font-size: .7rem;
  color: #bbb;
  margin: 0 0 10px 4px;
}

/* ── Memory card ── */
.memory-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 13px 0;
  border-bottom: 1px solid #FFF0F5;
}
.memory-item:last-child { border-bottom: none; }
.memory-ico {
  font-size: 1.3rem;
  flex-shrink: 0;
  width: 36px;
  text-align: center;
}
.memory-text { font-size: .93rem; color: #333; line-height: 1.65; flex: 1; }

/* ── AI insight card ── */
.insight-card-light {
  background: linear-gradient(135deg, #FFF7FB, #F5FBFF);
  border: 1.5px solid #FFD6E8;
  border-radius: 18px;
  padding: 18px 20px;
  margin-bottom: 12px;
}
.insight-label {
  font-size: .72rem;
  font-weight: 800;
  color: #FF8FAF;
  text-transform: uppercase;
  letter-spacing: .09em;
  margin-bottom: 8px;
}
.insight-value {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
}
.insight-sub {
  font-size: .82rem;
  color: #888;
  line-height: 1.6;
}

/* ── Confidence pill ── */
.conf-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: linear-gradient(135deg, #FF8FAF22, #7EC8E322);
  border: 1.5px solid #FFD6E8;
  border-radius: 20px;
  padding: 4px 14px;
  font-size: .8rem;
  font-weight: 700;
  color: #FF8FAF;
}

/* ── Brain scan animation ── */
@keyframes scanline {
  0%   { transform: translateY(0);   opacity: 1; }
  100% { transform: translateY(100%); opacity: 0; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.brain-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 12px;
  margin-bottom: 8px;
  border: 1.5px solid #FFD6E8;
  background: #fff;
  animation: fadeInUp .4s ease forwards;
}
.brain-step-done { border-color: #A8EEC0; background: #F0FFF8; }
.brain-step-ico { font-size: 1rem; flex-shrink: 0; }
.brain-step-text { font-size: .88rem; color: #444; flex: 1; }
.brain-step-check { font-size: 1rem; color: #34C759; flex-shrink: 0; }

/* ── Timeline ── */
.tl-wrap { position: relative; padding-left: 26px; }
.tl-wrap::before {
  content: '';
  position: absolute;
  left: 9px;
  top: 6px;
  bottom: 6px;
  width: 2px;
  background: linear-gradient(180deg, #FFD6E8 0%, #C8E4FF 100%);
}
.tl-entry {
  position: relative;
  margin-bottom: 22px;
}
.tl-dot {
  position: absolute;
  left: -22px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #FFD6E8;
}
.tl-dot-dream  { background: #FF8FAF; box-shadow: 0 0 0 2px #FF8FAF; }
.tl-dot-diary  { background: #7EC8E3; box-shadow: 0 0 0 2px #7EC8E3; }
.tl-dot-save   { background: #34C759; box-shadow: 0 0 0 2px #34C759; }
.tl-dot-wow    { background: #FFD700; box-shadow: 0 0 0 3px #FFD70060; width:16px; height:16px; left:-24px; }
.tl-date { font-size: .72rem; font-weight: 700; color: #bbb; margin-bottom: 4px; }
.tl-text { font-size: .9rem; color: #444; line-height: 1.65; }
.tl-amount {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #F0FFF8;
  border: 1px solid #A8EEC0;
  border-radius: 12px;
  padding: 2px 10px;
  font-size: .78rem;
  font-weight: 700;
  color: #1A8050;
  margin-top: 4px;
}
.tl-wow-card {
  background: linear-gradient(135deg, #FFF7FB, #F3F9FF);
  border: 2px solid #FFD6E8;
  border-radius: 18px;
  padding: 18px 20px;
  margin-top: 8px;
}
.tl-wow-title {
  font-size: 1rem;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 6px;
}
.tl-wow-pct {
  font-size: 2.6rem;
  font-weight: 900;
  color: #FF8FAF;
  line-height: 1;
  margin: 8px 0 4px;
}

/* ── Community card ── */
.comm-card {
  background: #fff;
  border: 1.5px solid #FFD6E8;
  border-radius: 18px;
  padding: 18px 20px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.comm-ico { font-size: 2rem; flex-shrink: 0; }
.comm-name { font-size: .97rem; font-weight: 800; color: #1a1a2e; margin-bottom: 2px; }
.comm-count { font-size: .8rem; color: #FF8FAF; font-weight: 700; margin-bottom: 3px; }
.comm-desc { font-size: .83rem; color: #666; line-height: 1.55; }

/* ── Micro saving step ── */
.ms-step {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 4px;
}
.ms-box {
  flex: 1;
  background: #fff;
  border: 1.5px solid #FFD6E8;
  border-radius: 14px;
  padding: 14px 16px;
  text-align: center;
}
.ms-arrow {
  font-size: 1.2rem;
  color: #FF8FAF;
  padding: 0 8px;
  flex-shrink: 0;
}
.ms-icon { font-size: 1.6rem; margin-bottom: 4px; }
.ms-label { font-size: .82rem; font-weight: 700; color: #1a1a2e; }
.ms-sub { font-size: .72rem; color: #888; margin-top: 2px; }

/* ── Demo banner ── */
.demo-banner {
  background: linear-gradient(135deg, #FFF0F7, #F0F7FF);
  border: 1.5px dashed #FFD6E8;
  border-radius: 18px;
  padding: 18px 22px;
  text-align: center;
  margin-bottom: 20px;
}

/* ── Progress bar (light) ── */
.prog-bar-wrap {
  background: #F5F5FA;
  border-radius: 10px;
  height: 10px;
  overflow: hidden;
  margin: 6px 0;
}
.prog-bar-fill {
  height: 100%;
  border-radius: 10px;
  background: linear-gradient(90deg, #FF8FAF, #7EC8E3);
}

/* ── Segment card light ── */
.seg-light {
  background: #fff;
  border: 1.5px solid #FFD6E8;
  border-radius: 18px;
  padding: 18px 20px;
  height: 100%;
}
.seg-light-active {
  border: 2.5px solid #FF8FAF;
  box-shadow: 0 0 0 4px #FF8FAF18;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CEO DEMO ENGINE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_demo_data():
    """30 ngày data cho CEO demo. Idempotent."""
    base = datetime(2026, 5, 12)  # concert mention date

    chat_script = [
        ("user",      "Cừu ơi em muốn đi concert Big Bang năm sau"),
        ("assistant", "🐑 Big Bang!! Bê bê~ Mình nghe tin rồi! Em đang ở đội 'đang lên kế hoạch' hay đội 'chưa biết bắt đầu từ đâu'? 😄"),
        ("user",      "Đội hai ạ 😂 vé chắc 3-4 triệu mà chưa biết làm sao"),
        ("assistant", "🐑 Mình hiểu! Vé concert thường 2-4 triệu tùy hạng. Còn bao lâu nữa đến concert?"),
        ("user",      "Tháng 5 năm sau, còn khoảng 12 tháng"),
        ("assistant", "🐑 12 tháng! Nếu mỗi ngày để dành 10k — chỉ bằng 1 ly trà sữa — thì 12 tháng là 3.6 triệu. Mình tạo 'Lọ Concert Big Bang' cho em nhé? 🎤"),
        ("user",      "Oke Cừu ơi! Em cũng muốn mua MacBook để học thiết kế nữa"),
        ("assistant", "🐑 Ồ thiết kế! Em học UI/UX hay đồ họa vậy? Mình hỏi để tính specs phù hợp nha."),
        ("user",      "UI/UX ạ, đang học Figma nên cần máy tốt hơn điện thoại"),
        ("assistant", "🐑 MacBook Air M4 là đủ rồi, khoảng 28-30 triệu. Em cần máy khi nào — gấp hay có thể chờ?"),
        ("user",      "Tầm 6 tháng nữa là lý tưởng ạ"),
        ("assistant", "🐑 6 tháng — cần để dành khoảng 5tr/tháng. Mình đặt mục tiêu 'MacBook Air M4' cho em nhé! 💻"),
        ("user",      "Hôm nay em mệt quá Cừu ơi, deadline 3 cái cùng lúc"),
        ("assistant", "🐑 Bê bê~ Ba deadline một lúc là quá tải thật 😔 Hôm nay không cần làm gì thêm — cứ nghỉ. Mình ở đây."),
        ("user",      "Em hay bị cuối tháng hết tiền trước lương Cừu ơi"),
        ("assistant", "🐑 Mình hiểu. Em hay tiêu nhiều nhất vào khoản nào — đồ ăn, Shopee hay gì khác?"),
        ("user",      "Shopee ạ, bạn bè tag deal là em mua luôn 😅"),
        ("assistant", "🐑 'Deal của bạn bè' — bẫy FOMO kinh điển đó! Thử mẹo này: muốn mua gì thì đặt vào wishlist, đợi 24h. 9/10 lần không mua nữa 😄"),
        ("user",      "Em thấy bạn bè đi Nhật nhiều quá, xem story mà thèm lắm"),
        ("assistant", "🐑 Nhật Bản nhỉ! Em hay xem về Kyoto hay Tokyo?"),
        ("user",      "Kyoto ạ, mùa anh đào nhìn đẹp quá Cừu ơi 🌸"),
        ("assistant", "🐑 Mình nghe đây 🌸 Có vẻ Nhật Bản không chỉ là 'muốn đi' — mà là mơ thật rồi đó. Biết đâu đây là mục tiêu thứ 3 sau concert và MacBook?"),
        ("user",      "Hôm nay sếp khen em trước team! Vui lắm Cừu ơi"),
        ("assistant", "🐑 Tin vui!!! 🎉 Em xứng đáng được khen lắm. Hôm nay phải cho Cừu ăn để ăn mừng nhé?"),
        ("user",      "Em tiết kiệm được 50k hôm nay, không mua cà phê ngoài"),
        ("assistant", "🐑 50k × 30 ngày = 1.5 triệu! Nghe nhỏ nhưng to lắm đó em ơi 🐑✨"),
        ("user",      "Cừu nhớ không em muốn đi Big Bang concert"),
        ("assistant", "🐑 Mình nhớ chứ! Em kể từ ngày 12/05 rồi — hôm nay ngày 43 em nói chuyện với mình. Em đã tích lũy được 2.3 triệu, còn 1.7 triệu nữa là đủ vé hạng B 🎤"),
    ]
    st.session_state.messages = [{"role": r, "content": c} for r, c in chat_script]

    diary_raw = [
        (0,  "😔", "áp lực",    ["cashflow","stress"],
         "Hôm nay em thấy bạn bè check-in concert nhiều quá. Mình không có tiền đi. Hơi tủi.",
         "Mình hiểu cảm giác nhìn story mà tủi 💙 Mỗi người có timeline riêng.", "Du lịch Đà Lạt"),
        (3,  "😔", "hối hận",   ["cashflow"],
         "Hôm nay em đặt Shopee hết 700k mà không biết mua gì. Xong lại tiếc.",
         "Không sao — quan trọng là em nhận ra điều này. Lần sau thử wishlist 24h nhé!", ""),
        (6,  "💪", "quyết tâm", ["milestone"],
         "Hôm nay em tiết kiệm được 50k. Không mua cà phê ngoài. Nhỏ thôi nhưng vui.",
         "50k × 30 ngày = 1.5 triệu! Mình tự hào về em đó 🐑✨", ""),
        (10, "😊", "vui",       ["career","milestone"],
         "Sếp khen em trước team hôm nay. Đang nghĩ cuối năm xin tăng lương.",
         "Em xứng đáng lắm! 🎉 Mình sẽ nhớ điều này.", "Career growth"),
        (13, "😴", "mệt",       ["stress","career"],
         "Mệt quá. Deadline 3 cái dồn lúc. Làm mãi cảm giác không đủ tiền.",
         "Ba deadline một lúc là quá tải thật. Hôm nay nghỉ ngơi đi 💙", ""),
        (16, "😊", "mơ mộng",   ["dream_travel"],
         "Em lại xem video Kyoto mùa anh đào. Đẹp quá. Không biết bao giờ đi được.",
         "Mình thấy em đang mơ về Nhật Bản thật sự rồi 🌸", "Du lịch Nhật Bản"),
        (19, "💪", "quyết tâm", ["milestone"],
         "Streak 19 ngày rồi! Em không nghĩ mình làm được lâu vậy.",
         "19 ngày! Đây là streak dài nhất của em đó 💪", ""),
        (22, "😔", "áp lực",    ["cashflow","stress"],
         "Cuối tháng lại hết tiền sớm. Em nghĩ mình không giỏi quản lý tiền.",
         "Đừng nghĩ vậy! Em đang streak 22 ngày — điều đó không phải ai cũng làm được 🐑", ""),
        (25, "😊", "vui",       ["career"],
         "Được giao project mới, team lead tin tưởng!",
         "Wow! Trách nhiệm lớn hơn nghĩa là người ta thấy tiềm năng của em 🌟", ""),
        (27, "😊", "mơ mộng",   ["dream_travel"],
         "Xem video Osaka hôm nay. Thức ăn trông ngon quá. Nhật Bản là trong top 3 mơ ước rồi.",
         "Lần thứ ba em nhắc Nhật rồi đó — mình đoán đây là giấc mơ thật sự! 🌸", "Du lịch Nhật Bản"),
        (29, "💪", "quyết tâm", ["milestone"],
         "30 ngày streak! Em không nghĩ mình làm được. Cừu ơi cảm ơn Cừu nhiều lắm 🥹",
         "30 NGÀY!! Mình tự hào về em vô cùng 🏆 Đây là cột mốc quan trọng lắm.", ""),
    ]

    entries = []
    for off, m_ico, m_txt, tags, content, reply, dream in diary_raw:
        dt = base + timedelta(days=off)
        entries.append({
            "date": dt.strftime("%d/%m/%Y"), "date_raw": dt.isoformat(),
            "mood": f"{m_ico} {m_txt}", "content": content,
            "reply": reply, "tags": tags, "dream": dream,
        })

    feed_log = []
    feed_pairs = [
        (2,50_000),(5,20_000),(7,50_000),(9,100_000),(11,20_000),
        (13,50_000),(15,50_000),(17,100_000),(19,50_000),(21,20_000),
        (22,50_000),(23,100_000),(24,50_000),(25,200_000),(26,50_000),
        (27,20_000),(28,50_000),(29,500_000),(30,100_000),(31,100_000),
    ]
    total = 0
    for day_off, amt in feed_pairs:
        dt = base + timedelta(days=day_off)
        total += amt
        feed_log.append({"date": dt.strftime("%Y-%m-%d"), "amount": amt, "cumulative": total})

    today_str = datetime.now().strftime("%Y-%m-%d")
    mem.update({
        "name": "Linh",
        "notes": [
            "Muốn đi concert Big Bang, còn 12 tháng, vé 2-4 triệu",
            "Đang học UI/UX Figma, muốn mua MacBook Air M4 trong 6 tháng",
            "Hay bị FOMO với Shopee deal từ bạn bè, đã biết mẹo wishlist 24h",
            "Hay xem video Kyoto mùa anh đào, mơ đi Nhật Bản",
            "Cuối năm muốn xin tăng lương sau khi được sếp khen",
            "Streak 30 ngày liên tiếp — kỷ lục cá nhân",
        ],
        "life_events": ["dream_travel","cashflow","career","stress","milestone","emotional"],
        "dreams": [
            {"name": "Concert Big Bang",  "amount": 4_000_000,  "saved": 2_300_000, "tags": ["entertainment"]},
            {"name": "MacBook Air M4",    "amount": 30_000_000, "saved": 1_800_000, "tags": ["education"]},
            {"name": "Du lịch Nhật Bản", "amount": 25_000_000, "saved": 500_000,   "tags": ["travel"]},
        ],
        "total_saved": total, "streak": 30,
        "last_fed_date": today_str, "last_visit_date": today_str,
        "sentiment": "positive",
        "diary_entries": entries, "feed_log": feed_log,
        "user_exp": 3_600, "current_level": 4,
        "ilucky_tickets": 6,
        "achievements": ["first_chat","streak_7","streak_30","level_4"],
        "daily_quests": {today_str: {"visit":True,"chat":True,"diary":True,"feed":True,"bonus_claimed":True}},
        "wealth_genome": {"risk_type":"medium","personality":"dream_chaser","stage":"accumulation"},
        # Demo trading data — Linh, sinh viên UI/UX, thận trọng
        "trading_data": {
            "cash_balance":        45_000_000,
            "stock_ratio":         5,
            "fund_ratio":          3,
            "bond_ratio":          2,
            "avg_holding_days":    180,
            "trade_frequency":     "low",
            "margin_usage":        False,
            "favorite_products":   ["Fund"],
            "last_30d_trade_count": 2,
        },
    })
    _save()
    st.session_state.demo_mode = True
    st.session_state.demo_dream_confirm = None


def _has_demo_data() -> bool:
    return bool(
        st.session_state.get("messages")
        or mem.get("total_saved", 0) > 0
        or mem.get("diary_entries")
    )


def _detect_latent_dream(m: dict) -> tuple | None:
    signals = {
        "Nhật Bản":  ["nhật","nhật bản","kyoto","tokyo","osaka","anh đào","sakura"],
        "Hàn Quốc": ["hàn","hàn quốc","seoul","kpop","bts","blackpink"],
        "Châu Âu":  ["châu âu","paris","rome","london","europe"],
        "iPhone":   ["iphone","16 pro","15 pro","đổi máy"],
    }
    existing = {d["name"].lower() for d in m.get("dreams", [])}
    all_text = (" ".join(m.get("notes", [])) + " " +
                " ".join(e.get("content","") for e in m.get("diary_entries",[]))).lower()

    best, best_s, best_e = None, 0, []
    for name, kws in signals.items():
        if any(name.lower() in ex for ex in existing):
            continue
        hits  = [kw for kw in kws if kw in all_text]
        count = sum(all_text.count(kw) for kw in kws)
        if count >= 2 and hits:
            score = min(97, 70 + count * 4 + len(hits) * 4)
            if score > best_s:
                best, best_s, best_e = name, score, hits[:3]
    return (best, best_s, best_e) if best and best_s >= 78 else None


def _churn_state(m: dict) -> tuple:
    """Returns (level, days, msg): level in low/medium/high"""
    today = datetime.now().date()
    def _days(key, fmt_str="%Y-%m-%d"):
        v = m.get(key, "")
        if not v: return 999
        try: return (today - datetime.strptime(v, fmt_str).date()).days
        except: return 999
    d_feed  = _days("last_fed_date")
    streak  = m.get("streak", 0)
    if d_feed >= 7:
        return "high", d_feed, (
            f"Mình hơi lo. {d_feed} ngày rồi bạn chưa ghé thăm mình. "
            "Có chuyện gì làm bạn mất động lực không? Mình ở đây mà."
        )
    if d_feed >= 3:
        return "medium", d_feed, (
            f"Đã {d_feed} ngày Cừu chưa được ăn rồi. "
            "Hôm nay cho mình ăn một chút nhé — dù nhỏ cũng được 🐑"
        )
    return "low", 0, ""


def render_future_memory(m: dict, dream_name: str = "Concert Big Bang"):
    """MÀN 7 — Future Memory Engine: timeline kể chuyện"""
    base  = datetime(2026, 5, 12)
    today = datetime.now()
    delta = (today - base).days
    dream = next((d for d in m.get("dreams",[]) if dream_name.lower() in d["name"].lower()), None)
    pct   = 0
    if dream and dream["amount"]:
        pct = min(100, int(dream.get("saved",0) / dream["amount"] * 100))

    # ── Timeline events ──
    events = [
        {
            "date": "12/05", "dot": "tl-dot-dream",
            "label": "Ngày đầu tiên",
            "text": f'"Em muốn đi concert Big Bang."',
            "sub": "Cừu lắng nghe. Và nhớ.",
        },
        {
            "date": "15/05", "dot": "tl-dot-diary",
            "label": "Nhật ký",
            "text": '"Hôm nay em thấy bạn bè check-in concert nhiều quá."',
            "sub": "AI phát hiện: FOMO + Dream signal",
        },
        {
            "date": "14/05", "dot": "tl-dot-save",
            "label": "Tiết kiệm đầu tiên",
            "text": "Cho Cừu ăn lần đầu",
            "amount": 50_000,
        },
        {
            "date": "15/06", "dot": "tl-dot-diary",
            "label": "Nhật ký ngày 34",
            "text": '"Không biết em có làm được không..."',
            "sub": "AI nhận ra: cần động viên, không cần sản phẩm",
        },
        {
            "date": "24/06", "dot": "tl-dot-wow",
            "label": None,
            "text": None,
            "wow": True,
            "pct": pct,
            "saved": dream.get("saved", 2_300_000) if dream else 2_300_000,
            "delta": delta,
        },
    ]

    st.markdown('<div class="tl-wrap">', unsafe_allow_html=True)
    for ev in events:
        if ev.get("wow"):
            st.markdown(f"""
            <div class="tl-entry">
              <div class="tl-dot {ev['dot']}"></div>
              <div class="tl-date">Hôm nay — {today.strftime('%d/%m/%Y')}</div>
              <div class="tl-wow-card">
                <div style="font-size:2rem;margin-bottom:6px;">🐑</div>
                <div class="tl-wow-title">
                  {ev['delta']} ngày trước bạn từng nghĩ điều này quá xa vời.
                </div>
                <div class="tl-wow-pct">{ev['pct']}%</div>
                <div style="font-size:.88rem;color:#888;margin-bottom:10px;">
                  hành trình {dream_name} đã hoàn thành
                </div>
                <div class="prog-bar-wrap">
                  <div class="prog-bar-fill" style="width:{ev['pct']}%;"></div>
                </div>
                <div style="margin-top:12px;font-size:.9rem;color:#555;line-height:1.65;">
                  Hôm nay bạn đã có <strong style="color:#FF8FAF;">{fmt(ev['saved'])}</strong>.<br/>
                  Mình tự hào về bạn.
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            amt_html = (
                f'<div class="tl-amount">+{fmt(ev["amount"])}</div>'
                if ev.get("amount") else ""
            )
            sub_html = (
                f'<div style="font-size:.76rem;color:#bbb;margin-top:3px;">{ev["sub"]}</div>'
                if ev.get("sub") else ""
            )
            st.markdown(f"""
            <div class="tl-entry">
              <div class="tl-dot {ev['dot']}"></div>
              <div class="tl-date">{ev['date']}  ·  {ev['label']}</div>
              <div class="tl-text">{ev['text']}</div>
              {amt_html}{sub_html}
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_ai_brain(m: dict):
    """MÀN 6 — AI Brain: step-by-step scan animation → insights"""
    import time

    dreams    = m.get("dreams", [])
    notes_cnt = len(m.get("notes", []))
    diary_cnt = len(m.get("diary_entries", []))
    chat_cnt  = len(st.session_state.get("messages", [])) // 2
    streak    = m.get("streak", 0)

    steps = [
        ("📨", f"Đọc {chat_cnt} cuộc trò chuyện..."),
        ("📔", f"Đọc {diary_cnt} nhật ký..."),
        ("💰", f"Đọc lịch sử tích lũy..."),
        ("👥", "Đọc hành vi cộng đồng..."),
    ]

    run_key = "brain_ran_" + (m.get("name") or "x")
    if not st.session_state.get(run_key):
        placeholder = st.empty()
        for i, (ico, txt) in enumerate(steps):
            rows_done = [
                f'<div class="brain-step brain-step-done">'
                f'<div class="brain-step-ico">{steps[j][0]}</div>'
                f'<div class="brain-step-text">{steps[j][1]}</div>'
                f'<div class="brain-step-check">✓</div></div>'
                for j in range(i)
            ]
            row_cur = (
                f'<div class="brain-step">'
                f'<div class="brain-step-ico">{ico}</div>'
                f'<div class="brain-step-text">{txt}</div>'
                f'<div style="font-size:.85rem;color:#bbb;">⟳</div></div>'
            )
            placeholder.markdown(
                "<div>" + "".join(rows_done) + row_cur + "</div>",
                unsafe_allow_html=True,
            )
            time.sleep(0.55)
        # Final — all done
        all_done = "".join(
            f'<div class="brain-step brain-step-done">'
            f'<div class="brain-step-ico">{ico}</div>'
            f'<div class="brain-step-text">{txt}</div>'
            f'<div class="brain-step-check">✓</div></div>'
            for ico, txt in steps
        )
        placeholder.markdown("<div>" + all_done + "</div>", unsafe_allow_html=True)
        st.session_state[run_key] = True
    else:
        all_done = "".join(
            f'<div class="brain-step brain-step-done">'
            f'<div class="brain-step-ico">{ico}</div>'
            f'<div class="brain-step-text">{txt}</div>'
            f'<div class="brain-step-check">✓</div></div>'
            for ico, txt in steps
        )
        st.markdown("<div>" + all_done + "</div>", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)

    # ── Insights ──
    findings = []
    if dreams:
        findings.append({
            "ico": "🎤",
            "label": "AI phát hiện — Giấc mơ lớn nhất",
            "value": dreams[0]["name"],
            "sub": f"Từ {chat_cnt} cuộc chat · {diary_cnt} nhật ký",
            "conf": 92,
        })
    if "stress" in m.get("life_events",[]) or "cashflow" in m.get("life_events",[]):
        findings.append({
            "ico": "💙",
            "label": "AI phát hiện — Xu hướng cảm xúc",
            "value": "Dễ bị áp lực cuối tháng",
            "sub": "Đặc biệt khi bạn bè check-in & Shopee notify",
            "conf": 88,
        })
    if streak > 0:
        findings.append({
            "ico": "🌱",
            "label": "AI phát hiện — Pattern hành vi",
            "value": f"Streak {streak} ngày — kỷ lục cá nhân",
            "sub": "Thường bỏ cuộc sau 2 tuần nếu không có milestone nhỏ",
            "conf": 84,
        })

    if findings:
        _f1, _f2, _f3 = st.columns(len(findings)) if len(findings) == 3 else (
            st.columns(2) + [st.empty()] if len(findings) == 2 else
            [st.columns(1)[0]] + [st.empty(), st.empty()]
        )
        for col, f in zip([_f1, _f2, _f3], findings):
            col.markdown(f"""
            <div class="insight-card-light">
              <div class="insight-label">{f['label']}</div>
              <div class="insight-value">{f['ico']} {f['value']}</div>
              <div class="insight-sub">{f['sub']}</div>
              <div style="margin-top:8px;">
                <span class="conf-pill">AI {f['conf']}%</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── AI Recommendations ──
    st.markdown("""
    <div style="margin-top:18px;padding:18px 20px;background:linear-gradient(135deg,#FFF7FB,#F3F9FF);
         border:1.5px solid #FFD6E8;border-radius:18px;">
      <div class="screen-label">AI đề xuất</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px;">
        <div>
          <div style="font-size:.78rem;font-weight:700;color:#888;margin-bottom:4px;">👥 Community phù hợp</div>
          <div style="font-size:.93rem;font-weight:800;color:#1a1a2e;">🎤 Big Bang Hunters</div>
          <div style="font-size:.78rem;color:#888;">3.200 người đang cùng tích lũy</div>
        </div>
        <div>
          <div style="font-size:.78rem;font-weight:700;color:#888;margin-bottom:4px;">💰 Saving habit</div>
          <div style="font-size:.93rem;font-weight:800;color:#1a1a2e;">20.000đ/ngày</div>
          <div style="font-size:.78rem;color:#888;">Phù hợp với capacity hiện tại</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


