#!/usr/bin/python3

from bitarray import bitarray

import mmh3
import sys
import os

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


if __name__ == '__main__':
    bloom = BFilter(10000, 10)
    bloom.load_words(sys.argv[1])

    while True:
        animal = input("input: ")
        print(animal.encode("utf-8"))
        if animal in bloom:
            print(animal+" is already in BloomFilter")
        else:
            print(animal+" is not in BloomFilter")
            bloom.add(animal)


