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
from rename_circuit.user_warning_rename_circuit import ErrorCircuitNoConect, ErrorEnglishLetter
from rename_circuit.take_magistral import FromUserFormNameMagistral
from rename_circuit.length_circuit import LengthCircuit


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

with DB.Transaction(doc, 'RenameСircuit') as t:
    t.Start()
    # А Л Г О Р И Т М   М   создан для решения проблемы - какая квартира к какому
    # щиту подключена, так решается распределение квартир на этаже по щитам
    # Дело в том, что на разных этажах может быть разное подключение потому нужен был этот алгоритм 
    # А Л Г О Р И Т М   М   (суть)
    # 1 получаем ЩЭ
    # 2 из ЩЭ получаем отходящие цепи (здесь видим к какому щиту какая квартира подключена)
    # 3 из каждой отходящей цепи получаем ЩК
    # 4 из ЩК получаем отходящие цепи
    # 5 из каждой отходящей цепи получаем КК

    # коэффициент запаса на длину цепи
    koef_circuit = 1.05
    # для всех элементов категории Электрооборудование, которые не являются вложенным семейством
    for equip in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType():
        # у вложенных семейств нет значения параметра "Уровень спецификации" потому его извлечение дает -1 (InvalidElementId)
        # если семейство не вложенное
        if equip.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
            # Если параметр "Имя панели" заполнен
            if equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() is not None:
                # значение параметра Имя панели
                old_name = equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
                # значение параметра Уровень спецификации
                curent_level = doc.GetElement(equip.Parameter[
                    DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name

                # если есть английская M, К или А в имени
                if any(x in old_name for x in ('M','K','A')):
                    raise ErrorEnglishLetter(old_name, equip.Id)

                # А Л Г О Р И Т М   М
                # 1 ЩИТ ЭТАЖНЫЙ
                # семейство Щит на 7 офисов 5574954
                # семейство Щит на 8 офисов 5596311
                # семейство Щит этажный 5415276
                if equip.Symbol.Family.Id.IntegerValue in [5574954, 5596311, 5415276]:
                    # M_number получает из параметра Номер стояка и выбирает значение указанное пользователем в форме
                    # если в экземпляр класса подается два словаря dict_1, dict_2, то сделано для двух стояков в проекте
                    M_number = FromUserFormNameMagistral(doc, dict_1, dict_2, equip).get_magistral()

                    if curent_level[1:2] == '0':
                        equip.LookupParameter('БУДОВА_Обозначение').Set(
                        'ЩЭ' + str(equip.Symbol.LookupParameter(
                                    'БУДОВА_Количество счетчиков').AsInteger()) + '-' + curent_level[2:3])
                    else:
                        equip.LookupParameter('БУДОВА_Обозначение').Set(
                        'ЩЭ' + str(equip.Symbol.LookupParameter(
                                    'БУДОВА_Количество счетчиков').AsInteger()) + '-' + curent_level[1:3])

                    equip.LookupParameter('БУДОВА_Группа').Set('ЩЭ' + M_number[1:])
                    equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                    equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                    # имя панели
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(
                                                'ЩЭ' + M_number[1:] + '.' + curent_level[1:3])

                    # 2 ИЗ ЩЭ ПОЛУЧАЕМ ОТХОДЯЩИЕ ЦЕПИ (БЕЗ ЦЕПЕЙ ПИТАЮЩИХ ЩЭ)
                    for el_circuit in equip.MEPModel.GetAssignedElectricalSystems():
                        # к ЩЭ подключены другие щиты 5 цепями (в будущем можно подключать через наконечники)
                        # нагрузка цепи - Id типоразмера коробки ввода в квартиру 545719
                        if [faminstan for faminstan in el_circuit.Elements][0].GetTypeId().IntegerValue == 545719:
                            # длина цепи переведем в метры
                            # (int чтобы избавиться от формата double "1.0" - получить целое число )
                            leng = int(round(koef_circuit * Unit(doc, el_circuit.Parameter[
                                DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM].AsDouble(), False).display / 1000))
                            # если параметр 'Тип кабеля' не заполнен
                            if el_circuit.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                                # присваиваем тип кабеля в зависимости от длины
                                el_circuit.LookupParameter('Тип кабеля').Set(DB.ElementId(
                                    LengthCircuit(leng).integer_Id_cable_for_length()))

                            # 3 ИЗ КАЖДОЙ ОТХОДЯЩЕЙ ЦЕПИ ПОЛУЧАЕМ ЩК (нагрузка должна обрабатываться раньше цепи)
                            schk = [faminstan for faminstan in el_circuit.Elements][0]
                            # Уровень спецификации, так как квартиры могут быть на разных этажах
                            schk_level = doc.GetElement(schk.Parameter[
                                DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
                            # имя панели М3-03/7
                            old_name_schk = schk.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
                            schk.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(
                                M_number + '-' + curent_level[1:3] + old_name_schk[old_name_schk.rfind('/'):])
                            schk.LookupParameter('БУДОВА_Группа').Set(
                                M_number + '-' + curent_level[1:3] + old_name_schk[old_name_schk.rfind('/'):])
                            schk.LookupParameter('БУДОВА_Этаж').Set(schk_level)
                            schk.LookupParameter('БУДОВА_Уровень оборудования').Set(schk_level[1:3])
                            schk.LookupParameter('БУДОВА_Black').Set(LengthCircuit(leng).for_black_tag())
                            schk.LookupParameter('БУДОВА_Red').Set(LengthCircuit(leng).for_red_tag())
                            schk.LookupParameter('БУДОВА_Green').Set(LengthCircuit(leng).for_green_tag())
                            # присваивам значение 'БУДОВА_Тип кабеля' для марки в схему
                            schk.LookupParameter('БУДОВА_Тип кабеля').Set(
                                schk.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString() + ' - ' + 
                                doc.GetElement(el_circuit.LookupParameter('Тип кабеля').AsElementId()).Name + 
                                ' L = ' + str(leng) + 'м')

                            el_circuit.LookupParameter('БУДОВА_Группа').Set(
                                                [faminstan for faminstan in el_circuit.Elements][0].Name)
                            el_circuit.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                            # если параметр 'БУДОВА_Признак цепи' не заполнен
                            if el_circuit.LookupParameter('БУДОВА_Признак цепи').AsString() is None:
                                el_circuit.LookupParameter('БУДОВА_Признак цепи').Set('магистраль')
                            el_circuit.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                            # Параметры 'Номер цепи' и 'Панель' только для чтения и заполняются ревитом
                            # Имя нагрузки (М3-02/6)
                            el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(
                                    [faminstan for faminstan in el_circuit.Elements][0].Name)
                            # все что не стояк – группа, для различных коэффициентов длины на стояки и группы
                            el_circuit.LookupParameter('БУДОВА_Group').Set(1)

                            # 4 ИЗ ЩК ПОЛУЧАЕМ ОТХОДЯЩИЕ ЦЕПИ (БЕЗ ЦЕПИ ПИТАЮЩЕЙ ЩК)
                            for el_circui in schk.MEPModel.GetAssignedElectricalSystems():

                                # 5 ИЗ КАЖДОЙ ОТХОДЯЩЕЙ ЦЕПИ ПОЛУЧАЕМ КК (нагрузка должна обрабатываться раньше цепи)
                                kk = [faminsta for faminsta in el_circui.Elements][0]
                                # Уровень спецификации, так как квартиры могут быть двухуровневые
                                kk_level = doc.GetElement(schk.Parameter[
                                    DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
                                old_name_kk = schk.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].AsString()
                                kk.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(
                                    'КК' + old_name_schk[old_name_schk.rfind('/')+1:]+ '.' + kk_level[1:3])
                                kk.LookupParameter('БУДОВА_Группа').Set(
                                    'КК' + old_name_schk[old_name_schk.rfind('/')+1:])
                                kk.LookupParameter('БУДОВА_Этаж').Set(kk_level)
                                kk.LookupParameter('БУДОВА_Уровень оборудования').Set(kk_level[1:3])
                                # если значение параметра "Обозначение цепей" С перфиксами ElementId -7000010
                                # (По проекту ElementId -7000014),(Параметр не заполнен ElementId <null>)
                                if kk.Parameter[
                                    DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAMING].AsElementId().IntegerValue == -7000010:
                                    # параметр Префикс цепи создаем из нового этажа, после копирования
                                    # название эл.цепи меняется с изменением префикса
                                    kk.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_PREFIX].Set(
                                        'КК' + old_name_schk[old_name_schk.rfind('/')+1:]+ '.' + kk_level[1:3] + 'эт_цепь')

                                el_circui.LookupParameter('БУДОВА_Группа').Set(
                                            'КК' + old_name_schk[old_name_schk.rfind('/')+1:])
                                el_circui.LookupParameter('БУДОВА_Этаж').Set(schk_level)
                                # если параметр 'БУДОВА_Признак цепи' не заполнен
                                if el_circui.LookupParameter('БУДОВА_Признак цепи').AsString() is None:
                                    el_circui.LookupParameter('БУДОВА_Признак цепи').Set('магистраль')
                                el_circui.LookupParameter('БУДОВА_Уровень оборудования').Set(schk_level[1:3])
                                # Параметры 'Номер цепи' и 'Панель' только для чтения и заполняются ревитом
                                # Имя нагрузки (КК7.02)
                                el_circui.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(
                                        'КК' + old_name_schk[old_name_schk.rfind('/')+1:]+ '.' + schk_level[1:3])
                                # если параметр 'Тип кабеля' не заполнен
                                if el_circui.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                                    # присваиваем значение 'ПВ 1х4' ElementId 356542
                                    el_circui.LookupParameter('Тип кабеля').Set(DB.ElementId(356542))
                                # все что не стояк – группа, для различных коэффициентов длины на стояки и группы
                                el_circui.LookupParameter('БУДОВА_Group').Set(1)

                # О С Н О В Н О Й   А Л Г О Р И Т М
                if all(y not in old_name for y in ('ЩЭ','М','КК')):
                    # из имени панели ".этаж" отбросили и вместо них вписали точку + этаж из текущего уровня
                    new_name = old_name[:old_name.rfind('.')] + '.' + curent_level[1:3]
                    equip.Parameter[DB.BuiltInParameter.RBS_ELEC_PANEL_NAME].Set(new_name)
                    equip.LookupParameter('БУДОВА_Группа').Set(old_name[:old_name.rfind('.')])
                    equip.LookupParameter('БУДОВА_Этаж').Set(curent_level)
                    equip.LookupParameter('БУДОВА_Уровень оборудования').Set(curent_level[1:3])
                    # если значение параметра "Обозначение цепей" С перфиксами ElementId -7000010
                    # (По проекту ElementId -7000014),(Параметр не заполнен ElementId <null>)
                    if equip.Parameter[
                        DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAMING].AsElementId().IntegerValue == -7000010:
                        # параметр Префикс цепи создаем из нового этажа, после копирования
                        # название эл.цепи (параметр 'Номер цепи') меняется с изменением префикса
                        equip.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_PREFIX].Set(
                            old_name[:old_name.rfind('.')] + '.' + curent_level[1:3] + 'эт_цепь')

    circuit_no_conect = []
    # категория Электрические цепи
    for el_circu in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
        # если есть английская M, К или А в имени
        if any(x in el_circu.Name for x in ('M','K','A')):
            raise ErrorEnglishLetter(el_circu.Name, el_circu.Id)

        if all(z not in el_circu.Name for z in ('М','КК')):
            if hasattr(el_circu.BaseEquipment, 'Parameter'):
                # если значение параметра панели "Обозначение цепей" По проекту ElementId -7000014
                # (С перфиксами ElementId -7000010),(Параметр не заполнен ElementId <null>)
                if el_circu.BaseEquipment.Parameter[
                    DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAMING].AsElementId().IntegerValue == -7000014:
                    # получаем нагрузку цепи
                    for faminstan in el_circu.Elements:
                        # имя нагрузки записали в параметр цепи "Имя нагрузки"
                        el_circu.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(faminstan.Name)

                # этаж и увровень оборудования заполняем из панели цепи
                el_circu.LookupParameter('БУДОВА_Этаж').Set(el_circu.BaseEquipment.Host.Name)
                el_circu.LookupParameter('БУДОВА_Уровень оборудования').Set(el_circu.BaseEquipment.Host.Name[1:3])
                # если в имени цепи есть точка "." (для всего что не магистрали квартир)
                if '.' in el_circu.Name: 
                    number_circuit = el_circu.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
                    el_circu.LookupParameter('БУДОВА_Группа').Set(number_circuit[:number_circuit.rfind('.')])

                # если в имени цепи есть "гр"
                if 'гр' in el_circu.Name:
                    # получаем нагрузку цепи
                    for faminstan in el_circu.Elements:
                        # имя нагрузки записали в параметр цепи "Имя нагрузки"
                        el_circu.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NAME].Set(faminstan.Name)
                    # если параметр 'БУДОВА_Признак цепи' не заполнен
                    if el_circu.LookupParameter('БУДОВА_Признак цепи').AsString() is None:
                        el_circu.LookupParameter('БУДОВА_Признак цепи').Set('магистраль')
                    # если параметр 'БУДОВА_Классификация нагрузок' не заполнен
                    if el_circu.LookupParameter('БУДОВА_Классификация нагрузок').AsElementId().IntegerValue == -1:
                        # присваиваем ему значение 'Освещение' ElementId 155010
                        el_circu.LookupParameter('БУДОВА_Классификация нагрузок').Set(DB.ElementId(155010))
                    # если параметр 'Тип кабеля' не заполнен
                    if el_circu.LookupParameter('Тип кабеля').AsElementId().IntegerValue == -1:
                        # если в имени цепи есть 'A' русская
                        if 'A' in el_circu.Name:
                            # присваиваем значение 'FLAME 3х2,5' ElementId 356558
                            el_circu.LookupParameter('Тип кабеля').Set(DB.ElementId(356558))
                        else:
                            # присваиваем значение 'ВВГнг-LS 3х2,5' ElementId 356552
                            el_circu.LookupParameter('Тип кабеля').Set(DB.ElementId(356552))
                    # Все что не стояк – группа, для различных коэффициентов длины
                    el_circu.LookupParameter('БУДОВА_Group').Set(1)
                else:
                    # все что не содержит "гр." будет с другим коэф. длины
                    el_circu.LookupParameter('БУДОВА_Group').Set(0)
            else:
                circuit_no_conect.append([el_circu, 'цепь не подключена к панели'])

    # Светильники, выключатели, розетки, ЯТП
    categories = [
        DB.BuiltInCategory.OST_ElectricalFixtures,  # здесь вложенные семейства (другой подход) электрические проборы
        DB.BuiltInCategory.OST_LightingDevices,  # здесь БЕЗ вложенных семейств (один подход) выключатели
        DB.BuiltInCategory.OST_LightingFixtures,  # здесь БЕЗ вложенных семейств (один подход) осветительные приборы
    ]
    element_no_connect = []
    multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))
    for elem in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():
        # если есть значение параметра Уровень спецификации - так исключаем вложенные семейства
        if elem.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
            # значение параметра Уровень спецификации
            level_spec = doc.GetElement(elem.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
            elem.LookupParameter('БУДОВА_Этаж').Set(level_spec)
            elem.LookupParameter('БУДОВА_Уровень оборудования').Set(level_spec[1:3])
            # если значение параметра Номер цепи
            number_circuit = elem.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
            elem.LookupParameter('БУДОВА_Группа').Set(number_circuit[:number_circuit.rfind('.')])
            # если значение параметра Номер цепи пустая строка, то элемент не подключен
            if number_circuit == "":
                element_no_connect.append([elem, elem.Id, level_spec, 'не подключен'])

    # выводим список неподсоединенных устройств и цепей
    OUT = element_no_connect, circuit_no_conect

    t.Commit()

if circuit_no_conect:
    ErrorCircuitNoConect()

# черновой рассчет стояков в экселе, а затем уточненный расчет в экселе после получения длин из ревита
# переименовать трубы
