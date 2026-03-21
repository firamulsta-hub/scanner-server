print("스캐너 8.0 시작 - 성과 분석 시스템")

import pandas as pd
import FinanceDataReader as fdr
import os
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR
from datetime import datetime, timedelta

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

print("과거 스캐너 결과 분석 시작...")

for path in DATA_PATHS:

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

                    price_df = fdr.DataReader(code, today - timedelta(days=30), today)

                    if len(price_df) < 10:
                        continue

                    start_price = price_df["Close"].iloc[-10]
                    max_price = price_df["High"].max()

                    max_return = (max_price / start_price - 1) * 100

                    results.append({
                        "종목코드": code,
                        "종목명": name,
                        "최대수익률(%)": round(max_return,2)
                    })

                except:
                    continue

        except:
            continue

analysis_df = pd.DataFrame(results)

if len(analysis_df) > 0:

    avg_return = analysis_df["최대수익률(%)"].mean()
    win_rate = (analysis_df["최대수익률(%)"] > 5).mean() * 100

    summary = {
        "분석 종목수": len(analysis_df),
        "평균 최대수익률": round(avg_return,2),
        "5% 이상 상승 확률": round(win_rate,2)
    }

    print("\n===== 분석 결과 =====")
    print(summary)

    analysis_file = os.path.join(
        OUTPUT_PATH,
        f"scanner80_analysis_{today.strftime('%Y%m%d')}.csv"
    )

    analysis_df.to_csv(analysis_file, index=False, encoding="utf-8-sig")

    print("\n분석 파일 저장:", analysis_file)

else:

    print("분석할 데이터가 없습니다.")
