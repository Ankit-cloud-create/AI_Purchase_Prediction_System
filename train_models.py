import json
import math
from pathlib import Path
from itertools import combinations

import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "Data" / "Prediction_System_1000_85_Natural.xlsx"
OUTPUT_DIR = BASE_DIR / "Data" / "Model_Results"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

MIN_SUPPORT = 0.02
MIN_CONFIDENCE = 0.50

EXPECTED_TRANSACTIONS = 1002
EXPECTED_PRODUCTS = 85


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_transaction_details(value):
    """
    Convert the Transaction_Details cell into a list of product names.

    Expected format:
    Product A, Product B, Product C
    """

    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def clean_itemset(itemset):
    """
    Convert an mlxtend frozenset into a sorted list.
    """
    return sorted(list(itemset))


def save_json(data, path):
    """
    Save Python data as formatted JSON.
    """
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("AI PURCHASE PREDICTION SYSTEM - MODEL TRAINING")
print("=" * 70)

print("\n[1/8] Loading dataset...")

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATASET_PATH}"
    )

transactions_df = pd.read_excel(
    DATASET_PATH,
    sheet_name="Transactions"
)

print(f"Dataset loaded: {DATASET_PATH.name}")


# ============================================================
# VERIFY DATASET STRUCTURE
# ============================================================

print("\n[2/8] Verifying dataset...")

required_columns = {
    "Transaction_ID",
    "Transaction_Date",
    "Basket_Size",
    "Transaction_Details"
}

missing_columns = required_columns - set(transactions_df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {sorted(missing_columns)}"
    )


transaction_count = len(transactions_df)

if transaction_count != EXPECTED_TRANSACTIONS:
    raise ValueError(
        f"Expected {EXPECTED_TRANSACTIONS} transactions, "
        f"but found {transaction_count}."
    )


transactions = [
    parse_transaction_details(value)
    for value in transactions_df["Transaction_Details"]
]


# Remove empty transactions
transactions = [
    basket for basket in transactions
    if basket
]


# Check basket count again
if len(transactions) != EXPECTED_TRANSACTIONS:
    raise ValueError(
        f"Expected {EXPECTED_TRANSACTIONS} non-empty transactions, "
        f"but found {len(transactions)}."
    )


# Check duplicate products inside a basket
for index, basket in enumerate(transactions, start=1):

    if len(basket) != len(set(basket)):
        raise ValueError(
            f"Duplicate product found inside transaction {index}: {basket}"
        )


# Collect all products
all_products = sorted(
    {
        product
        for basket in transactions
        for product in basket
    }
)


product_count = len(all_products)

if product_count != EXPECTED_PRODUCTS:
    raise ValueError(
        f"Expected {EXPECTED_PRODUCTS} unique products, "
        f"but found {product_count}."
    )


print(f"Transactions verified: {transaction_count}")
print(f"Unique products verified: {product_count}")

basket_sizes = [len(basket) for basket in transactions]

print(
    f"Basket size range: "
    f"{min(basket_sizes)} - {max(basket_sizes)}"
)

if min(basket_sizes) < 3 or max(basket_sizes) > 7:
    raise ValueError(
        "Basket size validation failed. "
        "Expected every basket to contain 3-7 products."
    )


# ============================================================
# CHECK TRANSACTION UNIQUENESS
# ============================================================

transaction_signatures = {
    tuple(sorted(basket))
    for basket in transactions
}

if len(transaction_signatures) != EXPECTED_TRANSACTIONS:
    raise ValueError(
        "Duplicate transaction combinations detected."
    )

print("Transaction uniqueness verified.")


# ============================================================
# ONE-HOT ENCODING
# ============================================================

print("\n[3/8] Encoding transactions...")

encoder = TransactionEncoder()

encoded_array = encoder.fit(transactions).transform(transactions)

encoded_df = pd.DataFrame(
    encoded_array,
    columns=encoder.columns_
)

print(
    f"Encoded transaction matrix: "
    f"{encoded_df.shape[0]} rows × {encoded_df.shape[1]} products"
)


# ============================================================
# SUPPORT COUNT
# ============================================================

minimum_support_count = math.ceil(
    EXPECTED_TRANSACTIONS * MIN_SUPPORT
)

print(
    f"Minimum support: {MIN_SUPPORT:.2f} "
    f"({MIN_SUPPORT * 100:.0f}%)"
)

print(
    f"Minimum support count: "
    f"{minimum_support_count} transactions"
)

print(
    f"Minimum confidence: "
    f"{MIN_CONFIDENCE:.2f} "
    f"({MIN_CONFIDENCE * 100:.0f}%)"
)


# ============================================================
# APRIORI
# ============================================================

print("\n[4/8] Running Apriori...")

apriori_itemsets = apriori(
    encoded_df,
    min_support=MIN_SUPPORT,
    use_colnames=True
)

print(
    f"Apriori frequent itemsets: "
    f"{len(apriori_itemsets)}"
)

if len(apriori_itemsets) > 0:

    apriori_rules = association_rules(
        apriori_itemsets,
        metric="confidence",
        min_threshold=MIN_CONFIDENCE
    )

else:

    apriori_rules = pd.DataFrame()


print(
    f"Apriori association rules: "
    f"{len(apriori_rules)}"
)


# Save Apriori frequent itemsets
if len(apriori_itemsets) > 0:

    apriori_output = apriori_itemsets.copy()

    apriori_output["itemsets"] = apriori_output[
        "itemsets"
    ].apply(clean_itemset)

    apriori_output["itemsets"] = apriori_output[
        "itemsets"
    ].apply(lambda x: ", ".join(x))

    apriori_output.to_excel(
        OUTPUT_DIR / "apriori_frequent_itemsets.xlsx",
        index=False
    )


# Save Apriori rules
if len(apriori_rules) > 0:

    apriori_rules_output = apriori_rules.copy()

    apriori_rules_output["antecedents"] = apriori_rules_output[
        "antecedents"
    ].apply(clean_itemset)

    apriori_rules_output["consequents"] = apriori_rules_output[
        "consequents"
    ].apply(clean_itemset)

    apriori_rules_output["antecedents"] = apriori_rules_output[
        "antecedents"
    ].apply(lambda x: ", ".join(x))

    apriori_rules_output["consequents"] = apriori_rules_output[
        "consequents"
    ].apply(lambda x: ", ".join(x))

    apriori_rules_output.to_excel(
        OUTPUT_DIR / "apriori_rules.xlsx",
        index=False
    )


# ============================================================
# FP-GROWTH
# ============================================================

print("\n[5/8] Running FP-Growth...")

fpgrowth_itemsets = fpgrowth(
    encoded_df,
    min_support=MIN_SUPPORT,
    use_colnames=True
)

print(
    f"FP-Growth frequent itemsets: "
    f"{len(fpgrowth_itemsets)}"
)

if len(fpgrowth_itemsets) > 0:

    fpgrowth_rules = association_rules(
        fpgrowth_itemsets,
        metric="confidence",
        min_threshold=MIN_CONFIDENCE
    )

else:

    fpgrowth_rules = pd.DataFrame()


print(
    f"FP-Growth association rules: "
    f"{len(fpgrowth_rules)}"
)


# Save FP-Growth frequent itemsets
if len(fpgrowth_itemsets) > 0:

    fpgrowth_output = fpgrowth_itemsets.copy()

    fpgrowth_output["itemsets"] = fpgrowth_output[
        "itemsets"
    ].apply(clean_itemset)

    fpgrowth_output["itemsets"] = fpgrowth_output[
        "itemsets"
    ].apply(lambda x: ", ".join(x))

    fpgrowth_output.to_excel(
        OUTPUT_DIR / "fpgrowth_frequent_itemsets.xlsx",
        index=False
    )


# Save FP-Growth rules
if len(fpgrowth_rules) > 0:

    fpgrowth_rules_output = fpgrowth_rules.copy()

    fpgrowth_rules_output["antecedents"] = fpgrowth_rules_output[
        "antecedents"
    ].apply(clean_itemset)

    fpgrowth_rules_output["consequents"] = fpgrowth_rules_output[
        "consequents"
    ].apply(clean_itemset)

    fpgrowth_rules_output["antecedents"] = fpgrowth_rules_output[
        "antecedents"
    ].apply(lambda x: ", ".join(x))

    fpgrowth_rules_output["consequents"] = fpgrowth_rules_output[
        "consequents"
    ].apply(lambda x: ", ".join(x))

    fpgrowth_rules_output.to_excel(
        OUTPUT_DIR / "fpgrowth_rules.xlsx",
        index=False
    )


# ============================================================
# ECLAT
# ============================================================

print("\n[6/8] Running ECLAT...")

# ------------------------------------------------------------
# Build vertical transaction-ID representation
# ------------------------------------------------------------

vertical_data = {}

for transaction_id, basket in enumerate(transactions):

    for item in basket:

        if item not in vertical_data:
            vertical_data[item] = set()

        vertical_data[item].add(transaction_id)


# ------------------------------------------------------------
# Recursive ECLAT
# ------------------------------------------------------------

eclat_itemsets = []


def eclat_recursive(prefix, items):

    while items:

        item, item_transactions = items.pop()

        new_itemset = prefix + [item]

        support_count = len(item_transactions)

        if support_count >= minimum_support_count:

            support = support_count / EXPECTED_TRANSACTIONS

            eclat_itemsets.append(
                {
                    "support": support,
                    "itemsets": sorted(new_itemset)
                }
            )

            suffix = []

            for other_item, other_transactions in items:

                intersection = (
                    item_transactions &
                    other_transactions
                )

                if len(intersection) >= minimum_support_count:

                    suffix.append(
                        (
                            other_item,
                            intersection
                        )
                    )

            eclat_recursive(
                new_itemset,
                suffix
            )


initial_items = [
    (item, transaction_ids)
    for item, transaction_ids in vertical_data.items()
    if len(transaction_ids) >= minimum_support_count
]

initial_items.sort(key=lambda x: x[0])

eclat_recursive([], initial_items)


# Remove duplicate itemsets
unique_eclat = {}

for itemset in eclat_itemsets:

    key = tuple(itemset["itemsets"])

    unique_eclat[key] = itemset["support"]


eclat_itemsets = [
    {
        "support": support,
        "itemsets": list(itemset)
    }
    for itemset, support in unique_eclat.items()
]

eclat_itemsets.sort(
    key=lambda x: (
        len(x["itemsets"]),
        x["itemsets"]
    )
)

print(
    f"ECLAT frequent itemsets: "
    f"{len(eclat_itemsets)}"
)


# ------------------------------------------------------------
# Generate ECLAT association rules
# ------------------------------------------------------------

support_lookup = {
    tuple(sorted(itemset["itemsets"])): itemset["support"]
    for itemset in eclat_itemsets
}

eclat_rules = []


for itemset_data in eclat_itemsets:

    itemset = itemset_data["itemsets"]

    if len(itemset) < 2:
        continue

    itemset_tuple = tuple(sorted(itemset))

    full_support = support_lookup[itemset_tuple]

    # Generate every non-empty proper subset
    for size in range(1, len(itemset)):

        for antecedent_tuple in combinations(itemset, size):

            antecedent = tuple(sorted(antecedent_tuple))

            consequent = tuple(
                sorted(
                    set(itemset) - set(antecedent)
                )
            )

            antecedent_support = support_lookup.get(
                antecedent
            )

            consequent_support = support_lookup.get(
                consequent
            )

            if antecedent_support is None:
                continue

            if consequent_support is None:
                continue

            confidence = (
                full_support /
                antecedent_support
            )

            if confidence < MIN_CONFIDENCE:
                continue

            lift = (
                confidence /
                consequent_support
            )

            eclat_rules.append(
                {
                    "antecedent": list(antecedent),
                    "consequent": list(consequent),
                    "support": full_support,
                    "confidence": confidence,
                    "lift": lift
                }
            )


print(
    f"ECLAT association rules: "
    f"{len(eclat_rules)}"
)


# Save ECLAT frequent itemsets
eclat_itemsets_output = pd.DataFrame(
    eclat_itemsets
)

if not eclat_itemsets_output.empty:

    eclat_itemsets_output["itemsets"] = (
        eclat_itemsets_output["itemsets"]
        .apply(lambda x: ", ".join(x))
    )

    eclat_itemsets_output.to_excel(
        OUTPUT_DIR / "eclat_frequent_itemsets.xlsx",
        index=False
    )


# Save ECLAT rules
if eclat_rules:

    eclat_rules_output = pd.DataFrame(
        eclat_rules
    )

    eclat_rules_output["antecedent"] = (
        eclat_rules_output["antecedent"]
        .apply(lambda x: ", ".join(x))
    )

    eclat_rules_output["consequent"] = (
        eclat_rules_output["consequent"]
        .apply(lambda x: ", ".join(x))
    )

    eclat_rules_output.to_excel(
        OUTPUT_DIR / "eclat_rules.xlsx",
        index=False
    )


# ============================================================
# CREATE WEBSITE FP-GROWTH JSON
# ============================================================

print("\n[7/8] Creating website recommendation rules...")

website_rules = []

for _, row in fpgrowth_rules.iterrows():

    antecedent = clean_itemset(
        row["antecedents"]
    )

    consequent = clean_itemset(
        row["consequents"]
    )

    website_rules.append(
        {
            "antecedent": antecedent,
            "consequent": consequent,
            "support": round(
                float(row["support"]),
                10
            ),
            "confidence": round(
                float(row["confidence"]),
                10
            ),
            "lift": round(
                float(row["lift"]),
                10
            )
        }
    )


# Sort rules by confidence, lift, support
website_rules.sort(
    key=lambda rule: (
        rule["confidence"],
        rule["lift"],
        rule["support"]
    ),
    reverse=True
)


new_rules_path = (
    OUTPUT_DIR /
    "fp_growth_rules_1002.json"
)

save_json(
    website_rules,
    new_rules_path
)


# ============================================================
# MODEL COMPARISON
# ============================================================

print("\n[8/8] Creating model comparison...")

comparison = pd.DataFrame(
    [
        {
            "Algorithm": "Apriori",
            "Transactions": EXPECTED_TRANSACTIONS,
            "Unique Products": EXPECTED_PRODUCTS,
            "Min Support": MIN_SUPPORT,
            "Min Support Count": minimum_support_count,
            "Min Confidence": MIN_CONFIDENCE,
            "Frequent Itemsets": len(apriori_itemsets),
            "Association Rules": len(apriori_rules)
        },
        {
            "Algorithm": "FP-Growth",
            "Transactions": EXPECTED_TRANSACTIONS,
            "Unique Products": EXPECTED_PRODUCTS,
            "Min Support": MIN_SUPPORT,
            "Min Support Count": minimum_support_count,
            "Min Confidence": MIN_CONFIDENCE,
            "Frequent Itemsets": len(fpgrowth_itemsets),
            "Association Rules": len(fpgrowth_rules)
        },
        {
            "Algorithm": "ECLAT",
            "Transactions": EXPECTED_TRANSACTIONS,
            "Unique Products": EXPECTED_PRODUCTS,
            "Min Support": MIN_SUPPORT,
            "Min Support Count": minimum_support_count,
            "Min Confidence": MIN_CONFIDENCE,
            "Frequent Itemsets": len(eclat_itemsets),
            "Association Rules": len(eclat_rules)
        }
    ]
)

comparison_path = (
    OUTPUT_DIR /
    "algorithm_comparison.xlsx"
)

comparison.to_excel(
    comparison_path,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETED")
print("=" * 70)

print(f"Transactions       : {EXPECTED_TRANSACTIONS}")
print(f"Unique products    : {EXPECTED_PRODUCTS}")
print(f"Minimum support    : {MIN_SUPPORT}")
print(f"Support count      : {minimum_support_count}")
print(f"Minimum confidence : {MIN_CONFIDENCE}")

print("\nModel results:")
print(comparison.to_string(index=False))

print("\nWebsite FP-Growth rules:")
print(f"  {len(website_rules)}")

print("\nOutput folder:")
print(f"  {OUTPUT_DIR}")

print("\nIMPORTANT:")
print("The existing Data/fp_growth_rules.json was NOT modified.")
print("The new website rules were saved separately.")

print("=" * 70)