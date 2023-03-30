# -*- coding: utf-8 -*
# dU строки округления для мощности
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа


in_dict = IN[0]

out_dict = {}

# округлено до ближайшего большего сотого  + 0.005
for key, value in in_dict.items():
    if key not in out_dict:
        out_dict[key] = str(round((value[0] + 0.005), 2))

OUT = out_dict

# # dU строки округления для косинусов нет, они приходят готовыми

# # dU строки округления для токов нет, они приходят готовыми


#  -*- coding: utf-8 -*
# # dU строки округления для длин
# import clr
# clr.AddReference('RevitAPI')
# clr.AddReference('RevitServices')  # Работа с документом и транзакциями
# from Autodesk.Revit import DB
# from Autodesk.Revit.DB import FilteredElementCollector as FEC
# from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

# doc = DM.Instance.CurrentDBDocument # Получение файла документа


# in_dict = IN[0]

# out_dict = {}

# for key, value in in_dict.items():
#     if key not in out_dict:
#     	out_dict[key] = str(round(value[0], 0))[:-2]

# OUT = out_dict


# # -*- coding: utf-8 -*
# # dU строки округления для типа кабеля
# import clr
# clr.AddReference('RevitAPI')
# clr.AddReference('RevitServices')  # Работа с документом и транзакциями
# from Autodesk.Revit import DB
# from Autodesk.Revit.DB import FilteredElementCollector as FEC
# from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

# doc = DM.Instance.CurrentDBDocument # Получение файла документа


# in_dict = IN[0]

# out_dict = {}

# # округлено до ближайшего большего сотого  + 0.005
# for key, value in in_dict.items():
#     if key not in out_dict:
#     	out_dict[key] = value[0]

# OUT = out_dict





