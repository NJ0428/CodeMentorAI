"""
코드 에디터 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from src.ui.components.code_editor import CodeEditor

def main():
    """메인 함수"""
    root = tk.Tk()
    root.title("Code Editor Test")
    root.geometry("900x700")

    # 코드 에디터 생성
    editor = CodeEditor(root)

    # 샘플 코드
    sample_code = '''def calculate_sum(a, b):
    """두 수의 합을 계산하는 함수"""
    result = a + b
    print(f"{a} + {b} = {result}")
    return result

def main():
    """메인 함수"""
    numbers = [1, 2, 3, 4, 5]
    total = 0

    for num in numbers:
        total += num

    print(f"Total: {total}")
    return total

if __name__ == "__main__":
    # 테스트
    sum_result = calculate_sum(10, 20)
    main_result = main()

    print(f"Sum Result: {sum_result}")
    print(f"Main Result: {main_result}")
'''

    editor.set_code(sample_code)
    editor.pack(fill=tk.BOTH, expand=True)

    # 종료 핸들러
    def on_closing():
        print("코드 에디터 테스트 종료")
        code = editor.get_code()
        print(f"코드 길이: {len(code)} 문자")
        print(f"라인 수: {len(code.split(chr(10)))} 라인")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    print("=== 코드 에디터 테스트 시작 ===")
    print("기능:")
    print("- 📁 파일 열기/저장")
    print("- ▶️ 코드 실행 (F5 또는 Ctrl+Enter)")
    print("- 🔍 코드 분석")
    print("- 🎨 문법 하이라이팅 (Pygments)")
    print("- 📝 라인 번호 및 상태 바")
    print("\n시작...")

    root.mainloop()

if __name__ == "__main__":
    main()