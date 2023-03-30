# -*- coding: utf-8 -*
# dU стояков
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

stoyak_light_sum_power = {}

for light in FEC(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType().ToElements():
    if light.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM):  # если рабочая плоскость не None (проверь строку)
        # мощность светильника
        parameter = doc.GetElement(light.GetTypeId()).LookupParameter('БУДОВА_Активная мощность')  # получили мощность светильника во внутренних единицах
        unit = parameter.GetUnitTypeId()
        power = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали мощность светильника во внешние единицы/как на экране пользователя
        # группа светильника
        # :key.rfind(".")
        group = light.LookupParameter('БУДОВА_Группа').AsString()  # получили имя группы
        # этаж светильника
        level = light.LookupParameter('БУДОВА_Уровень оборудования').AsString()  # получили уровень оборудования
    # мощность светильников по "группа.этаж"
        if group not in stoyak_light_sum_power:
            stoyak_light_sum_power[group] = [0.0]
    # просуммировали мощность в каждой "группе.этаже" перевели в кВт
        stoyak_sum = stoyak_light_sum_power[group].pop() + power / 1000  # просуммировали мощность в каждой группе.этаже, перевели в кВт
        stoyak_light_sum_power[group].append(stoyak_sum)
# OUT = stoyak_light_sum_power

# ПРОВЕРКА цепи в имени которых есть "гр", у которых классификация нагрузок не освещение
koef_circuit = 1.05  # коэффициент запаса на длину цепи

stoyak_group_sum_circuit = {}  # словарь сумм длин стояков по группам
stoyak_sechenie = {}
for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
    if not el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
        if doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name == 'Освещение':
            if 'гр' in el_circuit.Name:
                # circuit_cl.append(el_circuit.Name)
            # Будова_Этаж (str)
                # circuit_cl.append(el_circuit.LookupParameter('БУДОВА_Этаж').AsString())
            # БУДОВА_Признак цепи (str) отделили коэффициенты стояков от магистралей и линий 
                if 'стояк' in el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString():
                    parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]  # Длина цепи полная
                    unit = parameter.GetUnitTypeId()
                    leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали длину цепи во внешние единицы/как на экране пользователя
                    leng_with_koef = koef_circuit * leng  # длина цепи с коэффициентом запаса
                    # Коэффициент длины для dU (не полная длина):
                    str_stoyak = el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString()[:2]  # два первых символа для коэф длины при расчете dU
                    group_c = el_circuit.LookupParameter('БУДОВА_Группа').AsString()
                    # взяли глобальное имя группы (срезали все что после последней точки)
                    # group_c = group_c[:group_c.rfind(".")]
                    # :key.rfind(".")
                    if group_c not in stoyak_group_sum_circuit:
                        stoyak_group_sum_circuit[group_c] = [0]
                    stoyak_sum = stoyak_group_sum_circuit[group_c].pop() + ((float(str_stoyak[0] + '.' + str_stoyak[1]) / 1000) * leng_with_koef)
                    # Длина стояков для dU (коэффициент запаса и коэффициент из празнака цепи):
                    stoyak_group_sum_circuit[group_c].append(stoyak_sum)  # float(str_mag[0] + '.' + str_mag[1]) - это коэф получающийся из строки признака цепи
# OUT = stoyak_group_sum_circuit

                # Тип кабеля (str) (ВВГнг 3х2,5)
                    type_cbel = doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name
                # Сечение кабеля (str) Ищет 'х' на русском. Заменили запятую на точку. Перевели в число (пример: 2.5)
                    el = type_cbel.rfind('х') + 1
                    if el != -1:
                        if group_c not in stoyak_sechenie:
                            stoyak_sechenie[group_c] = []
                        stoyak_sechenie[group_c].append(float(type_cbel[el:].replace(',', '.')))
# OUT = stoyak_sechenie

moment_stoyakov = {}
dU_stoyakov = {}
for key in stoyak_group_sum_circuit.keys():
    if key in stoyak_light_sum_power:
        if key not in dU_stoyakov:
            dU_stoyakov[key] = []
        dU_stoyakov[key].append((stoyak_light_sum_power[key][0] * stoyak_group_sum_circuit[key][0]) / 12 / stoyak_sechenie[key][0])
        if key not in moment_stoyakov:
            moment_stoyakov[key] = []
        moment_stoyakov[key].append(stoyak_light_sum_power[key][0] * stoyak_group_sum_circuit[key][0])
# из списка стояков/цепей

# OUT = moment_stoyakov
# OUT = dU_stoyakov
# # # OUT = circuit_cl
# # # OUT = stoyak_light_sum_power
# # # OUT = stoyak_group_sum_circuit

OUT = dU_stoyakov, moment_stoyakov
