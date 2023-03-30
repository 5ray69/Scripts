# module v4.2.6_test.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB


def unit_converter(
        doc,
        value,
        to_internal=False,
        unit_type=DB.SpecTypeId.Length,  # тип единиц (объект класса ForgeTypeId())
        number_of_digits=None):  # возможность округления до целого числа или десятичных знаков
    display_units = doc.GetUnits().GetFormatOptions(
        unit_type).GetUnitTypeId()  # получили объект ForgeTypeId
    method = DB.UnitUtils.ConvertToInternalUnits if to_internal \
        else DB.UnitUtils.ConvertFromInternalUnits
    if number_of_digits is None:
        return method(value, display_units)
    elif number_of_digits > 0:
        return round(method(value, display_units), number_of_digits)
    return int(round(method(value, display_units), number_of_digits))

doc = __revit__.ActiveUIDocument.Document  # noqa

#  Теперь произведем простейшие конвертации длин и углов из единиц
#  интерфейса во внутренние и наоборот. Для начала по старинке
#  воспользуемся функцией unit_converter:

length_unit_type = DB.SpecTypeId.Length
length_internal = unit_converter(doc, 1500, True)
length_display = unit_converter(doc, length_internal)

unit_forgTypeid = doc.GetUnits().GetFormatOptions(length_unit_type).GetUnitTypeId()  # Получаем ForgeTypeId идентификатор единицы unitTypeId
# получили все возможные краткие символы единиц измерения (для метрических единиц в основном один символ для каждой единицы
# short_symbol = [DB.LabelUtils.GetLabelForSymbol(symbol) for symbol in DB.FormatOptions.GetValidSymbols(unit_forgTypeid) if not symbol.Empty()]
# bprint(short_symbol)
for symbol in DB.FormatOptions.GetValidSymbols(unit_forgTypeid):
    if not symbol.Empty():
        short_symbol = DB.LabelUtils.GetLabelForSymbol(symbol)  # получили краткий символ, обозначение единиц измерения (например, мм)

print '{}  |  {}  |  {}  |  {}  |  {}  |  {}  |  {}\n'.format(
    length_display,
    length_internal,
    length_unit_type.TypeId,  # получили строку ForgeTypeId
    DB.LabelUtils.GetLabelForSpec(length_unit_type),  # получили имя единицы "Длина". Объект ForgeTypeId идентификатор спецификаций specTypeId
    doc.GetUnits().GetFormatOptions(length_unit_type).GetUnitTypeId().TypeId,  # получили строку Идентификатор схемы.
    DB.LabelUtils.GetLabelForUnit(doc.GetUnits().GetFormatOptions(length_unit_type).GetUnitTypeId()),  # получили имя символа "Миллиметры". Объект ForgeTypeId идентификатор единиц unitTypeId
    short_symbol  # получили все возможные краткие символы единиц измерения (для метрических единиц в основном один символ для каждой единицы
)

    # DB.FormatOptions.GetValidSymbols(doc.GetUnits().GetFormatOptions(length_unit_type).GetUnitTypeId()),  # получили все возможные единицы измерения, напрмер для "Длины" (мм, см, дм, м)


# for unit in DB.UnitUtils.GetAllUnits():  # Получаем идентификаторы ForgeTypeId всех доступных единиц и итерируем по одному
#     for symbol in DB.FormatOptions.GetValidSymbols(unit):  # Получаем идентификатор ForgeTypeId символов для данной единицы и итерируем по одному
#         if not symbol.Empty():
#             if DB.LabelUtils.GetLabelForSymbol(symbol) == 'мм':
#                 print DB.LabelUtils.GetLabelForSymbol(symbol)  # получили краткий символ, обозначение единиц измерения (например, мм)


# результаты
# 1500.0  |  4.9213  |  UT_Length  |  DUT_MILLIMETERS
# 120.0  |  2.0944  |  UT_Angle  |  DUT_DECIMAL_DEGREES

# мои результаты (углы, видимо, в радианах, а не в десятичных градусах)
# >>> 
# ﻿1500.0  |  4.9213  |  <Autodesk.Revit.DB.ForgeTypeId object at 0x0000000000000036 [Autodesk.Revit.DB.ForgeTypeId]>  |  <Autodesk.Revit.DB.FormatOptions object at 0x0000000000000037 [Autodesk.Revit.DB.FormatOptions]>
# 120.0  |  0.3937  |  <Autodesk.Revit.DB.ForgeTypeId object at 0x0000000000000038 [Autodesk.Revit.DB.ForgeTypeId]>  |  <Autodesk.Revit.DB.FormatOptions object at 0x0000000000000039 [Autodesk.Revit.DB.FormatOptions]>
# >>> 

# После этого, аналогичные действия выполним с использованием класса Unit:




# length = Unit(doc, 1500)
# print '{}  |  {}  |  {}  |  {}'.format(
#     length.display,
#     length.internal,
#     length.unit_type,
#     length.display_units
# )

# angle = Unit(doc, 120, unit_type=DB.SpecTypeId.Angle)
# print '{}  |  {}  |  {}  |  {}'.format(
#     angle.display,
#     angle.internal,
#     angle.unit_type,
#     angle.display_units
# )

# результаты
# 1500.0  |  4.9213  |  UT_Length  |  DUT_MILLIMETERS
# 120.0  |  2.0944  |  UT_Angle  |  DUT_DECIMAL_DEGREES
