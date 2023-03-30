# module 078_09_select_active_view.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
# from Autodesk.Revit.DB import Architecture as AR
# from System.Collections.Generic import List
# from Autodesk.Revit.UI import Selection as SEL

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
]

doc = DM.Instance.CurrentDBDocument # Получение файла документа для Dynamo
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo

list_family_symbol = [family_symbol for family_symbol in FEC(doc).OfClass(DB.FamilySymbol) \
        if family_symbol.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == 'BDV_E000_Принципиальная схема освещения']


point_location = DB.XYZ(700, 5, 0)
# point_location = DB.XYZ(0, 0, 0)

list_view_drafting = [view_drafting for view_drafting in FEC(doc).OfClass(DB.ViewDrafting) \
        if view_drafting.Name == 'схема питающей сети']
with DB.Transaction(doc, 'create_family') as t:
    t.Start()
    family_ = doc.Create.NewFamilyInstance(
                                point_location,
                                list_family_symbol[0],
                                list_view_drafting[0]
    )
    family_.LookupParameter('BDV_E000_группа №').Set('77')
    family_.LookupParameter('BDV_E000_Мощность').Set(3.3)
    family_.LookupParameter('BDV_E000_Длина кабеля').Set(11)
    t.Commit()

OUT = family_.Id


# categories = [
#     DB.BuiltInCategory.OST_ElectricalFixtures,  # здесь вложенные семейства (другой подход)
#     DB.BuiltInCategory.OST_ElectricalEquipment,  # здесь вложенные семейства (другой подход)
#     DB.BuiltInCategory.OST_LightingDevices,  # здесь без вложенных семейств (один подход)
#     DB.BuiltInCategory.OST_LightingFixtures,  # здесь без вложенных семейств (один подход)
#     DB.BuiltInCategory.OST_Conduit,  # здесь без вложенных семейств (один подход)
#     DB.BuiltInCategory.OST_ElectricalCircuit,  # электрические цепи
#     DB.BuiltInCategory.OST_TextNotes,  # текстовые примечания
#     DB.BuiltInCategory.OST_Lines,  # линии детализации
#     DB.BuiltInCategory.OST_ElectricalEquipmentTags,  # марки электрооборудования
#     DB.BuiltInCategory.OST_LightingFixtureTags,  # марки осветительных приборов
#     DB.BuiltInCategory.OST_RoomTags,  # марки помещений
#     DB.BuiltInCategory.OST_GenericAnnotation  # типовые аннотации (стрелка выносок)
# ]

# multicategory_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](categories))

# element_ids = List[DB.ElementId]()
# for el in FEC(doc).WherePasses(multicategory_filter).WhereElementIsNotElementType():
#     if isinstance(el, DB.Electrical.ElectricalSystem):
#         # параметр Уровень спецификации коробки к которой подключена цепь
#         if doc.GetElement(doc.GetElement(el.BaseEquipment.Id).Parameter[
#                 DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name in level:
#             element_ids.Add(el.Id)

#     if isinstance(el, DB.FamilyInstance):
#         # у вложенных семейств нет значения параметра Уровень спецификации потому его извлечение дает -1 (InvalidElementId)
#         # если есть значение параметра Уровень спецификации
#         if el.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId().IntegerValue != -1:
#             # параметр Уровень спецификации
#             if doc.GetElement(el.Parameter[DB.BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM].AsElementId()).Name in level:
#                 element_ids.Add(el.Id)
#     elif isinstance(el, DB.Electrical.Conduit):
#         # параметр Базовый уровень
#         if doc.GetElement(el.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()).Name in level:
#             element_ids.Add(el.Id)

#     # если выполняется любое из условий (аналогично функция all - выполняются все условия)
#     if any([
#         isinstance(el, DB.CurveElement),
#         isinstance(el, DB.TextNote),
#         isinstance(el, DB.IndependentTag),
#         isinstance(el, DB.AnnotationSymbol),
#         isinstance(el, AR.RoomTag)
#     ]):
#         # если Id вида, которому принадлежит элемент, = Id активного вида
#         if el.OwnerViewId == doc.ActiveView.Id:
#             element_ids.Add(el.Id)

# # выделили в Ревите отобранные элементы
# uidoc.Selection.SetElementIds(element_ids)

# # # Элементы принадлежащие виду/зависимые от вида этим методом выделяются категории Траектория солнца и другие, мешающие копированию, не пользуйся им:
# # # выделили элементы принадлежащие виду/зависимые от вида (текстовые примечания, линии детализации, марки электрооборудования,
# # # марки осветительных приборов, марки помещений, типовые аннотации (стрелка выносок)
# # for el in FEC(doc).OwnedByView(doc.ActiveView.Id):
# #     element_ids.Add(el.Id)
