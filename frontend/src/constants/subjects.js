/**
 * 과목 및 토픽 상수 정의
 * SaaS 개발자 양성 과정을 위한 과목 구조
 */

// 전체 과목 정의
export const SUBJECTS = {
  python_basics: 'Python 기초',
  data_analysis: '데이터 분석',
  web_crawling: '웹 크롤링'
};

// 과목별 세부 토픽
export const SUBJECT_TOPICS = {
  python_basics: {
    variables: '변수와 자료형',
    control_flow: '제어문',
    functions: '함수',
    data_structures: '자료구조',
    object_oriented: '객체지향',
    file_handling: '파일 처리',
    error_handling: '예외 처리',
    modules: '모듈과 패키지'
  },
  data_analysis: {
    pandas_basics: 'Pandas 기초',
    pandas_advanced: 'Pandas 고급',
    numpy_operations: 'NumPy 연산',
    dataframe_manipulation: 'DataFrame 조작',
    data_visualization: '데이터 시각화',
    statistical_analysis: '통계 분석',
    data_cleaning: '데이터 전처리',
    time_series: '시계열 데이터',
    machine_learning_intro: '머신러닝 입문'
  },
  web_crawling: {
    requests_basics: 'Requests 기초',
    beautifulsoup: 'BeautifulSoup',
    selenium_basics: 'Selenium 기초',
    selenium_advanced: 'Selenium 고급',
    scrapy_framework: 'Scrapy 프레임워크',
    anti_detection: '탐지 회피 기법',
    data_extraction: '데이터 추출 패턴',
    browser_automation: '브라우저 자동화',
    api_integration: 'API 연동',
    crawling_ethics: '크롤링 윤리와 법적 고려사항'
  }
};

// 과목별 아이콘
export const SUBJECT_ICONS = {
  python_basics: '🐍',
  data_analysis: '📊',
  web_crawling: '🕷️'
};

// 과목별 색상 테마
export const SUBJECT_COLORS = {
  python_basics: {
    primary: '#3776ab',
    secondary: '#ffd43b',
    background: '#f8f9fa'
  },
  data_analysis: {
    primary: '#e97627',
    secondary: '#150458',
    background: '#f0f9ff'
  },
  web_crawling: {
    primary: '#00d2d3',
    secondary: '#ff6b6b',
    background: '#f0fdf4'
  }
};

// 난이도별 레벨 정의
export const DIFFICULTY_LEVELS = {
  1: '입문',
  2: '초급', 
  3: '중급',
  4: '고급',
  5: '전문가'
};

// 문제 유형 정의
export const QUESTION_TYPES = {
  multiple_choice: '객관식',
  short_answer: '단답형',
  code_completion: '코드 완성',
  code_execution: '코드 실행',
  debugging: '디버깅',
  theory: '이론'
};

// 과목별 기본 난이도 설정
export const SUBJECT_DEFAULT_DIFFICULTY = {
  python_basics: 2,
  data_analysis: 3,
  web_crawling: 3
};

// 과목별 설명
export const SUBJECT_DESCRIPTIONS = {
  python_basics: 'Python 프로그래밍의 기초부터 차근차근 배워보세요',
  data_analysis: 'Pandas, NumPy를 활용한 데이터 분석 및 시각화를 학습합니다',
  web_crawling: 'Requests, BeautifulSoup, Selenium을 활용한 웹 데이터 수집 기법을 익힙니다'
};

// 과목별 추천 학습 순서
export const RECOMMENDED_LEARNING_PATH = {
  python_basics: [
    'variables', 'control_flow', 'functions', 'data_structures',
    'object_oriented', 'file_handling', 'error_handling', 'modules'
  ],
  data_analysis: [
    'numpy_operations', 'pandas_basics', 'dataframe_manipulation',
    'data_cleaning', 'pandas_advanced', 'data_visualization',
    'statistical_analysis', 'time_series', 'machine_learning_intro'
  ],
  web_crawling: [
    'requests_basics', 'beautifulsoup', 'selenium_basics',
    'data_extraction', 'selenium_advanced', 'browser_automation',
    'scrapy_framework', 'anti_detection', 'api_integration', 'crawling_ethics'
  ]
};

// 토픽별 선수 학습 요구사항
export const TOPIC_PREREQUISITES = {
  data_analysis: {
    pandas_advanced: ['pandas_basics'],
    dataframe_manipulation: ['pandas_basics'],
    data_visualization: ['pandas_basics', 'numpy_operations'],
    statistical_analysis: ['pandas_basics', 'numpy_operations'],
    time_series: ['pandas_advanced', 'data_visualization'],
    machine_learning_intro: ['pandas_advanced', 'numpy_operations', 'statistical_analysis']
  },
  web_crawling: {
    beautifulsoup: ['requests_basics'],
    selenium_basics: ['requests_basics'],
    selenium_advanced: ['selenium_basics'],
    scrapy_framework: ['beautifulsoup', 'selenium_basics'],
    anti_detection: ['selenium_advanced'],
    browser_automation: ['selenium_advanced'],
    api_integration: ['requests_basics']
  }
};

// 유틸리티 함수들
export const getSubjectName = (subjectKey) => {
  return SUBJECTS[subjectKey] || subjectKey;
};

export const getTopicName = (subjectKey, topicKey) => {
  return SUBJECT_TOPICS[subjectKey]?.[topicKey] || topicKey;
};

export const getSubjectIcon = (subjectKey) => {
  return SUBJECT_ICONS[subjectKey] || '📚';
};

export const getSubjectColor = (subjectKey) => {
  return SUBJECT_COLORS[subjectKey] || SUBJECT_COLORS.python_basics;
};

export const getDifficultyLabel = (level) => {
  return DIFFICULTY_LEVELS[level] || `레벨 ${level}`;
};

export const getQuestionTypeLabel = (type) => {
  return QUESTION_TYPES[type] || type;
};
