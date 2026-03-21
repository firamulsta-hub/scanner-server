print("스캐너 9.3B 시작 - 보완형 매수 타이밍 계산기")

import pandas as pd
import FinanceDataReader as fdr
import os
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR
from datetime import datetime, timedelta

# =========================================
# 1. 경로 설정
# =========================================
DATA_FOLDERS = [
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

print("후보 종목 불러오는 중...")

# =========================================
# 2. 파일 선택 함수
# =========================================
def pick_target_file(folder, today_str):
    if not os.path.exists(folder):
        return None, None

    files = os.listdir(folder)

    a_files = [f for f in files if "_A_" in f and today_str in f]
    final_files = [f for f in files if "final" in f and today_str in f]
    all_files = [f for f in files if "all" in f and today_str in f]

    if a_files:
        return os.path.join(folder, a_files[0]), "A"
    elif final_files:
        return os.path.join(folder, final_files[0]), "final"
    elif all_files:
        return os.path.join(folder, all_files[0]), "all"
    else:
        return None, None

# =========================================
# 3. 파일별 종목 읽기
# =========================================
candidate_rows = []

for folder in DATA_FOLDERS:
    file_path, file_type = pick_target_file(folder, today_str)

    if file_path is None:
        continue

    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

        if len(df) == 0:
            continue

        # all 파일이면 상위 10개만 사용
        if file_type == "all":
            if "총점" in df.columns:
                df = df.sort_values(by="총점", ascending=False).head(10)
            elif "차트점수" in df.columns:
                df = df.sort_values(by="차트점수", ascending=False).head(10)
            else:
                df = df.head(10)

        for i in range(len(df)):
            candidate_rows.append({
                "file_type": file_type,
                "code": str(df.iloc[i]["종목코드"]).zfill(6),
                "name": df.iloc[i]["종목명"]
            })

    except Exception:
        continue

# 중복 제거
seen = set()
unique_candidates = []

for row in candidate_rows:
    if row["code"] in seen:
        continue
    seen.add(row["code"])
    unique_candidates.append(row)

# =========================================
# 4. 종목별 매수/손절/목표가 계산
# =========================================
for row in unique_candidates:
    code = row["code"]
    name = row["name"]
    source_type = row["file_type"]

    try:
        price_df = fdr.DataReader(code, today - timedelta(days=90), today)

        if len(price_df) < 25:
            continue

        last_close = price_df["Close"].iloc[-1]
        last_open = price_df["Open"].iloc[-1]
        last_high = price_df["High"].iloc[-1]
        last_low = price_df["Low"].iloc[-1]

        ma5 = price_df["Close"].rolling(5).mean().iloc[-1]
        ma20 = price_df["Close"].rolling(20).mean().iloc[-1]

        high_20 = price_df["High"].tail(20).max()
        low_20 = price_df["Low"].tail(20).min()

        avg_range = (price_df["High"] - price_df["Low"]).tail(5).mean()

        # 파일 타입별 매매 강도
        if source_type == "A":
            confidence = "높음"
        elif source_type == "final":
            confidence = "중간"
        else:
            confidence = "관찰"

        # 매매 스타일
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

        risk = buy_max - stop_loss
        reward = target_1 - buy_max

        if risk <= 0:
            rr_ratio = 0
        else:
            rr_ratio = round(reward / risk, 2)

        results.append({
            "출처": source_type,
            "신뢰도": confidence,
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

# =========================================
# 5. 결과 정리
# =========================================
result_df = pd.DataFrame(results)

if len(result_df) == 0:
    print("계산할 종목이 없습니다.")
else:
    # 신뢰도 우선, 손익비 우선
    confidence_order = {"높음": 0, "중간": 1, "관찰": 2}
    result_df["신뢰도정렬"] = result_df["신뢰도"].map(confidence_order)

    result_df = result_df.sort_values(
        by=["신뢰도정렬", "손익비", "현재가"],
        ascending=[True, False, False]
    ).reset_index(drop=True)

    result_df = result_df.drop(columns=["신뢰도정렬"])

    print("\n===== 9.3B 매수 타이밍 계산 결과 =====")
    print(result_df)

    output_file = os.path.join(
        OUTPUT_PATH,
        f"scanner93b_entry_{today_str}.csv"
    )

    result_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("\n저장 완료:", output_file)
