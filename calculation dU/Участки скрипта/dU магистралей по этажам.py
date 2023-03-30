# -*- coding: utf-8 -*
# dU магистралей по этажам
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

mag_light_sum_power = {}

for light in FEC(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType().ToElements():
    if light.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM):  # если рабочая плоскость не None (проверь строку)
        # мощность светильника
        parameter = doc.GetElement(light.GetTypeId()).LookupParameter('БУДОВА_Активная мощность')  # получили мощность светильника во внутренних единицах
        unit = parameter.GetUnitTypeId()
        power = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали мощность светильника во внешние единицы/как на экране пользователя
        # группа светильника
        group = light.LookupParameter('БУДОВА_Группа').AsString()  # получили имя группы
        # этаж светильника
        level = light.LookupParameter('БУДОВА_Уровень оборудования').AsString()  # получили уровень оборудования
    # мощность светильников по "группа.этаж"
        if group + '.' + level not in mag_light_sum_power:
            mag_light_sum_power[group + '.' + level] = [0.0]
    # просуммировали мощность в каждой "группе.этаже" перевели в кВт
        mag_sum = mag_light_sum_power[group + '.' + level].pop() + power / 1000  # просуммировали мощность в каждой группе.этаже, перевели в кВт
        mag_light_sum_power[group + '.' + level].append(mag_sum)
# OUT = mag_light_sum_power

# ПРОВЕРКА цепи в имени которых есть "гр", у которых классификация нагрузок не освещение
koef_circuit = 1.05  # коэффициент запаса на длину цепи

mag_group_sum_circuit = {}  # словарь сумм длин магистралей по группам
mag_sechenie = {}
for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
    if not el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
        if doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name == 'Освещение':
            if 'гр' in el_circuit.Name:
                # circuit_cl.append(el_circuit.Name)
            # Будова_Этаж (str)
                # circuit_cl.append(el_circuit.LookupParameter('БУДОВА_Этаж').AsString())
            # БУДОВА_Признак цепи (str) отделили коэффициенты стояков от магистралей 
                if 'магистраль' in el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString():
                    parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]  # Длина цепи полная
                    unit = parameter.GetUnitTypeId()
                    leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали длину цепи во внешние единицы/как на экране пользователя
                    leng_with_koef = koef_circuit * leng  # длина цепи с коэффициентом запаса
                    # Коэффициент длины для dU (не полная длина):
                    str_mag = el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString()[:2]  # два первых символа для коэф длины при расчете dU
                    group_c = el_circuit.LookupParameter('БУДОВА_Группа').AsString()
                    # имя уровня пaнели, к которой подключена цепь
                    level = doc.GetElement(el_circuit.BaseEquipment.Id).Host.Name[1:3]
                    if group_c + '.' + level not in mag_group_sum_circuit:
                        mag_group_sum_circuit[group_c + '.' + level] = [0]
                    mag_sum = mag_group_sum_circuit[group_c + '.' + level].pop() + ((float(str_mag[0] + '.' + str_mag[1]) / 1000) * leng_with_koef)
                    # Длина магистралей для dU (коэффициент запаса и коэффициент из празнака цепи):
                    mag_group_sum_circuit[group_c + '.' + level].append(mag_sum)  # float(str_mag[0] + '.' + str_mag[1]) - это коэф получающийся из строки признака цепи

                # Тип кабеля (str) (ВВГнг 3х2,5)
                    type_cbel = doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name
                # Сечение кабеля (str) Ищет 'х' на русском. Заменили запятую на точку. Перевели в число (пример: 2.5)
                    el = type_cbel.rfind('х') + 1
                    if el != -1:
                        if group_c + '.' + level not in mag_sechenie:
                            mag_sechenie[group_c + '.' + level] = []
                        mag_sechenie[group_c + '.' + level].append(float(type_cbel[el:].replace(',', '.')))
# OUT = mag_group_sum_circuit


moment_magistraley = {}
dU_magistraley = {}
for key in mag_group_sum_circuit.keys():
    if key in mag_light_sum_power:
        if key not in dU_magistraley:
            dU_magistraley[key] = []
        dU_magistraley[key].append((mag_light_sum_power[key][0] * mag_group_sum_circuit[key][0]) / 12 / mag_sechenie[key][0])
        if key not in moment_magistraley:
            moment_magistraley[key] = []
        moment_magistraley[key].append(mag_light_sum_power[key][0] * mag_group_sum_circuit[key][0])
# из списка магистралей/цепей

# OUT = dU_magistraley
# OUT = circuit_cl
# OUT = mag_sechenie
# OUT = mag_light_sum_power
# OUT = mag_group_sum_circuit

# Отобрали по глобальному имени группы dU магистралей (чтоб потом выбрать из них максимальную)
# получили список разных значений в одной группе
dU_magistraley_global = {}
for key, value in dU_magistraley.items():
    if (key[:key.rfind(".")]) not in dU_magistraley_global:
        dU_magistraley_global[key[:key.rfind(".")]] = []
    dU_magistraley_global[key[:key.rfind(".")]].append(value[0])

# OUT = dU_magistraley_global


# Отобрали по глобальному имени группы моменты магистралей (чтоб потом выбрать из них максимальный)
# получили список разных значений в одной группе

moment_magistraley_global = {}
for key, value in moment_magistraley.items():
    if (key[:key.rfind(".")]) not in moment_magistraley_global:
        moment_magistraley_global[key[:key.rfind(".")]] = []
    moment_magistraley_global[key[:key.rfind(".")]].append(value[0])

# OUT = moment_magistraley_global

# Отобрали максимальные значения dU магистралей (наибольшую dU из всех этажей)
dU_magistraley_global_max = {}
for key, value in dU_magistraley_global.items():
    dU_magistraley_global_max[key] = sorted(value)[-1:]

# OUT = dU_magistraley_global_max


# Отобрали максимальные значения моментов магистралей (наибольший момент из всех этажей)
moment_magistraley_global_max = {}
for key, value in moment_magistraley_global.items():
    moment_magistraley_global_max[key] = sorted(value)[-1:]

# OUT = moment_magistraley_global_max

OUT = dU_magistraley_global_max, moment_magistraley_global_max
