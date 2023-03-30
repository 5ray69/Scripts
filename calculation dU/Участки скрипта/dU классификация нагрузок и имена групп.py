# -*- coding: utf-8 -*
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

# ПРОВЕРКА цепи в имени которых есть "гр", у которых классификация нагрузок не освещение
circuit_cl = []
for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
    if not el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
        if not doc.GetElement(el_circuit.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId()).Name == 'Освещение':
            if 'гр' in el_circuit.Name:
                circuit_cl.append(el_circuit.Name)
                
OUT = circuit_cl

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
