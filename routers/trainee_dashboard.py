from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()


@router.post("/training-data/fetch")
async def fetch_user_training_stats(request: dict):
  user_id = request.get("id")

  if not user_id:
    raise HTTPException(status_code=400, detail="Missing 'id'")

  users_coll = db["users"]
  user = await users_coll.find_one({"_id": user_id})
  if not user:
    raise HTTPException(status_code=404, detail="User not found")

  division_id = user.get("divisionId")
  department_id = user.get("departmentId")

  assignments_coll = db["assignments"]
  assignments_cursor = assignments_coll.find({
      "assignedItemType":
      "trainingPlan",
      "status":
      "assigned",
      "$or": [{
          "assignedToType": "user",
          "assignedToId": user_id
      }, {
          "assignedToType": "division",
          "assignedToId": division_id
      }, {
          "assignedToType": "department",
          "assignedToId": department_id
      }]
  })

  training_plan_ids = set()
  async for assignment in assignments_cursor:
    training_plan_ids.add(assignment["assignedItemId"])

  training_plans_coll = db["trainingPlans"]
  modules_coll = db["modules"]
  simulations_coll = db["simulations"]
  user_sim_progress_coll = db["userSimulationProgress"]
  sim_attempts_coll = db["simulationAttempts"]

  training_plans_data = []
  total_sims = 0
  total_score = 0
  highest_score = 0

  for tp_id in training_plan_ids:
    plan = await training_plans_coll.find_one({"_id": tp_id})
    if plan:
      plan_data = {
          "training_plan_id": plan["_id"],
          "name": plan.get("name"),
          "modules": []
      }

      module_ids = plan.get("moduleIds", [])
      for module_id in module_ids:
        module = await modules_coll.find_one({"_id": module_id})
        if module:
          module_data = {
              "module_id": module["_id"],
              "name": module.get("name"),
              "simulations": []
          }

          sim_ids = module.get("simulationIds", [])
          for sim_id in sim_ids:
            total_sims += 1
            simulation = await simulations_coll.find_one({"_id": sim_id})
            if simulation:
              sim_progress = await user_sim_progress_coll.find_one({
                  "userId":
                  user_id,
                  "simulationId":
                  sim_id
              })

              sim_data = {
                  "simulation_id": simulation["_id"],
                  "name": simulation.get("name"),
                  "type": simulation.get("type"),
                  "level": simulation.get("level"),
                  "estTime": simulation.get("estTime"),
                  "dueDate": simulation.get("dueDate"),
                  "status": sim_progress.get("status"),
              }

              if sim_progress and sim_progress.get("attemptIds"):
                attempts_cursor = sim_attempts_coll.find({
                    "_id": {
                        "$in": sim_progress["attemptIds"]
                    },
                    "userId": user_id,
                    "simulationId": sim_id
                }).sort("lastAttemptedDate", -1)

                highest_attempt_score = 0
                async for attempt in attempts_cursor:
                  score = attempt.get("scorePercent", 0)
                  highest_attempt_score = max(highest_attempt_score, score)

                total_score += highest_attempt_score
                highest_score = max(highest_score, highest_attempt_score)
                sim_data["highest_attempt_score"] = highest_attempt_score

              module_data["simulations"].append(sim_data)

          plan_data["modules"].append(module_data)

      training_plans_data.append(plan_data)

  computed_training_plans_data = compute_training_plan_stats(
      training_plans_data)
  return computed_training_plans_data


def compute_training_plan_stats(fetched_training_plans_data):
  final_response = {
      "training_plans": [],
      "stats": {
          "simulation_completed": {
              "total_simulations": 0,
              "completed_simulations": 0,
              "percentage": 0
          },
          "timely_completion": {
              "total_simulations": 0,
              "completed_simulations": 0,
              "percentage": 0
          },
          "average_sim_score": 0,
          "highest_sim_score": 0
      }
  }

  total_simulations = 0
  completed_simulations = 0
  timely_simulations = 0
  total_score = 0
  highest_score = 0

  for plan in fetched_training_plans_data:
    plan_id = plan["training_plan_id"]
    plan_name = plan["name"]
    modules = plan["modules"]

    total_modules = len(modules)
    plan_total_simulations = 0
    plan_completed_simulations = 0
    plan_total_est_time = 0
    plan_total_score = 0
    plan_highest_score = 0
    plan_due_date = None
    plan_status = "not_started"
    progress_flag = False

    plan_modules = []

    for module in modules:
      module_id = module["module_id"]
      module_name = module["name"]
      simulations = module["simulations"]

      module_total_simulations = len(simulations)
      module_completed_simulations = 0
      module_total_est_time = 0
      module_total_score = 0
      module_highest_score = 0
      module_due_date = None
      module_status = "not_started"

      module_simulations = []

      for simulation in simulations:
        simulation_status = simulation["status"]
        simulation_score = simulation.get("highest_attempt_score", 0)
        simulation_due_date = simulation["dueDate"]
        simulation_est_time = simulation["estTime"]

        total_simulations += 1
        plan_total_simulations += 1
        module_total_simulations += 1
        module_total_est_time += simulation_est_time
        plan_total_est_time += simulation_est_time
        total_score += simulation_score
        plan_total_score += simulation_score
        module_total_score += simulation_score
        highest_score = max(highest_score, simulation_score)
        plan_highest_score = max(plan_highest_score, simulation_score)
        module_highest_score = max(module_highest_score, simulation_score)

        if simulation_status == "completed":
          completed_simulations += 1
          plan_completed_simulations += 1
          module_completed_simulations += 1
        if simulation_status == "completed" or simulation_status == "overdue":
          timely_simulations += 1

        if simulation_status == "overdue":
          plan_status = "overdue"
          module_status = "overdue"

        if simulation_status == "in_progress":
          progress_flag = True

        if plan_due_date is None or simulation_due_date < plan_due_date:
          plan_due_date = simulation_due_date
        if module_due_date is None or simulation_due_date < module_due_date:
          module_due_date = simulation_due_date

        module_simulations.append(simulation)

      if module_status == "not_started" and (module_completed_simulations > 0
                                             or progress_flag):
        module_status = "in_progress"
      if module_completed_simulations == module_total_simulations:
        module_status = "completed"

      module_avg_score = (module_total_score / module_total_simulations
                          if module_total_simulations > 0 else 0)

      plan_modules.append({
          "id": module_id,
          "name": module_name,
          "total_simulations": module_total_simulations,
          "average_score": module_avg_score,
          "due_date": module_due_date,
          "status": module_status,
          "simulations": module_simulations
      })

    if plan_status == "not_started" and (plan_completed_simulations > 0
                                         or progress_flag):
      plan_status = "in_progress"
    if plan_completed_simulations == plan_total_simulations:
      plan_status = "completed"

    plan_avg_score = (plan_total_score / plan_total_simulations
                      if plan_total_simulations > 0 else 0)

    final_response["training_plans"].append({
        "id":
        plan_id,
        "name":
        plan_name,
        "completion_percentage":
        ((plan_completed_simulations / plan_total_simulations) *
         100 if plan_total_simulations > 0 else 0),
        "total_modules":
        total_modules,
        "total_simulations":
        plan_total_simulations,
        "est_time":
        plan_total_est_time,
        "average_sim_score":
        plan_avg_score,
        "due_date":
        plan_due_date,
        "status":
        plan_status,
        "modules":
        plan_modules
    })

  overall_avg_score = total_score / total_simulations if total_simulations > 0 else 0

  final_response["stats"]["simulation_completed"] = {
      "total_simulations":
      total_simulations,
      "completed_simulations":
      completed_simulations,
      "percentage":
      round(((completed_simulations / total_simulations) *
             100 if total_simulations > 0 else 0), 2)
  }
  final_response["stats"]["timely_completion"] = {
      "total_simulations":
      timely_simulations,
      "completed_simulations":
      completed_simulations,
      "percentage":
      round(((completed_simulations / timely_simulations) *
             100 if timely_simulations > 0 else 0), 2)
  }
  final_response["stats"]["average_sim_score"] = round(overall_avg_score, 2)
  final_response["stats"]["highest_sim_score"] = highest_score

  return final_response
