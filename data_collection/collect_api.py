import os
import requests
import json
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv

# open.law.go.kr 아이디 정보 가져오기
load_dotenv()
OC = os.getenv('OC')
LAW_URL = "https://www.law.go.kr/"
DATA_PATH = "./data/law"
if not os.path.exists(DATA_PATH):
  os.makedirs(DATA_PATH, exist_ok=True)

def page_presearch(page, display = 100):
  precsearch_url = "/DRF/lawSearch.do?"

  params = {
    "OC": OC,
    "target": "prec",
    "type": "json",
    "display" : display,
    "JO": "민법",
    "page": page
  }

  response = requests.get(LAW_URL + precsearch_url, params=params)
  data = response.json()
  df = pd.DataFrame(data["PrecSearch"]['prec']).iloc[:, 1:]
  return df

def page_presearch_logic():
  if os.path.exists(os.path.join(DATA_PATH, "precsearch_df.csv")):
    precsearch_df = pd.read_csv(os.path.join(DATA_PATH, "precsearch_df.csv"))
    new_presearch_df = page_presearch(1, 10)
    for index, row in tqdm(new_presearch_df.iterrows(), total=len(new_presearch_df)):
      if row["사건명"] not in precsearch_df["사건명"].values:
        precsearch_df = pd.concat([precsearch_df, pd.DataFrame([row])])
    precsearch_df.reset_index(drop=True, inplace=True)
    precsearch_df.to_csv(os.path.join(DATA_PATH, "precsearch_df.csv"), index=False)
  else:
    precsearch_df = pd.DataFrame()
    for page in range(1, 100):
      precsearch_df = pd.concat([precsearch_df, page_presearch(page)])
      precsearch_df = precsearch_df[precsearch_df["사건명"].str.contains("손해배상\(자\)")]
      precsearch_df.reset_index(drop=True, inplace=True)
      precsearch_df.to_csv(os.path.join(DATA_PATH, "precsearch_df.csv"), index=False)

  return precsearch_df

def page_precservice(ID):
  precservice_url = "/DRF/lawService.do?"

  params = {
    "OC": OC,
    "target": "prec",
    "type": "json",
    "ID": ID
  }

  response = requests.get(LAW_URL + precservice_url, params=params)
  print(response.text)
  data = response.json()

  return data['PrecService']

if __name__ == "__main__":
  df = page_presearch_logic()
  for index, row in tqdm(df.iterrows(), total=len(df)):
    data = page_precservice(row["사건번호"])
    with open(os.path.join(DATA_PATH, f"{row['사건번호']}.json"), "w") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)