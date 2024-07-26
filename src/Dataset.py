#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Dataset.py
@Time    :   2024/07/24 18:00:31
@Author  :   chenziyang 
@description   :   preprocess the input file
'''

import numpy as np
import os
from matplotlib.path import Path
from util import *

DATA_DIR = '../Data/'

class Dataset:
    """
    process the input data
    """
    def __init__(self,path:str) -> None:
        self.path : str = path
        self.f_list : list = []
        self.d_list : list = []
        self.w_list : list = []

    def get_data(self) -> tuple[list,list,list]:
        """
        record the position of components and return the information of d,f,w 
        """
        with open(self.path,mode='r',encoding='utf-8') as f:
            content = f.read()
            # print(content)
            """
            ['d1\t20\t20\t15\t15',]
            """
            line : list = content.split('\n')
            # print(line)
            """
            [['d1', '20', '20', '15', '15'],...]
            """
            module : list[list[str]] = [mod.split('\t') for mod in line]
            # print(module)

            # determine the components successively
            for lin in module:
                ch : str = lin[0][0]
                pos_len : int = len(lin)
                # the first module
                if ch == 'd':
                    self.d_list.append(lin[1:pos_len])
                elif ch == 'f':
                    self.f_list.append(lin[1:pos_len])
                elif ch == 'w':
                    self.w_list.append(lin[1:pos_len])
        return self.d_list,self.f_list,self.w_list
    
    def process_data(self) -> list[Path]:
        """
        return constrained edges which consist of obstacle in Path
        """
        verticle_list = []
        _d_list,_f_list,_w_list = self.get_data()
        verticle_list += cal_four_verticles(_d_list)
        verticle_list += cal_four_verticles(_f_list)
        verticle_list += cal_four_verticles(_w_list)
        return verticle_list
    
    def write_fixed_data(self) -> np.array:
        """
        return constrained edges which consist of obstacle in array
        try to use the lab of PythonCDT
        """
        verticle_list = []
        _d_list,_f_list,_w_list = self.get_data()
        verticle_list += cal_four_verticles_v2(_d_list)
        verticle_list += cal_four_verticles_v2(_f_list)
        verticle_list += cal_four_verticles_v2(_w_list)

        # 索引序列
        final_index = []

        index_pair = np.array([[1, 2], [2, 3], [3, 4], [1, 4]])

        for idx in range(len(verticle_list)):
            cnt = idx * 4  # 计算偏移量
            # 根据偏移量修改索引对，并添加到最终结果中
            shifted_pairs = index_pair + cnt
            final_index.extend(shifted_pairs.tolist())  # 转换为列表并添加到最终结果中

        # print(final_index)
        
        # file_name = os.path.splitext(os.path.basename(DATA_DIR))[0]
        # file_extend = os.path.splitext(os.path.basename(DATA_DIR))[1]

        # 点数数量和边数数量
        total_coordinates = sum(len(sublist) for sublist in verticle_list)
        final_index_len = len(final_index)
        with open(self.path+'_tmp', 'w') as file:
            file.write(f"{total_coordinates} {final_index_len}\n")
            for sublist in verticle_list:
                for coord in sublist:
                    file.write(f"{coord[0]} {coord[1]}\n")
            for pair in final_index:
            # 写入每对索引，格式为 "索引1 索引2"
                file.write(f"{pair[0]} {pair[1]}\n")

        return verticle_list,final_index

        
    

if __name__ == '__main__':
    data = Dataset('.\Data\data1.txt')
    # print(data.get_data())
    # print(data.process_data())
    print(data.write_fixed_data())