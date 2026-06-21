# CodeMentorAI 개발자 가이드

## 개발 환경 설정

### 1. 개발 의존성 설치

```bash
# 개발용 의존성 설치
pip install -r requirements/dev.txt

# 테스트용 의존성 설치
pip install -r requirements/test.txt
```

### 2. 코드 스타일

```bash
# 코드 포맷팅
black src/

# 린트 검사
pylint src/

# 타입 검사
mypy src/
```

### 3. pre-commit 설정

```bash
# pre-commit 설치
pip install pre-commit

# hooks 설치
pre-commit install
```

## 프로젝트 구조

```
CodeMentorAI/
├── src/                    # 소스 코드
│   ├── main.py            # 진입점
│   ├── config/            # 설정
│   ├── core/              # 핵심 로직
│   ├── ui/                # UI 컴포넌트
│   ├── ai/                # AI 연동
│   ├── code_analysis/     # 코드 분석
│   ├── learning/          # 학습 시스템
│   ├── database/          # 데이터베이스
│   ├── utils/             # 유틸리티
│   └── services/          # 서비스
├── tests/                 # 테스트
├── resources/             # 리소스
├── docs/                  # 문서
└── scripts/               # 스크립트
```

## 코딩 규칙

### 1. Python 스타일

```python
# 좋은 예
class CodeAnalyzer:
    """코드 분석기 클래스"""

    def __init__(self):
        self.logger = logger
        self.config = settings

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """코드 분석 실행"""
        # 구현
        pass

# 나쁜 예
class codeAnalyzer:  # snake_case가 아님
    def __init__(self):  # 타입 힌트 없음
        pass
```

### 2. 타입 힌트 사용

```python
from typing import Dict, List, Optional

def analyze_code(
    code: str,
    user_level: str = "beginner"
) -> Dict[str, Any]:
    """코드 분석 실행"""
    pass
```

### 3. 문서화

```python
def analyze_code(code: str, user_level: str = "beginner") -> Dict[str, Any]:
    """
    코드 분석 실행

    Args:
        code: 분석할 Python 코드
        user_level: 사용자 수준 (beginner/intermediate/advanced)

    Returns:
        분석 결과 딕셔너리
        - score: 코드 점수 (1-10)
        - issues: 발견된 문제 목록
        - suggestions: 개선 제안 목록

    Raises:
        ValueError: 잘못된 user_level인 경우
    """
    pass
```

### 4. 에러 핸들링

```python
# 좋은 예
def analyze_code(code: str) -> Dict[str, Any]:
    try:
        result = _analyze_code(code)
        return result
    except SyntaxError as e:
        logger.error(f"문법 오류: {e}")
        return {"error": "syntax_error", "message": str(e)}
    except Exception as e:
        logger.error(f"분석 실패: {e}")
        raise

# 나쁜 예
def analyze_code(code: str) -> Dict[str, Any]:
    return _analyze_code(code)  # 에러 핸들링 없음
```

## 테스트 작성

### 1. 단위 테스트

```python
# tests/unit/test_analyzer.py
import pytest
from src.code_analysis.analyzer import CodeAnalyzer

def test_analyzer_initialization():
    """분석기 초기화 테스트"""
    analyzer = CodeAnalyzer()
    assert analyzer is not None

def test_code_analysis_with_valid_code():
    """유효한 코드 분석 테스트"""
    analyzer = CodeAnalyzer()
    code = "def hello():\n    print('Hello')"
    result = analyzer.analyze_code(code)

    assert result["success"] is True
    assert "score" in result
    assert 1 <= result["score"] <= 10

def test_code_analysis_with_syntax_error():
    """문법 오류 코드 분석 테스트"""
    analyzer = CodeAnalyzer()
    code = "def hello():\n    print('Hello'"  # 문법 오류
    result = analyzer.analyze_code(code)

    assert result["success"] is False
    assert len(result["errors"]) > 0
```

### 2. 통합 테스트

```python
# tests/integration/test_api_integration.py
import pytest
from src.ai.claude_client import get_claude_client

def test_claude_client_initialization():
    """Claude 클라이언트 초기화 테스트"""
    client = get_claude_client()
    assert client is not None

def test_code_analysis_with_claude():
    """Claude API를 통한 코드 분석 테스트"""
    client = get_claude_client()
    code = "def hello():\n    print('Hello')"

    result = client.analyze_code(code, user_level="beginner")

    assert "score" in result
    assert "issues" in result
    assert "suggestions" in result
```

### 3. 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/unit/test_analyzer.py

# 커버리지 리포트
pytest --cov=src --cov-report=html
```

## 디버깅

### 1. 로깅

```python
from loguru import logger

# 로그 출력
logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")

# 예외와 함께 로그
try:
    risky_operation()
except Exception as e:
    logger.error(f"작업 실패: {e}", exc_info=True)
```

### 2. 디버거 사용

```bash
# pdb 사용
python -m pdb src/main.py

# ipdb 사용 (더 나은 디버거)
pip install ipdb
python -m ipdb src/main.py
```

## 성능 최적화

### 1. 프로파일링

```python
import cProfile
import pstats

def profile_function():
    """함수 프로파일링"""
    profiler = cProfile.Profile()
    profiler.enable()

    # 분석할 코드
    analyze_code()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(10)
```

### 2. 메모리 최적화

```python
# 제너레이터 사용으로 메모리 절약
def process_large_file(filename):
    """대용량 파일 처리"""
    with open(filename) as f:
        for line in f:  # 한 줄씩 처리
            yield process_line(line)
```

## CI/CD

### 1. GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements/dev.txt
          pip install -r requirements/test.txt
      - name: Run tests
        run: pytest
      - name: Check code style
        run: |
          black --check src/
          pylint src/
```

## 기여 가이드

### 1. Pull Request 프로세스

1. Fork 리포지토리
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

### 2. 커밋 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경 (로직 변경 없음)
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드/설정 관련 변경
```

## 릴리스 프로세스

### 1. 버전 번호

```
MAJOR.MINOR.PATCH

예: 0.1.0
- MAJOR: 주요 변경사항
- MINOR: 새로운 기능
- PATCH: 버그 수정
```

### 2. 릴리스 체크리스트

- [ ] 테스트 통과
- [ ] 문서 업데이트
- [ ] CHANGELOG.md 업데이트
- [ ] 버전 번호 업데이트
- [ ] Git 태그 생성
- [ ] PyPI에 배포 (해당하는 경우)

## 문화

### 1. 협업 원칙

- 존중과 배려
- 명확한 커뮤니케이션
- 코드 리뷰 적극 참여
- 지속적인 학습

### 2. 문제 해결

- 작은 단위로 나누기
- 재현 가능한 예제 만들기
- 로그 및 에러 메시지 공유
- 해결책 문서화

## 리소스

- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)

---

**최종 업데이트**: 2024년 6월
**메인테이너**: CodeMentorAI Team