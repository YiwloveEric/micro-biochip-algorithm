#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   CDT.py
@Time    :   2024/07/24 17:43:48
@Author  :   chenziyang 
@description   :   create CDT model
'''

import numpy as np
from matplotlib.path import Path
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from Dataset import *
from shapely.geometry import Polygon, Point

class CDT:
    """
    construct the CDT
    """

    def __init__(self, constraint:list[Path],boundary:list = [[0,0],[0,70],[70,0],[70,70]]) -> None:
        """
        init the points and constraint set
        """
        point : list = [] 
        self.point = np.array([])
        self.constraint : list[Path] = constraint
        for pt in self.constraint:
            point.extend(pt.vertices)
        point.extend(boundary)
        self.point = np.array(point)
        # (44, 2) 10
        # print(self.point.shape,len(self.constraint))


    def generate_cdt(self) -> None:
        """
        Main function to generate the CDT.
        """
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
            print("没有有效的三角形，一般是因为所有三角形都在多边形中。")
        else:
            # Create a new set of points only containing valid triangles
            # Flatten and get unique points
            valid_points_indices = np.unique(np.concatenate(filtered_triangles))
            new_points = points[valid_points_indices]
            new_tri = Delaunay(new_points)

            # Plot the original and new triangulation
            plt.triplot(points[:, 0], points[:, 1], tri.simplices, color='red', label='Original Triangulation')
            plt.triplot(new_points[:, 0], new_points[:, 1], new_tri.simplices, color='blue', label='Filtered Triangulation')

        # Plot points
        plt.scatter(points[:, 0], points[:, 1], color='green', label='Points')

        plt.legend()
        plt.show()

    @staticmethod
    def is_triangle_in_polygon(triangle: np.array, polygon: list[Path]) -> bool:
        """ Check if the triangle is inside the polygon. """
        
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
                    point = Point(pt)
                    if not poly.contains(point):
                        all_points_inside = False
                        break
                if all_points_inside:
                    return True
            return False
        else:
            raise ValueError("No coordinates found in the provided paths")


if __name__ == "__main__":
    data = Dataset('Data\data1.txt')
    constraint = data.process_data()
    cdt = CDT(constraint)
    cdt.generate_cdt()