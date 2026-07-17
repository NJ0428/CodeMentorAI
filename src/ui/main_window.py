"""
메인 윈도우
Tkinter 기반 메인 애플리케이션 윈도우
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any
from loguru import logger

from src.config.settings import settings
from src.config.constants import APP_NAME, APP_VERSION
from src.core.engine import engine
from src.ui.components.code_editor import CodeEditor
from src.ui.components.learning_tab import LearningTab
from src.ui.components.enhanced_chat_tab import EnhancedChatTab
from src.ui.components.dashboard_tab import DashboardTab
from src.ui.components.resources_tab import ResourcesTab
from src.ui.styles.style_manager import get_style_manager


class MainWindow:
    """메인 윈도우 클래스"""

    def __init__(self):
        self.root = tk.Tk()
        
        self.style_manager = get_style_manager(self.root)
        
        self.root.title(f"{APP_NAME} v{APP_VERSION}")

        # 윈도우 크기 설정
        self.root.geometry(f"{settings.ui.window_width}x{settings.ui.window_height}")
        self.root.minsize(800, 600)
        
        self.style_manager.set_theme(settings.ui.theme)

        # 중앙 프레임 (메인 컨텐츠 영역)
        self.main_container = None
        self.sidebar = None
        self.content_area = None
        self.status_bar = None

        # 메뉴 바
        self._create_menu()

        # UI 컴포넌트 초기화
        self._initialize_ui()

        logger.info("메인 윈도우 초기화 완료")

    def _create_menu(self):
        """메뉴 바 생성"""
        menubar = tk.Menu(self.root)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Code", command=self.new_code)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_application)
        menubar.add_cascade(label="File", menu=file_menu)

        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # 보기 메뉴
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Sidebar", command=self.toggle_sidebar)
        view_menu.add_separator()

        theme_menu = tk.Menu(menubar, tearoff=0)
        self.theme_var = tk.StringVar(value=settings.ui.theme)
        theme_menu.add_radiobutton(label="Light", variable=self.theme_var, value="light", command=lambda: self.change_theme("light"))
        theme_menu.add_radiobutton(label="Dark", variable=self.theme_var, value="dark", command=lambda: self.change_theme("dark"))
        
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        view_menu.add_separator()
        view_menu.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="View", menu=view_menu)

        # 학습 메뉴
        learning_menu = tk.Menu(menubar, tearoff=0)
        learning_menu.add_command(label="Start Learning", command=self.start_learning)
        learning_menu.add_command(label="My Progress", command=self.show_progress)
        learning_menu.add_command(label="Achievements", command=self.show_achievements)
        menubar.add_cascade(label="Learning", menu=learning_menu)

        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def change_theme(self, theme_name):
        """테마 변경"""
        if settings.ui.theme != theme_name:
            settings.ui.theme = theme_name
            # In a real application, you might save this to a config file
            messagebox.showinfo("Theme Change", "The theme will be applied after restarting the application.")

    def _initialize_ui(self):
        """UI 컴포넌트 초기화"""
        colors = self.style_manager.get_current_theme_colors()
        self.root.configure(bg=colors["bg"])
        
        # 메인 컨테이너
        self.main_container = tk.Frame(self.root, bg=colors["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 사이드바
        self._create_sidebar()

        # 컨텐츠 영역
        self._create_content_area()

        # 상태 바
        self._create_status_bar()

    def _create_sidebar(self):
        """사이드바 생성"""
        colors = self.style_manager.get_current_theme_colors()
        self.sidebar = tk.Frame(self.main_container, width=200, bg=colors["bg_alt"])
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # 사이드바 내용
        tk.Label(self.sidebar, text="Navigation", bg=colors["bg_alt"], fg=colors["fg_alt"], font=("Arial", 12, "bold")).pack(pady=10)

        # 네비게이션 버튼들
        buttons = [
            ("Code Analysis", lambda: self.show_tab("code_analysis")),
            ("Learning", lambda: self.show_tab("learning")),
            ("Chat", lambda: self.show_tab("chat")),
            ("Dashboard", lambda: self.show_tab("dashboard")),
            ("Resources", lambda: self.show_tab("resources")),
            ("Progress", lambda: self.show_tab("progress"))
        ]

        for text, command in buttons:
            btn = tk.Button(self.sidebar, text=text, command=command, width=15, 
                           bg=colors["primary"], fg=colors["bg"], relief=tk.FLAT)
            btn.pack(pady=5)

    def _create_content_area(self):
        """컨텐츠 영역 생성"""
        colors = self.style_manager.get_current_theme_colors()
        self.content_area = tk.Frame(self.main_container, bg=colors["bg"])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 탭 노트북 생성
        self.notebook = ttk.Notebook(self.content_area)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 기본 탭들 생성
        self._create_code_analysis_tab()
        self._create_learning_tab()
        self._create_chat_tab()
        self._create_dashboard_tab()
        self._create_resources_tab()

    def _create_code_analysis_tab(self):
        """코드 분석 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text="Code Analysis")

        # 실제 코드 에디터 생성
        self.code_editor = CodeEditor(
            tab,
            self.style_manager,
            on_run=self.run_code,
            on_analyze=self.analyze_code
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)

        # 샘플 코드 로드
        sample_code = '''def hello_world():
    """Hello World 함수"""
    name = "World"
    print(f"Hello, {name}!")
    return name

if __name__ == "__main__":
    hello_world()
'''
        self.code_editor.set_code(sample_code)

    def _create_learning_tab(self):
        """학습 탭 생성"""
        # 학습 컨트롤러 가져오기
        learning_controller = None
        if hasattr(engine, 'get_learning_manager') and engine.get_learning_manager():
            learning_controller = engine.get_learning_manager()

        # LearningTab 생성
        self.learning_tab = LearningTab(self.notebook, learning_controller)
        self.notebook.add(self.learning_tab, text="📚 Learning")

    def _create_chat_tab(self):
        """채팅 탭 생성"""
        # 코드 컨텍스트 공유 콜백 함수
        def share_code_context():
            if hasattr(self, 'code_editor'):
                return self.code_editor.get_code()
            return None

        # 향상된 채팅 탭 생성
        self.chat_tab = EnhancedChatTab(
            self.notebook,
            on_code_share=share_code_context
        )
        self.notebook.add(self.chat_tab, text="💬 Chat")

    def _create_dashboard_tab(self):
        """시각화 대시보드 탭 생성"""
        # 학습 컨트롤러 가져오기
        learning_controller = None
        if hasattr(engine, 'get_learning_manager') and engine.get_learning_manager():
            learning_controller = engine.get_learning_manager()

        # DashboardTab 생성
        self.dashboard_tab = DashboardTab(self.notebook, learning_controller)
        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")

    def _create_resources_tab(self):
        """리소스 및 학습 자료 탭 생성"""
        # 학습 컨트롤러 가져오기
        learning_controller = None
        if hasattr(engine, 'get_learning_manager') and engine.get_learning_manager():
            learning_controller = engine.get_learning_manager()

        # ResourcesTab 생성
        self.resources_tab = ResourcesTab(self.notebook, learning_controller)
        self.notebook.add(self.resources_tab, text="📚 Resources")

    def _create_status_bar(self):
        """상태 바 생성"""
        colors = self.style_manager.get_current_theme_colors()
        self.status_bar = tk.Frame(self.root, relief=tk.SUNKEN, bg=colors["bg_alt"])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 상태 정보
        self.status_label = tk.Label(self.status_bar, text="Ready", anchor=tk.W, bg=colors["bg_alt"], fg=colors["fg_alt"])
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.progress_label = tk.Label(self.status_bar, text="Progress: 0%", anchor=tk.E, bg=colors["bg_alt"], fg=colors["fg_alt"])
        self.progress_label.pack(side=tk.RIGHT, padx=5)

    def update_status(self, message: str):
        """상태 메시지 업데이트"""
        self.status_label.config(text=message)

    def update_progress(self, progress: int):
        """진도 업데이트"""
        self.progress_label.config(text=f"Progress: {progress}%")

    def show_tab(self, tab_name: str):
        """특정 탭 표시"""
        # 나중에 구현
        logger.info(f"탭 전환 요청: {tab_name}")

    # 메뉴 커맨드 구현
    def new_code(self):
        """새 코드 생성"""
        logger.info("새 코드 생성")
        self.update_status("Creating new code...")

    def open_file(self):
        """파일 열기"""
        filetypes = [("Python Files", "*.py"), ("All Files", "*.*")]
        filename = filedialog.askopenfilename(filetypes=filetypes)

        if filename:
            logger.info(f"파일 열기: {filename}")
            self.update_status(f"Opened: {filename}")

    def save_file(self):
        """파일 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )

        if filename:
            logger.info(f"파일 저장: {filename}")
            self.update_status(f"Saved: {filename}")

    def export_data(self):
        """데이터 내보내기"""
        logger.info("데이터 내보내기")
        messagebox.showinfo("Export", "Export functionality coming soon!")

    def undo(self):
        """실행 취소"""
        logger.info("실행 취소")

    def redo(self):
        """재실행"""
        logger.info("재실행")

    def cut(self):
        """잘라내기"""
        logger.info("잘라내기")

    def copy(self):
        """복사"""
        logger.info("복사")

    def paste(self):
        """붙여넣기"""
        logger.info("붙여넣기")

    def toggle_sidebar(self):
        """사이드바 토글"""
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

    def open_settings(self):
        """설정 열기"""
        logger.info("설정 열기")
        messagebox.showinfo("Settings", "Settings dialog coming soon!")

    def start_learning(self):
        """학습 시작"""
        logger.info("학습 시작")
        self.update_status("Starting learning session...")

    def show_progress(self):
        """진도 표시"""
        logger.info("진도 표시")
        messagebox.showinfo("Progress", "Your learning progress: 45%")

    def show_achievements(self):
        """성취 표시"""
        logger.info("성취 표시")
        messagebox.showinfo("Achievements", "Achievements: 5 unlocked")

    def show_documentation(self):
        """문서 표시"""
        logger.info("문서 표시")
        messagebox.showinfo("Documentation", "Documentation coming soon!")

    def show_about(self):
        """정보 표시"""
        about_text = f"""
{APP_NAME} v{APP_VERSION}

Python 학습을 위한 AI 기반 멘토링 플랫폼

특징:
• AI 기반 코드 분석
• 실시간 멘토링
• 진도 추적
• 적응형 학습

개발자: {APP_AUTHOR}
        """
        messagebox.showinfo("About", about_text)

    def quit_application(self):
        """애플리케이션 종료"""
        if messagebox.askyesno("Exit", "정말 종료하시겠습니까?"):
            self.quit()

    def run_code(self, code: Optional[str] = None):
        """코드 실행"""
        try:
            if code is None:
                code = self.code_editor.get_code()

            if not code.strip():
                messagebox.showwarning("코드 실행", "실행할 코드가 없습니다.")
                return

            logger.info("코드 실행")
            self.update_status("Running code...")

            # 간단한 코드 실행
            import io
            import sys

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
                messagebox.showinfo("실행 결과", f"✅ 실행 성공!\n\n📄 출력:\n{output}")
                self.update_status(f"Code executed successfully! Output: {len(output)} chars")
            else:
                messagebox.showinfo("실행 결과", "✅ 코드가 성공적으로 실행되었습니다.\n(출력 없음)")
                self.update_status("Code executed successfully!")

            logger.info("코드 실행 성공")

        except Exception as e:
            error_msg = f"❌ 코드 실행 중 오류가 발생했습니다:\n\n{str(e)}"
            messagebox.showerror("실행 오류", error_msg)
            self.update_status(f"Execution error: {str(e)}")
            logger.error(f"코드 실행 실패: {e}")

    def analyze_code(self, code: Optional[str] = None):
        """코드 분석"""
        try:
            if code is None:
                code = self.code_editor.get_code()

            if not code.strip():
                messagebox.showwarning("코드 분석", "분석할 코드가 없습니다.")
                return

            logger.info("코드 분석")
            self.update_status("Analyzing code...")

            # 기본 분석 결과
            analysis = {
                "lines": len(code.split('\n')),
                "characters": len(code),
                "functions": code.count('def '),
                "classes": code.count('class '),
                "comments": code.count('#')
            }

            # 간단한 문법 체크
            try:
                import ast
                ast.parse(code)
                analysis["syntax"] = "✅ 문법 정상"
            except SyntaxError as e:
                analysis["syntax"] = f"❌ 문법 오류: {e.msg} (라인 {e.lineno})"

            # 결과 메시지 생성
            result_msg = f"""📊 코드 분석 결과

📏 길이: {analysis['lines']} 라인 ({analysis['characters']} 문자)
🔧 함수: {analysis['functions']}개
🏗️  클래스: {analysis['classes']}개
💬 주석: {analysis['comments']}개
📝 문법: {analysis['syntax']}

💡 팁: 더 상세한 분석을 위해 Claude API를 설정하세요!"""

            messagebox.showinfo("코드 분석 완료", result_msg)
            self.update_status("Analysis complete!")
            logger.info("코드 분석 완료")

        except Exception as e:
            error_msg = f"코드 분석 중 오류가 발생했습니다:\n\n{str(e)}"
            messagebox.showerror("분석 오류", error_msg)
            self.update_status(f"Analysis error: {str(e)}")
            logger.error(f"코드 분석 실패: {e}")

    def debug_code(self):
        """코드 디버그"""
        logger.info("코드 디버그")
        self.update_status("Debugging code...")

    def run(self):
        """메인 루프 시작"""
        try:
            logger.info("애플리케이션 시작")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"애플리케이션 실행 중 오류: {e}")
            raise

    def quit(self):
        """애플리케이션 종료"""
        try:
            logger.info("애플리케이션 종료 시작")

            # 엔진 종료
            if hasattr(engine, 'shutdown'):
                engine.shutdown()

            # 윈도우 종료
            self.root.quit()
            self.root.destroy()

            logger.info("애플리케이션 종료 완료")

        except Exception as e:
            logger.error(f"애플리케이션 종료 중 오류: {e}")


if __name__ == "__main__":
    # 메인 윈도우 테스트
    try:
        window = MainWindow()
        window.run()
    except Exception as e:
        logger.error(f"메인 윈도우 실행 실패: {e}")