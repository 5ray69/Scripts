# -*- coding: utf-8 -*
# dU стояков + dU магистралей
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

dU_stoyakov = IN[0]
dU_magistraley_on_level = IN[1]

sum_dU_stoy_and_dU_mag = {}

# округлено до ближайшего большего десятичного  + 0.05
for key_group, value_dU in dU_magistraley_on_level.items():
    if key_group not in sum_dU_stoy_and_dU_mag:
        sum_dU_stoy_and_dU_mag[key_group] = []
    if key_group in dU_stoyakov:
        sum_dU_stoy_and_dU_mag[key_group].append(str(round((dU_stoyakov[key_group][0] + value_dU[0]) + 0.05, 1)))
    else:
        sum_dU_stoy_and_dU_mag[key_group].append(str(round((dU_magistraley_on_level[key_group][0]) + 0.05, 1)))

OUT = sum_dU_stoy_and_dU_mag


# ПРОСУММИРОВАЛИ ДВА СЛОВАРЯ, В ИТОГОВОМ СЛОВАРЕ СОЗДАЮТСЯ КЛЮЧИ ИЗ КАЖДОГО СЛОВАРЯ
# # суммируем значения магистралей
# for key_group, value_dU in dU_magistraley_on_level.items():
#     if key_group not in sum_dU_stoy_and_dU_mag:
#         # 0.0 в списке иначе не сможет извлечь элемент в пустом списке по индексу
#         sum_dU_stoy_and_dU_mag[key_group] = [0.0]
#     # суммируем значения
#     sum_dU_stoy_and_dU_mag[key_group] = [sum_dU_stoy_and_dU_mag[key_group][0] + value_dU[0]]

# # суммируем значения стояков
# for key_group, value_dU in dU_stoyakov.items():
#     if key_group not in sum_dU_stoy_and_dU_mag:
#         # 0.0 в списке иначе не сможет извлечь элемент в пустом списке по индексу
#         sum_dU_stoy_and_dU_mag[key_group] = [0.0]
#     # суммируем значения
#     sum_dU_stoy_and_dU_mag[key_group] = [sum_dU_stoy_and_dU_mag[key_group][0] + value_dU[0]]

# # округляем и преобразовываем числа в строку
# for key, value in sum_dU_stoy_and_dU_mag.items():
#     sum_dU_stoy_and_dU_mag[key] = [str(round(value[0], 2))]

# OUT = sum_dU_stoy_and_dU_mag

# dU_stoyakov = {"гр.1":1.0, "гр.1А":1.0, "гр.2":1.0, "гр.2А":1.0, "гр.5":1.0, "гр.5А":1.0}
# dU_magistraley_on_level = {"гр.1":3.0, "гр.1А":3.0, "гр.2":3.0, "гр.2А":3.0, "гр.3":3.0, "гр.3А":3.0, "гр.4":3.0, "гр.4А":3.0}

# # СТОЯКИ НА IN[0], МАГИСТРАЛИ НА IN[1]

# # из ключей словаря стояков вычли ключи словаря магистралей и так узнали
# # какая группа промаркированная как "магистраль" не имеет стояка,
# # то есть должна была бы быть промаркирована как "линия"
# dU_stoyakov = IN[0]
# dU_magistraley_on_level = IN[1]

# list_stoy = set([group for group in dU_stoyakov.keys()])
# list_mag = set([group for group in dU_magistraley_on_level.keys()])

# # группы, которые должны были быть промаркированы как "линия" или не проложен для них стояк,
# # которые есть в магистралях, но их нет в стояках
# OUT = list_mag - list_stoy

def int_in_string(string):
    if 'А' in string:
        return int(string[3:len(string)-1])
    if 'А' not in string:
        return int(string[3:len(string)])


lt_s = ["гр.3", "гр.1А", "гр.1", "гр.11А", "гр.5", "гр.4", "гр.17А", "гр.20", "гр.16А", "гр.22", "гр.7А", "гр.18А", "гр.22А", "гр.41"]

# b = sorted(a, key=lambda t: (t[1], -t[0]))

L_s = []
for str_l in lt_s:
       L_s.append(int_in_string(str_l))


b = sorted(lt_s, key=lambda string: ('А' in string, int_in_string(string)))

bprint(b)
