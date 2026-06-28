"""
성취 규칙 엔진
이벤트 기반 성취 규칙 관리 및 검증
"""
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from loguru import logger
import json


@dataclass
class AchievementRule:
    """성취 규칙"""
    id: str
    name: str
    description: str
    achievement_type: str
    event_type: str
    condition_func: Callable
    xp_reward: int
    badge_icon: str
    target_value: Optional[int] = None

    def check_condition(self, user_id: int, event_data: Dict, db) -> bool:
        """조건 확인"""
        try:
            return self.condition_func(user_id, event_data, db, self.target_value)
        except Exception as e:
            logger.error(f"성취 규칙 확인 실패 ({self.id}): {e}")
            return False


class AchievementRules:
    """성취 규칙 관리자"""

    def __init__(self):
        self.rules = self._initialize_rules()
        self._event_rules_cache = {}
        logger.info("성취 규칙 엔진 초기화 완료")

    def get_rules_for_event(self, event_type: str) -> List[AchievementRule]:
        """이벤트별 규칙 반환"""
        if event_type not in self._event_rules_cache:
            self._event_rules_cache[event_type] = [
                rule for rule in self.rules if rule.event_type == event_type
            ]
        return self._event_rules_cache[event_type]

    def get_all_rules(self) -> List[AchievementRule]:
        """모든 규칙 반환"""
        return self.rules

    def get_rule_by_id(self, rule_id: str) -> Optional[AchievementRule]:
        """ID로 규칙 찾기"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def add_rule(self, rule: AchievementRule):
        """규칙 추가"""
        self.rules.append(rule)
        # 캐시 정리
        self._event_rules_cache.clear()
        logger.info(f"새로운 성취 규칙 추가: {rule.id}")

    def _initialize_rules(self) -> List[AchievementRule]:
        """성취 규칙 초기화"""
        return [
            # 첫 코드 제출
            AchievementRule(
                id="first_code",
                name="첫 번째 코드",
                description="첫 번째 코드를 제출했습니다",
                achievement_type="first_code",
                event_type="exercise_submit",
                condition_func=self._check_first_submission,
                xp_reward=10,
                badge_icon="🎯",
                target_value=1
            ),

            # 완벽 점수
            AchievementRule(
                id="perfect_score",
                name="완벽 점수",
                description="완벽한 점수를 받았습니다",
                achievement_type="perfect_score",
                event_type="exercise_submit",
                condition_func=self._check_perfect_score,
                xp_reward=20,
                badge_icon="⭐",
                target_value=10
            ),

            # 5연승
            AchievementRule(
                id="streak_5",
                name="5연승",
                description="5개 연속 문제를 완료했습니다",
                achievement_type="streak",
                event_type="exercise_complete",
                condition_func=self._check_streak,
                xp_reward=30,
                badge_icon="🔥",
                target_value=5
            ),

            # 10연승
            AchievementRule(
                id="streak_10",
                name="10연승",
                description="10개 연속 문제를 완료했습니다",
                achievement_type="streak",
                event_type="exercise_complete",
                condition_func=self._check_streak,
                xp_reward=50,
                badge_icon="💯",
                target_value=10
            ),

            # 주제 완료
            AchievementRule(
                id="completed_topic",
                name="주제 완료",
                description="첫 번째 주제를 완료했습니다",
                achievement_type="topic_complete",
                event_type="topic_complete",
                condition_func=self._check_topic_complete,
                xp_reward=40,
                badge_icon="📚",
                target_value=1
            ),

            # 레벨 업 (초급)
            AchievementRule(
                id="level_up_beginner",
                name="초급 달성",
                description="초급 과정을 완료했습니다",
                achievement_type="level_complete",
                event_type="level_complete",
                condition_func=self._check_level_complete,
                xp_reward=100,
                badge_icon="🎓",
                target_value=1
            ),

            # XP 100
            AchievementRule(
                id="xp_100",
                name="100 XP",
                description="100 XP를 획득했습니다",
                achievement_type="xp_milestone",
                event_type="xp_earn",
                condition_func=self._check_xp_milestone,
                xp_reward=0,
                badge_icon="💎",
                target_value=100
            ),

            # XP 500
            AchievementRule(
                id="xp_500",
                name="500 XP",
                description="500 XP를 획득했습니다",
                achievement_type="xp_milestone",
                event_type="xp_earn",
                condition_func=self._check_xp_milestone,
                xp_reward=0,
                badge_icon="💠",
                target_value=500
            )
        ]

    # ===== 규칙 조건 체크 함수 =====

    def _check_first_submission(self, user_id: int, event_data: Dict, db, target_value: int) -> bool:
        """첫 제출인지 확인"""
        try:
            from src.database.models import CodeSubmissionModel

            submission_count = CodeSubmissionModel.get_user_submission_count(user_id)
            return submission_count >= target_value

        except Exception as e:
            logger.error(f"첫 제출 확인 실패: {e}")
            return False

    def _check_perfect_score(self, user_id: int, event_data: Dict, db, target_value: int) -> bool:
        """완벽 점수 확인"""
        try:
            score = event_data.get("score", 0)
            return score >= target_value

        except Exception as e:
            logger.error(f"완벽 점수 확인 실패: {e}")
            return False

    def _check_streak(self, user_id: int, event_data: Dict, db, target_value: int) -> bool:
        """연승 확인"""
        try:
            from src.database.models import CurriculumProgressModel

            # 최근 완료한 연습 문제 확인
            recent_progress = CurriculumProgressModel.get_recent_completed_progress(
                user_id, limit=target_value
            )

            # 연속 완료인지 확인
            if len(recent_progress) < target_value:
                return False

            # 모두 완료 상태인지 확인
            all_completed = all(p.get("completed", False) for p in recent_progress)
            return all_completed

        except Exception as e:
            logger.error(f"연승 확인 실패: {e}")
            return False

    def _check_topic_complete(self, user_id: int, event_data: Dict, db, target_value: int) -> bool:
        """주제 완료 확인"""
        try:
            from src.database.models import CurriculumProgressModel

            completed_topics = CurriculumProgressModel.get_user_completed_topics(user_id)
            return len(completed_topics) >= target_value

        except Exception as e:
            logger.error(f"주제 완료 확인 실패: {e}")
            return False

    def _check_level_complete(self, user_id: int, event_data: Dict, db, target_value: int) -> bool:
        """레벨 완료 확인"""
        try:
            level = event_data.get("level", "beginner")

            from src.database.models import CurriculumProgressModel

            level_progress = CurriculumProgressModel.get_user_progress_by_level(user_id, level)
            completed_count = sum(1 for p in level_progress if p.get("completed", False))

            # 레벨의 모든 주제를 완료했는지 확인
            return completed_count >= len(level_progress) and len(level_progress) > 0

        except Exception as e:
            logger.error(f"레벨 완료 확인 실패: {e}")
            return False

    def _check_xp_milestone(self, user_id: int, event_data: Dict, db, target_value: int) -> bool:
        """XP 마일스톤 확인"""
        try:
            current_xp = event_data.get("total_xp", 0)
            return current_xp >= target_value

        except Exception as e:
            logger.error(f"XP 마일스톤 확인 실패: {e}")
            return False


# 전역 인스턴스
_achievement_rules = None


def get_achievement_rules() -> AchievementRules:
    """성취 규칙 엔진 인스턴스 반환"""
    global _achievement_rules
    if _achievement_rules is None:
        _achievement_rules = AchievementRules()
    return _achievement_rules


if __name__ == "__main__":
    # 성취 규칙 엔진 테스트
    print("🧪 성취 규칙 엔진 테스트")

    rules_engine = get_achievement_rules()

    # 모든 규칙 조회
    all_rules = rules_engine.get_all_rules()
    print(f"✅ 전체 규칙: {len(all_rules)}개")

    # 이벤트별 규칙 조회
    submit_rules = rules_engine.get_rules_for_event("exercise_submit")
    print(f"✅ 제출 이벤트 규칙: {len(submit_rules)}개")

    complete_rules = rules_engine.get_rules_for_event("exercise_complete")
    print(f"✅ 완료 이벤트 규칙: {len(complete_rules)}개")

    # 규칙 상세 정보
    for rule in all_rules[:3]:
        print(f"✅ 규칙: {rule.name}")
        print(f"   이벤트: {rule.event_type}")
        print(f"   보상: {rule.xp_reward} XP")
        print(f"   뱃지: {rule.badge_icon}")

    # 더미 데이터베이스로 규칙 테스트
    class DummyDB:
        pass

    dummy_db = DummyDB()

    # 완벽 점수 규칙 테스트
    perfect_rule = rules_engine.get_rule_by_id("perfect_score")
    if perfect_rule:
        event_data = {"score": 10}
        result = perfect_rule.check_condition(1, event_data, dummy_db)
        print(f"✅ 완벽 점수 규칙 테스트: {result}")

    # 일반 점수 규칙 테스트
    event_data = {"score": 7}
    result = perfect_rule.check_condition(1, event_data, dummy_db)
    print(f"✅ 일반 점수 규칙 테스트: {result}")

    print("\n🎉 성취 규칙 엔진 테스트 통과!")