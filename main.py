from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB操作用のモジュールインポート
from database.connection import get_db

# ルータのインポート
#from routers import project_registration, matching_results, researcher_information, offer, ai_diagnosis, projects_list, delete_project,test,auth
from routers import auth

# インスタンス化
app = FastAPI(
    title="KenQSenQ",
    description="研Qアプリ(事業会社側)のAPIです.",
    version="0.0.0"
)

# ルータ登録
'''
app.include_router(test.router) #テスト用
app.include_router(project_registration.router) #プロジェクト登録(PJ登録～ベクトルサーチ結果登録)
app.include_router(matching_results.router) #マッチング結果の抽出する(DBから)
app.include_router(researcher_information.router) #研究者詳細情報の取得する
app.include_router(offer.router) #オファーしてマッチングステータスを変更する
app.include_router(ai_diagnosis.router) #AI課題診断用
app.include_router(projects_list.router)
app.include_router(delete_project.router) #プロジェクト削除用
'''
app.include_router(auth.router) #ユーザー認証、登録用

# CORS設定.開発中はとりあえず全てのメソッド、ヘッダーを許可.オリジンはローカル/本番を併記
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app-advanced3-3-fferh5cydyawckfe.canadacentral-01.azurewebsites.net","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)