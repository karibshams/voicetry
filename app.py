from fastapi import FastAPI

app = FastAPI(
    title="TTS API",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def root():
    return {"status": "API running"}

@app.get("/health")
def health():
    return {"status": "ok"}
