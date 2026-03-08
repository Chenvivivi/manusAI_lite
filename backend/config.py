import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-reasoner"
    
    # 搜索引擎配置（可选）
    TAVILY_API_KEY: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None
    QIANFAN_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略额外的字段

settings = Settings()
