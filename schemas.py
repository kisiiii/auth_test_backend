'''
リクエストボディに使うスキーマを定義するファイルです。
'''

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# ユーザー登録用
class UserCreate(BaseModel):
    company_user_name: str
    company_id: int
    password: str

# ユーザー認証用
class UserLogin(BaseModel):
    company_user_name: str
    password: str

# 案件情報登録用
class Project(BaseModel):
    company_user_id: int
    project_title: str
    consultation_category: str
    project_content: str
    industry: str #業種情報。最終的には担当者が束なった企業の登録時に入力されていることを想定するので、将来的にはなくなる方向
    business_description: str #事業内容。最終的には担当者が束なった企業の登録時に入力されていることを想定するので、将来的にはなくなる方向
    university: Optional[List[str]] = None # 複数の大学名に対応
    research_field: str
    preferred_researcher_level: Optional[List[str]] = None # 複数の職位に対応
    application_deadline: date

# オファー用
class Offers(BaseModel):
    project_id: int
    researcher_ids: List[int]