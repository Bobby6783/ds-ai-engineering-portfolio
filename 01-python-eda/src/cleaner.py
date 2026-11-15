import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw_sales.csv"
SUMMARY_OUTPUT_PATH = BASE_DIR / "data" / "sales_summary.json"


def create_sample_data(filepath: Path) -> None:
    raw_content = """order_id,customer_name,category,amount,region
1001,  Rahul Sharma , electronics , 45000.50, West
1002,PRIYA PATEL,Clothing,1200.00,north
1001,  Rahul Sharma , electronics , 45000.50, West
1003,Amit Verma,GROCERIES,invalid_price,East
1004,Sneha Joshi,Electronics,28500,
1005,Vikram Singh,  clothing,3400.75,SOUTH
1006,Ananya Rao,Groceries,-500.00,West
1007,Karan Mehta,Books,850.00,North
"""
    with open(filepath, mode="w", encoding="utf-8") as file:
        file.write(raw_content)


def clean_sales_data(filepath: Path) -> list[dict]:
    cleaned_records: list[dict] = []
    seen_order_ids: set[str] = set()

    try:
        with open(filepath, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                order_id = row["order_id"].strip()

                if order_id in seen_order_ids:
                    continue

                try:
                    amount = float(row["amount"].strip())
                    if amount <= 0:
                        continue
                except ValueError:
                    continue

                customer_name = row["customer_name"].strip().title()
                category = row["category"].strip().lower()
                raw_region = row["region"].strip()
                region = raw_region.title() if raw_region else "Unknown"

                seen_order_ids.add(order_id)
                cleaned_records.append({
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "category": category,
                    "amount": amount,
                    "region": region,
                })

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")

    return cleaned_records


def summarize_sales(records: list[dict], output_path: Path) -> dict:
    total_revenue = round(sum(item["amount"] for item in records), 2)

    category_revenue: dict[str, float] = {}
    for item in records:
        cat = item["category"]
        category_revenue[cat] = round(category_revenue.get(cat, 0.0) + item["amount"], 2)

    top_orders = sorted(records, key=lambda x: x["amount"], reverse=True)

    summary = {
        "total_valid_orders": len(records),
        "total_revenue": total_revenue,
        "category_revenue": category_revenue,
        "top_orders": top_orders,
    }

    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    return summary


if __name__ == "__main__":
    create_sample_data(RAW_DATA_PATH)
    valid_sales = clean_sales_data(RAW_DATA_PATH)
    summary = summarize_sales(valid_sales, SUMMARY_OUTPUT_PATH)
    print(json.dumps(summary, indent=4))