"""
Script index tài liệu bảo hiểm vào ChromaDB.

Đọc tất cả file .txt trong thư mục data/, split thành chunks,
và lưu vào ChromaDB persistent storage.

Usage:
    cd backend
    python -m app.agent.rag.index_policies

Lưu ý: Không cần API key vì dùng ChromaDB default embedding (ONNX local).
"""
import os
import re
from app.agent.rag.retriever import policy_retriever

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def split_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """
    Split text thành các chunks với overlap.

    Args:
        text: Nội dung text cần split.
        chunk_size: Kích thước tối đa mỗi chunk (ký tự).
        overlap: Số ký tự overlap giữa 2 chunks liên tiếp.

    Returns:
        Danh sách text chunks.
    """
    # Split theo đoạn (double newline) trước
    paragraphs = re.split(r'\n\n+', text)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk += ("\n\n" + para) if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # Bắt đầu chunk mới với overlap từ chunk trước
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-overlap:]
                current_chunk = overlap_text + "\n\n" + para
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def index_text_policies():
    """Load và index tất cả file policy .txt vào ChromaDB."""
    text_files = [f for f in os.listdir(DATA_DIR) if f.startswith("policy_") and f.endswith(".txt")]

    if not text_files:
        print("[Index] Không tìm thấy file policy nào trong", DATA_DIR)
        return

    all_chunks = []
    all_metadatas = []
    all_ids = []
    chunk_counter = 0

    for fname in sorted(text_files):
        path = os.path.join(DATA_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Lấy tên insurer từ filename
        insurer = fname.replace("policy_", "").replace(".txt", "").upper()

        chunks = split_text(content, chunk_size=800, overlap=150)
        print(f"[Index] {fname}: {len(chunks)} chunks (insurer: {insurer})")

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": fname,
                "insurer": insurer,
                "chunk_index": i
            })
            all_ids.append(f"{insurer}_chunk_{chunk_counter}")
            chunk_counter += 1

    # Index vào ChromaDB
    policy_retriever.index_documents(
        texts=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids
    )

    # In thống kê
    stats = policy_retriever.get_stats()
    print(f"[Index] Hoàn tất! Total chunks: {stats['total_chunks']}")
    print(f"[Index] ChromaDB dir: {stats['chroma_db_dir']}")


if __name__ == "__main__":
    index_text_policies()
