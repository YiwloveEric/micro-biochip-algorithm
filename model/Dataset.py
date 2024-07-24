#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Dataset.py
@Time    :   2024/07/24 18:00:31
@Author  :   chenziyang 
@description   :   preprocess the input file
'''


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

            # 依次判断每个组件
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

if __name__ == '__main__':
    data = Dataset('Data\data1.txt')
    print(data.get_data())