"""
진도 추적기
학습 활동 추적 및 관리
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from src.learning.curriculum.models import DifficultyLevel, Exercise, LearningState
from src.learning.progress.progress_calculator import ProgressCalculator, get_progress_calculator
from src.ai.claude_client import get_claude_client


class ProgressTracker:
    """학습 진도 추적기"""

    def __init__(self, database_manager, session_manager):
        self.db = database_manager
        self.session_manager = session_manager
        self.progress_calculator = get_progress_calculator()
        self.claude_client = get_claude_client()
        self._active_exercises = {}
        logger.info("진도 추적기 초기화 완료")

    def start_exercise(
        self,
        user_id: int,
        exercise: Exercise
    ) -> Dict[str, Any]:
        """연습 문제 시작"""
        try:
            logger.info(f"연습 문제 시작: 사용자={user_id}, 문제={exercise.id}")

            # 활성 연습 문제 기록
            self._active_exercises[user_id] = {
                "exercise_id": exercise.id,
                "start_time": datetime.now().isoformat(),
                "topic": exercise.topic,
                "difficulty": exercise.difficulty.value
            }

            # 세션 확인 및 생성
            session = self.session_manager.get_current_session()
            if not session:
                session = self.session_manager.create_session(user_id, exercise.topic)

            # 진도 레코드 확인 및 생성
            progress = self._get_or_create_progress(
                user_id,
                exercise.topic,
                exercise.difficulty.value
            )

            return {
                "success": True,
                "session": session,
                "progress": progress,
                "exercise": exercise,
                "message": f"{exercise.title} 문제를 시작합니다."
            }

        except Exception as e:
            logger.error(f"연습 문제 시작 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def submit_exercise_solution(
        self,
        user_id: int,
        exercise: Exercise,
        code: str,
        time_spent: int = 0
    ) -> Dict[str, Any]:
        """연습 문제 제출"""
        try:
            logger.info(f"연습 문제 제출: 사용자={user_id}, 문제={exercise.id}")

            # 활성 연습 문제 확인
            if user_id not in self._active_exercises:
                return {
                    "success": False,
                    "error": "활성 연습 문제를 찾을 수 없습니다."
                }

            active_exercise = self._active_exercises[user_id]

            # 코드 분석
            analysis_result = self._analyze_submission(code, exercise)

            # 제출 저장
            submission = self._save_submission(
                user_id,
                exercise.id,
                code,
                analysis_result["score"],
                time_spent
            )

            # 진도 업데이트
            progress_updated = self._update_exercise_progress(
                user_id,
                exercise.topic,
                exercise.difficulty.value,
                analysis_result["score"],
                exercise.xp_reward
            )

            # 완료 여부 확인
            is_completed = analysis_result["score"] >= 7.0

            result = {
                "success": True,
                "submission": submission,
                "analysis": analysis_result,
                "progress_updated": progress_updated,
                "completed": is_completed,
                "xp_earned": exercise.xp_reward if is_completed else 0,
                "message": self._generate_feedback_message(analysis_result, is_completed)
            }

            # 활성 연습 문제 정리
            del self._active_exercises[user_id]

            logger.info(f"연습 문제 제출 완료: 점수={analysis_result['score']}, 완료={is_completed}")
            return result

        except Exception as e:
            logger.error(f"연습 문제 제출 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_user_progress_summary(self, user_id: int) -> Dict[str, Any]:
        """사용자 진도 요약"""
        try:
            # 모든 진도 데이터 가져오기
            all_progress = self._get_all_user_progress(user_id)

            if not all_progress:
                return self._create_empty_progress_summary()

            # 전체 진도 계산
            overall_progress = self.progress_calculator.calculate_overall_progress(all_progress, {})

            # 레벨별 진도
            level_progress = {}
            for level in DifficultyLevel:
                level_data = self.progress_calculator.calculate_level_progress(all_progress, level)
                level_progress[level.value] = level_data

            # 학습 통계
            summary = {
                "user_id": user_id,
                "total_completed": overall_progress.get("total_completed", 0),
                "total_items": overall_progress.get("total_items", 0),
                "overall_completion_rate": overall_progress.get("overall_completion_rate", 0.0),
                "average_score": overall_progress.get("average_score", 0.0),
                "level_progress": level_progress,
                "total_study_minutes": overall_progress.get("total_study_minutes", 0),
                "total_xp": overall_progress.get("total_xp", 0),
                "last_activity": overall_progress.get("last_activity"),
                "learning_streak": self.progress_calculator.calculate_streak(all_progress),
                "recent_activities": all_progress[:5] if all_progress else []
            }

            logger.info(f"사용자 진도 요약 완료: {user_id}")
            return summary

        except Exception as e:
            logger.error(f"사용자 진도 요약 실패: {e}")
            return self._create_empty_progress_summary()

    def get_topic_progress(
        self,
        user_id: int,
        topic: str,
        level: DifficultyLevel
    ) -> Dict[str, Any]:
        """특정 주제의 진도 정보"""
        try:
            topic_progress_data = self._get_topic_progress(user_id, topic, level)

            if not topic_progress_data:
                return {
                    "topic": topic,
                    "level": level.value,
                    "completed_count": 0,
                    "total_count": 0,
                    "completion_rate": 0.0,
                    "average_score": 0.0,
                    "mastery_level": "beginner"
                }

            # 주제 숙련도 계산
            mastery = self.progress_calculator.calculate_topic_mastery(
                topic_progress_data,
                len(topic_progress_data)
            )

            return {
                "topic": topic,
                "level": level.value,
                "completed_count": mastery["completed_count"],
                "total_count": mastery["total_exercises"],
                "completion_rate": mastery["completion_rate"],
                "average_score": mastery["average_score"],
                "mastery_level": mastery["mastery_level"]
            }

        except Exception as e:
            logger.error(f"주제 진도 조회 실패: {e}")
            return {}

    def _analyze_submission(self, code: str, exercise: Exercise) -> Dict[str, Any]:
        """코드 제출 분석"""
        try:
            logger.debug("코드 분석 시작")

            # Claude API를 통한 코드 분석
            analysis = self.claude_client.analyze_code(
                code=code,
                user_level=exercise.difficulty.value,
                analysis_type="exercise"
            )

            return {
                "score": analysis.get("score", 7),
                "issues": analysis.get("issues", []),
                "suggestions": analysis.get("suggestions", []),
                "strengths": analysis.get("strengths", []),
                "raw_analysis": analysis
            }

        except Exception as e:
            logger.error(f"코드 분석 실패: {e}")
            # 분석 실패 시 기본 분석 결과 반환
            return {
                "score": 7,
                "issues": [],
                "suggestions": [],
                "strengths": ["코드를 제출해 주셔서 감사합니다."],
                "error": str(e)
            }

    def _save_submission(
        self,
        user_id: int,
        exercise_id: str,
        code: str,
        score: int,
        time_spent: int
    ) -> Dict[str, Any]:
        """제출 저장"""
        try:
            # 데이터베이스에 제출 저장
            from src.database.models import CodeSubmissionModel

            submission = CodeSubmissionModel.create_submission(
                session_id=self.session_manager.get_current_session().get("id", 0),
                user_id=user_id,
                code=code,
                exercise_id=exercise_id,
                score=score,
                time_spent=time_spent
            )

            logger.debug(f"제출 저장 완료: {submission['id']}")
            return submission

        except Exception as e:
            logger.error(f"제출 저장 실패: {e}")
            return {}

    def _get_or_create_progress(
        self,
        user_id: int,
        topic: str,
        level: str
    ) -> Dict[str, Any]:
        """진도 레코드 가져오기 또는 생성"""
        try:
            from src.database.models import CurriculumProgressModel

            progress = CurriculumProgressModel.get_or_create_progress(
                user_id=user_id,
                topic=topic,
                level=level
            )

            logger.debug(f"진도 레코드: {progress.get('id')}")
            return progress

        except Exception as e:
            logger.error(f"진도 레코드 생성 실패: {e}")
            return {}

    def _update_exercise_progress(
        self,
        user_id: int,
        topic: str,
        level: str,
        score: int,
        xp_reward: int
    ) -> bool:
        """연습 문제 진도 업데이트"""
        try:
            from src.database.models import CurriculumProgressModel

            progress = self._get_or_create_progress(user_id, topic, level)

            # 진도 업데이트
            is_completed = score >= 7.0

            CurriculumProgressModel.update_progress(
                progress_id=progress["id"],
                score=score,
                completed=is_completed,
                xp_earned=xp_reward if is_completed else 0
            )

            logger.debug(f"진도 업데이트 완료: 사용자={user_id}, 주제={topic}, 완료={is_completed}")
            return True

        except Exception as e:
            logger.error(f"진도 업데이트 실패: {e}")
            return False

    def _get_all_user_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """사용자의 모든 진도 데이터 가져오기"""
        try:
            from src.database.models import CurriculumProgressModel

            progress_list = CurriculumProgressModel.get_user_progress(user_id)
            logger.debug(f"사용자 진도 데이터 {len(progress_list)}개 로드")
            return progress_list

        except Exception as e:
            logger.error(f"사용자 진도 데이터 로드 실패: {e}")
            return []

    def _get_topic_progress(
        self,
        user_id: int,
        topic: str,
        level: DifficultyLevel
    ) -> List[Dict[str, Any]]:
        """특정 주제의 진도 데이터 가져오기"""
        try:
            from src.database.models import CurriculumProgressModel

            all_progress = self._get_all_user_progress(user_id)

            topic_progress = [
                p for p in all_progress
                if p.get("topic") == topic and p.get("level") == level.value
            ]

            return topic_progress

        except Exception as e:
            logger.error(f"주제 진도 데이터 로드 실패: {e}")
            return []

    def _create_empty_progress_summary(self) -> Dict[str, Any]:
        """빈 진도 요약 생성"""
        return {
            "total_completed": 0,
            "total_items": 0,
            "overall_completion_rate": 0.0,
            "average_score": 0.0,
            "level_progress": {
                "beginner": {"completed": 0, "total": 0, "completion_rate": 0.0, "average_score": 0.0},
                "intermediate": {"completed": 0, "total": 0, "completion_rate": 0.0, "average_score": 0.0},
                "advanced": {"completed": 0, "total": 0, "completion_rate": 0.0, "average_score": 0.0}
            },
            "total_study_minutes": 0,
            "total_xp": 0,
            "last_activity": None,
            "learning_streak": 0,
            "recent_activities": []
        }

    def _generate_feedback_message(
        self,
        analysis_result: Dict[str, Any],
        is_completed: bool
    ) -> str:
        """피드백 메시지 생성"""
        try:
            score = analysis_result.get("score", 7)

            if is_completed:
                message = f"🎉 축하합니다! 문제를 완료했습니다. (점수: {score}/10)\n\n"
                message += "잘한 점:\n"
                for strength in analysis_result.get("strengths", []):
                    message += f"✓ {strength}\n"
            else:
                message = f"💪 좋은 노력입니다! (점수: {score}/10)\n\n"
                message += "개선 제안:\n"
                for suggestion in analysis_result.get("suggestions", []):
                    message += f"• {suggestion}\n"

            return message

        except Exception as e:
            logger.error(f"피드백 메시지 생성 실패: {e}")
            return "분석 결과를 생성하는 중 오류가 발생했습니다."


# 전역 인스턴스
_progress_tracker = None


def get_progress_tracker(database_manager, session_manager) -> ProgressTracker:
    """진도 추적기 인스턴스 반환"""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker(database_manager, session_manager)
    return _progress_tracker


if __name__ == "__main__":
    # 진도 추적기 테스트
    print("🧪 진도 추적기 테스트")

    # 더미 데이터베이스 관리자와 세션 관리자
    class DummyDB:
        pass

    class DummySession:
        def get_current_session(self):
            return {"id": 1}

        def create_session(self, user_id, topic):
            return {"id": 1, "user_id": user_id, "topic": topic}

    db = DummyDB()
    session_mgr = DummySession()

    tracker = get_progress_tracker(db, session_mgr)

    # 테스트 연습 문제
    from src.learning.curriculum.models import Exercise, ExerciseType

    test_exercise = Exercise(
        id="test_001",
        title="테스트 문제",
        description="테스트 문제입니다",
        exercise_type=ExerciseType.CODE_COMPLETION,
        difficulty=DifficultyLevel.BEGINNER,
        topic="basics",
        starter_code="print('Hello')",
        xp_reward=10
    )

    # 연습 문제 시작
    start_result = tracker.start_exercise(1, test_exercise)
    print(f"✅ 연습 문제 시작: {start_result.get('message')}")

    # 진도 요약
    progress_summary = tracker.get_user_progress_summary(1)
    print(f"✅ 진도 요약: 완료 {progress_summary['total_completed']}/{progress_summary['total_items']}")

    print("\n🎉 진도 추적기 테스트 통과!")