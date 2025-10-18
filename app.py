from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# --- Load environment ---
load_dotenv()

# --- Flask setup ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- OpenAI client ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

# --- Semantic Analysis Endpoint ---
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        turns = data.get("turns", [])
        texts = [t.get("text", "") for t in turns]

        if not texts:
            return jsonify({"error": "No texts provided"}), 400

        # 🔀 Choose embedding model
        model_choice = request.args.get("model", "small").lower()
        embed_model = (
            "text-embedding-3-large"
            if model_choice == "large"
            else "text-embedding-3-small"
        )

        print(f"🧠 Using model: {embed_model} | {len(texts)} texts")

        # 🔹 Generate embeddings
        emb_response = client.embeddings.create(model=embed_model, input=texts)
        embeddings = np.array([e.embedding for e in emb_response.data])

        # 🔹 Compute cosine similarity matrix
        sim_matrix = cosine_similarity(embeddings)

        # --- Core metrics ---
        n = len(texts)
        coherence = np.zeros(n)
        drift = np.zeros(n)
        entropy = np.zeros(n)
        resonance = np.zeros(n)
        novelty = np.zeros(n)
        volatility = np.zeros(n)

        for i in range(n):
            # Coherence: similarity with previous turns
            coherence[i] = np.mean(sim_matrix[i, :i]) if i > 0 else 0.8
            # Drift: dissimilarity to previous turn
            drift[i] = 1 - (sim_matrix[i, i - 1] if i > 0 else 0.2)
            # Entropy: spread of similarities (measure of distributional uncertainty)
            entropy[i] = float(np.std(sim_matrix[i])) * 2
            # Resonance: similarity with mean embedding
            resonance[i] = float(np.dot(embeddings[i], np.mean(embeddings, axis=0)))
            # Novelty: difference from cluster centroid (to be refined after clustering)
            novelty[i] = float(np.std(embeddings[i]))
            # Volatility: variability across neighborhood
            volatility[i] = np.mean(np.abs(np.diff(sim_matrix[i]))) if i > 1 else 0.1

        # --- PCA projection (3D coordinates) ---
        pca = PCA(n_components=3)
        coords = pca.fit_transform(embeddings)

        # --- Clustering ---
        num_clusters = min(5, max(2, n // 5))
        clusters = KMeans(n_clusters=num_clusters, n_init=10).fit_predict(embeddings)

        # --- Build analysis output ---
        analysis = []
        for i, t in enumerate(turns):
            analysis.append({
                "id": i + 1,
                "speaker": t.get("speaker", "user"),
                "text": texts[i],
                "phase": 1,
                "coherence": float(coherence[i]),
                "drift": float(drift[i]),
                "entropy": float(entropy[i]),
                "resonance": float(resonance[i]),
                "novelty": float(novelty[i]),
                "volatility": float(volatility[i]),
                "cluster": int(clusters[i]),
                "pca": coords[i].tolist()
            })

        print(f"✅ Analysis complete for {len(analysis)} turns.")
        return jsonify({"analysis": analysis})

    except Exception as e:
        print("🔥 API Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
