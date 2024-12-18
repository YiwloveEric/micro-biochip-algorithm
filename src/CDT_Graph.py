#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   CDT_Graph.py
@Time    :   2024/07/30 16:51:01
@Author  :   chenziyang 
@description   :   create CDT graph by networkX
"""

"""
构建graph过程:(节点位置采用节点的作坐标作为标识符)
SG = 空集
    加入点集：
        for 每个三角形边Te in CDT:
            if Te不在芯片边缘,障碍物边缘上:
                add Te的中点到SG
    
    加入边集:
        for 每个三角形 Tr in CDT:
            for 每个中位线Ej in Tr:
                if Ej的两个端点都在SG中:
                    add Ej到SG
    
    起点终点:
        for 每个起点/终点 Vj:
            for 每个三角形Tr in CDT(包含Vj的三角形):
                if Vj对应顶点的对边中点P包含在SG中:
                    add VjP到SG
"""


import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from CDT import chipCDT
from Dataset import Dataset
from util import calculate_midpoint_with2points, segment_dividers


class SG_graph:
    """
    construct the searching graph by CDT
    """

    def __init__(
        self,
        data_path: str,
        input_path: str,
        ratio: float,
    ) -> None:
        data = Dataset(data_path, input_path, ratio)
        self.cdt = chipCDT(data_path, input_path, ratio)
        self.graph = nx.Graph()
        self.point = self.cdt.get_all_points()
        self.tri = self.cdt.get_all_triangles()
        self.input_path = input_path
        self.constraint = data.process_data2array()
        self.compo_center_dict, self.compo_dict = data.get_point_dict()
        self.nearest_incomp, self.nearest_outcomp = data.process_input_data(
            self.compo_center_dict
        )
        self.terminal_to_mid = {}
        self.has_count_lenth = set()

    def add_midpoint_to_SG(self) -> list[tuple[np.float64, np.float64]]:
        """
        add valid triangles' midpoint into searching SG graph
        """
        mid_point_list: list[tuple[np.float64, np.float64]] = (
            self.calculate_tri_midpoint(self.point, self.tri)
        )
        self.graph.add_nodes_from(mid_point_list)
        # print(len(self.graph.nodes()))

        # 去除芯片边缘中点与障碍边缘中点
        # 计算边缘点的中点
        bound_mid_list: list[tuple[np.float64, np.float64]] = (
            SG_graph.calcuulate_boundary_midpoint(self.constraint)
        )
        # 只保留存在的点
        existing_nodes_to_remove = [
            node for node in bound_mid_list if node in self.graph.nodes
        ]
        self.graph.remove_nodes_from(existing_nodes_to_remove)
        # print(len(self.graph.nodes()))

        print("[*] add the midpoint to SG successfully!")
        return self.graph.nodes()

    def add_egdes_to_SG(
        self,
    ) -> list[tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]]:
        """
        add valid triangles' neutrality into searching SG graph
        """
        mid_point_list: list[list[tuple[np.float64, np.float64]]] = (
            SG_graph.calculate_tri_neutrality_edge(self.point, self.tri)
        )

        neutrality_edge_list: list[tuple[tuple[np.float64, np.float64]]] = (
            self.filter_valid_neutrality_edge(mid_point_list)
        )

        # 将边加入SG图
        self.graph.add_edges_from(neutrality_edge_list)
        print("[*] add the neutrality edge to SG successfully!")
        return self.graph.edges()

    def add_startarget_to_SG(
        self,
    ) -> tuple[
        list[tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]],
        list[tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]],
    ]:
        start_edges: list[
            tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]
        ] = []
        target_edges: list[
            tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]
        ] = []
        _, compo_dict = self.compo_center_dict, self.compo_dict
        nearest_incomp, nearest_outcomp = self.nearest_incomp, self.nearest_outcomp
        # print(nearest_incomp)
        # print(nearest_outcomp)
        # 将有选择到的流入端口及其四个端点信息加入字典
        edges = self._add_midpoint_ver_to_SG(compo_dict)
        # target_edges = self._add_midpoint_ver_to_SG(compo_dict)
        # print(start_edges)
        # print()
        # print(target_edges)
        self.graph.add_edges_from(edges)
        # self.graph.add_edges_from(target_edges)
        print("[*] add the midpoint and startarget edge to SG successfully!")
        return edges

    def _add_midpoint_ver_to_SG(self, compo_dict):
        startarget_edges: list[
            tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]
        ] = []
        # startarget_dict: dict[str, np.ndarray] = {}
        # for key in compo_dict.keys():
        # input_compo_key = nearest_comp[key]
        # print(input_compo_key,compo_dict[input_compo_key])
        # startarget_dict[input_compo_key] = compo_dict[input_compo_key]
        # print(start_dict)

        tri_list = []
        # 预先提取所有的三角形顶点坐标位置
        for t in self.tri:
            tri_list.append(self.point[t])
        # print(tri_list)

        for start in compo_dict.keys():
            start_four_pos: np.ndarray = compo_dict[start]
            # print(start_four_pos)
            for each_ver in start_four_pos:
                for triangles in tri_list:
                    # 判断该顶点被哪个三角形所包括
                    if np.any(np.all(each_ver == triangles, axis=1)):
                        # print(each_ver,triangles)
                        # 提取出非该顶点的其他顶点计算该边中点
                        mask = ~np.all(each_ver == triangles, axis=1)
                        # 三角形其他顶点
                        other_ver = triangles[mask]
                        # print(other_ver)
                        midpoint: tuple[np.float64, np.float64] = (
                            calculate_midpoint_with2points(other_ver)
                        )
                        # print(midpoint)
                        # 判断该点是否有在SG图中
                        if self.graph.has_node(midpoint):
                            float64_elements = tuple(np.float64(x) for x in each_ver)
                            startarget_edges.append((float64_elements, midpoint))
        # print(start_edges)
        return startarget_edges

    def draw_midpoint_and_neutrality(self) -> None:
        """
        draw the CDT graph and midpoint and neutrality line
        """
        points = self.graph.nodes()
        points_float = [(float(x), float(y)) for x, y in points]
        plt.scatter(
            *zip(*points_float), color="red", label="midpoint", marker="*", s=50
        )
        for edge in self.graph.edges():
            x_values, y_values = zip(*edge)  # 解包边的坐标
            plt.plot(x_values, y_values, "r--")
        self.cdt.dispaly_cdt()

    def filter_valid_neutrality_edge(
        self, mid_point: list[list[tuple[np.float64, np.float64]]]
    ) -> list[tuple[tuple[np.float64, np.float64]]]:
        """
        filter the valid neutrality edges
        only two terminals of edges are both included in SG -> valid
        """
        neutrality_edge_list: list = []
        for tri_list in mid_point:
            for idx in range(len(tri_list)):
                point1: tuple[np.float64, np.float64] = tri_list[idx]
                point2: tuple[np.float64, np.float64] = tri_list[
                    (idx + 1) % (len(tri_list))
                ]

                # 如果中位线两个端点都包括在SG中，就加入这条中位线
                if self.graph.has_node(point1) and self.graph.has_node(point2):
                    neutrality_edge_list.append((point1, point2))
        return neutrality_edge_list

    @staticmethod
    def calculate_tri_neutrality_edge(
        points: np.ndarray, tri: np.ndarray
    ) -> list[list[tuple[np.float64, np.float64]]]:
        """
        calculating the triangles' neutrality edge
        """
        mid_point_list: list[tuple[np.float64, np.float64]] = []
        for t in tri:
            each_tri = points[t]
            each_tri_list: list = []
            for idx in range(len(each_tri)):
                point1: np.ndarray = each_tri[idx]
                point2: np.ndarray = each_tri[(idx + 1) % (len(each_tri))]
                mid_point: np.ndarray = (point1 + point2) / 2
                each_tri_list.append(tuple(mid_point))
            # print(mid_point_list)
            mid_point_list.append(each_tri_list)
        # [[(np.float64(31.25), np.float64(33.75)), (np.float64(23.75), np.float64(33.75)), (np.float64(35.0), np.float64(27.5))]
        return mid_point_list

    @staticmethod
    def calcuulate_boundary_midpoint(
        constraint: np.ndarray,
    ) -> list[tuple[np.float64, np.float64]]:
        """
        calculating the triangles' boundary edge midpoint
        """
        bound_mid_list: list[tuple[np.float64, np.float64]] = []
        for area in constraint:
            for idx in range(len(area)):
                bound_point1: np.ndarray = area[idx]
                bound_point2: np.ndarray = area[(idx + 1) % (len(area))]
                bound_mid_point: np.ndarray = (bound_point1 + bound_point2) / 2
                bound_mid_list.append(tuple(bound_mid_point))
        return bound_mid_list

    def calculate_tri_midpoint(
        self, points: np.ndarray, tri: np.ndarray
    ) -> list[tuple[np.float64, np.float64]]:
        """
        calculating the triangles' midpoint
        """
        mid_point_list: list[tuple[np.float64, np.float64]] = []
        for t in tri:
            each_tri = points[t]
            # print(each_tri)
            for idx in range(len(each_tri)):
                point1: np.ndarray = each_tri[idx]
                point2: np.ndarray = each_tri[(idx + 1) % (len(each_tri))]
                mid_point: np.ndarray = (point1 + point2) / 2
                mid_point_list.append(tuple(mid_point))
                self.terminal_to_mid[tuple(mid_point)] = (tuple(point1), tuple(point2))
        # print(mid_point_list)
        return mid_point_list


if __name__ == "__main__":
    # cdt = chipCDT("Data\data1.txt", "Data\input1.txt", 0.6)
    # print(points.shape)
    # print(triangles.shape)
    sg = SG_graph("Data\data1.txt", "Data\input1.txt", 0.6)
    sg.add_midpoint_to_SG()
    sg.add_egdes_to_SG()
    sg.add_startarget_to_SG()
    # for key,value in sg.terminal_to_mid.items():
    #     print(key,value)
    # 可以求出每个中点的两个端点
    # print(sg.terminal_to_mid[(np.float64(60.0), np.float64(15.0))])
    print(
        segment_dividers(*sg.terminal_to_mid[(np.float64(60.0), np.float64(15.0))], 3)
    )
    # sg.draw_midpoint_and_neutrality()
    # for current in list(sg.graph.neighbors((np.float64(6.25), np.float64(3.75)))):
    #     print(current)
