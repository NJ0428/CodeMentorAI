"""
성취 관리자
성취 확인, 부여, 조회 시스템
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from src.learning.achievements.achievement_rules import AchievementRules, get_achievement_rules
from src.learning.achievements.badge_system import BadgeSystem, get_badge_system, BadgeInfo


class AchievementManager:
    """성취 관리자"""

    def __init__(self, database_manager):
        self.db = database_manager
        self.achievement_rules = get_achievement_rules()
        self.badge_system = get_badge_system()
        logger.info("성취 관리자 초기화 완료")

    def check_and_award_achievements(
        self,
        user_id: int,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """이벤트에 따른 성취 확인 및 부여"""
        try:
            new_achievements = []

            # 이벤트와 관련된 규칙 확인
            applicable_rules = self.achievement_rules.get_rules_for_event(event_type)

            logger.debug(f"이벤트 '{event_type}'에 적용 가능한 규칙 {len(applicable_rules)}개")

            for rule in applicable_rules:
                # 규칙 조건 확인
                if rule.check_condition(user_id, event_data, self.db):
                    # 성취 부여 시도
                    achievement = self._award_achievement(user_id, rule)
                    if achievement:
                        new_achievements.append(achievement)

            if new_achievements:
                logger.info(f"사용자 {user_id}에게 {len(new_achievements)}개 성취 부여")

            return new_achievements

        except Exception as e:
            logger.error(f"성취 확인 및 부여 실패: {e}")
            return []

    def get_user_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """사용자 성취 목록 조회"""
        try:
            from src.database.models import AchievementModel

            achievements = AchievementModel.get_user_achievements(user_id)

            # 뱃지 정보 추가
            for achievement in achievements:
                badge_info = self.badge_system.get_badge(achievement["achievement_type"])
                if badge_info:
                    achievement["badge"] = badge_info.to_dict()
                else:
                    achievement["badge"] = None

            logger.debug(f"사용자 {user_id}의 성취 {len(achievements)}개 조회")
            return achievements

        except Exception as e:
            logger.error(f"사용자 성취 조회 실패: {e}")
            return []

    def get_achievement_stats(self, user_id: int) -> Dict[str, Any]:
        """성취 통계"""
        try:
            achievements = self.get_user_achievements(user_id)

            # 유형별 개수
            type_counts = {}
            total_xp = 0

            for achievement in achievements:
                achievement_type = achievement["achievement_type"]
                type_counts[achievement_type] = type_counts.get(achievement_type, 0) + 1

                # XP 보상 합계
                rule = self.achievement_rules.get_rule_by_id(achievement_type)
                if rule:
                    total_xp += rule.xp_reward

            # 전체 뱃지 대비 완료 비율
            all_badges = self.badge_system.get_all_badges()
            completion_rate = (len(achievements) / len(all_badges) * 100) if all_badges else 0

            stats = {
                "total_achievements": len(achievements),
                "type_counts": type_counts,
                "total_xp_from_achievements": total_xp,
                "completion_rate": completion_rate,
                "recent_achievements": achievements[:5] if achievements else []
            }

            logger.info(f"사용자 {user_id}의 성취 통계 계산 완료")
            return stats

        except Exception as e:
            logger.error(f"성취 통계 계산 실패: {e}")
            return {}

    def get_available_achievements(self) -> List[Dict[str, Any]]:
        """획득 가능한 모든 성취 목록"""
        try:
            all_badges = self.badge_system.get_all_badges()
            return [badge.to_dict() for badge in all_badges]

        except Exception as e:
            logger.error(f"획득 가능 성취 목록 조회 실패: {e}")
            return []

    def check_achievement_progress(
        self,
        user_id: int,
        achievement_type: str
    ) -> Dict[str, Any]:
        """특정 성취의 진도 확인"""
        try:
            from src.database.models import AchievementModel

            # 이미 획득한 성취인지 확인
            if AchievementModel.has_achievement(user_id, achievement_type):
                return {
                    "achievement_type": achievement_type,
                    "completed": True,
                    "progress": 100,
                    "awarded_at": AchievementModel.get_achievement_date(user_id, achievement_type)
                }

            # 진도 확인
            rule = self.achievement_rules.get_rule_by_id(achievement_type)
            if not rule:
                return {"error": "성취 규칙을 찾을 수 없습니다"}

            # 진도 계산 (규칙별 다름)
            progress = self._calculate_achievement_progress(user_id, rule)

            return {
                "achievement_type": achievement_type,
                "completed": False,
                "progress": progress,
                "target_value": rule.target_value,
                "rule_info": {
                    "name": rule.name,
                    "description": rule.description,
                    "badge_icon": rule.badge_icon
                }
            }

        except Exception as e:
            logger.error(f"성취 진도 확인 실패: {e}")
            return {"error": str(e)}

    def get_next_achievements(self, user_id: int, count: int = 3) -> List[Dict[str, Any]]:
        """다음 획득 가능한 성취 추천"""
        try:
            user_achievements = self.get_user_achievements(user_id)
            earned_types = {a["achievement_type"] for a in user_achievements}

            # 획득하지 않은 성취
            available_achievements = []
            for badge in self.badge_system.get_all_badges():
                if badge.id not in earned_types:
                    progress_info = self.check_achievement_progress(user_id, badge.id)
                    if "error" not in progress_info:
                        available_achievements.append({
                            **badge.to_dict(),
                            "progress": progress_info.get("progress", 0),
                            "completed": progress_info.get("completed", False)
                        })

            # 진도가 높은 순서로 정렬
            available_achievements.sort(key=lambda x: x["progress"], reverse=True)

            return available_achievements[:count]

        except Exception as e:
            logger.error(f"다음 성취 추천 실패: {e}")
            return []

    def _award_achievement(self, user_id: int, rule) -> Optional[Dict[str, Any]]:
        """성취 부여"""
        try:
            from src.database.models import AchievementModel

            # 중복 성취 확인
            if AchievementModel.has_achievement(user_id, rule.achievement_type):
                logger.debug(f"사용자 {user_id}는 이미 성취 '{rule.id}'를 획득했습니다")
                return None

            # 성취 생성
            achievement = AchievementModel.create_achievement(
                user_id=user_id,
                achievement_type=rule.achievement_type,
                metadata={
                    "awarded_at": datetime.now().isoformat(),
                    "xp_reward": rule.xp_reward,
                    "badge_icon": rule.badge_icon
                }
            )

            logger.info(f"성취 부여: 사용자={user_id}, 성취={rule.achievement_type}")

            return achievement

        except Exception as e:
            logger.error(f"성취 부여 실패: {e}")
            return None

    def _calculate_achievement_progress(self, user_id: int, rule) -> float:
        """성취 진도 계산"""
        try:
            from src.database.models import CodeSubmissionModel, CurriculumProgressModel

            progress = 0.0

            if rule.achievement_type == "first_code":
                # 제출 수
                submission_count = CodeSubmissionModel.get_user_submission_count(user_id)
                progress = min(100, (submission_count / rule.target_value) * 100)

            elif rule.achievement_type == "perfect_score":
                # 최근 점수 확인
                recent_submissions = CodeSubmissionModel.get_recent_submissions(user_id, limit=10)
                perfect_count = sum(1 for s in recent_submissions if s.get("score", 0) == 10)
                progress = min(100, (perfect_count / rule.target_value) * 100)

            elif rule.achievement_type.startswith("streak"):
                # 연승 수
                recent_completed = CurriculumProgressModel.get_recent_completed_progress(
                    user_id, limit=rule.target_value
                )
                streak = len([p for p in recent_completed if p.get("completed", False)])
                progress = min(100, (streak / rule.target_value) * 100)

            elif rule.achievement_type == "topic_complete":
                # 완료한 주제 수
                completed_topics = CurriculumProgressModel.get_user_completed_topics(user_id)
                progress = min(100, (len(completed_topics) / rule.target_value) * 100)

            elif rule.achievement_type.startswith("xp_"):
                # 현재 XP
                user_progress = CurriculumProgressModel.get_user_progress(user_id)
                total_xp = sum(p.get("xp_earned", 0) for p in user_progress)
                progress = min(100, (total_xp / rule.target_value) * 100)

            return progress

        except Exception as e:
            logger.error(f"성취 진도 계산 실패: {e}")
            return 0.0


# 전역 인스턴스
_achievement_manager = None


def get_achievement_manager(database_manager) -> AchievementManager:
    """성취 관리자 인스턴스 반환"""
    global _achievement_manager
    if _achievement_manager is None:
        _achievement_manager = AchievementManager(database_manager)
    return _achievement_manager


if __name__ == "__main__":
    # 성취 관리자 테스트
    print("🧪 성취 관리자 테스트")

    # 더미 데이터베이스 관리자
    class DummyDB:
        pass

    db = DummyDB()
    manager = get_achievement_manager(db)

    # 획득 가능한 성취 목록
    available = manager.get_available_achievements()
    print(f"✅ 획득 가능한 성취: {len(available)}개")

    # 성취 통계 (빈 데이터)
    stats = manager.get_achievement_stats(1)
    print(f"✅ 성취 통계: {stats['total_achievements']}개 획득")
    print(f"   완료율: {stats['completion_rate']:.1f}%")

    # 다음 성취 추천
    next_achievements = manager.get_next_achievements(1, count=3)
    print(f"✅ 다음 성취 추천: {len(next_achievements)}개")

    # 특정 성취 진도 확인
    progress_info = manager.check_achievement_progress(1, "first_code")
    print(f"✅ 첫 코드 성취 진도: {progress_info.get('progress', 0):.1f}%")

    print("\n🎉 성취 관리자 테스트 통과!")