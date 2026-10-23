"""
ZentroMart Customer Support Agent — Main Entry Point

Steps covered:
  Step 1: Single-turn KB Q&A
  Step 2: Multi-source (KB + CSV data) answers
  Step 3: Multi-turn conversations with identity verification & tools
  Step 4: Voice (Gnani STT/TTS) — see voice.py
"""

import os
from dotenv import load_dotenv
from agent.retriever import KBRetriever
from agent.prompts import SYSTEM_PROMPT
from tools import lookup_order, create_ticket

load_dotenv()

REFERENCE_DATE = "2026-10-20"  # Fixed dataset reference date


class ZentroMartAgent:
    """Multi-turn customer support agent for ZentroMart."""

    def __init__(self, llm_client=None):
        self.retriever = KBRetriever()
        self.history: list[dict] = []
        self.llm = llm_client  # Inject your preferred LLM client
        self.verified_orders: dict = {}  # order_id -> order details (current session only)

    def chat(self, user_message: str) -> str:
        """Process a single customer turn and return the agent reply."""
        # 1. Retrieve relevant KB sections
        kb_context = self.retriever.search(user_message, top_k=5)

        # 2. Build messages for LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(
                reference_date=REFERENCE_DATE,
                kb_context=kb_context,
            )}
        ] + self.history + [
            {"role": "user", "content": user_message}
        ]

        # 3. Call LLM (replace with your client call)
        reply = self._call_llm(messages)

        # 4. Update history
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": reply})

        return reply

    def _call_llm(self, messages: list[dict]) -> str:
        """Call your LLM API here. Replace this stub."""
        raise NotImplementedError(
            "Plug in your LLM client (OpenAI, Gemini, Anthropic, etc.)"
        )

    def reset(self):
        """Start a new conversation session."""
        self.history = []
        self.verified_orders = {}


def main():
    """Simple CLI loop for testing."""
    agent = ZentroMartAgent()
    print("ZentroMart Support Agent (type 'quit' to exit)\n")
    while True:
        user_input = input("Customer: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue
        reply = agent.chat(user_input)
        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    main()
