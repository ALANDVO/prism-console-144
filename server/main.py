from fastapi import FastAPI
from server.routes import chat

app = FastAPI(title="Prism Console 144", version="0.1.0")
app.include_router(chat.router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "prism-console-144"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
