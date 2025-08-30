"""
과목 관리 서비스
다중 과목 지원을 위한 핵심 서비스
"""
from typing import List, Dict, Optional, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

class SubjectManager:
    """과목 관리 서비스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_all_subjects(self, db: Session) -> List[Dict[str, Any]]:
        """모든 과목 목록 조회"""
        try:
            result = db.execute(text("""
                SELECT
                    s.id, s.key, s.title, s.version, s.created_at,
                    COUNT(st.id) as topic_count,
                    COUNT(CASE WHEN st.is_core THEN 1 END) as core_topic_count
                FROM subjects s
                LEFT JOIN subject_topics st ON s.key = st.subject_key
                GROUP BY s.id, s.key, s.title, s.version, s.created_at
                ORDER BY s.title
            """))

            subjects = []
            for row in result.fetchall():
                subjects.append({
                    'id': row[0],
                    'key': row[1],
                    'title': row[2],
                    'version': row[3],
                    'created_at': row[4],
                    'topic_count': row[5],
                    'core_topic_count': row[6]
                })

            return subjects

        except Exception as e:
            self.logger.error(f"과목 목록 조회 실패: {e}")
            return []

    async def get_subject_topics(self, db: Session, subject_key: str) -> List[Dict[str, Any]]:
        """특정 과목의 토픽 목록 조회"""
        try:
            result = db.execute(text("""
                SELECT
                    t.id, t.key, t.title,
                    st.weight, st.is_core, st.display_order, st.show_in_coverage
                FROM topics t
                JOIN subject_topics st ON t.key = st.topic_key
                WHERE st.subject_key = :subject_key
                ORDER BY st.display_order
            """), {'subject_key': subject_key})

            topics = []
            for row in result.fetchall():
                topics.append({
                    'id': row[0],
                    'key': row[1],
                    'title': row[2],
                    'weight': float(row[3]),
                    'is_core': row[4],
                    'display_order': row[5],
                    'show_in_coverage': row[6]
                })

            return topics

        except Exception as e:
            self.logger.error(f"과목 토픽 조회 실패: {e}")
            return []

    async def get_subject_by_key(self, db: Session, subject_key: str) -> Optional[Dict[str, Any]]:
        """과목 키로 과목 정보 조회"""
        try:
            result = db.execute(text("""
                SELECT
                    s.id, s.key, s.title, s.version, s.created_at,
                    COUNT(st.id) as topic_count
                FROM subjects s
                LEFT JOIN subject_topics st ON s.key = st.subject_key
                WHERE s.key = :subject_key
                GROUP BY s.id, s.key, s.title, s.version, s.created_at
            """), {'subject_key': subject_key})

            row = result.fetchone()
            if row:
                return {
                    'id': row[0],
                    'key': row[1],
                    'title': row[2],
                    'version': row[3],
                    'created_at': row[4],
                    'topic_count': row[5]
                }
            return None

        except Exception as e:
            self.logger.error(f"과목 정보 조회 실패: {e}")
            return None

    async def get_subject_with_topics(self, db: Session, subject_key: str) -> Optional[Dict[str, Any]]:
        """과목 정보와 토픽 목록을 함께 조회"""
        try:
            # 과목 정보 조회
            subject = await self.get_subject_by_key(db, subject_key)
            if not subject:
                return None

            # 토픽 목록 조회
            topics = await self.get_subject_topics(db, subject_key)

            return {
                **subject,
                'topics': topics
            }

        except Exception as e:
            self.logger.error(f"과목 상세 정보 조회 실패: {e}")
            return None

    async def validate_subject_access(self, db: Session, subject_key: str, user_id: int = None) -> bool:
        """과목 접근 권한 검증"""
        try:
            # 과목 존재 여부 확인
            subject = await self.get_subject_by_key(db, subject_key)
            if not subject:
                return False

            # TODO: 사용자별 과목 접근 권한 로직 추가
            # 현재는 모든 과목에 대한 접근을 허용
            return True

        except Exception as e:
            self.logger.error(f"과목 접근 권한 검증 실패: {e}")
            return False

    async def get_subject_statistics(self, db: Session) -> Dict[str, Any]:
        """과목 통계 정보 조회"""
        try:
            # 전체 통계
            total_stats = db.execute(text("""
                SELECT
                    COUNT(DISTINCT s.id) as total_subjects,
                    COUNT(DISTINCT st.topic_key) as total_topics,
                    COUNT(st.id) as total_connections
                FROM subjects s
                LEFT JOIN subject_topics st ON s.key = st.subject_key
            """)).fetchone()

            # 과목별 통계
            subject_stats = db.execute(text("""
                SELECT
                    s.key, s.title,
                    COUNT(st.id) as topic_count,
                    COUNT(CASE WHEN st.is_core THEN 1 END) as core_topics,
                    AVG(st.weight) as avg_weight
                FROM subjects s
                LEFT JOIN subject_topics st ON s.key = st.subject_key
                GROUP BY s.id, s.key, s.title
                ORDER BY s.title
            """)).fetchall()

            return {
                'total_subjects': total_stats[0],
                'total_topics': total_stats[1],
                'total_connections': total_stats[2],
                'subject_details': [
                    {
                        'key': row[0],
                        'title': row[1],
                        'topic_count': row[2],
                        'core_topics': row[3],
                        'avg_weight': float(row[4]) if row[4] else 0.0
                    }
                    for row in subject_stats
                ]
            }

        except Exception as e:
            self.logger.error(f"과목 통계 조회 실패: {e}")
            return {
                'total_subjects': 0,
                'total_topics': 0,
                'total_connections': 0,
                'subject_details': []
            }

# 전역 인스턴스
subject_manager = SubjectManager()

def get_subject_manager() -> SubjectManager:
    """과목 관리자 인스턴스 반환"""
    return subject_manager
