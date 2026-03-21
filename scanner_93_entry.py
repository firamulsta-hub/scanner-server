print("스캐너 9.3 시작 - 매수 타이밍 계산기")

import pandas as pd
import FinanceDataReader as fdr
import os
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR
from datetime import datetime, timedelta

# =========================================
# 1. 경로 설정
# =========================================
DATA_FILES = [
    str(OUTPUT_70_DIR),
    str(OUTPUT_60_DIR),
    str(OUTPUT_SWING_DIR),
    str(OUTPUT_STABLE_DIR)
]

OUTPUT_PATH = str(ANALYSIS_DIR)

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

today = datetime.today()
today_str = today.strftime("%Y%m%d")

results = []

print("A등급 종목 불러오는 중...")

# =========================================
# 2. 최신 A 파일 찾기
# =========================================
target_files = []

for folder in DATA_FILES:
    if not os.path.exists(folder):
        continue

    files = [f for f in os.listdir(folder) if "_A_" in f and today_str in f]
    for f in files:
        target_files.append(os.path.join(folder, f))

if len(target_files) == 0:
    print("오늘 A등급 파일이 없습니다.")
    raise SystemExit

# =========================================
# 3. 종목별 매수/손절/목표가 계산
# =========================================
for file_path in target_files:
    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

        if len(df) == 0:
            continue

        for i in range(len(df)):
            try:
                code = str(df.iloc[i]["종목코드"]).zfill(6)
                name = df.iloc[i]["종목명"]

                price_df = fdr.DataReader(code, today - timedelta(days=90), today)

                if len(price_df) < 25:
                    continue

                # 최근 데이터
                last_close = price_df["Close"].iloc[-1]
                last_open = price_df["Open"].iloc[-1]
                last_high = price_df["High"].iloc[-1]
                last_low = price_df["Low"].iloc[-1]

                # 평균선
                ma5 = price_df["Close"].rolling(5).mean().iloc[-1]
                ma20 = price_df["Close"].rolling(20).mean().iloc[-1]

                # 최근 20일 고점/저점
                high_20 = price_df["High"].tail(20).max()
                low_20 = price_df["Low"].tail(20).min()

                # ATR 비슷하게 사용: 최근 5일 평균 변동폭
                avg_range = (price_df["High"] - price_df["Low"]).tail(5).mean()

                # -----------------------------
                # 매매 스타일 판별
                # -----------------------------
                # 현재가가 20일 고점 97% 이상이면 돌파형
                if last_close >= high_20 * 0.97:
                    style = "돌파 매수형"

                    buy_min = round(high_20 * 0.995, 2)
                    buy_max = round(high_20 * 1.01, 2)
                    chase_stop = round(high_20 * 1.03, 2)
                    stop_loss = round(ma20, 2)
                    target_1 = round(high_20 + avg_range * 2, 2)

                else:
                    style = "눌림 매수형"

                    buy_min = round(max(ma5, ma20), 2)
                    buy_max = round(last_close * 0.99, 2)
                    chase_stop = round(last_close * 1.03, 2)
                    stop_loss = round(low_20 * 0.98, 2)
                    target_1 = round(high_20, 2)

                # 손익비 계산
                risk = buy_max - stop_loss
                reward = target_1 - buy_max

                if risk <= 0:
                    rr_ratio = 0
                else:
                    rr_ratio = round(reward / risk, 2)

                results.append({
                    "종목코드": code,
                    "종목명": name,
                    "현재가": round(last_close, 2),
                    "매매스타일": style,
                    "매수구간_최소": buy_min,
                    "매수구간_최대": buy_max,
                    "추격금지": chase_stop,
                    "손절선": stop_loss,
                    "1차목표가": target_1,
                    "손익비": rr_ratio
                })

            except Exception:
                continue

    except Exception:
        continue

# =========================================
# 4. 결과 정리
# =========================================
result_df = pd.DataFrame(results)

if len(result_df) == 0:
    print("계산할 종목이 없습니다.")
else:
    result_df = result_df.sort_values(
        by=["손익비", "현재가"],
        ascending=[False, False]
    ).reset_index(drop=True)

    print("\n===== 9.3 매수 타이밍 계산 결과 =====")
    print(result_df)

    output_file = os.path.join(
        OUTPUT_PATH,
        f"scanner93_entry_{today_str}.csv"
    )

    result_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("\n저장 완료:", output_file)
