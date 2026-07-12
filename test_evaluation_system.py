"""
평가 시스템 통합 테스트
"""
import unittest
import sys
import os
from datetime import datetime

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 프로젝트 경로 추가
sys.path.insert(0, 'D:/claude/CodeMentorAI')

from src.evaluation import (
    QuizGenerator, DifficultyLevel,
    CodingProblemGenerator, ProblemCategory,
    AutoEvaluator,
    FeedbackGenerator, FeedbackType, FeedbackLevel
)


class TestQuizGenerator(unittest.TestCase):
    """퀴즈 생성기 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.generator = QuizGenerator()

    def test_create_quiz(self):
        """퀴즈 생성 테스트"""
        quiz = self.generator.create_quiz(
            title="테스트 퀴즈",
            description="테스트용 퀴즈입니다",
            difficulty=DifficultyLevel.BEGINNER,
            topic="variables"
        )

        self.assertIsNotNone(quiz)
        self.assertEqual(quiz.title, "테스트 퀴즈")
        self.assertEqual(quiz.difficulty, DifficultyLevel.BEGINNER)
        self.assertEqual(quiz.topic, "variables")
        print("✅ 퀴즈 생성 테스트 통과")

    def test_generate_questions(self):
        """문제 생성 테스트"""
        questions = self.generator.generate_questions_from_topic(
            topic="variables",
            difficulty=DifficultyLevel.BEGINNER,
            count=3
        )

        self.assertGreater(len(questions), 0)
        self.assertLessEqual(len(questions), 5)
        print(f"✅ 문제 생성 테스트 통과: {len(questions)}개 문제 생성")

    def test_quiz_submission(self):
        """퀴즈 제출 테스트"""
        # 퀴즈 생성
        quiz = self.generator.create_quiz(
            title="제출 테스트",
            description="제출 테스트용 퀴즈",
            difficulty=DifficultyLevel.BEGINNER,
            topic="variables"
        )

        # 문제 생성
        questions = self.generator.generate_questions_from_topic(
            topic="variables",
            difficulty=DifficultyLevel.BEGINNER,
            count=2
        )

        for question in questions:
            quiz.add_question(question)

        # 퀴즈 제출
        answers = {q.question_id: q.correct_answer for q in quiz.questions}
        result = self.generator.submit_quiz(
            quiz_id=quiz.quiz_id,
            user_id=1,
            answers=answers,
            time_taken=60.0
        )

        self.assertEqual(result.total_questions, len(quiz.questions))
        self.assertEqual(result.correct_count, len(quiz.questions))
        print(f"✅ 퀴즈 제출 테스트 통과: {result.score}/{result.total_points}점")


class TestCodingProblemGenerator(unittest.TestCase):
    """코딩 문제 생성기 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.generator = CodingProblemGenerator()

    def test_create_problem(self):
        """문제 생성 테스트"""
        problem = self.generator.create_problem(
            title="테스트 문제",
            description="테스트용 코딩 문제입니다",
            category=ProblemCategory.FUNCTIONAL,
            difficulty="beginner",
            starter_code="def test():\n    pass"
        )

        self.assertIsNotNone(problem)
        self.assertEqual(problem.title, "테스트 문제")
        self.assertEqual(problem.category, ProblemCategory.FUNCTIONAL)
        print("✅ 코딩 문제 생성 테스트 통과")

    def test_generate_from_template(self):
        """템플릿에서 문제 생성 테스트"""
        problem = self.generator.generate_problem_from_template("beginner", 0)

        self.assertIsNotNone(problem)
        self.assertGreater(len(problem.test_cases), 0)
        print(f"✅ 템플릿 문제 생성 테스트 통과: {problem.title}")
        print(f"   테스트 케이스: {len(problem.test_cases)}개")


class TestAutoEvaluator(unittest.TestCase):
    """자동 평가 시스템 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.evaluator = AutoEvaluator()

    def test_evaluate_correct_code(self):
        """정답 코드 평가 테스트"""
        from src.evaluation.coding_problem import TestCase

        # 테스트 케이스 생성
        test_cases = [
            TestCase(
                test_id="tc1",
                input_data=(1, 2),
                expected_output=3,
                description="기본 테스트"
            ),
            TestCase(
                test_id="tc2",
                input_data=(5, 3),
                expected_output=8,
                description="다른 숫자"
            )
        ]

        # 정답 코드
        correct_code = """
def add_numbers(a, b):
    return a + b
"""

        # 평가 실행
        result = self.evaluator.evaluate_submission(
            problem_id="test_problem",
            user_id=1,
            code=correct_code,
            test_cases=test_cases
        )

        self.assertEqual(result.status.value, "passed")
        self.assertEqual(result.passed_tests, len(test_cases))
        print(f"✅ 정답 코드 평가 테스트 통과: {result.score:.1f}점")

    def test_evaluate_wrong_code(self):
        """오답 코드 평가 테스트"""
        from src.evaluation.coding_problem import TestCase

        # 테스트 케이스 생성
        test_cases = [
            TestCase(
                test_id="tc1",
                input_data=(1, 2),
                expected_output=3,
                description="기본 테스트"
            )
        ]

        # 오답 코드
        wrong_code = """
def add_numbers(a, b):
    return a - b
"""

        # 평가 실행
        result = self.evaluator.evaluate_submission(
            problem_id="test_problem",
            user_id=2,
            code=wrong_code,
            test_cases=test_cases
        )

        self.assertNotEqual(result.status.value, "passed")
        print(f"✅ 오답 코드 평가 테스트 통과: {result.status.value}")


class TestFeedbackGenerator(unittest.TestCase):
    """피드백 생성기 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.generator = FeedbackGenerator()

    def test_generate_quiz_feedback(self):
        """퀴즈 피드백 생성 테스트"""
        feedback = self.generator.generate_feedback(
            feedback_type=FeedbackType.QUIZ,
            user_id=1,
            content_id="quiz_1",
            level=FeedbackLevel.BEGINNER,
            score_data={
                "score": 80.0,
                "percentage": 80.0,
                "total_questions": 10,
                "correct_count": 8,
                "time_taken": 200.0
            }
        )

        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.feedback_type, FeedbackType.QUIZ)
        self.assertGreater(len(feedback.overall_message), 0)
        print(f"✅ 퀴즈 피드백 생성 테스트 통과")
        print(f"   메시지: {feedback.overall_message}")

    def test_generate_coding_feedback(self):
        """코딩 피드백 생성 테스트"""
        feedback = self.generator.generate_feedback(
            feedback_type=FeedbackType.CODING,
            user_id=1,
            content_id="problem_1",
            level=FeedbackLevel.INTERMEDIATE,
            score_data={
                "score": 75.0,
                "total_tests": 10,
                "passed_tests": 7,
                "code_quality": {
                    "complexity_score": 75.0,
                    "style_score": 60.0,
                    "readability_score": 70.0,
                    "best_practices_score": 80.0
                }
            }
        )

        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.feedback_type, FeedbackType.CODING)
        print(f"✅ 코딩 피드백 생성 테스트 통과")
        print(f"   메시지: {feedback.overall_message}")

    def test_summary_report(self):
        """요약 리포트 생성 테스트"""
        # 여러 피드백 생성
        self.generator.generate_feedback(
            feedback_type=FeedbackType.QUIZ,
            user_id=1,
            content_id="quiz_1",
            level=FeedbackLevel.BEGINNER,
            score_data={"score": 80.0, "percentage": 80.0, "total_questions": 10, "correct_count": 8}
        )

        self.generator.generate_feedback(
            feedback_type=FeedbackType.CODING,
            user_id=1,
            content_id="problem_1",
            level=FeedbackLevel.INTERMEDIATE,
            score_data={"score": 70.0, "total_tests": 10, "passed_tests": 7}
        )

        # 요약 리포트 생성
        summary = self.generator.generate_summary_report(user_id=1)

        self.assertEqual(summary["user_id"], 1)
        self.assertGreater(summary["total_feedbacks"], 0)
        print(f"✅ 요약 리포트 생성 테스트 통과")
        print(f"   총 피드백: {summary['total_feedbacks']}건")
        print(f"   평균 점수: {summary['average_score']:.1f}점")


class TestIntegration(unittest.TestCase):
    """통합 테스트"""

    def test_complete_quiz_workflow(self):
        """완전한 퀴즈 워크플로우 테스트"""
        # 1. 퀴즈 생성
        quiz_generator = QuizGenerator()
        quiz = quiz_generator.create_quiz(
            title="통합 테스트 퀴즈",
            description="전체 시스템 테스트용 퀴즈",
            difficulty=DifficultyLevel.BEGINNER,
            topic="variables"
        )

        # 2. 문제 생성
        questions = quiz_generator.generate_questions_from_topic(
            topic="variables",
            difficulty=DifficultyLevel.BEGINNER,
            count=3
        )

        for question in questions:
            quiz.add_question(question)

        # 3. 퀴즈 제출
        answers = {q.question_id: q.correct_answer for q in quiz.questions}
        result = quiz_generator.submit_quiz(
            quiz_id=quiz.quiz_id,
            user_id=1,
            answers=answers,
            time_taken=60.0
        )

        # 4. 피드백 생성
        feedback_generator = FeedbackGenerator()
        feedback = feedback_generator.generate_feedback(
            feedback_type=FeedbackType.QUIZ,
            user_id=1,
            content_id=quiz.quiz_id,
            level=FeedbackLevel.BEGINNER,
            score_data={
                "score": result.score,
                "percentage": (result.score / result.total_points * 100) if result.total_points > 0 else 0,
                "total_questions": result.total_questions,
                "correct_count": result.correct_count,
                "time_taken": result.time_taken
            }
        )

        # 검증
        self.assertGreater(len(quiz.questions), 0)
        self.assertGreater(result.score, 0)
        self.assertIsNotNone(feedback)

        print("✅ 완전한 퀴즈 워크플로우 테스트 통과")
        print(f"   문제 수: {len(quiz.questions)}")
        print(f"   점수: {result.score}/{result.total_points}")
        print(f"   피드백: {feedback.overall_message}")

    def test_complete_coding_workflow(self):
        """완전한 코딩 워크플로우 테스트"""
        from src.evaluation.coding_problem import TestCase

        # 1. 문제 생성
        problem_generator = CodingProblemGenerator()
        problem = problem_generator.generate_problem_from_template("beginner", 0)

        # 2. 코드 평가
        evaluator = AutoEvaluator()

        correct_code = """
def add_numbers(a, b):
    return a + b
"""

        evaluation = evaluator.evaluate_submission(
            problem_id=problem.problem_id,
            user_id=1,
            code=correct_code,
            test_cases=problem.test_cases
        )

        # 3. 피드백 생성
        feedback_generator = FeedbackGenerator()
        feedback = feedback_generator.generate_feedback(
            feedback_type=FeedbackType.CODING,
            user_id=1,
            content_id=problem.problem_id,
            level=FeedbackLevel.BEGINNER,
            score_data={
                "score": evaluation.score,
                "total_tests": evaluation.total_tests,
                "passed_tests": evaluation.passed_tests,
                "code_quality": evaluation.code_quality.to_dict() if evaluation.code_quality else None
            }
        )

        # 검증
        self.assertIsNotNone(problem)
        self.assertGreater(len(problem.test_cases), 0)
        self.assertIsNotNone(evaluation)
        self.assertIsNotNone(feedback)

        print("✅ 완전한 코딩 워크플로우 테스트 통과")
        print(f"   문제: {problem.title}")
        print(f"   점수: {evaluation.score:.1f}")
        print(f"   피드백: {feedback.overall_message}")


def run_tests():
    """모든 테스트 실행"""
    print("🧪 평가 시스템 통합 테스트")
    print("="*60)

    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestQuizGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestCodingProblemGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestFeedbackGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print(f"실행된 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n❌ 일부 테스트 실패")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)