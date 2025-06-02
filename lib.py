import pygame
from math import sin, cos, pi, sqrt, ceil
from typing import Union


# It is recommended to use 32x48 pixels texture sizes


# constants
DISPLAY_RESOLUTION = (1280, 720)
BLOCK_SIZE = 50
RAYS_AMOUNT = 200
MINIMAP_SCALE = 0.5
MINIMAP_BLOCK_SIZE = BLOCK_SIZE * MINIMAP_SCALE
MIN_RENDER_DISTANCE = 10
ENTITY_SIZE = 50
ENTITY_HALF_SIZE = ENTITY_SIZE / 2

SPAWN_POINT_COLOR = "green"
ENTITY_1_SPAWN_POINT_COLOR = "red"
WALL_COLOR = "white"
FLOOR_COLOR = "grey"
BACKGROUND_COLOR = "black"

PLAYER_COLOR = "yellow"
PLAYER_LOOK_LINE_LEN = BLOCK_SIZE * 4 * MINIMAP_SCALE
PLAYER_COLLISION_SIZE = 15
PLAYER_SPEED = 70
PLAYER_RUN_SPEED_MODIFIER = 2


class Player:
    def __init__(self, name: str, look_ang: float, pos: pygame.Vector2):
        self.name = name
        self.pos = pos
        self.look_ang = look_ang
        self.fov = pi / 2
        self.vel = pygame.Vector2(0, 0)
        self.inventory = list()
        self.curr_inv_slot = 0
        self.inventory_size = 1

    def cur_block(self):
        return int(self.pos.x // BLOCK_SIZE), int(self.pos.y // BLOCK_SIZE)

    def move(self):
        self.pos += self.vel
        self.vel = pygame.Vector2(0, 0)

    def curr_weapon(self):
        return self.inventory[self.curr_inv_slot]

class Weapon:
    def __init__(self, user: Player):
        self.ammo = 100
        self.last_shot = pygame.time.get_ticks()
        self.use_speed = 100
        self.user = user
    def use(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.use_speed:
            self.last_shot = now
            return Projectile(self.user.pos, self.user.look_ang, now)
        return None


class Projectile:
    def __init__(self, pos: pygame.Vector2, ang: float, time):
        self.time = time
        self.decay_time = 1000
        self.speed = 200
        self.color = "red"
        self.length = 20
        self.direction = pygame.Vector2(cos(ang), -sin(ang))
        self.pos = pygame.Vector2(pos.x + cos(ang), pos.y - sin(ang))
    def update(self, dt: float):
        now = pygame.time.get_ticks()
        if now - self.time < self.decay_time:
            self.pos += self.direction * dt * self.speed
            return self
        return None


class Wall:
    def __init__(self, pos: pygame.Vector2, block_type: str, neighbours: tuple, texture: pygame.Surface):
        self.pos = pos
        self.type = block_type

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
        self.texture = texture
    def update_collision(self, obj: Player):
        for collision in self.collisions:
            collision(obj)


class EntityBasicClass:
    def __init__(self, pos: pygame.Vector2, frames_number:int):
        self.pos = pos
        self.frames = list()
        self.frames_number = frames_number
        self.curr_frame_number = 0
        self.animation_speed = 100
        self.last_update = pygame.time.get_ticks()
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            if self.curr_frame_number == self.frames_number - 1:
                self.curr_frame_number = 0
            else:
                self.curr_frame_number += 1
    def get_current_texture(self):
        self.update()
        return self.frames[self.curr_frame_number]


class PelmenKing(EntityBasicClass):
    def __init__(self, pos: pygame.Vector2):
        EntityBasicClass.__init__(self, pos, 12)
        for i in range(12):
            image = pygame.image.load("textures/pelmen_king/" + str(i) + ".png")
            self.frames.append(image.convert_alpha())


class FloorBlock:
    def __init__(self):
        pass
    def update_collision(self, obj):
        pass


class EntitySpawnBlock:
    def __init__(self, pos: pygame.Vector2, entity_type: int):
        self.pos = pos
        self.entity_type = entity_type
        pass
    def update_collision(self, obj):
        pass
    def spawn_entity(self):
        if self.entity_type == 1:
            return PelmenKing(self.pos)
        else:
            raise KeyError




class SpawnBlock:
    def __init__(self):
        pass
    def update_collision(self, obj):
        pass


def update_projectiles(objs:list, dt):
    projectiles = list()
    for obj in objs:
        projectile = obj.update(dt)
        if projectile:
            projectiles.append(projectile)
    return projectiles

def update_collisions(objs: list, level: list):
    for obj in objs:
        block = obj.cur_block()
        try:
            level[block[1] + 1][block[0]].update_collision(obj)
            level[block[1] - 1][block[0]].update_collision(obj)
            level[block[1]][block[0] + 1].update_collision(obj)
            level[block[1]][block[0] - 1].update_collision(obj)
            level[block[1] - 1][block[0] + 1].update_collision(obj)
            level[block[1] + 1][block[0] - 1].update_collision(obj)
            level[block[1] + 1][block[0] + 1].update_collision(obj)
            level[block[1] - 1][block[0] - 1].update_collision(obj)
        except IndexError:
            pass


def minimap_fov_end_point(ang: float, length: float, pos: pygame.Vector2):
    return pygame.Vector2(cos(ang) * length + pos[0], - sin(ang) * length + pos[1])

def distance(point1: Union[pygame.Vector2, tuple], point2: Union[pygame.Vector2, tuple]):
    return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def is_visible(look_ang: float, pos: pygame.Vector2, point: pygame.Vector2):
    player_vec = pygame.Vector2(cos(look_ang), -sin(look_ang))
    point_vec = pygame.Vector2(point.x - pos.x, point.y - pos.y)
    if player_vec.dot(point_vec) > 0:
        return True
    return False

def cast_ray(ang: float, look_ang: float, player_pos: pygame.Vector2, walls: list, entities: list, projectiles: list):
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
                        units_per_pixel = BLOCK_SIZE / (obj.texture.get_width())
                        pixel_row = int(distance(side[0], inter) / units_per_pixel)
                        arr = pygame.PixelArray(obj.texture)
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
                    texture = obj.get_current_texture()
                    shifted = pygame.Vector2(cos(look_ang + pi / 2) * ENTITY_HALF_SIZE + obj.pos.x, -sin(look_ang + pi / 2) * ENTITY_HALF_SIZE + obj.pos.y)
                    units_per_pixel = ENTITY_SIZE / texture.get_width()
                    pixel_row = int(distance(shifted, inter) / units_per_pixel)
                    arr = pygame.PixelArray(texture)
                    line = arr[pixel_row:pixel_row + 1, :].make_surface()
                    layers.append((dist, line, 1000))

    # process projectiles
    for obj in projectiles:
        if obj.direction.x == 0:
            k1 = None
        else:
            k1 = obj.direction.y / obj.direction.x
            b1 = obj.pos.y - k1 * obj.pos.x

        if k is None:
            if k1 is None:
                continue
            else:
                x = player_pos.x
                y = k1 * x + b1
        elif k1 is None:
            x = obj.pos.x
            y = k * x + b
        else:
            if k1 == k:
                continue
            else:
                x = (b1 - b) / (k - k1)
                y = k * x + b
        inter = pygame.Vector2(x, y)
        vec1 = obj.pos
        vec2 = obj.pos + obj.direction * obj.length
        product = (vec2 - vec1).dot(inter - vec1)
        if 0 < product < obj.length ** 2:
            if is_visible(look_ang, player_pos, inter):
                dist = distance(inter, player_pos)
                if min_distance > dist > MIN_RENDER_DISTANCE:
                    color = pygame.Surface((1, 1))
                    color.fill(obj.color)
                    layers.append((dist, color, 50))


    layers[1:].sort(key=lambda l: l[0])
    return layers

def render_image(screen: pygame.Surface, player_pos: pygame.Vector2, look_ang: float, fov: float, walls: list,
                 entities: list, projectiles: list, rays_amount: int, mode=0):
    ang_between_rays = fov / rays_amount
    ang = look_ang + fov / 2

    for i in range(rays_amount):
        layers = cast_ray(ang, look_ang, player_pos, walls, entities, projectiles)
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
