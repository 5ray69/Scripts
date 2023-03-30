# module boundingbox.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from geometry.align import Align
from iterfunctions import to_list


class BoundingBoxXYZExtended(DB.BoundingBoxXYZ):
    '''
    Габаритный ящик с дополнительными методами, расширяющими стандартный
    функционал родительского класса.
    '''
    def __init__(self, length=1, width=1, height=1):
        '''Конструктор класса позволяет создать объект на основе трех указанных
        величин габаритов ящика: длины, ширины и высоты. Значения указываются
        в футах'''
        super(BoundingBoxXYZExtended, self).__init__()
        self.length = length
        self.width = width
        self.height = height

    def _get_dimension(self, i):
        '''
        Получение величины одного из трех габаритов ящика по индексу
        i - индекс габарита:
            0 - длина
            1 - ширина
            2 - высота
        '''
        return self.Max[i] - self.Min[i]

    def _set_dimension(self, i, value, align=Align.CENTER):
        '''
        Изменение величины одного из трех габаритов ящика по индексу и
        типу привязки.
        i - индекс габарита:
            0 - длина
            1 - ширина
            2 - высота
        value - величина габарита
        align - привязка, перечисление Align:
            Align.START - привязка по начальной точке
            Align.CENTER - привязка по центру
            Align.END - привязка по конечной точке
        '''
        min_value = -value / 2.0 * align
        min_coordinates = [self.Min[j] for j in range(3)]
        max_coordinates = [self.Max[j] for j in range(3)]
        min_coordinates[i] = min_value
        max_coordinates[i] = min_value + value
        self.Min = DB.XYZ(*min_coordinates)
        self.Max = DB.XYZ(*max_coordinates)

    @property
    def length(self):
        '''Получение длины ящика'''
        return self._get_dimension(0)

    @length.setter
    def length(self, value):
        '''Задание длины ящика (с центральной привязкой)'''
        self._set_dimension(0, value)

    @property
    def width(self):
        '''Получение ширины ящика'''
        return self._get_dimension(1)

    @width.setter
    def width(self, value):
        '''Задание ширины ящика (с центральной привязкой)'''
        self._set_dimension(1, value)

    @property
    def height(self):
        '''Получение высоты ящика'''
        return self._get_dimension(2)

    @height.setter
    def height(self, value):
        '''Задание высоты ящика (с центральной привязкой)'''
        self._set_dimension(2, value)

    def align(self, i, align):
        '''
        Задание привязки указанному габариту ящика.
        Метод берет исходную величину габарита ящика и смещает
        точки минимума и максимума в соответствии с типом привязки
        i - индекс габарита:
            0 - длина
            1 - ширина
            2 - высота
        align - привязка, перечисление Align:
            Align.START - привязка по начальной точке
            Align.CENTER - привязка по центру
            Align.END - привязка по конечной точке
        '''
        if align not in range(3):
            raise Exception('Некорректное значение привязки')
        self._set_dimension(i, self._get_dimension(i), align)

    @property
    def origin(self):
        '''Получение точки начала ящика'''
        return self.Transform.Origin

    @origin.setter
    def origin(self, origin):
        '''Задание точки начала ящика'''
        transform = self.Transform
        transform.Origin = origin
        self.Transform = transform

    @property
    def center(self):
        '''Получение центра габаритного ящика'''
        return (self.Min + self.Max) / 2

    @staticmethod
    def create(b_box):
        '''Статический метод, позволяющий создать новый экземпляр данного класса
        на основе другого габаритного ящика'''
        b_box_extended = BoundingBoxXYZExtended()
        b_box_extended.Min = b_box.Min
        b_box_extended.Max = b_box.Max
        return b_box_extended

    @property
    def solid(self):
        ''' 4.4.7 Получение объекта класса Solid, совпадающего по габаритам
        и трансформации с исходным габаритным ящиком'''
        pt1 = self.Min
        pt2 = pt1 + DB.XYZ.BasisX * self.length
        pt3 = pt2 + DB.XYZ.BasisY * self.width
        pt4 = pt1 + DB.XYZ.BasisY * self.width
        solid = DB.GeometryCreationUtilities.CreateExtrusionGeometry(
            to_list(
                [
                    DB.CurveLoop.Create(
                        to_list(
                            [
                                DB.Line.CreateBound(pt1, pt2),
                                DB.Line.CreateBound(pt2, pt3),
                                DB.Line.CreateBound(pt3, pt4),
                                DB.Line.CreateBound(pt4, pt1),
                            ],
                            DB.Curve
                        )
                    )
                ],
                DB.CurveLoop
            ),
            DB.XYZ.BasisZ,
            self.height
        )
        return DB.SolidUtils.CreateTransformed(solid, self.Transform)
