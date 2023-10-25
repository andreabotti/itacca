import colorsys
import random
import plotly.graph_objects as go






def generate_random_rgb():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def rgb_to_hsv(rgb):
    normalized = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    return colorsys.rgb_to_hsv(*normalized)

def hsv_to_rgb(hsv):
    rgb = colorsys.hsv_to_rgb(*hsv)
    return (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))



def create_color_pools(num_colors, num_pools):
    # Generate random colors
    # num_colors = 100
    colors_rgb = [generate_random_rgb() for _ in range(num_colors)]
    colors_hsv = [rgb_to_hsv(color) for color in colors_rgb]

    # Sort colors by hue
    sorted_colors_hsv = sorted(colors_hsv, key=lambda x: x[0])
    sorted_colors_rgb = [hsv_to_rgb(hsv) for hsv in sorted_colors_hsv]

    # Create color pools (For this example, let's say we want 10 pools)
    # num_pools = 10
    pool_size = num_colors // num_pools
    color_pools = [sorted_colors_rgb[i:i+pool_size] for i in range(0, num_colors, pool_size)]

    return color_pools