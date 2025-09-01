"""
새로운 과목 (데이터 분석, 웹 크롤링)을 위한 문제 생성기
"""
import random
from typing import Dict, List, Any

def generate_data_analysis_questions() -> List[Dict[str, Any]]:
    """데이터 분석 과목 문제 생성"""
    questions = []
    
    # Pandas 기초 문제들
    pandas_basic_questions = [
        {
            "id": 2001,  # 2000번대: 데이터 분석
            "subject": "data_analysis",
            "topic": "pandas_basics",
            "question_type": "code_completion",
            "difficulty": 2,
            "code_snippet": "import pandas as pd\n\ndf = pd.DataFrame({\n    'name': ['Alice', 'Bob', 'Charlie'],\n    'age': [25, 30, 35]\n})\n\n# 여기에 코드를 작성하세요\naverage_age = ____",
            "correct_answer": "df['age'].mean()",
            "question_data": {
                "type": "code_completion",
                "question": "다음 DataFrame에서 'age' 컬럼의 평균값을 구하세요.",
                "code_template": "import pandas as pd\n\ndf = pd.DataFrame({\n    'name': ['Alice', 'Bob', 'Charlie'],\n    'age': [25, 30, 35]\n})\n\n# 여기에 코드를 작성하세요\naverage_age = ____",
                "correct_answer": "df['age'].mean()",
                "explanation": "DataFrame에서 특정 컬럼의 평균값은 df['컬럼명'].mean() 으로 구할 수 있습니다."
            },
            "metadata": {
                "learning_objectives": ["pandas DataFrame 기초", "컬럼 선택", "통계 함수"],
                "hints": ["DataFrame에서 컬럼을 선택하는 방법", "mean() 함수 사용법"],
                "tags": ["pandas", "statistics", "dataframe"]
            }
        },
        {
            "id": 2002, 
            "subject": "data_analysis",
            "topic": "pandas_basics",
            "question_type": "multiple_choice",
            "difficulty": 1,
            "code_snippet": "pandas에서 CSV 파일을 읽어오는 함수는?",
            "correct_answer": "A",
            "question_data": {
                "type": "multiple_choice",
                "question": "pandas에서 CSV 파일을 읽어오는 함수는?",
                "options": [
                    {"id": "A", "text": "pd.read_csv()"},
                    {"id": "B", "text": "pd.load_csv()"},
                    {"id": "C", "text": "pd.import_csv()"},
                    {"id": "D", "text": "pd.open_csv()"}
                ],
                "correct_answer": "A",
                "explanation": "pandas에서는 pd.read_csv() 함수를 사용하여 CSV 파일을 DataFrame으로 읽어올 수 있습니다."
            },
            "metadata": {
                "learning_objectives": ["pandas 파일 입출력", "CSV 파일 처리"],
                "hints": ["pandas의 파일 읽기 함수들"],
                "tags": ["pandas", "csv", "file-io"]
            }
        },
        {
            "id": 2003,
            "subject": "data_analysis", 
            "topic": "dataframe_manipulation",
            "question_type": "code_execution",
            "difficulty": 3,
            "code_snippet": "import pandas as pd\n\ndf = pd.DataFrame({\n    'name': ['Alice', 'Bob', 'Charlie', 'David'],\n    'age': [25, 35, 28, 32]\n})\n\n# 여기에 코드를 작성하세요\nfiltered_df = ____\n\nprint(filtered_df)",
            "correct_answer": "df[df['age'] >= 30]",
            "question_data": {
                "type": "code_execution",
                "question": "주어진 DataFrame에서 age가 30 이상인 행들만 필터링하세요.",
                "code_template": "import pandas as pd\n\ndf = pd.DataFrame({\n    'name': ['Alice', 'Bob', 'Charlie', 'David'],\n    'age': [25, 35, 28, 32]\n})\n\n# 여기에 코드를 작성하세요\nfiltered_df = ____\n\nprint(filtered_df)",
                "correct_answer": "df[df['age'] >= 30]",
                "expected_output": "    name  age\n1    Bob   35\n3  David   32"
            },
            "metadata": {
                "learning_objectives": ["DataFrame 필터링", "조건부 선택"],
                "hints": ["불린 인덱싱 사용", "비교 연산자 활용"],
                "tags": ["pandas", "filtering", "boolean-indexing"]
            }
        }
    ]
    
    # NumPy 문제들
    numpy_questions = [
        {
            "id": 2004,
            "subject": "data_analysis",
            "topic": "numpy_operations", 
            "question_type": "multiple_choice",
            "difficulty": 2,
            "code_snippet": "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nresult = np.sum(arr * 2)",
            "correct_answer": "B",
            "question_data": {
                "type": "multiple_choice",
                "question": "다음 NumPy 배열 연산의 결과는?",
                "code_snippet": "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nresult = np.sum(arr * 2)",
                "options": [
                    {"id": "A", "text": "15"},
                    {"id": "B", "text": "30"}, 
                    {"id": "C", "text": "25"},
                    {"id": "D", "text": "10"}
                ],
                "correct_answer": "B",
                "explanation": "배열의 각 원소에 2를 곱한 후 합계: (2+4+6+8+10) = 30"
            },
            "metadata": {
                "learning_objectives": ["NumPy 배열 연산", "브로드캐스팅"],
                "hints": ["벡터화 연산", "np.sum() 함수"],
                "tags": ["numpy", "array-operations", "vectorization"]
            }
        },
        {
            "id": 2005,
            "subject": "data_analysis",
            "topic": "numpy_operations",
            "question_type": "code_completion", 
            "difficulty": 2,
            "code_snippet": "import numpy as np\n\n# 여기에 코드를 작성하세요\nzero_matrix = ____",
            "correct_answer": "np.zeros((3, 3))",
            "question_data": {
                "type": "code_completion",
                "question": "3x3 크기의 영행렬(0으로 채워진 배열)을 생성하세요.",
                "code_template": "import numpy as np\n\n# 여기에 코드를 작성하세요\nzero_matrix = ____",
                "correct_answer": "np.zeros((3, 3))",
                "explanation": "np.zeros() 함수에 튜플 형태로 차원을 전달하면 해당 크기의 영행렬이 생성됩니다."
            },
            "metadata": {
                "learning_objectives": ["NumPy 배열 생성", "행렬 초기화"],
                "hints": ["np.zeros() 함수", "튜플로 크기 지정"],
                "tags": ["numpy", "array-creation", "matrix"]
            }
        }
    ]
    
    # 데이터 시각화 문제들
    visualization_questions = [
        {
            "id": 2006,
            "subject": "data_analysis",
            "topic": "data_visualization",
            "question_type": "code_completion",
            "difficulty": 3,
            "code_snippet": "import matplotlib.pyplot as plt\n\ndata = [1, 2, 2, 3, 3, 3, 4, 4, 5]\n\n# 여기에 코드를 작성하세요\nplt.____\nplt.show()",
            "correct_answer": "hist(data)",
            "question_data": {
                "type": "code_completion", 
                "question": "matplotlib을 사용하여 리스트 data의 히스토그램을 그리세요.",
                "code_template": "import matplotlib.pyplot as plt\n\ndata = [1, 2, 2, 3, 3, 3, 4, 4, 5]\n\n# 여기에 코드를 작성하세요\nplt.____\nplt.show()",
                "correct_answer": "hist(data)",
                "explanation": "plt.hist() 함수를 사용하여 데이터의 히스토그램을 그릴 수 있습니다."
            },
            "metadata": {
                "learning_objectives": ["matplotlib 기초", "히스토그램 생성"],
                "hints": ["plt.hist() 함수", "데이터 분포 시각화"],
                "tags": ["matplotlib", "visualization", "histogram"]
            }
        }
    ]
    
    questions.extend(pandas_basic_questions)
    questions.extend(numpy_questions)
    questions.extend(visualization_questions)
    
    return questions

def generate_web_crawling_questions() -> List[Dict[str, Any]]:
    """웹 크롤링 과목 문제 생성"""
    questions = []
    
    # Requests 기초 문제들
    requests_questions = [
        {
            "id": 3001,  # 3000번대: 웹 크롤링
            "subject": "web_crawling",
            "topic": "requests_basics",
            "question_type": "code_completion",
            "difficulty": 2,
            "code_snippet": "import requests\n\n# 여기에 코드를 작성하세요\nresponse = ____\nprint(response.status_code)",
            "correct_answer": "requests.get('https://httpbin.org/get')",
            "question_data": {
                "type": "code_completion",
                "question": "requests 라이브러리를 사용하여 'https://httpbin.org/get'에 GET 요청을 보내세요.",
                "code_template": "import requests\n\n# 여기에 코드를 작성하세요\nresponse = ____\nprint(response.status_code)",
                "correct_answer": "requests.get('https://httpbin.org/get')",
                "explanation": "requests.get() 함수에 URL을 전달하여 GET 요청을 보낼 수 있습니다."
            },
            "metadata": {
                "learning_objectives": ["HTTP GET 요청", "requests 라이브러리 기초"],
                "hints": ["requests.get() 함수", "URL 문자열 전달"],
                "tags": ["requests", "http", "api"]
            }
        },
        {
            "id": 3002,
            "subject": "web_crawling",
            "topic": "requests_basics",
            "question_type": "multiple_choice",
            "difficulty": 1,
            "code_snippet": "HTTP 요청이 성공했을 때 반환되는 상태 코드는?",
            "correct_answer": "A",
            "question_data": {
                "type": "multiple_choice",
                "question": "HTTP 요청이 성공했을 때 반환되는 상태 코드는?",
                "options": [
                    {"id": "A", "text": "200"},
                    {"id": "B", "text": "404"}, 
                    {"id": "C", "text": "500"},
                    {"id": "D", "text": "301"}
                ],
                "correct_answer": "A",
                "explanation": "HTTP 상태 코드 200은 요청이 성공적으로 처리되었음을 의미합니다."
            },
            "metadata": {
                "learning_objectives": ["HTTP 상태 코드", "웹 요청 기초"],
                "hints": ["HTTP 상태 코드의 의미"],
                "tags": ["http", "status-codes", "web"]
            }
        }
    ]
    
    # BeautifulSoup 문제들
    bs_questions = [
        {
            "id": 3003,
            "subject": "web_crawling",
            "topic": "beautifulsoup",
            "question_type": "code_execution",
            "difficulty": 3,
            "code_snippet": "from bs4 import BeautifulSoup\n\nhtml = '''<html><body>\n<a href='http://example.com'>Link1</a>\n<a href='http://test.com'>Link2</a>\n</body></html>'''\n\n# 여기에 코드를 작성하세요\nsoup = BeautifulSoup(html, 'html.parser')\nlinks = ____\n\nprint(links)",
            "correct_answer": "[a['href'] for a in soup.find_all('a')]",
            "question_data": {
                "type": "code_execution",
                "description": "주어진 HTML에서 모든 링크의 href 속성을 추출하세요.",
                "code_template": "from bs4 import BeautifulSoup\n\nhtml = '''<html><body>\n<a href='http://example.com'>Link1</a>\n<a href='http://test.com'>Link2</a>\n</body></html>'''\n\n# 여기에 코드를 작성하세요\nsoup = BeautifulSoup(html, 'html.parser')\nlinks = ____\n\nprint(links)",
                "correct_answer": "[a['href'] for a in soup.find_all('a')]",
                "expected_output": "['http://example.com', 'http://test.com']"
            },
            "metadata": {
                "learning_objectives": ["HTML 파싱", "속성 추출", "리스트 컴프리헨션"],
                "hints": ["find_all() 메서드", "속성 접근 방법"],
                "tags": ["beautifulsoup", "html-parsing", "web-scraping"]
            }
        },
        {
            "id": 3004,
            "subject": "web_crawling", 
            "topic": "beautifulsoup",
            "question_type": "code_completion",
            "difficulty": 2,
            "code_snippet": "from bs4 import BeautifulSoup\n\nhtml = '<html><body><h1>Welcome</h1><h1>Hello</h1></body></html>'\nsoup = BeautifulSoup(html, 'html.parser')\n\n# 여기에 코드를 작성하세요\nfirst_h1_text = ____",
            "correct_answer": "soup.find('h1').text",
            "question_data": {
                "type": "code_completion",
                "question": "BeautifulSoup으로 파싱된 HTML에서 첫 번째 h1 태그의 텍스트를 추출하세요.",
                "code_template": "from bs4 import BeautifulSoup\n\nhtml = '<html><body><h1>Welcome</h1><h1>Hello</h1></body></html>'\nsoup = BeautifulSoup(html, 'html.parser')\n\n# 여기에 코드를 작성하세요\nfirst_h1_text = ____",
                "correct_answer": "soup.find('h1').text",
                "explanation": "find() 메서드는 첫 번째로 찾은 태그를 반환하고, .text로 텍스트 내용을 가져올 수 있습니다."
            },
            "metadata": {
                "learning_objectives": ["태그 검색", "텍스트 추출"],
                "hints": ["find() vs find_all()", ".text 속성"],
                "tags": ["beautifulsoup", "text-extraction", "html"]
            }
        }
    ]
    
    # Selenium 기초 문제들
    selenium_questions = [
        {
            "id": 3005,
            "subject": "web_crawling",
            "topic": "selenium_basics", 
            "question_type": "short_answer",
            "difficulty": 2,
            "code_snippet": "Selenium에서 Chrome 브라우저를 자동화하기 위해 필요한 드라이버는?",
            "correct_answer": "ChromeDriver",
            "question_data": {
                "type": "short_answer",
                "question": "Selenium에서 Chrome 브라우저를 자동화하기 위해 필요한 드라이버는?",
                "correct_answer": "ChromeDriver",
                "alternatives": ["chromedriver", "Chrome Driver"],
                "explanation": "Chrome 브라우저 자동화를 위해서는 ChromeDriver가 필요합니다."
            },
            "metadata": {
                "learning_objectives": ["Selenium 드라이버", "브라우저 자동화"],
                "hints": ["각 브라우저별 전용 드라이버"],
                "tags": ["selenium", "webdriver", "browser-automation"]
            }
        },
        {
            "id": 3006,
            "subject": "web_crawling",
            "topic": "selenium_basics",
            "question_type": "code_completion",
            "difficulty": 3,
            "code_snippet": "from selenium import webdriver\nfrom selenium.webdriver.common.by import By\n\ndriver = webdriver.Chrome()\ndriver.get('http://example.com')\n\n# 여기에 코드를 작성하세요\nbutton = ____\nbutton.click()",
            "correct_answer": "driver.find_element(By.ID, 'submit-btn')",
            "question_data": {
                "type": "code_completion",
                "question": "Selenium으로 웹페이지에서 id가 'submit-btn'인 버튼을 찾아 클릭하세요.",
                "code_template": "from selenium import webdriver\nfrom selenium.webdriver.common.by import By\n\ndriver = webdriver.Chrome()\ndriver.get('http://example.com')\n\n# 여기에 코드를 작성하세요\nbutton = ____\nbutton.click()",
                "correct_answer": "driver.find_element(By.ID, 'submit-btn')",
                "explanation": "find_element() 메서드에 By.ID와 id 값을 전달하여 요소를 찾을 수 있습니다."
            },
            "metadata": {
                "learning_objectives": ["요소 검색", "클릭 이벤트", "By 클래스"],
                "hints": ["find_element() 메서드", "By.ID 사용법"],
                "tags": ["selenium", "element-finding", "click-event"]
            }
        }
    ]
    
    questions.extend(requests_questions)
    questions.extend(bs_questions)
    questions.extend(selenium_questions)
    
    return questions

def get_all_new_subject_questions() -> List[Dict[str, Any]]:
    """모든 새로운 과목의 문제들을 반환"""
    all_questions = []
    all_questions.extend(generate_data_analysis_questions())
    all_questions.extend(generate_web_crawling_questions())
    return all_questions
