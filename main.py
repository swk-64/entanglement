import pygame
from lib import *
from math import sin, cos, pi, atan


pygame.init()
screen = pygame.display.set_mode(DISPLAY_RESOLUTION)
clock = pygame.time.Clock()
running = True
dt = 0


file = open("levels/test_level.txt", "r")

level_data = [i.rstrip() for i in file.readlines()]
level = list()

#player init
player_1 = Player("player_1", PLAYER_COLOR, 0)
entity_texture = pygame.image.load("textures/test_sprite.jpg")
block_texture = pygame.image.load("textures/block_test.jpg")
entity = Entity(pygame.Vector2(3 * BLOCK_SIZE + BLOCK_SIZE // 2, 2 * BLOCK_SIZE + BLOCK_SIZE // 2), entity_texture)

for y in range(len(level_data)):
    for x in range(len(level_data[y])):
        if level_data[y][x] == "@":
            player_1.pos = pygame.Vector2(y * BLOCK_SIZE + BLOCK_SIZE // 2, x * BLOCK_SIZE + BLOCK_SIZE // 2)
        if level_data[y][x] != "0" and level_data[y][x] != "@":
            level.append(Block(pygame.Vector2(x, y), level_data[y][x], block_texture))

level.append(entity)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # keyboard
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_1.pos += pygame.Vector2(cos(player_1.look_ang), -sin(player_1.look_ang)) * dt * 30
    if keys[pygame.K_s]:
        player_1.pos += pygame.Vector2(-cos(player_1.look_ang), sin(player_1.look_ang)) * dt * 30
    if keys[pygame.K_a]:
        player_1.pos += pygame.Vector2(sin(player_1.look_ang), cos(player_1.look_ang)) * dt * 30
    if keys[pygame.K_d]:
        player_1.pos += pygame.Vector2(-sin(player_1.look_ang), -cos(player_1.look_ang)) * dt * 30

    # mouse
    player_1.look_ang += (pygame.mouse.get_pos()[0] - DISPLAY_RESOLUTION[0] / 2) / 10 * dt
    pygame.mouse.set_pos(DISPLAY_RESOLUTION[0] / 2, DISPLAY_RESOLUTION[1] / 2)

    # update frame
    screen.fill("black")

    # render image
    render_image(screen, player_1.pos, player_1.look_ang, player_1.fov, level, RAYS_AMOUNT)

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
                case _:
                    color = BACKGROUND_COLOR
            pygame.draw.rect(screen, color, block)

    # draw visualisation of field of view
    field_of_view_ind = pygame.Rect(player_1.pos.x * MINIMAP_SCALE - MINIMAP_BLOCK_SIZE * 1.5, player_1.pos.y * MINIMAP_SCALE - MINIMAP_BLOCK_SIZE * 1.5, MINIMAP_BLOCK_SIZE * 3, MINIMAP_BLOCK_SIZE * 3)
    pygame.draw.arc(screen, "green", field_of_view_ind, player_1.look_ang - player_1.fov / 2, player_1.look_ang + player_1.fov / 2)

    pygame.draw.line(screen, "green", player_1.pos * MINIMAP_SCALE, minimap_fov_end_point(player_1.look_ang - player_1.fov / 2, MINIMAP_BLOCK_SIZE * 1.5, player_1.pos * MINIMAP_SCALE))
    pygame.draw.line(screen, "green", player_1.pos * MINIMAP_SCALE, minimap_fov_end_point(player_1.look_ang + player_1.fov / 2, MINIMAP_BLOCK_SIZE * 1.5, player_1.pos * MINIMAP_SCALE))

    # draw player
    pygame.draw.circle(screen, player_1.color, player_1.pos * MINIMAP_SCALE, MINIMAP_BLOCK_SIZE / 2)

    # draw to frame
    pygame.display.flip()

    # get dt and wait
    dt = clock.tick(60) / 1000

pygame.quit()