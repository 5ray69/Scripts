# -*- coding: utf-8 -*-
import clr #чтоб посредством phyton получать доступ к бибилиотекам dot.net(к файлам формата dll)
clr.AddReference("RevitAPI") # Передача модулю clr ссылки на файл RevitAPI.dll
clr.AddReference("RevitNodes") # библиотека для работ с нодами и объектами Revit
import Revit
clr.ImportExtensions(Revit.GeometryConversion) #из clr набор расширений динамо для геометрических объектов ревит
from Autodesk.Revit import DB # импорт пространства имен

rebars = UnwrapElement(IN[0]) #разворачивает элемент, одинаково применяется что к одному элементу, что к списку элементов
list = []
for reb in rebars:
    list_Centerline = []
    if isinstance (reb, DB.Structure.Rebar): #проверка на принадлежность классу Rebar
        curves = reb.GetCenterlineCurves(False, False, False, DB.Structure.MultiplanarOption.IncludeOnlyPlanarCurves, 0)
        for c in curves:
            list_Centerline.append(c.ToProtoType()) #превращает линию Revit в аналогичный элемент Dynamo
        list.append(list_Centerline) #формируем список из списков кривых
    else:
        curvs = reb.GetCenterlineCurves(False, False, False)
        for curv in curvs:
            list_Centerline.append(curv.ToProtoType()) #превращает линию Revit в аналогичный элемент Dynamo
        list.append(list_Centerline) #формируем список из списков кривых

OUT = list




# # -*- coding: utf-8 -*-
# import clr #чтоб посредством phyton получать доступ к бибилиотекам dot.net(к файлам формата dll)
# clr.AddReference("RevitAPI") # Передача модулю clr ссылки на файл RevitAPI.dll
# clr.AddReference("RevitNodes") # библиотека для работ с нодами и объектами Revit
# import Revit
# clr.ImportExtensions(Revit.GeometryConversion) #из clr набор расширений динамо для геометрических объектов ревит
# from Autodesk.Revit import DB # импорт пространства имен

# rebars = UnwrapElement(IN[0]) #разворачивает элемент, одинаково применяется что к одному элементу, что к списку элементов
# list = []
# for reb in rebars:
#     list_Centerline = []
#     if isinstance (reb, DB.Structure.Rebar): #проверка на принадлежность классу Rebar
#         curves = reb.GetCenterlineCurves(False, False, False, DB.Structure.MultiplanarOption.IncludeOnlyPlanarCurves, 0)
#         for c in curves:
#             list_Centerline.append(c.ToProtoType()) #превращает линию Revit в аналогичный элемент Dynamo
#         list.append(list_Centerline) #формируем список из списков кривых
#     else:
#         curvs = reb.GetCenterlineCurves(False, False, False)
#         for curv in curvs:
#             list_Centerline.append(curv.ToProtoType()) #превращает линию Revit в аналогичный элемент Dynamo
#         list.append(list_Centerline) #формируем список из списков кривых

# OUT = list
