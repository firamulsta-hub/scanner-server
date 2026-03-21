print("스캐너 9.2 시작 - 자동 매매 전략 추천 시스템")

import pandas as pd
import os
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR
from datetime import datetime

# =========================================
# 1. 경로 설정
# =========================================
ANALYSIS_PATH = str(ANALYSIS_DIR)
today_str = datetime.today().strftime("%Y%m%d")

summary_file = os.path.join(ANALYSIS_PATH, f"scanner91_summary_{today_str}.csv")

if not os.path.exists(summary_file):
    print("9.1 요약 파일이 없습니다.")
    print("먼저 scanner_91_tracker.py 를 실행하세요.")
    raise SystemExit

# =========================================
# 2. 데이터 읽기
# =========================================
df = pd.read_csv(summary_file, encoding="utf-8-sig")

if len(df) == 0:
    print("분석 데이터가 없습니다.")
    raise SystemExit

print("\n===== 스캐너별 성과 =====")
print(df)

# =========================================
# 3. 전략 판단 로직
# =========================================
# 기준
# 평균종가수익률(%) > 2.0 이면 강한 스캐너
# 종가상승확률(%) > 65 이면 신뢰도 높음
# 장중3%상승확률(%) > 70 이면 단타 매력 높음

strong_scanners = []
swing_scanners = []
stable_scanners = []

for i in range(len(df)):
    row = df.iloc[i]

    scanner_name = row["스캐너"]
    avg_return = row["평균종가수익률(%)"]
    win_rate = row["종가상승확률(%)"]
    intraday_power = row["장중3%상승확률(%)"]

    # 강한 스캐너
    if avg_return >= 2.0 and win_rate >= 65:
        strong_scanners.append(scanner_name)

    # 장중 폭발력 좋음
    if intraday_power >= 70:
        swing_scanners.append(scanner_name)

    # 안정적
    if scanner_name == "5.0_stable" and avg_return >= 1.0:
        stable_scanners.append(scanner_name)

# =========================================
# 4. 시장 상태 판별
# =========================================
market_mode = "중립"
recommended_scanners = []
position_size = "관망"
strategy_type = "대기"
comment = ""

if len(strong_scanners) >= 3:
    market_mode = "강세 확산형"
    recommended_scanners = strong_scanners
    position_size = "총 자금의 30%~40%"
    strategy_type = "단타 + 스윙 병행"
    comment = "여러 스캐너가 동시에 강합니다. 시장이 상승장 초입일 가능성이 큽니다."

elif len(strong_scanners) >= 1 and len(swing_scanners) >= 2:
    market_mode = "초기 반등형"
    recommended_scanners = list(set(strong_scanners + swing_scanners))
    position_size = "총 자금의 20%~30%"
    strategy_type = "단타 중심 / 짧은 스윙"
    comment = "초기 반등이 강하게 나오고 있습니다. 다만 아직 추세 확정은 아닐 수 있습니다."

elif len(swing_scanners) >= 2:
    market_mode = "변동성 장세"
    recommended_scanners = swing_scanners
    position_size = "총 자금의 10%~20%"
    strategy_type = "단타 중심"
    comment = "장중 변동성은 좋지만 종가 확정력은 약할 수 있습니다."

elif len(stable_scanners) >= 1:
    market_mode = "안정형 반등"
    recommended_scanners = stable_scanners
    position_size = "총 자금의 20%"
    strategy_type = "보수적 스윙"
    comment = "안정 종목 중심으로 천천히 대응하는 장세입니다."

else:
    market_mode = "관망 구간"
    recommended_scanners = []
    position_size = "총 자금의 0%~10%"
    strategy_type = "매매 자제"
    comment = "아직 확실한 우위가 없습니다. 관망이 유리합니다."

# =========================================
# 5. 출력
# =========================================
print("\n===== 9.2 자동 전략 추천 =====")
print("시장 상태:", market_mode)
print("추천 스캐너:", ", ".join(recommended_scanners) if recommended_scanners else "없음")
print("권장 비중:", position_size)
print("매매 스타일:", strategy_type)
print("코멘트:", comment)

# =========================================
# 6. 저장
# =========================================
output_file = os.path.join(ANALYSIS_PATH, f"scanner92_strategy_{today_str}.txt")

with open(output_file, "w", encoding="utf-8-sig") as f:
    f.write("스캐너 9.2 자동 전략 추천\n")
    f.write("=" * 40 + "\n")
    f.write(f"기준일자: {today_str}\n")
    f.write(f"시장 상태: {market_mode}\n")
    f.write(f"추천 스캐너: {', '.join(recommended_scanners) if recommended_scanners else '없음'}\n")
    f.write(f"권장 비중: {position_size}\n")
    f.write(f"매매 스타일: {strategy_type}\n")
    f.write(f"코멘트: {comment}\n")

print("\n전략 파일 저장:", output_file)

# =========================================
# 7. 9.3B 연결용 데이터 반환 (추가)
# =========================================
strategy_result = {
    "date": today_str,
    "market_mode": market_mode,
    "recommended_scanners": recommended_scanners,
    "position_size": position_size,
    "strategy_type": strategy_type,
    "comment": comment
}

# 다른 파일에서 import해서 쓸 수 있게 변수 노출
