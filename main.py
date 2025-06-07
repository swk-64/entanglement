import pygame
from lib import *
from math import sin, cos, pi
from pygame import gfxdraw


pygame.init()
pygame.font.init()
font = pygame.font.SysFont("Comic Sans MS", 30)
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
door_texture = pygame.image.load("textures/white_red_tiles_wall.jpg")
block_texture.convert()
door_texture.convert()

# read level data
level_data = [i.rstrip() for i in file.readlines()]


#process level data
level_objs = list()
walls = list()
entities = list()
update_collision_objs = list()
projectiles = list()

minimap = pygame.Surface((len(level_data[0]) * MINIMAP_BLOCK_SIZE, len(level_data) * MINIMAP_BLOCK_SIZE))
minimap.convert()

for y in range(len(level_data)):
    level_objs.append([])
    for x in range(len(level_data[y])):
        pos = pygame.Vector2(x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2)
        left_b = x * MINIMAP_BLOCK_SIZE
        top_b = y * MINIMAP_BLOCK_SIZE
        minimap_block = pygame.Rect(left_b, top_b, MINIMAP_BLOCK_SIZE, MINIMAP_BLOCK_SIZE)
        match level_data[y][x]:
            case "@":
                block = SpawnBlockPlayer(pos)
                player_1 = block.spawn_entity()
                player_1.weapons.append(LaserGun(player_1))
                update_collision_objs.append(player_1)
                level_objs[y].append(block)

                color = SPAWN_POINT_COLOR
            case "#":
                left = True
                top = True
                right = True
                bottom = True

                if x != 0:
                    if level_data[y][x - 1] == "#":
                        left = False
                else:
                    left = False
                if y != 0:
                    if level_data[y - 1][x] == "#":
                        top = False
                else:
                    top = False
                if x != len(level_data[y]) - 1:
                    if level_data[y][x + 1] == "#":
                        right = False
                else:
                    right = False
                if y != len(level_data) - 1:
                    if level_data[y + 1][x] == "#":
                        bottom = False
                else:
                    bottom = False

                neighbours = (left, top, right, bottom)

                block = Wall(pos, '#', neighbours, block_texture)

                walls.append(block)
                level_objs[y].append(block)

                color = WALL_COLOR

            case "!":
                block = SpawnBlockPelmenKing(pos)
                entity = block.spawn_entity()
                entities.append(entity)
                level_objs[y].append(block)
                update_collision_objs.append(entity)

                color = ENTITY_1_SPAWN_POINT_COLOR
            case _:
                block = FloorBlock()
                level_objs[y].append(block)

                color = FLOOR_COLOR

        pygame.draw.rect(minimap, color, minimap_block)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # keyboard
    keys = pygame.key.get_pressed()

    velocity = pygame.Vector2(0, 0)
    if keys[pygame.K_w]:
        velocity += pygame.Vector2(cos(player_1.look_ang), -sin(player_1.look_ang))
    if keys[pygame.K_s]:
        velocity += pygame.Vector2(-cos(player_1.look_ang), sin(player_1.look_ang))
    if keys[pygame.K_a]:
        velocity += pygame.Vector2(-sin(player_1.look_ang), -cos(player_1.look_ang))
    if keys[pygame.K_d]:
        velocity += pygame.Vector2(sin(player_1.look_ang), cos(player_1.look_ang))

    if velocity != pygame.Vector2(0, 0):
        velocity = velocity.normalize() * dt * PLAYER_SPEED

    if keys[pygame.K_LSHIFT]:
        velocity *= PLAYER_RUN_SPEED_MODIFIER
    player_1.vel = velocity

    for obj in entities:
        obj.ai_update(player_1)
    update_collisions(update_collision_objs, level_objs)

    for obj in update_collision_objs:
        obj.move()

    buttons = pygame.mouse.get_pressed()
    if buttons[0]:
        proj = player_1.curr_weapon().use()
        if proj:
            projectiles.append(proj)
    else:
        player_1.curr_weapon().is_active = False

    # mouse
    player_1.look_ang -= (pygame.mouse.get_pos()[0] - DISPLAY_RESOLUTION[0] / 2) / 10 * dt
    pygame.mouse.set_pos(DISPLAY_RESOLUTION[0] / 2, DISPLAY_RESOLUTION[1] / 2)

    projectiles = update_projectiles(projectiles, dt)

    # render image
    render_image(screen, player_1, walls, entities, projectiles, RAYS_AMOUNT)

    # draw minimap
    look_ang = -((player_1.look_ang * 180 / pi) % 360)
    fov = player_1.fov * 90 / pi
    start_ang = int(look_ang - fov)
    end_ang = int(look_ang + fov)
    screen.blit(minimap, (0, 0))
    gfxdraw.pie(screen, int(player_1.pos.x * MINIMAP_SCALE), int(player_1.pos.y * MINIMAP_SCALE), int(MINIMAP_BLOCK_SIZE * 1.5), start_ang, end_ang, pygame.Color("green"))
    pygame.draw.circle(screen, "yellow", player_1.pos * MINIMAP_SCALE, MINIMAP_BLOCK_SIZE / 2)

    # show on display
    pygame.display.flip()

    # get dt and wait
    dt = clock.tick(60) / 1000

pygame.quit()
