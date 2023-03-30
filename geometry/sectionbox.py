# module sectionbox.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

from geometry.align import Align
from geometry.boundingbox import BoundingBoxXYZExtended


class SectionBoxXYZ(BoundingBoxXYZExtended):
    '''
    Габаритный ящик для создания сечений. Имеет расширенный конструктор,
        а также подобающие имена атрибутов для более удобного и интуитивного
        создания габаритных ящиков, используемых при генерации сечений.
    В классе есть три константы, обозначающие режим создания сечения:
        VERTICAL - вертикальное сечение;
        HORIZONTAL_DOWN - горизонтальное сечение, направленное вниз;
        HORIZONTAL_UP - горизонтальное сечение, направленное вверх.
    '''
    VERTICAL = 0
    HORIZONTAL_DOWN = -1
    HORIZONTAL_UP = 1

    def __init__(self, s_length, s_height, s_depth, mode, orientation_vector,
                 origin=DB.XYZ.Zero):
        '''
        Параметры, овтечающие за габариты ящика, имеют отличные
        от родительского класса имена, созвучные с габаритами будущего сечения:
            s_length - длина (сечения)
            s_height - высота (сечения)
            s_depth - глубина (сечения)
        mode - режим создания сечения, задается через следующие константы:
            SectionBoxXYZ.VERTICAL - вертикальное сечение;
            SectionBoxXYZ.HORIZONTAL_DOWN - горизонтальное сечение (вниз);
            SectionBoxXYZ.HORIZONTAL_UP - горизонтальное сечение (вверх)
        orientation_vector - вектор, задающий направление сечения:
            для горизонтальных сечений - RightDirection,
                (направление вдоль длины сечения);
            для вертикальных - DepthDirection,
                (направление вдоль глубины сечения).
        origin - точка размещения сечения
        Для глубины сечения сразу же задается привязка "по начальной точке".
        '''
        super(SectionBoxXYZ, self).__init__(s_length, s_height, s_depth)
        self._set_orientation(*self._get_basises(mode, orientation_vector))
        self.align(2, Align.START)
        self.origin = origin

    def _get_basises(self, mode, orientation_vector):
        '''
        Получение базисных векторов на основе указанного режима
        создания сечения и вектора, задающего его направление
        mode - режим создания сечения, задается через следующие константы:
            SectionBoxXYZ.VERTICAL - вертикальное сечение;
            SectionBoxXYZ.HORIZONTAL_DOWN - горизонтальное сечение (вниз);
            SectionBoxXYZ.HORIZONTAL_UP - горизонтальное сечение (вверх)
        orientation_vector - вектор, задающий направление сечения:
            для горизонтальных сечений он задает RightDirection,
                (направление вдоль длины сечения);
            для вертикальных - DepthDirection,
                (направление вдоль глубины сечения).
        '''
        if mode:
            right_direction = orientation_vector
            depth_direction = DB.XYZ.BasisZ * mode
            up_direction = -right_direction.CrossProduct(depth_direction)
        else:
            depth_direction = orientation_vector
            up_direction = DB.XYZ.BasisZ
            right_direction = -depth_direction.CrossProduct(up_direction)
        return right_direction, up_direction, depth_direction

    def _set_orientation(
            self,
            right_direction,
            up_direction,
            depth_direction):
        '''
        Задание ориентации ящика путем указания базисных векторов
        его объекта трансформации:
            right_direction - направление вдоль длины сечения,
                совпадает с RigthDirection;
            up_direction - направление вдоль высоты сечения,
                совпадает с UpDirection;
            depth_direction - направление вдоль глубины сечения,
                противоположно ViewDirection.
        '''
        transform = self.Transform
        for i, basis in enumerate(
                [
                    right_direction,
                    up_direction,
                    depth_direction
                ]):
            transform.Basis[i] = basis.Normalize()
        self.Transform = transform





