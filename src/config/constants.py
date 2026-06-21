"""
애플리케이션 상수 정의
전체 애플리케이션에서 사용하는 상수 값들
"""

from enum import Enum


class Level(str, Enum):
    """사용자 수준"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AnalysisType(str, Enum):
    """분석 유형"""
    SYNTAX = "syntax"
    STYLE = "style"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    PERFORMANCE = "performance"
    FULL = "full"


class MessageType(str, Enum):
    """메시지 유형"""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"
    ERROR = "error"


class IssueSeverity(str, Enum):
    """이슈 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AchievementType(str, Enum):
    """성취 유형"""
    FIRST_CODE = "first_code"
    FIRST_SUBMISSION = "first_submission"
    PERFECT_SCORE = "perfect_score"
    STREAK_5 = "streak_5"
    STREAK_10 = "streak_10"
    COMPLETED_TOPIC = "completed_topic"
    LEVEL_UP = "level_up"
    BUG_HUNTER = "bug_hunter"
    CODE_OPTIMIZER = "code_optimizer"


class TabType(str, Enum):
    """UI 탭 유형"""
    CODE_ANALYSIS = "code_analysis"
    LEARNING = "learning"
    CHAT = "chat"


# 애플리케이션 정보
APP_NAME = "CodeMentorAI"
APP_VERSION = "0.1.0"
APP_AUTHOR = "CodeMentorAI Team"

# UI 관련 상수
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MINIMUM_WINDOW_WIDTH = 800
MINIMUM_WINDOW_HEIGHT = 600

# 코드 에디터 관련
CODE_FONT_FAMILY = "Consolas"
CODE_FONT_SIZE = 10
TAB_WIDTH = 4
LINE_NUMBER_WIDTH = 40

# 코드 분석 관련
MAX_CODE_LENGTH = 10000
DEFAULT_TIMEOUT = 30
ANALYSIS_CACHE_TTL = 3600

# 학습 관련
DEFAULT_LEVELS = ["beginner", "intermediate", "advanced"]
TOPICS = [
    "variables",
    "data_types",
    "control_flow",
    "functions",
    "classes",
    "modules",
    "file_handling",
    "error_handling",
    "testing",
    "advanced_concepts"
]

# 점수 관련
MIN_SCORE = 1
MAX_SCORE = 10
PASSING_SCORE = 7

# 테마 색상
THEME_COLORS = {
    "default": {
        "background": "#ffffff",
        "foreground": "#000000",
        "accent": "#0078d4",
        "code_bg": "#f5f5f5",
        "error": "#d13438",
        "warning": "#ff8c00",
        "success": "#107c10",
        "info": "#0078d4"
    },
    "dark": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "accent": "#007acc",
        "code_bg": "#252526",
        "error": "#f48771",
        "warning": "#cca700",
        "success": "#89d185",
        "info": "#75beff"
    }
}

# 파일 필터
FILE_FILTERS = [
    ("Python Files", "*.py"),
    ("Text Files", "*.txt"),
    ("All Files", "*.*")
]

# 데이터베이스 관련
DEFAULT_DB_NAME = "codementorai.db"
BACKUP_DIR = "backups"

# API 관련
API_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1

# 로그 관련
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
LOG_ROTATION = "10 MB"
LOG_RETENTION = "1 month"

# 성취 관련
ACHIEVEMENT_ICONS = {
    AchievementType.FIRST_CODE: "🎉",
    AchievementType.FIRST_SUBMISSION: "📝",
    AchievementType.PERFECT_SCORE: "⭐",
    AchievementType.STREAK_5: "🔥",
    AchievementType.STREAK_10: "💯",
    AchievementType.COMPLETED_TOPIC: "🎯",
    AchievementType.LEVEL_UP: "📈",
    AchievementType.BUG_HUNTER: "🐛",
    AchievementType.CODE_OPTIMIZER: "🚀"
}

# 프롬프트 템플릿 경로
PROMPT_TEMPLATES = {
    "code_analysis": "resources/prompts/code_analysis.txt",
    "tutoring": "resources/prompts/tutoring.txt",
    "optimization": "resources/prompts/optimization.txt"
}

# 커리큘럼 경로
CURRICULUM_PATHS = {
    Level.BEGINNER: "resources/curriculum/beginner/",
    Level.INTERMEDIATE: "resources/curriculum/intermediate/",
    Level.ADVANCED: "resources/curriculum/advanced/"
}