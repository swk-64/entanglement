from pygame import gfxdraw
import pygame
from math import sin, cos, pi
from lib import (MINIMAP_BLOCK_SIZE, BLOCK_SIZE, DISPLAY_RESOLUTION, SpawnBlockPlayer, LaserGun, SPAWN_POINT_COLOR,
                 Wall, HASH_COLOR, SpawnBlockEnemy, ENTITY_1_SPAWN_POINT_COLOR, FLOOR_COLOR, FloorBlock,
                 PLAYER_SPEED, PLAYER_RUN_SPEED_MODIFIER, update_collisions, update_projectiles,
                 MINIMAP_SCALE, update_image, init_wall, get_EdgeTexture_object_ptr, Object, process_input, chasing, process_movement, screen_ptr, update_visuals)
import ctypes

# init textures

# stone_wall_1
stone_wall_1_EdgeTexture_object_ptr = get_EdgeTexture_object_ptr("./textures/stone_wall_1.jpg", 32, 48, False)

# pelmen_king
pelmen_king_frames = []
for i in range(12):
    frame_pointer = get_EdgeTexture_object_ptr(f"./textures/pelmen_king/{i}.png", 32, 48, True)
    pelmen_king_frames.append(frame_pointer)


pygame.init()
screen = pygame.display.set_mode(DISPLAY_RESOLUTION)
clock = pygame.time.Clock()
running = True
dt = 0

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

#load textures
block_texture = pygame.image.load("textures/stone_wall_2.jpg")
block_texture.convert()

# read level data
level_data = [i.rstrip() for i in file.readlines()]


#process level data
level_objs_map = []

visible_objects = []

entities = []
projectiles = []

minimap = pygame.Surface((len(level_data[0]) * MINIMAP_BLOCK_SIZE, len(level_data) * MINIMAP_BLOCK_SIZE))
minimap.convert()
player = None

for y in range(len(level_data)):
    level_objs_map.append([])
    for x in range(len(level_data[y])):
        pos = pygame.Vector2(x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2)
        left_b = x * MINIMAP_BLOCK_SIZE
        top_b = y * MINIMAP_BLOCK_SIZE
        minimap_block = pygame.Rect(left_b, top_b, MINIMAP_BLOCK_SIZE, MINIMAP_BLOCK_SIZE)
        match level_data[y][x]:
            case "@":
                block = SpawnBlockPlayer(pos)
                player = block.spawn_entity()
                player.weapons.append(LaserGun(player))

                level_objs_map[y].append(block)

                minimap_block_color = SPAWN_POINT_COLOR
            case "#":
                block = init_wall(level_data, "#", pos, stone_wall_1_EdgeTexture_object_ptr,x, y)

                visible_objects.append(block)
                level_objs_map[y].append(block)

                minimap_block_color = HASH_COLOR

            case "!":
                block = SpawnBlockEnemy(pos, pelmen_king_frames, PLAYER_SPEED, chasing)
                entity = block.spawn_entity()
                entities.append(entity)
                level_objs_map[y].append(block)

                minimap_block_color = ENTITY_1_SPAWN_POINT_COLOR
            case _:
                block = FloorBlock()
                level_objs_map[y].append(block)

                minimap_block_color = FLOOR_COLOR

        pygame.draw.rect(minimap, minimap_block_color, minimap_block)

if not player:
    raise IOError("No player block found")


objs_arr = (Object * len(visible_objects))()
for i in range(len(visible_objects)):
    objs_arr[i] = visible_objects[i].c_object


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # get input
    pressed_keys = pygame.key.get_pressed()
    pressed_mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    process_input(pressed_keys, pressed_mouse_buttons, mouse_pos, dt, player, projectiles)
    #############################

    process_movement(entities, player, level_objs_map, dt)

    update_visuals(entities, player)
    #projectiles = update_projectiles(projectiles, dt)



    # render image
    #render_image(screen, player, walls, entities, projectiles, RAYS_AMOUNT)
    update_image(screen_ptr, screen, player, len(visible_objects), objs_arr)

    # draw minimap
    looking_ang = -((player.look_ang * 180 / pi) % 360)
    fov = player.fov * 90 / pi
    start_ang = int(looking_ang - fov)
    end_ang = int(looking_ang + fov)
    screen.blit(minimap, (0, 0))
    gfxdraw.pie(screen, int(player.pos.x * MINIMAP_SCALE), int(player.pos.y * MINIMAP_SCALE), int(MINIMAP_BLOCK_SIZE * 1.5), start_ang, end_ang, pygame.Color("green"))
    pygame.draw.circle(screen, "yellow", player.pos * MINIMAP_SCALE, MINIMAP_BLOCK_SIZE / 2)

    # show on display
    pygame.display.flip()

    # get dt and wait
    dt = clock.tick(60) / 1000

pygame.quit()
