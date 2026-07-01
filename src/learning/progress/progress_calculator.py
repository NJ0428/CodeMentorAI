"""
진도 계산기
학습 진도 및 성과 지표 계산
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from src.learning.curriculum.models import DifficultyLevel


class ProgressCalculator:
    """진도 계산기"""

    def __init__(self):
        logger.info("진도 계산기 초기화 완료")

    def calculate_completion_rate(self, progress_list: List[Dict]) -> float:
        """완료율 계산"""
        try:
            if not progress_list:
                return 0.0

            completed = sum(1 for p in progress_list if p.get("completed", False))
            completion_rate = (completed / len(progress_list)) * 100

            logger.debug(f"완료율 계산: {completion_rate:.1f}%")
            return completion_rate

        except Exception as e:
            logger.error(f"완료율 계산 실패: {e}")
            return 0.0

    def calculate_average_score(self, progress_list: List[Dict]) -> float:
        """평균 점수 계산"""
        try:
            scored_progress = [p for p in progress_list if p.get("score") is not None]

            if not scored_progress:
                return 0.0

            total_score = sum(p["score"] for p in scored_progress)
            average_score = total_score / len(scored_progress)

            logger.debug(f"평균 점수 계산: {average_score:.1f}")
            return average_score

        except Exception as e:
            logger.error(f"평균 점수 계산 실패: {e}")
            return 0.0

    def calculate_level_progress(
        self,
        all_progress: List[Dict],
        level: DifficultyLevel
    ) -> Dict[str, Any]:
        """레벨별 진도 계산"""
        try:
            level_progress = [p for p in all_progress if p.get("level") == level.value]

            if not level_progress:
                return {
                    "level": level.value,
                    "total": 0,
                    "completed": 0,
                    "completion_rate": 0.0,
                    "average_score": 0.0
                }

            total = len(level_progress)
            completed = sum(1 for p in level_progress if p.get("completed", False))
            completion_rate = (completed / total) * 100 if total > 0 else 0.0
            average_score = self.calculate_average_score(level_progress)

            logger.debug(f"레벨별 진도 계산 ({level.value}): {completion_rate:.1f}%")

            return {
                "level": level.value,
                "total": total,
                "completed": completed,
                "completion_rate": completion_rate,
                "average_score": average_score
            }

        except Exception as e:
            logger.error(f"레벨별 진도 계산 실패: {e}")
            return {
                "level": level.value,
                "total": 0,
                "completed": 0,
                "completion_rate": 0.0,
                "average_score": 0.0
            }

    def calculate_overall_progress(
        self,
        all_progress: List[Dict],
        curriculum_totals: Dict[str, int]
    ) -> Dict[str, Any]:
        """전체 진도 계산"""
        try:
            total_completed = sum(1 for p in all_progress if p.get("completed", False))
            total_items = len(all_progress)

            # 레벨별 진도
            level_progress = {}
            for level in DifficultyLevel:
                level_data = self.calculate_level_progress(all_progress, level)
                level_progress[level.value] = level_data

            # 학습 활동
            total_study_time = sum(p.get("study_minutes", 0) for p in all_progress)
            total_xp = sum(p.get("xp_earned", 0) for p in all_progress)

            overall_progress = {
                "total_completed": total_completed,
                "total_items": total_items,
                "overall_completion_rate": self.calculate_completion_rate(all_progress),
                "average_score": self.calculate_average_score(all_progress),
                "level_progress": level_progress,
                "total_study_minutes": total_study_time,
                "total_xp": total_xp,
                "last_activity": self._get_last_activity(all_progress)
            }

            logger.info(f"전체 진도 계산 완료: {total_completed}/{total_items} 완료")
            return overall_progress

        except Exception as e:
            logger.error(f"전체 진도 계산 실패: {e}")
            return {}

    def calculate_learning_velocity(
        self,
        recent_progress: List[Dict],
        days: int = 7
    ) -> Dict[str, Any]:
        """학습 속도 계산 (일별 완료 수)"""
        try:
            if not recent_progress:
                return {"items_per_day": 0.0, "trend": "stable"}

            # 최근 N일간의 완료 항목 필터링
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_completed = [
                p for p in recent_progress
                if p.get("completed", False) and
                p.get("completed_at") and
                datetime.fromisoformat(p["completed_at"]) > cutoff_date
            ]

            items_per_day = len(recent_completed) / days if days > 0 else 0.0

            # 추세 분석
            trend = self._analyze_velocity_trend(recent_completed)

            logger.debug(f"학습 속도 계산: {items_per_day:.1f}항목/일")

            return {
                "items_per_day": items_per_day,
                "trend": trend,
                "period_days": days
            }

        except Exception as e:
            logger.error(f"학습 속도 계산 실패: {e}")
            return {"items_per_day": 0.0, "trend": "unknown"}

    def calculate_streak(self, progress_history: List[Dict]) -> int:
        """학습 연속 일수 계산"""
        try:
            if not progress_history:
                return 0

            # 날짜별 활동 추적
            activity_dates = set()
            for progress in progress_history:
                if progress.get("last_activity"):
                    try:
                        activity_date = datetime.fromisoformat(progress["last_activity"]).date()
                        activity_dates.add(activity_date)
                    except:
                        continue

            if not activity_dates:
                return 0

            # 연속 일수 계산
            sorted_dates = sorted(activity_dates, reverse=True)
            streak = 0
            current_date = datetime.now().date()

            for i, date in enumerate(sorted_dates):
                expected_date = current_date - timedelta(days=i)
                if date == expected_date:
                    streak += 1
                else:
                    break

            logger.debug(f"학습 연속 일수: {streak}일")
            return streak

        except Exception as e:
            logger.error(f"연속 일수 계산 실패: {e}")
            return 0

    def calculate_topic_mastery(
        self,
        topic_progress: List[Dict],
        topic_exercises: int
    ) -> Dict[str, Any]:
        """주제별 숙련도 계산"""
        try:
            if not topic_progress:
                return {"mastery_level": "beginner", "score": 0.0}

            completed_count = sum(1 for p in topic_progress if p.get("completed", False))
            average_score = self.calculate_average_score(topic_progress)

            # 숙련도 판정
            completion_rate = (completed_count / topic_exercises) * 100 if topic_exercises > 0 else 0.0

            if completion_rate >= 80 and average_score >= 8.0:
                mastery_level = "expert"
            elif completion_rate >= 60 and average_score >= 7.0:
                mastery_level = "proficient"
            elif completion_rate >= 40 and average_score >= 6.0:
                mastery_level = "intermediate"
            else:
                mastery_level = "beginner"

            mastery_score = (completion_rate * 0.6) + (average_score * 10 * 0.4)

            logger.debug(f"주제 숙련도: {mastery_level} (점수: {mastery_score:.1f})")

            return {
                "mastery_level": mastery_level,
                "score": mastery_score,
                "completion_rate": completion_rate,
                "average_score": average_score,
                "completed_count": completed_count,
                "total_exercises": topic_exercises
            }

        except Exception as e:
            logger.error(f"주제 숙련도 계산 실패: {e}")
            return {"mastery_level": "unknown", "score": 0.0}

    def _get_last_activity(self, progress_list: List[Dict]) -> Optional[str]:
        """마지막 활동 시간 가져오기"""
        try:
            activities = [
                p.get("last_activity")
                for p in progress_list
                if p.get("last_activity")
            ]

            if activities:
                return max(activities)
            return None

        except Exception as e:
            logger.error(f"마지막 활동 시간 가져오기 실패: {e}")
            return None

    def _analyze_velocity_trend(self, recent_completed: List[Dict]) -> str:
        """학습 속도 추세 분석"""
        try:
            if len(recent_completed) < 2:
                return "stable"

            # 최근 활동을 시간순으로 정렬
            sorted_activities = sorted(
                recent_completed,
                key=lambda x: datetime.fromisoformat(x["completed_at"])
            )

            # 전반부와 후반부 비교
            mid_point = len(sorted_activities) // 2
            first_half_time = (
                datetime.fromisoformat(sorted_activities[mid_point]["completed_at"]) -
                datetime.fromisoformat(sorted_activities[0]["completed_at"])
            ).total_seconds() / 86400  # days

            second_half_time = (
                datetime.fromisoformat(sorted_activities[-1]["completed_at"]) -
                datetime.fromisoformat(sorted_activities[mid_point]["completed_at"])
            ).total_seconds() / 86400  # days

            if first_half_time == 0 or second_half_time == 0:
                return "stable"

            time_ratio = second_half_time / first_half_time

            if time_ratio < 0.7:  # 후반부가 더 빠름
                return "accelerating"
            elif time_ratio > 1.3:  # 후반부가 더 느림
                return "decelerating"
            else:
                return "stable"

        except Exception as e:
            logger.error(f"속도 추세 분석 실패: {e}")
            return "unknown"


# 전역 인스턴스
_progress_calculator = None


def get_progress_calculator() -> ProgressCalculator:
    """진도 계산기 인스턴스 반환"""
    global _progress_calculator
    if _progress_calculator is None:
        _progress_calculator = ProgressCalculator()
    return _progress_calculator


if __name__ == "__main__":
    # 진도 계산기 테스트
    print("🧪 진도 계산기 테스트")

    calculator = get_progress_calculator()

    # 테스트 데이터
    test_progress = [
        {
            "level": "beginner",
            "completed": True,
            "score": 8,
            "study_minutes": 30,
            "xp_earned": 50,
            "last_activity": "2024-01-15T10:00:00"
        },
        {
            "level": "beginner",
            "completed": True,
            "score": 9,
            "study_minutes": 25,
            "xp_earned": 60,
            "last_activity": "2024-01-16T10:00:00"
        },
        {
            "level": "beginner",
            "completed": False,
            "score": 6,
            "study_minutes": 15,
            "xp_earned": 20,
            "last_activity": "2024-01-17T10:00:00"
        }
    ]

    # 완료율 계산
    completion_rate = calculator.calculate_completion_rate(test_progress)
    print(f"✅ 완료율: {completion_rate:.1f}%")

    # 평균 점수 계산
    average_score = calculator.calculate_average_score(test_progress)
    print(f"✅ 평균 점수: {average_score:.1f}")

    # 레벨별 진도 계산
    level_progress = calculator.calculate_level_progress(test_progress, DifficultyLevel.BEGINNER)
    print(f"✅ 초급 진도: {level_progress['completed']}/{level_progress['total']} 완료")

    # 전체 진도 계산
    overall_progress = calculator.calculate_overall_progress(test_progress, {})
    print(f"✅ 전체 진도: {overall_progress['total_completed']}/{overall_progress['total_items']} 완료")
    print(f"   총 학습 시간: {overall_progress['total_study_minutes']}분")
    print(f"   총 XP: {overall_progress['total_xp']}")

    # 주제 숙련도 계산
    topic_mastery = calculator.calculate_topic_mastery(test_progress, topic_exercises=5)
    print(f"✅ 주제 숙련도: {topic_mastery['mastery_level']} (점수: {topic_mastery['score']:.1f})")

    print("\n🎉 진도 계산기 테스트 통과!")