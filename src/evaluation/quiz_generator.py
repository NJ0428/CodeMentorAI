"""
퀴즈 생성기
Python 학습을 위한 퀴즈 생성 및 관리 기능
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger
import json
import uuid


class QuestionType(str, Enum):
    """문제 유형"""
    MULTIPLE_CHOICE = "multiple_choice"  # 객관식
    TRUE_FALSE = "true_false"  # 참/거짓
    SHORT_ANSWER = "short_answer"  # 단답형
    FILL_BLANK = "fill_blank"  # 빈칸 채우기
    CODE_COMPLETION = "code_completion"  # 코드 완성하기


class DifficultyLevel(str, Enum):
    """난이도 수준"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class QuizQuestion:
    """퀴즈 문제"""
    question_id: str
    question_type: QuestionType
    question_text: str
    difficulty: DifficultyLevel
    options: Optional[List[str]] = None  # 객관식 옵션
    correct_answer: str = ""
    explanation: str = ""  # 해설
    points: int = 10
    tags: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    code_example: Optional[str] = None  # 코드 예시

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "question_id": self.question_id,
            "question_type": self.question_type.value,
            "question_text": self.question_text,
            "difficulty": self.difficulty.value,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "points": self.points,
            "tags": self.tags,
            "hints": self.hints,
            "code_example": self.code_example
        }


@dataclass
class QuizResult:
    """퀴즈 결과"""
    result_id: str
    quiz_id: str
    user_id: int
    answers: Dict[str, str]  # 문제 ID -> 사용자 답안
    score: float
    total_points: int
    correct_count: int
    total_questions: int
    time_taken: float  # 초 단위
    completed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "result_id": self.result_id,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "answers": self.answers,
            "score": self.score,
            "total_points": self.total_points,
            "correct_count": self.correct_count,
            "total_questions": self.total_questions,
            "time_taken": self.time_taken,
            "completed_at": self.completed_at.isoformat(),
            "percentage": (self.score / self.total_points * 100) if self.total_points > 0 else 0
        }


@dataclass
class Quiz:
    """퀴즈"""
    quiz_id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    questions: List[QuizQuestion] = field(default_factory=list)
    topic: Optional[str] = None
    time_limit: Optional[int] = None  # 분 단위
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_question(self, question: QuizQuestion):
        """문제 추가"""
        self.questions.append(question)
        logger.debug(f"퀴즈 '{self.title}'에 문제 추가: {question.question_id}")

    def get_total_points(self) -> int:
        """총 점수 반환"""
        return sum(q.points for q in self.questions)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "quiz_id": self.quiz_id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "questions": [q.to_dict() for q in self.questions],
            "topic": self.topic,
            "time_limit": self.time_limit,
            "created_at": self.created_at.isoformat(),
            "total_points": self.get_total_points(),
            "question_count": len(self.questions)
        }


class QuizGenerator:
    """퀴즈 생성기"""

    def __init__(self):
        self.quizzes: Dict[str, Quiz] = {}
        self.results: Dict[str, QuizResult] = {}

        # Python 주제별 문제 템플릿
        self.question_templates = {
            "beginner": {
                "variables": [
                    {
                        "question": "Python에서 변수를 올바르게 선언하는 방법은?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": ["x = 10", "int x = 10", "var x = 10", "declare x = 10"],
                        "answer": "x = 10",
                        "explanation": "Python은 변수 타입 선언이 필요 없습니다. 값을 할당하여 변수를 생성합니다."
                    },
                    {
                        "question": "Python의 데이터 타입 중 '하나 이상의 값을 순서대로 저장하는 변경 가능한 자료구조'는?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": ["튜플 (tuple)", "리스트 (list)", "세트 (set)", "딕셔너리 (dict)"],
                        "answer": "리스트 (list)",
                        "explanation": "리스트는 변경 가능하며 순서가 있는 데이터 구조입니다."
                    },
                    {
                        "question": "print('Hello' + 'World')의 출력 결과는?",
                        "type": QuestionType.SHORT_ANSWER,
                        "answer": "HelloWorld",
                        "explanation": "문자열 연결 연산자 '+'로 두 문자열을 합칩니다."
                    }
                ],
                "conditionals": [
                    {
                        "question": "Python의 if 문 문법은 올바른 것은?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": [
                            "if x > 5:",
                            "if (x > 5):",
                            "if x > 5 then:",
                            "if [x > 5]:"
                        ],
                        "answer": "if x > 5:",
                        "explanation": "Python은 괄호 없이 if 문을 사용하며, 콜론(:)으로 끝납니다."
                    },
                    {
                        "question": "True and False의 결과는?",
                        "type": QuestionType.TRUE_FALSE,
                        "answer": "False",
                        "explanation": "논리곱(and)은 두 값이 모두 True일 때만 True를 반환합니다."
                    }
                ],
                "loops": [
                    {
                        "question": "range(5)는 어떤 값을 생성하는가?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": ["0, 1, 2, 3, 4", "1, 2, 3, 4, 5", "0, 1, 2, 3, 4, 5", "5개의 난수"],
                        "answer": "0, 1, 2, 3, 4",
                        "explanation": "range(n)은 0부터 n-1까지의 정수를 생성합니다."
                    }
                ]
            },
            "intermediate": {
                "functions": [
                    {
                        "question": "함수를 정의할 때 사용하는 키워드는?",
                        "type": QuestionType.SHORT_ANSWER,
                        "answer": "def",
                        "explanation": "Python에서는 def 키워드로 함수를 정의합니다."
                    },
                    {
                        "question": "다음 중 기본 매개변수값을 올바르게 설정한 것은?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": [
                            "def func(x = 5):",
                            "def func(x=5):",
                            "def func(x:=5):",
                            "def func(x): x=5"
                        ],
                        "answer": "def func(x=5):",
                        "explanation": "기본값은 공백 없이 등호(=)로 설정합니다."
                    }
                ],
                "data_structures": [
                    {
                        "question": "딕셔너리에서 값에 접근할 때 사용하는 연산자는?",
                        "type": QuestionType.SHORT_ANSWER,
                        "answer": "[]",
                        "explanation": "딕셔너리는 대괄호 []와 키로 값에 접근합니다."
                    },
                    {
                        "question": "리스트 슬라이싱 my_list[1:4]는 어떤 요소들을 반환하는가?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": [
                            "인덱스 1, 2, 3",
                            "인덱스 1, 2, 3, 4",
                            "인덱스 0, 1, 2, 3",
                            "인덱스 2, 3, 4"
                        ],
                        "answer": "인덱스 1, 2, 3",
                        "explanation": "슬라이싱은 시작 인덱스부터 끝 인덱스-1까지 반환합니다."
                    }
                ]
            },
            "advanced": {
                "oop": [
                    {
                        "question": "클래스의 생성자 메서드 이름은?",
                        "type": QuestionType.SHORT_ANSWER,
                        "answer": "__init__",
                        "explanation": "__init__ 메서드는 클래스 인스턴스 생성 시 호출됩니다."
                    },
                    {
                        "question": "self 매개변수의 용도는?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": [
                            "클래스 자체를 참조",
                            "인스턴스 자신을 참조",
                            "부모 클래스를 참조",
                            "전역 변수를 참조"
                        ],
                        "answer": "인스턴스 자신을 참조",
                        "explanation": "self는 클래스 인스턴스 자신을 참조하며, 모든 인스턴스 메서드의 첫 번째 매개변수입니다."
                    }
                ],
                "decorators": [
                    {
                        "question": "데코레이터를 사용하는 목적은?",
                        "type": QuestionType.MULTIPLE_CHOICE,
                        "options": [
                            "함수나 메서드의 기능을 확장하거나 수정",
                            "클래스를 장식함",
                            "코드 실행 속도 향상",
                            "메모리 사용량 감소"
                        ],
                        "answer": "함수나 메서드의 기능을 확장하거나 수정",
                        "explanation": "데코레이터는 함수나 메서드의 동작을 수정하거나 확장하는데 사용됩니다."
                    }
                ]
            }
        }

        logger.info("퀴즈 생성기 초기화 완료")

    def create_quiz(
        self,
        title: str,
        description: str,
        difficulty: DifficultyLevel,
        topic: Optional[str] = None,
        time_limit: Optional[int] = None
    ) -> Quiz:
        """새 퀴즈 생성"""
        quiz_id = str(uuid.uuid4())
        quiz = Quiz(
            quiz_id=quiz_id,
            title=title,
            description=description,
            difficulty=difficulty,
            topic=topic,
            time_limit=time_limit
        )

        self.quizzes[quiz_id] = quiz
        logger.info(f"퀴즈 생성: {title} (ID: {quiz_id})")
        return quiz

    def generate_questions_from_topic(
        self,
        topic: str,
        difficulty: DifficultyLevel,
        count: int = 5
    ) -> List[QuizQuestion]:
        """주제로부터 문제 생성"""
        questions = []

        # 해당 난이도의 문제 템플릿 가져오기
        templates = self.question_templates.get(difficulty.value, {}).get(topic, [])

        # AI 기반 문제 생성 시도
        try:
            ai_questions = self._generate_ai_questions(topic, difficulty, count)
            questions.extend(ai_questions)
        except Exception as e:
            logger.warning(f"AI 기반 문제 생성 실패: {e}")
            # 템플릿 문제 사용
            for i, template in enumerate(templates[:count]):
                question = QuizQuestion(
                    question_id=str(uuid.uuid4()),
                    question_type=template["type"],
                    question_text=template["question"],
                    difficulty=difficulty,
                    options=template.get("options"),
                    correct_answer=template["answer"],
                    explanation=template.get("explanation", ""),
                    tags=[topic]
                )
                questions.append(question)

        logger.info(f"주제 '{topic}'에서 {len(questions)}개 문제 생성")
        return questions

    def _generate_ai_questions(
        self,
        topic: str,
        difficulty: DifficultyLevel,
        count: int
    ) -> List[QuizQuestion]:
        """AI로 퀴즈 문제 생성"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            prompt = f"""
Python {topic} 주제에 대해 {difficulty.value} 수준의 퀴즈 문제 {count}개를 생성해주세요.

요구사항:
1. 다양한 유형의 문제 (객관식, 참/거짓, 단답형)
2. 각 문제마다 정답과 해설 포함
3. 문제 난이도는 {difficulty.value} 수준에 맞출 것
4. 실용적이고 교육적인 문제일 것

응답 형식 (JSON):
[
  {{
    "question_type": "multiple_choice|true_false|short_answer",
    "question_text": "문제 내용",
    "options": ["보기1", "보기2", "보기3", "보기4"],  // 객관식만
    "correct_answer": "정답",
    "explanation": "해설",
    "points": 10
  }}
]
"""

            response = client.send_message(
                message=prompt,
                system_prompt="당신은 Python 교육 전문가입니다. 학생들의 이해도를 평가할 수 있는 양질의 퀴즈 문제를 생성합니다.",
                max_tokens=2000
            )

            # JSON 파싱
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())

                questions = []
                for q_data in questions_data:
                    question = QuizQuestion(
                        question_id=str(uuid.uuid4()),
                        question_type=QuestionType(q_data.get("question_type", "multiple_choice")),
                        question_text=q_data["question_text"],
                        difficulty=difficulty,
                        options=q_data.get("options"),
                        correct_answer=q_data["correct_answer"],
                        explanation=q_data.get("explanation", ""),
                        points=q_data.get("points", 10),
                        tags=[topic]
                    )
                    questions.append(question)

                return questions

        except Exception as e:
            logger.error(f"AI 문제 생성 실패: {e}")
            raise

        return []

    def submit_quiz(
        self,
        quiz_id: str,
        user_id: int,
        answers: Dict[str, str],
        time_taken: float
    ) -> QuizResult:
        """퀴즈 제출 및 채점"""
        quiz = self.quizzes.get(quiz_id)
        if not quiz:
            raise ValueError(f"퀴즈를 찾을 수 없습니다: {quiz_id}")

        result_id = str(uuid.uuid4())
        correct_count = 0
        total_points = 0
        earned_points = 0

        # 각 문제 채점
        for question in quiz.questions:
            user_answer = answers.get(question.question_id, "")
            is_correct = self._check_answer(question, user_answer)

            if is_correct:
                correct_count += 1
                earned_points += question.points

            total_points += question.points

        score = earned_points
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0

        result = QuizResult(
            result_id=result_id,
            quiz_id=quiz_id,
            user_id=user_id,
            answers=answers,
            score=score,
            total_points=total_points,
            correct_count=correct_count,
            total_questions=len(quiz.questions),
            time_taken=time_taken
        )

        self.results[result_id] = result

        logger.info(
            f"퀴즈 제출 완료: 사용자 {user_id}, "
            f"점수: {score}/{total_points} ({percentage:.1f}%)"
        )

        return result

    def _check_answer(self, question: QuizQuestion, user_answer: str) -> bool:
        """답안 체크"""
        if not user_answer:
            return False

        # 정답과 사용자 답안 정규화
        correct_normalized = question.correct_answer.strip().lower()
        user_normalized = user_answer.strip().lower()

        return correct_normalized == user_normalized

    def get_feedback(self, result_id: str) -> Dict[str, Any]:
        """퀴즈 결과 피드백 생성"""
        result = self.results.get(result_id)
        quiz = self.quizzes.get(result.quiz_id) if result else None

        if not result or not quiz:
            return {}

        feedback = {
            "overall_performance": self._get_performance_feedback(result),
            "question_feedback": [],
            "improvement_suggestions": []
        }

        # 각 문제별 피드백
        for question in quiz.questions:
            user_answer = result.answers.get(question.question_id, "")
            is_correct = self._check_answer(question, user_answer)

            question_feedback = {
                "question_id": question.question_id,
                "question": question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
                "user_answer": user_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation if not is_correct else ""
            }
            feedback["question_feedback"].append(question_feedback)

        # 개선 제안
        if result.correct_count < len(quiz.questions) * 0.7:
            feedback["improvement_suggestions"].extend([
                "개념을 복습하고 추가 연습 문제를 풀어보세요.",
                "관련 학습 자료를 참고하여 약점을 보완하세요."
            ])

        return feedback

    def _get_performance_feedback(self, result: QuizResult) -> str:
        """전체 성적 피드백"""
        percentage = (result.score / result.total_points * 100) if result.total_points > 0 else 0

        if percentage >= 90:
            return "훌륭합니다! 해당 주제를 완벽하게 이해하고 있습니다."
        elif percentage >= 70:
            return "좋은 성적입니다. 약간의 추가 연습으로 완벽해질 수 있습니다."
        elif percentage >= 50:
            return "기본 개념은 이해하고 있으나, 더 많은 연습이 필요합니다."
        else:
            return "해당 주제를 다시 학습하고 기본 개념을 복습하는 것이 좋겠습니다."

    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """퀴즈 반환"""
        return self.quizzes.get(quiz_id)

    def get_result(self, result_id: str) -> Optional[QuizResult]:
        """결과 반환"""
        return self.results.get(result_id)


# 전역 인스턴스
quiz_generator = None


def get_quiz_generator() -> QuizGenerator:
    """퀴즈 생성기 인스턴스 반환"""
    global quiz_generator
    if quiz_generator is None:
        quiz_generator = QuizGenerator()
    return quiz_generator


if __name__ == "__main__":
    # 퀴즈 생성기 테스트
    print("🧪 퀴즈 생성기 테스트")

    generator = QuizGenerator()

    # 퀴즈 생성
    quiz = generator.create_quiz(
        title="Python 기초 테스트",
        description="Python 기본 개념 평가",
        difficulty=DifficultyLevel.BEGINNER,
        topic="variables"
    )

    # 문제 생성
    questions = generator.generate_questions_from_topic("variables", DifficultyLevel.BEGINNER, 3)
    for q in questions:
        quiz.add_question(q)

    print(f"✅ 퀴즈 생성: {quiz.title}")
    print(f"   문제 수: {len(quiz.questions)}")
    print(f"   총 점수: {quiz.get_total_points()}")

    # 퀴즈 제출 테스트
    answers = {q.question_id: q.correct_answer for q in quiz.questions}
    result = generator.submit_quiz(
        quiz_id=quiz.quiz_id,
        user_id=1,
        answers=answers,
        time_taken=120.0
    )

    print(f"✅ 퀴즈 제출 완료")
    print(f"   점수: {result.score}/{result.total_points}")
    print(f"   정답률: {result.correct_count}/{result.total_questions}")

    # 피드백
    feedback = generator.get_feedback(result.result_id)
    print(f"✅ 피드백 생성 완료")
    print(f"   성적 피드백: {feedback['overall_performance']}")

    print("\n🎉 퀴즈 생성기 테스트 완료!")