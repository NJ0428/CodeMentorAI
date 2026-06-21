# CodeMentorAI 사용자 가이드

## 시작하기

### 설치 방법

1. Python 3.11 이상 설치 확인
```bash
python --version
```

2. 리포지토리 클론
```bash
git clone <repository-url>
cd CodeMentorAI
```

3. 가상 환경 생성
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. 의존성 설치
```bash
pip install -r requirements/base.txt
```

5. API 키 설정
```bash
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 추가
```

6. 애플리케이션 실행
```bash
python src/main.py
```

## 인터페이스 가이드

### 메인 윈도우

```
┌─────────────────────────────────────────────────────────────┐
│  Menu: File | Edit | View | Learning | Tools | Help         │
├──────┬──────────────────────────────────────────────────────┤
│      │  [Code Analysis] [Learning] [Chat]                    │
│ Side │                                                       │
│ bar  │         Code Editor                                    │
│      │  ┌────────────────────────────────────────────────┐  │
│ Nav  │  │  def hello_world():                            │  │
│      │  │      print("Hello, World!")                     │  │
│      │  └────────────────────────────────────────────────┘  │
│      │                                                       │
│      │  [Run] [Analyze] [Ask Mentor]                         │
│      ├──────────────────────────────────────────────────────┤
│      │                                                       │
│      │         Analysis Results / Chat                       │
│      │  ┌────────────────────────────────────────────────┐  │
│      │  │  💡 Code Quality: 8/10                          │  │
│      │  │  ⚠️ Consider using f-string                     │  │
│      │  └────────────────────────────────────────────────┘  │
└──────┴──────────────────────────────────────────────────────┤
│  Status: Ready | Progress: 45%                                │
└─────────────────────────────────────────────────────────────┘
```

### 주요 기능

#### 1. 코드 작성 및 분석

1. **코드 작성**: Code Editor 탭에서 Python 코드 작성
2. **코드 실행**: `Run` 버튼으로 코드 실행
3. **코드 분석**: `Analyze` 버튼으로 AI 기반 코드 분석
4. **디버깅**: `Debug` 버튼으로 디버깅 모드

#### 2. AI 멘토링

1. **코드 분석 피드백**:
   - 코드 품질 점수 (1-10점)
   - 발견된 문제 및 해결책
   - 개선 제안
   - 좋은 점 칭찬

2. **실시간 튜터링**:
   - Chat 탭에서 질문 입력
   - Python 문법 및 개념 설명
   - 개인화된 학습 가이드

#### 3. 학습 진도

1. **Progress 탭**: 학습 진도 확인
2. **Achievements**: 성취 및 뱃지 확인
3. **커리큘럼**: 학습 주제 및 진도 상황

### 메뉴 기능

#### File 메뉴
- **New Code**: 새 코드 작성 시작
- **Open**: 기존 Python 파일 열기
- **Save**: 현재 코드 저장
- **Export**: 학습 데이터 내보내기
- **Exit**: 애플리케이션 종료

#### Edit 메뉴
- **Undo/Redo**: 실행 취소/재실행
- **Cut/Copy/Paste**: 텍스트 편집

#### View 메뉴
- **Toggle Sidebar**: 사이드바 표시/숨기기
- **Settings**: 애플리케이션 설정

#### Learning 메뉴
- **Start Learning**: 새로운 학습 세션 시작
- **My Progress**: 학습 진도 확인
- **Achievements**: 성취 목록 확인

## 사용 팁

### 1. 효과적인 코드 작성

- **점진적 개발**: 작은 함수부터 시작하여 점진적으로 복잡한 코드 작성
- **자주 분석 받기**: 코드 완성 전에 중간 단계에서 분석 요청
- **피드백 활용**: AI 제안을 적용하여 코드 개선

### 2. 학습 전략

**초보자 (Beginner)**:
- 기본 문법부터 시작
- 자주 질문하고 피드백 받기
- 예제 코드 많이 작성해보기

**중급자 (Intermediate)**:
- 실전 프로젝트 시작
- 디자인 패턴 학습
- 테스트 코드 작성

**고급자 (Advanced)**:
- 복잡한 아키텍처 설계
- 성능 최적화
- 오픈소스 프로젝트 참여

### 3. 일반적인 문제 해결

**API 연결 오류**:
- .env 파일의 API 키 확인
- 인터넷 연결 상태 확인
- API 할당량 확인

**코드 분석 오류**:
- 문법 오류 수정 후 재시도
- 코드 길이가 너무 길면 분할하여 분석

**성능 문제**:
- 캐시된 결과 확인
- 불필요한 탭 닫기
- 데이터베이스 정리

## 설정

### 기본 설정 (`.env`)

```bash
# API Keys
ANTHROPIC_API_KEY=your_api_key_here

# Database
DATABASE_PATH=sqlite:///codementorai.db

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/codementorai.log

# Application
DEFAULT_LANGUAGE=en
THEME=default
AUTO_SAVE_INTERVAL=300
```

### 애플리케이션 설정

**View > Settings** 메뉴에서 다음 설정 가능:

- **테마**: Default, Dark
- **언어**: 한국어, English
- **글꼴**: 코드 에디터 글꼴 및 크기
- **자동 저장**: 자동 저장 간격 설정

## 데이터 관리

### 백업

1. **자동 백업**: 매일 자정 자동 백업
2. **수동 백업**: File > Export > Backup
3. **백업 위치**: `backups/` 디렉토리

### 데이터 내보내기

1. **학습 진도**: JSON/CSV 형식
2. **코드 제출 기록**: Python 파일 형식
3. **분석 결과**: PDF 보고서 형식

### 데이터 가져오기

1. 백업 파일 선택
2. 가져올 데이터 유형 선택
3. 가져오기 실행

## 키보드 단축키

- **Ctrl+N**: 새 코드
- **Ctrl+O**: 파일 열기
- **Ctrl+S**: 저장
- **Ctrl+Z**: 실행 취소
- **Ctrl+Y**: 재실행
- **F5**: 코드 실행
- **F6**: 코드 분석
- **Ctrl+Q**: 애플리케이션 종료

## FAQ

**Q: 오프라인에서 사용할 수 있나요?**
A: 기본 코드 분석은 가능하지만, AI 멘토링 기능은 인터넷 연결이 필요합니다.

**Q: 여러 사용자 계정을 만들 수 있나요?**
A: 현재 버전은 단일 사용자를 지원합니다. 다중 사용자 지원은 향후 업데이트에서 제공될 예정입니다.

**Q: 코드 분석 결과는 얼마나 정확한가요?**
A: Claude API를 활용한 고급 분석으로 매우 정확하지만, 100% 완벽하지는 않습니다. 항상 코드를 직접 검토하세요.

**Q: 내 데이터가 안전한가요?**
A: 모든 데이터는 로컬에 저장됩니다. API 호출 시에만 코드 분석을 위해 Claude에 전송됩니다.

## 지원 및 피드백

- **버그 신고**: GitHub Issues
- **기능 제안**: GitHub Discussions
- **질문**: GitHub Discussions 또는 이메일

---

**최종 업데이트**: 2024년 6월
**버전**: 0.1.0