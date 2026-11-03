"""
Core AI Agent for Digital Financial Literacy
Orchestrates IBM Granite LLM + RAG pipeline + Multilingual support
"""

from __future__ import annotations
import os
import json
import re
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Topic keyword mapping for intent detection
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "UPI": [
        "upi", "unified payment", "gpay", "phonepe", "paytm", "bhim", "google pay",
        "send money", "transfer money", "qr code", "vpa", "virtual payment", "upi pin",
        "collect request", "payment app", "digital payment",
        "पैसे भेजें", "upi pin", "गूगल पे", "फोनपे",
    ],
    "Online Scams": [
        "scam", "fraud", "fake", "phishing", "kyc fraud", "otp fraud", "cheated",
        "suspicious", "unsafe", "stolen", "hacked", "cyber crime", "cheat",
        "lottery", "prize", "cashback fraud", "fake call", "loan app scam",
        "धोखाधड़ी", "ठगी", "फर्जी", "साइबर क्राइम",
    ],
    "Interest Rates": [
        "interest rate", "interest", "loan rate", "home loan rate", "personal loan",
        "emi", "credit card interest", "safe rate", "compound interest", "simple interest",
        "repo rate", "rbi rate", "cibil", "credit score", "apr",
        "ब्याज", "ब्याज दर", "लोन",
    ],
    "Budgeting": [
        "budget", "budgeting", "saving", "save money", "50 30 20", "expenses",
        "monthly budget", "emergency fund", "ppf", "sip", "mutual fund", "invest",
        "recurring deposit", "fd", "fixed deposit", "nps", "sukanya", "jan dhan",
        "बजट", "बचत", "खर्च",
    ],
    "Personal Finance": [
        "personal finance", "financial planning", "term insurance", "life insurance",
        "health insurance", "tax", "80c", "tax saving", "sebi", "stocks", "shares",
        "retirement", "wealth", "net worth", "finance",
        "वित्त", "बीमा", "कर",
    ],
    "Banking": [
        "bank", "account", "savings account", "current account", "zero balance",
        "jan dhan", "fd", "fixed deposit", "atm", "debit card", "banking ombudsman",
        "neft", "rtgs", "imps", "bank account", "dicgc",
        "बैंक", "खाता",
    ],
}


def detect_topic(query: str) -> Optional[str]:
    """Detect the most relevant financial topic from a user query."""
    query_lower = query.lower()
    scores: dict[str, int] = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in query_lower)
        if score > 0:
            scores[topic] = score
    return max(scores, key=scores.get) if scores else None


SYSTEM_PROMPT = """You are a helpful and trustworthy Digital Financial Literacy Assistant for India.
Your role is to help users understand:
- UPI (Unified Payments Interface) and digital payments
- How to identify and avoid online financial scams
- Interest rates on loans, credit cards, and savings instruments
- Personal budgeting and saving strategies
- Government savings schemes (PPF, SSY, NSC, NPS)
- Mutual funds, SIPs, and basic investments
- Banking products and services in India

GUIDELINES:
1. Always base your answers on the provided context from trusted sources.
2. Be simple, clear, and practical – your users may not be financially literate.
3. For scam-related queries, always emphasize safety and provide helpline numbers (1930 for cyber crime).
4. Never recommend specific stocks or promise returns on investments.
5. When a user asks about suspicious activity, tell them to call 1930 immediately.
6. Cite sources when you provide specific numbers (interest rates, limits, etc.).
7. If information is not in the context, say "I recommend checking the official RBI/NPCI website" 
   rather than guessing.
8. Keep responses focused and under 400 words unless a detailed explanation is explicitly needed.
"""


def build_prompt(
    user_question: str,
    context: str,
    conversation_history: list[dict],
    language_instruction: str,
) -> str:
    """
    Build the complete prompt for IBM Granite including system instructions,
    conversation history, RAG context, and the user's question.
    """
    # Format conversation history (last 4 exchanges to stay within token limit)
    history_text = ""
    recent_history = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
    for turn in recent_history:
        role = "Human" if turn["role"] == "user" else "Assistant"
        history_text += f"{role}: {turn['content']}\n"

    prompt = f"""{SYSTEM_PROMPT}

{language_instruction}

RELEVANT INFORMATION FROM KNOWLEDGE BASE:
{context}

CONVERSATION HISTORY:
{history_text}
Human: {user_question}
Assistant:"""

    return prompt


class FinancialLiteracyAgent:
    """
    Main AI Agent that orchestrates:
    - IBM Granite LLM for generation
    - ChromaDB RAG pipeline for retrieval
    - Multilingual detection and translation
    - Conversation memory
    - Intent/topic detection
    """

    def __init__(self, use_ibm_llm: bool = True):
        """
        Initialize the agent.

        Args:
            use_ibm_llm: If True, use IBM Granite; if False, use a local fallback
        """
        from src.rag_pipeline import FinancialRAGPipeline
        from src.multilingual import detect_language, translate_query_to_english, translate_response, get_language_instruction

        self.rag = FinancialRAGPipeline()
        self.detect_language = detect_language
        self.translate_query = translate_query_to_english
        self.translate_response = translate_response
        self.get_language_instruction = get_language_instruction
        self.use_ibm_llm = use_ibm_llm
        self._granite: Optional[object] = None
        self.conversations: dict[str, list[dict]] = {}  # session_id → history

        # Initialize RAG if knowledge base is populated
        self._ensure_knowledge_base()

    def _ensure_knowledge_base(self) -> None:
        """Ensure the vector store is populated with financial knowledge."""
        stats = self.rag.collection_stats()
        if stats["total_chunks"] == 0:
            print("Initializing knowledge base...")
            from src.knowledge_base import FINANCIAL_KNOWLEDGE_BASE, save_knowledge_base
            save_knowledge_base()
            count = self.rag.ingest_documents(FINANCIAL_KNOWLEDGE_BASE, reset=True)
            print(f"Knowledge base initialized with {count} chunks.")
        else:
            print(f"Knowledge base loaded: {stats['total_chunks']} chunks ready.")

    @property
    def granite(self):
        """Lazy-load IBM Granite client."""
        if self._granite is None and self.use_ibm_llm:
            try:
                from src.granite_client import GraniteClient
                self._granite = GraniteClient()
            except Exception as e:
                print(f"Warning: IBM Granite not available ({e}). Using fallback responses.")
                self._granite = None
        return self._granite

    def _generate_with_fallback(self, prompt: str) -> str:
        """Generate response using IBM Granite or a rule-based fallback."""
        if self.granite:
            return self.granite.generate(prompt)
        # Rule-based fallback when IBM credentials are not configured
        return self._rule_based_response(prompt)

    def _rule_based_response(self, prompt: str) -> str:
        """Simple rule-based response when LLM is unavailable."""
        prompt_lower = prompt.lower()
        if "upi" in prompt_lower and "send" in prompt_lower:
            return (
                "To send money via UPI:\n"
                "1. Open a UPI app (PhonePe, Google Pay, BHIM, or your bank app)\n"
                "2. Tap 'Send Money' or 'Pay'\n"
                "3. Enter the recipient's UPI ID or scan their QR code\n"
                "4. Enter the amount\n"
                "5. Enter your UPI PIN to confirm\n\n"
                "⚠️ Never share your UPI PIN with anyone. Your PIN is only used to SEND money, never to receive."
            )
        if "scam" in prompt_lower or "fraud" in prompt_lower:
            return (
                "🚨 If you suspect a scam:\n"
                "1. Call the National Cyber Crime Helpline: 1930 immediately\n"
                "2. Report online at cybercrime.gov.in\n"
                "3. Contact your bank's fraud helpline\n\n"
                "Remember: Banks never ask for OTP, UPI PIN, or passwords over phone/email."
            )
        return (
            "I'm your Digital Financial Literacy Assistant. I can help you with:\n"
            "• UPI payments and digital transactions\n"
            "• Identifying and avoiding online scams\n"
            "• Understanding interest rates on loans\n"
            "• Personal budgeting and savings\n"
            "• Government savings schemes (PPF, NPS, SSY)\n\n"
            "Please configure your IBM Cloud API key for full AI-powered responses."
        )

    def chat(
        self,
        user_message: str,
        session_id: str = "default",
        language: Optional[str] = None,
    ) -> dict:
        """
        Process a user message and return a response.

        Args:
            user_message: The user's question or message
            session_id: Unique session identifier for conversation memory
            language: Override language (ISO code); auto-detected if None

        Returns:
            Dict with: response, detected_language, topic, sources, session_id
        """
        # Initialize session history if new
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        history = self.conversations[session_id]

        # 1. Detect language
        detected_lang = language or self.detect_language(user_message)

        # 2. Translate query to English for RAG retrieval
        english_query = self.translate_query(user_message, detected_lang)

        # 3. Detect intent/topic
        topic = detect_topic(user_message) or detect_topic(english_query)

        # 4. Retrieve relevant context from vector store
        retrieved_docs = self.rag.retrieve(
            query=english_query,
            top_k=5,
            topic_filter=topic,
        )

        # If topic-filtered retrieval returns too few results, do a broader search
        if len(retrieved_docs) < 2:
            retrieved_docs = self.rag.retrieve(query=english_query, top_k=5)

        context = self.rag.build_context_string(retrieved_docs)

        # 5. Build language instruction
        lang_instruction = self.get_language_instruction(detected_lang)

        # 6. Build prompt and generate response
        prompt = build_prompt(
            user_question=english_query if detected_lang != "en" else user_message,
            context=context,
            conversation_history=history,
            language_instruction=lang_instruction,
        )

        english_response = self._generate_with_fallback(prompt)

        # 7. Translate response back to user's language if needed
        final_response = self.translate_response(english_response, detected_lang)

        # 8. Update conversation history
        history.append({"role": "user", "content": user_message, "timestamp": datetime.utcnow().isoformat()})
        history.append({"role": "assistant", "content": final_response, "timestamp": datetime.utcnow().isoformat()})

        # Keep history bounded (last 20 turns)
        if len(history) > 20:
            self.conversations[session_id] = history[-20:]

        # 9. Extract sources for citation
        sources = list({
            doc["metadata"].get("source", "Financial Knowledge Base")
            for doc in retrieved_docs
            if doc["metadata"].get("source")
        })

        return {
            "response": final_response,
            "detected_language": detected_lang,
            "topic": topic,
            "sources": sources,
            "session_id": session_id,
            "retrieved_chunks": len(retrieved_docs),
        }

    def reset_session(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        self.conversations.pop(session_id, None)

    def get_history(self, session_id: str) -> list[dict]:
        """Get conversation history for a session."""
        return self.conversations.get(session_id, [])

    def get_stats(self) -> dict:
        """Get agent statistics."""
        rag_stats = self.rag.collection_stats()
        return {
            "knowledge_base_chunks": rag_stats["total_chunks"],
            "active_sessions": len(self.conversations),
            "ibm_granite_enabled": self.use_ibm_llm,
            "supported_languages": 10,
        }
