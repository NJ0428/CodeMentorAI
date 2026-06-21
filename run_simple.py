"""
간단한 실행 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.core.engine import CodeMentorEngine
from src.ui.main_window import MainWindow

# 로그 설정 (간단하게)
logger.remove()
logger.add(sys.stderr, level="INFO")

try:
    print("CodeMentorAI 시작...")

    # 엔진 초기화
    print("엔진 초기화 중...")
    engine = CodeMentorEngine()
    engine.initialize()
    print("엔진 초기화 완료")

    # UI 생성 및 실행
    print("UI 생성 중...")
    app = MainWindow()
    print("UI 생성 완료")

    print("애플리케이션 시작!")
    app.run()

except KeyboardInterrupt:
    print("\n애플리케이션이 사용자에 의해 중단되었습니다.")
except Exception as e:
    print(f"에러: {e}")
    import traceback
    traceback.print_exc()