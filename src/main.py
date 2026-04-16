# pandasをimportしてpdとして扱う
import pandas as pd

# CSV読み込み
df = pd.read_csv("data/bugs.csv")
# 未対応のみを抽出
unresolved = df[df["Status"] == "未対応"]
# 担当者ごとの未対応件数
count_by_assignee = unresolved["Assignee"].value_counts()

# 未対応バグを出力
print("=== 未対応バグ ===")
print(unresolved)
# 担当者別の未対応件数を出力
print("=== 担当者別未対応件数 ===")
print(count_by_assignee)

# 結果をCSVとして出力
unresolved.to_csv("output/unresolved_bugs.csv", index=False)