"""
애플리케이션 설정 관리
환경 변수와 설정 파일을 통한 애플리케이션 설정 관리
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


@dataclass
class APISettings:
    """API 관련 설정"""
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    claude_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3
    rate_limit_requests: int = 60
    rate_limit_period: int = 60  # seconds


@dataclass
class DatabaseSettings:
    """데이터베이스 관련 설정"""
    path: str = field(default_factory=lambda: os.getenv("DATABASE_PATH", "sqlite:///codementorai.db"))
    echo_sql: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class LoggingSettings:
    """로깅 관련 설정"""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    file_path: str = field(default_factory=lambda: os.getenv("LOG_FILE_PATH", "logs/codementorai.log"))
    rotation: str = "10 MB"
    retention: str = "1 month"
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


@dataclass
class UISettings:
    """UI 관련 설정"""
    theme: str = field(default_factory=lambda: os.getenv("THEME", "light"))
    language: str = field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "ko"))
    window_width: int = 1200
    window_height: int = 800
    font_family: str = "Consolas"
    font_size: int = 10
    auto_save_interval: int = field(default_factory=lambda: int(os.getenv("AUTO_SAVE_INTERVAL", "300")))


@dataclass
class LearningSettings:
    """학습 관련 설정"""
    default_level: str = "beginner"  # beginner, intermediate, advanced
    max_exercises_per_session: int = 10
    feedback_detail_level: str = "medium"  # simple, medium, detailed
    enable_achievements: bool = True
    progress_update_frequency: int = 60  # seconds


@dataclass
class CodeAnalysisSettings:
    """코드 분석 관련 설정"""
    enable_pylint: bool = True
    enable_pep8: bool = True
    enable_bandit: bool = True
    enable_radon: bool = True
    max_code_length: int = 10000  # characters
    cache_results: bool = True
    cache_ttl: int = 3600  # seconds


class Settings:
    """메인 설정 클래스"""

    def __init__(self):
        self.api = APISettings()
        self.database = DatabaseSettings()
        self.logging = LoggingSettings()
        self.ui = UISettings()
        self.learning = LearningSettings()
        self.code_analysis = CodeAnalysisSettings()

        # 필요한 디렉토리 생성
        self._create_directories()

    def _create_directories(self):
        """필요한 디렉토리 생성"""
        # 로그 디렉토리
        log_dir = Path(self.logging.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # 데이터베이스 디렉토리
        if "sqlite:///" in self.database.path:
            db_path = self.database.path.replace("sqlite:///", "")
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> bool:
        """설정 유효성 검사"""
        if not self.api.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        return True

    def get_api_key(self) -> str:
        """API 키 반환"""
        return self.api.anthropic_api_key


# 전역 설정 인스턴스
settings = Settings()


if __name__ == "__main__":
    # 설정 테스트
    try:
        settings.validate()
        print("✅ 설정 유효성 검사 통과")
        print(f"📊 데이터베이스: {settings.database.path}")
        print(f"🎨 테마: {settings.ui.theme}")
        print(f"📝 로그 레벨: {settings.logging.level}")
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")