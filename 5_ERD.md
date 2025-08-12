## LMS 핵심 ERD 초안 (Mermaid)

```mermaid
erDiagram
  USER ||--o{ ENROLLMENT : enrolls
  USER ||--o{ SUBMISSION : makes
  USER {
    int id PK
    string username
    string email
    string password_hash
    string role  "student|teacher|admin"
    datetime created_at
    bool is_active
  }

  ORGANIZATION ||--o{ COURSE : offers
  ORGANIZATION {
    int id PK
    string name
    datetime created_at
  }

  COURSE ||--o{ MODULE : contains
  COURSE ||--o{ ENROLLMENT : has
  COURSE {
    int id PK
    int organization_id FK
    string title
    string description
    datetime created_at
    int created_by FK "USER.id"
  }

  MODULE ||--o{ LESSON : contains
  MODULE ||--o{ QUIZ : includes
  MODULE {
    int id PK
    int course_id FK
    string title
    int order_index
  }

  LESSON {
    int id PK
    int module_id FK
    string title
    text content_url
    int order_index
  }

  ENROLLMENT {
    int id PK
    int user_id FK
    int course_id FK
    string status "active|completed|dropped"
    datetime enrolled_at
    datetime completed_at
  }

  QUIZ ||--o{ QUIZ_ATTEMPT : has
  QUIZ ||--o{ QUIZ_QUESTION : maps
  QUIZ {
    int id PK
    int module_id FK
    string title
    float weight "grade weight"
    datetime due_at
    int time_limit_seconds
    bool randomized
  }

  QUESTION ||--o{ QUIZ_QUESTION : appears
  QUESTION ||--o{ SUBMISSION_ITEM : targeted_by
  QUESTION {
    int id PK
    string subject
    string topic
    string question_type "mcq|fill|coding|essay"
    text stem
    text code_snippet
    jsonb options
    text correct_answer
    string answer_type "exact|exec|llm"
    text grading_rubric
    string difficulty "easy|medium|hard"
    int created_by FK "USER.id"
    datetime created_at
    int version
    bool is_active
  }

  QUIZ_QUESTION {
    int id PK
    int quiz_id FK
    int question_id FK
    int order_index
    float points
  }

  QUIZ_ATTEMPT ||--o{ SUBMISSION_ITEM : contains
  QUIZ_ATTEMPT {
    int id PK
    int quiz_id FK
    int user_id FK
    int enrollment_id FK
    datetime started_at
    datetime submitted_at
    int time_spent_seconds
    float total_score
    string status "in_progress|submitted|graded"
  }

  SUBMISSION ||--o{ SUBMISSION_ITEM : groups
  SUBMISSION {
    int id PK
    int quiz_attempt_id FK
    float total_score
    datetime submitted_at
  }

  SUBMISSION_ITEM ||--o{ FEEDBACK : has
  SUBMISSION_ITEM {
    int id PK
    int submission_id FK
    int question_id FK
    text user_answer
    bool skipped
    float score
    text auto_feedback "template/LLM short"
  }

  FEEDBACK {
    int id PK
    int submission_item_id FK
    bool ai_generated
    text feedback_text
    jsonb detail_scores
    datetime created_at
  }

  USER ||--o{ ACTIVITY_LOG : generates
  ACTIVITY_LOG {
    int id PK
    int user_id FK
    string activity_type
    jsonb details
    datetime created_at
  }
```

설명
- 핵심 흐름: USER가 COURSE에 ENROLLMENT → MODULE/QUIZ 진행 → QUIZ_ATTEMPT 생성 → SUBMISSION/SUBMISSION_ITEM 저장 → FEEDBACK 생성.
- 문제은행은 `QUESTION` 단일 테이블 + 버전 필드로 관리(간단화). 버전 세분화가 필요하면 별도 `QUESTION_VERSION` 테이블 분리 가능.
- 성적 집계는 `QUIZ_ATTEMPT.total_score` 기준, COURSE 레벨 집계는 뷰/머티리얼라이즈드 뷰로 확장 가능.


