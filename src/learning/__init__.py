"""
학습 패키지
학습 시스템의 중앙 관리 패키지
"""
from src.learning.curriculum import (
    Exercise,
    Topic,
    LearningPath,
    LearningState,
    DifficultyLevel,
    ExerciseType,
    CurriculumManager,
    get_curriculum_manager
)
from src.learning.progress import (
    ProgressCalculator,
    get_progress_calculator,
    ProgressTracker,
    get_progress_tracker
)
from src.learning.achievements import (
    AchievementManager,
    get_achievement_manager
)
from src.learning.progress.adaptive_difficulty import (
    AdaptiveDifficulty,
    get_adaptive_difficulty
)

__all__ = [
    # Curriculum
    'Exercise',
    'Topic',
    'LearningPath',
    'LearningState',
    'DifficultyLevel',
    'ExerciseType',
    'CurriculumManager',
    'get_curriculum_manager',
    # Progress
    'ProgressCalculator',
    'get_progress_calculator',
    'ProgressTracker',
    'get_progress_tracker',
    # Achievements
    'AchievementManager',
    'get_achievement_manager',
    # Adaptive
    'AdaptiveDifficulty',
    'get_adaptive_difficulty'
]