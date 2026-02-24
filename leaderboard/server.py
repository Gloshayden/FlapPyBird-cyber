import json
import os
import sys
import traceback
from datetime import datetime
from fastapi import FastAPI, HTTPException

sys.dont_write_bytecode = True
app = FastAPI()

if not os.path.exists(
    "leaderboard.json"
):  # create leaderboard file if it doesn't exist
    with open("leaderboard.json", "w") as f:
        leaderboard = {"leaderboard": []}
        json.dump(leaderboard, f)


@app.get("/get")
async def getLeaderboard():
    with open("leaderboard.json", "r") as f:
        leaderboard = json.load(f)
    print(f"sending leaderboard to client: {leaderboard}")
    return json.dumps(leaderboard)  # send leaderboard to client


@app.patch("/score")
async def newScore(data: dict):
    name = data["name"]
    score = data["score"]
    try:
        score = int(score)
        if score < 0:
            raise HTTPException(
                status_code=406, detail="Score was a negitive int"
            )  # negative scores not allowed
    except ValueError:
        raise HTTPException(status_code=406, detail="Score wasnt an int")
    with open("leaderboard.json", "r") as f:  # load leaderboard
        leaderboard = json.load(f)
    leaderboard["leaderboard"].append({"name": name, "score": score})  # add new score
    leaderboard["leaderboard"] = sorted(
        leaderboard["leaderboard"],
        key=lambda x: x["score"],
        reverse=True,
    )[:10]  # sort and keep top 10 scores
    print(f"updated leaderboard: {leaderboard}")
    with open("leaderboard.json", "w") as f:  # save updated leaderboard
        leaderboard = {"leaderboard": leaderboard["leaderboard"]}
        json.dump(leaderboard, f)
    return {"message": "Score uploaded to server"}
