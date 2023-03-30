# -*- coding: utf-8 -*
# dU выводы
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

power_group = {}
cos_light = {}

for light in FEC(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType().ToElements():
    if light.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM):  # если рабочая плоскость не None (проверь строку)
        # мощность светильника
        parameter = doc.GetElement(light.GetTypeId()).LookupParameter('БУДОВА_Активная мощность')  # получили мощность светильника во внутренних единицах
        unit = parameter.GetUnitTypeId()
        power = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали мощность светильника во внешние единицы/как на экране пользователя
        # группа светильника
        group = light.LookupParameter('БУДОВА_Группа').AsString()  # получили имя группы
        # этаж светильника
        # level = light.LookupParameter('БУДОВА_Уровень оборудования').AsString()  # получили уровень оборудования
    # мощность светильников по "группа.этаж"
        if group not in power_group:
            power_group[group] = [0.0]
    # просуммировали мощность в каждой "группе.этаже" перевели в кВт
        mag_sum = power_group[group].pop() + power / 1000  # просуммировали мощность в каждой группе.этаже, перевели в кВт
        power_group[group].append(mag_sum)
        # коэффициент мощности светильника (cos f)
        cos = doc.GetElement(light.GetTypeId()).LookupParameter('БУДОВА_Коэффициент мощности').AsDouble()  # получили мощность светильника во внутренних единицах
        if group not in cos_light:
            cos_light[group] = []
        cos_light[group].append(cos)
# OUT = power_group
# OUT = cos_light

# Средневзвешенный косинус всей группы светильников
cos_light_center = {}
for key, value in cos_light.items():
    if key not in cos_light_center:
        cos_light_center[key] = round(sum(value) / len(value), 2)
# OUT = cos_light_center

# Ток всей группы светильников
tok_group = {}
for key, value in power_group.items():
    if key not in tok_group:
        # округление до ближайшего большего ( + 0.5) целого
        tok_group[key] = round(((value[0] / 0.22 / cos_light_center[key]) + 0.5), 0)
# OUT = tok_group


# ПРОВЕРКА цепи в имени которых есть "гр", у которых классификация нагрузок не освещение
koef_circuit = 1.05  # коэффициент запаса на длину цепи

sum_len_circuit = {}  # словарь сумм полных длин по группам
type_cabel = {}
for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
    if not el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
        if doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name == 'Освещение':
            if 'гр' in el_circuit.Name:
                        # circuit_cl.append(el_circuit.Name)
                        # Будова_Этаж (str)
                        # circuit_cl.append(el_circuit.LookupParameter('БУДОВА_Этаж').AsString())
                        # БУДОВА_Признак цепи (str) отделили коэффициенты стояков от магистралей
                gl_group_c = el_circuit.LookupParameter('БУДОВА_Группа').AsString()
                # gl_group_c = group_c[:group_c.rfind(".")]
                # if gl_group_c not in sum_len_circuit:
                #     sum_len_circuit[gl_group_c] = [0.0]
                if gl_group_c not in sum_len_circuit:
                    sum_len_circuit[gl_group_c] = [0.0]
                parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]  # Длина цепи полная
                unit = parameter.GetUnitTypeId()
                leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали длину цепи во внешние единицы/как на экране пользователя
                leng_with_koef = koef_circuit * leng  # длина цепи с коэффициентом запаса
                # Суммируем в словаре значения длин цепей  "+ 0.5" - округление до ближайшего большего целого (с Ревитом совпало полностью!!!):
                sum_circuit = sum_len_circuit[gl_group_c].pop() + round(((leng_with_koef / 1000) + 0.5), 0)
                sum_len_circuit[gl_group_c].append(sum_circuit)

                # Тип кабеля (str) (ВВГнг 3х2,5)
                type_cbel = doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name
                if gl_group_c not in type_cabel:
                    type_cabel[gl_group_c] = []
                # Добавляем только уникальные типы кабеля в список
                if type_cbel not in type_cabel[gl_group_c]:
                    type_cabel[gl_group_c].append(type_cbel)
# OUT = sum_len_circuit
# OUT = type_cabel

# Момент всей группы светильников
moment_group = {}
for key, value in power_group.items():
    if key not in moment_group:
        # округление до ближайшего большего ( + 0.5) целого
        moment_group[key] = round(((value[0] / 0.22 / cos_light_center[key]) + 0.5), 0)
# OUT = moment_group

OUT = power_group, cos_light_center, tok_group, sum_len_circuit, moment_group, type_cabel
