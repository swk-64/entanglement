import pygame
from lib import (DISPLAY_RESOLUTION, process_projectiles, render_image, process_input, process_movement, RAYS_AMOUNT,
                 load_level, draw_minimap, update_entities, is_player_dead)


pygame.init()
screen = pygame.display.set_mode(DISPLAY_RESOLUTION)
clock = pygame.time.Clock()
running = True
dt = 0

# init textures

# stone_wall_1
stone_wall_1_texture = pygame.image.load("./textures/stone_wall_1.jpg").convert()

# pelmen_king
pelmen_king_frames = []
for i in range(12):
    frame = pygame.image.load(f"./textures/pelmen_king/{i}.png").convert_alpha()
    pelmen_king_frames.append(frame)

# load level
file = open("levels/level_3.txt", "r")

'''
level symbols designations:
    # - wall
    0 - floor
    @ - player spawn
    ! - entity 1 spawn
    $ - entity 2 spawn
    ...
'''

# read level data
level_data = [i.rstrip() for i in file.readlines()]


#process level data
player, level_objs_map, walls, entities, minimap = load_level(screen, "levels/level_3.txt")
projectiles = []

in_level = True
while in_level:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            in_level = False

    # get input
    pressed_keys = pygame.key.get_pressed()
    pressed_mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    now = pygame.time.get_ticks()

    process_input(pressed_keys, pressed_mouse_buttons, mouse_pos, dt, player, projectiles, now)

    process_movement(entities, player, level_objs_map, projectiles, dt, now)


    projectiles = process_projectiles(projectiles, entities, player, dt, now)
    entities = update_entities(entities)

    if is_player_dead(player):
        in_level = False

    # render image
    render_image(screen, player, walls, entities, projectiles, RAYS_AMOUNT, now)
    draw_minimap(screen, minimap, player)

    # show on display
    pygame.display.update()

    # get dt and wait
    dt = clock.tick(60) / 1000

pygame.quit()
