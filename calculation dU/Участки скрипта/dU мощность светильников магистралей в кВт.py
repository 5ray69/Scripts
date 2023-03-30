# -*- coding: utf-8 -*
# dU мощность светильников магистралей в кВт
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа

doc = DM.Instance.CurrentDBDocument  # Получение файла документа

# получили светильники, у которых есть уровень - рабочая плоскость (у вложенных семейств нет уровней - лампа, стойка светильника светоогр....)
# получили Активную мощность каждого светильника, переведя из внутренних единиц во внешние
throughout_building = {}
list_level = {}
mag_light_sum_power = {}

for light in FEC(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType().ToElements():
    if light.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM):  # если рабочая плоскость не None (проверь строку)
        # light.append(el) # отобрали светильники
        parameter = doc.GetElement(light.GetTypeId()).LookupParameter('БУДОВА_Активная мощность')  # получили мощность светильника во внутренних единицах
        unit = parameter.GetUnitTypeId()
        power = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)  # конвертировали мощность светильника во внешние единицы/как на экране пользователя
        # группа
        group = light.LookupParameter('БУДОВА_Группа').AsString()  # получили имя группы
        if group not in throughout_building:
            throughout_building[group] = []
            throughout_building[group].append(power)
        # этаж
        level = light.LookupParameter('БУДОВА_Уровень оборудования').AsString()  # получили имя группы
        if level not in list_level:
            list_level[level] = []
            list_level[level].append(group)

        if group + '.' + level not in mag_light_sum_power:
            mag_light_sum_power[group + '.' + level] = [0]
        mag_sum = [mag_light_sum_power[group + '.' + level].pop() + power][0]
        mag_light_sum_power[group + '.' + level].append(round((float(mag_sum) / 1000), 3))
        # mag_light[group + '.' + level].append(power)

OUT = mag_light_sum_power

# # проссумировали значения списков в словаре для каждого ключа
# # мощность каждой группы по всему зданию
# throughout_building_sum = {}
# for key, value in throughout_building.items():
#     throughout_building_sum[key] = sum(value) / 1000

# # OUT = throughout_building_sum
