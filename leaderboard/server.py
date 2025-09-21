import asyncio, os, traceback, sys, json
from datetime import datetime
from websockets.server import serve
sys.dont_write_bytecode = True

if not os.path.exists("leaderboard.json"): #create leaderboard file if it doesn't exist
    with open("leaderboard.json","w") as f:
        leaderboard = {"leaderboard": []}
        json.dump(leaderboard, f)

async def handler(websocket):
    try:
        async for message in websocket:
            if message == "get": # getting leaderboard
                with open("leaderboard.json","r") as f:
                    leaderboard = json.load(f)
                print(f"sending leaderboard to client: {leaderboard}")
                await websocket.send(json.dumps(leaderboard)) #send leaderboard to client
                return
            
            elif message == "score": #client wants to send score
                score = json.loads(await websocket.recv()) #receive score data
                name = score["name"]
                score = score["score"]
                try:
                    score = int(score)
                    if score < 0: #negative scores not allowed
                        await websocket.send("err") #tell client to disconnect
                        return
                except:
                    await websocket.send("err") #tell client to disconnect
                    return
                with open("leaderboard.json","r") as f: #load leaderboard
                    leaderboard = json.load(f)
                leaderboard["leaderboard"].append({"name": name, "score": score}) #add new score
                leaderboard["leaderboard"] = sorted(leaderboard["leaderboard"], key=lambda x: x["score"], reverse=True)[:10] #sort and keep top 10 scores
                print(f"updated leaderboard: {leaderboard}")
                with open("leaderboard.json","w") as f: #save updated leaderboard
                    leaderboard = {"leaderboard": leaderboard["leaderboard"]}
                    json.dump(leaderboard, f)
                await websocket.send("ok") #acknowledge receipt of score
                return

            else: #api call not recognized
                print(f"unknown api call: {message} disconnecting client")
                await websocket.send("err") #tell client to disconnect
                return

    except Exception as e: #error handling
        if str(e) != "no close frame received or sent":
            now = datetime.now()
            name = now.strftime("%H_%M_%S")
            print(f"ERROR OCCURED! saved error to logs, {name}")
            with open("logs/"+name+".txt","w") as f: #save log to file
                tb = traceback.format_exc()
                f.write(str(e)+"\n-----traceback-----\n"+str(tb))
        return

async def main():
    print("starting leaderboard server")
    async with serve(handler, "127.0.0.1", 8000):
        await asyncio.Future()  # run forever

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nshutting down server")