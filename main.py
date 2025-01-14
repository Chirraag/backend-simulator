from fastapi import FastAPI
import uvicorn
from routers.trainee_dashboard import router as trainee_dashboard_router
from routers.playback_data import router as playback_data_router

app = FastAPI()

app.include_router(trainee_dashboard_router)
app.include_router(playback_data_router)


@app.get("/")
async def root():
  return {"message": "Hello from EverAI Simulator Backend"}


if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
