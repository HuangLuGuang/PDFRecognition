# -*- coding: utf-8 -*-
# @createTime    : 2020/5/12 8:46
# @author  : Huanglg
# @fileName: table.py
# @email: luguang.huang@mabotech.com
# -*- coding: utf-8 -*-
import json

import os
import time
import traceback
import natsort
import shutil
from PIL import Image, ImageEnhance
import multiprocessing
import tr
import cv2
import numpy as np
import config
import constants
from utils.Logger import Logger
from utils.RedisHelper import MyRedis

log = Logger()
try:
    redis = MyRedis(host=config.REDIS_HOST, password=config.REDIS_PASSWORD, port=config.REDIS_PORT)
except Exception:
    log.error(traceback.format_exc())

np_base_columns = np.array([])
text_base_columns = str()


def run_shell_cmd(cmd):
    try:
        ret = os.system(cmd)
        if ret == 0:
            return True
        else:
            return False
    except Exception as e:
        log.error(e)
        return False


def pdf_to_table(pdf_path):
    """

    :param pdf_path:
    :return: [table_png_path]
    """
    filename = os.path.split(pdf_path)[1]
    project_path = os.getcwd()
    out_dir = os.path.join(project_path, 'output', filename)
    # 如果之前存在，先删除
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    pdf_to_table_commond = 'pdftohtml -c -hidden -xml "{0}" "{1}"'.format(pdf_path,
                                                                          os.path.join(out_dir, filename + '.xml'))
    print(pdf_to_table_commond)
    ret = run_shell_cmd(pdf_to_table_commond)
    if ret:
        all_png_absolute_path = scan_file(out_dir)
        return all_png_absolute_path


def scan_file(path):
    # 获取文件夹下的所有文件，并自然排序
    files = os.listdir(path)
    files = natsort.natsorted(files)
    result = []
    for index, file in enumerate(files):
        # 文件后缀
        file_type = os.path.splitext(file)[1]
        if file_type == '.png':
            # 拼接待识别图片的绝对路径
            image_absolute_path = os.path.join(path, file)
            result.append(image_absolute_path)
    return result


def cut_img(img, coordinate):
    """
     根据坐标位置剪切图片
    :param img 图片路径或者， Image 对象， 或者numpy数组
    :param coordinate: 原始图片上的坐标(tuple) egg:(x, y, w, h) ---> x,y为矩形左上角坐标, w,h为右下角坐标
    :return:
    """
    # image = Image.open(imgsrc)
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    else:
        if isinstance(img, str):
            img = Image.open(img)
        elif isinstance(img, Image.Image):
            img = img
        else:
            raise NotImplementedError()
    region = img.crop(coordinate)
    region = ImageEnhance.Contrast(region).enhance(1.5)
    return region


def correct_text(key, text):
    """
    矫正OCR后的文字
    :param key:
    :param text:
    :return:
    """
    if key == 'title1':
        return text.replace('<>', '').replace('母', '').replace('团', '')
    elif key == 'title2':
        if text and text[0] == 7:
            text = text.replace('7', 'Z')
        return text.replace('|', '').replace('乙轴', 'Z轴')
    elif key == 'column_name':
        return text.replace('+TOL TOL', '+TOL -TOL').replace('特征NOMINAL', '特征 NOMINAL')
    else:
        return text


def is_exist_low_tol(title1):
    # 判断是否存在下限
    if isinstance(title1, str):
        for item in constants.NO_LOW_TOL_ITEMS:
            if title1.find(item) != -1:
                # 如果能找到这几个，不存在下限
                return False
    return True


def image_to_text(image_path, index, serial_num):
    """
    :param image_path: pdf 切割后每个小图片的路径
    :param index: 索引
    :param serial_num: pdf 序列号，也叫车辆架构号
    :return:

    """
    image = Image.open(image_path)
    # index=0 表头信息
    if index == 0:
        scope = constants.header_scope
        result = {}
        for k, v in scope.items():
            img = cut_img(img=image, coordinate=v)
            # 表头高度有轻微变化，用run_angle检测识别出范围
            tr_result = tr.run_angle(img)
            text = None
            for item in tr_result:
                if item[1] == 'r':
                    continue
                else:
                    text = correct_text(k, item[1])
            result[k] = text
        log.info('index:{0}, text:{1}'.format(*(index, result)))
        redis.hash_set(serial_num, index, json.dumps(result))
    else:
        scope = constants.normal_scope
        result = {}
        for k, v in scope.items():
            img = cut_img(img=image, coordinate=v)
            # 列名有很多重复的，判断是否和最新识别过的相同，避免在ORC的时候浪费时间
            if k == 'column_name':
                np_column = np.array(img)
                global np_base_columns, text_base_columns

                # 判断和之前的列名是否一样，避免重复识别，提高速度
                if (np_column.shape == np_base_columns.shape) and (not np.any(cv2.subtract(np_base_columns, np_column))):
                    result[k] = text_base_columns
                    continue
                else:
                    result[k] = correct_text(k, tr.recognize(img)[0])
                    # 更新要对比的基础列名
                    text_base_columns = result[k]
                    np_base_columns = np_column

            # 直线度 平面度 圆度 圆柱度 对称度 同轴度 位置度 全跳动 圆跳动 这几种没有下偏差 -TOL
            # 这种需要单独处理 如果用 tr.recognize 有些测试值空格识别不出来，会粘在一起
            elif k == 'test_value' and is_exist_low_tol(title1=result['title1']) is False :
                text = ''
                tr_result = tr.run_angle(img)
                for index, item in enumerate(tr_result):
                    # 第四列是-TOL，填充一个空置
                    if index == 3:
                        text = text + ' ' + 'null'
                    else:
                        text = text + ' ' + item[1]
                result[k] = text

                print('start', '*'*100)
                print(result)
                print('end', '*' * 100)
            else:
                result[k] = correct_text(k, tr.recognize(img)[0])
        log.info('index:{0}, text:{1}'.format(*(index, result)))
        redis.hash_set(serial_num, index, json.dumps(result))


def parse_pdf(pdf_path):
    all_png_absolute_path = pdf_to_table(pdf_path=pdf_path)
    actual_filename = os.path.basename(pdf_path)
    if all_png_absolute_path:
        header_image = Image.open(all_png_absolute_path[0])
        # 先识别序列序列号，作为业务主键
        serial_img = cut_img(img=header_image, coordinate=constants.header_scope['serialnum'])
        # serial = tr.recognize(serial_img)[0]
        serial = None
        tr_result = tr.run_angle(serial_img)
        for index, item in enumerate(tr_result):
            # 识别的结果里面 字符串 ’序列号‘ 下一个值就是序列号
            if item[1] == '序列号' and index + 1 < len(tr_result):
                serial = tr_result[index+1][1]
                break
        print(serial)
        # 如果序列号不为空，识别检验项
        if serial:
            # pool = multiprocessing.Pool(1)
            start_time = time.time()
            try:
                redis.hash_set(serial, 'actual_filename', actual_filename)
                redis.hash_set(serial, 'finish', 0)
                redis.hash_set(serial, 'image_count', len(all_png_absolute_path))
                for index, png_absolute_path in enumerate(all_png_absolute_path):
                        image_to_text(png_absolute_path, index, serial)
            except Exception:
                log.error(traceback.format_exc())
                # pool.apply_async(image_to_text, args=(png_absolute_path, index))
            # pool.close()
            # pool.join()
            try:
                redis.hash_set(serial, 'elapsed_time', str(time.time() - start_time))
                redis.hash_set(serial, 'finish', 1)
            except Exception:
                log.error(traceback.format_exc())
            print(time.time() - start_time)
        else:
            log.error('{}: 序列号为空'.format(pdf_path))


if __name__ == '__main__':
    parse_pdf(pdf_path=r"""example/160/00057A20.04.17.PDF""")
    # run(pdf_path=r"""example/160/19101132  2020.03.14.PDF""")
    # run(pdf_path=r"""example/160/19.11.13   106795   .PDF""")
    # run(pdf_path=r"""example/250/250070004011191200001.PDF""")
