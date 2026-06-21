"""
간단한 실행 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("1. 의존성 체크 시작...")
    import anthropic
    import dotenv
    import loguru
    print("OK 의존성 체크 통과")

    print("2. 설정 로드 시작...")
    from src.config.settings import settings
    print("OK 설정 로드 완료")

    print("3. API 키 확인 시작...")
    from src.config.api_keys import api_key_manager
    api_info = api_key_manager.get_safe_key_info()
    print(f"API 키 정보: {api_info}")
    print("OK API 키 확인 완료")

    print("4. 엔진 초기화 시작...")
    from src.core.engine import CodeMentorEngine
    engine = CodeMentorEngine()
    print("OK 엔진 인스턴스 생성")

    engine.initialize()
    print("OK 엔진 초기화 완료")

    print("5. UI 생성 시작...")
    from src.ui.main_window import MainWindow
    app = MainWindow()
    print("OK UI 생성 완료")

    print("SUCCESS: 모든 초기화 완료!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)