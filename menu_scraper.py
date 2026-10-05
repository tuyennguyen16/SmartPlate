import csv
import time
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# ============================================================
# SMARTPLATE CONFIGURATION
# ============================================================

FIU_TIMEZONE = ZoneInfo("America/New_York")

OUTPUT_FILE = "current_menu.csv"
DEBUG_FILE = "visible_menu.txt"

# 8th Street Campus Kitchen operating hours
# Monday = 0 ... Sunday = 6
OPERATING_HOURS = {
    0: (7, 23),   # Monday
    1: (7, 23),   # Tuesday
    2: (7, 23),   # Wednesday
    3: (7, 23),   # Thursday
    4: (8, 21),   # Friday
    5: (9, 21),   # Saturday
    6: (9, 21),   # Sunday
}

# Prototype meal-period boundaries.
# These are configurable SmartPlate assumptions,
# not claimed official FIU meal transition times.
BREAKFAST_END_HOUR = 11
LUNCH_END_HOUR = 16


# ============================================================
# 1. DATE / TIME
# ============================================================

def get_fiu_now():
    """Return current Miami/FIU local datetime."""
    return datetime.now(FIU_TIMEZONE)


def get_fiu_date():
    """Return current Miami/FIU date."""
    return get_fiu_now().strftime("%Y-%m-%d")


def format_hour(hour):
    """Convert a 24-hour integer into readable time."""

    if hour == 0:
        return "12:00 AM"

    if hour == 12:
        return "12:00 PM"

    if hour < 12:
        return f"{hour}:00 AM"

    return f"{hour - 12}:00 PM"


# ============================================================
# 2. OPERATING HOURS
# ============================================================

def get_today_hours(now=None):

    if now is None:
        now = get_fiu_now()

    return OPERATING_HOURS[now.weekday()]


def is_8th_street_open(now=None):

    if now is None:
        now = get_fiu_now()

    open_hour, close_hour = get_today_hours(now)

    current_minutes = (
        now.hour * 60
        + now.minute
    )

    open_minutes = open_hour * 60
    close_minutes = close_hour * 60

    return (
        open_minutes
        <= current_minutes
        < close_minutes
    )


def get_hours_message(now=None):

    if now is None:
        now = get_fiu_now()

    open_hour, close_hour = get_today_hours(now)

    return (
        f"{format_hour(open_hour)} – "
        f"{format_hour(close_hour)}"
    )


# ============================================================
# 3. MEAL PERIOD
# ============================================================

def get_current_meal_period(now=None):
    """
    SmartPlate prototype meal-period logic.

    Breakfast: before 11 AM
    Lunch:     11 AM - 3:59 PM
    Dinner:    4 PM onward
    """

    if now is None:
        now = get_fiu_now()

    hour = now.hour

    if hour < BREAKFAST_END_HOUR:
        return "breakfast"

    if hour < LUNCH_END_HOUR:
        return "lunch"

    return "dinner"


# ============================================================
# 4. DINEONCAMPUS URL
# ============================================================

def build_menu_url(date, meal_period):

    return (
        "https://dineoncampus.com/FIU/"
        "whats-on-the-menu/"
        "8th-street-campus-kitchen/"
        f"{date}/{meal_period.lower()}"
    )


# ============================================================
# 5. SMARTPLATE FOOD CATEGORIES
# ============================================================

def categorize_food(food_name):
    """
    Categorize foods for SmartPlate recommendations.

    NOTE:
    Station and category are different.

    Example:
        Grilled Herbed Chicken
        Station: FRESH 52
        Category: Protein
    """

    name = food_name.lower()

    # -------------------- ENTREE --------------------

    if any(word in name for word in [
        "pizza",
        "flatbread",
        "vindaloo",
        "bolognese",
    ]):
        return "Entrée"

    # -------------------- DESSERT -------------------

    if any(word in name for word in [
        "cookie",
        "brownie",
        "blondie",
        "pudding",
        "ice cream",
        "cake",
        "pie",
        "dessert",
    ]):
        return "Dessert"

    # -------------------- SOUP ----------------------

    if any(word in name for word in [
        "soup",
        "bisque",
        "chowder",
    ]):
        return "Soup"

    # -------------------- PROTEIN -------------------

    if any(word in name for word in [
        "egg",
        "sausage",
        "chicken",
        "turkey",
        "beef",
        "pork",
        "fish",
        "salmon",
        "shrimp",
        "meatball",
        "tofu",
        "ham",
        "steak",
        "hot dog",
        "omelet",
        "frittata",
    ]):
        return "Protein"

    # -------------------- GRAIN ---------------------

    if any(word in name for word in [
        "rice",
        "pasta",
        "penne",
        "spaghetti",
        "noodle",
        "bread",
        "toast",
        "roll",
        "tortilla",
        "farro",
        "oatmeal",
        "pancake",
        "waffle",
        "grits",
        "cereal",
    ]):
        return "Grain"

    # -------------------- LEGUME --------------------

    if any(word in name for word in [
        "chickpea",
        "garbanzo",
        "pinto bean",
        "black bean",
        "lentil",
        "hummus",
    ]):
        return "Legume"

    # -------------------- FRUIT ---------------------

    if any(word in name for word in [
        "fruit",
        "apple",
        "banana",
        "orange",
        "berry",
        "berries",
        "melon",
        "grape",
        "pineapple",
        "strawberry",
        "blueberry",
        "cranberry",
        "cranberries",
    ]):
        return "Fruit"

    # -------------------- DAIRY ---------------------

    if any(word in name for word in [
        "yogurt",
        "milk",
        "cheddar cheese",
        "swiss cheese",
        "american cheese",
        "feta cheese",
    ]):
        return "Dairy"

    # --------------- TOPPING / CONDIMENT -----------

    if any(word in name for word in [
        "dressing",
        "mustard",
        "mayonnaise",
        "vinegar",
        "olive oil",
        "parmesan",
        "crouton",
        "fried onion",
        "sauce",
        "syrup",
        "cracker",
        "pickle",
        "sesame seed",
        "chili crisp",
    ]):
        return "Topping / Condiment"

    # -------------------- SIDE ----------------------

    if any(word in name for word in [
        "potato",
        "tater",
        "fries",
        "chips",
    ]):
        return "Side"

    # ------------------ VEGETABLE -------------------

    if any(word in name for word in [
        "green bean",
        "brussels",
        "spinach",
        "lettuce",
        "tomato",
        "mushroom",
        "cucumber",
        "carrot",
        "onion",
        "bell pepper",
        "broccoli",
        "asparagus",
        "cabbage",
        "snap peas",
        "vegetable",
        "veggie",
    ]):
        return "Vegetable"

    return "Other"


# ============================================================
# 6. PARSER HELPERS
# ============================================================

def clean_lines(text):

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def looks_like_station(line):
    """
    Detect station headings dynamically.

    Examples:
        COMFORT/ HOMESTYLE
        DELICIOUS WITHOUT
        PLANT BASED
        FLAME
        BOK CHOY/MONGOLIAN
        FRESH 52
        CUCINA
    """

    if not line:
        return False

    ignored_uppercase = {
        "MEAL PLANS",
        "MENUS",
        "HOURS",
        "SHOPPING CART",
        "OPEN MENU",
        "FAVORITE",
        "MENU ITEM PORTION CALORIES",
    }

    if line.upper() in ignored_uppercase:
        return False

    if line != line.upper():
        return False

    if len(line) < 3:
        return False

    if not any(
        character.isalpha()
        for character in line
    ):
        return False

    return True


def looks_like_portion_calorie(line):
    """
    Examples:

        3 each 140
        1/2 cup 130
        4 ounce 200
        6 fl oz 90
        2 half 170
        1 ladle-1oz 35
    """

    pattern = re.compile(
        r"^(.+?)\s+(\d+(?:\.\d+)?)$"
    )

    match = pattern.match(line)

    if not match:
        return None

    portion = match.group(1).strip()

    portion_lower = portion.lower()

    portion_words = [
        "cup",
        "tbsp",
        "tsp",
        "oz",
        "ounce",
        "each",
        "slice",
        "ladle",
        "piece",
        "serving",
        "half",
        "portion",
    ]

    if not any(
        word in portion_lower
        for word in portion_words
    ):
        return None

    calories = int(
        float(match.group(2))
    )

    return portion, calories


# ============================================================
# 7. MENU PARSER
# ============================================================

def parse_visible_menu(
    text,
    meal_period,
    menu_date,
):
    """
    Parse DineOnCampus visible text.

    Typical structure:

        STATION
        Click any item for nutritional information.
        Menu Item Portion Calories
        Favorite

        Food Name
        Optional description
        Portion Calories

        Food Name
        Optional description
        Portion Calories

    The first content line after the previous food's
    portion/calorie row is treated as the next food name.
    """

    lines = clean_lines(text)

    menu = []

    current_station = None
    pending_content = []
    inside_menu = False

    ignored_lines = {
        "Favorite",
        "Click any item for nutritional information.",
        "Menu Item Portion Calories",
    }

    for i, line in enumerate(lines):

        # ----------------------------------------------------
        # END OF MENU
        # ----------------------------------------------------

        if (
            line.startswith("Last updated")
            or
            line == "Nutritional Information Disclaimer"
        ):
            break

        # ----------------------------------------------------
        # STATION DETECTION
        # ----------------------------------------------------

        if looks_like_station(line):

            next_lines = lines[
                i + 1:
                min(i + 4, len(lines))
            ]

            if (
                "Click any item for nutritional information."
                in next_lines
                or
                "Menu Item Portion Calories"
                in next_lines
            ):
                current_station = line
                pending_content = []
                inside_menu = True
                continue

        if not inside_menu:
            continue

        # ----------------------------------------------------
        # IGNORE WEBSITE LABELS
        # ----------------------------------------------------

        if line in ignored_lines:
            continue

        # ----------------------------------------------------
        # PORTION + CALORIE ROW
        # ----------------------------------------------------

        portion_result = (
            looks_like_portion_calorie(line)
        )

        if portion_result is not None:

            portion, calories = portion_result

            if (
                current_station
                and pending_content
            ):
                # The first line of the block is the food name.
                # Remaining lines, if any, are descriptions.
                food_name = (
                    pending_content[0].strip()
                )

                if (
                    food_name
                    and
                    not looks_like_station(
                        food_name
                    )
                ):
                    menu.append({
                        "food_name":
                            food_name,

                        "station":
                            current_station,

                        "category":
                            categorize_food(
                                food_name
                            ),

                        "portion":
                            portion,

                        "calories":
                            calories,

                        "meal_period":
                            meal_period.title(),

                        "date":
                            menu_date,
                    })

            # Start a fresh block for the next food.
            pending_content = []

            continue

        # ----------------------------------------------------
        # FOOD NAME / DESCRIPTION
        # ----------------------------------------------------

        if current_station:
            pending_content.append(line)

    # --------------------------------------------------------
    # REMOVE EXACT DUPLICATES
    # --------------------------------------------------------

    unique_menu = []
    seen = set()

    for food in menu:

        key = (
            food["food_name"],
            food["station"],
            food["portion"],
            food["calories"],
        )

        if key not in seen:
            seen.add(key)
            unique_menu.append(food)

    return unique_menu


# ============================================================
# 8. SELENIUM SCRAPER
# ============================================================

def scrape_menu(
    date=None,
    meal_period=None,
):

    if date is None:
        date = get_fiu_date()

    if meal_period is None:
        meal_period = (
            get_current_meal_period()
        )

    url = build_menu_url(
        date,
        meal_period,
    )

    print("=" * 65)
    print("🥗 SMARTPLATE MENU SYNC")
    print("=" * 65)

    print(f"Date: {date}")
    print(
        f"Meal: "
        f"{meal_period.title()}"
    )
    print(f"URL: {url}")
    print()

    # --------------------------------------------------------
    # CHROME
    # --------------------------------------------------------

    options = Options()

    # Keep browser visible.
    # DineOnCampus previously failed to render the full
    # dynamic menu reliably in headless mode.
    options.add_argument(
        "--window-size=1400,1000"
    )

    driver = webdriver.Chrome(
        options=options
    )

    try:

        print(
            "🌐 Opening DineOnCampus..."
        )

        driver.get(url)

        WebDriverWait(
            driver,
            20,
        ).until(
            lambda d:
            d.execute_script(
                "return document.readyState"
            )
            == "complete"
        )

        print(
            "✅ Main page loaded."
        )

        # Allow JavaScript menu content to load.
        time.sleep(5)

        print(
            "📜 Loading menu content..."
        )

        # Scroll to force lazy-loaded content to render.
        for _ in range(12):

            driver.execute_script(
                "window.scrollBy(0, 700);"
            )

            time.sleep(0.4)

        time.sleep(2)

        # ----------------------------------------------------
        # READ PAGE TEXT
        # ----------------------------------------------------

        body = driver.find_element(
            By.TAG_NAME,
            "body",
        )

        visible_text = body.text

        # ----------------------------------------------------
        # DEBUG COPY
        # ----------------------------------------------------

        with open(
            DEBUG_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                visible_text
            )

        print(
            f"💾 Saved raw page text "
            f"to {DEBUG_FILE}"
        )

        # ----------------------------------------------------
        # PARSE MENU
        # ----------------------------------------------------

        menu = parse_visible_menu(
            visible_text,
            meal_period,
            date,
        )

        print()
        print("=" * 65)
        print(
            "🍽️ EXTRACTED MENU BY STATION"
        )
        print("=" * 65)

        if not menu:

            print(
                "❌ 0 foods extracted."
            )

            return []

        # ----------------------------------------------------
        # GET STATIONS IN PAGE ORDER
        # ----------------------------------------------------

        stations = []

        for food in menu:

            station = food["station"]

            if station not in stations:
                stations.append(station)

        # ----------------------------------------------------
        # PRINT MENU
        # ----------------------------------------------------

        for station in stations:

            print()
            print(
                f"📍 {station}"
            )
            print("-" * 55)

            station_foods = [
                food
                for food in menu
                if food["station"]
                == station
            ]

            for food in station_foods:

                print(
                    f"• "
                    f"{food['food_name']} | "
                    f"{food['portion']} | "
                    f"{food['calories']} cal | "
                    f"{food['category']}"
                )

        print()

        print(
            f"✅ {len(menu)} foods "
            f"extracted from "
            f"{len(stations)} stations!"
        )

        return menu

    except Exception as error:

        print()
        print(
            "❌ SCRAPER ERROR:"
        )
        print(error)

        return []

    finally:

        driver.quit()


# ============================================================
# 9. SAVE CURRENT MENU
# ============================================================

def save_menu_to_csv(
    menu,
    filename=OUTPUT_FILE,
):
    """
    Save only successful menu data.

    If scraping fails, the previous valid
    current_menu.csv is preserved.
    """

    if not menu:

        print()

        print(
            "⚠️ No valid menu was extracted."
        )

        print(
            "Previous current_menu.csv "
            "was NOT overwritten."
        )

        return False

    fieldnames = [
        "food_name",
        "station",
        "category",
        "portion",
        "calories",
        "meal_period",
        "date",
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            menu
        )

    print()

    print(
        f"💾 Saved {len(menu)} foods "
        f"to {filename}"
    )

    return True


# ============================================================
# 10. SMARTPLATE MENU SYNC
# ============================================================

def sync_current_menu():

    now = get_fiu_now()

    menu_date = (
        now.strftime("%Y-%m-%d")
    )

    meal_period = (
        get_current_meal_period(now)
    )

    print()
    print("=" * 65)
    print(
        "🧠 SMARTPLATE SYNC CHECK"
    )
    print("=" * 65)

    print(
        "FIU Time:",
        now.strftime(
            "%A, %B %d, %Y %I:%M %p"
        ),
    )

    print(
        "Today's hours:",
        get_hours_message(now),
    )

    # --------------------------------------------------------
    # OPEN / CLOSED
    # --------------------------------------------------------

    if is_8th_street_open(now):

        print(
            "Dining Hall Status: "
            "🟢 OPEN"
        )

    else:

        print(
            "Dining Hall Status: "
            "🔴 CLOSED"
        )

        print(
            "ℹ️ SmartPlate will still "
            "attempt to sync today's "
            f"{meal_period.title()} menu."
        )

    print(
        "Selected Meal Period:",
        meal_period.title(),
    )

    print()

    # --------------------------------------------------------
    # SCRAPE
    # --------------------------------------------------------

    menu = scrape_menu(
        date=menu_date,
        meal_period=meal_period,
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    saved = save_menu_to_csv(
        menu,
        OUTPUT_FILE,
    )

    if saved:

        print()
        print("=" * 65)
        print(
            "🎉 MENU SYNC COMPLETE"
        )
        print("=" * 65)

        print(
            f"{meal_period.title()} "
            f"menu for {menu_date} "
            "is ready for SmartPlate."
        )

    else:

        print()
        print("=" * 65)
        print(
            "⚠️ MENU SYNC INCOMPLETE"
        )
        print("=" * 65)


# ============================================================
# 11. RUN
# ============================================================

if __name__ == "__main__":
    sync_current_menu()