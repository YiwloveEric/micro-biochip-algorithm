#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   testCDT.py
@Time    :   2024/07/25 10:26:10
@Author  :   chenziyang 
@description   :   test CDT
'''

import PythonCDT as cdt
from Dataset import *


vv, ee = read_input_file("Data\data1.txt_tmp")
t = cdt.Triangulation(cdt.VertexInsertionOrder.AS_PROVIDED, cdt.IntersectingConstraintEdges.TRY_RESOLVE, 0.0)
t.insert_vertices(vv)
# t.conform_to_edges(ee)
# t.erase_outer_triangles_and_holes()
print(t.triangles)