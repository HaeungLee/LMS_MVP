#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import DATABASE_URL
from sqlalchemy import create_engine, text

def check_subjects():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT key, title FROM subjects'))
        print('기존 subjects 테이블:')
        for row in result:
            print(f'  {row[0]}: {row[1]}')

if __name__ == "__main__":
    check_subjects()
