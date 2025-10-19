# app.py — Final Production Version
# ---------------------------------
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------
#  Load Environment
# --------------------------
load_dotenv()

# --------------------------
#  Flask Setup
# --------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Allow iframe embedding (for Vercel)
@app.after_request
def allow_iframe(response):
    response.headers["X-Frame-Options"] = "ALLOWALL"
    response.headers["Content-Security-Policy"] = "frame-ancestors *"
    return response

# --------------------------
#  Initialize OpenAI Client
# --------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --------------------------
#  Core Routes
# --------------------------

# Root index (optional)
@app.route("/")
def index():
    # If you have a templates/index.html
    try:
        return render_template("index.html")
    except:
        return jsonify({"message": "Flask app running. Use /constellation or /analyze"}), 200


# Serve the Constellation visualization
@app.route("/constellation")
def constellation():
    return render_template("constellation.html")


# --------------------------
#  API: Chat Endpoint
# --------------------------
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print("🔥 API Error:", e)
        return jsonify({"error": str(e)}), 500


# --------------------------
#  API: Analyze (Embeddings)
# --------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        texts = [t["text"] for t in data.get("turns", [])]

        # --- Get embeddings ---
        embeddings = []
        for t in texts:
            emb = client.embeddings.create(
                model="text-embedding-3-small",
                input=t
            ).data[0].embedding
            embeddings.append(emb)

        X = np.array(embeddings)
        similarities = cosine_similarity(X)
        pca = PCA(n_components=3)
        coords = pca.fit_transform(X).tolist()
        drift = [float(np.std(similarities[i])) for i in range(len(similarities))]
        entropy = [float(np.var(similarities[i])) for i in range(len(similarities))]

        # Optional clustering
        n_clusters = min(len(X), 3)
        kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
        clusters = kmeans.fit_predict(X).tolist()

        # Combine metrics
        analyzed = []
        for i, t in enumerate(data.get("turns", [])):
            analyzed.append({
                **t,
                "pca": coords[i],
                "drift": drift[i],
                "entropy": entropy[i],
                "cluster": int(clusters[i])
            })

        return jsonify({"turns": analyzed})

    except Exception as e:
        print("🔥 Analyze Error:", e)
        return jsonify({"error": str(e)}), 500


# --------------------------
#  Main Entry
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
