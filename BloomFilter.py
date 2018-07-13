#!/usr/bin/python3

from bitarray import bitarray

import mmh3
import sys
import json
import os
import tornado
import jieba

sens_words_dict = object

class BFilter(set):
    def __init__(self, size, hash_count):
        super(BFilter, self).__init__()
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)
        self.size = size
        self.hash_count = hash_count

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self.bit_array)

    def add(self, item):
        for ii in range(self.hash_count):
            index = mmh3.hash(item.encode("utf-8"), ii) % self.size
            self.bit_array[index]  = 1
        return self

    def __contains__(self, item):
        out = True
        for ii in range(self.hash_count):
            index = mmh3.hash(item.encode("utf-8"), ii) % self.size
            if self.bit_array[index] == 0:
                out = False
                break
        return out

    def load_words(self, filepath):
        ifile = open(filepath)
        for line in ifile:
            line.strip('\n')
            line.strip('\r')
            line.strip('\r\n')
            self.add(line[:-1])
            print(line[:-1] in self)
            print(line[:-1].encode("utf-8"))
        ifile.close()

class SensFilterHandler(tornado.web.RequestHandler):
    def get(self):
        sentence = self.get_argument("words")
        words = jieba.cut(sentence)
        ret = 1
        for word in words:
            if word in sens_words_dict:
                ret = -1
                break
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        result = {"result": ret}
        self.write(json.dumps(result))


