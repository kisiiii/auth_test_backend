import bcrypt

# ユーザーのパスワード
password = b"necpoc0103"

# ソルトを生成（コストファクターはデフォルトの12）
salt = bcrypt.gensalt()

# パスワードをハッシュ化
hashed_password = bcrypt.hashpw(password, salt)

# 結果を表示
print(f"Salt: {salt}")
print(f"Hashed Password: {hashed_password}")


# パスワードの検証
input_password = b"necpoc0103"

# パスワードを検証
if bcrypt.checkpw(input_password, hashed_password):
    print("パスワードが一致しました。")
else:
    print("パスワードが一致しません。")