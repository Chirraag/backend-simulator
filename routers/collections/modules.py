from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/modules/fetch")
async def fetch_module(request: dict):
    mod_id = request.get("id")
    if not mod_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["modules"]
    doc = await coll.find_one({"_id": mod_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"module": doc}
