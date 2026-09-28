from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# =========================
# PROJECT PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "Backend" / "database.db"
RULES_PATH = BASE_DIR / "Data" / "fp_growth_rules.json"
FRONTEND_DIR = BASE_DIR / "Frontend"
IMAGES_DIR = BASE_DIR / "images"


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# =========================
# LOAD FP-GROWTH RULES
# =========================

def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================
# FRONTEND
# =========================

@app.route("/")
def home():
    return send_file(FRONTEND_DIR / "index.html")


@app.route("/style.css")
def style():
    return send_file(FRONTEND_DIR / "style.css")


@app.route("/script.js")
def script():
    return send_file(FRONTEND_DIR / "script.js")


# =========================
# PRODUCT IMAGES
# =========================

@app.route("/images/<path:filename>")
def product_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


# =========================
# PRODUCTS API
# =========================

@app.route("/api/products")
def get_products():

    connection = get_db_connection()

    products = connection.execute("""
        SELECT id, name, brand, category, image
        FROM products
        ORDER BY id
    """).fetchall()

    connection.close()

    return jsonify([dict(product) for product in products])


# =========================
# RECOMMENDATION API
# =========================

@app.route("/api/recommend", methods=["POST"])
def recommend():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Invalid request"
        }), 400

    # Accept:
    # {"cart": ["Bread", "Butter"]}
    # OR
    # {"product": "Bread"}

    cart = data.get("cart")

    if cart is None:

        selected_product = data.get("product")

        if not selected_product:
            return jsonify({
                "error": "No product or cart selected"
            }), 400

        cart = [selected_product]

    if not isinstance(cart, list):
        return jsonify({
            "error": "Cart must be a list of products"
        }), 400

    # =========================
    # CLEAN CART
    # =========================

    cleaned_cart = []

    for product in cart:

        if not isinstance(product, str):
            continue

        product = product.strip()

        if product and product not in cleaned_cart:
            cleaned_cart.append(product)

    if not cleaned_cart:
        return jsonify({
            "error": "Cart is empty"
        }), 400

    cart_set = set(cleaned_cart)

    # =========================
    # LOAD RULES
    # =========================

    rules = load_rules()

    matching_recommendations = []

    # =========================
    # FIND MATCHING RULES
    # =========================

    for rule in rules:

        antecedent = set(rule.get("antecedent", []))
        consequent = rule.get("consequent", [])

        if not antecedent:
            continue

        if not antecedent.issubset(cart_set):
            continue

        for item in consequent:

            if item in cart_set:
                continue

            matching_recommendations.append({
                "product": item,
                "support": rule["support"],
                "confidence": rule["confidence"],
                "lift": rule["lift"],
                "matched_antecedent": sorted(antecedent)
            })

    # =========================
    # SORT MATCHING RULES
    # =========================

    matching_recommendations.sort(
        key=lambda x: (
            len(x["matched_antecedent"]),
            x["confidence"],
            x["lift"],
            x["support"]
        ),
        reverse=True
    )

    # =========================
    # RECOMMENDATIONS
    # =========================

    recommendations = []
    seen = set()

    # =========================================================
    # CASE 1: TOOTHPASTE
    #
    # Toothpaste -> Toothbrush + Bath Soap
    # =========================================================

    if "Toothpaste" in cart_set:

        preferred_products = [
            "Toothbrush",
            "Bath Soap"
        ]

        for preferred in preferred_products:

            if preferred in cart_set:
                continue

            if preferred in seen:
                continue

            matching_rule = next(
                (
                    r for r in matching_recommendations
                    if r["product"] == preferred
                ),
                None
            )

            if matching_rule:

                recommendations.append({
                    "product": preferred,
                    "support": matching_rule["support"],
                    "confidence": matching_rule["confidence"],
                    "lift": matching_rule["lift"]
                })

                seen.add(preferred)

    # =========================================================
    # CASE 2: TOOTHBRUSH
    #
    # Toothbrush -> Toothpaste mandatory
    #              + Bath Soap OR Face Wash
    #
    # The second recommendation is allowed even when
    # there is no direct FP-Growth rule for Toothbrush.
    # =========================================================

    elif "Toothbrush" in cart_set:

        # -----------------------------------------
        # Mandatory Toothpaste
        # -----------------------------------------

        if "Toothpaste" not in cart_set:

            toothpaste_rule = next(
                (
                    r for r in matching_recommendations
                    if r["product"] == "Toothpaste"
                ),
                None
            )

            if toothpaste_rule:

                recommendations.append({
                    "product": "Toothpaste",
                    "support": toothpaste_rule["support"],
                    "confidence": toothpaste_rule["confidence"],
                    "lift": toothpaste_rule["lift"]
                })

            else:

                # Fallback values from the existing
                # Toothbrush -> Toothpaste rule
                recommendations.append({
                    "product": "Toothpaste",
                    "support": 0.0239520958,
                    "confidence": 0.6153846154,
                    "lift": 13.1194762684
                })

            seen.add("Toothpaste")

        # -----------------------------------------
        # Second recommendation:
        # Bath Soap OR Face Wash
        # -----------------------------------------

        second_choice = None

        # First try Bath Soap from existing rules
        for r in matching_recommendations:

            if (
                r["product"] == "Bath Soap"
                and "Bath Soap" not in cart_set
            ):
                second_choice = r
                break

        # If Bath Soap isn't available from FP-Growth,
        # try Face Wash.
        if second_choice is None:

            for r in matching_recommendations:

                if (
                    r["product"] == "Face Wash"
                    and "Face Wash" not in cart_set
                ):
                    second_choice = r
                    break

        # -----------------------------------------
        # Database products exist, so if FP-Growth
        # has no rule, use a neutral fallback.
        # -----------------------------------------

        if second_choice:

            recommendations.append({
                "product": second_choice["product"],
                "support": second_choice["support"],
                "confidence": second_choice["confidence"],
                "lift": second_choice["lift"]
            })

            seen.add(second_choice["product"])

        else:

            # Prefer Bath Soap as fallback
            if "Bath Soap" not in cart_set:

                recommendations.append({
                    "product": "Bath Soap",
                    "support": 0.0,
                    "confidence": 0.0,
                    "lift": 0.0
                })

                seen.add("Bath Soap")

            elif "Face Wash" not in cart_set:

                recommendations.append({
                    "product": "Face Wash",
                    "support": 0.0,
                    "confidence": 0.0,
                    "lift": 0.0
                })

                seen.add("Face Wash")

    # =========================================================
    # CASE 3: ALL OTHER PRODUCTS
    #
    # Use the normal FP-Growth recommendation engine.
    # =========================================================

    else:

        for recommendation in matching_recommendations:

            product = recommendation["product"]

            if product in cart_set:
                continue

            if product in seen:
                continue

            recommendations.append({
                "product": product,
                "support": recommendation["support"],
                "confidence": recommendation["confidence"],
                "lift": recommendation["lift"]
            })

            seen.add(product)

            if len(recommendations) == 2:
                break

    # =========================
    # MAXIMUM 2 RECOMMENDATIONS
    # =========================

    recommendations = recommendations[:2]

    # =========================
    # RETURN RESPONSE
    # =========================

    return jsonify({
        "cart": cleaned_cart,
        "recommendations": recommendations
    })


# =========================
# RUN FLASK SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )