#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   util.py
@Time    :   2024/07/25 10:55:52
@Author  :   chenziyang 
@description   :   common tools
"""


import numpy as np
from matplotlib.path import Path

import PythonCDT as cdt


def calculate_midpoint_with2points(points_pos:np.ndarray) -> tuple[np.float64,np.float64]:
    point1 : np.ndarray = points_pos[0]
    point2 : np.ndarray = points_pos[1]
    midpoint : np.ndarray = (point1+point2)/2
    return tuple(midpoint)



def read_input_file(input_file):
    """
    read the process input file
    """
    with open(input_file, "r") as f:
        n_verts, n_edges = (int(s) for s in f.readline().split())
        verts = [
            cdt.V2d(*(float(s) for s in f.readline().split())) for _ in range(n_verts)
        ]
        edges = [
            cdt.Edge(*(int(s) for s in f.readline().split())) for _ in range(n_edges)
        ]
        return verts, edges


def get_compo_center(com_list: list[str]) -> np.ndarray:
    center_x = int(com_list[0])
    center_y = int(com_list[1])
    return np.stack([center_x, center_y])


def cal_only_one_verticles(com_list: list[str]) -> np.ndarray:
    center_x = int(com_list[0])
    center_y = int(com_list[1])
    height = int(com_list[2])
    length = int(com_list[3])

    # calculate the left top verticle and left down verticle
    left_top_ver_x = center_x - length / 2
    left_top_ver_y = center_y + height / 2

    left_down_ver_x = center_x - length / 2
    left_down_ver_y = center_y - height / 2

    # calculate the right top verticle and right down verticle
    right_top_ver_x = center_x + length / 2
    right_top_ver_y = center_y + height / 2

    right_down_ver_x = center_x + length / 2
    right_down_ver_y = center_y - height / 2

    return np.stack(
        (
            [left_top_ver_x, left_top_ver_y],
            [left_down_ver_x, left_down_ver_y],
            [right_down_ver_x, right_down_ver_y],
            [right_top_ver_x, right_top_ver_y],
        )
    )


def cal_four_verticles(com_list: list[list[str]]) -> list[Path]:
    """
    [['20', '20', '15', '15'], ['20', '50', '15', '15'], ['50', '20', '15', '15'], ['50', '40', '15', '15']]
    given a list of component's center[0] [1] and height [2] and length [3]
    return the four points of verticles
    """
    verticle_list: list = []
    for com_pos in com_list:
        center_x = int(com_pos[0])
        center_y = int(com_pos[1])
        height = int(com_pos[2])
        length = int(com_pos[3])

        # calculate the left top verticle and left down verticle
        left_top_ver_x = center_x - length / 2
        left_top_ver_y = center_y + height / 2

        left_down_ver_x = center_x - length / 2
        left_down_ver_y = center_y - height / 2

        # calculate the right top verticle and right down verticle
        right_top_ver_x = center_x + length / 2
        right_top_ver_y = center_y + height / 2

        right_down_ver_x = center_x + length / 2
        right_down_ver_y = center_y - height / 2

        path: Path = Path(
            np.stack(
                (
                    [left_top_ver_x, left_top_ver_y],
                    [left_down_ver_x, left_down_ver_y],
                    [right_down_ver_x, right_down_ver_y],
                    [right_top_ver_x, right_top_ver_y],
                )
            )
        )
        verticle_list.append(path)
    return verticle_list


def cal_four_verticles_v2(com_list: list[list[str]]) -> list[list[int]]:
    """
    [['20', '20', '15', '15'], ['20', '50', '15', '15'], ['50', '20', '15', '15'], ['50', '40', '15', '15']]
    given a list of component's center[0] [1] and height [2] and length [3]
    return the four points of verticles
    """
    verticle_list: list = []
    for com_pos in com_list:
        center_x = int(com_pos[0])
        center_y = int(com_pos[1])
        height = int(com_pos[2])
        length = int(com_pos[3])

        # calculate the left top verticle and left down verticle
        left_top_ver_x = center_x - length / 2
        left_top_ver_y = center_y + height / 2

        left_down_ver_x = center_x - length / 2
        left_down_ver_y = center_y - height / 2

        # calculate the right top verticle and right down verticle
        right_top_ver_x = center_x + length / 2
        right_top_ver_y = center_y + height / 2

        right_down_ver_x = center_x + length / 2
        right_down_ver_y = center_y - height / 2

        path: list = [
            [left_top_ver_x, left_top_ver_y],
            [left_down_ver_x, left_down_ver_y],
            [right_down_ver_x, right_down_ver_y],
            [right_top_ver_x, right_top_ver_y],
        ]
        verticle_list.append(path)
    return verticle_list


if __name__ == "__main__":
    test_input = [
        ["20", "20", "15", "15"],
        ["20", "50", "15", "15"],
        ["50", "20", "15", "15"],
        ["50", "40", "15", "15"],
    ]
    # [['5', '35', '5', '5'], ['45', '65', '5', '5'], ['65', '15', '5', '5']],
    # [['5', '45', '5', '5'], ['15', '5', '5', '5'], ['65', '35', '5', '5']]
    # print(cal_four_verticles_v2(test_input))
    # print(cal_only_one_verticles(test_input[0]))
    print(get_compo_center(test_input[0]))
