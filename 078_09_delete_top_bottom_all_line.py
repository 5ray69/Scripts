# -*- coding: utf-8 -*
# module 078_09_text_top_bottom_ level.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo

with DB.Transaction(doc, 'Delete_lines_top_bottom') as t:
    t.Start()
    # катеогория линии
    LinesCat = doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
    # подкатегория BDV_E000_С_top_bottom_level (выбрали существующий в проекте стиль линий)
    top_bottom = LinesCat.SubCategories.get_Item("BDV_E000_С_top_bottom_level")
    # получили типизированный список Id линий для удаления стиля BDV_E000_С_top_bottom_level
    line_ids = List[DB.ElementId]([line.Id for line in FEC(doc).OfCategory(DB.BuiltInCategory.OST_Lines) \
                    if 'top_bottom' in line.LineStyle.GraphicsStyleCategory.Name])
    # удаляем элементы из документа
    doc.Delete(line_ids)
    t.Commit()
