# module unit.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB  # noqa


class Unit(object):
    def __init__(self, doc, value, is_display=True,
                 unit_type=DB.SpecTypeId.Length):
        self._doc = doc
        self._unit_type = unit_type
        self._internal_value = self._convert_value(value, is_display) \
            if is_display else value

    def _convert_value(self, value, to_internal):
        conversion_method = DB.UnitUtils.ConvertToInternalUnits \
            if to_internal else DB.UnitUtils.ConvertFromInternalUnits
        return conversion_method(value, self._doc.GetUnits() \
            .GetFormatOptions(self._unit_type).GetUnitTypeId())

    @property
    def unit_type(self):
        '''Тип единиц'''
        return DB.LabelUtils.GetLabelForSpec(self._unit_type)

    @property
    def display_units(self):
        '''Обозначение единиц (длинный символ) в настройках едениц проекта'''
        return DB.LabelUtils.GetLabelForUnit(self._doc.GetUnits() \
            .GetFormatOptions(self._unit_type).GetUnitTypeId())

    @property
    def internal(self):
        '''Числовое значение во внутренних единицах Revit'''
        return self._internal_value

    @property
    def display(self):
        '''Числовое значение в единицах интерфейса Revit'''
        return self._convert_value(self._internal_value, False)

    def _unit_type_equals(self, other):
        '''Метод для проверки совпадения типа единиц исходного
        и другого объекта'''
        check_passed = self._unit_type == other.unit_type
        if not check_passed:
            print 'Ошибка операции: тип единиц операндов не совпадает'
        return check_passed

    def _set_internal_value(self, value):
        '''Метод присвоения полю _internal_value нового значения'''
        self._internal_value = value
        return self

    def __le__(self, other):
        '''Магический метод оператора меньше или равно'''
        if self._unit_type_equals(other):
            return self._internal_value <= other.internal

    def __add__(self, other):
        '''Магический метод оператора сложение'''
        if self._unit_type_equals(other):
            return Unit(self._doc,
                        self._internal_value + other.internal,
                        False,
                        self._unit_type)

    def __sub__(self, other):
        '''Магический метод оператора вычитание'''
        if self._unit_type_equals(other):
            return Unit(self._doc,
                        self._internal_value - other.internal,
                        False,
                        self._unit_type)

    def __eq__(self, other):
        '''Магический метод оператора сравнение'''
        if self._unit_type_equals(other):
            return self._internal_value == other.internal

    def __mul__(self, other):
        '''Магический метод оператора умножение'''
        if self._unit_type_equals(other):
            return Unit(self._doc,
                        self._internal_value * other.internal,
                        False,
                        self._unit_type)

    def __lt__(self, other):
        '''Магический метод оператора меньше'''
        if self._unit_type_equals(other):
            return self._internal_value < other.internal

    def __div__(self, other):
        '''Магический метод оператора деление'''
        if self._unit_type_equals(other):
            return Unit(self._doc,
                        self._internal_value / other.internal,
                        False,
                        self._unit_type)

    def __ne__(self, other):
        '''Магический метод оператора неравенства'''
        if self._unit_type_equals(other):
            return self._internal_value != other.internal

    def __gt__(self, other):
        '''Магический метод оператора больше'''
        if self._unit_type_equals(other):
            return self._internal_value > other.internal

    def __str__(self):
        '''Магический метод пределяет поведение функции str(),
        вызванной для экземпляра вашего класса'''
        return '{} | {} | {} | {}'.format(
            self.display,
            self.internal,
            self.unit_type,
            self.display_units_forgeTypeId
        )

    def __neg__(self):
        '''Магический метод унарный знак минуса (-self)'''
        return self._set_internal_value(-self._internal_value)

    def __ge__(self, other):
        '''Магический метод оператора больше или равно'''
        if self._unit_type_equals(other):
            return self._internal_value >= other.internal
