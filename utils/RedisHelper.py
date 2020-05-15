# -*- coding: utf-8 -*-
# @createTime    : 2020/5/14 13:52
# @author  : Huanglg
# @fileName: redis_utils.py
# @email: luguang.huang@mabotech.com

import redis


class MyRedis(object):
    def __init__(self, host, password=None, port=6379, db=0):
        try:
            self.r = redis.Redis(host=host, password=password, port=port, db=db)
        except Exception as e:
            self.record_log('redis connect failed :{}'.format(e), 'error')
            raise ConnectionError

    def str_get(self, k):
        res = self.r.get(k)  # 会从服务器传对应的值过来，性能慢
        if res:
            return res.decode()  # 从redis里面拿到的是bytes类型的数据，需要转换一下

    def str_set(self, k, v, time=None):  # time默认失效时间
        self.r.set(k, v, time)

    def delete(self, k):
        tag = self.r.exists(k)
        # 判断这个key是否存在,相对于get到这个key他只是传回一个存在火灾不存在的信息，
        # 而不用将整个k值传过来（如果k里面存的东西比较多，那么传输很耗时）
        if tag:
            self.r.delete(k)
        else:
            self.record_log('key:{} not found'.format(k), 'error')

    def hash_get(self, name, k):  # 哈希类型存储的是多层字典（嵌套字典）
        res = self.r.hget(name, k)
        if res:
            return res.decode()  # 因为get不到值得话也不会报错所以需要判断一下

    def hash_set(self, name, k, v):
        self.r.hset(name, k, v)

    def hash_get_all(self, name):
        res = self.r.hgetall(name)
        data = {}
        if res:
            for k, v in res.items():
                k = k.decode()
                v = v.decode()
                data[k] = v
        return data

    def hash_del(self, name, k):
        res = self.r.hdel(name, k)
        if res:
            return 1
        else:
            self.record_log('delete failed, key:{} not found'.format(k), 'error')
            return 0

    def list_lpush(self, name, v):
        self.r.lpush(name, v)

    def list_lpop(self, name):
        return self.r.lpop(name)

    def clean_redis(self):
        self.r.flushdb()
        self.record_log('flushdb successfully' 'info')
        return 0


    def record_log(self, str, level):
        print(str)
