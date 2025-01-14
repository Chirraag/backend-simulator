from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/attempts/fetch")
async def fetchSimulationsAttempt(request: dict):
    userId = request.get("id")
    if not userId:
        raise HTTPException(status_code=400, detail="Missing 'id'")

    # Reference the collections
    simAttemptsColl = db["simulationAttempts"]
    simulationsColl = db["simulations"]
    modulesColl = db["modules"]
    trainingPlansColl = db["trainingPlans"]

    # 1) Fetch all attempts by this user
    attemptsCursor = simAttemptsColl.find({"userId": userId})

    responseData = []
    async for attemptDoc in attemptsCursor:
        # Basic attempt info
        attemptId = attemptDoc.get("_id")
        simulationId = attemptDoc.get("simulationId")
        score = attemptDoc.get("scorePercent", 0)
        timeTaken = attemptDoc.get("timeTaken", 0)
        attemptType = attemptDoc.get("attemptType", "N/A")
        moduleId = attemptDoc.get("moduleId")
        trainingPlanId = attemptDoc.get("trainingPlanId")

        print(trainingPlanId)

        # 2) Fetch simulation details
        simulation = await simulationsColl.find_one({"_id": simulationId})
        if not simulation:
            # If simulation data not found, skip or handle differently
            continue

        simName = simulation.get("name", "")
        simType = simulation.get("type", "")
        simLevel = simulation.get("level", "")
        simDueDate = simulation.get("dueDate")
        simEstTime = simulation.get("estTime", 0)

        # 3) Fetch module details
        module = await modulesColl.find_one({"_id": moduleId}
                                            ) if moduleId else None
        moduleName = module.get("name", "") if module else ""

        # 4) Fetch training plan name
        trainingPlanName = ""
        trainingPlan = await trainingPlansColl.find_one(
            {"_id": trainingPlanId})
        if trainingPlan:
            trainingPlanName = trainingPlan.get("name", "")

        # Construct the response item in camelCase
        item = {
            "attemptId": str(attemptId),
            "trainingPlan": trainingPlanName,
            "moduleName": moduleName,
            "simId": simulationId,
            "simName": simName,
            "simType": simType,
            "simLevel": simLevel,
            "score": score,
            "timeTaken": timeTaken,
            "dueDate": simDueDate,
            "attemptType": attemptType,
            "estTime": simEstTime,
            "attemptCount": 1  # constant (per your requirement)
        }

        responseData.append(item)

    return {"attempts": responseData}


@router.post("/attempt/fetch")
async def getSimAttemptById(request: dict):

    userId = request.get("userId")
    attemptId = request.get("attemptId")

    if not userId:
        raise HTTPException(status_code=400, detail="Missing 'userId'")
    if not attemptId:
        raise HTTPException(status_code=400, detail="Missing 'attemptId'")

    # Reference the collections
    simAttemptsColl = db["simulationAttempts"]
    simulationsColl = db["simulations"]

    # 1) Fetch the specific attempt for this user + attemptId
    attemptDoc = await simAttemptsColl.find_one({
        "_id": attemptId,
        "userId": userId
    })
    if not attemptDoc:
        raise HTTPException(
            status_code=404,
            detail=
            f"No attempt found with attemptId={attemptId} for userId={userId}")

    # 2) Extract necessary fields from the attempt document
    simulationId = attemptDoc.get("simulationId")
    print("simId: ", simulationId)
    analytics = attemptDoc.get("analytics", {})
    playback = attemptDoc.get("playback", {})

    # sentencewiseAnalytics, audioUrl, transcript
    sentencewiseAnalytics = playback.get("sentencewiseAnalytics", [])
    audioUrl = playback.get("audioUrl", "")
    transcript = playback.get("transcript", "")

    # transcriptObject is now an array
    transcriptObject = playback.get("transcriptObject", [])

    # timeTakenSeconds
    timeTakenSeconds = attemptDoc.get("timeTakenSeconds", 0)

    # Pull out scores from analytics
    clickScore = analytics.get("clickScore", 0)
    textFieldKeywordScore = analytics.get("textFieldKeywordScore", 0)
    keywordScore = analytics.get("keywordScore", 0)
    simAccuracyScore = analytics.get("simAccuracyScore", 0)
    confidence = analytics.get("confidence", 0)
    energy = analytics.get("energy", 0)
    concentration = analytics.get("concentration", 0)

    # 3) Look up simulation doc to get minPassingScore
    simulation = await simulationsColl.find_one({"_id": simulationId})
    if not simulation:
        raise HTTPException(
            status_code=404,
            detail=f"No simulation found for simulationId={simulationId}")

    minPassingScore = simulation.get("minPassingScore", 0)

    # 4) Construct the single response object in camelCase
    responseItem = {
        "sentencewiseAnalytics": sentencewiseAnalytics,
        "audioUrl": audioUrl,
        "transcript": transcript,
        "transcriptObject": transcriptObject,
        "timeTakenSeconds": timeTakenSeconds,
        "clickScore": clickScore,
        "textFieldKeywordScore": textFieldKeywordScore,
        "keywordScore": keywordScore,
        "simAccuracyScore": simAccuracyScore,
        "confidence": confidence,
        "energy": energy,
        "concentration": concentration,
        "minPassingScore": minPassingScore
    }

    return {"attempt": responseItem}
