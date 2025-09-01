"""
새로운 과목 (데이터 분석, 웹 크롤링) 데이터베이스 초기화 스크립트
"""
import asyncio
import sys
import os

# 백엔드 패키지 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.orm import Question
from app.core.database import SessionLocal
from app.services.new_subject_generator import get_all_new_subject_questions
from app.core.subjects import SUBJECTS, SUBJECT_TOPICS
import json

def add_new_subject_questions():
    """새로운 과목 문제들을 데이터베이스에 추가"""
    
    print("🚀 새로운 과목 초기화를 시작합니다...")
    
    # 데이터베이스 세션 생성
    session = SessionLocal()
    try:
        # 새로운 과목 문제들 가져오기
        new_questions = get_all_new_subject_questions()
        
        print(f"📝 총 {len(new_questions)}개의 새로운 문제를 추가합니다...")
        
        added_count = 0
        for question_data in new_questions:
            # 중복 검사
            existing = session.get(Question, question_data["id"])
            if existing:
                print(f"⚠️  문제 {question_data['id']} 이미 존재함 - 건너뜀")
                continue
            
            # 새 문제 생성
            new_question = Question(
                id=question_data["id"],
                subject=question_data["subject"],
                topic=question_data["topic"],
                question_type=question_data["question_type"],
                code_snippet=question_data["code_snippet"],
                correct_answer=question_data["correct_answer"],
                difficulty=str(question_data["difficulty"]),
                question_data=json.dumps(question_data["question_data"], ensure_ascii=False),
                metadata=json.dumps(question_data["metadata"], ensure_ascii=False),
                ai_generated=True
            )
            
            session.add(new_question)
            added_count += 1
            print(f"✅ 추가됨: {question_data['id']} ({question_data['subject']} - {question_data['topic']})")
        
        # 변경사항 커밋
        session.commit()
        
        print(f"\n🎉 새로운 과목 초기화 완료!")
        print(f"📊 추가된 문제 수: {added_count}개")
        
        # 과목별 통계 출력
        print(f"\n📈 과목별 현황:")
        for subject_key, subject_name in SUBJECTS.items():
            subject_questions = [q for q in new_questions if q['subject'] == subject_key]
            print(f"  • {subject_name}: {len(subject_questions)}개 문제")
            
            # 토픽별 세부 현황
            if subject_key in SUBJECT_TOPICS:
                for topic_key, topic_name in SUBJECT_TOPICS[subject_key].items():
                    topic_questions = [q for q in subject_questions if q['topic'] == topic_key]
                    if topic_questions:
                        print(f"    - {topic_name}: {len(topic_questions)}개")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 오류 발생: {e}")
        raise
    finally:
        session.close()

def verify_new_subjects():
    """새로운 과목 데이터 검증"""
    print("\n🔍 데이터 검증을 시작합니다...")
    
    session = SessionLocal()
    try:
        # 각 과목별 문제 수 확인
        for subject_key, subject_name in SUBJECTS.items():
            from sqlalchemy import func
            
            # 전체 문제 수
            total_count = session.query(func.count(Question.id)).filter(Question.subject == subject_key).scalar()
            
            # 토픽별 문제 수
            topic_counts = {}
            if subject_key in SUBJECT_TOPICS:
                for topic_key in SUBJECT_TOPICS[subject_key].keys():
                    count = session.query(func.count(Question.id)).filter(
                        Question.subject == subject_key,
                        Question.topic == topic_key
                    ).scalar()
                    topic_counts[topic_key] = count
            
            print(f"\n📚 {subject_name} (총 {total_count}개 문제)")
            for topic_key, count in topic_counts.items():
                if count > 0:
                    topic_name = SUBJECT_TOPICS[subject_key][topic_key]
                    print(f"  • {topic_name}: {count}개")
    finally:
        session.close()

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🎓 LMS MVP - 새로운 과목 초기화")
    print("=" * 60)
    
    try:
        # 1. 새로운 과목 문제 추가
        add_new_subject_questions()
        
        # 2. 데이터 검증
        verify_new_subjects()
        
        print(f"\n✨ 모든 작업이 성공적으로 완료되었습니다!")
        print(f"💡 새로운 과목들:")
        for subject_key, subject_name in SUBJECTS.items():
            if subject_key != 'python_basics':  # 기존 과목 제외
                print(f"   🔸 {subject_name}")
        
    except Exception as e:
        print(f"\n💥 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
