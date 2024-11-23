import numpy as np

colors = [{'color_group': 0, 'color_rgb': [255, 255, 255]}, # white
          {'color_group': 0, 'color_rgb': [208, 219, 225]}, # white 2
          {'color_group': 1, 'color_rgb': [77, 109, 46]}, # green 1
          {'color_group': 1, 'color_rgb': [94, 95, 63]}, # green 2
          {'color_group': 1, 'color_rgb': [85, 107, 47]}, # green 3
          {'color_group': 1, 'color_rgb': [60, 71, 25]}, # green 4
          {'color_group': 2, 'color_rgb': [166, 133, 81]}, # brown 1
          {'color_group': 2, 'color_rgb': [188, 141, 111]}, # brown 2
          {'color_group': 2, 'color_rgb': [79, 61, 37]}, # brown 3
          {'color_group': 2, 'color_rgb': [116, 97, 65]},
         ]

# define which group of classes is displayed by which color
group_colors_to_display = {
    0: np.array([255, 0, 0]),
    1: np.array([0, 255, 0]),
    2: np.array([0, 0, 255]),
}

"""
Dict saying which color from colors list will be mapped to which color
e.g. 0-th color - white [255, 255, 255] will be mapped to [255, 0, 0] red
all three green colors will be mapped to green [0, 255, 0]
This creates dict of a form class_index: rgb_color_np_array
{0: array([255,   0,   0]),
 1: array([255,   0,   0]),
 2: array([  0, 255,   0]),
 ...}
 """
class_colors_to_display = {cl_index: group_colors_to_display[color_dict['color_group']] for cl_index, color_dict in enumerate(colors)}

base_images_dir = './105 listov_/'
# base_images_dir = './leaf_input_data/'

image_size_cm = 625 # A4 paper format has 620 cm^2

N_green_classes = 7 # To how many classes leaf green area percentage will be splited.