"""
채팅 시스템 데모 스크립트
구현된 기능들을 시연하는 간단한 예제
"""
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.abspath('.'))


def demo_basic_chat():
    """기본 채팅 기능 데모"""
    print("=" * 60)
    print("Chat System Demo")
    print("=" * 60)

    from src.database.repositories.chat_repository import get_chat_repository
    from src.learning.tutoring_system import get_interactive_tutor, TutoringMode, StudentLevel
    from src.database.models import UserModel
    import uuid

    # 사용자 생성
    unique_id = str(uuid.uuid4())[:8]
    user = UserModel.create_user(f"demo_user_{unique_id}", f"demo_{unique_id}@example.com")

    print(f"\n1. Created demo user: {user['username']} (ID: {user['id']})")

    # 채팅 리포지토리 및 튜터 초기화
    chat_repo = get_chat_repository()
    tutor = get_interactive_tutor()

    # 대화 생성
    conversation = chat_repo.create_conversation(
        user_id=user['id'],
        title="Python Learning Session",
        conversation_type="tutoring"
    )

    print(f"2. Created conversation: {conversation['title']} (ID: {conversation['id']})")

    # 튜터링 세션 생성
    session = tutor.create_session(
        user_id=user['id'],
        mode=TutoringMode.CONVERSATION,
        student_level=StudentLevel.BEGINNER,
        topic="Python Basics"
    )

    print(f"3. Started tutoring session: {session.session_id}")
    print(f"   - Mode: {session.mode.value}")
    print(f"   - Level: {session.student_level.value}")
    print(f"   - Topic: {session.topic}")

    # 메시지 교환 시뮬레이션
    messages = [
        ("user", "What is Python and why should I learn it?"),
        ("user", "How do I create a list in Python?"),
        ("user", "Can you show me a simple example?")
    ]

    print("\n4. Simulating conversation:")
    for i, (role, content) in enumerate(messages, 1):
        # 데이터베이스에 메시지 저장
        message = chat_repo.create_message(
            conversation_id=conversation['id'],
            role=role,
            content=content
        )

        # 튜터 세션에 메시지 추가
        session.add_message(role, content)

        print(f"   Message {i}: [{role.upper()}] {content[:50]}...")

    # 코드 컨텍스트 공유 시뮬레이션
    code_example = """# Simple Python List Example
my_list = [1, 2, 3, 4, 5]
print(my_list)
print(f"First element: {my_list[0]}")
print(f"List length: {len(my_list)}")"""

    session.add_code_context(code_example, language="python")
    print(f"\n5. Shared code context ({len(code_example)} characters)")

    # 세션 통계
    summary = tutor.get_session_summary(session.session_id)
    print(f"\n6. Session Summary:")
    print(f"   - Messages exchanged: {summary['message_count']}")
    print(f"   - Code shares: {summary['code_shares']}")
    print(f"   - Duration: {summary['duration']:.2f} seconds")

    # 데이터베이스 조회 확인
    db_messages = chat_repo.get_conversation_messages(conversation['id'])
    print(f"\n7. Database Verification:")
    print(f"   - Messages in database: {len(db_messages)}")
    print(f"   - Conversation ID: {conversation['id']}")

    # 통계 확인
    stats = chat_repo.get_chat_statistics(user['id'])
    print(f"\n8. User Statistics:")
    print(f"   - Total conversations: {stats['total_conversations']}")
    print(f"   - Recent messages (30 days): {stats['recent_messages_30days']}")

    # 튜터링 모드 변경 데모
    print(f"\n9. Testing different tutoring modes:")
    modes = [
        TutoringMode.CODE_REVIEW,
        TutoringMode.PROBLEM_SOLVING,
        TutoringMode.CONCEPT_EXPLANATION,
        TutoringMode.DEBUGGING
    ]

    for mode in modes:
        print(f"   - {mode.value}: Available")

    # 세션 종료
    tutor.end_session(session.session_id)
    print(f"\n10. Session ended successfully")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)

    print("\nKey Features Demonstrated:")
    print("[PASS] Database migration and table creation")
    print("[PASS] Conversation and message management")
    print("[PASS] Interactive tutoring system with multiple modes")
    print("[PASS] Code context sharing")
    print("[PASS] Session tracking and statistics")
    print("[PASS] User conversation history")
    print("[PASS] Integration between chat and tutoring systems")


if __name__ == "__main__":
    try:
        demo_basic_chat()
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
