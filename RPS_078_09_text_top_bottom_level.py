# -*- coding: utf-8 -*
# module 078_09_text_top_bottom_ level.py
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
]

from pack_functions.selections import get_element_by_name, BoundingBoxXyzContains
from pack_functions.texts import raplace_letter, my_sort
from revitutils.unit import Unit

uiapp = __revit__                          # noqa
app = __revit__.Application                # noqa
uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa

# def raplace_letter(strin):
#     return strin.replace('ЩЭ', 'М').replace('Л', 'М').replace('ВП', 'М').replace('ВВ', 'М').replace('ВН', 'М').replace('ВЗ', 'М').replace('НХ', 'М').replace('НП', 'М').replace('НТ', 'М').replace('ГК', 'М')


# группы лестничных клеток для исключения из списков стояков
list_stair = [
    'гр.1А',  # освещение лестничных переходов
    'гр.7А',  # освещение подъема на 1 этаж с подвала, СУВ
    'гр.9',  # освещение входа с улицы в подвал, выключатель при входе
    'гр.9А',  # освещение освновной лестничной клетки
    'гр.11А',  # освещение освновной лестничной клетки
    'гр.15А',  # освещение дополнительной лестничной клетки
    'гр.16А'  # освещение дополнительной лестничной клетки
]

# # не меняй порядок импортов (причина - модуль импортируется только один раз)
# # в create_list_lines тоже импортируется Unit
# from pack_functions.selections import get_element_by_name, BoundingBoxXyzContains
# from pack_functions.texts import raplace_letter, my_sort
# from pack_functions.creates import create_list_lines

# ТОЧКИ БАУНДИНГБОКСА
point_xyz = []
# отбираем семейства категории Датчики
for faminst in FEC(doc).OfCategory(DB.BuiltInCategory.OST_DataDevices).WhereElementIsNotElementType():
    point_xyz.append(faminst.Location.Point)
# отсортировали элементы списка по координате Z в порядке возрастания
point_xyz.sort(key=lambda x: x.Z)
# ТОЧКИ МИНИМУМА И МАКСИМУМА БАУНДИНГБОКСА
# если список не пуст, то берем точки баундингбокса (есть два основных стояка в здании)
if point_xyz:
    point_min = point_xyz[0]
    point_max = point_xyz[1]
# если список пуст, то точки баундингбокса не размещали (в здании один основной стояк)
else:
    point_min = DB.XYZ(1, 1, 1)
    point_max = DB.XYZ(2, 2, 2)

# СОЗДАЕМ СЛОВАРИ ЛЕВОГО И ПРАВОГО СТОЯКОВ
# ключ=уровень, а значение=имена ВСЕХ панелей и ВСЕХ нагрузок находящихся на этом уровне
level_name_left_stoyak = {}
level_name_right_stoyak = {}
for level in FEC(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType():
    if level.Name not in level_name_left_stoyak:
        # в множестве повторяющихся элементов нет
        level_name_left_stoyak[level.Name] = set()
    if level.Name not in level_name_right_stoyak:
        # в множестве повторяющихся элементов нет
        level_name_right_stoyak[level.Name] = set()

# НАПОЛНЯЕМ СЛОВАРЬ ЗНАЧЕНИЯМИ
for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
    # ПАНЕЛИ ЦЕПЕЙ
    # М русская и английская, КК русскими и английскими, очка == точка подключений
    if all(x not in (el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()) for x in ('очка','КК','KK','М','M','Я')):
        # если этой группы нет в лестничных клетках
        if el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString() not in list_stair:
            # если точка размещения панели попадает в баундингбокс
            if BoundingBoxXyzContains(point_min, point_max, el_circuit.BaseEquipment.Location.Point):
                # добавляем группу панели в словарь и заменяем буквы на М
                level_name_right_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()))
            else:
                # добавляем группу панели в словарь и заменяем буквы на М
                level_name_left_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()))
    # ЕСЛИ ПАНЕЛЬ ЭТО ТОЧКА ПОДКЛЮЧЕНИЙ, то получаем нагрузки цепей добавляем их в этаж "точки подключений" ВРУ
    if 'очка' in (el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()):
        # получаем нагрузки цепи
        for faminstan in el_circuit.Elements:
            # если этой группы нет в лестничных клетках
            if faminstan.LookupParameter('БУДОВА_Группа').AsString() not in list_stair:
                # если точка размещения нагрузки попадает в баундингбокс
                if BoundingBoxXyzContains(point_min, point_max, faminstan.Location.Point):
                    # добавляем группу нагрузки в словарь по ключу уровня точки подключений и заменяем буквы на М
                    level_name_right_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))
                else:
                    # добавляем группу нагрузки в словарь по ключу уровня точки подключений и заменяем буквы на М
                    level_name_left_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))
    # НАГРУЗКИ ЦЕПЕЙ
    # получаем нагрузки цепи
    for faminstan in el_circuit.Elements:
        # если этой группы нет в лестничных клетках
        if faminstan.LookupParameter('БУДОВА_Группа').AsString() not in list_stair:
            # М русская и английская, КК русскими и английскими, очка == точка подключений
            if all(x not in (faminstan.LookupParameter('БУДОВА_Группа').AsString()) for x in ('очка','КК','KK','М','M','Я')):
                # если точка размещения нагрузки попадает в баундингбокс
                if BoundingBoxXyzContains(point_min, point_max, faminstan.Location.Point):
                    # добавляем группу нагрузки в словарь и заменяем буквы на М
                    level_name_right_stoyak[faminstan.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))
                else:
                    # добавляем группу нагрузки в словарь и заменяем буквы на М
                    level_name_left_stoyak[faminstan.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))

# УДАЛЯЕМ В СЛОВАРЯХ ИЗ УРОВНЯ ПОДВАЛА ВСЕ ЗНАЧЕНИЯ, КОТОРЫХ НЕТ НА ВЕРХНИХ УРОВНЯХ
# метод pop из словаря удалил ключ с значениями и вернул значения удаленного ключа в виде кортежа
new_s = set(level_name_left_stoyak.pop('LU100'))
# создали множество всех уникальных значений словаря без значений ключа LU100
s_t = set()
for el_s in dict.values(level_name_left_stoyak):
    s_t.update(el_s)
# вычли те группы, которых нет в верхних этажах с уровня подвала и добавили ключ:значения в словарь
level_name_left_stoyak['LU100'] = new_s - (new_s - s_t)

# метод pop из словаря удалил ключ с значениями и вернул значения удаленного ключа в виде кортежа
new_s = set(level_name_right_stoyak.pop('LU100'))
# создали множество всех уникальных значений словаря без значений ключа LU100
s_t = set()
for el_s in dict.values(level_name_right_stoyak):
    s_t.update(el_s)
# вычли те группы, которых нет в верхних этажах с уровня подвала и добавили ключ:значения в словарь
level_name_right_stoyak['LU100'] = new_s - (new_s - s_t)

# ПОЛУЧАЕМ ПОЗИЦИИ ДЛЯ РАЗМЕЩЕНИЯ ТЕКСТА И ЛИНИЙ ИЗ РАЗМЕЩЕННЫХ СЕМЕЙСТВ ТИПОВЫХ АННОТАЦИЙ
верх_лево_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'верх_лево_магистралей' in type_annot.Name]
верх_лево_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'верх_лево_аварийного_освещения' in type_annot.Name]
верх_право_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'верх_право_магистралей' in type_annot.Name]
верх_право_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'верх_право_аварийного_освещения' in type_annot.Name]
низ_лево_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'низ_лево_магистралей' in type_annot.Name]
низ_лево_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'низ_лево_аварийного_освещения' in type_annot.Name]
низ_право_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'низ_право_магистралей' in type_annot.Name]
низ_право_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
                                OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
                                if 'низ_право_аварийного_освещения' in type_annot.Name]


# ПОЛУЧАЕМ ПЛАНЫ ОСВЕЩЕНИЯ
# НИЗ ПОДВАЛА - ТО ЧТО НАХОИДИТСЯ В САМОМ ПОДВАЛЕ, ПРОСТО УДАЛИ НА ПЛАНЕ
# НЕ ПЕРЕДЕЛЫВАЙ, МОЖЕТ ПОНАДОБИТЬСЯ, ЕСЛИ ПОДВАЛ ИЗ НЕСКОЛЬКИХ УРОВНЕЙ
for view_plan in FEC(doc).OfClass(DB.ViewPlan):
    # отбираем только планы, у которых шаблон BDV_E000_Освещение
    if view_plan.ViewTemplateId.IntegerValue != -1 and 'Освещение' in doc.GetElement(view_plan.ViewTemplateId).Name:

        верх_лево_магистралей = []
        низ_лево_магистралей = []

        верх_право_магистралей = []
        низ_право_магистралей = []

        верх_лево_аварийного_освещения = []
        низ_лево_аварийного_освещения = []

        верх_право_аварийного_освещения = []
        низ_право_аварийного_освещения = []

        # Перебираем все уровни проекта
        for lev in FEC(doc).OfClass(DB.Level):
            # ФИЛЬТРАЦИЯ УРОВНЕЙ ОТНОСИТЕЛЬНО ТЕКУЩЕГО уровеня, с которым связан план
            # если план освещения меньше перебираемого уровня
            if view_plan.GenLevel.Elevation < lev.Elevation:
                # то это верхние тексты
                # ВЕРХ_ЛЕВО списки групп идущих на ВЕРХНИЕ уровни
                # из словаря левого стояка
                for elem in level_name_left_stoyak[lev.Name]:
                    if 'А' in elem:
                        if elem not in верх_лево_аварийного_освещения:
                            верх_лево_аварийного_освещения.append(elem)
                    else:
                        if elem not in верх_лево_магистралей:
                            верх_лево_магистралей.append(elem)
                # ВЕРХ_ПРАВО списки групп идущих на ВЕРХНИЕ уровни
                # из словаря правого стояка
                for elem in level_name_right_stoyak[lev.Name]:
                    if 'А' in elem:
                        if elem not in верх_право_аварийного_освещения:
                            верх_право_аварийного_освещения.append(elem)
                    else:
                        if elem not in верх_право_магистралей:
                            верх_право_магистралей.append(elem)
            else:
                # иначе это нижние тексты
                # НИЗ_ЛЕВО списки групп идущих с НИЖНИХ уровней
                # здесь оказывается и текущий уровень
                # из словаря левого стояка
                for elem in level_name_left_stoyak[lev.Name]:
                    if 'А' in elem:
                        if elem not in низ_лево_аварийного_освещения:
                            низ_лево_аварийного_освещения.append(elem)
                    else:
                        if elem not in низ_лево_магистралей:
                            низ_лево_магистралей.append(elem)
                # НИЗ_ПРАВО списки групп идущих с НИЖНИХ уровней
                # здесь оказывается и текущий уровень
                # из словаря правого стояка
                for elem in level_name_right_stoyak[lev.Name]:
                    if 'А' in elem:
                        if elem not in низ_право_аварийного_освещения:
                            низ_право_аварийного_освещения.append(elem)
                    else:
                        if elem not in низ_право_магистралей:
                            низ_право_магистралей.append(elem)

        # СОРТИРОВКА СПИСКОВ
        new_верх_лево_магистралей = my_sort(верх_лево_магистралей)
        new_верх_лево_магистралей.append('\nна верхний этаж')
        new_низ_лево_магистралей = my_sort(низ_лево_магистралей)
        new_низ_лево_магистралей.append('\nс нижнего этажа')

        new_верх_право_магистралей = my_sort(верх_право_магистралей)
        new_верх_право_магистралей.append('\nна верхний этаж')
        new_низ_право_магистралей = my_sort(низ_право_магистралей)
        new_низ_право_магистралей.append('\nс нижнего этажа')

        new_верх_лево_аварийного_освещения = my_sort(верх_лево_аварийного_освещения)
        new_верх_лево_аварийного_освещения.append('\nна верхний этаж')
        new_низ_лево_аварийного_освещения = my_sort(низ_лево_аварийного_освещения)
        new_низ_лево_аварийного_освещения.append('\nс нижнего этажа')

        new_верх_право_аварийного_освещения = my_sort(верх_право_аварийного_освещения)
        new_верх_право_аварийного_освещения.append('\nна верхний этаж')
        new_низ_право_аварийного_освещения = my_sort(низ_право_аварийного_освещения)
        new_низ_право_аварийного_освещения.append('\nс нижнего этажа')



        print('текущий уровень:  ' + view_plan.GenLevel.Name)
        print('верх_лево_магистралей:  ')
        bprint(sorted(верх_лево_магистралей))
        print('верх_лево_аварийного_освещения:  ')
        bprint(sorted(верх_лево_аварийного_освещения))
        print('верх_право_магистралей:  ')
        bprint(sorted(верх_право_магистралей))
        print('верх_право_аварийного_освещения:  ')
        bprint(sorted(верх_право_аварийного_освещения))
        print('низ_лево_магистралей:  ')
        bprint(sorted(низ_лево_магистралей))
        print('низ_лево_аварийного_освещения:  ')
        bprint(sorted(низ_лево_аварийного_освещения))
        print('низ_право_магистралей:  ')
        bprint(sorted(низ_право_магистралей))
        print('низ_право_аварийного_освещения:  ')
        bprint(sorted(низ_право_аварийного_освещения))
        print('______________________________________________________________')

# # УДАЛЯЕМ В СЛОВАРЕ ИЗ УРОВНЯ ПОДВАЛА ВСЕ ЗНАЧЕНИЯ, КОТОРЫХ НЕТ НА ВЕРХНИХ УРОВНЯХ
# d = {'LU100': ('гр.14', 'гр.15', 'гр.16', 'гр.17', 'гр.20', 'гр.21'),
# 'L0100': ('гр.99', 'гр.15', 'гр.16', 'гр.17'),
# 'L0200': ('гр.13', 'гр.15', 'гр.16', 'гр.77'),
# 'L0300': ('гр.12', 'гр.15', 'гр.16', 'гр.17'),
# 'L0400': ('гр.11', 'гр.55', 'гр.16', 'гр.17')}
# # метод pop из словаря удалил ключ с значениями и вернул значения удаленного ключа в виде кортежа
# new_s = set(d.pop('LU100'))
# # получили множество всех уникальных значений словаря без значений ключа LU100
# s_t = set()
# for el_s in dict.values(d):
#     s_t.update(el_s)
# # вычли те группы, которых нет в верхних этажах с уровня подвала и добавили ключ:значения в словарь
# d['LU100'] = new_s - (new_s - s_t)
# bprint(d)

# УДАЛЯЕМ В СЛОВАРЕ ИЗ УРОВНЯ ПОДВАЛА ВСЕ ЗНАЧЕНИЯ, КОТОРЫХ НЕТ НА ВЕРХНИХ УРОВНЯХ
d_left = {'LU100': ('гр.14', 'гр.15', 'гр.16', 'гр.17', 'гр.18'),
'L0100': ('гр.14', 'гр.15', 'гр.16', 'гр.17', 'гр.18'),
'L0200': ('гр.14', 'гр.15', 'гр.16', 'гр.77', 'гр.18'),
'L0300': ('гр.14', 'гр.15', 'гр.16', 'гр.17', 'гр.18')}

d_righ = {'LU100': ('гр.15', 'гр.16', 'гр.17', 'М1'),
'L0100': ('гр.15' 'гр.16', 'гр.17', 'М1'),
'L0200': ('гр.15', 'гр.16', 'гр.17', 'М1')}


# УДАЛЯЕМ В СЛОВАРЕ ИЗ УРОВНЯ ПОДВАЛА ВСЕ ЗНАЧЕНИЯ, КОТОРЫХ НЕТ НА ВЕРХНИХ УРОВНЯХ
d_left = {'LU100': ('гр.14', 'гр.15', 'гр.16', 'гр.17', 'гр.18'),
'L0100': ('гр.14', 'гр.15', 'гр.16', 'гр.17', 'гр.18'),
'L0200': ('гр.14', 'гр.15', 'гр.16', 'гр.77', 'гр.18'),
'L0300': ('гр.14', 'гр.15', 'гр.16', 'гр.17', 'гр.88')}

d_righ = {'LU100': ('гр.15', 'гр.16', 'гр.17', 'М1'),
'L0100': ('гр.15', 'гр.16', 'гр.17', 'М1'),
'L0200': ('гр.15', 'гр.16', 'гр.17', 'М1')}

# вычли те группы, что есть в словаре правого стояка из словаря левого стояка
for key_righ in d_righ.keys():
    d_left[key_righ] = set(d_left[key_righ]) - set(d_righ[key_righ])
bprint(d_righ)