"""SmartPlate recommendation engine — finalist demo version.

Reads current_menu.csv produced by menu_scraper.py.
Returns up to five meals as (tuple_of_food_dicts, total_calories).
Hunger calorie targets are prototype heuristics, not dietary advice.
"""

import csv
import heapq
import itertools
import re

MENU_FILE = "current_menu.csv"

REQUIRED_STATIONS = (
    "DELICIOUS WITHOUT",
    "COMFORT/HOMESTYLE",
    "THE SWEET SHOPPE",
)

OPTIONAL_STATIONS = (
    "THE SOUP BOWL",
    "FRESH 52",
    "PIZZA, FLATBREAD",
    "PLANT BASED",
    "FLAME",
    "BOK CHOY/MONGOLIAN",
    "DELI CRAFTED",
    "CUCINA",
)

BREAKFAST_STATIONS = ("THE SOUP BOWL", "PIZZA/FLATBREAD", "FRESH 52")

NUMBER_OF_OPTIONS = 5
MIN_ITEMS = 3
MAX_ITEMS = 5
MAX_FOODS_PER_STATION = 10
MAX_OPTIONAL_FOODS_PER_STATION = 4
CANDIDATE_SHORTLIST = 1500


def load_menu(filename=MENU_FILE):
    """Load and normalize the CSV schema produced by menu_scraper.py."""
    menu = []
    try:
        with open(filename, "r", encoding="utf-8-sig", newline="") as file:
            for food in csv.DictReader(file):
                try:
                    food["calories"] = int(float(food.get("calories", 0)))
                except (TypeError, ValueError):
                    food["calories"] = 0
                for field, default in (
                    ("station", "Unknown Station"),
                    ("category", "Other"),
                    ("portion", ""),
                    ("meal_period", ""),
                    ("date", ""),
                ):
                    food.setdefault(field, default)
                menu.append(food)
    except FileNotFoundError:
        print(f"⚠️ {filename} not found. Run menu_scraper.py first.")
    return menu


def calculate_total_calories(meal):
    return sum(int(food.get("calories", 0) or 0) for food in meal)


def get_target_calories(hunger_level):
    """Internal demo targets, not medical or nutritional recommendations."""
    return {"Light": 600, "Moderate": 800, "Very Hungry": 1200}.get(hunger_level, 600)


def get_variety_score(meal):
    excluded = {"Other", "Topping", "Topping / Condiment", "Dessert"}
    return len({f.get("category", "Other") for f in meal if f.get("category", "Other") not in excluded})


def get_station_score(meal):
    return len({normalize_station(f.get("station", "")) for f in meal})


def normalize_station(value):
    """Make 'COMFORT/ HOMESTYLE' and 'COMFORT/HOMESTYLE' equivalent."""
    return " ".join(re.findall(r"[A-Z0-9]+", (value or "").upper()))


def station_matches(food, station_name):
    actual = normalize_station(food.get("station", ""))
    wanted = normalize_station(station_name)
    return bool(actual and wanted and (actual == wanted or actual.startswith(wanted + " ")))


def foods_at_station(menu, station_name):
    foods, seen = [], set()
    for food in menu:
        if not station_matches(food, station_name):
            continue
        try:
            calories = int(float(food.get("calories", 0)))
        except (TypeError, ValueError):
            continue
        if calories <= 0 or not str(food.get("food_name", "")).strip():
            continue
        item = dict(food)
        item["calories"] = calories
        key = (item["food_name"].strip().lower(), normalize_station(item.get("station", "")),
               str(item.get("portion", "")).strip(), calories)
        if key not in seen:
            seen.add(key)
            foods.append(item)
    foods.sort(key=lambda f: (f["calories"], f.get("food_name", "")))
    return foods[:MAX_FOODS_PER_STATION]


def meal_signature(meal):
    return tuple(sorted((f.get("food_name", ""), normalize_station(f.get("station", "")),
                         str(f.get("portion", ""))) for f in meal))


def build_candidate_pool(menu):
    """Compatibility helper: unique positive-calorie foods for other app imports."""
    candidates, seen = [], set()
    for food in menu:
        try:
            calories = int(float(food.get("calories", 0)))
        except (TypeError, ValueError):
            continue
        if calories <= 0:
            continue
        key = (food.get("food_name"), food.get("station"), food.get("portion"), calories)
        if key not in seen:
            seen.add(key)
            candidates.append(food)
    return candidates


def find_meal_options(menu, target_calories):
    """Suggest up to five unique 3–5-item plates.

    Lunch/dinner plates use three required stations plus up to two optional
    stations. Breakfast uses Soup Bowl, Pizza/Flatbread and Fresh 52.
    Ranking favors calorie-target proximity, category variety, and different
    foods across the five suggestions. All optional stations are eligible.
    """
    if not menu:
        return []

    # The scraper supplies a single current meal period. Breakfast has
    # different stations, so do not apply lunch/dinner requirements to it.
    meal_periods = {str(f.get("meal_period", "")).strip().lower()
                    for f in menu if str(f.get("meal_period", "")).strip()}
    is_breakfast = meal_periods == {"breakfast"}

    if is_breakfast:
        # For breakfast, use the three actual breakfast stations as the base.
        # If a station has no valid items, use the available stations instead.
        active_required = [s for s in BREAKFAST_STATIONS if foods_at_station(menu, s)]
        if not active_required:
            print("No valid breakfast foods available.")
            return []
        active_optional = []
    else:
        active_required = list(REQUIRED_STATIONS)
        active_optional = list(OPTIONAL_STATIONS)

    station_foods = {
        station: foods_at_station(menu, station)
        for station in active_required + active_optional
    }
    missing = [s for s in active_required if not station_foods[s]]
    if missing:
        print("Missing required station(s): " + ", ".join(missing))
        return []

    required_lists = [station_foods[s] for s in active_required]
    optional_groups = [station_foods[s][:MAX_OPTIONAL_FOODS_PER_STATION]
                       for s in active_optional if station_foods[s]]

    # Breakfast: select one from each available station; add extra distinct
    # foods when fewer than three stations are available.
    if is_breakfast:
        def breakfast_meals():
            for combo in itertools.product(*required_lists):
                base = tuple(combo)
                if len(base) >= MIN_ITEMS:
                    yield base
                if len(base) < MIN_ITEMS:
                    extras = [f for group in required_lists for f in group
                              if f not in base]
                    for addition in itertools.combinations(extras, MIN_ITEMS - len(base)):
                        meal = base + addition
                        if len(meal_signature(meal)) == len(set(meal_signature(meal))):
                            yield meal
        candidate_iter = breakfast_meals()
    else:
        candidate_iter = (
            meal
            for required in itertools.product(*required_lists)
            for meal in itertools.chain(
                (tuple(required),),
                (tuple(required) + (food,) for group in optional_groups for food in group),
                (tuple(required) + (a, b)
                 for group_a, group_b in itertools.combinations(optional_groups, 2)
                 for a in group_a for b in group_b),
            )
        )

    # Keep only the strongest candidates rather than materializing hundreds
    # of thousands of combinations. This makes demo reruns more predictable.
    candidate_iter = (
        meal
        for required in itertools.product(*required_lists)
        for meal in itertools.chain(
            (tuple(required),),
            (tuple(required) + (food,) for group in optional_groups for food in group),
            (tuple(required) + (a, b)
             for group_a, group_b in itertools.combinations(optional_groups, 2)
             for a in group_a for b in group_b),
        )
    )

    def base_score(meal):
        total = calculate_total_calories(meal)
        return (abs(total - target_calories), -get_variety_score(meal), len(meal), meal_signature(meal))

    candidates = heapq.nsmallest(CANDIDATE_SHORTLIST, candidate_iter, key=base_score)
    final_options, used, food_usage = [], set(), {}

    while candidates and len(final_options) < NUMBER_OF_OPTIONS:
        best_index, best_score = None, None
        for i, meal in enumerate(candidates):
            signature = meal_signature(meal)
            if signature in used:
                continue
            repeat_penalty = sum(food_usage.get(
                (f.get("food_name", ""), normalize_station(f.get("station", ""))), 0
            ) for f in meal)
            score = (
                abs(calculate_total_calories(meal) - target_calories) + 35 * repeat_penalty,
                -get_variety_score(meal),
                len(meal),
                signature,
            )
            if best_score is None or score < best_score:
                best_index, best_score = i, score

        if best_index is None:
            break
        chosen = candidates.pop(best_index)
        used.add(meal_signature(chosen))
        final_options.append((chosen, calculate_total_calories(chosen)))
        for food in chosen:
            key = (food.get("food_name", ""), normalize_station(food.get("station", "")))
            food_usage[key] = food_usage.get(key, 0) + 1

    return final_options


if __name__ == "__main__":
    menu = load_menu()
    print(f"Loaded {len(menu)} menu items.")
    print("Stations:", sorted({f.get("station", "") for f in menu}))
    for hunger in ("Light", "Moderate", "Very Hungry"):
        print(f"\n{'=' * 55}\n{hunger.upper()}\n{'=' * 55}")
        options = find_meal_options(menu, get_target_calories(hunger))
        if not options:
            print("No suggestions. Check station names and calories in current_menu.csv.")
        for i, (meal, total) in enumerate(options, 1):
            print(f"OPTION {i}: {total} calories")
            for food in meal:
                print(f"  - {food['food_name']} [{food.get('station', '')}]")
