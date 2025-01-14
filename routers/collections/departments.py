from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/departments/fetch")
async def fetch_department(request: dict):
    dept_id = request.get("id")
    if not dept_id:
        raise HTTPException(status_code=400, detail="Missing 'id'")
    coll = db["departments"]
    doc = await coll.find_one({"_id": dept_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"department": doc}
