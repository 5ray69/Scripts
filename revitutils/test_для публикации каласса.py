# module v4.2.6_test_for_class.py
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


length = Unit(doc, 1500)
print '{}  |  {}  |  {}  |  {}'.format(
    length.display,
    length.internal,
    length.unit_type,
    length.display_units
)

# теперь вместо константы подаем свойство класса SpecTypeId
angle = Unit(doc, 120, unit_type=DB.SpecTypeId.Angle)
print '{}  |  {}  |  {}  |  {}'.format(
    angle.display,
    angle.internal,
    angle.unit_type,
    angle.display_units
)

# Результаты:
# >>> 
# ﻿1500.0  |  4.9213  |  Длина  |  Миллиметры
# 120.0  |  2.0944  |  Угол  |  Градусы
# >>> 