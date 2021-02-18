# -*- coding: utf-8 -*-

"""

@file: building2.py
@time: 2021/1/13 7:35 下午
@desc: 带index的building

"""

from rdflib import Graph, Literal
from rdflib.plugins.sparql import prepareQuery

from engine.indexing import Indexing
from config import BUILDING_INDEX, SUB_FLAG
from tools.basic import merge_dicts


def load_building_index(ttl_path):
    """
    index管理器
    """
    if ttl_path in BUILDING_INDEX:
        return BUILDING_INDEX[ttl_path]
    else:
        building_index = Indexing(ttl_file_path=ttl_path)  # 读入整个楼的Indexing
        BUILDING_INDEX[ttl_path] = building_index
        return BUILDING_INDEX[ttl_path]


class Building2:

    def __init__(self, building_id, ttl_path=None):
        """
        buildingID 也是ttl 文件名
        """
        self.building_index = None
        self.ttl_path = ttl_path
        if self.ttl_path:
            # 子类的构造函数不需要传入ttl_path, 不执行 load_building_index
            self.building_index = load_building_index(ttl_path=self.ttl_path)

        self.building_id = building_id

    def extract_sub_system(self, subsystem):
        """
        根据 system name取出下面segment list
        """
        sub_system = Building2Sub(building_id=self.building_id,
                                  sub_type=subsystem,
                                  sys_func_flag=SUB_FLAG['system'],
                                  ttl_path=self.ttl_path)
        return sub_system  # 对象

    def extract_sub_functionality(self, subsystem):
        """
        根据 system name取出下面segment list
        """
        sub_func = Building2Sub(building_id=self.building_id,
                                sub_type=subsystem,
                                sys_func_flag=SUB_FLAG['functionality'],
                                ttl_path=self.ttl_path)
        return sub_func  # 对象


class Building2Sub():
    """
    subsystem，继承的主要原因是因为要用ttl文件名去找 building level的indexing
    主要是index
    """

    def __init__(self, building_id, sub_type, sys_func_flag, ttl_path, sub_index=None):
        """
        :parameter sub_type: e.g. 'VAV'
        :parameter sys_func_flag: system或者functionality的标志位，(0system，1functionality)
        :parameter sub_index: 该子系统的sub_index ，可以直接赋值
        """
        # super().__init__(building_id)
        self.building_id = building_id

        # 1. 初始化
        self.ttl_path = ttl_path
        self.sys_func_flag = sys_func_flag
        if isinstance(sub_type, str):
            self.sub_type_list = [sub_type.upper()]  # 大写字母
        else:
            self.sub_type_list = sub_type  # 最后 self.sub_type_list = []

        # 2. load sub's indexing
        if sub_index:
            # 这种情况是初始化就给了sub_index，主要是在做运算的时候，先在__add__里面把index做好直接赋值
            self.sub_index = sub_index
        else:
            if self.sys_func_flag == SUB_FLAG['system']:
                self.sub_index = {}
                for sub_type in self.sub_type_list:
                    sub_dict = BUILDING_INDEX[self.ttl_path].index_system[sub_type]  # dict {Chiller_1, Chiller_2}, if type is 'CHILLER'
                    self.sub_index.update(sub_dict)
            else:
                self.sub_index = []
                for sub_type in self.sub_type_list:
                    sub_list = BUILDING_INDEX[self.ttl_path].index_func[sub_type]  # 和上面不一样，这里是list
                    self.sub_index.extend(sub_list)

    def __add__(self, other):
        """
        子系统相加，我们不evaluate s+f
        """
        sub_type_list = []
        sub_type_list.extend(self.sub_type_list)
        sub_type_list.extend(other.sub_type_list)

        if self.sys_func_flag == SUB_FLAG['system'] and other.sys_func_flag == SUB_FLAG['system']:
            # s + s = s
            sys_func_flag = SUB_FLAG['system']

            added_sub_index = {}
            added_sub_index.update(self.sub_index)
            added_sub_index.update(other.sub_index)

            return Building2Sub(building_id=self.building_id,
                                sub_type=sub_type_list,
                                sys_func_flag=sys_func_flag,
                                ttl_path=self.ttl_path,
                                sub_index=added_sub_index
                                )

        elif self.sys_func_flag == SUB_FLAG['functionality'] and other.sys_func_flag == SUB_FLAG['functionality']:
            # f + f = f
            sys_func_flag = SUB_FLAG['functionality']

            added_sub_index = []
            added_sub_index.extend(self.sub_index)
            added_sub_index.extend(other.sub_index)

            return Building2Sub(building_id=self.building_id,
                                sub_type=sub_type_list,
                                sys_func_flag=sys_func_flag,
                                ttl_path=self.ttl_path,
                                sub_index=added_sub_index
                                )
        else:
            raise TypeError("__add__ error: Can't add system + functionality")

    def __mul__(self, other):
        """
        子系统相乘法，只考虑 s * f ,   (s * s很特殊，是join的下游例子，必须要两个s是相同type
        and result is `s * f =s`
        """
        sub_type_list = []
        sub_type_list.extend(self.sub_type_list)
        sub_type_list.extend(other.sub_type_list)

        if self.sys_func_flag == SUB_FLAG['system'] and other.sys_func_flag == SUB_FLAG['functionality']:
            final_index = system_mul_func(s=self, f=other)
            return Building2Sub(building_id=self.building_id,
                                sub_type=sub_type_list,
                                sys_func_flag=SUB_FLAG['system'],
                                ttl_path=self.ttl_path,
                                sub_index=final_index
                                )

        elif self.sys_func_flag == SUB_FLAG['functionality'] and other.sys_func_flag == SUB_FLAG['system']:
            final_index = system_mul_func(s=other, f=self)
            return Building2Sub(building_id=self.building_id,
                                sub_type=sub_type_list,
                                sys_func_flag=SUB_FLAG['system'],
                                ttl_path=self.ttl_path,
                                sub_index=final_index
                                )

        else:
            raise TypeError("__mul__ error: ")

    def __mod__(self, other):
        """
        符号是: %; 用于重载join
        """
        self_feeds_entity_name = []  # 被self system feeds的所有entity name

        if self.sys_func_flag != SUB_FLAG['system'] or other.sys_func_flag != SUB_FLAG['system']:
            raise TypeError("__join__ error: ")
        for entity_name, entity_dict in self.sub_index.items():
            self_feeds_entity_name.extend(entity_dict['inter']['feeds'])

        final_sub_dict = other.sub_index.copy()
        for entity in other.sub_index:
            if entity not in self_feeds_entity_name:
                del final_sub_dict[entity]

        return Building2Sub(building_id=self.building_id,
                            sub_type=other.sub_type_list,
                            sys_func_flag=SUB_FLAG['system'],
                            ttl_path=self.ttl_path,
                            sub_index=final_sub_dict
                            )




def system_mul_func(s, f):
    """
    只针对 s*f, 都是Building2Sub的对象
    """
    the_system_index_dict = s.sub_index.copy()  # dict in `system`
    for segment_name, segment_dict in the_system_index_dict.items():
        belonged_sensors = segment_dict['intra']['hasPoint']
        segment_dict['intra']['hasPoint'] = list(set(belonged_sensors) &
                                                 set(f.sub_index))
    return s.sub_index
