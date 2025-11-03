from flask import Flask, request, jsonify
from utils.helpers import load_data, save_data, paginate
from utils.logger import logger
from flask import Flask, request, jsonify, render_template


app = Flask(__name__)


#  GET 

@app.route("/characters", methods=["GET"])
def get_characters():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 5))

        import pandas as pd
        df = load_data()
        if df.empty:
            return jsonify({"error": "No data found"}), 404

        
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"]).astype({"id": int}).sort_values("id").reset_index(drop=True)

        total = len(df)
        start = max(0, (page - 1) * per_page)
        end   = min(total, start + per_page)

        paginated = df.iloc[start:end]
        meta = {
            "page": page,
            "per_page": per_page,
            "total_records": total,
            "total_pages": (total + per_page - 1) // per_page
        }

        
        app.logger.info(f"/characters page={page} -> ids={paginated['id'].tolist()}")

        return jsonify({"meta": meta, "data": paginated.to_dict(orient="records")}), 200

    except Exception as e:
        app.logger.exception("Pagination error")
        return jsonify({"error": "Internal Server Error"}), 500

#  GET 

@app.route("/characters/search", methods=["GET"])
def search_characters():
    """Search characters by first or last name."""
    try:
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")

        if not first_name and not last_name:
            return jsonify({"error": "Please provide first_name or last_name"}), 400

        df = load_data()
        if df.empty:
            return jsonify({"error": "No data found"}), 404

        results = df.copy()
        if first_name:
            results = results[results["first_name"].str.contains(first_name, case=False, na=False)]
        if last_name:
            results = results[results["last_name"].str.contains(last_name, case=False, na=False)]

        if results.empty:
            logger.info(f"No results found for: {first_name or last_name}")
            return jsonify({"message": "No matching characters found"}), 404

        logger.info(f"Search success: first_name={first_name}, last_name={last_name}")
        return jsonify(results.to_dict(orient="records")), 200

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500



#  PUT 

@app.route("/characters/<int:char_id>", methods=["PUT"])
def update_character(char_id):
    """Update a character by ID and persist to CSV."""
    try:
        df = load_data()
        if df.empty:
            return jsonify({"error": "No data found"}), 404

        if char_id not in df["id"].values:
            return jsonify({"error": f"Character with id {char_id} not found"}), 404

        update_data = request.get_json()
        if not update_data:
            return jsonify({"error": "No update data provided"}), 400

        for key, value in update_data.items():
            if key in df.columns:
                df.loc[df["id"] == char_id, key] = value

        save_data(df)
        logger.info(f"Character with id {char_id} updated successfully.")
        return jsonify({"message": f"Character {char_id} updated successfully"}), 200

    except Exception as e:
        logger.error(f"Update failed for id {char_id}: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


#  DELETE 

@app.route("/characters/<int:char_id>", methods=["DELETE"])
def delete_character(char_id):
    """Delete a character by ID and persist to CSV."""
    try:
        df = load_data()
        if df.empty:
            return jsonify({"error": "No data found"}), 404

        if char_id not in df["id"].values:
            return jsonify({"error": f"Character with id {char_id} not found"}), 404

        df = df[df["id"] != char_id]
        save_data(df)

        logger.info(f"Character with id {char_id} deleted successfully.")
        return jsonify({"message": f"Character {char_id} deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete failed for id {char_id}: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


# ERROR HANDLERS

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/")
def home():
    """Serve the frontend page"""
    return render_template("index.html")

# MAIN

if __name__ == "__main__":
    import socket
    host = "127.0.0.1"
    port = 5000
    print(f" Flask server starting...")
    print(f"👉 Open your browser at: http://{host}:{port}\n")
    app.run(host=host, port=port, debug=True, use_reloader=False)



