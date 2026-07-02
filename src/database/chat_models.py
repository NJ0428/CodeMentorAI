"""
채팅 시스템 데이터베이스 모델 헬퍼
대화, 메시지, 튜터링 세션 관리
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger
import json


class ConversationModel:
    """대화 모델 헬퍼"""

    @staticmethod
    def create_conversation(
        user_id: int,
        title: Optional[str] = None,
        conversation_type: str = "chat",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """새 대화 생성"""
        db = get_db_manager()
        query = """
            INSERT INTO conversations (user_id, title, conversation_type, created_at, updated_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        db.execute_query(query, (
            user_id,
            title,
            conversation_type,
            now,
            now,
            json.dumps(metadata) if metadata else None
        ))

        # 생성된 대화 조회
        return db.fetch_one("SELECT * FROM conversations WHERE id = last_insert_rowid()")

    @staticmethod
    def get_conversation_by_id(conversation_id: int) -> Optional[Dict[str, Any]]:
        """ID로 대화 조회"""
        db = get_db_manager()
        return db.fetch_one(
            "SELECT * FROM conversations WHERE id = ?",
            (conversation_id,)
        )

    @staticmethod
    def get_user_conversations(
        user_id: int,
        limit: int = 20,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """사용자 대화 목록 조회"""
        db = get_db_manager()

        if include_archived:
            return db.fetch_all(
                """SELECT * FROM conversations
                   WHERE user_id = ?
                   ORDER BY updated_at DESC
                   LIMIT ?""",
                (user_id, limit)
            )
        else:
            return db.fetch_all(
                """SELECT * FROM conversations
                   WHERE user_id = ? AND is_archived = 0
                   ORDER BY updated_at DESC
                   LIMIT ?""",
                (user_id, limit)
            )

    @staticmethod
    def update_conversation(
        conversation_id: int,
        title: Optional[str] = None,
        is_archived: Optional[bool] = None
    ):
        """대화 업데이트"""
        db = get_db_manager()
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if is_archived is not None:
            updates.append("is_archived = ?")
            params.append(is_archived)

        if not updates:
            return

        updates.append("updated_at = ?")
        params.append(datetime.utcnow())
        params.append(conversation_id)

        query = f"UPDATE conversations SET {', '.join(updates)} WHERE id = ?"
        db.execute_query(query, params)

    @staticmethod
    def touch_conversation(conversation_id: int):
        """대화 업데이트 시간 갱신"""
        db = get_db_manager()
        db.execute_query(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (datetime.utcnow(), conversation_id)
        )


class MessageModel:
    """메시지 모델 헬퍼"""

    @staticmethod
    def create_message(
        conversation_id: int,
        role: str,
        content: str,
        code_context: Optional[Dict] = None,
        tokens_used: int = 0,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """메시지 생성"""
        db = get_db_manager()
        query = """
            INSERT INTO messages (
                conversation_id, role, content, timestamp,
                code_context_json, tokens_used, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            conversation_id,
            role,
            content,
            datetime.utcnow(),
            json.dumps(code_context) if code_context else None,
            tokens_used,
            json.dumps(metadata) if metadata else None
        ))

        # 생성된 메시지 조회
        return db.fetch_one("SELECT * FROM messages WHERE id = last_insert_rowid()")

    @staticmethod
    def get_conversation_messages(
        conversation_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """대화 메시지 목록 조회"""
        db = get_db_manager()
        messages = db.fetch_all(
            """SELECT * FROM messages
               WHERE conversation_id = ?
               ORDER BY timestamp ASC
               LIMIT ?""",
            (conversation_id, limit)
        )

        # JSON 필드 파싱
        for msg in messages:
            if msg.get("code_context_json"):
                try:
                    msg["code_context"] = json.loads(msg["code_context_json"])
                except:
                    msg["code_context"] = None
            if msg.get("metadata_json"):
                try:
                    msg["metadata"] = json.loads(msg["metadata_json"])
                except:
                    msg["metadata"] = None

        return messages

    @staticmethod
    def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
        """ID로 메시지 조회"""
        db = get_db_manager()
        return db.fetch_one(
            "SELECT * FROM messages WHERE id = ?",
            (message_id,)
        )

    @staticmethod
    def delete_conversation_messages(conversation_id: int):
        """대화의 모든 메시지 삭제"""
        db = get_db_manager()
        db.execute_query(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,)
        )


class TutoringSessionModel:
    """튜터링 세션 모델 헬퍼"""

    @staticmethod
    def create_tutoring_session(
        user_id: int,
        conversation_id: Optional[int] = None,
        topic: Optional[str] = None,
        student_level: str = "beginner",
        learning_objectives: Optional[str] = None
    ) -> Dict[str, Any]:
        """튜터링 세션 생성"""
        db = get_db_manager()
        query = """
            INSERT INTO tutoring_sessions (
                conversation_id, user_id, topic, student_level,
                start_time, learning_objectives
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            conversation_id,
            user_id,
            topic,
            student_level,
            datetime.utcnow(),
            learning_objectives
        ))

        # 생성된 세션 조회
        return db.fetch_one("SELECT * FROM tutoring_sessions WHERE id = last_insert_rowid()")

    @staticmethod
    def get_active_tutoring_session(user_id: int) -> Optional[Dict[str, Any]]:
        """활성 튜터링 세션 조회"""
        db = get_db_manager()
        return db.fetch_one(
            """SELECT * FROM tutoring_sessions
               WHERE user_id = ? AND end_time IS NULL
               ORDER BY id DESC LIMIT 1""",
            (user_id,)
        )

    @staticmethod
    def end_tutoring_session(
        session_id: int,
        rating: Optional[int] = None,
        feedback: Optional[str] = None
    ):
        """튜터링 세션 종료"""
        db = get_db_manager()
        db.execute_query(
            """UPDATE tutoring_sessions
               SET end_time = ?, session_rating = ?, feedback_text = ?
               WHERE id = ?""",
            (datetime.utcnow(), rating, feedback, session_id)
        )

    @staticmethod
    def increment_message_count(session_id: int):
        """메시지 교환 수 증가"""
        db = get_db_manager()
        db.execute_query(
            "UPDATE tutoring_sessions SET messages_exchanged = messages_exchanged + 1 WHERE id = ?",
            (session_id,)
        )

    @staticmethod
    def increment_code_share_count(session_id: int):
        """코드 공유 수 증가"""
        db = get_db_manager()
        db.execute_query(
            "UPDATE tutoring_sessions SET code_snippets_shared = code_snippets_shared + 1 WHERE id = ?",
            (session_id,)
        )

    @staticmethod
    def get_user_tutoring_sessions(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """사용자 튜터링 세션 목록 조회"""
        db = get_db_manager()
        return db.fetch_all(
            """SELECT * FROM tutoring_sessions
               WHERE user_id = ?
               ORDER BY start_time DESC
               LIMIT ?""",
            (user_id, limit)
        )


class CodeContextShareModel:
    """코드 컨텍스트 공유 모델 헬퍼"""

    @staticmethod
    def create_code_share(
        message_id: int,
        conversation_id: int,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None
    ) -> Dict[str, Any]:
        """코드 공유 생성"""
        db = get_db_manager()
        query = """
            INSERT INTO code_context_shares (
                message_id, conversation_id, code, language,
                file_path, line_start, line_end, shared_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (
            message_id,
            conversation_id,
            code,
            language,
            file_path,
            line_start,
            line_end,
            datetime.utcnow()
        ))

        # 생성된 코드 공유 조회
        return db.fetch_one("SELECT * FROM code_context_shares WHERE id = last_insert_rowid()")

    @staticmethod
    def get_conversation_code_shares(conversation_id: int) -> List[Dict[str, Any]]:
        """대화의 코드 공유 목록 조회"""
        db = get_db_manager()
        return db.fetch_all(
            """SELECT * FROM code_context_shares
               WHERE conversation_id = ?
               ORDER BY shared_at DESC""",
            (conversation_id,)
        )

    @staticmethod
    def get_message_code_share(message_id: int) -> Optional[Dict[str, Any]]:
        """메시지의 코드 공유 조회"""
        db = get_db_manager()
        return db.fetch_one(
            "SELECT * FROM code_context_shares WHERE message_id = ?",
            (message_id,)
        )


# 순환 방지를 위해 import를 나중에 실행
from src.database.db_manager import get_db_manager


if __name__ == "__main__":
    # 모델 테스트
    from src.database.db_manager import get_db_manager

    print("🧪 채팅 시스템 모델 테스트")

    # 테스트용 사용자 생성
    from src.database.models import UserModel
    user = UserModel.create_user("test_user", "test@example.com")
    print(f"✅ 테스트 사용자 생성: {user['id']}")

    # 대화 생성 테스트
    conversation = ConversationModel.create_conversation(
        user_id=user['id'],
        title="Python 기초 질문",
        conversation_type="tutoring"
    )
    print(f"✅ 대화 생성: {conversation['id']}")

    # 메시지 생성 테스트
    message = MessageModel.create_message(
        conversation_id=conversation['id'],
        role="user",
        content="Python에서 리스트를 어떻게 사용하나요?"
    )
    print(f"✅ 메시지 생성: {message['id']}")

    # 튜터링 세션 생성 테스트
    session = TutoringSessionModel.create_tutoring_session(
        user_id=user['id'],
        conversation_id=conversation['id'],
        topic="Python 리스트",
        student_level="beginner"
    )
    print(f"✅ 튜터링 세션 생성: {session['id']}")

    # 코드 공유 테스트
    code_share = CodeContextShareModel.create_code_share(
        message_id=message['id'],
        conversation_id=conversation['id'],
        code="my_list = [1, 2, 3]\nprint(my_list[0])",
        language="python"
    )
    print(f"✅ 코드 공유 생성: {code_share['id']}")

    # 조회 테스트
    conversations = ConversationModel.get_user_conversations(user['id'])
    print(f"✅ 사용자 대화 목록: {len(conversations)}개")

    messages = MessageModel.get_conversation_messages(conversation['id'])
    print(f"✅ 대화 메시지: {len(messages)}개")

    print("\n🎉 모든 모델 테스트 통과!")
