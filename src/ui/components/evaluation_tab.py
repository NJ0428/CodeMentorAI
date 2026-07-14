"""
평가 시스템 탭
퀴즈, 코딩 문제, 자동 평가 기능 UI
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
from loguru import logger

from src.evaluation import (
    QuizGenerator, DifficultyLevel, Quiz,
    CodingProblemGenerator, ProblemCategory,
    AutoEvaluator, EvaluationStatus,
    FeedbackGenerator, FeedbackType, FeedbackLevel
)


class EvaluationTab(ttk.Frame):
    """평가 시스템 탭"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        # 시스템 컴포넌트 초기화
        self.quiz_generator = QuizGenerator()
        self.problem_generator = CodingProblemGenerator()
        self.auto_evaluator = AutoEvaluator()
        self.feedback_generator = FeedbackGenerator()

        # 현재 상태
        self.current_quiz = None
        self.current_problem = None
        self.user_id = 1  # 기본 사용자 ID
        self.quiz_answers = {}
        self.coding_code = ""

        # UI 초기화
        self.setup_ui()

        # 샘플 데이터 로드
        self.load_sample_data()

        logger.info("평가 시스템 탭 초기화 완료")

    def setup_ui(self):
        """UI 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 노트북 (탭)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 퀴즈 탭
        self.quiz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quiz_frame, text="퀴즈")
        self.setup_quiz_tab()

        # 코딩 문제 탭
        self.coding_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.coding_frame, text="코딩 문제")
        self.setup_coding_tab()

        # 결과 및 피드백 탭
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="결과 및 피드백")
        self.setup_results_tab()

    def setup_quiz_tab(self):
        """퀴즈 탭 설정"""
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(self.quiz_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 난이도 선택
        ttk.Label(control_frame, text="난이도:").pack(side=tk.LEFT)
        self.quiz_difficulty = tk.StringVar(value="beginner")
        difficulty_combo = ttk.Combobox(
            control_frame,
            textvariable=self.quiz_difficulty,
            values=["beginner", "intermediate", "advanced"],
            state="readonly",
            width=10
        )
        difficulty_combo.pack(side=tk.LEFT, padx=5)

        # 주제 선택
        ttk.Label(control_frame, text="주제:").pack(side=tk.LEFT, padx=(10, 0))
        self.quiz_topic = tk.StringVar(value="variables")
        topic_combo = ttk.Combobox(
            control_frame,
            textvariable=self.quiz_topic,
            values=["variables", "conditionals", "loops", "functions", "data_structures", "oop"],
            state="readonly",
            width=15
        )
        topic_combo.pack(side=tk.LEFT, padx=5)

        # 퀴즈 생성 버튼
        generate_btn = ttk.Button(
            control_frame,
            text="퀴즈 생성",
            command=self.generate_new_quiz
        )
        generate_btn.pack(side=tk.LEFT, padx=10)

        # 퀴즈 제출 버튼
        submit_btn = ttk.Button(
            control_frame,
            text="퀴즈 제출",
            command=self.submit_quiz
        )
        submit_btn.pack(side=tk.LEFT, padx=5)

        # 퀴즈 영역
        quiz_area_frame = ttk.Frame(self.quiz_frame)
        quiz_area_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 퀴즈 정보
        self.quiz_info_label = ttk.Label(quiz_area_frame, text="퀴즈를 생성하세요")
        self.quiz_info_label.pack(anchor=tk.W, pady=5)

        # 문제 영역
        self.quiz_questions_frame = ttk.Frame(quiz_area_frame)
        self.quiz_questions_frame.pack(fill=tk.BOTH, expand=True)

        # 스크롤 프레임
        quiz_canvas = tk.Canvas(self.quiz_questions_frame)
        quiz_scrollbar = ttk.Scrollbar(self.quiz_questions_frame, orient="vertical", command=quiz_canvas.yview)
        self.quiz_questions_inner = ttk.Frame(quiz_canvas)

        self.quiz_questions_inner.bind(
            "<Configure>",
            lambda e: quiz_canvas.configure(scrollregion=quiz_canvas.bbox("all"))
        )

        quiz_canvas.create_window((0, 0), window=self.quiz_questions_inner, anchor="nw")
        quiz_canvas.configure(yscrollcommand=quiz_scrollbar.set)

        quiz_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        quiz_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_coding_tab(self):
        """코딩 문제 탭 설정"""
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(self.coding_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 난이도 선택
        ttk.Label(control_frame, text="난이도:").pack(side=tk.LEFT)
        self.coding_difficulty = tk.StringVar(value="beginner")
        difficulty_combo = ttk.Combobox(
            control_frame,
            textvariable=self.coding_difficulty,
            values=["beginner", "intermediate", "advanced"],
            state="readonly",
            width=10
        )
        difficulty_combo.pack(side=tk.LEFT, padx=5)

        # 문제 선택
        ttk.Label(control_frame, text="문제:").pack(side=tk.LEFT, padx=(10, 0))
        self.problem_index = tk.StringVar(value="0")
        problem_combo = ttk.Combobox(
            control_frame,
            textvariable=self.problem_index,
            values=["0", "1"],
            state="readonly",
            width=5
        )
        problem_combo.pack(side=tk.LEFT, padx=5)

        # 문제 로드 버튼
        load_btn = ttk.Button(
            control_frame,
            text="문제 로드",
            command=self.load_coding_problem
        )
        load_btn.pack(side=tk.LEFT, padx=10)

        # 코드 실행 버튼
        run_btn = ttk.Button(
            control_frame,
            text="코드 실행",
            command=self.run_coding_problem
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        # 메인 영역 분할
        main_paned = ttk.PanedWindow(self.coding_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 왼쪽: 문제 설명
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="문제 설명", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)

        self.problem_description = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            height=20,
            width=40
        )
        self.problem_description.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 오른쪽: 코드 편집
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="코드 편집기", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)

        self.code_editor = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.NONE,
            height=20,
            width=50,
            font=("Courier New", 10)
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 실행 결과 영역
        result_frame = ttk.Frame(self.coding_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(result_frame, text="실행 결과", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)

        self.execution_result = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            height=10,
            width=80
        )
        self.execution_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_results_tab(self):
        """결과 및 피드백 탭 설정"""
        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(self.results_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 표시 유형 선택
        ttk.Label(control_frame, text="표시:").pack(side=tk.LEFT)
        self.result_type = tk.StringVar(value="all")
        result_combo = ttk.Combobox(
            control_frame,
            textvariable=self.result_type,
            values=["all", "quiz", "coding"],
            state="readonly",
            width=10
        )
        result_combo.pack(side=tk.LEFT, padx=5)

        # 새로고침 버튼
        refresh_btn = ttk.Button(
            control_frame,
            text="새로고침",
            command=self.refresh_results
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)

        # 요약 통계 영역
        stats_frame = ttk.LabelFrame(self.results_frame, text="요약 통계")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        self.stats_label = ttk.Label(
            stats_frame,
            text="아직 결과가 없습니다",
            font=("Arial", 9)
        )
        self.stats_label.pack(anchor=tk.W, padx=5, pady=5)

        # 결과 목록
        results_frame = ttk.LabelFrame(self.results_frame, text="결과 목록")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 결과 트리뷰
        result_columns = ("type", "date", "score", "status")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=result_columns,
            show="headings",
            height=10
        )

        self.results_tree.heading("type", text="유형")
        self.results_tree.heading("date", text="날짜")
        self.results_tree.heading("score", text="점수")
        self.results_tree.heading("status", text="상태")

        self.results_tree.column("type", width=100)
        self.results_tree.column("date", width=150)
        self.results_tree.column("score", width=80)
        self.results_tree.column("status", width=100)

        # 스크롤바
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 결과 상세 보기
        detail_frame = ttk.LabelFrame(self.results_frame, text="상세 정보")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.result_detail = scrolledtext.ScrolledText(
            detail_frame,
            wrap=tk.WORD,
            height=10,
            width=80
        )
        self.result_detail.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 이벤트 바인딩
        self.results_tree.bind("<Button-1>", self.on_result_select)

    def load_sample_data(self):
        """샘플 데이터 로드"""
        try:
            # 샘플 퀴즈 생성
            sample_quiz = self.quiz_generator.create_quiz(
                title="Python 기초 테스트",
                description="Python 기본 개념 평가",
                difficulty=DifficultyLevel.BEGINNER,
                topic="variables"
            )

            # 샘플 코딩 문제 생성
            sample_problem = self.problem_generator.generate_problem_from_template("beginner", 0)

            logger.info("샘플 데이터 로드 완료")

        except Exception as e:
            logger.error(f"샘플 데이터 로드 실패: {e}")

    def generate_new_quiz(self):
        """새 퀴즈 생성"""
        try:
            # 이전 문제 제거
            for widget in self.quiz_questions_inner.winfo_children():
                widget.destroy()

            self.quiz_answers.clear()

            # 퀴즈 생성
            difficulty = DifficultyLevel(self.quiz_difficulty.get())
            topic = self.quiz_topic.get()

            self.current_quiz = self.quiz_generator.create_quiz(
                title=f"Python {topic} 퀴즈",
                description=f"{topic} 주제의 {difficulty.value} 수준 퀴즈",
                difficulty=difficulty,
                topic=topic
            )

            # 문제 생성
            questions = self.quiz_generator.generate_questions_from_topic(topic, difficulty, 5)
            for question in questions:
                self.current_quiz.add_question(question)

            # UI 업데이트
            self.update_quiz_ui()

            messagebox.showinfo("성공", f"{len(questions)}개의 문제가 생성되었습니다!")

        except Exception as e:
            logger.error(f"퀴즈 생성 실패: {e}")
            messagebox.showerror("오류", f"퀴즈 생성 중 오류가 발생했습니다: {str(e)}")

    def update_quiz_ui(self):
        """퀴즈 UI 업데이트"""
        if not self.current_quiz:
            return

        # 퀴즈 정보 업데이트
        self.quiz_info_label.config(
            text=f"📝 {self.current_quiz.title} - {len(self.current_quiz.questions)}개 문제"
        )

        # 문제 UI 생성
        for i, question in enumerate(self.current_quiz.questions):
            question_frame = ttk.LabelFrame(
                self.quiz_questions_inner,
                text=f"문제 {i + 1} ({question.points}점)"
            )
            question_frame.pack(fill=tk.X, padx=5, pady=5)

            # 문제 텍스트
            question_text = tk.Text(question_frame, wrap=tk.WORD, height=4, width=60)
            question_text.insert("1.0", question.question_text)
            question_text.config(state=tk.DISABLED)
            question_text.pack(fill=tk.X, padx=5, pady=5)

            # 코드 예시
            if question.code_example:
                code_frame = ttk.Frame(question_frame)
                code_frame.pack(fill=tk.X, padx=5, pady=5)

                code_label = ttk.Label(code_frame, text="코드 예시:")
                code_label.pack(anchor=tk.W)

                code_text = tk.Text(code_frame, wrap=tk.NONE, height=3, width=60, font=("Courier New", 9))
                code_text.insert("1.0", question.code_example)
                code_text.config(state=tk.DISABLED)
                code_text.pack(fill=tk.X, padx=5, pady=5)

            # 답변 입력
            answer_frame = ttk.Frame(question_frame)
            answer_frame.pack(fill=tk.X, padx=5, pady=5)

            if question.question_type.value == "multiple_choice":
                # 객관식
                self.quiz_answers[question.question_id] = tk.StringVar()
                for option in (question.options or []):
                    ttk.Radiobutton(
                        answer_frame,
                        text=option,
                        variable=self.quiz_answers[question.question_id],
                        value=option
                    ).pack(anchor=tk.W)

            elif question.question_type.value == "true_false":
                # 참/거짓
                self.quiz_answers[question.question_id] = tk.StringVar()
                ttk.Radiobutton(
                    answer_frame,
                    text="참",
                    variable=self.quiz_answers[question.question_id],
                    value="True"
                ).pack(anchor=tk.W)
                ttk.Radiobutton(
                    answer_frame,
                    text="거짓",
                    variable=self.quiz_answers[question.question_id],
                    value="False"
                ).pack(anchor=tk.W)

            else:
                # 단답형
                ttk.Label(answer_frame, text="답안:").pack(side=tk.LEFT)
                self.quiz_answers[question.question_id] = tk.StringVar()
                answer_entry = ttk.Entry(
                    answer_frame,
                    textvariable=self.quiz_answers[question.question_id],
                    width=30
                )
                answer_entry.pack(side=tk.LEFT, padx=5)

            # 힌트
            if question.hints:
                hint_frame = ttk.Frame(question_frame)
                hint_frame.pack(fill=tk.X, padx=5, pady=5)

                ttk.Label(hint_frame, text="💡 힌트:", foreground="blue").pack(anchor=tk.W)
                for hint in question.hints:
                    ttk.Label(hint_frame, text=f"• {hint}", foreground="gray").pack(anchor=tk.W)

    def submit_quiz(self):
        """퀴즈 제출"""
        if not self.current_quiz:
            messagebox.showwarning("경고", "먼저 퀴즈를 생성하세요!")
            return

        try:
            # 답안 수집
            answers = {}
            for question in self.current_quiz.questions:
                answer = self.quiz_answers.get(question.question_id)
                if answer:
                    answers[question.question_id] = answer.get()

            # 퀴즈 제출
            import time
            start_time = time.time()

            result = self.quiz_generator.submit_quiz(
                quiz_id=self.current_quiz.quiz_id,
                user_id=self.user_id,
                answers=answers,
                time_taken=time.time() - start_time
            )

            # 피드백 생성
            feedback_data = {
                "score": result.score,
                "percentage": (result.score / result.total_points * 100) if result.total_points > 0 else 0,
                "total_questions": result.total_questions,
                "correct_count": result.correct_count,
                "time_taken": result.time_taken
            }

            feedback = self.feedback_generator.generate_feedback(
                feedback_type=FeedbackType.QUIZ,
                user_id=self.user_id,
                content_id=self.current_quiz.quiz_id,
                level=FeedbackLevel.BEGINNER,
                score_data=feedback_data
            )

            # 결과 표시
            self.display_quiz_result(result, feedback)

            messagebox.showinfo(
                "제출 완료",
                f"점수: {result.score}/{result.total_points}점\n"
                f"정답률: {result.correct_count}/{result.total_questions} ({feedback_data['percentage']:.1f}%)"
            )

        except Exception as e:
            logger.error(f"퀴즈 제출 실패: {e}")
            messagebox.showerror("오류", f"퀴즈 제출 중 오류가 발생했습니다: {str(e)}")

    def display_quiz_result(self, result, feedback):
        """퀴즈 결과 표시"""
        # 결과 탭으로 전환
        self.notebook.select(2)  # 결과 탭

        # 결과 디테일에 표시
        self.result_detail.delete("1.0", tk.END)

        result_text = f"""
📝 퀴즈 결과
{'='*50}

점수: {result.score}/{result.total_points}점
정답률: {result.correct_count}/{result.total_questions} ({(result.score / result.total_points * 100) if result.total_points > 0 else 0:.1f}%)
소요 시간: {result.time_taken:.1f}초

{feedback.overall_message}

{feedback.encouragement_message}

강점:
"""
        for strength in feedback.strengths:
            result_text += f"✓ {strength.title}: {strength.description}\n"

        if feedback.weaknesses:
            result_text += "\n개선이 필요한 부분:\n"
            for weakness in feedback.weaknesses:
                result_text += f"• {weakness.title}: {weakness.description}\n"

        if feedback.suggestions:
            result_text += "\n제안:\n"
            for suggestion in feedback.suggestions:
                result_text += f"• {suggestion.description}\n"

        result_text += f"\n다음 단계:\n"
        for step in feedback.next_steps:
            result_text += f"• {step}\n"

        self.result_detail.insert("1.0", result_text)

    def load_coding_problem(self):
        """코딩 문제 로드"""
        try:
            difficulty = self.coding_difficulty.get()
            index = int(self.problem_index.get())

            problem = self.problem_generator.generate_problem_from_template(difficulty, index)

            if problem:
                self.current_problem = problem
                self.display_coding_problem(problem)
                messagebox.showinfo("성공", f"'{problem.title}' 문제가 로드되었습니다!")
            else:
                messagebox.showwarning("경고", "해당 문제를 찾을 수 없습니다.")

        except Exception as e:
            logger.error(f"코딩 문제 로드 실패: {e}")
            messagebox.showerror("오류", f"문제 로드 중 오류가 발생했습니다: {str(e)}")

    def display_coding_problem(self, problem):
        """코딩 문제 표시"""
        # 문제 설명
        self.problem_description.delete("1.0", tk.END)

        description = f"""
📝 {problem.title}

{problem.description}

난이도: {problem.difficulty}
카테고리: {problem.category.value}
점수: {problem.points}점

"""

        if problem.constraints:
            description += "제약 조건:\n"
            for constraint in problem.constraints:
                description += f"• {constraint}\n"
            description += "\n"

        if problem.hints:
            description += "힌트:\n"
            for hint in problem.hints:
                description += f"💡 {hint}\n"
            description += "\n"

        if problem.test_cases:
            description += "테스트 케이스 (일부):\n"
            for tc in problem.test_cases[:3]:
                if not tc.is_hidden:
                    description += f"• 입력: {tc.input_data} → 출력: {tc.expected_output}\n"

        self.problem_description.insert("1.0", description)

        # 시작 코드
        self.code_editor.delete("1.0", tk.END)
        if problem.starter_code:
            self.code_editor.insert("1.0", problem.starter_code)

    def run_coding_problem(self):
        """코딩 문제 실행"""
        if not self.current_problem:
            messagebox.showwarning("경고", "먼저 문제를 로드하세요!")
            return

        try:
            # 코드 가져오기
            code = self.code_editor.get("1.0", tk.END).strip()

            if not code:
                messagebox.showwarning("경고", "코드를 입력하세요!")
                return

            # 실행 결과 초기화
            self.execution_result.delete("1.0", tk.END)
            self.execution_result.insert("1.0", "코드 실행 중...\n")
            self.execution_result.update()

            # 코드 평가
            evaluation = self.auto_evaluator.evaluate_submission(
                problem_id=self.current_problem.problem_id,
                user_id=self.user_id,
                code=code,
                test_cases=self.current_problem.test_cases
            )

            # 결과 표시
            self.display_evaluation_result(evaluation)

            # 피드백 생성
            feedback_data = {
                "score": evaluation.score,
                "total_tests": evaluation.total_tests,
                "passed_tests": evaluation.passed_tests,
                "code_quality": evaluation.code_quality.to_dict() if evaluation.code_quality else None
            }

            feedback = self.feedback_generator.generate_feedback(
                feedback_type=FeedbackType.CODING,
                user_id=self.user_id,
                content_id=self.current_problem.problem_id,
                level=FeedbackLevel.BEGINNER,
                score_data=feedback_data
            )

            # 결과 탭에 상세 정보 표시
            self.notebook.select(2)  # 결과 탭
            self.display_evaluation_detail(evaluation, feedback)

        except Exception as e:
            logger.error(f"코드 실행 실패: {e}")
            messagebox.showerror("오류", f"코드 실행 중 오류가 발생했습니다: {str(e)}")

    def display_evaluation_result(self, evaluation):
        """평가 결과 표시"""
        self.execution_result.delete("1.0", tk.END)

        result_text = f"""
실행 결과
{'='*50}

상태: {evaluation.status.value}
테스트 결과: {evaluation.passed_tests}/{evaluation.total_tests} 통과
점수: {evaluation.score:.1f}점
실행 시간: {evaluation.execution_time:.3f}초

"""

        for test_result in evaluation.test_results:
            status_icon = "✓" if test_result.status == EvaluationStatus.PASSED else "✗"
            result_text += f"{status_icon} {test_result.test_name}\n"

            if test_result.status != EvaluationStatus.PASSED:
                result_text += f"  입력: {test_result.input_data}\n"
                result_text += f"  예상: {test_result.expected_output}\n"
                result_text += f"  실제: {test_result.actual_output}\n"
                if test_result.error_message:
                    result_text += f"  오류: {test_result.error_message}\n"
            result_text += "\n"

        self.execution_result.insert("1.0", result_text)

    def display_evaluation_detail(self, evaluation, feedback):
        """평가 상세 정보 표시"""
        self.result_detail.delete("1.0", tk.END)

        detail_text = f"""
💻 코딩 평가 결과
{'='*50}

{feedback.overall_message}

{feedback.encouragement_message}

테스트 결과: {evaluation.passed_tests}/{evaluation.total_tests} 통과
점수: {evaluation.score:.1f}점
"""

        if evaluation.code_quality:
            quality = evaluation.code_quality
            detail_text += f"""
코드 품질:
• 복잡도 점수: {quality.complexity_score:.1f}
• 스타일 점수: {quality.style_score:.1f}
• 가독성 점수: {quality.readability_score:.1f}
• 베스트 프랙티스: {quality.best_practices_score:.1f}
"""

        detail_text += "\n강점:\n"
        for strength in feedback.strengths:
            detail_text += f"✓ {strength.title}: {strength.description}\n"

        if feedback.weaknesses:
            detail_text += "\n개선이 필요한 부분:\n"
            for weakness in feedback.weaknesses:
                detail_text += f"• {weakness.title}: {weakness.description}\n"

        if feedback.suggestions:
            detail_text += "\n제안:\n"
            for suggestion in feedback.suggestions:
                detail_text += f"• {suggestion.description}\n"

        detail_text += f"\n다음 단계:\n"
        for step in feedback.next_steps:
            detail_text += f"• {step}\n"

        self.result_detail.insert("1.0", detail_text)

    def refresh_results(self):
        """결과 새로고침"""
        try:
            # 결과 목록 업데이트
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            # 퀴즈 결과
            quiz_results = [r for r in self.quiz_generator.results.values()]
            for result in quiz_results:
                self.results_tree.insert("", "end", values=(
                    "퀴즈",
                    result.completed_at.strftime("%Y-%m-%d %H:%M"),
                    f"{result.score}/{result.total_points}",
                    "완료"
                ))

            # 코딩 평가 결과
            coding_results = self.auto_evaluator.evaluation_history
            for evaluation in coding_results:
                self.results_tree.insert("", "end", values=(
                    "코딩",
                    evaluation.evaluated_at.strftime("%Y-%m-%d %H:%M"),
                    f"{evaluation.score:.1f}",
                    evaluation.status.value
                ))

            # 통계 업데이트
            total_results = len(quiz_results) + len(coding_results)
            avg_score = 0.0

            if total_results > 0:
                quiz_score = sum(r.score for r in quiz_results) / len(quiz_results) if quiz_results else 0
                coding_score = sum(e.score for e in coding_results) / len(coding_results) if coding_results else 0
                avg_score = (quiz_score + coding_score) / 2

            self.stats_label.config(
                text=f"총 결과: {total_results}건 | 평균 점수: {avg_score:.1f}점"
            )

        except Exception as e:
            logger.error(f"결과 새로고침 실패: {e}")

    def on_result_select(self, event):
        """결과 선택 이벤트"""
        # 결과 상세 표시 로직
        pass


if __name__ == "__main__":
    # 테스트
    root = tk.Tk()
    root.title("평가 시스템 탭 테스트")
    root.geometry("1200x800")

    tab = EvaluationTab(root)
    tab.pack(fill=tk.BOTH, expand=True)

    root.mainloop()