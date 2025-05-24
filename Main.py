import turtle
import random
import time
import heapq
import pandas as pd
import datetime

# Game settings
DIFFICULTY = {
    "easy": {"width": 10, "height": 10},
    "medium": {"width": 20, "height": 20},
    "hard": {"width": 30, "height": 30}
}
CELL_SIZE = 20
PLAYER_COLOR = "green"
EXIT_COLOR = "red"
PATH_COLOR = "blue"
HINT_COLOR = "gold"

# Set up the screen
screen = turtle.Screen()
screen.title("AI Maze Game")
screen.bgcolor("white")
screen.tracer(0)

# Set up all the turtles we need
pen = turtle.Turtle()
pen.hideturtle()
pen.penup()
pen.speed(0)

player = turtle.Turtle()
player.shape("turtle")
player.color(PLAYER_COLOR)
player.penup()
player.speed(0)

timer = turtle.Turtle()
timer.hideturtle()
timer.penup()
timer.speed(0)

path_turtle = turtle.Turtle()
path_turtle.hideturtle()
path_turtle.penup()
path_turtle.color(PATH_COLOR)
path_turtle.speed(0)

hint_turtle = turtle.Turtle()
hint_turtle.hideturtle()
hint_turtle.penup()
hint_turtle.color(HINT_COLOR)
hint_turtle.speed(0)

message_turtle = turtle.Turtle()
message_turtle.hideturtle()
message_turtle.penup()
message_turtle.speed(0)

# Ask player for name and difficulty
player_name = screen.textinput("Player Name", "Enter your name:")
if not player_name:
    player_name = "Player"

difficulty = screen.textinput("Difficulty", "Choose difficulty (easy, medium, hard):").lower()
if difficulty not in DIFFICULTY:
    difficulty = "medium"

# Set maze dimensions
MAZE_WIDTH = DIFFICULTY[difficulty]["width"]
MAZE_HEIGHT = DIFFICULTY[difficulty]["height"]
screen.setup(MAZE_WIDTH * CELL_SIZE + 250, MAZE_HEIGHT * CELL_SIZE + 150)

# Create the maze grid (1 = wall, 0 = path)
maze = [[1 for i in range(MAZE_WIDTH)] for i in range(MAZE_HEIGHT)]

solution_path = []
hints_remaining = 3
show_full_solution = False

# Performance data tracking
move_count = 0
correct_moves = 0
hint_uses = 0
solution_views = 0
game_start_time = None
move_timestamps = []
moves_on_path = []
reaction_times = []
session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_maze():
    stack = [(0, 0)]
    maze[0][0] = 0

    while stack:
        x, y = stack[-1]

        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and maze[ny][nx] == 1:
                neighbors.append((nx, ny, dx, dy))

        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[y + dy][x + dx] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()


# A* pathfinding algorithm
def find_path(start, end):
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        x, y = current
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor

            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and maze[ny][nx] == 0:
                tentative_g = g_score.get(current, float('inf')) + 1

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)

                    if all(neighbor != pos for _, pos in open_set):
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None


# Calculate heuristic (Manhattan distance)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Show the AI solution path
def draw_solution():
    global solution_views
    solution_views += 1  # Track when solution is viewed

    if solution_path:
        path_turtle.clear()
        path_turtle.pensize(3)

        x, y = solution_path[0]
        screen_x = (x - MAZE_WIDTH / 2) * CELL_SIZE + CELL_SIZE / 2
        screen_y = (MAZE_HEIGHT / 2 - y) * CELL_SIZE - CELL_SIZE / 2
        path_turtle.goto(screen_x, screen_y)
        path_turtle.pendown()

        for x, y in solution_path[1:]:
            screen_x = (x - MAZE_WIDTH / 2) * CELL_SIZE + CELL_SIZE / 2
            screen_y = (MAZE_HEIGHT / 2 - y) * CELL_SIZE - CELL_SIZE / 2
            path_turtle.goto(screen_x, screen_y)

        path_turtle.penup()
        screen.update()


# Show a hint - the next step on the path
def show_hint():
    global hints_remaining, hint_uses

    if hints_remaining > 0 and solution_path:
        hint_uses += 1

        # Get player position
        px = int((player.xcor() + MAZE_WIDTH * CELL_SIZE / 2) // CELL_SIZE)
        py = int((MAZE_HEIGHT * CELL_SIZE / 2 - player.ycor()) // CELL_SIZE)

        # Find where to go next
        next_x, next_y = solution_path[0]

        # If player is on path, show next step
        for i in range(len(solution_path) - 1):
            if (px, py) == solution_path[i]:
                next_x, next_y = solution_path[i + 1]
                break

        # Show the hint
        screen_x = (next_x - MAZE_WIDTH / 2) * CELL_SIZE + CELL_SIZE / 2
        screen_y = (MAZE_HEIGHT / 2 - next_y) * CELL_SIZE - CELL_SIZE / 2

        hint_turtle.clear()
        hint_turtle.goto(screen_x, screen_y)
        hint_turtle.dot(CELL_SIZE // 3, HINT_COLOR)

        hints_remaining -= 1
        show_message(f"Hints: {hints_remaining}")

    elif hints_remaining <= 0:
        show_message("No hints!")

    screen.update()


# Toggle showing or hiding the solution
def toggle_solution():
    global show_full_solution
    show_full_solution = not show_full_solution

    if show_full_solution:
        draw_solution()
        show_message("Solution shown!")
    else:
        path_turtle.clear()
        show_message("Solution hidden")
    screen.update()


# Show a message on screen
def show_message(msg, duration=2):
    message_turtle.clear()
    message_turtle.goto(0, -MAZE_HEIGHT * CELL_SIZE / 2 - 40)
    message_turtle.write(msg, align = "center", font = ("Arial", 12, "normal"))
    screen.update()
    screen.ontimer(message_turtle.clear, duration * 1000)


# Draw the maze walls
def draw_maze():
    pen.color("black")
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 1:
                screen_x = x * CELL_SIZE - MAZE_WIDTH * CELL_SIZE / 2
                screen_y = MAZE_HEIGHT * CELL_SIZE / 2 - y * CELL_SIZE
                pen.goto(screen_x, screen_y)
                pen.pendown()
                pen.begin_fill()
                for i in range(4):
                    pen.forward(CELL_SIZE)
                    pen.right(90)
                pen.end_fill()
                pen.penup()

    # Draw border
    pen.pensize(2)
    pen.goto(-MAZE_WIDTH * CELL_SIZE / 2, MAZE_HEIGHT * CELL_SIZE / 2)
    pen.pendown()
    for i in range(2):
        pen.forward(MAZE_WIDTH * CELL_SIZE)
        pen.right(90)
        pen.forward(MAZE_HEIGHT * CELL_SIZE)
        pen.right(90)
    pen.penup()

    screen.update()


# Create exit point
def create_exit():
    start_x, start_y = 0, 0

    path_cells = [(x, y) for y in range(MAZE_HEIGHT) for x in range(MAZE_WIDTH)
                  if maze[y][x] == 0 and (x != start_x or y != start_y)]

    far_cells = [(x, y) for x, y in path_cells if abs(x - start_x) + abs(y - start_y) >= 5]

    if far_cells:
        end_x, end_y = random.choice(far_cells)
    else:
        end_x, end_y = random.choice(path_cells)

    pen.goto(end_x * CELL_SIZE - MAZE_WIDTH * CELL_SIZE / 2 + CELL_SIZE / 2,
             MAZE_HEIGHT * CELL_SIZE / 2 - end_y * CELL_SIZE - CELL_SIZE / 2)
    pen.dot(CELL_SIZE // 2, EXIT_COLOR)

    return end_x, end_y


# Move the player
def move_player(dx, dy):
    global move_count, correct_moves, last_move_time, move_timestamps, moves_on_path, reaction_times

    if game_over:
        return

    # Get current position
    x = int((player.xcor() + MAZE_WIDTH * CELL_SIZE / 2) // CELL_SIZE)
    y = int((MAZE_HEIGHT * CELL_SIZE / 2 - player.ycor()) // CELL_SIZE)
    new_x, new_y = x + dx, y + dy

    # Check if move is valid
    if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and maze[new_y][new_x] == 0:
        move_count += 1
        current_time = time.time()
        move_timestamps.append(current_time)

        # Calculate reaction time (time since last move)
        if move_count > 1:
            reaction_time = current_time - move_timestamps[-2]
            reaction_times.append(reaction_time)

        # Check if move is on optimal path
        is_on_path = False
        for i in range(len(solution_path) - 1):
            if (x, y) == solution_path[i] and (new_x, new_y) == solution_path[i + 1]:
                is_on_path = True
                correct_moves += 1
                break

        # Record if move was on path
        moves_on_path.append(is_on_path)

        # Move player
        player.goto((new_x - MAZE_WIDTH / 2) * CELL_SIZE + CELL_SIZE / 2,
                    (MAZE_HEIGHT / 2 - new_y) * CELL_SIZE - CELL_SIZE / 2)
        screen.update()

        # Check if reached exit
        if new_x == exit_x and new_y == exit_y:
            end_game(True)


# End the game
def end_game(won):
    global game_over
    game_over = True

    # Calculate final performance metrics
    completion_time = time.time() - game_start_time
    path_accuracy = (correct_moves / move_count) * 100 if move_count > 0 else 0
    avg_reaction_time = sum(reaction_times) / len(reaction_times) if reaction_times else 0

    # Save performance data
    save_performance_data(won, completion_time, path_accuracy, avg_reaction_time)

    # Display game results
    screen.clear()
    screen.bgcolor("white")
    pen.goto(0, 50)

    if won:
        remaining_time = max(0, 30 - int(completion_time))
        pen.write(f"You Win!\nTime Remaining: {remaining_time} seconds",
                  align="center", font=("Arial", 24, "normal"))

        # Show performance stats
        pen.goto(0, -50)
        pen.write(f"Moves: {move_count} | Path Accuracy: {path_accuracy:.1f}%\n"
                  f"Average Reaction Time: {avg_reaction_time:.2f} seconds\n"
                  f"Hints Used: {hint_uses}",
                  align="center", font=("Arial", 16, "normal"))
    else:
        pen.write("Time's Up!\nYou Lose!", align="center", font=("Arial", 24, "normal"))

    screen.update()


# Update the timer
def update_timer():
    if not game_over:
        elapsed_time = int(time.time() - game_start_time)
        remaining_time = max(0, 30 - elapsed_time)

        timer.clear()
        timer.goto(0, MAZE_HEIGHT * CELL_SIZE / 2 + 20)
        timer.write(f"Time: {remaining_time} seconds | Hints: {hints_remaining}",
                    align="center", font=("Arial", 16, "normal"))

        if remaining_time > 0:
            screen.ontimer(update_timer, 1000)
        else:
            end_game(False)


# Set up keyboard controls
def setup_controls():
    key_states = {"Up": False, "Down": False, "Left": False, "Right": False}

    def key_press(key):
        key_states[key] = True

    def key_release(key):
        key_states[key] = False

    # Set up arrow keys
    screen.onkeypress(lambda: key_press("Up"), "Up")
    screen.onkeypress(lambda: key_press("Down"), "Down")
    screen.onkeypress(lambda: key_press("Left"), "Left")
    screen.onkeypress(lambda: key_press("Right"), "Right")

    screen.onkeyrelease(lambda: key_release("Up"), "Up")
    screen.onkeyrelease(lambda: key_release("Down"), "Down")
    screen.onkeyrelease(lambda: key_release("Left"), "Left")
    screen.onkeyrelease(lambda: key_release("Right"), "Right")

    # AI helper keys
    screen.onkey(show_hint, "h")
    screen.onkey(toggle_solution, "s")

    # Check for movement
    def check_movement():
        if not game_over:
            if key_states["Up"]: move_player(0, -1)
            if key_states["Down"]: move_player(0, 1)
            if key_states["Left"]: move_player(-1, 0)
            if key_states["Right"]: move_player(1, 0)

            screen.ontimer(check_movement, 100)

    screen.listen()
    check_movement()


# Show controls info
def display_info():
    info_turtle = turtle.Turtle()
    info_turtle.hideturtle()
    info_turtle.penup()
    info_turtle.speed(0)

    info_turtle.goto(0, -MAZE_HEIGHT * CELL_SIZE / 2 - 20)
    info_turtle.write("Press 'h' for hint | Press 's' to show/hide solution",
                      align="center", font=("Arial", 12, "normal"))
    screen.update()


# Calculate the solution using A*
def calculate_solution_path():
    global solution_path
    start = (0, 0)
    end = (exit_x, exit_y)

    solution_path = find_path(start, end)

    if solution_path:
        print(f"Solution found! Path length: {len(solution_path)}")
    else:
        print("No solution found!")


# Save performance data to CSV
def save_performance_data(won, completion_time, path_accuracy, avg_reaction_time):
    # Create a dictionary with all performance metrics
    performance_data = {
        'session_id': [session_id],
        'player_name': [player_name],
        'difficulty': [difficulty],
        'completed': [won],
        'completion_time': [completion_time],
        'total_moves': [move_count],
        'correct_moves': [correct_moves],
        'path_accuracy': [path_accuracy],
        'avg_reaction_time': [avg_reaction_time],
        'hints_used': [hint_uses],
        'solution_views': [solution_views],
        'optimal_path_length': [len(solution_path) if solution_path else 0],
        'timestamp': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    }

    # Create DataFrame
    df = pd.DataFrame(performance_data)

    try:
        # Try to read existing data file
        existing_df = pd.read_csv('maze_performance_data.csv')
        # Append new data
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_csv('maze_performance_data.csv', index=False)
    except:
        # If file doesn't exist, create new one
        df.to_csv('maze_performance_data.csv', index=False)

    print(f"Performance data saved for {player_name}")

    # Also save detailed move data for analysis
    move_details = {
        'session_id': [session_id] * len(moves_on_path),
        'move_number': list(range(1, len(moves_on_path) + 1)),
        'on_optimal_path': moves_on_path,
        'timestamp': move_timestamps[:len(moves_on_path)],
        'reaction_time': reaction_times + [0]  # Add padding for first move
    }

    # Create DataFrame for move details
    moves_df = pd.DataFrame(move_details)

    try:
        # Try to read existing move data file
        existing_moves_df = pd.read_csv('maze_move_details.csv')
        # Append new data
        updated_moves_df = pd.concat([existing_moves_df, moves_df], ignore_index=True)
        updated_moves_df.to_csv('maze_move_details.csv', index=False)
    except:
        # If file doesn't exist, create new one
        moves_df.to_csv('maze_move_details.csv', index=False)


# MAIN PROGRAM STARTS HERE

# Initialize game
game_over = False
screen.listen()

# Create and draw the maze
generate_maze()
draw_maze()

# Put player at start
player.goto(-MAZE_WIDTH * CELL_SIZE / 2 + CELL_SIZE / 2,
            MAZE_HEIGHT * CELL_SIZE / 2 - CELL_SIZE / 2)
screen.update()

# Create exit
exit_x, exit_y = create_exit()
screen.update()

# Find solution path with AI
calculate_solution_path()

# Show controls info
display_info()

# Set up keyboard controls
setup_controls()

# Start the timer and game
game_start_time = time.time()
last_move_time = game_start_time
update_timer()

# Welcome message
show_message(f"Welcome {player_name}! Use arrow keys to move. Press 'h' for hint, 's' to see solution.", 4)

# Start the game loop
turtle.mainloop()