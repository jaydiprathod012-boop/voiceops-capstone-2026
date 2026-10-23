"""
ZentroMart Customer Support Agent — Powered by Google Gemini

Steps covered:
  Step 1: Single-turn KB Q&A
  Step 2: Multi-source (KB + CSV data) answers
  Step 3: Multi-turn conversations with identity verification & tools
  Step 4: Voice (Gnani STT/TTS) — see voice.py
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from agent.retriever import KBRetriever
from agent.prompts import SYSTEM_PROMPT
from tools import lookup_order, create_ticket

load_dotenv()

REFERENCE_DATE = "2026-10-20"  # Fixed dataset reference date


class ZentroMartAgent:
    """Multi-turn customer support agent for ZentroMart — powered by Gemini."""

    def __init__(self):
        self.retriever = KBRetriever()
        self.history: list = []          # Gemini chat history
        self.verified_orders: dict = {}  # order_id -> details (session only)
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.system_prompt = SYSTEM_PROMPT.format(
            reference_date=REFERENCE_DATE,
            kb_context="(KB context injected per turn)",
        )
        # Start a persistent chat session
        self.chat_session = self.client.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
            )
        )

    def chat(self, user_message: str) -> str:
        """Process a single customer turn and return the agent reply."""
        # 1. Retrieve relevant KB sections for this message
        kb_context = self.retriever.search(user_message, top_k=5)

        # 2. Prepend KB context to the user message
        enriched_message = (
            f"[Relevant KB sections for this query]\n{kb_context}\n\n"
            f"[Customer message]\n{user_message}"
        )

        # 3. Send to Gemini and get reply
        response = self.chat_session.send_message(enriched_message)
        reply = response.text

        return reply

    def reset(self):
        """Start a new conversation session."""
        self.chat_session = self.client.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
            )
        )
        self.verified_orders = {}


def main():
    """Simple CLI loop for testing."""
    print("=" * 50)
    print("  ZentroMart Support Agent (Gemini-powered)")
    print("  Type 'quit' to exit | 'reset' for new session")
    print("=" * 50)
    agent = ZentroMartAgent()
    while True:
        try:
            user_input = input("\nCustomer: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("[Session reset]")
            continue
        if not user_input:
            continue
        print("\nAgent: ", end="", flush=True)
        reply = agent.chat(user_input)
        print(reply)


if __name__ == "__main__":
    main()
