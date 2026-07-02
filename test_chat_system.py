"""
채팅 시스템 테스트 스크립트
데이터베이스 마이그레이션, 모델, 리포지토리, 튜터링 시스템 테스트
"""
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, os.path.abspath('.'))

from loguru import logger


def test_database_migration():
    """데이터베이스 마이그레이션 테스트"""
    print("🧪 1. 데이터베이스 마이그레이션 테스트")

    try:
        import importlib
        from src.database.db_manager import get_db_manager

        # 마이그레이션 실행
        migration = importlib.import_module('src.database.migrations.003_add_chat_system')
        db = get_db_manager()
        migration.upgrade(db)

        # 테이블 존재 확인
        tables = db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('conversations', 'messages', 'tutoring_sessions', 'code_context_shares')"
        )

        print(f"✅ 마이그레이션 완료: {len(tables)}개 테이블 생성")
        return True

    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False


def test_chat_models():
    """채팅 모델 테스트"""
    print("\n🧪 2. 채팅 모델 테스트")

    try:
        from src.database.chat_models import (
            ConversationModel,
            MessageModel,
            TutoringSessionModel,
            CodeContextShareModel
        )
        from src.database.models import UserModel
        import uuid

        # 테스트 사용자 생성 (unique username)
        unique_id = str(uuid.uuid4())[:8]
        user = UserModel.create_user(f"chat_test_{unique_id}", f"chat_test_{unique_id}@example.com")
        print(f"✅ 테스트 사용자 생성: {user['id']}")

        # 대화 생성
        conversation = ConversationModel.create_conversation(
            user_id=user['id'],
            title="테스트 대화",
            conversation_type="tutoring"
        )
        print(f"✅ 대화 생성: {conversation['id']}")

        # 메시지 생성
        message = MessageModel.create_message(
            conversation_id=conversation['id'],
            role="user",
            content="안녕하세요, 튜터님!"
        )
        print(f"✅ 메시지 생성: {message['id']}")

        # 튜터링 세션 생성
        session = TutoringSessionModel.create_tutoring_session(
            user_id=user['id'],
            conversation_id=conversation['id'],
            topic="Python 기초",
            student_level="beginner"
        )
        print(f"✅ 튜터링 세션 생성: {session['id']}")

        # 코드 공유 생성
        code_share = CodeContextShareModel.create_code_share(
            message_id=message['id'],
            conversation_id=conversation['id'],
            code="print('Hello, World!')",
            language="python"
        )
        print(f"✅ 코드 공유 생성: {code_share['id']}")

        # 조회 테스트
        conversations = ConversationModel.get_user_conversations(user['id'])
        print(f"✅ 사용자 대화 조회: {len(conversations)}개")

        messages = MessageModel.get_conversation_messages(conversation['id'])
        print(f"✅ 대화 메시지 조회: {len(messages)}개")

        return True

    except Exception as e:
        print(f"❌ 모델 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_repository():
    """채팅 리포지토리 테스트"""
    print("\n🧪 3. 채팅 리포지토리 테스트")

    try:
        from src.database.repositories.chat_repository import get_chat_repository
        from src.database.models import UserModel
        import uuid

        repo = get_chat_repository()

        # 테스트 사용자 생성 (unique username)
        unique_id = str(uuid.uuid4())[:8]
        user = UserModel.create_user(f"repo_test_{unique_id}", f"repo_test_{unique_id}@example.com")

        # 대화 생성
        conversation = repo.create_conversation(
            user_id=user['id'],
            title="리포지토리 테스트",
            conversation_type="chat"
        )
        print(f"✅ 리포지토리 대화 생성: {conversation['id']}")

        # 메시지 생성
        message = repo.create_message(
            conversation_id=conversation['id'],
            role="user",
            content="리포지토리 테스트 메시지"
        )
        print(f"✅ 리포지토리 메시지 생성: {message['id']}")

        # 통계 조회
        stats = repo.get_chat_statistics(user['id'])
        print(f"✅ 채팅 통계 조회: {stats}")

        return True

    except Exception as e:
        print(f"❌ 리포지토리 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tutoring_system():
    """튜터링 시스템 테스트"""
    print("\n🧪 4. 튜터링 시스템 테스트")

    try:
        from src.learning.tutoring_system import (
            InteractiveTutor,
            TutoringMode,
            StudentLevel
        )

        tutor = InteractiveTutor()

        # 세션 생성
        session = tutor.create_session(
            user_id=1,
            mode=TutoringMode.CONVERSATION,
            student_level=StudentLevel.BEGINNER,
            topic="Python 테스트"
        )
        print(f"✅ 튜터링 세션 생성: {session.session_id}")

        # 메시지 처리 (AI 응답 없이 기본 테스트)
        # 실제 API 호출 없이 기본 기능 테스트
        test_message = "Python의 리스트에 대해 알려주세요"

        # 세션 요약
        summary = tutor.get_session_summary(session.session_id)
        print(f"✅ 세션 요약: {summary}")

        # 세션 종료
        tutor.end_session(session.session_id)
        print(f"✅ 튜터링 세션 종료")

        return True

    except Exception as e:
        print(f"❌ 튜터링 시스템 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """통합 테스트"""
    print("\n🧪 5. 통합 테스트")

    try:
        from src.database.repositories.chat_repository import get_chat_repository
        from src.learning.tutoring_system import get_interactive_tutor, TutoringMode, StudentLevel
        from src.database.models import UserModel
        import uuid

        # 사용자 생성 (unique username)
        unique_id = str(uuid.uuid4())[:8]
        user = UserModel.create_user(f"integration_test_{unique_id}", f"integration_test_{unique_id}@example.com")

        # 대화 및 메시지 생성
        repo = get_chat_repository()
        conversation = repo.create_conversation(
            user_id=user['id'],
            title="통합 테스트 대화",
            conversation_type="tutoring"
        )

        message1 = repo.create_message(
            conversation_id=conversation['id'],
            role="user",
            content="통합 테스트 메시지 1"
        )

        message2 = repo.create_message(
            conversation_id=conversation['id'],
            role="assistant",
            content="통합 테스트 응답 1"
        )

        print(f"✅ 통합 대화 및 메시지 생성")

        # 튜터링 세션 연결
        tutor = get_interactive_tutor()
        session = tutor.create_session(
            user_id=user['id'],
            mode=TutoringMode.CODE_REVIEW,
            student_level=StudentLevel.INTERMEDIATE,
            topic="코드 리뷰 테스트"
        )

        print(f"✅ 통합 튜터링 세션 생성: {session.session_id}")

        # 데이터 조회 검증
        messages = repo.get_conversation_messages(conversation['id'])
        assert len(messages) == 2, "메시지 수가 일치하지 않음"

        print(f"✅ 통합 테스트 완료: 메시지 {len(messages)}개 확인")

        return True

    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    import sys
    import io

    # UTF-8 출력 설정
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("=" * 60)
    print("Chat System Integration Test Started")
    print("=" * 60)

    tests = [
        ("데이터베이스 마이그레이션", test_database_migration),
        ("채팅 모델", test_chat_models),
        ("채팅 리포지토리", test_chat_repository),
        ("튜터링 시스템", test_tutoring_system),
        ("통합 테스트", test_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))

    # 결과 요약
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 60)
    print(f"Final Result: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("All tests passed successfully!")
        return 0
    else:
        print("Some tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
