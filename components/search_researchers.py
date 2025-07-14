import os
import pandas as pd
import openai
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, HnswParameters, VectorSearchProfile
)
import requests
import json

# ローカルで動かす時用
# from dotenv import load_dotenv

# load_dotenv()


# 環境変数からAzureのAPIキーを取得
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_GPT_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_GPT_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

# OpenAI API クライアント設定
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-07-01-preview"

# Azure AI Search クライアント設定
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

# 埋め込みを取得する関数
def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
    )
    return response.data[0].embedding

# 依頼に基づく研究者検索
def search_researchers(category, title, description, industry, business_description, university, top_k=10):
    try:
        query_text = f"{category} {title} {description}"
        embedding = get_embedding(query_text)
        
        results = search_client.search(
            search_text=None,
            vector_queries=[
                VectorizedQuery(
                    vector=embedding,
                    k_nearest_neighbors=top_k * 3,
                    fields="vector"
                )
            ],
            select=["id", "researcher_id", "researcher_affiliation_current", "researcher_position_current", "research_field_pi", "keywords_pi", "research_project_title"],
            filter=f"researcher_affiliation_current eq '{university}'"
        )

        # 検索結果における研究者の重複削除用
        seen_researchers = set()
        search_results = []
        
        for result in results:
            researcher_id = result.get("researcher_id")
            # 既に検索結果に含まれている研究者はスキップ
            if researcher_id not in seen_researchers:
                explanation = generate_explanation(query_text, result)
                search_results.append({
                    "id": result["id"],
                    "researcher_id": researcher_id,
                    "researcher_affiliation_current": result["researcher_affiliation_current"],
                    "researcher_position_current": result["researcher_position_current"],
                    "research_field_pi": result["research_field_pi"],
                    "keywords_pi": result["keywords_pi"],
                    "research_project_title": result["research_project_title"],
                    "explanation": explanation
                })
                seen_researchers.add(researcher_id)
                # top_k件まで結果を出したら終了する
                if len(search_results) >= top_k:
                    break
        
        return search_results
    
    except Exception as e:
        print("search_researchers内で例外発生:", e)
        raise

def get_openai_response(messages):
    """
    Azure OpenAI Serviceにチャットメッセージを送信し、応答を取得する関数。

    Parameters:
    messages (list): チャットメッセージのリスト。各メッセージは辞書で、'role'と'content'を含む。

    Returns:
    str: アシスタントからの応答メッセージ。
    """
    # 環境変数からAPIキーとエンドポイントを取得
    api_key = os.getenv("AZURE_OPENAI_GPT_API_KEY")
    api_base = os.getenv("AZURE_OPENAI_GPT_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")  # デプロイメント名を環境変数から取得

    # エンドポイントURLの構築
    api_version = "2024-08-01-preview"  # 使用するAPIバージョンを指定
    endpoint = f"{api_base}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

    # ヘッダーの設定
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # リクエストデータの作成
    data = {
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 300
    }

    # POSTリクエストの送信
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))

    # レスポンスの処理
    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


# 研究者のマッチ理由を生成
def generate_explanation(query_text, researcher):
    prompt = f"""
    依頼内容: {query_text}
    大学: {researcher["researcher_affiliation_current"]}
    役職: {researcher["researcher_position_current"]}
    研究分野： {researcher["research_field_pi"]}
    キーワード： {researcher["keywords_pi"]}
    研究課題課題： {researcher["research_project_title"]}

    なぜこの研究者が依頼内容に適しているのかを簡潔に説明してください。
    """
    messages=[{"role": "system", "content": "あなたは検索結果の解説を行うアシスタントです。"},
            {"role": "user", "content": prompt}]

    return get_openai_response(messages)

# 動作検証用
# 検索実行
# input1 = "研究のアドバイス"
# input2 = "建築構造一貫計算ソフトウェアに対する生成系AI機能を応用した操作性向上の研究"
# input3 = "建築構造一貫計算ソフトウェアという専門ソフトウェアは操作性が難しく、初学者の習得ハードルを高める要因になっている。そこでUI/UX改善の手段として生成系AIをどのように活用できるか、専門者の知見を仮りたい。またアドバイスの方向性によっては今後の共同研究の方向性も探りたい。"
# input1 = "コンサルティング・共同研究の相談"
# input2 = "社会科教育における授業づくりを支援するアプリの開発"
# input3 = "社会参加できる市民を育てるための授業作りを支援するアプリを開発するために、専門者の知見をかりたい。またアドバイスの方向性によっては今後の共同研究の方向性も探りたい。"
# input1 = "アドバイス・業務改善の相談"
# input2 = "小学校における授業づくりに関する相談"
# input3 = "現在行っている授業の内容を分析してよりよい授業づくりを行うために、専門者の知見をかりたい。またアドバイスの方向性によっては今後のコラボレーションについても検討したい。"


# results = search_researchers(category=input1, title=input2, description=input3, industry="", business_description="", university="", top_k=3)

# for res in results:
#     # print(f"研究者: {res['name']}")
#     # print(f"研究分野: {res['research_field']}")
#     print(f"マッチ理由: {res['explanation']}")
#     print("------")