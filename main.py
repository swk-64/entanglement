
import pygame
from lib import (DISPLAY_RESOLUTION, process_projectiles, render_image, process_input, process_movement, RAYS_AMOUNT,
                 load_level, draw_minimap, update_entities, check_player_health)

pygame.init()
screen = pygame.display.set_mode(DISPLAY_RESOLUTION)
velocity = pygame.Vector2(0,0)

def game_cycle(events: list[pygame.event.Event], window: pygame.Surface) -> bool:
    clock = pygame.time.Clock()
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

    # process level data
    player, level_objs_map, walls, entities, minimap = load_level(screen, "levels/level_3.txt")
    projectiles = []

    now = pygame.time.get_ticks()

    in_level = process_input(pygame.event.get(), velocity, dt, player, projectiles, now)

    process_movement(entities, player, level_objs_map, projectiles, dt, now)

    projectiles = process_projectiles(projectiles, entities, player, dt, now)
    entities = update_entities(entities)
    if not check_player_health(player):
        in_level = False

    # render image
    render_image(screen, player, walls, entities, projectiles, RAYS_AMOUNT, now)
    draw_minimap(screen, minimap, player)

    # show on display
    pygame.display.update()

    # get dt and wait
    dt = clock.tick(60) / 1000
    return in_level
