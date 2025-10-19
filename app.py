# app.py — Final Integrated Version (Constellation + Chat Agent)
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# --- Environment Setup ---
load_dotenv()

# --- Flask Setup ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Initialize OpenAI Client ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================================================
# 🧠 ROUTE 1: Semantic Analysis for Constellation (JSON upload)
# ===============================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Accepts a JSON payload containing a conversation ledger.
    Computes embeddings, drift, entropy, and cluster metrics.
    Returns enriched turn-level data for visualization.
    """
    try:
        data = request.get_json()
        turns = data.get("turns", [])
        if not turns:
            return jsonify({"error": "No turns provided"}), 400

        # 1. Extract text
        texts = [t.get("text", "") for t in turns]
        speakers = [t.get("speaker", "user") for t in turns]

        # 2. Compute embeddings
        embeddings = []
        for text in texts:
            emb = client.embeddings.create(
                input=text, model="text-embedding-3-small"
            ).data[0].embedding
            embeddings.append(emb)
        embeddings = np.array(embeddings)

        # 3. PCA dimensionality reduction (for visualization)
        pca = PCA(n_components=3)
        coords = pca.fit_transform(embeddings).tolist()

        # 4. Pairwise coherence + drift metrics
        coherence = [float(np.dot(embeddings[i], embeddings[i]))
                     for i in range(len(embeddings))]
        drift = [float(np.linalg.norm(embeddings[i] - embeddings[i - 1]))
                 if i > 0 else 0 for i in range(len(embeddings))]

        # 5. Entropy (rough measure of dispersion)
        entropy = []
        for emb in embeddings:
            dist = cosine_similarity([emb], embeddings)[0]
            dist /= dist.sum()
            e = -np.sum(dist * np.log(dist + 1e-10))
            entropy.append(float(e))

        # 6. Cluster detection (KMeans)
        kmeans = KMeans(n_clusters=min(3, len(embeddings)), n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)

        # 7. Build enriched ledger
        enriched = []
        for i, t in enumerate(turns):
            enriched.append({
                "id": i + 1,
                "speaker": speakers[i],
                "text": texts[i],
                "coherence": round(coherence[i], 2),
                "drift": round(drift[i], 2),
                "entropy": round(entropy[i], 2),
                "cluster": int(cluster_labels[i]),
                "pca": coords[i],
            })

        return jsonify({"turns": enriched})

    except Exception as e:
        print("❌ Error in /analyze:", str(e))
        return jsonify({"error": str(e)}), 500


# ===============================================================
# 🤖 ROUTE 2: Simple Chat Agent (used by front-end "Compose" UI)
# ===============================================================
@app.route("/ask", methods=["POST"])
def ask():
    """
    Accepts a JSON payload: {"prompt": "some text"}
    Returns a model-generated reply.
    """
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply, "model": "gpt-4o-mini"})
    except Exception as e:
        print("❌ Error in /ask:", str(e))
        return jsonify({"error": str(e)}), 500


# ===============================================================
# 🌐 ROUTE 3: Root (Optional sanity check endpoint)
# ===============================================================
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Constellation API is running"})


# ===============================================================
# 🚀 Launch App
# ===============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
