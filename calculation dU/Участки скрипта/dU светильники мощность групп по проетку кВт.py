# -*- coding: utf-8 -*
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices') # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM # Менеджер документа

doc = DM.Instance.CurrentDBDocument # Получение файла документа

# получили светильники, у которых есть уровень - рабочая плоскость (у вложенных семейств нет уровней - лампа, стойка светильника светоогр....)
# получили Активную мощность каждого светильника, переведя из внутренних единиц во внешние
throughout_building = {}
list_level = {}

for light in FEC(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType().ToElements():
    if not light.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM) == None:
        # light.append(el) # отобрали светильники
        parameter = doc.GetElement(light.GetTypeId()).LookupParameter('БУДОВА_Активная мощность') # получили мощность светильника во внутренних единицах
        unit = parameter.GetUnitTypeId()
        power = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали мощность светильника во внешние единицы/как на экране пользователя
# группа
        group = light.LookupParameter('БУДОВА_Группа').AsString() # получили имя группы
        if group not in throughout_building:
                throughout_building[group] = []
        throughout_building[group].append(power)

# проссумировали значения списков в словаре для каждого ключа
throughout_building_sum = {}
for key, value in throughout_building.items():
        throughout_building_sum[key] = sum(value)/1000

OUT = throughout_building_sum




# OUT = light_pover

        # name_group.append(light.LookupParameter('БУДОВА_Группа').AsString()) # получили имя группы

# def group_by_key(elements, key_type='Type'):
#     elements = flatten(elements)
#     element_groups = {}
#     for element in elements:
#         if key_type == 'Type':
#             key = type(element)
#         elif key_type == 'Category':
#             for key in DB.BuiltInCategory.GetValues(DB.BuiltInCategory):
#                 if int(key) == element.Category.Id.IntegerValue:
#                     break
#         else:
#             key = 'Unknown Key'
#         if key not in element_groups:
#             element_groups[key] = []
#         element_groups[key].append(element)
#     return element_groups





        # получили названия уровней/рабочих плоскостей в виде строки
        # light.append(el.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM).AsString())  # SKETCH_PLANE_PARAM => Рабочая плоскость




# Группируем колонны по помещениям через функцию group_columns_by_room_id. В качестве результата получаем словарь,
#  ключами которого являются Id помещений, а значениями - колонны, которые к ним относятся.
# sortgroup.py
# def group_columns_by_room_id(doc, columns, phase):
#     room_ids = {} #  это словарь
#     with DB.Transaction(doc, 'Temporary Transaction') as t:
#         t.Start()
#         for column in columns:
#             column.Parameter[
#                 DB.BuiltInParameter.WALL_ATTR_ROOM_BOUNDING].Set(False) # параметр колонны типа да/нет "Граница помещения"
#             doc.Regenerate() # регенерация всей модели, чтоб обновления вступили в силу - чтоб перестроились помещения
#             if column.Room[phase] is None:
#                 room_id = DB.ElementId.InvalidElementId
#             else:
#                 room_id = column.Room[phase].Id
#             if room_id not in room_ids:
#                 room_ids[room_id] = []
#             room_ids[room_id].append(column) # в словарь добавили ключ - id помещения
#         t.RollBack() #  откатили назад все изменения произведенные в транзакции
#     return room_ids