"""
데이터베이스 마이그레이션: 학습 시스템 테이블 추가
"""
import sqlite3
from pathlib import Path
from loguru import logger
from typing import Optional


class Migration002LearningSystem:
    """학습 시스템 테이블 추가 마이그레이션"""

    def __init__(self, db_path: str = "codementorai.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """데이터베이스 연결"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"데이터베이스 연결 완료: {self.db_path}")
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("데이터베이스 연결 종료")

    def upgrade(self):
        """마이그레이션 실행 (테이블 생성)"""
        try:
            logger.info("마이그레이션 002 시작: 학습 시스템 테이블 추가")

            # 연습 문제 테이블
            self._create_exercises_table()

            # 학습 활동 테이블
            self._create_learning_activities_table()

            # 성취 규칙 테이블
            self._create_achievement_rules_table()

            # 사용자 성취 진도 테이블
            self._create_user_achievement_progress_table()

            # 기본 성취 규칙 추가
            self._insert_default_achievement_rules()

            self.conn.commit()
            logger.info("✅ 마이그레이션 002 완료")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"마이그레이션 002 실패: {e}")
            raise

    def downgrade(self):
        """마이그레이션 롤백 (테이블 삭제)"""
        try:
            logger.info("마이그레이션 002 롤백 시작")

            self.cursor.execute("DROP TABLE IF EXISTS user_achievement_progress")
            self.cursor.execute("DROP TABLE IF EXISTS achievement_rules")
            self.cursor.execute("DROP TABLE IF EXISTS learning_activities")
            self.cursor.execute("DROP TABLE IF EXISTS exercises")

            self.conn.commit()
            logger.info("✅ 마이그레이션 002 롤백 완료")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"마이그레이션 002 롤백 실패: {e}")
            raise

    def _create_exercises_table(self):
        """연습 문제 테이블 생성"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    exercise_type TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    starter_code TEXT,
                    solution TEXT,
                    hints TEXT,
                    time_estimate INTEGER DEFAULT 30,
                    xp_reward INTEGER DEFAULT 10,
                    prerequisites TEXT,
                    learning_objectives TEXT,
                    test_cases TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.debug("연습 문제 테이블 생성 완료")

            # 인덱스 생성
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_exercises_difficulty
                ON exercises(difficulty)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_exercises_topic
                ON exercises(topic)
            """)

        except Exception as e:
            logger.error(f"연습 문제 테이블 생성 실패: {e}")
            raise

    def _create_learning_activities_table(self):
        """학습 활동 테이블 생성"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exercise_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL,
                    score INTEGER,
                    time_spent INTEGER DEFAULT 0,
                    xp_earned INTEGER DEFAULT 0,
                    code_submitted TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
                )
            """)
            logger.debug("학습 활동 테이블 생성 완료")

            # 인덱스 생성
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_learning_activities_user
                ON learning_activities(user_id)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_learning_activities_exercise
                ON learning_activities(exercise_id)
            """)

        except Exception as e:
            logger.error(f"학습 활동 테이블 생성 실패: {e}")
            raise

    def _create_achievement_rules_table(self):
        """성취 규칙 테이블 생성"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievement_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    achievement_type TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    condition_config TEXT,
                    xp_reward INTEGER DEFAULT 0,
                    badge_icon TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.debug("성취 규칙 테이블 생성 완료")

        except Exception as e:
            logger.error(f"성취 규칙 테이블 생성 실패: {e}")
            raise

    def _create_user_achievement_progress_table(self):
        """사용자 성취 진도 테이블 생성"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_achievement_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_rule_id TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    target_value INTEGER,
                    completed BOOLEAN DEFAULT FALSE,
                    completed_at TIMESTAMP NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (achievement_rule_id) REFERENCES achievement_rules(id),
                    UNIQUE(user_id, achievement_rule_id)
                )
            """)
            logger.debug("사용자 성취 진도 테이블 생성 완료")

            # 인덱스 생성
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_achievement_progress_user
                ON user_achievement_progress(user_id)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_achievement_progress_rule
                ON user_achievement_progress(achievement_rule_id)
                """)

        except Exception as e:
            logger.error(f"사용자 성취 진도 테이블 생성 실패: {e}")
            raise

    def _insert_default_achievement_rules(self):
        """기본 성취 규칙 추가"""
        try:
            import json

            default_rules = [
                {
                    "id": "first_code",
                    "name": "첫 번째 코드",
                    "description": "첫 번째 코드를 제출했습니다",
                    "achievement_type": "first_code",
                    "event_type": "exercise_submit",
                    "condition_config": json.dumps({"count": 1}),
                    "xp_reward": 10,
                    "badge_icon": "🎯"
                },
                {
                    "id": "perfect_score",
                    "name": "완벽 점수",
                    "description": "완벽한 점수를 받았습니다",
                    "achievement_type": "perfect_score",
                    "event_type": "exercise_submit",
                    "condition_config": json.dumps({"score": 10}),
                    "xp_reward": 20,
                    "badge_icon": "⭐"
                },
                {
                    "id": "streak_5",
                    "name": "5연승",
                    "description": "5개 연속 문제를 완료했습니다",
                    "achievement_type": "streak",
                    "event_type": "exercise_complete",
                    "condition_config": json.dumps({"streak": 5}),
                    "xp_reward": 30,
                    "badge_icon": "🔥"
                },
                {
                    "id": "streak_10",
                    "name": "10연승",
                    "description": "10개 연속 문제를 완료했습니다",
                    "achievement_type": "streak",
                    "event_type": "exercise_complete",
                    "condition_config": json.dumps({"streak": 10}),
                    "xp_reward": 50,
                    "badge_icon": "💯"
                },
                {
                    "id": "completed_topic",
                    "name": "주제 완료",
                    "description": "첫 번째 주제를 완료했습니다",
                    "achievement_type": "topic_complete",
                    "event_type": "topic_complete",
                    "condition_config": json.dumps({"topics": 1}),
                    "xp_reward": 40,
                    "badge_icon": "📚"
                },
                {
                    "id": "level_up_beginner",
                    "name": "초급 달성",
                    "description": "초급 과정을 완료했습니다",
                    "achievement_type": "level_complete",
                    "event_type": "level_complete",
                    "condition_config": json.dumps({"level": "beginner"}),
                    "xp_reward": 100,
                    "badge_icon": "🎓"
                },
                {
                    "id": "xp_100",
                    "name": "100 XP",
                    "description": "100 XP를 획득했습니다",
                    "achievement_type": "xp_milestone",
                    "event_type": "xp_earn",
                    "condition_config": json.dumps({"xp": 100}),
                    "xp_reward": 0,
                    "badge_icon": "💎"
                },
                {
                    "id": "xp_500",
                    "name": "500 XP",
                    "description": "500 XP를 획득했습니다",
                    "achievement_type": "xp_milestone",
                    "event_type": "xp_earn",
                    "condition_config": json.dumps({"xp": 500}),
                    "xp_reward": 0,
                    "badge_icon": "👑"
                }
            ]

            for rule in default_rules:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO achievement_rules
                    (id, name, description, achievement_type, event_type, condition_config, xp_reward, badge_icon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule["id"],
                    rule["name"],
                    rule["description"],
                    rule["achievement_type"],
                    rule["event_type"],
                    rule["condition_config"],
                    rule["xp_reward"],
                    rule["badge_icon"]
                ))

            logger.debug(f"기본 성취 규칙 {len(default_rules)}개 추가 완료")

        except Exception as e:
            logger.error(f"기본 성취 규칙 추가 실패: {e}")
            raise

    def run(self, direction: str = "up"):
        """마이그레이션 실행"""
        try:
            self.connect()

            if direction == "up":
                self.upgrade()
            elif direction == "down":
                self.downgrade()
            else:
                raise ValueError(f"잘못된 방향: {direction}")

            logger.info(f"마이그레이션 002 {'실행' if direction == 'up' else '롤백'} 완료")

        except Exception as e:
            logger.error(f"마이그레이션 002 실행 실패: {e}")
            raise
        finally:
            self.close()


def run_migration(db_path: str = "codementorai.db", direction: str = "up"):
    """마이그레이션 실행 함수"""
    migration = Migration002LearningSystem(db_path)
    migration.run(direction)


if __name__ == "__main__":
    # 마이그레이션 테스트
    print("🧪 마이그레이션 002 테스트")

    # 테스트용 데이터베이스 파일
    test_db = "test_migration.db"

    try:
        # 업그레이드
        print("⬆️  업그레이드 실행 중...")
        run_migration(test_db, "up")
        print("✅ 업그레이드 완료")

        # 롤백
        print("⬇️  롤백 실행 중...")
        run_migration(test_db, "down")
        print("✅ 롤백 완료")

        # 재업그레이드
        print("⬆️  재업그레이드 실행 중...")
        run_migration(test_db, "up")
        print("✅ 재업그레이드 완료")

        print("\n🎉 마이그레이션 002 테스트 통과!")

    except Exception as e:
        print(f"❌ 마이그레이션 002 테스트 실패: {e}")

    finally:
        # 테스트 파일 삭제
        import os
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"🗑️  테스트 파일 삭제: {test_db}")