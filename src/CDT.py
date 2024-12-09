#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   CDT.py
@Time    :   2024/07/24 17:43:48
@Author  :   chenziyang 
@description   :   create CDT model
"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
from scipy.spatial import Delaunay
from shapely.geometry import Point, Polygon

import PythonCDT as cdt
from Dataset import Dataset
from util import read_input_file


class chipCDT:
    """
    construct the CDT
    """

    def __init__(self, file_path: str, input_path: str, ratio: float) -> None:
        """
        init the CDT graph
        """
        data = Dataset(file_path, input_path, ratio)
        process_data_path, _, _ = data.write_fixed_data()

        self.vv, self.ee = read_input_file(process_data_path)
        self.CDT = cdt.Triangulation(
            cdt.VertexInsertionOrder.AS_PROVIDED,
            cdt.IntersectingConstraintEdges.TRY_RESOLVE,
            0.0,
        )
        self.CDT.insert_vertices(self.vv)
        self.CDT.insert_edges(self.ee)
        self.CDT.erase_outer_triangles_and_holes()

    def get_all_points(self) -> np.ndarray:
        """
        get an ndarray of all points
        """
        all_vec_list = []
        for vec in self.vv:
            all_vec_list.append([vec.x, vec.y])
        self.all_vec_arr = np.array(all_vec_list)

        return self.all_vec_arr

    def get_all_triangles(self) -> np.ndarray:
        """
        get an ndarray of all index of triangles
        """
        final_list = []
        for tri in self.CDT.triangles:
            final_list.append(tri.vertices)

        self.final_arr = np.array(final_list)
        return self.final_arr

    def dispaly_cdt(self) -> None:
        """
        display the CDT graph
        """
        all_vec_arr = self.get_all_points()
        final_arr = self.get_all_triangles()
        plt.triplot(all_vec_arr[:, 0], all_vec_arr[:, 1], final_arr, label="CDT line")
        plt.scatter(all_vec_arr[:, 0], all_vec_arr[:, 1], color="green", label="Points")
        plt.legend(loc="upper center")
        print("[*] draw the CDT and search SG graph successfully!")
        plt.show()


if __name__ == "__main__":
    t = chipCDT("Data\data5.txt", "Data\input5.txt", 0.6)
    t.dispaly_cdt()
