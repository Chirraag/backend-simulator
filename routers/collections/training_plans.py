from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/training-plans/fetch")
async def fetch_training_plan(request: dict):
    tp_id = request.get("id")
    if not tp_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["trainingPlans"]
    doc = await coll.find_one({"_id": tp_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"training_plan": doc}
