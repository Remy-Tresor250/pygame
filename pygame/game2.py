import sys

import pygame
import serial

pygame.init()
screen_width = 1600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gotcha")

sun_img = pygame.transform.scale(
    pygame.image.load("./images/sun.png"),
    (100, 100)
)
sky_img = pygame.transform.scale(
    pygame.image.load("./images/sky.jpg"),
    (1600, 800)
)

helicopter = pygame.image.load("./images/helicopter.png")
pygame.mixer.music.load("./audio/Helicopter Sound.mp3")
pygame.mixer.music.play(-1)

tile_size = 200
obstacle_x = 1600
obstacle_y = 400

ser = serial.Serial('/dev/ttyACM0', 9600)


class World:
    def __init__(self, data):
        self.tile_list = []
        ground_img = pygame.image.load("./images/ground.png")

        row_count = 0
        for row in data:
            col_count = 0

            for tile in row:
                if tile == 2:
                    img = pygame.transform.scale(
                        ground_img,
                        (tile_size, tile_size)
                    )

                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


world_data = [
    [1, 3, 1, 1, 1, 3, 1, 1],
    [1, 0, 0, 0, 0, 0, 3, 1],
    [1, 0, 0, 3, 0, 3, 0, 1],
    [2, 2, 2, 2, 2, 2, 2, 2],
]

obstacles = [
    (obstacle_x - 500, obstacle_y),
    (obstacle_x, obstacle_y + 100),
    (obstacle_x - 350, obstacle_y + 100),
    (obstacle_x - 150, obstacle_y + 150),
    (obstacle_x - 200, obstacle_y - 110),
    (obstacle_x - 700, obstacle_y - 90),
    (obstacle_x + 250, obstacle_y - 280),
    (obstacle_x + 300, obstacle_y + 220)
]


def check_collision(hel_x, hel_y, obstacles_list):
    helicopter_rect = helicopter.get_rect(topleft=(hel_x, hel_y))

    for obst_x, obst_y in obstacles_list:
        obstacle_rect = obstacle_img.get_rect(topleft=(obst_x, obst_y))
        if helicopter_rect.colliderect(obstacle_rect):
            return True

    return False


game_over_font = pygame.font.Font(None, 72)
game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
game_over_text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
game_over = False

red_screen = pygame.Surface((screen_width, screen_height))
red_screen.fill((255, 0, 0))

world = World(world_data)

running = True

helicopter_x = 100
helicopter_y = 400

obstacle_img = pygame.image.load("./images/bird.png")
game_over_sound = pygame.mixer.Sound("./audio/Explosion Sound.mp3")

while running:

    if obstacle_x < 0:
        obstacle_x = 2000
    obstacle_x -= 20

    screen.blit(sky_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    screen.blit(helicopter, (helicopter_x, helicopter_y))
    screen.blit(obstacle_img, (obstacle_x - 500, obstacle_y))
    screen.blit(obstacle_img, (obstacle_x, obstacle_y + 100))
    screen.blit(obstacle_img, (obstacle_x - 350, obstacle_y + 100))
    screen.blit(obstacle_img, (obstacle_x - 150, obstacle_y + 150))
    screen.blit(obstacle_img, (obstacle_x - 200, obstacle_y - 110))
    screen.blit(obstacle_img, (obstacle_x - 700, obstacle_y - 90))
    screen.blit(obstacle_img, (obstacle_x + 250, obstacle_y - 280))
    screen.blit(obstacle_img, (obstacle_x + 300, obstacle_y + 220))

    world.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    arduino_data = ser.readline().decode().strip().split('|')

    if len(arduino_data) == 3:
        x_value, y_value, button_state = arduino_data
        x_value = int(x_value.split(':')[1].strip())
        y_value = int(y_value.split(':')[1].strip())

        helicopter_x = int((x_value / 600) * screen_width)
        helicopter_y = int((y_value / 600) * screen_height)

        collision = check_collision(helicopter_x, helicopter_y, obstacles)
        if collision:
            game_over_sound.play()
            game_over = True

            # Display the red screen and "Game Over" text
        if game_over:
            screen.blit(red_screen, (0, 0))
            screen.blit(game_over_text, game_over_text_rect)
            pygame.display.update()
            pygame.time.delay(5000)
            pygame.quit()
            sys.exit()

    pygame.display.update()

pygame.quit()
sys.exit()
