# module v4.2.6_test.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

from revitutils.unit import Unit
from revitutils.functions import unit_converter

doc = __revit__.ActiveUIDocument.Document  # noqa

length_unit_type = DB.SpecTypeId.Length
length_internal = unit_converter(doc, 1500, True)
length_display = unit_converter(doc, length_internal)

unit_forgTypeid = doc.GetUnits().GetFormatOptions(length_unit_type).GetUnitTypeId()
for symbol in DB.FormatOptions.GetValidSymbols(unit_forgTypeid):
    if not symbol.Empty():
        short_symbol = DB.LabelUtils.GetLabelForSymbol(symbol)

print '{}  |  {}  |  {}  |  {}  |  {}  |  {}  |  {}\n'.format(
    length_display,
    length_internal,
    length_unit_type.TypeId,
    DB.LabelUtils.GetLabelForSpec(length_unit_type),
    doc.GetUnits().GetFormatOptions(length_unit_type).GetUnitTypeId().TypeId,
    DB.LabelUtils.GetLabelForUnit(doc.GetUnits().GetFormatOptions(length_unit_type).GetUnitTypeId()),
    short_symbol
)

angle_unit_type = DB.SpecTypeId.Angle
angle_internal = unit_converter(doc, 120, True, angle_unit_type)
angle_display = unit_converter(
    doc, angle_internal, unit_type=angle_unit_type)

unit_forgTypeid = doc.GetUnits().GetFormatOptions(angle_unit_type).GetUnitTypeId()
for symbol in DB.FormatOptions.GetValidSymbols(unit_forgTypeid):
    if not symbol.Empty():
        short_symbol = DB.LabelUtils.GetLabelForSymbol(symbol)

print '{}  |  {}  |  {}  |  {}  |  {}  |  {}  |  {}\n'.format(
    angle_display,
    angle_internal,
    angle_unit_type.TypeId,
    DB.LabelUtils.GetLabelForSpec(angle_unit_type),
    doc.GetUnits().GetFormatOptions(angle_unit_type).GetUnitTypeId().TypeId,
    DB.LabelUtils.GetLabelForUnit(doc.GetUnits().GetFormatOptions(angle_unit_type).GetUnitTypeId()),
    short_symbol
)
# Результаты:
# >>> 
# ﻿1500.0  |  4.9213  |  autodesk.spec.aec:length-2.0.0  |  Длина  |  autodesk.unit.unit:millimeters-1.0.1  |  Миллиметры  |  мм

# 120.0  |  2.0944  |  autodesk.spec.aec:angle-2.0.0  |  Угол  |  autodesk.unit.unit:degrees-1.0.1  |  Градусы  |  °

# >>>
