from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Gemini API
    GEMINI_API_KEY: str
    
    # MT5 Configuration
    MT5_LOGIN: Optional[int] = 0
    MT5_PASSWORD: Optional[str] = ""
    MT5_SERVER: str = "ICMarkets-Demo"
    
    # OANDA Configuration (for live prices) - Optional
    OANDA_API_KEY: Optional[str] = ""
    OANDA_ACCOUNT_ID: Optional[str] = ""
    OANDA_BASE_URL: str = "https://api-fxpractice.oanda.com/v3"
    
    # Database - Optional
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "trading_system"
    POSTGRES_USER: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] = "postgres"
    
    # Trading Parameters
    SYMBOLS: str = "XAUUSD,GBPUSD,USDJPY"
    TIMEFRAMES: str = "M15,H1,H4,D1"
    RISK_PER_TRADE: float = 0.01  # 1%
    MAX_DAILY_RISK: float = 0.03  # 3%
    MIN_CONFIDENCE: int = 70
    MIN_RR_RATIO: float = 2.0
    MAX_SIGNALS_PER_DAY: int = 10
    
    # Telegram
    TELEGRAM_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # System
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    FRONTEND_URL_PRODUCTION: str = "https://alphaforge.com"
    BACKEND_PORT: int = 8000
    BACKEND_HOST: str = "0.0.0.0"
    
    @property
    def database_url(self) -> str:
        if self.POSTGRES_USER and self.POSTGRES_PASSWORD:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return None
    
    @property
    def PORT(self) -> int:
        """Alias for BACKEND_PORT"""
        return self.BACKEND_PORT
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()