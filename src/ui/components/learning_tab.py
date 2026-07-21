"""
학습 탭 컴포넌트
학습 시스템의 메인 UI 인터페이스
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, Dict, Any, List, Callable
from loguru import logger

from src.learning.curriculum.models import DifficultyLevel, Exercise, Topic
from src.ui.components.code_editor import CodeEditor
from src.ui.language_manager import get_translator

_ = get_translator()


class LearningTab(tk.Frame):
    """학습 탭 컴포넌트"""

    def __init__(self, parent, style_manager, learning_controller=None):
        super().__init__(parent)
        self.style_manager = style_manager
        self.controller = learning_controller
        self.current_level = DifficultyLevel.BEGINNER
        self.current_topic = None
        self.current_exercise = None
        self.user_id = 1  # 기본 사용자 ID

        self._create_ui()
        self._load_curriculum_data()

        logger.info(_("Learning tab initialization complete"))

    def _create_ui(self):
        """UI 생성"""
        colors = self.style_manager.get_current_theme_colors()
        self.configure(bg=colors["bg"])
        
        # 상단 진도 표시 영역
        self._create_progress_header()

        # 메인 컨텐츠 영역
        content_frame = tk.Frame(self, bg=colors["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 노트북 구조
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 커리큘럼 탭
        self._create_curriculum_tab()

        # 연습 문제 탭
        self._create_exercise_tab()

        # 성취 탭
        self._create_achievements_tab()

        # 진도 탭
        self._create_progress_tab()

        # 하단 도구 모음
        self._create_action_toolbar()

    def _create_progress_header(self):
        """진도 헤더 생성"""
        colors = self.style_manager.get_current_theme_colors()
        header_frame = tk.Frame(self, bg=colors["bg_alt"], height=100)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        # 제목
        title_label = tk.Label(
            header_frame,
            text=_("📚 Python Learning Path"),
            font=("Arial", 16, "bold"),
            bg=colors["bg_alt"],
            fg=colors["fg"]
        )
        title_label.pack(pady=5)

        # 진도 정보
        self.progress_info_frame = tk.Frame(header_frame, bg=colors["bg_alt"])
        self.progress_info_frame.pack(fill=tk.X, padx=10)

        # 완료율 프로그레스 바
        self.progress_bar = ttk.Progressbar(
            self.progress_info_frame,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5)

        # 통계 라벨
        self.stats_label = tk.Label(
            self.progress_info_frame,
            text=_("Completed: 0/0 topics | Study time: 0 min | XP: 0"),
            bg=colors["bg_alt"],
            fg=colors["fg_alt"],
            font=("Arial", 10)
        )
        self.stats_label.pack(side=tk.LEFT, padx=10)

        # 레벨 선택
        level_frame = tk.Frame(header_frame, bg=colors["bg_alt"])
        level_frame.pack(side=tk.RIGHT, padx=10)

        tk.Label(level_frame, text=_("Difficulty:"), bg=colors["bg_alt"], fg=colors["fg"]).pack(side=tk.LEFT)

        self.level_var = tk.StringVar(value="beginner")
        level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.level_var,
            values=["beginner", "intermediate", "advanced"],
            state="readonly",
            width=10
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind("<<ComboboxSelected>>", self._on_level_changed)

    def _create_curriculum_tab(self):
        """커리큘럼 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("📖 Curriculum"))

        # 주제 목록 프레임
        left_frame = tk.Frame(tab, bg=colors["bg"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 주제 목록 헤더
        tk.Label(
            left_frame,
            text=_("Learning Topics"),
            font=("Arial", 12, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(pady=5)

        # 주제 목록
        self.topic_listbox = tk.Listbox(
            left_frame,
            font=("Arial", 11),
            selectmode=tk.SINGLE,
            bg=colors["editor_bg"],
            fg=colors["editor_fg"],
            selectbackground=colors["primary"],
            selectforeground=colors["editor_bg"]
        )
        self.topic_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.topic_listbox.bind("<<ListboxSelect>>", self._on_topic_selected)

        # 주제 상세 정보
        right_frame = tk.Frame(tab, bg=colors["bg"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 주제 상세 헤더
        tk.Label(
            right_frame,
            text=_("Topic Details"),
            font=("Arial", 12, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(pady=5)

        # 주제 정보 표시
        self.topic_title = tk.Label(
            right_frame,
            text="",
            font=("Arial", 14, "bold"),
            wraplength=400,
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.topic_title.pack(pady=10)

        self.topic_description = tk.Text(
            right_frame,
            wrap=tk.WORD,
            height=8,
            font=("Arial", 10),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.topic_description.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 학습 목표
        tk.Label(
            right_frame,
            text=_("Learning Objectives:"),
            font=("Arial", 10, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, padx=5)

        self.learning_objectives_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            height=4,
            font=("Arial", 9),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.learning_objectives_text.pack(fill=tk.X, padx=5, pady=5)

        # 시작 버튼
        button_frame = tk.Frame(right_frame, bg=colors["bg"])
        button_frame.pack(fill=tk.X, pady=10)

        self.start_topic_button = tk.Button(
            button_frame,
            text=_("Start Learning"),
            command=self.start_topic,
            bg=colors["success"],
            fg="white",
            font=("Arial", 11),
            state=tk.DISABLED,
            relief=tk.FLAT
        )
        self.start_topic_button.pack(side=tk.RIGHT, padx=5)

    def _create_exercise_tab(self):
        """연습 문제 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("✏️ Exercises"))

        # 문제 정보 영역
        problem_frame = tk.Frame(tab, bg=colors["bg"])
        problem_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(
            problem_frame,
            text=_("Problem:"),
            font=("Arial", 12, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W)

        self.problem_text = tk.Text(
            problem_frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.problem_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 힌트 영역
        hint_frame = tk.Frame(problem_frame, bg=colors["bg"])
        hint_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            hint_frame,
            text=_("Hint:"),
            font=("Arial", 10, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(side=tk.LEFT)

        self.hint_label = tk.Label(
            hint_frame,
            text=_("None"),
            fg="gray",
            font=("Arial", 9),
            bg=colors["bg"]
        )
        self.hint_label.pack(side=tk.LEFT, padx=5)

        self.show_hint_button = tk.Button(
            hint_frame,
            text=_("Show Hint"),
            command=self.show_hint,
            state=tk.DISABLED,
            bg=colors["secondary"],
            fg=colors["bg"],
            relief=tk.FLAT
        )
        self.show_hint_button.pack(side=tk.RIGHT, padx=5)

        # 코드 에디터
        editor_frame = tk.Frame(tab, bg=colors["bg"])
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(
            editor_frame,
            text=_("Write Code:"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W)

        self.exercise_editor = CodeEditor(editor_frame, self.style_manager)
        self.exercise_editor.pack(fill=tk.BOTH, expand=True)

        # 제출 버튼
        submit_frame = tk.Frame(tab, bg=colors["bg"])
        submit_frame.pack(fill=tk.X, padx=5, pady=5)

        self.submit_button = tk.Button(
            submit_frame,
            text=_("Submit"),
            command=self.submit_exercise,
            bg=colors["info"],
            fg="white",
            font=("Arial", 11),
            state=tk.DISABLED,
            relief=tk.FLAT
        )
        self.submit_button.pack(side=tk.RIGHT, padx=5)

        # 결과 표시 영역
        result_frame = tk.Frame(tab, bg=colors["bg"])
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(
            result_frame,
            text=_("Result:"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 9),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_achievements_tab(self):
        """성취 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("🏆 Achievements"))

        # 성취 헤더
        header_frame = tk.Frame(tab, bg=colors["bg"])
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(
            header_frame,
            text=_("My Achievements"),
            font=("Arial", 14, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(side=tk.LEFT)

        self.achievement_stats_label = tk.Label(
            header_frame,
            text=_("Earned: 0/0"),
            font=("Arial", 10),
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.achievement_stats_label.pack(side=tk.RIGHT)

        # 성쉴 그리드
        self.achievements_canvas = tk.Canvas(tab, bg=colors["bg"], highlightthickness=0)
        self.achievements_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.achievements_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.achievements_canvas.configure(yscrollcommand=scrollbar.set)

        # 성취 내용을 담을 프레임
        self.achievements_frame = tk.Frame(self.achievements_canvas, bg=colors["bg"])
        self.achievements_canvas.create_window((0, 0), window=self.achievements_frame, anchor="nw")

    def _create_progress_tab(self):
        """진도 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("📊 Progress"))

        # 진도 정보
        info_frame = tk.Frame(tab, bg=colors["bg"])
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            info_frame,
            text=_("Learning Progress"),
            font=("Arial", 14, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(pady=5)

        # 전체 진도
        self.overall_progress_frame = tk.Frame(info_frame, bg=colors["bg"])
        self.overall_progress_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            self.overall_progress_frame,
            text=_("Overall Progress:"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(side=tk.LEFT)

        self.overall_progress_bar = ttk.Progressbar(
            self.overall_progress_frame,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.overall_progress_bar.pack(side=tk.LEFT, padx=10)

        self.overall_progress_label = tk.Label(
            self.overall_progress_frame,
            text="0%",
            bg=colors["bg"],
            fg=colors["fg"]
        )
        self.overall_progress_label.pack(side=tk.LEFT)

        # 레벨별 진도
        level_progress_frame = tk.Frame(tab, bg=colors["bg"])
        level_progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            level_progress_frame,
            text=_("Progress by Level:"),
            font=("Arial", 12, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(pady=5)

        self.level_progress_text = tk.Text(
            level_progress_frame,
            height=10,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.level_progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_action_toolbar(self):
        """하단 도구 모음 생성"""
        colors = self.style_manager.get_current_theme_colors()
        toolbar = tk.Frame(self, bg=colors["bg_alt"], height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # 새로고침 버튼
        tk.Button(
            toolbar,
            text=_("🔄 Refresh"),
            command=self.refresh_data,
            bg=colors["secondary"],
            fg=colors["bg"],
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        # 다음 문제 버튼
        tk.Button(
            toolbar,
            text=_("⏭️ Next Exercise"),
            command=self.next_exercise,
            bg=colors["primary"],
            fg="white",
            state=tk.DISABLED,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        # 상태 라벨
        self.status_label = tk.Label(
            toolbar,
            text=_("Ready"),
            bg=colors["bg_alt"],
            fg=colors["fg_alt"],
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

    def _load_curriculum_data(self):
        """커리큘럼 데이터 로드"""
        try:
            if self.controller:
                # 주제 목록 로드
                curriculum = self.controller.get_curriculum(self.current_level)
                if curriculum:
                    self._load_topic_list(curriculum.topics)
                    self._update_progress_display()
            else:
                # 기본 테스트 데이터
                logger.warning(_("Learning controller not available. Using default data."))
                self._load_default_data()

        except Exception as e:
            logger.error(_("Failed to load curriculum data: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Could not load curriculum data: {error}").format(error=e))

    def _load_topic_list(self, topics: List[Topic]):
        """주제 목록 로드"""
        self.topic_listbox.delete(0, tk.END)

        for topic in topics:
            status = "✅" if topic.completed else "⭕"
            self.topic_listbox.insert(tk.END, f"{status} {topic.order}. {topic.title}")

        logger.debug(_("{count} topics loaded successfully").format(count=len(topics)))

    def _load_default_data(self):
        """기본 데이터 로드 (테스트용)"""
        # 기본 주제들
        default_topics = [
            {"id": "basics", "title": _("Python Basics"), "completed": False},
            {"id": "control_flow", "title": _("Control Flow"), "completed": False},
            {"id": "functions", "title": _("Functions"), "completed": False}
        ]

        self.topic_listbox.delete(0, tk.END)
        for topic in default_topics:
            status = "⭕"
            self.topic_listbox.insert(tk.END, f"{status} {topic['title']}")

    def _on_level_changed(self, event=None):
        """레벨 변경 이벤트"""
        selected_level = self.level_var.get()
        self.current_level = DifficultyLevel(selected_level)

        logger.info(_("Level changed: {level}").format(level=self.current_level.value))

        # 커리큘럼 데이터 다시 로드
        self._load_curriculum_data()

    def _on_topic_selected(self, event=None):
        """주제 선택 이벤트"""
        selection = self.topic_listbox.curselection()
        if not selection:
            return

        topic_index = selection[0]

        # 주제 정보 표시
        if self.controller:
            curriculum = self.controller.get_curriculum(self.current_level)
            if curriculum and topic_index < len(curriculum.topics):
                topic = curriculum.topics[topic_index]
                self._display_topic_info(topic)
                self.start_topic_button.config(state=tk.NORMAL)
        else:
            # 기본 정보 표시
            self.topic_title.config(text=_("Python Basics"))
            self.topic_description.delete(1.0, tk.END)
            self.topic_description.insert(1.0, _("Learn the basic syntax and concepts of Python."))
            self.start_topic_button.config(state=tk.NORMAL)

    def _display_topic_info(self, topic: Topic):
        """주제 정보 표시"""
        self.current_topic = topic

        # 주제 제목
        self.topic_title.config(text=f"{topic.order}. {topic.title}")

        # 주제 설명
        self.topic_description.delete(1.0, tk.END)
        self.topic_description.insert(1.0, topic.description)

        # 학습 목표
        self.learning_objectives_text.delete(1.0, tk.END)
        for i, objective in enumerate(topic.learning_objectives, 1):
            self.learning_objectives_text.insert(tk.END, f"{i}. {objective}\n")

    def start_topic(self):
        """주제 학습 시작"""
        try:
            logger.info(_("Starting topic: {topic_id}").format(topic_id=self.current_topic.id if self.current_topic else 'unknown'))

            if self.controller and self.current_topic:
                # 연습 문제 로드
                exercises = self.controller.get_topic_exercises(
                    self.current_level.value,
                    self.current_topic.id
                )

                if exercises:
                    self.current_exercise = exercises[0]
                    self._display_exercise(self.current_exercise)
                    self.notebook.select(1)  # 연습 문제 탭으로 이동
                    self.status_label.config(text=_("Exercise: {title}").format(title=self.current_exercise.title))
                else:
                    messagebox.showinfo(_("Notification"), _("There are no exercises for this topic yet."))
            else:
                messagebox.showinfo(_("Notification"), _("Learning controller is not initialized."))

        except Exception as e:
            logger.error(_("Failed to start topic: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Could not start topic: {error}").format(error=e))

    def _display_exercise(self, exercise: Exercise):
        """연습 문제 표시"""
        # 문제 설명
        self.problem_text.delete(1.0, tk.END)
        self.problem_text.insert(1.0, f"{exercise.title}\n\n{exercise.description}")

        # 힌트
        if exercise.hints:
            self.hint_label.config(text=_("{count} hints available").format(count=len(exercise.hints)))
            self.show_hint_button.config(state=tk.NORMAL)
            self.current_hints = exercise.hints
            self.current_hint_index = 0
        else:
            self.hint_label.config(text=_("No hints"))
            self.show_hint_button.config(state=tk.DISABLED)

        # 시작 코드
        if exercise.starter_code:
            self.exercise_editor.set_code(exercise.starter_code)
        else:
            self.exercise_editor.clear()

        # 버튼 활성화
        self.submit_button.config(state=tk.NORMAL)

        # 결과 영역 초기화
        self.result_text.delete(1.0, tk.END)

    def show_hint(self):
        """힌트 보기"""
        try:
            if hasattr(self, 'current_hints') and self.current_hint_index < len(self.current_hints):
                hint = self.current_hints[self.current_hint_index]
                self.result_text.insert(tk.END, _("💡 Hint {index}: {hint}\n\n").format(index=self.current_hint_index + 1, hint=hint))
                self.current_hint_index += 1

                if self.current_hint_index >= len(self.current_hints):
                    self.show_hint_button.config(state=tk.DISABLED)
                    self.show_hint_button.config(text=_("All hints shown"))

        except Exception as e:
            logger.error(_("Failed to show hint: {error}").format(error=e))

    def submit_exercise(self):
        """연습 문제 제출"""
        try:
            if not self.current_exercise:
                messagebox.showwarning(_("Warning"), _("No active exercise."))
                return

            # 코드 가져오기
            code = self.exercise_editor.get_code()

            if not code.strip():
                messagebox.showwarning(_("Warning"), _("Please enter your code."))
                return

            # 제출 처리
            if self.controller:
                self.status_label.config(text=_("Analyzing code..."))
                self.update()

                result = self.controller.submit_exercise(
                    user_id=self.user_id,
                    exercise=self.current_exercise,
                    code=code
                )

                # 결과 표시
                self._display_submission_result(result)

                if result.get("completed"):
                    messagebox.showinfo(_("Congratulations!"), _("You have completed the exercise! XP +{xp}").format(xp=result.get('xp_earned', 0)))
                    self.start_topic_button.config(state=tk.DISABLED)
                else:
                    messagebox.showinfo(_("Result"), _("Try again!"))

                self.status_label.config(text=_("Submission complete"))
                self._update_progress_display()
            else:
                # 테스트 결과
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, _("✅ Code submitted!\n\n(Test mode - no real analysis results)"))

        except Exception as e:
            logger.error(_("Exercise submission failed: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("An error occurred during submission: {error}").format(error=e))

    def _display_submission_result(self, result: Dict[str, Any]):
        """제출 결과 표시"""
        self.result_text.delete(1.0, tk.END)

        # 기본 정보
        self.result_text.insert(tk.END, _("Score: {score}/10\n").format(score=result.get('analysis', {}).get('score', 'N/A')))
        self.result_text.insert(tk.END, _("Completed: {completed}\n").format(completed=_('Yes') if result.get('completed') else _('No')))
        self.result_text.insert(tk.END, _("XP Earned: {xp}\n\n").format(xp=result.get('xp_earned', 0)))

        # 피드백
        feedback = result.get("message", "")
        if feedback:
            self.result_text.insert(tk.END, _("Feedback:\n{feedback}\n\n").format(feedback=feedback))

        # 분석 결과
        analysis = result.get("analysis", {})
        if analysis.get("strengths"):
            self.result_text.insert(tk.END, _("Strengths:\n"))
            for strength in analysis["strengths"]:
                self.result_text.insert(tk.END, f"✓ {strength}\n")

        if analysis.get("suggestions"):
            self.result_text.insert(tk.END, _("\nSuggestions for improvement:\n"))
            for suggestion in analysis["suggestions"]:
                self.result_text.insert(tk.END, f"• {suggestion}\n")

    def next_exercise(self):
        """다음 연습 문제"""
        try:
            if self.controller:
                # 다음 문제 추천
                exercises = self.controller.recommend_exercise(self.user_id, count=1)

                if exercises:
                    self.current_exercise = exercises[0]
                    self._display_exercise(self.current_exercise)
                    self.status_label.config(text=_("New exercise: {title}").format(title=self.current_exercise.title))
                else:
                    messagebox.showinfo(_("Notification"), _("No recommended exercises available."))
            else:
                messagebox.showinfo(_("Notification"), _("Learning controller is not initialized."))

        except Exception as e:
            logger.error(_("Failed to load next exercise: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Could not load next exercise: {error}").format(error=e))

    def refresh_data(self):
        """데이터 새로고침"""
        try:
            logger.info(_("Refreshing data"))
            self._load_curriculum_data()
            messagebox.showinfo(_("Complete"), _("Data has been refreshed."))
        except Exception as e:
            logger.error(_("Data refresh failed: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Data refresh failed: {error}").format(error=e))

    def _update_progress_display(self):
        """진도 표시 업데이트"""
        try:
            if self.controller:
                # 진도 데이터 가져오기
                progress_summary = self.controller.get_user_progress_summary(self.user_id)

                # 헤더 업데이트
                completed = progress_summary.get("total_completed", 0)
                total = progress_summary.get("total_items", 1)
                completion_rate = progress_summary.get("overall_completion_rate", 0.0)

                self.progress_bar["value"] = completion_rate

                stats_text = _("Completed: {completed}/{total} topics | ").format(completed=completed, total=total)
                stats_text += _("Study time: {minutes} min | ").format(minutes=progress_summary.get('total_study_minutes', 0))
                stats_text += _("XP: {xp}").format(xp=progress_summary.get('total_xp', 0))

                self.stats_label.config(text=stats_text)

                # 진도 탭 업데이트
                self.overall_progress_bar["value"] = completion_rate
                self.overall_progress_label.config(text=f"{completion_rate:.1f}%")

                # 레벨별 진도
                self.level_progress_text.delete(1.0, tk.END)
                level_progress = progress_summary.get("level_progress", {})

                for level_name, level_data in level_progress.items():
                    self.level_progress_text.insert(tk.END, f"{level_name.capitalize()}:\n")
                    self.level_progress_text.insert(tk.END, _("  Completed: {completed}/{total}\n").format(completed=level_data.get('completed', 0), total=level_data.get('total', 0)))
                    self.level_progress_text.insert(tk.END, _("  Completion Rate: {rate:.1f}%\n").format(rate=level_data.get('completion_rate', 0)))
                    self.level_progress_text.insert(tk.END, _("  Average Score: {score:.1f}/10\n\n").format(score=level_data.get('average_score', 0)))

                # 성채 탭 업데이트
                self._update_achievements_display()

        except Exception as e:
            logger.error(_("Failed to update progress display: {error}").format(error=e))

    def _update_achievements_display(self):
        """성취 표시 업데이트"""
        try:
            # 기존 성취 위젯 제거
            for widget in self.achievements_frame.winfo_children():
                widget.destroy()

            if self.controller:
                # 성취 데이터 가져오기
                achievements = self.controller.get_user_achievements(self.user_id)
                available_achievements = self.controller.get_available_achievements()

                # 획득 성취 표시
                earned_count = 0
                row, col = 0, 0
                for achievement_data in available_achievements:
                    # 성취 획득 여부 확인
                    is_earned = any(a["achievement_type"] == achievement_data["id"] for a in achievements)

                    if is_earned:
                        earned_count += 1
                        badge_style = {"bg": "#90EE90"}  # 연두색
                    else:
                        badge_style = {"bg": "#D3D3D3"}  # 회색

                    # 뱃지 버튼
                    badge = tk.Label(
                        self.achievements_frame,
                        text=f"{achievement_data['icon']}\n{achievement_data['name']}",
                        **badge_style,
                        width=15,
                        height=3,
                        relief=tk.RAISED
                    )
                    badge.grid(row=row, column=col, padx=5, pady=5)

                    col += 1
                    if col >= 4:  # 4열로 표시
                        col = 0
                        row += 1

                # 성취 통계 업데이트
                total_count = len(available_achievements)
                self.achievement_stats_label.config(text=_("Earned: {earned}/{total}").format(earned=earned_count, total=total_count))

                # 캔버스 스크롤 영역 업데이트
                self.achievements_frame.update_idletasks()
                self.achievements_canvas.config(
                    scrollregion=self.achievements_canvas.bbox("all")
                )

        except Exception as e:
            logger.error(_("Failed to update achievements display: {error}").format(error=e))



if __name__ == "__main__":
    # 학습 탭 테스트
    print("🧪 학습 탭 테스트")

    root = tk.Tk()
    root.title("학습 탭 테스트")
    root.geometry("1000x700")

    learning_tab = LearningTab(root)
    learning_tab.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

    print("✅ 학습 탭 테스트 완료")