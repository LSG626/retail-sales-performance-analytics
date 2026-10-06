from pathlib import Path
import pandas as pd

from data_loader import load_all_raw_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = (
    BASE_DIR
    / "data"
    / "raw"
)

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

PROCESSED_FILE = (
    PROCESSED_DIR
    / "retail_transactions_clean.csv"
)


# =========================================================
# START PIPELINE
# =========================================================

print("=" * 70)
print("DAY 1 - RETAIL SALES ANALYTICS")
print("=" * 70)


# =========================================================
# LOAD ALL FILES + ALL EXCEL SHEETS
# =========================================================

df = load_all_raw_data(
    RAW_DIR
)


# =========================================================
# SHOW ORIGINAL COLUMNS
# =========================================================

print("\nColumns detected:")

for column in df.columns:
    print(f" - {column}")


# =========================================================
# STANDARDIZE COLUMN NAMES
# =========================================================

# This allows slightly different versions
# of the Online Retail dataset.

COLUMN_MAPPING = {

    # Invoice
    "Invoice": "invoice",
    "InvoiceNo": "invoice",
    "invoice": "invoice",

    # Product
    "StockCode": "stock_code",
    "stock_code": "stock_code",

    # Description
    "Description": "description",
    "description": "description",

    # Quantity
    "Quantity": "quantity",
    "quantity": "quantity",

    # Invoice date
    "InvoiceDate": "invoice_date",
    "invoice_date": "invoice_date",

    # Price
    "Price": "price",
    "UnitPrice": "price",
    "price": "price",

    # Customer
    "Customer ID": "customer_id",
    "CustomerID": "customer_id",
    "customer_id": "customer_id",

    # Country
    "Country": "country",
    "country": "country",
}


df = df.rename(
    columns=COLUMN_MAPPING
)


# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_columns = [

    "invoice",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "price",
    "customer_id",
    "country",

]


missing_columns = [

    col
    for col in required_columns
    if col not in df.columns

]


if missing_columns:

    raise ValueError(

        "Required columns are missing:\n"
        + "\n".join(missing_columns)

    )


# =========================================================
# INITIAL SUMMARY
# =========================================================

print("\n" + "=" * 70)
print("INITIAL DATA SUMMARY")
print("=" * 70)

print(
    f"Total rows loaded: "
    f"{len(df):,}"
)

if "source_file" in df.columns:

    print(
        f"\nSource files:"
    )

    print(
        df["source_file"]
        .value_counts()
    )


if "source_sheet" in df.columns:

    print(
        "\nRows by worksheet:"
    )

    print(
        df["source_sheet"]
        .value_counts()
    )


# =========================================================
# REMOVE COMPLETELY EMPTY ROWS
# =========================================================

df = df.dropna(
    how="all"
)


# =========================================================
# REMOVE DUPLICATES
# =========================================================

duplicate_count = df.duplicated().sum()

print(
    f"\nDuplicate rows found: "
    f"{duplicate_count:,}"
)

df = df.drop_duplicates()


# =========================================================
# CLEAN TEXT
# =========================================================

df["invoice"] = (
    df["invoice"]
    .astype("string")
    .str.strip()
)


df["stock_code"] = (
    df["stock_code"]
    .astype("string")
    .str.strip()
)


df["description"] = (
    df["description"]
    .astype("string")
    .str.strip()
)


df["country"] = (
    df["country"]
    .astype("string")
    .str.strip()
)


# =========================================================
# CONVERT TYPES
# =========================================================

df["invoice_date"] = pd.to_datetime(
    df["invoice_date"],
    errors="coerce"
)


df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce"
)


df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)


df["customer_id"] = pd.to_numeric(
    df["customer_id"],
    errors="coerce"
).astype("Int64")


# =========================================================
# MISSING VALUES
# =========================================================

print("\nMissing values:")

print(
    df[
        required_columns
    ]
    .isnull()
    .sum()
    .sort_values(
        ascending=False
    )
)


# =========================================================
# REMOVE RECORDS WITHOUT REQUIRED TRANSACTION DATA
# =========================================================

df = df.dropna(
    subset=[
        "invoice",
        "stock_code",
        "invoice_date",
        "quantity",
        "price",
        "country",
    ]
)


# =========================================================
# CLEAN DESCRIPTION
# =========================================================

df["description"] = (
    df["description"]
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
    .str.strip()
)


# =========================================================
# TRANSACTION FLAGS
# =========================================================

df["is_cancelled"] = (
    df["invoice"]
    .str.upper()
    .str.startswith("C")
)


df["is_return"] = (
    df["quantity"] < 0
)


df["is_sale"] = (

    (~df["is_cancelled"])

    &

    (df["quantity"] > 0)

    &

    (df["price"] > 0)

)


# =========================================================
# REVENUE
# =========================================================

df["revenue"] = (
    df["quantity"]
    *
    df["price"]
)


# =========================================================
# DATE FEATURES
# =========================================================

df["order_date"] = (
    df["invoice_date"]
    .dt.date
)


df["year"] = (
    df["invoice_date"]
    .dt.year
)


df["month"] = (
    df["invoice_date"]
    .dt.month
)


df["month_name"] = (
    df["invoice_date"]
    .dt.month_name()
)


df["year_month"] = (
    df["invoice_date"]
    .dt.to_period("M")
    .astype(str)
)


df["quarter"] = (
    df["invoice_date"]
    .dt.quarter
)


df["day_name"] = (
    df["invoice_date"]
    .dt.day_name()
)


df["day_number"] = (
    df["invoice_date"]
    .dt.dayofweek
    +
    1
)


df["hour"] = (
    df["invoice_date"]
    .dt.hour
)


# =========================================================
# FINAL COLUMN ORDER
# =========================================================

final_columns = [

    "invoice",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "price",
    "customer_id",
    "country",

    "revenue",

    "order_date",
    "year",
    "month",
    "month_name",
    "year_month",
    "quarter",
    "day_name",
    "day_number",
    "hour",

    "is_cancelled",
    "is_return",
    "is_sale",

]


# Keep lineage information
if "source_file" in df.columns:

    final_columns.append(
        "source_file"
    )


if "source_sheet" in df.columns:

    final_columns.append(
        "source_sheet"
    )


df = df[
    final_columns
]


# =========================================================
# FINAL QUALITY CHECK
# =========================================================

print("\n" + "=" * 70)
print("FINAL DATA QUALITY SUMMARY")
print("=" * 70)


print(
    f"Final rows: "
    f"{len(df):,}"
)


print(
    f"Date range: "
    f"{df['invoice_date'].min()}"
    f" → "
    f"{df['invoice_date'].max()}"
)


print(
    f"Unique invoices: "
    f"{df['invoice'].nunique():,}"
)


print(
    f"Unique customers: "
    f"{df['customer_id'].nunique():,}"
)


print(
    f"Unique products: "
    f"{df['stock_code'].nunique():,}"
)


print(
    f"Countries: "
    f"{df['country'].nunique():,}"
)


print(
    f"Valid sales rows: "
    f"{df['is_sale'].sum():,}"
)


print(
    f"Return rows: "
    f"{df['is_return'].sum():,}"
)


print(
    f"Cancelled rows: "
    f"{df['is_cancelled'].sum():,}"
)


print("\nRows by year:")

print(
    df["year"]
    .value_counts()
    .sort_index()
)


if "source_sheet" in df.columns:

    print(
        "\nRows after cleaning by sheet:"
    )

    print(
        df["source_sheet"]
        .value_counts()
    )


# =========================================================
# SAVE
# =========================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


df.to_csv(
    PROCESSED_FILE,
    index=False
)


print("\n" + "=" * 70)

print(
    "CLEANING COMPLETE"
)

print("=" * 70)

print(
    f"\nSaved to:\n"
    f"{PROCESSED_FILE}"
)