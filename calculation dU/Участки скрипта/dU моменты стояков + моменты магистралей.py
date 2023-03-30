# -*- coding: utf-8 -*
# dU моменты стояков + моменты магистралей
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

moment_stoyakov = IN[0]
moment_magistraley_on_level = IN[1]

sum_moment_stoy_and_moment_mag = {}

# округлено до ближайшего большего целого  + 0.5
for key_group, value_moment in moment_magistraley_on_level.items():
    if key_group not in sum_moment_stoy_and_moment_mag:
        sum_moment_stoy_and_moment_mag[key_group] = []
    if key_group in moment_stoyakov:
        sum_moment_stoy_and_moment_mag[key_group].append(str(round((moment_stoyakov[key_group][0] + value_moment[0]) + 0.5, 0))[:-2])
    else:
        sum_moment_stoy_and_moment_mag[key_group].append(str(round((moment_magistraley_on_level[key_group][0]) + 0.5, 0))[:-2])

OUT = sum_moment_stoy_and_moment_mag




# # ПРОСУММИРОВАЛИ ДВА СЛОВАРЯ, В ИТОГОВОМ СЛОВАРЕ СОЗДАЮТСЯ КЛЮЧИ ИЗ КАЖДОГО СЛОВАРЯ
# # суммируем значения магистралей
# for key_group, value_dU in moment_magistraley_on_level.items():
#     if key_group not in sum_moment_stoy_and_moment_mag:
#         # 0.0 в списке иначе не сможет извлечь элемент в пустом списке по индексу
#         sum_moment_stoy_and_moment_mag[key_group] = [0.0]
#     # суммируем значения
#     sum_moment_stoy_and_moment_mag[key_group] = [sum_moment_stoy_and_moment_mag[key_group][0] + value_dU[0]]

# # суммируем значения стояков
# for key_group, value_dU in moment_stoyakov.items():
#     if key_group not in sum_moment_stoy_and_moment_mag:
#         # 0.0 в списке иначе не сможет извлечь элемент в пустом списке по индексу
#         sum_moment_stoy_and_moment_mag[key_group] = [0.0]
#     # суммируем значения
#     sum_moment_stoy_and_moment_mag[key_group] = [sum_moment_stoy_and_moment_mag[key_group][0] + value_dU[0]]

# # округляем и преобразовываем числа в строку
# for key, value in sum_moment_stoy_and_moment_mag.items():
#     sum_moment_stoy_and_moment_mag[key] = [str(round(value[0], 2))]

# OUT = sum_moment_stoy_and_moment_mag
