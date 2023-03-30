# -*- coding: utf-8 -*
# module creates.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List

# import sys
# sys.path += [
#     r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
# ]

from revitutils.unit import Unit

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo


def create_list_lines(p_xyz, n_line = 3, X_right = 1, Y_up = 1):
    '''
    Подаем XYZ, число линий, по Х=1 вправо (-1 влево), по Y=1 вверх (-1 вниз)
    получаем список линиий
    '''
    list_line = []
    for i in range(n_line):
        line = DB.Line.CreateBound(
            DB.XYZ(*[p_xyz[0].X,
                    p_xyz[0].Y + (Y_up)*Unit(doc, i*385).internal,  # -1 вниз, 1 вверх
                    p_xyz[0].Z]
                    ),
            DB.XYZ(*[p_xyz[0].X + (X_right)*Unit(doc, 3200).internal,  # -1 лево, 1 право
                    p_xyz[0].Y + (Y_up)*Unit(doc, i*385).internal,  # -1 вниз, 1 вверх
                    p_xyz[0].Z]
                    )
            )
        list_line.append(line)
    line_vert = DB.Line.CreateBound(
        p_xyz[0],
        DB.XYZ(*[p_xyz[0].X,
                p_xyz[0].Y + (Y_up)*Unit(doc, (n_line - 1)*385).internal,  # -1 вниз, 1 вверх
                p_xyz[0].Z]
                )
        )
    list_line.append(line_vert)
    return list_line
