"""
복잡도 분석기
Cyclomatic Complexity 및 기타 복잡도 지표 분석
"""
import ast
from typing import Dict, Any, List
from loguru import logger


class ComplexityAnalyzer:
    """코드 복잡도 분석기"""

    def __init__(self):
        logger.info("복잡도 분석기 초기화 완료")

    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        """복잡도 분석 실행"""
        try:
            result = {
                "total_complexity": 0,
                "average_complexity": 0,
                "max_complexity": 0,
                "function_complexities": {},
                "complex_functions": [],
                "assessment": ""
            }

            # AST 파싱
            tree = ast.parse(code)

            # 함수별 복잡도 계산
            function_complexities = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    function_complexities[node.name] = complexity

                    result["total_complexity"] += complexity
                    result["max_complexity"] = max(result["max_complexity"], complexity)

            # 평균 복잡도 계산
            if function_complexities:
                result["average_complexity"] = result["total_complexity"] / len(function_complexities)
                result["function_complexities"] = function_complexities

            # 복잡한 함수 식별
            result["complex_functions"] = [
                name for name, complexity in function_complexities.items()
                if complexity > 10
            ]

            # 전체 평가
            result["assessment"] = self._assess_complexity(result)

            logger.info(f"복잡도 분석 완료: 평균={result['average_complexity']:.1f}")
            return result

        except Exception as e:
            logger.error(f"복잡도 분석 실패: {e}")
            return {
                "total_complexity": 0,
                "average_complexity": 0,
                "max_complexity": 0,
                "error": str(e)
            }

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Cyclomatic Complexity 계산"""
        complexity = 1  # 기본 복잡도

        for child in ast.walk(node):
            # 분기문별 복잡도 증가
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _assess_complexity(self, analysis_result: Dict[str, Any]) -> str:
        """복잡도 평가"""
        avg_complexity = analysis_result["average_complexity"]
        max_complexity = analysis_result["max_complexity"]

        if avg_complexity <= 5:
            return "코드 복잡도가 매우 낮습니다. 잘 작성되었습니다!"
        elif avg_complexity <= 10:
            return "코드 복잡도가 적절한 수준입니다."
        elif avg_complexity <= 15:
            return "코드 복잡도가 다소 높습니다. 함수를 더 작게 분리하는 것을 고려해보세요."
        else:
            return "코드 복잡도가 높습니다. 함수를 더 작게 분리하고 로직을 단순화하는 것을 권장합니다."

    def get_complexity_rating(self, complexity: int) -> str:
        """복잡도 등급 반환"""
        if complexity <= 5:
            return "낮음"
        elif complexity <= 10:
            return "보통"
        elif complexity <= 15:
            return "높음"
        else:
            return "매우 높음"