import pygame
import random
import sys
import cv2

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
sound_enabled = True
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Running Capital Quiz Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
CRIMSON = (220, 20, 60)
DARK_GRAY = (64, 64, 64)

# Load Fonts
font = pygame.font.Font(None, 36)

# Load Sound Effects
correct_sound = pygame.mixer.Sound("correct.mp3")
wrong_sound = pygame.mixer.Sound("wrong.mp3")

# Load Background Music
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)  # Set volume for background music
pygame.mixer.music.play(-1)  # Play music in an infinite loop

# Load Character Images for Animation
character_image = pygame.image.load("chr.png")  # Replace with your character image
character_image = pygame.transform.scale(character_image, (400, 200))
character_images = [character_image]  # You can add more frames for animation
current_character_frame = 0

# Initial Character Position
character_x = SCREEN_WIDTH // 2 - 25
character_y = SCREEN_HEIGHT - 150
character_speed = 4  # Increased speed to make the game faster

# Game Variables
score = 0
lives = 3
answered_questions = 0
current_level = 1
questions_per_level = 5  # Number of questions per level
level_questions = {}  # Dictionary to store unique questions for each level
correct_answers = 0  # Tracks the number of correct answers per level
paused = False  # Tracks whether the game is paused


question, correct_answer, wrong_answers = None, None, None
timer = 10  # Timer for each question

# Country-capital pairs
# Expanded country-capital pairs for more levels
countries_capitals = [
    ("France", "Paris"),
    ("Germany", "Berlin"),
    ("Japan", "Tokyo"),
    ("Brazil", "Brasilia"),
    ("Australia", "Canberra"),
    ("Canada", "Ottawa"),
    ("India", "New Delhi"),
    ("China", "Beijing"),
    ("Italy", "Rome"),
    ("South Korea", "Seoul"),
    ("Spain", "Madrid"),
    ("United States", "Washington, D.C."),
    ("Russia", "Moscow"),
    ("South Africa", "Pretoria"),
    ("Mexico", "Mexico City"),
    ("Egypt", "Cairo"),
    ("Argentina", "Buenos Aires"),
    ("Turkey", "Ankara"),
    ("Saudi Arabia", "Riyadh"),
    ("Thailand", "Bangkok"),
    ("Vietnam", "Hanoi"),
    ("Malaysia", "Kuala Lumpur"),
    ("Singapore", "Singapore"),
    ("Netherlands", "Amsterdam"),
    ("Belgium", "Brussels"),
    ("Sweden", "Stockholm"),
    ("Norway", "Oslo"),
    ("Denmark", "Copenhagen"),
    ("Finland", "Helsinki"),
    ("Poland", "Warsaw"),
    ("Greece", "Athens"),
    ("Portugal", "Lisbon"),
    ("New Zealand", "Wellington"),
    ("Switzerland", "Bern"),
    ("Austria", "Vienna"),
    ("Ireland", "Dublin"),
    ("Palestine", "Jerusalem"),
    ("Czech Republic", "Prague"),
    ("Hungary", "Budapest"),
    ("Pakistan", "Islamabad"),
    ("Bangladesh", "Dhaka"),
    ("Sri Lanka", "Colombo"),
    ("Nigeria", "Abuja"),
    ("Kenya", "Nairobi"),
    ("Tanzania", "Dodoma"),
    ("Chile", "Santiago"),
    ("Colombia", "Bogotá"),
    ("Peru", "Lima"),
    ("Venezuela", "Caracas")
]
level_questions = {
    1: [("Sri Lanka", "Colombo"), ("Mexico", "Mexico City"), ("Saudi Arabia", "Riyadh"),
        ("Denmark", "Copenhagen"), ("Austria", "Vienna")],
    2: [("Ireland", "Dublin"), ("Turkey", "Ankara"), ("Japan", "Tokyo"),
        ("South Africa", "Pretoria"), ("United States", "Washington, D.C.")],
    3: [("Czech Republic", "Prague"), ("Colombia", "Bogotá"), ("Thailand", "Bangkok"),
        ("Vietnam", "Hanoi"), ("Venezuela", "Caracas")],
    4: [("Tanzania", "Dodoma"), ("Germany", "Berlin"), ("Norway", "Oslo"),
        ("Egypt", "Cairo"), ("Argentina", "Buenos Aires")],
    5: [("Sweden", "Stockholm"), ("Chile", "Santiago"), ("Peru", "Lima"),
        ("Finland", "Helsinki"), ("South Korea", "Seoul")],
    6: [("Belgium", "Brussels"), ("Bangladesh", "Dhaka"), ("Portugal", "Lisbon"),
        ("Spain", "Madrid"), ("Nigeria", "Abuja")],
    7: [("Kenya", "Nairobi"), ("Palestine", "Jerusalem"), ("France", "Paris"),
        ("Singapore", "Singapore"), ("Poland", "Warsaw")],
    8: [("China", "Beijing"), ("Pakistan", "Islamabad"), ("Malaysia", "Kuala Lumpur"),
        ("Canada", "Ottawa"), ("Netherlands", "Amsterdam")],
    9: [("Greece", "Athens"), ("Australia", "Canberra"), ("Switzerland", "Bern"),
        ("Italy", "Rome"), ("Hungary", "Budapest")]
}


total_levels = len(countries_capitals) // questions_per_level  # Automatically calculate total levels
original_level_questions = {
    level: questions[:] for level, questions in level_questions.items()
}
# Load Street Segment Images
street_segments = []
answer_options = []
missed_question = None

video_capture_1 = cv2.VideoCapture("left (online-video-cutter.com).mp4")  # Replace with your first video file for left segment
video_capture_2 = cv2.VideoCapture("mid (online-video-cutter.com).mp4")  # Replace with your second video file for center segment
video_capture_3 = cv2.VideoCapture("right (online-video-cutter.com).mp4")  # Replace with your third video file for right segment

# Function to get the next frame from the video
def get_video_frame(video_capture):
    ret, frame = video_capture.read()
    if not ret:
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
        ret, frame = video_capture.read()

    # Resize and convert the frame for Pygame display
    frame = cv2.resize(frame, (SCREEN_WIDTH // 3, SCREEN_HEIGHT))  # Scale to exact third of the screen
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))  # Convert to Pygame surface
    return frame


# Function to generate a question
def generate_question():
    global question, correct_answer, wrong_answers, timer

    # Repeat missed question if one exists
    if missed_question:
        question, correct_answer = missed_question
    else:
        # Check if there are questions left for the current level
        if current_level not in level_questions or not level_questions[current_level]:
            question, correct_answer = None, None  # No more questions
            return None

        # Get the next question from the current level's question pool
        question_data = level_questions[current_level].pop(0)
        question, correct_answer = question_data

    # Generate wrong answers
    wrong_answers = random.sample(
        [cap[1] for cap in sum(level_questions.values(), []) if cap[1] != correct_answer], 2
    )
    answer_options[:] = [correct_answer] + wrong_answers
    random.shuffle(answer_options)
    timer = 10  # Reset timer for the new question
    return answer_options








def generate_level_questions():
    global level_questions
    questions_per_level = 5  # Ensure each level gets exactly 5 questions
    shuffled_questions = random.sample(countries_capitals, len(countries_capitals))

    # Split questions evenly across levels
    level_questions.clear()
    for level in range(1, total_levels + 1):
        start_index = (level - 1) * questions_per_level
        end_index = start_index + questions_per_level
        level_questions[level] = shuffled_questions[start_index:end_index]

    print("Generated questions for each level:")
    for level, questions in level_questions.items():
        print(f"Level {level}: {questions}")


# Function to display start screen
def start_screen():
    # Define button properties
    button_color = GREEN
    button_hover_color = (0, 200, 0)  # Slightly darker green when hovered
    button_width = 150
    button_height = 50

    # Button positions
    start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2, button_width,
                                    button_height)
    quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height + 20,
                                   button_width, button_height)
    settings_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2,
                                       SCREEN_HEIGHT // 2 + (button_height + 20) * 2, button_width, button_height)

    # Button texts
    start_button_text = font.render("Start", True, WHITE)
    quit_button_text = font.render("Quit", True, WHITE)
    settings_button_text = font.render("Settings", True, WHITE)

    # Larger font for the title
    title_font = pygame.font.Font(None, 72)  # Adjust font size for the title
    title_text = title_font.render("Running Capital Quiz Game", True, WHITE)

    while True:
        # Draw background
        screen.fill((30, 30, 60))  # Dark blue background

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Check if mouse is over buttons
        if start_button_rect.collidepoint(mouse_pos):
            start_button_color = button_hover_color
        else:
            start_button_color = button_color

        if quit_button_rect.collidepoint(mouse_pos):
            quit_button_color = button_hover_color
        else:
            quit_button_color = button_color

        if settings_button_rect.collidepoint(mouse_pos):
            settings_button_color = button_hover_color
        else:
            settings_button_color = button_color

        # Draw title
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))

        # Draw start button
        pygame.draw.rect(screen, start_button_color, start_button_rect)
        screen.blit(start_button_text,
                    (start_button_rect.x + (start_button_rect.width - start_button_text.get_width()) // 2,
                     start_button_rect.y + (start_button_rect.height - start_button_text.get_height()) // 2))

        # Draw quit button
        pygame.draw.rect(screen, quit_button_color, quit_button_rect)
        screen.blit(quit_button_text,
                    (quit_button_rect.x + (quit_button_rect.width - quit_button_text.get_width()) // 2,
                     quit_button_rect.y + (quit_button_rect.height - quit_button_text.get_height()) // 2))

        # Draw settings button
        pygame.draw.rect(screen, settings_button_color, settings_button_rect)
        screen.blit(settings_button_text,
                    (settings_button_rect.x + (settings_button_rect.width - settings_button_text.get_width()) // 2,
                     settings_button_rect.y + (settings_button_rect.height - settings_button_text.get_height()) // 2))

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    return  # Start the game if start button is clicked
                elif quit_button_rect.collidepoint(event.pos):
                    pygame.quit()  # Quit the game if quit button is clicked
                    sys.exit()
                elif settings_button_rect.collidepoint(event.pos):
                    settings_screen()  # Go to the settings screen if settings button is clicked



def settings_screen():
    # Declare sound_enabled as global at the beginning of the function
    global sound_enabled

    # Define button properties for the settings screen
    button_color = GREEN
    button_hover_color = (0, 200, 0)
    button_width = 200
    button_height = 50

    # Button positions
    toggle_sound_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2, button_width,
                                           button_height)
    back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height + 20,
                                   button_width, button_height)

    # Initial text and button color
    sound_status_text = font.render(f"Sound: {'On' if sound_enabled else 'Off'}", True, WHITE)
    back_button_text = font.render("Back", True, WHITE)

    while True:
        screen.fill((30, 30, 60))  # Dark blue background

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Check if mouse is over buttons
        if toggle_sound_button_rect.collidepoint(mouse_pos):
            toggle_sound_button_color = button_hover_color
        else:
            toggle_sound_button_color = button_color

        if back_button_rect.collidepoint(mouse_pos):
            back_button_color = button_hover_color
        else:
            back_button_color = button_color

        # Draw sound status
        screen.blit(sound_status_text,
                    (SCREEN_WIDTH // 2 - sound_status_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        # Draw toggle sound button
        pygame.draw.rect(screen, toggle_sound_button_color, toggle_sound_button_rect)
        screen.blit(sound_status_text,
                    (toggle_sound_button_rect.x + (toggle_sound_button_rect.width - sound_status_text.get_width()) // 2,
                     toggle_sound_button_rect.y + (
                             toggle_sound_button_rect.height - sound_status_text.get_height()) // 2))

        # Draw back button
        pygame.draw.rect(screen, back_button_color, back_button_rect)
        screen.blit(back_button_text,
                    (back_button_rect.x + (back_button_rect.width - back_button_text.get_width()) // 2,
                     back_button_rect.y + (back_button_rect.height - back_button_text.get_height()) // 2))

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if toggle_sound_button_rect.collidepoint(event.pos):
                    # Toggle the sound status when the button is clicked
                    sound_enabled = not sound_enabled

                    # Change sound text based on the new state
                    sound_status_text = font.render(f"Sound: {'On' if sound_enabled else 'Off'}", True, WHITE)

                    # Toggle the sound
                    if sound_enabled:
                        pygame.mixer.music.unpause()  # Resume background music
                    else:
                        pygame.mixer.music.pause()  # Pause background music

                elif back_button_rect.collidepoint(event.pos):
                    return  # Go back to the start screen



# Function to display game over screen
def game_over_screen(win=False):
    button_color = GREEN
    button_hover_color = (0, 200, 0)
    button_width = 200
    button_height = 50

    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 50, button_width, button_height)
    quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 120, button_width, button_height)

    if win:
        game_over_text = font.render("Congratulations, You Won!", True, GREEN)
        restart_label = "Back to Levels"
    else:
        game_over_text = font.render("Game Over!", True, RED)
        restart_label = "Restart"

    score_text = font.render(f"Your final score: {score}", True, RED)
    restart_text = font.render(restart_label, True, WHITE)
    quit_text = font.render("Quit", True, WHITE)

    while True:
        screen.fill((30, 30, 60))  # Dark blue background
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))

        mouse_pos = pygame.mouse.get_pos()

        # Highlight buttons on hover
        restart_button_color = button_hover_color if restart_button_rect.collidepoint(mouse_pos) else button_color
        quit_button_color = button_hover_color if quit_button_rect.collidepoint(mouse_pos) else button_color

        pygame.draw.rect(screen, restart_button_color, restart_button_rect)
        screen.blit(restart_text, (restart_button_rect.x + (button_width - restart_text.get_width()) // 2,
                                   restart_button_rect.y + (button_height - restart_text.get_height()) // 2))

        pygame.draw.rect(screen, quit_button_color, quit_button_rect)
        screen.blit(quit_text, (quit_button_rect.x + (button_width - quit_text.get_width()) // 2,
                                quit_button_rect.y + (button_height - quit_text.get_height()) // 2))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    if win:
                        return "levels"  # Go back to the level selection screen
                    else:
                        return "restart"  # Restart the current level
                elif quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()




# Function to check if player should level up
def level_up():
    global current_level, answered_questions, missed_question

    if answered_questions >= questions_per_level and not missed_question:
        if current_level < len(level_questions):
            current_level += 1
            answered_questions = 0
            missed_question = None
            print(f"Level {current_level} unlocked! Transitioning to level selection.")
            return "level_selection"
        else:
            print("All levels completed!")
            return "win"
    return None



# Function to display level selection screen
def level_selection_screen():
    global current_level

    # Define button properties
    button_radius = 40  # Radius of the circular level buttons
    padding = 60  # Space between buttons
    rows = 2  # Number of rows for level buttons
    cols = 5  # Number of columns for level buttons

    # Load lock icon
    lock_icon = pygame.image.load("lock_icon.png")  # Replace with your lock icon path
    lock_icon = pygame.transform.scale(lock_icon, (button_radius * 2, button_radius * 2))

    unlocked_levels = [True if i < current_level else False for i in range(len(level_questions))]

    while True:
        # Fill background with a solid color
        screen.fill((30, 30, 60))  # Dark blue background

        # Draw title
        title_font = pygame.font.Font(None, 72)  # Larger custom font for the title
        title_text = title_font.render("Select Level", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        # Center the grid of buttons
        total_width = cols * (button_radius * 2 + padding) - padding
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 150

        # Draw buttons for each level
        for i in range(len(level_questions)):
            col = i % cols
            row = i // cols

            x = start_x + col * (button_radius * 2 + padding)
            y = start_y + row * (button_radius * 2 + padding)

            # Draw a circular button
            center = (x + button_radius, y + button_radius)
            color = GREEN if unlocked_levels[i] else DARK_GRAY

            # Highlight button on hover
            if pygame.Rect(center[0] - button_radius, center[1] - button_radius, button_radius * 2,
                           button_radius * 2).collidepoint(pygame.mouse.get_pos()):
                if unlocked_levels[i]:
                    color = (0, 200, 0)  # Slightly darker green for unlocked levels
                else:
                    color = CRIMSON  # Highlight locked button in red

            pygame.draw.circle(screen, color, center, button_radius)

            if unlocked_levels[i]:
                # Draw the level number for unlocked levels
                level_text = font.render(f"{i + 1}", True, WHITE)
                screen.blit(level_text, (
                    center[0] - level_text.get_width() // 2,
                    center[1] - level_text.get_height() // 2
                ))
            else:
                # Draw the lock icon for locked levels
                screen.blit(lock_icon, (center[0] - lock_icon.get_width() // 2, center[1] - lock_icon.get_height() // 2))

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(level_questions)):
                    col = i % cols
                    row = i // cols

                    x = start_x + col * (button_radius * 2 + padding)
                    y = start_y + row * (button_radius * 2 + padding)

                    center = (x + button_radius, y + button_radius)
                    level_button_rect = pygame.Rect(
                        center[0] - button_radius, center[1] - button_radius, button_radius * 2, button_radius * 2
                    )

                    if level_button_rect.collidepoint(event.pos) and unlocked_levels[i]:
                        current_level = i + 1
                        print(f"Starting Level {current_level}")
                        return






def restart_level():
    global level_questions, missed_question, answered_questions
    missed_question = None
    answered_questions = 0
    level_questions = {level: questions[:] for level, questions in original_level_questions.items()}
    main()



answer_y_position = 25

def main():
    global score, lives, character_x, character_y, timer, answered_questions, correct_answers, current_level, answer_y_position, missed_question, paused

    if current_level not in level_questions or not level_questions[current_level]:
        print(f"No questions left for level {current_level}. Returning to level selection.")
        return  # Go back to level selection

    # Initialize game variables
    score = 0
    lives = 3
    answered_questions = 0
    correct_answers = 0  # Reset correct answers for the level
    timer = 10
    answer_y_position = 50
    missed_question = None  # Reset missed question
    generate_question()  # Generate the first question
    paused = False

    # Define segment positions for easier tracking
    LEFT_X = SCREEN_WIDTH // 6  # Left segment center
    MIDDLE_X = SCREEN_WIDTH // 2  # Center segment center
    RIGHT_X = 5 * SCREEN_WIDTH // 6  # Right segment center

    # Initialize current segment (0 = left, 1 = middle, 2 = right)
    current_segment = 1  # Start in the middle segment
    character_x = MIDDLE_X  # Start character in the center
    character_y = SCREEN_HEIGHT - 150  # Start at the bottom

    # Game loop
    while True:
        screen.fill(WHITE)  # Clear the screen

        if correct_answers >= 5:  # Check if the player has answered 5 questions correctly
            print(f"Level {current_level} completed! Moving to the next level.")
            result = level_up()
            if result == "level_selection":
                return  # Exit to level selection screen
            elif result == "win":
                if game_over_screen(win=True) == "levels":
                    return  # Go back to level selection
                else:
                    sys.exit()  # Exit the game

            if not level_questions[current_level] and not missed_question:
                print(f"No questions left for level {current_level}. Returning to level selection.")
                return  # Transition to level selection

        if question is None:
            generate_question()
            continue

        # Draw street segments with frames from separate videos
        if not paused:
            # Draw street segments with frames from separate videos
            frames = [
                get_video_frame(video_capture_1),  # Left segment
                get_video_frame(video_capture_2),  # Center segment
                get_video_frame(video_capture_3)  # Right segment
            ]
        # Display each frame in the corresponding segment
        for i, frame in enumerate(frames):
            segment_x = [LEFT_X, MIDDLE_X, RIGHT_X][i]
            frame = pygame.transform.scale(frame, (SCREEN_WIDTH // 3 + 1, SCREEN_HEIGHT))
            screen.blit(frame, (segment_x - SCREEN_WIDTH // 6, 0))  # Draw each video segment

        # Display answer options
        for i, option in enumerate(answer_options):
            segment_x = [LEFT_X, MIDDLE_X, RIGHT_X][i]
            answer_text = font.render(option, True, BLACK)
            answer_x = segment_x - answer_text.get_width() // 2  # Center the answer horizontally
            screen.blit(answer_text, (answer_x, answer_y_position))  # Draw the answer text

        # Display the question above the character
        if question:
            question_text = font.render(question, True, BLACK)
            screen.blit(question_text, (character_x - question_text.get_width() // 2, character_y - 50))
        else:
            print("No question to display.")  # Debugging output

        # Draw the character
        screen.blit(character_image, (character_x - character_image.get_width() // 2, character_y))

        # Draw Pause Button (always under the score)
        pause_button_rect = pygame.Rect(10, 80, 120, 40)  # Position: Below the score
        pygame.draw.rect(screen, (0, 0, 255), pause_button_rect)  # Blue background for the button
        pause_text = font.render("Pause" if not paused else "Resume", True, WHITE)  # Button label
        screen.blit(pause_text, (pause_button_rect.x + (pause_button_rect.width - pause_text.get_width()) // 2,
                                 pause_button_rect.y + (pause_button_rect.height - pause_text.get_height()) // 2))

        # Handle Pause Logic
        if paused:
            pause_message = font.render("Game Paused", True, (0, 0, 0))  # Black text
            screen.blit(pause_message, (SCREEN_WIDTH // 2 - pause_message.get_width() // 2, 20))  # Top center

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_button_rect.collidepoint(event.pos):
                        paused = False  # Resume the game
            continue  # Skip game updates while paused

        # Event handling for character movement and answer selection
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button_rect.collidepoint(event.pos):  # Pause button clicked
                    paused = True  # Toggle pause state
                    continue  # Skip further event handling
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if current_segment > 0:  # Move to the left segment
                        current_segment -= 1
                        character_x = [LEFT_X, MIDDLE_X, RIGHT_X][current_segment]
                elif event.key == pygame.K_RIGHT:
                    if current_segment < 2:  # Move to the right segment
                        current_segment += 1
                        character_x = [LEFT_X, MIDDLE_X, RIGHT_X][current_segment]

        # Countdown timer
        timer -= 0.1
        if timer <= 0:  # Handle timeout
            if missed_question is None:  # Only decrement lives if it's not already a repeated question
                lives -= 1
                print(f"Time's up! Missed question: {question}")
                wrong_sound.play()  # Play wrong sound for time up
                missed_question = (question, correct_answer)  # Store the missed question for repeating
            timer = 10  # Reset timer

            if lives <= 0:  # Check for game over
                result = game_over_screen(win=False)
                if result == "restart":
                    restart_level()
                elif result == "levels":
                    return
            continue  # Skip to the next iteration to handle the missed question again

        if character_y <= answer_y_position:  # Check if the character reached the answers
            selected_answer = answer_options[current_segment]
            answered_questions += 1  # Increment answered questions count
            if selected_answer == correct_answer:  # Correct answer logic
                score += 1
                correct_answers += 1  # Increment correct answers count
                print(f"Correct! Answered: {correct_answer}")
                correct_sound.play()  # Play correct sound for a correct answer
                missed_question = None  # Clear missed question if answered correctly
            else:  # Incorrect answer logic
                if missed_question is None:  # Only decrement lives if it's not already a repeated question
                    lives -= 1
                    print(f"Wrong answer! Correct answer was: {correct_answer}")
                    missed_question = (question, correct_answer)  # Store the missed question
                    wrong_sound.play()

                if lives <= 0:  # Handle game over
                    result = game_over_screen(win=False)
                    if result == "restart":
                        restart_level()
                    elif result == "levels":
                        return

            # Reset positions for the next question
            character_y = SCREEN_HEIGHT - 150  # Reset character position
            answer_y_position = 50  # Reset answers to starting position

            if lives <= 0:
                if game_over_screen():
                    main()  # Restart the game
                return  # End the game

            generate_question()  # Generate the next question

        # Move character up and answers down
        character_y -= character_speed
        answer_y_position += character_speed

        # Use a more elegant font style if supported
        score_text = font.render(f"Score: {score}", True, GOLD)
        level_text = font.render(f"Level: {current_level}", True, LIGHT_BLUE)
        lives_text = font.render(f"Lives: {lives}", True, CRIMSON)
        timer_text = font.render(f"Time: {int(timer)}", True, DARK_GRAY)

        # Optionally, add a subtle shadow effect for depth
        shadow_offset = 2
        score_shadow = font.render(f"Score: {score}", True, DARK_GRAY)
        level_shadow = font.render(f"Level: {current_level}", True, DARK_GRAY)
        lives_shadow = font.render(f"Lives: {lives}", True, DARK_GRAY)
        timer_shadow = font.render(f"Time: {int(timer)}", True, DARK_GRAY)

        # Blit the shadow first for a shadow effect
        screen.blit(score_shadow, (10 + shadow_offset, 10 + shadow_offset))
        screen.blit(level_shadow, (10 + shadow_offset, 50 + shadow_offset))
        screen.blit(lives_shadow, (SCREEN_WIDTH - 150 + shadow_offset, 10 + shadow_offset))
        screen.blit(timer_shadow, (SCREEN_WIDTH // 2 - 50 + shadow_offset, 10 + shadow_offset))

        # Then blit the actual text
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - 50, 10))

        pygame.display.update()  # Refresh the screen
        pygame.time.delay(50)  # Frame delay for smooth animation

    # Release video captures when the game ends
    video_capture_1.release()
    video_capture_2.release()
    video_capture_3.release()



# Start the game
start_screen()
while True:
    level_selection_screen()
    generate_level_questions()
    main()

# Quit Pygame
pygame.quit()
