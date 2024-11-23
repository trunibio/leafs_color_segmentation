import os
from PIL import Image

from sklearn.cluster import KMeans

import numpy as np
import fitz


def read_file(dir_path, filename):
    """
    Read image from pdf or one of png, jpg, jpeg formats 
    to the image_dict structure.
    Input
        - dir_path: str, address of dir, where the file to be read is located
        - filename: str, name of the file to be read
    Output
        - image_dict: {'filename': sample_filename, 'image': sample_image}
        sample_image is a np.array of shape (heigh, width, 3)
    """
    
    image_dict = {'filename': filename, 'image': None}
    if filename.lower().split('.')[-1] in ['png', 'jpg', 'jpeg']:
        file_path = os.path.join(dir_path, filename)
        im = np.array(Image.open(file_path))
        image_dict['image'] = im 
    
    return image_dict


def map_colors(pixel_classes, class_colors_to_display):
    """
    Map RGB colors to pixel color classes in the input matrix
    
    Input
    - pixel_classes: np.array of shape im_height, im_width, 1 - color classes of each pixels
    - class_colors_to_display: list of dicts - see const.class_colors_to_display
    
    Output
    - out_image: np.array of shape (im_height, im_width, 3), where 3 stands for 3 RGB channels
    """
    out_image = [class_colors_to_display[pixel_class] for row in pixel_classes for pixel_class in row]
    return out_image


def calculate_pixel_classes(image_input, colors_base_list):
    """
    Calculate pixel class to each pixel of input image base on which 
    color from colors_base_list is the closest to pixel color in the RGB space.
    
    Input
    - image_input: np.array of shape (im_height, im_width, 3), where 3 stands for 3 RGB channels
    - colors_base_list: list of dicts - see const.colors
    
    Output
    - pixel_classes_reshaped: np.array of shape im_height, im_width, 1 - color classes of each pixels
        color_class number is given by the order of specific base_color in cons.color list
    
    NOTE: k-means algo is only used for easy pixel distances calculation in the RGB space. 
    We do not really use k-means algo to determine clusters.
    """
    # Get only list of base_colors rgb codes
    clusters_base_colors = [d['color_rgb'] for d in colors_base_list]
    kmeans = KMeans(n_clusters=len(clusters_base_colors), init=clusters_base_colors).fit(clusters_base_colors)

    # Transform all pixels to the 2D array of RGB triplets
    pixel_array = image_input.reshape((-1, 3)).astype(np.int32)
    
    # Predict class for each pixel (closses of predefined colors)
    pixel_classes = kmeans.predict(pixel_array)
    
    # Reshape resul to the same shape as input_image
    height, width, _ = image_input.shape
    pixel_classes_reshaped = pixel_classes.reshape((height, width))
    return pixel_classes_reshaped


def calculate_image_statistics(pixel_classes_im_shape, colors_base_list, n_green_orders):
    """
    Calculate what part of leaf is green (green_ratio), what part of image is leaf (leaf_ratio)
    and what green class is leaf (green_class).
    
    Input
    - pixel_classes_im_shape: np.array of shape (im_height, im_width, 3), where 3 stands for 3 RGB channels
    - colors_base_list: list of dicts - see const.colors
    - n_green_orders: int, to how many classes should green_ratio be divided, see green_class
        
    
    Output
    - green_ratio: float from [0, 1] - what part of leaf is assigned green class
    - leaf_ratio: float from [0, 1] - what part of image is leaf (i.e. pixels which are not background)
    - green_class: int, from [1, n_green_orders]
        1 means, that green ratio is [0 to 1/n_green_orders)
        n_green_orders means, that green ratio is [1 - 1/n_green_orders, 1)
    """
    # Get dict of which color group -> has which color indices (order of base color in const.colors list)
    # classes_group_dict look like: {0: [0, 1], 1: [2, 3, 4, 5], 2: [6, 7, 8]}
    classes_group_dict = {}
    for color_class_index, d in enumerate(colors_base_list):
        if d['color_group'] in classes_group_dict:
            classes_group_dict[d['color_group']].append(color_class_index)
        else:
            classes_group_dict[d['color_group']] = []

    pixel_classes = pixel_classes_im_shape.reshape(-1)
    group_counts_dict = {}
    for group_class_index, group_pixel_classes_list in classes_group_dict.items():
        group_counts_dict[group_class_index] = sum([pixel_classes == class_index for class_index in group_pixel_classes_list]).sum()

    green_ratio = group_counts_dict[1] / (group_counts_dict[1] + group_counts_dict[2])
    leaf_ratio = (group_counts_dict[1] + group_counts_dict[2]) / (group_counts_dict[0] + group_counts_dict[1] + group_counts_dict[2])
    green_pct = round(green_ratio * 100)
    # green_class = n_green_orders - int(green_pct // (int(100 / n_green_orders)))
    green_class = get_green_class(green_pct)
    return green_ratio, leaf_ratio, green_class


def get_green_class(green_pct):
    """
    Assigns green class to green_pct based on rules below
    
    Inupt
    - green_pct: float, <0,100> describes what portion of leaf is green
    
    Output
    - green_class: int, 1-7 describing portion part of leaf is green
    """
    green_class = -1
    brown_pct = 100 - green_pct
    
    if brown_pct >= 0 and brown_pct < 2:
        green_class = 0
    elif brown_pct >= 2 and brown_pct < 5:
        green_class = 1
    elif brown_pct >= 5 and brown_pct < 10:
        green_class = 2
    elif brown_pct >= 10 and brown_pct < 25:
        green_class = 3
    elif brown_pct >= 25 and brown_pct < 50:
        green_class = 4
    elif brown_pct >= 50 and brown_pct < 75:
        green_class = 5
    elif brown_pct >= 75 and brown_pct < 98:
        green_class = 6
    elif brown_pct >= 98 and brown_pct <= 100:
        green_class = 7
    return green_class