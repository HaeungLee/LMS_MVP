#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import DATABASE_URL
from sqlalchemy import create_engine, text

def check_table_structure():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # 테이블 구조 확인
        result = conn.execute(text("""
            SELECT column_name, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'subject_topics' 
            ORDER BY ordinal_position
        """))
        print('subject_topics 테이블 구조:')
        for row in result:
            print(f'  {row[0]}: nullable={row[1]}, default={row[2]}')

if __name__ == "__main__":
    check_table_structure()
