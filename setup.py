"""
Setup and initialization script for the Digital Financial Literacy Agent.
Run this once before starting the application to:
1. Verify IBM Cloud credentials
2. Build the knowledge base JSON files
3. Populate the ChromaDB vector store
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def check_env() -> bool:
    """Verify required environment variables are set."""
    print("=" * 60)
    print("  Digital Financial Literacy Agent - Setup")
    print("=" * 60)

    issues: list[str] = []
    if not os.getenv("IBM_API_KEY"):
        issues.append("IBM_API_KEY not set (required for IBM Granite LLM)")
    if not os.getenv("IBM_PROJECT_ID"):
        issues.append("IBM_PROJECT_ID not set (required for IBM Granite LLM)")

    if issues:
        print("\n[WARN] Missing IBM Cloud credentials:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n  Get free IBM Cloud Lite account at: https://cloud.ibm.com/registration")
        print("  Then create a Watson Studio project at: https://dataplatform.cloud.ibm.com")
        print("  Copy .env.example to .env and fill in your credentials.\n")
        print("  [NOTE] The agent will still run with rule-based fallback responses.")
    else:
        print("\n[OK] IBM Cloud credentials found.")

    return len(issues) == 0


def build_knowledge_base() -> None:
    """Build knowledge base JSON files and populate the vector store."""
    print("\nBuilding knowledge base...")

    # Save JSON files
    from src.knowledge_base import save_knowledge_base
    save_knowledge_base(output_dir="./data/knowledge_base")

    # Populate vector store
    print("\nPopulating vector store (ChromaDB)...")
    from src.rag_pipeline import FinancialRAGPipeline
    from src.knowledge_base import FINANCIAL_KNOWLEDGE_BASE

    pipeline = FinancialRAGPipeline()
    count = pipeline.ingest_documents(FINANCIAL_KNOWLEDGE_BASE, reset=True)
    stats = pipeline.collection_stats()

    print(f"[OK] Vector store populated: {count} chunks from {len(FINANCIAL_KNOWLEDGE_BASE)} documents")
    print(f"   Stored at: {stats['persist_dir']}")


def verify_rag() -> None:
    """Run a quick retrieval test."""
    print("\nTesting RAG retrieval...")
    from src.rag_pipeline import FinancialRAGPipeline

    pipeline = FinancialRAGPipeline()
    test_queries = [
        "How do I send money via UPI?",
        "What is a safe interest rate for a loan?",
        "How to avoid online scams?",
    ]
    for query in test_queries:
        results = pipeline.retrieve(query, top_k=2)
        if results:
            print(f"  [OK] '{query[:40]}...' -> {len(results)} chunks retrieved")
        else:
            print(f"  [WARN] '{query[:40]}...' -> No results (check vector store)")


def print_summary() -> None:
    """Print setup summary."""
    print("\n" + "=" * 60)
    print("  Setup Complete! Start the application:")
    print("=" * 60)
    print("\n  python app.py")
    print("\n  Then open: http://localhost:5000")
    print("\n  API endpoints:")
    print("    GET  /api/health       - Agent health check")
    print("    POST /api/chat         - Send a message")
    print("    GET  /api/languages    - Supported languages")
    print("    GET  /api/topics       - Financial topics")
    print("\n  Try these example queries:")
    print('    curl -X POST http://localhost:5000/api/chat \\')
    print('      -H "Content-Type: application/json" \\')
    print('      -d \'{"message": "How do I send money via UPI?", "session_id": "test"}\'')
    print()


if __name__ == "__main__":
    credentials_ok = check_env()
    build_knowledge_base()
    verify_rag()
    print_summary()
    sys.exit(0)
