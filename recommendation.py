import csv

import itertools





# ============================================================

# CONFIG

# ============================================================



MENU_FILE = "current_menu.csv"





# ============================================================

# LOAD CURRENT MENU

# ============================================================



def load_menu(filename=MENU_FILE):

    """

    Load the menu synced by menu_scraper.py.

    """



    menu = []



    try:

        with open(

            filename,

            "r",

            encoding="utf-8"

        ) as file:



            reader = csv.DictReader(file)



            for food in reader:



                try:

                    food["calories"] = int(

                        float(food["calories"])

                    )

                except (ValueError, TypeError):

                    food["calories"] = 0



                # Keep scraper fields available

                food.setdefault(

                    "station",

                    "Unknown Station"

                )



                food.setdefault(

                    "category",

                    "Other"

                )



                food.setdefault(

                    "portion",

                    ""

                )



                food.setdefault(

                    "meal_period",

                    ""

                )



                food.setdefault(

                    "date",

                    ""

                )



                menu.append(food)



    except FileNotFoundError:



        print(

            "⚠️ current_menu.csv not found. "

            "Run menu_scraper.py first."

        )



    return menu





# ============================================================

# CALCULATE TOTAL CALORIES

# ============================================================



def calculate_total_calories(meal):



    return sum(

        food.get("calories", 0)

        for food in meal

    )





# ============================================================

# HUNGER TARGET

# ============================================================



def get_target_calories(hunger_level):

    """

    Internal SmartPlate recommendation targets.



    These are prototype portion-awareness values,

    not medical or nutritional recommendations.

    """



    targets = {

        "Light": 600,

        "Moderate": 800,

        "Very Hungry": 1200

    }



    return targets.get(

        hunger_level,

        600

    )





# ============================================================

# VARIETY SCORE

# ============================================================



def get_variety_score(meal):



    excluded_categories = {

        "Other",

        "Topping",

        "Topping / Condiment",

        "Dessert"

    }



    categories = {

        food.get(

            "category",

            "Other"

        )

        for food in meal

        if food.get(

            "category",

            "Other"

        )

        not in excluded_categories

    }



    return len(categories)





# ============================================================

# STATION VARIETY

# ============================================================



def get_station_score(meal):

    """

    Slightly prefer meals that do not require

    too many different station stops.

    """



    stations = {

        food.get(

            "station",

            "Unknown Station"

        )

        for food in meal

    }



    return len(stations)





# ============================================================

# RECOMMENDATION CANDIDATES

# ============================================================



def build_candidate_pool(menu):

    """

    Reduce the live menu into a manageable candidate pool.



    This prevents millions of combinations while still

    keeping foods from the major SmartPlate categories.

    """



    excluded = {

        "Topping",

        "Topping / Condiment",

        "Dessert"

    }



    main_foods = [

        food

        for food in menu

        if food.get(

            "category",

            "Other"

        )

        not in excluded

        and food.get(

            "calories",

            0

        ) > 0

    ]



    if not main_foods:

        main_foods = [

            food

            for food in menu

            if food.get(

                "calories",

                0

            ) > 0

        ]



    # Maximum foods considered from each category.

    category_limits = {

        "Protein": 6,

        "Entrée": 5,

        "Grain": 5,

        "Vegetable": 5,

        "Side": 4,

        "Legume": 3,

        "Fruit": 3,

        "Dairy": 3,

        "Soup": 3,

        "Other": 3

    }



    candidates = []



    for category, limit in category_limits.items():



        category_foods = [

            food

            for food in main_foods

            if food.get(

                "category"

            ) == category

        ]



        # Moderate-calorie items are easier to combine

        # into reasonable first-plate suggestions.

        category_foods.sort(

            key=lambda food:

            abs(

                food["calories"] - 150

            )

        )



        candidates.extend(

            category_foods[:limit]

        )



    # --------------------------------------------------------

    # REMOVE DUPLICATES

    # --------------------------------------------------------



    unique_candidates = []

    seen = set()



    for food in candidates:



        key = (

            food.get(

                "food_name",

                ""

            ),

            food.get(

                "station",

                ""

            ),

            food.get(

                "portion",

                ""

            ),

            food.get(

                "calories",

                0

            )

        )



        if key in seen:

            continue



        seen.add(key)



        unique_candidates.append(

            food

        )



    return unique_candidates





# ============================================================
# FIND MEAL OPTIONS — SMARTPLATE STATION RULES
# ============================================================

REQUIRED_STATIONS = ("DELICIOUS WITHOUT", "PLANT BASED", "THE SWEET SHOPPE")
OPTIONAL_STATIONS = ("THE SOUP BOWL", "FRESH 52")
NUMBER_OF_OPTIONS = 5
MIN_ITEMS = 3
MAX_ITEMS = 5


def normalize_station(value):
    return " ".join((value or "").upper().replace("/", " ").split())


def station_matches(food, station_name):
    actual = normalize_station(food.get("station", ""))
    wanted = normalize_station(station_name)
    return actual == wanted or wanted in actual


def foods_at_station(menu, station_name):
    foods, seen = [], set()
    for food in menu:
        if not station_matches(food, station_name):
            continue
        try:
            calories = int(float(food.get("calories", 0)))
        except (TypeError, ValueError):
            continue
        if calories <= 0:
            continue
        item = dict(food)
        item["calories"] = calories
        key = (item.get("food_name",""), normalize_station(item.get("station","")),
               item.get("portion",""), calories)
        if key not in seen:
            seen.add(key)
            foods.append(item)
    foods.sort(key=lambda f: (f["calories"], f.get("food_name","")))
    return foods[:10]


def meal_signature(meal):
    return tuple(sorted(
        (f.get("food_name",""), normalize_station(f.get("station","")), f.get("portion",""))
        for f in meal
    ))


def find_meal_options(menu, target_calories):
    """
    Return up to 5 suggestions, each containing 3–5 foods.
    Required: Delicious Without + Plant Based + The Sweet Shoppe.
    Optional: The Soup Bowl + Fresh 52.
    """
    if not menu:
        return []

    station_foods = {
        s: foods_at_station(menu, s)
        for s in REQUIRED_STATIONS + OPTIONAL_STATIONS
    }

    missing = [s for s in REQUIRED_STATIONS if not station_foods[s]]
    if missing:
        print("Missing required station(s): " + ", ".join(missing))
        return []

    options = []
    required_lists = [station_foods[s] for s in REQUIRED_STATIONS]
    soups = station_foods["THE SOUP BOWL"]
    fresh = station_foods["FRESH 52"]

    for required_combo in itertools.product(*required_lists):
        base = list(required_combo)
        meals = [base]
        meals += [base + [x] for x in soups]
        meals += [base + [x] for x in fresh]
        meals += [base + [s, f] for s in soups for f in fresh]

        for meal in meals:
            if not (MIN_ITEMS <= len(meal) <= MAX_ITEMS):
                continue
            total = calculate_total_calories(meal)
            if total <= 0:
                continue
            options.append({
                "meal": tuple(meal),
                "total": total,
                "difference": abs(total - target_calories),
                "variety": get_variety_score(meal),
                "item_count": len(meal),
            })

    options.sort(key=lambda o: (
        o["difference"], -o["variety"], o["item_count"], meal_signature(o["meal"])
    ))

    final_options, used, food_usage = [], set(), {}

    while options and len(final_options) < NUMBER_OF_OPTIONS:
        best_i, best_score = None, None
        for i, option in enumerate(options):
            sig = meal_signature(option["meal"])
            if sig in used:
                continue

            repeat_penalty = sum(
                food_usage.get(
                    (f.get("food_name",""), normalize_station(f.get("station",""))), 0
                )
                for f in option["meal"]
            )

            score = (
                option["difference"] + repeat_penalty * 35,
                -option["variety"],
                option["item_count"],
            )

            if best_score is None or score < best_score:
                best_i, best_score = i, score

        if best_i is None:
            break

        chosen = options.pop(best_i)
        used.add(meal_signature(chosen["meal"]))
        final_options.append((chosen["meal"], chosen["total"]))

        for f in chosen["meal"]:
            key = (f.get("food_name",""), normalize_station(f.get("station","")))
            food_usage[key] = food_usage.get(key, 0) + 1

    return final_options


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":
    menu = load_menu()
    print(f"Loaded {len(menu)} live menu items.")

    for hunger in ["Light", "Moderate", "Very Hungry"]:
        print("\n" + "=" * 60)
        print(f"🍽️ {hunger.upper()}")
        print("=" * 60)

        target = get_target_calories(hunger)
        recommendations = find_meal_options(menu, target)

        if not recommendations:
            print("No valid suggestion. Check the three required stations.")
            continue

        for number, (meal, total) in enumerate(recommendations[:5], 1):
            print(f"\nOPTION {number} — {total} cal")
            for food in meal:
                print(
                    f"  • {food['food_name']} "
                    f"({food.get('station','Unknown Station')})"
                )
