"""
학습 시스템 통합 테스트
모든 컴포넌트가 올바르게 작동하는지 확인
"""
import sys
import os
from pathlib import Path

# UTF-8 인코딩 설정
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger

# 테스트를 위한 의존성 모의 설정
try:
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:
    # tenacity가 없는 경우 mock 생성
    import sys
    import functools

    class retry:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
        def __call__(self, func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

    def stop_after_attempt(max_attempts):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def wait_exponential(multiplier, min, max):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    # mock을 sys.modules에 등록
    tenacity_module = type(sys)('tenacity')
    tenacity_module.retry = retry
    tenacity_module.stop_after_attempt = stop_after_attempt
    tenacity_module.wait_exponential = wait_exponential
    sys.modules['tenacity'] = tenacity_module

try:
    from anthropic import Anthropic
except ImportError:
    # anthropic가 없는 경우 mock 생성
    import sys
    class Anthropic:
        def __init__(self, *args, **kwargs):
            pass

        class messages:
            @staticmethod
            def create(*args, **kwargs):
                class Response:
                    content = [type('Content', (), {'text': 'Mock response'})()]
                return Response()

    anthropic_module = type(sys)('anthropic')
    anthropic_module.Anthropic = Anthropic
    sys.modules['anthropic'] = anthropic_module


def test_curriculum_system():
    """커리큘럼 시스템 테스트"""
    print("\n" + "="*50)
    print("🧪 커리큘럼 시스템 테스트")
    print("="*50)

    try:
        from src.learning.curriculum import get_curriculum_manager, DifficultyLevel

        manager = get_curriculum_manager()

        # 초급 커리큘럼 로드
        beginner_curriculum = manager.get_curriculum(DifficultyLevel.BEGINNER)
        if beginner_curriculum:
            print(f"✅ 초급 커리큘럼: {beginner_curriculum.name}")
            print(f"   주제 수: {beginner_curriculum.get_total_topics()}")
            for topic in beginner_curriculum.topics:
                print(f"   - {topic.title} ({len(topic.exercises)}개 문제)")
        else:
            print("❌ 초급 커리큘럼 로드 실패")

        # 중급 커리큘럼 로드
        intermediate_curriculum = manager.get_curriculum(DifficultyLevel.INTERMEDIATE)
        if intermediate_curriculum:
            print(f"✅ 중급 커리큘럼: {intermediate_curriculum.name}")
            print(f"   주제 수: {intermediate_curriculum.get_total_topics()}")

        # 고급 커리큘럼 로드
        advanced_curriculum = manager.get_curriculum(DifficultyLevel.ADVANCED)
        if advanced_curriculum:
            print(f"✅ 고급 커리큘럼: {advanced_curriculum.name}")
            print(f"   주제 수: {advanced_curriculum.get_total_topics()}")

        print("🎉 커리큘럼 시스템 테스트 통과!")
        return True

    except Exception as e:
        print(f"❌ 커리큘럼 시스템 테스트 실패: {e}")
        return False


def test_progress_system():
    """진도 추적 시스템 테스트"""
    print("\n" + "="*50)
    print("🧪 진도 추적 시스템 테스트")
    print("="*50)

    try:
        from src.learning.progress import get_progress_calculator

        calculator = get_progress_calculator()

        # 테스트 데이터
        test_progress = [
            {"level": "beginner", "completed": True, "score": 8, "study_minutes": 30, "xp_earned": 50},
            {"level": "beginner", "completed": True, "score": 9, "study_minutes": 25, "xp_earned": 60},
            {"level": "beginner", "completed": False, "score": 6, "study_minutes": 15, "xp_earned": 20}
        ]

        # 완료율 계산
        completion_rate = calculator.calculate_completion_rate(test_progress)
        print(f"✅ 완료율: {completion_rate:.1f}%")

        # 평균 점수 계산
        average_score = calculator.calculate_average_score(test_progress)
        print(f"✅ 평균 점수: {average_score:.1f}")

        # 레벨별 진도 계산
        from src.learning.curriculum.models import DifficultyLevel
        level_progress = calculator.calculate_level_progress(test_progress, DifficultyLevel.BEGINNER)
        print(f"✅ 초급 진도: {level_progress['completed']}/{level_progress['total']} 완료")

        print("🎉 진도 추적 시스템 테스트 통과!")
        return True

    except Exception as e:
        print(f"❌ 진도 추적 시스템 테스트 실패: {e}")
        return False


def test_achievement_system():
    """성취 시스템 테스트"""
    print("\n" + "="*50)
    print("🧪 성취 시스템 테스트")
    print("="*50)

    try:
        from src.learning.achievements import get_badge_system

        badge_system = get_badge_system()

        # 모든 뱃지 조회
        all_badges = badge_system.get_all_badges()
        print(f"✅ 전체 뱃지: {len(all_badges)}개")

        # 카테고리별 뱃지
        from src.learning.achievements import BadgeCategory
        milestone_badges = badge_system.get_badges_by_category(BadgeCategory.MILESTONE)
        print(f"✅ 마일스톤 뱃지: {len(milestone_badges)}개")

        # 특정 뱃지 조회
        perfect_badge = badge_system.get_badge("perfect_score")
        if perfect_badge:
            print(f"✅ 뱃지 조회: {perfect_badge.name} ({perfect_badge.icon})")
            print(f"   희귀도: {perfect_badge.rarity.value}")

        print("🎉 성취 시스템 테스트 통과!")
        return True

    except Exception as e:
        print(f"❌ 성취 시스템 테스트 실패: {e}")
        return False


def test_learning_manager():
    """학습 관리자 테스트"""
    print("\n" + "="*50)
    print("🧪 학습 관리자 테스트")
    print("="*50)

    try:
        from src.learning.learning_manager import get_learning_manager
        from src.learning.curriculum.models import DifficultyLevel

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

        # 획득 가능한 성취
        available_achievements = manager.get_available_achievements()
        print(f"✅ 획득 가능한 성취: {len(available_achievements)}개")

        print("🎉 학습 관리자 테스트 통과!")
        return True

    except Exception as e:
        print(f"❌ 학습 관리자 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_components():
    """UI 컴포넌트 테스트"""
    print("\n" + "="*50)
    print("🧪 UI 컴포넌트 테스트")
    print("="*50)

    try:
        # UI 컴포넌트 임포트 확인
        from src.ui.components.learning_tab import LearningTab
        print("✅ LearningTab 임포트 성공")

        print("🎉 UI 컴포넌트 테스트 통과!")
        return True

    except Exception as e:
        print(f"❌ UI 컴포넌트 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("🚀 CodeMentorAI 학습 시스템 통합 테스트 시작")

    results = []

    # 각 시스템 테스트
    results.append(("커리큘럼 시스템", test_curriculum_system()))
    results.append(("진도 추적 시스템", test_progress_system()))
    results.append(("성취 시스템", test_achievement_system()))
    results.append(("학습 관리자", test_learning_manager()))
    results.append(("UI 컴포넌트", test_ui_components()))

    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status}: {name}")

    print(f"\n총 결과: {passed}/{total} 테스트 통과")

    if passed == total:
        print("🎉 모든 테스트 통과! 학습 시스템이 성공적으로 구현되었습니다.")
        return 0
    else:
        print("⚠️  일부 테스트가 실패했습니다. 구현을 확인해주세요.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)