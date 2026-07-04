"""
대화형 튜터링 시스템
AI 기반 Python 튜터링 시스템
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger
import json


class TutoringMode(str, Enum):
    """튜터링 모드"""
    CONVERSATION = "conversation"  # 자유 대화
    CODE_REVIEW = "code_review"    # 코드 리뷰
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결
    CONCEPT_EXPLANATION = "concept_explanation"  # 개념 설명
    DEBUGGING = "debugging"        # 디버깅 도움


class StudentLevel(str, Enum):
    """학생 수준"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class TutoringSession:
    """튜터링 세션"""
    session_id: str
    user_id: int
    mode: TutoringMode
    student_level: StudentLevel
    topic: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    message_count: int = 0
    code_shares: int = 0
    learning_objectives: List[str] = field(default_factory=list)
    conversation_history: List[Dict] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """메시지 추가"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.message_count += 1

    def add_code_context(self, code: str, language: str = "python", file_path: Optional[str] = None):
        """코드 컨텍스트 추가"""
        self.context["code"] = code
        self.context["language"] = language
        self.context["file_path"] = file_path
        self.context["last_updated"] = datetime.utcnow().isoformat()
        self.code_shares += 1

    def get_recent_context(self, limit: int = 5) -> str:
        """최근 대화 컨텍스트 반환"""
        recent_messages = self.conversation_history[-limit:] if self.conversation_history else []
        context_parts = []

        for msg in recent_messages:
            role_name = "사용자" if msg["role"] == "user" else "튜터"
            context_parts.append(f"{role_name}: {msg['content']}")

        return "\n".join(context_parts)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "mode": self.mode.value,
            "student_level": self.student_level.value,
            "topic": self.topic,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "message_count": self.message_count,
            "code_shares": self.code_shares,
            "learning_objectives": self.learning_objectives,
            "conversation_history": self.conversation_history,
            "context": self.context
        }


class InteractiveTutor:
    """대화형 튜터"""

    def __init__(self):
        self.sessions: Dict[str, TutoringSession] = {}
        self.current_session_id: Optional[str] = None

        # 튜터링 전략
        self.tutoring_strategies = {
            TutoringMode.CONVERSATION: self._conversation_strategy,
            TutoringMode.CODE_REVIEW: self._code_review_strategy,
            TutoringMode.PROBLEM_SOLVING: self._problem_solving_strategy,
            TutoringMode.CONCEPT_EXPLANATION: self._concept_explanation_strategy,
            TutoringMode.DEBUGGING: self._debugging_strategy
        }

        logger.info("대화형 튜터 초기화 완료")

    def create_session(
        self,
        user_id: int,
        mode: TutoringMode = TutoringMode.CONVERSATION,
        student_level: StudentLevel = StudentLevel.BEGINNER,
        topic: Optional[str] = None,
        learning_objectives: Optional[List[str]] = None
    ) -> TutoringSession:
        """새 튜터링 세션 생성"""
        import uuid

        session_id = str(uuid.uuid4())
        session = TutoringSession(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            student_level=student_level,
            topic=topic,
            learning_objectives=learning_objectives or []
        )

        self.sessions[session_id] = session
        self.current_session_id = session_id

        logger.info(f"튜터링 세션 생성: {session_id} (모드: {mode.value})")
        return session

    def get_current_session(self) -> Optional[TutoringSession]:
        """현재 세션 반환"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None

    def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        code_context: Optional[str] = None
    ) -> str:
        """사용자 메시지 처리 및 응답 생성"""
        session = self._get_session(session_id)

        if not session:
            return "죄송합니다. 활성화된 튜터링 세션을 찾을 수 없습니다."

        try:
            # 사용자 메시지 추가
            session.add_message("user", message)

            # 코드 컨텍스트 업데이트
            if code_context:
                session.add_code_context(code_context)

            # 적절한 튜터링 전략 선택
            strategy = self.tutoring_strategies.get(session.mode, self._conversation_strategy)

            # AI 응답 생성
            response = strategy(message, session)

            # 튜터 응답 추가
            session.add_message("assistant", response)

            return response

        except Exception as e:
            logger.error(f"메시지 처리 실패: {e}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"

    def _get_session(self, session_id: Optional[str]) -> Optional[TutoringSession]:
        """세션 가져오기"""
        if session_id:
            return self.sessions.get(session_id)
        return self.get_current_session()

    def _conversation_strategy(self, message: str, session: TutoringSession) -> str:
        """대화 모드 튜터링 전략"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            # 컨텍스트 구성
            context = f"""
학생 질문: {message}
학생 수준: {session.student_level.value}
최근 대화 맥락:
{session.get_recent_context()}
"""

            # 코드 컨텍스트가 있으면 추가
            if session.context.get("code"):
                context += f"\n관련 코드:\n```python\n{session.context['code']}\n```"

            # AI 응답 생성
            response = client.get_tutoring_response(
                question=message,
                code_context=session.context.get("code"),
                student_level=session.student_level.value
            )

            return response

        except Exception as e:
            logger.error(f"대화 전략 실행 실패: {e}")
            return self._fallback_response(message, session.student_level)

    def _code_review_strategy(self, message: str, session: TutoringSession) -> str:
        """코드 리뷰 전략"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            if not session.context.get("code"):
                return "코드 리뷰를 위해 코드를 공유해주세요."

            # 코드 분석
            analysis = client.analyze_code(
                code=session.context["code"],
                user_level=session.student_level.value,
                analysis_type="educational"
            )

            # 분석 결과를 친절한 피드백으로 변환
            response = f"""📊 **코드 리뷰 결과**

**점수**: {analysis.get('score', 'N/A')}/10점

"""

            # 문제점
            if analysis.get('issues'):
                response += "**개선이 필요한 부분:**\n"
                for issue in analysis['issues']:
                    response += f"• [{issue.get('severity', 'medium')}] {issue.get('description', '')}\n"
                    if issue.get('solution'):
                        response += f"  해결책: {issue.get('solution', '')}\n"
                response += "\n"

            # 제안
            if analysis.get('suggestions'):
                response += "**개선 제안:**\n"
                for suggestion in analysis['suggestions']:
                    response += f"• {suggestion.get('description', '')}\n"
                    if suggestion.get('example'):
                        response += f"  예시:\n  ```python\n{suggestion.get('example', '')}\n```\n"
                response += "\n"

            # 좋은 점
            if analysis.get('strengths'):
                response += "**잘한 점:** 🎉\n"
                for strength in analysis['strengths']:
                    response += f"✓ {strength}\n"

            return response

        except Exception as e:
            logger.error(f"코드 리뷰 전략 실행 실패: {e}")
            return "코드 리뷰 중 오류가 발생했습니다. 다시 시도해주세요."

    def _problem_solving_strategy(self, message: str, session: TutoringSession) -> str:
        """문제 해결 전략"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            # 문제 해결 프롬프트
            prompt = f"""
학생이 다음 문제에 대해 도움을 요청하고 있습니다:

{message}

학생 수준: {session.student_level.value}
"""

            if session.context.get("code"):
                prompt += f"\n학생의 현재 코드:\n```python\n{session.context['code']}\n```\n"

            prompt += """
단계별 가이드를 제공해주세요:
1. 문제를 명확히 이해하는 데 도움
2. 해결 방향 제시
3. 힌트 제공 (즉시 정답을 말하지 않고)
4. 학생이 직접 해결할 수 있도록 격려
"""

            response = client.send_message(
                message=prompt,
                system_prompt="당신은 Python 문제 해결 튜터입니다. 학생들이 스스로 문제를 해결할 수 있도록 단계별로 안내해주세요.",
                max_tokens=2000
            )

            return response

        except Exception as e:
            logger.error(f"문제 해결 전략 실행 실패: {e}")
            return "문제 해결 도움 중 오류가 발생했습니다."

    def _concept_explanation_strategy(self, message: str, session: TutoringSession) -> str:
        """개념 설명 전략"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            # 개념 설명 프롬프트
            prompt = f"""
다음 Python 개념에 대해 설명해주세요:

{message}

학생 수준: {session.student_level.value}

설명 원칙:
1. 개념을 쉽게 이해할 수 있도록 설명
2. 실용적인 예제 제공
3. 언제 사용하는지 설명
4. 학생 수준에 맞는 언어 사용
"""

            response = client.send_message(
                message=prompt,
                system_prompt="당신은 Python 개념 설명 전문가입니다. 복잡한 개념을 쉽게 설명하는 능력이 있습니다.",
                max_tokens=2500
            )

            return response

        except Exception as e:
            logger.error(f"개념 설명 전략 실행 실패: {e}")
            return "개념 설명 중 오류가 발생했습니다."

    def _debugging_strategy(self, message: str, session: TutoringSession) -> str:
        """디버깅 전략"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            if not session.context.get("code"):
                return "디버깅 도움을 받으려면 코드를 공유해주세요."

            # 디버깅 프롬프트
            prompt = f"""
학생이 다음 디버깅 문제에 대해 도움을 요청하고 있습니다:

{message}

학생 수준: {session.student_level.value}

학생의 코드:
```python
{session.context['code']}
```

디버깅 도움 원칙:
1. 오류의 원인을 찾아서 설명
2. 해결 방법 제안
3. 오류 방지 방법 교육
4. 학생이 직접 수정할 수 있도록 격려
"""

            response = client.send_message(
                message=prompt,
                system_prompt="당신은 Python 디버깅 전문가입니다. 학생들이 버그를 찾고 수정할 수 있도록 도와주세요.",
                max_tokens=2500
            )

            return response

        except Exception as e:
            logger.error(f"디버깅 전략 실행 실패: {e}")
            return "디버깅 도움 중 오류가 발생했습니다."

    def _fallback_response(self, message: str, student_level: StudentLevel) -> str:
        """대체 응답 (AI 사용 불가능한 경우)"""
        responses = {
            StudentLevel.BEGINNER: f"'{message}'에 대해 좋은 질문이에요! 아직 해당 기능을 사용할 수 없지만, Python 문서를 확인해보세요.",
            StudentLevel.INTERMEDIATE: f"'{message}'는 흥미로운 주제입니다. 현재 시스템 설정으로는 상세한 답변을 제공할 수 없습니다.",
            StudentLevel.ADVANCED: f"'{message}'에 대해 현재는 상세한 답변을 드릴 수 없습니다. 문서를 참고해주세요."
        }
        return responses.get(student_level, "현재 해당 기능을 사용할 수 없습니다.")

    def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """세션 요약 반환"""
        session = self._get_session(session_id)

        if not session:
            return {}

        return {
            "session_id": session.session_id,
            "mode": session.mode.value,
            "student_level": session.student_level.value,
            "topic": session.topic,
            "message_count": session.message_count,
            "code_shares": session.code_shares,
            "duration": (datetime.utcnow() - session.start_time).total_seconds() if not session.end_time else 0
        }

    def end_session(self, session_id: Optional[str] = None):
        """튜터링 세션 종료"""
        session = self._get_session(session_id)

        if session:
            session.end_time = datetime.utcnow()
            logger.info(f"튜터링 세션 종료: {session.session_id}")


# 전역 튜터 인스턴스
interactive_tutor = None


def get_interactive_tutor() -> InteractiveTutor:
    """대화형 튜터 인스턴스 반환"""
    global interactive_tutor
    if interactive_tutor is None:
        interactive_tutor = InteractiveTutor()
    return interactive_tutor


if __name__ == "__main__":
    # 튜터 테스트
    print("🧪 대화형 튜터 테스트")

    tutor = InteractiveTutor()

    # 세션 생성
    session = tutor.create_session(
        user_id=1,
        mode=TutoringMode.CONVERSATION,
        student_level=StudentLevel.BEGINNER,
        topic="Python 기초"
    )

    print(f"✅ 세션 생성: {session.session_id}")

    # 메시지 처리 테스트
    try:
        response = tutor.process_message(
            "Python에서 리스트는 어떻게 사용하나요?",
            session_id=session.session_id
        )
        print(f"✅ 응답 생성: {len(response)} 문자")

        # 세션 요약
        summary = tutor.get_session_summary(session.session_id)
        print(f"✅ 세션 요약: {summary}")

        print("\n🎉 튜터 테스트 완료!")

    except Exception as e:
        print(f"❌ 튜터 테스트 실패: {e}")
