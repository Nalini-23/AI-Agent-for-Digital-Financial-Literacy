"""
Unit and integration tests for the Digital Financial Literacy Agent.
Run: python -m pytest tests/ -v
"""

import pytest
import json


# ── Knowledge Base Tests ──────────────────────────────────────────────────────

class TestKnowledgeBase:
    def test_knowledge_base_not_empty(self):
        from src.knowledge_base import FINANCIAL_KNOWLEDGE_BASE
        assert len(FINANCIAL_KNOWLEDGE_BASE) > 0

    def test_all_documents_have_required_fields(self):
        from src.knowledge_base import FINANCIAL_KNOWLEDGE_BASE
        for doc in FINANCIAL_KNOWLEDGE_BASE:
            assert "id" in doc, f"Missing 'id' in document: {doc}"
            assert "topic" in doc, f"Missing 'topic' in document: {doc}"
            assert "content" in doc, f"Missing 'content' in document: {doc}"
            assert "language" in doc, f"Missing 'language' in document: {doc}"

    def test_topics_coverage(self):
        from src.knowledge_base import FINANCIAL_KNOWLEDGE_BASE
        topics = {doc["topic"] for doc in FINANCIAL_KNOWLEDGE_BASE}
        required_topics = {"UPI", "Online Scams", "Interest Rates", "Budgeting", "Personal Finance"}
        for topic in required_topics:
            assert topic in topics, f"Missing topic in knowledge base: {topic}"

    def test_multilingual_documents_present(self):
        from src.knowledge_base import FINANCIAL_KNOWLEDGE_BASE
        languages = {doc["language"] for doc in FINANCIAL_KNOWLEDGE_BASE}
        assert "en" in languages, "English documents missing"
        assert "hi" in languages, "Hindi documents missing"


# ── Multilingual Tests ────────────────────────────────────────────────────────

class TestMultilingual:
    def test_supported_languages_count(self):
        from src.multilingual import SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) >= 10

    def test_english_in_supported(self):
        from src.multilingual import SUPPORTED_LANGUAGES
        assert "en" in SUPPORTED_LANGUAGES

    def test_hindi_in_supported(self):
        from src.multilingual import SUPPORTED_LANGUAGES
        assert "hi" in SUPPORTED_LANGUAGES

    def test_detect_english(self):
        from src.multilingual import detect_language
        lang = detect_language("How do I send money via UPI?")
        assert lang == "en"

    def test_detect_hindi(self):
        from src.multilingual import detect_language
        lang = detect_language("मुझे UPI से पैसे कैसे भेजने हैं?")
        assert lang == "hi"

    def test_get_greeting_english(self):
        from src.multilingual import get_greeting
        greeting = get_greeting("en")
        assert len(greeting) > 0
        assert "Hello" in greeting or "Assistant" in greeting

    def test_get_greeting_hindi(self):
        from src.multilingual import get_greeting
        greeting = get_greeting("hi")
        assert len(greeting) > 0

    def test_language_instruction_no_translate_needed(self):
        from src.multilingual import get_language_instruction
        instruction = get_language_instruction("en")
        assert "English" in instruction

    def test_language_instruction_hindi(self):
        from src.multilingual import get_language_instruction
        instruction = get_language_instruction("hi")
        assert "Hindi" in instruction or "हिंदी" in instruction


# ── Topic Detection Tests ─────────────────────────────────────────────────────

class TestTopicDetection:
    def test_detect_upi_topic(self):
        from src.agent import detect_topic
        assert detect_topic("How do I send money via UPI?") == "UPI"

    def test_detect_scam_topic(self):
        from src.agent import detect_topic
        result = detect_topic("I think I'm being scammed online")
        assert result == "Online Scams"

    def test_detect_interest_topic(self):
        from src.agent import detect_topic
        result = detect_topic("What is a safe interest rate for a personal loan?")
        assert result == "Interest Rates"

    def test_detect_budgeting_topic(self):
        from src.agent import detect_topic
        result = detect_topic("How do I create a monthly budget and save money?")
        assert result == "Budgeting"

    def test_detect_banking_topic(self):
        from src.agent import detect_topic
        result = detect_topic("What types of bank accounts can I open?")
        assert result == "Banking"

    def test_unknown_topic_returns_none(self):
        from src.agent import detect_topic
        result = detect_topic("What is the weather today?")
        assert result is None


# ── RAG Pipeline Tests ────────────────────────────────────────────────────────

class TestRAGPipeline:
    @pytest.fixture(scope="class")
    def pipeline_with_data(self, tmp_path_factory):
        from src.rag_pipeline import FinancialRAGPipeline
        from src.knowledge_base import FINANCIAL_KNOWLEDGE_BASE
        tmp_dir = str(tmp_path_factory.mktemp("vector_store"))
        pipeline = FinancialRAGPipeline(persist_dir=tmp_dir)
        pipeline.ingest_documents(FINANCIAL_KNOWLEDGE_BASE, reset=True)
        return pipeline

    def test_ingest_returns_positive_count(self, pipeline_with_data):
        stats = pipeline_with_data.collection_stats()
        assert stats["total_chunks"] > 0

    def test_retrieve_upi_query(self, pipeline_with_data):
        results = pipeline_with_data.retrieve("How to send money via UPI?", top_k=3)
        assert len(results) > 0
        assert "content" in results[0]
        assert "metadata" in results[0]

    def test_retrieve_returns_relevant_topic(self, pipeline_with_data):
        results = pipeline_with_data.retrieve("UPI PIN safety", top_k=3, topic_filter="UPI")
        assert len(results) > 0
        for r in results:
            assert r["metadata"]["topic"] == "UPI"

    def test_build_context_string(self, pipeline_with_data):
        results = pipeline_with_data.retrieve("scam", top_k=3)
        context = pipeline_with_data.build_context_string(results)
        assert isinstance(context, str)
        assert len(context) > 0

    def test_retrieve_empty_query_graceful(self, pipeline_with_data):
        # Should not raise, just return low-relevance results or empty list
        try:
            results = pipeline_with_data.retrieve("xyzzy nonsense query 12345", top_k=3)
            assert isinstance(results, list)
        except Exception as e:
            pytest.fail(f"Retrieval raised an exception: {e}")


# ── Flask API Tests ───────────────────────────────────────────────────────────

class TestFlaskAPI:
    @pytest.fixture
    def client(self):
        import os
        os.environ.setdefault("IBM_API_KEY", "")
        os.environ.setdefault("IBM_PROJECT_ID", "")
        from app import create_app
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c

    def test_health_endpoint(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert "status" in data

    def test_languages_endpoint(self, client):
        res = client.get("/api/languages")
        assert res.status_code == 200
        data = res.get_json()
        assert "languages" in data
        assert "en" in data["languages"]

    def test_topics_endpoint(self, client):
        res = client.get("/api/topics")
        assert res.status_code == 200
        data = res.get_json()
        assert "topics" in data
        assert len(data["topics"]) >= 6

    def test_chat_missing_message(self, client):
        res = client.post("/api/chat", json={}, content_type="application/json")
        assert res.status_code == 400

    def test_chat_empty_message(self, client):
        res = client.post("/api/chat", json={"message": "   "}, content_type="application/json")
        assert res.status_code == 400

    def test_chat_valid_message(self, client):
        res = client.post(
            "/api/chat",
            json={"message": "How do I send money via UPI?", "session_id": "test_session"},
            content_type="application/json",
        )
        assert res.status_code == 200
        data = res.get_json()
        assert "response" in data
        assert "session_id" in data
        assert len(data["response"]) > 0

    def test_session_history(self, client):
        session_id = "history_test_session"
        client.post(
            "/api/chat",
            json={"message": "What is UPI?", "session_id": session_id},
            content_type="application/json",
        )
        res = client.get(f"/api/session/{session_id}/history")
        assert res.status_code == 200
        data = res.get_json()
        assert "history" in data

    def test_session_reset(self, client):
        session_id = "reset_test_session"
        res = client.delete(f"/api/session/{session_id}/reset")
        assert res.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
