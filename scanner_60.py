print("스캐너 6.0 시작 - 세력 포착형")

import FinanceDataReader as fdr
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
import glob
import os
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR

# =========================================
# 0. 저장 폴더
# =========================================
OUTPUT_DIR = str(OUTPUT_60_DIR)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# =========================================
# 1. 날짜 설정
# =========================================
today = datetime.today()
today_str = today.strftime("%Y%m%d")
start_date = today - timedelta(days=240)

print("종목 리스트 불러오는 중...")

# =========================================
# 2. 시장 데이터
# =========================================
kospi = fdr.StockListing("KOSPI")
kosdaq = fdr.StockListing("KOSDAQ")

kospi["MarketType"] = "KOSPI"
kosdaq["MarketType"] = "KOSDAQ"

stocks = pd.concat([kospi, kosdaq], ignore_index=True)

# 시총 컬럼 자동 판별
if "Marcap" in stocks.columns:
    market_cap_col = "Marcap"
elif "MarketCap" in stocks.columns:
    market_cap_col = "MarketCap"
else:
    market_cap_col = None

if market_cap_col:
    stocks = stocks.sort_values(by=market_cap_col, ascending=False)

# 세력 포착형은 1500개 사용
stocks = stocks.head(1500).reset_index(drop=True)

print("스캔 대상 종목 수:", len(stocks))

# =========================================
# 3. 시장 위험도 체크
# =========================================
print("시장 위험도 체크 중...")

risk_mode = False
risk_reason = []

try:
    kospi_index = fdr.DataReader("KS11", today - timedelta(days=120), today)

    if len(kospi_index) >= 60:
        kospi_index["MA20"] = kospi_index["Close"].rolling(20).mean()
        kospi_index["MA60"] = kospi_index["Close"].rolling(60).mean()

        idx_close = kospi_index["Close"].iloc[-1]
        idx_ma20 = kospi_index["MA20"].iloc[-1]
        idx_ma60 = kospi_index["MA60"].iloc[-1]
        idx_change_1d = (idx_close / kospi_index["Close"].iloc[-2] - 1) * 100
        idx_change_5d = (idx_close / kospi_index["Close"].iloc[-6] - 1) * 100

        if idx_close < idx_ma20:
            risk_mode = True
            risk_reason.append("KOSPI가 20일선 아래")

        if idx_close < idx_ma60:
            risk_mode = True
            risk_reason.append("KOSPI가 60일선 아래")

        if abs(idx_change_1d) >= 3:
            risk_mode = True
            risk_reason.append("KOSPI 일간 변동성 3% 이상")

        if abs(idx_change_5d) >= 6:
            risk_mode = True
            risk_reason.append("KOSPI 5일 변동성 6% 이상")

except Exception:
    print("시장 위험도 체크 실패 - 기본모드로 진행")

print("위험모드:", "ON" if risk_mode else "OFF")
if len(risk_reason) > 0:
    print("위험사유:", ", ".join(risk_reason))

print("\n1차 세력 포착 스캔 시작...\n")

# =========================================
# 4. 1차 후보 추출
# =========================================
results = []

for i in range(len(stocks)):
    code = stocks.iloc[i]["Code"]
    name = stocks.iloc[i]["Name"]
    market = stocks.iloc[i]["MarketType"]

    try:
        df = fdr.DataReader(code, start_date, today)

        if len(df) < 80:
            continue

        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA60"] = df["Close"].rolling(60).mean()
        df["VOL20"] = df["Volume"].rolling(20).mean()
        df["VOL5"] = df["Volume"].rolling(5).mean()

        last_close = df["Close"].iloc[-1]
        last_open = df["Open"].iloc[-1]
        last_high = df["High"].iloc[-1]
        last_low = df["Low"].iloc[-1]
        last_volume = df["Volume"].iloc[-1]

        ma20 = df["MA20"].iloc[-1]
        ma60 = df["MA60"].iloc[-1]
        vol20 = df["VOL20"].iloc[-1]
        vol5 = df["VOL5"].iloc[-1]

        high_20 = df["High"].tail(20).max()
        low_20 = df["Low"].tail(20).min()
        high_60 = df["High"].tail(60).max()
        low_60 = df["Low"].tail(60).min()

        close_5days_ago = df["Close"].iloc[-6]
        close_20days_ago = df["Close"].iloc[-21]

        change_5d = (last_close / close_5days_ago - 1) * 100
        change_20d = (last_close / close_20days_ago - 1) * 100

        traded_value = last_close * last_volume

        # ---------------------------------
        # 기본 제외 조건
        # ---------------------------------
        if traded_value < 3000000000:   # 30억 이상
            continue

        if last_close < 1500:
            continue

        # ---------------------------------
        # 기본 추세 조건
        # ---------------------------------
        cond1 = last_close > ma20
        cond2 = last_close > ma60
        cond3 = last_volume > vol20 * 1.10
        cond4 = last_close >= high_20 * 0.93
        cond5 = change_5d <= 15
        cond6 = last_close > last_open
        cond7 = change_20d >= 2
        cond8 = last_high >= high_20 * 0.96

        chart_score = sum([cond1, cond2, cond3, cond4, cond5, cond6, cond7, cond8])

        # ---------------------------------
        # 세력 매집 점수
        # ---------------------------------
        cond_acc_1 = vol5 > vol20 * 1.05                 # 최근 거래량이 조금씩 붙음
        cond_acc_2 = last_close >= low_20 * 1.05         # 박스 하단에서 올라옴
        cond_acc_3 = last_close < high_20 * 1.02         # 너무 멀리 급등 안함
        cond_acc_4 = (high_20 / low_20) <= 1.35          # 박스폭이 너무 과하지 않음
        cond_acc_5 = change_20d <= 25                    # 20일 급등주 제외

        accumulation_score = sum([cond_acc_1, cond_acc_2, cond_acc_3, cond_acc_4, cond_acc_5])

        # ---------------------------------
        # 돌파 임박 점수
        # ---------------------------------
        cond_br_1 = last_close >= high_20 * 0.95
        cond_br_2 = last_high >= high_20 * 0.98
        cond_br_3 = last_close < high_60 * 1.03
        cond_br_4 = last_close > ma20 and ma20 > ma60
        cond_br_5 = traded_value >= 5000000000           # 50억 이상이면 우선

        breakout_score = sum([cond_br_1, cond_br_2, cond_br_3, cond_br_4, cond_br_5])

        # ---------------------------------
        # 총점
        # ---------------------------------
        total_score = chart_score + accumulation_score + breakout_score

        # 위험모드면 더 엄격하게
        if risk_mode:
            if traded_value < 5000000000:
                continue
            if change_5d > 10:
                continue
            if total_score < 12:
                continue

        # 등급
        if total_score >= 15:
            grade = "A"
        elif total_score >= 12:
            grade = "B"
        elif total_score >= 10:
            grade = "C"
        else:
            grade = "D"

        if grade in ["A", "B"]:
            results.append({
                "등급": grade,
                "시장": market,
                "종목코드": str(code).zfill(6),
                "종목명": name,
                "현재가": round(last_close, 2),
                "5일변화율(%)": round(change_5d, 2),
                "20일변화율(%)": round(change_20d, 2),
                "거래대금(원)": int(traded_value),
                "차트점수": chart_score,
                "매집점수": accumulation_score,
                "돌파점수": breakout_score,
                "총점": total_score,
                "기준일자": df.index[-1].strftime("%Y%m%d")
            })

    except Exception:
        continue

base_df = pd.DataFrame(results)

print("[1차 후보 종목 수]", len(base_df))

# =========================================
# 5. 2차 수급 검사
# =========================================
final_rows = []

if len(base_df) > 0:
    print("2차 기관/외국인 수급 검사 시작...\n")

    for i in range(len(base_df)):
        row = base_df.iloc[i]
        code = row["종목코드"]
        base_date = row["기준일자"]

        try:
            from_date = (datetime.strptime(base_date, "%Y%m%d") - timedelta(days=15)).strftime("%Y%m%d")
            to_date = base_date

            trading_df = stock.get_market_trading_value_by_date(from_date, to_date, code)

            if trading_df is None or len(trading_df) < 3:
                continue

            trading_df = trading_df.tail(3)

            inst_col = None
            foreign_col = None

            for c in trading_df.columns:
                if "기관합계" in c:
                    inst_col = c
                if "외국인합계" in c:
                    foreign_col = c

            if inst_col is None or foreign_col is None:
                continue

            inst_series = trading_df[inst_col].fillna(0)
            foreign_series = trading_df[foreign_col].fillna(0)

            inst_sum_3d = inst_series.sum()
            foreign_sum_3d = foreign_series.sum()

            inst_positive_days = (inst_series > 0).sum()
            foreign_positive_days = (foreign_series > 0).sum()

            cond_inst_1 = inst_sum_3d > 0
            cond_inst_2 = inst_positive_days >= 1
            cond_for_1 = foreign_sum_3d > 0
            cond_for_2 = foreign_positive_days >= 1
            cond_lastday = (inst_series.iloc[-1] > 0) or (foreign_series.iloc[-1] > 0)

            investor_score = sum([cond_inst_1, cond_inst_2, cond_for_1, cond_for_2, cond_lastday])

            if investor_score >= 4:
                investor_grade = "A"
            elif investor_score >= 3:
                investor_grade = "B"
            elif investor_score >= 2:
                investor_grade = "C"
            else:
                investor_grade = "D"

            if risk_mode:
                pass_condition = investor_score >= 3
            else:
                pass_condition = investor_score >= 2

            if pass_condition:
                if row["등급"] == "A" and investor_grade in ["A", "B"]:
                    final_grade = "A"
                else:
                    final_grade = "B"

                final_rows.append({
                    "최종등급": final_grade,
                    "차트등급": row["등급"],
                    "수급등급": investor_grade,
                    "시장": row["시장"],
                    "종목코드": row["종목코드"],
                    "종목명": row["종목명"],
                    "현재가": row["현재가"],
                    "5일변화율(%)": row["5일변화율(%)"],
                    "20일변화율(%)": row["20일변화율(%)"],
                    "거래대금(원)": row["거래대금(원)"],
                    "차트점수": row["차트점수"],
                    "매집점수": row["매집점수"],
                    "돌파점수": row["돌파점수"],
                    "총점": row["총점"],
                    "수급점수": investor_score,
                    "기관3일합계": int(inst_sum_3d),
                    "외국인3일합계": int(foreign_sum_3d),
                    "기관양수일수": int(inst_positive_days),
                    "외국인양수일수": int(foreign_positive_days)
                })

        except Exception:
            continue

final_df = pd.DataFrame(final_rows)

# =========================================
# 6. 신규 후보 표시
# =========================================
if len(final_df) > 0:
    final_df["신규후보"] = "Y"

    prev_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "scanner60_final_*.csv")))
    prev_files = [f for f in prev_files if today_str not in f]

    if len(prev_files) > 0:
        prev_file = prev_files[-1]
        try:
            prev_df = pd.read_csv(prev_file, encoding="utf-8-sig")
            if "종목코드" in prev_df.columns:
                prev_codes = set(prev_df["종목코드"].astype(str).str.zfill(6))
                final_df["종목코드"] = final_df["종목코드"].astype(str).str.zfill(6)
                final_df["신규후보"] = final_df["종목코드"].apply(
                    lambda x: "Y" if x not in prev_codes else ""
                )
        except Exception:
            pass

    final_df = final_df.sort_values(
        by=["최종등급", "총점", "수급점수", "거래대금(원)"],
        ascending=[True, False, False, False]
    ).reset_index(drop=True)

# =========================================
# 7. 저장
# =========================================
all_file = os.path.join(OUTPUT_DIR, f"scanner60_all_{today_str}.csv")
final_file = os.path.join(OUTPUT_DIR, f"scanner60_final_{today_str}.csv")
a_file = os.path.join(OUTPUT_DIR, f"scanner60_A_{today_str}.csv")
summary_file = os.path.join(OUTPUT_DIR, f"scanner60_summary_{today_str}.txt")

base_df.to_csv(all_file, index=False, encoding="utf-8-sig")

if len(final_df) > 0:
    final_df.to_csv(final_file, index=False, encoding="utf-8-sig")
    a_df = final_df[final_df["최종등급"] == "A"].reset_index(drop=True)
    a_df.to_csv(a_file, index=False, encoding="utf-8-sig")
else:
    pd.DataFrame().to_csv(final_file, index=False, encoding="utf-8-sig")
    pd.DataFrame().to_csv(a_file, index=False, encoding="utf-8-sig")

# =========================================
# 8. 요약 저장
# =========================================
with open(summary_file, "w", encoding="utf-8-sig") as f:
    f.write("스캐너 6.0 요약\n")
    f.write("=" * 40 + "\n")
    f.write(f"기준일자: {today_str}\n")
    f.write(f"위험모드: {'ON' if risk_mode else 'OFF'}\n")
    if len(risk_reason) > 0:
        f.write("위험사유: " + ", ".join(risk_reason) + "\n")
    f.write(f"1차 후보 수: {len(base_df)}\n")
    f.write(f"최종 후보 수: {len(final_df)}\n")

    if len(final_df) > 0:
        f.write("\n[최종 상위 10종목]\n")
        top10 = final_df.head(10)
        for i in range(len(top10)):
            r = top10.iloc[i]
            f.write(
                f"{i+1}. {r['최종등급']} / {r['시장']} / {r['종목명']} / "
                f"총점 {r['총점']} / 신규 {r['신규후보']}\n"
            )

# =========================================
# 9. 출력
# =========================================
print("\n[스캐너 6.0 최종 후보]")
print("-" * 100)

if len(final_df) == 0:
    print("최종 통과 종목이 없습니다.")
else:
    print(final_df)

print("\n저장 위치:", OUTPUT_DIR)
print("1차 후보 저장:", all_file)
print("최종 후보 저장:", final_file)
print("A등급 저장:", a_file)
print("요약 저장:", summary_file)
