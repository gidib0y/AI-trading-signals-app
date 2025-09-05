from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Test App", version="1.0")

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Hello World! App is working!</h1>"

@app.get("/test")
async def test():
    return {"message": "API is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
