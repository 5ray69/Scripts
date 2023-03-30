# -*- coding: utf-8 -*
# module take_magistral.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


class LengthCircuit(object):
    '''Возвращает значения в зависимости от длины цепи, идущей от ЩЭ до ЩК'''
    def __init__(self, leng):
        self.leng = leng

    def for_black_tag(self):
        # цвет марки панели черный
        if self.leng < 25:
            return 1
        if 25 <= self.leng < 40:
            return 0
        if self.leng >= 40:
            return 0

    def for_red_tag(self):
        # цвет марки панели красный
        if self.leng < 25:
            return 0
        if 25 <= self.leng < 40:
            return 1
        if self.leng >= 40:
            return 0

    def for_green_tag(self):
        # цвет марки панели зеленый
        if self.leng < 25:
            return 0
        if 25 <= self.leng < 40:
            return 0
        if self.leng >= 40:
            return 1

    def integer_Id_cable_for_length(self):
        # 'ВВГнг-LS 3х10' ElementId 356553
        if self.leng < 25:
            return 356553
        # 'ВВГнг-LS 3х16' ElementId 356554
        if 25 <= self.leng < 40:
            return 356554
        # 'ВВГнг-LS 3х25' ElementId 356572
        if self.leng >= 40:
            return 356572
