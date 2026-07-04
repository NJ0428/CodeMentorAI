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


class EnhancedChatTab(tk.Frame):
    """향상된 채팅 탭 컴포넌트"""

    def __init__(self, parent, on_code_share: Optional[Callable] = None):
        super().__init__(parent)

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

        logger.info("향상된 채팅 탭 초기화 완료")

    def _create_ui(self):
        """UI 컴포넌트 생성"""
        # 메인 컨테이너
        main_container = tk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 상단 도구 모음
        toolbar = tk.Frame(main_container, bg="#f0f0f0", height=60)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        # 첫 번째 행: 대화 관리
        first_row = tk.Frame(toolbar, bg="#f0f0f0")
        first_row.pack(fill=tk.X, pady=5)

        # 새 대화 버튼
        tk.Button(
            first_row,
            text="➕ 새 대화",
            command=self._create_new_conversation,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # 대화 제목
        self.conversation_label = tk.Label(
            first_row,
            text="새 대화",
            bg="#f0f0f0",
            font=("Arial", 12, "bold")
        )
        self.conversation_label.pack(side=tk.LEFT, padx=10)

        # 대화 기록 버튼
        tk.Button(
            first_row,
            text="📜 기록",
            command=self._show_conversation_history,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)

        # 두 번째 행: 튜터링 설정
        second_row = tk.Frame(toolbar, bg="#f0f0f0")
        second_row.pack(fill=tk.X, pady=5)

        # 튜터링 모드 선택
        tk.Label(
            second_row,
            text="튜터링 모드:",
            bg="#f0f0f0",
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
            text="수준:",
            bg="#f0f0f0",
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
            text="메시지: 0",
            bg="#f0f0f0",
            font=("Arial", 8),
            fg="#666666"
        )
        self.stats_label.pack(side=tk.RIGHT, padx=5)

        # 메인 콘텐츠 영역
        content_area = tk.Frame(main_container)
        content_area.pack(fill=tk.BOTH, expand=True)

        # 채팅 메시지 영역
        chat_frame = tk.Frame(content_area)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 메시지 표시 영역
        message_frame = tk.Frame(chat_frame, relief=tk.SUNKEN, borderwidth=1)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 메시지 텍스트 위젯
        self.messages_display = scrolledtext.ScrolledText(
            message_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            background="#ffffff",
            foreground="#333333",
            state="disabled",
            padx=10,
            pady=10
        )
        self.messages_display.pack(fill=tk.BOTH, expand=True)

        # 메시지 태그 설정 (기존 + 튜터링 모드별)
        self.messages_display.tag_config("user", background="#e3f2fd", font=("Arial", 11, "bold"))
        self.messages_display.tag_config("assistant", background="#f1f8e9")
        self.messages_display.tag_config("system", foreground="#666666", font=("Arial", 9, "italic"))
        self.messages_display.tag_config("timestamp", foreground="#999999", font=("Arial", 8))
        self.messages_display.tag_config("code", background="#f5f5f5", font=("Consolas", 10))

        # 튜터링 모드별 태그
        self.messages_display.tag_config("mode_conversation", foreground="#1976D2")
        self.messages_display.tag_config("mode_code_review", foreground="#388E3C")
        self.messages_display.tag_config("mode_problem_solving", foreground="#F57C00")
        self.messages_display.tag_config("mode_concept", foreground="#7B1FA2")
        self.messages_display.tag_config("mode_debugging", foreground="#D32F2F")

        # 입력 영역
        input_frame = tk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 메시지 입력
        self.message_input = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            height=4,
            font=("Arial", 11),
            background="#ffffff",
            foreground="#333333"
        )
        self.message_input.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.message_input.bind("<Control-Return>", lambda e: self.send_message())

        # 입력 도구 모음
        input_toolbar = tk.Frame(input_frame, bg="#f0f0f0")
        input_toolbar.pack(fill=tk.X)

        # 코드 공유 버튼
        tk.Button(
            input_toolbar,
            text="📋 코드 공유",
            command=self._share_code,
            bg="#FF9800",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=3
        ).pack(side=tk.LEFT, padx=5)

        # 전송 버튼
        self.send_button = tk.Button(
            input_toolbar,
            text="📤 전송",
            command=self.send_message,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # 안내 메시지
        tk.Label(
            input_toolbar,
            text="Ctrl+Enter로 전송",
            bg="#f0f0f0",
            font=("Arial", 8),
            fg="#666666"
        ).pack(side=tk.RIGHT, padx=5)

        # 사이드바 (코드 컨텍스트 + 튜터링 정보)
        sidebar = tk.Frame(content_area, width=300, bg="#f8f9fa")
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        sidebar.pack_propagate(False)

        # 코드 컨텍스트 영역
        tk.Label(
            sidebar,
            text="📝 코드 컨텍스트",
            bg="#f8f9fa",
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        self.code_context_display = scrolledtext.ScrolledText(
            sidebar,
            wrap=tk.WORD,
            font=("Consolas", 9),
            background="#ffffff",
            foreground="#333333",
            height=12,
            state="disabled"
        )
        self.code_context_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 코드 컨텍스트 버튼
        context_toolbar = tk.Frame(sidebar, bg="#f8f9fa")
        context_toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            context_toolbar,
            text="📋 복사",
            command=self._copy_code_context,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            context_toolbar,
            text="🗑️ 삭제",
            command=self._clear_code_context,
            bg="#f44336",
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT, padx=2)

        # 구분선
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=10)

        # 튜터링 세션 정보
        tk.Label(
            sidebar,
            text="🎓 튜터링 세션",
            bg="#f8f9fa",
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        # 세션 정보 표시 영역
        self.session_info_display = scrolledtext.ScrolledText(
            sidebar,
            wrap=tk.WORD,
            font=("Arial", 9),
            background="#ffffff",
            foreground="#333333",
            height=8,
            state="disabled"
        )
        self.session_info_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 세션 관리 버튼
        session_toolbar = tk.Frame(sidebar, bg="#f8f9fa")
        session_toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            session_toolbar,
            text="🔄 새 세션",
            command=self._start_new_tutoring_session,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            session_toolbar,
            text="⏹️ 종료",
            command=self._end_tutoring_session,
            bg="#607D8B",
            fg="white",
            font=("Arial", 8),
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT, padx=2)

        # 상태 바
        self.status_bar = tk.Label(
            main_container,
            text="준비 완료",
            anchor=tk.W,
            bg="#f0f0f0",
            font=("Arial", 9)
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def _setup_bindings(self):
        """키 바인딩 설정"""
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
                title=f"튜터링 세션 {datetime.now().strftime('%H:%M')}",
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

            self._update_status("새 튜터링 세션이 시작되었습니다")
            logger.info(f"새 튜터링 세션 초기화: {self.tutoring_session.session_id}")

        except Exception as e:
            logger.error(f"세션 초기화 실패: {e}")
            messagebox.showerror("오류", f"세션 초기화에 실패했습니다: {e}")

    def _add_welcome_message(self):
        """환영 메시지 추가"""
        mode_descriptions = {
            TutoringMode.CONVERSATION: "자유 대화",
            TutoringMode.CODE_REVIEW: "코드 리뷰",
            TutoringMode.PROBLEM_SOLVING: "문제 해결",
            TutoringMode.CONCEPT_EXPLANATION: "개념 설명",
            TutoringMode.DEBUGGING: "디버깅 도움"
        }

        welcome_text = f"""👋 안녕하세요! 저는 Python AI 튜터입니다.

🎯 현재 모드: {mode_descriptions.get(self.current_mode, '자유 대화')}
📊 수준: {self.student_level.value}

💡 도움을 드릴 수 있는 내용:
• Python 개념 설명 및 예제
• 코드 분석 및 피드백
• 버그 찾기 및 해결 방법
• 최적화 및 베스트 프랙티스
• 문제 해결 단계별 안내

📋 코드를 분석하려면 "코드 공유" 버튼을 클릭하세요.

질문을 입력하거나 코드를 공유해주세요!"""

        self._display_message("system", welcome_text)

    def _display_message(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """메시지 표시"""
        self.messages_display.config(state="normal")

        if timestamp is None:
            timestamp = datetime.now()

        # 메시지 헤더
        role_names = {
            "user": "👤 사용자",
            "assistant": "🤖 튜터",
            "system": "ℹ️  시스템"
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

            self._update_status(f"튜터링 모드 변경: {self.current_mode.value}")
            logger.info(f"튜터링 모드 변경: {self.current_mode.value}")

        except Exception as e:
            logger.error(f"모드 변경 실패: {e}")

    def _on_level_change(self, event):
        """학생 수준 변경"""
        try:
            selected_level = self.level_var.get()
            self.student_level = StudentLevel(selected_level)

            # 튜터 세션 수준 업데이트
            if self.tutoring_session:
                self.tutoring_session.student_level = self.student_level

            self._update_status(f"학생 수준 변경: {self.student_level.value}")
            logger.info(f"학생 수준 변경: {self.student_level.value}")

        except Exception as e:
            logger.error(f"수준 변경 실패: {e}")

    def send_message(self):
        """메시지 전송"""
        if self.is_processing:
            messagebox.showwarning("처리 중", "이전 메시지를 처리 중입니다. 잠시만 기다려주세요.")
            return

        message_text = self.message_input.get(1.0, tk.END).strip()

        if not message_text:
            messagebox.showwarning("빈 메시지", "메시지를 입력해주세요.")
            return

        try:
            self.is_processing = True
            self.send_button.config(state="disabled", text="⏳ 처리 중...")

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
            logger.error(f"메시지 전송 실패: {e}")
            messagebox.showerror("오류", f"메시지 전송에 실패했습니다: {e}")
            self.is_processing = False
            self.send_button.config(state="normal", text="📤 전송")

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
            logger.error(f"AI 응답 생성 실패: {e}")
            error_message = f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
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
            logger.error(f"AI 응답 표시 실패: {e}")

        finally:
            self.is_processing = False
            self.send_button.config(state="normal", text="📤 전송")
            self._update_status("응답 완료")

    def _update_session_info(self):
        """세션 정보 업데이트"""
        try:
            if not self.tutoring_session:
                return

            summary = self.tutor.get_session_summary(self.tutoring_session.session_id)

            info_text = f"""🎯 튜터링 세션 정보

모드: {summary.get('mode', 'N/A')}
수준: {summary.get('student_level', 'N/A')}
주제: {summary.get('topic', '일반')}

📊 통계:
• 메시지: {summary.get('message_count', 0)}개
• 코드 공유: {summary.get('code_shares', 0)}개
• 지속 시간: {int(summary.get('duration', 0) // 60)}분

💡 학습 목표:
"""

            learning_objectives = self.tutoring_session.learning_objectives
            if learning_objectives:
                for obj in learning_objectives:
                    info_text += f"  • {obj}\n"
            else:
                info_text += "  설정되지 않음\n"

            self.session_info_display.config(state="normal")
            self.session_info_display.delete(1.0, tk.END)
            self.session_info_display.insert(1.0, info_text)
            self.session_info_display.config(state="disabled")

            # 상태 바 업데이트
            self.stats_label.config(text=f"메시지: {summary.get('message_count', 0)}")

        except Exception as e:
            logger.error(f"세션 정보 업데이트 실패: {e}")

    def _share_code(self):
        """코드 컨텍스트 공유"""
        if self.on_code_share:
            code = self.on_code_share()
            if code:
                self._set_code_context(code)

                # 튜터 세션에 코드 컨텍스트 추가
                if self.tutoring_session:
                    self.tutoring_session.add_code_context(code)

                messagebox.showinfo("코드 공유", "코드가 컨텍스트에 추가되었습니다.")
            else:
                messagebox.showwarning("코드 없음", "공유할 코드가 없습니다.")
        else:
            messagebox.showinfo("코드 공유", "코드 공유 기능이 준비되지 않았습니다.")

    def _set_code_context(self, code: str):
        """코드 컨텍스트 설정"""
        self.code_context_display.config(state="normal")
        self.code_context_display.delete(1.0, tk.END)
        self.code_context_display.insert(1.0, code)
        self.code_context_display.config(state="disabled")

        self._update_status(f"코드 컨텍스트 업데이트 ({len(code)} 문자)")

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
                self._update_status("코드 컨텍스트 복사됨")
            else:
                messagebox.showwarning("복사 실패", "복사할 코드가 없습니다.")
        except Exception as e:
            logger.error(f"코드 복사 실패: {e}")

    def _clear_code_context(self):
        """코드 컨텍스트 삭제"""
        self.code_context_display.config(state="normal")
        self.code_context_display.delete(1.0, tk.END)
        self.code_context_display.config(state="disabled")

        # 튜터 세션에서도 제거
        if self.tutoring_session:
            self.tutoring_session.context = {}

        self._update_status("코드 컨텍스트 삭제됨")

    def _create_new_conversation(self):
        """새 대화 생성"""
        if messagebox.askyesno("새 대화", "현재 대화를 저장하고 새 대화를 시작하시겠습니까?"):
            self._initialize_session()

    def _show_conversation_history(self):
        """대화 기록 표시"""
        try:
            conversations = self.chat_repository.get_user_conversations(self.current_user_id)

            if not conversations:
                messagebox.showinfo("대화 기록", "저장된 대화가 없습니다.")
                return

            # 간단한 대화 목록 표시
            history_window = tk.Toplevel(self)
            history_window.title("대화 기록")
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
                text="불러오기",
                command=load_selected_conversation,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 10)
            ).pack(pady=10)

        except Exception as e:
            logger.error(f"대화 기록 표시 실패: {e}")
            messagebox.showerror("오류", f"대화 기록을 불러올 수 없습니다: {e}")

    def _start_new_tutoring_session(self):
        """새 튜터링 세션 시작"""
        self._initialize_session()

    def _end_tutoring_session(self):
        """튜터링 세션 종료"""
        try:
            if self.tutoring_session:
                # 평가 요청
                rating = simpledialog.askinteger(
                    "세션 평가",
                    "이 튜터링 세션을 평가해주세요 (1-5점):",
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

                messagebox.showinfo("세션 종료", "튜터링 세션이 종료되었습니다.")
                self._update_status("튜터링 세션 종료됨")

        except Exception as e:
            logger.error(f"튜터링 세션 종료 실패: {e}")

    def load_conversation(self, conversation_id: int):
        """특정 대화 로드"""
        try:
            conversation = self.chat_repository.get_conversation(conversation_id)
            if not conversation:
                messagebox.showerror("오류", "대화를 찾을 수 없습니다.")
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
            self._update_status(f"대화 로드됨: {conversation['title']}")

            logger.info(f"대화 로드: {conversation_id}")

        except Exception as e:
            logger.error(f"대화 로드 실패: {e}")
            messagebox.showerror("오류", f"대화를 로드할 수 없습니다: {e}")

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
