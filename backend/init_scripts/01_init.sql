-- LMS MVP 데이터베이스 초기화 스크립트
-- 이 스크립트는 PostgreSQL 컨테이너 시작 시 자동으로 실행됩니다.

-- UTF8 인코딩 설정 확인
SHOW server_encoding;

-- 필요한 확장 프로그램 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 인덱스 최적화를 위한 설정
SET maintenance_work_mem = '64MB';

-- 기본 스키마 확인
\dt

-- 로그 출력
DO $$
BEGIN
    RAISE NOTICE '=== LMS MVP 데이터베이스 초기화 완료 ===';
    RAISE NOTICE '데이터베이스: %', current_database();
    RAISE NOTICE '사용자: %', current_user;
    RAISE NOTICE '시간: %', now();
END $$;
