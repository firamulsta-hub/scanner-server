print("스캐너 9.0 시작 - 종목 추적 시스템")

import pandas as pd
import FinanceDataReader as fdr
import os
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR
from datetime import datetime, timedelta

# 🔹 경로 설정
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
yesterday = today - timedelta(days=1)

results = []

print("어제 추천 종목 추적 시작...")

for path in DATA_PATHS:

    if not os.path.exists(path):
        continue

    for file in os.listdir(path):

        if "final" not in file:
            continue

        try:
            file_path = os.path.join(path, file)
            df = pd.read_csv(file_path, encoding="utf-8-sig")

            if len(df) == 0:
                continue

            for i in range(len(df)):

                code = str(df.iloc[i]["종목코드"]).zfill(6)
                name = df.iloc[i]["종목명"]

                try:
                    price_df = fdr.DataReader(code, today - timedelta(days=5), today)

                    if len(price_df) < 2:
                        continue

                    yesterday_close = price_df["Close"].iloc[-2]
                    today_close = price_df["Close"].iloc[-1]

                    return_pct = (today_close / yesterday_close - 1) * 100

                    results.append({
                        "종목코드": code,
                        "종목명": name,
                        "전일종가": yesterday_close,
                        "금일종가": today_close,
                        "수익률(%)": round(return_pct, 2)
                    })

                except:
                    continue

        except:
            continue

# 결과 정리
result_df = pd.DataFrame(results)

if len(result_df) > 0:

    avg_return = result_df["수익률(%)"].mean()
    win_rate = (result_df["수익률(%)"] > 0).mean() * 100

    print("\n===== 추적 결과 =====")
    print("종목 수:", len(result_df))
    print("평균 수익률:", round(avg_return, 2))
    print("상승 확률:", round(win_rate, 2), "%")

    file_name = os.path.join(
        OUTPUT_PATH,
        f"scanner90_result_{today.strftime('%Y%m%d')}.csv"
    )

    result_df.to_csv(file_name, index=False, encoding="utf-8-sig")

    print("\n저장 완료:", file_name)

else:
    print("추적할 종목이 없습니다.")
