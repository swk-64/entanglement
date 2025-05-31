import pygame
from lib import *
from math import sin, cos, pi, atan
from pygame import gfxdraw


pygame.init()
pygame.font.init()
font = pygame.font.SysFont("Comic Sans MS", 30)
screen = pygame.display.set_mode(DISPLAY_RESOLUTION)
clock = pygame.time.Clock()
running = True
dt = 0

# load level
file = open("levels/test_level.txt", "r")


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
entity_texture = pygame.image.load("textures/test_sprite.jpg")
block_texture = pygame.image.load("textures/block_test.jpg")

# read level data
level_data = [i.rstrip() for i in file.readlines()]


#player init
player_1 = Player("player_1", PLAYER_COLOR, 0)



#process level data
level_objs = list()
visible_objs = list()
collidable_objs = list()
update_collision_objs = list()

for y in range(len(level_data)):
    level_objs.append([])
    for x in range(len(level_data[y])):
        match level_data[y][x]:
            case "@":
                block = SpawnBlock()
                player_1 = Player("player_1", PLAYER_COLOR, 0)
                player_1.pos = pygame.Vector2(y * BLOCK_SIZE + BLOCK_SIZE // 2, x * BLOCK_SIZE + BLOCK_SIZE // 2)
                update_collision_objs.append(player_1)
                level_objs[y].append(block)
            case "#":
                block = Wall(pygame.Vector2(x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2), '#', block_texture)
                visible_objs.append(block)
                collidable_objs.append(block)
                level_objs[y].append(block)
            case "!":
                block = EntitySpawnBlock()
                entity = Entity(pygame.Vector2(y * BLOCK_SIZE + BLOCK_SIZE // 2, x * BLOCK_SIZE + BLOCK_SIZE // 2), entity_texture)
                visible_objs.append(entity)
                level_objs[y].append(block)
            case _:
                block = FloorBlock()
                level_objs[y].append(block)

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
        velocity += pygame.Vector2(sin(player_1.look_ang), cos(player_1.look_ang))
    if keys[pygame.K_d]:
        velocity += pygame.Vector2(-sin(player_1.look_ang), -cos(player_1.look_ang))

    if velocity != pygame.Vector2(0, 0):
        velocity = velocity.normalize() * dt * PLAYER_SPEED
    player_1.vel = velocity

    update_collisions(update_collision_objs, level_objs)

    player_1.move()

    # mouse
    player_1.look_ang += (pygame.mouse.get_pos()[0] - DISPLAY_RESOLUTION[0] / 2) / 10 * dt
    pygame.mouse.set_pos(DISPLAY_RESOLUTION[0] / 2, DISPLAY_RESOLUTION[1] / 2)

    # update screen
    screen.fill("black")

    # render image
    render_image(screen, player_1.pos, player_1.look_ang, player_1.fov, visible_objs, RAYS_AMOUNT)

    # draw minimap
    for y in range(len(level_data)):
        for x in range(len(level_data[y])):
            left_b = x * MINIMAP_BLOCK_SIZE
            top_b = y * MINIMAP_BLOCK_SIZE
            block = pygame.Rect(left_b, top_b, MINIMAP_BLOCK_SIZE, MINIMAP_BLOCK_SIZE)
            match level_data[y][x]:
                case "0":
                    color = FLOOR_COLOR
                case "#":
                    color = WALL_COLOR
                case "@":
                    color = SPAWN_POINT_COLOR
                case "!":
                    color = ENTITY_1_SPAWN_POINT_COLOR
                case _:
                    color = BACKGROUND_COLOR
            pygame.draw.rect(screen, color, block)

    # draw visualisation of field of view
    look_ang = -((player_1.look_ang * 180 / pi) % 360)
    fov = player_1.fov / 2 * 180 / pi
    start_ang = round(look_ang - fov)
    end_ang = round(look_ang + fov)
    gfxdraw.pie(screen, int(player_1.pos.x * MINIMAP_SCALE), int(player_1.pos.y * MINIMAP_SCALE), int(MINIMAP_BLOCK_SIZE * 1.5), start_ang, end_ang, pygame.Color("green"))

    # draw player
    pygame.draw.circle(screen, player_1.color, player_1.pos * MINIMAP_SCALE, MINIMAP_BLOCK_SIZE / 2)

    # show on display
    pygame.display.flip()

    # get dt and wait
    dt = clock.tick(60) / 1000

pygame.quit()