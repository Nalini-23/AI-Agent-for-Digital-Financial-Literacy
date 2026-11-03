"""
Test Results – 20 predefined Q&A pairs with expected topics and sources.
Used to render the Test Results table in the dashboard.
The agent is called for each question and the answer is validated against
expected keywords and sources.
"""

from __future__ import annotations

TEST_QUESTIONS: list[dict] = [
    # UPI
    {"id": 1, "category": "UPI", "question": "How do I send money via UPI?",
     "expected_keywords": ["PhonePe", "Google Pay", "UPI ID", "PIN", "QR"],
     "expected_source_kw": "NPCI"},
    {"id": 2, "category": "UPI", "question": "What is a UPI PIN and why is it secret?",
     "expected_keywords": ["PIN", "secret", "never share", "transaction"],
     "expected_source_kw": "NPCI"},
    {"id": 3, "category": "UPI", "question": "What is the daily UPI transaction limit?",
     "expected_keywords": ["1,00,000", "1 lakh", "2,00,000", "limit"],
     "expected_source_kw": "NPCI"},
    {"id": 4, "category": "UPI", "question": "What should I do if a UPI collect request says I will receive money?",
     "expected_keywords": ["scam", "approve", "send", "PIN"],
     "expected_source_kw": "RBI"},

    # Scams
    {"id": 5, "category": "Online Scams", "question": "What is a phishing scam?",
     "expected_keywords": ["fake", "link", "OTP", "password", "bank"],
     "expected_source_kw": "Cyber Crime"},
    {"id": 6, "category": "Online Scams", "question": "What is KYC fraud and how can I avoid it?",
     "expected_keywords": ["KYC", "Aadhaar", "OTP", "block", "official"],
     "expected_source_kw": "Cyber Crime"},
    {"id": 7, "category": "Online Scams", "question": "What number should I call if I am scammed online?",
     "expected_keywords": ["1930", "cybercrime.gov.in"],
     "expected_source_kw": "Cyber Crime"},
    {"id": 8, "category": "Online Scams", "question": "How do I verify if a bank or NBFC is legitimate?",
     "expected_keywords": ["RBI", "registered", "rbi.org.in"],
     "expected_source_kw": "RBI"},

    # Interest Rates
    {"id": 9, "category": "Interest Rates", "question": "What is compound interest?",
     "expected_keywords": ["principal", "interest", "compound", "formula"],
     "expected_source_kw": "RBI"},
    {"id": 10, "category": "Interest Rates", "question": "What is a safe interest rate for a personal loan in India?",
     "expected_keywords": ["10", "18", "24", "percent", "bank"],
     "expected_source_kw": "RBI"},
    {"id": 11, "category": "Interest Rates", "question": "What interest rate do credit cards charge?",
     "expected_keywords": ["24", "48", "percent", "annual", "minimum"],
     "expected_source_kw": "RBI"},
    {"id": 12, "category": "Interest Rates", "question": "How is EMI calculated?",
     "expected_keywords": ["EMI", "principal", "rate", "months"],
     "expected_source_kw": "RBI"},

    # Budgeting
    {"id": 13, "category": "Budgeting", "question": "What is the 50/30/20 budgeting rule?",
     "expected_keywords": ["50", "30", "20", "needs", "wants", "savings"],
     "expected_source_kw": "Financial Planning"},
    {"id": 14, "category": "Budgeting", "question": "Why do I need an emergency fund?",
     "expected_keywords": ["emergency", "months", "expenses", "liquid"],
     "expected_source_kw": "Financial Planning"},
    {"id": 15, "category": "Budgeting", "question": "What is PPF and what interest rate does it offer?",
     "expected_keywords": ["PPF", "7", "percent", "tax", "15 years"],
     "expected_source_kw": "India Post"},
    {"id": 16, "category": "Budgeting", "question": "What is a SIP in mutual funds?",
     "expected_keywords": ["SIP", "monthly", "invest", "mutual fund", "rupee cost"],
     "expected_source_kw": "AMFI"},

    # Personal Finance
    {"id": 17, "category": "Personal Finance", "question": "How much life insurance coverage do I need?",
     "expected_keywords": ["10", "15", "annual income", "term", "cover"],
     "expected_source_kw": "SEBI"},
    {"id": 18, "category": "Personal Finance", "question": "What is a CIBIL score and how does it affect loans?",
     "expected_keywords": ["CIBIL", "750", "credit score", "loan", "interest"],
     "expected_source_kw": "RBI"},

    # Banking
    {"id": 19, "category": "Banking", "question": "What is a zero-balance savings account?",
     "expected_keywords": ["zero", "BSBD", "Jan Dhan", "balance", "RBI"],
     "expected_source_kw": "RBI"},
    {"id": 20, "category": "Banking", "question": "How much of my bank deposit is insured in India?",
     "expected_keywords": ["5 lakh", "DICGC", "insured", "deposit"],
     "expected_source_kw": "RBI"},
]


def run_tests(agent) -> list[dict]:
    """
    Run all 20 test questions through the agent and evaluate answers.
    Returns list of result dicts.
    """
    results = []
    for test in TEST_QUESTIONS:
        try:
            response = agent.chat(
                user_message=test["question"],
                session_id=f"test_{test['id']}",
            )
            answer = response.get("response", "")
            sources = response.get("sources", [])

            # Check keywords
            answer_lower = answer.lower()
            matched_kws = [kw for kw in test["expected_keywords"]
                           if kw.lower() in answer_lower]
            kw_score = len(matched_kws) / len(test["expected_keywords"])

            # Check source
            source_ok = any(
                test["expected_source_kw"].lower() in s.lower()
                for s in sources
            )

            # Determine pass/partial/fail
            if kw_score >= 0.6 and source_ok:
                status = "PASS"
            elif kw_score >= 0.4:
                status = "PARTIAL"
            else:
                status = "FAIL"

            results.append({
                "id": test["id"],
                "category": test["category"],
                "question": test["question"],
                "status": status,
                "keyword_score": round(kw_score * 100),
                "source_ok": source_ok,
                "matched_keywords": matched_kws,
                "sources": sources,
                "answer_snippet": answer[:200],
            })
        except Exception as e:
            results.append({
                "id": test["id"],
                "category": test["category"],
                "question": test["question"],
                "status": "ERROR",
                "keyword_score": 0,
                "source_ok": False,
                "matched_keywords": [],
                "sources": [],
                "answer_snippet": str(e)[:200],
            })
    return results


def get_test_questions() -> list[dict]:
    """Return just the question definitions (no agent calls)."""
    return [{"id": q["id"], "category": q["category"], "question": q["question"]}
            for q in TEST_QUESTIONS]
