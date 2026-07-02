"""
채팅 시스템 리포지토리
대화 기록 관리 및 검색 기능
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from src.database.db_manager import get_db_manager
from src.database.chat_models import (
    ConversationModel,
    MessageModel,
    TutoringSessionModel,
    CodeContextShareModel
)


class ChatRepository:
    """채팅 데이터 리포지토리"""

    def __init__(self):
        self.db = get_db_manager()

    def create_conversation(
        self,
        user_id: int,
        title: Optional[str] = None,
        conversation_type: str = "chat",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """새 대화 생성"""
        try:
            conversation = ConversationModel.create_conversation(
                user_id=user_id,
                title=title,
                conversation_type=conversation_type,
                metadata=metadata
            )
            logger.info(f"대화 생성: {conversation['id']}")
            return conversation
        except Exception as e:
            logger.error(f"대화 생성 실패: {e}")
            raise

    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """대화 조회"""
        try:
            return ConversationModel.get_conversation_by_id(conversation_id)
        except Exception as e:
            logger.error(f"대화 조회 실패: {e}")
            return None

    def get_user_conversations(
        self,
        user_id: int,
        limit: int = 20,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """사용자 대화 목록 조회"""
        try:
            return ConversationModel.get_user_conversations(
                user_id=user_id,
                limit=limit,
                include_archived=include_archived
            )
        except Exception as e:
            logger.error(f"사용자 대화 목록 조회 실패: {e}")
            return []

    def update_conversation(
        self,
        conversation_id: int,
        title: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> bool:
        """대화 업데이트"""
        try:
            ConversationModel.update_conversation(
                conversation_id=conversation_id,
                title=title,
                is_archived=is_archived
            )
            logger.info(f"대화 업데이트: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"대화 업데이트 실패: {e}")
            return False

    def touch_conversation(self, conversation_id: int) -> bool:
        """대화 업데이트 시간 갱신"""
        try:
            ConversationModel.touch_conversation(conversation_id)
            return True
        except Exception as e:
            logger.error(f"대화 시간 갱신 실패: {e}")
            return False

    def archive_conversation(self, conversation_id: int) -> bool:
        """대화 아카이브"""
        try:
            return self.update_conversation(conversation_id, is_archived=True)
        except Exception as e:
            logger.error(f"대화 아카이브 실패: {e}")
            return False

    def delete_conversation(self, conversation_id: int) -> bool:
        """대화 삭제"""
        try:
            # 메시지 삭제
            MessageModel.delete_conversation_messages(conversation_id)

            # 대화 삭제 (CASCADE로 인해 관련 데이터도 삭제됨)
            self.db.execute_query(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,)
            )

            logger.info(f"대화 삭제: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"대화 삭제 실패: {e}")
            return False

    def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        code_context: Optional[Dict] = None,
        tokens_used: int = 0,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """메시지 생성"""
        try:
            message = MessageModel.create_message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                code_context=code_context,
                tokens_used=tokens_used,
                metadata=metadata
            )

            # 대화 업데이트 시간 갱신
            self.touch_conversation(conversation_id)

            logger.info(f"메시지 생성: {message['id']}")
            return message
        except Exception as e:
            logger.error(f"메시지 생성 실패: {e}")
            raise

    def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """대화 메시지 목록 조회"""
        try:
            return MessageModel.get_conversation_messages(
                conversation_id=conversation_id,
                limit=limit
            )
        except Exception as e:
            logger.error(f"대화 메시지 목록 조회 실패: {e}")
            return []

    def get_message(self, message_id: int) -> Optional[Dict[str, Any]]:
        """메시지 조회"""
        try:
            return MessageModel.get_message_by_id(message_id)
        except Exception as e:
            logger.error(f"메시지 조회 실패: {e}")
            return None

    def search_messages(
        self,
        user_id: int,
        keyword: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """메시지 검색"""
        try:
            query = """
                SELECT DISTINCT m.*
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.user_id = ? AND m.content LIKE ?
                ORDER BY m.timestamp DESC
                LIMIT ?
            """
            results = self.db.fetch_all(
                query,
                (user_id, f"%{keyword}%", limit)
            )

            logger.info(f"메시지 검색: {keyword} ({len(results)}개 결과)")
            return results
        except Exception as e:
            logger.error(f"메시지 검색 실패: {e}")
            return []

    def create_tutoring_session(
        self,
        user_id: int,
        conversation_id: Optional[int] = None,
        topic: Optional[str] = None,
        student_level: str = "beginner",
        learning_objectives: Optional[str] = None
    ) -> Dict[str, Any]:
        """튜터링 세션 생성"""
        try:
            session = TutoringSessionModel.create_tutoring_session(
                user_id=user_id,
                conversation_id=conversation_id,
                topic=topic,
                student_level=student_level,
                learning_objectives=learning_objectives
            )
            logger.info(f"튜터링 세션 생성: {session['id']}")
            return session
        except Exception as e:
            logger.error(f"튜터링 세션 생성 실패: {e}")
            raise

    def get_active_tutoring_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """활성 튜터링 세션 조회"""
        try:
            return TutoringSessionModel.get_active_tutoring_session(user_id)
        except Exception as e:
            logger.error(f"활성 튜터링 세션 조회 실패: {e}")
            return None

    def end_tutoring_session(
        self,
        session_id: int,
        rating: Optional[int] = None,
        feedback: Optional[str] = None
    ) -> bool:
        """튜터링 세션 종료"""
        try:
            TutoringSessionModel.end_tutoring_session(
                session_id=session_id,
                rating=rating,
                feedback=feedback
            )
            logger.info(f"튜터링 세션 종료: {session_id}")
            return True
        except Exception as e:
            logger.error(f"튜터링 세션 종료 실패: {e}")
            return False

    def increment_tutoring_metrics(self, session_id: int, metric: str = "messages") -> bool:
        """튜터링 지표 증가"""
        try:
            if metric == "messages":
                TutoringSessionModel.increment_message_count(session_id)
            elif metric == "code_shares":
                TutoringSessionModel.increment_code_share_count(session_id)
            return True
        except Exception as e:
            logger.error(f"튜터링 지표 증가 실패: {e}")
            return False

    def create_code_share(
        self,
        message_id: int,
        conversation_id: int,
        code: str,
        language: str = "python",
        file_path: Optional[str] = None,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None
    ) -> Dict[str, Any]:
        """코드 공유 생성"""
        try:
            code_share = CodeContextShareModel.create_code_share(
                message_id=message_id,
                conversation_id=conversation_id,
                code=code,
                language=language,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end
            )
            logger.info(f"코드 공유 생성: {code_share['id']}")
            return code_share
        except Exception as e:
            logger.error(f"코드 공유 생성 실패: {e}")
            raise

    def get_conversation_code_shares(self, conversation_id: int) -> List[Dict[str, Any]]:
        """대화의 코드 공유 목록 조회"""
        try:
            return CodeContextShareModel.get_conversation_code_shares(conversation_id)
        except Exception as e:
            logger.error(f"대화 코드 공유 목록 조회 실패: {e}")
            return []

    def get_chat_statistics(self, user_id: int) -> Dict[str, Any]:
        """채팅 통계 조회"""
        try:
            # 총 대화 수
            total_conversations = len(self.get_user_conversations(user_id, limit=1000))

            # 총 메시지 수 (최근 30일)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_messages = self.db.fetch_all(
                """
                SELECT COUNT(*) as count
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.user_id = ? AND m.timestamp >= ?
                """,
                (user_id, thirty_days_ago.isoformat())
            )
            total_recent_messages = recent_messages[0]['count'] if recent_messages else 0

            # 활성 튜터링 세션
            active_session = self.get_active_tutoring_session(user_id)

            # 튜터링 통계
            tutoring_stats = self.db.fetch_one(
                """
                SELECT
                    COUNT(*) as total_sessions,
                    SUM(messages_exchanged) as total_messages,
                    SUM(code_snippets_shared) as total_code_shares,
                    AVG(session_rating) as avg_rating
                FROM tutoring_sessions
                WHERE user_id = ? AND end_time IS NOT NULL
                """,
                (user_id,)
            )

            return {
                "total_conversations": total_conversations,
                "recent_messages_30days": total_recent_messages,
                "has_active_session": active_session is not None,
                "tutoring": {
                    "total_sessions": tutoring_stats['total_sessions'] if tutoring_stats else 0,
                    "total_messages": tutoring_stats['total_messages'] if tutoring_stats else 0,
                    "total_code_shares": tutoring_stats['total_code_shares'] if tutoring_stats else 0,
                    "average_rating": round(tutoring_stats['avg_rating'], 1) if tutoring_stats and tutoring_stats['avg_rating'] else None
                }
            }
        except Exception as e:
            logger.error(f"채팅 통계 조회 실패: {e}")
            return {}


# 전역 리포지토리 인스턴스
chat_repository = None


def get_chat_repository() -> ChatRepository:
    """채팅 리포지토리 인스턴스 반환"""
    global chat_repository
    if chat_repository is None:
        chat_repository = ChatRepository()
    return chat_repository


if __name__ == "__main__":
    # 리포지토리 테스트
    print("🧪 채팅 리포지토리 테스트")

    repo = ChatRepository()

    # 테스트용 사용자 생성
    from src.database.models import UserModel
    user = UserModel.create_user("test_user_chat", "test_chat@example.com")

    # 대화 생성
    conversation = repo.create_conversation(
        user_id=user['id'],
        title="테스트 대화",
        conversation_type="chat"
    )
    print(f"✅ 대화 생성: {conversation['id']}")

    # 메시지 생성
    message = repo.create_message(
        conversation_id=conversation['id'],
        role="user",
        content="안녕하세요!"
    )
    print(f"✅ 메시지 생성: {message['id']}")

    # 대화 목록 조회
    conversations = repo.get_user_conversations(user['id'])
    print(f"✅ 사용자 대화 목록: {len(conversations)}개")

    # 메시지 목록 조회
    messages = repo.get_conversation_messages(conversation['id'])
    print(f"✅ 대화 메시지: {len(messages)}개")

    # 튜터링 세션 생성
    tutoring_session = repo.create_tutoring_session(
        user_id=user['id'],
        conversation_id=conversation['id'],
        topic="Python 기초",
        student_level="beginner"
    )
    print(f"✅ 튜터링 세션 생성: {tutoring_session['id']}")

    # 통계 조회
    stats = repo.get_chat_statistics(user['id'])
    print(f"✅ 채팅 통계: {stats}")

    print("\n🎉 리포지토리 테스트 완료!")
