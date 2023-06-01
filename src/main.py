import pygame
import pygame_menu
from pygame_menu import events as py_events, sound
from random import randint
from Database.GameDatabaseManager import GameDatabaseManager

# inital
pygame.init()
pygame.font.init()
pygame.mixer.init()

# initial screen
WIDTH, HEIGHT = 900, 500
Screen = pygame.display.set_mode((WIDTH, HEIGHT))


# Assets
Fighter = pygame.transform.rotate(pygame.transform.scale(
    pygame.image.load('Assets/images/Fighter.png'), (80, 80)), 90).convert_alpha()

Health = pygame.transform.rotate(pygame.transform.scale(
    pygame.image.load('Assets/images/Fighter.png'), (35, 35)), 180).convert_alpha()

Clouds = pygame.transform.scale(pygame.image.load(
    'Assets/images/clouds.png'), (800, 400)).convert_alpha()

Font_agancy = pygame.font.Font('Assets/fonts/agancy_fb.ttf', 30)

Fire_sound = pygame.mixer.Sound('Assets/sounds/fire.mp3')
Fire_sound.set_volume(.4)

Fly_sound = pygame.mixer.Sound('Assets/sounds/fly.mp3')
Fly_sound.set_volume(.3)

# enemis
enemy_1 = pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(
    pygame.image.load('Assets/images/enemy/1.png'), (50, 50)), 180), False, True).convert_alpha()

enemy_2 = pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(
    pygame.image.load('Assets/images/enemy/2.png'), (50, 50)), 180), False, True).convert_alpha()

enemy_3 = pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(
    pygame.image.load('Assets/images/enemy/3.png'), (50, 50)), 180), False, True).convert_alpha()

enemy_4 = pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(
    pygame.image.load('Assets/images/enemy/4.png'), (50, 50)), 180), False, True).convert_alpha()

enemy_5 = pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(
    pygame.image.load('Assets/images/enemy/5.png'), (50, 50)), 180), False, True).convert_alpha()

# Set Screen Title And Icon
pygame.display.set_caption("bang BANG!")
pygame.display.set_icon(Fighter)


# Const Variables
PLAYER = pygame.USEREVENT
ENEMY_HIT = pygame.USEREVENT + 1
ENEMY_ECAPE = pygame.USEREVENT + 2
GAME_OVER = pygame.USEREVENT + 3
FPS = 60
SPEED = 3
BULLET_SPEED = 6
ENEMY_SPEED = 5
FIGHTER_START_Y_LOCATION = (HEIGHT // 2)-(Fighter.get_height() // 2)
MAX_BULLET = 5
MAX_ENEMIES = 7
ENEMY_SPOWAN = 700

# Colors
Sky = (135, 206, 235)
Bullet = (252, 252, 40)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# variable
player_name = 'GUEST'
p_id = 0
high_score = 0
health = 5
score = 0
bullets = []
cloud_locations = []
enemies = []
playing = False
running = True
gameOver = False
fighter_location = None

# initial database manager
dbManager = GameDatabaseManager()

# Menu and Menu Sounds
sound_engine = sound.Sound()
sound_engine.set_sound(sound.SOUND_TYPE_OPEN_MENU, 'Assets/sounds/menu_music.ogg')
sound_engine.play_open_menu()

def input_change(value):
    global player_name
    player_name = value

def start_game():
    global playing, gameOver, health, fighter_location, score, player_name, p_id, high_score
    fighter_location = pygame.Rect(100, FIGHTER_START_Y_LOCATION, 80, 80)
    if gameOver:
        score = 0
        health = 5
        gameOver = False
        enemies.clear()
        bullets.clear()

    game_menu.disable_render()
    playing = True
    sound_engine.pause()
    Fly_sound.play(-1)
    p_id = dbManager.CheckPlayerNameExist(player_name)
    high_score = dbManager.GetHighScore()[1]

game_menu = pygame_menu.Menu('Bang Bang', WIDTH, HEIGHT, True)
game_menu.set_sound(sound_engine, True)

game_menu.add.text_input("Player Name ", default="GUEST", copy_paste_enable=True, onchange=input_change)
game_menu.add.button("Play", start_game)
game_menu.add.button("Quit", py_events.EXIT)

# Fighter movment handelr
def fighter_movement(key, fighter):
    if key[pygame.K_UP] and fighter.y - SPEED > 0:
        fighter.y -= SPEED
    if key[pygame.K_DOWN] and fighter.y + SPEED < HEIGHT - Fighter.get_height():
        fighter.y += SPEED
    if key[pygame.K_RIGHT] and fighter.x + SPEED < WIDTH - Fighter.get_width():
        fighter.x += SPEED
    if key[pygame.K_LEFT] and fighter.x - SPEED > 0:
        fighter.x -= SPEED

# handel bullet destroy when outside window or colided with enemy
def bullet_handler(bullets, enemies):
    try:
        for bullet in bullets:
            bullet.x += BULLET_SPEED
            if bullet.x > WIDTH:
                bullets.remove(bullet)
            for enemy in enemies:
                _, loc = enemy
                if (bullet.colliderect(loc)):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    pygame.event.post(pygame.event.Event(ENEMY_HIT))
    except:
        pass


# move colud on screen
def cloud_handler(cloud_locations):
    cloud_locations[0].x -= SPEED
    if cloud_locations[0].x + cloud_locations[0].width < 0:
        cloud_locations.remove(cloud_locations[0])

# move enemy and check take bullet
def enemy_handler(enemies, fighter):
    try:
        global health
        for enemy in enemies:
            _, loc = enemy
            loc.x -= ENEMY_SPEED
            if loc.x <= 0:
                enemies.remove(enemy)
                pygame.event.post(pygame.event.Event(ENEMY_ECAPE))
            if loc.colliderect(fighter):
                enemies.remove(enemy)
                health -= 1
    except:
        pass

# check if health equal to 0 game is done
def game_over(health):
    global playing, gameOver, p_id, score
    if health < 1:
        Fly_sound.stop()
        playing = False
        gameOver = True
        dbManager.UpdateScore(p_id, score)
        


# draw game objects
def draw_window(cloud_locations, score):
    Screen.fill(Sky)
    if len(cloud_locations) != 0:
        Screen.blit(Clouds, cloud_locations[0])
    # draw score
    score_surface = Font_agancy.render(f'Score {score}', True, WHITE)
    Screen.blit(score_surface, (10, 10))

    # draw player name
    player_name_surface = Font_agancy.render(player_name, True, WHITE)
    Screen.blit(player_name_surface, (10, 50))

    # draw player name
    high_score_surface = Font_agancy.render("HIGH SCORE:"+str(high_score), True, WHITE)
    Screen.blit(high_score_surface, (WIDTH - 10 - high_score_surface.get_width(), 10))

    # draw health
    for h in range(health):
        Screen.blit(Health, (Health.get_width() * h,
                    HEIGHT - Health.get_height()))

    # draw fighter
    Screen.blit(Fighter, (fighter_location.x, fighter_location.y))

    # respown enemies
    for enemy in enemies:
        enemy_num, enemy_loc = enemy
        # wich enemy
        my_enemy = enemy_1
        if enemy_num == 1:
            my_enemy = enemy_1
        elif enemy_num == 2:
            my_enemy = enemy_2
        elif enemy_num == 2:
            my_enemy = enemy_3
        elif enemy_num == 2:
            my_enemy = enemy_4
        else:
            my_enemy = enemy_5
        Screen.blit(my_enemy, enemy_loc)

    # fire bullets
    for bullet in bullets:
        pygame.draw.rect(Screen, Bullet, bullet)

    pygame.display.update()


def main():
    global running, playing, health,score
    clock = pygame.time.Clock()
    pygame.time.set_timer(PLAYER, 700)
    while running:
        events = pygame.event.get()
        if playing:
            clock.tick(FPS)
            # handel events
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and len(bullets) < MAX_BULLET:
                        bullet = pygame.Rect(fighter_location.x + Fighter.get_width() //
                                             2, fighter_location.y + Fighter.get_height() // 2, 10, 5)
                        bullets.append(bullet)
                        Fire_sound.play()

                    if event.key == pygame.K_ESCAPE:
                        game_menu.enable_render()
                        Fly_sound.stop()
                        playing = False

                if event.type == PLAYER:
                    # make enemy
                    if len(enemies) < MAX_ENEMIES:
                        enemy_number = randint(1, 5)
                        enemy_x = randint(WIDTH, WIDTH + 50)
                        enemy_y = randint(10, HEIGHT - 50)
                        enemies.append(
                            (enemy_number, pygame.Rect(enemy_x, enemy_y, 50, 50)))
                if event.type == ENEMY_HIT:
                    score += 2
                if event.type == ENEMY_ECAPE:
                    score -= 1
                if event.type == GAME_OVER:
                    running = False
            key_pressed = pygame.key.get_pressed()
            fighter_movement(key_pressed, fighter_location)

            bullet_handler(bullets, enemies)
            if len(cloud_locations) == 0:
                cloud_locations.append(pygame.Rect(
                    WIDTH, randint(100, 400), Clouds.get_width(), Clouds.get_height()))

            cloud_handler(cloud_locations)
            enemy_handler(enemies, fighter_location)

            draw_window(cloud_locations, score)
            game_over(health)

        if game_menu.is_enabled() and not playing:
            sound_engine.unpause()
            game_menu.update(events)
            game_menu.draw(Screen)
            pygame.display.update()


if __name__ == "__main__":
    main()
