import pandas as pd
from flask import jsonify

CSV_FILE = "friends_data.csv"

def load_data():
    """Safely load CSV into a pandas DataFrame."""
    try:
        df = pd.read_csv(CSV_FILE)
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {e}")

def save_data(df):
    """Safely save updated DataFrame back to CSV."""
    try:
        df.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to save data: {e}")

def paginate(df, page, per_page):
    """Paginate DataFrame results safely."""
    from math import ceil
    df = df.sort_values("id").reset_index(drop=True)

    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page

    # Handle out-of-range pages gracefully
    if start >= total:
        return jsonify({
            "meta": {
                "page": page,
                "per_page": per_page,
                "total_records": total,
                "total_pages": ceil(total / per_page)
            },
            "data": []
        })

    paginated = df.iloc[start:end]
    meta = {
        "page": page,
        "per_page": per_page,
        "total_records": total,
        "total_pages": ceil(total / per_page)
    }

    return jsonify({
        "meta": meta,
        "data": paginated.to_dict(orient="records")
    })
