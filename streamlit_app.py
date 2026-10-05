import csv
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import pandas as pd

from recommendation import get_target_calories, find_meal_options

# ============================================================
# PAGE / CONFIG
# ============================================================
st.set_page_config(page_title="SmartPlate", page_icon="🥗", layout="centered")


# ============================================================
# SMARTPLATE VISUAL IDENTITY — CAMPUS NAVY + GOLD + GREEN
# ============================================================
st.markdown("""
<style>
:root {
    --sp-navy: #081E3F;
    --sp-gold: #B6862C;
    --sp-green: #2F6B4F;
    --sp-cream: #F7F3E8;
    --sp-soft-green: #E8F0E9;
    --sp-ink: #20252B;
    --sp-white: #FFFFFF;
}

/* Page */
.stApp {
    background:
      radial-gradient(circle at 90% 0%, rgba(182,134,44,.10), transparent 24rem),
      linear-gradient(180deg, #FBF8F0 0%, var(--sp-cream) 100%);
    color: var(--sp-ink);
}
.block-container {
    max-width: 920px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* A thin campus-gold signature line */
.block-container::before {
    content: "SMARTPLATE  •  8TH STREET";
    display: block;
    color: var(--sp-gold);
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .16em;
    border-top: 5px solid var(--sp-navy);
    padding-top: .8rem;
    margin-bottom: 1.2rem;
}

/* Typography */
h1, h2, h3 { color: var(--sp-navy) !important; letter-spacing: -0.025em; }
h1 { font-weight: 850 !important; }
p, label, .stCaption { color: var(--sp-ink); }

/* Cards / bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.88);
    border: 1px solid rgba(8,30,63,.12) !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 26px rgba(8,30,63,.055);
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,.92);
    border: 1px solid rgba(8,30,63,.10);
    border-top: 4px solid var(--sp-gold);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: 0 7px 20px rgba(8,30,63,.05);
}
[data-testid="stMetricValue"] { color: var(--sp-navy); font-weight: 800; }

/* Buttons */
.stButton > button {
    border-radius: 999px !important;
    min-height: 2.8rem;
    font-weight: 750 !important;
    border: 1px solid rgba(8,30,63,.20) !important;
    transition: transform .14s ease, box-shadow .14s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    border-color: var(--sp-gold) !important;
    box-shadow: 0 7px 18px rgba(8,30,63,.10);
}
.stButton > button[kind="primary"] {
    background: var(--sp-navy) !important;
    color: white !important;
    border-color: var(--sp-navy) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 7px 0 var(--sp-gold), 0 12px 24px rgba(8,30,63,.14);
}

/* Inputs */
input, textarea, [data-baseweb="select"] > div {
    border-radius: 12px !important;
}
input:focus, textarea:focus {
    border-color: var(--sp-green) !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 750;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--sp-navy) !important;
}
[data-baseweb="tab-highlight"] { background-color: var(--sp-gold) !important; }

/* Progress = reward gold */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--sp-gold), #D8B45C) !important;
    border-radius: 999px;
}

/* Status messages */
[data-testid="stAlert"] { border-radius: 14px; }

/* Dividers */
hr { border-color: rgba(8,30,63,.12) !important; }

/* Expander */
[data-testid="stExpander"] {
    background: rgba(255,255,255,.68);
    border-radius: 14px !important;
    border-color: rgba(8,30,63,.10) !important;
}

/* Mobile */
@media (max-width: 640px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
    .block-container::before { font-size: .62rem; }
}


/* ==========================================================
   SMARTPLATE MICRO-ANIMATIONS — CSS ONLY, NO EXTRA PACKAGES
   ========================================================== */
@keyframes spFadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes spFloat {
    0%, 100% { transform: translateY(0) rotate(-2deg); }
    50%      { transform: translateY(-7px) rotate(2deg); }
}
@keyframes spPulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50%      { transform: scale(1.06); opacity: .78; }
}
@keyframes spShimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Gentle entrance for the page content */
.block-container > div {
    animation: spFadeUp .45s ease-out both;
}

/* Animated SmartPlate signature icon */
.block-container::after {
    content: "🍽️";
    position: fixed;
    right: 2.2rem;
    bottom: 1.8rem;
    width: 3.2rem;
    height: 3.2rem;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: var(--sp-navy);
    border: 3px solid var(--sp-gold);
    box-shadow: 0 10px 28px rgba(8,30,63,.18);
    font-size: 1.35rem;
    animation: spFloat 3.2s ease-in-out infinite;
    z-index: 50;
    pointer-events: none;
}

/* Cards feel alive without being distracting */
[data-testid="stVerticalBlockBorderWrapper"] {
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    border-color: rgba(182,134,44,.42) !important;
    box-shadow: 0 13px 30px rgba(8,30,63,.09);
}

/* Ready/success messages get a subtle pulse */
[data-testid="stAlert"] {
    animation: spFadeUp .3s ease-out both;
}

/* Gold shimmer on progress bars */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--sp-gold), #E3C66E, var(--sp-gold));
    background-size: 200% 100%;
    animation: spShimmer 2.4s linear infinite;
}

/* Respect accessibility preference */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
    }
}


.sp-countdown-card {
    text-align: center;
    padding: 30px;
    margin-top: 16px;
    background: rgba(255,255,255,.96);
    border: 1px solid rgba(8,30,63,.12);
    border-radius: 22px;
    box-shadow: 0 10px 30px rgba(8,30,63,.08);
}
.sp-countdown-label {font-size:.85rem;font-weight:800;letter-spacing:.08em;color:#5b6472;}
.sp-countdown-number {font-size:4rem;font-weight:900;color:#081E3F;line-height:1.15;}
.sp-countdown-note {color:#5b6472;}
/* Hide Streamlit top header only */
header[data-testid="stHeader"] {
    display: none !important;
}
/* =========================================================
   FORCE ALL BUTTON TEXT TO WHITE
   ========================================================= */

div.stButton > button,
div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Keep text white on hover / focus / click */
div.stButton > button:hover,
div.stButton > button:hover p,
div.stButton > button:hover span,
div.stButton > button:hover div,
div.stButton > button:focus,
div.stButton > button:focus p,
div.stButton > button:active,
div.stButton > button:active p {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* Feedback text area */
div[data-testid="stTextArea"] textarea {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    caret-color: #FFFFFF !important;
}

/* Placeholder text */
div[data-testid="stTextArea"] textarea::placeholder {
    color: #BFC5D0 !important;
    -webkit-text-fill-color: #BFC5D0 !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

CURRENT_MENU_FILE = "current_menu.csv"
MEAL_HISTORY_FILE = "meal_history.csv"
STUDENT_PROFILES_FILE = "student_profiles.csv"
PENDING_ORDERS_FILE = "pending_orders.csv"
FREE_MEAL_THRESHOLD = 1000
DEMO_FEEDBACK_WAIT_SECONDS = 10
PORTION_THRESHOLDS = {"Breakfast": 700, "Lunch": 1500, "Dinner": 1200}
FIU_TZ = ZoneInfo("America/New_York")

# ============================================================
# HELPERS
# ============================================================
def now_fiu():
    return datetime.now(FIU_TZ)


def valid_panther_id(value):
    return len(value) == 7 and value.isdigit()


def go(screen):
    st.session_state.screen = screen
    st.rerun()


def food_key(food):
    return (
        food.get("food_name", ""),
        food.get("station", ""),
        food.get("portion", ""),
        int(food.get("calories", 0)),
    )


def load_current_menu():
    if not os.path.exists(CURRENT_MENU_FILE):
        return []
    menu = []
    with open(CURRENT_MENU_FILE, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                row["calories"] = int(float(row.get("calories", 0)))
            except (TypeError, ValueError):
                continue
            row.setdefault("station", "Unknown Station")
            row.setdefault("category", "Other")
            row.setdefault("portion", "")
            row.setdefault("meal_period", "")
            row.setdefault("date", "")
            menu.append(row)
    return menu


def load_profiles():
    if not os.path.exists(STUDENT_PROFILES_FILE):
        return {}
    profiles = {}
    with open(STUDENT_PROFILES_FILE, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                profiles[row["panther_id"]] = {
                    "student_name": row.get("student_name", ""),
                    "total_points": int(row.get("total_points", 0)),
                    "free_meals_earned": int(row.get("free_meals_earned", 0)),
                }
            except (KeyError, ValueError):
                continue
    return profiles


def save_profiles(profiles):
    with open(STUDENT_PROFILES_FILE, "w", newline="", encoding="utf-8") as f:
        fields = ["panther_id", "student_name", "total_points", "free_meals_earned"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for pid, p in profiles.items():
            writer.writerow({
                "panther_id": pid,
                "student_name": p["student_name"],
                "total_points": p["total_points"],
                "free_meals_earned": p["free_meals_earned"],
            })


def get_or_create_student(pid, name):
    profiles = load_profiles()
    profile = profiles.get(pid, {
        "student_name": name,
        "total_points": 0,
        "free_meals_earned": 0,
    })
    profile["student_name"] = name
    profiles[pid] = profile
    save_profiles(profiles)
    return profile


def calculate_points(waste):
    return {"Nothing": 20, "A little": 10, "Some": 5, "A lot": 0}.get(waste, 0)


def update_points(pid, earned):
    profiles = load_profiles()
    p = profiles[pid]
    combined = p["total_points"] + earned
    new_rewards = combined // FREE_MEAL_THRESHOLD
    p["total_points"] = combined % FREE_MEAL_THRESHOLD
    p["free_meals_earned"] += new_rewards
    profiles[pid] = p
    save_profiles(profiles)
    return p["total_points"], p["free_meals_earned"], new_rewards


def save_history(waste, leftovers, comment, points):
    fields = [
        "timestamp", "order_id", "panther_id", "student_name", "hunger_level",
        "meal_period", "meal_type", "foods_selected", "stations", "total_calories",
        "waste_level", "leftover_food", "feedback_comment", "smartpoints"
    ]
    row = {
        "timestamp": now_fiu().strftime("%Y-%m-%d %H:%M:%S"),
        "order_id": st.session_state.order_id,
        "panther_id": st.session_state.panther_id,
        "student_name": st.session_state.name,
        "hunger_level": st.session_state.hunger_level,
        "meal_period": st.session_state.meal_period,
        "meal_type": st.session_state.meal_type,
        "foods_selected": " | ".join(f["food_name"] for f in st.session_state.selected_meal),
        "stations": " | ".join(dict.fromkeys(f.get("station", "Unknown") for f in st.session_state.selected_meal)),
        "total_calories": st.session_state.selected_total,
        "waste_level": waste,
        "leftover_food": " | ".join(leftovers) if leftovers else "None",
        "feedback_comment": comment.strip(),
        "smartpoints": points,
    }
    # Keep the MVP safe even if an older history CSV has a different schema.
    old_rows = []
    if os.path.exists(MEAL_HISTORY_FILE):
        try:
            with open(MEAL_HISTORY_FILE, "r", encoding="utf-8") as f:
                old_rows = list(csv.DictReader(f))
        except Exception:
            old_rows = []
    with open(MEAL_HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for old in old_rows:
            writer.writerow({k: old.get(k, "") for k in fields})
        writer.writerow(row)



def save_pending_order():
    """Persist the current collected order until mandatory feedback is submitted."""
    fields = [
        "order_id", "panther_id", "student_name", "hunger_level",
        "meal_period", "meal_type", "foods_selected", "stations",
        "total_calories", "collected_at"
    ]

    row = {
        "order_id": st.session_state.order_id,
        "panther_id": st.session_state.panther_id,
        "student_name": st.session_state.name,
        "hunger_level": st.session_state.hunger_level,
        "meal_period": st.session_state.meal_period,
        "meal_type": st.session_state.meal_type,
        "foods_selected": " | ".join(
            f["food_name"] for f in st.session_state.selected_meal
        ),
        "stations": " | ".join(
            dict.fromkeys(
                f.get("station", "Unknown")
                for f in st.session_state.selected_meal
            )
        ),
        "total_calories": st.session_state.selected_total,
        "collected_at": st.session_state.collected_at or time.time(),
    }

    old_rows = []
    if os.path.exists(PENDING_ORDERS_FILE):
        try:
            with open(PENDING_ORDERS_FILE, "r", encoding="utf-8") as f:
                old_rows = list(csv.DictReader(f))
        except Exception:
            old_rows = []

    # One pending order per student. Re-saving updates the same order
    # instead of creating duplicates.
    old_rows = [
        r for r in old_rows
        if r.get("panther_id") != st.session_state.panther_id
    ]
    old_rows.append(row)

    with open(PENDING_ORDERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in old_rows:
            writer.writerow({k: r.get(k, "") for k in fields})


def load_pending_order(pid):
    """Return a student's unfinished order, if one exists."""
    if not os.path.exists(PENDING_ORDERS_FILE):
        return None

    try:
        with open(PENDING_ORDERS_FILE, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("panther_id") == pid:
                    return row
    except Exception:
        return None

    return None


def clear_pending_order(pid):
    """Remove a pending order after feedback is successfully submitted."""
    if not os.path.exists(PENDING_ORDERS_FILE):
        return

    fields = [
        "order_id", "panther_id", "student_name", "hunger_level",
        "meal_period", "meal_type", "foods_selected", "stations",
        "total_calories", "collected_at"
    ]

    try:
        with open(PENDING_ORDERS_FILE, "r", encoding="utf-8") as f:
            rows = [
                row for row in csv.DictReader(f)
                if row.get("panther_id") != pid
            ]
    except Exception:
        rows = []

    with open(PENDING_ORDERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def restore_pending_order(row):
    """Restore enough state to force completion of feedback after a new login."""
    st.session_state.order_id = row.get("order_id")
    st.session_state.hunger_level = row.get("hunger_level")
    st.session_state.meal_period = row.get("meal_period")
    st.session_state.meal_type = row.get("meal_type")

    try:
        st.session_state.selected_total = int(float(row.get("total_calories", 0)))
    except (TypeError, ValueError):
        st.session_state.selected_total = 0

    # Rebuild selected_meal from the current menu when possible so the
    # leftover-food multiselect still contains the original food names.
    wanted_names = [
        name.strip()
        for name in (row.get("foods_selected") or "").split("|")
        if name.strip()
    ]

    current_menu = st.session_state.menu or load_current_menu()
    restored = []
    used = set()

    for wanted in wanted_names:
        match = next(
            (
                food for food in current_menu
                if food.get("food_name") == wanted
                and food_key(food) not in used
            ),
            None,
        )

        if match:
            restored.append(match)
            used.add(food_key(match))
        else:
            # Minimal fallback if the live menu changed between meals.
            restored.append({
                "food_name": wanted,
                "station": "Previous Order",
                "category": "Other",
                "portion": "",
                "calories": 0,
            })

    st.session_state.selected_meal = restored
    st.session_state.feedback_submitted = False

    try:
        st.session_state.collected_at = float(row.get("collected_at") or time.time())
    except (TypeError, ValueError):
        st.session_state.collected_at = time.time()


def make_order_id():
    return "SP" + now_fiu().strftime("%H%M%S")


def load_student_history(pid):
    """Return completed meal transactions for one Panther ID."""
    if not os.path.exists(MEAL_HISTORY_FILE):
        return []
    with open(MEAL_HISTORY_FILE, "r", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("panther_id") == pid]


def render_reward_progress():
    points = int(st.session_state.current_points)
    rewards = int(st.session_state.free_meals_earned)
    remaining = FREE_MEAL_THRESHOLD - points
    st.markdown("### 🎁 Prototype Reward Progress")
    st.progress(min(points / FREE_MEAL_THRESHOLD, 1.0))
    st.markdown(f"**{points:,} / {FREE_MEAL_THRESHOLD:,} SmartPoints**")
    st.caption(f"{remaining:,} points until your next Prototype Reward • 1,000 SmartPoints = 1 proposed free meal")
    if rewards:
        st.success(f"🏆 Prototype rewards earned: {rewards}")
    st.caption("Prototype concept only — not an existing FIU Dining benefit.")


def render_my_impact():
    rows = load_student_history(st.session_state.panther_id)
    st.title("📊 My Impact")
    st.caption("Your personal SmartPlate history — based only on completed meals and submitted feedback.")

    if not rows:
        st.info("No completed meals yet. Finish an order and submit feedback to start building your impact dashboard.")
        render_reward_progress()
        return

    total = len(rows)
    low_waste = sum(1 for r in rows if r.get("waste_level") in {"Nothing", "A little"})
    low_rate = round(100 * low_waste / total) if total else 0
    total_points_earned = sum(int(float(r.get("smartpoints") or 0)) for r in rows)

    c1, c2, c3 = st.columns(3)
    c1.metric("🍽️ Meals Tracked", total)
    c2.metric("♻️ Low-Waste Rate", f"{low_rate}%")
    c3.metric("⭐ Points Earned", total_points_earned)

    render_reward_progress()
    st.divider()

    st.subheader("♻️ My Waste Pattern")
    order = ["Nothing", "A little", "Some", "A lot"]
    counts = {label: 0 for label in order}
    for r in rows:
        level = r.get("waste_level")
        if level in counts:
            counts[level] += 1
    waste_df = pd.DataFrame({"Waste Level": order, "Meals": [counts[x] for x in order]}).set_index("Waste Level")
    st.bar_chart(waste_df, use_container_width=True)
    st.caption(f"{low_waste} of {total} tracked meals had little or no reported waste.")

    st.subheader("🥡 Foods I Leave Most")
    leftover_counts = {}
    for r in rows:
        raw = (r.get("leftover_food") or "").strip()
        if not raw or raw.lower() == "none":
            continue
        for food in [x.strip() for x in raw.split("|") if x.strip()]:
            leftover_counts[food] = leftover_counts.get(food, 0) + 1
    if leftover_counts:
        top = sorted(leftover_counts.items(), key=lambda x: (-x[1], x[0]))[:5]
        left_df = pd.DataFrame(top, columns=["Food", "Times Left"]).set_index("Food")
        st.bar_chart(left_df, use_container_width=True)
    else:
        st.success("No noticeable leftover foods have been reported yet. 🎉")

    st.subheader("🕘 Recent Meals")
    for r in list(reversed(rows))[:5]:
        when = r.get("timestamp", "")
        meal_period = r.get("meal_period", "Meal")
        foods = (r.get("foods_selected") or "").replace(" | ", ", ")
        waste = r.get("waste_level", "")
        pts = r.get("smartpoints", "0")
        with st.container(border=True):
            st.markdown(f"**{meal_period} • {when}**")
            st.write(foods or "No food details")
            st.caption(f"Waste: {waste} • +{pts} SmartPoints")


def group_by_station(meal):
    grouped = {}
    for food in meal:
        grouped.setdefault(food.get("station", "Unknown Station"), []).append(food)
    return grouped


def reset_order():
    for key, value in {
        "hunger_level": None,
        "meal_options": None,
        "selected_meal": [],
        "selected_total": 0,
        "meal_type": None,
        "custom_plate": [],
        "order_id": None,
        "station_status": {},
        "collected_at": None,
        "feedback_submitted": False,
        "smartpoints_earned": 0,
        "new_free_meals": 0,
        "waste_level": None,
        "leftover_food": [],
        "feedback_comment": "",
    }.items():
        st.session_state[key] = value


# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "screen": "login", "name": "", "panther_id": "", "menu": None,
    "meal_period": "", "hunger_level": None, "meal_options": None,
    "selected_meal": [], "selected_total": 0, "meal_type": None,
    "custom_plate": [], "current_points": 0, "free_meals_earned": 0,
    "smartpoints_earned": 0, "new_free_meals": 0, "order_id": None,
    "station_status": {}, "collected_at": None, "feedback_submitted": False,
    "waste_level": None, "leftover_food": [], "feedback_comment": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# LOGIN
# ============================================================
if st.session_state.screen == "login":
    st.title("🥗 SmartPlate")
    st.subheader("Smarter portions. Less food waste.")
    st.write("Prototype for 8th Street Campus Kitchen")
    name = st.text_input("Name", value=st.session_state.name)
    pid = st.text_input("Panther ID", value=st.session_state.panther_id, max_chars=7)
    st.caption("Demo login: enter a name and any 7-digit Panther ID.")
    if st.button("Get Started →", type="primary", use_container_width=True):
        if not name.strip():
            st.error("Please enter your name.")
        elif not valid_panther_id(pid):
            st.error("Panther ID must be exactly 7 digits.")
        else:
            st.session_state.name = name.strip()
            st.session_state.panther_id = pid
            profile = get_or_create_student(pid, name.strip())
            st.session_state.current_points = profile["total_points"]
            st.session_state.free_meals_earned = profile["free_meals_earned"]
            st.session_state.menu = load_current_menu()

            pending = load_pending_order(pid)
            if pending:
                restore_pending_order(pending)
                go("feedback")

            if st.session_state.menu:
                st.session_state.meal_period = st.session_state.menu[0].get(
                    "meal_period", "Current Meal"
                )
            go("hunger")

# ============================================================
# HUNGER
# ============================================================
elif st.session_state.screen == "hunger":
    menu = st.session_state.menu or []
    st.title("🥗 SmartPlate")
    st.write(f"Hi, **{st.session_state.name}** 👋")
    c1, c2 = st.columns(2)
    c1.metric("⭐ SmartPoints", f"{st.session_state.current_points:,} / {FREE_MEAL_THRESHOLD:,}")
    c2.metric("🎟️ Prototype Rewards", st.session_state.free_meals_earned)
    st.progress(min(st.session_state.current_points / FREE_MEAL_THRESHOLD, 1.0))
    st.caption(f"{FREE_MEAL_THRESHOLD - st.session_state.current_points:,} points until your next Prototype Reward • 1,000 points = 1 proposed free meal")
    if st.button("📊 View My Impact", use_container_width=True):
        go("impact")
    if menu:
        st.success(f"🟢 {st.session_state.meal_period} menu • {len(menu)} items synced")
    else:
        st.error("No synced menu found. Run menu_scraper.py, then reload SmartPlate.")
    st.header("How hungry are you?")
    hunger = st.radio("Choose one:", ["Light", "Moderate", "Very Hungry"], index=1)
    st.caption("Used only to estimate a first-order size; not medical or nutritional advice.")
    if st.button("Find My Plate →", type="primary", use_container_width=True, disabled=not menu):
        st.session_state.hunger_level = hunger
        st.session_state.meal_options = find_meal_options(menu, get_target_calories(hunger))
        go("meal_selection")

# ============================================================
# MY IMPACT — PERSONAL STUDENT DASHBOARD
# ============================================================
elif st.session_state.screen == "impact":
    render_my_impact()
    st.divider()
    if st.button("← Back to SmartPlate", use_container_width=True):
        go("hunger")

# ============================================================
# MEAL SELECTION
# ============================================================
elif st.session_state.screen == "meal_selection":
    menu = st.session_state.menu or []
    st.title(f"🍽️ Today's {st.session_state.meal_period}")
    st.caption("Choose a suggestion or build an order by station.")
    suggestion_tab,menu_tab, build_tab = st.tabs(["✨ Suggestions","📋 Menu", "🥣 Build My Order"])

    with suggestion_tab:
            options = (st.session_state.meal_options or [])[:5]
            if not options:
                st.info("No suggestion available. Build your own order instead.")
            for i, (meal, total) in enumerate(options, 1):
                with st.container(border=True):
                    st.markdown(f"### Plate {i} — {total} cal")
                    for f in meal:
                        st.write(f"• **{f['food_name']}** — {f.get('station','Unknown')}")
                    if st.button(f"Choose Plate {i}", key=f"rec_{i}", use_container_width=True):
                        st.session_state.selected_meal = list(meal)
                        st.session_state.selected_total = total
                        st.session_state.meal_type = "Recommended"
                        go("confirm")
    with menu_tab:
        for station in dict.fromkeys(f.get("station", "Unknown Station") for f in menu):
            foods = [f for f in menu if f.get("station", "Unknown Station") == station]
            with st.expander(f"📍 {station} ({len(foods)})"):
                for f in foods:
                    st.markdown(f"**{f['food_name']}**")
                    st.caption(f"{f.get('portion','')} • {f['calories']} cal • {f.get('category','Other')}")


    with build_tab:
        st.write("Add foods station by station. Your order stays saved while you browse.")
        stations = list(dict.fromkeys(f.get("station", "Unknown Station") for f in menu))
        station = st.selectbox("Choose a station", stations)
        station_foods = [f for f in menu if f.get("station", "Unknown Station") == station]
        lookup = {}
        for i, f in enumerate(station_foods):
            label = f"{f['food_name']} — {f.get('portion','')} — {f['calories']} cal"
            if label in lookup:
                label += f" #{i+1}"
            lookup[label] = f
        labels = st.multiselect("Select food(s)", list(lookup), key=f"pick_{station}")
        if st.button("➕ Add to Order", use_container_width=True):
            existing = {food_key(f) for f in st.session_state.custom_plate}
            for label in labels:
                f = lookup[label]
                if food_key(f) not in existing:
                    st.session_state.custom_plate.append(f)
                    existing.add(food_key(f))
            st.rerun()

        st.divider()
        st.subheader("🧾 Your Order")
        plate = st.session_state.custom_plate
        if not plate:
            st.info("Your order is empty.")
        else:
            for i, f in enumerate(plate):
                a, b = st.columns([5, 1])
                a.write(f"**{f['food_name']}** — {f.get('station','Unknown')}")
                a.caption(f"{f.get('portion','')} • {f['calories']} cal")
                if b.button("✕", key=f"rm_{i}"):
                    st.session_state.custom_plate.pop(i)
                    st.rerun()
            total = sum(f["calories"] for f in plate)
            st.metric("Order Calories", f"{total} cal")
            threshold = PORTION_THRESHOLDS.get(st.session_state.meal_period)
            if threshold and total > threshold:
                st.warning("⚠️ **Portion Reminder**\n\nThis first order may be larger than a typical portion. Consider starting smaller to help reduce food waste. You can still continue with your current order.")
                st.caption("Portion-awareness guidance only; not medical or nutritional advice.")
            if st.button("Continue with My Order →", type="primary", use_container_width=True):
                st.session_state.selected_meal = list(plate)
                st.session_state.selected_total = total
                st.session_state.meal_type = "Custom"
                go("confirm")

# ============================================================
# CONFIRM / PLACE ORDER
# ============================================================
elif st.session_state.screen == "confirm":
    meal = st.session_state.selected_meal or []
    st.title("🧾 Review Your Order")
    grouped = group_by_station(meal)
    for station, foods in grouped.items():
        st.markdown(f"### 📍 {station}")
        for f in foods:
            st.write(f"• {f['food_name']} — {f.get('portion','')} — {f['calories']} cal")
    st.metric("Total", f"{st.session_state.selected_total} cal")
    st.caption("Calories are shown as a meal-size reference only.")
    c1, c2 = st.columns(2)
    if c1.button("← Change", use_container_width=True):
        go("meal_selection")
    if c2.button("Place Order →", type="primary", use_container_width=True):
        st.session_state.order_id = make_order_id()
        st.session_state.station_status = {station: "Preparing" for station in grouped}
        go("order_status")

# ============================================================
# DIGITAL TICKET / STATION FULFILLMENT
# ============================================================
elif st.session_state.screen == "order_status":
    meal = st.session_state.selected_meal or []
    grouped = group_by_station(meal)
    st.title(f"🎫 Order {st.session_state.order_id}")
    st.write("Pick up your food station by station as each ticket becomes ready.")

    for station, foods in grouped.items():
        status = st.session_state.station_status.get(station, "Preparing")
        with st.container(border=True):
            st.markdown(f"### 📍 {station}")
            for f in foods:
                st.write(f"• {f['food_name']} — {f.get('portion','')}")
            if status == "Preparing":
                st.warning("🟡 Preparing")
            elif status == "Ready":
                st.success("🟢 Ready for pickup")
            else:
                st.info("✅ Collected")

            # Demo controls simulate the station-side workflow.
            with st.expander("🧑‍🍳 Station Demo Control"):
                if status == "Preparing":
                    if st.button("Mark Ready", key=f"ready_{station}"):
                        st.session_state.station_status[station] = "Ready"
                        st.rerun()
                elif status == "Ready":
                    if st.button("Mark Collected", key=f"collect_{station}"):
                        st.session_state.station_status[station] = "Collected"
                        st.rerun()

    statuses = list(st.session_state.station_status.values())
    if statuses and all(s == "Collected" for s in statuses):
        if st.session_state.collected_at is None:
            st.session_state.collected_at = time.time()
            save_pending_order()
        st.success("🎉 Full order collected. Enjoy your meal!")
        if st.button("Continue →", type="primary", use_container_width=True):
            go("meal_in_progress")
    else:
        st.caption("Feedback unlocks only after the full order has been collected.")

# ============================================================
# MEAL IN PROGRESS / DEMO TIMER
# ============================================================
elif st.session_state.screen == "meal_in_progress":
    st.title("🍽️ Meal in Progress")
    st.write(f"Order **{st.session_state.order_id}** has been fully collected.")

    # Store one Unix timestamp and keep it unchanged across Streamlit reruns.
    if st.session_state.collected_at is None:
        st.session_state.collected_at = time.time()

    elapsed = time.time() - float(st.session_state.collected_at)
    remaining = max(0, DEMO_FEEDBACK_WAIT_SECONDS - int(elapsed))

    if remaining > 0:
        st.markdown(
            f"""
            <div class="sp-countdown-card">
                <div class="sp-countdown-label">FEEDBACK UNLOCKS IN</div>
                <div class="sp-countdown-number">{remaining}</div>
                <div class="sp-countdown-note">Enjoy your meal first ♡</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Demo mode: the production feedback delay would be longer so students can finish eating first.")
        time.sleep(1)
        st.rerun()
    else:
        st.success("🎉 YAYYYYY! FEEDBACK UNLOCKED")
        time.sleep(0.6)
        go("feedback")


# ============================================================
# MANDATORY FEEDBACK
# ============================================================
elif st.session_state.screen == "feedback":
    st.title("♻️ How Did Your Portion Work?")
    st.write("Complete this feedback before starting another order.")
    waste = st.radio("How much food was left?", ["Nothing", "A little", "Some", "A lot"])
    names = list(dict.fromkeys(f["food_name"] for f in (st.session_state.selected_meal or [])))
    leftovers = []
    if waste == "Nothing":
        st.success("🎉 Great — no noticeable food was left.")
    else:
        leftovers = st.multiselect(
            "Which food(s) did you leave a noticeable amount of? Select all that apply.",
            names,
        )
    comment = st.text_area("💬 Want to tell us more? (Optional)", placeholder="Example: portion was too large, food was cold, too salty...")

    if st.button("Submit Feedback →", type="primary", use_container_width=True):
        if waste != "Nothing" and not leftovers:
            st.error("Please select at least one leftover food.")
        elif st.session_state.feedback_submitted:
            st.warning("Feedback for this order has already been submitted.")
        else:
            points = calculate_points(waste)
            save_history(waste, leftovers, comment, points)
            current, rewards, new_rewards = update_points(st.session_state.panther_id, points)
            clear_pending_order(st.session_state.panther_id)
            st.session_state.current_points = current
            st.session_state.free_meals_earned = rewards
            st.session_state.new_free_meals = new_rewards
            st.session_state.smartpoints_earned = points
            st.session_state.waste_level = waste
            st.session_state.leftover_food = leftovers
            st.session_state.feedback_comment = comment
            st.session_state.feedback_submitted = True
            go("summary")

# ============================================================
# SUMMARY
# ============================================================
elif st.session_state.screen == "summary":
    st.title("⭐ SmartPoints")
    if st.session_state.new_free_meals > 0:
        st.balloons()
        st.success("🏆 You earned a prototype free-meal reward!")
        st.caption("Prototype reward concept — not an existing FIU Dining benefit.")
    else:
        st.success("Feedback submitted successfully!")
    st.metric("Points earned this order", f"+{st.session_state.smartpoints_earned}")
    render_reward_progress()
    st.divider()
    st.subheader("Order Summary")
    st.write(f"**Order:** {st.session_state.order_id}")
    st.write(f"**Hunger:** {st.session_state.hunger_level}")
    st.write(f"**Order type:** {st.session_state.meal_type}")
    st.write(f"**Meal size:** {st.session_state.selected_total} calories")
    st.write(f"**Food left:** {st.session_state.waste_level}")
    if st.session_state.leftover_food:
        st.write("**Leftover foods:** " + ", ".join(st.session_state.leftover_food))
    st.caption("Your feedback can be aggregated in Power BI to identify waste patterns by food, station, hunger level, and order type.")
    if st.button("📊 View My Impact", use_container_width=True):
        go("impact")
    if st.button("Start Another Order ↻", type="primary", use_container_width=True):
        reset_order()
        go("hunger")
