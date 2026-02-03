import json
import time
import tkinter as tk

root = tk.Tk()
root.title("Leaderboard")
root.geometry("400x600")
tk.Label(root, text="Current Leaderboard", font=("Helvetica", 16)).pack(pady=10)
tk.Label(
    root, text="leaderboard updates every 5 seconds", font=("Helvetica", 16)
).pack(pady=10)

leaderboard_frame = tk.Frame(root)
leaderboard_frame.pack(fill=tk.BOTH, expand=True)


def update_leaderboard(data):
    for widget in leaderboard_frame.winfo_children():
        widget.destroy()

    for index, entry in enumerate(data):
        rank_label = tk.Label(
            leaderboard_frame, text=f"{index + 1}.", font=("Helvetica", 14)
        )
        rank_label.grid(row=index, column=0, padx=10, pady=5, sticky="w")

        name_label = tk.Label(
            leaderboard_frame, text=entry["name"], font=("Helvetica", 14)
        )
        name_label.grid(row=index, column=1, padx=10, pady=5, sticky="w")

        score_label = tk.Label(
            leaderboard_frame, text=str(entry["score"]), font=("Helvetica", 14)
        )
        score_label.grid(row=index, column=2, padx=10, pady=5, sticky="e")


while True:
    with open("leaderboard.json", "r") as f:
        leaderboard = json.load(f)
    update_leaderboard(leaderboard["leaderboard"])
    root.update()
    time.sleep(5)
