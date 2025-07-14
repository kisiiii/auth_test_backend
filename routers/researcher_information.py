'''
クエリパラメータにプロジェクトIDを渡して、研究者情報詳細を取得するエンドポイントです
'''
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import ResearcherInformation

router = APIRouter(prefix="/researcher-information", tags=["researcher-information"])

@router.get("")
def researcher_information(
    researcher_id: int,
    db: Session = Depends(get_db),
    ):
    # マッチング情報を取得（該当プロジェクト）
    researcher = db.query(ResearcherInformation).filter(ResearcherInformation.researcher_id == researcher_id).first()

    if researcher is None:
        return None

    return {
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
        "projects": [
            {
                "project_id": p.research_project_id,
                "title": p.research_project_title,
                "details": p.research_project_details,
                "field": p.research_field,
                "achievement": p.research_achievement
            }
            for p in researcher.research_projects
        ]
    }
