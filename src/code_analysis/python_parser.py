"""
Python 파서
AST 기반 Python 코드 파싱
"""
import ast
from typing import Dict, Any, List
from loguru import logger


class PythonParser:
    """Python AST 파서"""

    def __init__(self):
        logger.info("Python 파서 초기화 완료")

    def parse_code(self, code: str) -> Dict[str, Any]:
        """코드 파싱"""
        try:
            result = {
                "success": False,
                "ast": None,
                "errors": [],
                "warnings": [],
                "info": {}
            }

            # AST 파싱
            try:
                tree = ast.parse(code)
                result["ast"] = tree
                result["success"] = True

                # 기본 정보 추출
                result["info"] = self._extract_basic_info(tree, code)

            except SyntaxError as e:
                result["errors"].append({
                    "type": "SyntaxError",
                    "line": e.lineno,
                    "column": e.offset,
                    "message": e.msg
                })
                logger.warning(f"문법 오류 발생: {e.msg} (라인 {e.lineno})")

            except Exception as e:
                result["errors"].append({
                    "type": type(e).__name__,
                    "message": str(e)
                })
                logger.error(f"파싱 중 오류: {e}")

            return result

        except Exception as e:
            logger.error(f"파서 오류: {e}")
            return {
                "success": False,
                "ast": None,
                "errors": [str(e)],
                "warnings": [],
                "info": {}
            }

    def _extract_basic_info(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """기본 코드 정보 추출"""
        info = {
            "lines": len(code.split('\n')),
            "characters": len(code),
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "comments": 0
        }

        # AST 순회하며 정보 추출
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                info["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                info["classes"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                info["imports"] += 1

        # 주석 카운트 (간단 구현)
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                info["comments"] += 1

        return info

    def get_function_names(self, code: str) -> List[str]:
        """함수 이름 추출"""
        try:
            tree = ast.parse(code)
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

            return functions

        except Exception as e:
            logger.error(f"함 이름 추출 실패: {e}")
            return []

    def get_class_names(self, code: str) -> List[str]:
        """클래스 이름 추출"""
        try:
            tree = ast.parse(code)
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            return classes

        except Exception as e:
            logger.error(f"클래스 이름 추출 실패: {e}")
            return []

    def get_imports(self, code: str) -> List[str]:
        """임포트 목록 추출"""
        try:
            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            return imports

        except Exception as e:
            logger.error(f"임포트 추출 실패: {e}")
            return []