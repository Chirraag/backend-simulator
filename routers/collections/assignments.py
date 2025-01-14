from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/assignments/fetch")
async def fetch_assignment(request: dict):
    assign_id = request.get("id")
    if not assign_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["assignments"]
    doc = await coll.find_one({"_id": assign_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"assignment": doc}
