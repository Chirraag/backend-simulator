from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/users/fetch")
async def fetch_user(request: dict):
    user_id = request.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["users"]
    doc = await coll.find_one({"_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"user": doc}
