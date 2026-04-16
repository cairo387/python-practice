# sysをimportする
import sys
# pandasをimportしてpdとして扱う
import pandas as pd

# コマンドで渡されたファイル名を受け取る
file_path = sys.argv[1]
# CSV読み込み
df = pd.read_csv(file_path)

# 未対応のみを抽出(関数)
def extract_unresolved(df):
    return df[df["Status"] == "未対応"]
# 担当者ごとの未対応件数(関数)
def count_by_assignee(df):
    return df["Assignee"].value_counts()

unresolved = extract_unresolved(df)
count = count_by_assignee(df)

# 未対応バグを出力
print("=== 未対応バグ ===")
print(unresolved)
# 担当者別の未対応件数を出力
print("=== 担当者別未対応件数 ===")
print(count)

# 結果をCSVとして出力
unresolved.to_excel("output/unresolved.xlsx", index=False)