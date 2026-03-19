from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS (모바일/웹 접속 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 서버 상태 확인용
@app.get("/")
def home():
    return {"message": "scanner server running"}

# -----------------------------
# SCANNERS
# -----------------------------

@app.get("/scan/50")
def scan_50():
    return {
        "scanner": "5.0_stable",
        "result": [
            {"code": "263750", "name": "펄어비스", "status": "PASS"},
            {"code": "85910", "name": "네오티스", "status": "WATCH"}
        ]
    }

@app.get("/scan/51")
def scan_51():
    return {
        "scanner": "5.1_swing",
        "result": [
            {"code": "1510", "name": "SK증권", "status": "PASS"},
            {"code": "37350", "name": "성도이엔지", "status": "PASS"}
        ]
    }

@app.get("/scan/60")
def scan_60():
    return {
        "scanner": "6.0_force",
        "result": [
            {"code": "660", "name": "SK하이닉스", "status": "WATCH"}
        ]
    }

@app.get("/scan/70")
def scan_70():
    return {
        "scanner": "7.0_early",
        "result": [
            {"code": "6260", "name": "LS", "status": "WATCH"}
        ]
    }

@app.get("/scan/92")
def scan_92():
    return {
        "date": "20260318",
        "market_mode": "강세 확산형",
        "recommended_scanners": ["5.0_stable", "5.1_swing", "6.0_force", "7.0_early"],
        "position_size": "총 자금의 30%~40%",
        "strategy_type": "단타 + 스윙 병행",
        "comment": "여러 스캐너가 동시에 강합니다. 시장이 상승장 초입일 가능성이 큽니다."
    }

@app.get("/scan/93b")
def scan_93b():
    return {
        "scanner": "9.3B",
        "result": [
            {
                "code": "1510",
                "name": "SK증권",
                "entry1": 1838.64,
                "stop": 1750.66,
                "target": 1983.40,
                "rr": 1.65,
                "status": "PASS"
            },
            {
                "code": "263750",
                "name": "펄어비스",
                "entry1": 63960.00,
                "stop": 60768.56,
                "target": 69208.00,
                "rr": 1.64,
                "status": "PASS"
            },
            {
                "code": "660",
                "name": "SK하이닉스",
                "entry1": 1043328.00,
                "stop": 998712.00,
                "target": 1119360.00,
                "rr": 1.70,
                "status": "WATCH"
            }
        ]
    }

# ✅ Render용 (중요)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)