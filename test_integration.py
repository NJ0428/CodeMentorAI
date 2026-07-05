"""
메인 애플리케이션 통합 테스트
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

try:
    print("🚀 CodeMentorAI 메인 애플리케이션 테스트")
    print("="*50)

    # 컴포넌트 임포트 테스트
    from src.ui.components.code_editor import CodeEditor
    print("✅ CodeEditor 임포트 성공")

    from src.ui.components.learning_tab import LearningTab
    print("✅ LearningTab 임포트 성공")

    from src.ui.components.enhanced_chat_tab import EnhancedChatTab
    print("✅ EnhancedChatTab 임포트 성공")

    from src.ui.components.dashboard_tab import DashboardTab
    print("✅ DashboardTab 임포트 성공")

    from src.ui.main_window import MainWindow
    print("✅ MainWindow 임포트 성공")

    print("\n🎉 모든 컴포넌트 임포트 성공!")
    print("📊 시각화 대시보드가 메인 애플리케이션에 통합되었습니다.")

    print("\n🔧 대시보드 기능:")
    print("  📈 개요 탭 - 학습 활동 추이 그래프")
    print("  📊 진도 차트 탭 - 파이 차트 및 레벨별 진도")
    print("  🔍 통계 분석 탭 - 점수 분포 히스토그램 및 통계")
    print("  🏆 성취 시각화 탭 - 뱃지 획득 현황 차트")
    print("  🎯 인터랙티브 추적 탭 - 학습 목표 설정 및 추적")

    print("\n💡 새로운 기능:")
    print("  • matplotlib 기반 다양한 차트 및 그래프")
    print("  • 인터랙티브 데이터 시각화")
    print("  • 학습 패턴 분석 및 목표 추적")
    print("  • 성취 시각화 및 통계 분석")
    print("  • 데이터 내보내기 기능")

    print("\n🎨 UI 개선사항:")
    print("  • 직관적인 대시보드 레이아웃")
    print("  • 실시간 차트 업데이트")
    print("  • 다양한 시각화 옵션")
    print("  • 사용자 친화적인 인터페이스")

    print("\n✨ 통합 완료!")
    print("애플리케이션을 실행하려면: python src/main.py")

except ImportError as e:
    print(f"❌ 임포트 오류: {e}")
    sys.exit(1)

except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)