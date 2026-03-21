"""
Unit tests cho RAG Retriever module.
"""
import os
import shutil
import pytest
from app.agent.rag.retriever import PolicyRetriever


@pytest.fixture
def temp_retriever(tmp_path):
    """Tạo PolicyRetriever với temp directory."""
    os.environ["CHROMA_DB_DIR"] = str(tmp_path / "test_chroma")
    retriever = PolicyRetriever.__new__(PolicyRetriever)
    import chromadb
    retriever._client = chromadb.PersistentClient(path=str(tmp_path / "test_chroma"))
    retriever._collection = None
    return retriever


class TestPolicyRetriever:
    """Test PolicyRetriever class."""

    def test_init(self, temp_retriever):
        """Test khởi tạo retriever."""
        assert temp_retriever._client is not None

    def test_get_collection(self, temp_retriever):
        """Test lấy/tạo collection."""
        collection = temp_retriever._get_collection()
        assert collection is not None

    def test_index_and_retrieve(self, temp_retriever):
        """Test index documents rồi retrieve."""
        # Index sample data
        texts = [
            "Bảo hiểm vật chất xe ô tô bao gồm va chạm, đâm, lật xe.",
            "Trường hợp loại trừ: lái xe khi say rượu, không có bằng lái.",
            "Phạm vi bảo hiểm: thiệt hại do tai nạn giao thông.",
        ]
        metadatas = [
            {"source": "test_policy.txt", "insurer": "TEST"},
            {"source": "test_policy.txt", "insurer": "TEST"},
            {"source": "test_policy.txt", "insurer": "TEST"},
        ]
        ids = ["test_0", "test_1", "test_2"]

        temp_retriever.index_documents(texts=texts, metadatas=metadatas, ids=ids)

        # Verify index
        stats = temp_retriever.get_stats()
        assert stats["total_chunks"] == 3

        # Retrieve
        result = temp_retriever.retrieve("tai nạn va chạm xe", k=2)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "[RAG] Chưa có tài liệu" not in result

    def test_retrieve_empty_collection(self, temp_retriever):
        """Test retrieve khi chưa có documents."""
        result = temp_retriever.retrieve("test query")
        assert "Chưa có tài liệu" in result

    def test_get_stats_empty(self, temp_retriever):
        """Test stats khi collection rỗng."""
        stats = temp_retriever.get_stats()
        assert stats["total_chunks"] == 0
        assert stats["collection_name"] == "insurance_policies"

    def test_index_documents_upsert(self, temp_retriever):
        """Test upsert: index cùng ID không tạo duplicate."""
        texts = ["Document 1"]
        ids = ["doc_1"]
        temp_retriever.index_documents(texts=texts, ids=ids)
        assert temp_retriever.get_stats()["total_chunks"] == 1

        # Upsert cùng ID
        texts = ["Document 1 updated"]
        temp_retriever.index_documents(texts=texts, ids=ids)
        assert temp_retriever.get_stats()["total_chunks"] == 1


class TestTextSplitter:
    """Test text splitting function."""

    def test_split_text_basic(self):
        """Test split text cơ bản."""
        from app.agent.rag.index_policies import split_text
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunks = split_text(text, chunk_size=50, overlap=0)
        assert len(chunks) >= 1
        assert all(len(c) > 0 for c in chunks)

    def test_split_text_long(self):
        """Test split text dài thành nhiều chunks."""
        from app.agent.rag.index_policies import split_text
        text = "\n\n".join([f"Đoạn văn số {i} với nội dung dài." * 5 for i in range(20)])
        chunks = split_text(text, chunk_size=200, overlap=50)
        assert len(chunks) > 1

    def test_split_text_empty(self):
        """Test split text rỗng."""
        from app.agent.rag.index_policies import split_text
        chunks = split_text("", chunk_size=100, overlap=0)
        assert len(chunks) == 0
