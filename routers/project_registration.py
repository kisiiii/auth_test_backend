'''
案件情報を登録し、ベクトルサーチによるマッチングを行った結果を返すエンドポイントです。
'''

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import ProjectInformation, MatchingInformation

# スキーマのインポート
from schemas import Project

# ベクトル検索用のモジュールインポート
from components.search_researchers import search_researchers
from components.search_researchers_temp import search_researchers_temp

router = APIRouter(prefix="/project-registration", tags=["project-registration"])

# 開発用。大学のID紐づけ
# university_list = {
#     "1101": "東京大学",
#     "1022": "筑波大学",
#     "2011": "東京科学大学"
# }

'''
事業者の課題登録
'''
@router.post("")
def add_project(
    project_info: Project,
    db: Session = Depends(get_db)
    ):
    try:
        # 日本時間(UTS+9)
        JST = timezone(timedelta(hours=9))
        now_jst = datetime.now(JST)
        # print("受け取ったデータ:", project_info)
        # Step1: クエリ用のテキストを抽出（Projectモデルから）
        company_user_id = project_info.company_user_id
        category = project_info.consultation_category
        title = project_info.project_title
        description = project_info.project_content
        industry = project_info.industry #業種情報
        business_description = project_info.business_description #事業内容
        university = project_info.university # university_list[project_info.university] #大学フィルタリング用
        field = project_info.research_field
        level = project_info.preferred_researcher_level
        deadline = project_info.application_deadline

        task = "ここに深堀した課題を入れる"

        # Step 2: DBに新しいプロジェクトを登録
        level_str = ",".join(level)
        university_str = ",".join(university)
        new_project = ProjectInformation(
            company_user_id=company_user_id,
            consultation_category=category,
            project_title=title,
            project_content=description,
            research_field=field,
            preferred_researcher_level=level_str,
            application_deadline=deadline,
            industry_temp = industry,
            business_temp = business_description,
            university_temp = university_str,
            detailed_task = task,
            registration_date = now_jst
        )
        # print("プロジェクト登録前")
        db.add(new_project)
        db.commit()
        db.refresh(new_project)  # 登録後のIDなどを取得
        # print("プロジェクト登録完了")

        # Step 3: ベクトル検索実行（top_k件の研究者を取得）
        search_results = search_researchers_temp(
                category=category,
                title=title,
                description=description,
                industry=industry,
                business_description=business_description,
                preferred_researcher_level=level,
                university=university,
                top_k=10
            )
        # if university[0] == "0": # 多数データを登録したキーワードベクトル化のリソースでの検索
        #     search_results = search_researchers_temp(
        #         category=category,
        #         title=title,
        #         description=description,
        #         industry=industry,
        #         business_description=business_description,
        #         preferred_researcher_level=level,
        #         university=university[1:],
        #         top_k=10
        #     )
        # else:
        #     search_results = search_researchers(
        #         category=category,
        #         title=title,
        #         description=description,
        #         industry=industry,
        #         business_description=business_description,
        #         university=university,
        #         top_k=10
        #     )

        # Step 4: マッチング結果をDBに登録
        for researcher in search_results:
            matching = MatchingInformation(
                project_id=new_project.project_id,
                researcher_id=researcher["researcher_id"],
                matching_reason=researcher["explanation"],
                matching_status=0,  # 初期値: 未対応 or 要検討
                matched_date=now_jst
            )
            db.add(matching)

        db.commit()  # まとめてコミット

        # Step 5: 結果を返す
        return {
            "project_id": new_project.project_id,
            # "project_title": title,
            # "matched_researchers": search_results
        }
        # return {"project_id": 1}

    except Exception as e:
        db.rollback()
        # print("例外発生！:", e)
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")