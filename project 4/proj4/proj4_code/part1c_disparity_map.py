#!/usr/bin/python3

"""Calculates disparity maps."""

from typing import Callable, Tuple

import numpy as np
import torch


def calculate_disparity_map(
    left_img: torch.Tensor,
    right_img: torch.Tensor,
    block_size: int,
    sim_measure_function: Callable,
    max_search_bound: int = 50,
) -> torch.Tensor:
    """
    Calculate the disparity value at each pixel by searching a small patch
    around a pixel from the left image in the right image.

    Note:
    1. It is important for this project to follow the convention of search
       input in left image and search target in right image
    2. While searching for disparity value for a patch, it may happen that
       there are multiple disparity values with the minimum value of the
       similarity measure. In that case we need to pick the smallest disparity
       value. Please check the numpy's argmin and pytorch's argmin carefully.
       Example:
       -- diparity_val -- | -- similarity error --
       -- 0               | 5
       -- 1               | 4
       -- 2               | 7
       -- 3               | 4
       -- 4               | 12

       In this case we need the output to be 1 and not 3.
    3. The max_search_bound is defined from the patch center.

    Args:
        left_img: image Tensor of shape (H,W,C) from the left stereo camera.
            C will be >= 1
        right_img: image Tensor of shape (H,W,C) from the right stereo camera
        block_size: the size of the block to be used for searching between the
            left and right image (should be odd)
        sim_measure_function: a function to measure similarity measure between
            two tensors of the same shape; returns the error value
        max_search_bound: the maximum horizontal distance (in terms of pixels)
            to use for searching
    Returns:
        disparity_map: The map of disparity values at each pixel. Tensor of
            shape (H-2*(block_size//2),W-2*(block_size//2))
    """

    assert left_img.shape == right_img.shape
    disp_map = torch.zeros(1)  # placeholder, this is not the actual size

    ###########################################################################
    # Student code begins
    ###########################################################################

    H, W, C = left_img.shape
    small = block_size // 2
    disp_map = torch.zeros(H - 2 * small, W - 2 * small)

    for y in range(small, H - small):
      for x in range(small, W - small):
          min_err = np.inf
          min_err_disp = 0

          offset = min(x - small, max_search_bound) 
          for disp in range(0, offset + 1):
            err = sim_measure_function(left_img[y - small : y+ small + 1, x - small : x + small + 1],
                right_img[y - small : y+ small + 1, x - small - disp : x + small - disp + 1])
            if err < min_err: # use small disparity val
                min_err = err
                min_err_disp = disp 

          disp_map[y - small, x - small] = min_err_disp

    ###########################################################################
    # Student code ends
    ###########################################################################
    return disp_map


def calculate_cost_volume(
    left_img: torch.Tensor,
    right_img: torch.Tensor,
    max_disparity: int,
    sim_measure_function: Callable,
    block_size: int = 9,
):
    """
    Calculate the cost volume. Each pixel will have D=max_disparity cost values
    associated with it. Basically for each pixel, we compute the cost of
    different disparities and put them all into a tensor.

    Note:
    1. It is important for this project to follow the convention of search
       input in left image and search target in right image
    2. If the shifted patch in the right image will go out of bounds, it is
       good to set the default cost for that pixel and disparity to be
       something high (we recommend 255) so that when we consider costs, valid
       disparities will have a lower cost.

    Args:
        left_img: image Tensor of shape (H,W,C) from the left stereo camera.
            C will be 1 or 3.
        right_img: image Tensor of shape (H,W,C) from the right stereo camera
        max_disparity: represents the range of disparity values we will
            consider (0 to max_disparity-1)
        sim_measure_function: a function to measure similarity measure between
            two tensors of the same shape; returns the error value
        block_size: the size of the block to be used for searching between the
            left and right image, it should be odd
    Returns:
        cost_volume: The cost volume tensor of shape (H,W,D). H,W are image
            dimensions, and D is max_disparity. cost_volume[x,y,d] represents
            the similarity or cost between a patch around left[x,y] and a patch
            shifted by disparity d in the right image.
    """
    # placeholders
    H = left_img.shape[0]
    W = right_img.shape[1]
    cost_volume = torch.zeros(H, W, max_disparity)

    ###########################################################################
    # Student code begins
    ###########################################################################

    H, W, C = left_img.shape
    small = block_size // 2
    cost_volume = torch.zeros(H - 2 * small, W - 2 * small, max_disparity)

    for y in range(small, H - small):
          for x in range(small, W - small):
              D = torch.ones(max_disparity,) * 255

              offset = min(x - small, max_disparity - 1) 
              for disp in range(0, offset + 1):
                err = sim_measure_function(left_img[y - small : y+ small + 1, x - small : x + small + 1],
                    right_img[y - small : y+ small + 1, x - small - disp : x + small - disp + 1])
                D[disp] = err

              cost_volume[y - small, x - small] = D


    ###########################################################################
    # Student code ends
    ###########################################################################

    return cost_volume
