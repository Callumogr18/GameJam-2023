# GAMEJAM 23
# Author: Callum O'Gorman - Team Air Hockey
import pygame
import os

#  Initialize the font and mixer(For music)
pygame.font.init()
pygame.mixer.init()

SHIP_WIDTH, SHIP_HEIGHT = 55, 40
WIDTH, HEIGHT = 900, 500
VEL = 5
BORDER = pygame.Rect(WIDTH/2, 0, 10, HEIGHT)
BALL_RADIUS = 7

# Our images for the background, yellow and red spaceships
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("SpaceHockey", "assets", "space.png")), (WIDTH, HEIGHT))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
    os.path.join("SpaceHockey", "assets", "spaceship_yellow.png")), (SHIP_WIDTH, SHIP_HEIGHT)), 90)
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(
    os.path.join("SpaceHockey", "assets", "spaceship_red.png")), (SHIP_WIDTH, SHIP_HEIGHT)), 270)

#  Setting the display height, width for the pygame window and font type and size
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AIR HOCKEY")
FONT = pygame.font.SysFont("Comic Sans MS", 40)
pygame.mixer.music.load("SpaceHockey/assets/Ove Melaa Supa Powa Loop B.mp3")

# Colours used: White, Black, pink. Also the FPS for the pygame clock
WHITE = (255, 255, 255)
PINK = (255, 0, 0)
BLACK = (0, 0, 0)
FPS = 60


class Ball():
    MAX_VEL = 6
    COLOUR = PINK

    # The constructor method, which sets the initial values of the ball's properties
    def __init__(self, x, y, radius):
        # Note self.start_x and start_y, this was for the reset function
        self.x = self.start_x = x
        self.y = self.start_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    # Method that draws the ball on the screen
    def draw(self, WIN):
        pygame.draw.circle(WIN, self.COLOUR, (self.x, self.y), self.radius)

    # Method that updates the position of the ball based on its velocity
    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    # Method that resets the position of the ball to its starting position and reverses its x velocity
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.x_vel *= 1
        self.y_vel = 0


def handle_collision(ball, yellow, red):
    #  If we are colliding with the bottom of the window, we are checking ball.y (Ball centre) and ball radius
    #  If that is the case, we reverse the direction of the ball, (*= -1)
    #  Aside: ball.y + ball.radius = Edge of ball (Key for collision detection)
    if ball.y + ball.radius >= HEIGHT:
        ball.y_vel *= -1
    # This is similar to above but checking for top ceiling
    elif ball.y - ball.radius <= 0:
        ball.y_vel *= -1

    """
    This is the complicated part...This is handling collisions with the yellow and red ship. I had to watch
    multiple youtube videos trying to figure this one out.
    Watch this if you're interested: https://www.youtube.com/watch?v=vVGTZlnnX3U&t=2052s (39:00 - 59:00)
    """
    if ball.x_vel < 0:
        #  If the y value of the ball is greater than y value of ship, but less than y value of ship + height of ship...
        # tells us where the ship is essentially
        if ball.y >= yellow.y and ball.y <= yellow.y + yellow.height:
            if ball.x - ball.radius <= yellow.x + yellow.width:
                ball.x_vel *= -1

                middle_y = yellow.y + yellow.height / 2
                difference_y = middle_y - ball.y
                reduction_factor = (yellow.height / 2) / ball.MAX_VEL
                y_vel = difference_y / reduction_factor
                ball.y_vel = -1 * y_vel
                # EDITOR'S NOTE: Maybe create function for math
    else:
        if ball.y >= red.y and ball.y <= red.y + red.height:
            if ball.x + ball.radius >= red.x:
                ball.x_vel *= -1

                middle_y = red.y + red.height / 2
                difference_y = middle_y - ball.y
                reduction_factor = (red.height / 2) / ball.MAX_VEL
                y_vel = difference_y / reduction_factor
                ball.y_vel = -1 * y_vel


def draw_window(red, yellow, ball, red_score, yellow_score):
    WIN.fill(WHITE)
    WIN.blit(BG, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)
    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))
    # Note the "1" is for anti-aliasing purposes
    yellow_scoreboard = FONT.render(f"{yellow_score}", 1, WHITE)
    red_scoreboard = FONT.render(f"{red_score}", 1, WHITE)
    WIN.blit(yellow_scoreboard, (WIDTH//4 -
             yellow_scoreboard.get_width()//2, 20))
    WIN.blit(red_scoreboard, (WIDTH * (3/4) -
             red_scoreboard.get_width()//2, 20))
    ball.draw(WIN)
    pygame.display.update()


def yellow_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x > 0:
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + yellow.width < BORDER.x:
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y > 0:
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + yellow.height < BORDER.x + 30:
        yellow.y += VEL


def red_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x > BORDER.x + BORDER.width:
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + red.width < WIDTH:
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y > 0:
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + red.height < BORDER.x + 30:
        red.y += VEL


def main():
    # The first two numbers in yellow and red indicate starting position. For ball we start from middle of window
    yellow = pygame.Rect(100, 250, SHIP_WIDTH, SHIP_HEIGHT)
    red = pygame.Rect(700, 250, SHIP_WIDTH, SHIP_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    yellow_score = 0
    red_score = 0

    #  Some of the booleans used in this main function
    game_running = True
    music = False
    won = False
    clock = pygame.time.Clock()

    while game_running:
        #  Every second 60 frames will be passed
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

        keys_pressed = pygame.key.get_pressed()
        draw_window(red, yellow, ball, yellow_score, red_score)
        yellow_movement(keys_pressed, yellow)
        red_movement(keys_pressed, red)
        ball.move()
        handle_collision(ball, yellow, red)

        """
        MUSIC HANDLER:
        If "m" is pressed and music = False, the music is played. If "m" is pressed after this, music = True,
        So we skip over the first if statement and go to the else, stopping the music. Allow some time for turning
        on and off though, need to fix that issue in the future
        """
        if keys_pressed[pygame.K_m]:
            if not music:
                #  (-1) will play the music in a loop
                pygame.mixer.music.play(-1)
                music = True
            else:
                pygame.mixer.music.stop()
                music = False

        if ball.x < 0:
            yellow_score += 1
            ball.reset()
        elif ball.x > WIDTH:
            red_score += 1
            ball.reset()

        # winning_score = 10
        # if yellow_score == winning_score:
        #    won = True
        #    score_text = "Yellow Wins!"
        # elif red_score == winning_score:
        #    won = True
        #    score_text = "Red Wins!"

        #  if won:
            # winner = FONT.render(score_text, 1, WHITE)
            # WIN.blit(winner, WIDTH // 2 - winner.get_width() //
            #         2, HEIGHT // 2 - winner.get_height() // 2)
            # pygame.display.update()
            #  pygame.time.delay(5000)
            #  ball.reset()
            # yellow_score = 0
            # red_score = 0

    pygame.quit()


if __name__ == "__main__":
    main()
