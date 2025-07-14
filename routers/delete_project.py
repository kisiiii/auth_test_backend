'''
クエリパラメータにプロジェクトIDを渡して、プロジェクト並びに紐づくマッチング結果を削除するエンドポイントです
'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import MatchingInformation, ProjectInformation

router = APIRouter(prefix="/delete-project", tags=["delete-project"])

'''
プロジェクトの削除
'''
@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    ):
    project = db.query(ProjectInformation).filter(ProjectInformation.project_id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="ProjectInformation not found")

    # 紐づくマッチング情報を削除
    db.query(MatchingInformation).filter(MatchingInformation.project_id == project_id).delete()

    # プロジェクトを削除
    db.delete(project)
    db.commit()

    return