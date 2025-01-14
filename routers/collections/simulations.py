from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/simulations/fetch")
async def fetch_simulation(request: dict):
    sim_id = request.get("id")
    if not sim_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["simulations"]
    doc = await coll.find_one({"_id": sim_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"simulation": doc}
