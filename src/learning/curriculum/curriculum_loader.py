"""
커리큘럼 로더
JSON 파일에서 커리큘럼 데이터를 로드
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from src.learning.curriculum.models import LearningPath, Topic, Exercise, DifficultyLevel


class CurriculumLoader:
    """커리큘럼 데이터 로더"""

    def __init__(self, curriculum_base_path: str = "resources/curriculum"):
        self.curriculum_base_path = Path(curriculum_base_path)
        logger.info(f"커리큘럼 로더 초기화: {curriculum_base_path}")

    def load_level(self, level: DifficultyLevel) -> Optional[LearningPath]:
        """특정 레벨의 커리큘럼 로드"""
        try:
            level_path = self.curriculum_base_path / level.value
            if not level_path.exists():
                logger.warning(f"커리큘럼 경로 없음: {level_path}")
                return self._create_default_curriculum(level)

            # 학습 경로 로드
            learning_path_file = level_path / "learning_path.json"
            if not learning_path_file.exists():
                logger.warning(f"학습 경로 파일 없음: {learning_path_file}")
                return self._create_default_curriculum(level)

            with open(learning_path_file, 'r', encoding='utf-8') as f:
                learning_path_data = json.load(f)

            learning_path = LearningPath.from_dict(learning_path_data)

            # 주제들 로드
            topics_file = level_path / "topics.json"
            if topics_file.exists():
                with open(topics_file, 'r', encoding='utf-8') as f:
                    topics_data = json.load(f)

                for topic_data in topics_data.get("topics", []):
                    topic = Topic.from_dict(topic_data)
                    learning_path.add_topic(topic)

            logger.info(f"커리큘럼 로드 완료: {level.value} ({learning_path.get_total_topics()}개 주제)")
            return learning_path

        except Exception as e:
            logger.error(f"커리큘럼 로드 실패 ({level.value}): {e}")
            return self._create_default_curriculum(level)

    def load_topic(self, level: DifficultyLevel, topic_id: str) -> Optional[Topic]:
        """특정 주제 로드"""
        try:
            level_path = self.curriculum_base_path / level.value
            topic_file = level_path / f"topic_{topic_id}.json"

            if topic_file.exists():
                with open(topic_file, 'r', encoding='utf-8') as f:
                    topic_data = json.load(f)
                return Topic.from_dict(topic_data)
            else:
                # topics.json에서 찾기
                topics_file = level_path / "topics.json"
                if topics_file.exists():
                    with open(topics_file, 'r', encoding='utf-8') as f:
                        topics_data = json.load(f)

                    for topic_data in topics_data.get("topics", []):
                        if topic_data["id"] == topic_id:
                            return Topic.from_dict(topic_data)

            logger.warning(f"주제를 찾을 수 없음: {topic_id}")
            return None

        except Exception as e:
            logger.error(f"주제 로드 실패 ({topic_id}): {e}")
            return None

    def load_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """연습 문제 로드"""
        try:
            # 모든 레벨 검색
            for level in DifficultyLevel:
                level_path = self.curriculum_base_path / level.value
                exercises_file = level_path / "exercises.json"

                if exercises_file.exists():
                    with open(exercises_file, 'r', encoding='utf-8') as f:
                        exercises_data = json.load(f)

                    for exercise_data in exercises_data.get("exercises", []):
                        if exercise_data["id"] == exercise_id:
                            return Exercise.from_dict(exercise_data)

            logger.warning(f"연습 문제를 찾을 수 없음: {exercise_id}")
            return None

        except Exception as e:
            logger.error(f"연습 문제 로드 실패 ({exercise_id}): {e}")
            return None

    def load_all_exercises(self, level: DifficultyLevel) -> list[Exercise]:
        """레벨별 모든 연습 문제 로드"""
        try:
            level_path = self.curriculum_base_path / level.value
            exercises_file = level_path / "exercises.json"

            if not exercises_file.exists():
                logger.warning(f"연습 문제 파일 없음: {exercises_file}")
                return []

            with open(exercises_file, 'r', encoding='utf-8') as f:
                exercises_data = json.load(f)

            exercises = [Exercise.from_dict(ex_data) for ex_data in exercises_data.get("exercises", [])]
            logger.info(f"연습 문제 로드 완료: {level.value} ({len(exercises)}개)")
            return exercises

        except Exception as e:
            logger.error(f"연습 문제 로드 실패 ({level.value}): {e}")
            return []

    def save_curriculum(self, learning_path: LearningPath) -> bool:
        """커리큘럼 저장"""
        try:
            level_path = self.curriculum_base_path / learning_path.level.value
            level_path.mkdir(parents=True, exist_ok=True)

            # 학습 경로 저장
            learning_path_file = level_path / "learning_path.json"
            with open(learning_path_file, 'w', encoding='utf-8') as f:
                json.dump(learning_path.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"커리큘럼 저장 완료: {learning_path.level.value}")
            return True

        except Exception as e:
            logger.error(f"커리큘럼 저장 실패: {e}")
            return False

    def _create_default_curriculum(self, level: DifficultyLevel) -> LearningPath:
        """기본 커리큘럼 생성"""
        logger.info(f"기본 커리큘럼 생성: {level.value}")

        learning_path = LearningPath(
            id=f"default_{level.value}",
            name=f"Python {level.value.capitalize()} Course",
            level=level,
            description="기본 학습 과정"
        )

        # 기본 주제들
        if level == DifficultyLevel.BEGINNER:
            default_topics = [
                Topic(
                    id="basics",
                    title="Python 기초",
                    description="Python의 기본 문법과 개념을 학습합니다",
                    level=level,
                    order=1,
                    learning_objectives=[
                        "변수와 데이터 타입 이해",
                        "기본 연산자 사용법",
                        "입력과 출력"
                    ],
                    estimated_duration=60
                ),
                Topic(
                    id="control_flow",
                    title="제어 흐름",
                    description="조건문과 반복문을 학습합니다",
                    level=level,
                    order=2,
                    learning_objectives=[
                        "if/elif/else 조건문",
                        "for/while 반복문",
                        "break와 continue"
                    ],
                    estimated_duration=90
                )
            ]
        elif level == DifficultyLevel.INTERMEDIATE:
            default_topics = [
                Topic(
                    id="functions",
                    title="함수",
                    description="함수의 정의와 활용을 학습합니다",
                    level=level,
                    order=1,
                    learning_objectives=[
                        "함수 정의와 호출",
                        "매개변수와 반환값",
                        "람다 함수"
                    ],
                    estimated_duration=120
                )
            ]
        else:  # ADVANCED
            default_topics = [
                Topic(
                    id="oop",
                    title="객체 지향 프로그래밍",
                    description="클래스와 객체를 학습합니다",
                    level=level,
                    order=1,
                    learning_objectives=[
                        "클래스와 객체",
                        "상속과 다형성",
                        "캡슐화"
                    ],
                    estimated_duration=180
                )
            ]

        for topic in default_topics:
            learning_path.add_topic(topic)

        return learning_path


# 전역 인스턴스
_curriculum_loader = None


def get_curriculum_loader(curriculum_path: str = "resources/curriculum") -> CurriculumLoader:
    """커리큘럼 로더 인스턴스 반환"""
    global _curriculum_loader
    if _curriculum_loader is None:
        _curriculum_loader = CurriculumLoader(curriculum_path)
    return _curriculum_loader


if __name__ == "__main__":
    # 커리큘럼 로더 테스트
    print("🧪 커리큘럼 로더 테스트")

    loader = get_curriculum_loader()

    # 초급 커리큘럼 로드
    beginner_path = loader.load_level(DifficultyLevel.BEGINNER)
    if beginner_path:
        print(f"✅ 초급 커리큘럼: {beginner_path.name}")
        print(f"   주제 수: {beginner_path.get_total_topics()}")
        for topic in beginner_path.topics:
            print(f"   - {topic.title}")

    # 중급 커리큘럼 로드
    intermediate_path = loader.load_level(DifficultyLevel.INTERMEDIATE)
    if intermediate_path:
        print(f"✅ 중급 커리큘럼: {intermediate_path.name}")
        print(f"   주제 수: {intermediate_path.get_total_topics()}")

    print("\n🎉 커리큘럼 로더 테스트 통과!")