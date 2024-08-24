from __future__ import annotations
import os
from typing import Literal, Iterator
import httpx

from dotenv import load_dotenv

from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain.tools.retriever import create_retriever_tool
from langchain.prompts import PromptTemplate
from langchain.document_loaders.base import BaseLoader
from langchain.docstore.document import Document
from langchain_qdrant import QdrantVectorStore as Qdrant
from langchain.indexes import SQLRecordManager, index
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")


def create_vector_store(
    collection_name: str,
    event_hooks: dict | None = None,
    aevent_hooks: dict | None = None,
) -> Qdrant:
    """
    Create a Qdrant vector store for the given collection name.

    Args:
        collection_name (str): The name of the Qdrant collection.
        event_hooks (dict, optional): Event hooks for the HTTP client. Defaults to None.
        aevent_hooks (dict, optional): Event hooks for the async HTTP client. Defaults to None.

    Returns:
        Qdrant: The Qdrant vector store instance.
    """

    qdrant = QdrantClient(QDRANT_HOST)
    qdrant_async = AsyncQdrantClient(QDRANT_HOST)

    event_hooks = {} if event_hooks is None else event_hooks
    aevent_hooks = {} if aevent_hooks is None else aevent_hooks

    embeddings = OpenAIEmbeddings(
        http_async_client=httpx.AsyncClient(event_hooks=aevent_hooks),
        http_client=httpx.Client(event_hooks=event_hooks),
    )

    if not qdrant.collection_exists(collection_name):
        qdrant.create_collection(
            collection_name,
            vectors_config=VectorParams(distance=Distance.COSINE, size=1536),
        )

    return Qdrant(
        client=qdrant,
        # async_client=qdrant_async,
        collection_name=collection_name,
        embedding=embeddings,
    )


def create_record_manager(ns: str, db: str | None = None) -> SQLRecordManager:
    """
    Create a SQLRecordManager for the given namespace.

    Args:
        ns (str): The namespace for the SQLRecordManager.
        db (str, optional): The database URL. Defaults to None, in which case the Postgres URL is used.

    Returns:
        SQLRecordManager: The SQLRecordManager instance.
    """

    manager = SQLRecordManager(ns, db_url="sqlite:///record_manager_cache.sql")
    manager.create_schema()

    return manager


def create_indexer(*args, **kwargs) -> Indexer:
    return Indexer(*args, **kwargs)


class Indexer:
    def __init__(
        self,
        ns: str,
        db: str | None = None,
        cleanup: Literal["incremental", "full"] = "incremental",
        source_key: str = "source",
        event_hooks: dict | None = None,
        aevent_hooks: dict | None = None,
    ):
        """
        Initialize the Indexer.

        Args:
            ns (str): The namespace for the indexer.
            db (str, optional): The database URL. Defaults to None, in which case the Postgres URL is used.
            cleanup (str, optional): The cleanup strategy for the indexer. Defaults to "incremental".
            source (str, optional): The source ID key for the indexer. Defaults to "source".
            event_hooks (dict, optional): Event hooks for the HTTP client. Defaults to None.
            aevent_hooks (dict, optional): Event hooks for the async HTTP client. Defaults to None.
        """

        self.ns = ns
        self.db = db
        self.cleanup: Literal["incremental", "full"] = cleanup
        self.source_key = source_key
        self.event_hooks = event_hooks or {}
        self.aevent_hooks = aevent_hooks or {}

        self.vector_store = self._create_vector_store()
        self.record_manager = self._create_record_manager()

    def retriever_tool(self):
        doc_prompt = PromptTemplate(
            input_variables=["page_content", "source"],
            template="{source}\n{page_content}",
        )

        return create_retriever_tool(
            document_prompt=doc_prompt,
            document_separator="\n\n",
            retriever=self.retriever,
            name="retrieve_context",
            description="useful for retrieving relevant information from the context",
        )

    @property
    def retriever(self):
        return self.vector_store.as_retriever()

    def compressor(
        self, chunk_size=1000, chunk_overlap=100, similarity_threshold=0.3, k=10
    ):
        embeddings = OpenAIEmbeddings()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        relevance_filter = EmbeddingsFilter(
            embeddings=embeddings, similarity_threshold=similarity_threshold
        )
        compressor = DocumentCompressorPipeline(
            transformers=[splitter, relevance_filter]
        )

        return ContextualCompressionRetriever(
            base_retriever=self.vector_store.as_retriever(search_kwargs={"k": k}),
            base_compressor=compressor,
        )

    def _create_vector_store(self) -> Qdrant:
        """Create a Qdrant vector store for the given namespace."""

        return create_vector_store(self.ns, self.event_hooks, self.aevent_hooks)

    def _create_record_manager(self) -> SQLRecordManager:
        """
        Create a SQLRecordManager.

        Returns:
            SQLRecordManager: The SQLRecordManager instance.
        """

        return create_record_manager(
            ns=self.ns,
            db=self.db,
        )

    def __call__(self, documents: Iterator[Document] | BaseLoader):
        self.index(documents)

    def index(self, documents: Iterator[Document] | BaseLoader):
        """Index the given documents."""

        result = index(
            documents,
            record_manager=self.record_manager,
            vector_store=self.vector_store,
            cleanup=self.cleanup,
            source_id_key=self.source_key,
        )

        print(result)

    def clear(self):
        """Clear the indexed content."""
        index(
            [],
            record_manager=self.record_manager,
            vector_store=self.vector_store,
            cleanup="full",
            source_id_key=self.source_key,
        )
