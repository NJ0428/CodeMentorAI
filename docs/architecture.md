# CodeMentorAI 아키텍처 문서

## 시스템 개요

CodeMentorAI는 Python 학습을 위한 AI 기반 멘토링 데스크톱 애플리케이션입니다. Anthropic Claude API를 활용하여 개인화된 코드 피드백과 실시간 상호작용을 제공합니다.

## 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│                   (Tkinter UI Components)                    │
├─────────────────────────────────────────────────────────────┤
│                     Application Layer                        │
│              (Business Logic & Services)                     │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│              (Core Engines & Analyzers)                      │
├─────────────────────────────────────────────────────────────┤
│                   Integration Layer                          │
│              (Claude API, File System)                       │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                        │
│           (Database, Cache, Logging, etc.)                   │
└─────────────────────────────────────────────────────────────┘
```

## 핵심 컴포넌트

### 1. UI Layer (`src/ui/`)

- **MainWindow**: 메인 애플리케이션 윈도우
- **Components**: 코드 에디터, 채팅 패널, 분석 결과 패널 등
- **Dialogs**: 설정, 세션 관리, 내보내기 다이얼로그

### 2. Core Engine (`src/core/`)

- **CodeMentorEngine**: 중앙 코디네이터
- **SessionManager**: 학습 세션 관리
- **EventBus**: 이벤트 버스 (pub/sub)

### 3. AI Integration (`src/ai/`)

- **ClaudeClient**: Claude API 클라이언트
- **PromptManager**: 프롬프트 템플릿 관리
- **ResponseParser**: API 응답 파서

### 4. Code Analysis (`src/code_analysis/`)

- **CodeAnalyzer**: 통합 코드 분석 시스템
- **PythonParser**: AST 기반 파서
- **ComplexityAnalyzer**: 복잡도 분석
- **StyleChecker**: PEP8 스타일 검사
- **SecurityChecker**: 보안 취약점 검사

### 5. Database (`src/database/`)

- **Models**: SQLAlchemy ORM 모델
- **Repositories**: 데이터 접근 패턴
- **Migrations**: 데이터베이스 마이그레이션

## 데이터 흐름

### 코드 분석 흐름

```
User Code Input
    ↓
PythonParser (AST Parsing)
    ↓
StyleChecker (PEP8)
    ↓
ComplexityAnalyzer (Complexity)
    ↓
SecurityChecker (Security)
    ↓
ClaudeClient (AI Analysis)
    ↓
Result Merger
    ↓
UI Display
```

### 학습 세션 흐름

```
User Login
    ↓
SessionManager.create_session()
    ↓
Code Submission
    ↓
Code Analysis
    ↓
AI Tutoring
    ↓
Progress Update
    ↓
Session Save
```

## 기술 스택

- **GUI**: Tkinter (Python 표준 라이브러리)
- **AI**: Anthropic Claude API
- **Database**: SQLite + SQLAlchemy
- **Code Analysis**: pylint, radon, bandit, black
- **Logging**: loguru
- **Testing**: pytest

## 확장 포인트

### 1. 새로운 분석기 추가
```python
class CustomAnalyzer:
    def analyze(self, code: str) -> Dict[str, Any]:
        # 사용자 정의 분석 로직
        pass
```

### 2. 새로운 학습 커리큘럼 추가
```
resources/curriculum/
├── beginner/
├── intermediate/
└── advanced/
```

### 3. 새로운 프롬프트 템플릿 추가
```
resources/prompts/
├── code_analysis.txt
├── tutoring.txt
└── custom_prompt.txt
```

## 보안 고려사항

1. **API 키 관리**: 환경 변수를 통한 안전한 저장
2. **코드 실행**: 샌드박스 환경에서의 코드 실행
3. **데이터 저장**: 사용자 데이터 로컬 저장
4. **입력 검증**: 모든 사용자 입력 검증

## 성능 최적화

1. **결과 캐싱**: 동일 코드 분석 결과 재사용
2. **비동기 처리**: 백그라운드에서 코드 분석
3. **지연 로딩**: 대규모 커리큘럼 데이터 효율적 로드
4. **API 속도 제한**: Claude API 호출 최적화

## 배포

### 빌드
```bash
python scripts/build.py
```

### 패키징
```bash
pyinstaller --onefile --windowed src/main.py
```

### 설치
```bash
pip install -e .
```