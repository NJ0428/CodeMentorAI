# CodeMentorAI

Python 학습을 위한 AI 기반 멘토링 플랫폼입니다. Anthropic Claude API를 활용하여 개인화된 코드 피드백과 실시간 상호작용을 제공합니다.

## 특징

- **AI 기반 코드 분석**: Claude API를 통한 지능적인 코드 분석 및 최적화 제안
- **실시간 멘토링**: Python 문법과 개념에 대한 개인화된 튜터링
- **진도 추적**: 학습 진행 상황과 성취를 시각화
- **적응형 학습**: 사용자 수준에 맞춘 동적 난이도 조절
- **정적 코드 분석**: PEP8, 복잡도, 보안 취약점 검사
- **로컬 데이터 저장**: SQLite 기반 개인 정보 보호

## 기술 스택

- **GUI**: Tkinter (Python 표준 라이브러리)
- **AI**: Anthropic Claude API
- **코드 분석**: pylint, radon, bandit, black
- **데이터베이스**: SQLite + SQLAlchemy
- **언어**: Python 3.11+

## 설치 방법

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements/base.txt

# API 키 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 추가
```

## 실행 방법

```bash
python src/main.py
```

## 프로젝트 구조

```
CodeMentorAI/
├── src/                     # 소스 코드
│   ├── main.py             # 진입점
│   ├── core/               # 핵심 로직
│   ├── ui/                 # Tkinter UI
│   ├── ai/                 # Claude API 연동
│   ├── code_analysis/      # 코드 분석
│   ├── learning/           # 학습 시스템
│   └── database/           # 데이터베이스
├── resources/              # 학습 자료
├── tests/                  # 테스트
└── docs/                   # 문서
```

## 사용 방법

1. 애플리케이션 실행 후 코드를 작성합니다
2. "Analyze" 버튼으로 코드 분석을 받습니다
3. AI 멘토와 실시간으로 소화하며 개선합니다
4. 학습 진도를 추적하고 성취를 확인합니다
