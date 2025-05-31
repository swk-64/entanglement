import pygame
from math import sin, cos, tan, pi, sqrt, ceil
from typing import Union

from pygame import Vector2

# constants
DISPLAY_RESOLUTION = (1280, 720)
BLOCK_SIZE = 50
RAYS_AMOUNT = 200
MINIMAP_SCALE = 0.5
PLAYER_SPEED = 70
MINIMAP_BLOCK_SIZE = BLOCK_SIZE * MINIMAP_SCALE
MIN_RENDER_DISTANCE = 15
ENTITY_SIZE = 50
ENTITY_HALF_SIZE = ENTITY_SIZE / 2

SPAWN_POINT_COLOR = "green"
ENTITY_1_SPAWN_POINT_COLOR = "red"
WALL_COLOR = "white"
FLOOR_COLOR = "grey"
BACKGROUND_COLOR = "black"

PLAYER_COLOR = "yellow"
PLAYER_LOOK_LINE_LEN = BLOCK_SIZE * 4 * MINIMAP_SCALE
PLAYER_COLLISION_SIZE = 10


class Player:
    def __init__(self, name: str, color: str, look_ang: float, pos=pygame.Vector2(0, 0)):
        self.name = name
        self.pos = pos
        self.color = color
        self.look_ang = look_ang
        self.fov = pi / 2
        self.vel = pygame.Vector2(0, 0)

    def cur_block(self):
        return int(self.pos.x // BLOCK_SIZE), int(self.pos.y // BLOCK_SIZE)

    def move(self):
        self.pos += self.vel
        self.vel = pygame.Vector2(0, 0)


class Wall:
    def __init__(self, pos: pygame.Vector2, block_type: str, texture: pygame.Surface):
        self.pos = pos
        self.type = block_type
        # the elements near connected between each other
        self.points = [(pos.x - BLOCK_SIZE / 2, pos.y - BLOCK_SIZE / 2), (pos.x + BLOCK_SIZE / 2, pos.y - BLOCK_SIZE / 2),
                       (pos.x + BLOCK_SIZE / 2, pos.y + BLOCK_SIZE / 2),
                       (pos.x - BLOCK_SIZE / 2, pos.y + BLOCK_SIZE / 2), (pos.x - BLOCK_SIZE / 2, pos.y - BLOCK_SIZE / 2)]
        self.texture = texture
    def update_collision(self, obj: Player):
        if self.pos.x - BLOCK_SIZE / 2 <= obj.pos.x <= self.pos.x + BLOCK_SIZE / 2:
            # top
            if self.pos.y + BLOCK_SIZE / 2 <= obj.pos.y <= self.pos.y + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                if obj.vel.y < 0:
                    obj.vel += pygame.Vector2(0, -obj.vel.y)

            # bottom
            if self.pos.y - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE <= obj.pos.y <= self.pos.y - BLOCK_SIZE / 2:
                if obj.vel.y > 0:
                    obj.vel += pygame.Vector2(0, -obj.vel.y)

        if self.pos.y - BLOCK_SIZE / 2 <= obj.pos.y <= self.pos.y + BLOCK_SIZE / 2:
            # left
            if self.pos.x - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE <= obj.pos.x <= self.pos.x - BLOCK_SIZE / 2:
                if obj.vel.x > 0:
                    obj.vel += pygame.Vector2(-obj.vel.x, 0)
            #right
            if self.pos.x + BLOCK_SIZE / 2 <= obj.pos.x <= self.pos.x + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                if obj.vel.x < 0:
                    obj.vel += pygame.Vector2(-obj.vel.x, 0)

        if self.pos.x + BLOCK_SIZE / 2 < obj.pos.x < self.pos.x + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
            # top-right
            if self.pos.y + BLOCK_SIZE / 2 < obj.pos.y < self.pos.y + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                vec = pygame.Vector2(-1, -1)
                if vec.dot(obj.vel) > 0:
                    vec.scale_to_length(vec.dot(obj.vel)/(vec.magnitude()*obj.vel.magnitude()) * obj.vel.magnitude())
                    obj.vel -= vec
            # bottom-right
            if self.pos.y - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE < obj.pos.y < self.pos.y - BLOCK_SIZE / 2:
                vec = pygame.Vector2(-1, 1)
                if vec.dot(obj.vel) > 0:
                    vec.scale_to_length(vec.dot(obj.vel)/(vec.magnitude()*obj.vel.magnitude()) * obj.vel.magnitude())
                    obj.vel -= vec

        if self.pos.x - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE < obj.pos.x < self.pos.x - BLOCK_SIZE / 2:
            # top-left
            if self.pos.y + BLOCK_SIZE / 2 < obj.pos.y < self.pos.y + BLOCK_SIZE / 2 + PLAYER_COLLISION_SIZE:
                vec = pygame.Vector2(1, -1)
                if vec.dot(obj.vel) > 0:
                    vec.scale_to_length(
                        vec.dot(obj.vel) / (vec.magnitude() * obj.vel.magnitude()) * obj.vel.magnitude())
                    obj.vel -= vec
            # bottom-left
            if self.pos.y - BLOCK_SIZE / 2 - PLAYER_COLLISION_SIZE < obj.pos.y < self.pos.y - BLOCK_SIZE / 2:
                vec = pygame.Vector2(1, 1)
                if vec.dot(obj.vel) > 0:
                    vec.scale_to_length(
                        vec.dot(obj.vel) / (vec.magnitude() * obj.vel.magnitude()) * obj.vel.magnitude())
                    obj.vel -= vec

class Entity:
    def __init__(self, pos: pygame.Vector2, texture: pygame.Surface):
        self.pos = pos
        self.texture = texture
        self.collision = None


class FloorBlock:
    def __init__(self):
        pass
    def update_collision(self, obj):
        pass


class SpawnBlock:
    def __init__(self):
        pass
    def update_collision(self, obj):
        pass


class EntitySpawnBlock:
    def __init__(self):
        pass
    def update_collision(self, obj):
        pass


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
    vec = pygame.Vector2(cos(look_ang), -sin(look_ang))
    point_vec = pygame.Vector2(point.x - pos.x, point.y - pos.y)
    zero_vec = pygame.Vector2(0, 0)
    angle_cosine = (cos(look_ang) * (point.x - pos.x) + -sin(look_ang) * (point.y - pos.y)) / distance(zero_vec, vec) * distance(zero_vec, point_vec)
    if angle_cosine > 0:
        return True
    return False

def cast_ray(ang: float, look_ang: float, start_point: pygame.Vector2, objects: list, screen):
    min_distance = 65536.0
    filler = pygame.Surface((1, 1))
    filler.fill("white")
    pixels = filler
    look_vec = pygame.Vector2(cos(ang) + start_point[0], -sin(ang) + start_point[1])
    k1 = (look_vec.y - start_point.y) / (look_vec.x - start_point.x)
    b1 = start_point.y - k1 * start_point.x
    for obj in objects:
        if type(obj) == Wall:
            for i in range(len(obj.points) - 1):
                try:
                    k2 = (obj.points[i + 1][1] - obj.points[i][1]) / (obj.points[i + 1][0] - obj.points[i][0])
                    b2 = obj.points[i][1] - k2 * obj.points[i][0]
                    y = obj.points[i][1]
                    x = (b2 - b1) / (k1 - k2)

                    # strange behavior if replace k2 and b2 by k1 and b1
                    y = k2 * x + b2
                except ZeroDivisionError:
                    x = obj.points[i][0]
                    y = k1 * x + b1
                inter = pygame.Vector2(x, y)
                if obj.points[0][0] <= inter.x <= obj.points[1][0] and obj.points[1][1] <= inter.y <= obj.points[2][1]:
                    if is_visible(look_ang, start_point, inter):
                        if min_distance > distance(inter, start_point):
                            min_distance = distance(inter, start_point)
                            units_per_pixel = BLOCK_SIZE / (obj.texture.get_width() - 1)
                            pixel_row = round(distance(obj.points[i], inter) / units_per_pixel)
                            arr = pygame.PixelArray(obj.texture)
                            pixels = arr[pixel_row:pixel_row + 1, :].make_surface()

        elif type(obj) == Entity:
            vec = pygame.Vector2(cos(look_ang) + start_point[0], -sin(look_ang) + start_point[1])
            k = (vec.y - start_point.y) / (vec.x - start_point.x)
            try:
                k2 = - 1 / k
                b2 = obj.pos.y - k2 * obj.pos.x
                x = (b2 - b1) / (k1 - k2)
                y = k2 * x + b2
            except ZeroDivisionError:
                x = obj.pos.x
                y = start_point.y

            inter = pygame.Vector2(x, y)
            if (obj.pos.x - inter[0]) ** 2 + (obj.pos.y - inter[1]) ** 2 < ENTITY_HALF_SIZE**2:
                if is_visible(look_ang, start_point, inter):
                    if min_distance > distance(inter, start_point) > MIN_RENDER_DISTANCE:
                        min_distance = distance(inter, start_point)
                        shifted = pygame.Vector2(-cos(look_ang + pi / 2) * ENTITY_HALF_SIZE + obj.pos.x, sin(look_ang + pi / 2) * ENTITY_HALF_SIZE + obj.pos.y)
                        units_per_pixel = ENTITY_SIZE / (obj.texture.get_width() - 1)
                        pixel_row = round(distance(shifted, inter) / units_per_pixel)
                        arr = pygame.PixelArray(obj.texture)
                        pixels = arr[pixel_row:pixel_row + 1, :].make_surface()


    return min_distance, pixels

def render_image(screen: pygame.Surface, player_pos: pygame.Vector2, look_ang: float, fov: float, objects: list, rays_amount: int):
    ang_between_rays = fov / rays_amount
    ang = look_ang - fov / 2

    for i in range(rays_amount):
        dist, pixels = cast_ray(ang, look_ang, player_pos, objects, screen)
        height = BLOCK_SIZE / dist * 800
        width = DISPLAY_RESOLUTION[0] / rays_amount
        line = pygame.transform.scale(pixels, (ceil(width), height))
        screen.blit(line, (i * width, (DISPLAY_RESOLUTION[1] - height) / 2))
        ang += ang_between_rays
