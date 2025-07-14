from connection import engine  # engine を読み込み
from mymodels import Base      # モデル（Base）を読み込み

# テーブル作成
if __name__ == "__main__":
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ テーブル作成が完了しました")
    except Exception as e:
        print(f"❌ テーブル作成時にエラーが発生しました: {e}")
