import pygame
from pygame import gfxdraw
from math import sin, cos, pi, sqrt, ceil, asin
from typing import Union

# It is recommended to use 32x48 pixels texture size


# constants
DISPLAY_RESOLUTION = (1280, 720)
BLOCK_SIZE = 50
RAYS_AMOUNT = 200
MINIMAP_SCALE = 0.3
MINIMAP_BLOCK_SIZE = BLOCK_SIZE * MINIMAP_SCALE
MIN_RENDER_DISTANCE = 10
ENTITY_SIZE = 50
ENTITY_HALF_SIZE = ENTITY_SIZE / 2

SPAWN_POINT_COLOR = "green"
ENTITY_1_SPAWN_POINT_COLOR = "red"
HASH_COLOR = "white"
FLOOR_COLOR = "grey"
BACKGROUND_COLOR = "black"

PLAYER_COLOR = "yellow"
PLAYER_LOOK_LINE_LEN = BLOCK_SIZE * 4 * MINIMAP_SCALE
PLAYER_COLLISION_SIZE = 15
PLAYER_SPEED = 70
PLAYER_RUN_SPEED_MODIFIER = 2
DOOR_FRAMES = 5
DOOR_WIDTH = 2

WALL_SYMS = '#'

class AnimatedImage:
    def __init__(self, frames: list[pygame.Surface], now: int, speed=100):
        self.frames = frames
        self.frames_number = len(frames)
        self.curr_frame_number = 0
        self.animation_speed = speed
        self.last_update = now
    def check_time(self, now: int):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            if self.curr_frame_number == self.frames_number - 1:
                self.curr_frame_number = 0
            else:
                self.curr_frame_number += 1
    def get_cur_texture(self, now: int):
        self.check_time(now)
        return self.frames[self.curr_frame_number]


class EntityBasicClass:
    def __init__(self, pos: pygame.Vector2, speed: int, health=100):
        self.pos = pos
        self.speed = speed
        self.vel = pygame.Vector2(0, 0)
        self.health = health

    def move(self):
        self.pos += self.vel
        self.vel = pygame.Vector2(0, 0)

    def check_collision(self, level: list):
        x, y = self.cur_block()

        if 0 < x < len(level[0]) - 1 and 0 < y < len(level) - 1:
            level[y - 1][x - 1].check_collision(self)
            level[y + 1][x + 1].check_collision(self)
            level[y + 1][x - 1].check_collision(self)
            level[y - 1][x + 1].check_collision(self)
            level[y][x - 1].check_collision(self)
            level[y - 1][x].check_collision(self)
            level[y][x + 1].check_collision(self)
            level[y + 1][x].check_collision(self)

    def update_ai(self, player: "Player", projectiles: list, dt: int, now: int):
        pass

    def deal_damage(self, damage: int, now: int):
        self.health -= damage

    def cur_block(self):
        return int(self.pos.x // BLOCK_SIZE), int(self.pos.y // BLOCK_SIZE)


class Sprite(EntityBasicClass):
    def __init__(self, pos: pygame.Vector2, speed: int):
        super().__init__(pos, speed)

    def get_cur_points(self, player: "Player"):
        point1 = pygame.Vector2(cos(player.look_ang) * ENTITY_HALF_SIZE + self.pos.x, sin(player.look_ang) * ENTITY_HALF_SIZE + self.pos.y)
        point2 = pygame.Vector2(-cos(player.look_ang) * ENTITY_HALF_SIZE + self.pos.x, -sin(player.look_ang) * ENTITY_HALF_SIZE + self.pos.y)
        return point1, point2


class Player(EntityBasicClass):
    def __init__(self, pos: pygame.Vector2, look_ang=0.0):
        super().__init__(pos, PLAYER_SPEED)
        self.look_ang = look_ang
        self.fov = pi / 2
        self.weapons = []
        self.curr_weapon_number = 0

    def get_look_ang(self):
        return self.look_ang

    def cur_weapon(self):
        return self.weapons[self.curr_weapon_number]


class Enemy(EntityBasicClass):
    def __init__(self, pos: pygame.Vector2, speed: int, frames: list[pygame.Surface], ai, now):
        super().__init__(pos, speed)
        self.ai = ai
        self.texture = AnimatedImage(frames, now)
        self.damage_time = None
        self.damage_duration = 300
        self.weapon = None
    def update_ai(self, player: Player, projectiles: list, dt: int, now: int):
        self.ai(self, player, projectiles, dt, now)
    def deal_damage(self, damage: int, now: int):
        self.health -= damage
        self.damage_time = pygame.time.get_ticks()
    def get_cur_texture(self, now: int):
        now = pygame.time.get_ticks()

        if not (self.damage_time is None):
            if now - self.damage_time >= self.damage_duration:
                self.damage_time = None
            else:
                texture = self.texture.get_cur_texture(now).copy()
                red_rect = pygame.Surface(texture.get_size()).convert_alpha()
                red_rect.fill(pygame.Color(255, 0, 0, 100))
                texture.blit(red_rect, (0, 0))
                return texture
        return self.texture.get_cur_texture(now)
    def get_look_ang(self, player: "Player"):
        return asin((self.pos - player.pos).normalize().y)

class EntityWeaponClass:
    def __init__(self, user: Enemy, speed: int,  now: int, damage: int):
        self.start_time = now
        self.use_speed = speed
        self.user = user
        self.damage = damage
    def use(self, now: int, player: "Player"):
        if now - self.start_time >= self.use_speed:
            self.start_time = now
            direction = -(self.user.pos - player.pos).normalize()
            proj = Projectile(self.user.pos, direction, now, self.damage)
            proj.damaged_entities.append(self.user)
            return proj
        return None


class Weapon:
    def __init__(self, user: Player, speed: int, frames: list[pygame.Surface], now: int, damage: int):
        self.texture = AnimatedImage(frames, now, int(speed // len(frames)))
        self.start_time = now
        self.use_speed = speed
        self.user = user
        self.damage = damage
        self.is_active = False
    def use(self, now: int):
        if self.is_active:
            if now - self.start_time >= self.use_speed:
                self.is_active = False
                ang = self.user.look_ang
                direction = pygame.Vector2(cos(ang), -sin(ang))
                proj = Projectile(self.user.pos, direction, now, self.damage)
                proj.damaged_entities.append(self.user)
                return proj
        return None

    def get_cur_texture(self, now: int):
        if self.is_active:
            return self.texture.get_cur_texture(now)
        else:
            return self.texture.frames[0]

class LaserGun(Weapon):
    def __init__(self, user: Player, now: int):
        frames = []
        for i in range(3):
            image = pygame.image.load("textures/lasergun/" + str(i) + ".png")
            frames.append(image.convert_alpha())
        super().__init__(user, 800, frames, now, 20)

class PelmenLaserGun(EntityWeaponClass):
    def __init__(self, user: Enemy, now: int):
        super().__init__(user, 800, now, 20)


class Projectile:
    def __init__(self, pos: pygame.Vector2, direction: pygame.Vector2, now: int, damage: int, ):
        self.pos = pygame.Vector2(pos.x + direction.x, pos.y + direction.y)
        self.time = now
        self.decay_time = 2000
        self.speed = 200
        self.color = "red"
        self.length = 20
        self.width = 2
        self.damage = damage
        # unit vector with right direction
        self.direction = direction
        self.damaged_entities = []
    def update(self, dt: int):
        now = pygame.time.get_ticks()
        if now - self.time < self.decay_time:
            self.pos += self.direction * dt * self.speed
            return self
        return None
    def get_lines(self):
        rotated = pygame.Vector2(-self.direction.y, self.direction.x)
        return (self.pos, self.direction, self.length), (self.pos - rotated * self.width / 2, rotated, self.width)


class Wall:
    def __init__(self, pos: pygame.Vector2, block_type: str, neighbours: tuple, texture: pygame.Surface):
        self.pos = pos
        self.type = block_type
        self.texture = texture

        # wall points
        top_left = (pos.x - BLOCK_SIZE / 2, pos.y - BLOCK_SIZE / 2)
        top_right = (pos.x + BLOCK_SIZE / 2, pos.y - BLOCK_SIZE / 2)
        bottom_right = (pos.x + BLOCK_SIZE / 2, pos.y + BLOCK_SIZE / 2)
        bottom_left = (pos.x - BLOCK_SIZE / 2, pos.y + BLOCK_SIZE / 2)

        # collision areas
        def bottom(obj: Player):
            if self.pos.x - BLOCK_SIZE / 2 <= obj.pos.x <= self.pos.x + BLOCK_SIZE / 2:
                if self.pos.y + BLOCK_SIZE / 2 <= obj.pos.y <= self.pos.y + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                    if obj.vel.y < 0:
                        obj.vel += pygame.Vector2(0, -obj.vel.y)
        def top(obj: Player):
            if self.pos.x - BLOCK_SIZE / 2 <= obj.pos.x <= self.pos.x + BLOCK_SIZE / 2:
                if self.pos.y - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE <= obj.pos.y <= self.pos.y - BLOCK_SIZE / 2:
                    if obj.vel.y > 0:
                        obj.vel += pygame.Vector2(0, -obj.vel.y)
        def left(obj: Player):
            if self.pos.y - BLOCK_SIZE / 2 <= obj.pos.y <= self.pos.y + BLOCK_SIZE / 2:
                if self.pos.x - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE <= obj.pos.x <= self.pos.x - BLOCK_SIZE / 2:
                    if obj.vel.x > 0:
                        obj.vel += pygame.Vector2(-obj.vel.x, 0)
        def right(obj: Player):
            if self.pos.y - BLOCK_SIZE / 2 <= obj.pos.y <= self.pos.y + BLOCK_SIZE / 2:
                if self.pos.x + BLOCK_SIZE / 2 <= obj.pos.x <= self.pos.x + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                    if obj.vel.x < 0:
                        obj.vel += pygame.Vector2(-obj.vel.x, 0)
        def bottomleft(obj: Player):
            if self.pos.x - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE < obj.pos.x < self.pos.x - BLOCK_SIZE / 2:
                if self.pos.y + BLOCK_SIZE / 2 < obj.pos.y < self.pos.y + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                    vec = pygame.Vector2(1, -1)
                    if vec.dot(obj.vel) > 0:
                        vec.scale_to_length(
                            vec.dot(obj.vel) / (vec.magnitude() * obj.vel.magnitude()) * obj.vel.magnitude())
                        obj.vel -= vec
        def topleft(obj: Player):
            if self.pos.x - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE < obj.pos.x < self.pos.x - BLOCK_SIZE / 2:
                if self.pos.y - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE < obj.pos.y < self.pos.y - BLOCK_SIZE / 2:
                    vec = pygame.Vector2(1, 1)
                    if vec.dot(obj.vel) > 0:
                        vec.scale_to_length(
                            vec.dot(obj.vel) / (vec.magnitude() * obj.vel.magnitude()) * obj.vel.magnitude())
                        obj.vel -= vec
        def bottomright(obj: Player):
            if self.pos.x + BLOCK_SIZE / 2 < obj.pos.x < self.pos.x + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                if self.pos.y + BLOCK_SIZE / 2 < obj.pos.y < self.pos.y + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                    vec = pygame.Vector2(-1, -1)
                    if vec.dot(obj.vel) > 0:
                        vec.scale_to_length(
                            vec.dot(obj.vel) / (vec.magnitude() * obj.vel.magnitude()) * obj.vel.magnitude())
                        obj.vel -= vec
        def topright(obj: Player):
            if self.pos.x + BLOCK_SIZE / 2 < obj.pos.x < self.pos.x + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                if self.pos.y - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE < obj.pos.y < self.pos.y - BLOCK_SIZE / 2:
                    vec = pygame.Vector2(-1, 1)
                    if vec.dot(obj.vel) > 0:
                        vec.scale_to_length(
                            vec.dot(obj.vel) / (vec.magnitude() * obj.vel.magnitude()) * obj.vel.magnitude())
                        obj.vel -= vec

        connections = set()
        collisions = set()
        # left side check
        if neighbours[0]:
            connections.add((bottom_left, top_left))
            collisions.add(left)
        # top side check
        if neighbours[1]:
            connections.add((top_left, top_right))
            collisions.add(top)
        # right side check
        if neighbours[2]:
            connections.add((top_right, bottom_right))
            collisions.add(right)
        # bottom side check
        if neighbours[3]:
            connections.add((bottom_right, bottom_left))
            collisions.add(bottom)

        if neighbours[0] and neighbours[1]:
            collisions.add(topleft)
        if neighbours[1] and neighbours[2]:
            collisions.add(topright)
        if neighbours[2] and neighbours[3]:
            collisions.add(bottomright)
        if neighbours[3] and neighbours[0]:
            collisions.add(bottomleft)

        self.sides = tuple(connections)
        self.collisions = tuple(collisions)
    def check_collision(self, obj: Player):
        for collision in self.collisions:
            collision(obj)


class FloorBlock:
    def __init__(self):
        pass
    def check_collision(self, obj):
        pass


class SpawnBlockPlayer:
    def __init__(self, pos: pygame.Vector2):
        self.pos = pos
    def check_collision(self, obj):
        pass
    def spawn_entity(self):
        return Player(self.pos)


class SpawnBlockEnemy:
    def __init__(self, pos: pygame.Vector2, frames: list[pygame.Surface], speed: int, ai):
        self.pos = pos
        # block's entity traits
        self.entity_frames = frames
        self.entity_speed = speed
        self.entity_ai = ai
    def check_collision(self, obj):
        pass
    def spawn_entity(self, now: int):
        return init_enemy(self.pos, self.entity_frames, self.entity_speed, self.entity_ai, now)

def load_level(screen:pygame.Surface, path: str):
    now = 0

    stone_wall_1_texture = pygame.image.load("./textures/stone_wall_1.jpg").convert()
    pelmen_king_frames = []
    for i in range(12):
        frame = pygame.image.load(f"./textures/pelmen_king/{i}.png").convert_alpha()
        pelmen_king_frames.append(frame)


    file = open(path, "r")

    level_data = [i.rstrip() for i in file.readlines()]

    # process level data
    level_objs_map = []
    walls = []
    entities = []
    player = None

    minimap = pygame.Surface((len(level_data[0]) * MINIMAP_BLOCK_SIZE, len(level_data) * MINIMAP_BLOCK_SIZE)).convert()

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
                    player.weapons.append(LaserGun(player, now))

                    level_objs_map[y].append(block)

                    minimap_block_color = SPAWN_POINT_COLOR
                case "#":
                    block = init_wall(level_data, "#", pos, stone_wall_1_texture, x, y)

                    walls.append(block)
                    level_objs_map[y].append(block)

                    minimap_block_color = HASH_COLOR

                case "!":
                    block = SpawnBlockEnemy(pos, pelmen_king_frames, PLAYER_SPEED * 2, chasing)
                    entity = block.spawn_entity(now)
                    entity.weapon = PelmenLaserGun(entity, now)
                    entities.append(entity)
                    level_objs_map[y].append(block)

                    minimap_block_color = ENTITY_1_SPAWN_POINT_COLOR
                case _:
                    block = FloorBlock()
                    level_objs_map[y].append(block)

                    minimap_block_color = FLOOR_COLOR

            pygame.draw.rect(minimap, minimap_block_color, minimap_block)
    if player is None:
        raise IOError("No player block found")

    return player, level_objs_map, walls, entities, minimap

def draw_minimap(screen:pygame.Surface, minimap:pygame.Surface, player:Player):
    screen.blit(minimap, (0, 0))
    looking_ang = -((player.look_ang * 180 / pi) % 360)
    fov = player.fov * 90 / pi
    start_ang = int(looking_ang - fov)
    end_ang = int(looking_ang + fov)
    gfxdraw.pie(screen, int(player.pos.x * MINIMAP_SCALE), int(player.pos.y * MINIMAP_SCALE), int(MINIMAP_BLOCK_SIZE * 1.5), start_ang, end_ang, pygame.Color("green"))
    pygame.draw.circle(screen, "yellow", player.pos * MINIMAP_SCALE, MINIMAP_BLOCK_SIZE / 2)

def chasing(entity: Enemy, player: Player, projectiles: list, dt: int, now: int):
    chase_distance = 150
    shoot_distance = 350
    cur_distance = distance(player.pos, entity.pos)

    if shoot_distance >= cur_distance > chase_distance:
        proj = entity.weapon.use(now, player)
        if proj:
            projectiles.append(proj)

    elif chase_distance >= cur_distance > 40:
        vel = (player.pos - entity.pos).normalize() * entity.speed * dt
        entity.vel = vel

    elif cur_distance < 40:
        vel = -(player.pos - entity.pos).normalize() * entity.speed * dt
        entity.vel = vel

# def standing_shooting(entity: EntityBasicClass, player: Player, projectiles: list, dt: int):
#     if 250 > distance(player.pos, entity.pos) > 40:


def init_enemy(pos: pygame.Vector2, frames: list[pygame.Surface], speed: int, ai, now: int):
    entity = Enemy(pos, speed, frames, ai, now)
    return entity

def check_player_health(player: Player):
    if player.health <= 0:
        return False
    else:
        return True
def process_projectiles(projs: list[Projectile], entities: list[EntityBasicClass], player: Player, dt: int, now: int):
    projectiles = []
    for proj in projs:
        projectile = proj.update(dt)
        if projectile:
            for entity in [*entities, player]:
                if (entity.pos.x - proj.pos.x) ** 2 + (entity.pos.y - proj.pos.y) ** 2 < ENTITY_HALF_SIZE**2:
                    if entity not in proj.damaged_entities:
                        entity.deal_damage(proj.damage, now)
                        proj.damaged_entities.append(entity)

            projectiles.append(projectile)
    return projectiles

def update_entities(entities: list[EntityBasicClass]):
    valid_entities = []
    for entity in entities:
        if entity.health > 0:
            valid_entities.append(entity)
    return valid_entities

def process_movement(entities:list, player: Player, level_map: list, projectiles: list, dt: int, now: int) -> None:
    for obj in entities:
        obj.update_ai(player, projectiles, dt, now)
        obj.check_collision(level_map)
        obj.move()
    player.check_collision(level_map)
    player.move()

def process_input(pressed_keys, pressed_mouse_buttons, mouse_pos, dt: int, player: Player, projectiles, now: int) -> None:

    # keyboard
    velocity = pygame.Vector2(0, 0)
    if pressed_keys[pygame.K_w]:
        velocity += pygame.Vector2(cos(player.look_ang), -sin(player.look_ang))
    if pressed_keys[pygame.K_s]:
        velocity += pygame.Vector2(-cos(player.look_ang), sin(player.look_ang))
    if pressed_keys[pygame.K_a]:
        velocity += pygame.Vector2(-sin(player.look_ang), -cos(player.look_ang))
    if pressed_keys[pygame.K_d]:
        velocity += pygame.Vector2(sin(player.look_ang), cos(player.look_ang))

    if velocity != pygame.Vector2(0, 0):
        velocity = velocity.normalize() * dt * player.speed

    if pressed_keys[pygame.K_LSHIFT]:
        velocity *= PLAYER_RUN_SPEED_MODIFIER
    player.vel = velocity

    # mouse buttons
    cur_weapon = player.cur_weapon()
    if pressed_mouse_buttons[0]:
        if not cur_weapon.is_active:
            cur_weapon.is_active = True
            cur_weapon.start_time = now
            cur_weapon.texture.curr_frame_number = 0
            cur_weapon.texture.last_update = now
        proj = player.cur_weapon().use(now)
        if proj:
            projectiles.append(proj)
    elif cur_weapon.is_active:
        player.cur_weapon().is_active = False
    # mouse movement
    player.look_ang -= (mouse_pos[0] - DISPLAY_RESOLUTION[0] / 2) / 10 * dt
    pygame.mouse.set_pos(DISPLAY_RESOLUTION[0] / 2, DISPLAY_RESOLUTION[1] / 2)

def init_wall(level_data: list,
              wall_type: str,
              wall_pos: pygame.Vector2,
              texture: pygame.Surface,
              x: int,
              y: int
              ):
    edges = []
    # True - There isn't neighbour, False - opposite
    left = True
    top = True
    right = True
    bottom = True

    if x != 0:
        if level_data[y][x - 1] in WALL_SYMS:
            left = False
    else:
        left = False
    if y != 0:
        if level_data[y - 1][x] in WALL_SYMS:
            top = False

    else:
        top = False
    if x != len(level_data[y]) - 1:
        if level_data[y][x + 1] in WALL_SYMS:
            right = False
    else:
        right = False
    if y != len(level_data) - 1:
        if level_data[y + 1][x] in WALL_SYMS:
            bottom = False
    else:
        bottom = False

    neighbours = (left, top, right, bottom)
    block = Wall(wall_pos, wall_type, neighbours, texture)
    return block

def distance(point1: Union[pygame.Vector2, tuple], point2: Union[pygame.Vector2, tuple]):
    return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def is_visible(look_ang: float, pos: pygame.Vector2, point: pygame.Vector2):
    player_vec = pygame.Vector2(cos(look_ang), -sin(look_ang))
    point_vec = pygame.Vector2(point.x - pos.x, point.y - pos.y)
    if player_vec.dot(point_vec) > 0:
        return True
    return False


def cast_ray(ang: float, look_ang: float, player_pos: pygame.Vector2, walls: list, entities: list, projectiles: list, now: int):
    min_distance = 1000.0
    layers = [(min_distance, pygame.Surface((1, 1)), 1000)]
    if cos(ang) == 0:
        k = None
    else:
        k = -sin(ang) / cos(ang)
        b = player_pos.y - k * player_pos.x

    # process walls
    for obj in walls:
        for side in obj.sides:
            if side[0][0] == side[1][0]:
                if k is None:
                    continue
                else:
                    x = side[0][0]
                    y = k * x + b
            else:
                if k == 0:
                    continue
                elif k is None:
                    y = side[0][1]
                    x = player_pos.x
                else:
                    y = side[0][1]
                    x = (y - b) / k
            inter = pygame.Vector2(x, y)
            if obj.pos.x - BLOCK_SIZE / 2 <= inter.x <= obj.pos.x + BLOCK_SIZE / 2 and obj.pos.y - BLOCK_SIZE / 2 <= inter.y <= obj.pos.y + BLOCK_SIZE / 2:
                if is_visible(look_ang, player_pos, inter):
                    dist = distance(inter, player_pos)
                    if min_distance > dist > MIN_RENDER_DISTANCE:
                        min_distance = dist
                        texture_width = obj.texture.get_width()
                        units_per_pixel = BLOCK_SIZE / texture_width
                        if side[0][0] == side[1][0]:
                            dst = abs(inter.y - side[0][1])
                        else:
                            dst = abs(inter.x - side[0][0])
                        pixel_row = int(dst // units_per_pixel)
                        # for the situation if ray got accurate in a corner of wall
                        if pixel_row == texture_width:
                            pixel_row = 0
                        arr = pygame.PixelArray(obj.texture)
                        if arr[pixel_row:pixel_row + 1, :]:
                            line = arr[pixel_row:pixel_row + 1, :].make_surface()
                            layers[0] = (dist, line, 1000)

    # process entities
    for obj in entities:
        if cos(look_ang) == 0:
            if k == 0:
                continue
            elif k is None:
                y = obj.pos.y
                x = player_pos.x
            else:
                y = obj.pos.y
                x = (y - b) / k
        elif sin(look_ang) == 0:
            if k is None:
                continue
            else:
                x = obj.pos.x
                y = k * x + b
        else:
            k1 = cos(look_ang) / sin(look_ang)
            b1 = obj.pos.y - k1 * obj.pos.x
            if k is None:
                x = player_pos.x
                y = x * k1 + b1
            else:
                x = (b1 - b) / (k - k1)
                y = k1 * x + b1

        inter = pygame.Vector2(x, y)
        if (obj.pos.x - inter[0]) ** 2 + (obj.pos.y - inter[1]) ** 2 < ENTITY_HALF_SIZE**2:
            if is_visible(look_ang, player_pos, inter):
                dist = distance(inter, player_pos)
                if min_distance > dist > MIN_RENDER_DISTANCE:
                    texture = obj.get_cur_texture(now)
                    shifted = pygame.Vector2(cos(look_ang + pi / 2) * ENTITY_HALF_SIZE + obj.pos.x, -sin(look_ang + pi / 2) * ENTITY_HALF_SIZE + obj.pos.y)
                    units_per_pixel = ENTITY_SIZE / texture.get_width()
                    pixel_row = int(distance(shifted, inter) // units_per_pixel)
                    # for the situation if ray got accurate in end
                    if pixel_row == texture.get_width():
                        pixel_row = 0
                    arr = pygame.PixelArray(texture)
                    line = arr[pixel_row:pixel_row + 1, :].make_surface()
                    layers.append((dist, line, 1000))

    # process projectiles
    for obj in projectiles:
        for line in obj.get_lines():
            if line[1].x == 0:
                k1 = None
            else:
                k1 = line[1].y / line[1].x
                b1 = line[0].y - k1 * line[0].x

            if k is None:
                if k1 is None:
                    continue
                else:
                    x = player_pos.x
                    y = k1 * x + b1
            elif k1 is None:
                x = line[0].x
                y = k * x + b
            else:
                if k1 == k:
                    continue
                else:
                    x = (b1 - b) / (k - k1)
                    y = k * x + b
            inter = pygame.Vector2(x, y)
            vec1 = line[0]
            vec2 = line[0] + line[1] * line[2]
            product = (vec2 - vec1).dot(inter - vec1)
            if 0 < product < line[2] ** 2:
                if is_visible(look_ang, player_pos, inter):
                    dist = distance(inter, player_pos)
                    if min_distance > dist > MIN_RENDER_DISTANCE:
                        layer = pygame.Surface((1, 1))
                        layer.fill(obj.color)
                        layers.append((dist, layer, 50))


    layers.sort(key=lambda l: l[0], reverse=True)
    return layers

def render_image(screen: pygame.Surface, player: Player, walls: list, entities: list, projectiles: list,
                 rays_amount: int, now: int, mode=0):

    pos = player.pos
    look_ang = player.look_ang
    fov = player.fov

    ang_between_rays = fov / rays_amount
    ang = look_ang + fov / 2

    weapon = pygame.transform.scale(player.cur_weapon().get_cur_texture(now), (400, 400))

    for i in range(rays_amount):
        layers = cast_ray(ang, look_ang, pos, walls, entities, projectiles, now)
        width = DISPLAY_RESOLUTION[0] / rays_amount

        if mode == 0:
            pixels = pygame.Surface((ceil(width), DISPLAY_RESOLUTION[1]))
        else:
            height = BLOCK_SIZE / layers[0][0] * 1000
            pixels = pygame.Surface((ceil(width), height))
        pixels.fill("grey")
        for j in layers:
            layer_height = BLOCK_SIZE / j[0] * j[2]
            layer_line = pygame.transform.scale(j[1], (ceil(width), layer_height))
            pixels.blit(layer_line, (0, (DISPLAY_RESOLUTION[1] - layer_height) / 2))

        screen.blit(pixels, (i * width, 0))

        ang -= ang_between_rays
    weapon_pos = ((DISPLAY_RESOLUTION[0] - weapon.get_width()) // 2, DISPLAY_RESOLUTION[1] - weapon.get_height())
    screen.blit(weapon, weapon_pos)
