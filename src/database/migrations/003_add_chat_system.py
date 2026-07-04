"""
채팅 시스템 데이터베이스 마이그레이션
대화 기록, 메시지, 튜터링 세션을 위한 테이블 생성
"""
from datetime import datetime
from typing import Dict, Any
from loguru import logger


def upgrade(db):
    """채팅 시스템 테이블 생성"""

    # 대화 테이블
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            conversation_type TEXT DEFAULT 'chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_archived BOOLEAN DEFAULT 0,
            metadata_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 메시지 테이블
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            code_context_json TEXT,
            tokens_used INTEGER DEFAULT 0,
            metadata_json TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """)

    # 튜터링 세션 테이블
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS tutoring_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            user_id INTEGER NOT NULL,
            topic TEXT,
            student_level TEXT DEFAULT 'beginner',
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            messages_exchanged INTEGER DEFAULT 0,
            code_snippets_shared INTEGER DEFAULT 0,
            learning_objectives TEXT,
            session_rating INTEGER,
            feedback_text TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 코드 컨텍스트 공유 테이블
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS code_context_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            conversation_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            language TEXT DEFAULT 'python',
            file_path TEXT,
            line_start INTEGER,
            line_end INTEGER,
            shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages(id),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    # 인덱스 생성
    db.execute_query("""
        CREATE INDEX IF NOT EXISTS idx_conversations_user_id
        ON conversations(user_id)
    """)

    db.execute_query("""
        CREATE INDEX IF NOT EXISTS idx_conversations_created_at
        ON conversations(created_at DESC)
    """)

    db.execute_query("""
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
        ON messages(conversation_id, timestamp)
    """)

    db.execute_query("""
        CREATE INDEX IF NOT EXISTS idx_tutoring_sessions_user_id
        ON tutoring_sessions(user_id)
    """)

    db.execute_query("""
        CREATE INDEX IF NOT EXISTS idx_code_context_shares_conversation_id
        ON code_context_shares(conversation_id)
    """)

    logger.info("✅ 채팅 시스템 테이블 생성 완료")


def downgrade(db):
    """채팅 시스템 테이블 삭제"""

    db.execute_query("DROP INDEX IF EXISTS idx_code_context_shares_conversation_id")
    db.execute_query("DROP INDEX IF EXISTS idx_tutoring_sessions_user_id")
    db.execute_query("DROP INDEX IF EXISTS idx_messages_conversation_id")
    db.execute_query("DROP INDEX IF EXISTS idx_conversations_created_at")
    db.execute_query("DROP INDEX IF EXISTS idx_conversations_user_id")

    db.execute_query("DROP TABLE IF EXISTS code_context_shares")
    db.execute_query("DROP TABLE IF EXISTS tutoring_sessions")
    db.execute_query("DROP TABLE IF EXISTS messages")
    db.execute_query("DROP TABLE IF EXISTS conversations")

    logger.info("✅ 채팅 시스템 테이블 삭제 완료")


if __name__ == "__main__":
    # 마이그레이션 테스트
    from src.database.db_manager import get_db_manager

    db = get_db_manager()
    upgrade(db)

    print("🎉 채팅 시스템 마이그레이션 완료!")
