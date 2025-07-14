'''
事業者ユーザIDを元に紐づく案件リストを返す。
トップページの読み込み時の使用を想定
*フロントでIDを元にproject情報詳細を取りに行くようにしているが、このエンドポイントで一緒に渡した方が処理が早くてよいかも。。。
'''
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# スキーマのインポート

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import MatchingInformation, ResearcherInformation, ProjectInformation

router = APIRouter(prefix="/projects-list", tags=["projects-list"])

'''
'''
@router.get("")
def projects_list(
    company_user_id: int,
    db: Session = Depends(get_db)
    ):

    # 事業者ユーザIDに紐づくプロジェクト情報とマッチング情報を取得
    results = (
        db.query(
            ProjectInformation.project_id,
            ProjectInformation.project_title,
            ProjectInformation.registration_date,
            ProjectInformation.application_deadline,
            ProjectInformation.project_status,
            MatchingInformation.researcher_id,
            MatchingInformation.matching_status,
            ResearcherInformation.researcher_name
        )
        .outerjoin(MatchingInformation, ProjectInformation.project_id == MatchingInformation.project_id)
        .outerjoin(ResearcherInformation, MatchingInformation.researcher_id == ResearcherInformation.researcher_id)
        .filter(ProjectInformation.company_user_id == company_user_id)
        .all()
    )

    # 結果を辞書のリストに整形して出力.プロジェクトIDでグルーピング
    project_dict = {}

    for row in results:
        pid = row.project_id

        if pid not in project_dict:
            project_dict[pid] = {
                "project_id": pid,
                "project_title": row.project_title,
                "registration_date": row.registration_date,
                "application_deadline": row.application_deadline,
                "project_status": row.project_status,
                "researchers": []
            }

        if row.researcher_id:  # マッチングが存在する場合のみ追加
            project_dict[pid]["researchers"].append({
                "researcher_id": row.researcher_id,
                "matching_status": row.matching_status,
                "researcher_name": row.researcher_name
            })
    
    return list(project_dict.values())

    # return[
    #     {
    #         "project_id": r.project_id,
    #         "project_title": r.project_title,
    #         "registration_date": r.registration_date,
    #         "application_deadline": r.application_deadline,
    #         "project_status": r.project_status,
    #         "researcher_id": r.researcher_id,
    #         "matching_status": r.matching_status,
    #         "researcher_name": r.researcher_name
    #     }
    #     for r in results
    # ]


    ## project_idだけを取得するver
    ## 事業者ユーザIDに紐づくプロジェクト情報を取得
    # projects = db.query(ProjectInformation).filter(ProjectInformation.company_user_id == company_user_id).all()

    # # 各プロジェクトからプロジェクトIDを取得
    # project_ids = []
    # for project in projects:
    #     project_ids.append(project.project_id)
    # return project_ids