"""
Cấu hình tập trung cho AI Agent module.
Đọc từ file .env hoặc biến môi trường hệ thống.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class AgentSettings:
    """
    Tập hợp các cấu hình cần thiết cho AI Agent.
    Ưu tiên đọc từ biến môi trường để đảm bảo bảo mật khi deploy Docker.
    """
    # LLM API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    
    # Agent Config
    AGENT_LLM_MODEL: str = os.getenv("AGENT_LLM_MODEL", "gpt-4.1-mini")
    AGENT_LLM_TEMPERATURE: float = float(os.getenv("AGENT_LLM_TEMPERATURE", "0"))
    
    # ChromaDB
    CHROMA_DB_DIR: str = os.getenv(
        "CHROMA_DB_DIR",
        os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")
    )
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "lotushacks")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "10080"))
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

agent_settings = AgentSettings()
