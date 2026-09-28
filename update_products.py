import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

PRODUCTS_PATH = BASE_DIR / "Data" / "products.json"


# ============================================================
# LOAD EXISTING PRODUCTS
# ============================================================

with open(PRODUCTS_PATH, "r", encoding="utf-8") as file:
    products = json.load(file)


# ============================================================
# VERIFY ORIGINAL DATA
# ============================================================

if len(products) != 65:
    raise ValueError(
        f"Expected the original 65 products, "
        f"but found {len(products)}."
    )


existing_ids = {product["id"] for product in products}
existing_names = {product["name"] for product in products}


# ============================================================
# NEW PRODUCTS: IDs 66-85
# ============================================================

new_products = [
    {
        "id": 66,
        "name": "Ghee",
        "brand": "Amul Pure Ghee",
        "category": "Dairy",
        "image": "ghee.jpg"
    },
    {
        "id": 67,
        "name": "Lassi",
        "brand": "Amul Lassi",
        "category": "Dairy",
        "image": "lassi.jpg"
    },
    {
        "id": 68,
        "name": "Peanut Butter",
        "brand": "Pintola All Natural Peanut Butter",
        "category": "Breakfast",
        "image": "peanut_butter.jpg"
    },
    {
        "id": 69,
        "name": "Granola",
        "brand": "Yoga Bar Granola",
        "category": "Breakfast",
        "image": "granola.jpg"
    },
    {
        "id": 70,
        "name": "Fruit Juice",
        "brand": "Real Fruit Power",
        "category": "Beverages",
        "image": "fruit_juice.jpg"
    },
    {
        "id": 71,
        "name": "Hot Chocolate",
        "brand": "Cadbury Hot Chocolate",
        "category": "Beverages",
        "image": "hot_chocolate.jpg"
    },
    {
        "id": 72,
        "name": "Poha",
        "brand": "Tata Sampann Poha",
        "category": "Breakfast",
        "image": "poha.jpg"
    },
    {
        "id": 73,
        "name": "Besan",
        "brand": "Fortune Besan",
        "category": "Staples",
        "image": "besan.jpg"
    },
    {
        "id": 74,
        "name": "Urad Dal",
        "brand": "Tata Sampann Urad Dal",
        "category": "Pulses",
        "image": "urad_dal.jpg"
    },
    {
        "id": 75,
        "name": "Kabuli Chana",
        "brand": "Tata Sampann Kabuli Chana",
        "category": "Pulses",
        "image": "kabuli_chana.jpg"
    },
    {
        "id": 76,
        "name": "Black Pepper",
        "brand": "Everest Black Pepper",
        "category": "Spices",
        "image": "black_pepper.jpg"
    },
    {
        "id": 77,
        "name": "Chaat Masala",
        "brand": "Everest Chaat Masala",
        "category": "Spices",
        "image": "chaat_masala.jpg"
    },
    {
        "id": 78,
        "name": "Namkeen",
        "brand": "Haldiram's Aloo Bhujia",
        "category": "Snacks",
        "image": "namkeen.jpg"
    },
    {
        "id": 79,
        "name": "Cookies",
        "brand": "Britannia NutriChoice Cookies",
        "category": "Snacks",
        "image": "cookies.jpg"
    },
    {
        "id": 80,
        "name": "Hand Sanitizer",
        "brand": "Dettol Hand Sanitizer",
        "category": "Personal Care",
        "image": "hand_sanitizer.jpg"
    },
    {
        "id": 81,
        "name": "Body Lotion",
        "brand": "Nivea Body Lotion",
        "category": "Personal Care",
        "image": "body_lotion.jpg"
    },
    {
        "id": 82,
        "name": "Laundry Liquid",
        "brand": "Surf Excel Matic Liquid",
        "category": "Household",
        "image": "laundry_liquid.jpg"
    },
    {
        "id": 83,
        "name": "Scrub Pad",
        "brand": "Scotch-Brite Scrub Pad",
        "category": "Household",
        "image": "scrub_pad.jpg"
    },
    {
        "id": 84,
        "name": "Toor Dal Split",
        "brand": "Tata Sampann Toor Dal Split",
        "category": "Pulses",
        "image": "toor_dal_split.jpg"
    },
    {
        "id": 85,
        "name": "Mixed Nuts",
        "brand": "Happilo Premium Mixed Nuts",
        "category": "Dry Fruits",
        "image": "mixed_nuts.jpg"
    }
]


# ============================================================
# VALIDATE NEW PRODUCTS
# ============================================================

if len(new_products) != 20:
    raise ValueError(
        f"Expected 20 new products, "
        f"but found {len(new_products)}."
    )


for product in new_products:

    if product["id"] in existing_ids:
        raise ValueError(
            f"Product ID already exists: {product['id']}"
        )

    if product["name"] in existing_names:
        raise ValueError(
            f"Product name already exists: {product['name']}"
        )


new_ids = [product["id"] for product in new_products]

if new_ids != list(range(66, 86)):
    raise ValueError(
        "New product IDs must be exactly 66 through 85."
    )


# ============================================================
# APPEND NEW PRODUCTS
# ============================================================

updated_products = products + new_products


# ============================================================
# FINAL VALIDATION
# ============================================================

if len(updated_products) != 85:
    raise ValueError(
        f"Expected 85 products after update, "
        f"but found {len(updated_products)}."
    )


all_ids = [product["id"] for product in updated_products]

if all_ids != list(range(1, 86)):
    raise ValueError(
        "Product IDs are not sequential from 1 through 85."
    )


# ============================================================
# SAVE
# ============================================================

with open(PRODUCTS_PATH, "w", encoding="utf-8") as file:
    json.dump(
        updated_products,
        file,
        indent=2,
        ensure_ascii=False
    )


print("=" * 60)
print("PRODUCT DATA UPDATED")
print("=" * 60)
print(f"Original products : 65")
print(f"New products      : 20")
print(f"Total products    : {len(updated_products)}")
print("IDs               : 1-85")
print("=" * 60)