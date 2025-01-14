from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/simulation-attempts/fetch")
async def fetch_simulation_attempt(request: dict):
    attempt_id = request.get("id")
    if not attempt_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["simulationAttempts"]
    doc = await coll.find_one({"_id": attempt_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"simulation_attempt": doc}
