"""
Insurance AI Agents Module.

Chứa 2 agent chính:
    - Agent 1 (Triage Agent): Phân loại sự cố phức tạp/không phức tạp
    - Agent 2 (Coverage Agent): Kiểm tra điều kiện bồi thường sơ bộ

Mỗi agent sử dụng RAG context từ ChromaDB + LLM (OpenAI-compatible API).
"""
import json
import os
from openai import OpenAI
from app.core.config import agent_settings
from app.rag.retriever import policy_retriever
from app.models.agent.schemas import IncidentInput, TriageOutput, CoverageOutput


def _get_llm_client() -> OpenAI:
    """
    Tạo OpenAI client.
    Hỗ trợ cả OpenAI gốc và proxy (Manus, vLLM, LiteLLM...).
    Nếu OPENAI_BASE_URL được set trong env, client sẽ tự dùng.
    """
    return OpenAI(
        api_key=agent_settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
    )


def _call_llm(prompt: str, model: str = None) -> str:
    """
    Gọi LLM và trả về response text.

    Args:
        prompt: Prompt đầy đủ gửi cho LLM.
        model: Tên model (mặc định từ config).

    Returns:
        Nội dung response từ LLM.
    """
    client = _get_llm_client()
    model = model or agent_settings.AGENT_LLM_MODEL

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia bảo hiểm ô tô Việt Nam. Luôn trả lời bằng JSON hợp lệ."},
            {"role": "user", "content": prompt}
        ],
        temperature=agent_settings.AGENT_LLM_TEMPERATURE,
        max_tokens=1500
    )
    return response.choices[0].message.content


def _parse_json_response(content: str) -> dict:
    """
    Parse JSON từ LLM response (hỗ trợ cả markdown code block).

    Args:
        content: Raw response text từ LLM.

    Returns:
        Dict parsed từ JSON.
    """
    # Loại bỏ markdown code block nếu có
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    return json.loads(content.strip())


class InsuranceAgents:
    """
    Lớp chứa logic cho 2 AI Agent trong workflow bồi thường bảo hiểm.

    Agent 1 (Triage Agent):
        - Input: Thông tin sự cố từ user
        - Process: RAG truy xuất luật + LLM phân loại
        - Output: {is_complex: bool, description: str}

    Agent 2 (Coverage Agent):
        - Input: Thông tin sự cố + kết quả Agent 1
        - Process: RAG truy xuất điều khoản bảo hiểm + LLM đánh giá
        - Output: {is_eligible: bool, description: str}
    """

    # ================================================================
    # AGENT 1: TRIAGE AGENT (Policy + Rule Engine)
    # ================================================================
    def run_triage_agent(self, incident: IncidentInput) -> TriageOutput:
        """
        Agent 1: Đánh giá sơ bộ mức độ phức tạp của sự cố.

        Workflow:
            1. Tạo query từ thông tin sự cố
            2. RAG truy xuất điều khoản liên quan từ ChromaDB
            3. Gửi prompt + context cho LLM phân loại
            4. Parse kết quả JSON

        Args:
            incident: Thông tin sự cố từ user.

        Returns:
            TriageOutput với is_complex (True/False) và mô tả lý do.
        """
        # 1. Tạo RAG query
        rag_query = (
            f"tai nạn xe ô tô, "
            f"có người bị thương: {'có' if incident.injuries else 'không'}, "
            f"có bên thứ ba: {'có' if incident.third_party_involved else 'không'}, "
            f"xe còn chạy được: {'có' if incident.vehicle_drivable else 'không'}, "
            f"sự cố: {incident.description}"
        )

        # 2. Truy xuất context từ RAG
        rag_context = policy_retriever.retrieve(rag_query, k=5)

        # 3. Xây dựng prompt cho LLM
        prompt = f"""Bạn là Agent phân loại sự cố bảo hiểm ô tô (Triage Agent).

## Thông tin sự cố từ người dùng:
- Thời gian: {incident.time}
- Địa điểm: {incident.location}
- Mô tả sự cố: {incident.description}
- Có bên thứ ba liên quan: {"Có" if incident.third_party_involved else "Không"}
- Xe còn chạy được: {"Có" if incident.vehicle_drivable else "Không"}
- Có người bị thương: {"Có" if incident.injuries else "Không"}

## Điều khoản bảo hiểm tham khảo (từ RAG):
{rag_context}

## Tiêu chí phân loại "Phức tạp" (is_complex = true):
1. Có người bị thương hoặc tử vong
2. Có liên quan đến bên thứ ba (xe khác, người đi bộ, tài sản người khác)
3. Tai nạn liên hoàn (từ 3 xe trở lên)
4. Xe không thể di chuyển + cần cứu hộ
5. Xảy ra trên đường cao tốc
6. Thiệt hại ước tính lớn (>100 triệu VNĐ)

## Yêu cầu:
Phân tích kỹ thông tin sự cố, đối chiếu với điều khoản bảo hiểm, và trả về JSON:
{{
    "is_complex": true hoặc false,
    "description": "Giải thích chi tiết lý do phân loại, dẫn chiếu điều khoản cụ thể nếu có."
}}

Chỉ trả về JSON, không thêm text nào khác."""

        # 4. Gọi LLM
        try:
            raw_response = _call_llm(prompt)
            result = _parse_json_response(raw_response)
            return TriageOutput(
                is_complex=result.get("is_complex", True),
                description=result.get("description", "Không thể phân tích chi tiết.")
            )
        except Exception as e:
            # Fallback: nếu LLM lỗi, mặc định là phức tạp (an toàn hơn)
            return TriageOutput(
                is_complex=True,
                description=f"[Fallback] Lỗi phân tích LLM: {str(e)}. Mặc định phân loại là phức tạp để đảm bảo an toàn."
            )

    # ================================================================
    # AGENT 2: COVERAGE AGENT (Coverage Pre-check)
    # ================================================================
    def run_coverage_agent(self, incident: IncidentInput) -> CoverageOutput:
        """
        Agent 2: Kiểm tra điều kiện bồi thường sơ bộ.

        Chỉ chạy khi Agent 1 phân loại sự cố là KHÔNG phức tạp.

        Workflow:
            1. Tạo query từ thông tin sự cố + nhà bảo hiểm
            2. RAG truy xuất điều khoản bồi thường + loại trừ
            3. Gửi prompt + context cho LLM đánh giá eligibility
            4. Parse kết quả JSON

        Args:
            incident: Thông tin sự cố từ user.

        Returns:
            CoverageOutput với is_eligible (True/False) và mô tả lý do.
        """
        # 1. Tạo RAG query tập trung vào coverage
        insurer = incident.insurer or "chung"
        rag_query = (
            f"điều kiện bồi thường bảo hiểm {insurer}, "
            f"loại trừ bảo hiểm, phạm vi bảo hiểm, "
            f"sự cố: {incident.description}"
        )

        # 2. Truy xuất context từ RAG
        rag_context = policy_retriever.retrieve(rag_query, k=5)

        # 3. Xây dựng prompt cho LLM
        prompt = f"""Bạn là Agent kiểm tra điều kiện bồi thường bảo hiểm ô tô (Coverage Agent).

## Thông tin sự cố:
- Mô tả: {incident.description}
- Thời gian: {incident.time}
- Địa điểm: {incident.location}
- Nhà bảo hiểm: {insurer}
- Mã hợp đồng: {incident.policy_id or "Không rõ"}

## Điều khoản bảo hiểm tham khảo (từ RAG):
{rag_context}

## Nhiệm vụ:
1. Kiểm tra sự cố có nằm trong PHẠM VI BẢO HIỂM không
2. Kiểm tra sự cố có thuộc TRƯỜNG HỢP LOẠI TRỪ không
3. Đánh giá sơ bộ khả năng được bồi thường

## Yêu cầu:
Trả về JSON:
{{
    "is_eligible": true (đủ điều kiện sơ bộ) hoặc false (không đủ/bị loại trừ),
    "description": "Giải thích chi tiết: phạm vi bảo hiểm áp dụng, có loại trừ nào không, và kết luận."
}}

Chỉ trả về JSON, không thêm text nào khác."""

        # 4. Gọi LLM
        try:
            raw_response = _call_llm(prompt)
            result = _parse_json_response(raw_response)
            return CoverageOutput(
                is_eligible=result.get("is_eligible", False),
                description=result.get("description", "Không thể phân tích chi tiết.")
            )
        except Exception as e:
            return CoverageOutput(
                is_eligible=False,
                description=f"[Fallback] Lỗi phân tích LLM: {str(e)}. Không thể xác nhận điều kiện bồi thường."
            )


# Singleton instance
insurance_agents = InsuranceAgents()
