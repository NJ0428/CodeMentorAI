"""
CodeMentorAI 메인 진입점
애플리케이션 초기화 및 실행
"""
import sys
import logging
from pathlib import Path
from loguru import logger
import tkinter as tk
from tkinter import messagebox

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import settings
from src.config.api_keys import api_key_manager
from src.core.engine import CodeMentorEngine
from src.ui.main_window import MainWindow


def setup_logging():
    """로깅 시스템 설정"""
    try:
        # loguru 설정
        logger.remove()  # 기본 핸들러 제거

        # 콘솔 출력
        logger.add(
            sys.stderr,
            level=settings.logging.level,
            format=settings.logging.format
        )

        # 파일 출력
        log_file = Path(settings.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            settings.logging.file_path,
            level=settings.logging.level,
            format=settings.logging.format,
            rotation=settings.logging.rotation,
            retention=settings.logging.retention
        )

        logger.info("로깅 시스템 초기화 완료")

    except Exception as e:
        print(f"로깅 시스템 초기화 실패: {e}")
        raise


def check_dependencies():
    """필수 의존성 확인"""
    missing_packages = []

    try:
        import anthropic
    except ImportError:
        missing_packages.append("anthropic")

    try:
        import python_dotenv
    except ImportError:
        missing_packages.append("python-dotenv")

    try:
        import loguru
    except ImportError:
        missing_packages.append("loguru")

    if missing_packages:
        error_msg = f"필수 패키지가 누락되었습니다: {', '.join(missing_packages)}\n"
        error_msg += "설치 방법: pip install -r requirements/base.txt"
        print(error_msg)
        return False

    return True


def check_api_key():
    """API 키 확인"""
    try:
        api_info = api_key_manager.get_safe_key_info()

        if not api_info["is_set"]:
            logger.error("API 키가 설정되지 않았습니다.")
            return False

        if not api_info["is_valid_format"]:
            logger.error("API 키 형식이 올바르지 않습니다.")
            return False

        logger.info(f"API 키 확인 완료: {api_info['key_preview']}")
        return True

    except Exception as e:
        logger.error(f"API 키 확인 중 오류 발생: {e}")
        return False


def initialize_engine() -> CodeMentorEngine:
    """엔진 초기화"""
    try:
        engine = CodeMentorEngine()
        engine.initialize()
        return engine

    except Exception as e:
        logger.error(f"엔진 초기화 실패: {e}")
        raise


def create_application(engine: CodeMentorEngine) -> MainWindow:
    """UI 애플리케이션 생성"""
    try:
        app = MainWindow()
        return app

    except Exception as e:
        logger.error(f"UI 애플리케이션 생성 실패: {e}")
        raise


def show_startup_error(title: str, message: str):
    """시작 오류 표시"""
    try:
        root = tk.Tk()
        root.withdraw()  # 메인 윈도우 숨기기
        messagebox.showerror(title, message)
        root.destroy()
    except:
        # GUI가 작동하지 않는 경우 콘솔에 메시지 출력
        print(f"{title}: {message}")


def main():
    """메인 함수"""
    try:
        # 애플리케이션 시작 메시지
        logger.info("=" * 50)
        logger.info("CodeMentorAI 시작 중...")
        logger.info("=" * 50)

        # 1. 의존성 확인
        if not check_dependencies():
            show_startup_error(
                "의존성 오류",
                "필수 패키지가 누락되었습니다.\n"
                "터미널에서 다음 명령을 실행하세요:\n"
                "pip install -r requirements/base.txt"
            )
            sys.exit(1)

        # 2. 로깅 설정
        setup_logging()

        # 3. API 키 확인
        if not check_api_key():
            show_startup_error(
                "API 키 오류",
                "API 키가 설정되지 않았습니다.\n"
                ".env 파일에 ANTHROPIC_API_KEY를 설정하세요."
            )
            sys.exit(1)

        # 4. 설정 유효성 확인
        try:
            settings.validate()
            logger.info("설정 유효성 검사 통과")
        except ValueError as e:
            show_startup_error("설정 오류", str(e))
            sys.exit(1)

        # 5. 엔진 초기화
        logger.info("엔진 초기화 중...")
        app_engine = initialize_engine()

        # 6. UI 생성 및 실행
        logger.info("UI 생성 중...")
        app = create_application(app_engine)

        # 애플리케이션 실행
        logger.info("애플리케이션 시작 완료!")
        logger.info("=" * 50)

        app.run()

        # 정상 종료
        logger.info("CodeMentorAI가 정상적으로 종료되었습니다.")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("사용자에 의해 애플리케이션이 중단되었습니다.")
        sys.exit(0)

    except Exception as e:
        error_msg = f"애플리케이션 시작 중 치명적 오류 발생: {e}"
        logger.error(error_msg)
        show_startup_error("시작 오류", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()