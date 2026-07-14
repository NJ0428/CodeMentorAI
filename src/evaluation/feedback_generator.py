"""
피드백 생성기
학습 결과에 대한 상세 피드백 생성 기능
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger
import json
import uuid


class FeedbackType(str, Enum):
    """피드백 유형"""
    QUIZ = "quiz"
    CODING = "coding"
    LEARNING_PATH = "learning_path"
    GENERAL = "general"


class FeedbackLevel(str, Enum):
    """피드백 수준"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class FeedbackItem:
    """개별 피드백 항목"""
    item_id: str
    category: str  # "strength", "weakness", "suggestion", "achievement"
    title: str
    description: str
    priority: str = "medium"  # "high", "medium", "low"
    actionable: bool = True
    resources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "item_id": self.item_id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "actionable": self.actionable,
            "resources": self.resources
        }


@dataclass
class Feedback:
    """피드백"""
    feedback_id: str
    feedback_type: FeedbackType
    user_id: int
    content_id: str  # 퀴즈 ID, 문제 ID 등
    level: FeedbackLevel
    overall_score: float
    overall_message: str
    strengths: List[FeedbackItem] = field(default_factory=list)
    weaknesses: List[FeedbackItem] = field(default_factory=list)
    suggestions: List[FeedbackItem] = field(default_factory=list)
    achievements: List[FeedbackItem] = field(default_factory=list)
    learning_recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    encouragement_message: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "feedback_id": self.feedback_id,
            "feedback_type": self.feedback_type.value,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "level": self.level.value,
            "overall_score": self.overall_score,
            "overall_message": self.overall_message,
            "strengths": [item.to_dict() for item in self.strengths],
            "weaknesses": [item.to_dict() for item in self.weaknesses],
            "suggestions": [item.to_dict() for item in self.suggestions],
            "achievements": [item.to_dict() for item in self.achievements],
            "learning_recommendations": self.learning_recommendations,
            "next_steps": self.next_steps,
            "encouragement_message": self.encouragement_message,
            "created_at": self.created_at.isoformat()
        }


class FeedbackGenerator:
    """피드백 생성기"""

    def __init__(self):
        self.feedbacks: Dict[str, Feedback] = {}
        self.feedback_templates = self._load_feedback_templates()

        logger.info("피드백 생성기 초기화 완료")

    def _load_feedback_templates(self) -> Dict[str, Any]:
        """피드백 템플릿 로드"""
        return {
            "quiz": {
                "excellent": {
                    "message": "훌륭합니다! 이 주제를 완벽하게 이해하고 있습니다.",
                    "encouragement": "이러한 실력을 유지하면서 더 어려운 주제에도 도전해보세요!",
                    "next_steps": ["다음 단계의 주제로 넘어가세요", "다른 학생들에게 knowledge를 공유해보세요"]
                },
                "good": {
                    "message": "좋은 성적입니다. 약간의 추가 연습으로 완벽해질 수 있습니다.",
                    "encouragement": "계속해서 노력하면 곧 완벽하게 이해하게 될 것입니다!",
                    "next_steps": ["약간의 추가 연습이 필요합니다", "비슷한 유형의 문제를 더 풀어보세요"]
                },
                "needs_improvement": {
                    "message": "기본 개념은 이해하고 있으나, 더 많은 연습이 필요합니다.",
                    "encouragement": "포기하지 마세요! 연습하면 반드시 실력이 향상됩니다.",
                    "next_steps": ["해당 주제를 다시 학습하세요", "기본 개념을 복습하세요", "추가 문제를 풀어보세요"]
                },
                "beginner": {
                    "message": "해당 주제를 다시 학습하고 기본 개념을 복습하는 것이 좋겠습니다.",
                    "encouragement": "모든 개발자는 처음에는 초보자였습니다. 천천히 이해하며 나아가세요!",
                    "next_steps": ["기초부터 다시 학습하세요", "관련 학습 자료를 참고하세요", "튜터에게 질문하세요"]
                }
            },
            "coding": {
                "perfect": {
                    "message": "완벽한 코드입니다! 모든 테스트를 통과하고 코드 품질도 우수합니다.",
                    "encouragement": "이러한 코딩 실력을 자랑스럽게 생각하세요!",
                    "next_steps": ["더 복잡한 문제에 도전하세요", "최적화 기법을 학습하세요"]
                },
                "functional": {
                    "message": "코드가 정상적으로 동작합니다. 일부 개선의 여지가 있습니다.",
                    "encouragement": "작동하는 코드를 작성하는 것이 가장 중요합니다!",
                    "next_steps": ["코드 품질을 개선해보세요", "다른 풀이 방법도 탐색해보세요"]
                },
                "needs_work": {
                    "message": "일부 테스트를 통과하지 못했습니다. 코드를 수정해야 합니다.",
                    "encouragement": "디버깅 과정은 모든 개발자의 성장 경로에 필수적입니다!",
                    "next_steps": ["실패한 테스트 케이스를 분석하세요", "에러 메시지를 주의 깊게 읽어보세요", "작은 단위로 테스트해보세요"]
                },
                "critical": {
                    "message": "코드가 동작하지 않습니다. 전반적인 코드 검토가 필요합니다.",
                    "encouragement": "실패는 성공으로 가는 과정의 일부입니다. 다시 시도하세요!",
                    "next_steps": ["문제를 더 작은 단위로 나누세요", "샘플 해결책을 참고하세요", "튜터의 도움을 받으세요"]
                }
            }
        }

    def generate_feedback(
        self,
        feedback_type: FeedbackType,
        user_id: int,
        content_id: str,
        level: FeedbackLevel,
        score_data: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """피드백 생성"""
        feedback_id = str(uuid.uuid4())

        # 기본 피드백 구조 생성
        feedback = Feedback(
            feedback_id=feedback_id,
            feedback_type=feedback_type,
            user_id=user_id,
            content_id=content_id,
            level=level,
            overall_score=score_data.get("score", 0.0),
            overall_message="",
            encouragement_message=""
        )

        # 피드백 유형별 생성 로직
        if feedback_type == FeedbackType.QUIZ:
            self._generate_quiz_feedback(feedback, score_data, additional_context)
        elif feedback_type == FeedbackType.CODING:
            self._generate_coding_feedback(feedback, score_data, additional_context)
        elif feedback_type == FeedbackType.LEARNING_PATH:
            self._generate_learning_path_feedback(feedback, score_data, additional_context)
        else:
            self._generate_general_feedback(feedback, score_data, additional_context)

        # AI 기반 개선 피드백 생성 시도
        try:
            ai_feedback = self._generate_ai_feedback(feedback, score_data)
            if ai_feedback:
                feedback.suggestions.extend(ai_feedback)
        except Exception as e:
            logger.warning(f"AI 피드백 생성 실패: {e}")

        self.feedbacks[feedback_id] = feedback

        logger.info(f"피드백 생성 완료: {feedback_id} (타입: {feedback_type.value})")
        return feedback

    def _generate_quiz_feedback(
        self,
        feedback: Feedback,
        score_data: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]]
    ):
        """퀴즈 피드백 생성"""
        score_percentage = score_data.get("percentage", 0.0)
        total_questions = score_data.get("total_questions", 1)
        correct_count = score_data.get("correct_count", 0)

        # 성적 범주 결정
        if score_percentage >= 90:
            template = self.feedback_templates["quiz"]["excellent"]
        elif score_percentage >= 70:
            template = self.feedback_templates["quiz"]["good"]
        elif score_percentage >= 50:
            template = self.feedback_templates["quiz"]["needs_improvement"]
        else:
            template = self.feedback_templates["quiz"]["beginner"]

        feedback.overall_message = template["message"]
        feedback.encouragement_message = template["encouragement"]
        feedback.next_steps = template["next_steps"].copy()

        # 강점 분석
        if score_percentage >= 70:
            feedback.strengths.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="strength",
                title="높은 정답률",
                description=f"{total_questions}개 문제 중 {correct_count}개를 맞추었습니다.",
                priority="high"
            ))

        if score_data.get("time_taken", 0) < total_questions * 30:  # 문제당 30초 미만
            feedback.strengths.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="strength",
                title="빠른 해결 속도",
                description="빠르게 문제를 해결하는 능력이 있습니다.",
                priority="medium"
            ))

        # 약점 분석
        if score_percentage < 70:
            feedback.weaknesses.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="weakness",
                title="개선이 필요한 정답률",
                description=f"정답률이 {score_percentage:.0f}%로 개선이 필요합니다.",
                priority="high",
                actionable=True
            ))

        # 성채 분석
        if score_percentage == 100:
            feedback.achievements.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="achievement",
                title="완벽한 점수",
                description="모든 문제를 정답으로 맞추셨습니다!",
                priority="high"
            ))

    def _generate_coding_feedback(
        self,
        feedback: Feedback,
        score_data: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]]
    ):
        """코딩 문제 피드백 생성"""
        total_tests = score_data.get("total_tests", 1)
        passed_tests = score_data.get("passed_tests", 0)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # 코드 품질 정보
        code_quality = score_data.get("code_quality")

        # 성적 범주 결정
        if pass_rate == 100 and code_quality and code_quality.get("style_score", 0) > 80:
            template = self.feedback_templates["coding"]["perfect"]
        elif pass_rate >= 70:
            template = self.feedback_templates["coding"]["functional"]
        elif pass_rate >= 30:
            template = self.feedback_templates["coding"]["needs_work"]
        else:
            template = self.feedback_templates["coding"]["critical"]

        feedback.overall_message = template["message"]
        feedback.encouragement_message = template["encouragement"]
        feedback.next_steps = template["next_steps"].copy()

        # 강점 분석
        if pass_rate == 100:
            feedback.strengths.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="strength",
                title="모든 테스트 통과",
                description="모든 테스트 케이스를 성공적으로 통과했습니다.",
                priority="high"
            ))

        if code_quality:
            if code_quality.get("complexity_score", 0) > 80:
                feedback.strengths.append(FeedbackItem(
                    item_id=str(uuid.uuid4()),
                    category="strength",
                    title="우수한 코드 복잡도",
                    description="코드가 간결하고 이해하기 쉽습니다.",
                    priority="medium"
                ))

            if code_quality.get("style_score", 0) > 80:
                feedback.strengths.append(FeedbackItem(
                    item_id=str(uuid.uuid4()),
                    category="strength",
                    title="우수한 코드 스타일",
                    description="코딩 스타일이 잘 지켜져 있습니다.",
                    priority="medium"
                ))

        # 약점 분석
        if pass_rate < 100:
            failed_count = total_tests - passed_tests
            feedback.weaknesses.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="weakness",
                title=f"{failed_count}개의 테스트 실패",
                description="일부 테스트 케이스를 통과하지 못했습니다.",
                priority="high",
                actionable=True
            ))

        if code_quality:
            if code_quality.get("complexity_score", 100) < 50:
                feedback.weaknesses.append(FeedbackItem(
                    item_id=str(uuid.uuid4()),
                    category="weakness",
                    title="높은 코드 복잡도",
                    description="코드 복잡도가 높습니다. 간단하게 만들 수 있는지 확인해보세요.",
                    priority="medium",
                    actionable=True,
                    resources=["코드 리팩토링 가이드", "함수 분할 방법"]
                ))

            if code_quality.get("style_score", 100) < 50:
                feedback.weaknesses.append(FeedbackItem(
                    item_id=str(uuid.uuid4()),
                    category="weakness",
                    title="개선이 필요한 코드 스타일",
                    description="코딩 스타일 개선이 필요합니다.",
                    priority="low",
                    actionable=True,
                    resources=["PEP 8 스타일 가이드"]
                ))

        # 성채 분석
        if pass_rate == 100:
            feedback.achievements.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="achievement",
                title="테스트 마스터",
                description="모든 테스트를 통과하여 문제를 해결했습니다!",
                priority="high"
            ))

    def _generate_learning_path_feedback(
        self,
        feedback: Feedback,
        score_data: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]]
    ):
        """학습 경로 피드백 생성"""
        completed_topics = score_data.get("completed_topics", [])
        total_topics = score_data.get("total_topics", 1)
        progress = (len(completed_topics) / total_topics * 100) if total_topics > 0 else 0

        feedback.overall_message = f"학습 진행률: {progress:.0f}%"
        feedback.encouragement_message = "꾸준히 학습하면 목표를 달성할 수 있습니다!"

        if progress >= 50:
            feedback.strengths.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="strength",
                title="꾸준한 학습",
                description="학습 과정의 절반 이상을 완료했습니다.",
                priority="high"
            ))

        if progress < 30:
            feedback.weaknesses.append(FeedbackItem(
                item_id=str(uuid.uuid4()),
                category="weakness",
                title="낮은 학습 진행률",
                description="학습 진행률을 높이기 위해 더 규칙적으로 학습하세요.",
                priority="high",
                actionable=True
            ))

        # 다음 단계 제안
        next_topic = score_data.get("next_topic")
        if next_topic:
            feedback.next_steps.append(f"{next_topic} 주제 학습")

    def _generate_general_feedback(
        self,
        feedback: Feedback,
        score_data: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]]
    ):
        """일반 피드백 생성"""
        score = score_data.get("score", 0.0)
        max_score = score_data.get("max_score", 100.0)
        percentage = (score / max_score * 100) if max_score > 0 else 0

        if percentage >= 80:
            feedback.overall_message = "훌륵한 성과입니다!"
            feedback.encouragement_message = "이러한 실력을 계속 유지하세요!"
        elif percentage >= 60:
            feedback.overall_message = "좋은 성과입니다."
            feedback.encouragement_message = "계속 노력하면 더 나아질 것입니다!"
        else:
            feedback.overall_message = "개선이 필요합니다."
            feedback.encouragement_message = "포기하지 마세요. 계속 노력하면 실력이 향상됩니다!"

    def _generate_ai_feedback(
        self,
        feedback: Feedback,
        score_data: Dict[str, Any]
    ) -> List[FeedbackItem]:
        """AI 기반 개인화 피드백 생성"""
        try:
            from src.ai.claude_client import get_claude_client

            client = get_claude_client()

            # 피드백 요약 정보
            feedback_summary = {
                "type": feedback.feedback_type.value,
                "score": feedback.overall_score,
                "level": feedback.level.value,
                "strengths": [s.description for s in feedback.strengths],
                "weaknesses": [w.description for w in feedback.weaknesses]
            }

            prompt = f"""
다음 학습 결과에 대한 개인화된 피드백과 개선 제안을 생성해주세요.

학습 결과:
{json.dumps(feedback_summary, ensure_ascii=False, indent=2)}

요구사항:
1. 구체적이고 실행 가능한 피드백 3-5개
2. 학생 수준에 맞는 언어 ({feedback.level.value})
3. 동기부여가 되는 내용
4. 실용적인 학습 자료 추천

응답 형식 (JSON):
[
  {{
    "title": "피드백 제목",
    "description": "상세 설명",
    "priority": "high|medium|low",
    "actionable": true,
    "category": "suggestion"
  }}
]
"""

            response = client.send_message(
                message=prompt,
                system_prompt="당신은 Python 교육 전문가이자 멘토입니다. 학생들의 성장을 위한 개인화된 피드백을 제공합니다.",
                max_tokens=1500
            )

            # JSON 파싱
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggestions_data = json.loads(json_match.group())

                suggestions = []
                for s_data in suggestions_data:
                    suggestion = FeedbackItem(
                        item_id=str(uuid.uuid4()),
                        category=s_data.get("category", "suggestion"),
                        title=s_data["title"],
                        description=s_data["description"],
                        priority=s_data.get("priority", "medium"),
                        actionable=s_data.get("actionable", True)
                    )
                    suggestions.append(suggestion)

                return suggestions

        except Exception as e:
            logger.error(f"AI 피드백 생성 실패: {e}")

        return []

    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """피드백 반환"""
        return self.feedbacks.get(feedback_id)

    def get_user_feedbacks(self, user_id: int) -> List[Feedback]:
        """사용자의 모든 피드백 반환"""
        return [f for f in self.feedbacks.values() if f.user_id == user_id]

    def generate_summary_report(
        self,
        user_id: int,
        feedback_type: Optional[FeedbackType] = None
    ) -> Dict[str, Any]:
        """사용자 피드백 요약 리포트 생성"""
        user_feedbacks = self.get_user_feedbacks(user_id)

        if feedback_type:
            user_feedbacks = [f for f in user_feedbacks if f.feedback_type == feedback_type]

        if not user_feedbacks:
            return {
                "user_id": user_id,
                "total_feedbacks": 0,
                "average_score": 0.0,
                "common_strengths": [],
                "common_weaknesses": [],
                "recommendations": []
            }

        # 통계 분석
        total_score = sum(f.overall_score for f in user_feedbacks)
        average_score = total_score / len(user_feedbacks)

        # 공통 강점 및 약점 추출
        strength_counts = {}
        weakness_counts = {}

        for feedback in user_feedbacks:
            for strength in feedback.strengths:
                key = strength.title
                strength_counts[key] = strength_counts.get(key, 0) + 1

            for weakness in feedback.weaknesses:
                key = weakness.title
                weakness_counts[key] = weakness_counts.get(key, 0) + 1

        # 가장 빈번한 강점 및 약점
        common_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        common_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # 종합 추천
        recommendations = []
        if average_score >= 80:
            recommendations.append("전반적으로 우수한 성과를 보이고 있습니다. 더 어려운 주제에 도전해보세요.")
        elif average_score >= 60:
            recommendations.append("꾸준한 향상이 있습니다. 약점을 보완하며 실력을 키워가세요.")
        else:
            recommendations.append("기본 개념을 다시 복습하고 추가 연습이 필요합니다.")

        return {
            "user_id": user_id,
            "total_feedbacks": len(user_feedbacks),
            "average_score": average_score,
            "common_strengths": [{"title": title, "count": count} for title, count in common_strengths],
            "common_weaknesses": [{"title": title, "count": count} for title, count in common_weaknesses],
            "recommendations": recommendations,
            "feedback_type": feedback_type.value if feedback_type else "all"
        }


# 전역 인스턴스
feedback_generator = None


def get_feedback_generator() -> FeedbackGenerator:
    """피드백 생성기 인스턴스 반환"""
    global feedback_generator
    if feedback_generator is None:
        feedback_generator = FeedbackGenerator()
    return feedback_generator


if __name__ == "__main__":
    # 피드백 생성기 테스트
    print("🧪 피드백 생성기 테스트")

    generator = FeedbackGenerator()

    # 퀴즈 피드백 테스트
    print("\n📝 퀴즈 피드백:")
    quiz_feedback = generator.generate_feedback(
        feedback_type=FeedbackType.QUIZ,
        user_id=1,
        content_id="quiz_1",
        level=FeedbackLevel.BEGINNER,
        score_data={
            "score": 80.0,
            "percentage": 80.0,
            "total_questions": 10,
            "correct_count": 8,
            "time_taken": 200.0
        }
    )

    print(f"✅ 피드백 생성: {quiz_feedback.feedback_id}")
    print(f"   전체 메시지: {quiz_feedback.overall_message}")
    print(f"   격려 메시지: {quiz_feedback.encouragement_message}")
    print(f"   강점 수: {len(quiz_feedback.strengths)}")
    print(f"   약점 수: {len(quiz_feedback.weaknesses)}")
    print(f"   제안 수: {len(quiz_feedback.suggestions)}")

    # 코딩 피드백 테스트
    print("\n💻 코딩 피드백:")
    coding_feedback = generator.generate_feedback(
        feedback_type=FeedbackType.CODING,
        user_id=1,
        content_id="problem_1",
        level=FeedbackLevel.INTERMEDIATE,
        score_data={
            "score": 75.0,
            "total_tests": 10,
            "passed_tests": 7,
            "code_quality": {
                "complexity_score": 75.0,
                "style_score": 60.0,
                "readability_score": 70.0,
                "best_practices_score": 80.0
            }
        }
    )

    print(f"✅ 피드백 생성: {coding_feedback.feedback_id}")
    print(f"   전체 메시지: {coding_feedback.overall_message}")
    print(f"   강점 수: {len(coding_feedback.strengths)}")
    print(f"   약점 수: {len(coding_feedback.weaknesses)}")

    # 요약 리포트
    print("\n📊 요약 리포트:")
    summary = generator.generate_summary_report(user_id=1)
    print(f"   총 피드백 수: {summary['total_feedbacks']}")
    print(f"   평균 점수: {summary['average_score']:.1f}")
    print(f"   공통 강점: {[s['title'] for s in summary['common_strengths']]}")
    print(f"   공통 약점: {[w['title'] for w in summary['common_weaknesses']]}")

    print("\n🎉 피드백 생성기 테스트 완료!")