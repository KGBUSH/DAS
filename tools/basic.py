# -*- coding: utf-8 -*-

"""

@file: basic.py
@time: 2021/1/13 8:34 下午
@desc:

"""
from config import reverse_pairs_list
import time


def find_inverse_predicate(p):
    """ find_inverse_predicate, can return None """
    for s in reverse_pairs_list:
        if p in s:
            s_tmp = s.copy()
            s_tmp.remove(p)
            return s_tmp.pop()
    return None  # 不是所有predicate都有相反值


def multi_hop_traversal(g, subject0, p, results_list):  # todo 需要测试
    """
    根据（跨system的）predicate，找到初始subject0能到达的所有system
    subject0: 遍历的初始节点
    """
    # 3.2 inter edge
    # for predicate, down_list in segment_dict['inter'].items():  # edge的name和下游节点list（在Storage Table用list存）
    for obj in g.objects(subject=subject0, predicate=p):
        results_list.append(obj)
        # 递归寻找
        multi_hop_traversal(g=g, subject0=obj, p=p, results_list=results_list)  # 第二个参数


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


class TimeRecorder(object):
    def __init__(self):
        self.tick_time = 0

    def tick(self):
        self.tick_time = time.time()

    def tock(self, process_name):
        now = time.time()
        elpased = now - self.tick_time
        self.tick_time = now
        print("\n\n[%s] used time : %8.6fs" % (process_name, elpased))
