import os
import pandas as pd
import numpy as np
from datetime import datetime
from path_config import OUTPUT_STABLE_DIR, OUTPUT_SWING_DIR, OUTPUT_60_DIR, OUTPUT_70_DIR, ANALYSIS_DIR

print("스캐너 9.3B 통합 시작 - final 우선 / 없으면 all 대체 / 엔트리 계산")

# =========================================
# 0. 기본 설정
# =========================================
today_str = datetime.today().strftime("%Y%m%d")

PATHS = {
    "5.0_stable": {
        "final": str(OUTPUT_STABLE_DIR / f"scanner5_final_{today_str}.csv"),
        "all": str(OUTPUT_STABLE_DIR / f"scanner5_all_{today_str}.csv"),
    },
    "5.1_swing": {
        "final": str(OUTPUT_SWING_DIR / f"scanner51_final_{today_str}.csv"),
        "all": str(OUTPUT_SWING_DIR / f"scanner51_all_{today_str}.csv"),
    },
    "6.0_force": {
        "final": str(OUTPUT_60_DIR / f"scanner60_final_{today_str}.csv"),
        "all": str(OUTPUT_60_DIR / f"scanner60_all_{today_str}.csv"),
    },
    "7.0_early": {
        "final": str(OUTPUT_70_DIR / f"scanner70_final_{today_str}.csv"),
        "all": str(OUTPUT_70_DIR / f"scanner70_all_{today_str}.csv"),
    },
}

ANALYSIS_PATH = str(ANALYSIS_DIR)
os.makedirs(ANALYSIS_PATH, exist_ok=True)


# =========================================
# 1. CSV 안전 로드
# =========================================
def load_csv_safe(path):
    if not os.path.exists(path):
        print(f"[로드 실패] 파일 없음: {path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        print(f"[로드 성공] {path} / 행수: {len(df)}")
        return df
    except pd.errors.EmptyDataError:
        print(f"[로드 실패] {path} / 오류: No columns to parse from file")
        return pd.DataFrame()
    except Exception as e:
        print(f"[로드 실패] {path} / 오류: {e}")
        return pd.DataFrame()


# =========================================
# 2. 스캐너 파일 로드
# final 우선 / 비면 all 대체
# =========================================
def load_scanner_candidates():
    print("\n[1단계] 스캐너 파일 로드 시작")

    loaded = {}

    for scan_tag, path_info in PATHS.items():
        final_df = load_csv_safe(path_info["final"])

        if final_df.empty:
            print(f"[{scan_tag}] final 비어 있음 -> all 파일 대체 시도")
            all_df = load_csv_safe(path_info["all"])

            if all_df.empty:
                print(f"[{scan_tag}] all도 비어 있음")
                loaded[scan_tag] = pd.DataFrame()
            else:
                all_df = all_df.copy()
                all_df["candidate_source"] = "all_fallback"
                loaded[scan_tag] = all_df
                print(f"[{scan_tag}] all 사용")
        else:
            final_df = final_df.copy()
            final_df["candidate_source"] = "final"
            loaded[scan_tag] = final_df
            print(f"[{scan_tag}] final 사용")

    print("\n[로드 결과]")
    for k, v in loaded.items():
        print(f" - {k}: {len(v)}개")

    return loaded


# =========================================
# 3. 컬럼 표준화
# =========================================
def normalize_scanner_df(df, scan_tag):
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "code", "name", "close",
            "차트점수", "5일변화율(%)", "20일변화율(%)", "거래대금(원)",
            "20일선위", "60일선위", "거래량증가", "고점근접", "양봉마감", "상단압박",
            "scan_tag", "candidate_source"
        ])

    df = df.copy()

    def pick_col(possible_cols):
        for c in possible_cols:
            if c in df.columns:
                return c
        return None

    col_code = pick_col(["종목코드", "code", "ticker", "symbol"])
    col_name = pick_col(["종목명", "name", "company"])
    col_close = pick_col(["현재가", "close", "종가", "price"])
    col_score = pick_col(["차트점수", "score"])
    col_ch5 = pick_col(["5일변화율(%)", "5일변화율"])
    col_ch20 = pick_col(["20일변화율(%)", "20일변화율"])
    col_amount = pick_col(["거래대금(원)", "거래대금"])
    col_ma20 = pick_col(["20일선위"])
    col_ma60 = pick_col(["60일선위"])
    col_vol = pick_col(["거래량증가"])
    col_high = pick_col(["고점근접"])
    col_bull = pick_col(["양봉마감"])
    col_pressure = pick_col(["상단압박"])
    col_source = pick_col(["candidate_source"])

    out = pd.DataFrame()
    out["code"] = df[col_code] if col_code else np.nan
    out["name"] = df[col_name] if col_name else np.nan
    out["close"] = df[col_close] if col_close else np.nan
    out["차트점수"] = df[col_score] if col_score else 0
    out["5일변화율(%)"] = df[col_ch5] if col_ch5 else 0
    out["20일변화율(%)"] = df[col_ch20] if col_ch20 else 0
    out["거래대금(원)"] = df[col_amount] if col_amount else 0
    out["20일선위"] = df[col_ma20] if col_ma20 else 0
    out["60일선위"] = df[col_ma60] if col_ma60 else 0
    out["거래량증가"] = df[col_vol] if col_vol else 0
    out["고점근접"] = df[col_high] if col_high else 0
    out["양봉마감"] = df[col_bull] if col_bull else 0
    out["상단압박"] = df[col_pressure] if col_pressure else 0
    out["scan_tag"] = scan_tag
    out["candidate_source"] = df[col_source] if col_source else "unknown"

    numeric_cols = [
        "close", "차트점수", "5일변화율(%)", "20일변화율(%)", "거래대금(원)",
        "20일선위", "60일선위", "거래량증가", "고점근접", "양봉마감", "상단압박"
    ]

    for c in numeric_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out[out["code"].notna()].copy()
    out = out[out["name"].notna()].copy()

    return out


# =========================================
# 4. 9.25 후보 종목 통합
# =========================================
def build_entry_candidates(loaded_dict):
    print("\n[2단계] 9.25 후보 종목 통합 시작")

    frames = []

    for scan_tag in ["5.0_stable", "5.1_swing", "6.0_force", "7.0_early"]:
        df = loaded_dict.get(scan_tag, pd.DataFrame())
        normalized = normalize_scanner_df(df, scan_tag)
        print(f"[{scan_tag}] 표준화 후 후보 수: {len(normalized)}")
        frames.append(normalized)

    merged = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    if merged.empty:
        print("[9.25] 통합 결과: 후보 없음")
        return merged

    before_code = len(merged)
    merged = merged[merged["code"].notna()].copy()
    print(f"[9.25] code 없는 행 제거: {before_code - len(merged)}개")

    merged["code"] = merged["code"].astype(str).str.replace(".0", "", regex=False).str.strip()

    before_dup = len(merged)

    priority_map = {
        "5.0_stable": 4,
        "5.1_swing": 3,
        "6.0_force": 2,
        "7.0_early": 1
    }
    merged["scan_priority"] = merged["scan_tag"].map(priority_map).fillna(0)

    merged["차트점수"] = merged["차트점수"].fillna(0)
    merged = merged.sort_values(
        by=["code", "차트점수", "scan_priority"],
        ascending=[True, False, False]
    ).reset_index(drop=True)

    merged = merged.drop_duplicates(subset=["code"], keep="first").reset_index(drop=True)
    print(f"[9.25] 중복 제거: {before_dup - len(merged)}개")
    print(f"[9.25] 최종 통합 후보 수: {len(merged)}개")

    preview_cols = ["code", "name", "close", "scan_tag", "candidate_source", "차트점수"]
    print("\n[9.25] 후보 미리보기")
    print(merged[preview_cols].head(20).to_string(index=False))

    return merged


# =========================================
# 5. 9.3B 엔트리 계산
# =========================================
def run_scanner_93b(candidates_df):
    print("\n[3단계] 스캐너 9.3B 시작 - 보완형 매수 타이밍 계산기")
    print("후보 종목 불러오는 중...")

    if candidates_df is None or len(candidates_df) == 0:
        print("[9.3B] 계산할 종목이 없습니다.")
        return pd.DataFrame()

    work_df = candidates_df.copy()

    num_cols = [
        "close", "차트점수", "5일변화율(%)", "20일변화율(%)", "거래대금(원)",
        "20일선위", "60일선위", "거래량증가", "고점근접", "양봉마감", "상단압박"
    ]
    for c in num_cols:
        if c in work_df.columns:
            work_df[c] = pd.to_numeric(work_df[c], errors="coerce").fillna(0)

    def calc_entry(row):
        close = float(row["close"]) if pd.notna(row["close"]) else 0.0
        if close <= 0:
            return pd.Series({
                "entry1": None,
                "entry2": None,
                "stop_calc": None,
                "target1": None,
                "target2": None,
                "risk": None,
                "rr": None,
                "entry_gap_pct": None,
                "entry_status": "SKIP",
                "entry_comment": "가격 데이터 없음"
            })

        score = float(row.get("차트점수", 0))
        change5 = float(row.get("5일변화율(%)", 0))
        change20 = float(row.get("20일변화율(%)", 0))
        amount = float(row.get("거래대금(원)", 0))
        ma20 = float(row.get("20일선위", 0))
        ma60 = float(row.get("60일선위", 0))
        vol_up = float(row.get("거래량증가", 0))
        near_high = float(row.get("고점근접", 0))
        bullish = float(row.get("양봉마감", 0))
        pressure = float(row.get("상단압박", 0))

        # 엔트리 계산
        if near_high >= 1 and pressure == 0:
            entry1 = close * 0.988
            entry2 = close * 0.975
        elif change5 >= 5:
            entry1 = close * 0.975
            entry2 = close * 0.955
        elif change20 >= 15:
            entry1 = close * 0.978
            entry2 = close * 0.960
        else:
            entry1 = close * 0.985
            entry2 = close * 0.970

        stop_calc = entry2 * 0.970

        if near_high >= 1 and pressure == 0:
            target1 = close * 1.060
            target2 = close * 1.120
        elif change20 >= 15:
            target1 = close * 1.055
            target2 = close * 1.100
        else:
            target1 = close * 1.045
            target2 = close * 1.090

        risk = entry1 - stop_calc
        if risk <= 0:
            return pd.Series({
                "entry1": None,
                "entry2": None,
                "stop_calc": None,
                "target1": None,
                "target2": None,
                "risk": None,
                "rr": None,
                "entry_gap_pct": None,
                "entry_status": "SKIP",
                "entry_comment": "위험 계산 오류"
            })

        rr = (target1 - entry1) / risk
        entry_gap_pct = ((close - entry1) / close) * 100.0

        # 상태 분류
        reasons = []

        # 차트점수는 현재 10점 기준
        if score < 7:
            reasons.append("차트점수 낮음")

        if pressure >= 1:
            reasons.append("상단압박 있음")

        if amount < 500000000:
            reasons.append("거래대금 부족")

        if ma20 < 0:
            reasons.append("20일선 아래")

        if ma60 < 0:
            reasons.append("60일선 아래")

        if entry_gap_pct > 6:
            reasons.append("진입가 괴리 큼")

        if bullish < 1:
            reasons.append("양봉마감 아님")

        if len(reasons) > 0:
            status = "SKIP"
            comment = ", ".join(reasons)
        else:
            if rr >= 1.6 and vol_up >= 1:
                status = "PASS"
                comment = "보상비 우수, 우선 검토"
            elif rr >= 1.2:
                status = "WATCH"
                comment = "관찰 필요"
            else:
                status = "SKIP"
                comment = "보상비 부족"

        return pd.Series({
            "entry1": round(entry1, 2),
            "entry2": round(entry2, 2),
            "stop_calc": round(stop_calc, 2),
            "target1": round(target1, 2),
            "target2": round(target2, 2),
            "risk": round(risk, 2),
            "rr": round(rr, 2),
            "entry_gap_pct": round(entry_gap_pct, 2),
            "entry_status": status,
            "entry_comment": comment
        })

    result_calc = work_df.apply(calc_entry, axis=1)
    result_df = pd.concat([work_df.reset_index(drop=True), result_calc.reset_index(drop=True)], axis=1)

    status_order = {"PASS": 0, "WATCH": 1, "SKIP": 2}
    result_df["status_order"] = result_df["entry_status"].map(status_order).fillna(9)

    result_df = result_df.sort_values(
        by=["status_order", "rr", "차트점수", "거래대금(원)"],
        ascending=[True, False, False, False]
    ).reset_index(drop=True)

    print(f"[9.3B] 입력 후보 수: {len(work_df)}")
    print(f"[9.3B] 계산 완료 / 결과 수: {len(result_df)}개")

    show_cols = [
        "code", "name", "scan_tag", "candidate_source", "close",
        "차트점수", "5일변화율(%)", "20일변화율(%)", "거래대금(원)",
        "entry1", "entry2", "stop_calc", "target1", "target2",
        "risk", "rr", "entry_gap_pct", "entry_status", "entry_comment"
    ]

    pass_df = result_df[result_df["entry_status"] == "PASS"].copy()
    watch_df = result_df[result_df["entry_status"] == "WATCH"].copy()

    print("\n[상위 PASS 20개]")
    if len(pass_df) == 0:
        print("PASS 종목 없음")
    else:
        print(pass_df[show_cols].head(20).to_string(index=False))

    print("\n[상위 WATCH 20개]")
    if len(watch_df) == 0:
        print("WATCH 종목 없음")
    else:
        print(watch_df[show_cols].head(20).to_string(index=False))

    return result_df


# =========================================
# 6. 저장
# =========================================
def save_results(candidates_df, entry_df):
    candidates_file = os.path.join(ANALYSIS_PATH, f"scanner925_candidates_{today_str}.csv")
    entry_file = os.path.join(ANALYSIS_PATH, f"scanner93b_entry_{today_str}.csv")
    pass_file = os.path.join(ANALYSIS_PATH, f"scanner93b_pass_{today_str}.csv")
    watch_file = os.path.join(ANALYSIS_PATH, f"scanner93b_watch_{today_str}.csv")
    summary_file = os.path.join(ANALYSIS_PATH, f"scanner93b_summary_{today_str}.txt")

    if candidates_df is not None and not candidates_df.empty:
        candidates_df.to_csv(candidates_file, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame().to_csv(candidates_file, index=False, encoding="utf-8-sig")

    if entry_df is not None and not entry_df.empty:
        entry_df.to_csv(entry_file, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame().to_csv(entry_file, index=False, encoding="utf-8-sig")

    if entry_df is not None and not entry_df.empty:
        pass_df = entry_df[entry_df["entry_status"] == "PASS"].copy()
        watch_df = entry_df[entry_df["entry_status"] == "WATCH"].copy()
    else:
        pass_df = pd.DataFrame()
        watch_df = pd.DataFrame()

    pass_df.to_csv(pass_file, index=False, encoding="utf-8-sig")
    watch_df.to_csv(watch_file, index=False, encoding="utf-8-sig")

    total_count = len(entry_df) if entry_df is not None else 0
    pass_count = len(pass_df)
    watch_count = len(watch_df)
    skip_count = len(entry_df[entry_df["entry_status"] == "SKIP"]) if entry_df is not None and not entry_df.empty else 0

    with open(summary_file, "w", encoding="utf-8-sig") as f:
        f.write("스캐너 9.3B 통합 요약\n")
        f.write("=" * 50 + "\n")
        f.write(f"기준일자: {today_str}\n")
        f.write(f"전체 후보 수: {total_count}\n")
        f.write(f"PASS 수: {pass_count}\n")
        f.write(f"WATCH 수: {watch_count}\n")
        f.write(f"SKIP 수: {skip_count}\n\n")

        f.write("[상위 PASS 20개]\n")
        if len(pass_df) == 0:
            f.write("PASS 종목 없음\n")
        else:
            for _, row in pass_df.head(20).iterrows():
                f.write(
                    f"{row['code']} / {row['name']} / {row['scan_tag']} / "
                    f"현재가:{row['close']} / 진입1:{row['entry1']} / 손절:{row['stop_calc']} / "
                    f"목표1:{row['target1']} / RR:{row['rr']} / 코멘트:{row['entry_comment']}\n"
                )

        f.write("\n[상위 WATCH 20개]\n")
        if len(watch_df) == 0:
            f.write("WATCH 종목 없음\n")
        else:
            for _, row in watch_df.head(20).iterrows():
                f.write(
                    f"{row['code']} / {row['name']} / {row['scan_tag']} / "
                    f"현재가:{row['close']} / 진입1:{row['entry1']} / 손절:{row['stop_calc']} / "
                    f"목표1:{row['target1']} / RR:{row['rr']} / 코멘트:{row['entry_comment']}\n"
                )

    print("\n[4단계] 저장 완료")
    print(f"통합 후보 저장: {candidates_file}")
    print(f"엔트리 결과 저장: {entry_file}")
    print(f"PASS 전용 저장: {pass_file}")
    print(f"WATCH 전용 저장: {watch_file}")
    print(f"요약 저장: {summary_file}")


# =========================================
# 7. 메인 실행
# =========================================
def main():
    loaded = load_scanner_candidates()
    candidates_df = build_entry_candidates(loaded)
    entry_df = run_scanner_93b(candidates_df)
    save_results(candidates_df, entry_df)

    print("\n실행 완료")
    print(" - final 파일이 있으면 final 사용")
    print(" - final 파일이 비면 all 파일 자동 대체")
    print(" - 9.25 통합 후 9.3B 계산")
    print(" - PASS / WATCH 전용 파일도 저장")


if __name__ == "__main__":
    main()
