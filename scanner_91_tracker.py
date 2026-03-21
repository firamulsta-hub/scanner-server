print("스캐너 9.1 시작 - 후보 종목 추적 시스템")

import pandas as pd
import FinanceDataReader as fdr
import os
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR
from datetime import datetime, timedelta

# =========================================
# 1. 경로 설정
# =========================================
DATA_PATHS = [
    str(OUTPUT_STABLE_DIR),
    str(OUTPUT_SWING_DIR),
    str(OUTPUT_60_DIR),
    str(OUTPUT_70_DIR)
]

OUTPUT_PATH = str(ANALYSIS_DIR)

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

today = datetime.today()

results = []

print("과거 후보 종목 추적 시작...")

# =========================================
# 2. 파일 순회
# =========================================
for path in DATA_PATHS:

    if not os.path.exists(path):
        print("경로 없음, 건너뜀:", path)
        continue

    for file in os.listdir(path):

        # all / final 파일만 분석
        if ("all" not in file) and ("final" not in file):
            continue

        try:
            file_path = os.path.join(path, file)
            df = pd.read_csv(file_path, encoding="utf-8-sig")

            if len(df) == 0:
                continue

            # 파일 종류 구분
            if "final" in file:
                file_type = "final"
            else:
                file_type = "all"

            # 스캐너 종류 구분
            if "scanner5_" in file:
                scanner_type = "5.0_stable"
            elif "scanner51_" in file:
                scanner_type = "5.1_swing"
            elif "scanner60_" in file:
                scanner_type = "6.0_force"
            elif "scanner70_" in file:
                scanner_type = "7.0_early"
            else:
                scanner_type = "unknown"

            for i in range(len(df)):

                try:
                    code = str(df.iloc[i]["종목코드"]).zfill(6)
                    name = df.iloc[i]["종목명"]

                    # 최근 7거래일 정도 가격 가져오기
                    price_df = fdr.DataReader(code, today - timedelta(days=10), today)

                    if len(price_df) < 2:
                        continue

                    # 전일 종가 / 금일 종가
                    prev_close = price_df["Close"].iloc[-2]
                    today_close = price_df["Close"].iloc[-1]
                    today_high = price_df["High"].iloc[-1]

                    day_return = (today_close / prev_close - 1) * 100
                    intraday_max = (today_high / prev_close - 1) * 100

                    results.append({
                        "스캐너": scanner_type,
                        "파일종류": file_type,
                        "종목코드": code,
                        "종목명": name,
                        "전일종가": prev_close,
                        "금일종가": today_close,
                        "장중최대상승률(%)": round(intraday_max, 2),
                        "종가수익률(%)": round(day_return, 2)
                    })

                except:
                    continue

        except:
            continue

# =========================================
# 3. 결과 정리
# =========================================
result_df = pd.DataFrame(results)

if len(result_df) == 0:
    print("추적할 데이터가 없습니다.")
else:
    print("\n===== 전체 추적 결과 =====")
    print("총 종목 수:", len(result_df))

    avg_close_return = result_df["종가수익률(%)"].mean()
    avg_intraday = result_df["장중최대상승률(%)"].mean()
    win_rate_close = (result_df["종가수익률(%)"] > 0).mean() * 100
    win_rate_intraday = (result_df["장중최대상승률(%)"] > 3).mean() * 100

    print("평균 종가 수익률:", round(avg_close_return, 2), "%")
    print("평균 장중 최대상승률:", round(avg_intraday, 2), "%")
    print("종가 기준 상승 확률:", round(win_rate_close, 2), "%")
    print("장중 3% 이상 상승 확률:", round(win_rate_intraday, 2), "%")

    # 스캐너별 요약
    summary_rows = []

    for scanner_name in result_df["스캐너"].unique():
        temp = result_df[result_df["스캐너"] == scanner_name]

        summary_rows.append({
            "스캐너": scanner_name,
            "종목수": len(temp),
            "평균종가수익률(%)": round(temp["종가수익률(%)"].mean(), 2),
            "평균장중최대상승률(%)": round(temp["장중최대상승률(%)"].mean(), 2),
            "종가상승확률(%)": round((temp["종가수익률(%)"] > 0).mean() * 100, 2),
            "장중3%상승확률(%)": round((temp["장중최대상승률(%)"] > 3).mean() * 100, 2)
        })

    summary_df = pd.DataFrame(summary_rows)

    print("\n===== 스캐너별 요약 =====")
    print(summary_df)

    # 저장
    detail_file = os.path.join(
        OUTPUT_PATH,
        f"scanner91_detail_{today.strftime('%Y%m%d')}.csv"
    )

    summary_file = os.path.join(
        OUTPUT_PATH,
        f"scanner91_summary_{today.strftime('%Y%m%d')}.csv"
    )

    result_df.to_csv(detail_file, index=False, encoding="utf-8-sig")
    summary_df.to_csv(summary_file, index=False, encoding="utf-8-sig")

    print("\n상세 저장:", detail_file)
    print("요약 저장:", summary_file)
