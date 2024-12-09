#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   A-star.py
@Time    :   2024/08/02 14:56:34
@Author  :   chenziyang 
@description   :   construct A-star to search the path in SG
"""

import heapq

import networkx as nx
import numpy as np
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt

from CDT_Graph import SG_graph
from util import segment_dividers


class PriorityQueue:
    """
    imitate the priorityqueue by heapq
    """

    def __init__(self) -> None:
        self.elements: list[tuple[float, tuple[np.float64, np.float64]]] = []

    def empty(self) -> bool:
        """
        the priorityqueue empty or not
        """
        return not self.elements

    def put(self, point: tuple[np.float64, np.float64], priority: float) -> None:
        """
        put the item into the priorityqueue
        """
        heapq.heappush(self.elements, (priority, point))

    def get(self) -> tuple[np.float64, np.float64]:
        """
        get the top one
        """
        return heapq.heappop(self.elements)[1]


def heuristic(
    a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]
) -> float:
    """
    Manhanton distance
    """
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def Euclidean(
    a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]
) -> float:
    """
    Euclidean distance
    """
    (x1, y1) = a
    (x2, y2) = b
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def a_star_search(
    graph: nx.Graph,
    start: tuple[np.float64, np.float64],
    goal: tuple[np.float64, np.float64],
):
    """
    a searching algorithm to find the best path
    """
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[tuple[np.float64, np.float64], tuple[np.float64, np.float64]] = {}
    cost_so_far: dict[tuple[np.float64, np.float64], float] = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current: tuple[np.float64, np.float64] = frontier.get()

        if current == goal:
            break

        for next in list(graph.neighbors(current)):
            new_cost = cost_so_far[current] + euclidean(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far


def reconstruct_path(
    came_from: dict[tuple[np.float64, np.float64], tuple[np.float64, np.float64]],
    start: tuple[np.float64, np.float64],
    goal: tuple[np.float64, np.float64],
) -> list[tuple[np.float64, np.float64]]:
    """
    reverse the path because when recoring the path is reverse
    """
    current: tuple[np.float64, np.float64] = goal
    path: list[tuple[np.float64, np.float64]] = []
    if goal not in came_from:  # no path was found
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)  # optional
    path.reverse()  # optional
    return path


def find_shortest_path(start_name: str, targe_name: str, compo_dict: dict):
    shortest_path = None
    shortest_distance = float("inf")
    best_start = None
    best_target = None

    for start in compo_dict[start_name]:
        for target in compo_dict[targe_name]:
            start = tuple(np.float64(x) for x in start)
            target = tuple(np.float64(x) for x in target)
            # print(start,target)
            came_from, cost_so_far = a_star_search(sg.graph, start, target)
            if target in cost_so_far and cost_so_far[target] < shortest_distance:
                shortest_distance = cost_so_far[target]
                shortest_path = reconstruct_path(came_from, start, target)
                best_start = start
                best_target = target

    return best_start, best_target, shortest_path


def construct_path(
    data_path: str, nearest_incomp: dict, nearest_outcomp: dict, compo_dict: dict
):
    all_path: list[list[tuple[np.float64, np.float64]]] = []
    with open(data_path, mode="r", encoding="utf-8") as f:
        line = f.read().split("\n")
        # print(line)
    route_list = [lin.split("\t") for lin in line]
    # print(route_list)

    # process complete route path
    for route in route_list:
        route.insert(0, nearest_incomp[route[0]])
        # ignore * first
        if "*" in route[-1]:
            route[-1] = route[-1].replace("*", "")
        route.append(nearest_outcomp[route[-1]])
        # print(route)
        # store each path
        each_path_list: list[tuple[np.float64, np.float64]] = []
        for idx in range(len(route) - 1):
            start_name = route[idx]
            targe_name = route[idx + 1]
            best_start, best_target, shortest_path = find_shortest_path(
                start_name, targe_name, compo_dict
            )
            each_path_list.append(shortest_path)
        all_path.append(each_path_list)

    return all_path


def calcu_length(path: list[list[tuple]]):
    total_length = 0
    has_count = set()
    for each_path in path:
        for seg in each_path:
            for i in range(len(seg) - 1):
                if tuple([seg[i], seg[i + 1]]) in has_count:
                    pass
                else:
                    total_length += Euclidean(seg[i], seg[i + 1])
                    has_count.add(tuple([seg[i], seg[i + 1]]))

    return total_length


# detail routing
# 1. 首先获取路径中除去首尾元素
# 2. 其次获取中间线段的端点，并获得n等分点坐标
# 3. 动态规划获取首到中间段到最终的优化后的最小长度


def detail_routing(sg: SG_graph, path: list[list[tuple]], n: int):
    total_lenth = 0
    final_path = []

    for each_path in path:
        path = []
        for seg in each_path:
            real_path = one_detail_routing(sg, seg, n)
            path.append(real_path)
        final_path.append(path)
    return final_path


def one_detail_routing(sg: SG_graph, path: list[tuple], n: int) -> tuple[list, float]:
    head = path[0]
    tail = path[-1]
    middle_path = path[1:-1]
    # return head,tail,middle_path
    # 存储总的中间线段n等分的n个坐标位置
    global_n_points_pos = []

    for mid in middle_path:
        # print(mid)
        global_n_points_pos.append(segment_dividers(*sg.terminal_to_mid[tuple(mid)], n))

    real_path = [head]
    min_point = None
    for path_list in global_n_points_pos:
        min_length = 1e9
        for point in path_list:
            if min_length > Euclidean(head, point):
                min_length = Euclidean(head, point)
                min_point = point
        real_path.append(min_point)
        head = min_point
    real_path.append(tail)
    # total_lenth
    return real_path


if __name__ == "__main__":
    # # point1 = (np.float64(6), np.float64(1))
    # # point2 = (np.float64(6), np.float64(6))
    # # print(euclidean(point1,point2))
    sg = SG_graph("Data\data5.txt", "Data\input5.txt", 0.6)
    sg.add_midpoint_to_SG()
    sg.add_egdes_to_SG()
    sg.add_startarget_to_SG()
    path_list = construct_path(
        "Data\input5.txt", sg.nearest_incomp, sg.nearest_outcomp, sg.compo_dict
    )
    # print(path_list[0],len(path_list))
    print(calcu_length(path_list))

    route = detail_routing(sg, path_list, 7)
    print(calcu_length(route))
    # print(one_detail_routing(sg,path_list[0][0],2))
    # print(Euclidean((62.5, 12.5), (60.0, 15.0))+Euclidean((60.0,15.0), (57.5,27.5)))

    # colors = ['blue', 'black', 'red', 'purple', 'orange']

    # for i,each_path in enumerate(route):
    #     plt.figure(figsize=(8, 6))
    #     color = colors[i % len(colors)]
    #     for partial_path in each_path:
    #         x_coords, y_coords = zip(*partial_path)
    #         plt.plot(x_coords, y_coords, marker='o', color=color, linestyle='-', linewidth=2, markersize=6)
    #     sg.cdt.dispaly_cdt()

    # # sg.draw_midpoint_and_neutrality()
    # with open("Data\input1.txt", mode="r", encoding="utf-8") as f:
    #     content = f.readline().strip()
    #     # print(content)
    #     first_name = content.split("\t")[0]
    #     second_name = content.split("\t")[1]
    #     print("the test components are:", first_name, second_name)
    #     start_name = sg.nearest_incomp[first_name]
    #     target_name = sg.nearest_outcomp[second_name]
    #     # target = sg.compo_dict[first]
    #     print("the input component and output component are:",start_name,target_name)

    # shortest_path = None
    # shortest_distance = float('inf')
    # best_start = None
    # best_target = None

    # for start in sg.compo_dict[start_name]:
    #     for target in sg.compo_dict[first_name]:
    #         start = tuple(np.float64(x) for x in start)
    #         target = tuple(np.float64(x) for x in target)
    #         # print(start,target)
    #         came_from, cost_so_far = a_star_search(sg.graph, start, target)
    #         if target in cost_so_far and cost_so_far[target] < shortest_distance:
    #             shortest_distance = cost_so_far[target]
    #             shortest_path = reconstruct_path(came_from, start, target)
    #             best_start = start
    #             best_target = target

    # # print(best_start,best_target)
    # print(shortest_path)
    # x_coords, y_coords = zip(*shortest_path)
    # plt.plot(x_coords, y_coords, marker='o', color='black', linestyle='-', linewidth=2, markersize=6)
    # sg.draw_midpoint_and_neutrality()
    # # print(list(sg.graph.edges()))
