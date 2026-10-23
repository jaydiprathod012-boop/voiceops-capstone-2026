# 🛒 VoiceOps Capstone 2026 — ZentroMart Customer Support Agent

> **FTTT Capstone Project** | Dataset reference date: **20 October 2026**

A multi-modal (text + voice) AI customer-support agent for **ZentroMart**, a fictional Indian e-commerce platform. This agent handles chat, email, support tickets, and voice queries using Gnani STT/TTS.

---

## 📁 Project Structure

```
voiceops-capstone-2026/
├── agent/                   # Core agent implementation
│   ├── agent.py             # Main agent entry point
│   ├── retriever.py         # KB retrieval (RAG)
│   ├── prompts.py           # System prompts
│   └── voice.py             # Gnani STT/TTS integration (Step 4)
├── data/                    # CSV data tables (7 files)
│   ├── customers.csv
│   ├── orders.csv
│   ├── order_items.csv
│   ├── products.csv
│   ├── pincodes.csv
│   ├── holidays.csv
│   └── support_logs.csv
├── kb/                      # 21 Markdown knowledge-base documents
├── practice/                # Evaluation datasets
│   ├── questions.csv        # 52 individual Q&A pairs
│   └── conversations.csv    # 23 multi-turn conversations (96 turns)
├── tools/                   # Mock order-lookup & ticket tools
│   ├── __init__.py
│   └── tools.py
├── notebooks/               # Exploration & evaluation notebooks
├── validate_dataset.py      # Dataset integrity checker
├── DATA_DICTIONARY.md       # Field-by-field data reference
├── ZIP_SCHEMA.md            # Relational schema overview
├── CHANGELOG.md             # Dataset changelog
├── requirements.txt
└── README.md
```

---

## 🚀 Steps / Milestones

| Step | Goal |
|------|------|
| **Step 1** | Single-turn Q&A: answer policy questions from `kb/` |
| **Step 2** | Multi-source answers: combine KB + catalog/pincode data |
| **Step 3** | Multi-turn conversations with identity verification & tool calls |
| **Step 4** | Voice: Gnani STT (WebSocket) + Gnani TTS for audio replies |

---

## ⚙️ Setup

```bash
# Clone the repo
git clone https://github.com/jaydiprathod012-boop/voiceops-capstone-2026.git
cd voiceops-capstone-2026

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Validate the dataset
python validate_dataset.py
```

---

## 🔧 Mock Tools

```python
from tools import lookup_order, create_ticket

# Step 1: Unverified lookup — returns verification prompt only
pending = lookup_order("8978 2837")

# Step 2: Verified lookup — pass phone last-4 OR delivery pincode
order = lookup_order("8978 2837", verification_value="4533")
assert order["found"] and order["verified"]

# Step 3: Escalate to human
ticket = create_ticket(
    summary="Verified caller reports a damaged TV on order 89782837; human review required.",
    order_id="89782837",
    reason="high_value_damage",
)
```

> ⚠️ Always verify identity before sharing order details. Maximum **one retry** allowed.

---

## 📊 Evaluation

- **52 single-turn questions** in `practice/questions.csv` with gold section IDs, must-include facts, and reference answers.
- **23 multi-turn conversations** in `practice/conversations.csv` with expected tool calls and decisions per turn.
- Scoring uses **section ID retrieval accuracy** + **must_include fact coverage**.

---

## 🌐 Key Design Constraints

- **Reference date**: 20 October 2026 (use for all deadline/delay calculations).
- **Business days**: Monday–Saturday, skipping holidays in `data/holidays.csv`.
- **Languages**: English, Hindi (Devanagari), Hinglish — agent must handle all.
- **Policy conflicts**: `kb/00_about_this_knowledge_base.md` defines precedence.
- **Support logs are NOT ground truth** — use only for tone/style learning.

---

## 📝 License

This project uses a **synthetic dataset** — no real customer data. Created for the FTTT 2026 Capstone.
