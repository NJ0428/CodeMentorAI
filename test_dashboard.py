"""
시각화 대시보드 테스트
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
    import tkinter as tk
    from src.ui.components.dashboard_tab import DashboardTab

    print("🧪 시각화 대시보드 테스트 시작")

    root = tk.Tk()
    root.title("시각화 대시보드 테스트")
    root.geometry("1200x800")

    dashboard_tab = DashboardTab(root)
    dashboard_tab.pack(fill=tk.BOTH, expand=True)

    print("✅ 대시보드 컴포넌트 생성 성공")
    print("📊 다음 기능들이 포함되어 있습니다:")
    print("  • 개요 탭 - 주요 통계 카드 및 학습 활동 그래프")
    print("  • 진도 차트 탭 - 파이 차트 및 레벨별 진도")
    print("  • 통계 분석 탭 - 점수 분포 및 성과 통계")
    print("  • 성취 시각화 탭 - 뱃지 획득 현황")
    print("  • 인터랙티브 추적 탭 - 학습 목표 설정 및 추적")

    root.mainloop()

    print("✅ 시각화 대시보드 테스트 완료")

except ImportError as e:
    print(f"❌ 임포트 오류: {e}")
    print("필요한 패키지를 설치하세요:")
    print("pip install matplotlib plotly pandas numpy")
    sys.exit(1)

except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)