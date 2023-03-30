# -*- coding: utf-8 -*
# module conduit_for_forge.py

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
clr.AddReference("System.Core")  # для Linq
import System  # для Linq
clr.ImportExtensions(System.Linq)  # для Linq
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
]

doc = DM.Instance.CurrentDBDocument  # Получение файла документа

its = []
for conduit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_Conduit).WhereElementIsNotElementType().ToElements():
    # получили имя типоразмера короба из короба
    its.append(DB.Element.Name.GetValue(conduit))
OUT = its