#データベースに接続
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# ローカルで動かす時用
from dotenv import load_dotenv
load_dotenv()

SERVER_URL=os.getenv("SERVER_URL")
DATABASE=os.getenv("DATABASE")
USER_NAME=os.getenv("USER_NAME")
PASSWORD=os.getenv("PASSWORD")
SERVER_PORT=os.getenv("SERVER_PORT")
SSL_CA_PATH=os.getenv("SSL_CA_PATH") #本番で必要

#ローカルでは不要
#DATABASE_URL = f"mysql+pymysql://{USER_NAME}:{PASSWORD}@{SERVER_URL}:{SERVER_PORT}/{DATABASE}?charset=utf8"

#本番環境で動かす時用
DATABASE_URL = f"mysql+pymysql://{USER_NAME}:{PASSWORD}@{SERVER_URL}:{SERVER_PORT}/{DATABASE}?charset=utf8&ssl_ca={SSL_CA_PATH}"

# データベースエンジンを作成
engine = create_engine(
    DATABASE_URL,echo=False, pool_pre_ping=True
)

# セッションファクトリを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # セッションを作成
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test the connection
if __name__ == "__main__":
    try:
        # Try to connect to the database
        connection = engine.connect()
        print("Connection successful!")
        connection.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
