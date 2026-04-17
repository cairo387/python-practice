# 基本構造
import sys
import os
import argparse
import pandas as pd

# 文字色
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
# 必須カラム
REQUIRED_COLUMNS = ["Status", "Priority", "Assignee", "CreatedDate"]

#csv読み込み関数
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    #例外処理
    except FileNotFoundError:
        print(f"{RED}存在エラー：ファイルが見つかりません: ファイル名：{file_path}{RESET}")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"{RED}存在エラー：CSVファイルにデータが存在しません。ファイル名：{file_path}{RESET}")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"{RED}形式エラー：CSVの形式が正しくありません。ファイル名：{file_path}{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}予期しないエラーが発生しました。エラー内容: {e}{RESET}")
        sys.exit(1)
    
# 単純集計
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

# データ絞り込み
# Statusが「未対応」のデータのみを抽出する関数
def extract_unresolved(df):
    return df[df["Status"] == "未対応"]

# クロス集計対応
# Status × Priority集計関数
def summarize_status_priority(df):
    return pd.crosstab(df["Status"], df["Priority"])
#　日別のステータスの集計関数
def summarize_daily_trend(df):
    return pd.crosstab(df["CreatedDate"], df["Status"]).sort_index()

# SLA（サービスレベルアグリーメント）違反検知
# CreatedDateから3日以上未対応のデータを抽出し、警告する関数
def detect_sla_violation(df):
    today = pd.Timestamp.today()
    unresolved = df[df["Status"] == "未対応"]
    overdue = unresolved[
        (today.normalize()  - unresolved["CreatedDate"]).dt.days > 3
        ]
    return overdue

# Excelへレポートを出力する
def export_to_excel(output_path, df, status_summary, priority_summary, assignee_summary, unresolved_df, status_priority, daily_trend, unresolved_over_3days):
    try:
        with pd.ExcelWriter(output_path) as writer:
            df.to_excel(writer, sheet_name="サマリー", index=False)
            status_summary.to_excel(writer, sheet_name="ステータス別集計")
            priority_summary.to_excel(writer, sheet_name="優先度別集計")
            assignee_summary.to_excel(writer, sheet_name="担当者別集計")
            unresolved_df.to_excel(writer, sheet_name="未対応データのみ抽出", index=False)
            status_priority.to_excel(writer, sheet_name="ステータス×優先度のクロス集計")
            daily_trend.to_excel(writer, sheet_name="日別のステータス推移")
            unresolved_over_3days.to_excel(writer, sheet_name="SLA違反_3日以上未対応")
    # 例外処理
    except PermissionError:
        print(f"{RED}出力エラー：出力先のExcelファイルが開かれています。閉じてから再実行してください。{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}出力エラー：Excelファイルのへの出力に失敗しました。{RESET}")
        sys.exit(1)


# 引数パーサー作成
def parse_args():
    parser = argparse.ArgumentParser(description="不具合分析レポート生成ツール")

    parser.add_argument("file", help="入力CSVファイルパス")
    parser.add_argument("--start", help="開始日（YYYY-MM-DD）", default=None)
    parser.add_argument("--end", help="終了日（YYYY-MM-DD）", default=None)
    parser.add_argument("--output", help="出力Excelファイル名", default="output/bug_report.xlsx")
    
    return parser.parse_args()

# CSVのカラム構成が条件を満たすかを検証する関数（満たさない場合はエラーメッセージを表示）
def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        print(f"{RED}存在エラー：必要な列[ {', '.join(missing)}]が存在しません。{RESET}")
        print(f"{RED}現在の列: {list(df.columns)}{RESET}")
        sys.exit(1)

# main関数
def main():
    args = parse_args()

    if not os.path.exists(args.file):
        print(f"{RED}存在エラー：指定されたファイルが存在しません。: 指定したファイル名：{args.file}{RESET}")
        sys.exit(1)
    
    file_path = args.file
    output_path = args.output

    df = load_csv(file_path)

    validate_columns(df)

    try:
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"])
    # 例外処理
    except Exception:
        print(f"{RED}形式エラー：CreatedDate列の日付形式が不正です。{RESET}")
        sys.exit(1)

    if args.start:
        start_date = pd.to_datetime(args.start)
        df = df[df["CreatedDate"] >= start_date]
    
    if args.end:
        end_date = pd.to_datetime(args.end)
        df = df[df["CreatedDate"] <= end_date]
    
    status_summary = summarize_by_status(df)
    priority_summary = summarize_by_priority(df)
    assignee_summary = summarize_by_assignee(df)
    unresolved_df = extract_unresolved(df)
    status_priority_df = summarize_status_priority(df)
    daily_trend_df = summarize_daily_trend(df)
    unresolved_over_3days_df = detect_sla_violation(df)

    export_to_excel(output_path, df, status_summary, priority_summary, assignee_summary, unresolved_df, status_priority_df, daily_trend_df, unresolved_over_3days_df)

    print(f"{GREEN}レポートが正常に出力されました。出力先：{args.output}{RESET}")

# エントリーポイント
if __name__ == "__main__":
    main()