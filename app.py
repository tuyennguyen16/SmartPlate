import csv
import itertools

menu = []

with open("menu.csv", "r") as file:
    reader = csv.DictReader(file)

    for food in reader:
        food["calories"] = int(food["calories"])
        menu.append(food)

def calculate_total_calories(meal):
    total = 0

    for food in meal:
        total = total + food["calories"]

    return total
def is_valid_meal(meal):
    
    categories = []
    for food in meal:
        categories.append(food["category"])

    has_protein = "Protein" in categories
    has_base = "Grain" in categories or "Side" in categories

    return has_protein and has_base
def get_target_calories(hunger_level):
    if hunger_level == "Light":
        return 500

    elif hunger_level == "Moderate":
        return 600

    elif hunger_level == "Very Hungry":
        return 700

    else:
        return 600
def find_meal_options(menu, target_calories, tolerance=50):
    options = []

    for size in range(3, 6):

        combinations = itertools.combinations(menu, size)

        for meal in combinations:
            total = calculate_total_calories(meal)

            if abs(total - target_calories) <= tolerance and is_valid_meal(meal):
                options.append((meal, total))
    options.sort(key=lambda option: abs(option[1] - target_calories))
    return options

print("\nHow hungry are you?")

print("1. Light")
print("2. Moderate")
print("3. Very Hungry")

choice = input("\nChoose 1, 2, or 3: ")
if choice == "1":
    hunger_level = "Light"

elif choice == "2":
    hunger_level = "Moderate"

elif choice == "3":
    hunger_level = "Very Hungry"

else:
    hunger_level = "Moderate"

target = get_target_calories(hunger_level)
options = find_meal_options(menu, target)

print("SMARTPLATE MEAL OPTIONS")
print("-----------------------")
print("Hunger Level:", hunger_level)
print("Meal Size Target:", target, "calories")

for number, option in enumerate(options[:5], start=1):

    meal = option[0]
    total = option[1]

    print("\nOption", number)

    for food in meal:
        print("-", food["food_name"], food["calories"], "cal")

    print("Total:", total, "calories")

