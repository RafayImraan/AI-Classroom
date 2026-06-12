import os
import glob
import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import DistanceStrategy


class TextbookRAG:
    """Retrieval-Augmented Generation system for school textbooks."""

    def __init__(self, textbooks_dir="data/textbooks"):
        self.textbooks_dir = textbooks_dir
        self.vector_store = None
        self.embeddings = None
        self._initialized = False

    def initialize(self):
        """Initialize embeddings and load existing index if available."""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
            )

            index_path = os.path.join(self.textbooks_dir, "faiss_index")
            if os.path.exists(index_path):
                self.vector_store = FAISS.load_local(
                    index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                self._initialized = True
                return True

            self._initialized = True
            return True
        except Exception as e:
            st.warning(f"RAG initialization limited: {str(e)}")
            self._initialized = False
            return False

    def load_pdfs(self):
        """Load all PDFs from the textbooks directory.

        Returns:
            List of Document objects
        """
        pdf_files = glob.glob(os.path.join(self.textbooks_dir, "*.pdf"))
        if not pdf_files:
            st.warning(f"No PDFs found in {self.textbooks_dir}")
            return []

        documents = []
        for pdf_path in pdf_files:
            try:
                reader = PdfReader(pdf_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"

                doc = Document(
                    page_content=text,
                    metadata={"source": os.path.basename(pdf_path)},
                )
                documents.append(doc)
            except Exception as e:
                st.warning(f"Failed to load {pdf_path}: {str(e)}")

        return documents

    def build_index(self):
        """Build FAISS index from textbook PDFs.

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            self.initialize()

        documents = self.load_pdfs()
        if not documents:
            return False

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        chunks = text_splitter.split_documents(documents)

        if not chunks:
            st.warning("No text chunks created from PDFs")
            return False

        try:
            self.vector_store = FAISS.from_documents(
                chunks,
                self.embeddings,
                distance_strategy=DistanceStrategy.COSINE,
            )
            index_path = os.path.join(self.textbooks_dir, "faiss_index")
            self.vector_store.save_local(index_path)
            st.success(f"Index built from {len(chunks)} text chunks")
            return True
        except Exception as e:
            st.error(f"Failed to build FAISS index: {str(e)}")
            return False

    def retrieve_context(self, query, k=3):
        """Retrieve relevant context for a query.

        Args:
            query: Search query (topic/concept)
            k: Number of chunks to retrieve

        Returns:
            Concatenated context string, or empty string
        """
        if not self._initialized:
            self.initialize()

        if self.vector_store is None:
            st.info("No textbook index available. Running without RAG context.")
            return ""

        try:
            docs = self.vector_store.similarity_search(query, k=k)
            context = "\n\n".join(
                [f"[From {doc.metadata.get('source', 'textbook')}]:\n{doc.page_content}" for doc in docs]
            )
            return context
        except Exception as e:
            st.warning(f"Context retrieval failed: {str(e)}")
            return ""

    def is_index_available(self):
        """Check if a FAISS index exists.

        Returns:
            True if index exists
        """
        index_path = os.path.join(self.textbooks_dir, "faiss_index")
        return os.path.exists(index_path)


@st.cache_resource
def get_rag_system():
    """Get singleton RAG system instance."""
    rag = TextbookRAG()
    rag.initialize()
    return rag
