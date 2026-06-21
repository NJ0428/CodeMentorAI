"""
보안 체커
보안 취약점 검사
"""
import ast
import re
from typing import Dict, Any, List
from loguru import logger


class SecurityChecker:
    """보안 취약점 체커"""

    def __init__(self):
        self.dangerous_functions = [
            'eval', 'exec', 'compile', '__import__',
            'open', 'input', 'raw_input'
        ]

        self.dangerous_modules = [
            'os', 'subprocess', 'sys', 'pickle',
            'shutil', 'commands', 'pty'
        ]

        logger.info("보안 체커 초기화 완료")

    def check_security(self, code: str) -> Dict[str, Any]:
        """보안 검사 실행"""
        try:
            result = {
                "issues": [],
                "warnings": [],
                "risk_level": "low",
                "dangerous_calls": [],
                "hardcoded_secrets": [],
                "sql_injection_risks": []
            }

            # AST 파싱
            try:
                tree = ast.parse(code)

                # 위험한 함수 호출 검사
                self._check_dangerous_calls(tree, result)

                # 하드코딩된 시크릿 검사
                self._check_hardcoded_secrets(code, result)

                # SQL 인젝션 위험 검사
                self._check_sql_injection(code, result)

                # 위험 수준 결정
                result["risk_level"] = self._determine_risk_level(result)

            except SyntaxError:
                # 문법 오류가 있는 경우 기본 검사만 수행
                self._check_hardcoded_secrets(code, result)
                self._check_sql_injection(code, result)

            logger.info(f"보안 검사 완료: {len(result['issues'])}개 이슈 발견")
            return result

        except Exception as e:
            logger.error(f"보안 검사 실패: {e}")
            return {
                "issues": [],
                "error": str(e)
            }

    def _check_dangerous_calls(self, tree: ast.AST, result: Dict[str, Any]):
        """위험한 함수 호출 검사"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node)

                if func_name in self.dangerous_functions:
                    issue = {
                        "type": "dangerous_function",
                        "function": func_name,
                        "message": f"위험한 함수 사용: {func_name}",
                        "severity": "high" if func_name in ['eval', 'exec'] else "medium",
                        "recommendation": self._get_safe_alternative(func_name)
                    }
                    result["issues"].append(issue)
                    result["dangerous_calls"].append(issue)

                # 위험한 모듈의 함수 호출
                if func_name:
                    for module in self.dangerous_modules:
                        if func_name.startswith(f"{module}."):
                            result["issues"].append({
                                "type": "dangerous_module",
                                "function": func_name,
                                "message": f"위험한 모듈 함수 사용: {func_name}",
                                "severity": "medium",
                                "recommendation": f"안전한 대안을 고려하세요"
                            })

    def _check_hardcoded_secrets(self, code: str, result: Dict[str, Any]):
        """하드코딩된 시크릿 검사"""
        # API 키, 비밀번호, 토큰 패턴
        secret_patterns = [
            (r'(api_key|apikey|API_KEY|APIKEY)\s*=\s*["\']([^"\']{10,})["\']', "API Key"),
            (r'(password|passwd|PASSWORD)\s*=\s*["\']([^"\']{6,})["\']', "Password"),
            (r'(secret|token|SECRET)\s*=\s*["\']([^"\']{10,})["\']', "Secret/Token"),
            (r'(Bearer\s+|Authorization:\s+)([A-Za-z0-9\-._~+/]+=*)', "Bearer Token"),
        ]

        for pattern, secret_type in secret_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                issue = {
                    "type": "hardcoded_secret",
                    "secret_type": secret_type,
                    "message": f"하드코딩된 {secret_type}가 있습니다",
                    "severity": "high",
                    "recommendation": "환경 변수나 설정 파일을 사용하세요"
                }
                result["issues"].append(issue)
                result["hardcoded_secrets"].append(issue)

    def _check_sql_injection(self, code: str, result: Dict[str, Any]):
        """SQL 인젝션 위험 검사"""
        # SQL 쿼리 패턴
        sql_patterns = [
            r'(execute|executemany|cursor\.execute)\s*\(\s*["\'][^\"\']*%s[^\"\']*["\']',
            r'(execute|executemany)\s*\(\s*["\'][^\"\']*\\+[^\"\']*["\']',
            r'(execute|executemany)\s*\(\s*f["\'][^\"\']*\{[^}]*\}[^\"\']*["\']'
        ]

        for pattern in sql_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                issue = {
                    "type": "sql_injection",
                    "message": "SQL 인젝션 위험이 있습니다",
                    "severity": "high",
                    "recommendation": "파라미터화된 쿼리를 사용하세요"
                }
                result["issues"].append(issue)
                result["sql_injection_risks"].append(issue)

    def _get_function_name(self, node: ast.Call) -> str:
        """함수 이름 추출"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return f"{node.func.value.id}.{node.func.attr}" if hasattr(node.func.value, 'id') else str(node.func.attr)
        return ""

    def _get_safe_alternative(self, func_name: str) -> str:
        """안전한 대안 제안"""
        alternatives = {
            'eval': 'ast.literal_eval() 사용을 고려하세요',
            'exec': '필요한 기능만 수행하는 안전한 함수를 작성하세요',
            'open': '파일 경로를 검증하고 제한된 경로만 접근하세요',
            'input': '입력값을 검증하고 정제하세요'
        }
        return alternatives.get(func_name, "안전한 대안을 고려하세요")

    def _determine_risk_level(self, result: Dict[str, Any]) -> str:
        """위험 수준 결정"""
        high_issues = len([issue for issue in result["issues"] if issue.get("severity") == "high"])
        medium_issues = len([issue for issue in result["issues"] if issue.get("severity") == "medium"])

        if high_issues > 0:
            return "high"
        elif medium_issues > 2:
            return "medium"
        else:
            return "low"

    def get_security_recommendations(self, risk_level: str) -> List[str]:
        """보안 권장사항 반환"""
        recommendations = []

        if risk_level == "high":
            recommendations.extend([
                "위험한 함수 사용을 피하세요",
                "모든 사용자 입력을 검증하고 정제하세요",
                "파라미터화된 쿼리를 사용하세요",
                "시크릿 정보를 환경 변수로 관리하세요"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "사용자 입력 검증을 강화하세요",
                "코드 리뷰를 수행하세요"
            ])
        else:
            recommendations.append("현재 보안 위험이 낮습니다. 계속해서 모범 사례를 따르세요.")

        return recommendations