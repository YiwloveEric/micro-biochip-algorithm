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


    def generate_cdt(self)->None:
        """
        main function to generate the CDT
        """
        points : np.array = self.point
        constraint : list[Path] = self.constraint

        # init Delaunay
        tri = Delaunay(points)

        # Multi polygon
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
            valid_points = np.unique(np.concatenate(filtered_triangles))  # Flatten and get unique points
            new_points = points[valid_points]
            new_tri = Delaunay(new_points)
            
            # Plot the original and new triangulation
            plt.triplot(points[:, 0], points[:, 1], tri.simplices, color='red', label='Original Triangulation')
            plt.triplot(new_points[:, 0], new_points[:, 1], new_tri.simplices, color='blue', label='Filtered Triangulation')
        
        # Add polygon boundary
        polygon_x, polygon_y = zip(*constraint, constraint[0])  # Ensure the polygon is closed
        plt.plot(polygon_x, polygon_y, 'k--', label='Polygon Boundary')

        # Plot points
        plt.scatter(points[:, 0], points[:, 1], color='green', label='Points')

        plt.legend()
        plt.show()

    @staticmethod
    def is_triangle_in_polygon(triangle: Delaunay, polygon: list[Path]) -> bool:
        """ Check if the triangle is inside the polygon. """
        
        # 提取每个 Path 对象的坐标并构造 Polygon
        polygon_coords = []
        for path in polygon:
            if isinstance(path, Path):
                polygon_coords.extend(path.vertices.tolist())  # 提取坐标并添加到列表中
            else:
                raise TypeError("Expected Path object")
        
        # 确保坐标列表有正确的格式 (如: [[x1, y1], [x2, y2], ...])
        if polygon_coords:
            # 假设 polygon 是一个闭合的多边形
            poly = Polygon(polygon_coords)

            # 检查三角形的每个顶点是否在多边形内
            for pt in triangle.points:
                if not poly.contains(Point(pt)):
                    return False
            return True
        else:
            raise ValueError("No coordinates found in the provided paths")


if __name__ == "__main__":
    data = Dataset('Data\data1.txt')
    constraint = data.process_data()
    cdt = CDT(constraint)
    cdt.generate_cdt()