"""
평가 시스템 데이터베이스 마이그레이션
퀴즈, 코딩 문제, 평가 결과, 피드백 테이블 추가
"""
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class DifficultyLevel(str, enum.Enum):
    """난이도 수준"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProblemCategory(str, enum.Enum):
    """문제 카테고리"""
    ALGORITHM = "algorithm"
    DATA_STRUCTURE = "data_structure"
    STRING_MANIPULATION = "string_manipulation"
    MATHEMATICS = "mathematics"
    FUNCTIONAL = "functional"
    CLASS_DESIGN = "class_design"
    DEBUGGING = "debugging"


class EvaluationStatus(str, enum.Enum):
    """평가 상태"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


class Quiz(Base):
    """퀴즈 테이블"""
    __tablename__ = 'quizzes'

    quiz_id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    topic = Column(String(100))
    time_limit = Column(Integer)  # 분 단위
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    results = relationship("QuizResult", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    """퀴즈 문제 테이블"""
    __tablename__ = 'quiz_questions'

    question_id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey('quizzes.quiz_id'), nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, true_false, short_answer 등
    question_text = Column(Text, nullable=False)
    options = Column(JSON)  # 객관식 옵션
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)  # 해설
    points = Column(Integer, default=10)
    tags = Column(JSON)  # 태그 목록
    hints = Column(JSON)  # 힌트 목록
    code_example = Column(Text)  # 코드 예시
    difficulty = Column(SQLEnum(DifficultyLevel))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    quiz = relationship("Quiz", back_populates="questions")


class QuizResult(Base):
    """퀴즈 결과 테이블"""
    __tablename__ = 'quiz_results'

    result_id = Column(String(36), primary_key=True)
    quiz_id = Column(String(36), ForeignKey('quizzes.quiz_id'), nullable=False)
    user_id = Column(Integer, nullable=False)
    answers = Column(JSON)  # 사용자 답안
    score = Column(Float, nullable=False)
    total_points = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_taken = Column(Float, nullable=False)  # 초 단위
    completed_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    quiz = relationship("Quiz", back_populates="results")


class CodingProblem(Base):
    """코딩 문제 테이블"""
    __tablename__ = 'coding_problems'

    problem_id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(ProblemCategory), nullable=False)
    difficulty = Column(String(50), nullable=False)
    starter_code = Column(Text)
    template_code = Column(Text)
    constraints = Column(JSON)  # 제약 조건 목록
    hints = Column(JSON)  # 힌트 목록
    sample_solution = Column(Text)
    time_limit = Column(Float, default=5.0)  # 초 단위
    memory_limit = Column(Integer, default=256)  # MB 단위
    tags = Column(JSON)  # 태그 목록
    points = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    test_cases = relationship("CodingTestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("CodingSubmission", back_populates="problem", cascade="all, delete-orphan")


class CodingTestCase(Base):
    """코딩 테스트 케이스 테이블"""
    __tablename__ = 'coding_test_cases'

    test_id = Column(String(36), primary_key=True)
    problem_id = Column(String(36), ForeignKey('coding_problems.problem_id'), nullable=False)
    input_data = Column(JSON, nullable=False)  # 입력 데이터
    expected_output = Column(JSON, nullable=False)  # 예상 출력
    description = Column(String(500))
    is_hidden = Column(Boolean, default=False)  # 숨겨진 테스트 케이스 여부
    timeout = Column(Float, default=5.0)  # 실행 시간 제한 (초)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    problem = relationship("CodingProblem", back_populates="test_cases")


class CodingSubmission(Base):
    """코딩 제출 테이블"""
    __tablename__ = 'coding_submissions'

    submission_id = Column(String(36), primary_key=True)
    problem_id = Column(String(36), ForeignKey('coding_problems.problem_id'), nullable=False)
    user_id = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    submitted_at = Column(DateTime, default=datetime.utcnow)
    execution_time = Column(Float)  # 실행 시간 (초)
    memory_used = Column(Integer)  # 메모리 사용량 (MB)
    status = Column(SQLEnum(EvaluationStatus), default=EvaluationStatus.PENDING)
    error_message = Column(Text)
    score = Column(Float, default=0.0)
    test_results = Column(JSON)  # 테스트 결과 목록

    # 관계
    problem = relationship("CodingProblem", back_populates="submissions")
    evaluations = relationship("EvaluationResult", back_populates="submission", cascade="all, delete-orphan")


class EvaluationResult(Base):
    """평가 결과 테이블"""
    __tablename__ = 'evaluation_results'

    evaluation_id = Column(String(36), primary_key=True)
    submission_id = Column(String(36), ForeignKey('coding_submissions.submission_id'), nullable=False)
    problem_id = Column(String(36), nullable=False)
    user_id = Column(Integer, nullable=False)
    status = Column(SQLEnum(EvaluationStatus), nullable=False)
    total_tests = Column(Integer, nullable=False)
    passed_tests = Column(Integer, nullable=False)
    failed_tests = Column(Integer, nullable=False)
    test_results = Column(JSON)  # 테스트 결과 상세
    code_quality = Column(JSON)  # 코드 품질 메트릭
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    execution_time = Column(Float, default=0.0)
    memory_used = Column(Integer, default=0)
    feedback = Column(Text)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    submission = relationship("CodingSubmission", back_populates="evaluations")


class Feedback(Base):
    """피드백 테이블"""
    __tablename__ = 'feedbacks'

    feedback_id = Column(String(36), primary_key=True)
    feedback_type = Column(String(50), nullable=False)  # quiz, coding, learning_path, general
    user_id = Column(Integer, nullable=False)
    content_id = Column(String(36), nullable=False)  # 퀴즈 ID, 문제 ID 등
    level = Column(SQLEnum(DifficultyLevel))
    overall_score = Column(Float, nullable=False)
    overall_message = Column(Text)
    encouragement_message = Column(Text)
    strengths = Column(JSON)  # 강점 목록
    weaknesses = Column(JSON)  # 약점 목록
    suggestions = Column(JSON)  # 제안 목록
    achievements = Column(JSON)  # 성취 목록
    learning_recommendations = Column(JSON)  # 학습 추천
    next_steps = Column(JSON)  # 다음 단계
    created_at = Column(DateTime, default=datetime.utcnow)


def upgrade_database():
    """데이터베이스 업그레이드"""
    from src.database.db_manager import get_database_manager

    db_manager = get_database_manager()

    # 새 테이블 생성
    Base.metadata.create_all(db_manager.engine)

    print("✅ 평가 시스템 데이터베이스 마이그레이션 완료")
    print("생성된 테이블:")
    print("  - quizzes")
    print("  - quiz_questions")
    print("  - quiz_results")
    print("  - coding_problems")
    print("  - coding_test_cases")
    print("  - coding_submissions")
    print("  - evaluation_results")
    print("  - feedbacks")


def downgrade_database():
    """데이터베이스 다운그레이드"""
    from src.database.db_manager import get_database_manager
    from sqlalchemy import inspect

    db_manager = get_database_manager()
    inspector = inspect(db_manager.engine)

    # 테이블 삭제 (역순)
    tables_to_drop = [
        'feedbacks',
        'evaluation_results',
        'coding_submissions',
        'coding_test_cases',
        'coding_problems',
        'quiz_results',
        'quiz_questions',
        'quizzes'
    ]

    for table_name in tables_to_drop:
        if inspector.has_table(table_name):
            with db_manager.engine.connect() as conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.commit()
            print(f"✅ {table_name} 테이블 삭제 완료")


if __name__ == "__main__":
    print("🔧 평가 시스템 데이터베이스 마이그레이션")
    print("="*50)

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade_database()
    else:
        upgrade_database()