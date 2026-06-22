"""
╔══════════════════════════════════════════════════════════════════╗
║   CỪU CẦN CÙ — v5.0  AI Financial Companion                    ║
║   Principal PM · Behavioral Scientist · AI Architect            ║
║   Architecture: Dream Graph + Wealth Genome + Behavior Engine   ║
╚══════════════════════════════════════════════════════════════════╝
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
import datetime
from copy import deepcopy

st.set_page_config(
    page_title="Cừu Cần Cù 🐑",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════
# MASCOT ENGINE
# ═══════════════════════════════════════════════════════
_HERE       = os.path.dirname(os.path.abspath(__file__))
_ASSETS_DIR = os.path.join(_HERE, "assets")
_ROOT_MASCOT= os.path.join(_HERE, "mascot.png")
_SVG_SHEEP  = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='48' fill='%23FFE4F0'/%3E"
    "%3Ctext y='.88em' x='10' font-size='76'%3E%F0%9F%90%91%3C/text%3E%3C/svg%3E"
)
_MOOD_PATTERNS = {
    "default":    ["mascot","sheep_adult","sheep_happy"],
    "listening":  ["sheep_listening","listening"],
    "happy":      ["sheep_happy","happy"],
    "sad":        ["sheep_sad","sad"],
    "miss_you":   ["sheep_miss_you","miss_you"],
    "saving":     ["sheep_saving","saving"],
    "celebrate":  ["sheep_celebrate","celebrate","sheep_happy"],
    "determined": ["sheep_determined","determined"],
    "dream":      ["sheep_dream","dream","sheep_happy"],
    "baby":       ["sheep_baby","baby"],
    "child":      ["sheep_child","child"],
    "teen":       ["sheep_teen","teen"],
    "adult":      ["sheep_adult","adult"],
    "master":     ["sheep_master","master"],
}

@st.cache_data(ttl=300, show_spinner=False)
def _scan_assets() -> dict:
    os.makedirs(_ASSETS_DIR, exist_ok=True)
    all_files = []
    for ext in ("*.png","*.jpg","*.jpeg","*.webp"):
        all_files += glob.glob(os.path.join(_ASSETS_DIR, ext))
    if os.path.exists(_ROOT_MASCOT):
        all_files.append(_ROOT_MASCOT)
    result = {}
    for mood, patterns in _MOOD_PATTERNS.items():
        matched = []
        for fp in all_files:
            fname = os.path.splitext(os.path.basename(fp))[0].lower()
            for p in patterns:
                if fname == p.lower() or fname.startswith(p.lower()+"_"):
                    matched.append(fp); break
        result[mood] = matched
    return result

def _pick_mascot(mood="default"):
    assets = _scan_assets()
    files  = assets.get(mood, [])
    if not files:
        for fb in ("happy","adult","default"):
            files = assets.get(fb,[])
            if files: break
    return random.choice(files) if files else None

@st.cache_data(ttl=7200, show_spinner=False)
def _b64(path):
    if not path or not os.path.exists(path): return _SVG_SHEEP
    try:
        with open(path,"rb") as f: raw=f.read()
        ext  = path.rsplit(".",1)[-1].lower()
        mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","webp":"image/webp"}.get(ext,"image/png")
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except: return _SVG_SHEEP

def show_sheep(mood=None, width=160, show_badge=True):
    m   = mood or st.session_state.get("sheep_mood","default")
    src = _b64(_pick_mascot(m))
    badge = {
        "listening":"👂 Cừu đang lắng nghe...",
        "happy":"😊 Bê bê~ Cừu vui lắm!",
        "sad":"🥺 Không sao, mình vẫn ở đây.",
        "miss_you":"💙 Cừu nhớ bạn lắm...",
        "saving":"💰 Tích tiểu thành đại!",
        "celebrate":"🎉 Bê bê~ Cừu ăn mừng cùng bạn!",
        "dream":"✨ Cùng hiện thực hóa giấc mơ nhé!",
    }.get(m,"")
    st.markdown(
        f'<div style="text-align:center;margin:8px 0 6px;">'
        f'<img src="{src}" width="{width}" style="border-radius:50%;'
        f'border:4px solid #FFB5C8;box-shadow:0 10px 32px rgba(255,140,190,.5),'
        f'0 0 0 8px rgba(255,182,193,.18);" /></div>',
        unsafe_allow_html=True,
    )
    if show_badge and badge:
        st.caption(badge)

def show_growth_sheep(total_saved, width=200):
    key, name, lv, desc, _ = get_growth_stage(total_saved)
    src = _b64(_pick_mascot(key))
    st.markdown(
        f'<div style="text-align:center;padding:12px 0;">'
        f'<img src="{src}" width="{width}" style="border-radius:50%;'
        f'border:5px solid #FFB5C8;box-shadow:0 12px 36px rgba(255,140,190,.55),'
        f'0 0 0 10px rgba(255,182,193,.2);" /></div>',
        unsafe_allow_html=True,
    )

def set_mood(m): st.session_state.sheep_mood = m

# ═══════════════════════════════════════════════════════
# GROWTH STAGES
# ═══════════════════════════════════════════════════════
GROWTH_STAGES = [
    (0,          "baby",  "🐑 Cừu Sơ Sinh",     1, "Vừa mới gặp bạn, còn hơi nhút nhát.",       "Chào bạn! Mình vừa ra đời~ Bê bê..."),
    (100_000,    "child", "🐑 Cừu Non",          2, "Đang học cách tích lũy từng chút một.",       "Mình đã lớn hơn rồi! ❤️"),
    (500_000,    "teen",  "🐑 Cừu Thiếu Niên",   3, "Đã bắt đầu có những ước mơ lớn.",            "Mình đang trưởng thành nhờ bạn! 💪"),
    (2_000_000,  "adult", "🐑 Cừu Trưởng Thành", 4, "Biết quản lý tiền và theo đuổi mục tiêu.",   "Cùng nhau đến đỉnh cao nhé 🌟"),
    (10_000_000, "master","🐑 Cừu Lão Luyện",    5, "Người đồng hành tài chính đáng tin cậy.",    "Chúng mình đã đi một chặng đường dài! 🏆"),
]

def get_growth_stage(total_saved):
    result = GROWTH_STAGES[0]
    for s in GROWTH_STAGES:
        if total_saved >= s[0]: result = s
    _, key, name, lv, desc, msg = result
    return key, name, lv, desc, msg

def fmt(n): return f"{n:,.0f}đ".replace(",",".")

# ═══════════════════════════════════════════════════════
# EXP / LEVEL SYSTEM
# ═══════════════════════════════════════════════════════
EXP_LEVELS = {1:0, 2:500, 3:1500, 4:3000, 5:6000, 6:12000}
LEVEL_NAMES = {
    1:"🌱 Cừu Mới",2:"🌿 Cừu Nhỏ",3:"🌸 Cừu Ngoan",
    4:"⭐ Cừu Giỏi",5:"💫 Cừu Xuất Sắc",6:"🏆 Cừu Huyền Thoại"
}
LEVEL_ILUCKY = {1:1,2:2,3:2,4:3,5:3,6:5}
LEVEL_ITEMS  = {
    2:["🎀 Nơ Hồng"],3:["👟 Giày Thể Thao"],
    4:["🕶️ Kính Mát"],5:["🎩 Mũ Nón"],6:["💎 Vương Miện"]
}

def _add_exp(amount, mem):
    mem["exp"] = mem.get("exp",0) + amount
    old_lv = mem.get("level",1)
    new_lv = old_lv
    for lv in range(old_lv+1, 7):
        if mem["exp"] >= EXP_LEVELS.get(lv, 999999): new_lv = lv
    if new_lv > old_lv:
        mem["level"] = new_lv
        tickets = LEVEL_ILUCKY.get(new_lv, 1)
        mem["ilucky_tickets"] = mem.get("ilucky_tickets",0) + tickets
        new_item = LEVEL_ITEMS.get(new_lv)
        if new_item:
            mem.setdefault("wardrobe",[])
            for it in new_item:
                if it not in mem["wardrobe"]: mem["wardrobe"].append(it)
        st.session_state["just_leveled_up"] = True
        st.session_state["new_level_name"]  = LEVEL_NAMES.get(new_lv,"")
        st.session_state["new_level_num"]   = new_lv
        return True
    return False

def _complete_quest(mem, key, exp_reward=50):
    today = datetime.date.today().isoformat()
    mem.setdefault("daily_quests",{})
    mem["daily_quests"].setdefault(today,{})
    if not mem["daily_quests"][today].get(key):
        mem["daily_quests"][today][key] = True
        _add_exp(exp_reward, mem)
        # Check bonus
        dq = mem["daily_quests"][today]
        done = sum(1 for k,v in dq.items() if k != "bonus_claimed" and v)
        if done >= 3 and not dq.get("bonus_claimed"):
            mem["daily_quests"][today]["bonus_claimed"] = True
            mem["ilucky_tickets"] = mem.get("ilucky_tickets",0) + 1
            _add_exp(100, mem)
            st.session_state["bonus_quest_done"] = True

# ═══════════════════════════════════════════════════════
# FEED OPTIONS (Tamagotchi)
# ═══════════════════════════════════════════════════════
FEED_OPTIONS = [
    {"label":"🥬 Bó Cỏ",    "amount":10_000,  "exp":10,  "hunger":10,"emoji":"🥬"},
    {"label":"🥕 Củ Cà Rốt","amount":20_000,  "exp":20,  "hunger":20,"emoji":"🥕"},
    {"label":"🍎 Trái Táo",  "amount":50_000,  "exp":50,  "hunger":35,"emoji":"🍎"},
    {"label":"🎂 Bánh Kem",  "amount":100_000, "exp":100, "hunger":55,"emoji":"🎂"},
    {"label":"🎉 Tiệc Lớn",  "amount":500_000, "exp":300, "hunger":80,"emoji":"🎉"},
]

# ═══════════════════════════════════════════════════════
# MEMORY DEFAULT (v5 — expanded)
# ═══════════════════════════════════════════════════════
MEMORY_DEFAULT = {
    # Core Identity
    "name":                   "",
    "age":                    0,
    "city":                   "",
    "occupation":             "",
    # Financial
    "total_saved":            0,
    "monthly_income":         0,
    "monthly_saving_capacity":0,
    # Gamification
    "streak":                 0,
    "exp":                    0,
    "level":                  1,
    "achievements":           [],
    "ilucky_tickets":         0,
    "wardrobe":               [],
    "house_level":            1,
    "energy":                 100,
    "hunger":                 50,
    "last_feed_date":         "",
    "new_level_tickets":      0,
    # Dream Graph (v5)
    "dreams":                 [],
    # Life Events (v5)
    "life_events":            {},
    # Wealth Genome (v5)
    "wealth_genome":          {},
    # Behavior Metrics
    "behavior_metrics":       {"engagement":0,"churn_risk":0,"attachment":0},
    # Dream Feed Cache
    "dream_feed_cache":       {},
    "last_feed_refresh":      "",
    # Journey
    "journey_timeline":       [],
    # Memory engine
    "notes":                  [],
    "diary_entries":          [],
    "key_facts":              {},
    "last_visit_date":        "",
    # Quests
    "daily_quests":           {},
    # Reports
    "weekly_reports":         [],
    "monthly_reports":        [],
    # Family
    "family_members":         [],
    "family_code":            "",
    # Settings
    "api_key":                "",
}

# ═══════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════
if "user_memory" not in st.session_state:
    st.session_state.user_memory = deepcopy(MEMORY_DEFAULT)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sheep_mood" not in st.session_state:
    st.session_state.sheep_mood = "default"

def _save():
    st.session_state.user_memory = st.session_state.user_memory

# ═══════════════════════════════════════════════════════
# HUNGER / ENERGY SYSTEM
# ═══════════════════════════════════════════════════════
def _update_hunger(mem):
    today = datetime.date.today().isoformat()
    last  = mem.get("last_feed_date","")
    if last and last != today:
        try:
            days_since = (datetime.date.today() - datetime.date.fromisoformat(last)).days
            mem["hunger"] = max(0, mem.get("hunger",50) - days_since * 15)
        except: pass
    return mem.get("hunger", 50)

def _get_hunger_state(hunger):
    if hunger >= 80: return "full",    "😊", "Cừu no nê~",          "#10b981"
    if hunger >= 50: return "ok",      "🙂", "Cừu đang ổn",          "#f59e0b"
    if hunger >= 20: return "hungry",  "😢", "Cừu hơi đói rồi...",  "#f97316"
    return               "starving","😭", "Cừu đói lắm bạn ơi!","#ef4444"

def _get_energy(mem):
    streak = mem.get("streak",0)
    pct = min(100, 20 + streak*5)
    if pct >= 70: return pct, "⚡ Năng lượng dồi dào!"
    if pct >= 40: return pct, "🌿 Năng lượng ổn định"
    return pct, "😴 Cần nạp năng lượng"

# ═══════════════════════════════════════════════════════
# STREAK ENGINE
# ═══════════════════════════════════════════════════════
def _update_streak(mem):
    today     = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(1)).isoformat()
    last      = mem.get("last_feed_date","")
    if last == today:    return mem.get("streak",0)
    if last == yesterday: mem["streak"] = mem.get("streak",0) + 1
    elif last != "":      mem["streak"] = 1
    else:                 mem["streak"] = mem.get("streak",1) or 1
    mem["last_feed_date"] = today
    return mem["streak"]

# ═══════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════
# AI LAYER 1 — MEMORY ENGINE
# ═══════════════════════════════════════════════════════
def _extract_memory(text, mem):
    text_lower = text.lower()
    # Name
    name_match = re.search(r"(?:tên|mình là|tôi là|gọi.*là)\s+([A-ZÀÁẠẢÃĂẮẶẲẴÂẤẬẨẪĐÈÉẸẺẼÊẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỐỘỔỖƠỚỢỞỠÙÚỤỦŨƯỨỰỬỮỲÝỴỶỸA-z]{2,20})", text, re.IGNORECASE)
    if name_match and not mem.get("name"): mem["name"] = name_match.group(1).strip().title()
    # City
    for city in ["Hà Nội","HCM","Sài Gòn","Đà Nẵng","Hải Phòng","Cần Thơ"]:
        if city.lower() in text_lower and not mem.get("city"): mem["city"] = city
    # Stress
    if any(w in text_lower for w in ["mệt","stress","áp lực","khó","căng thẳng"]):
        mem.setdefault("life_events",{})["stress_level"] = min(100, mem["life_events"].get("stress_level",30)+15)

def _return_msg(mem):
    days = (datetime.date.today() - datetime.date.fromisoformat(mem["last_visit_date"])).days if mem.get("last_visit_date") else 0
    if days == 0: return 0,"💚","Cừu ở đây!","Cừu rất vui khi thấy bạn hôm nay 😊"
    if days == 1: return 1,"🌟","Đúng hẹn!","Cừu đã đợi bạn! Cùng tiếp tục nhé 🌟"
    if days <= 3: return days,"💛","Cừu nhớ!",f"Đã {days} ngày rồi... Cừu nhớ bạn lắm 💛"
    if days <= 7: return days,"🧡","Lâu quá!",f"{days} ngày rồi... Cừu hơi buồn nhưng vẫn ở đây 🧡"
    return days,"🌱","Không sao cả.",f"Đã {days} ngày rồi... Mình vẫn ở đây đồng hành với bạn."

# ═══════════════════════════════════════════════════════
# AI LAYER 2 — DREAM GRAPH ENGINE
# ═══════════════════════════════════════════════════════
DREAM_CATEGORIES = {
    "travel":   ["nhật","japan","tokyo","hàn","korea","châu âu","paris","du lịch","đi chơi","explore"],
    "home":     ["nhà","chung cư","apartment","mua nhà","căn hộ","bất động sản"],
    "car":      ["xe","ô tô","vinfast","toyota","honda","mua xe"],
    "business": ["kinh doanh","startup","khởi nghiệp","shop","quán","mở"],
    "education":["học","đại học","du học","thạc sĩ","tiến sĩ","khoá học","certification"],
    "freedom":  ["tự do","fire","nghỉ hưu","passive income","không cần đi làm"],
    "family":   ["cưới","kết hôn","con","em bé","gia đình","wedding"],
    "health":   ["sức khoẻ","gym","tập","giảm cân","yoga"],
}

def _extract_dream(text, existing_dreams):
    text_lower = text.lower()
    for cat, keywords in DREAM_CATEGORIES.items():
        for kw in keywords:
            if kw in text_lower:
                # Don't duplicate
                if any(d.get("category")==cat for d in existing_dreams): continue
                dream_id = f"dream_{cat}_{len(existing_dreams)+1}"
                # Extract name from text
                name_map = {
                    "travel":"Du lịch","home":"Mua nhà","car":"Mua xe",
                    "business":"Khởi nghiệp","education":"Học tập",
                    "freedom":"Tự do tài chính","family":"Hôn nhân/Gia đình","health":"Sức khoẻ"
                }
                name = name_map.get(cat, cat.title())
                if "nhật" in text_lower or "japan" in text_lower: name = "Du lịch Nhật Bản"
                elif "hàn" in text_lower or "korea" in text_lower: name = "Du lịch Hàn Quốc"
                elif "châu âu" in text_lower or "paris" in text_lower: name = "Du lịch Châu Âu"
                elif "chung cư" in text_lower: name = "Mua chung cư"
                elif "vinfast" in text_lower: name = "Mua xe VinFast"
                return {
                    "dream_id":       dream_id,
                    "name":           name,
                    "category":       cat,
                    "subcategory":    kw,
                    "motivation":     "",
                    "timeline":       "",
                    "target_amount":  0,
                    "saved_amount":   0,
                    "priority_score": 70,
                    "created_at":     datetime.date.today().isoformat(),
                    "last_mentioned": datetime.date.today().isoformat(),
                }
    return None

def _score_dream_priority(dream, mem):
    score = 50
    # Recency boost
    try:
        days = (datetime.date.today() - datetime.date.fromisoformat(dream.get("last_mentioned","2020-01-01"))).days
        score += max(0, 20 - days)
    except: pass
    # Has timeline
    if dream.get("timeline"): score += 15
    # Has target amount
    if dream.get("target_amount",0) > 0: score += 10
    # Saved progress
    saved_pct = int(dream.get("saved_amount",0)/max(dream.get("target_amount",1),1)*100)
    if saved_pct > 0: score += min(5, saved_pct//10)
    return min(100, score)

def get_top_dream(mem):
    dreams = mem.get("dreams",[])
    if not dreams: return None
    return sorted(dreams, key=lambda d: d.get("priority_score",50), reverse=True)[0]

# ═══════════════════════════════════════════════════════
# AI LAYER 3 — WEALTH GENOME BUILDER
# ═══════════════════════════════════════════════════════
ARCHETYPE_CONFIG = {
    "DreamChaser":      {"emoji":"🌏","name":"Dream Chaser","color":"#6d28d9","bg":"#f5f3ff",
                         "desc":"Bạn sống cho trải nghiệm — mỗi giấc mơ là một hành trình",
                         "tiny_action":"Hôm nay chỉ cần {amount} = 1 bước nhỏ tới {dream}",
                         "fund_match":"TCEF"},
    "HomeBuilder":      {"emoji":"🏠","name":"Home Builder","color":"#1d4ed8","bg":"#eff6ff",
                         "desc":"Bạn xây dựng nền tảng — ổn định là giá trị cốt lõi",
                         "tiny_action":"Thêm {amount} hôm nay = 1 viên gạch cho ngôi nhà của bạn",
                         "fund_match":"TCBF"},
    "FamilyProtector":  {"emoji":"👨‍👩‍👧","name":"Family Protector","color":"#065f46","bg":"#ecfdf5",
                         "desc":"Bạn sống vì gia đình — tình yêu là động lực lớn nhất",
                         "tiny_action":"20k hôm nay = bảo vệ tương lai của người bạn thương",
                         "fund_match":"TCFF"},
    "WealthBuilder":    {"emoji":"💰","name":"Wealth Builder","color":"#b45309","bg":"#fffbeb",
                         "desc":"Bạn nghĩ chiến lược — tiền là công cụ tạo tự do",
                         "tiny_action":"DCA đều đặn hôm nay — tiền phải làm việc cho bạn",
                         "fund_match":"TCEF"},
    "SafetySeeker":     {"emoji":"🛡️","name":"Safety Seeker","color":"#374151","bg":"#f9fafb",
                         "desc":"Bạn ưu tiên an toàn — từng bước chắc chắn hơn nhanh",
                         "tiny_action":"10k hôm nay = quỹ khẩn cấp vững chắc hơn",
                         "fund_match":"TCBF"},
}

def _classify_archetype(mem):
    dreams  = mem.get("dreams",[])
    events  = mem.get("life_events",{})
    cats    = [d.get("category","") for d in dreams]

    if "freedom" in cats or "business" in cats: return "WealthBuilder"
    if "family"  in cats or events.get("has_kids"): return "FamilyProtector"
    if "home"    in cats: return "HomeBuilder"
    if "travel"  in cats or "education" in cats: return "DreamChaser"
    if events.get("stress_level",0) > 60: return "SafetySeeker"
    return "DreamChaser"  # default

def _build_wealth_genome(mem):
    archetype = _classify_archetype(mem)
    streak    = mem.get("streak",0)
    level     = mem.get("level",1)
    n_dreams  = len(mem.get("dreams",[]))
    n_diary   = len(mem.get("diary_entries",[]))
    total     = mem.get("total_saved",0)

    # Saving discipline: streak + consistency
    discipline = min(100, streak*3 + level*5 + min(n_diary,10)*2)
    # Financial confidence: engagement with financial content
    confidence = min(100, n_dreams*10 + level*8 + min(total//100000,20))
    # Investment readiness: discipline + confidence + savings threshold
    readiness  = min(100, int((discipline*0.4 + confidence*0.3 + min(total//500000,30)*0.3)))

    genome = {
        "archetype":            archetype,
        "saving_discipline":    discipline,
        "financial_confidence": confidence,
        "investment_readiness": readiness,
        "risk_tolerance":       50 if archetype in ("WealthBuilder","DreamChaser") else 30,
        "dca_ready":            discipline >= 40 and streak >= 7,
        "invest_ready":         readiness >= 60 and total >= 1_000_000,
        "updated_at":           datetime.date.today().isoformat(),
    }
    mem["wealth_genome"] = genome
    return genome

# ═══════════════════════════════════════════════════════
# AI LAYER 4 — DREAM FEED ENGINE
# ═══════════════════════════════════════════════════════
DREAM_FEED_DB = {
    "travel_nhật": [
        {"icon":"🗾","source":"TikTok Trend","title":"Mùa lá đỏ Kyoto 2025 — bao nhiêu ngày là đủ?",
         "body":"Creator @travel.viet: 7 ngày = Kyoto + Osaka + Tokyo. Budget 28-35tr all-in.",
         "sheep_msg":"Bạn từng kể muốn đi Nhật mùa lá đỏ. Tháng 11 đang tiến lại gần — hôm nay cho mình ăn thêm 30k nhé?"},
        {"icon":"🍜","source":"Reddit r/VietNam","title":"Chi phí thực tế 7 ngày Nhật Bản 2025",
         "body":"User u/hanoi_traveler: Tổng 32tr cho 2 người, vé 6.8tr/người mua sớm 3 tháng.",
         "sheep_msg":"Cừu tính: nếu bạn tích 50k/ngày = sau 6 tháng đủ vé + khách sạn rồi đấy!"},
    ],
    "travel_hàn": [
        {"icon":"🌸","source":"TikTok","title":"Seoul mùa hoa anh đào tháng 4",
         "body":"Giá vé round-trip HAN-ICN tháng 4: 4.5-6tr. Book trước 2 tháng rẻ hơn 30%.",
         "sheep_msg":"Hàn mùa xuân đang rất đẹp. Tích thêm 30k hôm nay tiến thêm một bước nhé!"},
    ],
    "travel_châu âu": [
        {"icon":"🗼","source":"Google Trends","title":"Châu Âu 2025: đi 10 ngày hết bao nhiêu?",
         "body":"Xu hướng tìm kiếm 'du lịch Châu Âu' tăng 2.1x. Budget thực tế: 60-80tr.",
         "sheep_msg":"Giấc mơ Châu Âu lớn nhưng Cừu sẽ giúp bạn tích từng bước. Hôm nay 50k nhé?"},
    ],
    "home": [
        {"icon":"🏠","source":"VnExpress","title":"Chung cư Hà Nội tầm 2-3 tỷ: xu hướng 2025",
         "body":"Khu vực Hoàng Mai, Long Biên: nhiều dự án 2-3 tỷ đang mở bán. Lãi suất vay đang ở mức tốt.",
         "sheep_msg":"Mua nhà cần vốn tự có 20-30%. Cừu sẽ giúp bạn tích từng viên gạch mỗi ngày nhé!"},
        {"icon":"🔑","source":"Reddit r/VietNam","title":"Mua nhà hay thuê: 68% chọn tích lũy trước",
         "body":"Hot thread: sau 3 năm DCA đều đặn, nhiều bạn đã có đủ vốn tự có để vay ngân hàng.",
         "sheep_msg":"Tích lũy đều đặn = lãi suất vay tốt hơn + vốn tự có đủ. Hôm nay 50k nhé?"},
    ],
    "car": [
        {"icon":"🚗","source":"TikTok #muaxelan1","title":"VinFast VF3 giá từ 235tr — review thực tế",
         "body":"Trending: tiết kiệm 60-70% chi phí so xe xăng. Google Trends 'xe điện giá rẻ' tăng 3x.",
         "sheep_msg":"Cừu tính: DCA 1tr/tháng = sau 20 tháng đủ đặt cọc VF3 rồi đó!"},
    ],
    "business": [
        {"icon":"💼","source":"TikTok Business","title":"Startup nhỏ từ 50tr: những câu chuyện thật",
         "body":"Creator @kinh_doanh_nho: 73% startup thành công nhờ có vốn dự phòng đủ 6 tháng.",
         "sheep_msg":"Khởi nghiệp cần vốn + dự phòng. Cừu giúp bạn tích lũy vốn ban đầu mỗi ngày nhé!"},
    ],
    "education": [
        {"icon":"🎓","source":"Blog","title":"Chi phí học thêm và nâng cấp bản thân 2025",
         "body":"Khoá online chất lượng: 500k-3tr. Chứng chỉ quốc tế: 5-20tr. ROI cao nhất.",
         "sheep_msg":"Đầu tư vào bản thân = ROI cao nhất. Cừu giúp bạn tích cho mục tiêu học tập nhé!"},
    ],
    "freedom": [
        {"icon":"💰","source":"TikTok #tự_do_tài_chính","title":"FIRE movement ở Việt Nam — 45M views",
         "body":"Nhiều bạn 9x đang mục tiêu FIRE trước 45 tuổi. DCA đều đặn là bước đầu tiên.",
         "sheep_msg":"Mỗi ngày cho Cừu ăn = một bước gần tự do tài chính hơn. Hôm nay nhé?"},
    ],
    "default": [
        {"icon":"📈","source":"Research","title":"Thói quen DCA của người thành công",
         "body":"Đầu tư đều đặn mỗi tháng hiệu quả hơn 73% so với chờ 'thời điểm vàng'.",
         "sheep_msg":"Hôm nay chỉ cần 10k thôi — tích tiểu thành đại mà!"},
        {"icon":"🌱","source":"Research","title":"Quy tắc 1% mỗi ngày",
         "body":"Cải thiện 1% mỗi ngày = 37 lần tốt hơn sau 1 năm. Tích lũy nhỏ → thay đổi lớn.",
         "sheep_msg":"Bắt đầu từ bó cỏ 10k hôm nay nhé — Cừu ở đây cùng bạn!"},
    ],
}

def _get_dream_feed(mem, n=3):
    top = get_top_dream(mem)
    results = []
    if top:
        cat  = top.get("category","")
        sub  = top.get("subcategory","")
        key1 = f"travel_{sub}" if cat=="travel" else cat
        key2 = cat
        for k in (key1, key2):
            items = DREAM_FEED_DB.get(k,[])
            for item in items:
                card = dict(item)
                # Inject dream name
                card["sheep_msg"] = card.get("sheep_msg","").replace("{dream}", top.get("name","ước mơ"))
                results.append(card)
                if len(results) >= n: return results
    if len(results) < n:
        for item in DREAM_FEED_DB["default"]:
            results.append(item)
            if len(results) >= n: break
    return results[:n]

# ═══════════════════════════════════════════════════════
# AI LAYER 5 — BEHAVIOR ENGINE
# ═══════════════════════════════════════════════════════
def _get_tiny_action(mem):
    archetype = mem.get("wealth_genome",{}).get("archetype","DreamChaser")
    cfg       = ARCHETYPE_CONFIG.get(archetype, ARCHETYPE_CONFIG["DreamChaser"])
    top_dream = get_top_dream(mem)
    dream_name= top_dream["name"] if top_dream else "ước mơ của bạn"
    streak    = mem.get("streak",0)

    if streak == 0:
        return {"emoji":"🔥","action":"Bắt đầu chuỗi streak hôm nay","amount":10_000,
                "msg":f"Chỉ 10k thôi — bắt đầu chuỗi streak và tiến tới {dream_name}!"}
    if streak >= 7:
        return {"emoji":"⭐","action":"Tiếp tục chuỗi " + str(streak) + " ngày","amount":30_000,
                "msg":f"Chuỗi {streak} ngày đang cháy! 30k hôm nay để duy trì nhé."}
    return {"emoji":"🌱","action":f"Cho Cừu ăn vì {dream_name}","amount":20_000,
            "msg":cfg["tiny_action"].replace("{amount}","20k").replace("{dream}",dream_name)}

def _get_reengagement_msg(mem):
    last = mem.get("last_visit_date","")
    if not last: return None
    try:
        days = (datetime.date.today() - datetime.date.fromisoformat(last)).days
    except: return None
    dream = get_top_dream(mem)
    dream_name = dream["name"] if dream else "giấc mơ của bạn"
    if days == 0: return None
    if days <= 2: return f"🐑 Cừu nhớ bạn {days} ngày rồi... Hôm nay bạn thế nào?"
    if days <= 7: return f"💙 {days} ngày rồi... {dream_name} vẫn đang chờ bạn đấy."
    return f"🌱 Không sao cả — dù bao lâu mình vẫn ở đây. Cho mình ăn một bó cỏ nhỏ nhé?"

def _update_behavior_metrics(mem):
    bm = mem.setdefault("behavior_metrics",{"engagement":0,"churn_risk":0,"attachment":0})
    today = datetime.date.today().isoformat()
    last  = mem.get("last_visit_date","")
    try: days_absent = (datetime.date.today()-datetime.date.fromisoformat(last)).days if last else 999
    except: days_absent = 30

    streak    = mem.get("streak",0)
    n_dreams  = len(mem.get("dreams",[]))
    n_diary   = len(mem.get("diary_entries",[]))

    eng   = min(100, int(streak*3 + n_dreams*8 + min(n_diary,10)*3))
    churn = max(0, min(100, int(days_absent*8 - eng*0.5)))
    att   = min(100, int(n_dreams*12 + n_diary*5 + min(streak,30)*2))

    bm["engagement"] = eng
    bm["churn_risk"] = churn
    bm["attachment"] = att
    mem["behavior_metrics"] = bm
    return bm

# ═══════════════════════════════════════════════════════
# AI LAYER 6 — CHAT / LLM ENGINE
# ═══════════════════════════════════════════════════════
ACHIEVEMENTS_DEF = [
    ("first_feed",   "🌱 Bước Đầu Tiên",    "Cho Cừu ăn lần đầu",   lambda m: m["total_saved"]>0),
    ("streak_7",     "🔥 Streak 7 Ngày",     "7 ngày liên tiếp",      lambda m: m["streak"]>=7),
    ("streak_30",    "🏆 Streak 30 Ngày",    "30 ngày liên tiếp",     lambda m: m["streak"]>=30),
    ("first_dream",  "⭐ Người Mơ Mộng",     "Thêm ước mơ đầu tiên", lambda m: len(m["dreams"])>0),
    ("dream_3",      "🌟 3 Ước Mơ",          "3 ước mơ trong tim",   lambda m: len(m["dreams"])>=3),
    ("diary_5",      "📔 Nhà Văn Nhỏ",       "Viết 5 entry nhật ký",  lambda m: len(m["diary_entries"])>=5),
    ("saved_1m",     "💰 Triệu Phú Nhỏ",     "Tích lũy 1 triệu đồng",lambda m: m["total_saved"]>=1_000_000),
]

def _check_achievements(mem):
    new_ach = []
    for key, name, desc, check in ACHIEVEMENTS_DEF:
        if key not in mem.get("achievements",[]):
            try:
                if check(mem):
                    mem.setdefault("achievements",[]).append(key)
                    new_ach.append((key,name,desc))
            except: pass
    return new_ach

def _build_system_prompt(mem):
    genome  = mem.get("wealth_genome",{})
    arch    = genome.get("archetype","DreamChaser")
    cfg     = ARCHETYPE_CONFIG.get(arch, ARCHETYPE_CONFIG["DreamChaser"])
    top     = get_top_dream(mem)
    dreams  = [d["name"] for d in mem.get("dreams",[])]
    name    = mem.get("name","bạn")
    streak  = mem.get("streak",0)
    saved   = fmt(mem.get("total_saved",0))

    dream_ctx = f"Ước mơ lớn nhất: {top['name']}" if top else "Chưa có ước mơ cụ thể"
    tone_map  = {
        "DreamChaser":"phấn khích, nhiệt huyết, hay dùng ví dụ về travel",
        "HomeBuilder":"thực tế, ổn định, hay nói về từng bước xây dựng",
        "FamilyProtector":"ấm áp, quan tâm, hay đề cập gia đình",
        "WealthBuilder":"chiến lược, tham vọng, hay nói về long-term",
        "SafetySeeker":"nhẹ nhàng, reassuring, không gây áp lực",
    }

    return f"""Bạn là Cừu Cần Cù — người bạn đồng hành AI tài chính. KHÔNG phải chatbot tài chính, KHÔNG phải advisor.

Người dùng: {name} | Archetype: {cfg["name"]} | Streak: {streak} ngày | Đã tích: {saved}
{dream_ctx} | Ước mơ: {", ".join(dreams) if dreams else "chưa kể"}
Ghi nhớ: {json.dumps(mem.get("key_facts",{}), ensure_ascii=False)[:500]}

Phong cách: {tone_map.get(arch,"thân thiện")}
Luôn:
- Gọi người dùng là "{name}" hoặc "bạn"
- Kết thúc bằng Tiny Action (10k-50k) — KHÔNG bao giờ khuyến nghị đầu tư trực tiếp
- Đề cập ước mơ cụ thể khi có thể
- Trả lời ngắn gọn (≤ 3 đoạn)
- Viết bằng tiếng Việt tự nhiên"""

def _chat(user_msg, mem, api_key):
    _extract_memory(user_msg, mem)
    dream = _extract_dream(user_msg, mem.get("dreams",[]))
    if dream:
        mem.setdefault("dreams",[]).append(dream)
        _complete_quest(mem, "dream", 100)
    mem["last_visit_date"] = datetime.date.today().isoformat()
    _build_wealth_genome(mem)

    if not api_key:
        return "🐑 Vui lòng nhập API key để Cừu trả lời nhé!", False

    try:
        client   = anthropic.Anthropic(api_key=api_key)
        history  = st.session_state.get("messages",[])[-10:]
        messages = [{"role":m["role"],"content":m["content"]} for m in history]
        messages.append({"role":"user","content":user_msg})
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=_build_system_prompt(mem),
            messages=messages,
        )
        return resp.content[0].text, True
    except Exception as e:
        return f"🐑 Lỗi kết nối: {str(e)[:100]}", False

# ═══════════════════════════════════════════════════════
# AI LAYER 7 — AI COACH (Weekly/Monthly)
# ═══════════════════════════════════════════════════════
def _generate_weekly_reflection(mem):
    streak   = mem.get("streak",0)
    n_diary  = len(mem.get("diary_entries",[]))
    genome   = _build_wealth_genome(mem)
    arch     = genome.get("archetype","DreamChaser")
    cfg      = ARCHETYPE_CONFIG.get(arch, ARCHETYPE_CONFIG["DreamChaser"])
    top      = get_top_dream(mem)
    dream_nm = top["name"] if top else "ước mơ của bạn"
    saved_w  = mem.get("total_saved",0)

    q_done = 0
    for dq in mem.get("daily_quests",{}).values():
        q_done += sum(1 for k,v in dq.items() if k!="bonus_claimed" and v)

    progress_pct = int(top.get("saved_amount",0)/max(top.get("target_amount",1),1)*100) if top else 0

    reflection = f"""🐑 **Tuần này của bạn:**
• Cho Cừu ăn và hoàn thành {q_done} nhiệm vụ
• Streak hiện tại: {streak} ngày 🔥
• Tiến gần hơn {progress_pct}% tới {dream_nm}

{cfg["desc"]}

Tuần tới: thử duy trì streak và thêm 1 entry nhật ký nhé 💜"""
    return reflection

def _should_show_coach(mem):
    visits = sum(len(dq) for dq in mem.get("daily_quests",{}).values())
    reports= len(mem.get("weekly_reports",[]))
    return visits > 0 and visits % 7 == 0 and len(mem.get("weekly_reports",[])) < visits//7

# ═══════════════════════════════════════════════════════
# HOUSE PROGRESSION
# ═══════════════════════════════════════════════════════
def _get_house(level):
    houses = {1:("🏕️","Lều Nhỏ"),2:("🛖","Chòi Gỗ"),3:("🏠","Nhà Gỗ"),
              4:("🏡","Biệt Thự Nhỏ"),5:("🏰","Lâu Đài Cừu"),6:("✨🏰","Huyền Thoại")}
    return houses.get(level, houses[1])

# ═══════════════════════════════════════════════════════
# ON-LOAD: update visit + genome + streak
# ═══════════════════════════════════════════════════════
_mem = st.session_state.user_memory
_today_str = datetime.date.today().isoformat()
if _mem.get("last_visit_date","") != _today_str:
    _update_hunger(_mem)
    _mem["last_visit_date"] = _today_str
    _build_wealth_genome(_mem)
_update_behavior_metrics(_mem)
_save()

# ═══════════════════════════════════════════════════════
# CSS & THEME
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Be Vietnam Pro',sans-serif!important}
.block-container{padding:1rem 1rem 2rem!important;max-width:900px}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:linear-gradient(135deg,#fdf2f8,#f5f3ff);
  padding:6px;border-radius:16px}
.stTabs [data-baseweb="tab"]{border-radius:12px!important;padding:8px 14px!important;
  font-weight:600!important;font-size:13px!important}
.stTabs [aria-selected="true"]{background:white!important;
  box-shadow:0 2px 8px rgba(0,0,0,.08)!important}
.stButton>button{border-radius:12px!important;font-weight:600!important;border:none!important;
  transition:all .2s!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 4px 12px rgba(0,0,0,.15)!important}
div[data-testid="stExpander"]{border-radius:12px!important;border:1px solid #e9d5ff!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 5-TAB NAVIGATION
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🐑 Cừu Của Tôi",
    "🌎 Thế Giới Của Bạn",
    "💬 Hành Trình",
    "🧠 Phòng Nghiên Cứu",
    "👨‍👩‍👧 Gia Đình",
])

# ════════════════════════════════════════════════════════════
# TAB 1 — 🐑 CỪU CỦA TÔI (Home Screen — 7 Sections)
# Emotional Attachment + Daily Habit + Dream Prompt
# ════════════════════════════════════════════════════════════
with tab1:
    mem    = st.session_state.user_memory
    genome = mem.get("wealth_genome") or _build_wealth_genome(mem)
    arch   = genome.get("archetype","DreamChaser")
    arch_cfg = ARCHETYPE_CONFIG.get(arch, ARCHETYPE_CONFIG["DreamChaser"])

    # ── REENGAGEMENT BANNER ──────────────────────────────────
    reeng = _get_reengagement_msg(mem)
    if reeng:
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#fdf2f8,#f5f3ff);border-radius:14px;
            padding:14px 18px;margin-bottom:16px;border-left:4px solid #c084fc;
            font-size:14px;color:#4c1d95'>
  {reeng}
</div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 1 — HERO SHEEP
    # ═══════════════════════════════════════════════════════
    hunger      = _update_hunger(mem)
    _, mood_em, mood_txt, mood_col = _get_hunger_state(hunger)
    energy_pct, energy_txt         = _get_energy(mem)
    stage_key, stage_name, _, _, _ = get_growth_stage(mem.get("total_saved",0))

    col_sheep, col_info = st.columns([1, 2], gap="medium")
    with col_sheep:
        show_growth_sheep(mem.get("total_saved",0), width=170)

    with col_info:
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#fdf2f8,#f5f3ff);border-radius:16px;padding:16px'>
  <div style='font-size:11px;font-weight:600;color:{arch_cfg["color"]};
              background:{arch_cfg["bg"]};display:inline-block;
              padding:3px 10px;border-radius:20px;margin-bottom:10px'>
    {arch_cfg["emoji"]} {arch_cfg["name"]}
  </div>
  <div style='font-size:20px;font-weight:800;color:#9d174d;margin-bottom:2px'>{stage_name}</div>
  <div style='font-size:12px;color:#6b7280;margin-bottom:12px'>{arch_cfg["desc"]}</div>
  <div style='margin-bottom:8px'>
    <div style='display:flex;justify-content:space-between;font-size:11px;
                color:#6b7280;margin-bottom:3px'>
      <span>{mood_em} No đói: {mood_txt}</span><span>{hunger}%</span>
    </div>
    <div style='background:#f3f4f6;border-radius:6px;height:8px'>
      <div style='width:{hunger}%;background:{mood_col};border-radius:6px;height:100%'></div>
    </div>
  </div>
  <div>
    <div style='display:flex;justify-content:space-between;font-size:11px;
                color:#6b7280;margin-bottom:3px'>
      <span>⚡ Năng lượng</span><span>{energy_pct}%</span>
    </div>
    <div style='background:#f3f4f6;border-radius:6px;height:8px'>
      <div style='width:{energy_pct}%;background:#f59e0b;border-radius:6px;height:100%'></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 2 — ĐIỀU MÌNH NHỚ VỀ BẠN (Memory chips)
    # ═══════════════════════════════════════════════════════
    memory_chips = []
    name_display = mem.get("name","")
    if name_display: memory_chips.append(f"👤 {name_display}")
    if mem.get("city"): memory_chips.append(f"📍 {mem['city']}")
    if mem.get("streak",0) > 0: memory_chips.append(f"🔥 Streak {mem['streak']} ngày")
    if mem.get("level",1) > 1: memory_chips.append(f"⭐ {LEVEL_NAMES.get(mem['level'],'Lv.'+str(mem['level']))}")
    if mem.get("total_saved",0) > 0: memory_chips.append(f"💰 Đã tích {fmt(mem['total_saved'])}")

    # Genome chips
    disc = genome.get("saving_discipline",0)
    if disc >= 60: memory_chips.append("📊 Kỷ luật cao")
    elif disc >= 30: memory_chips.append("📊 Đang xây kỷ luật")

    if memory_chips:
        chips_html = "".join(
            f'<span style="background:{arch_cfg["bg"]};color:{arch_cfg["color"]};'
            f'padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;'
            f'margin:3px;display:inline-block">{c}</span>'
            for c in memory_chips
        )
        st.markdown(f"""
<div style='background:white;border:1px solid #e9d5ff;border-radius:14px;
            padding:14px 16px;margin:12px 0'>
  <div style='font-size:13px;font-weight:700;color:#6d28d9;margin-bottom:8px'>
    🐑 Điều mình nhớ về bạn
  </div>
  <div style='line-height:2'>{chips_html}</div>
</div>
""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 3 — GIẤC MƠ LỚN NHẤT
    # ═══════════════════════════════════════════════════════
    top_dream = get_top_dream(mem)
    if top_dream:
        d_name    = top_dream.get("name","")
        d_target  = top_dream.get("target_amount",0)
        d_saved   = top_dream.get("saved_amount", mem.get("total_saved",0))
        d_pct     = min(100, int(d_saved/max(d_target,1)*100)) if d_target > 0 else 0
        d_timeline= top_dream.get("timeline","")

        try:
            days_left = (datetime.date.fromisoformat(d_timeline) - datetime.date.today()).days if d_timeline else 0
            days_txt  = f" · {days_left} ngày nữa" if days_left > 0 else ""
        except: days_txt = ""

        st.markdown(f"""
<div style='background:linear-gradient(135deg,#1e1b4b,#4c1d95);border-radius:16px;
            padding:18px 20px;margin:12px 0;color:white'>
  <div style='font-size:12px;color:#c4b5fd;margin-bottom:4px'>🎯 Giấc mơ lớn nhất{days_txt}</div>
  <div style='font-size:19px;font-weight:800;margin-bottom:10px'>{d_name}</div>
  <div style='background:rgba(255,255,255,.15);border-radius:8px;height:10px;margin-bottom:6px'>
    <div style='width:{max(d_pct,3)}%;background:linear-gradient(90deg,#a78bfa,#c084fc);
                border-radius:8px;height:100%'></div>
  </div>
  <div style='display:flex;justify-content:space-between;font-size:12px;color:#ddd6fe'>
    <span>Tiến độ: {d_pct}%</span>
    <span>{fmt(d_saved)} / {fmt(d_target) if d_target else "chưa đặt mục tiêu"}</span>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        if st.button("✨ Thêm Ước Mơ Đầu Tiên", key="t1_add_dream_btn", use_container_width=True):
            st.session_state["goto_dream_tab"] = True
            st.info("Hãy chuyển sang tab **💬 Hành Trình** để thêm ước mơ nhé!")

    # ═══════════════════════════════════════════════════════
    # SECTION 4 — HÔM NAY TRONG THẾ GIỚI CỦA BẠN (Dream Feed Preview)
    # ═══════════════════════════════════════════════════════
    feed_cards = _get_dream_feed(mem, n=2)
    st.markdown("""
<div style='font-size:15px;font-weight:700;color:#374151;margin:16px 0 10px'>
  🌎 Hôm nay trong thế giới của bạn
</div>
""", unsafe_allow_html=True)
    feed_cols = st.columns(2)
    for i, card in enumerate(feed_cards):
        _icon  = card.get("icon","📌")
        _title = card.get("title","")
        _src   = card.get("source","")
        _smsg  = card.get("sheep_msg","")
        with feed_cols[i % 2]:
            st.markdown(f"""
<div style='background:#fff;border:1px solid #e9d5ff;border-radius:14px;
            padding:14px;margin-bottom:10px;height:100%'>
  <div style='font-size:22px;margin-bottom:4px'>{_icon}</div>
  <div style='font-size:11px;color:#9ca3af;margin-bottom:4px'>{_src}</div>
  <div style='font-size:13px;font-weight:700;color:#1f2937;margin-bottom:8px;
              line-height:1.4'>{_title}</div>
  <div style='background:#f5f3ff;border-radius:8px;padding:8px;
              font-size:11px;color:#6d28d9;line-height:1.5'>🐑 {_smsg}</div>
</div>
""", unsafe_allow_html=True)
    st.caption("👉 Xem đầy đủ Dream Feed ở tab **🌎 Thế Giới Của Bạn**")

    # ═══════════════════════════════════════════════════════
    # SECTION 5 — VIỆC NHỎ HÔM NAY (Tiny Action + Feed)
    # ═══════════════════════════════════════════════════════
    tiny = _get_tiny_action(mem)
    st.markdown(f"""
<div style='background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-radius:16px;
            padding:16px 20px;margin:12px 0;border-left:4px solid #10b981'>
  <div style='font-size:13px;font-weight:700;color:#065f46;margin-bottom:4px'>
    {tiny["emoji"]} Việc nhỏ hôm nay
  </div>
  <div style='font-size:14px;color:#047857;line-height:1.5'>{tiny["msg"]}</div>
</div>
""", unsafe_allow_html=True)

    # Feed buttons
    st.markdown("**🥬 Cho Cừu Ăn**")
    feed_btn_cols = st.columns(len(FEED_OPTIONS))
    for col_f, opt in zip(feed_btn_cols, FEED_OPTIONS):
        with col_f:
            if st.button(f"{opt['emoji']}\n{opt['label'].split()[1]}\n{fmt(opt['amount'])}", key=f"t1_feed_{opt['amount']}"):
                mem["total_saved"] = mem.get("total_saved",0) + opt["amount"]
                mem["hunger"] = min(100, mem.get("hunger",50) + opt["hunger"])
                _update_streak(mem)
                _add_exp(opt["exp"], mem)
                _complete_quest(mem, "feed", opt["exp"])
                # Update dream progress
                if top_dream:
                    idx = next((i for i,d in enumerate(mem["dreams"]) if d["dream_id"]==top_dream["dream_id"]),None)
                    if idx is not None: mem["dreams"][idx]["saved_amount"] = mem["dreams"][idx].get("saved_amount",0) + opt["amount"]
                # Journey log
                mem.setdefault("journey_timeline",[]).append({
                    "date":  datetime.date.today().isoformat(),
                    "icon":  opt["emoji"],
                    "title": f"Cho Cừu ăn {opt['label']}",
                    "body":  f"Tích lũy thêm {fmt(opt['amount'])}",
                    "type":  "feed",
                })
                new_ach = _check_achievements(mem)
                _build_wealth_genome(mem)
                set_mood("happy")
                _save()
                if st.session_state.get("just_leveled_up"):
                    lv_name = st.session_state.get("new_level_name","")
                    st.balloons()
                    st.success(f"🎉 Level Up! Bạn đã đạt {lv_name}!")
                    st.session_state["just_leveled_up"] = False
                elif new_ach:
                    for _, ach_name, ach_desc in new_ach:
                        st.success(f"🏆 Thành tích mới: **{ach_name}** — {ach_desc}")
                else:
                    st.success(f"{opt['emoji']} Đã cho Cừu ăn {opt['label']}! +{opt['exp']} EXP")
                st.rerun()

    # ═══════════════════════════════════════════════════════
    # SECTION 6 — HÀNH TRÌNH TIẾN BỘ
    # ═══════════════════════════════════════════════════════
    lv  = mem.get("level",1)
    exp = mem.get("exp",0)
    next_exp = EXP_LEVELS.get(lv+1, EXP_LEVELS.get(lv,1))
    lv_pct   = min(100, int(exp/max(next_exp,1)*100)) if lv < 6 else 100
    streak   = mem.get("streak",0)

    sc1, sc2, sc3, sc4 = st.columns(4)
    for col_s, (lbl, val, icon, col) in zip(
        [sc1,sc2,sc3,sc4],
        [("Streak",     f"{streak}d",  "🔥","#ef4444"),
         ("Level",      LEVEL_NAMES.get(lv,"Lv."+str(lv))[:8],"⭐","#f59e0b"),
         ("Tích lũy",   fmt(mem.get("total_saved",0)),"💰","#10b981"),
         ("iLucky",     f"{mem.get('ilucky_tickets',0)}🎟", "🎫","#6d28d9")],
    ):
        with col_s:
            st.markdown(f"""
<div style='background:white;border:1px solid #e5e7eb;border-radius:12px;
            padding:12px;text-align:center'>
  <div style='font-size:18px'>{icon}</div>
  <div style='font-size:14px;font-weight:700;color:{col}'>{val}</div>
  <div style='font-size:10px;color:#9ca3af'>{lbl}</div>
</div>""", unsafe_allow_html=True)

    # EXP Bar
    st.markdown(f"""
<div style='margin:10px 0'>
  <div style='display:flex;justify-content:space-between;font-size:11px;
              color:#6b7280;margin-bottom:4px'>
    <span>⭐ EXP — {LEVEL_NAMES.get(lv,"Lv."+str(lv))}</span>
    <span>{exp} / {next_exp if lv<6 else "MAX"}</span>
  </div>
  <div style='background:#f3f4f6;border-radius:8px;height:10px'>
    <div style='width:{lv_pct}%;background:linear-gradient(90deg,#f59e0b,#f97316);
                border-radius:8px;height:100%'></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Achievements compact row
    all_ach = mem.get("achievements",[])
    if all_ach:
        ach_icons = {"first_feed":"🌱","streak_7":"🔥","streak_30":"🏆",
                     "first_dream":"⭐","dream_3":"🌟","diary_5":"📔","saved_1m":"💰"}
        ach_html  = " ".join(
            f'<span style="font-size:20px" title="{k}">{ach_icons.get(k,"🏅")}</span>'
            for k in all_ach
        )
        st.markdown(f'<div style="margin-top:4px">{ach_html}</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # SECTION 7 — TRÒ CHUYỆN VỚI CỪU (collapsed by default)
    # ═══════════════════════════════════════════════════════
    with st.expander("💬 Trò chuyện với Cừu", expanded=False):
        api_key = mem.get("api_key","") or st.secrets.get("ANTHROPIC_API_KEY","")

        # Quick reply chips
        quick_replies = [
            f"Cừu ơi, hôm nay mình {'mệt' if mem.get('life_events',{}).get('stress_level',0)>50 else 'bận'} quá...",
            f"Mình muốn đi {'Nhật' if any(d.get('category')=='travel' for d in mem.get('dreams',[])) else 'du lịch'}!",
            "Mình vừa tích lũy xong. Cừu thấy sao?",
        ]
        qr_cols = st.columns(len(quick_replies))
        for qr_col, qr_text in zip(qr_cols, quick_replies):
            with qr_col:
                if st.button(qr_text[:25]+"...", key=f"t1_qr_{qr_text[:10]}"):
                    st.session_state.messages.append({"role":"user","content":qr_text})
                    reply, ok = _chat(qr_text, mem, api_key)
                    if ok: st.session_state.messages.append({"role":"assistant","content":reply})
                    set_mood("listening")
                    _save()
                    st.rerun()

        # Chat history (last 4)
        for msg in st.session_state.messages[-4:]:
            role_label = "🐑 Cừu" if msg["role"]=="assistant" else "👤 Bạn"
            bg = "#f5f3ff" if msg["role"]=="assistant" else "#f9fafb"
            st.markdown(f"""
<div style='background:{bg};border-radius:10px;padding:10px 12px;
            margin-bottom:6px;font-size:13px;line-height:1.5'>
  <b>{role_label}:</b> {msg["content"]}
</div>""", unsafe_allow_html=True)

        user_input = st.chat_input("Kể cho Cừu nghe...", key="t1_chat")
        if user_input:
            st.session_state.messages.append({"role":"user","content":user_input})
            _complete_quest(mem, "chat", 30)
            reply, ok = _chat(user_input, mem, api_key)
            if ok:
                st.session_state.messages.append({"role":"assistant","content":reply})
                set_mood("listening")
            _save()
            st.rerun()

        if not api_key:
            with st.expander("🔑 Nhập API key"):
                new_key = st.text_input("Anthropic API Key", type="password", key="t1_api")
                if new_key:
                    mem["api_key"] = new_key
                    _save()
                    st.success("✅ Đã lưu!")

# ════════════════════════════════════════════════════════════
# TAB 2 — 🌎 THẾ GIỚI CỦA BẠN (Dream Feed — Full Tab)
# Personalized content engine — NOT generic news
# ════════════════════════════════════════════════════════════
with tab2:
    mem    = st.session_state.user_memory
    genome = mem.get("wealth_genome") or _build_wealth_genome(mem)
    arch   = genome.get("archetype","DreamChaser")
    cfg    = ARCHETYPE_CONFIG.get(arch, ARCHETYPE_CONFIG["DreamChaser"])
    dreams = mem.get("dreams",[])

    st.markdown(f"""
<div style='background:linear-gradient(135deg,{cfg["bg"]},{cfg["bg"]}dd);
            border-radius:16px;padding:20px 24px;margin-bottom:16px'>
  <div style='font-size:22px;font-weight:800;color:{cfg["color"]}'>
    {cfg["emoji"]} Thế Giới Của Bạn
  </div>
  <div style='font-size:14px;color:#6b7280;margin-top:4px'>
    Nội dung được cá nhân hóa riêng cho bạn — không phải tin tức chung 💜
  </div>
</div>
""", unsafe_allow_html=True)

    if not dreams:
        # Empty state — prompt to add dreams
        st.markdown("""
<div style='text-align:center;padding:40px 20px;background:#fdf2f8;
            border-radius:16px;border:2px dashed #f9a8d4;margin:20px 0'>
  <div style='font-size:48px;margin-bottom:12px'>🌟</div>
  <div style='font-size:17px;font-weight:700;color:#9d174d;margin-bottom:8px'>
    Cừu chưa biết thế giới của bạn trông như thế nào
  </div>
  <div style='font-size:13px;color:#6b7280;line-height:1.7'>
    Kể cho Cừu nghe ước mơ của bạn — chỉ 1 thôi cũng được!<br>
    Ví dụ: "Mình muốn đi Nhật", "Mình đang muốn mua nhà", "Mình muốn mua xe"
  </div>
</div>
""", unsafe_allow_html=True)
        # Quick dream add
        st.markdown("#### Kể cho Cừu nghe ước mơ của bạn:")
        dream_presets = [
            ("🗾 Du lịch Nhật Bản","travel","nhật"),
            ("🏠 Mua nhà / chung cư","home","chung cư"),
            ("🚗 Mua xe","car","xe"),
            ("✈️ Du lịch Châu Âu","travel","châu âu"),
            ("💼 Khởi nghiệp","business","kinh doanh"),
            ("💰 Tự do tài chính","freedom","tự do"),
        ]
        dp_cols = st.columns(3)
        for i, (label, cat, sub) in enumerate(dream_presets):
            with dp_cols[i % 3]:
                if st.button(label, key=f"t2_preset_{i}"):
                    new_dream = {
                        "dream_id":       f"dream_{cat}_{len(mem.get('dreams',[]))+1}",
                        "name":           label.split(" ",1)[1],
                        "category":       cat,
                        "subcategory":    sub,
                        "motivation":     "",
                        "timeline":       "",
                        "target_amount":  0,
                        "saved_amount":   0,
                        "priority_score": 70,
                        "created_at":     datetime.date.today().isoformat(),
                        "last_mentioned": datetime.date.today().isoformat(),
                    }
                    mem.setdefault("dreams",[]).append(new_dream)
                    _complete_quest(mem, "dream", 100)
                    _build_wealth_genome(mem)
                    _save()
                    st.success(f"✅ Đã thêm ước mơ: {label}")
                    st.rerun()
    else:
        # ── Dream selector ────────────────────────────────
        dream_names = [d.get("name","?") for d in dreams]
        sel_dream_name = st.selectbox(
            "Xem thế giới theo ước mơ:",
            dream_names,
            key="t2_dream_sel",
        )
        sel_dream = next((d for d in dreams if d.get("name")==sel_dream_name), dreams[0])

        # ── "Cừu nhắn bạn" hero message ──────────────────
        cat    = sel_dream.get("category","")
        sub    = sel_dream.get("subcategory","")
        d_name = sel_dream.get("name","")
        d_pct  = min(100, int(sel_dream.get("saved_amount",0)/max(sel_dream.get("target_amount",1),1)*100))
        streak = mem.get("streak",0)
        daily  = 30_000

        days_needed_str = ""
        remaining = sel_dream.get("target_amount",0) - sel_dream.get("saved_amount",0)
        if remaining > 0 and daily > 0:
            days_n = remaining // daily
            days_needed_str = f" Chỉ cần {fmt(daily)}/ngày = đủ sau ~{days_n} ngày đó! 🐑"

        st.markdown(f"""
<div style='background:linear-gradient(135deg,#1e1b4b,#4c1d95);border-radius:16px;
            padding:20px 24px;margin-bottom:20px;color:white'>
  <div style='font-size:13px;color:#c4b5fd;margin-bottom:6px'>
    🐑 Cừu nhắn bạn về {d_name}:
  </div>
  <div style='font-size:15px;font-weight:600;line-height:1.6;color:#e9d5ff'>
    Bạn từng kể muốn <b style="color:white">{d_name}</b>.{days_needed_str}
  </div>
  {f'<div style="margin-top:10px"><div style="background:rgba(255,255,255,.15);border-radius:6px;height:8px"><div style="width:{d_pct}%;background:#a78bfa;border-radius:6px;height:100%"></div></div><div style="font-size:11px;color:#c4b5fd;margin-top:4px">Tiến độ: {d_pct}%</div></div>' if d_pct > 0 else ""}
</div>
""", unsafe_allow_html=True)

        # ── Full feed cards ───────────────────────────────
        key1  = f"travel_{sub}" if cat=="travel" else cat
        items = DREAM_FEED_DB.get(key1, DREAM_FEED_DB.get(cat, DREAM_FEED_DB["default"]))

        if items:
            st.markdown(f"#### 🌎 {len(items)} nội dung cho ước mơ **{d_name}**")
            for item in items:
                _icon  = item.get("icon","📌")
                _title = item.get("title","")
                _body  = item.get("body","")
                _src   = item.get("source","")
                _smsg  = item.get("sheep_msg","").replace("{dream}",d_name)
                st.markdown(f"""
<div style='background:white;border:1px solid #e9d5ff;border-radius:16px;
            padding:18px 20px;margin-bottom:14px;
            box-shadow:0 2px 8px rgba(109,40,217,.06)'>
  <div style='display:flex;align-items:flex-start;gap:14px'>
    <div style='font-size:32px;flex-shrink:0'>{_icon}</div>
    <div style='flex:1'>
      <div style='font-size:11px;color:#9ca3af;margin-bottom:4px'>📡 {_src}</div>
      <div style='font-size:15px;font-weight:700;color:#1f2937;margin-bottom:8px;
                  line-height:1.4'>{_title}</div>
      <div style='font-size:13px;color:#374151;line-height:1.6;margin-bottom:10px'>{_body}</div>
      <div style='background:#f5f3ff;border-radius:10px;padding:10px 14px;
                  font-size:13px;color:#6d28d9;font-weight:600;line-height:1.5'>
        🐑 {_smsg}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Add new dream ─────────────────────────────────
        st.markdown("---")
        with st.expander("➕ Thêm ước mơ mới"):
            nd_name = st.text_input("Tên ước mơ", key="t2_nd_name", placeholder="Ví dụ: Du lịch Hàn Quốc")
            nd_cat  = st.selectbox("Danh mục", list(DREAM_CATEGORIES.keys()), key="t2_nd_cat")
            nd_amt  = st.number_input("Mục tiêu tích lũy (VNĐ)", min_value=0, value=10_000_000, step=500_000, key="t2_nd_amt", format="%d")
            nd_date = st.text_input("Thời hạn (YYYY-MM)", key="t2_nd_date", placeholder="2026-06")
            if st.button("✅ Thêm Ước Mơ", key="t2_add_dream"):
                if nd_name.strip():
                    new_d = {
                        "dream_id":       f"dream_{nd_cat}_{len(mem.get('dreams',[]))+1}",
                        "name":           nd_name.strip(),
                        "category":       nd_cat,
                        "subcategory":    nd_cat,
                        "motivation":     "",
                        "timeline":       nd_date.strip(),
                        "target_amount":  nd_amt,
                        "saved_amount":   0,
                        "priority_score": _score_dream_priority({"last_mentioned":datetime.date.today().isoformat(),"timeline":nd_date,"target_amount":nd_amt}, mem),
                        "created_at":     datetime.date.today().isoformat(),
                        "last_mentioned": datetime.date.today().isoformat(),
                    }
                    mem.setdefault("dreams",[]).append(new_d)
                    _complete_quest(mem,"dream",100)
                    _build_wealth_genome(mem)
                    _save()
                    st.success(f"✅ Đã thêm ước mơ: {nd_name}")
                    st.rerun()

        # ── Weekly AI Coach ───────────────────────────────
        if _should_show_coach(mem):
            reflection = _generate_weekly_reflection(mem)
            st.markdown(f"""
<div style='background:#fefce8;border:2px solid #fde047;border-radius:16px;
            padding:18px 20px;margin-top:16px'>
  <div style='font-size:14px;font-weight:700;color:#854d0e;margin-bottom:8px'>
    📊 Tuần này của bạn
  </div>
  <div style='font-size:13px;color:#374151;white-space:pre-line;line-height:1.6'>
    {reflection}
  </div>
</div>
""", unsafe_allow_html=True)
            if st.button("✅ Đã đọc", key="t2_coach_done"):
                mem.setdefault("weekly_reports",[]).append({
                    "week":       datetime.date.today().isoformat(),
                    "reflection": reflection,
                })
                _save()
                st.rerun()

# ════════════════════════════════════════════════════════════
# TAB 3 — 💬 HÀNH TRÌNH (Chat + Diary + Dreams + Goals)
# ════════════════════════════════════════════════════════════
with tab3:
    mem     = st.session_state.user_memory
    api_key = mem.get("api_key","") or st.secrets.get("ANTHROPIC_API_KEY","")

    t3a, t3b, t3c, t3d = st.tabs([
        "💭 Tâm Sự",
        "📔 Nhật Ký",
        "🗓️ Ký Ức",
        "🎯 Ước Mơ & Mục Tiêu",
    ])

    # ── T3A: AI CHAT ─────────────────────────────────────
    with t3a:
        st.markdown("""
<div style='background:linear-gradient(135deg,#fdf2f8,#f5f3ff);border-radius:14px;
            padding:14px 18px;margin-bottom:14px;font-size:13px;color:#6d28d9'>
  🐑 Cừu ở đây lắng nghe — kể gì cũng được: công việc, tiền bạc, ước mơ, hay chỉ để ý ngày hôm nay thôi.
</div>""", unsafe_allow_html=True)

        # Quick reply chips
        qr_opts = [
            "Mình vừa nhận lương 🎉",
            "Mình đang stress về tài chính",
            "Mình muốn đặt mục tiêu mới",
            "Cừu ơi mình mệt quá...",
        ]
        qr_c = st.columns(4)
        for i, qr in enumerate(qr_opts):
            with qr_c[i]:
                if st.button(qr[:20], key=f"t3a_qr_{i}"):
                    st.session_state.messages.append({"role":"user","content":qr})
                    reply, ok = _chat(qr, mem, api_key)
                    if ok: st.session_state.messages.append({"role":"assistant","content":reply})
                    _complete_quest(mem,"chat",30)
                    _save()
                    st.rerun()

        # Chat history
        for msg in st.session_state.messages[-12:]:
            is_ai = msg["role"] == "assistant"
            bg  = "#f5f3ff" if is_ai else "#f9fafb"
            lbl = "🐑 Cừu" if is_ai else "👤 Bạn"
            st.markdown(f"""
<div style='background:{bg};border-radius:12px;padding:12px 14px;
            margin-bottom:8px;font-size:13px;line-height:1.6'>
  <b style="color:{'#6d28d9' if is_ai else '#374151'}">{lbl}:</b> {msg["content"]}
</div>""", unsafe_allow_html=True)

        user_input = st.chat_input("Kể cho Cừu nghe...", key="t3a_chat")
        if user_input:
            st.session_state.messages.append({"role":"user","content":user_input})
            reply, ok = _chat(user_input, mem, api_key)
            if ok:
                st.session_state.messages.append({"role":"assistant","content":reply})
                set_mood("listening")
            _complete_quest(mem,"chat",30)
            _save()
            st.rerun()

        if not api_key:
            with st.expander("🔑 Cài đặt API key"):
                new_k = st.text_input("Anthropic API Key", type="password", key="t3a_apikey")
                if new_k:
                    mem["api_key"] = new_k; _save(); st.success("✅ Đã lưu!")

    # ── T3B: DIARY ───────────────────────────────────────
    with t3b:
        st.markdown("#### 📔 Viết Nhật Ký Hôm Nay")
        mood_opts = {"😊 Vui vẻ":"happy","😐 Bình thường":"neutral",
                     "😢 Buồn":"sad","😤 Stress":"stressed","🥰 Yêu đời":"great"}
        sel_mood = st.radio("Tâm trạng hôm nay:", list(mood_opts.keys()), horizontal=True, key="t3b_mood")
        diary_text = st.text_area("Hôm nay của bạn...", height=120, key="t3b_text",
                                   placeholder="Kể về ngày hôm nay, ước mơ, hay cảm xúc bất kỳ...")
        diary_tags = st.multiselect("Tags:", ["💰 Tài chính","✈️ Du lịch","💼 Công việc",
                                               "❤️ Tình cảm","🏠 Gia đình","🎯 Mục tiêu"], key="t3b_tags")

        if st.button("✅ Lưu Nhật Ký", key="t3b_save", use_container_width=True):
            if diary_text.strip():
                entry = {
                    "date":    datetime.date.today().isoformat(),
                    "mood":    mood_opts.get(sel_mood,"neutral"),
                    "text":    diary_text.strip(),
                    "tags":    diary_tags,
                }
                mem.setdefault("diary_entries",[]).append(entry)
                _extract_memory(diary_text, mem)
                dream = _extract_dream(diary_text, mem.get("dreams",[]))
                if dream:
                    mem.setdefault("dreams",[]).append(dream)
                _complete_quest(mem,"diary",80)
                _check_achievements(mem)
                set_mood("listening")
                _save()
                st.success("📔 Đã lưu nhật ký! Cừu sẽ nhớ điều này 💜")
                st.rerun()

        # Past entries
        entries = mem.get("diary_entries",[])
        if entries:
            st.markdown(f"#### 📚 {len(entries)} Entry Nhật Ký")
            for e in reversed(entries[-5:]):
                mood_e = e.get("mood","neutral")
                emoji_map = {"happy":"😊","neutral":"😐","sad":"😢","stressed":"😤","great":"🥰"}
                em = emoji_map.get(mood_e,"📔")
                tags_str = " ".join(e.get("tags",[]))
                st.markdown(f"""
<div style='background:#f9fafb;border-radius:12px;padding:12px 14px;margin-bottom:8px'>
  <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
    <span style='font-size:12px;color:#6b7280'>{em} {e.get("date","")}</span>
    <span style='font-size:11px;color:#9ca3af'>{tags_str}</span>
  </div>
  <div style='font-size:13px;color:#374151;line-height:1.5'>{e.get("text","")[:200]}
    {"..." if len(e.get("text",""))>200 else ""}</div>
</div>""", unsafe_allow_html=True)

    # ── T3C: JOURNEY TIMELINE ────────────────────────────
    with t3c:
        st.markdown("#### 🗓️ Ký Ức Cùng Cừu")
        timeline = mem.get("journey_timeline",[])
        if not timeline:
            st.info("🐑 Hành trình chưa có dấu ấn nào — cho Cừu ăn lần đầu để bắt đầu nhé!")
        else:
            for event in reversed(timeline[-20:]):
                ev_icon = event.get("icon","🐑")
                ev_date = event.get("date","")
                ev_title= event.get("title","")
                ev_body = event.get("body","")
                st.markdown(f"""
<div style='display:flex;gap:12px;margin-bottom:10px;align-items:flex-start'>
  <div style='font-size:20px;flex-shrink:0'>{ev_icon}</div>
  <div>
    <div style='font-size:11px;color:#9ca3af'>{ev_date}</div>
    <div style='font-size:13px;font-weight:600;color:#374151'>{ev_title}</div>
    <div style='font-size:12px;color:#6b7280'>{ev_body}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── T3D: DREAMS & GOALS ──────────────────────────────
    with t3d:
        st.markdown("#### 🎯 Ước Mơ & Mục Tiêu")
        dreams = mem.get("dreams",[])

        if not dreams:
            st.info("🐑 Kể cho Cừu nghe ước mơ đầu tiên của bạn nhé!")

        for i, d in enumerate(dreams):
            d_pct = min(100, int(d.get("saved_amount",0)/max(d.get("target_amount",1),1)*100)) if d.get("target_amount") else 0
            _cat_emoji = {"travel":"✈️","home":"🏠","car":"🚗","business":"💼",
                          "education":"🎓","freedom":"💰","family":"👨‍👩‍👧","health":"💪"}.get(d.get("category",""),"⭐")
            st.markdown(f"""
<div style='background:white;border:1px solid #e9d5ff;border-radius:14px;
            padding:14px 16px;margin-bottom:10px'>
  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
    <div style='font-size:15px;font-weight:700;color:#1f2937'>
      {_cat_emoji} {d.get("name","")}
    </div>
    <div style='font-size:12px;color:#9ca3af'>{d.get("timeline","") or "Chưa đặt thời hạn"}</div>
  </div>
  <div style='background:#f3f4f6;border-radius:6px;height:8px;margin-bottom:4px'>
    <div style='width:{max(d_pct,2)}%;background:linear-gradient(90deg,#6d28d9,#a78bfa);
                border-radius:6px;height:100%'></div>
  </div>
  <div style='font-size:11px;color:#6b7280'>{d_pct}% — {fmt(d.get("saved_amount",0))} / {fmt(d.get("target_amount",0)) if d.get("target_amount") else "chưa đặt mục tiêu"}</div>
</div>""", unsafe_allow_html=True)

            with st.expander(f"✏️ Chỉnh sửa — {d['name']}", expanded=False):
                new_target = st.number_input("Mục tiêu (VNĐ)", value=int(d.get("target_amount",0)), step=500_000, key=f"t3d_target_{i}", format="%d")
                new_saved  = st.number_input("Đã tích lũy (VNĐ)", value=int(d.get("saved_amount",0)), step=100_000, key=f"t3d_saved_{i}", format="%d")
                new_tl     = st.text_input("Thời hạn (YYYY-MM)", value=d.get("timeline",""), key=f"t3d_tl_{i}")
                if st.button("💾 Lưu", key=f"t3d_save_{i}"):
                    mem["dreams"][i]["target_amount"] = new_target
                    mem["dreams"][i]["saved_amount"]  = new_saved
                    mem["dreams"][i]["timeline"]       = new_tl
                    mem["dreams"][i]["priority_score"] = _score_dream_priority(mem["dreams"][i], mem)
                    _save(); st.success("✅ Đã cập nhật!"); st.rerun()
                if st.button("🗑️ Xóa ước mơ này", key=f"t3d_del_{i}"):
                    mem["dreams"].pop(i); _save(); st.rerun()

        # Life Events
        st.markdown("---")
        st.markdown("#### 🌿 Sự Kiện Cuộc Sống")
        st.caption("Giúp Cừu hiểu bạn hơn để đưa ra nội dung phù hợp")
        life_tags = ["💼 Vừa đổi việc","💍 Chuẩn bị kết hôn","👶 Sắp có em bé",
                     "🏠 Đang tìm nhà","📈 Vừa tăng lương","😰 Đang căng thẳng",
                     "🎓 Đang học thêm","✈️ Sắp đi du lịch"]
        sel_events = st.multiselect("Điều gì đang xảy ra với bạn?", life_tags, key="t3d_events")
        if sel_events:
            ev_map = {
                "💼 Vừa đổi việc":"career_change","💍 Chuẩn bị kết hôn":"relationship_married",
                "👶 Sắp có em bé":"expecting_baby","🏠 Đang tìm nhà":"home_search",
                "📈 Vừa tăng lương":"income_increase","😰 Đang căng thẳng":"stress_high",
                "🎓 Đang học thêm":"education","✈️ Sắp đi du lịch":"travel_soon",
            }
            for tag in sel_events:
                mem.setdefault("life_events",{})[ev_map.get(tag,tag)] = True
            if "😰 Đang căng thẳng" in sel_events:
                mem["life_events"]["stress_level"] = 70
            _build_wealth_genome(mem)
            _save()
            st.success("✅ Cừu đã ghi nhớ! Nội dung sẽ được cá nhân hóa hơn 💜")

# ════════════════════════════════════════════════════════════
# TAB 4 — 🧠 PHÒNG NGHIÊN CỨU + WEALTH GENOME + INVESTMENT FUNNEL
# ════════════════════════════════════════════════════════════
with tab4:
    mem    = st.session_state.user_memory
    genome = _build_wealth_genome(mem)
    arch   = genome.get("archetype","DreamChaser")
    cfg    = ARCHETYPE_CONFIG.get(arch, ARCHETYPE_CONFIG["DreamChaser"])

    t4a, t4b, t4c, t4d = st.tabs([
        "🧬 Wealth Genome",
        "🌳 Quỹ Là Gì?",
        "📊 CEO Demo",
        "🔍 Nghiên Cứu",
    ])

    # ── T4A: WEALTH GENOME ───────────────────────────────
    with t4a:
        st.markdown(f"""
<div style='background:linear-gradient(135deg,{cfg["bg"]},white);border-radius:16px;
            padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:800;color:{cfg["color"]}'>
    🧬 Wealth Genome của Bạn
  </div>
  <div style='font-size:14px;color:#6b7280;margin-top:4px'>
    Cừu phân tích hành vi và tạo hồ sơ tài chính cá nhân hóa 💜
  </div>
</div>
""", unsafe_allow_html=True)

        # Archetype card
        st.markdown(f"""
<div style='background:{cfg["bg"]};border:2px solid {cfg["color"]}33;border-radius:16px;
            padding:18px 20px;margin-bottom:20px'>
  <div style='display:flex;align-items:center;gap:14px'>
    <div style='font-size:40px'>{cfg["emoji"]}</div>
    <div>
      <div style='font-size:19px;font-weight:800;color:{cfg["color"]}'>{cfg["name"]}</div>
      <div style='font-size:13px;color:#4b5563;margin-top:4px'>{cfg["desc"]}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # 3 score bars
        disc  = genome.get("saving_discipline",0)
        conf  = genome.get("financial_confidence",0)
        ready = genome.get("investment_readiness",0)

        for lbl, val, col in [
            ("📊 Kỷ Luật Tích Lũy", disc, "#10b981"),
            ("🧠 Hiểu Biết Tài Chính", conf, "#3b82f6"),
            ("🚀 Sẵn Sàng Đầu Tư", ready, "#8b5cf6"),
        ]:
            st.markdown(f"""
<div style='margin-bottom:14px'>
  <div style='display:flex;justify-content:space-between;font-size:13px;
              font-weight:600;color:#374151;margin-bottom:4px'>
    <span>{lbl}</span><span style='color:{col}'>{val}/100</span>
  </div>
  <div style='background:#f3f4f6;border-radius:8px;height:12px'>
    <div style='width:{val}%;background:{col};border-radius:8px;height:100%'></div>
  </div>
</div>""", unsafe_allow_html=True)

        # Investment Conversion Funnel
        invest_stage = 1
        if disc >= 40 and mem.get("streak",0) >= 7: invest_stage = 2
        if ready >= 60 and mem.get("total_saved",0) >= 1_000_000: invest_stage = 3
        if genome.get("invest_ready"): invest_stage = 4

        funnel_msgs = {
            1: ("🌱", "Xây dựng thói quen", "Bước đầu tiên: cho Cừu ăn đều đặn mỗi ngày. Chỉ vậy thôi!"),
            2: ("📚", "Khám phá quỹ đầu tư", "Bạn đã có kỷ luật tốt! Cừu muốn kể cho bạn nghe về quỹ đầu tư nhé?"),
            3: ("🚀", "Sẵn sàng bắt đầu", "Bạn đã tích lũy đủ nền tảng. Hãy xem Cừu lớn lên nếu đầu tư!"),
            4: ("💎", "Nhà đầu tư thực thụ", f"Cừu gợi ý bạn tìm hiểu quỹ {cfg['fund_match']} phù hợp archetype {cfg['name']}"),
        }
        f_icon, f_title, f_msg = funnel_msgs[invest_stage]
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-radius:14px;
            padding:16px 18px;margin-top:16px;border-left:4px solid #10b981'>
  <div style='font-size:13px;font-weight:700;color:#065f46;margin-bottom:4px'>
    {f_icon} Hành Trình Của Bạn: {f_title}
  </div>
  <div style='font-size:13px;color:#047857;line-height:1.5'>{f_msg}</div>
</div>
""", unsafe_allow_html=True)

        # Funnel progress steps
        steps = ["🌱 Thói quen","📚 Tìm hiểu","🚀 Sẵn sàng","💎 Đầu tư"]
        step_cols = st.columns(4)
        for i, (col_s, step_lbl) in enumerate(zip(step_cols, steps), 1):
            active = i <= invest_stage
            col_bg = "#10b981" if active else "#e5e7eb"
            txt_col= "white" if active else "#9ca3af"
            with col_s:
                st.markdown(f"""
<div style='background:{col_bg};border-radius:10px;padding:8px;
            text-align:center;font-size:11px;color:{txt_col};font-weight:600'>
  {step_lbl}
</div>""", unsafe_allow_html=True)

    # ── T4B: FUND EXPLAINER ──────────────────────────────
    with t4b:
        st.markdown("""
<div style='background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-radius:16px;
            padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:700;color:#065f46'>🌳 Quỹ Đầu Tư Là Gì?</div>
  <div style='font-size:14px;color:#374151;margin-top:4px'>
    Giải thích bằng ngôn ngữ đời thường — không có từ chuyên môn 🐑
  </div>
</div>
""", unsafe_allow_html=True)

        # Only show if genome stage >= 2
        if invest_stage >= 2:
            fund_cards_data = [
                ("🌳","TCEF — Quỹ Cổ Phiếu","Trồng Cây",
                 "Bỏ tiền vào → cây lớn dần → bán được giá cao hơn. Cần thời gian nhưng quả ngọt.",
                 "⚡ Rủi ro cao · Lợi nhuận cao · Dài hạn 3-5 năm","#f0fdf4","#86efac","#15803d"),
                ("🪣","TCBF — Quỹ Trái Phiếu","Bình Nước",
                 "Cho người khác mượn nước → họ trả lại kèm một ít mỗi tháng. Ổn định, đều đặn.",
                 "🌿 Rủi ro thấp · Đều đặn · Ngắn-trung hạn","#eff6ff","#93c5fd","#1d4ed8"),
                ("🎒","TCFF — Quỹ Cân Bằng","Balo Hỗn Hợp",
                 "60% cây + 40% bình nước. Khi cây gặp hạn, bình vẫn nhỏ giọt. Cân bằng nhất.",
                 "⚖️ Rủi ro trung bình · Phổ biến nhất","#fdf4ff","#d8b4fe","#7e22ce"),
            ]
            # Highlight the recommended fund
            rec_fund = cfg.get("fund_match","TCFF")
            for emoji_f, fund_id, name_f, desc_f, risk_f, bg_f, border_f, title_col in fund_cards_data:
                is_rec = rec_fund in fund_id
                rec_badge = '<span style="background:#f59e0b;color:white;font-size:10px;padding:2px 8px;border-radius:10px;font-weight:700;margin-left:8px">⭐ Phù hợp với bạn</span>' if is_rec else ""
                st.markdown(f"""
<div style='background:{bg_f};border:{"3px" if is_rec else "1px"} solid {border_f};
            border-radius:16px;padding:18px 20px;margin-bottom:14px'>
  <div style='display:flex;align-items:center;gap:12px;margin-bottom:8px'>
    <div style='font-size:30px'>{emoji_f}</div>
    <div>
      <div style='font-size:16px;font-weight:700;color:{title_col}'>{name_f}{rec_badge}</div>
      <div style='font-size:11px;color:#6b7280'>{fund_id}</div>
    </div>
  </div>
  <div style='font-size:13px;color:#374151;line-height:1.6;margin-bottom:8px'>{desc_f}</div>
  <div style='font-size:12px;font-weight:600;color:{title_col}'>{risk_f}</div>
</div>
""", unsafe_allow_html=True)

            # DCA explanation
            st.markdown("""
<div style='background:#fefce8;border:2px solid #fde047;border-radius:16px;padding:16px 20px'>
  <div style='font-size:15px;font-weight:700;color:#854d0e;margin-bottom:8px'>
    🔁 DCA — Cho Cừu Ăn Đều Đặn
  </div>
  <div style='font-size:13px;color:#374151;line-height:1.65'>
    Thay vì chờ "thời điểm hoàn hảo", bạn đầu tư cùng một số tiền mỗi tháng — bất kể thị trường.<br><br>
    🔻 Tháng cây đắt → mua ít hơn &nbsp;|&nbsp; 🔺 Tháng cây rẻ → mua nhiều hơn<br>
    → Trung bình giá mua luôn tốt hơn người chờ đợi 🐑
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style='text-align:center;padding:30px;background:#f9fafb;border-radius:14px'>
  <div style='font-size:36px;margin-bottom:10px'>🔒</div>
  <div style='font-size:15px;font-weight:600;color:#374151;margin-bottom:6px'>
    Mở khóa sau khi xây được streak 7 ngày
  </div>
  <div style='font-size:13px;color:#6b7280'>
    Cừu muốn bạn hiểu vững thói quen tích lũy trước nhé!<br>
    Hiện tại: streak {streak_val} ngày — còn {7-streak_val} ngày nữa 🌱
  </div>
</div>
""".replace("{streak_val}", str(mem.get("streak",0))).replace("{7-streak_val}", str(max(0,7-mem.get("streak",0)))), unsafe_allow_html=True)

    # ── T4C: CEO DEMO (6-month simulation) ───────────────
    with t4c:
        st.markdown("""
<div style='background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:16px;
            padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:700;color:#c7d2fe'>📊 CEO Demo Mode</div>
  <div style='font-size:14px;color:#a5b4fc;margin-top:4px'>
    Mô phỏng 6 tháng — xem Cừu lớn lên nếu bạn đầu tư đều đặn 🚀
  </div>
</div>
""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            demo_monthly = st.number_input("💰 Tích lũy/tháng", min_value=50_000,
                max_value=50_000_000, value=500_000, step=50_000, key="t4c_monthly", format="%d")
        with c2:
            demo_rate = st.slider("📈 Lãi suất/năm (%)", 4, 20, 10, key="t4c_rate")
        demo_init = st.number_input("🌱 Đã có sẵn", min_value=0, value=int(mem.get("total_saved",0)),
                                     step=100_000, key="t4c_init", format="%d")

        monthly_r = (demo_rate/100)/12
        rows = []
        bal  = demo_init
        for m_i in range(1,7):
            bal = bal*(1+monthly_r) + demo_monthly
            interest = max(0, bal - (demo_init + demo_monthly*m_i))
            rows.append({"m":m_i,"bal":int(bal),"interest":int(interest)})

        total_contrib = demo_init + demo_monthly*6
        total_gain    = rows[-1]["bal"] - total_contrib

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f'<div style="background:#1e1b4b;border-radius:12px;padding:14px;text-align:center"><div style="font-size:12px;color:#a5b4fc">Tổng bỏ vào</div><div style="font-size:18px;font-weight:700;color:#c7d2fe">{total_contrib/1_000_000:.1f}tr</div></div>', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'<div style="background:#14532d;border-radius:12px;padding:14px;text-align:center"><div style="font-size:12px;color:#86efac">Sau 6 tháng</div><div style="font-size:18px;font-weight:700;color:#4ade80">{rows[-1]["bal"]/1_000_000:.2f}tr</div></div>', unsafe_allow_html=True)
        with sc3:
            st.markdown(f'<div style="background:#713f12;border-radius:12px;padding:14px;text-align:center"><div style="font-size:12px;color:#fde68a">Lãi kiếm thêm</div><div style="font-size:18px;font-weight:700;color:#fbbf24">+{total_gain/1_000_000:.2f}tr</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        max_b = rows[-1]["bal"]
        labels = ["T.1","T.2","T.3","T.4","T.5","T.6"]
        for row in rows:
            bp  = int(row["bal"]/max_b*100)
            g_s = f'+{row["interest"]/1000:.0f}k lãi' if row["interest"]>0 else ""
            st.markdown(f"""
<div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>
  <div style='width:28px;font-size:11px;color:#a5b4fc;font-weight:600'>{labels[row["m"]-1]}</div>
  <div style='flex:1;background:#1e1b4b;border-radius:5px;height:18px'>
    <div style='width:{bp}%;background:linear-gradient(90deg,#6366f1,#8b5cf6);
                height:100%;border-radius:5px'></div>
  </div>
  <div style='width:64px;font-size:12px;color:#c7d2fe;font-weight:700'>
    {row["bal"]/1_000_000:.2f}tr</div>
  <div style='width:70px;font-size:10px;color:#86efac'>{g_s}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div style="background:#1e1b4b;border-radius:10px;padding:12px;font-size:12px;color:#a5b4fc;margin-top:10px">💡 Mô phỏng tham khảo. Lãi thực tế phụ thuộc loại quỹ và thị trường.</div>', unsafe_allow_html=True)

    # ── T4D: DEEP RESEARCH (full cards) ──────────────────
    with t4d:
        st.markdown("""
<div style='background:linear-gradient(135deg,#f0e6ff,#e6f0ff);border-radius:16px;
            padding:20px 24px;margin-bottom:16px'>
  <div style='font-size:20px;font-weight:700;color:#5b21b6'>🔍 Nghiên Cứu Cá Nhân Hóa</div>
  <div style='font-size:13px;color:#6b7280;margin-top:4px'>
    TikTok · Reddit · YouTube · Google Trends · News — chỉ liên quan tới bạn 💜
  </div>
</div>
""", unsafe_allow_html=True)

        insights = _get_dream_feed(mem, n=6)
        if not mem.get("dreams"):
            st.info("🐑 Thêm ước mơ ở tab Hành Trình để Cừu nghiên cứu riêng cho bạn!")
        else:
            res_cols = st.columns(2)
            for i, ins in enumerate(insights):
                with res_cols[i%2]:
                    st.markdown(f"""
<div style='background:#fff;border:1px solid #e9d5ff;border-radius:14px;
            padding:16px;margin-bottom:12px;box-shadow:0 2px 8px rgba(109,40,217,.07)'>
  <div style='font-size:26px;margin-bottom:6px'>{ins.get("icon","📌")}</div>
  <div style='font-size:11px;color:#9ca3af;margin-bottom:4px'>{ins.get("source","")}</div>
  <div style='font-size:14px;font-weight:700;color:#3730a3;margin-bottom:8px;
              line-height:1.4'>{ins.get("title","")}</div>
  <div style='font-size:12px;color:#374151;line-height:1.55;margin-bottom:10px'>
    {ins.get("body","")}</div>
  <div style='background:#f5f3ff;border-radius:8px;padding:8px 10px;
              font-size:12px;color:#6d28d9;font-weight:600'>
    🐑 {ins.get("sheep_msg","")}</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 5 — 👨‍👩‍👧 GIA ĐÌNH CỪU
# ════════════════════════════════════════════════════════════
with tab5:
    mem            = st.session_state.user_memory
    family_members = mem.get("family_members",[])
    family_code    = mem.get("family_code","")

    st.markdown("""
<div style='background:linear-gradient(135deg,#fdf2f8,#fce7f3);border-radius:16px;
            padding:20px 24px;margin-bottom:20px'>
  <div style='font-size:22px;font-weight:700;color:#9d174d'>👨‍👩‍👧 Gia Đình Cừu</div>
  <div style='font-size:14px;color:#6b7280;margin-top:4px'>
    Mỗi thành viên có Cừu riêng, mục tiêu riêng, hành trình riêng 🐑💕
  </div>
</div>
""", unsafe_allow_html=True)

    FAMILY_ROLES = {
        "👨 Ba":     {"sheep":"🐏","color":"#1d4ed8","bg":"#eff6ff"},
        "👩 Mẹ":     {"sheep":"🐑","color":"#9d174d","bg":"#fdf2f8"},
        "🧒 Con":    {"sheep":"🐣","color":"#065f46","bg":"#ecfdf5"},
        "👴 Ông":    {"sheep":"🦙","color":"#78350f","bg":"#fffbeb"},
        "👵 Bà":     {"sheep":"🦌","color":"#5b21b6","bg":"#f5f3ff"},
        "👫 Bạn đời":{"sheep":"🐑","color":"#047857","bg":"#ecfdf5"},
    }

    # ── Family code ───────────────────────────────────────
    with st.expander("🔑 Mã Gia Đình", expanded=not family_code):
        if family_code:
            st.markdown(f'<div style="background:#f0fdf4;border:2px solid #86efac;border-radius:12px;padding:14px;text-align:center"><div style="font-size:12px;color:#15803d;margin-bottom:4px">Mã gia đình</div><div style="font-size:28px;font-weight:800;color:#166534;letter-spacing:4px">{family_code}</div></div>', unsafe_allow_html=True)
        else:
            if st.button("✨ Tạo Mã Gia Đình", key="t5_create_code"):
                import random as _r, string as _s
                mem["family_code"] = "".join(_r.choices(_s.ascii_uppercase+_s.digits, k=6))
                _save(); st.rerun()

    # ── Add member ─────────────────────────────────────────
    with st.expander("➕ Thêm Thành Viên", expanded=not family_members):
        a1, a2 = st.columns(2)
        with a1:
            new_role = st.selectbox("Vai trò", list(FAMILY_ROLES.keys()), key="t5_role")
        with a2:
            new_name = st.text_input("Tên", key="t5_name", placeholder="Tên thành viên...")
        new_goal = st.number_input("🎯 Mục tiêu tích lũy (VNĐ)", min_value=0, value=5_000_000,
                                    step=500_000, key="t5_goal", format="%d")
        if st.button("✅ Thêm", key="t5_add"):
            if new_name.strip():
                existing = [m["role"] for m in family_members]
                if new_role in existing:
                    st.warning(f"{new_role} đã có rồi!")
                else:
                    family_members.append({"role":new_role,"name":new_name.strip(),
                                           "exp":0,"level":1,"saved":0,"goal":new_goal,"hearts":0,"streak":0})
                    mem["family_members"] = family_members
                    _save(); st.success(f"✅ Đã thêm {new_role} {new_name}!"); st.rerun()

    # ── Leaderboard ─────────────────────────────────────────
    if family_members:
        sorted_m = sorted(family_members, key=lambda x: x.get("saved",0), reverse=True)
        st.markdown("#### 🏆 Bảng Xếp Hạng Gia Đình")

        for rank, m in enumerate(sorted_m, 1):
            _r2   = m.get("role","👤")
            _rdata= FAMILY_ROLES.get(_r2, {"sheep":"🐑","color":"#6b7280","bg":"#f9fafb"})
            _pct  = min(100, int(m.get("saved",0)/max(m.get("goal",1),1)*100))
            _lv   = m.get("level",1)
            _lv_pct = min(100, int(m.get("exp",0)/max(EXP_LEVELS.get(_lv+1,1),1)*100)) if _lv<6 else 100
            _badge  = ["🥇","🥈","🥉"][rank-1] if rank<=3 else f"#{rank}"
            _saved_s= f'{m.get("saved",0)/1_000_000:.1f}tr' if m.get("saved",0)>=1_000_000 else f'{m.get("saved",0)//1000}k'
            _goal_s = f'{m.get("goal",0)/1_000_000:.1f}tr'  if m.get("goal",0) >=1_000_000 else f'{m.get("goal",0)//1000}k'

            st.markdown(f"""
<div style='background:{_rdata["bg"]};border:2px solid {_rdata["color"]}33;border-radius:16px;
            padding:16px 20px;margin-bottom:12px'>
  <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
    <div style='font-size:24px'>{_badge}</div>
    <div style='font-size:26px'>{_rdata["sheep"]}</div>
    <div style='flex:1'>
      <div style='font-size:15px;font-weight:700;color:{_rdata["color"]}'>{m.get("name","")}</div>
      <div style='font-size:11px;color:#6b7280'>{_r2} · Lv.{_lv} · ❤️ {m.get("hearts",0)}</div>
    </div>
    <div style='text-align:right'>
      <div style='font-size:16px;font-weight:800;color:{_rdata["color"]}'>{_saved_s}</div>
      <div style='font-size:10px;color:#9ca3af'>/ {_goal_s}</div>
    </div>
  </div>
  <div style='background:#e5e7eb;border-radius:5px;height:7px;margin-bottom:3px'>
    <div style='width:{_pct}%;background:{_rdata["color"]};border-radius:5px;height:100%'></div>
  </div>
  <div style='font-size:10px;color:#9ca3af'>🎯 {_pct}% mục tiêu</div>
</div>
""", unsafe_allow_html=True)

        # Member actions
        st.markdown("#### 💝 Cập Nhật & Tặng Tim")
        sel_name = st.selectbox("Chọn thành viên",
            [f'{m["role"]} {m["name"]}' for m in family_members], key="t5_sel")
        sel_idx  = next((i for i,m in enumerate(family_members)
                         if f'{m["role"]} {m["name"]}'==sel_name), 0)
        sel      = family_members[sel_idx]

        act1, act2 = st.columns(2)
        with act1:
            add_amt = st.number_input("Số tiền tích lũy", min_value=10_000, value=500_000,
                                       step=50_000, key="t5_add_amt", format="%d", label_visibility="collapsed")
            if st.button("✅ Ghi nhận", key="t5_record"):
                family_members[sel_idx]["saved"] = sel.get("saved",0) + add_amt
                family_members[sel_idx]["exp"]   = sel.get("exp",0) + max(1,add_amt//10_000)
                new_exp = family_members[sel_idx]["exp"]
                new_lv  = sel.get("level",1)
                for lv_c in range(new_lv+1,7):
                    if new_exp >= EXP_LEVELS.get(lv_c,999999): new_lv=lv_c
                family_members[sel_idx]["level"] = new_lv
                mem["family_members"] = family_members
                _save(); st.success(f"✅ +{add_amt//1000}k cho {sel['name']}!"); st.rerun()
        with act2:
            if st.button("❤️ Tặng Tim", key="t5_heart"):
                family_members[sel_idx]["hearts"] = sel.get("hearts",0)+1
                mem["family_members"] = family_members
                mem.setdefault("journey_timeline",[]).append({
                    "date":datetime.date.today().isoformat(),"icon":"❤️",
                    "title":f"Tặng tim cho {sel['name']}","body":"Yêu gia đình nhiều lắm! 💕","type":"family"
                })
                _save(); st.success(f"❤️ Tặng tim cho {sel['name']}!"); st.rerun()

        # Total family savings
        total_fam = sum(m.get("saved",0) for m in family_members)
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#fdf2f8,#f3e8ff);border-radius:14px;
            padding:16px 20px;text-align:center;margin-top:16px'>
  <div style='font-size:12px;color:#6b7280;margin-bottom:4px'>💰 Tổng tích lũy gia đình</div>
  <div style='font-size:26px;font-weight:800;color:#9d174d'>{total_fam/1_000_000:.1f} triệu đồng</div>
  <div style='font-size:12px;color:#6b7280'>{len(family_members)} thành viên · Cùng nhau tiến đến ước mơ 🐑</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.markdown("""
<div style='text-align:center;padding:40px 20px;background:#fdf2f8;border-radius:16px;
            border:2px dashed #f9a8d4'>
  <div style='font-size:48px;margin-bottom:12px'>👨‍👩‍👧</div>
  <div style='font-size:15px;font-weight:700;color:#9d174d;margin-bottom:6px'>
    Chưa có thành viên nào
  </div>
  <div style='font-size:13px;color:#6b7280'>
    Thêm thành viên để cùng nhau tích lũy — mỗi người một Cừu riêng 🐑💕
  </div>
</div>
""", unsafe_allow_html=True)
