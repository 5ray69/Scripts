# -*- coding: utf-8 -*
# dU линий по этажам
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

line_light_sum_power = {}

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
        if group not in line_light_sum_power:
            line_light_sum_power[group] = [0.0]
    # просуммировали мощность в каждой "группе.этаже" перевели в кВт
        line_sum = line_light_sum_power[group].pop() + power / 1000  # просуммировали мощность в каждой группе.этаже, перевели в кВт
        line_light_sum_power[group].append(line_sum)
# OUT = line_light_sum_power

# ПРОВЕРКА цепи в имени которых есть "гр", у которых классификация нагрузок не освещение
koef_circuit = 1.05  # коэффициент запаса на длину цепи

dU_line_group_circuit = {}  # словарь сумм длин линий по группам
line_sechenie = {}
for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
    if not el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
        if doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name == 'Освещение':
            if 'гр' in el_circuit.Name:
                # circuit_cl.append(el_circuit.Name)
            # Будова_Этаж (str)
                # circuit_cl.append(el_circuit.LookupParameter('БУДОВА_Этаж').AsString())
            # БУДОВА_Признак цепи (str) отделили коэффициенты стояков от линий 
                if 'линия' in el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString():
                    parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]  # Длина цепи полная
                    unit = parameter.GetUnitTypeId()
                    leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали длину цепи во внешние единицы/как на экране пользователя
                    leng_with_koef = koef_circuit * leng  # длина цепи с коэффициентом запаса
                    # Коэффициент длины для dU (не полная длина):
                    str_mag = el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString()[:2]  # два первых символа для коэф длины при расчете dU
                    group_c = el_circuit.LookupParameter('БУДОВА_Группа').AsString()
                    # dU_lines_global[key[:key.rfind(".")]] = []
                    # group_c.rfind(".") - возвращает индекс последней точки в строке group_c
                    # if group_c[:group_c.rfind(".")] not in dU_line_group_circuit:
                    #     dU_line_group_circuit[group_c[:group_c.rfind(".")]] = [0]
                    # line_sum = dU_line_group_circuit[group_c[:group_c.rfind(".")]].pop() + ((float(str_mag[0] + '.' + str_mag[1]) / 1000) * leng_with_koef)
                    # # Длина линий для dU (коэффициент запаса и коэффициент из празнака цепи):
                    # dU_line_group_circuit[group_c[:group_c.rfind(".")]].append(line_sum)  # float(str_mag[0] + '.' + str_mag[1]) - это коэф получающийся из строки признака цепи
                # # Тип кабеля (str) (ВВГнг 3х2,5)
                #     type_cbel = doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name
                # # Сечение кабеля (str) Ищет 'х' на русском. Заменили запятую на точку. Перевели в число (пример: 2.5)
                #     el = type_cbel.rfind('х') + 1
                #     if el != -1:
                #         if group_c[:group_c.rfind(".")] not in line_sechenie:
                #             line_sechenie[group_c[:group_c.rfind(".")]] = []
                #         line_sechenie[group_c[:group_c.rfind(".")]].append(float(type_cbel[el:].replace(',', '.')))
                    if group_c not in dU_line_group_circuit:
                        dU_line_group_circuit[group_c] = [0]
                    line_sum = dU_line_group_circuit[group_c].pop() + ((float(str_mag[0] + '.' + str_mag[1]) / 1000) * leng_with_koef)
                    # Длина линий для dU (коэффициент запаса и коэффициент из празнака цепи):
                    dU_line_group_circuit[group_c].append(line_sum)  # float(str_mag[0] + '.' + str_mag[1]) - это коэф получающийся из строки признака цепи

                # Тип кабеля (str) (ВВГнг 3х2,5)
                    type_cbel = doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name
                # Сечение кабеля (str) Ищет 'х' на русском. Заменили запятую на точку. Перевели в число (пример: 2.5)
                    el = type_cbel.rfind('х') + 1
                    if el != -1:
                        if group_c not in line_sechenie:
                            line_sechenie[group_c] = []
                        line_sechenie[group_c].append(float(type_cbel[el:].replace(',', '.')))
# OUT = dU_line_group_circuit


moment_lines = {}
dU_lines = {}
for key in dU_line_group_circuit.keys():
    if key in line_light_sum_power:
        if key not in dU_lines:
            dU_lines[key] = []
        dU_lines[key].append(str(round((line_light_sum_power[key][0] * dU_line_group_circuit[key][0] / 12 / line_sechenie[key][0]) + 0.05, 1)))
        if key not in moment_lines:
            moment_lines[key] = []
        moment_lines[key].append(str(round((line_light_sum_power[key][0] * dU_line_group_circuit[key][0]) + 0.5, 0))[:-2])
# из списка линий/цепей

# OUT = dU_lines
# OUT = circuit_cl
# OUT = line_sechenie
# OUT = line_light_sum_power
# OUT = dU_line_group_circuit

OUT = dU_lines, moment_lines
