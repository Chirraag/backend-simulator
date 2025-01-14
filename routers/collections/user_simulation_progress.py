from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/user-simulation-progress/fetch")
async def fetch_user_sim_progress(request: dict):
    usp_id = request.get("id")
    if not usp_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["userSimulationProgress"]
    doc = await coll.find_one({"_id": usp_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"user_simulation_progress": doc}
