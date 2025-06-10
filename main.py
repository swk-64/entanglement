from math import sin, cos, pi

import pygame
from pygame import gfxdraw

import lib


def read_level_data() -> None:
    with open("levels/level_3.txt", "r") as f:
        return [i.rstrip() for i in f.readlines()]


def setup_map(entities, level_data, level_objs, update_collision_objs, walls) -> None:
    """
    level symbol designations:
        # - wall
        0 - floor
        @ - player spawn
        ! - entity 1 spawn
        $ - entity 2 spawn
        ...
    """

    block_texture = pygame.image.load("textures/stone_wall_2.jpg")
    door_texture = pygame.image.load("textures/white_red_tiles_wall.jpg")
    block_texture.convert()
    door_texture.convert()

    minimap = pygame.Surface(
        (
            len(level_data[0]) * lib.MINIMAP_BLOCK_SIZE,
            len(level_data) * lib.MINIMAP_BLOCK_SIZE,
        )
    )
    minimap.convert()

    for y in range(len(level_data)):
        level_objs.append([])
        for x in range(len(level_data[y])):
            pos = pygame.Vector2(
                x * lib.BLOCK_SIZE + lib.BLOCK_SIZE // 2,
                y * lib.BLOCK_SIZE + lib.BLOCK_SIZE // 2,
            )
            left_b = x * lib.MINIMAP_BLOCK_SIZE
            top_b = y * lib.MINIMAP_BLOCK_SIZE
            minimap_block = pygame.Rect(
                left_b, top_b, lib.MINIMAP_BLOCK_SIZE, lib.MINIMAP_BLOCK_SIZE
            )
            match level_data[y][x]:
                case "@":
                    block = lib.SpawnBlockPlayer(pos)
                    player_1 = block.spawn_entity()
                    player_1.weapons.append(lib.LaserGun(player_1))
                    update_collision_objs.append(player_1)
                    level_objs[y].append(block)

                    color = lib.SPAWN_POINT_COLOR
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

                    block = lib.Wall(pos, "#", neighbours, block_texture)

                    walls.append(block)
                    level_objs[y].append(block)

                    color = lib.WALL_COLOR

                case "!":
                    block = lib.SpawnBlockPelmenKing(pos)
                    entity = block.spawn_entity()
                    entities.append(entity)
                    level_objs[y].append(block)
                    update_collision_objs.append(entity)

                    color = lib.ENTITY_1_SPAWN_POINT_COLOR
                case _:
                    block = lib.FloorBlock()
                    level_objs[y].append(block)

                    color = lib.FLOOR_COLOR

            pygame.draw.rect(minimap, color, minimap_block)
    return minimap, player_1, pos


def draw_minimap(minimap, player_1, pos, screen):
    look_ang = -((player_1.look_ang * 180 / pi) % 360)
    fov = player_1.fov * 90 / pi
    start_ang = int(look_ang - fov)
    end_ang = int(look_ang + fov)
    screen.blit(minimap, (0, 0))
    gfxdraw.pie(
        screen,
        int(player_1.pos.x * lib.MINIMAP_SCALE),
        int(player_1.pos.y * lib.MINIMAP_SCALE),
        int(lib.MINIMAP_BLOCK_SIZE * 1.5),
        start_ang,
        end_ang,
        pygame.Color("green"),
    )
    pygame.draw.circle(
        screen,
        "yellow",
        player_1.pos * lib.MINIMAP_SCALE,
        lib.MINIMAP_BLOCK_SIZE / 2,
    )


def process_input(
    dt, entities, level_objs, player_1, projectiles, update_collision_objs, velocity
):
    # keyboard
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        velocity += pygame.Vector2(cos(player_1.look_ang), -sin(player_1.look_ang))
    if keys[pygame.K_s]:
        velocity += pygame.Vector2(-cos(player_1.look_ang), sin(player_1.look_ang))
    if keys[pygame.K_a]:
        velocity += pygame.Vector2(-sin(player_1.look_ang), -cos(player_1.look_ang))
    if keys[pygame.K_d]:
        velocity += pygame.Vector2(sin(player_1.look_ang), cos(player_1.look_ang))

    if velocity != pygame.Vector2(0, 0):
        velocity = velocity.normalize() * dt * lib.PLAYER_SPEED

    if keys[pygame.K_LSHIFT]:
        velocity *= lib.PLAYER_RUN_SPEED_MODIFIER
    player_1.vel = velocity

    for obj in entities:
        obj.ai_update(player_1)
    lib.update_collisions(update_collision_objs, level_objs)

    for obj in update_collision_objs:
        obj.move()

    # mouse
    buttons = pygame.mouse.get_pressed()
    if buttons[0]:
        proj = player_1.curr_weapon().use()
        if proj:
            projectiles.append(proj)
    else:
        player_1.curr_weapon().is_active = False

    player_1.look_ang -= (
        (pygame.mouse.get_pos()[0] - lib.DISPLAY_RESOLUTION[0] / 2) / 10 * dt
    )
    pygame.mouse.set_pos(lib.DISPLAY_RESOLUTION[0] / 2, lib.DISPLAY_RESOLUTION[1] / 2)


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(lib.DISPLAY_RESOLUTION)
    clock = pygame.time.Clock()
    running = True
    dt = 0

    level_data = read_level_data()

    # process level data
    level_objs = []
    walls = []
    entities = []
    update_collision_objs = []
    projectiles = []

    minimap, player_1, pos = setup_map(
        entities, level_data, level_objs, update_collision_objs, walls
    )

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        velocity = pygame.Vector2(0, 0)
        process_input(
            dt,
            entities,
            level_objs,
            player_1,
            projectiles,
            update_collision_objs,
            velocity,
        )

        projectiles = lib.update_projectiles(projectiles, dt)

        # render image
        lib.render_image(
            screen, player_1, walls, entities, projectiles, lib.RAYS_AMOUNT
        )

        # draw minimap
        draw_minimap(minimap, player_1, pos, screen)

        # show on display
        pygame.display.flip()

        # get dt and wait
        dt = clock.tick(60) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
