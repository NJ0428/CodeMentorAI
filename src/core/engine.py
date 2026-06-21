"""
CodeMentorAI 메인 엔진
모든 하위 시스템을 조율하고 중앙 집중식 관리
"""
from typing import Optional, Dict, Any
from loguru import logger
from pathlib import Path

from src.config.settings import settings
from src.config.constants import Level, MessageType
from src.database.db_manager import DatabaseManager
from src.core.session_manager import SessionManager
from src.database.models import UserModel


class CodeMentorEngine:
    """메인 엔진 - 모든 하위 시스템 조율"""

    def __init__(self):
        self.database_manager: Optional[DatabaseManager] = None
        self.session_manager: Optional[SessionManager] = None
        self.is_running = False
        self.current_user = None

        logger.info("CodeMentorAI 엔진 초기화 시작")

    def initialize(self):
        """엔진 초기화"""
        try:
            logger.info("데이터베이스 초기화")
            self.database_manager = DatabaseManager()
            self.database_manager.init_database()

            logger.info("세션 관리자 초기화")
            self.session_manager = SessionManager(self.database_manager)

            self.is_running = True
            logger.info("✅ CodeMentorAI 엔진 초기화 완료")

        except Exception as e:
            logger.error(f"❌ 엔진 초기화 실패: {e}")
            raise

    def shutdown(self):
        """엔진 종료"""
        try:
            if self.session_manager:
                self.session_manager.save_current_session()

            self.is_running = False
            logger.info("CodeMentorAI 엔진 종료 완료")

        except Exception as e:
            logger.error(f"엔진 종료 중 오류 발생: {e}")

    def get_status(self) -> Dict[str, Any]:
        """엔진 상태 반환"""
        try:
            db_info = {}
            if self.database_manager:
                db_info = self.database_manager.get_database_info()

            return {
                "is_running": self.is_running,
                "current_user": self.current_user,
                "database": db_info,
                "session": self.session_manager.get_session_info() if self.session_manager else {}
            }

        except Exception as e:
            logger.error(f"엔진 상태 조회 실패: {e}")
            return {
                "is_running": False,
                "error": str(e)
            }

    def handle_error(self, error: Exception, context: str = ""):
        """에러 처리"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        logger.error(error_msg)

        # UI로 에러 전송 (나중에 구현)
        # self.ui.show_error(error_msg)

    def register_user(self, username: str, email: Optional[str] = None):
        """사용자 등록"""
        try:
            # 기존 사용자 확인
            existing_user = UserModel.get_user_by_username(username)

            if existing_user:
                self.current_user = existing_user
                logger.info(f"기존 사용자 로드: {username}")
            else:
                # 새 사용자 생성
                new_user = UserModel.create_user(username, email)
                self.current_user = new_user
                logger.info(f"새 사용자 생성: {username}")

            return self.current_user

        except Exception as e:
            logger.error(f"사용자 등록 실패: {e}")
            raise

    def get_current_user(self):
        """현재 사용자 반환"""
        return self.current_user


# 전역 엔진 인스턴스
engine = CodeMentorEngine()


if __name__ == "__main__":
    # 엔진 테스트
    try:
        test_engine = CodeMentorEngine()
        test_engine.initialize()

        status = test_engine.get_status()
        print("🔧 엔진 상태:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        test_engine.shutdown()

    except Exception as e:
        print(f"❌ 엔진 테스트 실패: {e}")