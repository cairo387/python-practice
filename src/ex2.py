# 基本構造
import sys
import os
import pandas as pd

#文字色定義
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

#csv読み込み関数
def load_csv(file_path):
    return pd.read_csv(file_path)

# ステータス別件数のカウント関数
def summarize_by_status(df):
    #value_counts()は出現回数をカウントするメソッド
    return df["Status"].value_counts()

# 優先度別件数のカウント関数
def summarize_by_priority(df):
    return df["Priority"].value_counts()

# 担当者別件数のカウント関数
def summarize_by_assignee(df):
    return df["Assignee"].value_counts()

# Statusが「未対応」のデータのみを抽出する関数
def extract_unresolved(df):
    return df[df["Status"] == "未対応"]

# Excelへレポートを出力する
def export_to_excel(df, status_summary, priority_summary, assignee_summary, unresolved_df):
    with pd.ExcelWriter("output/bug_report.xlsx") as writer:
        df.to_excel(writer, sheet_name="RawData", index=False)
        status_summary.to_excel(writer, sheet_name="StatusSummary")
        priority_summary.to_excel(writer, sheet_name="PrioritySummary")
        assignee_summary.to_excel(writer, sheet_name="AssigneeSummary")
        unresolved_df.to_excel(writer, sheet_name="Unresolved", index=False)

# main関数
def main():
    #例外処理：コマンドエラー
    if len(sys.argv) < 2:
        print(f"{RED}コマンドエラー：「python ex2.py 【csvファイル】の形式でターミナル実行してください。」{RESET}")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    #例外処理：ファイル存在チェック
    if not os.path.exists(file_path):
        print(f"{RED}存在エラー：指定されたファイルが存在しません。{RESET}")
        sys.exit(1)

    #例外処理：ファイル読み込みエラー
    try:
        df = load_csv(file_path)
    except Exception as e:
        print(f"{RED}読み込みエラー：CSVの読み込みに失敗しました。エラー内容:{e}{RESET}")
        sys.exit(1)
    
    status_summary = summarize_by_status(df)
    priority_summary = summarize_by_priority(df)
    assignee_summary = summarize_by_assignee(df)
    unresolved_df = extract_unresolved(df)

    export_to_excel(df, status_summary, priority_summary, assignee_summary, unresolved_df)

    print(f"{GREEN}レポートが正常に出力されました。{RESET}")

# エントリーポイント
if __name__ == "__main__":
    main()