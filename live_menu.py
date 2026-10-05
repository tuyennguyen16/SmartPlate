import requests
from datetime import datetime
from zoneinfo import ZoneInfo


# -----------------------------------------
# SMARTPLATE LIVE MENU
# -----------------------------------------

BASE_URL = "https://apiv4.dineoncampus.com"

FIU_SLUG = "FIU"
LOCATION_NAME = "8th Street Campus Kitchen"


def get_fiu_time():
    """
    Returns the current FIU local date and time.
    """
    return datetime.now(
        ZoneInfo("America/New_York")
    )


def categorize_food(food_name):
    """
    Temporary SmartPlate categorization system.

    DineOnCampus categories/stations are not necessarily
    the same categories needed by our recommendation engine.
    """

    name = food_name.lower()

    protein_words = [
        "egg",
        "sausage",
        "chicken",
        "turkey",
        "beef",
        "pork",
        "fish",
        "salmon",
        "tofu",
        "frittata",
        "omelet"
    ]

    grain_words = [
        "pancake",
        "waffle",
        "grits",
        "rice",
        "bread",
        "toast",
        "pasta",
        "noodle",
        "cereal",
        "oatmeal"
    ]

    side_words = [
        "potato",
        "hash brown",
        "puff",
        "vegetable",
        "veggie",
        "fries"
    ]

    fruit_words = [
        "fruit",
        "apple",
        "banana",
        "orange",
        "berry",
        "berries",
        "melon"
    ]

    dairy_words = [
        "yogurt",
        "milk"
    ]

    topping_words = [
        "cheese",
        "sauce",
        "syrup",
        "dressing"
    ]

    if any(word in name for word in protein_words):
        return "Protein"

    if any(word in name for word in grain_words):
        return "Grain"

    if any(word in name for word in side_words):
        return "Side"

    if any(word in name for word in fruit_words):
        return "Fruit"

    if any(word in name for word in dairy_words):
        return "Dairy"

    if any(word in name for word in topping_words):
        return "Topping"

    return "Other"


def determine_meal_period(current_time=None):
    """
    TEMPORARY time rules for testing.

    IMPORTANT:
    These are NOT claimed to be FIU's official serving hours.
    Later we will replace them with actual meal-period data
    if DineOnCampus exposes it.
    """

    if current_time is None:
        current_time = get_fiu_time()

    hour = current_time.hour

    if 7 <= hour < 11:
        return "Breakfast"

    elif 11 <= hour < 16:
        return "Lunch"

    elif 16 <= hour < 22:
        return "Dinner"

    return None


def test_api():
    """
    First diagnostic test.

    We are NOT connecting this to Streamlit yet.
    This checks whether Python can successfully reach
    the DineOnCampus API.
    """

    print("=" * 55)
    print("🥗 SMARTPLATE LIVE MENU TEST")
    print("=" * 55)

    now = get_fiu_time()

    print()
    print("FIU local time:")
    print(now.strftime("%Y-%m-%d %I:%M %p"))

    meal_period = determine_meal_period(now)

    print()
    print("Detected meal period:")
    print(meal_period)

    print()
    print("Testing DineOnCampus API...")

    try:
        response = requests.get(
            BASE_URL,
            timeout=10
        )

        print("Status code:", response.status_code)
        print("Final URL:", response.url)

        if response.status_code < 500:
            print()
            print("✅ DineOnCampus server reached.")
        else:
            print()
            print("⚠️ Server responded, but returned an error.")

    except requests.RequestException as error:

        print()
        print("❌ Could not reach DineOnCampus.")
        print(error)


if __name__ == "__main__":
    test_api()