from __future__ import annotations

from datetime import datetime
from typing import Any


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def scanner_descriptions() -> dict[str, dict[str, str]]:
    return {
        "50": {
            "title": "Stable 5.0 (안정형)",
            "subtitle": "안정형 스캐너",
            "description": "상대적으로 안정적인 흐름의 종목을 찾는 스캐너입니다."
        },
        "51": {
            "title": "Swing 5.1 (단타형)",
            "subtitle": "단타형 스캐너",
            "description": "단기 탄력과 스윙 흐름을 함께 보는 스캐너입니다."
        },
        "60": {
            "title": "Force 6.0 (세력포착형)",
            "subtitle": "세력포착형 스캐너",
            "description": "강한 수급과 추세 강화 구간을 포착하는 스캐너입니다."
        },
        "70": {
            "title": "Early 7.0 (세력초기진입포착형)",
            "subtitle": "초기진입 포착형",
            "description": "초기 진입 구간을 빠르게 찾는 스캐너입니다."
        },
        "91": {
            "title": "Tracker 9.1 (후보 종목 추적 시스템)",
            "subtitle": "후보 추적 시스템",
            "description": "후보 종목의 변화를 추적하는 시스템입니다."
        },
        "92": {
            "title": "Strategy 9.2 (자동 매매 전략 추천 시스템)",
            "subtitle": "자동 전략 추천",
            "description": "시장 상태에 맞는 스캐너와 비중을 자동 추천합니다."
        },
        "93b": {
            "title": "Total 9.3B (전체 조건 통합 시스템)",
            "subtitle": "통합 조건 시스템",
            "description": "후보군 전체를 통합 평가해 PASS/WATCH/SKIP으로 나눕니다."
        },
    }


def build_default_payload() -> dict[str, Any]:
    updated = now_text()
    return {
        "updated_at": updated,
        "indexes": {
            "kospi": {"name": "KOSPI", "value": 2718.35, "change_percent": 0.42},
            "kosdaq": {"name": "KOSDAQ", "value": 889.44, "change_percent": -0.31},
        },
        "scanners": {
            "50": {
                "meta": {
                    "key": "50",
                    "title": "Stable 5.0 (안정형)",
                    "description": "상대적으로 안정적인 흐름의 종목을 찾는 스캐너입니다.",
                    "updated_at": updated,
                    "summary_text": "스캐너 5.0 안정형\n" + "=" * 50 + f"\n기준일시: {updated}"
                },
                "result": [
                    {"code": "263750", "name": "펄어비스", "status": "PASS", "market": "KOSDAQ", "current_price": 63960, "change_percent": 1.85},
                    {"code": "085910", "name": "네오티스", "status": "WATCH", "market": "KOSDAQ", "current_price": 4835, "change_percent": -0.62},
                ],
            },
            "51": {
                "meta": {
                    "key": "51",
                    "title": "Swing 5.1 (단타형)",
                    "description": "단기 탄력과 스윙 흐름을 함께 보는 스캐너입니다.",
                    "updated_at": updated,
                    "summary_text": "스캐너 5.1 단타형\n" + "=" * 50 + f"\n기준일시: {updated}"
                },
                "result": [
                    {"code": "001510", "name": "SK증권", "status": "PASS", "market": "KOSPI", "current_price": 1838, "change_percent": 2.10},
                    {"code": "037350", "name": "성도이엔지", "status": "PASS", "market": "KOSDAQ", "current_price": 5290, "change_percent": 0.88},
                ],
            },
            "60": {
                "meta": {
                    "key": "60",
                    "title": "Force 6.0 (세력포착형)",
                    "description": "강한 수급과 추세 강화 구간을 포착하는 스캐너입니다.",
                    "updated_at": updated,
                    "summary_text": "스캐너 6.0 세력포착형\n" + "=" * 50 + f"\n기준일시: {updated}"
                },
                "result": [
                    {"code": "000660", "name": "SK하이닉스", "status": "WATCH", "market": "KOSPI", "current_price": 104332, "change_percent": -0.44},
                ],
            },
            "70": {
                "meta": {
                    "key": "70",
                    "title": "Early 7.0 (세력초기진입포착형)",
                    "description": "초기 진입 구간을 빠르게 찾는 스캐너입니다.",
                    "updated_at": updated,
                    "summary_text": "스캐너 7.0 세력초기진입포착형\n" + "=" * 50 + f"\n기준일시: {updated}"
                },
                "result": [
                    {"code": "006260", "name": "LS", "status": "WATCH", "market": "KOSPI", "current_price": 146200, "change_percent": 1.12},
                ],
            },
            "92": {
                "meta": {
                    "key": "92",
                    "title": "Strategy 9.2 (자동 매매 전략 추천 시스템)",
                    "description": "시장 상태에 맞는 스캐너와 비중을 자동 추천합니다.",
                    "updated_at": updated,
                    "summary_text": "스캐너 9.2 자동 전략 추천\n"
                        + "=" * 50
                        + f"\n기준일시: {updated}\n시장 상태: 안정형 반등\n추천 스캐너: 5.0_stable\n권장 비중: 총 자금의 20%\n매매 스타일: 보수적 스윙\n코멘트: 안정 종목 중심으로 천천히 대응하는 장세입니다."
                },
                "result": [],
                "strategy": {
                    "date": updated,
                    "market_mode": "안정형 반등",
                    "recommended_scanners": ["5.0_stable"],
                    "position_size": "총 자금의 20%",
                    "strategy_type": "보수적 스윙",
                    "comment": "안정 종목 중심으로 천천히 대응하는 장세입니다.",
                }
            },
            "93b": {
                "meta": {
                    "key": "93b",
                    "title": "Total 9.3B (전체 조건 통합 시스템)",
                    "description": "후보군 전체를 통합 평가해 PASS/WATCH/SKIP으로 나눕니다.",
                    "updated_at": updated,
                    "summary_text": "스캐너 9.3B 통합 요약\n"
                        + "=" * 50
                        + f"\n기준일시: {updated}\n전체 후보 수: 251\nPASS 수: 7\nWATCH 수: 70\nSKIP 수: 174"
                },
                "summary": {
                    "date": updated,
                    "total_candidates": 251,
                    "pass_count": 7,
                    "watch_count": 70,
                    "skip_count": 174,
                },
                "result": [
                    {
                        "code": "009450",
                        "name": "경동나비엔",
                        "scanner_type": "5.1_swing",
                        "market": "KOSPI",
                        "current_price": 66800,
                        "change_percent": 1.20,
                        "entry1": 65998.4,
                        "stop": 63176.1,
                        "target1": 70808.0,
                        "rr": 1.70,
                        "status": "PASS",
                        "comment": "보상비 우수, 우선 검토",
                    },
                    {
                        "code": "327260",
                        "name": "RF머트리얼즈",
                        "scanner_type": "5.0_stable",
                        "market": "KOSDAQ",
                        "current_price": 60500,
                        "change_percent": -0.82,
                        "entry1": 59169.0,
                        "stop": 56337.6,
                        "target1": 63827.5,
                        "rr": 1.65,
                        "status": "PASS",
                        "comment": "보상비 우수, 우선 검토",
                    },
                    {
                        "code": "011070",
                        "name": "LG이노텍",
                        "scanner_type": "5.1_swing",
                        "market": "KOSPI",
                        "current_price": 286000,
                        "change_percent": 0.63,
                        "entry1": 278850.0,
                        "stop": 264936.1,
                        "target1": 301730.0,
                        "rr": 1.64,
                        "status": "WATCH",
                        "comment": "보상비 우수, 우선 검토",
                    },
                    {
                        "code": "019210",
                        "name": "와이지-원",
                        "scanner_type": "5.0_stable",
                        "market": "KOSDAQ",
                        "current_price": 12810,
                        "change_percent": -1.14,
                        "entry1": 12489.75,
                        "stop": 11866.54,
                        "target1": 13514.55,
                        "rr": 1.64,
                        "status": "WATCH",
                        "comment": "보상비 우수, 우선 검토",
                    },
                ],
            },
        },
    }
