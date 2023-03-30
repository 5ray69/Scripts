# -*- coding: utf-8 -*
# module rename_circuit.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List
import json

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

from revitutils.unit import Unit
from rename_circuit.user_form_rename_circuit import UserInputForm
from rename_circuit.user_warning_rename_circuit import ErrorCircuitNoConect, ErrorEnglishLetter, ErrorNumberStoyak


# DESERIALIZATION
# FOR DYNAMO читаем файл из текущей дирректории
with open(IN[0].DirectoryName + r'\rename_circuit\drop_list.json', 'r') as file:
    Dict_from_json = json.load(file)

user_form = UserInputForm(Dict_from_json)
user_form.ShowDialog()
# di = user_form.dict_user_select
# словарь основного стояка
dict_1 = user_form.dict_user_select["1"]
# словарь второго стояка
dict_2 = user_form.dict_user_select["2"]




# SERIALIZATION ЗАПОМИНАЕМ ВЫБОР ПОЛЬЗОВАТЕЛЯ
# FOR DYNAMO создаем файл json в текущей дирректории, существующий с тем же именем перезапишется
with open(IN[0].DirectoryName + r'\rename_circuit\drop_list.json', 'w') as file:
    json.dump(user_form.dict_user_select, file, indent=4)

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo


class FromUserFormNameMagistral(object):
    '''Извлекает имя мгистрали указанное в форме пользователем'''
    def __init__(self, doc, dict_1, dict_2, equipment):
        self.doc = doc
        self.dict_1 = dict_1
        self.dict_2 = dict_2
        self.equipment = equipment
        # self.short_name = self.get_magistral

    def get_magistral(self):
        name_level_specifikacyi = doc.GetElement(equip.Parameter[
            DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
        if self.equipment.LookupParameter('Номер стояка').AsInteger() == 1:
            return self.dict_1[name_level_specifikacyi]
        elif self.equipment.LookupParameter('Номер стояка').AsInteger() == 2:
            return self.dict_2[name_level_specifikacyi]
        else:
            raise ErrorNumberStoyak(self.equipment, self.equipment.Id)



OUT = []

# категория Электрооборудование
# для всех элементов категории Электрооборудование, которые не являются вложенным семейством
for equip in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
    # у вложенных семейств нет значения параметра "Уровень спецификации" потому его извлечение дает -1 (InvalidElementId)
    # если семейство не вложенное
    if equip.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
        # значение параметра Уровень спецификации
        curent_level = doc.GetElement(equip.Parameter[
            DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
        # Если параметр "Имя панели" заполнен
        if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() is not None:
            # значение параметра Имя панели
            old_name = equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()

            # если есть английская M или А в имени
            if 'M' in old_name or 'A' in old_name:
                raise ErrorEnglishLetter(old_name, equip.Id)

            # # если в имени панели есть 'М' русская
            # if 'М' in old_name and 'Щ' not in old_name:

            # ЩИТ ЭТАЖНЫЙ
            # если в имени панели есть 'ЩЭ'
            if 'ЩЭ' in equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString():
                OUT.append(FromUserFormNameMagistral(doc, dict_1, dict_2, equip).get_magistral())
                # OUT.append(equip.LookupParameter('BDV_E000_номер_стояка').AsInteger())



# Сделай класс, принимающий два словаря и щит, а возвращающий значение по ключу, в соответствии с 
# значением параметра номер стояка из щита. Если значение параметра в щите больше 2, то исключение
# parameter = 3
# dict1 = '1'
# dict2 = '2'
# if parameter == 1:
#     var = dict1
# elif parameter == 2:
#     var = dict2
# else:
#     var = 'в параметре щита (указать щит и id)проставлен номер стояка больше двух'

# OUT = var




















# черновой рассчет стояков в экселе, а затем уточненный расчет в экселе после получения длин из ревита
# переименовать трубы

# АЛГОРИТМ С ВЫБОРОМ М1

# если параметр щита ни 1 ни 2, то ошибка
# если параметр 1, то дикт1, если параметр 2 то дикт 2 (переменная в зависимости от значения параметра)



# Получаем панель ЩЭ
# 1.прописываем все параметры панели (имя точка этаж)
#     получаем цепи нагрузок
#         для каждой цепи: (цепь от ЩЭ до ЩК)
#             М МЕНЯЕТСЯ ТОЛЬКО ДЛЯ КВАРТИР БОЛЬШЕ НИ ДЛЯ КОГО, ОТДЕЛЬНЫЙ АЛГОРИТМ
#             А.прописываеем все параметры цепи (имя с М)
#             длина цепи мз не тип кабеля выбираем

#             получаем нагрузку одной цепи (панель ЩК)
#                 2.прописываем все параметры панели (имя с М)
#                 тип кабеля для марки из длины цепи

#                         у панели ЩК 
#                         получаем получаем цепи нагрузок (цепь от ЩК до КК)
#                         Б.прописываем все параметры (имя точка этаж)
#                         назначаем тип кабеля цепи

# Все остальные цепи и панели это те, которые не содержат ЩЭ, М энд Щ и КК

# ОСНОВНОЙ АЛГОРИТМ

# 1. Для всех панелей и цепей, кроме М из имя панели название и этаж в цепь
# 2. Префикс цепи составь и перезапиши
