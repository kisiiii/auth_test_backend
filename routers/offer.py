'''
オファーを押したら、マッチングステータスを変更するエンドポイントです。
'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# スキーマのインポート
from schemas import Offers

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import MatchingInformation

router = APIRouter(prefix="/offers", tags=["offers"])

'''
マッチングステータスを0:マッチング待機 ⇒ 1:オファー中に変更する
'''
@router.post("")
def offers(
    offer_list: Offers,
    db: Session = Depends(get_db)
    ):
    try:
        for researcher_id in offer_list.researcher_ids:
            record = db.query(MatchingInformation).filter_by(
                project_id=offer_list.project_id,
                researcher_id=researcher_id,
            ).first()

            if record:
                if record.matching_status == 0:
                    record.matching_status = 1  # オファー中に変更
            else:
                raise HTTPException(status_code=404, detail=f"該当するマッチング情報が見つかりません: project_id={offer_list.projectId}, researcher_id={researcher_id}")

        db.commit()
        return {"message": "すべてのマッチングステータスをオファー中に更新しました"}

    except Exception as e:
        db.rollback()
        print("例外発生！:", e)
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")