"""
리소스 및 학습 자료 탭 컴포넌트
예제 코드, 학습 가이드, 문제 해결 예시, 베스트 프랙티스를 제공하는 UI 인터페이스
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, Any, List
import json
import os
from loguru import logger

from src.ui.language_manager import get_translator

_ = get_translator()


class ResourcesTab(tk.Frame):
    """리소스 및 학습 자료 탭 컴포넌트"""

    def __init__(self, parent, style_manager, learning_controller=None):
        super().__init__(parent)
        self.style_manager = style_manager
        self.controller = learning_controller
        self.user_id = 1  # 기본 사용자 ID

        # 리소스 데이터
        self.resources_data = {}
        self.current_category = None
        self.current_item = None

        # UI 컴포넌트 참조
        self.content_text = None
        self.code_examples_text = None
        self.search_var = None
        
        self._apply_theme()
        self._create_ui()
        self._load_resources_data()

        logger.info(_("Resources and learning materials tab initialized"))

    def _apply_theme(self):
        """테마 적용"""
        colors = self.style_manager.get_current_theme_colors()
        self.configure(bg=colors["bg"])

    def _create_ui(self):
        """UI 생성"""
        # 상단 검색 및 필터 영역
        self._create_header_panel()

        # 메인 컨텐츠 영역
        main_frame = tk.Frame(self, bg=self.style_manager.get_current_theme_colors()["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 리소스 카테고리 노트북
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 각 카테고리 탭 생성
        self._create_code_examples_tab()
        self._create_learning_guides_tab()
        self._create_troubleshooting_tab()
        self._create_best_practices_tab()

        # 하단 상태바
        self._create_status_bar()

    def _create_header_panel(self):
        """상단 헤더 패널 생성"""
        colors = self.style_manager.get_current_theme_colors()
        header_frame = tk.Frame(self, bg=colors["bg_alt"], height=80)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        # 제목
        title_label = tk.Label(
            header_frame,
            text=_("📚 Resources and Learning Materials"),
            font=("Arial", 16, "bold"),
            bg=colors["bg_alt"],
            fg=colors["fg"]
        )
        title_label.pack(pady=5)

        # 검색 및 필터 프레임
        search_frame = tk.Frame(header_frame, bg=colors["bg_alt"])
        search_frame.pack(fill=tk.X, padx=10)

        # 검색 입력
        tk.Label(
            search_frame,
            text=_("🔍 Search:"),
            bg=colors["bg_alt"],
            fg=colors["fg"],
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=30,
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self._on_search)

        # 검색 버튼
        search_btn = tk.Button(
            search_frame,
            text=_("Search"),
            command=self.perform_search,
            bg=colors["info"],
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        )
        search_btn.pack(side=tk.LEFT, padx=5)

        # 초기화 버튼
        reset_btn = tk.Button(
            search_frame,
            text=_("Reset"),
            command=self.reset_search,
            bg=colors["warning"],
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

    def _create_code_examples_tab(self):
        """예제 코드 라이브러리 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("💻 Code Examples"))

        # 레이아웃: 좌측 카테고리 트리, 우측 코드 내용
        paned_window = tk.PanedWindow(tab, orient=tk.HORIZONTAL, bg=colors["bg"], sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 좌측: 카테고리 및 예제 리스트
        left_frame = tk.Frame(paned_window, bg=colors["bg"])
        paned_window.add(left_frame, minsize=250)

        tk.Label(
            left_frame,
            text=_("Categories"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 5))

        # 예제 카테고리 트리뷰
        self.code_tree = ttk.Treeview(left_frame, selectmode="browse")
        self.code_tree.pack(fill=tk.BOTH, expand=True)

        # 스크롤바
        tree_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.code_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_tree.configure(yscrollcommand=tree_scrollbar.set)

        # 트리 아이템 선택 이벤트
        self.code_tree.bind("<<TreeviewSelect>>", self._on_code_example_selected)

        # 우측: 코드 내용 표시
        right_frame = tk.Frame(paned_window, bg=colors["bg"])
        paned_window.add(right_frame, minsize=400)

        tk.Label(
            right_frame,
            text=_("Example Code"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 5))

        # 코드 표시 영역
        self.code_examples_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.code_examples_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 코드 실행 버튼
        code_btn_frame = tk.Frame(right_frame, bg=colors["bg"])
        code_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            code_btn_frame,
            text=_("▶ Run"),
            command=self.run_example_code,
            bg=colors["success"],
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            code_btn_frame,
            text=_("📋 Copy"),
            command=self.copy_example_code,
            bg=colors["info"],
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

    def _create_learning_guides_tab(self):
        """학습 가이드 및 튜토리얼 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("📖 Learning Guides"))

        # 레이아웃: 좌측 가이드 리스트, 우측 내용
        paned_window = tk.PanedWindow(tab, orient=tk.HORIZONTAL, bg=colors["bg"], sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 좌측: 가이드 리스트
        left_frame = tk.Frame(paned_window, bg=colors["bg"])
        paned_window.add(left_frame, minsize=250)

        tk.Label(
            left_frame,
            text=_("Learning Guides"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 5))

        # 가이드 리스트박스
        guide_list_frame = tk.Frame(left_frame, bg=colors["bg"])
        guide_list_frame.pack(fill=tk.BOTH, expand=True)

        # 난이도 필터
        filter_frame = tk.Frame(guide_list_frame, bg=colors["bg"])
        filter_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(filter_frame, text=_("Difficulty:"), bg=colors["bg"], fg=colors["fg"]).pack(side=tk.LEFT)

        self.guide_level_var = tk.StringVar(value="all")
        level_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.guide_level_var,
            values=["all", "beginner", "intermediate", "advanced"],
            state="readonly",
            width=15
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind("<<ComboboxSelected>>", self._on_guide_level_changed)

        # 가이드 리스트
        self.guides_listbox = tk.Listbox(
            guide_list_frame,
            font=("Arial", 10),
            selectmode=tk.SINGLE,
            bg=colors["editor_bg"],
            fg=colors["editor_fg"],
            selectbackground=colors["primary"],
            selectforeground=colors["editor_bg"]
        )
        self.guides_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 스크롤바
        guide_scrollbar = ttk.Scrollbar(guide_list_frame, orient=tk.VERTICAL, command=self.guides_listbox.yview)
        guide_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.guides_listbox.configure(yscrollcommand=guide_scrollbar.set)

        # 리스트 선택 이벤트
        self.guides_listbox.bind("<<ListboxSelect>>", self._on_guide_selected)

        # 우측: 가이드 내용
        right_frame = tk.Frame(paned_window, bg=colors["bg"])
        paned_window.add(right_frame, minsize=400)

        tk.Label(
            right_frame,
            text=_("Guide Content"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 5))

        # 가이드 내용 표시
        self.guide_content_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.guide_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 진도 추적 버튼
        guide_btn_frame = tk.Frame(right_frame, bg=colors["bg"])
        guide_btn_frame.pack(fill=tk.X, pady=5)

        self.guide_progress_btn = tk.Button(
            guide_btn_frame,
            text=_("✅ Mark as Complete"),
            command=self.mark_guide_complete,
            bg=colors["success"],
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        )
        self.guide_progress_btn.pack(side=tk.LEFT, padx=5)

    def _create_troubleshooting_tab(self):
        """문제 해결 예시 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("🔧 Troubleshooting"))

        # 레이아웃: 좌측 문제 리스트, 우측 해결책
        paned_window = tk.PanedWindow(tab, orient=tk.HORIZONTAL, bg=colors["bg"], sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 좌측: 문제 카테고리 및 리스트
        left_frame = tk.Frame(paned_window, bg=colors["bg"])
        paned_window.add(left_frame, minsize=250)

        tk.Label(
            left_frame,
            text=_("Problem Type"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 5))

        # 문제 카테고리
        problem_category_frame = tk.Frame(left_frame, bg=colors["bg"])
        problem_category_frame.pack(fill=tk.X, pady=(0, 5))

        self.problem_category_var = tk.StringVar(value="syntax")
        categories = [
            ("syntax", _("Syntax Error")),
            ("runtime", _("Runtime Error")),
            ("logical", _("Logical Error")),
            ("performance", _("Performance Issue")),
            ("debugging", _("Debugging"))
        ]

        for value, text in categories:
            rb = tk.Radiobutton(
                problem_category_frame,
                text=text,
                variable=self.problem_category_var,
                value=value,
                command=self._on_problem_category_changed,
                font=("Arial", 9),
                bg=colors["bg"],
                fg=colors["fg"],
                selectcolor=colors["bg_alt"]
            )
            rb.pack(anchor=tk.W)

        # 문제 리스트
        tk.Label(
            left_frame,
            text=_("Common Problems:"),
            font=("Arial", 10, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(10, 0))

        self.problems_listbox = tk.Listbox(
            left_frame,
            font=("Arial", 9),
            selectmode=tk.SINGLE,
            height=15,
            bg=colors["editor_bg"],
            fg=colors["editor_fg"],
            selectbackground=colors["primary"],
            selectforeground=colors["editor_bg"]
        )
        self.problems_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # 리스트 선택 이벤트
        self.problems_listbox.bind("<<ListboxSelect>>", self._on_problem_selected)

        # 우측: 해결책 내용
        right_frame = tk.Frame(paned_window, bg=colors["bg"])
        paned_window.add(right_frame, minsize=400)

        tk.Label(
            right_frame,
            text=_("Solution"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 5))

        # 해결책 표시
        self.solution_content_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"]
        )
        self.solution_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 유용한 도구 버튼
        solution_btn_frame = tk.Frame(right_frame, bg=colors["bg"])
        solution_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            solution_btn_frame,
            text=_("💡 Show Related Example"),
            command=self.show_related_example,
            bg=colors["info"],
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            solution_btn_frame,
            text=_("🔍 Learn More"),
            command=self.learn_more_about_problem,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

    def _create_best_practices_tab(self):
        """베스트 프랙티스 가이드 탭 생성"""
        colors = self.style_manager.get_current_theme_colors()
        tab = tk.Frame(self.notebook, bg=colors["bg"])
        self.notebook.add(tab, text=_("⭐ Best Practices"))

        # 메인 컨텐츠 영역
        content_frame = tk.Frame(tab, bg=colors["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 주제 영역
        topics_frame = tk.Frame(content_frame, bg=colors["bg"])
        topics_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            topics_frame,
            text=_("Coding Best Practices Topics"),
            font=("Arial", 12, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 10))

        # 주제 카드들
        practices_topics = [
            {
                "id": "code_style",
                "title": _("📝 Code Style"),
                "description": _("PEP 8 guidelines, naming conventions, code formatting"),
                "icon": "📝"
            },
            {
                "id": "error_handling",
                "title": _("⚠️ Error Handling"),
                "description": _("Exception handling, error messages, debugging"),
                "icon": "⚠️"
            },
            {
                "id": "performance",
                "title": _("🚀 Performance Optimization"),
                "description": _("Algorithms, memory management, efficiency"),
                "icon": "🚀"
            },
            {
                "id": "security",
                "title": _("🔒 Security"),
                "description": _("Input validation, data protection, secure coding"),
                "icon": "🔒"
            },
            {
                "id": "testing",
                "title": _("🧪 Testing"),
                "description": _("Unit testing, test-driven development"),
                "icon": "🧪"
            },
            {
                "id": "documentation",
                "title": _("📚 Documentation"),
                "description": _("Comments, docstrings, README writing"),
                "icon": "📚"
            }
        ]

        # 카드 생성
        self.practice_buttons = {}
        for topic in practices_topics:
            card = tk.Frame(
                topics_frame,
                bg=colors["bg_alt"],
                relief=tk.RAISED,
                borderwidth=2
            )
            card.pack(fill=tk.X, pady=5)

            # 카드 내용
            content = tk.Frame(card, bg=colors["bg_alt"])
            content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(
                content,
                text=topic["title"],
                font=("Arial", 11, "bold"),
                bg=colors["bg_alt"],
                fg=colors["fg"]
            ).pack(anchor=tk.W)

            tk.Label(
                content,
                text=topic["description"],
                font=("Arial", 9),
                bg=colors["bg_alt"],
                fg=colors["fg"],
                wraplength=500
            ).pack(anchor=tk.W, pady=(5, 0))

            # 보기 버튼
            btn = tk.Button(
                card,
                text=_("📖 View"),
                command=lambda t=topic["id"]: self.show_practice_detail(t),
                bg=colors["info"],
                fg="white",
                font=("Arial", 9),
                relief=tk.FLAT
            )
            btn.pack(side=tk.RIGHT, padx=10, pady=5)

            self.practice_buttons[topic["id"]] = btn

        # 하단: 베스트 프랙티스 요약
        summary_frame = tk.Frame(content_frame, bg=colors["bg"])
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(
            summary_frame,
            text=_("📋 Best Practices Summary"),
            font=("Arial", 11, "bold"),
            bg=colors["bg"],
            fg=colors["fg"]
        ).pack(anchor=tk.W, pady=(0, 5))

        self.practices_summary_text = scrolledtext.ScrolledText(
            summary_frame,
            wrap=tk.WORD,
            font=("Arial", 9),
            bg=colors["editor_bg"],
            fg=colors["editor_fg"],
            height=8
        )
        self.practices_summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_status_bar(self):
        """상태바 생성"""
        colors = self.style_manager.get_current_theme_colors()
        status_bar = tk.Frame(self, bg=colors["bg_alt"], height=30)
        status_bar.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = tk.Label(
            status_bar,
            text=_("Resources loaded"),
            bg=colors["bg_alt"],
            fg=colors["fg_alt"],
            font=("Arial", 9),
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # 리소스 카운트
        self.resource_count_label = tk.Label(
            status_bar,
            text=_("Total resources: 0"),
            bg=colors["bg_alt"],
            fg=colors["fg_alt"],
            font=("Arial", 9)
        )
        self.resource_count_label.pack(side=tk.RIGHT, padx=10)

    def _load_resources_data(self):
        """리소스 데이터 로드"""
        try:
            # 예제 코드 데이터
            self._load_code_examples()

            # 학습 가이드 데이터
            self._load_learning_guides()

            # 문제 해결 데이터
            self._load_troubleshooting_data()

            # 베스트 프랙티스 데이터
            self._load_best_practices()

            # 베스트 프랙티스 요약 업데이트
            self._update_practices_summary()

            logger.info("리소스 데이터 로드 완료")

        except Exception as e:
            logger.error(f"리소스 데이터 로드 실패: {e}")
            self._load_test_data()

    def _load_code_examples(self):
        """예제 코드 데이터 로드"""
        # 예제 카테고리와 예제들
        code_examples = {
            "기초": {
                "Hello World": {
                    "code": 'def hello_world():\n    """Hello World 프로그램"""\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    hello_world()',
                    "description": "프로그래밍의 전통적인 시작입니다!"
                },
                "변수와 자료형": {
                    "code": '# 변수와 자료형 예제\nname = "Alice"\nage = 25\nheight = 165.5\nis_student = True\n\n# 출력\nprint(f"이름: {name}")\nprint(f"나이: {age}세")\nprint(f"키: {height}cm")\nprint(f"학생 여부: {is_student}")',
                    "description": "Python의 기본 자료형을 학습합니다."
                },
                "조건문": {
                    "code": '# if-elif-else 문\nscore = 85\n\nif score >= 90:\n    grade = "A"\nelif score >= 80:\n    grade = "B"\nelif score >= 70:\n    grade = "C"\nelse:\n    grade = "F"\n\nprint(f"점수: {score}, 등급: {grade}")',
                    "description": "조건에 따라 다른 동작을 수행합니다."
                }
            },
            "반복문": {
                "for 루프": {
                    "code": '# for 루프 예제\nprint("1부터 5까지 출력:")\nfor i in range(1, 6):\n    print(f"숫자: {i}")\n\n# 리스트 순회\nfruits = ["사과", "바나나", "체리"]\nprint("\\n과일 목록:")\nfor fruit in fruits:\n    print(f"- {fruit}")',
                    "description": "반복적인 작업을 위해 for 루프를 사용합니다."
                },
                "while 루프": {
                    "code": '# while 루프 예제\ncount = 0\nprint("카운트다운:")\nwhile count < 5:\n    print(f"{5 - count}...")\n    count += 1\nprint("발사!")',
                    "description": "조건이 참인 동안 반복합니다."
                }
            },
            "함수": {
                "기본 함수": {
                    "code": '# 함수 정의와 호출\ndef greet(name):\n    """인사말을 출력하는 함수"""\n    return f"안녕하세요, {name}님!"\n\n# 함수 호출\nmessage = greet("철수")\nprint(message)\n\n# 여러 값 반환\ndef calculate(a, b):\n    return a + b, a - b, a * b, a / b\n\nadd, sub, mul, div = calculate(10, 5)\nprint(f"합: {add}, 차: {sub}, 곱: {mul}, 나눗셈: {div:.2f}")',
                    "description": "코드를 재사용 가능한 함수로 만듭니다."
                },
                "람다 함수": {
                    "code": '# 람다 함수 예제\ndef square(x):\n    return x ** 2\n\nsquare_lambda = lambda x: x ** 2\n\nprint(square(5))\nprint(square_lambda(5))\n\nnumbers = [1, 2, 3, 4, 5]\nsquared = list(map(lambda x: x**2, numbers))\nprint(f"제곱: {squared}")',
                    "description": "간단한 함수를 한 줄로 정의합니다."
                }
            },
            "자료구조": {
                "리스트": {
                    "code": '# 리스트 예제\nfruits = ["사과", "바나나", "체리"]\n\n# 추가\nfruits.append("오렌지")\n# 삭제\nfruits.remove("바나나")\n# 수정\nfruits[0] = "배"\n\n# 슬라이싱\nprint(f"처음 2개: {fruits[:2]}")\nprint(f"마지막 2개: {fruits[-2:]}")\n\n# 리스트 컴프리헨션\nnumbers = [1, 2, 3, 4, 5]\neven_squares = [x**2 for x in numbers if x % 2 == 0]\nprint(f"짝수 제곱: {even_squares}")',
                    "description": "순서가 있는 자료를 저장합니다."
                },
                "딕셔너리": {
                    "code": '# 딕셔너리 예제\nperson = {\n    "name": "Alice",\n    "age": 25,\n    "city": "Seoul"\n}\n\n# 접근\nprint(f"이름: {person[\'name\']}")\n# 추가\nperson["job"] = "개발자"\n# 수정\nperson["age"] = 26\n\n# 순회\nprint("\\n사람 정보:")\nfor key, value in person.items():\n    print(f"{key}: {value}")',
                    "description": "키-값 쌍으로 자료를 저장합니다."
                }
            },
            "클래스": {
                "기본 클래스": {
                    "code": '# 클래스 정의\nclass Dog:\n    def __init__(self, name, breed):\n        self.name = name\n        self.breed = breed\n\n    def bark(self):\n        return f"{self.name}가 멍멍!"\n\n    def info(self):\n        return f"{self.name}는 {self.breed}종입니다"\n\n# 인스턴스 생성\nmy_dog = Dog("바둑이", "시바")\nprint(my_dog.bark())\nprint(my_dog.info())',
                    "description": "객체 지향 프로그래밍의 기초입니다."
                },
                "상속": {
                    "code": '# 클래스 상속\nclass Animal:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        pass\n\nclass Dog(Animal):\n    def speak(self):\n        return f"{self.name}가 멍멍!"\n\nclass Cat(Animal):\n    def speak(self):\n        return f"{self.name}가 야옹!"\n\n# 다형성\nanimals = [Dog("바둑이"), Cat("나비")]\nfor animal in animals:\n    print(animal.speak())',
                    "description": "기존 클래스를 확장합니다."
                }
            }
        }

        # 트리뷰에 로드
        for category, examples in code_examples.items():
            category_id = self.code_tree.insert("", "end", text=category)
            for example_name, example_data in examples.items():
                self.code_tree.insert(
                    category_id,
                    "end",
                    text=example_name,
                    values=(example_data["code"], example_data["description"])
                )

        self.resources_data['code_examples'] = code_examples

    def _load_learning_guides(self):
        """학습 가이드 데이터 로드"""
        guides = {
            "Python 기초": {
                "level": "beginner",
                "content": "# Python 기초 가이드\n\n## 1. Python 소개\nPython은 배우기 쉽고 강력한 프로그래밍 언어입니다.\n\n## 2. 설치 및 설정\n- Python 공식 웹사이트에서 설치\n- IDE 선택 (VS Code, PyCharm 등)\n\n## 3. 기초 문법\n- 변수: 데이터를 저장하는 공간\n- 자료형: 문자열, 숫자, 불린\n- 연산자: 산술, 비교, 논리\n\n## 4. 제어문\n- if/elif/else: 조건문\n- for/while: 반복문\n\n## 5. 함수\n- 코드 재사용을 위한 함수 정의\n- 매개변수와 반환값\n\n## 연습 문제\n1. 1부터 100까지 합계 계산 프로그램 작성\n2. 구구단 프로그램 작성\n3. 간단한 계산기 만들기"
            },
            "객체 지향 프로그래밍": {
                "level": "intermediate",
                "content": "# 객체 지향 프로그래밍 가이드\n\n## 1. 클래스와 객체\n- 클래스: 객체의 설계도\n- 객체: 클래스의 인스턴스\n\n## 2. 주요 개념\n- **캡슐화**: 데이터를 보호\n- **상속**: 기존 코드 재사용\n- **다형성**: 다양한 형태로 동작\n- **추상화**: 복잡성 숨기기\n\n## 3. 예시\n프로그램 코드 예시\n\n## 연습 문제\n1. 학생 관리 프로그램 작성\n2. 은행 계좌 클래스 만들기\n3. 도서 관리 시스템 구현"
            },
            "고급 Python 기법": {
                "level": "advanced",
                "content": "# 고급 Python 기법 가이드\n\n## 1. 데코레이터\n함수를 감싸는 기능\n\n## 2. 제너레이터\n메모리 효율적인 반복자\n\n## 3. 컨텍스트 매니저\n리소스 관리 자동화\n\n## 4. 메타클래스\n클래스의 클래스\n\n## 연습 문제\n1. 커스텀 데코레이터 작성\n2. 제너레이터로 무한 시퀀스 만들기\n3. 컨텍스트 매니저 구현"
            }
        }

        # 리스트박스에 로드
        self.guides_listbox.delete(0, tk.END)
        for guide_name, guide_data in guides.items():
            level_text = {
                "beginner": "초급",
                "intermediate": "중급",
                "advanced": "고급"
            }.get(guide_data["level"], guide_data["level"])
            self.guides_listbox.insert(tk.END, f"[{level_text}] {guide_name}")

        self.resources_data['learning_guides'] = guides

    def _load_troubleshooting_data(self):
        """문제 해결 데이터 로드"""
        troubleshooting = {
            "syntax": {
                "IndentationError": {
                    "title": "들여쓰기 오류",
                    "solution": "# 들여쓰기 오류 해결\n\n## 문제\n들여쓰기 오류 발생\n\n## 원인\nPython은 들여쓰기로 코드 블록을 구분합니다.\n\n## 해결 방법\n4칸 들여쓰기 사용\n\n## 팁\n- 일관된 들여쓰기 사용 (4칸 권장)\n- Tab과 Space 혼합 사용 금지\n- IDE의 자동 들여쓰기 기능 활용",
                    "related_examples": ["조건문", "함수"]
                },
                "SyntaxError: invalid syntax": {
                    "title": "문법 오류",
                    "solution": "# 문법 오류 해결\n\n## 흔한 문법 오류들\n\n### 1. 콜론(:) 누락\nif 다음에 콜론 필요\n\n### 2. 괄호 불일치\n괄호 개수 맞아야 함\n\n### 3. 따옴표 불일치\n따옴표 쌍이 맞아야 함\n\n## 예방 팁\n- IDE의 문법 하이라이팅 활용\n- 코드를 작성하면서 즉시 테스트"
                }
            },
            "runtime": {
                "NameError": {
                    "title": "이름 오류",
                    "solution": "# NameError 해결\n\n## 문제\n정의되지 않은 변수 사용\n\n## 해결 방법\n먼저 변수 정의\n\n## 흔한 원인\n1. 오타\n2. 정의 전 사용\n3. 스코프 문제\n\n## 예방 방법\n- 변수명 일관성 유지\n- 함수 상단에 변수 정의"
                },
                "TypeError": {
                    "title": "타입 오류",
                    "solution": "# TypeError 해결\n\n## 흔한 타입 오류\n\n### 1. 문자열과 숫자 연결\n형변환 필요\n\n### 2. 숫자 대신 문자열 사용\n타입 확인 필요\n\n## 예방 방법\n- 타입 확인: type(variable)\n- 명시적 형변환 사용"
                }
            },
            "logical": {
                "무한 루프": {
                    "title": "무한 루프",
                    "solution": "# 무한 루프 해결\n\n## 문제\n종료 조건 없는 반복문\n\n## 해결 방법\n종료 조건 포함\n\n## 예방 방법\n- 항상 종료 조건 포함\n- 카운터 변수 사용\n- 최대 반복 횟수 설정"
                },
                "오프 바이 원 에러": {
                    "title": "오프 바이 원 에러",
                    "solution": "# 오프 바이 원 에러 해결\n\n## 문제\n인덱스 시작 오류\n\n## 해결 방법\n인덱스 0부터 시작 확인\n\n## 예방 방법\n- 인덱스가 0부터 시작함 기억\n- 직접 순회보다는 for item in list 사용"
                }
            },
            "performance": {
                "느린 루프": {
                    "title": "성능 최적화",
                    "solution": "# 성능 최적화 가이드\n\n## 흔한 성능 문제들\n\n### 1. 루프 내 불필요한 연산\n반복되는 계산 루프 밖으로\n\n### 2. 리스트 대신 집합 사용\n검색 시간 단축\n\n## 최적화 팁\n- 프로파일링으로 병목 찾기\n- 적절한 자료구조 선택\n- 불필요한 연산 제거"
                }
            },
            "debugging": {
                "디버깅 기법": {
                    "title": "디버깅 방법",
                    "solution": "# 효과적인 디버깅 기법\n\n## 1. print 디버깅\n중간 결과 출력\n\n## 2. pdb 디버거\n중단점 설정\n\n## 3. 예외 처리\n오류 메시지 확인\n\n## 디버깅 팁\n- 작은 단위로 테스트\n- 오류 메시지 주의 깊게 읽기\n- 재현 가능한 최소 예제 만들기"
                }
            }
        }

        self.resources_data['troubleshooting'] = troubleshooting

        # 기본 카테고리 로드
        self._on_problem_category_changed()

    def _load_best_practices(self):
        """베스트 프랙티스 데이터 로드"""
        practices = {
            "code_style": "# 코드 스타일 베스트 프랙티스\n\n## PEP 8 가이드라인\n\n### 1. 들여쓰기\n- 4칸 공백 사용 (Tab 혼용 금지)\n- 일관된 들여쓰기 유지\n\n### 2. 명명 규칙\n변수/함수: snake_case\n클래스: PascalCase\n상수: UPPER_CASE\n\n### 3. 줄 길이\n- 최대 79자 (코드)\n- 최대 72자 (주석/문서)\n\n### 4. 공백\n연산자 주변 공백 사용\n괄호 내부 불필요한 공백 제거\n\n## 코드 포맷팅 도구\n- **Black**: 자동 코드 포맷터\n- **isort**: import 정렬\n- **flake8**: 스타일 검사",

            "error_handling": "# 에러 처리 베스트 프랙티스\n\n## 1. 예외 처리 기본\n\n### 구체적 예외 잡기\n구체적인 예외 타입 사용\n\n### 예외 메시지 제공\n명확한 에러 메시지 작성\n\n## 2. 에러 처리 전략\n\n### LBYL (Look Before You Leap)\n검사 후 수행\n\n### EAFP (Easier to Ask Forgiveness)\n수행 후 예외 처리\n\n## 3. 커스텀 예외\n사용자 정의 예외 클래스\n\n## 4. finally 활용\n리소스 정리 보장",

            "performance": "# 성능 최적화 베스트 프랙티스\n\n## 1. 알고리즘 최적화\n\n### 시간 복잡도 고려\nO(n) vs O(n^2)\n\n## 2. 메모리 관리\n\n### 제너레이터 사용\n메모리 효율적 반복\n\n### 대용량 파일 처리\n줄 단위 읽기\n\n## 3. 자료구조 선택\n\n### 리스트 vs 집합\n검색 속도 차이\n\n### 딕셔너리 최적화\n한 번만 접근\n\n## 4. 문자열 연결\njoin() 메서드 사용",

            "security": "# 보안 코딩 베스트 프랙티스\n\n## 1. 입력 검증\n\n### 사용자 입력 검사\n타입과 범위 확인\n\n### SQL Injection 방지\n파라미터화된 쿼리 사용\n\n## 2. 데이터 보호\n\n### 비밀번호 처리\n해시 저장\n\n### 민감 정보 제거\n로그에서 비밀번호 제거\n\n## 3. 파일 시스템 보안\n\n### 경로 검증\n허용된 경로만 접근\n\n## 4. 의존성 관리\n\n### 패키지 업데이트\n정기적 업데이트\n\n### 보안 스캔\n취약점 검사",

            "testing": "# 테스트 베스트 프랙티스\n\n## 1. 단위 테스트\n\n### 기본 테스트 구조\nunittest 또는 pytest 사용\n\n### 테스트 케이스 작성\n정상, 경계, 예외 케이스\n\n## 2. 테스트 주도 개발 (TDD)\n\n### Red-Green-Refactor\n1. 실패하는 테스트 작성\n2. 최소한의 구현으로 통과\n3. 코드 개선\n\n## 3. 테스트 더블\n\n### Mock 사용\n외부 의존성 격리\n\n## 4. 테스트 커버리지\n\n### 커버리지 측정\ntest-cov 사용\n\n### 목표 커버리지\n핵심: 90% 이상\n전체: 80% 이상\n\n## 5. 통합 테스트\n전체 흐름 테스트\n\n## 테스트 팁\n- 독립적인 테스트 유지\n- 명확한 테스트 이름 사용\n- 하나의 테스트는 하나의 것만 테스트",

            "documentation": "# 문서화 베스트 프랙티스\n\n## 1. 코드 주석\n\n### 좋은 주석의 원칙\n코드를 반복하지 말고 이유 설명\n\n### 주석이 필요한 경우\n- 복잡한 알고리즘 설명\n- 비즈니스 로직의 이유\n- 버전 관리 정보\n- TODO/FIXME 마크\n\n## 2. Docstring 작성\n\n### 함수 문서화\nArgs, Returns, Raises 설명\n\n### 클래스 문서화\nAttributes 설명\n\n## 3. README 작성\n\n### 프로젝트 README 템플릿\n설치, 사용법, 기능, 기여, 라이선스\n\n## 4. API 문서화\n\n### Sphinx 사용\n자동 문서 생성\n\n### docstring 형식\nGoogle 또는 NumPy 스타일\n\n## 5. 코드 예제\n\n### 사용법 예시 제공\n실제 동작하는 코드 예시\n\n## 6. 버전 관리\n변경 이력 기록\n\n## 문서화 팁\n- 코드와 문서 동시 업데이트\n- 명확하고 간결한 언어 사용\n- 실용적인 예시 포함\n- 문서도 테스트 필요"
        }

        self.resources_data['best_practices'] = practices

    def _load_test_data(self):
        """테스트 데이터 로드"""
        logger.warning("테스트 데이터 사용")

    def _update_practices_summary(self):
        """베스트 프랙티스 요약 업데이트"""
        summary_text = """📋 코딩 베스트 프랙티스 핵심 요약

📝 코드 스타일
- PEP 8 가이드라인 준수
- 일관된 명명 규칙 사용
- 명확한 변수/함수 이름

⚠️ 에러 처리
- 구체적 예외 처리
- 의미 있는 에러 메시지
- 자원 해제 보장 (finally 활용)

🚀 성능
- 적절한 자료구조 선택
- 불필요한 연산 제거
- 메모리 효율적 코드 작성

🔒 보안
- 입력 검증 수행
- 민감 정보 보호
- 의존성 정기 업데이트

🧪 테스트
- 단위 테스트 작성
- 경계값 테스트 수행
- 높은 테스트 커버리지 유지

📚 문서화
- 명확한 주석 작성
- docstring 활용
- 사용 예시 제공

💡 핵심 원칙
가독성이 좋은 코드가 좋은 코드입니다!
다른 사람이 쉽게 이해할 수 있는 코드를 작성하세요."""

        self.practices_summary_text.delete(1.0, tk.END)
        self.practices_summary_text.insert(tk.END, summary_text)

    # 이벤트 핸들러 메서드들

    def _on_search(self, event=None):
        """검색 입력 이벤트"""
        # 실시간 검색 기능 (선택적)
        pass

    def perform_search(self):
        """검색 수행"""
        search_term = self.search_var.get().strip().lower()

        if not search_term:
            messagebox.showinfo("검색", "검색어를 입력해주세요.")
            return

        # 모든 리소스에서 검색
        results = []

        # 예제 코드 검색
        code_examples = self.resources_data.get('code_examples', {})
        for category, examples in code_examples.items():
            for example_name, example_data in examples.items():
                if (search_term in example_name.lower() or
                    search_term in example_data.get("description", "").lower() or
                    search_term in example_data.get("code", "").lower()):
                    results.append({
                        "type": "예제 코드",
                        "location": f"{category} > {example_name}",
                        "data": example_data
                    })

        # 검색 결과 표시
        if results:
            result_text = f"🔍 '{search_term}' 검색 결과: {len(results)}개 발견\n\n"
            for i, result in enumerate(results[:10], 1):  # 최대 10개 표시
                result_text += f"{i}. [{result['type']}] {result['location']}\n"

            if len(results) > 10:
                result_text += f"\n... 그 외 {len(results) - 10}개"

            messagebox.showinfo("검색 결과", result_text)
            self.status_label.config(text=f"검색 완료: {len(results)}개 발견")
        else:
            messagebox.showinfo("검색 결과", f"'{search_term}'에 대한 결과가 없습니다.")
            self.status_label.config(text="검색 결과 없음")

    def reset_search(self):
        """검색 초기화"""
        self.search_var.set("")
        self.status_label.config(text="검색 초기화 완료")

    def _on_code_example_selected(self, event):
        """예제 코드 선택 이벤트"""
        selection = self.code_tree.selection()
        if selection:
            item = selection[0]
            values = self.code_tree.item(item, "values")

            if values:  # 예제 코드 선택
                code = values[0]
                description = values[1]

                # 코드 표시
                self.code_examples_text.delete(1.0, tk.END)
                self.code_examples_text.insert(tk.END, f"# {description}\n\n")
                self.code_examples_text.insert(tk.END, code)

                self.current_item = {"code": code, "description": description}
                self.status_label.config(text=f"예제 코드 로드됨")

    def run_example_code(self):
        """예제 코드 실행"""
        if self.current_item and "code" in self.current_item:
            code = self.current_item["code"]
            try:
                # 코드 실행
                exec(code, {"__name__": "__main__"})
                messagebox.showinfo("실행 완료", "✅ 코드가 성공적으로 실행되었습니다!")
                self.status_label.config(text="코드 실행 성공")
            except Exception as e:
                messagebox.showerror("실행 오류", f"코드 실행 중 오류가 발생했습니다:\n{str(e)}")
                self.status_label.config(text="코드 실행 실패")
        else:
            messagebox.showwarning("경고", "먼저 실행할 예제 코드를 선택해주세요.")

    def copy_example_code(self):
        """예제 코드 복사"""
        if self.current_item and "code" in self.current_item:
            code = self.current_item["code"]
            self.clipboard_clear()
            self.clipboard_append(code)
            messagebox.showinfo("복사 완료", "코드가 클립보드에 복사되었습니다!")
            self.status_label.config(text="코드 복사 완료")
        else:
            messagebox.showwarning("경고", "먼저 복사할 예제 코드를 선택해주세요.")

    def _on_guide_level_changed(self, event=None):
        """가이드 레벨 변경 이벤트"""
        selected_level = self.guide_level_var.get()

        # 가이드 필터링
        self.guides_listbox.delete(0, tk.END)

        guides = self.resources_data.get('learning_guides', {})
        for guide_name, guide_data in guides.items():
            guide_level = guide_data.get("level", "beginner")

            if selected_level == "all" or guide_level == selected_level:
                level_text = {
                    "beginner": "초급",
                    "intermediate": "중급",
                    "advanced": "고급"
                }.get(guide_level, guide_level)
                self.guides_listbox.insert(tk.END, f"[{level_text}] {guide_name}")

    def _on_guide_selected(self, event):
        """가이드 선택 이벤트"""
        selection = self.guides_listbox.curselection()
        if selection:
            index = selection[0]
            guide_text = self.guides_listbox.get(index)

            # 가이드 이름 추출
            guide_name = guide_text.split("] ")[1]

            guides = self.resources_data.get('learning_guides', {})
            if guide_name in guides:
                guide_content = guides[guide_name]['content']

                # 내용 표시
                self.guide_content_text.delete(1.0, tk.END)
                self.guide_content_text.insert(tk.END, guide_content)

                self.current_item = {"type": "guide", "name": guide_name}
                self.status_label.config(text=f"가이드: {guide_name}")

    def mark_guide_complete(self):
        """가이드 학습 완료 표시"""
        if self.current_item and self.current_item.get("type") == "guide":
            guide_name = self.current_item.get("name")

            # 완료 표시 (실제로는 데이터베이스에 저장)
            messagebox.showinfo("완료", f"🎉 '{guide_name}' 학습 완료!")

            # 진도 버튼 업데이트
            self.guide_progress_btn.config(text="✅ 완료됨", state=tk.DISABLED)
            self.status_label.config(text=f"가이드 완료 표시: {guide_name}")

    def _on_problem_category_changed(self):
        """문제 카테고리 변경 이벤트"""
        category = self.problem_category_var.get()

        # 문제 리스트 업데이트
        self.problems_listbox.delete(0, tk.END)

        troubleshooting = self.resources_data.get('troubleshooting', {})
        if category in troubleshooting:
            for problem_name, problem_data in troubleshooting[category].items():
                self.problems_listbox.insert(tk.END, problem_name)

    def _on_problem_selected(self, event):
        """문제 선택 이벤트"""
        selection = self.problems_listbox.curselection()
        if selection:
            index = selection[0]
            problem_name = self.problems_listbox.get(index)

            category = self.problem_category_var.get()
            troubleshooting = self.resources_data.get('troubleshooting', {})

            if category in troubleshooting and problem_name in troubleshooting[category]:
                solution = troubleshooting[category][problem_name]

                # 해결책 표시
                self.solution_content_text.delete(1.0, tk.END)
                self.solution_content_text.insert(tk.END, f"# {solution['title']}\n\n")
                self.solution_content_text.insert(tk.END, solution['solution'])

                self.current_item = {
                    "type": "problem",
                    "name": problem_name,
                    "data": solution
                }
                self.status_label.config(text=f"문제: {problem_name}")

    def show_related_example(self):
        """관련 예제 표시"""
        if self.current_item and self.current_item.get("type") == "problem":
            problem_data = self.current_item.get("data", {})
            related = problem_data.get("related_examples", [])

            if related:
                examples_text = "💡 관련 예제:\n\n"
                for i, example_name in enumerate(related, 1):
                    examples_text += f"{i}. {example_name}\n"

                messagebox.showinfo("관련 예제", examples_text)
            else:
                messagebox.showinfo("관련 예제", "이 주제와 관련된 예제가 없습니다.")

    def learn_more_about_problem(self):
        """문제에 대해 더 알아보기"""
        if self.current_item and self.current_item.get("type") == "problem":
            problem_name = self.current_item.get("name")
            messagebox.showinfo("더 알아보기", f"'{problem_name}'에 대한 추가 자료를 준비 중입니다.\n\n곧 제공될 예정입니다!")

    def show_practice_detail(self, practice_id):
        """베스트 프랙티스 상세 보기"""
        practices = self.resources_data.get('best_practices', {})

        if practice_id in practices:
            practice_content = practices[practice_id]

            # 새 창으로 상세 내용 표시
            detail_window = tk.Toplevel(self)
            detail_window.title(f"베스트 프랙티스: {practice_id}")
            detail_window.geometry("800x600")

            # 내용 표시
            content_text = scrolledtext.ScrolledText(
                detail_window,
                wrap=tk.WORD,
                font=("Arial", 10)
            )
            content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            content_text.insert(tk.END, practice_content)
            content_text.config(state=tk.DISABLED)

            # 닫기 버튼
            close_btn = tk.Button(
                detail_window,
                text="닫기",
                command=detail_window.destroy,
                bg="#f44336",
                fg="white",
                font=("Arial", 10)
            )
            close_btn.pack(pady=10)

            self.status_label.config(text=f"베스트 프랙티스: {practice_id}")


if __name__ == "__main__":
    # 리소스 탭 테스트
    print("🧪 리소스 탭 테스트")

    root = tk.Tk()
    root.title("리소스 탭 테스트")
    root.geometry("1200x800")

    resources_tab = ResourcesTab(root)
    resources_tab.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

    print("✅ 리소스 탭 테스트 완료")