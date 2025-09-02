#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import DATABASE_URL
from sqlalchemy import create_engine, text

def check_topics_table():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # topics 테이블 확인
        result = conn.execute(text('SELECT key, title FROM topics LIMIT 10'))
        print('기존 topics 테이블:')
        for row in result:
            print(f'  {row[0]}: {row[1]}')
        
        # 외래키 제약조건 확인
        result2 = conn.execute(text("""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'subject_topics'::regclass AND contype = 'f'
        """))
        print('\nsubject_topics 외래키 제약조건:')
        for row in result2:
            print(f'  {row[0]}: {row[1]}')

if __name__ == "__main__":
    check_topics_table()
