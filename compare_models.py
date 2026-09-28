import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "Data" / "Model_Results"


def normalize_rules(df, antecedent_col, consequent_col):

    normalized = set()

    for _, row in df.iterrows():

        antecedent = tuple(
            sorted(
                str(row[antecedent_col]).split(", ")
            )
        )

        consequent = tuple(
            sorted(
                str(row[consequent_col]).split(", ")
            )
        )

        normalized.add(
            (
                antecedent,
                consequent,
                round(float(row["support"]), 10),
                round(float(row["confidence"]), 10),
                round(float(row["lift"]), 10)
            )
        )

    return normalized


print("=" * 70)
print("ALGORITHM RULE COMPARISON")
print("=" * 70)


apriori = pd.read_excel(
    RESULTS_DIR / "apriori_rules.xlsx"
)

fpgrowth = pd.read_excel(
    RESULTS_DIR / "fpgrowth_rules.xlsx"
)

eclat = pd.read_excel(
    RESULTS_DIR / "eclat_rules.xlsx"
)


apriori_set = normalize_rules(
    apriori,
    "antecedents",
    "consequents"
)

fpgrowth_set = normalize_rules(
    fpgrowth,
    "antecedents",
    "consequents"
)

eclat_set = normalize_rules(
    eclat,
    "antecedent",
    "consequent"
)


print(f"\nApriori rules : {len(apriori_set)}")
print(f"FP-Growth rules: {len(fpgrowth_set)}")
print(f"ECLAT rules   : {len(eclat_set)}")


print("\nApriori == FP-Growth:")
print(apriori_set == fpgrowth_set)


print("\nApriori == ECLAT:")
print(apriori_set == eclat_set)


print("\nFP-Growth == ECLAT:")
print(fpgrowth_set == eclat_set)


print("\n" + "=" * 70)