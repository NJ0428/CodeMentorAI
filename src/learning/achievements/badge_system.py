"""
뱃지 시스템
성취 뱃지 정보 및 아이콘 관리
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class BadgeCategory(str, Enum):
    """뱃지 카테고리"""
    MILESTONE = "milestone"      # 마일스톤
    STREAK = "streak"            # 연승
    SKILL = "skill"             # 스킬
    TIME = "time"               # 시간
    SOCIAL = "social"           # 소셜
    SPECIAL = "special"         # 특별


class BadgeRarity(str, Enum):
    """뱃지 희귀도"""
    COMMON = "common"           # 일반
    RARE = "rare"              # 희귀
    EPIC = "epic"              # 에픽
    LEGENDARY = "legendary"     # 전설


@dataclass
class BadgeInfo:
    """뱃지 정보"""
    id: str
    name: str
    description: str
    icon: str
    category: BadgeCategory
    rarity: BadgeRarity
    xp_reward: int
    unlock_requirements: str

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category.value,
            "rarity": self.rarity.value,
            "xp_reward": self.xp_reward,
            "unlock_requirements": self.unlock_requirements
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BadgeInfo':
        """딕셔너리에서 인스턴스 생성"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            icon=data["icon"],
            category=BadgeCategory(data["category"]),
            rarity=BadgeRarity(data["rarity"]),
            xp_reward=data["xp_reward"],
            unlock_requirements=data["unlock_requirements"]
        )


class BadgeSystem:
    """뱃지 시스템"""

    def __init__(self):
        self.badges = self._initialize_badges()
        logger.info("뱃지 시스템 초기화 완료")

    def get_badge(self, badge_id: str) -> Optional[BadgeInfo]:
        """뱃지 정보 조회"""
        return self.badges.get(badge_id)

    def get_all_badges(self) -> List[BadgeInfo]:
        """모든 뱃지 목록 반환"""
        return list(self.badges.values())

    def get_badges_by_category(self, category: BadgeCategory) -> List[BadgeInfo]:
        """카테고리별 뱃지 목록 반환"""
        return [badge for badge in self.badges.values() if badge.category == category]

    def get_badges_by_rarity(self, rarity: BadgeRarity) -> List[BadgeInfo]:
        """희귀도별 뱃지 목록 반환"""
        return [badge for badge in self.badges.values() if badge.rarity == rarity]

    def calculate_badge_power(self, badge_id: str) -> int:
        """뱃지 파워 계산 (희귀도 기반)"""
        badge = self.get_badge(badge_id)
        if not badge:
            return 0

        rarity_power = {
            BadgeRarity.COMMON: 1,
            BadgeRarity.RARE: 2,
            BadgeRarity.EPIC: 3,
            BadgeRarity.LEGENDARY: 5
        }

        return rarity_power.get(badge.rarity, 0)

    def get_rarity_color(self, rarity: BadgeRarity) -> str:
        """희귀도별 색상 반환"""
        colors = {
            BadgeRarity.COMMON: "#808080",      # 회색
            BadgeRarity.RARE: "#0078D4",        # 파란색
            BadgeRarity.EPIC: "#9B59B6",        # 보라색
            BadgeRarity.LEGENDARY: "#FFD700"     # 금색
        }
        return colors.get(rarity, "#808080")

    def _initialize_badges(self) -> Dict[str, BadgeInfo]:
        """뱃지 초기화"""
        badges = {}

        # 마일스톤 뱃지
        badges["first_code"] = BadgeInfo(
            id="first_code",
            name="첫 번째 코드",
            description="첫 번째 코드를 제출했습니다",
            icon="🎯",
            category=BadgeCategory.MILESTONE,
            rarity=BadgeRarity.COMMON,
            xp_reward=10,
            unlock_requirements="첫 번째 코드 제출"
        )

        badges["perfect_score"] = BadgeInfo(
            id="perfect_score",
            name="완벽 점수",
            description="완벽한 점수를 받았습니다",
            icon="⭐",
            category=BadgeCategory.MILESTONE,
            rarity=BadgeRarity.RARE,
            xp_reward=20,
            unlock_requirements="10점 만점 획득"
        )

        # 연승 뱃지
        badges["streak_5"] = BadgeInfo(
            id="streak_5",
            name="5연승",
            description="5개 연속 문제를 완료했습니다",
            icon="🔥",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.COMMON,
            xp_reward=30,
            unlock_requirements="5개 연속 문제 완료"
        )

        badges["streak_10"] = BadgeInfo(
            id="streak_10",
            name="10연승",
            description="10개 연속 문제를 완료했습니다",
            icon="💯",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.RARE,
            xp_reward=50,
            unlock_requirements="10개 연속 문제 완료"
        )

        badges["streak_30"] = BadgeInfo(
            id="streak_30",
            name="30연승",
            description="30개 연속 문제를 완료했습니다",
            icon="🏆",
            category=BadgeCategory.STREAK,
            rarity=BadgeRarity.EPIC,
            xp_reward=150,
            unlock_requirements="30개 연속 문제 완료"
        )

        # 스킬 뱃지
        badges["completed_topic"] = BadgeInfo(
            id="completed_topic",
            name="주제 완료",
            description="첫 번째 주제를 완료했습니다",
            icon="📚",
            category=BadgeCategory.SKILL,
            rarity=BadgeRarity.COMMON,
            xp_reward=40,
            unlock_requirements="주제 1개 완료"
        )

        badges["level_up_beginner"] = BadgeInfo(
            id="level_up_beginner",
            name="초급 달성",
            description="초급 과정을 완료했습니다",
            icon="🎓",
            category=BadgeCategory.SKILL,
            rarity=BadgeRarity.RARE,
            xp_reward=100,
            unlock_requirements="초급 과정 완료"
        )

        badges["level_up_intermediate"] = BadgeInfo(
            id="level_up_intermediate",
            name="중급 달성",
            description="중급 과정을 완료했습니다",
            icon="🎖️",
            category=BadgeCategory.SKILL,
            rarity=BadgeRarity.EPIC,
            xp_reward=200,
            unlock_requirements="중급 과정 완료"
        )

        badges["level_up_advanced"] = BadgeInfo(
            id="level_up_advanced",
            name="고급 달성",
            description="고급 과정을 완료했습니다",
            icon="👑",
            category=BadgeCategory.SKILL,
            rarity=BadgeRarity.LEGENDARY,
            xp_reward=500,
            unlock_requirements="고급 과정 완료"
        )

        # XP 마일스톤 뱃지
        badges["xp_100"] = BadgeInfo(
            id="xp_100",
            name="100 XP",
            description="100 XP를 획득했습니다",
            icon="💎",
            category=BadgeCategory.MILESTONE,
            rarity=BadgeRarity.COMMON,
            xp_reward=0,
            unlock_requirements="100 XP 획득"
        )

        badges["xp_500"] = BadgeInfo(
            id="xp_500",
            name="500 XP",
            description="500 XP를 획득했습니다",
            icon="💠",
            category=BadgeCategory.MILESTONE,
            rarity=BadgeRarity.RARE,
            xp_reward=0,
            unlock_requirements="500 XP 획득"
        )

        badges["xp_1000"] = BadgeInfo(
            id="xp_1000",
            name="1000 XP",
            description="1000 XP를 획득했습니다",
            icon="🔮",
            category=BadgeCategory.MILESTONE,
            rarity=BadgeRarity.EPIC,
            xp_reward=0,
            unlock_requirements="1000 XP 획득"
        )

        # 시간 뱃지
        badges["study_1_hour"] = BadgeInfo(
            id="study_1_hour",
            name="1시간 학습",
            description="1시간 이상 학습했습니다",
            icon="⏰",
            category=BadgeCategory.TIME,
            rarity=BadgeRarity.COMMON,
            xp_reward=10,
            unlock_requirements="1시간 학습"
        )

        badges["study_10_hours"] = BadgeInfo(
            id="study_10_hours",
            name="10시간 학습",
            description="10시간 이상 학습했습니다",
            icon="🕐",
            category=BadgeCategory.TIME,
            rarity=BadgeRarity.RARE,
            xp_reward=50,
            unlock_requirements="10시간 학습"
        )

        # 특별 뱃지
        badges["early_adopter"] = BadgeInfo(
            id="early_adopter",
            name="얼리 어답터",
            description="CodeMentorAI 초기 사용자입니다",
            icon="🚀",
            category=BadgeCategory.SPECIAL,
            rarity=BadgeRarity.LEGENDARY,
            xp_reward=100,
            unlock_requirements="서비스 초기 참여"
        )

        logger.info(f"뱃지 {len(badges)}개 초기화 완료")
        return badges


# 전역 인스턴스
_badge_system = None


def get_badge_system() -> BadgeSystem:
    """뱃지 시스템 인스턴스 반환"""
    global _badge_system
    if _badge_system is None:
        _badge_system = BadgeSystem()
    return _badge_system


if __name__ == "__main__":
    # 뱃지 시스템 테스트
    print("🧪 뱃지 시스템 테스트")

    badge_system = get_badge_system()

    # 모든 뱃지 조회
    all_badges = badge_system.get_all_badges()
    print(f"✅ 전체 뱃지: {len(all_badges)}개")

    # 카테고리별 뱃지
    milestone_badges = badge_system.get_badges_by_category(BadgeCategory.MILESTONE)
    print(f"✅ 마일스톤 뱃지: {len(milestone_badges)}개")

    streak_badges = badge_system.get_badges_by_category(BadgeCategory.STREAK)
    print(f"✅ 연승 뱃지: {len(streak_badges)}개")

    # 특정 뱃지 조회
    perfect_badge = badge_system.get_badge("perfect_score")
    if perfect_badge:
        print(f"✅ 뱃지 조회: {perfect_badge.name} ({perfect_badge.icon})")
        print(f"   희귀도: {perfect_badge.rarity.value}")
        print(f"   파워: {badge_system.calculate_badge_power('perfect_score')}")

    # 희귀도별 색상
    for rarity in BadgeRarity:
        color = badge_system.get_rarity_color(rarity)
        print(f"✅ {rarity.value} 색상: {color}")

    print("\n🎉 뱃지 시스템 테스트 통과!")