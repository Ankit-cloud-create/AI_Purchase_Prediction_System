import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

RULES_PATH = (
    BASE_DIR
    / "Data"
    / "Model_Results"
    / "fp_growth_rules_1002.json"
)


with open(RULES_PATH, "r", encoding="utf-8") as file:
    rules = json.load(file)


print("=" * 70)
print("FP-GROWTH RULE INSPECTION")
print("=" * 70)

print(f"Total rules: {len(rules)}")


# ============================================================
# RULE SIZE SUMMARY
# ============================================================

single_antecedent = 0
multi_antecedent = 0
single_consequent = 0
multi_consequent = 0


for rule in rules:

    if len(rule["antecedent"]) == 1:
        single_antecedent += 1
    else:
        multi_antecedent += 1

    if len(rule["consequent"]) == 1:
        single_consequent += 1
    else:
        multi_consequent += 1


print("\nRule structure:")
print(f"Single-item antecedents : {single_antecedent}")
print(f"Multi-item antecedents  : {multi_antecedent}")
print(f"Single-item consequents : {single_consequent}")
print(f"Multi-item consequents  : {multi_consequent}")


# ============================================================
# SINGLE PRODUCT RECOMMENDATIONS
# ============================================================

products_to_check = [
    "Toothpaste",
    "Toothbrush",
    "Garbage Bags",
    "Milk",
    "Bread",
    "Cooking Oil",
    "Rice",
    "Shampoo",
]


print("\n" + "=" * 70)
print("SINGLE-PRODUCT RULES")
print("=" * 70)


for product in products_to_check:

    matching = [
        rule
        for rule in rules
        if rule["antecedent"] == [product]
    ]

    print(f"\n{product}")
    print("-" * len(product))

    if not matching:
        print("No qualifying single-product rule.")
        continue

    for rule in matching[:10]:

        print(
            f"  -> {', '.join(rule['consequent'])}"
            f" | support={rule['support']:.4f}"
            f" | confidence={rule['confidence']:.4f}"
            f" | lift={rule['lift']:.4f}"
        )


# ============================================================
# EXAMPLES OF MULTI-ITEM RULES
# ============================================================

print("\n" + "=" * 70)
print("MULTI-ITEM RULE EXAMPLES")
print("=" * 70)


multi_rules = [
    rule
    for rule in rules
    if len(rule["antecedent"]) >= 2
]


for rule in multi_rules[:10]:

    print(
        f"{' + '.join(rule['antecedent'])}"
        f" -> "
        f"{' + '.join(rule['consequent'])}"
        f" | support={rule['support']:.4f}"
        f" | confidence={rule['confidence']:.4f}"
        f" | lift={rule['lift']:.4f}"
    )


print("\n" + "=" * 70)
print("INSPECTION COMPLETED")
print("=" * 70)