"""
학습 관리자
학습 시스템의 중앙 관리 시스템
"""
from typing import Dict, Any, List, Optional
from loguru import logger

from src.learning.curriculum import CurriculumManager, get_curriculum_manager
from src.learning.progress import ProgressTracker, get_progress_tracker
from src.learning.achievements import AchievementManager, get_achievement_manager
from src.learning.progress.adaptive_difficulty import AdaptiveDifficulty, get_adaptive_difficulty
from src.learning.curriculum.models import DifficultyLevel, Exercise


class LearningManager:
    """학습 관리자 - 모든 학습 시스템 컴포넌트 통합"""

    def __init__(self, database_manager, session_manager):
        self.db = database_manager
        self.session_manager = session_manager

        # 하위 시스템 초기화
        self.curriculum_manager = get_curriculum_manager()
        self.progress_tracker = get_progress_tracker(database_manager, session_manager)
        self.achievement_manager = get_achievement_manager(database_manager)
        self.adaptive_difficulty = get_adaptive_difficulty(database_manager)

        logger.info("학습 관리자 초기화 완료")

    def get_curriculum(self, level: DifficultyLevel):
        """커리큘럼 반환"""
        return self.curriculum_manager.get_curriculum(level)

    def get_all_curricula(self) -> Dict[DifficultyLevel, Any]:
        """모든 커리큘럼 반환"""
        return self.curriculum_manager.get_all_curricula()

    def get_topic(self, level: DifficultyLevel, topic_id: str) -> Optional:
        """특정 주제 반환"""
        return self.curriculum_manager.get_topic(level, topic_id)

    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """연습 문제 반환"""
        return self.curriculum_manager.get_exercise(exercise_id)

    def get_topic_exercises(self, level: str, topic_id: str) -> List[Exercise]:
        """주제별 연습 문제 목록 반환"""
        try:
            level_enum = DifficultyLevel(level)
            return self.curriculum_manager.get_topic_exercises(level_enum, topic_id)
        except Exception as e:
            logger.error(f"주제 연습 문제 로드 실패: {e}")
            return []

    def start_exercise(self, user_id: int, exercise: Exercise) -> Dict[str, Any]:
        """연습 문제 시작"""
        return self.progress_tracker.start_exercise(user_id, exercise)

    def submit_exercise(
        self,
        user_id: int,
        exercise: Exercise,
        code: str
    ) -> Dict[str, Any]:
        """연습 문제 제출"""
        try:
            # 코드 제출
            result = self.progress_tracker.submit_exercise_solution(
                user_id=user_id,
                exercise=exercise,
                code=code
            )

            if result.get("success"):
                # 성취 확인
                event_data = {
                    "score": result.get("analysis", {}).get("score", 0),
                    "exercise_id": exercise.id,
                    "topic": exercise.topic
                }

                achievements = self.achievement_manager.check_and_award_achievements(
                    user_id=user_id,
                    event_type="exercise_submit",
                    event_data=event_data
                )

                result["new_achievements"] = achievements

                # 완료된 경우 추가 이벤트 처리
                if result.get("completed"):
                    complete_achievements = self.achievement_manager.check_and_award_achievements(
                        user_id=user_id,
                        event_type="exercise_complete",
                        event_data=event_data
                    )
                    result["new_achievements"].extend(complete_achievements)

            return result

        except Exception as e:
            logger.error(f"연습 문제 제출 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_user_progress_summary(self, user_id: int) -> Dict[str, Any]:
        """사용자 진도 요약"""
        return self.progress_tracker.get_user_progress_summary(user_id)

    def get_topic_progress(
        self,
        user_id: int,
        topic: str,
        level: DifficultyLevel
    ) -> Dict[str, Any]:
        """특정 주제의 진도 정보"""
        return self.progress_tracker.get_topic_progress(user_id, topic, level)

    def recommend_exercise(
        self,
        user_id: int,
        topic: Optional[str] = None,
        count: int = 1
    ) -> List[Exercise]:
        """다음 연습 문제 추천"""
        return self.adaptive_difficulty.recommend_exercise(user_id, topic, count)

    def assess_user_level(self, user_id: int) -> Dict[str, Any]:
        """사용자 수준 평가"""
        return self.adaptive_difficulty.assess_user_level(user_id)

    def get_personalized_learning_path(self, user_id: int) -> Dict[str, Any]:
        """개인화된 학습 경로 생성"""
        return self.adaptive_difficulty.get_personalized_learning_path(user_id)

    def get_user_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """사용자 성취 목록 조회"""
        return self.achievement_manager.get_user_achievements(user_id)

    def get_achievement_stats(self, user_id: int) -> Dict[str, Any]:
        """성취 통계"""
        return self.achievement_manager.get_achievement_stats(user_id)

    def get_available_achievements(self) -> List[Dict[str, Any]]:
        """획득 가능한 모든 성취 목록"""
        return self.achievement_manager.get_available_achievements()

    def check_achievement_progress(
        self,
        user_id: int,
        achievement_type: str
    ) -> Dict[str, Any]:
        """특정 성취의 진도 확인"""
        return self.achievement_manager.check_achievement_progress(user_id, achievement_type)

    def get_next_achievements(self, user_id: int, count: int = 3) -> List[Dict[str, Any]]:
        """다음 획득 가능한 성취 추천"""
        return self.achievement_manager.get_next_achievements(user_id, count)

    def adjust_exercise_difficulty(
        self,
        base_exercise: Exercise,
        user_performance: Dict[str, Any]
    ) -> Exercise:
        """연습 문제 난이도 조절"""
        return self.adaptive_difficulty.adjust_exercise_difficulty(base_exercise, user_performance)

    def get_curriculum_stats(self, level: DifficultyLevel) -> Dict[str, Any]:
        """커리큘럼 통계 정보"""
        return self.curriculum_manager.get_curriculum_stats(level)

    def refresh_curriculum_cache(self, level: Optional[DifficultyLevel] = None):
        """커리큘럼 캐시 새로고침"""
        self.curriculum_manager.refresh_cache(level)

    def get_system_status(self) -> Dict[str, Any]:
        """학습 시스템 상태 반환"""
        try:
            return {
                "curriculum_loaded": len(self.curriculum_manager.get_all_curricula()) > 0,
                "progress_tracker_active": self.progress_tracker is not None,
                "achievement_manager_active": self.achievement_manager is not None,
                "adaptive_difficulty_active": self.adaptive_difficulty is not None,
                "database_connected": self.db is not None,
                "session_manager_active": self.session_manager is not None
            }
        except Exception as e:
            logger.error(f"시스템 상태 확인 실패: {e}")
            return {"error": str(e)}


# 전역 인스턴스
_learning_manager = None


def get_learning_manager(database_manager, session_manager) -> LearningManager:
    """학습 관리자 인스턴스 반환"""
    global _learning_manager
    if _learning_manager is None:
        _learning_manager = LearningManager(database_manager, session_manager)
    return _learning_manager


if __name__ == "__main__":
    # 학습 관리자 테스트
    print("🧪 학습 관리자 테스트")

    # 더미 데이터베이스 관리자와 세션 관리자
    class DummyDB:
        pass

    class DummySession:
        pass

    db = DummyDB()
    session_mgr = DummySession()

    manager = get_learning_manager(db, session_mgr)

    # 시스템 상태 확인
    status = manager.get_system_status()
    print(f"✅ 학습 시스템 상태:")
    for key, value in status.items():
        print(f"   {key}: {value}")

    # 커리큘럼 로드
    curriculum = manager.get_curriculum(DifficultyLevel.BEGINNER)
    if curriculum:
        print(f"✅ 커리큘럼 로드: {curriculum.name}")

    # 사용자 진도 요약
    progress_summary = manager.get_user_progress_summary(1)
    print(f"✅ 사용자 진도: {progress_summary.get('total_completed', 0)}/{progress_summary.get('total_items', 0)} 완료")

    print("\n🎉 학습 관리자 테스트 통과!")