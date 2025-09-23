import pygame
import random
import math

# Calculate dx, dy from speed and angle
def get_ball_velocity(speed, angle, direction):
    dx = speed * math.cos(angle) * direction
    dy = speed * math.sin(angle)
    return dx, dy

pygame.init()

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
SCORE_MAX = 2

size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("MyPong - PyGame Edition - 2024-09-02")

# Score text
score_font = pygame.font.Font('assets/PressStart2P.ttf', 44)
score_text = score_font.render('00 x 00', True, COLOR_WHITE, COLOR_BLACK)
score_text_rect = score_text.get_rect(center=(680, 50))

# Victory text
victory_font = pygame.font.Font('assets/PressStart2P.ttf', 100)
victory_player1_text = victory_font.render('Player 1 Wins!', True, COLOR_WHITE, COLOR_BLACK)
victory_player2_text = victory_font.render('Player 2 Wins!', True, COLOR_WHITE, COLOR_BLACK)
victory_player1_text_rect = victory_player1_text.get_rect(center=(640, 350))  # Center of screen
victory_player2_text_rect = victory_player2_text.get_rect(center=(640, 350))  # Center of screen

# Sound effects
bounce_sound_effect = pygame.mixer.Sound('assets/bounce.wav')
scoring_sound_effect = pygame.mixer.Sound('assets/258020__kodack__arcade-bleep-sound.wav')

# Player 1
player_1 = pygame.image.load("assets/player.png")
player_1_y = 300
player_1_move_up = False
player_1_move_down = False

# Player 2 - robot
player_2 = pygame.image.load("assets/player.png")
player_2_y = 300

# Ball
ball = pygame.image.load("assets/ball.png")
ball_x = 640
ball_y = 360
ball_speed = 7
ball_angle = random.uniform(-math.pi / 4, math.pi / 4)  # Start with a random angle
ball_dir = random.choice([1, -1])  # 1: right, -1: left

ball_dx, ball_dy = get_ball_velocity(ball_speed, ball_angle, ball_dir)

# Score
score_1 = 0
score_2 = 0

# Game loop
game_loop = True
game_clock = pygame.time.Clock()

while game_loop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_loop = False

        # Keystroke events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_1_move_up = True
            if event.key == pygame.K_DOWN:
                player_1_move_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player_1_move_up = False
            if event.key == pygame.K_DOWN:
                player_1_move_down = False

    # Checking the victory condition
    if score_1 < SCORE_MAX and score_2 < SCORE_MAX:
        # Clear screen
        screen.fill(COLOR_BLACK)

        # Ball collision with the wall
        if ball_y > size[1] - ball.get_height():
            ball_y = size[1] - ball.get_height()
            ball_dy *= -1
            bounce_sound_effect.play()
        elif ball_y <= 0:
            ball_y = 0
            ball_dy *= -1
            bounce_sound_effect.play()

        # Paddle rectangles
        player_1_rect = pygame.Rect(
            50, player_1_y, player_1.get_width(), player_1.get_height()
        )
        player_2_rect = pygame.Rect(
            1180, player_2_y, player_2.get_width(), player_2.get_height()
        )
        ball_rect = pygame.Rect(
            ball_x, ball_y, ball.get_width(), ball.get_height()
        )

        # Ball collision with player 1
        if ball_rect.colliderect(player_1_rect) and ball_dx < 0:
            # Calculate hit position on the paddle (relative to center)
            rel = (ball_y + ball.get_height() / 2) - (player_1_y + player_1.get_height() / 2)
            norm = rel / (player_1.get_height() / 2)
            bounce_angle = norm * (math.pi / 3)  # Max 60 degrees
            ball_speed = min(ball_speed + 0.5, 16)  # Increase speed, cap at 16
            ball_dx, ball_dy = get_ball_velocity(ball_speed, bounce_angle, 1)
            bounce_sound_effect.play()

        # Ball collision with player 2
        if ball_rect.colliderect(player_2_rect) and ball_dx > 0:
            rel = (ball_y + ball.get_height() / 2) - (player_2_y + player_2.get_height() / 2)
            norm = rel / (player_2.get_height() / 2)
            bounce_angle = norm * (math.pi / 3)  # Max 60 degrees
            ball_speed = min(ball_speed + 0.5, 16)
            ball_dx, ball_dy = get_ball_velocity(ball_speed, bounce_angle, -1)
            bounce_sound_effect.play()

        # Scoring points
        if ball_x < -50:
            ball_x = 640
            ball_y = 360
            ball_speed = 7
            ball_angle = random.uniform(-math.pi / 4, math.pi / 4)
            ball_dir = 1
            ball_dx, ball_dy = get_ball_velocity(ball_speed, ball_angle, ball_dir)
            score_2 += 1
            scoring_sound_effect.play()
        elif ball_x > 1320:
            ball_x = 640
            ball_y = 360
            ball_speed = 7
            ball_angle = random.uniform(-math.pi / 4, math.pi / 4)
            ball_dir = -1
            ball_dx, ball_dy = get_ball_velocity(ball_speed, ball_angle, ball_dir)
            score_1 += 1
            scoring_sound_effect.play()

        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        # Player 1 movement
        if player_1_move_up:
            player_1_y -= 5
        if player_1_move_down:
            player_1_y += 5

        # Clamp player 1
        if player_1_y <= 0:
            player_1_y = 0
        elif player_1_y >= size[1] - player_1.get_height():
            player_1_y = size[1] - player_1.get_height()

        # Player 2 AI
        if player_2_y + player_2.get_height() // 2 < ball_y:
            player_2_y += 5
        elif player_2_y + player_2.get_height() // 2 > ball_y:
            player_2_y -= 5

        # Clamp player 2
        if player_2_y <= 0:
            player_2_y = 0
        elif player_2_y >= size[1] - player_2.get_height():
            player_2_y = size[1] - player_2.get_height()

        # Update score HUD
        score_text = score_font.render(
            f"{score_1} x {score_2}", True, COLOR_WHITE, COLOR_BLACK
        )
        score_text_rect = score_text.get_rect(center=(680, 50))

        # Drawing objects
        screen.blit(ball, (ball_x, ball_y))
        screen.blit(player_1, (50, player_1_y))
        screen.blit(player_2, (1180, player_2_y))
        screen.blit(score_text, score_text_rect)
    else:
        if score_1 == SCORE_MAX:
            # Drawing victory player 1
            screen.fill(COLOR_BLACK)
            screen.blit(score_text, score_text_rect)
            screen.blit(victory_player1_text, victory_player1_text_rect)
        else:
            # Drawing victory player 2
            screen.fill(COLOR_BLACK)
            screen.blit(score_text, score_text_rect)
            screen.blit(victory_player2_text, victory_player2_text_rect)

    # Update screen
    pygame.display.flip()
    game_clock.tick(60)

pygame.quit()