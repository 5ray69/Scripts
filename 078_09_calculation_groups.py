# module 078_09_calculation_groups.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

from calculation_groups.circuit_servis_calculation_groups import CircuitСontain
from calculation_groups.calculationGroups import CalculationGroups
from calculation_groups.my_sort import my_sort_group

doc = DM.Instance.CurrentDBDocument # Получение файла документа
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo


list_family_symbol = [family_symbol for family_symbol in FEC(doc).OfClass(DB.FamilySymbol) \
        if family_symbol.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == 'BDV_E000_Принципиальная схема освещения']

list_view_drafting = [view_drafting for view_drafting in FEC(doc).OfClass(DB.ViewDrafting) \
        if view_drafting.Name == 'схема питающей сети']

family_id = []
with DB.Transaction(doc, 'create_family') as t:
    t.Start()
    display_units = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()  # получили объект ForgeTypeId
    # 700 - начало отсчета по Х
    # задаем в мм, удобно для человека, а код переводит во внутренние единицы
    valueX = DB.UnitUtils.ConvertToInternalUnits(82000, display_units)

    calculationGroups = CalculationGroups(doc, uidoc)
    dict_group_str_max_dU = calculationGroups.get_value_max_dU_from_path_with_max_dU()

    for group_str in my_sort_group(dict_group_str_max_dU.keys()):
        # 1900 - смещение по Х
        valueX += DB.UnitUtils.ConvertToInternalUnits(1900, display_units)
        family_ = doc.Create.NewFamilyInstance(
                                    DB.XYZ(valueX, 50, 0),
                                    list_family_symbol[0],
                                    list_view_drafting[0]
        )
        family_.LookupParameter('BDV_E000_группа №').Set(group_str)

        # цепей может быть подключено к головной панели несколько, потому суммируем их мощность
        # отходящая цепь теущей группы от головной панели
        list_circuits_loads = calculationGroups.get_circuit_loads_from_panel_for_group()[group_str][0]
        act_power = sum([CircuitСontain(cir).get_active_power() for cir in list_circuits_loads])
        family_.LookupParameter('BDV_E000_Мощность').Set(round(act_power, 2))

        # КОСИНУС
        full_power = sum([CircuitСontain(circ).get_full_power() for circ in list_circuits_loads])
        if full_power == 0:
            # если косинус сделать = 0, то ток в семействе будет деление на ноль, поэтому = 1
            family_.LookupParameter('BDV_E000_cos φ').Set(1)
        else:
            family_.LookupParameter('BDV_E000_cos φ').Set(round(act_power / full_power, 2))

        # ДЛИНА всех проводов какие только есть в группе
        family_.LookupParameter('BDV_E000_Длина кабеля').Set(
            calculationGroups.get_length_by_groups_all_circuits()[group_str][0])

        family_.LookupParameter('BDV_E000_Момент мощности').Set(calculationGroups.get_maxM_path_with_maxdU()[group_str])

        family_.LookupParameter('BDV_E000_dU').Set(round(dict_group_str_max_dU[group_str], 2))

        family_id.append(family_.Id)
    t.Commit()

OUT = family_id
