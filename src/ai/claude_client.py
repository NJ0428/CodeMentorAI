"""
Claude API 클라이언트
Anthropic Claude API와의 통신 관리
"""
import time
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import settings
from src.config.api_keys import api_key_manager


class RateLimiter:
    """API 속도 제한 관리"""

    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def acquire(self, timeout: Optional[float] = None):
        """속도 제한 확보"""
        current_time = time.time()

        # 오래된 요청 제거
        self.requests = [req_time for req_time in self.requests
                         if current_time - req_time < self.time_window]

        # 속도 제한 확인
        if len(self.requests) >= self.max_requests:
            if timeout is None:
                wait_time = self.requests[0] + self.time_window - current_time
                logger.warning(f"속도 제한 도달. {wait_time:.2f}초 대기 중...")
                time.sleep(wait_time)
                self.acquire()  # 재시도
            else:
                raise Exception("속도 제한 초과")

        # 요청 기록
        self.requests.append(current_time)


class ClaudeClient:
    """Claude API 클라이언트"""

    def __init__(self):
        try:
            api_key = api_key_manager.get_api_key()
            self.client = Anthropic(api_key=api_key)
            self.model = settings.api.claude_model
            self.max_tokens = settings.api.max_tokens
            self.timeout = settings.api.timeout

            # 속도 제한
            self.rate_limiter = RateLimiter(
                max_requests=settings.api.rate_limit_requests,
                time_window=settings.api.rate_limit_period
            )

            logger.info("Claude API 클라이언트 초기화 완료")

        except Exception as e:
            logger.error(f"Claude API 클라이언트 초기화 실패: {e}")
            raise

    @retry(
        stop=stop_after_attempt(settings.api.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def send_message(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """메시지 전송 및 응답 수신"""
        try:
            # 속도 제한 확인
            self.rate_limiter.acquire()

            # 파라미터 설정
            max_tokens = max_tokens or self.max_tokens

            logger.debug(f"Claude API 요청 전송 (모델: {self.model})")

            # API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message}
                ]
            )

            # 응답 텍스트 추출
            response_text = response.content[0].text
            logger.debug(f"Claude API 응답 수신 (길이: {len(response_text)}자)")

            return response_text

        except Exception as e:
            logger.error(f"Claude API 요청 실패: {e}")
            raise

    def analyze_code(
        self,
        code: str,
        user_level: str = "beginner",
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """코드 분석 요청"""
        try:
            # 프롬프트 생성
            prompt = self._create_code_analysis_prompt(code, user_level, analysis_type)

            # API 호출
            system_prompt = "당신은 Python 코드 전문가입니다. 코드를 분석하고 구체적이고 실행 가능한 피드백을 제공하세요."

            response_text = self.send_message(
                message=prompt,
                system_prompt=system_prompt,
                max_tokens=3000
            )

            # 응답 파싱
            result = self._parse_code_analysis_response(response_text)

            logger.info(f"코드 분석 완료: 점수={result.get('score', 'N/A')}")
            return result

        except Exception as e:
            logger.error(f"코드 분석 실패: {e}")
            raise

    def get_tutoring_response(
        self,
        question: str,
        code_context: Optional[str] = None,
        student_level: str = "beginner"
    ) -> str:
        """튜터링 응답 요청"""
        try:
            # 프롬프트 생성
            prompt = self._create_tutoring_prompt(question, code_context, student_level)

            # API 호출
            system_prompt = "당신은 친절하고 유능한 Python 튜터입니다. 학생의 질문에 명확하고 격려하는 답변을 제공하세요."

            response_text = self.send_message(
                message=prompt,
                system_prompt=system_prompt,
                max_tokens=2000
            )

            logger.info("튜터링 응답 생성 완료")
            return response_text

        except Exception as e:
            logger.error(f"튜터링 응답 생성 실패: {e}")
            raise

    def _create_code_analysis_prompt(
        self,
        code: str,
        user_level: str,
        analysis_type: str
    ) -> str:
        """코드 분석 프롬프트 생성"""
        prompt = f"""다음 Python 코드를 분석해주세요:

```python
{code}
```

사용자 수준: {user_level}
분석 유형: {analysis_type}

다음 형식으로 분석 결과를 제공해주세요:

1. **코드 품질 점수**: 1-10점
2. **발견된 문제**: (있는 경우)
   - 심각도 (높음/중간/낮음)
   - 문제 설명
   - 해결 제안
3. **개선 제안**: (있는 경우)
   - 구체적이고 실행 가능한 방법
   - 예제 코드
4. **좋은 점**: (있는 경우)
   - 잘 구현된 부분
   - 칭찬과 격려

응답은 JSON 형식으로 제공해주세요:
{{
    "score": 1-10,
    "issues": [{{"severity": "high/medium/low", "description": "문제 설명", "solution": "해결책"}}],
    "suggestions": [{{"description": "제안", "example": "예제 코드"}}],
    "strengths": ["좋은 점들"]
}}"""

        return prompt

    def _create_tutoring_prompt(
        self,
        question: str,
        code_context: Optional[str],
        student_level: str
    ) -> str:
        """튜터링 프롬프트 생성"""
        prompt = f"""학생의 질문에 답변해주세요:

학생 질문: {question}
학생 수준: {student_level}
"""

        if code_context:
            prompt += f"\n관련 코드:\n```python\n{code_context}\n```\n"

        prompt += """
답변 원칙:
1. 단계별로 설명하세요 (너무 많은 정보 한 번에 제공하지 않기)
2. 실용적인 예제를 제공하세요
3. 격려와 긍정적 피드백을 포함하세요
4. 다음 학습 단계를 제안하세요
5. 학생 수준에 맞는 언어를 사용하세요
"""

        return prompt

    def _parse_code_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """코드 분석 응답 파싱"""
        try:
            import json

            # JSON 파싅 시도
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # JSON 형식이 아닌 경우 기본 구조 생성
                result = {
                    "score": 7,
                    "issues": [],
                    "suggestions": [],
                    "strengths": [],
                    "raw_response": response_text
                }

            # 필수 필드 확인
            if "score" not in result:
                result["score"] = 7
            if "issues" not in result:
                result["issues"] = []
            if "suggestions" not in result:
                result["suggestions"] = []
            if "strengths" not in result:
                result["strengths"] = []

            return result

        except Exception as e:
            logger.error(f"응답 파싱 실패: {e}")
            return {
                "score": 5,
                "issues": [],
                "suggestions": [],
                "strengths": [],
                "error": str(e)
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """사용 통계 반환"""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "rate_limit": {
                "max_requests": self.rate_limiter.max_requests,
                "time_window": self.rate_limiter.time_window,
                "recent_requests": len(self.rate_limiter.requests)
            }
        }


# 전역 클라이언트 인스턴스
claude_client = None


def get_claude_client() -> ClaudeClient:
    """클라이언트 인스턴스 반환"""
    global claude_client
    if claude_client is None:
        claude_client = ClaudeClient()
    return claude_client


if __name__ == "__main__":
    # 클라이언트 테스트
    try:
        client = get_claude_client()

        # 사용 통계
        stats = client.get_usage_stats()
        print("📊 Claude API 클라이언트 상태:")
        print(f"  모델: {stats['model']}")
        print(f"  최대 토큰: {stats['max_tokens']}")
        print(f"  속도 제한: {stats['rate_limit']['max_requests']} 요청/{stats['rate_limit']['time_window']}초")

        # 간단한 테스트
        test_code = """
def hello_world():
    print("Hello, World!")
    x = 10
    return x
"""

        result = client.analyze_code(test_code, user_level="beginner")
        print("✅ 코드 분석 테스트 완료")
        print(f"  점수: {result.get('score')}")

    except Exception as e:
        print(f"❌ 클라이언트 테스트 실패: {e}")