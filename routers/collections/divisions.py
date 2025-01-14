from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/divisions/fetch")
async def fetch_division(request: dict):
    div_id = request.get("id")
    if not div_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["divisions"]
    doc = await coll.find_one({"_id": div_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"division": doc}
