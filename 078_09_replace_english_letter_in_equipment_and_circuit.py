# -*- coding: utf-8 -*
# module rename_circuit.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo

with DB.Transaction(doc, 'correctErrorsCircuitsAndEquipments') as t:
    t.Start()
    # категория Электрооборудование
    # для всех элементов категории Электрооборудование, которые не являются вложенным семейством
    for equip in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
        # у вложенных семейств нет значения параметра "Уровень спецификации" потому его извлечение дает -1 (InvalidElementId)
        # если семейство не вложенное
        if equip.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
            # Если параметр "Имя панели" заполнен
            if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() is not None:
                # значение параметра Имя панели
                old_name = equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
                # если есть английская M в имени
                if 'M' in old_name:
                    # заменяем английскую М на русскую М
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(old_name.replace('M', 'М'))
                if 'A' in old_name:
                    # заменяем английскую М на русскую М .replace('old', 'new', количество замен цифрой)
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(old_name.replace('A', 'А'))
                if 'K' in old_name:
                    # заменяем английскую М на русскую М .replace('old', 'new', количество замен цифрой)
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(old_name.replace('K', 'К'))

    # категория Электрические цепи
    for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
        if 'M' in el_circuit.Name:
            # Имя нагрузки
            old_name_load = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].AsString()
            el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(old_name_load.replace('M', 'М'))
            # Номер цепи
            old_name_number = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
            el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(old_name_number.replace('M', 'М'))
        if 'A' in el_circuit.Name:
            # Имя нагрузки
            old_name_load = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].AsString()
            el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(old_name_load.replace('A', 'А'))
            # Номер цепи
            old_name_number = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
            el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(old_name_number.replace('A', 'А'))
        if 'K' in el_circuit.Name:
            # Имя нагрузки
            old_name_load = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].AsString()
            el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(old_name_load.replace('K', 'К'))
            # Номер цепи
            old_name_number = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
            el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(old_name_number.replace('K', 'К'))

    t.Commit()
