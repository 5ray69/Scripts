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

dict_1 = {
    'LU100': 'дом часть 1',
    'L0100': 'дом часть 1',
    'L0200': 'дом часть 2',
    'L0300': 'дом часть 2',
    'L0400': 'дом часть 2',
    'L0500': 'дом часть 2',
    'L0600': 'дом часть 2',
    'L0700': 'дом часть 2',
    'L0800': 'дом часть 2',
    'L0900': 'дом часть 2',
    'L1000': 'дом часть 2',
    'L1100': 'дом часть 2',
    'L1200': 'дом часть 2',
    'L1300': 'дом часть 2',
    'L1400': 'дом часть 2',
    'L1500': 'дом часть 2',
    'L1600': 'дом часть 2',
    'L1700': 'дом часть 2',
    'L1800': 'дом часть 2',
    'L1900': 'дом часть 2',
    'L2000': 'дом часть 2',
    'L2100': 'дом часть 2',
    'L2200': 'дом часть 2',
    'L2300': 'дом часть 2',
    'L2400': 'дом часть 2',
    'L2500': 'дом часть 2',
    'L2600': 'дом часть 2',
    'LT100': 'дом часть 3',
    'LR100': 'дом часть 3',
    'LR200': 'дом часть 3'
}

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

with DB.Transaction(doc, 'fill_in_zahv') as t:
    t.Start()
    for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():
        # полоса заземления, категория пожарная сигнализация
        if el.Category.Id.IntegerValue == -2008085:
            # если 'БУДОВА_Захватка' не заполнен
            if el.LookupParameter('БУДОВА_Захватка').AsString() is None:
                # минимльное значение Z края элемента (прямой)
                z_element = round(min(el.Location.Curve.GetEndPoint(0).Z, el.Location.Curve.GetEndPoint(1).Z), 3)
                # отметка самого нижнего уровня
                lev_elev_min = sorted([lev.Elevation for lev in FEC(doc).OfClass(DB.Level)])[0]
                # если край элемента ниже самого нижнего уровня
                if z_element < lev_elev_min:
                    lev_elev_min_name = [lev.Name for lev in FEC(doc).OfClass(DB.Level) \
                                        if round(lev.Elevation, 3) == round(lev_elev_min, 3)][0]
                    el.LookupParameter('БУДОВА_Захватка').Set(dict_1[lev_elev_min_name])
                    el.LookupParameter('БУДОВА_Этаж').Set(lev_elev_min_name)
                else:
                    # уровни, которые ниже отметки элемента
                    levs_elev_below = [lev for lev in FEC(doc).OfClass(DB.Level) if lev.Elevation <= z_element]
                    # минимальная разница между Z уровня и Z элемента
                    min_difference = sorted([z_element - lev.Elevation for lev in levs_elev_below])[0]
                    # имя уровня с короторым разница минимальная, над которым элемент
                    lev_name = [lev.Name for lev in FEC(doc).OfClass(DB.Level) \
                                if round(z_element - lev.Elevation, 3) == round(min_difference, 3)][0]
                    el.LookupParameter('БУДОВА_Захватка').Set(dict_1[lev_name])
                    el.LookupParameter('БУДОВА_Этаж').Set(lev_name)

        # электрические цепи
        if isinstance(el, DB.Electrical.ElectricalSystem):
            # если 'БУДОВА_Захватка' не заполнен
            if el.LookupParameter('БУДОВА_Захватка').AsString() is None:
                # имя уровня из параметра 'Уровень спецификации' панели к которой подключена цепь
                level_name = doc.GetElement(doc.GetElement(el.BaseEquipment.Id).Parameter[
                    DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
                el.LookupParameter('БУДОВА_Захватка').Set(dict_1[level_name])

        if isinstance(el, DB.FamilyInstance) and el.LookupParameter('БУДОВА_Захватка'):
            # соединительные детали кабельных лотков и соединительные детали коробов
            # это класс FamilyInstance и у них параметр Уровень, а не Базовый уровень или Уровень спецификации
            if any([
                el.Category.Id.IntegerValue == -2008128,  # соединительные детали коробов
                el.Category.Id.IntegerValue == -2008126  # соединительные детали кабельных лотков
            ]):
                # если семейство не вложенное
                if el.SuperComponent is None:
                    # имя уровня из параметра Уровень
                    level_name = doc.GetElement(el.Parameter[DB.BuiltInParameter.FAMILY_LEVEL_PARAM].AsElementId()).Name
                    el.LookupParameter('БУДОВА_Захватка').Set(dict_1[level_name])
                    el.LookupParameter('БУДОВА_Этаж').Set(level_name)

            # у вложенных семейств нет значения параметра Уровень спецификации потому его извлечение дает -1 (InvalidElementId)
            # если есть значение параметра Уровень спецификации
            if el.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
            # имя уровня из параметра Уровень спецификации
                level_name = doc.GetElement(el.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name
                el.LookupParameter('БУДОВА_Захватка').Set(dict_1[level_name])

        # у коробов кабельных лотков нет параметра Уровень спецификации, а есть параметр Базовый уровень
        # потому нужна отдельная обработка
        # если выполняется любое из условий (аналогично функция all - выполняются все условия)
        if any([
            isinstance(el, DB.Electrical.Conduit),
            isinstance(el, DB.Electrical.CableTray)
        ]):
            # имя уровня из параметра
            level_name = doc.GetElement(el.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name
            el.LookupParameter('БУДОВА_Захватка').Set(dict_1[level_name])
            el.LookupParameter('БУДОВА_Этаж').Set(level_name)
    t.Commit()
