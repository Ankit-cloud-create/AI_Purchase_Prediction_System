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

    selected_product = data.get("product")

    if not selected_product:
        return jsonify({
            "error": "No product selected"
        }), 400

    # Load the 1,200 FP-Growth rules
    rules = load_rules()

    matching_rules = []

    # Find rules where the antecedent
    # is exactly the selected product
    for rule in rules:

        antecedent = set(rule["antecedent"])
        consequent = rule["consequent"]

        if antecedent == {selected_product}:

            for item in consequent:

                matching_rules.append({
                    "product": item,
                    "support": rule["support"],
                    "confidence": rule["confidence"],
                    "lift": rule["lift"]
                })


    # Sort recommendations by:
    # 1. Confidence
    # 2. Lift
    # 3. Support
    matching_rules.sort(
        key=lambda x: (
            x["confidence"],
            x["lift"],
            x["support"]
        ),
        reverse=True
    )


    # Return maximum 2 recommendations
    recommendations = []
    seen = set()

    for recommendation in matching_rules:

        product = recommendation["product"]

        if product not in seen:

            recommendations.append(recommendation)
            seen.add(product)

        if len(recommendations) == 2:
            break


    return jsonify({
        "selected_product": selected_product,
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