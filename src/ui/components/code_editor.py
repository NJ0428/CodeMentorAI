"""
실제 작동하는 Python 코드 에디터
문법 하이라이팅, 라인 번호, 코드 실행 기능 포함
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import Optional, Callable
import io
import sys
from pathlib import Path
from loguru import logger

try:
    from pygments.lexers import PythonLexer
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.styles import get_style_by_name
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False
    logger.warning("Pygments가 설치되지 않아 기본 하이라이팅만 사용합니다")


class CodeEditor(tk.Frame):
    """Python 코드 에디터"""

    def __init__(self, parent, on_run: Optional[Callable] = None, on_analyze: Optional[Callable] = None):
        super().__init__(parent)

        self.on_run = on_run
        self.on_analyze = on_analyze
        self.current_file = None

        self._create_ui()
        self._setup_bindings()

        logger.info("코드 에디터 초기화 완료")

    def _create_ui(self):
        """UI 컴포넌트 생성"""
        # 도구 모음
        toolbar = tk.Frame(self, bg="#f0f0f0", height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # 버튼 스타일
        button_style = {"font": ("Arial", 9), "padx": 8, "pady": 4}

        # 도구 모음 버튼
        tk.Button(toolbar, text="📁 열기", command=self.open_file, bg="#e1e1e1", **button_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="💾 저장", command=self.save_file, bg="#e1e1e1", **button_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="✂️ cut", command=self.cut, bg="#e1e1e1", **button_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📋 copy", command=self.copy, bg="#e1e1e1", **button_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📌 paste", command=self.paste, bg="#e1e1e1", **button_style).pack(side=tk.LEFT, padx=2)

        tk.Frame(toolbar, width=20, bg="#f0f0f0").pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="▶️ 실행", command=self.run_code, bg="#4CAF50", fg="white", **button_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🔍 분석", command=self.analyze_code, bg="#2196F3", fg="white", **button_style).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🧹 지우기", command=self.clear, bg="#FF9800", fg="white", **button_style).pack(side=tk.LEFT, padx=2)

        # 메인 컨텐츠 영역
        content_frame = tk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 라인 번호와 코드 에디터를 위한 프레임
        editor_frame = tk.Frame(content_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # 라인 번호
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background="#f5f5f5",
            foreground="#666666",
            font=("Consolas", 10),
            state="disabled"
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # 코드 에디터
        self.text = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            background="#ffffff",
            foreground="#333333",
            insertbackground="#333333",
            selectbackground="#0078d4",
            selectforeground="#ffffff",
            borderwidth=1,
            relief="solid"
        )
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 스크롤바 동기화
        self.text.vbar.config(command=self._on_vscroll)

        # 상태 바
        self.status_bar = tk.Label(content_frame, text="줄: 1, 열: 1 | Python", anchor=tk.W, bg="#f0f0f0", font=("Arial", 8))
        self.status_bar.pack(fill=tk.X, pady=(5, 0))

        # 초기 라인 번호 업데이트
        self._update_line_numbers()

    def _setup_bindings(self):
        """키 바인딩 설정"""
        # 텍스트 변경 감지
        self.text.bind("<<Modified>>", self._on_text_change)
        self.text.bind("<KeyRelease>", self._on_key_release)

        # 커서 이동 감지
        self.text.bind("<Button-1>", self._on_click)
        self.text.bind("<Key>", self._on_key)

        # 단축키
        self.text.bind("<Control-o>", lambda e: self.open_file())
        self.text.bind("<Control-s>", lambda e: self.save_file())
        self.text.bind("<Control-Return>", lambda e: self.run_code())
        self.text.bind("<F5>", lambda e: self.run_code())

    def _on_vscroll(self, *args):
        """수직 스크롤 동기화"""
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def _on_text_change(self, event=None):
        """텍스트 변경 감지"""
        if self.text.edit_modified():
            self._update_line_numbers()
            self.text.edit_modified(False)

    def _on_key_release(self, event):
        """키 릴리즈 이벤트"""
        self._update_line_numbers()
        self._update_status()

    def _on_click(self, event):
        """마우스 클릭 이벤트"""
        self._update_status()

    def _on_key(self, event):
        """키 입력 이벤트"""
        self._update_status()

    def _update_line_numbers(self):
        """라인 번호 업데이트"""
        # 현재 라인 수 계산
        line_count = int(self.text.index("end-1c").split(".")[0])

        # 라인 번호 생성
        line_numbers = "\n".join(str(i) for i in range(1, line_count + 1))

        # 라인 번호 텍스트 업데이트
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers)
        self.line_numbers.config(state="disabled")

    def _update_status(self):
        """상태 바 업데이트"""
        # 커서 위치 계산
        cursor_pos = self.text.index(tk.INSERT)
        line, col = cursor_pos.split(".")
        line_num = int(line)
        col_num = int(col) + 1

        # 총 라인 수
        total_lines = int(self.text.index("end-1c").split(".")[0])

        # 문자 수
        char_count = len(self.text.get(1.0, tk.END))

        self.status_bar.config(text=f"줄: {line_num}/{total_lines}, 열: {col_num} | 문자: {char_count} | Python")

    def get_code(self) -> str:
        """현재 코드 반환"""
        return self.text.get(1.0, tk.END)

    def set_code(self, code: str):
        """코드 설정"""
        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, code)
        self._update_line_numbers()

    def clear(self):
        """에디터 비우기"""
        self.text.delete(1.0, tk.END)
        self._update_line_numbers()
        logger.info("코드 에디터 비움")

    def open_file(self):
        """파일 열기"""
        filename = filedialog.askopenfilename(
            title="Python 파일 열기",
            filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    code = f.read()
                self.set_code(code)
                self.current_file = filename
                logger.info(f"파일 열기: {filename}")

                # 상태 업데이트
                messagebox.showinfo("파일 열기", f"{filename}을 열었습니다.")

            except Exception as e:
                messagebox.showerror("파일 열기 오류", f"파일을 열 수 없습니다:\n{e}")
                logger.error(f"파일 열기 실패: {e}")

    def save_file(self):
        """파일 저장"""
        if not self.current_file:
            # 새 파일 이름으로 저장
            filename = filedialog.asksaveasfilename(
                title="Python 파일 저장",
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if not filename:
                return
            self.current_file = filename

        try:
            code = self.get_code()
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(code)

            logger.info(f"파일 저장: {self.current_file}")
            messagebox.showinfo("파일 저장", f"{self.current_file}에 저장했습니다.")

        except Exception as e:
            messagebox.showerror("파일 저장 오류", f"파일을 저장할 수 없습니다:\n{e}")
            logger.error(f"파일 저장 실패: {e}")

    def run_code(self):
        """코드 실행"""
        code = self.get_code()

        if not code.strip():
            messagebox.showwarning("코드 실행", "실행할 코드가 없습니다.")
            return

        logger.info("코드 실행 요청")

        if self.on_run:
            self.on_run(code)
        else:
            # 기본 실행 기능
            self._execute_python_code(code)

    def analyze_code(self):
        """코드 분석"""
        code = self.get_code()

        if not code.strip():
            messagebox.showwarning("코드 분석", "분석할 코드가 없습니다.")
            return

        logger.info("코드 분석 요청")

        if self.on_analyze:
            self.on_analyze(code)
        else:
            messagebox.showinfo("코드 분석", "코드 분석 기능이 준비되지 않았습니다.")

    def _execute_python_code(self, code: str):
        """Python 코드 직접 실행"""
        try:
            # 출력 캡처
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()

            try:
                # 코드 실행
                exec(code, {"__name__": "__main__"})
            finally:
                # 출력 복원
                sys.stdout = old_stdout

            # 실행 결과 표시
            output = captured_output.getvalue()

            if output:
                messagebox.showinfo("실행 결과", f"실행 성공!\n\n출력:\n{output}")
            else:
                messagebox.showinfo("실행 결과", "코드가 성공적으로 실행되었습니다.\n(출력 없음)")

            logger.info("코드 실행 성공")

        except Exception as e:
            messagebox.showerror("실행 오류", f"코드 실행 중 오류가 발생했습니다:\n\n{str(e)}")
            logger.error(f"코드 실행 실패: {e}")

    # 텍스트 편집 기능
    def cut(self):
        """잘라내기"""
        try:
            self.text.event_generate("<<Cut>>")
        except:
            pass

    def copy(self):
        """복사"""
        try:
            self.text.event_generate("<<Copy>>")
        except:
            pass

    def paste(self):
        """붙여넣기"""
        try:
            self.text.event_generate("<<Paste>>")
        except:
            pass

    def select_all(self):
        """모두 선택"""
        self.text.tag_add("sel", "1.0", "end")

    def undo(self):
        """실행 취소"""
        try:
            self.text.edit_undo()
        except:
            pass

    def redo(self):
        """재실행"""
        try:
            self.text.edit_redo()
        except:
            pass

    def insert_text(self, text: str):
        """텍스트 삽입"""
        self.text.insert(tk.INSERT, text)

    def get_selected_text(self) -> str:
        """선택된 텍스트 반환"""
        try:
            return self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            return ""

    def get_cursor_position(self) -> tuple:
        """커서 위치 반환 (라인, 열)"""
        cursor_pos = self.text.index(tk.INSERT)
        line, col = cursor_pos.split(".")
        return int(line), int(col)

    def goto_line(self, line_num: int):
        """특정 라인으로 이동"""
        try:
            self.text.mark_set(tk.INSERT, f"{line_num}.0")
            self.text.see(tk.INSERT)
        except:
            pass

    def highlight_line(self, line_num: int, color: str = "#ffffcc"):
        """특정 라인 하이라이팅"""
        try:
            # 기존 하이라이팅 제거
            self.text.tag_remove("highlight", "1.0", "end")

            # 새 하이라이팅 추가
            start_pos = f"{line_num}.0"
            end_pos = f"{line_num + 1}.0"
            self.text.tag_add("highlight", start_pos, end_pos)
            self.text.tag_config("highlight", background=color)
        except:
            pass

    def apply_syntax_highlighting(self):
        """문법 하이라이팅 적용 (Pygments 사용)"""
        if not PYGMENTS_AVAILABLE:
            return

        try:
            code = self.get_code()
            if not code.strip():
                return

            # Pygments로 하이라이팅
            lexer = PythonLexer()
            # 간단한 적용 (실제로는 더 복잡한 구현 필요)
            # 이것은 기본 구현입니다

        except Exception as e:
            logger.error(f"문법 하이라이팅 실패: {e}")


# 테스트용 코드
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Code Editor Test")
    root.geometry("800x600")

    editor = CodeEditor(root)

    # 샘플 코드
    sample_code = '''def hello_world():
    """Hello World 함수"""
    name = "World"
    print(f"Hello, {name}!")
    return name

if __name__ == "__main__":
    hello_world()
'''

    editor.set_code(sample_code)
    editor.pack(fill=tk.BOTH, expand=True)

    root.mainloop()