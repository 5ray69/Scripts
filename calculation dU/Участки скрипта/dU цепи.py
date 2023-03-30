# -*- coding: utf-8 -*
# dU цепи
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

# ПРОВЕРКА цепи в имени которых есть "гр", у которых классификация нагрузок не освещение
all_group_c = {}
circuit_cl = []
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
            # БУДОВА_Признак цепи (str)
                # circuit_cl.append(el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString())
            # Длина цепи (Double)
                parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]
                unit = parameter.GetUnitTypeId()
                leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали длину цепи во внешние единицы/как на экране пользователя
                koef = 1.05  # коэффициент запаса
                leng_koef = koef * leng

                # id_leng = [el_circuit.Id, leng]
                # circuit_cl.append(id_leng)
            # Тип кабеля (str) (ВВГнг 3х2,5)
                # type_cbel = doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name
                # circuit_cl.append(type_cbel)
            # Сечение кабеля (str) Ищет 'х' на русском. Перевели в число (2.5)
                # i = type_cbel.rfind('х') + 1
                # if i != -1:
                #     circuit_cl.append(float(type_cbel[i:].replace(',', '.')))
                # else:
                #     circuit_cl.append('не нашел х')
            # Отобрать все цепи одной группы
                group_c = el_circuit.LookupParameter('БУДОВА_Группа').AsString()
                if group_c not in all_group_c:
                    all_group_c[group_c] = []
                all_group_c[group_c].append(leng_koef)

# OUT = circuit_cl
OUT = all_group_c




# RBS_ELEC_CIRCUIT_LENGTH_PARAM => Длина

# # отобрали эл.цепи с классификацией нагрузок "Освещение",
# circuit = []
# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
# отделили от цепей, у которых не заполнен параметр освещение
#     if not el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1: 
#         if doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name == 'Освещение':
#             circuit.append(el_circuit)
# OUT = circuit


# # ПРОВЕРКА цепи в имени которых есть "гр", у которых не заполнен параметр классификация нагрузок
# circuit_name = []
# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     if el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
#         if 'гр' in el_circuit.Name:
#             circuit_name.append(el_circuit.Name)
# OUT = circuit_name
