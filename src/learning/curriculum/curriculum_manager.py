"""
커리큘럼 관리자
학습 커리큘럼의 중앙 관리 시스템
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from src.learning.curriculum.models import LearningPath, Topic, Exercise, DifficultyLevel, LearningState
from src.learning.curriculum.curriculum_loader import CurriculumLoader, get_curriculum_loader
from src.learning.curriculum.exercise_generator import ExerciseGenerator, get_exercise_generator


class CurriculumManager:
    """커리큘럼 관리자"""

    def __init__(self, curriculum_path: str = "resources/curriculum"):
        self.curriculum_loader = get_curriculum_loader(curriculum_path)
        self.exercise_generator = get_exercise_generator()
        self._curriculum_cache = {}
        self._user_states = {}
        logger.info("커리큘럼 관리자 초기화 완료")

    def get_curriculum(self, level: DifficultyLevel) -> Optional[LearningPath]:
        """레벨별 커리큘럼 반환"""
        try:
            cache_key = f"curriculum_{level.value}"
            if cache_key not in self._curriculum_cache:
                self._curriculum_cache[cache_key] = self.curriculum_loader.load_level(level)
            return self._curriculum_cache[cache_key]
        except Exception as e:
            logger.error(f"커리큘럼 로드 실패 ({level.value}): {e}")
            return None

    def get_all_curricula(self) -> Dict[DifficultyLevel, LearningPath]:
        """모든 레벨의 커리큘럼 반환"""
        try:
            curricula = {}
            for level in DifficultyLevel:
                curriculum = self.get_curriculum(level)
                if curriculum:
                    curricula[level] = curriculum
            return curricula
        except Exception as e:
            logger.error(f"모든 커리큘럼 로드 실패: {e}")
            return {}

    def get_topic(self, level: DifficultyLevel, topic_id: str) -> Optional[Topic]:
        """특정 주제 반환"""
        try:
            curriculum = self.get_curriculum(level)
            if curriculum:
                return curriculum.get_topic_by_id(topic_id)
            return None
        except Exception as e:
            logger.error(f"주제 로드 실패 ({topic_id}): {e}")
            return None

    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """연습 문제 반환"""
        try:
            return self.curriculum_loader.load_exercise(exercise_id)
        except Exception as e:
            logger.error(f"연습 문제 로드 실패 ({exercise_id}): {e}")
            return None

    def get_topic_exercises(self, level: DifficultyLevel, topic_id: str) -> List[Exercise]:
        """주제별 연습 문제 목록 반환"""
        try:
            topic = self.get_topic(level, topic_id)
            if topic:
                return topic.exercises
            return []
        except Exception as e:
            logger.error(f"주제 연습 문제 로드 실패 ({topic_id}): {e}")
            return []

    def get_next_exercise(
        self,
        user_id: int,
        current_level: DifficultyLevel,
        completed_exercises: List[str]
    ) -> Optional[Exercise]:
        """다음 연습 문제 추천"""
        try:
            curriculum = self.get_curriculum(current_level)
            if not curriculum:
                return None

            # 완료하지 않은 연습 문제 찾기
            for topic in curriculum.topics:
                for exercise in topic.exercises:
                    if exercise.id not in completed_exercises:
                        return exercise

            # 모든 문제를 완료한 경우
            logger.info(f"사용자 {user_id}는 모든 연습 문제를 완료했습니다.")
            return None

        except Exception as e:
            logger.error(f"다음 연습 문제 추천 실패: {e}")
            return None

    def get_personalized_exercises(
        self,
        user_id: int,
        weak_topics: List[str],
        current_level: DifficultyLevel,
        performance_data: Dict[str, Any],
        count: int = 5
    ) -> List[Exercise]:
        """개인화된 연습 문제 추천"""
        try:
            return self.exercise_generator.generate_personalized_exercises(
                user_level=current_level,
                weak_topics=weak_topics,
                recent_performance=performance_data,
                count=count
            )
        except Exception as e:
            logger.error(f"개인화된 연습 문제 생성 실패: {e}")
            return []

    def create_adaptive_exercise(
        self,
        base_exercise: Exercise,
        user_performance: Dict[str, Any]
    ) -> Exercise:
        """사용자 성과에 맞는 적응형 연습 문제 생성"""
        try:
            avg_score = user_performance.get("average_score", 7.0)

            if avg_score < 6.0:
                # 더 쉬운 변형
                return self.exercise_generator.create_variant_exercise(base_exercise, "easier")
            elif avg_score > 8.5:
                # 더 어려운 변형
                return self.exercise_generator.create_variant_exercise(base_exercise, "harder")
            else:
                # 동일한 난이도
                return base_exercise

        except Exception as e:
            logger.error(f"적응형 연습 문제 생성 실패: {e}")
            return base_exercise

    def get_user_learning_state(self, user_id: int) -> LearningState:
        """사용자 학습 상태 반환"""
        try:
            if user_id not in self._user_states:
                # 기본 학습 상태 생성
                self._user_states[user_id] = LearningState(
                    user_id=user_id,
                    current_level=DifficultyLevel.BEGINNER
                )
            return self._user_states[user_id]
        except Exception as e:
            logger.error(f"사용자 학습 상태 로드 실패: {e}")
            return LearningState(
                user_id=user_id,
                current_level=DifficultyLevel.BEGINNER
            )

    def update_user_learning_state(
        self,
        user_id: int,
        topic_id: Optional[str] = None,
        exercise_id: Optional[str] = None,
        xp_earned: int = 0
    ) -> bool:
        """사용자 학습 상태 업데이트"""
        try:
            state = self.get_user_learning_state(user_id)

            if topic_id:
                state.current_topic_id = topic_id

            if exercise_id:
                state.current_exercise_id = exercise_id
                state.complete_exercise(exercise_id)

            if xp_earned > 0:
                state.add_xp(xp_earned)

            logger.info(f"사용자 {user_id} 학습 상태 업데이트: XP {xp_earned}")
            return True

        except Exception as e:
            logger.error(f"사용자 학습 상태 업데이트 실패: {e}")
            return False

    def assess_user_level(
        self,
        user_id: int,
        completed_exercises: List[str],
        average_score: float
    ) -> DifficultyLevel:
        """사용자 수준 평가"""
        try:
            state = self.get_user_learning_state(user_id)

            # 평균 점수 기반 레벨 추천
            if average_score >= 8.5 and len(completed_exercises) >= 10:
                recommended_level = DifficultyLevel.ADVANCED
            elif average_score >= 7.0 and len(completed_exercises) >= 5:
                recommended_level = DifficultyLevel.INTERMEDIATE
            else:
                recommended_level = DifficultyLevel.BEGINNER

            # 레벨 업데이트
            if recommended_level != state.current_level:
                logger.info(f"사용자 {user_id} 레벨 변경: {state.current_level} -> {recommended_level}")
                state.current_level = recommended_level

            return recommended_level

        except Exception as e:
            logger.error(f"사용자 수준 평가 실패: {e}")
            return DifficultyLevel.BEGINNER

    def get_curriculum_stats(self, level: DifficultyLevel) -> Dict[str, Any]:
        """커리큘럼 통계 정보 반환"""
        try:
            curriculum = self.get_curriculum(level)
            if not curriculum:
                return {}

            total_exercises = sum(len(topic.exercises) for topic in curriculum.topics)
            total_xp = curriculum.calculate_total_xp()
            total_duration = curriculum.calculate_total_duration()

            return {
                "level": level.value,
                "total_topics": curriculum.get_total_topics(),
                "total_exercises": total_exercises,
                "total_xp": total_xp,
                "estimated_hours": total_duration,
                "completion_rate": curriculum.calculate_completion_rate()
            }

        except Exception as e:
            logger.error(f"커리큘럼 통계 로드 실패: {e}")
            return {}

    def refresh_cache(self, level: Optional[DifficultyLevel] = None):
        """커리큘럼 캐시 새로고침"""
        try:
            if level:
                cache_key = f"curriculum_{level.value}"
                if cache_key in self._curriculum_cache:
                    del self._curriculum_cache[cache_key]
                    logger.info(f"커리큘럼 캐시 새로고침: {level.value}")
            else:
                self._curriculum_cache.clear()
                logger.info("모든 커리큘럼 캐시 새로고침")
        except Exception as e:
            logger.error(f"커리큘럼 캐시 새로고침 실패: {e}")


# 전역 인스턴스
_curriculum_manager = None


def get_curriculum_manager(curriculum_path: str = "resources/curriculum") -> CurriculumManager:
    """커리큘럼 관리자 인스턴스 반환"""
    global _curriculum_manager
    if _curriculum_manager is None:
        _curriculum_manager = CurriculumManager(curriculum_path)
    return _curriculum_manager


if __name__ == "__main__":
    # 커리큘럼 관리자 테스트
    print("🧪 커리큘럼 관리자 테스트")

    manager = get_curriculum_manager()

    # 초급 커리큘럼 로드
    beginner_curriculum = manager.get_curriculum(DifficultyLevel.BEGINNER)
    if beginner_curriculum:
        print(f"✅ 초급 커리큘럼: {beginner_curriculum.name}")
        print(f"   주제 수: {beginner_curriculum.get_total_topics()}")

    # 커리큘럼 통계
    stats = manager.get_curriculum_stats(DifficultyLevel.BEGINNER)
    if stats:
        print(f"✅ 커리큘럼 통계:")
        print(f"   총 주제: {stats.get('total_topics')}")
        print(f"   총 연습 문제: {stats.get('total_exercises')}")
        print(f"   총 XP: {stats.get('total_xp')}")

    # 사용자 학습 상태
    state = manager.get_user_learning_state(1)
    print(f"✅ 사용자 학습 상태: 레벨 {state.current_level}")

    # 개인화된 연습 문제
    weak_topics = ["basics", "control_flow"]
    performance = {"average_score": 6.5}
    personalized = manager.get_personalized_exercises(
        user_id=1,
        weak_topics=weak_topics,
        current_level=DifficultyLevel.BEGINNER,
        performance_data=performance,
        count=3
    )
    print(f"✅ 개인화된 연습 문제: {len(personalized)}개")

    print("\n🎉 커리큘럼 관리자 테스트 통과!")