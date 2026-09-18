# 🧠 AI Maze Game

An interactive, AI-assisted maze game built in Python using Turtle Graphics and the A* pathfinding algorithm. Navigate a randomly generated maze with real-time hints, solution visualization, and detailed performance tracking.

## 🎮 Features

- Procedurally generated mazes with difficulty levels: Easy, Medium, Hard
- Player-controlled movement using arrow keys
- A* algorithm for optimal pathfinding
- AI-assisted gameplay with:
  - Real-time hints (`h` key)
  - Toggle solution visualization (`s` key)
- Performance metrics tracking:
  - Move count, path accuracy, reaction time
  - Hints used, solution views
  - Data logged to CSV for analysis

## 📦 Requirements

- Python 3.11 or newer with Tk support
- Standard libraries:
  - `turtle`
  - `random`
  - `heapq`
  - `csv`
  - `datetime`
  - `time`

No third-party packages, API keys, or environment variables are required.
This is a desktop application and needs a graphical display; it is not a
browser-hosted web app.

## 🚀 How to Run

Clone this repository and run the main script:

```bash
git clone https://github.com/KareemN1936/AIMazeGame.git
cd AIMazeGame
python Main.py
```

## ⌨️ Controls

- Arrow keys to move
- `h` – Show next hint (limited uses)
- `s` – Toggle solution path display

## 📊 Data Logging

Gameplay performance is automatically saved to:
- `maze_performance_data.csv` – Session-level statistics
- `maze_move_details.csv` – Move-by-move breakdown

These files are created/updated on each game session.


## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---
