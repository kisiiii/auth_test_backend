from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.mymodels import CompanyUser
from components.hash import hash_password, verify_password
from schemas import UserCreate, UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["認証"]
)

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(CompanyUser).filter_by(company_user_name=user.company_user_name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ユーザー名はすでに存在します")

    new_user = CompanyUser(
        company_user_name=user.company_user_name,
        company_id=user.company_id,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "ユーザー登録に成功しました", "user_id": new_user.company_user_id}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(CompanyUser).filter_by(company_user_name=user.company_user_name).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="認証に失敗しました")

    return {
        "id": db_user.company_user_id,
        "name": db_user.company_user_name
    }
