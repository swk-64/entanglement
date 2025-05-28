import pygame
from math import sin, cos, tan, pi, sqrt


BLOCK_SIZE = 50
RAYS_AMOUNT = 200
DISPLAY_RESOLUTION = (1280, 720)


class Player:
    def __init__(self, name, color, look_ang, pos=pygame.Vector2(0, 0)):
        self.name = name
        self.pos = pos
        self.color = color
        self.vel = pygame.Vector2(0, 0)
        self.look_ang = look_ang
        self.fov = pi / 2


class Block:
    def __init__(self, pos, block_type):
        self.pos = pos
        self.type = block_type
        # (left, right, top, bottom)
        self.borders = (pos.x * BLOCK_SIZE, pos.x * BLOCK_SIZE + BLOCK_SIZE, pos.y * BLOCK_SIZE, pos.y * BLOCK_SIZE + BLOCK_SIZE)


def calculate_look_end_point(ang, length, pos):
    return pygame.Vector2(cos(ang) * length + pos[0], - sin(ang) * length + pos[1])

def distance(point1, point2):
    return sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def is_visible(look_ang, pos, point):
    look_vector = pygame.Vector2(cos(look_ang), -sin(look_ang))
    point_vector = pygame.Vector2(point.x - pos.x, point.y - pos.y)
    zero_vector = pygame.Vector2(0, 0)
    angle_cosine = (cos(look_ang) * (point.x - pos.x) + -sin(look_ang) * (point.y - pos.y)) / distance(zero_vector, look_vector) * distance(zero_vector, point_vector)
    if angle_cosine > 0:
        return True
    return False

def cast_ray(ang, look_ang, start_point, objects):
    min_distance = 65536.0
    for cur_object in objects:
        intersects = []
        left = pygame.Vector2(cur_object.borders[0], tan(-ang) * cur_object.borders[0] + start_point.y + tan(ang) * start_point.x)
        right = pygame.Vector2(cur_object.borders[1], tan(-ang) * cur_object.borders[1] + start_point.y + tan(ang) * start_point.x)
        intersects.append(left)
        intersects.append(right)
        if tan(ang) != 0:
            top = pygame.Vector2((cur_object.borders[2] - start_point.y - tan(ang) * start_point.x) / tan(-ang), cur_object.borders[2])
            bot = pygame.Vector2((cur_object.borders[3] - start_point.y - tan(ang) * start_point.x) / tan(-ang), cur_object.borders[3])
            intersects.append(top)
            intersects.append(bot)
        for inter in intersects:
            if cur_object.borders[0] <= inter[0] <= cur_object.borders[1] and cur_object.borders[2] <= inter[1] <= cur_object.borders[3]:
                if is_visible(look_ang, start_point, inter):
                    if min_distance > distance(inter, start_point):
                        min_distance = distance(inter, start_point)
    return min_distance

def render_image(screen, player_pos, look_ang, fov, objects, rays_amount):
    ang_between_rays = fov / rays_amount
    ang = look_ang - fov / 2

    for i in range(rays_amount):
        dist = cast_ray(ang, look_ang, player_pos, objects)
        height = BLOCK_SIZE / dist * 500
        if height > DISPLAY_RESOLUTION[1]:
            height = DISPLAY_RESOLUTION[1]
        width = DISPLAY_RESOLUTION[0] / rays_amount
        line = pygame.Rect(i * width, (DISPLAY_RESOLUTION[1] - height) / 2, width, height)
        pygame.draw.rect(screen, "white", line)
        ang += ang_between_rays
