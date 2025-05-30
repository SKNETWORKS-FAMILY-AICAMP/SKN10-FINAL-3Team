import os
from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig, chain
import json
from tqdm.auto import tqdm

load_dotenv()

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

prompt = ChatPromptTemplate(
  [
    ("system", """
      당신은 단어를 법률에서 사용하는 뜻으로 알려주는 어시스턴트입니다.
      당신이 알려주는 단어는 법률 모델 파인튜닝에 사용될 단어입니다.

      대답은 한국어로 해주세요.
      대답은 아래 예시와 같이 json 형식으로 출력해주세요.
      {{
        "title": "{title}",
        "definition": "..."
      }}
      """),
    ("human", "{user_input}"),
    ("placeholder", "{messages}"),
  ]
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

tool = TavilySearchResults(
    max_results=5,
    include_answer=True,
    include_raw_content=True,
    search_depth="advanced",
    include_domains=[
      "ko.wikipedia.org/wiki/",
      "naver.com",
      "google.com",
      "sldongbu.scourt.go.kr/word/new/WordList.work"
      ]
)

llm_with_tools = llm.bind_tools([tool])

llm_chain = prompt | llm_with_tools

@chain
def tool_chain(user_input: str, config: RunnableConfig):
  input_ = {
    "user_input": f"{user_input}에 대해 알려줘.",
    "title": user_input
  }
  ai_msg = llm_chain.invoke(input_, config=config)
  tool_msgs = tool.batch(ai_msg.tool_calls, config=config)
  return llm_chain.invoke({**input_, "messages": [ai_msg, *tool_msgs]}, config=config)

# 법률 용어 파일 읽기
with open('data/law_word/filtered_nn_word.txt', 'r', encoding='utf-8') as f:
    law_words = [line.strip() for line in f.readlines()]

# 결과를 저장할 딕셔너리
results = {}

# 각 법률 용어에 대해 처리
for word in tqdm(law_words, leave=True):
    try:
        result = tool_chain.invoke(word)
        print(result.content)
        result_dict = json.loads(result.content)
        results[word] = result_dict
        print(f"처리 완료: {word}")
    except Exception as e:
        print(f"오류 발생 ({word}): {str(e)}")

# 결과를 JSON 파일로 저장
with open('data/law_word/law_definitions.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("모든 처리가 완료되었습니다.")