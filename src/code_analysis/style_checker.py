"""
스타일 체커
PEP8 스타일 가이드 준수 확인
"""
from typing import Dict, Any, List
from loguru import logger
import re


class StyleChecker:
    """PEP8 스타일 체커"""

    def __init__(self):
        logger.info("스타일 체커 초기화 완료")

    def check_style(self, code: str) -> Dict[str, Any]:
        """스타일 검사 실행"""
        try:
            result = {
                "issues": [],
                "warnings": [],
                "score": 0,
                "line_length_issues": [],
                "naming_issues": [],
                "whitespace_issues": []
            }

            lines = code.split('\n')

            # 라인 길이 검사
            self._check_line_length(lines, result)

            # 네이밍 컨벤션 검사
            self._check_naming_convention(code, result)

            # 공백 검사
            self._check_whitespace(code, result)

            # import 스타일 검사
            self._check_import_style(code, result)

            # 점수 계산
            total_issues = len(result["issues"])
            result["score"] = max(0, 10 - total_issues * 0.5)

            logger.info(f"스타일 검사 완료: {total_issues}개 이슈 발견")
            return result

        except Exception as e:
            logger.error(f"스타일 검사 실패: {e}")
            return {
                "issues": [],
                "error": str(e)
            }

    def _check_line_length(self, lines: List[str], result: Dict[str, Any]):
        """라인 길이 검사 (79자 권장)"""
        max_line_length = 79

        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                issue = {
                    "line": i,
                    "type": "line_too_long",
                    "message": f"라인이 너무 깁니다 ({len(line)} > {max_line_length})",
                    "severity": "low"
                }
                result["issues"].append(issue)
                result["line_length_issues"].append(issue)

    def _check_naming_convention(self, code: str, result: Dict[str, Any]):
        """네이밍 컨벤션 검사"""
        # 함수명: snake_case
        function_pattern = r'def\s+([a-z_][a-z0-9_]*)\s*\('
        # 클래스명: CapWords (PascalCase)
        class_pattern = r'class\s+([A-Z][a-zA-Z0-9]*)\s*:'
        # 변수명: snake_case
        variable_pattern = r'([a-z_][a-z0-9_]*)\s*='

        # 함수명 검사
        for match in re.finditer(function_pattern, code):
            func_name = match.group(1)
            if not self._is_snake_case(func_name):
                result["issues"].append({
                    "type": "naming_convention",
                    "message": f"함수명은 snake_case로 작성해야 합니다: {func_name}",
                    "severity": "low"
                })

        # 클래스명 검사
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            if not self._is_cap_words(class_name):
                result["issues"].append({
                    "type": "naming_convention",
                    "message": f"클래스명은 CapWords(PascalCase)로 작성해야 합니다: {class_name}",
                    "severity": "low"
                })

    def _check_whitespace(self, code: str, result: Dict[str, Any]):
        """공백 검사"""
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # trailing whitespace 검사
            if line.rstrip() != line.rstrip('\n').rstrip():
                result["issues"].append({
                    "line": i,
                    "type": "trailing_whitespace",
                    "message": "불필요한 trailing whitespace가 있습니다",
                    "severity": "low"
                })
                result["whitespace_issues"].append({
                    "line": i,
                    "message": "불필요한 trailing whitespace"
                })

            # tab 대 space 검사
            if '\t' in line:
                result["issues"].append({
                    "line": i,
                    "type": "tab_instead_of_spaces",
                    "message": "탭 대신 4개의 공백을 사용하세요",
                    "severity": "low"
                })

    def _check_import_style(self, code: str, result: Dict[str, Any]):
        """import 스타일 검사"""
        lines = code.split('\n')

        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append((i, stripped))

        # import는 파일 상단에 위치해야 함
        if len(import_lines) > 0:
            last_import_line = import_lines[-1][0]
            total_lines = len(lines)

            # import 후 코드 라인 확인
            for i in range(last_import_line, total_lines):
                if i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#'):
                    # import 후 첫 번째 코드 라인
                    if i - last_import_line > 2:
                        result["issues"].append({
                            "line": last_import_line + 1,
                            "type": "import_placement",
                            "message": "import 문들은 파일 상단에 배치하세요",
                            "severity": "low"
                        })
                    break

    def _is_snake_case(self, name: str) -> bool:
        """snake_case 확인"""
        return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))

    def _is_cap_words(self, name: str) -> bool:
        """CapWords(PascalCase) 확인"""
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))