from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/organisations/fetch")
async def fetch_organisation(request: dict):
    org_id = request.get("id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["organisations"]
    doc = await coll.find_one({"_id": org_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"organisation": doc}
