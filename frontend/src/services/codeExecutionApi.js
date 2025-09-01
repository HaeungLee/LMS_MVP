/**
 * Code Execution API Service
 * 코드 실행 관련 API 호출 서비스
 */

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') + '/api/v1';

// 샘플 문제 데이터
export const getSampleProblems = () => [
  {
    id: 1,
    title: "두 수의 합",
    description: "두 개의 정수를 입력받아 합을 출력하는 프로그램을 작성하세요.",
    category: "Python 기초",
    difficulty: "easy",
    acceptance_rate: 85,
    solved: true,
    starter_code: "# 두 개의 정수를 입력받아 합을 출력하세요\na = int(input())\nb = int(input())\n\n# 여기에 코드를 작성하세요\n",
    test_cases: [
      { input: "3\n5", expected_output: "8" },
      { input: "10\n20", expected_output: "30" }
    ]
  },
  {
    id: 2,
    title: "리스트 최댓값 찾기",
    description: "주어진 리스트에서 최댓값을 찾는 함수를 작성하세요.",
    category: "Python 기초",
    difficulty: "easy",
    acceptance_rate: 78,
    solved: false,
    starter_code: "def find_max(numbers):\n    # 여기에 코드를 작성하세요\n    pass\n\n# 테스트\nresult = find_max([1, 5, 3, 9, 2])\nprint(result)\n",
    test_cases: [
      { input: "[1, 5, 3, 9, 2]", expected_output: "9" },
      { input: "[10, 3, 8, 1]", expected_output: "10" }
    ]
  },
  {
    id: 3,
    title: "문자열 뒤집기",
    description: "입력받은 문자열을 뒤집어서 출력하는 프로그램을 작성하세요.",
    category: "알고리즘",
    difficulty: "medium",
    acceptance_rate: 65,
    solved: false,
    starter_code: "def reverse_string(s):\n    # 여기에 코드를 작성하세요\n    pass\n\n# 테스트\ntext = input()\nresult = reverse_string(text)\nprint(result)\n",
    test_cases: [
      { input: "hello", expected_output: "olleh" },
      { input: "python", expected_output: "nohtyp" }
    ]
  },
  {
    id: 4,
    title: "피보나치 수열",
    description: "n번째 피보나치 수를 계산하는 함수를 작성하세요.",
    category: "알고리즘",
    difficulty: "medium",
    acceptance_rate: 55,
    solved: false,
    starter_code: "def fibonacci(n):\n    # 여기에 코드를 작성하세요\n    pass\n\nn = int(input())\nresult = fibonacci(n)\nprint(result)\n",
    test_cases: [
      { input: "5", expected_output: "5" },
      { input: "8", expected_output: "21" }
    ]
  },
  {
    id: 5,
    title: "데이터 분석 - 평균 계산",
    description: "CSV 형태의 데이터에서 특정 열의 평균을 계산하세요.",
    category: "데이터 분석",
    difficulty: "hard",
    acceptance_rate: 42,
    solved: false,
    starter_code: "import csv\nimport io\n\ndef calculate_average(csv_data, column_name):\n    # 여기에 코드를 작성하세요\n    pass\n\n# 테스트 데이터\ntest_data = \"name,age,score\\nAlice,25,85\\nBob,30,92\\nCharlie,35,78\"\nresult = calculate_average(test_data, 'score')\nprint(result)\n",
    test_cases: [
      { input: "score", expected_output: "85.0" },
      { input: "age", expected_output: "30.0" }
    ]
  }
];

/**
 * 코드 실행 API
 */
export const executeCode = async (code, language = 'python', userInput = '', testCases = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/code/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        language,
        user_input: userInput,
        test_cases: testCases
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Code execution failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Code execution error:', error);
    throw error;
  }
};

/**
 * 문제 정보 조회 API
 */
export const getProblem = async (problemId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/code/problems/${problemId}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch problem');
    }

    return await response.json();
  } catch (error) {
    console.error('Get problem error:', error);
    throw error;
  }
};

/**
 * 문제 목록 조회 API
 */
export const getProblems = async (filters = {}) => {
  try {
    const queryParams = new URLSearchParams();
    
    if (filters.category) queryParams.append('category', filters.category);
    if (filters.difficulty) queryParams.append('difficulty', filters.difficulty);
    if (filters.limit) queryParams.append('limit', filters.limit);
    if (filters.offset) queryParams.append('offset', filters.offset);

    const response = await fetch(`${API_BASE_URL}/code/problems?${queryParams}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch problems');
    }

    return await response.json();
  } catch (error) {
    console.error('Get problems error:', error);
    throw error;
  }
};

/**
 * 코드 제출 API
 */
export const submitCode = async (problemId, code, language = 'python') => {
  try {
    const response = await fetch(`${API_BASE_URL}/code/problems/${problemId}/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        language
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Code submission failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Code submission error:', error);
    throw error;
  }
};

/**
 * 지원되는 언어 목록 조회 API
 */
export const getSupportedLanguages = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/code/languages`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch supported languages');
    }

    return await response.json();
  } catch (error) {
    console.error('Get supported languages error:', error);
    throw error;
  }
};
