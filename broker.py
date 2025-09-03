#-*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

# Abstract class
class Broker(metaclass=ABCMeta):

    @classmethod
    def getHistory(self, symbol):
        raise NotImplementedError("Impriment getHistory()")


    def readCach(self, filename):
        raise NotImplementedError("Imprement readCach()")


