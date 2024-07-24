#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   CDT.py
@Time    :   2024/07/24 17:43:48
@Author  :   chenziyang 
@description   :   create cdt model
'''

import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt








if __name__ == '__main__':

    # 生成随机点
    points = np.random.rand(10, 2)

    # 进行德劳内三角剖分
    tri = Delaunay(points)

    # 绘制结果
    plt.triplot(points[:,0], points[:,1], tri.simplices)
    plt.plot(points[:,0], points[:,1], 'o')
    plt.show()