# -*- coding: utf-8 -*-
# module fill_in_the _zahv look.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import Architecture as AR
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List
# from Autodesk.Revit.UI import Selection as SEL

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
]

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo

categories = [
    DB.BuiltInCategory.OST_ElectricalFixtures,  # здесь вложенные семейства (другой подход) электрические приборы
    DB.BuiltInCategory.OST_ElectricalEquipment,  # здесь вложенные семейства (другой подход) электрооборудование
    DB.BuiltInCategory.OST_LightingDevices,  # здесь без вложенных семейств (один подход) выключатели
    DB.BuiltInCategory.OST_LightingFixtures,  # здесь без вложенных семейств (один подход) осветительные приборы
    DB.BuiltInCategory.OST_Conduit,  # здесь без вложенных семейств (один подход) короба
    DB.BuiltInCategory.OST_ConduitFitting,  # без вложенных семейств (один подход) соденительные детали коробов
    DB.BuiltInCategory.OST_CableTray,  # без вложенных семейств (один подход) кабельные лотки
    DB.BuiltInCategory.OST_CableTrayFitting,  # здесь вложенные семейства  (другой подход)соденительные детали кабельных лотков
    DB.BuiltInCategory.OST_ElectricalCircuit,  # электрические цепи
    DB.BuiltInCategory.OST_FireAlarmDevices  # без вложенных семейств (один подход) пожарная сигнализация
]

multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))

val_zahv = []

# электрические цепи
for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():
    if isinstance(el, DB.Electrical.ElectricalSystem):
        # если параметр 'БУДОВА_Захватка' не заполнен
        if el.LookupParameter('БУДОВА_Захватка').AsString() is None:
            # имя уровня из параметра 'Уровень спецификации' панели к которой подключена цепь
            val_zahv.append(el)
            val_zahv.append(el.LookupParameter('БУДОВА_Захватка').AsString())
            val_zahv.append(el.LookupParameter('БУДОВА_Этаж').AsString())
            val_zahv.append('*******')

    if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Захватка') is None:
        # соединительные детали кабельных лотков и соединительные детали коробов
        # это класс FamilyInstance и у них параметр Уровень, а не Базовый уровень или Уровень спецификации
        if any([
            el.Category.Id.IntegerValue == -2008128,  # соединительные детали коробов
            el.Category.Id.IntegerValue == -2008126,  # соединительные детали кабельных лотков
            el.Category.Id.IntegerValue == -2008085  # заземление, категория пожарная сигнализация
        ]):
            # если семейство не вложенное
            if el.SuperComponent is None:
                # имя уровня из параметра Уровень
                val_zahv.append(el)
                val_zahv.append(el.LookupParameter('БУДОВА_Захватка').AsString())
                val_zahv.append(el.LookupParameter('БУДОВА_Этаж').AsString())
                val_zahv.append('*******')

        # у вложенных семейств нет значения параметра Уровень спецификации потому его извлечение дает -1 (InvalidElementId)
        # если есть значение параметра Уровень спецификации
        if el.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
            if el.LookupParameter('БУДОВА_Захватка').AsString() is None:
                val_zahv.append(el)
                val_zahv.append(el.LookupParameter('БУДОВА_Захватка').AsString())
                val_zahv.append(el.LookupParameter('БУДОВА_Этаж').AsString())
                val_zahv.append('*******')

    # у коробов кабельных лотков нет параметра Уровень спецификации, а есть параметр Базовый уровень
    # потому нужна отдельная обработка
    # если выполняется любое из условий (аналогично функция all - выполняются все условия)
    if any([
        isinstance(el, DB.Electrical.Conduit),
        isinstance(el, DB.Electrical.CableTray)
    ]):
        if el.LookupParameter('БУДОВА_Захватка').AsString() is None:
            val_zahv.append(el)
            val_zahv.append(el.LookupParameter('БУДОВА_Захватка').AsString())
            val_zahv.append(el.LookupParameter('БУДОВА_Этаж').AsString())
            val_zahv.append('*******')
# объект с незаполненным параметром появится на выходе
OUT = val_zahv
