"""
Pydantic Schemas cho AI Agent workflow.

Định nghĩa input/output cho:
    - Agent 1 (Triage): Phân loại sự cố
    - Agent 2 (Coverage): Kiểm tra điều kiện bồi thường
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class IncidentType(str, Enum):
    """Loại sự cố theo phân loại VETC."""
    COLLISION = "va_cham"               # Va chạm
    SCRATCH = "tray_xuoc"               # Trầy xước / Móp nhẹ
    GLASS_BREAK = "vo_kinh"             # Vỡ kính
    FLOOD = "ngap_nuoc"                 # Ngập nước / Thủy kích
    THEFT = "mat_cap"                   # Mất cắp bộ phận
    OTHER = "khac"                      # Sự cố khác


class IncidentInput(BaseModel):
    """
    Input schema cho workflow xử lý sự cố.

    Bao gồm các trường thu thập từ AI Interview:
    - Thông tin sự cố cơ bản (thời gian, địa điểm, mô tả)
    - Đánh giá tình trạng (bên thứ 3, thương tích, xe chạy được)
    - Thông tin bảo hiểm (policy, insurer)
    - Thông tin xe và lái xe
    - Thông tin bổ sung (nhân chứng, ảnh, biên bản)
    """
    # --- Thông tin sự cố cơ bản (từ AI Interview) ---
    time: str = Field(..., description="Thời gian xảy ra sự cố (VD: 2024-06-15 08:30)")
    location: str = Field(..., description="Địa điểm xảy ra sự cố, có thể kèm GPS")
    description: str = Field(..., description="Mô tả chi tiết sự cố từ user")
    incident_type: IncidentType = Field(
        default=IncidentType.OTHER,
        description="Loại sự cố (va_cham, tray_xuoc, vo_kinh, ngap_nuoc, mat_cap, khac)"
    )

    # --- Đánh giá tình trạng ---
    third_party_involved: bool = Field(..., description="Có bên thứ ba liên quan không")
    vehicle_drivable: bool = Field(..., description="Xe còn chạy được không")
    injuries: bool = Field(..., description="Có người bị thương không")

    # --- Thông tin bảo hiểm ---
    policy_id: Optional[str] = Field(None, description="Mã hợp đồng bảo hiểm")
    insurer: Optional[str] = Field(None, description="Tên công ty bảo hiểm (VD: Bảo Việt, PTI, MIC)")

    # --- Thông tin xe & lái xe (Điều 7 - Hồ sơ bồi thường) ---
    vehicle_plate: Optional[str] = Field(None, description="Biển số xe")
    vehicle_model: Optional[str] = Field(None, description="Hãng xe và đời xe")
    driver_license: Optional[str] = Field(None, description="Số GPLX người điều khiển")

    # --- Thông tin bổ sung ---
    estimated_damage: Optional[float] = Field(None, description="Ước tính thiệt hại (VNĐ)")
    witnesses: Optional[List[str]] = Field(default_factory=list, description="Danh sách nhân chứng")
    police_report: Optional[bool] = Field(False, description="Đã có biên bản công an chưa")
    photos_taken: Optional[bool] = Field(False, description="Đã chụp ảnh hiện trường chưa")
    notes: Optional[str] = Field(None, description="Ghi chú thêm từ user")


class TriageOutput(BaseModel):
    """
    Output schema cho Agent 1 (Triage Agent).

    Phân loại sự cố thành 2 class:
        - is_complex = True  -> Chuyển Assisted Mode
        - is_complex = False -> Tiếp tục AI Claim Flow (Agent 2)
    """
    is_complex: bool = Field(..., description="True nếu sự cố phức tạp, False nếu đơn giản")
    description: str = Field(..., description="Giải thích lý do phân loại, dẫn chiếu điều khoản")


class CoverageOutput(BaseModel):
    """
    Output schema cho Agent 2 (Coverage Agent).

    Kiểm tra điều kiện bồi thường sơ bộ:
        - is_eligible = True  -> Đủ điều kiện, sinh checklist hồ sơ
        - is_eligible = False -> Cảnh báo nguy cơ bị từ chối
    """
    is_eligible: bool = Field(..., description="True nếu đủ điều kiện sơ bộ, False nếu không")
    description: str = Field(..., description="Giải thích chi tiết về phạm vi bảo hiểm và loại trừ")


class WorkflowResponse(BaseModel):
    """
    Response schema cho toàn bộ workflow (Agent 1 + Agent 2).
    """
    triage_result: TriageOutput = Field(..., description="Kết quả phân loại từ Agent 1")
    coverage_result: Optional[CoverageOutput] = Field(
        None, description="Kết quả kiểm tra bồi thường từ Agent 2 (None nếu sự cố phức tạp)"
    )
    next_step: str = Field(..., description="Bước tiếp theo trong workflow")
    assisted_mode: Optional[dict] = Field(
        None, description="Thông tin hỗ trợ khẩn cấp (chỉ khi sự cố phức tạp)"
    )
