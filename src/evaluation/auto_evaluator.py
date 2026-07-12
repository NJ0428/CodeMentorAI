"""
자동 평가 시스템
코드 실행, 테스트 케이스 검증, 성능 평가 기능
"""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger
import json
import uuid
import ast
import sys
from io import StringIO
import time
import tracemalloc


class EvaluationStatus(str, Enum):
    """평가 상태"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class TestResult:
    """테스트 결과"""
    test_id: str
    test_name: str
    status: EvaluationStatus
    input_data: str = ""
    expected_output: str = ""
    actual_output: str = ""
    execution_time: float = 0.0
    memory_used: int = 0
    error_message: str = ""
    is_hidden: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "input_data": str(self.input_data),
            "expected_output": str(self.expected_output),
            "actual_output": str(self.actual_output),
            "execution_time": self.execution_time,
            "memory_used": self.memory_used,
            "error_message": self.error_message,
            "is_hidden": self.is_hidden
        }


@dataclass
class CodeQualityMetrics:
    """코드 품질 메트릭"""
    complexity_score: float = 0.0  # 복잡도 점수 (0-100)
    style_score: float = 0.0  # 스타일 점수 (0-100)
    readability_score: float = 0.0  # 가독성 점수 (0-100)
    best_practices_score: float = 0.0  # 베스트 프랙티스 점수 (0-100)
    security_issues: List[str] = field(default_factory=list)
    code_smells: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    line_count: int = 0
    function_count: int = 0
    comment_ratio: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "complexity_score": self.complexity_score,
            "style_score": self.style_score,
            "readability_score": self.readability_score,
            "best_practices_score": self.best_practices_score,
            "security_issues": self.security_issues,
            "code_smells": self.code_smells,
            "suggestions": self.suggestions,
            "line_count": self.line_count,
            "function_count": self.function_count,
            "comment_ratio": self.comment_ratio
        }


@dataclass
class EvaluationResult:
    """평가 결과"""
    evaluation_id: str
    problem_id: str
    user_id: int
    code: str
    status: EvaluationStatus
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    test_results: List[TestResult] = field(default_factory=list)
    code_quality: Optional[CodeQualityMetrics] = None
    score: float = 0.0
    max_score: float = 100.0
    execution_time: float = 0.0
    memory_used: int = 0
    feedback: str = ""
    evaluated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_score(self):
        """점수 계산"""
        if self.total_tests > 0:
            test_score = (self.passed_tests / self.total_tests) * 70  # 70%는 테스트 통과

            quality_score = 0
            if self.code_quality:
                quality_scores = [
                    self.code_quality.complexity_score,
                    self.code_quality.style_score,
                    self.code_quality.readability_score,
                    self.code_quality.best_practices_score
                ]
                quality_score = sum(quality_scores) / len(quality_scores) * 0.3  # 30%는 코드 품질

            self.score = test_score + quality_score

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "evaluation_id": self.evaluation_id,
            "problem_id": self.problem_id,
            "user_id": self.user_id,
            "code": self.code,
            "status": self.status.value,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "test_results": [tr.to_dict() for tr in self.test_results],
            "code_quality": self.code_quality.to_dict() if self.code_quality else None,
            "score": self.score,
            "max_score": self.max_score,
            "execution_time": self.execution_time,
            "memory_used": self.memory_used,
            "feedback": self.feedback,
            "evaluated_at": self.evaluated_at.isoformat(),
            "pass_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        }


class AutoEvaluator:
    """자동 평가 시스템"""

    def __init__(self):
        self.evaluations: Dict[str, EvaluationResult] = {}
        self.evaluation_history: List[EvaluationResult] = []

        logger.info("자동 평가 시스템 초기화 완료")

    def evaluate_submission(
        self,
        problem_id: str,
        user_id: int,
        code: str,
        test_cases: List[Any],
        timeout: float = 5.0,
        include_quality_analysis: bool = True
    ) -> EvaluationResult:
        """코드 제출 평가"""
        evaluation_id = str(uuid.uuid4())

        # 평가 결과 생성
        evaluation = EvaluationResult(
            evaluation_id=evaluation_id,
            problem_id=problem_id,
            user_id=user_id,
            code=code,
            status=EvaluationStatus.RUNNING
        )

        self.evaluations[evaluation_id] = evaluation

        try:
            # 코드 기본 검증
            if not self._validate_python_syntax(code):
                evaluation.status = EvaluationStatus.ERROR
                evaluation.feedback = "파이썬 문법 오류가 있습니다."
                return evaluation

            # 테스트 케이스 실행
            start_time = time.time()

            for test_case in test_cases:
                test_result = self._run_test_case(
                    code=code,
                    test_case=test_case,
                    timeout=timeout
                )
                evaluation.test_results.append(test_result)

                if test_result.status == EvaluationStatus.PASSED:
                    evaluation.passed_tests += 1
                else:
                    evaluation.failed_tests += 1

                evaluation.total_tests += 1

                # 메모리 및 시간 업데이트
                evaluation.execution_time += test_result.execution_time
                evaluation.memory_used = max(evaluation.memory_used, test_result.memory_used)

            evaluation.execution_time = time.time() - start_time

            # 코드 품질 분석
            if include_quality_analysis:
                evaluation.code_quality = self._analyze_code_quality(code)

            # 최종 상태 결정
            if evaluation.passed_tests == evaluation.total_tests:
                evaluation.status = EvaluationStatus.PASSED
            elif evaluation.passed_tests > 0:
                evaluation.status = EvaluationStatus.FAILED
            else:
                evaluation.status = EvaluationStatus.FAILED

            # 점수 계산
            evaluation.calculate_score()

            # 피드백 생성
            evaluation.feedback = self._generate_feedback(evaluation)

            logger.info(
                f"평가 완료: {evaluation_id} "
                f"(통과: {evaluation.passed_tests}/{evaluation.total_tests}, "
                f"점수: {evaluation.score:.1f})"
            )

        except Exception as e:
            logger.error(f"평가 중 오류 발생: {e}")
            evaluation.status = EvaluationStatus.ERROR
            evaluation.feedback = f"평가 중 오류가 발생했습니다: {str(e)}"

        # 평가 기록 저장
        self.evaluation_history.append(evaluation)

        return evaluation

    def _validate_python_syntax(self, code: str) -> bool:
        """파이썬 문법 검증"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _run_test_case(
        self,
        code: str,
        test_case: Any,
        timeout: float = 5.0
    ) -> TestResult:
        """단일 테스트 케이스 실행"""
        test_id = getattr(test_case, 'test_id', str(uuid.uuid4()))
        test_name = getattr(test_case, 'description', f'Test {test_id}')

        test_result = TestResult(
            test_id=test_id,
            test_name=test_name,
            status=EvaluationStatus.PENDING
        )

        try:
            # 메모리 추적 시작
            tracemalloc.start()

            # 실행 환경 설정
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            # 입력 데이터 추출
            input_data = getattr(test_case, 'input_data', None)
            expected_output = getattr(test_case, 'expected_output', None)

            test_result.input_data = str(input_data)
            test_result.expected_output = str(expected_output)
            test_result.is_hidden = getattr(test_case, 'is_hidden', False)

            # 코드 실행 준비
            namespace = {}
            exec(code, namespace)

            # 함수 찾기
            solution_func = None
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    solution_func = obj
                    break

            if solution_func is None:
                test_result.status = EvaluationStatus.ERROR
                test_result.error_message = "실행 가능한 함수를 찾을 수 없습니다."
                return test_result

            # 함수 실행
            start_time = time.time()

            if isinstance(input_data, tuple):
                result = solution_func(*input_data)
            elif isinstance(input_data, list):
                result = solution_func(*input_data)
            else:
                result = solution_func(input_data)

            execution_time = time.time() - start_time

            # 메모리 사용량 확인
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            test_result.execution_time = execution_time
            test_result.memory_used = peak

            # 시간 초과 확인
            if execution_time > timeout:
                test_result.status = EvaluationStatus.TIMEOUT
                test_result.error_message = f"실행 시간 초과 ({timeout}초)"
                return test_result

            # 결과 비교
            test_result.actual_output = str(result)

            if result == expected_output:
                test_result.status = EvaluationStatus.PASSED
            else:
                test_result.status = EvaluationStatus.FAILED
                test_result.error_message = f"예상값: {expected_output}, 실제값: {result}"

        except SyntaxError as e:
            test_result.status = EvaluationStatus.ERROR
            test_result.error_message = f"문법 오류: {str(e)}"
            tracemalloc.stop()

        except Exception as e:
            test_result.status = EvaluationStatus.ERROR
            test_result.error_message = f"실행 오류: {str(e)}"
            tracemalloc.stop()

        finally:
            # stdout 복원
            sys.stdout = old_stdout

        return test_result

    def _analyze_code_quality(self, code: str) -> CodeQualityMetrics:
        """코드 품질 분석"""
        metrics = CodeQualityMetrics()

        try:
            # 기본 통계
            lines = code.split('\n')
            metrics.line_count = len([l for l in lines if l.strip()])

            # 주석 분석
            comment_lines = len([l for l in lines if l.strip().startswith('#')])
            if metrics.line_count > 0:
                metrics.comment_ratio = comment_lines / metrics.line_count

            # AST 파싱
            tree = ast.parse(code)

            # 함수 수
            metrics.function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])

            # 복잡도 분석
            complexity = self._calculate_complexity(tree)
            metrics.complexity_score = max(0, 100 - complexity * 10)

            # 스타일 점수
            metrics.style_score = self._calculate_style_score(code)

            # 가독성 점수
            metrics.readability_score = self._calculate_readability_score(code)

            # 베스트 프랙티스 점수
            metrics.best_practices_score = self._check_best_practices(tree)

            # 코드 스멀과 제안
            metrics.code_smells = self._detect_code_smells(tree)
            metrics.suggestions = self._generate_suggestions(metrics)

        except Exception as e:
            logger.error(f"코드 품질 분석 실패: {e}")

        return metrics

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """복잡도 계산 (McCabe 복잡도)"""
        complexity = 1  # 기본 복잡도

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _calculate_style_score(self, code: str) -> float:
        """스타일 점수 계산"""
        score = 100.0

        lines = code.split('\n')

        # 줄 길이 확인
        for line in lines:
            if len(line) > 100:  # 너무 긴 줄
                score -= 2

        # 불필요한 공백 확인
        for i, line in enumerate(lines):
            if line.rstrip() != line.rstrip('\n').rstrip():
                score -= 1

        # 빈 줄이 너무 많은 경우
        empty_line_count = sum(1 for line in lines if not line.strip())
        if empty_line_count > len(lines) * 0.3:
            score -= 5

        return max(0, score)

    def _calculate_readability_score(self, code: str) -> float:
        """가독성 점수 계산"""
        score = 100.0

        lines = code.split('\n')
        total_lines = len([l for l in lines if l.strip()])

        if total_lines == 0:
            return 0.0

        # 너무 긴 함수 확인
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 10
                if func_lines > 50:  # 너무 긴 함수
                    score -= 10

        # 주문 부족
        comment_ratio = len([l for l in lines if l.strip().startswith('#')]) / total_lines
        if comment_ratio < 0.1:  # 주석이 10% 미만
            score -= 5

        return max(0, score)

    def _check_best_practices(self, tree: ast.AST) -> float:
        """베스트 프랙티스 확인"""
        score = 100.0

        # docstring 확인
        has_docstring = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    has_docstring = True
                    break

        if not has_docstring:
            score -= 10

        # 전역 변수 사용 확인
        global_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Global)])
        if global_count > 0:
            score -= global_count * 5

        return max(0, score)

    def _detect_code_smells(self, tree: ast.AST) -> List[str]:
        """코드 스멀 감지"""
        smells = []

        # 너무 긴 함수
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    smells.append(f"함수 '{node.name}'이 너무 깁니다 ({func_lines}줄)")

        # 너무 많은 매개변수
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 5:
                    smells.append(f"함수 '{node.name}'에 매개변수가 너무 많습니다 ({len(node.args.args)}개)")

        return smells

    def _generate_suggestions(self, metrics: CodeQualityMetrics) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        if metrics.complexity_score < 70:
            suggestions.append("함수 복잡도를 낮추세요. 작은 함수로 분할하는 것을 고려해보세요.")

        if metrics.style_score < 70:
            suggestions.append("코드 스타일을 개선하세요. 줄 길이와 공백 사용을 확인하세요.")

        if metrics.readability_score < 70:
            suggestions.append("가독성을 높이세요. 주석을 추가하고 함수 길이를 줄이세요.")

        if metrics.comment_ratio < 0.1:
            suggestions.append("코드에 주석을 추가하세요.")

        if metrics.best_practices_score < 70:
            suggestions.append("베스트 프랙티스를 따르세요. docstring을 추가하고 전역 변수를 피하세요.")

        return suggestions

    def _generate_feedback(self, evaluation: EvaluationResult) -> str:
        """피드백 생성"""
        feedback_parts = []

        # 전체 성적
        pass_rate = (evaluation.passed_tests / evaluation.total_tests * 100) if evaluation.total_tests > 0 else 0

        if pass_rate == 100:
            feedback_parts.append("🎉 모든 테스트를 통과했습니다!")
        elif pass_rate >= 70:
            feedback_parts.append(f"👍 {pass_rate:.0f}%의 테스트를 통과했습니다. 좋은 시작입니다!")
        elif pass_rate >= 30:
            feedback_parts.append(f"📚 {pass_rate:.0f}%의 테스트를 통과했습니다. 개선이 필요합니다.")
        else:
            feedback_parts.append(f"💪 {pass_rate:.0f}%의 테스트를 통과했습니다. 코드를 다시 검토해보세요.")

        # 코드 품질 피드백
        if evaluation.code_quality:
            if evaluation.code_quality.complexity_score < 50:
                feedback_parts.append("⚠️  코드 복잡도가 높습니다. 함수를 분할해보세요.")

            if evaluation.code_quality.style_score < 50:
                feedback_parts.append("⚠️  코드 스타일을 개선해주세요.")

        # 개선 제안
        if evaluation.code_quality and evaluation.code_quality.suggestions:
            feedback_parts.append("\n개선 제안:")
            for suggestion in evaluation.code_quality.suggestions[:3]:  # 상위 3개만
                feedback_parts.append(f"• {suggestion}")

        return "\n".join(feedback_parts)

    def get_evaluation(self, evaluation_id: str) -> Optional[EvaluationResult]:
        """평가 결과 반환"""
        return self.evaluations.get(evaluation_id)

    def get_user_evaluations(self, user_id: int) -> List[EvaluationResult]:
        """사용자의 모든 평가 결과 반환"""
        return [e for e in self.evaluation_history if e.user_id == user_id]

    def get_problem_evaluations(self, problem_id: str) -> List[EvaluationResult]:
        """문제의 모든 평가 결과 반환"""
        return [e for e in self.evaluation_history if e.problem_id == problem_id]


# 전역 인스턴스
auto_evaluator = None


def get_auto_evaluator() -> AutoEvaluator:
    """자동 평가 시스템 인스턴스 반환"""
    global auto_evaluator
    if auto_evaluator is None:
        auto_evaluator = AutoEvaluator()
    return auto_evaluator


if __name__ == "__main__":
    # 자동 평가 시스템 테스트
    print("🧪 자동 평가 시스템 테스트")

    from .coding_problem import TestCase

    evaluator = AutoEvaluator()

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
            input_data=(-1, 1),
            expected_output=0,
            description="음수 포함"
        ),
        TestCase(
            test_id="tc3",
            input_data=(0, 0),
            expected_output=0,
            description="0 테스트"
        )
    ]

    # 정답 코드 테스트
    correct_code = """
def add_numbers(a, b):
    return a + b
"""

    print("\n✅ 정답 코드 테스트:")
    result = evaluator.evaluate_submission(
        problem_id="test_problem",
        user_id=1,
        code=correct_code,
        test_cases=test_cases
    )

    print(f"   상태: {result.status.value}")
    print(f"   점수: {result.score:.1f}/{result.max_score}")
    print(f"   통과: {result.passed_tests}/{result.total_tests}")
    print(f"   실행 시간: {result.execution_time:.3f}초")
    print(f"   피드백:\n{result.feedback}")

    # 오답 코드 테스트
    wrong_code = """
def add_numbers(a, b):
    return a - b
"""

    print("\n❌ 오답 코드 테스트:")
    result = evaluator.evaluate_submission(
        problem_id="test_problem",
        user_id=2,
        code=wrong_code,
        test_cases=test_cases
    )

    print(f"   상태: {result.status.value}")
    print(f"   점수: {result.score:.1f}/{result.max_score}")
    print(f"   통과: {result.passed_tests}/{result.total_tests}")

    # 코드 품질 분석 테스트
    print("\n📊 코드 품질 분석:")
    if result.code_quality:
        quality = result.code_quality
        print(f"   복잡도 점수: {quality.complexity_score:.1f}")
        print(f"   스타일 점수: {quality.style_score:.1f}")
        print(f"   가독성 점수: {quality.readability_score:.1f}")
        print(f"   베스트 프랙티스: {quality.best_practices_score:.1f}")
        print(f"   함수 수: {quality.function_count}")
        print(f"   줄 수: {quality.line_count}")

    print("\n🎉 자동 평가 시스템 테스트 완료!")