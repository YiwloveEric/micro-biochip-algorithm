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

from CDT_Graph import SG_graph


class PriorityQueue:
    def __init__(self) -> None:
        self.elements: list[tuple[float, tuple[np.float64, np.float64]]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, point: tuple[np.float64, np.float64], priority: float) -> None:
        heapq.heappush(self.elements, (priority, point))

    def get(self) -> tuple[np.float64, np.float64]:
        return heapq.heappop(self.elements)[1]


def heuristic(
    a: tuple[np.float64, np.float64], b: tuple[np.float64, np.float64]
) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(
    graph: nx.Graph,
    start: tuple[np.float64, np.float64],
    goal: tuple[np.float64, np.float64],
):
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


if __name__ == "__main__":
    # point1 = (np.float64(6), np.float64(1))
    # point2 = (np.float64(6), np.float64(6))
    # print(euclidean(point1,point2))
    sg = SG_graph("Data\data1.txt", "Data\input1.txt", 0.6)
    sg.add_midpoint_to_SG()
    sg.add_egdes_to_SG()
    sg.add_startarget_to_SG()
    # sg.draw_midpoint_and_neutrality()
    with open("Data\input1.txt", mode="r", encoding="utf-8") as f:
        content = f.readline().strip()
        # print(content)
        first = content.split("\t")[0]
        second = content.split("\t")[1]
        print("the test components are:", first, second)
        start = sg.nearest_incomp[first]
        target = sg.compo_dict[first]
        # print(target)
        # print(start)
        
        for start_ver in sg.compo_dict[start]:
            start_ver = tuple(np.float64(x) for x in start_ver)


        for target_ver in sg.compo_dict[first]:
            # 转换成tuple[np.float64,np.float64]
            target_ver = tuple(np.float64(x) for x in target_ver)
