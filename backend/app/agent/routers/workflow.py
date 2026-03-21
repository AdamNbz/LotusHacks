"""
API Router cho AI Agent Workflow.

Endpoints:
    POST /workflow/process-incident  - Xử lý sự cố qua 2 Agent
    GET  /workflow/rag-stats         - Thống kê RAG vectorstore
    POST /workflow/index-policies    - Trigger index lại policy documents
"""
from fastapi import APIRouter, HTTPException
from app.agent.models.schemas import (
    IncidentInput,
    WorkflowResponse,
    TriageOutput,
    CoverageOutput
)
from app.agent.agents.insurance_agents import insurance_agents
from app.agent.rag.retriever import policy_retriever

router = APIRouter(prefix="/workflow", tags=["AI Agent Workflow"])


@router.post("/process-incident", response_model=WorkflowResponse)
async def process_incident(incident: IncidentInput):
    """
    Xử lý sự cố bảo hiểm qua pipeline 2 Agent.

    **Workflow:**
    1. Agent 1 (Triage): Phân loại sự cố phức tạp/không phức tạp
    2. Nếu phức tạp → Assisted Mode (hotline + hướng dẫn khẩn cấp)
    3. Nếu không phức tạp → Agent 2 (Coverage): Kiểm tra điều kiện bồi thường

    **Input:** IncidentInput (thông tin sự cố từ user)
    **Output:** WorkflowResponse (kết quả 2 agent + bước tiếp theo)
    """
    # ---- AGENT 1: TRIAGE ----
    try:
        triage_result = insurance_agents.run_triage_agent(incident)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent 1 (Triage) lỗi: {str(e)}"
        )

    # ---- ROUTING LOGIC ----
    if triage_result.is_complex:
        # Sự cố phức tạp → Assisted Mode
        return WorkflowResponse(
            triage_result=triage_result,
            coverage_result=None,
            next_step="ASSISTED_MODE: Hướng dẫn khẩn cấp + hotline + giữ hiện trường. Thu first notice tối thiểu + bằng chứng ban đầu. Chuyển theo dõi hồ sơ / phối hợp insurer.",
            assisted_mode={
                "emergency_hotline": "113 (Công an) / 115 (Cấp cứu)",
                "insurer_hotline": _get_insurer_hotline(incident.insurer),
                "instructions": [
                    "Giữ nguyên hiện trường nếu có thể",
                    "Gọi cấp cứu nếu có người bị thương",
                    "Gọi công an nếu có bên thứ ba",
                    "Chụp ảnh hiện trường từ nhiều góc",
                    "Thu thập thông tin nhân chứng",
                    "Không di chuyển xe trước khi công an đến (trừ trường hợp nguy hiểm)"
                ]
            }
        )

    # ---- AGENT 2: COVERAGE PRE-CHECK ----
    try:
        coverage_result = insurance_agents.run_coverage_agent(incident)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent 2 (Coverage) lỗi: {str(e)}"
        )

    # Xác định next step dựa trên kết quả Agent 2
    if coverage_result.is_eligible:
        next_step = "ELIGIBLE: Đủ điều kiện sơ bộ → Sinh checklist hồ sơ theo insurer → Upload documents."
    else:
        next_step = "NOT_ELIGIBLE: Cảnh báo nguy cơ bị từ chối → Gợi ý không claim / tự sửa ngoài / lưu sự cố."

    return WorkflowResponse(
        triage_result=triage_result,
        coverage_result=coverage_result,
        next_step=next_step,
        assisted_mode=None
    )


@router.get("/rag-stats")
async def get_rag_stats():
    """Trả về thống kê ChromaDB vectorstore."""
    return policy_retriever.get_stats()


@router.post("/index-policies")
async def trigger_index_policies():
    """
    Trigger index lại policy documents vào ChromaDB.
    Dùng khi thêm file policy mới vào thư mục data/.
    """
    try:
        from app.agent.rag.index_policies import index_text_policies
        index_text_policies()
        return {"status": "ok", "stats": policy_retriever.get_stats()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index lỗi: {str(e)}")


def _get_insurer_hotline(insurer: str | None) -> str:
    """Trả về hotline của nhà bảo hiểm."""
    hotlines = {
        "Bảo Việt": "1800 599 945",
        "PTI": "1800 1567",
        "MIC": "1900 9466",
        "PVI": "1900 545 458",
        "Bảo Minh": "1900 558 891",
    }
    if insurer and insurer in hotlines:
        return hotlines[insurer]
    return "Liên hệ nhà bảo hiểm của bạn"
