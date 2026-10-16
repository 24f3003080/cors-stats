import time
import uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-8owh7z.example.com"
EMAIL = "24F3003080@ds.study.iitm.ac.in"   # <-- apna exact email

# 1) CORS guard: sirf ek origin allowed, koi "*" nahi
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# 2) Har response pe 2 headers lagao
# (CORS ke BAAD add kiya hai, isliye ye sabse bahar wala layer hai
#  aur preflight responses pe bhi headers lagenge)
@app.middleware("http")
async def add_custom_headers(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response

# 3) Stats endpoint
@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        nums = [int(v) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values given")

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }