"""
Flask Web API for the Digital Financial Literacy Agent
Serves both the REST API endpoints and the static frontend.
"""

import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Lazy-load agent to avoid slow startup
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        from src.agent import FinancialLiteracyAgent
        # Use IBM LLM only if credentials are configured
        use_ibm = bool(os.getenv("IBM_API_KEY") and os.getenv("IBM_PROJECT_ID"))
        _agent = FinancialLiteracyAgent(use_ibm_llm=use_ibm)
    return _agent


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="")
    CORS(app, origins="*")

    # ─── API Routes ────────────────────────────────────────────────────────────

    @app.route("/api/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        try:
            agent = get_agent()
            stats = agent.get_stats()
            return jsonify({"status": "healthy", "stats": stats}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """
        Main chat endpoint.
        Request body: { "message": str, "session_id": str (optional), "language": str (optional) }
        """
        data = request.get_json(silent=True)
        if not data or not data.get("message"):
            return jsonify({"error": "Request body must include 'message' field"}), 400

        message = data["message"].strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        session_id = data.get("session_id") or str(uuid.uuid4())
        language = data.get("language")  # Optional override

        try:
            agent = get_agent()
            result = agent.chat(
                user_message=message,
                session_id=session_id,
                language=language,
            )
            # Record analytics
            try:
                from src.analytics import record_query
                record_query(
                    topic=result.get("topic"),
                    language=result.get("detected_language", "en"),
                    session_id=session_id,
                )
            except Exception:
                pass
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                "error": "Agent error",
                "message": str(e),
                "response": "I'm sorry, I encountered an error. Please try again.",
                "session_id": session_id,
            }), 500

    @app.route("/api/feedback", methods=["POST"])
    def feedback():
        """
        Record thumbs-up / thumbs-down feedback.
        Request body: { "sentiment": "up" | "down" }
        """
        data = request.get_json(silent=True)
        if not data or data.get("sentiment") not in ("up", "down"):
            return jsonify({"error": "sentiment must be 'up' or 'down'"}), 400
        try:
            from src.analytics import record_feedback
            record_feedback(data["sentiment"])
            return jsonify({"ok": True}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/analytics", methods=["GET"])
    def analytics():
        """Return aggregated analytics stats."""
        try:
            from src.analytics import get_stats
            return jsonify(get_stats()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/test-questions", methods=["GET"])
    def test_questions():
        """Return the 20 test question definitions (no agent calls)."""
        from src.test_suite import get_test_questions
        return jsonify({"questions": get_test_questions()}), 200

    @app.route("/api/run-tests", methods=["POST"])
    def run_tests():
        """
        Run all 20 test questions through the agent and return scored results.
        Can take 60-120s depending on IBM Granite response time.
        """
        try:
            agent = get_agent()
            from src.test_suite import run_tests as _run
            results = _run(agent)
            passed = sum(1 for r in results if r["status"] == "PASS")
            partial = sum(1 for r in results if r["status"] == "PARTIAL")
            failed = sum(1 for r in results if r["status"] in ("FAIL", "ERROR"))
            return jsonify({
                "results": results,
                "summary": {
                    "total": len(results),
                    "passed": passed,
                    "partial": partial,
                    "failed": failed,
                    "pass_rate": round(passed / len(results) * 100, 1),
                },
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/session/<session_id>/history", methods=["GET"])
    def get_history(session_id: str):
        """Get conversation history for a session."""
        try:
            agent = get_agent()
            history = agent.get_history(session_id)
            return jsonify({"session_id": session_id, "history": history}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/session/<session_id>/reset", methods=["DELETE"])
    def reset_session(session_id: str):
        """Clear conversation history for a session."""
        try:
            agent = get_agent()
            agent.reset_session(session_id)
            return jsonify({"message": f"Session {session_id} cleared"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/languages", methods=["GET"])
    def get_languages():
        """Return list of supported languages."""
        from src.multilingual import SUPPORTED_LANGUAGES
        return jsonify({"languages": SUPPORTED_LANGUAGES}), 200

    @app.route("/api/topics", methods=["GET"])
    def get_topics():
        """Return list of available financial topics."""
        topics = [
            {"id": "upi", "name": "UPI & Digital Payments", "icon": "💳"},
            {"id": "scams", "name": "Online Scam Prevention", "icon": "🛡️"},
            {"id": "interest", "name": "Interest Rates & Loans", "icon": "📊"},
            {"id": "budgeting", "name": "Budgeting & Savings", "icon": "💰"},
            {"id": "personal_finance", "name": "Personal Finance", "icon": "📈"},
            {"id": "banking", "name": "Banking & Accounts", "icon": "🏦"},
        ]
        return jsonify({"topics": topics}), 200

    @app.route("/api/scam-check", methods=["POST"])
    def scam_check():
        """
        Scam Checker endpoint — analyzes a pasted SMS or suspicious message.
        Request body: { "message": str }
        Response: { risk_level, verdict, scam_type, red_flags, explanation, actions, helplines }
        """
        data = request.get_json(silent=True)
        if not data or not data.get("message"):
            return jsonify({"error": "Request body must include 'message' field"}), 400

        message = data["message"].strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        if len(message) > 5000:
            return jsonify({"error": "Message too long (max 5000 characters)"}), 400

        try:
            from src.scam_checker import check_scam
            # Get IBM Granite client if available
            granite_client = None
            try:
                agent = get_agent()
                if agent.use_ibm_llm and agent.granite:
                    granite_client = agent.granite
            except Exception:
                pass

            result = check_scam(message, granite_client=granite_client)
            try:
                from src.analytics import record_scam_check
                record_scam_check(result.get("risk_level", "LOW"))
            except Exception:
                pass
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": "Scam check failed", "message": str(e)}), 500

    # ─── Static Frontend ───────────────────────────────────────────────────────

    @app.route("/")
    def index():
        return send_from_directory("static", "index.html")

    @app.errorhandler(404)
    def not_found(e):
        return send_from_directory("static", "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    # Disable reloader to prevent watchdog from reloading on site-package changes
    print(f"\nDigital Financial Literacy Agent running at http://localhost:{port}")
    print(f"API docs: http://localhost:{port}/api/health\n")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
