# -*- coding: utf-8 -*
# dU цепи длины магистралей по этажам
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

# ПРОВЕРКА цепи в имени которых есть "гр", у которых классификация нагрузок не освещение
koef_circuit = 1.05  # коэффициент запаса на длину цепи
mag_group_sum_circuit = {}  # словарь сумм длин магистралей по группам
all_group_c = {}  # словарь всех длин по группам
mag = []
styk = []
for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
    if not el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
        if doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name == 'Освещение':
            if 'гр' in el_circuit.Name:
                # circuit_cl.append(el_circuit)
                # circuit_cl.append(el_circuit.Name)
            # Будова_Этаж (str)
                # circuit_cl.append(el_circuit.LookupParameter('БУДОВА_Этаж').AsString())
            # Будова_Группа
                # circuit_cl.append(el_circuit.LookupParameter('БУДОВА_Группа').AsString())
            # БУДОВА_Признак цепи (str) отделили коэффициенты стояков от магистралей 
                if 'магистраль' in el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString():
                    parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]  # Длина цепи полная
                    unit = parameter.GetUnitTypeId()
                    leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали длину цепи во внешние единицы/как на экране пользователя
                    leng_koef = koef_circuit * leng  # длина цепи с коэффициентом запаса
                    # Коэффициент длины для dU (не полная длина):
                    str_mag = el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString()[:2]  # два первых символа для коэф длины при расчете dU
                    group_c = el_circuit.LookupParameter('БУДОВА_Группа').AsString()
                    if group_c not in mag_group_sum_circuit:
                        mag_group_sum_circuit[group_c] = [0]
                    mag_sum = mag_group_sum_circuit[group_c].pop() + (float(str_mag[0] + '.' + str_mag[1]) * leng_koef)
                    # Длина магистралей для dU (коэффициент запаса и коэффициент из празнака цепи):
                    mag_group_sum_circuit[group_c].append(mag_sum)  # float(str_mag[0] + '.' + str_mag[1]) - это коэф получающийся из строки признака цепи

OUT = mag_group_sum_circuit




# # Отобрали по глобальному имени группы длины магистралей (чтоб потом выбрать из них максимальную)
# mag_global_group_sum_circuit = {}
# for key, value in mag_group_sum_circuit.items():
#     if (key[:key.rfind(".")]) not in mag_global_group_sum_circuit:
#         mag_global_group_sum_circuit[key[:key.rfind(".")]] = []
#     mag_global_group_sum_circuit[key[:key.rfind(".")]].append(value[0])

# OUT = mag_global_group_sum_circuit




# # Но на самом деле нужно отбирать максимальный момент этажа, а не максимальную длину линии
# # Отобрали максимальные значения магистралей (наибольшую длину из всех этажей)
# mag_global_group_sum_max_circuit = {}
# for key, value in mag_global_group_sum_circuit.items():
#     mag_global_group_sum_max_circuit[key] = sorted(value)[-1:]

# OUT = mag_global_group_sum_max_circuit
