import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

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
    saved_presearch_df = pd.read_csv(os.path.join(DATA_PATH, "precsearch_df.csv"))
    new_presearch_df = page_presearch(1, 10)
    for row in new_presearch_df.iterrows():
      if row["사건명"] not in saved_presearch_df["사건명"].values:
        saved_presearch_df = pd.concat([row, saved_presearch_df])
    saved_presearch_df.reset_index(drop=True, inplace=True)
    saved_presearch_df.to_csv(os.path.join(DATA_PATH, "precsearch_df.csv"), index=False)

  else:
    precsearch_df = pd.DataFrame()
    for page in range(1, 100):
      precsearch_df = pd.concat([precsearch_df, page_presearch(page)])
      precsearch_df = precsearch_df[precsearch_df["사건명"].str.contains("손해배상\(자\)")]
      precsearch_df.reset_index(drop=True, inplace=True)
      precsearch_df.to_csv(os.path.join(DATA_PATH, "precsearch_df.csv"), index=False)

def page_precservice(ID):
  precservice_url = "/DRF/lawService.do?"

  params = {
    "OC": OC,
    "target": "prec",
    "type": "json",
    "ID": ID
  }

  response = requests.get(LAW_URL + precservice_url, params=params)
  data = response.json()

  return data['PrecService']

if __name__ == "__main__":
  OC = os.getenv('OC')
  LAW_URL = "https://www.law.go.kr/"
  DATA_PATH = "../data/law"
  os.makedirs(DATA_PATH, exist_ok=True)

  page_presearch_logic()
  page_precservice()

