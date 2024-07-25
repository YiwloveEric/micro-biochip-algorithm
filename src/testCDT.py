#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   testCDT.py
@Time    :   2024/07/25 10:26:10
@Author  :   chenziyang 
@description   :   test CDT
'''

import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from matplotlib.path import Path

# 创建点集
points = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2],
                   [2, 0], [2, 1], [2, 2], [1, 1.5], [1.5, 1], [2, 1.5], [1.5, 2]])

# 进行德劳内三角剖分
tri = Delaunay(points)

# 创建一个多边形，表示要删除的约束区域
polygon = Path([(1, 0), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)])

# 定义一个函数，用来判断三角形是否与多边形相交
def is_triangle_in_polygon(triangle, polygon):
    # 如果三角形的任意一个顶点在多边形内，就返回真
    for vertex in triangle:
        if polygon.contains_point(vertex):
            return True
    return False

# 筛选出在多边形之外的三角形
filtered_triangles = []
for simplex in tri.simplices:
    triangle = points[simplex]
    if not is_triangle_in_polygon(triangle, polygon):
        filtered_triangles.append(simplex)

# 检查是否有有效的三角形
if not filtered_triangles:
    print("没有有效的三角形，一般是因为所有三角形都在多边形中。")
else:
    # 创建一个新的点集，只包含有效的三角形
    new_points = points[np.unique(filtered_triangles)]  # 确保只提取唯一的点
    new_tri = Delaunay(new_points)

    # 可视化结果
    # plt.triplot(points[:, 0], points[:, 1], tri.simplices, color='blue', label='original')
    plt.triplot(new_points[:, 0], new_points[:, 1], new_tri.simplices, color='red', label='new')

    # 添加多边形边界
    plt.plot(*zip(*polygon.vertices), 'k--', label='delete')
    plt.scatter(points[:, 0], points[:, 1], color='green')
    plt.legend()
    plt.show()



