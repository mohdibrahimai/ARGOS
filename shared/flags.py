"""Feature flags and configuration options for ARGOS.

These flags centralise configuration of embedding models, LLM providers and
indexing backends.  Values can be overridden via environment variables.
"""

import os


class Flags:
    """Container for ARGOS feature flags.

    Flags are resolved from environment variables, falling back to defaults
    defined here.  Each flag controls a specific aspect of the system.
    """

    # Embedding provider: "e5" for intfloat/multilingual-e5-base, "openai" for OpenAI embeddings
    EMBEDDINGS_PROVIDER: str = os.getenv("ARGOS_EMBEDDINGS_PROVIDER", "e5")

    # LLM provider for answer generation: "openai", "anthropic", or "local" for a stubbed model
    LLM_PROVIDER: str = os.getenv("ARGOS_LLM_PROVIDER", "local")

    # Vector index backend: "faiss" or "qdrant"; note that qdrant is only available in production
    INDEX_BACKEND: str = os.getenv("ARGOS_INDEX_BACKEND", "faiss")

    # Strict mode depth: number of multi-hop retrieval iterations
    STRICT_DEPTH: int = int(os.getenv("ARGOS_STRICT_DEPTH", "2"))

    # Retriever top k: number of candidate passages to return per query
    RETRIEVER_TOP_K: int = int(os.getenv("ARGOS_RETRIEVER_TOP_K", "6"))

    # Enable debug logging
    DEBUG: bool = os.getenv("ARGOS_DEBUG", "false").lower() == "true"


FLAGS = Flags()

__all__ = ["FLAGS"]