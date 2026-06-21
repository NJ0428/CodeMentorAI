"""
데이터베이스 관리자
SQLite (sqlite3) 기반 데이터베이스 관리
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from src.config.settings import settings


class DatabaseManager:
    """데이터베이스 관리자 (SQLite 기반)"""

    def __init__(self, database_path: Optional[str] = None):
        self.database_path = database_path or self._get_db_path()
        self.connection = None
        self._initialize_database()

        logger.info(f"데이터베이스 관리자 초기화: {self.database_path}")

    def _get_db_path(self) -> str:
        """데이터베이스 파일 경로 반환"""
        db_url = settings.database.path
        if "sqlite:///" in db_url:
            return db_url.replace("sqlite:///", "")
        return db_url

    def _initialize_database(self):
        """데이터베이스 초기화 (내부 메서드)"""
        try:
            # 데이터베이스 파일 디렉토리 생성
            db_file = Path(self.database_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)

            # 테이블 생성
            self.create_tables()

            logger.info("데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise

    def init_database(self):
        """데이터베이스 초기화 (공개 메서드)"""
        self._initialize_database()

    def get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환"""
        try:
            if self.connection is None:
                self.connection = sqlite3.connect(self.database_path)
                self.connection.row_factory = sqlite3.Row  # 딕셔너리 형식 접근

                # 외래 키 활성화
                self.connection.execute("PRAGMA foreign_keys = ON")

            return self.connection

        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise

    def close_connection(self):
        """데이터베이스 연결 종료"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                logger.info("데이터베이스 연결 종료")

        except Exception as e:
            logger.error(f"데이터베이스 연결 종료 실패: {e}")

    def create_tables(self):
        """모든 테이블 생성"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 사용자 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_level TEXT DEFAULT 'beginner',
                    total_study_time INTEGER DEFAULT 0,
                    settings_json TEXT
                )
            """)

            # 세션 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    curriculum_topic TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 코드 제출 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    exercise_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 분석 결과 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    score INTEGER,
                    issues_json TEXT,
                    suggestions_json TEXT,
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (submission_id) REFERENCES code_submissions(id)
                )
            """)

            # AI 대화 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER,
                    FOREIGN KEY (submission_id) REFERENCES code_submissions(id)
                )
            """)

            # 커리큘럼 진도 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS curriculum_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    topic_id TEXT NOT NULL,
                    level TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    score INTEGER,
                    last_attempted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, topic_id, level)
                )
            """)

            # 성취 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_type TEXT NOT NULL,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata_json TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            conn.commit()
            logger.info("데이터베이스 테이블 생성 완료")

        except Exception as e:
            logger.error(f"테이블 생성 실패: {e}")
            raise

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """쿼리 실행"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

        except Exception as e:
            logger.error(f"쿼리 실행 실패: {e}")
            raise

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """단일 행 조회"""
        try:
            cursor = self.execute_query(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

        except Exception as e:
            logger.error(f"단일 행 조회 실패: {e}")
            return None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """전체 행 조회"""
        try:
            cursor = self.execute_query(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"전체 행 조회 실패: {e}")
            return []

    def backup_database(self, backup_path: Optional[str] = None) -> Optional[str]:
        """데이터베이스 백업"""
        try:
            db_file = Path(self.database_path)

            if backup_path is None:
                backup_dir = Path("backups")
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

            # 파일 복사
            import shutil
            shutil.copy2(db_file, backup_path)

            logger.info(f"데이터베이스 백업 완료: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"데이터베이스 백업 실패: {e}")
            return None

    def get_database_info(self) -> Dict[str, Any]:
        """데이터베이스 정보 반환"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 테이블별 row count
            info = {
                "database_path": self.database_path,
                "user_count": 0,
                "session_count": 0,
                "submission_count": 0,
                "analysis_count": 0
            }

            # 사용자 수
            cursor.execute("SELECT COUNT(*) FROM users")
            info["user_count"] = cursor.fetchone()[0]

            # 세션 수
            cursor.execute("SELECT COUNT(*) FROM sessions")
            info["session_count"] = cursor.fetchone()[0]

            # 코드 제출 수
            cursor.execute("SELECT COUNT(*) FROM code_submissions")
            info["submission_count"] = cursor.fetchone()[0]

            # 분석 결과 수
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            info["analysis_count"] = cursor.fetchone()[0]

            return info

        except Exception as e:
            logger.error(f"데이터베이스 정보 조회 실패: {e}")
            return {"error": str(e)}

    def __del__(self):
        """소멸자 - 연결 정리"""
        self.close_connection()


# 전역 데이터베이스 관리자 인스턴스
db_manager = None


def get_db_manager() -> DatabaseManager:
    """데이터베이스 관리자 인스턴스 반환"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


if __name__ == "__main__":
    # 데이터베이스 관리자 테스트
    try:
        manager = DatabaseManager()

        info = manager.get_database_info()
        print("📊 데이터베이스 정보:")
        for key, value in info.items():
            print(f"  {key}: {value}")

        # 연결 종료
        manager.close_connection()

    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")