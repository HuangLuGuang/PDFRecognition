# -*- coding: utf-8 -*-
# @createTime    : 2020/5/14 13:39
# @author  : Huanglg
# @fileName: constants.py
# @email: luguang.huang@mabotech.com

# pdf 表头识别像素范围
header_scope = {
            "title": (500, 20, 1520, 90),  # 标题
            "testtime": (1920, 25, 2147, 86),  # 检测时间
            "serialnum": (500, 135, 1600, 240),  # 序列号
            "operator": (1900, 135, 2150, 240),  # 操作人
}

# 测试值识别像素范围
normal_scope = {
            "title1": (8, 8, 177, 64),  # 标题
            "title2": (650, 8, 1977, 65),
            "column_name": (10, 82, 1735, 140),  # 列名
            "test_value": (8, 153, 1788, 208),  # 测试值
}

# 直线度 平面度 圆度 圆柱度 对称度 同轴度 位置度 全跳动 圆跳动 这几种没有下偏差 -TOL
NO_LOW_TOL_ITEMS = [
    '直线度',
    '平面度',
    '圆度',
    '圆柱度',
    '对称度',
    '同轴度',
    '位置度',
    '全跳动',
    '圆跳动',
]
