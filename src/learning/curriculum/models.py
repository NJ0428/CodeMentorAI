"""
커리큘럼 모델
학습 콘텐츠 데이터 모델 정의
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class DifficultyLevel(str, Enum):
    """난이도 수준"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseType(str, Enum):
    """연습 문제 유형"""
    CODE_COMPLETION = "code_completion"      # 코드 완성
    BUG_FIXING = "bug_fixing"                # 버그 수정
    CODE_REFACTORING = "code_refactoring"    # 코드 리팩토링
    CONCEPTUAL = "conceptual"                # 개념 이해
    PROJECT = "project"                      # 프로젝트


@dataclass
class Exercise:
    """연습 문제 모델"""
    id: str
    title: str
    description: str
    exercise_type: ExerciseType
    difficulty: DifficultyLevel
    topic: str
    starter_code: Optional[str] = None
    solution: Optional[str] = None
    hints: List[str] = field(default_factory=list)
    time_estimate: int = 30  # minutes
    xp_reward: int = 10
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    test_cases: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "exercise_type": self.exercise_type.value,
            "difficulty": self.difficulty.value,
            "topic": self.topic,
            "starter_code": self.starter_code,
            "solution": self.solution,
            "hints": self.hints,
            "time_estimate": self.time_estimate,
            "xp_reward": self.xp_reward,
            "prerequisites": self.prerequisites,
            "learning_objectives": self.learning_objectives,
            "test_cases": self.test_cases
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Exercise':
        """딕셔너리에서 인스턴스 생성"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            exercise_type=ExerciseType(data["exercise_type"]),
            difficulty=DifficultyLevel(data["difficulty"]),
            topic=data["topic"],
            starter_code=data.get("starter_code"),
            solution=data.get("solution"),
            hints=data.get("hints", []),
            time_estimate=data.get("time_estimate", 30),
            xp_reward=data.get("xp_reward", 10),
            prerequisites=data.get("prerequisites", []),
            learning_objectives=data.get("learning_objectives", []),
            test_cases=data.get("test_cases", [])
        )


@dataclass
class Topic:
    """학습 주제 모델"""
    id: str
    title: str
    description: str
    level: DifficultyLevel
    order: int
    exercises: List[Exercise] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    estimated_duration: int = 60  # minutes
    tags: List[str] = field(default_factory=list)
    completed: bool = False

    def add_exercise(self, exercise: Exercise):
        """연습 문제 추가"""
        self.exercises.append(exercise)

    def get_total_xp(self) -> int:
        """총 XP 계산"""
        return sum(exercise.xp_reward for exercise in self.exercises)

    def get_total_time(self) -> int:
        """총 예상 시간 계산"""
        base_time = self.estimated_duration
        exercise_time = sum(exercise.time_estimate for exercise in self.exercises)
        return base_time + exercise_time

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level.value,
            "order": self.order,
            "exercises": [exercise.to_dict() for exercise in self.exercises],
            "learning_objectives": self.learning_objectives,
            "estimated_duration": self.estimated_duration,
            "tags": self.tags,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':
        """딕셔너리에서 인스턴스 생성"""
        exercises = [Exercise.from_dict(ex_data) for ex_data in data.get("exercises", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            level=DifficultyLevel(data["level"]),
            order=data["order"],
            exercises=exercises,
            learning_objectives=data.get("learning_objectives", []),
            estimated_duration=data.get("estimated_duration", 60),
            tags=data.get("tags", []),
            completed=data.get("completed", False)
        )


@dataclass
class LearningPath:
    """학습 경로 모델"""
    id: str
    name: str
    level: DifficultyLevel
    topics: List[Topic] = field(default_factory=list)
    description: str = ""
    total_xp: int = 0
    estimated_duration: int = 0  # hours
    tags: List[str] = field(default_factory=list)

    def add_topic(self, topic: Topic):
        """주제 추가"""
        self.topics.append(topic)
        self.topics.sort(key=lambda t: t.order)

    def get_total_topics(self) -> int:
        """총 주제 수 반환"""
        return len(self.topics)

    def get_completed_topics(self) -> int:
        """완료된 주제 수 반환"""
        return sum(1 for topic in self.topics if topic.completed)

    def calculate_completion_rate(self) -> float:
        """완료율 계산"""
        total = self.get_total_topics()
        if total == 0:
            return 0.0
        completed = self.get_completed_topics()
        return (completed / total) * 100

    def calculate_total_xp(self) -> int:
        """총 XP 계산"""
        return sum(topic.get_total_xp() for topic in self.topics)

    def calculate_total_duration(self) -> int:
        """총 소요 시간 계산 (시간)"""
        total_minutes = sum(topic.get_total_time() for topic in self.topics)
        return total_minutes // 60

    def get_topic_by_id(self, topic_id: str) -> Optional[Topic]:
        """ID로 주제 찾기"""
        for topic in self.topics:
            if topic.id == topic_id:
                return topic
        return None

    def get_next_topic(self, completed_topic_id: str) -> Optional[Topic]:
        """다음 주제 찾기"""
        current_topic = self.get_topic_by_id(completed_topic_id)
        if not current_topic:
            return None

        # 다음 순서의 주제 찾기
        for topic in self.topics:
            if topic.order == current_topic.order + 1:
                return topic
        return None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "topics": [topic.to_dict() for topic in self.topics],
            "description": self.description,
            "total_xp": self.total_xp,
            "estimated_duration": self.estimated_duration,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningPath':
        """딕셔너리에서 인스턴스 생성"""
        topics = [Topic.from_dict(topic_data) for topic_data in data.get("topics", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            level=DifficultyLevel(data["level"]),
            topics=topics,
            description=data.get("description", ""),
            total_xp=data.get("total_xp", 0),
            estimated_duration=data.get("estimated_duration", 0),
            tags=data.get("tags", [])
        )


# 학습 상태 모델
@dataclass
class LearningState:
    """학습 상태 모델"""
    user_id: int
    current_level: DifficultyLevel
    current_topic_id: Optional[str] = None
    current_exercise_id: Optional[str] = None
    total_xp: int = 0
    completed_exercises: List[str] = field(default_factory=list)
    learning_streak: int = 0
    last_activity: Optional[str] = None

    def add_xp(self, xp: int):
        """XP 추가"""
        self.total_xp += xp

    def complete_exercise(self, exercise_id: str):
        """연습 문제 완료"""
        if exercise_id not in self.completed_exercises:
            self.completed_exercises.append(exercise_id)

    def increment_streak(self):
        """연승 증가"""
        self.learning_streak += 1

    def reset_streak(self):
        """연승 리셋"""
        self.learning_streak = 0

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "user_id": self.user_id,
            "current_level": self.current_level.value,
            "current_topic_id": self.current_topic_id,
            "current_exercise_id": self.current_exercise_id,
            "total_xp": self.total_xp,
            "completed_exercises": self.completed_exercises,
            "learning_streak": self.learning_streak,
            "last_activity": self.last_activity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningState':
        """딕셔너리에서 인스턴스 생성"""
        return cls(
            user_id=data["user_id"],
            current_level=DifficultyLevel(data["current_level"]),
            current_topic_id=data.get("current_topic_id"),
            current_exercise_id=data.get("current_exercise_id"),
            total_xp=data.get("total_xp", 0),
            completed_exercises=data.get("completed_exercises", []),
            learning_streak=data.get("learning_streak", 0),
            last_activity=data.get("last_activity")
        )


if __name__ == "__main__":
    # 모델 테스트
    print("🧪 커리큘럼 모델 테스트")

    # Exercise 테스트
    exercise = Exercise(
        id="ex_001",
        title="Hello World",
        description="첫 번째 프로그램 작성",
        exercise_type=ExerciseType.CODE_COMPLETION,
        difficulty=DifficultyLevel.BEGINNER,
        topic="기초",
        starter_code='print("Hello, ___!")',
        hints=["따옴표 안에 내용을 채우세요"],
        learning_objectives=["print 함수 사용법 익히기"]
    )
    print(f"✅ Exercise 생성: {exercise.title}")

    # Topic 테스트
    topic = Topic(
        id="topic_001",
        title="Python 기초",
        description="Python의 기본 문법 학습",
        level=DifficultyLevel.BEGINNER,
        order=1,
        learning_objectives=["변수, 데이터 타입, 기본 연산자 이해"]
    )
    topic.add_exercise(exercise)
    print(f"✅ Topic 생성: {topic.title} (XP: {topic.get_total_xp()})")

    # LearningPath 테스트
    learning_path = LearningPath(
        id="path_beginner",
        name="Python 초급 과정",
        level=DifficultyLevel.BEGINNER,
        description="Python 프로그래밍의 기초를 배웁니다"
    )
    learning_path.add_topic(topic)
    print(f"✅ LearningPath 생성: {learning_path.name}")
    print(f"   완료율: {learning_path.calculate_completion_rate():.1f}%")
    print(f"   총 주제: {learning_path.get_total_topics()}개")

    print("\n🎉 모든 모델 테스트 통과!")