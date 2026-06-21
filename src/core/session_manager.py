"""
학습 세션 관리자
세션 생성, 로드, 저장 및 자동 저장 관리
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from loguru import logger
from threading import Thread
import time

from src.config.settings import settings
from src.database.db_manager import DatabaseManager
from src.database.models import SessionModel


class SessionManager:
    """학습 세션 관리자"""

    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager
        self.current_session: Optional[Dict[str, Any]] = None
        self.current_user_id: Optional[int] = None
        self.auto_save_enabled = True
        self.auto_save_interval = settings.ui.auto_save_interval
        self.auto_save_thread: Optional[Thread] = None
        self.is_running = False

        logger.info("세션 관리자 초기화 완료")

    def create_session(self, user_id: int, topic: Optional[str] = None) -> Dict[str, Any]:
        """새 세션 생성"""
        try:
            # 이전 활성 세션 종료
            if self.current_session:
                self.end_current_session()

            # 새 세션 생성
            new_session = SessionModel.create_session(user_id, topic)
            self.current_session = new_session
            self.current_user_id = user_id

            logger.info(f"새 세션 생성: ID={new_session['id']}, 사용자={user_id}")
            return new_session

        except Exception as e:
            logger.error(f"세션 생성 실패: {e}")
            raise

    def load_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """기존 세션 로드"""
        try:
            db = self.database_manager
            loaded_session = db.fetch_one(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,)
            )

            if loaded_session:
                self.current_session = loaded_session
                logger.info(f"세션 로드 완료: ID={session_id}")

            return loaded_session

        except Exception as e:
            logger.error(f"세션 로드 실패: {e}")
            return None

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """현재 세션 반환"""
        return self.current_session

    def save_current_session(self):
        """현재 세션 저장"""
        try:
            if not self.current_session:
                logger.warning("저장할 활성 세션이 없습니다.")
                return

            # SQLite는 자동 커밋이므로 별도 저장 로직 불필요
            logger.debug(f"세션 저장 완료: ID={self.current_session['id']}")

        except Exception as e:
            logger.error(f"세션 저장 실패: {e}")
            raise

    def end_current_session(self) -> Optional[int]:
        """현재 세션 종료 및 기간 반환"""
        try:
            if not self.current_session:
                return None

            session_id = self.current_session["id"]

            # 세션 종료
            SessionModel.end_session(session_id)

            # 종료된 세션 정보 조회
            duration = SessionModel.get_session_duration(session_id)

            logger.info(f"세션 종료: ID={session_id}, 기간={duration}분")

            self.current_session = None
            return duration

        except Exception as e:
            logger.error(f"세션 종료 실패: {e}")
            return None

    def get_session_info(self) -> Dict[str, Any]:
        """세션 정보 반환"""
        if not self.current_session:
            return {
                "active": False,
                "session_id": None,
                "duration": 0
            }

        # 세션 활성 상태 확인
        is_active = self.current_session.get("end_time") is None

        return {
            "active": is_active,
            "session_id": self.current_session["id"],
            "topic": self.current_session.get("curriculum_topic"),
            "start_time": self.current_session.get("start_time"),
            "duration": SessionModel.get_session_duration(self.current_session["id"]) if not is_active else 0
        }

    def start_auto_save(self):
        """자동 저장 시작"""
        if not self.auto_save_enabled:
            return

        self.is_running = True
        self.auto_save_thread = Thread(target=self._auto_save_loop, daemon=True)
        self.auto_save_thread.start()
        logger.info(f"자동 저장 시작 (간격: {self.auto_save_interval}초)")

    def stop_auto_save(self):
        """자동 저장 중지"""
        self.is_running = False
        if self.auto_save_thread:
            self.auto_save_thread.join(timeout=5)
        logger.info("자동 저장 중지")

    def _auto_save_loop(self):
        """자동 저장 루프"""
        while self.is_running:
            try:
                time.sleep(self.auto_save_interval)
                if self.current_session:
                    self.save_current_session()
                    logger.debug("자동 저장 완료")

            except Exception as e:
                logger.error(f"자동 저장 중 오류 발생: {e}")

    def get_user_total_study_time(self, user_id: int) -> int:
        """사용자 총 학습 시간 조회 (분)"""
        try:
            db = self.database_manager

            # 완료된 세션들의 총 시간 계산
            completed_sessions = db.fetch_all(
                """SELECT * FROM sessions
                   WHERE user_id = ? AND end_time IS NOT NULL""",
                (user_id,)
            )

            total_minutes = 0
            for session in completed_sessions:
                total_minutes += SessionModel.get_session_duration(session["id"])

            # 현재 세션 시간 추가 (활성인 경우)
            if self.current_session and self.current_session.get("end_time") is None:
                if self.current_session.get("start_time"):
                    start = datetime.fromisoformat(self.current_session["start_time"])
                    duration = datetime.utcnow() - start
                    total_minutes += int(duration.total_seconds() / 60)

            return total_minutes

        except Exception as e:
            logger.error(f"학습 시간 조회 실패: {e}")
            return 0

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """오래된 세션 정리"""
        try:
            db = self.database_manager
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # 오래된 세션 삭제
            db.execute_query(
                "DELETE FROM sessions WHERE end_time < ?",
                (cutoff_date.isoformat(),)
            )

            # 삭제된 세션 수 확인
            result = db.fetch_one("SELECT changes() as count")
            count = result["count"] if result else 0

            logger.info(f"{count}개의 오래된 세션 삭제 완료")
            return count

        except Exception as e:
            logger.error(f"세션 정리 실패: {e}")
            return 0