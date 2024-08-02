#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   Dataset.py
@Time    :   2024/07/24 18:00:31
@Author  :   chenziyang 
@description   :   preprocess the input file
"""

import os

import numpy as np
from matplotlib.path import Path
from scipy.spatial.distance import euclidean

from util import (cal_four_verticles, cal_four_verticles_v2,
                  cal_only_one_verticles, get_compo_center)

DATA_DIR = "./Data/"


class Dataset:
    """
    process the input data
    """

    def __init__(self, path: str, input_path: str, ratio: float | np.float64) -> None:
        self.path: str = path
        self.input_path: str = input_path
        self.f_list: list = []
        self.d_list: list = []
        self.w_list: list = []
        self.ratio: float | np.float64 = ratio

    def get_point_dict(self) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
        """
        return center of the components and four verticles of the components
        """
        compo_dict: dict[str, np.ndarray] = {}
        compo_center_dict: dict[str, np.ndarray] = {}
        with open(self.path, mode="r", encoding="utf-8") as f:
            content = f.read()
            line: list = content.split("\n")
            # print(line)
            module: list[list[str]] = [mod.split("\t") for mod in line]
            # print(module)
            for lin in module:
                comp_name: str = lin[0]
                if comp_name not in compo_dict:
                    compo_dict[comp_name] = cal_only_one_verticles(lin[1:])
                    compo_center_dict[comp_name] = get_compo_center((lin[1:]))
            # print(compo_dict)
            # self.compo_dict = compo_dict
        return compo_center_dict, compo_dict

    @staticmethod
    def calculate_nearest_IO() -> None:
        pass

    def process_input_data(
        self, compo_center_dict: dict[str, np.ndarray]
    ) -> tuple[dict[str, str], dict[str, str]]:
        """
        calculate the nearest input components and output components
        and return in a dict
        """
        # 存放每个组件相离最近的流入端口组件编号
        nearest_incomp: dict = {}
        # 存放每个组件相离最近的流出端口组件编号
        nearest_outcomp: dict = {}
        # 存放已经选择过的流入流出组件编号
        chosen_comp: set = set()
        with open(self.input_path, mode="r", encoding="utf-8") as f:
            line = f.read().split("\n")
            # print(line)
            route_list: list[list[str]] = [rt.split("\t") for rt in line]
            # print(route_list)
            for route in route_list:
                route_len = len(route)
                if route_len == 1:
                    # 需要定义在loop外
                    head_min_distance: np.ndarray = 200
                    tail_min_distance: np.ndarray = 200
                    for key in compo_center_dict.keys():
                        # 计算流入模块距离
                        if "f" in key:
                            head_comp: str = route[0]
                            head_real_distance = euclidean(
                                compo_center_dict[key], compo_center_dict[head_comp]
                            )
                            if head_real_distance < head_min_distance:
                                # 需要尽可能减少流入端口的使用，使用阈值进行可操作性设定
                                # 这里采用小于chip的len*ratio时,进行复用
                                if len(chosen_comp) != 0 and key not in chosen_comp:
                                    for chosen_key in chosen_comp:
                                        if "f" in chosen_key:
                                            chosen_distance = euclidean(
                                                compo_center_dict[chosen_key],
                                                compo_center_dict[head_comp],
                                            )
                                            # print(
                                            #     "component:"
                                            #     + str(head_comp)
                                            #     + "\tchosen_key:"
                                            #     + chosen_key
                                            #     + "\t"
                                            #     + str(
                                            #         chosen_distance <= 70 * self.ratio
                                            #     )
                                            # )
                                            if chosen_distance <= 70 * self.ratio:
                                                nearest_incomp[head_comp] = chosen_key
                                                break
                                nearest_incomp[head_comp] = key
                                head_min_distance = head_real_distance
                                chosen_comp.add(key)
                                # print(
                                #     "key:"
                                #     + str(key)
                                #     + "\tcomp:"
                                #     + str(head_comp)
                                #     + "\tdistance:"
                                #     + str(head_min_distance)
                                # )
                        # 计算流出模块距离
                        if "w" in key:
                            tail_comp: str = route[0]
                            # 这边要单独判断一下d*
                            if "*" in tail_comp:
                                # 先忽略处理
                                tail_comp = tail_comp.replace("*", "")
                                # print(tail_comp)
                            tail_real_distance = euclidean(
                                compo_center_dict[key], compo_center_dict[tail_comp]
                            )
                            if tail_real_distance < tail_min_distance:
                                # 需要尽可能减少流入端口的使用，使用阈值进行可操作性设定
                                # 这里采用小于chip的len*ratio时,进行复用
                                if len(chosen_comp) != 0 and key not in chosen_comp:
                                    for chosen_key in chosen_comp:
                                        if "w" in chosen_key:
                                            chosen_distance = euclidean(
                                                compo_center_dict[chosen_key],
                                                compo_center_dict[tail_comp],
                                            )
                                            # print(
                                            #     "component:"
                                            #     + str(tail_comp)
                                            #     + "\tchosen_key:"
                                            #     + chosen_key
                                            #     + "\t"
                                            #     + str(
                                            #         chosen_distance <= 70 * self.ratio
                                            #     )
                                            # )
                                            if chosen_distance <= 70 * self.ratio:
                                                nearest_outcomp[tail_comp] = chosen_key
                                                break
                                nearest_outcomp[tail_comp] = key
                                tail_min_distance = tail_real_distance
                                chosen_comp.add(key)
                                # print(
                                #     "key:"
                                #     + str(key)
                                #     + "\tcomp:"
                                #     + str(tail_comp)
                                #     + "\tdistance:"
                                #     + str(tail_min_distance)
                                # )
                else:
                    # 需要定义在loop外
                    head_min_distance: np.ndarray = 200
                    tail_min_distance: np.ndarray = 200
                    for key in compo_center_dict.keys():
                        # 计算流入模块距离
                        if "f" in key:
                            head_comp: str = route[0]
                            head_real_distance = euclidean(
                                compo_center_dict[key], compo_center_dict[head_comp]
                            )
                            if head_real_distance < head_min_distance:
                                # 需要尽可能减少流入端口的使用，使用阈值进行可操作性设定
                                # 这里采用小于chip的len*ratio时,进行复用
                                if len(chosen_comp) != 0 and key not in chosen_comp:
                                    for chosen_key in chosen_comp:
                                        if "f" in chosen_key:
                                            chosen_distance = euclidean(
                                                compo_center_dict[chosen_key],
                                                compo_center_dict[head_comp],
                                            )
                                            # print(
                                            #     "component:"
                                            #     + str(head_comp)
                                            #     + "\tchosen_key:"
                                            #     + chosen_key
                                            #     + "\t"
                                            #     + str(
                                            #         chosen_distance <= 70 * self.ratio
                                            #     )
                                            # )
                                            if chosen_distance <= 70 * self.ratio:
                                                nearest_incomp[head_comp] = chosen_key
                                                break
                                nearest_incomp[head_comp] = key
                                head_min_distance = head_real_distance
                                chosen_comp.add(key)
                                # print(
                                #     "key:"
                                #     + str(key)
                                #     + "\tcomp:"
                                #     + str(head_comp)
                                #     + "\tdistance:"
                                #     + str(head_min_distance)
                                # )
                        # 计算流出模块距离
                        if "w" in key:
                            tail_comp: str = route[-1]
                            # 这边要单独判断一下d*
                            if "*" in tail_comp:
                                # 先忽略处理
                                tail_comp = tail_comp.replace("*", "")
                                # print(tail_comp)
                            tail_real_distance = euclidean(
                                compo_center_dict[key], compo_center_dict[tail_comp]
                            )
                            if tail_real_distance < tail_min_distance:
                                # 需要尽可能减少流入端口的使用，使用阈值进行可操作性设定
                                # 这里采用小于chip的len*ratio时,进行复用
                                if len(chosen_comp) != 0 and key not in chosen_comp:
                                    for chosen_key in chosen_comp:
                                        if "w" in chosen_key:
                                            chosen_distance = euclidean(
                                                compo_center_dict[chosen_key],
                                                compo_center_dict[tail_comp],
                                            )
                                            # print(
                                            #     "component:"
                                            #     + str(tail_comp)
                                            #     + "\tchosen_key:"
                                            #     + chosen_key
                                            #     + "\t"
                                            #     + str(
                                            #         chosen_distance <= 70 * self.ratio
                                            #     )
                                            # )
                                            if chosen_distance <= 70 * self.ratio:
                                                nearest_outcomp[tail_comp] = chosen_key
                                                break
                                nearest_outcomp[tail_comp] = key
                                tail_min_distance = tail_real_distance
                                chosen_comp.add(key)
                                # print(
                                #     "key:"
                                #     + str(key)
                                #     + "\tcomp:"
                                #     + str(tail_comp)
                                #     + "\tdistance:"
                                #     + str(tail_min_distance)
                                # )
        # print(nearest_incomp)
        # print(nearest_outcomp)
        print("[*] nearest input and output construct successfully!")
        return nearest_incomp, nearest_outcomp

    def get_data(self) -> tuple[list, list, list]:
        """
        record the position of components and return the information of d,f,w
        """
        with open(self.path, mode="r", encoding="utf-8") as f:
            content = f.read()
            # print(content)
            """
            ['d1\t20\t20\t15\t15',]
            """
            line: list = content.split("\n")
            # print(line)
            """
            [['d1', '20', '20', '15', '15'],...]
            """
            module: list[list[str]] = [mod.split("\t") for mod in line]
            # print(module)

            # determine the components successively
            for lin in module:
                ch: str = lin[0][0]
                pos_len: int = len(lin)
                # the first module
                if ch == "d":
                    self.d_list.append(lin[1:pos_len])
                elif ch == "f":
                    self.f_list.append(lin[1:pos_len])
                elif ch == "w":
                    self.w_list.append(lin[1:pos_len])
        return self.d_list, self.f_list, self.w_list

    def process_data2path(self) -> list[Path]:
        """
        return constrained edges which consist of obstacle in Path
        """
        verticle_list = []
        _d_list, _f_list, _w_list = self.get_data()
        verticle_list += cal_four_verticles(_d_list)
        verticle_list += cal_four_verticles(_f_list)
        verticle_list += cal_four_verticles(_w_list)
        return verticle_list

    def process_data2list(self) -> list[list[list[int]]]:
        """
        return constrained edges which consist of obstacle in list
        """
        verticle_list: list[list[list[int]]] = []
        _d_list, _f_list, _w_list = self.get_data()
        verticle_list += cal_four_verticles_v2(_d_list)
        verticle_list += cal_four_verticles_v2(_f_list)
        verticle_list += cal_four_verticles_v2(_w_list)
        verticle_list.append([[0, 70], [0, 0], [70, 0], [70, 70]])
        return verticle_list

    def process_data2array(self) -> np.ndarray:
        return np.array(self.process_data2list())

    def write_fixed_data(self) -> tuple[str, np.ndarray, np.ndarray]:
        """
        return constrained edges which consist of obstacle in array
        and write the file
        """
        verticle_list = []
        verticle_list = self.process_data2list()

        # 加入boundary[[0,70],[0,0],[70,0],[70,70]]
        # verticle_list.extend([[0,70],[0,0],[70,0],[70,70]])
        # 索引序列
        final_index = []

        index_pair = np.array([[1, 2], [2, 3], [3, 4], [1, 4]])

        for idx in range(len(verticle_list)):
            cnt = idx * 4  # 计算偏移量
            # 根据偏移量修改索引对，并添加到最终结果中
            shifted_pairs = index_pair + cnt
            final_index.extend(shifted_pairs.tolist())  # 转换为列表并添加到最终结果中

        # print(final_index)

        file_name = os.path.splitext(os.path.basename(self.path))[0]
        file_extend = os.path.splitext(os.path.basename(self.path))[1]

        file_place = DATA_DIR + file_name + "_processed" + file_extend

        # 点数数量和边数数量
        total_coordinates = sum(len(sublist) for sublist in verticle_list)
        final_index_len = len(final_index)

        if os.path.exists(file_place):
            print("[*] file has been processed!")
            return file_place, verticle_list, final_index

        else:
            with open(file_place, "w") as file:
                file.write(f"{total_coordinates} {final_index_len}\n")
                for sublist in verticle_list:
                    for coord in sublist:
                        file.write(f"{coord[0]} {coord[1]}\n")
                for pair in final_index:
                    # 写入每对索引，格式为 "索引1 索引2"
                    file.write(f"{pair[0]-1} {pair[1]-1}\n")

            return file_place, verticle_list, final_index


if __name__ == "__main__":
    data = Dataset(".\Data\data1.txt", ".\Data\input1.txt", 0.6)
    # print(data.get_data())
    # print(data.write_fixed_data())
    # print(data.process_data2array().shape)
    compo_center_dict, compo_dict = data.get_point_dict()
    # print(compo_center_dict)
    data.process_input_data(compo_center_dict)
