# -*- coding: utf-8 -*
# modul parameters
import clr  # чтоб посредством phyton получать доступ к бибилиотекам dot.net(к файлам формата dll)
clr.AddReference('RevitAPI')  # Передача модулю clr ссылки на файл RevitAPI.dll
from Autodesk.Revit import DB  # импортировали пространство имен DB


def get_parameter_value_v1(parameter):  # здесь значения Double выводятся в едbницах, как на экране Ревит (в мм, не в футах)
    if isinstance(parameter, DB.Parameter):
        storage_type = parameter.StorageType  # свойство StorageType примененное к объекту класса Parameter возвращает StorageType параметра (объекта)
        if storage_type == DB.StorageType.Integer:
            return parameter.AsInteger()
        elif storage_type == DB.StorageType.Double:
            return DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), parameter.DisplayUnitType) #значения Double выводятся в единицах, как на экране Ревит
        elif storage_type == DB.StorageType.String:
            return parameter.AsString()
        elif storage_type == DB.StorageType.ElementId:
            return parameter.AsElementId()


def get_parameter_value_v2(parameter):  # здесь значения Double выводятся в футах
    if isinstance(parameter, DB.Parameter):
        storage_type = parameter.StorageType  # свойство StorageType примененное к объекту класса Parameter возвращает StorageType параметра (объекта)
        if storage_type:
            exec 'parameter_value = parameter.As{}()'.format(storage_type)
            return parameter_value
