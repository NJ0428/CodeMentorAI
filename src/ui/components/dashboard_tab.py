"""
시각화 대시보드 탭 컴포넌트
학습 진도, 통계, 성과 분석을 시각화하는 UI 인터페이스
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

# 한글 폰트 설정 (matplotlib)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


class DashboardTab(tk.Frame):
    """시각화 대시보드 탭 컴포넌트"""

    def __init__(self, parent, learning_controller=None):
        super().__init__(parent)

        self.controller = learning_controller
        self.user_id = 1  # 기본 사용자 ID

        # 대시보드 데이터 캐시
        self.dashboard_data = {}

        # matplotlib Figure 객체 저장
        self.figures = {}

        self._create_ui()
        self._load_dashboard_data()

        logger.info("시각화 대시보드 초기화 완료")

    def _create_ui(self):
        """UI 생성"""
        # 상단 컨트롤 영역
        self._create_control_panel()

        # 메인 대시보드 영역
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 대시보드 노트북
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 개요 탭
        self._create_overview_tab()

        # 진도 차트 탭
        self._create_progress_charts_tab()

        # 통계 분석 탭
        self._create_statistics_tab()

        # 성취 시각화 탭
        self._create_achievements_visualization_tab()

        # 인터랙티브 추적 탭
        self._create_interactive_tracking_tab()

        # 하단 상태바
        self._create_status_bar()

    def _create_control_panel(self):
        """상단 컨트롤 패널 생성"""
        control_frame = tk.Frame(self, bg="#f0f0f0", height=80)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 제목
        title_label = tk.Label(
            control_frame,
            text="📊 학습 분석 대시보드",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=5)

        # 컨트롤 버튼 프레임
        button_frame = tk.Frame(control_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=10)

        # 새로고침 버튼
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 새로고침",
            command=self.refresh_dashboard,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10)
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # 내보내기 버튼
        export_btn = tk.Button(
            button_frame,
            text="📥 데이터 내보내기",
            command=self.export_data,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10)
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        # 기간 선택
        period_frame = tk.Frame(button_frame, bg="#f0f0f0")
        period_frame.pack(side=tk.RIGHT, padx=5)

        tk.Label(
            period_frame,
            text="기간:",
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        self.period_var = tk.StringVar(value="week")
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.period_var,
            values=["week", "month", "all"],
            state="readonly",
            width=8
        )
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self._on_period_changed)

    def _create_overview_tab(self):
        """개요 탭 생성"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 개요")

        # 주요 통계 카드
        stats_frame = tk.Frame(tab)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        # 통계 카드들
        self.stats_cards = {}

        # 총 학습 시간 카드
        self._create_stat_card(
            stats_frame,
            "study_time",
            "⏰ 총 학습 시간",
            "0시간 0분",
            "#4CAF50"
        )

        # 완료한 문제 수 카드
        self._create_stat_card(
            stats_frame,
            "completed_exercises",
            "✅ 완료한 문제",
            "0개",
            "#2196F3"
        )

        # 평균 점수 카드
        self._create_stat_card(
            stats_frame,
            "avg_score",
            "📊 평균 점수",
            "0.0/10",
            "#FF9800"
        )

        # 획득 XP 카드
        self._create_stat_card(
            stats_frame,
            "total_xp",
            "🏆 획득 XP",
            "0 XP",
            "#9C27B0"
        )

        # 학습 활동 그래프
        graph_frame = tk.Frame(tab)
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            graph_frame,
            text="학습 활동 추이",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        # matplotlib Figure
        self.activity_figure = Figure(figsize=(8, 3), dpi=100)
        self.activity_canvas = FigureCanvasTkAgg(self.activity_figure, graph_frame)
        self.activity_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['activity'] = self.activity_figure

    def _create_stat_card(self, parent, card_id, title, value, color):
        """통계 카드 생성"""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, borderwidth=2)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 카드 내용
        tk.Label(
            card,
            text=title,
            font=("Arial", 11, "bold"),
            bg=color,
            fg="white"
        ).pack(pady=(10, 5))

        value_label = tk.Label(
            card,
            text=value,
            font=("Arial", 14, "bold"),
            bg=color,
            fg="white"
        )
        value_label.pack(pady=(0, 10))

        self.stats_cards[card_id] = value_label

    def _create_progress_charts_tab(self):
        """진도 차트 탭 생성"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 진도 차트")

        # 차트 컨테이너
        chart_container = tk.Frame(tab)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 완료율 파이 차트
        pie_frame = tk.Frame(chart_container)
        pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            pie_frame,
            text="주제 완료율",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.completion_pie_figure = Figure(figsize=(5, 4), dpi=100)
        self.completion_pie_canvas = FigureCanvasTkAgg(self.completion_pie_figure, pie_frame)
        self.completion_pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['completion_pie'] = self.completion_pie_figure

        # 레벨별 진도 바 차트
        bar_frame = tk.Frame(chart_container)
        bar_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            bar_frame,
            text="레벨별 진도",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.level_progress_figure = Figure(figsize=(5, 4), dpi=100)
        self.level_progress_canvas = FigureCanvasTkAgg(self.level_progress_figure, bar_frame)
        self.level_progress_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['level_progress'] = self.level_progress_figure

    def _create_statistics_tab(self):
        """통계 분석 탭 생성"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 통계 분석")

        # 통계 컨테이너
        stats_container = tk.Frame(tab)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 점수 분포 히스토그램
        histogram_frame = tk.Frame(stats_container)
        histogram_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            histogram_frame,
            text="점수 분포",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.score_histogram_figure = Figure(figsize=(8, 3), dpi=100)
        self.score_histogram_canvas = FigureCanvasTkAgg(self.score_histogram_figure, histogram_frame)
        self.score_histogram_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['score_histogram'] = self.score_histogram_figure

        # 성과 통계 텍스트 영역
        text_frame = tk.Frame(stats_container)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(
            text_frame,
            text="성과 통계",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.statistics_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=6,
            font=("Arial", 10)
        )
        self.statistics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_achievements_visualization_tab(self):
        """성취 시각화 탭 생성"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="🏆 성취 시각화")

        # 성취 차기용성 컨테이너
        achievement_container = tk.Frame(tab)
        achievement_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 뱃지 획득 현황
        badge_frame = tk.Frame(achievement_container)
        badge_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            badge_frame,
            text="뱃지 획득 현황",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.badge_figure = Figure(figsize=(8, 4), dpi=100)
        self.badge_canvas = FigureCanvasTkAgg(self.badge_figure, badge_frame)
        self.badge_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['badges'] = self.badge_figure

        # 성취 상세 정보
        detail_frame = tk.Frame(achievement_container)
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(
            detail_frame,
            text="최근 성취",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.recent_achievements_text = tk.Text(
            detail_frame,
            wrap=tk.WORD,
            height=8,
            font=("Arial", 10)
        )
        self.recent_achievements_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_interactive_tracking_tab(self):
        """인터랙티브 추적 탭 생성"""
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text="🎯 인터랙티브 추적")

        # 추적 컨트롤
        control_frame = tk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            control_frame,
            text="학습 목표 설정",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        # 목표 입력
        goal_frame = tk.Frame(control_frame)
        goal_frame.pack(fill=tk.X, pady=5)

        tk.Label(goal_frame, text="일일 학습 시간 목표 (분):").pack(side=tk.LEFT)
        self.daily_goal_entry = tk.Entry(goal_frame, width=10)
        self.daily_goal_entry.pack(side=tk.LEFT, padx=5)
        self.daily_goal_entry.insert(0, "30")

        set_goal_btn = tk.Button(
            goal_frame,
            text="목표 설정",
            command=self.set_learning_goal,
            bg="#4CAF50",
            fg="white"
        )
        set_goal_btn.pack(side=tk.LEFT, padx=5)

        # 진도 추적 차트
        tracking_frame = tk.Frame(tab)
        tracking_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            tracking_frame,
            text="학습 목표 대비 실적",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.tracking_figure = Figure(figsize=(8, 4), dpi=100)
        self.tracking_canvas = FigureCanvasTkAgg(self.tracking_figure, tracking_frame)
        self.tracking_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['tracking'] = self.tracking_figure

        # 학습 패턴 분석
        pattern_frame = tk.Frame(tab)
        pattern_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        tk.Label(
            pattern_frame,
            text="학습 패턴 분석",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)

        self.pattern_text = tk.Text(
            pattern_frame,
            wrap=tk.WORD,
            height=5,
            font=("Arial", 10)
        )
        self.pattern_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_status_bar(self):
        """상태바 생성"""
        status_bar = tk.Frame(self, bg="#f0f0f0", height=30)
        status_bar.pack(fill=tk.X, padx=5, pady=5)

        self.status_label = tk.Label(
            status_bar,
            text="대시보드 준비 완료",
            bg="#f0f0f0",
            font=("Arial", 9),
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # 마지막 업데이트 시간
        self.last_update_label = tk.Label(
            status_bar,
            text="마지막 업데이트: 없음",
            bg="#f0f0f0",
            font=("Arial", 9)
        )
        self.last_update_label.pack(side=tk.RIGHT, padx=10)

    def _load_dashboard_data(self):
        """대시보드 데이터 로드"""
        try:
            if self.controller:
                # 실제 컨트롤러에서 데이터 가져오기
                progress_summary = self.controller.get_user_progress_summary(self.user_id)
                achievements = self.controller.get_user_achievements(self.user_id)

                self.dashboard_data = {
                    'progress': progress_summary,
                    'achievements': achievements,
                    'last_update': datetime.now()
                }

                logger.info("대시보드 데이터 로드 완료")
            else:
                # 테스트용 더미 데이터
                self._load_test_data()

                logger.warning("컨트롤러가 없어 테스트 데이터 사용")

        except Exception as e:
            logger.error(f"대시보드 데이터 로드 실패: {e}")
            self._load_test_data()

        # 차트 업데이트
        self._update_all_charts()
        self._update_statistics_display()
        self._update_status_display()

    def _load_test_data(self):
        """테스트 데이터 로드"""
        # 더미 진도 데이터
        test_progress = {
            'total_completed': 12,
            'total_items': 50,
            'overall_completion_rate': 24.0,
            'total_study_minutes': 450,
            'total_xp': 850,
            'average_score': 7.8,
            'level_progress': {
                'beginner': {'completed': 8, 'total': 20, 'completion_rate': 40.0, 'average_score': 8.2},
                'intermediate': {'completed': 4, 'total': 20, 'completion_rate': 20.0, 'average_score': 7.1},
                'advanced': {'completed': 0, 'total': 10, 'completion_rate': 0.0, 'average_score': 0.0}
            },
            'daily_activity': [
                {'date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'), 'minutes': 30, 'exercises': 2},
                {'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), 'minutes': 45, 'exercises': 3},
                {'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'), 'minutes': 20, 'exercises': 1},
                {'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'), 'minutes': 60, 'exercises': 4},
                {'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 'minutes': 35, 'exercises': 2},
                {'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), 'minutes': 50, 'exercises': 3},
                {'date': datetime.now().strftime('%Y-%m-%d'), 'minutes': 40, 'exercises': 2}
            ],
            'score_distribution': [5, 6, 7, 8, 8, 9, 7, 6, 8, 9, 10, 7]
        }

        # 더미 성취 데이터
        test_achievements = [
            {'achievement_type': 'first_exercise', 'earned_at': '2024-07-01', 'name': '첫걸음', 'icon': '👶'},
            {'achievement_type': 'streak_3_days', 'earned_at': '2024-07-03', 'name': '3일 연속', 'icon': '🔥'},
            {'achievement_type': 'perfect_score', 'earned_at': '2024-07-02', 'name': '완벽한 점수', 'icon': '⭐'},
            {'achievement_type': 'topic_complete', 'earned_at': '2024-07-04', 'name': '주제 완료', 'icon': '📚'}
        ]

        self.dashboard_data = {
            'progress': test_progress,
            'achievements': test_achievements,
            'last_update': datetime.now()
        }

    def _update_all_charts(self):
        """모든 차트 업데이트"""
        try:
            self._update_activity_chart()
            self._update_completion_pie_chart()
            self._update_level_progress_chart()
            self._update_score_histogram()
            self._update_badge_chart()
            self._update_tracking_chart()

            logger.info("모든 차트 업데이트 완료")
        except Exception as e:
            logger.error(f"차트 업데이트 실패: {e}")

    def _update_activity_chart(self):
        """학습 활동 차트 업데이트"""
        try:
            fig = self.activity_figure
            fig.clear()

            ax = fig.add_subplot(111)

            # 데이터 추출
            daily_activity = self.dashboard_data.get('progress', {}).get('daily_activity', [])

            if daily_activity:
                dates = [activity['date'] for activity in daily_activity]
                minutes = [activity['minutes'] for activity in daily_activity]

                # 꺾은선 그래프
                ax.plot(dates, minutes, marker='o', linestyle='-', color='#4CAF50', linewidth=2)
                ax.fill_between(dates, minutes, alpha=0.3, color='#4CAF50')

                ax.set_title('일일 학습 시간', fontsize=12, fontweight='bold')
                ax.set_xlabel('날짜', fontsize=10)
                ax.set_ylabel('학습 시간 (분)', fontsize=10)
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)

            fig.tight_layout()
            self.activity_canvas.draw()

        except Exception as e:
            logger.error(f"활동 차트 업데이트 실패: {e}")

    def _update_completion_pie_chart(self):
        """완료율 파이 차트 업데이트"""
        try:
            fig = self.completion_pie_figure
            fig.clear()

            ax = fig.add_subplot(111)

            # 데이터 추출
            progress = self.dashboard_data.get('progress', {})
            completed = progress.get('total_completed', 0)
            total = progress.get('total_items', 1)
            remaining = total - completed

            # 파이 차트
            sizes = [completed, remaining]
            labels = [f'완료 ({completed})', f'남음 ({remaining})']
            colors = ['#4CAF50', '#E0E0E0']
            explode = (0.1, 0)  # 완료 부분 강조

            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90)
            ax.set_title('전체 완료율', fontsize=12, fontweight='bold')

            fig.tight_layout()
            self.completion_pie_canvas.draw()

        except Exception as e:
            logger.error(f"완료율 파이 차트 업데이트 실패: {e}")

    def _update_level_progress_chart(self):
        """레벨별 진도 차트 업데이트"""
        try:
            fig = self.level_progress_figure
            fig.clear()

            ax = fig.add_subplot(111)

            # 데이터 추출
            level_progress = self.dashboard_data.get('progress', {}).get('level_progress', {})

            levels = []
            completion_rates = []

            for level_name, level_data in level_progress.items():
                levels.append(level_name.capitalize())
                completion_rates.append(level_data.get('completion_rate', 0))

            if levels:
                # 막대 그래프
                colors = ['#4CAF50', '#2196F3', '#FF9800']
                bars = ax.bar(levels, completion_rates, color=colors, alpha=0.7)

                # 값 표시
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=10)

                ax.set_title('레벨별 완료율', fontsize=12, fontweight='bold')
                ax.set_xlabel('레벨', fontsize=10)
                ax.set_ylabel('완료율 (%)', fontsize=10)
                ax.set_ylim(0, 100)
                ax.grid(True, alpha=0.3, axis='y')

            fig.tight_layout()
            self.level_progress_canvas.draw()

        except Exception as e:
            logger.error(f"레벨별 진도 차트 업데이트 실패: {e}")

    def _update_score_histogram(self):
        """점수 분포 히스토그램 업데이트"""
        try:
            fig = self.score_histogram_figure
            fig.clear()

            ax = fig.add_subplot(111)

            # 데이터 추출
            scores = self.dashboard_data.get('progress', {}).get('score_distribution', [])

            if scores:
                # 히스토그램
                ax.hist(scores, bins=range(1, 12), color='#2196F3', alpha=0.7, edgecolor='black')

                ax.set_title('점수 분포', fontsize=12, fontweight='bold')
                ax.set_xlabel('점수', fontsize=10)
                ax.set_ylabel('빈도', fontsize=10)
                ax.set_xticks(range(1, 11))
                ax.grid(True, alpha=0.3, axis='y')

            fig.tight_layout()
            self.score_histogram_canvas.draw()

        except Exception as e:
            logger.error(f"점수 분포 히스토그램 업데이트 실패: {e}")

    def _update_badge_chart(self):
        """뱃지 차트 업데이트"""
        try:
            fig = self.badge_figure
            fig.clear()

            ax = fig.add_subplot(111)

            # 성취 데이터
            achievements = self.dashboard_data.get('achievements', [])

            if achievements:
                # 카테고리별 뱃지 수 집계
                badge_counts = {}
                for achievement in achievements:
                    name = achievement.get('name', '알 수 없음')
                    icon = achievement.get('icon', '🏅')
                    badge_counts[f"{icon} {name}"] = badge_counts.get(f"{icon} {name}", 0) + 1

                if badge_counts:
                    # 수평 막대 그래프
                    badges = list(badge_counts.keys())
                    counts = list(badge_counts.values())

                    bars = ax.barh(badges, counts, color='#9C27B0', alpha=0.7)

                    # 값 표시
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(width, bar.get_y() + bar.get_height()/2.,
                               f'{int(width)}', ha='left', va='center', fontsize=10)

                    ax.set_title('획득한 뱃지', fontsize=12, fontweight='bold')
                    ax.set_xlabel('획득 횟수', fontsize=10)
                    ax.grid(True, alpha=0.3, axis='x')

            fig.tight_layout()
            self.badge_canvas.draw()

        except Exception as e:
            logger.error(f"뱃지 차트 업데이트 실패: {e}")

    def _update_tracking_chart(self):
        """추적 차트 업데이트"""
        try:
            fig = self.tracking_figure
            fig.clear()

            ax = fig.add_subplot(111)

            # 일일 학습 시간 데이터
            daily_activity = self.dashboard_data.get('progress', {}).get('daily_activity', [])

            if daily_activity:
                dates = [activity['date'] for activity in daily_activity]
                minutes = [activity['minutes'] for activity in daily_activity]

                # 목표선 (기본 30분)
                goal = 30
                goal_line = [goal] * len(dates)

                # 꺾은선 그래프
                ax.plot(dates, minutes, marker='o', linestyle='-', color='#4CAF50', linewidth=2, label='실제 학습 시간')
                ax.plot(dates, goal_line, linestyle='--', color='red', linewidth=2, label='목표')

                # 목표 미달 날짜 강조
                for i, (date, minute) in enumerate(zip(dates, minutes)):
                    if minute < goal:
                        ax.scatter(date, minute, color='red', s=100, zorder=5)
                    else:
                        ax.scatter(date, minute, color='green', s=100, zorder=5)

                ax.set_title('학습 목표 대비 실적', fontsize=12, fontweight='bold')
                ax.set_xlabel('날짜', fontsize=10)
                ax.set_ylabel('학습 시간 (분)', fontsize=10)
                ax.legend()
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)

            fig.tight_layout()
            self.tracking_canvas.draw()

        except Exception as e:
            logger.error(f"추적 차트 업데이트 실패: {e}")

    def _update_statistics_display(self):
        """통계 표시 업데이트"""
        try:
            # 통계 카드 업데이트
            progress = self.dashboard_data.get('progress', {})

            # 총 학습 시간
            total_minutes = progress.get('total_study_minutes', 0)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            self.stats_cards['study_time'].config(text=f"{hours}시간 {minutes}분")

            # 완료한 문제 수
            completed = progress.get('total_completed', 0)
            self.stats_cards['completed_exercises'].config(text=f"{completed}개")

            # 평균 점수
            avg_score = progress.get('average_score', 0.0)
            self.stats_cards['avg_score'].config(text=f"{avg_score:.1f}/10")

            # 획득 XP
            total_xp = progress.get('total_xp', 0)
            self.stats_cards['total_xp'].config(text=f"{total_xp} XP")

            # 통계 분석 텍스트
            self._update_statistics_text()
            self._update_achievements_text()
            self._update_pattern_text()

        except Exception as e:
            logger.error(f"통계 표시 업데이트 실패: {e}")

    def _update_statistics_text(self):
        """통계 분석 텍스트 업데이트"""
        try:
            self.statistics_text.delete(1.0, tk.END)

            progress = self.dashboard_data.get('progress', {})
            scores = progress.get('score_distribution', [])

            if scores:
                import statistics

                # 기본 통계
                mean_score = statistics.mean(scores)
                median_score = statistics.median(scores)
                std_score = statistics.stdev(scores) if len(scores) > 1 else 0
                min_score = min(scores)
                max_score = max(scores)

                text = f"""📊 성과 통계 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 평균 점수: {mean_score:.2f}/10
📈 중앙값: {median_score:.1f}/10
📉 표준편차: {std_score:.2f}
🔻 최저 점수: {min_score}/10
🔺 최고 점수: {max_score}/10
📝 총 제출 횟수: {len(scores)}회

🎯 성과 평가:
"""

                # 성과 평가
                if mean_score >= 8:
                    text += "   매우 우수한 성과를 보이고 있습니다!\n"
                elif mean_score >= 6:
                    text += "   안정적인 학습 성과를 보이고 있습니다.\n"
                else:
                    text += "   추가적인 연습이 필요합니다.\n"

                if std_score < 1.5:
                    text += "   점수가 일정하여 실력이 안정되어 있습니다.\n"
                elif std_score > 2.5:
                    text += "   점수 편차가 크므로 복습이 필요할 수 있습니다.\n"

                self.statistics_text.insert(tk.END, text)

        except Exception as e:
            logger.error(f"통계 텍스트 업데이트 실패: {e}")

    def _update_achievements_text(self):
        """성취 텍스트 업데이트"""
        try:
            self.recent_achievements_text.delete(1.0, tk.END)

            achievements = self.dashboard_data.get('achievements', [])

            if achievements:
                text = "🏆 최근 획득한 성취\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                # 최근 성취 5개 표시
                recent_achievements = sorted(achievements, key=lambda x: x.get('earned_at', ''), reverse=True)[:5]

                for i, achievement in enumerate(recent_achievements, 1):
                    icon = achievement.get('icon', '🏅')
                    name = achievement.get('name', '알 수 없음')
                    earned_at = achievement.get('earned_at', '알 수 없는 날짜')

                    text += f"{i}. {icon} {name}\n"
                    text += f"   획득일: {earned_at}\n\n"

                self.recent_achievements_text.insert(tk.END, text)
            else:
                self.recent_achievements_text.insert(tk.END, "🏆 아직 획득한 성취가 없습니다.\n   학습을 시작하여 첫 성취를 달성해보세요!")

        except Exception as e:
            logger.error(f"성취 텍스트 업데이트 실패: {e}")

    def _update_pattern_text(self):
        """학습 패턴 텍스트 업데이트"""
        try:
            self.pattern_text.delete(1.0, tk.END)

            daily_activity = self.dashboard_data.get('progress', {}).get('daily_activity', [])

            if daily_activity:
                text = "🎯 학습 패턴 분석\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                # 주별 학습 패턴 분석
                total_minutes = sum(activity['minutes'] for activity in daily_activity)
                avg_daily = total_minutes / len(daily_activity)
                max_day = max(daily_activity, key=lambda x: x['minutes'])
                min_day = min(daily_activity, key=lambda x: x['minutes'])

                text += f"📊 일일 평균 학습 시간: {avg_daily:.1f}분\n"
                text += f"🔥 가장 많이 학습한 날: {max_day['date']} ({max_day['minutes']}분)\n"
                text += f"💤 가장 적게 학습한 날: {min_day['date']} ({min_day['minutes']}분)\n\n"

                # 학습 패턴 추천
                consecutive_days = self._count_consecutive_days(daily_activity)
                if consecutive_days >= 5:
                    text += "🌟 연속 학습 습관이 훌륭합니다! 이势头를 유지하세요.\n"
                elif consecutive_days >= 3:
                    text += "👍 꾸준한 학습 습관을形成하고 있습니다.\n"
                else:
                    text += "💡 매일 꾸준히 학습하는 습관을 들여보세요.\n"

                # 목표 달성률
                goal_minutes = 30  # 기본 목표
                goal_achieved_days = sum(1 for activity in daily_activity if activity['minutes'] >= goal_minutes)
                achievement_rate = (goal_achieved_days / len(daily_activity)) * 100

                text += f"\n🎯 일일 목표({goal_minutes}분) 달성률: {achievement_rate:.1f}%\n"

                if achievement_rate >= 80:
                    text += "🎉 목표 달성률이 매우 우수합니다!\n"
                elif achievement_rate >= 50:
                    text += "👍 목표를 잘 달성하고 있습니다.\n"
                else:
                    text += "💪 목표 달성을 위해 조금 더 노력이 필요합니다.\n"

                self.pattern_text.insert(tk.END, text)
            else:
                self.pattern_text.insert(tk.END, "🎯 학습 패턴 분석\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                self.pattern_text.insert(tk.END, "아직 학습 데이터가 충분하지 않습니다.\n")
                self.pattern_text.insert(tk.END, "학습을 시작하여 패턴 분석 데이터를 수집하세요.")

        except Exception as e:
            logger.error(f"패턴 텍스트 업데이트 실패: {e}")

    def _count_consecutive_days(self, daily_activity):
        """연속 학습 일수 계산"""
        if not daily_activity:
            return 0

        # 날짜 정렬
        sorted_activities = sorted(daily_activity, key=lambda x: x['date'])

        consecutive_count = 1
        max_consecutive = 1

        for i in range(1, len(sorted_activities)):
            current_date = datetime.strptime(sorted_activities[i]['date'], '%Y-%m-%d')
            prev_date = datetime.strptime(sorted_activities[i-1]['date'], '%Y-%m-%d')

            # 하루 차이면 연속
            if (current_date - prev_date).days == 1:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1

        return max_consecutive

    def _update_status_display(self):
        """상태 표시 업데이트"""
        try:
            last_update = self.dashboard_data.get('last_update')
            if last_update:
                update_str = last_update.strftime('%Y-%m-%d %H:%M:%S')
                self.last_update_label.config(text=f"마지막 업데이트: {update_str}")

            self.status_label.config(text="대시보드 데이터 로드 완료")

        except Exception as e:
            logger.error(f"상태 표시 업데이트 실패: {e}")

    def _on_period_changed(self, event=None):
        """기간 변경 이벤트"""
        selected_period = self.period_var.get()
        logger.info(f"기간 변경: {selected_period}")

        # 기간에 따라 데이터 필터링 및 재로드
        self._load_dashboard_data()

    def refresh_dashboard(self):
        """대시보드 새로고침"""
        try:
            self.status_label.config(text="새로고침 중...")
            self.update()

            # 데이터 다시 로드
            self._load_dashboard_data()

            self.status_label.config(text="새로고침 완료")
            messagebox.showinfo("완료", "대시보드가 새로고쳐졌습니다.")

        except Exception as e:
            logger.error(f"대시보드 새로고침 실패: {e}")
            messagebox.showerror("오류", f"새로고침 실패: {e}")

    def export_data(self):
        """데이터 내보내기"""
        try:
            # CSV 파일로 내보내기
            progress = self.dashboard_data.get('progress', {})
            daily_activity = progress.get('daily_activity', [])

            if daily_activity:
                # DataFrame 생성
                df = pd.DataFrame(daily_activity)

                # 파일 저장
                filename = f"learning_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')

                messagebox.showinfo("완료", f"데이터가 {filename}로 내보내기 되었습니다.")
            else:
                messagebox.showwarning("경고", "내보낼 데이터가 없습니다.")

        except Exception as e:
            logger.error(f"데이터 내보내기 실패: {e}")
            messagebox.showerror("오류", f"내보내기 실패: {e}")

    def set_learning_goal(self):
        """학습 목표 설정"""
        try:
            goal_text = self.daily_goal_entry.get()
            goal_minutes = int(goal_text) if goal_text.isdigit() else 30

            # 목표 저장 (실제로는 데이터베이스에 저장)
            messagebox.showinfo("완료", f"일일 학습 목표가 {goal_minutes}분으로 설정되었습니다.")

            # 추적 차트 업데이트
            self._update_tracking_chart()

        except Exception as e:
            logger.error(f"목표 설정 실패: {e}")
            messagebox.showerror("오류", f"목표 설정 실패: {e}")


if __name__ == "__main__":
    # 대시보드 탭 테스트
    print("🧪 시각화 대시보드 탭 테스트")

    root = tk.Tk()
    root.title("시각화 대시보드 테스트")
    root.geometry("1200x800")

    dashboard_tab = DashboardTab(root)
    dashboard_tab.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

    print("✅ 시각화 대시보드 탭 테스트 완료")