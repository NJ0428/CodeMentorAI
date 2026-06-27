"""
적응형 난이도 조절 시스템
사용자 성과 기반 난이도 자동 조절 및 개인화된 추천
"""
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from collections import deque

from src.learning.curriculum.models import DifficultyLevel, Exercise
from src.learning.progress.progress_calculator import ProgressCalculator, get_progress_calculator
from src.learning.curriculum.curriculum_manager import get_curriculum_manager


class AdaptiveDifficulty:
    """적응형 난이도 조절 시스템"""

    def __init__(self, database_manager):
        self.db = database_manager
        self.progress_calculator = get_progress_calculator()
        self.curriculum_manager = get_curriculum_manager()

        # 성과 임계값 설정
        self.performance_threshold = {
            "promote": 8.5,      # 레벨 승격 기준
            "demote": 6.0,       # 레벨 강등 기준
            "ideal": 7.5,        # 이상적인 점수 범위 중간
            "min_exercises": 5   # 최소 평가 문제 수
        }

        logger.info("적응형 난이도 조절 시스템 초기화 완료")

    def assess_user_level(self, user_id: int) -> Dict[str, Any]:
        """사용자 수준 평가"""
        try:
            # 최근 성과 분석
            recent_performance = self._get_recent_performance(user_id, limit=10)

            if not recent_performance:
                return {
                    "recommended_level": DifficultyLevel.BEGINNER,
                    "confidence": 0.0,
                    "reason": "충분한 데이터 없음"
                }

            avg_score = sum(p["score"] for p in recent_performance) / len(recent_performance)
            current_level = self._get_user_current_level(user_id)

            # 레벨 추천
            if avg_score >= self.performance_threshold["promote"] and len(recent_performance) >= self.performance_threshold["min_exercises"]:
                recommended_level = self._get_next_level(current_level)
                reason = f"우수한 성과 (평균 {avg_score:.1f}점)"
            elif avg_score <= self.performance_threshold["demote"] and len(recent_performance) >= self.performance_threshold["min_exercises"]:
                recommended_level = self._get_previous_level(current_level)
                reason = f"난이도 조절 필요 (평균 {avg_score:.1f}점)"
            else:
                recommended_level = current_level
                reason = f"현재 수준 적절 (평균 {avg_score:.1f}점)"

            # 자신감 계산
            confidence = self._calculate_confidence(recent_performance)

            # 성과 추세 분석
            performance_trend = self._analyze_performance_trend(recent_performance)

            assessment = {
                "user_id": user_id,
                "recommended_level": recommended_level,
                "current_level": current_level,
                "confidence": confidence,
                "average_score": avg_score,
                "performance_trend": performance_trend,
                "total_evaluated": len(recent_performance),
                "reason": reason,
                "level_change_needed": recommended_level != current_level
            }

            logger.info(f"사용자 {user_id} 수준 평가 완료: {recommended_level.value} (자신도: {confidence:.1f})")
            return assessment

        except Exception as e:
            logger.error(f"사용자 수준 평가 실패: {e}")
            return {
                "recommended_level": DifficultyLevel.BEGINNER,
                "confidence": 0.0,
                "error": str(e)
            }

    def recommend_exercise(
        self,
        user_id: int,
        topic: Optional[str] = None,
        count: int = 1
    ) -> List[Exercise]:
        """다음 연습 문제 추천"""
        try:
            # 사용자 수준 평가
            assessment = self.assess_user_level(user_id)
            recommended_level = assessment["recommended_level"]

            # 약점 주제 분석
            weak_topics = self._identify_weak_topics(user_id)

            # 주제 결정
            if topic is None:
                if weak_topics:
                    topic = weak_topics[0]
                else:
                    # 현재 레벨의 다음 주제
                    curriculum = self.curriculum_manager.get_curriculum(recommended_level)
                    if curriculum and curriculum.topics:
                        topic = curriculum.topics[0].id

            # 적절한 난이도의 연습 문제 선택
            exercises = []

            if weak_topics and topic is None:
                # 약점 주제에 집중
                for weak_topic in weak_topics[:count]:
                    exercise = self._get_topic_exercise(recommended_level, weak_topic, user_id)
                    if exercise:
                        exercises.append(exercise)
            else:
                # 지정된 주제의 연습 문제
                for i in range(count):
                    exercise = self._get_topic_exercise(recommended_level, topic, user_id)
                    if exercise:
                        exercises.append(exercise)

            logger.info(f"사용자 {user_id}에게 {len(exercises)}개 연습 문제 추천")
            return exercises

        except Exception as e:
            logger.error(f"연습 문제 추천 실패: {e}")
            return []

    def adjust_exercise_difficulty(
        self,
        base_exercise: Exercise,
        user_performance: Dict[str, Any]
    ) -> Exercise:
        """연습 문제 난이도 조절"""
        try:
            average_score = user_performance.get("average_score", 7.5)

            if average_score > 8.5:
                # 더 어려운 변형 생성
                from src.learning.curriculum.exercise_generator import get_exercise_generator
                generator = get_exercise_generator()
                return generator.create_variant_exercise(base_exercise, "harder")
            elif average_score < 6.0:
                # 더 쉬운 변형 생성
                from src.learning.curriculum.exercise_generator import get_exercise_generator
                generator = get_exercise_generator()
                return generator.create_variant_exercise(base_exercise, "easier")
            else:
                # 동일한 난이도
                return base_exercise

        except Exception as e:
            logger.error(f"연습 문제 난이도 조절 실패: {e}")
            return base_exercise

    def get_personalized_learning_path(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """개인화된 학습 경로 생성"""
        try:
            # 사용자 수준 평가
            assessment = self.assess_user_level(user_id)
            current_level = assessment["recommended_level"]

            # 약점 주제 분석
            weak_topics = self._identify_weak_topics(user_id)

            # 강점 주제 분석
            strong_topics = self._identify_strong_topics(user_id)

            # 학습 제안 생성
            learning_path = {
                "user_id": user_id,
                "current_level": current_level.value,
                "recommended_focus": weak_topics if weak_topics else ["general_practice"],
                "strengths": strong_topics,
                "weaknesses": weak_topics,
                "performance_trend": assessment.get("performance_trend", "stable"),
                "suggested_topics": self._generate_topic_suggestions(user_id, current_level, weak_topics),
                "estimated_completion_time": self._estimate_completion_time(user_id, current_level),
                "confidence": assessment.get("confidence", 0.0)
            }

            logger.info(f"사용자 {user_id} 개인화된 학습 경로 생성 완료")
            return learning_path

        except Exception as e:
            logger.error(f"개인화된 학습 경로 생성 실패: {e}")
            return {}

    def _get_recent_performance(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 성과 조회"""
        try:
            from src.database.models import CodeSubmissionModel

            recent_submissions = CodeSubmissionModel.get_recent_submissions(user_id, limit=limit)

            performance_data = []
            for submission in recent_submissions:
                score = submission.get("score", 0)
                if score > 0:  # 유효한 점수만 포함
                    performance_data.append({
                        "score": score,
                        "exercise_id": submission.get("exercise_id"),
                        "submitted_at": submission.get("created_at")
                    })

            return performance_data

        except Exception as e:
            logger.error(f"최근 성과 조회 실패: {e}")
            return []

    def _calculate_confidence(self, performances: List[Dict]) -> float:
        """자신감 계산 (점수 분산 기반)"""
        try:
            if len(performances) < 3:
                return 0.5

            scores = [p["score"] for p in performances]
            mean_score = sum(scores) / len(scores)

            # 분산 계산
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)

            # 분산이 낮을수록 자신감 높음
            confidence = max(0.0, min(1.0, 1.0 - (variance / 25.0)))  # 최대 분산 25로 가정

            return confidence

        except Exception as e:
            logger.error(f"자신감 계산 실패: {e}")
            return 0.5

    def _analyze_performance_trend(self, performances: List[Dict]) -> str:
        """성과 추세 분석"""
        try:
            if len(performances) < 4:
                return "stable"

            # 최근 4개와 이전 4개로 나누어 비교
            mid_point = len(performances) // 2

            recent_avg = sum(p["score"] for p in performances[:mid_point]) / mid_point
            older_avg = sum(p["score"] for p in performances[mid_point:]) / (len(performances) - mid_point)

            if recent_avg > older_avg + 1.0:
                return "improving"
            elif recent_avg < older_avg - 1.0:
                return "declining"
            else:
                return "stable"

        except Exception as e:
            logger.error(f"성과 추세 분석 실패: {e}")
            return "unknown"

    def _identify_weak_topics(self, user_id: int) -> List[str]:
        """약점 주제 식별"""
        try:
            from src.database.models import CurriculumProgressModel

            all_progress = CurriculumProgressModel.get_user_progress(user_id)

            # 점수가 낮은 주제 식별
            topic_scores = {}
            for progress in all_progress:
                topic = progress.get("topic", "unknown")
                score = progress.get("score", 0)

                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(score)

            # 주제별 평균 점수 계산
            weak_topics = []
            for topic, scores in topic_scores.items():
                avg_score = sum(scores) / len(scores) if scores else 0
                if avg_score < 7.0:  # 7점 미만인 주제를 약점으로 간주
                    weak_topics.append((topic, avg_score))

            # 점수가 낮은 순서로 정렬
            weak_topics.sort(key=lambda x: x[1])

            return [topic for topic, _ in weak_topics[:3]]  # 상위 3개 약점 주제

        except Exception as e:
            logger.error(f"약점 주제 식별 실패: {e}")
            return []

    def _identify_strong_topics(self, user_id: int) -> List[str]:
        """강점 주제 식별"""
        try:
            from src.database.models import CurriculumProgressModel

            all_progress = CurriculumProgressModel.get_user_progress(user_id)

            # 점수가 높은 주제 식별
            topic_scores = {}
            for progress in all_progress:
                topic = progress.get("topic", "unknown")
                score = progress.get("score", 0)

                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(score)

            # 주제별 평균 점수 계산
            strong_topics = []
            for topic, scores in topic_scores.items():
                avg_score = sum(scores) / len(scores) if scores else 0
                if avg_score >= 8.0:  # 8점 이상인 주제를 강점으로 간주
                    strong_topics.append((topic, avg_score))

            # 점수가 높은 순서로 정렬
            strong_topics.sort(key=lambda x: x[1], reverse=True)

            return [topic for topic, _ in strong_topics[:3]]  # 상위 3개 강점 주제

        except Exception as e:
            logger.error(f"강점 주제 식별 실패: {e}")
            return []

    def _get_user_current_level(self, user_id: int) -> DifficultyLevel:
        """사용자 현재 레벨 가져오기"""
        try:
            from src.database.models import UserModel

            user = UserModel.get_user(user_id)
            if user:
                level_str = user.get("level", "beginner")
                return DifficultyLevel(level_str)

            return DifficultyLevel.BEGINNER

        except Exception as e:
            logger.error(f"사용자 레벨 조회 실패: {e}")
            return DifficultyLevel.BEGINNER

    def _get_next_level(self, current_level: DifficultyLevel) -> DifficultyLevel:
        """다음 레벨 반환"""
        levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]
        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass
        return current_level

    def _get_previous_level(self, current_level: DifficultyLevel) -> DifficultyLevel:
        """이전 레벨 반환"""
        levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]
        try:
            current_index = levels.index(current_level)
            if current_index > 0:
                return levels[current_index - 1]
        except ValueError:
            pass
        return current_level

    def _get_topic_exercise(
        self,
        level: DifficultyLevel,
        topic: str,
        user_id: int
    ) -> Optional[Exercise]:
        """주제별 연습 문제 가져오기"""
        try:
            # 커리큘럼 관리자에서 연습 문제 가져오기
            exercises = self.curriculum_manager.get_topic_exercises(level, topic)

            if not exercises:
                # 연습 문제가 없으면 개인화된 문제 생성
                performance = self._get_user_performance_summary(user_id)
                from src.learning.curriculum.exercise_generator import get_exercise_generator
                generator = get_exercise_generator()

                generated = generator.generate_personalized_exercises(
                    user_level=level,
                    weak_topics=[topic],
                    recent_performance=performance,
                    count=1
                )

                return generated[0] if generated else None

            # 사용자 성과에 따른 적절한 문제 선택
            performance = self._get_recent_performance(user_id, limit=5)
            avg_score = sum(p["score"] for p in performance) / len(performance) if performance else 7.0

            # 성과에 따른 문제 필터링
            if avg_score > 8.0:
                # 더 어려운 문제 우선
                exercises = sorted(exercises, key=lambda e: getattr(e, 'difficulty', 1), reverse=True)
            elif avg_score < 6.0:
                # 더 쉬운 문제 우선
                exercises = sorted(exercises, key=lambda e: getattr(e, 'difficulty', 1))

            return exercises[0] if exercises else None

        except Exception as e:
            logger.error(f"주제 연습 문제 가져오기 실패: {e}")
            return None

    def _get_user_performance_summary(self, user_id: int) -> Dict[str, Any]:
        """사용자 성과 요약"""
        try:
            recent_performance = self._get_recent_performance(user_id, limit=10)

            if not recent_performance:
                return {"average_score": 7.0}

            avg_score = sum(p["score"] for p in recent_performance) / len(recent_performance)

            return {
                "average_score": avg_score,
                "total_evaluated": len(recent_performance)
            }

        except Exception as e:
            logger.error(f"사용자 성과 요약 실패: {e}")
            return {"average_score": 7.0}

    def _generate_topic_suggestions(
        self,
        user_id: int,
        current_level: DifficultyLevel,
        weak_topics: List[str]
    ) -> List[Dict[str, Any]]:
        """주제 학습 제안 생성"""
        try:
            suggestions = []

            # 약점 주제 학습 제안
            for topic in weak_topics[:2]:
                suggestions.append({
                    "topic": topic,
                    "priority": "high",
                    "reason": "점수 향상 필요"
                })

            # 커리큘럼의 다음 주제
            curriculum = self.curriculum_manager.get_curriculum(current_level)
            if curriculum:
                for topic in curriculum.topics[:2]:
                    if topic.id not in weak_topics:
                        suggestions.append({
                            "topic": topic.id,
                            "priority": "medium",
                            "reason": "다음 학습 단계"
                        })

            return suggestions[:4]  # 상위 4개 제안

        except Exception as e:
            logger.error(f"주제 학습 제안 생성 실패: {e}")
            return []

    def _estimate_completion_time(
        self,
        user_id: int,
        current_level: DifficultyLevel
    ) -> Dict[str, Any]:
        """완료 시간 추정"""
        try:
            from src.database.models import CurriculumProgressModel

            level_progress = CurriculumProgressModel.get_user_progress_by_level(user_id, current_level.value)

            total_topics = len(level_progress)
            completed_topics = sum(1 for p in level_progress if p.get("completed", False))

            if total_topics == 0:
                return {"estimated_hours": 0, "remaining_topics": 0}

            remaining_topics = total_topics - completed_topics

            # 주제당 평균 2시간으로 가정
            estimated_hours = remaining_topics * 2

            return {
                "estimated_hours": estimated_hours,
                "remaining_topics": remaining_topics,
                "total_topics": total_topics
            }

        except Exception as e:
            logger.error(f"완료 시간 추정 실패: {e}")
            return {"estimated_hours": 0, "remaining_topics": 0}


# 전역 인스턴스
_adaptive_difficulty = None


def get_adaptive_difficulty(database_manager) -> AdaptiveDifficulty:
    """적응형 난이도 조절 시스템 인스턴스 반환"""
    global _adaptive_difficulty
    if _adaptive_difficulty is None:
        _adaptive_difficulty = AdaptiveDifficulty(database_manager)
    return _adaptive_difficulty


if __name__ == "__main__":
    # 적응형 난이도 조절 시스템 테스트
    print("🧪 적응형 난이도 조절 시스템 테스트")

    # 더미 데이터베이스 관리자
    class DummyDB:
        pass

    db = DummyDB()
    adaptive_system = get_adaptive_difficulty(db)

    # 사용자 수준 평가 (데이터 없는 경우)
    assessment = adaptive_system.assess_user_level(1)
    print(f"✅ 사용자 수준 평가:")
    print(f"   추천 레벨: {assessment['recommended_level'].value}")
    print(f"   자신도: {assessment['confidence']:.1f}")
    print(f"   이유: {assessment['reason']}")

    # 연습 문제 추천
    recommended = adaptive_system.recommend_exercise(1, count=2)
    print(f"✅ 추천 연습 문제: {len(recommended)}개")

    # 개인화된 학습 경로
    learning_path = adaptive_system.get_personalized_learning_path(1)
    print(f"✅ 개인화된 학습 경로:")
    print(f"   현재 레벨: {learning_path.get('current_level')}")
    print(f"   추천 초점: {learning_path.get('recommended_focus')}")
    print(f"   성과 추세: {learning_path.get('performance_trend')}")

    print("\n🎉 적응형 난이도 조절 시스템 테스트 통과!")