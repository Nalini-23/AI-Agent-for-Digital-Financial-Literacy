"""
RAG Pipeline for Digital Financial Literacy Agent
Handles document ingestion, vector storage, and retrieval using ChromaDB
with IBM Granite embeddings.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

load_dotenv()


class FinancialRAGPipeline:
    """
    RAG pipeline that:
    1. Ingests financial literacy documents into ChromaDB
    2. Retrieves relevant context for user queries
    3. Supports multilingual queries via language-aware retrieval
    """

    COLLECTION_NAME = "financial_literacy"

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or os.getenv(
            "CHROMA_PERSIST_DIR", "./data/vector_store"
        )
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        # ChromaDB client with persistence
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )

        # Local embedding model (fallback; IBM Slate used when available)
        self._embedding_model: Optional[SentenceTransformer] = None

        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", "!", "?", " "],
        )

        # Get or create the ChromaDB collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def embedding_model(self) -> SentenceTransformer:
        """Lazy-load local sentence-transformer for embeddings."""
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._embedding_model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using local sentence-transformers model."""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def ingest_documents(
        self,
        documents: list[dict],
        batch_size: int = 20,
        reset: bool = False,
    ) -> int:
        """
        Ingest financial literacy documents into the vector store.

        Args:
            documents: List of document dicts with keys: id, topic, title, content, language, source
            batch_size: Number of documents to process per batch
            reset: If True, clears existing collection first

        Returns:
            Number of chunks ingested
        """
        if reset:
            self.chroma_client.delete_collection(self.COLLECTION_NAME)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

        all_chunks: list[str] = []
        all_ids: list[str] = []
        all_metadata: list[dict] = []

        for doc in documents:
            # Split document into chunks
            chunks = self.text_splitter.split_text(doc["content"].strip())

            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc['id']}_chunk_{i}"
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadata.append({
                    "doc_id": doc["id"],
                    "topic": doc.get("topic", "General"),
                    "title": doc.get("title", ""),
                    "language": doc.get("language", "en"),
                    "source": doc.get("source", ""),
                    "chunk_index": i,
                })

        # Batch embed and upsert
        total_ingested = 0
        for start in range(0, len(all_chunks), batch_size):
            end = min(start + batch_size, len(all_chunks))
            batch_chunks = all_chunks[start:end]
            batch_ids = all_ids[start:end]
            batch_meta = all_metadata[start:end]

            embeddings = self.embed_texts(batch_chunks)

            self.collection.upsert(
                ids=batch_ids,
                embeddings=embeddings,
                documents=batch_chunks,
                metadatas=batch_meta,
            )
            total_ingested += len(batch_chunks)

        return total_ingested

    def ingest_from_json_dir(self, json_dir: str = "./data/knowledge_base") -> int:
        """Load and ingest all JSON knowledge base files from a directory."""
        json_path = Path(json_dir)
        if not json_path.exists():
            raise FileNotFoundError(f"Knowledge base directory not found: {json_dir}")

        all_docs: list[dict] = []
        for json_file in json_path.glob("*.json"):
            if json_file.name == "all_documents.json":
                continue
            with open(json_file, encoding="utf-8") as f:
                docs = json.load(f)
                all_docs.extend(docs)

        return self.ingest_documents(all_docs, reset=True)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        language_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: User's question
            top_k: Number of results to retrieve
            language_filter: ISO language code to filter by (e.g., "hi", "ta")
            topic_filter: Topic to filter by (e.g., "UPI", "Budgeting")

        Returns:
            List of dicts with 'content', 'metadata', 'distance' keys
        """
        query_embedding = self.embed_texts([query])[0]

        # Build optional where filter
        where: Optional[dict] = None
        if language_filter and topic_filter:
            where = {
                "$and": [
                    {"language": {"$eq": language_filter}},
                    {"topic": {"$eq": topic_filter}},
                ]
            }
        elif language_filter:
            where = {"language": {"$eq": language_filter}}
        elif topic_filter:
            where = {"topic": {"$eq": topic_filter}}

        query_kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_kwargs["where"] = where

        results = self.collection.query(**query_kwargs)

        retrieved: list[dict] = []
        if results["documents"]:
            for i, (doc, meta, dist) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ):
                retrieved.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "relevance_score": round(1 - dist, 4),
                })

        return retrieved

    def build_context_string(self, retrieved_docs: list[dict], max_chars: int = 3000) -> str:
        """
        Build a formatted context string from retrieved documents for the LLM prompt.

        Args:
            retrieved_docs: List of retrieved document dicts
            max_chars: Maximum character length of context

        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found in knowledge base."

        context_parts: list[str] = []
        total_chars = 0

        for doc in retrieved_docs:
            meta = doc["metadata"]
            header = f"[Source: {meta.get('source', 'Financial Knowledge Base')} | Topic: {meta.get('topic', 'General')}]"
            chunk = f"{header}\n{doc['content']}\n"

            if total_chars + len(chunk) > max_chars:
                break

            context_parts.append(chunk)
            total_chars += len(chunk)

        return "\n---\n".join(context_parts)

    def collection_stats(self) -> dict:
        """Return statistics about the vector store collection."""
        count = self.collection.count()
        return {
            "collection": self.COLLECTION_NAME,
            "total_chunks": count,
            "persist_dir": self.persist_dir,
        }
