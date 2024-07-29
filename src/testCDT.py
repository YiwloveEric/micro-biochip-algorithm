#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   testCDT.py
@Time    :   2024/07/25 10:26:10
@Author  :   chenziyang 
@description   :   test CDT
"""

import matplotlib.pyplot as plt
import numpy as np

import PythonCDT as cdt
from Dataset import *
from util import *

# vv, ee = read_input_file("Data\data1.txt_tmp")
vv, ee = read_input_file(r"Data\data1 copy.txt_tmp")
t = cdt.Triangulation(
    cdt.VertexInsertionOrder.AS_PROVIDED,
    cdt.IntersectingConstraintEdges.TRY_RESOLVE,
    0.0,
)
t.insert_vertices(vv)
t.insert_edges(ee)
# t.conform_to_edges(ee)
t.erase_outer_triangles_and_holes()
# print(vv)
# print(t.triangles)
# print('\n')
all_vec_list = []
for vec in vv:
    all_vec_list.append([vec.x, vec.y])
# print(all_vec_list)
all_vec_arr = np.array(all_vec_list)
print(all_vec_arr)
final_list = []
for tri in t.triangles:
    final_list.append(tri.vertices)

# print(final_list)
final_arr = np.array(final_list)
print(final_arr)

plt.triplot(all_vec_arr[:, 0], all_vec_arr[:, 1], final_arr, color="blue", label="FT")
plt.scatter(all_vec_arr[:, 0], all_vec_arr[:, 1], color="green", label="Points")
plt.legend()
plt.show()
