'''
フロントエンドとバックエンドのつなぎこみテスト用のエンドポイントです。
'''
from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])

# テスト用のAPI
@router.get("")
def test():
    return {"message": "HelloWorld!"}
