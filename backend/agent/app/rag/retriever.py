"""
RAG Retriever Module - Truy xuất tài liệu bảo hiểm từ ChromaDB.

Sử dụng ChromaDB native với default embedding (all-MiniLM-L6-v2 ONNX)
để không phụ thuộc vào OpenAI Embeddings API.
Phù hợp cho máy không có GPU mạnh (chạy CPU, ONNX runtime).
"""
import os
import chromadb

# Đường dẫn mặc định cho ChromaDB persistent storage
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CHROMA_DB_DIR = os.getenv(
    "CHROMA_DB_DIR",
    os.path.join(DATA_DIR, "chroma_db")
)

# Tên collection mặc định
COLLECTION_NAME = "insurance_policies"


class PolicyRetriever:
    """
    RAG module sử dụng ChromaDB native để index và truy xuất policy documents.

    Workflow:
        1. index_documents() - Load text files, split chunks, lưu vào ChromaDB
        2. retrieve() - Tìm kiếm semantic similarity từ query

    Embedding: ChromaDB default (all-MiniLM-L6-v2 ONNX) - chạy local, không cần API key.
    """

    def __init__(self):
        """Khởi tạo ChromaDB client với persistent storage."""
        self._client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self._collection = None

    def _get_collection(self):
        """Lấy hoặc tạo collection."""
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}  # Cosine similarity
            )
        return self._collection

    def index_documents(self, texts: list[str], metadatas: list[dict] = None, ids: list[str] = None):
        """
        Index danh sách text chunks vào ChromaDB.

        Args:
            texts: Danh sách text chunks cần index.
            metadatas: Metadata cho mỗi chunk (source file, page, etc.).
            ids: ID duy nhất cho mỗi chunk.
        """
        collection = self._get_collection()

        if ids is None:
            ids = [f"chunk_{i}" for i in range(len(texts))]
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in texts]

        collection.upsert(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"[RAG] Indexed {len(texts)} chunks into collection '{COLLECTION_NAME}'.")

    def retrieve(self, query: str, k: int = 5) -> str:
        """
        Truy xuất context liên quan từ ChromaDB dựa trên query.

        Args:
            query: Câu hỏi hoặc mô tả sự cố từ user.
            k: Số lượng chunks trả về (top-k).

        Returns:
            Chuỗi text chứa các chunks liên quan, ngăn cách bằng dấu phân cách.
        """
        collection = self._get_collection()

        if collection.count() == 0:
            return "[RAG] Chưa có tài liệu nào được index. Vui lòng chạy index_policies trước."

        results = collection.query(
            query_texts=[query],
            n_results=min(k, collection.count())
        )

        # Ghép các documents trả về thành context string
        documents = results.get("documents", [[]])[0]
        if not documents:
            return "[RAG] Không tìm thấy tài liệu liên quan."

        context = "\n\n---\n\n".join(documents)
        return context

    def get_stats(self) -> dict:
        """Trả về thống kê collection hiện tại."""
        collection = self._get_collection()
        return {
            "collection_name": COLLECTION_NAME,
            "total_chunks": collection.count(),
            "chroma_db_dir": CHROMA_DB_DIR
        }


# Singleton instance - dùng chung cho toàn bộ application
policy_retriever = PolicyRetriever()
