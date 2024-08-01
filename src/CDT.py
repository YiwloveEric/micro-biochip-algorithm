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

    def __init__(self, file_path: str) -> None:
        """
        init the CDT graph
        """
        data = Dataset(file_path)
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


class CDT:
    """
    construct the CDT
    """

    def __init__(
        self,
        constraint: list[Path],
        boundary: list = [[0, 0], [0, 70], [70, 0], [70, 70]],
    ) -> None:
        """
        init the points and constraint set
        """

        warnings.warn(
            "该类已被废弃,将在未来的版本中移除。请使用chipCDT代替。",
            DeprecationWarning,
            stacklevel=2,
        )

        point: list = []
        self.point = np.array([])
        self.constraint: list[Path] = constraint
        for pt in self.constraint:
            point.extend(pt.vertices)
        point.extend(boundary)
        self.point = np.array(point)
        # (44, 2) 10
        # print(self.point.shape,len(self.constraint))

    def generate_cdt(self) -> None:
        """
        Main function to generate the CDT.
        Has been deprecated!! use the newone
        """

        warnings.warn(
            "该方法已被废弃,将在未来的版本中移除。请使用chipCDT.generateCDT()代替。",
            DeprecationWarning,
            stacklevel=2,
        )

        points: np.array = self.point
        constraint: list[Path] = self.constraint

        # Initialize Delaunay triangulation
        tri = Delaunay(points)

        # Filter out triangles that are inside the polygon
        filtered_triangles = []
        for simplex in tri.simplices:
            triangle = points[simplex]
            if not CDT.is_triangle_in_polygon(triangle, constraint):
                filtered_triangles.append(simplex)

        if not filtered_triangles:
            print("No valid triangles for all triangles in the constrait polygon!")
        else:
            # Create a new set of points only containing valid triangles
            # Flatten and get unique points
            valid_points_indices = np.unique(np.concatenate(filtered_triangles))
            new_points = points[valid_points_indices]
            new_tri = Delaunay(new_points)

            # Plot the original and new triangulation
            plt.triplot(
                points[:, 0],
                points[:, 1],
                tri.simplices,
                color="red",
                label="Original Triangulation",
            )
            plt.triplot(
                new_points[:, 0],
                new_points[:, 1],
                new_tri.simplices,
                color="blue",
                label="Filtered Triangulation",
            )

        # Plot points
        plt.scatter(points[:, 0], points[:, 1], color="green", label="Points")

        plt.legend()
        plt.show()

    @staticmethod
    def is_triangle_in_polygon(triangle: np.array, polygon: list[Path]) -> bool:
        """Check if the triangle is inside the polygon."""

        # 提取每个 Path 对象的坐标并构造 Polygon
        polygon_coords = []
        for path in polygon:
            if isinstance(path, Path):
                polygon_coords.append(path.vertices.tolist())  # 提取坐标并添加到列表中
            else:
                raise TypeError("Expected Path object")

        # 确保坐标列表有正确的格式
        if polygon_coords:
            for poly_list in polygon_coords:
                poly = Polygon(poly_list)
                all_points_inside = True
                for pt in triangle:
                    # 比较单个三角形的每个顶点是否在给定poly顶点
                    point = Point(pt)
                    if not poly.intersects(point):
                        all_points_inside = False
                        break
                if all_points_inside:
                    return True
            return False
        else:
            raise ValueError("No coordinates found in the provided paths")


if __name__ == "__main__":
    t = chipCDT("Data\data3.txt")
    t.dispaly_cdt()
