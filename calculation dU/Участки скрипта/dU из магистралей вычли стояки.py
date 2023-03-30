# -*- coding: utf-8 -*
# dU из магистралей вычли стояки
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

# СТОЯКИ НА IN[0], МАГИСТРАЛИ НА IN[1]

# из ключей словаря стояков вычли ключи словаря магистралей и так узнали
# какая группа промаркированная как "магистраль" не имеет стояка,
# то есть должна была бы быть промаркирована как "линия"
dU_stoyakov = IN[0]
dU_magistraley_on_level = IN[1]

list_stoy = set([group for group in dU_stoyakov.keys()])
list_mag = set([group for group in dU_magistraley_on_level.keys()])

# группы, которые должны были быть промаркированы как "линия" или не проложен для них стояк,
# которые есть в магистралях, но их нет в стояках
OUT = list_mag - list_stoy
