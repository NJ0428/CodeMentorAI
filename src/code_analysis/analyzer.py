"""
코드 분석 메인 모듈
통합 코드 분석 시스템
"""
from typing import Dict, Any, List
from loguru import logger
import ast

from src.code_analysis.python_parser import PythonParser
from src.code_analysis.complexity_analyzer import ComplexityAnalyzer
from src.code_analysis.style_checker import StyleChecker
from src.code_analysis.security_checker import SecurityChecker


class CodeAnalyzer:
    """통합 코드 분석 시스템"""

    def __init__(self):
        self.python_parser = PythonParser()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.style_checker = StyleChecker()
        self.security_checker = SecurityChecker()

        logger.info("코드 분석기 초기화 완료")

    def analyze_code(
        self,
        code: str,
        user_level: str = "beginner",
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """코드 분석 실행"""
        try:
            logger.info(f"코드 분석 시작 (유형: {analysis_type}, 수준: {user_level})")

            result = {
                "code": code,
                "user_level": user_level,
                "analysis_type": analysis_type,
                "success": False,
                "errors": [],
                "warnings": [],
                "score": 0,
                "issues": [],
                "suggestions": [],
                "strengths": []
            }

            # 1. 기본 파싱
            try:
                parsed_result = self.python_parser.parse_code(code)
                result["parsed"] = parsed_result["success"]
                if not parsed_result["success"]:
                    result["errors"].extend(parsed_result["errors"])
                    logger.warning("코드 파싱 실패")
                    return result
            except Exception as e:
                result["errors"].append(f"파싱 오류: {str(e)}")
                logger.error(f"코드 파싱 중 오류: {e}")
                return result

            # 2. 분석 유형에 따른 검사 실행
            if analysis_type in ["full", "syntax"]:
                syntax_result = self._check_syntax(code)
                result["syntax"] = syntax_result

            if analysis_type in ["full", "style"]:
                style_result = self.style_checker.check_style(code)
                result["style"] = style_result
                result["issues"].extend(style_result.get("issues", []))

            if analysis_type in ["full", "complexity"]:
                complexity_result = self.complexity_analyzer.analyze_complexity(code)
                result["complexity"] = complexity_result

                # 복잡도가 높은 경우 경고
                if complexity_result.get("average_complexity", 0) > 10:
                    result["warnings"].append("코드의 복잡도가 높습니다. 함수를 분리하세요.")

            if analysis_type in ["full", "security"]:
                security_result = self.security_checker.check_security(code)
                result["security"] = security_result
                result["issues"].extend(security_result.get("issues", []))

            # 3. 전체 점수 계산
            result["score"] = self._calculate_score(result, user_level)

            # 4. 제안사항 생성
            result["suggestions"] = self._generate_suggestions(result, user_level)

            # 5. 강점 추출
            result["strengths"] = self._identify_strengths(result)

            result["success"] = True
            logger.info(f"코드 분석 완료: 점수={result['score']}/10")

            return result

        except Exception as e:
            logger.error(f"코드 분석 중 오류: {e}")
            result["errors"].append(f"분석 오류: {str(e)}")
            return result

    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """문법 검사"""
        try:
            result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }

            # AST 파싱으로 문법 확인
            ast.parse(code)

            return result

        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [{
                    "line": e.lineno,
                    "column": e.offset,
                    "message": e.msg,
                    "severity": "critical"
                }],
                "warnings": []
            }

    def _calculate_score(self, analysis_result: Dict[str, Any], user_level: str) -> int:
        """코드 점수 계산"""
        score = 10

        # 문법 오류
        syntax_errors = len(analysis_result.get("errors", []))
        if syntax_errors > 0:
            score -= min(syntax_errors * 2, 5)

        # 스타일 이슈
        style_issues = len(analysis_result.get("style", {}).get("issues", []))
        if style_issues > 0:
            score -= min(style_issues * 0.5, 2)

        # 보안 이슈
        security_issues = len(analysis_result.get("security", {}).get("issues", []))
        if security_issues > 0:
            score -= min(security_issues * 1, 3)

        # 복잡도
        complexity = analysis_result.get("complexity", {}).get("average_complexity", 0)
        if complexity > 15:
            score -= 1
        elif complexity > 10:
            score -= 0.5

        # 최소 점수 보장
        return max(1, min(10, int(score)))

    def _generate_suggestions(self, analysis_result: Dict[str, Any], user_level: str) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        # 사용자 수준에 따른 제안
        if user_level == "beginner":
            suggestions.extend([
                "코드를 더 작은 함수로 분리해보세요.",
                "변수명을 더 명확하게 지어보세요.",
                "주석을 추가하여 코드를 설명해보세요."
            ])
        elif user_level == "intermediate":
            suggestions.extend([
                "예외 처리를 추가해보세요.",
                "타입 힌트를 사용해보세요.",
                "테스트 코드를 작성해보세요."
            ])
        elif user_level == "advanced":
            suggestions.extend([
                "디자인 패턴을 적용해보세요.",
                "성능 최적화를 고려해보세요.",
                "문서화를 강화해보세요."
            ])

        # 분석 결과에 따른 제안
        complexity = analysis_result.get("complexity", {}).get("average_complexity", 0)
        if complexity > 10:
            suggestions.append("복잡한 로직을 별도 함수로 분리하세요.")

        style_issues = analysis_result.get("style", {}).get("issues", [])
        if len(style_issues) > 5:
            suggestions.append("PEP8 스타일 가이드를 따르도록 코드를 수정하세요.")

        return suggestions

    def _identify_strengths(self, analysis_result: Dict[str, Any]) -> List[str]:
        """코드 강점 식별"""
        strengths = []

        # 문법이 정확한 경우
        if len(analysis_result.get("errors", [])) == 0:
            strengths.append("문법적으로 올바른 코드입니다.")

        # 보안 이슈가 없는 경우
        security_issues = len(analysis_result.get("security", {}).get("issues", []))
        if security_issues == 0:
            strengths.append("보안 취약점이 없습니다.")

        # 복잡도가 적절한 경우
        complexity = analysis_result.get("complexity", {}).get("average_complexity", 0)
        if complexity <= 10:
            strengths.append("적절한 복잡도를 유지하고 있습니다.")

        # 스타일 이슈가 적은 경우
        style_issues = len(analysis_result.get("style", {}).get("issues", []))
        if style_issues <= 2:
            strengths.append("좋은 코드 스타일을 유지하고 있습니다.")

        return strengths if strengths else ["코드를 작성해 주셔서 감사합니다! 계속 노력해주세요."]


# 전역 분석기 인스턴스
code_analyzer = None


def get_code_analyzer() -> CodeAnalyzer:
    """분석기 인스턴스 반환"""
    global code_analyzer
    if code_analyzer is None:
        code_analyzer = CodeAnalyzer()
    return code_analyzer


if __name__ == "__main__":
    # 분석기 테스트
    try:
        analyzer = get_code_analyzer()

        test_code = """
def hello_world():
    print("Hello, World!")
    x = 10
    return x
"""

        result = analyzer.analyze_code(test_code, user_level="beginner")
        print("✅ 코드 분석 테스트 완료")
        print(f"  점수: {result['score']}/10")
        print(f"  강점: {result['strengths']}")
        print(f"  제안: {result['suggestions']}")

    except Exception as e:
        print(f"❌ 분석기 테스트 실패: {e}")