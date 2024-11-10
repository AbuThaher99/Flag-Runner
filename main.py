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
character_image = pygame.image.load("character.png")  # Replace with your character image
character_image = pygame.transform.scale(character_image, (50, 80))
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
questions_per_level = 3  # Change this value if you want more/less questions per level
total_levels = 3  # Adjust this if you add more levels
question, correct_answer, wrong_answers = None, None, None
timer = 10  # Timer for each question

# Country-capital pairs
countries_capitals = [
    ("France", "Paris"),
    ("Germany", "Berlin"),
    ("Japan", "Tokyo"),
    ("Brazil", "Brasilia"),
    ("Australia", "Canberra"),
    ("Canada", "Ottawa"),
    ("India", "New Delhi"),
    ("China", "Beijing"),
    ("Italy", "Rome")
]

# Load Street Segment Images
street_segments = []
answer_options = []

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
    country, capital = random.choice(countries_capitals)
    question = f"  {country}?"
    correct_answer = capital

    # Create random wrong answers
    wrong_answers = random.sample(
        [cap[1] for cap in countries_capitals if cap[1] != capital], 2)

    answer_options[:] = [correct_answer] + wrong_answers
    random.shuffle(answer_options)
    timer = 10  # Reset timer for the new question
    return answer_options


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

    while True:
        screen.fill(WHITE)
        title_text = font.render("Running Capital Quiz Game", True, BLACK)

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
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

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
        screen.fill(WHITE)

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
    # Define button properties for the game over screen
    button_color = GREEN
    button_hover_color = (0, 200, 0)
    button_width = 200
    button_height = 50

    # Button positions
    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 50, button_width,
                                      button_height)
    quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 120, button_width,
                                   button_height)

    # Define the text
    if win:
        game_over_text = font.render("Congratulations, You Won!", True, GREEN)
    else:
        game_over_text = font.render("Game Over!", True, BLACK)
    score_text = font.render(f"Your final score: {score}", True, RED)
    restart_text = font.render("Restart", True, WHITE)
    quit_text = font.render("Quit", True, WHITE)

    while True:
        screen.fill(WHITE)

        # Draw the main text and score
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()

        # Check for button hover
        if restart_button_rect.collidepoint(mouse_pos):
            restart_button_color = button_hover_color
        else:
            restart_button_color = button_color

        if quit_button_rect.collidepoint(mouse_pos):
            quit_button_color = button_hover_color
        else:
            quit_button_color = button_color

        # Draw restart button
        pygame.draw.rect(screen, restart_button_color, restart_button_rect)
        screen.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width()) // 2,
                                   restart_button_rect.y + (
                                               restart_button_rect.height - restart_text.get_height()) // 2))

        # Draw quit button
        pygame.draw.rect(screen, quit_button_color, quit_button_rect)
        screen.blit(quit_text, (quit_button_rect.x + (quit_button_rect.width - quit_text.get_width()) // 2,
                                quit_button_rect.y + (quit_button_rect.height - quit_text.get_height()) // 2))

        pygame.display.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    return True  # Restart the game
                elif quit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()  # Quit the game


# Function to check if player should level up
def level_up():
    global current_level, answered_questions
    if answered_questions >= current_level * questions_per_level:
        if current_level < total_levels:
            current_level += 1
            print(f"Level Up! Now on Level {current_level}")
        else:
            game_over_screen(win=True)
            return True  # Player won
    return False

answer_y_position = 25

def main():
    global score, lives, character_x, character_y, timer, answered_questions, current_level, answer_y_position

    # Initialize game variables
    score = 0
    lives = 3
    answered_questions = 0
    current_level = 1
    timer = 10  # Timer for each question
    answer_y_position = 50  # Initial position for answer options

    answer_positions = [0, SCREEN_WIDTH // 3, 2 * SCREEN_WIDTH // 3]

    generate_question()  # Generate initial question

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

        # Draw street segments with frames from separate videos
        frames = [
            get_video_frame(video_capture_1),  # Left segment
            get_video_frame(video_capture_2),  # Center segment
            get_video_frame(video_capture_3)   # Right segment
        ]

        # Display each frame in the corresponding segment without gaps
        for i, frame in enumerate(frames):
            segment_x = answer_positions[i]
            frame = pygame.transform.scale(frame, (SCREEN_WIDTH // 3 + 1, SCREEN_HEIGHT))  # Add 1 pixel to avoid gaps
            screen.blit(frame, (segment_x, 0))  # Draw each video segment in its exact position

            # Calculate the center for the answer in each segment
            answer_text = font.render(answer_options[i], True, BLACK)
            answer_x = segment_x + (SCREEN_WIDTH // 3 - answer_text.get_width()) // 2  # Center the answer horizontally
            screen.blit(answer_text, (answer_x, answer_y_position))  # Draw the answer text at the current position

        # Display the question following the character
        question_text = font.render(question, True, BLACK)
        screen.blit(question_text, (character_x, character_y - 30))  # Display question above the character

        # Event handling for character movement
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if current_segment == 1:
                        # Move to the left segment (middle -> left)
                        character_x = LEFT_X  # Center of the left segment
                        current_segment = 0
                    elif current_segment == 2:
                        # Move to the middle segment (right -> middle)
                        character_x = MIDDLE_X  # Center of the middle segment
                        current_segment = 1
                elif event.key == pygame.K_RIGHT:
                    if current_segment == 0:
                        # Move to the middle segment (left -> middle)
                        character_x = MIDDLE_X  # Center of the middle segment
                        current_segment = 1
                    elif event.key == pygame.K_RIGHT:
                        if current_segment == 1:
                            # Move to the right segment (middle -> right)
                            character_x = RIGHT_X  # Center of the right segment
                            current_segment = 2

        # Move character up and answers down
        character_y -= character_speed
        answer_y_position += character_speed  # Move answers downward

        # Countdown timer
        timer -= 0.1  # Decrement timer faster for quicker gameplay
        if timer <= 0:
            lives -= 1
            print("Time's up!")
            wrong_sound.play()  # Play wrong sound for time up
            timer = 10  # Reset timer for next question
            character_y = SCREEN_HEIGHT - 150  # Reset character position
            answer_y_position = 50  # Reset answers position

            if lives <= 0:
                if game_over_screen():
                    main()  # Restart the game
                return  # End the game

            generate_question()  # Generate new question

        # Check if character reaches one of the answers
        if character_y <= answer_y_position:  # Assuming answer options are at answer_y_position
            # Determine the selected answer based on character's horizontal position
            selected_index = current_segment  # Current segment corresponds to the answer's index
            selected_answer = answer_options[selected_index]  # Get the selected answer

            # Check if the selected answer is correct
            if selected_answer == correct_answer:
                score += 1
                answered_questions += 1
                correct_sound.play()  # Play correct sound

                # Check if the player should level up
                if level_up():
                    if game_over_screen(win=True):
                        main()  # Restart the game
                    return  # End the game (win)

            else:
                lives -= 1
                wrong_sound.play()  # Play wrong sound for wrong answer

            # Reset the character and answer positions
            character_y = SCREEN_HEIGHT - 150  # Reset character position
            answer_y_position = 50  # Reset answers to starting position

            if lives <= 0:
                if game_over_screen():
                    main()  # Restart the game
                return  # End the game

            generate_question()  # Generate a new question

        # Draw character animation
        screen.blit(character_images[current_character_frame], (character_x, character_y))

        # Render text
        score_text = font.render(f"Score: {score}", True, GREEN)
        level_text = font.render(f"Level: {current_level}", True, GREEN)
        lives_text = font.render(f"Lives: {lives}", True, RED)
        timer_text = font.render(f"Time: {int(timer)}", True, BLACK)

        # Draw score and level
        screen.blit(score_text, (10, 10))  # Score at top left
        screen.blit(level_text, (10 + score_text.get_width() + 10, 10))  # Level beside score

        # Display lives on the right
        screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))  # Lives at top right

        # Center the timer at the top of the screen
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 10))

        pygame.display.update()  # Refresh the screen

        # Frame rate
        pygame.time.delay(50)  # Increase delay for animation speed

    # Release all video captures when the game ends
    video_capture_1.release()
    video_capture_2.release()
    video_capture_3.release()


# Start the game
start_screen()
main()

# Quit Pygame
pygame.quit()
