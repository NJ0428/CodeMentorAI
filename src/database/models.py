"""
데이터베이스 모델 및 유틸리티 함수
SQLite 기반 데이터베이스 작업 헬퍼 함수
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

from src.database.db_manager import get_db_manager


class UserModel:
    """사용자 모델 헬퍼"""

    @staticmethod
    def create_user(username: str, email: Optional[str] = None) -> Dict[str, Any]:
        """사용자 생성"""
        db = get_db_manager()
        query = """
            INSERT INTO users (username, email, created_at, current_level)
            VALUES (?, ?, ?, ?)
        """
        db.execute_query(query, (username, email, datetime.utcnow(), "beginner"))

        # 생성된 사용자 조회
        return UserModel.get_user_by_username(username)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """사용자명으로 사용자 조회"""
        db = get_db_manager()
        return db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """ID로 사용자 조회"""
        db = get_db_manager()
        return db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )

    @staticmethod
    def update_level(user_id: int, new_level: str):
        """사용자 수준 업데이트"""
        db = get_db_manager()
        db.execute_query(
            "UPDATE users SET current_level = ? WHERE id = ?",
            (new_level, user_id)
        )

    @staticmethod
    def add_study_time(user_id: int, minutes: int):
        """학습 시간 추가"""
        db = get_db_manager()
        db.execute_query(
            "UPDATE users SET total_study_time = total_study_time + ? WHERE id = ?",
            (minutes, user_id)
        )


class SessionModel:
    """세션 모델 헬퍼"""

    @staticmethod
    def create_session(user_id: int, topic: Optional[str] = None) -> Dict[str, Any]:
        """세션 생성"""
        db = get_db_manager()
        query = """
            INSERT INTO sessions (user_id, start_time, curriculum_topic)
            VALUES (?, ?, ?)
        """
        db.execute_query(query, (user_id, datetime.utcnow(), topic))

        # 생성된 세션 조회 (마지막 ID)
        session = db.fetch_one("SELECT * FROM sessions WHERE id = last_insert_rowid()")
        return session

    @staticmethod
    def get_active_session(user_id: int) -> Optional[Dict[str, Any]]:
        """활성 세션 조회"""
        db = get_db_manager()
        return db.fetch_one(
            "SELECT * FROM sessions WHERE user_id = ? AND end_time IS NULL ORDER BY id DESC LIMIT 1",
            (user_id,)
        )

    @staticmethod
    def end_session(session_id: int):
        """세션 종료"""
        db = get_db_manager()
        db.execute_query(
            "UPDATE sessions SET end_time = ? WHERE id = ?",
            (datetime.utcnow(), session_id)
        )

    @staticmethod
    def get_session_duration(session_id: int) -> int:
        """세션 지속 시간 (분) 반환"""
        db = get_db_manager()
        session = db.fetch_one(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        )

        if session and session["end_time"]:
            start = datetime.fromisoformat(session["start_time"])
            end = datetime.fromisoformat(session["end_time"])
            duration = end - start
            return int(duration.total_seconds() / 60)
        return 0


class CodeSubmissionModel:
    """코드 제출 모델 헬퍼"""

    @staticmethod
    def create_submission(session_id: int, user_id: int, code: str, exercise_id: Optional[str] = None) -> Dict[str, Any]:
        """코드 제출 생성"""
        db = get_db_manager()
        query = """
            INSERT INTO code_submissions (session_id, user_id, code, submitted_at, exercise_id)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute_query(query, (session_id, user_id, code, datetime.utcnow(), exercise_id))

        # 생성된 제출 조회
        return db.fetch_one("SELECT * FROM code_submissions WHERE id = last_insert_rowid()")

    @staticmethod
    def get_submission_by_id(submission_id: int) -> Optional[Dict[str, Any]]:
        """ID로 코드 제출 조회"""
        db = get_db_manager()
        return db.fetch_one(
            "SELECT * FROM code_submissions WHERE id = ?",
            (submission_id,)
        )

    @staticmethod
    def get_user_submissions(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 코드 제출 목록 조회"""
        db = get_db_manager()
        return db.fetch_all(
            "SELECT * FROM code_submissions WHERE user_id = ? ORDER BY submitted_at DESC LIMIT ?",
            (user_id, limit)
        )


class AnalysisResultModel:
    """분석 결과 모델 헬퍼"""

    @staticmethod
    def create_analysis_result(submission_id: int, score: int, issues: List[Dict], suggestions: List[Dict]) -> Dict[str, Any]:
        """분석 결과 생성"""
        db = get_db_manager()
        import json

        query = """
            INSERT INTO analysis_results (submission_id, score, issues_json, suggestions_json, analysis_timestamp)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            submission_id,
            score,
            json.dumps(issues),
            json.dumps(suggestions),
            datetime.utcnow()
        ))

        # 생성된 결과 조회
        return db.fetch_one("SELECT * FROM analysis_results WHERE id = last_insert_rowid()")

    @staticmethod
    def get_analysis_by_submission(submission_id: int) -> Optional[Dict[str, Any]]:
        """제출 ID로 분석 결과 조회"""
        db = get_db_manager()
        result = db.fetch_one(
            "SELECT * FROM analysis_results WHERE submission_id = ?",
            (submission_id,)
        )

        if result:
            # JSON 필드 파싱
            import json
            if result["issues_json"]:
                result["issues"] = json.loads(result["issues_json"])
            if result["suggestions_json"]:
                result["suggestions"] = json.loads(result["suggestions_json"])

        return result


class CurriculumProgressModel:
    """커리큘럼 진도 모델 헬퍼"""

    @staticmethod
    def get_or_create_progress(user_id: int, topic_id: str, level: str) -> Dict[str, Any]:
        """진도 조회 또는 생성"""
        db = get_db_manager()

        # 기존 진도 조회
        existing = db.fetch_one(
            "SELECT * FROM curriculum_progress WHERE user_id = ? AND topic_id = ? AND level = ?",
            (user_id, topic_id, level)
        )

        if existing:
            return existing

        # 새 진도 생성
        db.execute_query(
            "INSERT INTO curriculum_progress (user_id, topic_id, level) VALUES (?, ?, ?)",
            (user_id, topic_id, level)
        )

        return db.fetch_one("SELECT * FROM curriculum_progress WHERE id = last_insert_rowid()")

    @staticmethod
    def update_progress(progress_id: int, score: int, completed: bool = False):
        """진도 업데이트"""
        db = get_db_manager()
        db.execute_query(
            "UPDATE curriculum_progress SET score = ?, completed = ?, last_attempted = ? WHERE id = ?",
            (score, completed, datetime.utcnow(), progress_id)
        )

    @staticmethod
    def get_user_progress(user_id: int) -> List[Dict[str, Any]]:
        """사용자 진도 목록 조회"""
        db = get_db_manager()
        return db.fetch_all(
            "SELECT * FROM curriculum_progress WHERE user_id = ? ORDER BY last_attempted DESC",
            (user_id,)
        )


class AchievementModel:
    """성취 모델 헬퍼"""

    @staticmethod
    def create_achievement(user_id: int, achievement_type: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """성취 생성"""
        db = get_db_manager()
        import json

        query = """
            INSERT INTO achievements (user_id, achievement_type, achieved_at, metadata_json)
            VALUES (?, ?, ?, ?)
        """
        db.execute_query(query, (
            user_id,
            achievement_type,
            datetime.utcnow(),
            json.dumps(metadata) if metadata else None
        ))

        # 생성된 성취 조회
        return db.fetch_one("SELECT * FROM achievements WHERE id = last_insert_rowid()")

    @staticmethod
    def get_user_achievements(user_id: int) -> List[Dict[str, Any]]:
        """사용자 성취 목록 조회"""
        db = get_db_manager()
        return db.fetch_all(
            "SELECT * FROM achievements WHERE user_id = ? ORDER BY achieved_at DESC",
            (user_id,)
        )

    @staticmethod
    def has_achievement(user_id: int, achievement_type: str) -> bool:
        """특정 성취 보유 여부 확인"""
        db = get_db_manager()
        result = db.fetch_one(
            "SELECT COUNT(*) as count FROM achievements WHERE user_id = ? AND achievement_type = ?",
            (user_id, achievement_type)
        )
        return result["count"] > 0 if result else False