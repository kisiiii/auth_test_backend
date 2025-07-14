'''
クエリパラメータにプロジェクトIDを渡して、マッチング結果を取得するエンドポイントです
'''
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import MatchingInformation, ResearcherInformation, ProjectInformation

router = APIRouter(prefix="/matching-results", tags=["matching-results"])

'''
マッチング情報の取得
'''
@router.get("")
def matching_results(
    project_id: int,
    db: Session = Depends(get_db),
    ):
    # マッチング情報を取得（該当プロジェクト）
    matchings = db.query(MatchingInformation).filter(MatchingInformation.project_id == project_id).all()
    # プロジェクト情報を取得（1件のみ想定）
    project = db.query(ProjectInformation).filter(ProjectInformation.project_id == project_id).first()

    # 各マッチングから研究者IDを使って研究者情報を取得
    researcher_results = []
    for match in matchings:
        researcher = db.query(ResearcherInformation).filter(ResearcherInformation.researcher_id == match.researcher_id).first()
        if researcher:
            researcher_results.append({
                "researcher": {
                    "researcher_id": researcher.researcher_id,
                    "researcher_name": researcher.researcher_name,
                    "researcher_name_kana": researcher.researcher_name_kana,
                    "researcher_name_alphabet": researcher.researcher_name_alphabet,
                    "researcher_affiliation_current": researcher.researcher_affiliation_current,
                    "researcher_department_current": researcher.researcher_department_current,
                    "researcher_position_current": researcher.researcher_position_current,
                    "research_field_pi": researcher.research_field_pi,
                    "keywords_pi": researcher.keywords_pi,
                    "researcher_affiliations_past": researcher.researcher_affiliations_past
                },
                "matching_reason": match.matching_reason,
                "matching_status": match.matching_status,
                "matched_date": match.matched_date
            })
            #     {
            #     "id": researcher.researcher_id,
            #     "name": researcher.researcher_name,
            #     "affiliation": researcher.affiliation
            # })

    return {
        "project": {
            "project_title": project.project_title,
            "consultation_category": project.consultation_category,
            "project_content": project.project_content,
            "research_field": project.research_field,
            "preferred_researcher_level": project.preferred_researcher_level,
            "application_deadline": project.application_deadline,
            "project_status": project.project_status,
            "registration_date": project.registration_date,
            "closed_date": project.closed_date,
        } if project else None,
        "matchings": researcher_results
    }