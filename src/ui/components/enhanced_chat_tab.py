"""
향상된 채팅 UI 컴포넌트
튜터링 시스템 통합, 고급 기능 포함
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from loguru import logger
import threading
import json

from src.learning.tutoring_system import (
    InteractiveTutor,
    TutoringMode,
    StudentLevel,
    get_interactive_tutor
)
from src.database.repositories.chat_repository import get_chat_repository
from src.ui.language_manager import get_translator

_ = get_translator()


class EnhancedChatTab(tk.Frame):
    """향상된 채팅 탭 컴포넌트"""

    def __init__(self, parent, style_manager, shortcut_manager, on_code_share: Optional[Callable] = None):
        super().__init__(parent)
        self.style_manager = style_manager
        self.shortcut_manager = shortcut_manager
        self.on_code_share = on_code_share
        self.current_user_id = 1  # 기본 사용자 ID
        self.is_processing = False
        self.current_conversation = None

        # 튜터링 시스템 초기화
        self.tutor = get_interactive_tutor()
        self.chat_repository = get_chat_repository()

        # 현재 튜터링 모드
        self.current_mode = TutoringMode.CONVERSATION
        self.student_level = StudentLevel.BEGINNER

        # UI 컴포넌트 초기화
        self._create_ui()
        self._setup_bindings()

        # 기본 대화 및 세션 생성
        self._initialize_session()

        logger.info(_("Enhanced chat tab initialization complete"))

    def _create_ui(self):
        """UI 컴포넌트 생성"""
        colors = self.style_manager.get_current_theme_colors()
        self.configure(bg=colors["bg"])
        
        # 메인 컨테이너
        main_container = tk.Frame(self, bg=colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 상단 도구 모음
        toolbar = tk.Frame(main_container, bg=colors["bg_alt"], height=60)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        # 첫 번째 행: 대화 관리
        first_row = tk.Frame(toolbar, bg=colors["bg_alt"])
        first_row.pack(fill=tk.X, pady=5)

        # 새 대화 버튼
        tk.Button(
            first_row,
            text=_("➕ New Conversation"),
            command=self._create_new_conversation,
            bg=colors["success"],
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        # 대화 제목
        self.conversation_label = tk.Label(
            first_row,
            text=_("New Conversation"),
            bg=colors["bg_alt"],
            fg=colors["fg"],
            font=("Arial", 12, "bold")
        )
        self.conversation_label.pack(side=tk.LEFT, padx=10)

        # 대화 기록 버튼
        tk.Button(
            first_row,
            text=_("📜 History"),
            command=self._show_conversation_history,
            bg=colors["info"],
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT
        ).pack(side=tk.RIGHT, padx=5)

        # 두 번째 행: 튜터링 설정
        second_row = tk.Frame(toolbar, bg=colors["bg_alt"])
        second_row.pack(fill=tk.X, pady=5)

        # 튜터링 모드 선택
        tk.Label(
            second_row,
            text=_("Tutoring Mode:"),
            bg=colors["bg_alt"],
            fg=colors["fg_alt"],
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=5)

        self.mode_var = tk.StringVar(value=TutoringMode.CONVERSATION.value)
        mode_options = [mode.value for mode in TutoringMode]
        self.mode_menu = ttk.Combobox(
            second_row,
            textvariable=self.mode_var,
            values=mode_options,
            state="readonly",
            width=15,
            font=("Arial", 9)
        )
        self.mode_menu.pack(side=tk.LEFT, padx=5)
        self.mode_menu.bind("<<ComboboxSelected>>", self._on_mode_change)

        # 학생 수준 선택
        tk.Label(
            second_row,
            text=_("Level:"),
            bg=colors["bg_alt"],
            fg=colors["fg_alt"],
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=5)

        self.level_var = tk.StringVar(value=StudentLevel.BEGINNER.value)
        level_options = [level.value for level in StudentLevel]
        self.level_menu = ttk.Combobox(
            second_row,
            textvariable=self.level_var,
            values=level_options,
            state="readonly",
            width=12,
            font=("Arial", 9)
        )
        self.level_menu.pack(side=tk.LEFT, padx=5)
        self.level_menu.bind("<<ComboboxSelected>>", self._on_level_change)

        # 세션 통계
        self.stats_label = tk.Label(
            second_row,
            text=_("Messages: 0"),
            bg=colors["bg_alt"],
            font=("Arial", 8),
            fg=colors["fg_alt"]
        )
        self.stats_label.pack(side=tk.RIGHT, padx=5)

        # 메인 콘텐츠 영역
        content_area = tk.Frame(main_container, bg=colors["bg"])
        content_area.pack(fill=tk.BOTH, expand=True)

        # 채팅 메시지 영역
        chat_frame = tk.Frame(content_area, bg=colors["bg"])
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 메시지 표시 영역
        message_frame = tk.Frame(chat_frame, relief=tk.SUNKEN, borderwidth=1)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 메시지 텍스트 위젯
        self.messages_display = scrolledtext.ScrolledText(
            message_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            background=colors["editor_bg"],
            foreground=colors["editor_fg"],
            state="disabled",
            padx=10,
            pady=10
        )
        self.messages_display.pack(fill=tk.BOTH, expand=True)

        # 메시지 태그 설정 (기존 + 튜터링 모드별)
        self.messages_display.tag_config("user", background="#e3f2fd", font=("Arial", 11, "bold"))
        self.messages_display.tag_config("assistant", background="#f1f8e9")
        self.messages_display.tag_config("system", foreground=colors["fg_alt"], font=("Arial", 9, "italic"))
        self.messages_display.tag_config("timestamp", foreground=colors["fg_alt"], font=("Arial", 8))
        self.messages_display.tag_config("code", background=colors["bg_alt"], font=("Consolas", 10))

        # 튜터링 모드별 태그
        self.messages_display.tag_config("mode_conversation", foreground="#1976D2")
        self.messages_display.tag_config("mode_code_review", foreground="#388E3C")
        self.messages_display.tag_config("mode_problem_solving", foreground="#F57C00")
        self.messages_display.tag_config("mode_concept", foreground="#7B1FA2")
        self.messages_display.tag_config("mode_debugging", foreground="#D32F2F")

        # 입력 영역
        input_frame = tk.Frame(chat_frame, bg=colors["bg"])
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 메시지 입력
        self.message_input = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            height=4,
            font=("Arial", 11),
            background=colors["editor_bg"],
            foreground=colors["editor_fg"],
            insertbackground=colors["editor_fg"]
        )
        self.message_input.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.message_input.bind("<Control-Return>", lambda e: self.send_message())

        # 입력 도구 모음
        input_toolbar = tk.Frame(input_frame, bg=colors["bg"])
        input_toolbar.pack(fill=tk.X)

        # 코드 공유 버튼
        tk.Button(
            input_toolbar,
            text=_("📋 Share Code"),
            command=self._share_code,
            bg=colors["warning"],
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=3,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        # 전송 버튼
        self.send_button = tk.Button(
            input_toolbar,
            text=_("📤 Send"),
            command=self.send_message,
            bg=colors["primary"],
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            relief=tk.FLAT
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # 안내 메시지
        tk.Label(
            input_toolbar,
            text=_("Ctrl+Enter to send"),
            bg=colors["bg"],
            font=("Arial", 8),
            fg=colors["fg_alt"]
        ).pack(side=tk.RIGHT, padx=5)

        # 사이드바 (코드 컨텍스트 + 튜터링 정보)
        sidebar = tk.Frame(content_area, width=300, bg=colors["bg_alt"])
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        sidebar.pack_propagate(False)

        # 코드 컨텍스트 영역
        tk.Label(
            sidebar,
            text=_("📝 Code Context"),
            bg=colors["bg_alt"],
            fg=colors["fg"],
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        self.code_context_display = scrolledtext.ScrolledText(
            sidebar,
            wrap=tk.WORD,
            font=("Consolas", 9),
            background=colors["editor_bg"],
            foreground=colors["editor_fg"],
            height=12,
            state="disabled"
        )
        self.code_context_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 코드 컨텍스트 버튼
        context_toolbar = tk.Frame(sidebar, bg=colors["bg_alt"])
        context_toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            context_toolbar,
            text=_("📋 Copy"),
            command=self._copy_code_context,
            bg=colors["success"],
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            context_toolbar,
            text=_("🗑️ Clear"),
            command=self._clear_code_context,
            bg=colors["danger"],
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2,
            relief=tk.FLAT
        ).pack(side=tk.RIGHT, padx=2)

        # 구분선
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)

        # 튜터링 세션 정보
        tk.Label(
            sidebar,
            text=_("🎓 Tutoring Session"),
            bg=colors["bg_alt"],
            fg=colors["fg"],
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        # 세션 정보 표시 영역
        self.session_info_display = scrolledtext.ScrolledText(
            sidebar,
            wrap=tk.WORD,
            font=("Arial", 9),
            background=colors["editor_bg"],
            foreground=colors["editor_fg"],
            height=8,
            state="disabled"
        )
        self.session_info_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 세션 관리 버튼
        session_toolbar = tk.Frame(sidebar, bg=colors["bg_alt"])
        session_toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            session_toolbar,
            text=_("🔄 New Session"),
            command=self._start_new_tutoring_session,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            session_toolbar,
            text=_("⏹️ End"),
            command=self._end_tutoring_session,
            bg="#607D8B",
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2,
            relief=tk.FLAT
        ).pack(side=tk.RIGHT, padx=2)

        # 상태 바
        self.status_bar = tk.Label(
            main_container,
            text=_("Ready"),
            anchor=tk.W,
            bg=colors["bg_alt"],
            fg=colors["fg_alt"],
            font=("Arial", 9)
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def _setup_bindings(self):
        """키 바인딩 설정"""
        self.message_input.bind(self.shortcut_manager.get_shortcut("chat.send"), lambda e: self.send_message())
        self.message_input.bind("<Key>", self._on_input_change)

    def _on_input_change(self, event):
        """입력 변경 감지"""
        text = self.message_input.get(1.0, tk.END).strip()
        if text:
            self.send_button.config(state="normal")
        else:
            self.send_button.config(state="disabled")

    def _initialize_session(self):
        """초기 세션 초기화"""
        try:
            # 데이터베이스에 새 대화 생성
            self.current_conversation = self.chat_repository.create_conversation(
                user_id=self.current_user_id,
                title=_("Tutoring Session {timestamp}").format(timestamp=datetime.now().strftime('%H:%M')),
                conversation_type="tutoring"
            )

            self.conversation_label.config(text=self.current_conversation['title'])

            # 튜터링 세션 생성
            self.tutoring_session = self.tutor.create_session(
                user_id=self.current_user_id,
                mode=self.current_mode,
                student_level=self.student_level
            )

            # 메시지 영역 초기화
            self.messages_display.config(state="normal")
            self.messages_display.delete(1.0, tk.END)
            self.messages_display.config(state="disabled")

            # 환영 메시지 추가
            self._add_welcome_message()

            # 세션 정보 업데이트
            self._update_session_info()

            self._update_status(_("New tutoring session started"))
            logger.info(_("New tutoring session initialized: {session_id}").format(session_id=self.tutoring_session.session_id))

        except Exception as e:
            logger.error(_("Session initialization failed: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Failed to initialize session: {error}").format(error=e))

    def _add_welcome_message(self):
        """환영 메시지 추가"""
        mode_descriptions = {
            TutoringMode.CONVERSATION: _("Free Conversation"),
            TutoringMode.CODE_REVIEW: _("Code Review"),
            TutoringMode.PROBLEM_SOLVING: _("Problem Solving"),
            TutoringMode.CONCEPT_EXPLANATION: _("Concept Explanation"),
            TutoringMode.DEBUGGING: _("Debugging Help")
        }

        welcome_text = f"""👋 {_("Hello! I am your Python AI Tutor.")}

🎯 {_("Current Mode")}: {mode_descriptions.get(self.current_mode, 'Free Conversation')}
📊 {_("Level")}: {self.student_level.value}

💡 {_("How I can help")}:
• {_("Explain Python concepts and provide examples")}
• {_("Analyze code and provide feedback")}
• {_("Find bugs and suggest solutions")}
• {_("Discuss optimization and best practices")}
• {_("Guide you through problem-solving steps")}

📋 {_("Click the 'Share Code' button to analyze your code.")}

{_("Please ask a question or share your code!")}"""

        self._display_message("system", welcome_text)

    def _display_message(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """메시지 표시"""
        self.messages_display.config(state="normal")

        if timestamp is None:
            timestamp = datetime.now()

        # 메시지 헤더
        role_names = {
            "user": _("👤 User"),
            "assistant": _("🤖 Tutor"),
            "system": _("ℹ️ System")
        }

        # 튜터링 모드 태그
        mode_tag = f"mode_{self.current_mode.value}"

        # 메시지 표시
        self.messages_display.insert(tk.END, f"{role_names.get(role, role)}: ", (role, mode_tag))
        self.messages_display.insert(tk.END, f"({timestamp.strftime('%H:%M')})\n", "timestamp")

        # 메시지 내용
        self._insert_formatted_content(content)

        # 구분선
        self.messages_display.insert(tk.END, "\n" + "─" * 60 + "\n\n")

        self.messages_display.config(state="disabled")
        self.messages_display.see(tk.END)

    def _insert_formatted_content(self, content: str):
        """형식화된 콘텐츠 삽입"""
        lines = content.split('\n')
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                self.messages_display.insert(tk.END, line + "\n", "code")
            else:
                self.messages_display.insert(tk.END, line + "\n")

    def _on_mode_change(self, event):
        """튜터링 모드 변경"""
        try:
            selected_mode = self.mode_var.get()
            self.current_mode = TutoringMode(selected_mode)

            # 튜터 세션 모드 업데이트
            if self.tutoring_session:
                self.tutoring_session.mode = self.current_mode

            self._update_status(_("Tutoring mode changed: {mode}").format(mode=self.current_mode.value))
            logger.info(_("Tutoring mode changed: {mode}").format(mode=self.current_mode.value))

        except Exception as e:
            logger.error(_("Mode change failed: {error}").format(error=e))

    def _on_level_change(self, event):
        """학생 수준 변경"""
        try:
            selected_level = self.level_var.get()
            self.student_level = StudentLevel(selected_level)

            # 튜터 세션 수준 업데이트
            if self.tutoring_session:
                self.tutoring_session.student_level = self.student_level

            self._update_status(_("Student level changed: {level}").format(level=self.student_level.value))
            logger.info(_("Student level changed: {level}").format(level=self.student_level.value))

        except Exception as e:
            logger.error(_("Level change failed: {error}").format(error=e))

    def send_message(self):
        """메시지 전송"""
        if self.is_processing:
            messagebox.showwarning(_("Processing"), _("Please wait for the previous message to be processed."))
            return

        message_text = self.message_input.get(1.0, tk.END).strip()

        if not message_text:
            messagebox.showwarning(_("Empty Message"), _("Please enter a message."))
            return

        try:
            self.is_processing = True
            self.send_button.config(state="disabled", text=_("⏳ Processing..."))

            # 사용자 메시지 표시
            self._display_message("user", message_text)

            # 데이터베이스에 저장
            self.chat_repository.create_message(
                conversation_id=self.current_conversation['id'],
                role="user",
                content=message_text
            )

            # 입력창 비우기
            self.message_input.delete(1.0, tk.END)

            # 코드 컨텍스트 가져오기
            code_context = self._get_current_code_context()

            # 백그라운드에서 응답 생성
            response_thread = threading.Thread(
                target=self._generate_ai_response,
                args=(message_text, code_context)
            )
            response_thread.daemon = True
            response_thread.start()

        except Exception as e:
            logger.error(_("Message send failed: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Failed to send message: {error}").format(error=e))
            self.is_processing = False
            self.send_button.config(state="normal", text=_("📤 Send"))

    def _generate_ai_response(self, user_message: str, code_context: Optional[str] = None):
        """AI 응답 생성 (백그라운드 스레드)"""
        try:
            # 튜터를 사용하여 응답 생성
            response = self.tutor.process_message(
                message=user_message,
                session_id=self.tutoring_session.session_id,
                code_context=code_context
            )

            # 메인 스레드에서 UI 업데이트
            self.after(0, lambda: self._display_ai_response(response))

        except Exception as e:
            logger.error(_("AI response generation failed: {error}").format(error=e))
            error_message = _("Sorry, an error occurred while generating the response: {error}").format(error=str(e))
            self.after(0, lambda: self._display_ai_response(error_message))

    def _display_ai_response(self, response: str):
        """AI 응답 표시"""
        try:
            # AI 응답 표시
            self._display_message("assistant", response)

            # 데이터베이스에 저장
            self.chat_repository.create_message(
                conversation_id=self.current_conversation['id'],
                role="assistant",
                content=response
            )

            # 세션 정보 업데이트
            self._update_session_info()

        except Exception as e:
            logger.error(_("AI response display failed: {error}").format(error=e))

        finally:
            self.is_processing = False
            self.send_button.config(state="normal", text=_("📤 Send"))
            self._update_status(_("Response complete"))

    def _update_session_info(self):
        """세션 정보 업데이트"""
        try:
            if not self.tutoring_session:
                return

            summary = self.tutor.get_session_summary(self.tutoring_session.session_id)

            info_text = f"""🎯 {_("Tutoring Session Info")}

{_("Mode")}: {summary.get('mode', 'N/A')}
{_("Level")}: {summary.get('student_level', 'N/A')}
{_("Topic")}: {summary.get('topic', 'General')}

📊 {_("Statistics")}:
• {_("Messages")}: {summary.get('message_count', 0)}
• {_("Code Shares")}: {summary.get('code_shares', 0)}
• {_("Duration")}: {int(summary.get('duration', 0) // 60)} {_("min")}

💡 {_("Learning Objectives")}:
"""

            learning_objectives = self.tutoring_session.learning_objectives
            if learning_objectives:
                for obj in learning_objectives:
                    info_text += f"  • {obj}\n"
            else:
                info_text += f"  {_('Not set')}\n"

            self.session_info_display.config(state="normal")
            self.session_info_display.delete(1.0, tk.END)
            self.session_info_display.insert(1.0, info_text)
            self.session_info_display.config(state="disabled")

            # 상태 바 업데이트
            self.stats_label.config(text=_("Messages: {count}").format(count=summary.get('message_count', 0)))

        except Exception as e:
            logger.error(_("Session info update failed: {error}").format(error=e))

    def _share_code(self):
        """코드 컨텍스트 공유"""
        if self.on_code_share:
            code = self.on_code_share()
            if code:
                self._set_code_context(code)

                # 튜터 세션에 코드 컨텍스트 추가
                if self.tutoring_session:
                    self.tutoring_session.add_code_context(code)

                messagebox.showinfo(_("Share Code"), _("Code has been added to the context."))
            else:
                messagebox.showwarning(_("No Code"), _("There is no code to share."))
        else:
            messagebox.showinfo(_("Share Code"), _("Code sharing feature is not ready."))

    def _set_code_context(self, code: str):
        """코드 컨텍스트 설정"""
        self.code_context_display.config(state="normal")
        self.code_context_display.delete(1.0, tk.END)
        self.code_context_display.insert(1.0, code)
        self.code_context_display.config(state="disabled")

        self._update_status(_("Code context updated ({length} chars)").format(length=len(code)))

    def _get_current_code_context(self) -> Optional[str]:
        """현재 코드 컨텍스트 반환"""
        try:
            code = self.code_context_display.get(1.0, tk.END).strip()
            return code if code else None
        except:
            return None

    def _copy_code_context(self):
        """코드 컨텍스트 복사"""
        try:
            code = self._get_current_code_context()
            if code:
                self.clipboard_clear()
                self.clipboard_append(code)
                self._update_status(_("Code context copied"))
            else:
                messagebox.showwarning(_("Copy Failed"), _("There is no code to copy."))
        except Exception as e:
            logger.error(_("Code copy failed: {error}").format(error=e))

    def _clear_code_context(self):
        """코드 컨텍스트 삭제"""
        self.code_context_display.config(state="normal")
        self.code_context_display.delete(1.0, tk.END)
        self.code_context_display.config(state="disabled")

        # 튜터 세션에서도 제거
        if self.tutoring_session:
            self.tutoring_session.context = {}

        self._update_status(_("Code context cleared"))

    def _create_new_conversation(self):
        """새 대화 생성"""
        if messagebox.askyesno(_("New Conversation"), _("Are you sure you want to save the current conversation and start a new one?")):
            self._initialize_session()

    def _show_conversation_history(self):
        """대화 기록 표시"""
        try:
            conversations = self.chat_repository.get_user_conversations(self.current_user_id)

            if not conversations:
                messagebox.showinfo(_("Conversation History"), _("No saved conversations found."))
                return

            # 간단한 대화 목록 표시
            history_window = tk.Toplevel(self)
            history_window.title(_("Conversation History"))
            history_window.geometry("600x400")

            # 대화 목록
            listbox = tk.Listbox(history_window, font=("Arial", 10))
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            for conv in conversations:
                created_at = datetime.fromisoformat(conv['created_at']).strftime('%Y-%m-%d %H:%M')
                listbox.insert(tk.END, f"{conv['title']} ({created_at})")

            # 선택시 대화 로드
            def load_selected_conversation():
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    conversation = conversations[index]
                    self.load_conversation(conversation['id'])
                    history_window.destroy()

            tk.Button(
                history_window,
                text=_("Load"),
                command=load_selected_conversation,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 10)
            ).pack(pady=10)

        except Exception as e:
            logger.error(_("Failed to show conversation history: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Could not load conversation history: {error}").format(error=e))

    def _start_new_tutoring_session(self):
        """새 튜터링 세션 시작"""
        self._initialize_session()

    def _end_tutoring_session(self):
        """튜터링 세션 종료"""
        try:
            if self.tutoring_session:
                # 평가 요청
                rating = simpledialog.askinteger(
                    _("Rate Session"),
                    _("Please rate this tutoring session (1-5):"),
                    minvalue=1,
                    maxvalue=5
                )

                # 세션 종료
                self.tutor.end_session(self.tutoring_session.session_id)

                # 데이터베이스에 세션 종료 기록
                if hasattr(self, 'tutoring_db_session') and self.tutoring_db_session:
                    self.chat_repository.end_tutoring_session(
                        self.tutoring_db_session['id'],
                        rating=rating
                    )

                messagebox.showinfo(_("Session Ended"), _("The tutoring session has ended."))
                self._update_status(_("Tutoring session ended"))

        except Exception as e:
            logger.error(_("Failed to end tutoring session: {error}").format(error=e))

    def load_conversation(self, conversation_id: int):
        """특정 대화 로드"""
        try:
            conversation = self.chat_repository.get_conversation(conversation_id)
            if not conversation:
                messagebox.showerror(_("Error"), _("Conversation not found."))
                return

            self.current_conversation = conversation
            self.conversation_label.config(text=conversation['title'])

            # 메시지 영역 초기화
            self.messages_display.config(state="normal")
            self.messages_display.delete(1.0, tk.END)

            # 메시지 로드
            messages = self.chat_repository.get_conversation_messages(conversation_id)
            for msg in messages:
                timestamp = datetime.fromisoformat(msg['timestamp'])
                self._display_message(msg['role'], msg['content'], timestamp)

            self.messages_display.config(state="disabled")
            self._update_status(_("Conversation loaded: {title}").format(title=conversation['title']))

            logger.info(_("Conversation loaded: {id}").format(id=conversation_id))

        except Exception as e:
            logger.error(_("Failed to load conversation: {error}").format(error=e))
            messagebox.showerror(_("Error"), _("Could not load conversation: {error}").format(error=e))

    def _update_status(self, message: str):
        """상태 메시지 업데이트"""
        self.status_bar.config(text=message)


# 테스트용 코드
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Enhanced Chat Tab Test")
    root.geometry("1000x700")

    chat_tab = EnhancedChatTab(root)
    chat_tab.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
