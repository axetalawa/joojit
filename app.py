from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print("🔥 API Error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# Expanded Semantic Analysis Route
# ─────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        turns = data.get("turns", [])
        texts = [t["text"] for t in turns]
        speakers = [t["speaker"] for t in turns]
        n = len(texts)

        # Step 1 — Get embeddings from OpenAI
        emb_response = client.embeddings.create(model="text-embedding-3-small", input=texts)
        embeddings = np.array([e.embedding for e in emb_response.data])

        # Step 2 — Compute similarity matrix
        sim_matrix = cosine_similarity(embeddings)

        # Step 3 — Base metrics
        coherence = [sim_matrix[i, i - 1] if i > 0 else 0.9 for i in range(n)]
        drift = [1 - sim_matrix[i, i - 1] if i > 0 else 0.9 for i in range(n)]
        entropy = [
            np.std([sim_matrix[i, j] for j in range(max(0, i - 2), min(n, i + 3)) if j != i])
            for i in range(n)
        ]

        # Step 4 — Expanded metrics
        mean_vector = np.mean(embeddings, axis=0)
        resonance, volatility, novelty = [], [], []

        for i in range(n):
            # Forward similarities (next 2 turns)
            forward_sims = [sim_matrix[i, j] for j in range(i + 1, min(n, i + 3))]
            resonance.append(np.mean(forward_sims) if forward_sims else 0.0)
            volatility.append(np.std(forward_sims) if forward_sims else 0.0)

            # Novelty (distance from conversation mean)
            nov = 1 - cosine_similarity(
                embeddings[i].reshape(1, -1), mean_vector.reshape(1, -1)
            )[0][0]
            novelty.append(nov)

        # Step 5 — Clustering + PCA
        num_clusters = min(4, n)
        kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42)
        clusters = kmeans.fit_predict(embeddings)

        pca = PCA(n_components=3)
        pca_coords = pca.fit_transform(embeddings)

        # Step 6 — Package response
        analysis = []
        for i in range(n):
            analysis.append({
                "id": i + 1,
                "speaker": speakers[i],
                "text": texts[i],
                "coherence": float(coherence[i]),
                "drift": float(drift[i]),
                "entropy": float(entropy[i]),
                "resonance": float(resonance[i]),
                "volatility": float(volatility[i]),
                "novelty": float(novelty[i]),
                "cluster": int(clusters[i]),
                "pca": pca_coords[i].tolist()
            })

        return jsonify({
            "analysis": analysis,
            "embeddings": embeddings.tolist(),
            "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
            "similarity_matrix": sim_matrix.tolist()
        })

    except Exception as e:
        print("🔥 Analysis Error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# Run Server
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

