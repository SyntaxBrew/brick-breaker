from math import sqrt
from pygame import Color

def clamp(n, min_n, max_n):
    return min(max_n, max(n, min_n))

def get_distance(pos_a: tuple[int, int], pos_b: tuple[int, int]):
    distance_x = pos_b[0] - pos_a[0]
    distance_y = pos_b[1] - pos_a[1]
    return sqrt(distance_x ** 2 + distance_y ** 2)

def darken(color: Color, factor=0.5):
    return Color(
        max(0, min(255, int(color.r * factor))),  # Red component
        max(0, min(255, int(color.g * factor))),  # Green component
        max(0, min(255, int(color.b * factor)))  # Blue component
    )