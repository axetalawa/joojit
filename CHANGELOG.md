---
# CHANGELOG.md — Commit Story of JOOJIT  
### Conversational Ledger & Cognitive Mirror System  
*by Mute Logic Lab — Salvador, Bahia (2025)*  

> *A browser that learned to remember —  
> not what was said, but how saying unfolded.*

---

## 🌑 Phase I — Ledger Genesis (May 2025)

**Objective:**  
Establish a minimal structure for recording conversations between human and model — a *ledger of turns* stored locally in the browser.

**Key work**
- Designed **localStorage architecture** for storing prompt/reply pairs.  
- Created **`joojit.js`** — functions for session creation, saving, clearing, exporting.  
- Implemented the **HTML interface** (`joojit.html`) with minimal CSS and temporal layout.  
- Added session metadata: UUID, timestamp, latency, and model name.

**Artifacts**
- `joojit.html`
- `joojit.js`
- Local ledger schema (`ledgerStore`)

**Decisions**
- No backend; full autonomy inside the browser.  
- Each conversation is its own data structure, not a chat history.  
- Storage must be transparent, user-controlled, and easily exportable.  

---

## 🌒 Phase II — Affect Engine (June 2025)

**Objective:**  
Integrate emotional and semantic analysis into each ledger entry.

**Key work**
- Added **Flask backend** (`app.py`, `affect.py`) for text analysis.  
- Implemented lexical affect scoring using **NRC Emotion Lexicon** (`English-NRC-EmoLex.txt`).  
- Calculated six emotional vectors: *joy, sadness, fear, anger, trust, surprise*.  
- Derived secondary metrics: **coherence**, **drift**, **entropy**, **resonance**, **novelty**, and **volatility**.  
- Exposed `/analyze` API endpoint returning analytic fields for each message.

**Artifacts**
- `app.py`
- `affect.py`
- `English-NRC-EmoLex.txt`

**Decisions**
- Use **lexicon-based affect modeling** for transparency over black-box sentiment models.  
- Keep computation light — one pass per turn.  
- Return JSON for immediate front-end visualization.

---

## 🌓 Phase III — Metrics & Visualization Layer (July 2025)

**Objective:**  
Render analytic results as dynamic geometry — turning text into visible form.

**Key work**
- Authored **`metrics.js`** — client-side computation and rendering coordination.  
- Added **`constellation.html`** — a 2D/3D visualization of conversation nodes connected by semantic drift.  
- Encoded affect polarity in **color** and resonance intensity in **node size**.  
- Built hoverable tooltips for each turn’s text and metrics.  
- Introduced **drift vectors** between nodes to visualize coherence decay.

**Artifacts**
- `metrics.js`
- `constellation.html`

**Decisions**
- Visualization should *breathe*, not refresh.  
- Each session is a “micro-galaxy” — conversation as stellar topology.  
- Metrics are not evaluation — they are weather patterns of cognition.

---

## 🌔 Phase IV — Recursive Dialogue Layer (August–September 2025)

**Objective:**  
Enable Joojit to *think about its own thinking*.

**Key work**
- Introduced **`recursive.jsonl`** — templates for recursive reflection and meta-prompting.  
- Added modes for self-referential response: `"reflect"`, `"revise"`, `"invert"`, `"echo"`.  
- Implemented recursive generation logic in `joojit.js`.  
- Integrated **semantic depth control** (`depth: 1–3`) to guide recursion intensity.  

**Artifacts**
- `recursive.jsonl`
- Updated `joojit.js` and `metrics.js` for recursive mode.  

**Decisions**
- Recursion must remain *semantic*, not syntactic — each loop reframes the previous one.  
- Depth should modulate reflection, not repetition.  
- Establish **“recursive mind”** as experiment: what happens when chat reflects on its own topology?

---

## 🌕 Phase V — Integration & Constellation Unification (October 2025)

**Objective:**  
Unify ledger, affect, and visualization into one continuous system — the *Cognitive Mirror.*

**Key work**
- Merged all front-end components under unified **session management**.  
- Finalized **API routes** `/analyze` and `/export`.  
- Enabled live updating of constellation as new turns arrive.  
- Added multilingual placeholder (Portuguese/English) for future expansion.  
- Authored `README.md` and `CHANGELOG.md` for release.  

**Artifacts**
- `README.md`
- `CHANGELOG.md`
- Updated `index.html`, `joojit.html`, `constellation.html`
- Unified dataset: `recursive.jsonl` + `English-NRC-EmoLex.txt`

**Decisions**
- Treat Joojit as **interface, not product**.  
- Documentation should double as reflection — the changelog is part of the artwork.  
- Commit messages now follow semantic pattern:
```

add: affect engine — emotion scoring
refactor: metrics — resonance computation
docs: readme — ledger architecture

```

---

## 🪶 Forward Trajectory

- [ ] Real-time **WebSocket** streaming for live constellation updates.  
- [ ] **Portuguese affect lexicon** and dual-language interface.  
- [ ] **Embeddings integration** for semantic proximity mapping.  
- [ ] Archive-ready **ledger export** for longitudinal analysis.  
- [ ] Visual timeline of affect evolution per session.  

---

## ✴︎ Coda

> *A ledger becomes a mirror.  
> A mirror becomes a map.  
> A conversation becomes a weather system.*  

---

**Authored by:** [Javed Saunja Jaghai](https://javedjaghai.com)  
**Lab:** Mute Logic Lab — Salvador, Bahia (2025)  
**License:** MIT

---