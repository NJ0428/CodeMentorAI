"""
코딩 문제 생성기
Python 코딩 문제 생성 및 관리 기능
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger
import json
import uuid
import ast
import sys
from io import StringIO


class ProblemCategory(str, Enum):
    """문제 카테고리"""
    ALGORITHM = "algorithm"  # 알고리즘
    DATA_STRUCTURE = "data_structure"  # 자료구조
    STRING_MANIPULATION = "string_manipulation"  # 문자열 처리
    MATHEMATICS = "mathematics"  # 수학
    FUNCTIONAL = "functional"  # 함수 작성
    CLASS_DESIGN = "class_design"  # 클래스 설계
    DEBUGGING = "debugging"  # 디버깅


@dataclass
class TestCase:
    """테스트 케이스"""
    test_id: str
    input_data: Any
    expected_output: Any
    description: str = ""
    is_hidden: bool = False  # 숨겨진 테스트 케이스 여부
    timeout: float = 5.0  # 실행 시간 제한 (초)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "test_id": self.test_id,
            "input_data": str(self.input_data),
            "expected_output": str(self.expected_output),
            "description": self.description,
            "is_hidden": self.is_hidden,
            "timeout": self.timeout
        }


@dataclass
class CodingProblem:
    """코딩 문제"""
    problem_id: str
    title: str
    description: str
    category: ProblemCategory
    difficulty: str  # "beginner", "intermediate", "advanced"
    starter_code: str = ""
    template_code: str = ""
    test_cases: List[TestCase] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    sample_solution: str = ""
    time_limit: float = 5.0
    memory_limit: int = 256  # MB
    tags: List[str] = field(default_factory=list)
    points: int = 100
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_test_case(self, test_case: TestCase):
        """테스트 케이스 추가"""
        self.test_cases.append(test_case)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "problem_id": self.problem_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "difficulty": self.difficulty,
            "starter_code": self.starter_code,
            "template_code": self.template_code,
            "test_cases": [tc.to_dict() for tc in self.test_cases if not tc.is_hidden],
            "hidden_test_count": sum(1 for tc in self.test_cases if tc.is_hidden),
            "constraints": self.constraints,
            "hints": self.hints,
            "time_limit": self.time_limit,
            "memory_limit": self.memory_limit,
            "tags": self.tags,
            "points": self.points,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ProblemSubmission:
    """문제 제출"""
    submission_id: str
    problem_id: str
    user_id: int
    code: str
    language: str = "python"
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    status: str = "pending"  # "pending", "running", "passed", "failed", "error"
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "submission_id": self.submission_id,
            "problem_id": self.problem_id,
            "user_id": self.user_id,
            "code": self.code,
            "language": self.language,
            "submitted_at": self.submitted_at.isoformat(),
            "execution_time": self.execution_time,
            "memory_used": self.memory_used,
            "status": self.status,
            "test_results": self.test_results,
            "error_message": self.error_message,
            "score": self.score
        }


class CodingProblemGenerator:
    """코딩 문제 생성기"""

    def __init__(self):
        self.problems: Dict[str, CodingProblem] = {}
        self.submissions: Dict[str, ProblemSubmission] = {}

        # 기본 문제 템플릿
        self.problem_templates = {
            "beginner": [
                {
                    "title": "두 수의 합",
                    "description": "두 정수 a와 b가 주어졌을 때, 두 수의 합을 반환하는 함수를 작성하세요.",
                    "category": ProblemCategory.FUNCTIONAL,
                    "starter_code": "def add_numbers(a, b):\n    # 여기에 코드를 작성하세요\n    pass",
                    "template_code": "def add_numbers(a, b):\n    pass",
                    "sample_solution": "def add_numbers(a, b):\n    return a + b",
                    "test_cases": [
                        {"input": (1, 2), "output": 3, "description": "기본 테스트"},
                        {"input": (-1, 1), "output": 0, "description": "음수 포함"},
                        {"input": (0, 0), "output": 0, "description": "0 테스트"}
                    ],
                    "constraints": ["-1000 <= a, b <= 1000"],
                    "hints": ["단순히 a와 b를 더하면 됩니다."],
                    "points": 50
                },
                {
                    "title": "짝수 판별",
                    "description": "주어진 정수가 짝수인지 홀수인지 판별하는 함수를 작성하세요.",
                    "category": ProblemCategory.FUNCTIONAL,
                    "starter_code": "def is_even(n):\n    # 여기에 코드를 작성하세요\n    pass",
                    "template_code": "def is_even(n):\n    pass",
                    "sample_solution": "def is_even(n):\n    return n % 2 == 0",
                    "test_cases": [
                        {"input": (2,), "output": True, "description": "짝수"},
                        {"input": (3,), "output": False, "description": "홀수"},
                        {"input": (0,), "output": True, "description": "0은 짝수"}
                    ],
                    "constraints": ["-1000 <= n <= 1000"],
                    "hints": ["나머지 연산자 %를 사용하세요."],
                    "points": 50
                }
            ],
            "intermediate": [
                {
                    "title": "리스트 평균 계산",
                    "description": "정수 리스트의 평균을 계산하는 함수를 작성하세요.",
                    "category": ProblemCategory.FUNCTIONAL,
                    "starter_code": "def calculate_average(numbers):\n    # 여기에 코드를 작성하세요\n    pass",
                    "template_code": "def calculate_average(numbers):\n    pass",
                    "sample_solution": "def calculate_average(numbers):\n    return sum(numbers) / len(numbers) if numbers else 0",
                    "test_cases": [
                        {"input": ([1, 2, 3, 4, 5],), "output": 3.0, "description": "기본 리스트"},
                        {"input": ([10, 20, 30],), "output": 20.0, "description": "3개 숫자"},
                        {"input": ([],), "output": 0, "description": "빈 리스트"}
                    ],
                    "constraints": ["빈 리스트의 경우 0을 반환"],
                    "hints": ["sum() 함수와 len() 함수를 사용하세요.", "0으로 나누기에 주의하세요."],
                    "points": 100
                },
                {
                    "title": "문자열 뒤집기",
                    "description": "주어진 문자열을 뒤집는 함수를 작성하세요.",
                    "category": ProblemCategory.STRING_MANIPULATION,
                    "starter_code": "def reverse_string(s):\n    # 여기에 코드를 작성하세요\n    pass",
                    "template_code": "def reverse_string(s):\n    pass",
                    "sample_solution": "def reverse_string(s):\n    return s[::-1]",
                    "test_cases": [
                        {"input": ("hello",), "output": "olleh", "description": "일반 문자열"},
                        {"input": ("Python",), "output": "nohtyP", "description": "대소문자 혼합"},
                        {"input": ("a",), "output": "a", "description": "한 문자"},
                        {"input": ("",), "output": "", "description": "빈 문자열"}
                    ],
                    "constraints": ["길이 제한 없음"],
                    "hints": ["슬라이싱 [::-1]을 사용하면 쉽게 해결할 수 있습니다."],
                    "points": 100
                }
            ],
            "advanced": [
                {
                    "title": "소수 판별",
                    "description": "주어진 정수가 소수(Prime Number)인지 판별하는 함수를 작성하세요.",
                    "category": ProblemCategory.ALGORITHM,
                    "starter_code": "def is_prime(n):\n    # 여기에 코드를 작성하세요\n    pass",
                    "template_code": "def is_prime(n):\n    pass",
                    "sample_solution": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
                    "test_cases": [
                        {"input": (2,), "output": True, "description": "가장 작은 소수"},
                        {"input": (7,), "output": True, "description": "소수"},
                        {"input": (4,), "output": False, "description": "합성수"},
                        {"input": (1,), "output": False, "description": "1은 소수가 아님"},
                        {"input": (97,), "output": True, "description": "큰 소수"}
                    ],
                    "constraints": ["1 <= n <= 10^6"],
                    "hints": ["2는 특수 케이스입니다.", "n의 제곱근까지만 확인하면 충분합니다."],
                    "points": 150
                },
                {
                    "title": "피보나치 수열",
                    "description": "n번째 피보나치 수를 반환하는 함수를 작성하세요.",
                    "category": ProblemCategory.ALGORITHM,
                    "starter_code": "def fibonacci(n):\n    # 여기에 코드를 작성하세요\n    pass",
                    "template_code": "def fibonacci(n):\n    pass",
                    "sample_solution": "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
                    "test_cases": [
                        {"input": (0,), "output": 0, "description": "F(0)"},
                        {"input": (1,), "output": 1, "description": "F(1)"},
                        {"input": (5,), "output": 5, "description": "F(5)"},
                        {"input": (10,), "output": 55, "description": "F(10)"}
                    ],
                    "constraints": ["0 <= n <= 30", "재귀 사용 시 시간 초과 가능성"],
                    "hints": ["반복문을 사용하면 더 효율적입니다.", "두 변수만으로 풀이할 수 있습니다."],
                    "points": 150
                }
            ]
        }

        logger.info("코딩 문제 생성기 초기화 완료")

    def create_problem(
        self,
        title: str,
        description: str,
        category: ProblemCategory,
        difficulty: str,
        starter_code: str = "",
        template_code: str = "",
        constraints: Optional[List[str]] = None,
        hints: Optional[List[str]] = None,
        time_limit: float = 5.0,
        memory_limit: int = 256,
        tags: Optional[List[str]] = None,
        points: int = 100
    ) -> CodingProblem:
        """새 코딩 문제 생성"""
        problem_id = str(uuid.uuid4())
        problem = CodingProblem(
            problem_id=problem_id,
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            starter_code=starter_code,
            template_code=template_code,
            constraints=constraints or [],
            hints=hints or [],
            time_limit=time_limit,
            memory_limit=memory_limit,
            tags=tags or [],
            points=points
        )

        self.problems[problem_id] = problem
        logger.info(f"코딩 문제 생성: {title} (ID: {problem_id})")
        return problem

    def generate_problem_from_template(self, difficulty: str, index: int = 0) -> Optional[CodingProblem]:
        """템플릿에서 문제 생성"""
        templates = self.problem_templates.get(difficulty, [])

        if 0 <= index < len(templates):
            template = templates[index]

            problem = self.create_problem(
                title=template["title"],
                description=template["description"],
                category=template["category"],
                difficulty=difficulty,
                starter_code=template["starter_code"],
                template_code=template["template_code"],
                constraints=template["constraints"],
                hints=template["hints"],
                points=template["points"]
            )

            # 테스트 케이스 추가
            for tc_data in template["test_cases"]:
                test_case = TestCase(
                    test_id=str(uuid.uuid4()),
                    input_data=tc_data["input"],
                    expected_output=tc_data["output"],
                    description=tc_data["description"]
                )
                problem.add_test_case(test_case)

            logger.info(f"템플릿에서 문제 생성: {template['title']}")
            return problem

        return None

    def generate_ai_problem(
        self,
        topic: str,
        difficulty: str,
        category: ProblemCategory
    ) -> Optional[CodingProblem]:
        """AI로 코딩 문제 생성"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            prompt = f"""
Python {topic} 주제에 대해 {difficulty} 수준의 코딩 문제를 생성해주세요.

카테고리: {category.value}

요구사항:
1. 문제 설명이 명확할 것
2. 시작 코드 템플릿 제공
3. 3개 이상의 테스트 케이스
4. 문제 제약 조건과 힌트 포함
5. 실용적이고 교육적인 문제일 것

응답 형식 (JSON):
{{
  "title": "문제 제목",
  "description": "문제 설명",
  "starter_code": "def solution():\\n    pass",
  "test_cases": [
    {{"input": [1, 2], "output": 3, "description": "테스트 설명"}},
    ...
  ],
  "constraints": ["제약 조건1", "제약 조건2"],
  "hints": ["힌트1", "힌트2"],
  "sample_solution": "def solution():\\n    return result",
  "points": 100
}}
"""

            response = client.send_message(
                message=prompt,
                system_prompt="당신은 Python 코딩 문제 작성 전문가입니다. 학생들의 프로그래밍 능력을 향상시킬 수 있는 양질의 문제를 생성합니다.",
                max_tokens=2500
            )

            # JSON 파싱
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                problem_data = json.loads(json_match.group())

                problem = self.create_problem(
                    title=problem_data["title"],
                    description=problem_data["description"],
                    category=category,
                    difficulty=difficulty,
                    starter_code=problem_data["starter_code"],
                    template_code=problem_data.get("starter_code", ""),
                    constraints=problem_data.get("constraints", []),
                    hints=problem_data.get("hints", []),
                    points=problem_data.get("points", 100)
                )

                # 테스트 케이스 추가
                for tc_data in problem_data.get("test_cases", []):
                    test_case = TestCase(
                        test_id=str(uuid.uuid4()),
                        input_data=tuple(tc_data["input"]) if isinstance(tc_data["input"], list) else tc_data["input"],
                        expected_output=tc_data["output"],
                        description=tc_data.get("description", "")
                    )
                    problem.add_test_case(test_case)

                # 샘플 해결책
                if "sample_solution" in problem_data:
                    problem.sample_solution = problem_data["sample_solution"]

                logger.info(f"AI 문제 생성 완료: {problem.title}")
                return problem

        except Exception as e:
            logger.error(f"AI 문제 생성 실패: {e}")

        return None

    def get_problem(self, problem_id: str) -> Optional[CodingProblem]:
        """문제 반환"""
        return self.problems.get(problem_id)

    def get_all_problems(self) -> List[CodingProblem]:
        """모든 문제 반환"""
        return list(self.problems.values())

    def get_problems_by_difficulty(self, difficulty: str) -> List[CodingProblem]:
        """난이도별 문제 반환"""
        return [p for p in self.problems.values() if p.difficulty == difficulty]

    def get_problems_by_category(self, category: ProblemCategory) -> List[CodingProblem]:
        """카테고리별 문제 반환"""
        return [p for p in self.problems.values() if p.category == category]


# 전역 인스턴스
coding_problem_generator = None


def get_coding_problem_generator() -> CodingProblemGenerator:
    """코딩 문제 생성기 인스턴스 반환"""
    global coding_problem_generator
    if coding_problem_generator is None:
        coding_problem_generator = CodingProblemGenerator()
    return coding_problem_generator


if __name__ == "__main__":
    # 코딩 문제 생성기 테스트
    print("🧪 코딩 문제 생성기 테스트")

    generator = CodingProblemGenerator()

    # 템플릿에서 문제 생성
    print("\n📝 템플릿 문제 생성:")
    beginner_problem = generator.generate_problem_from_template("beginner", 0)
    if beginner_problem:
        print(f"✅ 문제: {beginner_problem.title}")
        print(f"   테스트 케이스: {len(beginner_problem.test_cases)}개")
        print(f"   난이도: {beginner_problem.difficulty}")

    # 사용자 정의 문제 생성
    print("\n📝 사용자 정의 문제 생성:")
    custom_problem = generator.create_problem(
        title="최댓값 찾기",
        description="정수 리스트에서 최댓값을 찾는 함수를 작성하세요.",
        category=ProblemCategory.ALGORITHM,
        difficulty="beginner",
        starter_code="def find_maximum(numbers):\n    # 여기에 코드를 작성하세요\n    pass",
        constraints=["리스트는 최소 1개 이상의 요소"],
        hints=["max() 함수를 사용하지 말고 직접 구현해보세요."],
        points=75
    )

    # 테스트 케이스 추가
    test_cases = [
        {"input": ([1, 5, 3],), "output": 5, "description": "일반 케이스"},
        {"input": ([10],), "output": 10, "description": "요소 1개"},
        {"input": ([-5, -2, -10],), "output": -2, "description": "음수만"}
    ]

    for tc_data in test_cases:
        test_case = TestCase(
            test_id=str(uuid.uuid4()),
            input_data=tc_data["input"],
            expected_output=tc_data["output"],
            description=tc_data["description"]
        )
        custom_problem.add_test_case(test_case)

    print(f"✅ 문제: {custom_problem.title}")
    print(f"   테스트 케이스: {len(custom_problem.test_cases)}개")
    print(f"   점수: {custom_problem.points}")

    # AI 문제 생성 시도
    print("\n🤖 AI 문제 생성:")
    try:
        ai_problem = generator.generate_ai_problem(
            topic="리스트 처리",
            difficulty="intermediate",
            category=ProblemCategory.FUNCTIONAL
        )
        if ai_problem:
            print(f"✅ AI 생성 문제: {ai_problem.title}")
            print(f"   설명: {ai_problem.description[:100]}...")
    except Exception as e:
        print(f"⚠️  AI 문제 생성 실패 (예상됨): {e}")

    # 전체 문제 목록
    all_problems = generator.get_all_problems()
    print(f"\n📊 전체 문제 수: {len(all_problems)}개")

    print("\n🎉 코딩 문제 생성기 테스트 완료!")