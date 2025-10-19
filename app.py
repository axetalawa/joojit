from flask import Flask, jsonify, request, render_template, make_response
from flask_cors import CORS
import os, math, numpy as np, re
import json
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# --- Load NRC Emotion Lexicon ---
LEXICON_FILE = "dictionaries/English-NRC-EmoLex.txt"
NRC_LEXICON = {}
NRC_EMOTIONS = set()

if os.path.exists(LEXICON_FILE):
    with open(LEXICON_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 3:
                word, emotion, value = parts
                word = word.lower().strip()
                if int(value) == 1:
                    NRC_LEXICON.setdefault(word, []).append(emotion)
                    NRC_EMOTIONS.add(emotion)
    print(f"✅ Loaded {len(NRC_LEXICON)} words, {len(NRC_EMOTIONS)} emotions")
else:
    print(f"⚠️ Lexicon file not found: {LEXICON_FILE}")

# --- Compute metrics ---
def compute_semantic_metrics(turns):
    results = []

    for i, t in enumerate(turns):
        text = t.get("text", "")
        tokens = re.findall(r"[a-zA-Z']+", text.lower())
        affect = {emo: 0 for emo in NRC_EMOTIONS}

        for w in tokens:
            if w in NRC_LEXICON:
                for emo in NRC_LEXICON[w]:
                    affect[emo] += 1

        total = sum(affect.values())
        if total > 0:
            affect = {k: round(v / total, 4) for k, v in affect.items()}
        else:
            affect = {k: 0.0 for k in NRC_EMOTIONS}

        coherence = round(abs(math.sin(i + 1)) * 0.4 + 0.3, 6)
        drift = round(abs(math.cos(i + 2)) * 0.2 + 0.3, 6)
        novelty = round(abs(math.sin(i + 0.5)) * 0.3 + 0.4, 6)
        cluster = (i % 3) + 1
        pca = list(np.random.uniform(-0.6, 0.6, 3))

        enriched = {
            "id": t.get("id", i + 1),
            "speaker": t.get("speaker", "user"),
            "text": text,
            "phase": t.get("phase", 1),
            "coherence": coherence,
            "alignment": t.get("alignment", 0.9),
            "reference": t.get("reference", 0),
            "fragmented": t.get("fragmented", False),
            "drift": drift,
            "novelty": novelty,
            "cluster": cluster,
            "pca": pca,
            "affect": affect
        }
        results.append(enriched)

    return results

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/joojit')
def joojit():
    return render_template('joojit.html')

@app.route('/constellation')
def constellation():
    return render_template('constellation.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"error": "Empty prompt"}), 400

        # Call OpenAI or any backend model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Joojit, an experimental dialogic engine."},
                {"role": "user", "content": prompt}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({
            "reply": reply,
            "model": "gpt-4o-mini"
        })

    except Exception as e:
        print("Error in /ask:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of turns"}), 400

        enriched = compute_semantic_metrics(data)
        return jsonify(enriched)
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500
    

@app.route("/export", methods=["POST"])
def export_conversation():
    """Receive a conversation ledger and return it as downloadable JSONL."""
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of conversation turns"}), 400

        # Convert list to JSONL string
        jsonl_data = "\n".join(json.dumps(turn, ensure_ascii=False) for turn in data)
        filename = f"session_{datetime.now().strftime('%Y-%m-%d')}.jsonl"

        # Prepare response
        response = make_response(jsonl_data)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-Type"] = "application/jsonl; charset=utf-8"

        return response
    except Exception as e:
        print("❌ Error exporting:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
