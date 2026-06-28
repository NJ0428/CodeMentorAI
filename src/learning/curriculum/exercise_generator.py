"""
연습 문제 생성기
사용자 진도에 맞춘 개인화된 연습 문제 생성
"""
import random
from typing import List, Dict, Any, Optional
from loguru import logger

from src.learning.curriculum.models import Exercise, DifficultyLevel, ExerciseType


class ExerciseGenerator:
    """연습 문제 생성기"""

    def __init__(self):
        self.exercise_templates = self._initialize_templates()
        logger.info("연습 문제 생성기 초기화 완료")

    def generate_personalized_exercises(
        self,
        user_level: DifficultyLevel,
        weak_topics: List[str],
        recent_performance: Dict[str, Any],
        count: int = 5
    ) -> List[Exercise]:
        """개인화된 연습 문제 생성"""
        try:
            recommended_exercises = []

            # 약점 주제에 대한 문제 생성
            for topic in weak_topics[:count]:
                exercise = self._generate_exercise_for_topic(
                    topic, user_level, recent_performance
                )
                if exercise:
                    recommended_exercises.append(exercise)

            # 부족한 경우 추가 문제 생성
            while len(recommended_exercises) < count:
                exercise = self._generate_mixed_exercise(user_level, recent_performance)
                if exercise:
                    recommended_exercises.append(exercise)

            logger.info(f"개인화된 연습 문제 {len(recommended_exercises)}개 생성")
            return recommended_exercises

        except Exception as e:
            logger.error(f"개인화된 연습 문제 생성 실패: {e}")
            return []

    def generate_practice_exercises(
        self,
        topic: str,
        user_level: DifficultyLevel,
        count: int = 3
    ) -> List[Exercise]:
        """특정 주제의 연습 문제 생성"""
        try:
            exercises = []

            for i in range(count):
                exercise = self._generate_exercise_for_topic(topic, user_level, {})
                if exercise:
                    exercises.append(exercise)

            logger.info(f"연습 문제 {len(exercises)}개 생성: {topic}")
            return exercises

        except Exception as e:
            logger.error(f"연습 문제 생성 실패: {e}")
            return []

    def create_variant_exercise(
        self,
        base_exercise: Exercise,
        difficulty_modifier: str = "same"
    ) -> Exercise:
        """기존 문제의 변형 생성"""
        try:
            # 난이도 조절
            if difficulty_modifier == "easier":
                xp_reward = max(5, base_exercise.xp_reward - 5)
                time_estimate = max(15, base_exercise.time_estimate - 10)
                hints = base_exercise.hints + ["추가 힌트: 문제를 단순화해보세요"]
            elif difficulty_modifier == "harder":
                xp_reward = base_exercise.xp_reward + 5
                time_estimate = base_exercise.time_estimate + 10
                hints = base_exercise.hints[:-1] if len(base_exercise.hints) > 1 else base_exercise.hints
            else:  # same
                xp_reward = base_exercise.xp_reward
                time_estimate = base_exercise.time_estimate
                hints = base_exercise.hints

            # 변형 문제 생성
            variant_exercise = Exercise(
                id=f"{base_exercise.id}_variant_{random.randint(1000, 9999)}",
                title=f"{base_exercise.title} (변형)",
                description=base_exercise.description,
                exercise_type=base_exercise.exercise_type,
                difficulty=base_exercise.difficulty,
                topic=base_exercise.topic,
                starter_code=base_exercise.starter_code,
                solution=base_exercise.solution,
                hints=hints,
                time_estimate=time_estimate,
                xp_reward=xp_reward,
                prerequisites=base_exercise.prerequisites,
                learning_objectives=base_exercise.learning_objectives,
                test_cases=base_exercise.test_cases
            )

            logger.info(f"변형 문제 생성: {variant_exercise.id}")
            return variant_exercise

        except Exception as e:
            logger.error(f"변형 문제 생성 실패: {e}")
            return base_exercise

    def _generate_exercise_for_topic(
        self,
        topic: str,
        user_level: DifficultyLevel,
        performance: Dict[str, Any]
    ) -> Optional[Exercise]:
        """주제별 연습 문제 생성"""
        try:
            # 주제에 맞는 템플릿 찾기
            template_key = f"{user_level.value}_{topic}"
            template = self.exercise_templates.get(template_key)

            if not template:
                # 기본 템플릿 사용
                template = self.exercise_templates.get(f"{user_level.value}_default")

            if not template:
                return None

            # 문제 ID 생성
            exercise_id = f"ex_{user_level.value}_{topic}_{random.randint(1000, 9999)}"

            # 난이도 조절
            avg_score = performance.get("average_score", 7.0)
            if avg_score < 6.0:
                xp_multiplier = 0.8  # 더 쉬운 문제
            elif avg_score > 8.5:
                xp_multiplier = 1.2  # 더 어려운 문제
            else:
                xp_multiplier = 1.0

            exercise = Exercise(
                id=exercise_id,
                title=template["title"],
                description=template["description"],
                exercise_type=ExerciseType(template.get("exercise_type", "code_completion")),
                difficulty=user_level,
                topic=topic,
                starter_code=template.get("starter_code"),
                solution=template.get("solution"),
                hints=template.get("hints", []),
                time_estimate=template.get("time_estimate", 30),
                xp_reward=int(template.get("xp_reward", 10) * xp_multiplier),
                learning_objectives=template.get("learning_objectives", [])
            )

            return exercise

        except Exception as e:
            logger.error(f"주제별 문제 생성 실패: {e}")
            return None

    def _generate_mixed_exercise(
        self,
        user_level: DifficultyLevel,
        performance: Dict[str, Any]
    ) -> Optional[Exercise]:
        """혼합형 연습 문제 생성"""
        try:
            # 다양한 주제에서 문제 생성
            topics = ["basics", "control_flow", "functions", "data_structures"]
            topic = random.choice(topics)

            return self._generate_exercise_for_topic(topic, user_level, performance)

        except Exception as e:
            logger.error(f"혼합형 문제 생성 실패: {e}")
            return None

    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """연습 문제 템플릿 초기화"""
        templates = {}

        # 초급 - 기초
        templates["beginner_basics"] = {
            "title": "변수와 출력 연습",
            "description": "변수를 생성하고 print 함수로 출력해보세요.",
            "exercise_type": "code_completion",
            "starter_code": "# 이름 변수를 만들고 출력하세요\nname = \"___\"\nprint(name)",
            "solution": "name = \"홍길동\"\nprint(name)",
            "hints": [
                "따옴표 안에 이름을 입력하세요",
                "변수명은 자유롭게 지을 수 있습니다"
            ],
            "time_estimate": 15,
            "xp_reward": 10,
            "learning_objectives": ["변수 생성", "print 함수 사용"]
        }

        # 초급 - 제어 흐름
        templates["beginner_control_flow"] = {
            "title": "if 조건문 연습",
            "description": "숫자가 짝수인지 확인하는 코드를 완성하세요.",
            "exercise_type": "code_completion",
            "starter_code": "num = 4\nif num % 2 == ___:\n    print(\"짝수입니다\")",
            "solution": "num = 4\nif num % 2 == 0:\n    print(\"짝수입니다\")",
            "hints": [
                "나머지 연산자 %의 결과가 0이면 짝수입니다",
                "빈칸에 0을 입력하세요"
            ],
            "time_estimate": 20,
            "xp_reward": 15,
            "learning_objectives": ["if 조건문", "나머지 연산자"]
        }

        # 초급 - 기본
        templates["beginner_default"] = {
            "title": "Hello Python",
            "description": "첫 Python 프로그램을 작성해보세요.",
            "exercise_type": "code_completion",
            "starter_code": 'print("___, World!")',
            "solution": 'print("Hello, World!")',
            "hints": ["따옴표 안에 Hello를 입력하세요"],
            "time_estimate": 10,
            "xp_reward": 5,
            "learning_objectives": ["print 함수 사용법"]
        }

        # 중급 - 함수
        templates["intermediate_functions"] = {
            "title": "함수 정의 연습",
            "description": "두 수를 더하는 함수를 만드세요.",
            "exercise_type": "code_completion",
            "starter_code": "def add_numbers(a, b):\n    ___ a + b\n\nresult = add_numbers(3, 5)\nprint(result)",
            "solution": "def add_numbers(a, b):\n    return a + b\n\nresult = add_numbers(3, 5)\nprint(result)",
            "hints": [
                "함수의 결과를 반환하려면 return을 사용하세요",
                "return 키워드를 사용하세요"
            ],
            "time_estimate": 25,
            "xp_reward": 20,
            "learning_objectives": ["함수 정의", "return 문", "매개변수"]
        }

        # 중급 - 기본
        templates["intermediate_default"] = {
            "title": "리스트 comprehension",
            "description": "리스트 comprehension을 사용하여 짝수 리스트를 만드세요.",
            "exercise_type": "code_completion",
            "starter_code": "numbers = [1, 2, 3, 4, 5, 6]\neven_numbers = [num for num in numbers if num % 2 == ___]\nprint(even_numbers)",
            "solution": "numbers = [1, 2, 3, 4, 5, 6]\neven_numbers = [num for num in numbers if num % 2 == 0]\nprint(even_numbers)",
            "hints": ["짝수는 2로 나누어 떨어지는 수입니다"],
            "time_estimate": 20,
            "xp_reward": 15,
            "learning_objectives": ["리스트 comprehension", "조건 필터링"]
        }

        # 고급 - 기본
        templates["advanced_default"] = {
            "title": "클래스 정의 연습",
            "description": "간단한 Person 클래스를 만드세요.",
            "exercise_type": "code_completion",
            "starter_code": "class Person:\n    def __init__(self, name, age):\n        self.name = ___\n        self.age = age\n\nperson = Person(\"철수\", 20)\nprint(person.name)",
            "solution": "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n\nperson = Person(\"철수\", 20)\nprint(person.name)",
            "hints": [
                "__init__ 메서드에서 속성을 초기화하세요",
                "self.name = name 형식을 사용하세요"
            ],
            "time_estimate": 30,
            "xp_reward": 25,
            "learning_objectives": ["클래스 정의", "__init__ 메서드", "속성 초기화"]
        }

        # 고급 - OOP
        templates["advanced_oop"] = {
            "title": "상속 구현",
            "description": "Student 클래스가 Person을 상속받도록 만드세요.",
            "exercise_type": "code_completion",
            "starter_code": "class Person:\n    def __init__(self, name):\n        self.name = name\n\nclass Student(Person):\n    def __init__(self, name, student_id):\n         ___.__init__(name)\n        self.student_id = student_id",
            "solution": "class Person:\n    def __init__(self, name):\n        self.name = name\n\nclass Student(Person):\n    def __init__(self, name, student_id):\n        super().__init__(name)\n        self.student_id = student_id",
            "hints": [
                "부모 클래스의 초기화 메서드를 호출하세요",
                "super()를 사용하세요"
            ],
            "time_estimate": 35,
            "xp_reward": 30,
            "learning_objectives": ["클래스 상속", "super() 사용법"]
        }

        return templates


# 전역 인스턴스
_exercise_generator = None


def get_exercise_generator() -> ExerciseGenerator:
    """연습 문제 생성기 인스턴스 반환"""
    global _exercise_generator
    if _exercise_generator is None:
        _exercise_generator = ExerciseGenerator()
    return _exercise_generator


if __name__ == "__main__":
    # 연습 문제 생성기 테스트
    print("🧪 연습 문제 생성기 테스트")

    generator = get_exercise_generator()

    # 개인화된 문제 생성
    weak_topics = ["basics", "control_flow"]
    performance = {"average_score": 6.5}

    exercises = generator.generate_personalized_exercises(
        DifficultyLevel.BEGINNER,
        weak_topics,
        performance,
        count=3
    )

    print(f"✅ 생성된 연습 문제: {len(exercises)}개")
    for exercise in exercises:
        print(f"   - {exercise.title} (XP: {exercise.xp_reward})")

    # 주제별 연습 문제 생성
    topic_exercises = generator.generate_practice_exercises(
        "functions",
        DifficultyLevel.INTERMEDIATE,
        count=2
    )

    print(f"✅ 함수 연습 문제: {len(topic_exercises)}개")
    for exercise in topic_exercises:
        print(f"   - {exercise.title}")

    # 변형 문제 생성
    if exercises:
        variant = generator.create_variant_exercise(exercises[0], "easier")
        print(f"✅ 변형 문제: {variant.title} (XP: {variant.xp_reward})")

    print("\n🎉 연습 문제 생성기 테스트 통과!")