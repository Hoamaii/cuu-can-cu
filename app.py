
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


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — 🎯 CEO DEMO FLOW
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:

    # ── 0. DEMO GATE ────────────────────────────────────────────────────────────
    _top_col1, _top_col2 = st.columns([5, 1])
    with _top_col2:
        if st.button("🔄 Reset Demo", key="btn_reset_demo", help="Load lại demo data"):
            for k in list(st.session_state.keys()):
                if k.startswith("brain_ran_"):
                    del st.session_state[k]
            _generate_demo_data()
            st.rerun()

    if not _has_demo_data():
        st.markdown("""
        <div class="demo-banner">
          <div style="font-size:2rem;margin-bottom:8px;">🐑</div>
          <div style="font-size:1.1rem;font-weight:800;color:#1a1a2e;margin-bottom:6px;">
            Chào CEO — Chưa có dữ liệu thực tế
          </div>
          <div style="font-size:.88rem;color:#888;">
            Click bên dưới để xem AI hoạt động với 30 ngày dữ liệu của Linh — 21 tuổi, UI/UX student.
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎬 Xem CEO Demo — 30 ngày dữ liệu Linh", type="primary",
                     use_container_width=True, key="btn_start_demo"):
            _generate_demo_data()
            st.rerun()
        st.stop()

    # ════════════════════════════════════════════
    # MÀN 1 — HERO
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="ceo-hero-light">
      <div style="font-size:3rem;margin-bottom:12px;">🐑</div>
      <h1>Đây không phải chatbot tài chính.</h1>
      <p style="max-width:540px;margin:0 auto;">
        Hầu hết ứng dụng đầu tư chỉ xuất hiện khi khách hàng muốn giao dịch.<br/><br/>
        Cừu xuất hiện mỗi ngày. Lắng nghe. Ghi nhớ. Hiểu khách hàng.<br/>
        Từ những điều rất đời thường:<br/><br/>
        <strong>🎤 Concert Big Bang &nbsp;·&nbsp; 💻 MacBook &nbsp;·&nbsp; ✈️ Du lịch Nhật</strong><br/><br/>
        Và biến chúng thành hành vi tích lũy mỗi ngày.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── CEO Flow indicator ──────────────────────────────────────────────────────
    _screens = [
        ("💬","Chat"),("📔","Nhật ký"),("🧠","AI nhớ"),
        ("✨","Phát hiện"),("🤖","AI Brain"),("⏳","Timeline"),
        ("👥","Cộng đồng"),("💰","Micro Saving"),
    ]
    _flow_items = "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;min-width:72px;text-align:center;">'
        f'<div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#FF8FAF,#7EC8E3);'
        f'color:#fff;display:flex;align-items:center;justify-content:center;font-size:.88rem;">{ico}</div>'
        f'<div style="font-size:.62rem;color:#aaa;margin-top:4px;">{lbl}</div></div>'
        + (f'<div style="width:20px;height:2px;background:linear-gradient(90deg,#FFD6E8,#C8E4FF);'
           f'margin-top:16px;flex-shrink:0;"></div>' if i < len(_screens)-1 else "")
        for i, (ico, lbl) in enumerate(_screens)
    )
    st.markdown(
        f'<div style="background:#fff;border:1.5px solid #FFD6E8;border-radius:18px;'
        f'padding:14px 18px;margin-bottom:24px;overflow-x:auto;">'
        f'<div style="display:flex;align-items:center;gap:0;min-width:max-content;">'
        f'{_flow_items}</div></div>',
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════
    # MÀN 2 — CHAT DEMO
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 2 · Chat</div>
      <div class="screen-title">💬 Khách hàng nói chuyện với Cừu mỗi ngày</div>
    """, unsafe_allow_html=True)

    _demo_chat = [
        ("user",  "Cừu ơi em muốn đi concert Big Bang.", None),
        ("sheep", "🐑 Big Bang!! Bê bê~ Mình nghe rồi! Em đang ở đội nào — 'đang có kế hoạch' hay 'chưa biết bắt đầu'? 😄", None),
        ("user",  "Đội hai ạ 😂 vé chắc 3-4 triệu mà em chưa biết làm sao.", None),
        ("sheep", "🐑 Vé concert thường 2-4 triệu. Còn bao lâu nữa đến concert?", "Rule Engine · 0 token"),
        ("user",  "Tháng 5 năm sau, còn 12 tháng.", None),
        ("sheep", "🐑 12 tháng! Nếu mỗi ngày để dành 10k — bằng 1 ly trà sữa — thì 12 tháng là 3.6 triệu rồi. Mình tạo 'Lọ Concert Big Bang' cho em nhé? 🎤", "LLM · Dream extracted"),
        ("user",  "Không biết em có đủ tiền không Cừu ơi.", None),
        ("sheep", "🐑 43 ngày là rất dài. Nhưng 43 ngày cũng đủ để thay đổi rất nhiều điều đó — và em đã làm được rồi 💙", "Rule Engine · Memory recall · 0 token"),
    ]

    for role, text, meta in _demo_chat:
        css = "cb-user" if role == "user" else "cb-sheep"
        align = "text-align:right;" if role == "user" else ""
        st.markdown(f'<div style="{align}"><div class="{css}">{text}</div></div>',
                    unsafe_allow_html=True)
        if meta:
            st.markdown(f'<div class="cb-meta">{meta}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # MÀN 3 — DIARY DEMO
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 3 · Nhật ký</div>
      <div class="screen-title">📔 Khách hàng viết nhật ký — AI lắng nghe</div>
    """, unsafe_allow_html=True)

    _diary_demos = [
        ("15/05", "😔", "Hôm nay em thấy bạn bè check-in concert nhiều quá. Mình không có tiền đi. Hơi tủi.",
         "Mình hiểu cảm giác nhìn story mà tủi 💙 Mỗi người có timeline riêng.", "#FFE8F0"),
        ("18/05", "😔", "Hôm nay em đặt Shopee hết 700k mà không biết mình mua gì.",
         "Không sao — quan trọng là em nhận ra. Lần sau thử wishlist 24h nhé!", "#FFF5E0"),
        ("06/06", "💪", "Hôm nay em tiết kiệm được 50k. Không mua cà phê ngoài. Nhỏ thôi nhưng em vui.",
         "50k × 30 ngày = 1.5 triệu! Mình tự hào về em đó 🐑✨", "#F0FFF8"),
    ]

    for date, mood, content, reply, bg in _diary_demos:
        st.markdown(f"""
        <div style="background:{bg};border-radius:16px;padding:16px 18px;margin-bottom:12px;
             border:1.5px solid #FFD6E8;">
          <div style="font-size:.75rem;color:#bbb;margin-bottom:6px;">{date} · {mood}</div>
          <div style="font-size:.9rem;color:#333;font-style:italic;line-height:1.65;margin-bottom:10px;">
            "{content}"
          </div>
          <div style="display:flex;align-items:flex-start;gap:8px;">
            <span style="font-size:1rem;">🐑</span>
            <div style="font-size:.85rem;color:#666;line-height:1.6;">{reply}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # MÀN 4 — ĐIỀU MÌNH NHỚ VỀ BẠN
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 4 · Memory</div>
      <div class="screen-title">🐑 Điều mình nhớ về bạn</div>
    """, unsafe_allow_html=True)

    _mem_items = [
        ("🎤", "Bạn từng kể muốn đi concert Big Bang. Còn 12 tháng — và mình đang giúp bạn đếm từng ngày."),
        ("💻", "Bạn đang tìm hiểu MacBook Air M4 để học thiết kế UI/UX trên Figma."),
        ("✈️", "Bạn hay xem video Kyoto mùa anh đào. Mình nghĩ Nhật Bản là giấc mơ thật sự của bạn."),
        ("💸", "Bạn thường thấy áp lực vào cuối tháng — hay bị kéo bởi Shopee deal từ bạn bè."),
        ("🌱", "Nhưng gần đây bạn đang cố gắng hơn. Streak 30 ngày — kỷ lục cá nhân của bạn."),
    ]

    _mh = "".join(
        f'<div class="memory-item">'
        f'<div class="memory-ico">{ico}</div>'
        f'<div class="memory-text">{txt}</div>'
        f'</div>'
        for ico, txt in _mem_items
    )
    st.markdown(f'<div>{_mh}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # MÀN 5 — ĐIỀU CỪUỪU VỪA NHẬN RA
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 5 · AI Insight</div>
      <div class="screen-title">🧠 Điều Cừu vừa nhận ra</div>
    """, unsafe_allow_html=True)

    _dreams_cur = mem.get("dreams", [])
    _streak_cur = mem.get("streak", 0)
    _churn_lv, _churn_days, _churn_msg = _churn_state(mem)

    _i1, _i2, _i3 = st.columns(3)

    # Dream insight
    if _dreams_cur:
        _d = _dreams_cur[0]
        _pct_d = min(100, int(_d.get("saved",0)/_d["amount"]*100)) if _d["amount"] else 0
        _i1.markdown(f"""
        <div class="insight-card-light" style="height:100%;">
          <div class="insight-label">🎤 Giấc mơ lớn nhất</div>
          <div class="insight-value">{_d['name']}</div>
          <div class="insight-sub">
            AI phát hiện từ 4 cuộc chat · 3 nhật ký · 2 lần nhắc lại
          </div>
          <div class="prog-bar-wrap" style="margin:10px 0 4px;">
            <div class="prog-bar-fill" style="width:{_pct_d}%;"></div>
          </div>
          <div style="font-size:.78rem;color:#FF8FAF;font-weight:700;">{_pct_d}% hành trình</div>
        </div>
        """, unsafe_allow_html=True)

    # Churn / care insight
    _churn_ico  = "🟢" if _churn_lv == "low" else ("🟡" if _churn_lv == "medium" else "🔴")
    _care_title = "Bạn đang ổn 🌿" if _churn_lv == "low" else "Cừu đang lo"
    _care_body  = (
        "Bạn đang duy trì đều đặn. Cừu không lo gì lúc này."
        if _churn_lv == "low" else _churn_msg
    )
    _i2.markdown(f"""
    <div class="insight-card-light" style="height:100%;">
      <div class="insight-label">💙 Điều AI đang lo</div>
      <div class="insight-value">{_churn_ico} {_care_title}</div>
      <div class="insight-sub">{_care_body}</div>
    </div>
    """, unsafe_allow_html=True)

    # Pride insight
    _i3.markdown(f"""
    <div class="insight-card-light" style="height:100%;">
      <div class="insight-label">🌱 Điều AI tự hào</div>
      <div class="insight-value">🔥 {_streak_cur} ngày liên tục</div>
      <div class="insight-sub">
        Đây là streak dài nhất của bạn — top 8% người dùng kiên trì nhất.<br/>
        14 ngày gần đây bạn đang kiên trì hơn trước rất nhiều.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Dream detection WOW
    _latent = _detect_latent_dream(mem)
    if _latent and not st.session_state.get("demo_dream_confirm"):
        _dn, _dc, _de = _latent
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FFF7FB,#F3F9FF);border:2px solid #FFD6E8;
             border-radius:18px;padding:22px 24px;margin-top:14px;text-align:center;">
          <div style="font-size:1.8rem;margin-bottom:8px;">🐑</div>
          <div style="font-size:1rem;color:#555;line-height:1.7;margin-bottom:12px;">
            Mình nghĩ mình vừa phát hiện ra điều gì đó...<br/>
            Bạn hay nhắc đến
            <strong style="color:#FF8FAF;">{', '.join(_de)}</strong> nhiều lần.<br/>
            Có vẻ bạn đang mơ về:
          </div>
          <div style="font-size:1.6rem;font-weight:900;color:#1a1a2e;margin:8px 0;">
            ✨ {_dn} ✨
          </div>
          <div style="font-size:.85rem;color:#888;margin-bottom:14px;">Mình có đoán đúng không?</div>
          <span class="conf-pill">AI {_dc}%</span>
        </div>
        """, unsafe_allow_html=True)
        _wc1, _wc2, _wc3 = st.columns([3,1,1])
        with _wc2:
            if st.button("✅ Đúng rồi!", type="primary", key="btn_wow_yes", use_container_width=True):
                if _dn not in [d["name"] for d in mem.get("dreams",[])]:
                    mem.setdefault("dreams",[]).append(
                        {"name":_dn,"amount":25_000_000,"saved":0,"tags":["travel"]}
                    )
                    _save()
                st.session_state.demo_dream_confirm = _dn
                st.rerun()
        with _wc3:
            if st.button("❌ Chưa", key="btn_wow_no", use_container_width=True):
                st.session_state.demo_dream_confirm = f"no_{_dn}"
                st.rerun()
    elif st.session_state.get("demo_dream_confirm") and not str(st.session_state.demo_dream_confirm).startswith("no_"):
        st.markdown(f"""
        <div style="background:#F0FFF8;border:1.5px solid #A8EEC0;border-radius:14px;
             padding:14px 18px;margin-top:14px;">
          <span style="font-size:.9rem;color:#1A8050;">
            🐑 Bê bê~ Mình đoán đúng rồi! Đã thêm
            <strong>{st.session_state.demo_dream_confirm}</strong> vào mục tiêu của bạn 💙
          </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # MÀN 6 — AI BRAIN
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 6 · AI Brain</div>
      <div class="screen-title">🤖 AI đang suy luận</div>
    """, unsafe_allow_html=True)

    render_ai_brain(mem)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # MÀN 7 — FUTURE MEMORY ENGINE
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 7 · Future Memory</div>
      <div class="screen-title">⏳ Hành trình của bạn — AI nhớ từng ngày</div>
    """, unsafe_allow_html=True)

    _tm1, _tm2 = st.columns([2, 3])
    with _tm1:
        _d_main = next(
            (d for d in mem.get("dreams",[]) if "big bang" in d["name"].lower()),
            mem.get("dreams",[{}])[0] if mem.get("dreams") else {},
        )
        _pct_main = 0
        if _d_main.get("amount"):
            _pct_main = min(100, int(_d_main.get("saved",0)/_d_main["amount"]*100))
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FFF7FB,#F3F9FF);border:1.5px solid #FFD6E8;
             border-radius:18px;padding:20px;text-align:center;">
          <div style="font-size:.78rem;font-weight:800;color:#FF8FAF;text-transform:uppercase;
               letter-spacing:.08em;margin-bottom:10px;">Mục tiêu đang theo dõi</div>
          <div style="font-size:1rem;font-weight:800;color:#1a1a2e;margin-bottom:14px;">
            {_d_main.get('name','Concert Big Bang')}
          </div>
          <div style="font-size:2.8rem;font-weight:900;color:#FF8FAF;line-height:1;">
            {_pct_main}%
          </div>
          <div style="font-size:.82rem;color:#888;margin-bottom:12px;">hoàn thành</div>
          <div class="prog-bar-wrap">
            <div class="prog-bar-fill" style="width:{_pct_main}%;"></div>
          </div>
          <div style="margin-top:12px;font-size:.85rem;color:#555;">
            <strong style="color:#FF8FAF;">{fmt(_d_main.get('saved',2_300_000))}</strong>
            &nbsp;/&nbsp; {fmt(_d_main.get('amount',4_000_000))}
          </div>
          <div style="margin-top:10px;font-size:.82rem;color:#888;font-style:italic;">
            Streak 30 ngày · 43 ngày hành trình
          </div>
        </div>
        """, unsafe_allow_html=True)
    with _tm2:
        render_future_memory(mem, _d_main.get("name","Concert Big Bang"))

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # MÀN 8 — COMMUNITY
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 8 · Community</div>
      <div class="screen-title">👥 Bạn không đi một mình</div>
    """, unsafe_allow_html=True)

    _communities = [
        ("🎤","Big Bang Hunters","3.200 người","Đang cùng tích lũy để đi concert. Chia sẻ setlist, tips săn vé, hỗ trợ nhau."),
        ("💻","MacBook Builders","5.100 người","Đang tích lũy mua MacBook để học thiết kế, code, content."),
        ("✈️","Japan Dreamers","4.700 người","Đang tiết kiệm cho chuyến đi Nhật. Lịch trình Kyoto, Osaka, tips visa."),
    ]
    for ico, name, count, desc in _communities:
        _is_me = ("big bang" in name.lower() and
                  any("big bang" in d["name"].lower() for d in mem.get("dreams",[])))
        _border = "border:2px solid #FF8FAF;box-shadow:0 0 0 4px #FF8FAF12;" if _is_me else ""
        _badge  = f'<span style="font-size:.72rem;font-weight:800;color:#FF8FAF;margin-left:8px;">← bạn ở đây</span>' if _is_me else ""
        st.markdown(f"""
        <div class="comm-card" style="{_border}">
          <div class="comm-ico">{ico}</div>
          <div style="flex:1;">
            <div class="comm-name">{name}{_badge}</div>
            <div class="comm-count">{count}</div>
            <div class="comm-desc">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # MÀN 9 — MICRO SAVING
    # ════════════════════════════════════════════
    st.markdown("""
    <div class="screen-card">
      <div class="screen-label">Màn 9 · Micro Saving</div>
      <div class="screen-title">💰 Tiền lẻ → Giấc mơ</div>
    """, unsafe_allow_html=True)

    _ms1, _ms2 = st.columns([3, 2])

    with _ms1:
        _flow_ms = [
            ("💸", "Tiền lẻ",          "10k · 20k · 50k mỗi ngày"),
            ("🐑", "Cho Cừu ăn",        "1 tap · Streak tăng · Level lên"),
            ("🔄", "Mua Chứng Chỉ Quỹ TCC", "TCBF · TCFF · TCEF tự động"),
            ("📈", "Tài sản tăng nhẹ",  "Tốt hơn gửi ngân hàng"),
            ("🎯", "Giấc mơ tiến gần",  "Concert · MacBook · Nhật Bản"),
        ]
        for i, (ico, label, sub) in enumerate(_flow_ms):
            arrow = (
                f'<div class="ms-arrow">↓</div>'
                if i < len(_flow_ms)-1 else ""
            )
            st.markdown(f"""
            <div class="ms-box" style="margin-bottom:4px;">
              <div class="ms-icon">{ico}</div>
              <div class="ms-label">{label}</div>
              <div class="ms-sub">{sub}</div>
            </div>
            {arrow}
            """, unsafe_allow_html=True)

    with _ms2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF7FB,#F3F9FF);border:1.5px solid #FFD6E8;
             border-radius:18px;padding:20px 22px;">
          <div class="screen-label">Token Architecture</div>
          <div style="font-size:.9rem;font-weight:800;color:#1a1a2e;margin-bottom:14px;">
            90% tương tác không cần AI
          </div>
        """, unsafe_allow_html=True)

        _arch_rows = [
            ("🔵", "Rule Engine", "90%", "Greeting · Streak · Feed · Reminder"),
            ("🟡", "Embedding",   "8%",  "Dream match · Segment classify"),
            ("🔴", "LLM",         "2%",  "Diary mới · Dream mới · Insight mới"),
        ]
        for dot, label, pct, desc in _arch_rows:
            _pct_num = int(pct.replace("%",""))
            st.markdown(f"""
            <div style="margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                <span style="font-size:.82rem;font-weight:700;color:#333;">{dot} {label}</span>
                <span style="font-size:.82rem;font-weight:800;color:#FF8FAF;">{pct}</span>
              </div>
              <div class="prog-bar-wrap">
                <div class="prog-bar-fill" style="width:{_pct_num}%;"></div>
              </div>
              <div style="font-size:.72rem;color:#aaa;margin-top:2px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
          <div style="border-top:1px solid #FFD6E8;padding-top:12px;margin-top:4px;">
            <div style="font-size:.82rem;color:#555;line-height:1.65;">
              → Chi phí AI giảm <strong style="color:#FF8FAF;">90%</strong><br/>
              → 100.000 user/tháng ≈ <strong>$6.700</strong><br/>
              → vs không tối ưu: ~$67.000
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # CLOSING — CEO Summary
    # ════════════════════════════════════════════
    _dreams_all = mem.get("dreams",[])
    _total_saved = mem.get("total_saved", 0)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FFF7FB,#FFFDF8,#F3F9FF);
         border:2px solid #FFD6E8;border-radius:24px;padding:36px 32px;
         text-align:center;margin-top:8px;">
      <div style="font-size:2.5rem;margin-bottom:12px;">🐑</div>
      <div style="font-size:1.4rem;font-weight:900;color:#1a1a2e;margin-bottom:14px;">
        AI đang hiểu khách hàng tốt hơn TCBS từng làm.
      </div>
      <div style="font-size:.95rem;color:#666;line-height:1.9;max-width:580px;margin:0 auto;">
        Không phải vì AI phân tích dữ liệu.<br/>
        Mà vì AI <strong style="color:#FF8FAF;">lắng nghe</strong> ·
        <strong style="color:#7EC8E3;">ghi nhớ</strong> ·
        <strong style="color:#34C759;">suy luận</strong> ·
        <strong style="color:#FFD700;">dự đoán</strong> ·
        <strong style="color:#FF8FAF;">động viên</strong>.<br/><br/>
        Mỗi ngày. Không chỉ khi khách hàng muốn giao dịch.
      </div>
      <div style="margin-top:20px;display:flex;justify-content:center;gap:24px;flex-wrap:wrap;">
        <div style="text-align:center;">
          <div style="font-size:1.5rem;font-weight:900;color:#FF8FAF;">{mem.get('streak',30)}</div>
          <div style="font-size:.75rem;color:#aaa;">ngày streak</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:1.5rem;font-weight:900;color:#7EC8E3;">{fmt(_total_saved)}</div>
          <div style="font-size:.75rem;color:#aaa;">tích lũy được</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:1.5rem;font-weight:900;color:#34C759;">{len(_dreams_all)}</div>
          <div style="font-size:.75rem;color:#aaa;">giấc mơ AI nhớ</div>
        </div>
        <div style="text-align:center;">
          <div style="font-size:1.5rem;font-weight:900;color:#FFD700;">-90%</div>
          <div style="font-size:.75rem;color:#aaa;">chi phí AI</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
