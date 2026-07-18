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
from src.ui.language_manager import get_translator
from src.ui.shortcut_manager import get_shortcut_manager
import os

_ = get_translator()


class MainWindow:
    """메인 윈도우 클래스"""

    def __init__(self):
        self.root = tk.Tk()
        
        self.style_manager = get_style_manager(self.root)
        
        resources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        self.shortcut_manager = get_shortcut_manager(resources_path)
        
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

        logger.info(_("메인 윈도우 초기화 완료"))

    def _create_menu(self):
        """메뉴 바 생성"""
        menubar = tk.Menu(self.root)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=_("New Code"), command=self.new_code)
        file_menu.add_command(label=_("Open"), command=self.open_file, accelerator=self.shortcut_manager.get_shortcut("file.open"))
        file_menu.add_command(label=_("Save"), command=self.save_file, accelerator=self.shortcut_manager.get_shortcut("file.save"))
        file_menu.add_separator()
        file_menu.add_command(label=_("Export"), command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label=_("Exit"), command=self.quit_application)
        menubar.add_cascade(label=_("File"), menu=file_menu)

        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label=_("Undo"), command=self.undo)
        edit_menu.add_command(label=_("Redo"), command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label=_("Cut"), command=self.cut)
        edit_menu.add_command(label=_("Copy"), command=self.copy)
        edit_menu.add_command(label=_("Paste"), command=self.paste)
        menubar.add_cascade(label=_("Edit"), menu=edit_menu)

        # 보기 메뉴
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label=_("Toggle Sidebar"), command=self.toggle_sidebar)
        view_menu.add_separator()

        theme_menu = tk.Menu(menubar, tearoff=0)
        self.theme_var = tk.StringVar(value=settings.ui.theme)
        theme_menu.add_radiobutton(label=_("Light"), variable=self.theme_var, value="light", command=lambda: self.change_theme("light"))
        theme_menu.add_radiobutton(label=_("Dark"), variable=self.theme_var, value="dark", command=lambda: self.change_theme("dark"))
        
        view_menu.add_cascade(label=_("Theme"), menu=theme_menu)
        
        language_menu = tk.Menu(menubar, tearoff=0)
        self.language_var = tk.StringVar(value=settings.ui.language)
        language_menu.add_radiobutton(label=_("English"), variable=self.language_var, value="en", command=lambda: self.change_language("en"))
        language_menu.add_radiobutton(label=_("Korean"), variable=self.language_var, value="ko", command=lambda: self.change_language("ko"))
        view_menu.add_cascade(label=_("Language"), menu=language_menu)

        view_menu.add_separator()
        view_menu.add_command(label=_("Customize Shortcuts"), command=self.open_shortcut_settings)
        view_menu.add_separator()
        view_menu.add_command(label=_("Settings"), command=self.open_settings)
        menubar.add_cascade(label=_("View"), menu=view_menu)

        # 학습 메뉴
        learning_menu = tk.Menu(menubar, tearoff=0)
        learning_menu.add_command(label=_("Start Learning"), command=self.start_learning)
        learning_menu.add_command(label=_("My Progress"), command=self.show_progress)
        learning_menu.add_command(label=_("Achievements"), command=self.show_achievements)
        menubar.add_cascade(label=_("Learning"), menu=learning_menu)

        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=_("Documentation"), command=self.show_documentation)
        help_menu.add_command(label=_("About"), command=self.show_about)
        menubar.add_cascade(label=_("Help"), menu=help_menu)

        self.root.config(menu=menubar)

    def open_shortcut_settings(self):
        """단축키 설정 열기"""
        from src.ui.components.shortcut_editor import ShortcutEditor
        ShortcutEditor(self.root, self.shortcut_manager)

    def change_theme(self, theme_name):
        """테마 변경"""
        if settings.ui.theme != theme_name:
            settings.ui.theme = theme_name
            # In a real application, you might save this to a config file
            messagebox.showinfo(_("Theme Change"), _("The theme will be applied after restarting the application."))


    def change_language(self, lang_code):
        """언어 변경"""
        if settings.ui.language != lang_code:
            settings.ui.language = lang_code
            messagebox.showinfo(_("Language Change"), _("The language will be applied after restarting the application."))

    def _initialize_ui(self):
        """UI 컴포넌트 초기화"""
        colors = self.style_manager.get_current_theme_colors()
        self.root.configure(bg=colors["bg"])
        
        # 메인 컨테이너
        self.main_container = tk.Frame(self.root, bg=colors["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

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
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.pack_propagate(False)

        # 사이드바 내용
        tk.Label(self.sidebar, text=_("Navigation"), bg=colors["bg_alt"], fg=colors["fg_alt"], font=("Arial", 12, "bold")).pack(pady=10)

        # 네비게이션 버튼들
        buttons = [
            (_("Code Analysis"), lambda: self.show_tab("code_analysis")),
            (_("Learning"), lambda: self.show_tab("learning")),
            (_("Chat"), lambda: self.show_tab("chat")),
            (_("Dashboard"), lambda: self.show_tab("dashboard")),
            (_("Resources"), lambda: self.show_tab("resources")),
            (_("Progress"), lambda: self.show_tab("progress"))
        ]

        for text, command in buttons:
            btn = tk.Button(self.sidebar, text=text, command=command, width=15, 
                           bg=colors["primary"], fg=colors["bg"], relief=tk.FLAT)
            btn.pack(pady=5)

    def _create_content_area(self):
        """컨텐츠 영역 생성"""
        colors = self.style_manager.get_current_theme_colors()
        self.content_area = tk.Frame(self.main_container, bg=colors["bg"])
        self.content_area.grid(row=0, column=1, sticky="nsew")


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
        self.notebook.add(tab, text=_("Code Analysis"))

        # 실제 코드 에디터 생성
        self.code_editor = CodeEditor(
            tab,
            self.style_manager,
            self.shortcut_manager,
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
        self.learning_tab = LearningTab(self.notebook, self.style_manager, learning_controller)
        self.notebook.add(self.learning_tab, text=_("📚 Learning"))

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
            self.style_manager,
            self.shortcut_manager,
            on_code_share=share_code_context
        )
        self.notebook.add(self.chat_tab, text=_("💬 Chat"))

    def _create_dashboard_tab(self):
        """시각화 대시보드 탭 생성"""
        # 학습 컨트롤러 가져오기
        learning_controller = None
        if hasattr(engine, 'get_learning_manager') and engine.get_learning_manager():
            learning_controller = engine.get_learning_manager()

        # DashboardTab 생성
        self.dashboard_tab = DashboardTab(self.notebook, self.style_manager, learning_controller)
        self.notebook.add(self.dashboard_tab, text=_("📊 Dashboard"))

    def _create_resources_tab(self):
        """리소스 및 학습 자료 탭 생성"""
        # 학습 컨트롤러 가져오기
        learning_controller = None
        if hasattr(engine, 'get_learning_manager') and engine.get_learning_manager():
            learning_controller = engine.get_learning_manager()

        # ResourcesTab 생성
        self.resources_tab = ResourcesTab(self.notebook, self.style_manager, learning_controller)
        self.notebook.add(self.resources_tab, text=_("📚 Resources"))

    def _create_status_bar(self):
        """상태 바 생성"""
        colors = self.style_manager.get_current_theme_colors()
        self.status_bar = tk.Frame(self.root, relief=tk.SUNKEN, bg=colors["bg_alt"])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 상태 정보
        self.status_label = tk.Label(self.status_bar, text=_("Ready"), anchor=tk.W, bg=colors["bg_alt"], fg=colors["fg_alt"])
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.progress_label = tk.Label(self.status_bar, text=_("Progress: 0%"), anchor=tk.E, bg=colors["bg_alt"], fg=colors["fg_alt"])
        self.progress_label.pack(side=tk.RIGHT, padx=5)

    def update_status(self, message: str):
        """상태 메시지 업데이트"""
        self.status_label.config(text=message)

    def update_progress(self, progress: int):
        """진도 업데이트"""
        self.progress_label.config(text=_("Progress: {progress}%").format(progress=progress))

    def show_tab(self, tab_name: str):
        """특정 탭 표시"""
        # 나중에 구현
        logger.info(_("탭 전환 요청: {tab_name}").format(tab_name=tab_name))

    # 메뉴 커맨드 구현
    def new_code(self):
        """새 코드 생성"""
        logger.info(_("새 코드 생성"))
        self.update_status(_("Creating new code..."))

    def open_file(self):
        """파일 열기"""
        filetypes = [(_("Python Files"), "*.py"), (_("All Files"), "*.*")]
        filename = filedialog.askopenfilename(filetypes=filetypes)

        if filename:
            logger.info(_("파일 열기: {filename}").format(filename=filename))
            self.update_status(_("Opened: {filename}").format(filename=filename))

    def save_file(self):
        """파일 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[(_("Python Files"), "*.py"), (_("All Files"), "*.*")]
        )

        if filename:
            logger.info(_("파일 저장: {filename}").format(filename=filename))
            self.update_status(_("Saved: {filename}").format(filename=filename))

    def export_data(self):
        """데이터 내보내기"""
        logger.info(_("데이터 내보내기"))
        messagebox.showinfo(_("Export"), _("Export functionality coming soon!"))

    def undo(self):
        """실행 취소"""
        logger.info(_("실행 취소"))

    def redo(self):
        """재실행"""
        logger.info(_("재실행"))

    def cut(self):
        """잘라내기"""
        logger.info(_("잘라내기"))

    def copy(self):
        """복사"""
        logger.info(_("복사"))

    def paste(self):
        """붙여넣기"""
        logger.info(_("붙여넣기"))

    def toggle_sidebar(self):
        """사이드바 토글"""
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

    def open_settings(self):
        """설정 열기"""
        logger.info(_("설정 열기"))
        messagebox.showinfo(_("Settings"), _("Settings dialog coming soon!"))

    def start_learning(self):
        """학습 시작"""
        logger.info(_("학습 시작"))
        self.update_status(_("Starting learning session..."))

    def show_progress(self):
        """진도 표시"""
        logger.info(_("진도 표시"))
        messagebox.showinfo(_("Progress"), _("Your learning progress: 45%"))

    def show_achievements(self):
        """성취 표시"""
        logger.info(_("성취 표시"))
        messagebox.showinfo(_("Achievements"), _("Achievements: 5 unlocked"))

    def show_documentation(self):
        """문서 표시"""
        logger.info(_("문서 표시"))
        messagebox.showinfo(_("Documentation"), _("Documentation coming soon!"))

    def show_about(self):
        """정보 표시"""
        about_text = f"""
{APP_NAME} v{APP_VERSION}

{_("Python learning AI based mentoring platform")}

{_("Features")}:
• {_("AI based code analysis")}
• {_("Real-time mentoring")}
• {_("Progress tracking")}
• {_("Adaptive learning")}

{_("Developer")}: {APP_AUTHOR}
        """
        messagebox.showinfo(_("About"), about_text)

    def quit_application(self):
        """애플리케이션 종료"""
        if messagebox.askyesno(_("Exit"), _("Are you sure you want to quit?")):
            self.quit()

    def run_code(self, code: Optional[str] = None):
        """코드 실행"""
        try:
            if code is None:
                code = self.code_editor.get_code()

            if not code.strip():
                messagebox.showwarning(_("Run Code"), _("There is no code to run."))
                return

            logger.info(_("코드 실행"))
            self.update_status(_("Running code..."))

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
                messagebox.showinfo(_("Execution Result"), _("✅ Execution successful!\n\n📄 Output:\n{output}").format(output=output))
                self.update_status(_("Code executed successfully! Output: {len_output} chars").format(len_output=len(output)))
            else:
                messagebox.showinfo(_("Execution Result"), _("✅ Code executed successfully.\n(No output)"))
                self.update_status(_("Code executed successfully!"))

            logger.info(_("코드 실행 성공"))

        except Exception as e:
            error_msg = _("❌ An error occurred while running the code:\n\n{error}").format(error=str(e))
            messagebox.showerror(_("Execution Error"), error_msg)
            self.update_status(_("Execution error: {error}").format(error=str(e)))
            logger.error(_("코드 실행 실패: {error}").format(error=e))

    def analyze_code(self, code: Optional[str] = None):
        """코드 분석"""
        try:
            if code is None:
                code = self.code_editor.get_code()

            if not code.strip():
                messagebox.showwarning(_("Code Analysis"), _("There is no code to analyze."))
                return

            logger.info(_("코드 분석"))
            self.update_status(_("Analyzing code..."))

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
                analysis["syntax"] = _("✅ Syntax OK")
            except SyntaxError as e:
                analysis["syntax"] = _("❌ Syntax Error: {error_msg} (line {line_num})").format(error_msg=e.msg, line_num=e.lineno)

            # 결과 메시지 생성
            result_msg = f"""📊 {_("Code Analysis Result")}

📏 {_("Length")}: {analysis['lines']} {_("lines")} ({analysis['characters']} {_("characters")})
🔧 {_("Functions")}: {analysis['functions']}
🏗️  {_("Classes")}: {analysis['classes']}
💬 {_("Comments")}: {analysis['comments']}
📝 {_("Syntax")}: {analysis['syntax']}

💡 {_("Tip: Configure the Claude API for more detailed analysis!")}"""

            messagebox.showinfo(_("Code Analysis Complete"), result_msg)
            self.update_status(_("Analysis complete!"))
            logger.info(_("코드 분석 완료"))

        except Exception as e:
            error_msg = _("An error occurred during code analysis:\n\n{error}").format(error=str(e))
            messagebox.showerror(_("Analysis Error"), error_msg)
            self.update_status(_("Analysis error: {error}").format(error=str(e)))
            logger.error(_("코드 분석 실패: {error}").format(error=e))


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