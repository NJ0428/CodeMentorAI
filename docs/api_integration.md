# Claude API 연동 가이드

## API 키 설정

### 1. 환경 변수 설정

`.env` 파일을 생성하고 API 키를 추가하세요:

```bash
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### 2. API 키 확인

```python
from src.config.api_keys import api_key_manager

# API 키 상태 확인
info = api_key_manager.get_safe_key_info()
print(f"API Key 설정됨: {info['is_set']}")
print(f"키 미리보기: {info['key_preview']}")
```

## Claude 클라이언트 사용

### 기본 사용

```python
from src.ai.claude_client import get_claude_client

# 클라이언트 인스턴스 가져오기
client = get_claude_client()

# 메시지 전송
response = client.send_message("안녕하세요, Claude!")
print(response)
```

### 코드 분석

```python
# 코드 분석 요청
code = """
def hello_world():
    print("Hello, World!")
"""

result = client.analyze_code(
    code=code,
    user_level="beginner",
    analysis_type="full"
)

print(f"점수: {result['score']}")
print(f"이슈: {result['issues']}")
print(f"제안: {result['suggestions']}")
```

### 튜터링

```python
# 학습 질문에 대한 답변 요청
response = client.get_tutoring_response(
    question="Python에서 리스트와 튜플의 차이는 무엇인가요?",
    code_context=None,
    student_level="beginner"
)

print(response)
```

## API 사용 패턴

### 속도 제한 관리

```python
from src.ai.claude_client import RateLimiter

# 속도 제한 설정 (60초 동안 60개 요청)
rate_limiter = RateLimiter(max_requests=60, time_window=60)

# 요청 전 속도 제한 확인
rate_limiter.acquire()
# API 요청 실행
```

### 재시도 로직

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_claude_api(prompt):
    # API 호출
    response = client.send_message(prompt)
    return response
```

## 비용 최적화

### 1. 캐싱 전략

```python
import hashlib

def get_cache_key(code):
    return hashlib.md5(code.encode()).hexdigest()

# 분석 결과 캐싱
cache = {}
cache_key = get_cache_key(code)

if cache_key in cache:
    return cache[cache_key]

# 새로운 분석 실행
result = client.analyze_code(code)
cache[cache_key] = result
```

### 2. 모델 선택

```python
# 단순 작업: Haiku (저렴)
# 복잡한 작업: Sonnet (고성능)

# 프롬프트 복잡도에 따른 모델 선택
if complexity < 3:
    model = "claude-3-5-haiku-20241022"
else:
    model = "claude-3-5-sonnet-20241022"
```

### 3. 토큰 최적화

```python
def optimize_code_for_analysis(code):
    # 주석 제거
    code = remove_comments(code)

    # 불필요한 공백 제거
    code = compress_whitespace(code)

    # 관련 없는 코드 제외
    code = extract_relevant_code(code)

    return code
```

## 프롬프트 템플릿

### 코드 분석 프롬프트

`resources/prompts/code_analysis.txt`:

```
당신은 Python 코드 전문가입니다. 다음 코드를 분석하여:

코드: {code}
사용자 수준: {user_level}

다음 형식으로 분석 결과를 제공해주세요:
{
    "score": 1-10,
    "issues": [...],
    "suggestions": [...],
    "strengths": [...]
}
```

### 튜터링 프롬프트

`resources/prompts/tutoring.txt`:

```
당신은 친절한 Python 튜터입니다.

학생 질문: {question}
학생 수준: {student_level}

답변 원칙:
- 단계별 설명
- 실용적인 예제
- 격려와 긍정적 피드백
- 다음 학습 단계 제안
```

## 에러 핸들링

```python
import anthropic

try:
    response = client.send_message(message)
except anthropic.APIError as e:
    print(f"API 오류: {e}")
    # 재시도 또는 다른 조치
except anthropic.RateLimitError as e:
    print(f"속도 제한: {e}")
    # 잠시 대기 후 재시도
except anthropic.AuthenticationError as e:
    print(f"인증 오류: {e}")
    # API 키 확인
```

## 사용 통계

```python
# 클라이언트 사용 통계
stats = client.get_usage_stats()

print(f"모델: {stats['model']}")
print(f"최대 토큰: {stats['max_tokens']}")
print(f"속도 제한: {stats['rate_limit']}")
```

## 보안 모범 사례

1. **API 키 보호**: 절대 코드에 API 키를 하드코딩하지 마세요
2. **입력 검증**: 모든 사용자 입력을 검증하세요
3. **속도 제한**: API 속도 제한을 준수하세요
4. **에러 핸들링**: 적절한 에러 핸들링을 구현하세요
5. **로그 관리**: API 키가 로그에 남지 않도록 주의하세요