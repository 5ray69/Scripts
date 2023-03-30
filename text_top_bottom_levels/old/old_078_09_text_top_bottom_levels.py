# -*- coding: utf-8 -*
# module 078_09_text_top_bottom_ level.py
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

# не меняй порядок импортов (причина - модуль импортируется только один раз)
# в create_list_lines тоже импортируется Unit
from pack_functions.selections import get_element_by_name, BoundingBoxXyzContains
from pack_functions.texts import raplace_letter, my_sort
from pack_functions.creates import create_list_lines
from revitutils.unit import Unit
from text_top_bottom_level.user_form_top_bottom_levels import UserFormTopBottomLevels


f = UserFormTopBottomLevels()
f.ShowDialog()
list_stair = f.dict_user_select["list_stair"]
delete_from_right_stoyak = f.dict_user_select["delete_from_right_stoyak"]
OUT = list_stair, delete_from_right_stoyak


# # группы лестничных клеток для исключения из списков стояков
# list_stair = [
#     'гр.1А',  # освещение лестничных переходов
#     'гр.7А',  # освещение подъема на 1 этаж с подвала, СУВ
#     'гр.9',  # освещение входа с улицы в подвал, выключатель при входе
#     'гр.9А',  # освещение освновной лестничной клетки
#     'гр.11А',  # освещение освновной лестничной клетки
#     'гр.15А',  # освещение дополнительной лестничной клетки
#     'гр.16А'  # освещение дополнительной лестничной клетки
# ]

# # ИСКЛЮЧИТЬ ГРУППЫ ИЗ ПРАВОГО СТОЯКА
# # (группы заходящие в пределы баундингбокса, которые не должны быть в его пределах)
# delete_from_right_stoyak = [
#     'гр.16'  # на первом этаже из-за сложного ветвления попала в баундингбокс
# ]

# # ТОЧКИ БАУНДИНГБОКСА
# point_xyz = []
# # отбираем семейства категории Датчики
# for faminst in FEC(doc).OfCategory(DB.BuiltInCategory.OST_DataDevices).WhereElementIsNotElementType():
#     point_xyz.append(faminst.Location.Point)
# # отсортировали элементы списка по координате Z в порядке возрастания
# point_xyz.sort(key=lambda x: x.Z)
# # ТОЧКИ МИНИМУМА И МАКСИМУМА БАУНДИНГБОКСА
# # если список не пуст, то берем точки баундингбокса (есть два основных стояка в здании)
# if point_xyz:
#     point_min = point_xyz[0]
#     point_max = point_xyz[1]
# # если список пуст, то точки баундингбокса не размещали (в здании один основной стояк)
# else:
#     point_min = DB.XYZ(1, 1, 1)
#     point_max = DB.XYZ(2, 2, 2)

# # СОЗДАЕМ СЛОВАРИ ЛЕВОГО И ПРАВОГО СТОЯКОВ
# # ключ=уровень, а значение=имена ВСЕХ панелей и ВСЕХ нагрузок находящихся на этом уровне
# level_group_left_stoyak = {}
# level_group_right_stoyak = {}
# for level in FEC(doc).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType():
#     if level.Name not in level_group_left_stoyak:
#         # в множестве повторяющихся элементов нет
#         level_group_left_stoyak[level.Name] = set()
#     if level.Name not in level_group_right_stoyak:
#         # в множестве повторяющихся элементов нет
#         level_group_right_stoyak[level.Name] = set()

# # НАПОЛНЯЕМ СЛОВАРЬ ЗНАЧЕНИЯМИ
# for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
#     # ПАНЕЛИ ЦЕПЕЙ
#     # М русская и английская, КК русскими и английскими, очка == точка подключений
#     if all(x not in (el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()) for x in ('очка','КК','KK','М','M','Я')):
#         # если этой группы нет в лестничных клетках
#         if el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString() not in list_stair:
#             # если точка размещения панели попадает в баундингбокс
#             if BoundingBoxXyzContains(point_min, point_max, el_circuit.BaseEquipment.Location.Point):
#                 # если этой группы нет в списке для исключения из правого стояка
#                 if el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString() not in delete_from_right_stoyak:
#                     level_group_right_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()))
#             else:
#                 # добавляем группу панели в словарь и заменяем буквы на М
#                 level_group_left_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()))
#     # ЕСЛИ ПАНЕЛЬ ЭТО ТОЧКА ПОДКЛЮЧЕНИЙ, то получаем нагрузки цепей добавляем их в этаж "точки подключений" ВРУ
#     if 'очка' in (el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString()):
#         # получаем нагрузки цепи
#         for faminstan in el_circuit.Elements:
#             # если этой группы нет в лестничных клетках
#             if faminstan.LookupParameter('БУДОВА_Группа').AsString() not in list_stair:
#                 # если точка размещения нагрузки попадает в баундингбокс
#                 if BoundingBoxXyzContains(point_min, point_max, faminstan.Location.Point):
#                     # если этой группы нет в списке для исключения из правого стояка
#                     if el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString() not in delete_from_right_stoyak:
#                         # добавляем группу нагрузки в словарь по ключу уровня точки подключений и заменяем буквы на М
#                         level_group_right_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))
#                 else:
#                     # добавляем группу нагрузки в словарь по ключу уровня точки подключений и заменяем буквы на М
#                     level_group_left_stoyak[el_circuit.BaseEquipment.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))
#     # НАГРУЗКИ ЦЕПЕЙ
#     # получаем нагрузки цепи
#     for faminstan in el_circuit.Elements:
#         # если этой группы нет в лестничных клетках
#         if faminstan.LookupParameter('БУДОВА_Группа').AsString() not in list_stair:
#             # М русская и английская, КК русскими и английскими, очка == точка подключений
#             if all(x not in (faminstan.LookupParameter('БУДОВА_Группа').AsString()) for x in ('очка','КК','KK','М','M','Я')):
#                 # если точка размещения нагрузки попадает в баундингбокс
#                 if BoundingBoxXyzContains(point_min, point_max, faminstan.Location.Point):
#                     # если этой группы нет в списке для исключения из правого стояка
#                     if el_circuit.BaseEquipment.LookupParameter('БУДОВА_Группа').AsString() not in delete_from_right_stoyak:
#                         # добавляем группу нагрузки в словарь и заменяем буквы на М
#                         level_group_right_stoyak[faminstan.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))
#                 else:
#                     # добавляем группу нагрузки в словарь и заменяем буквы на М
#                     level_group_left_stoyak[faminstan.Host.Name].add(raplace_letter(faminstan.LookupParameter('БУДОВА_Группа').AsString()))

# # ВЫЧЛИ В СЛОВАРЯХ ИЗ УРОВНЯ ПОДВАЛА ВСЕ ЗНАЧЕНИЯ, КОТОРЫХ НЕТ НА ВЕРХНИХ УРОВНЯХ
# # метод pop из словаря удалил ключ с значениями и вернул значения удаленного ключа в виде кортежа
# new_s = set(level_group_left_stoyak.pop('LU100'))
# # создали множество всех уникальных значений словаря без значений ключа LU100
# s_t = set()
# for el_s in dict.values(level_group_left_stoyak):
#     s_t.update(el_s)
# # вычли те группы, которых нет в верхних этажах с уровня подвала и заменили ключ:значения в словаре
# level_group_left_stoyak['LU100'] = new_s - (new_s - s_t)
# # метод pop из словаря удалил ключ с значениями и вернул значения удаленного ключа в виде кортежа
# new_s = set(level_group_right_stoyak.pop('LU100'))
# # создали множество всех уникальных значений словаря без значений ключа LU100
# s_t = set()
# for el_s in dict.values(level_group_right_stoyak):
#     s_t.update(el_s)
# # вычли те группы, которых нет в верхних этажах с уровня подвала и заменили ключ:значения в словарь
# level_group_right_stoyak['LU100'] = new_s - (new_s - s_t)
# # ВЫЧЛИ ТЕ ГРУППЫ, ЧТО ЕСТЬ В СЛОВАРЕ ПРАВОГО СТОЯКА ИЗ СЛОВАРЯ ЛЕВОГО СТОЯКА
# # те мелочи что выходят за пределы баундингбокса не будет учитываться в правом стояке
# for key_righ in level_group_right_stoyak.keys():
#     level_group_left_stoyak[key_righ] = set(level_group_left_stoyak[key_righ]) - set(level_group_right_stoyak[key_righ])

# # OUT = level_group_right_stoyak['L0100'], level_group_left_stoyak['L0100']
# # OUT = level_group_right_stoyak['LU100'], level_group_left_stoyak['LU100']








# # ПОЛУЧАЕМ ПОЗИЦИИ ДЛЯ РАЗМЕЩЕНИЯ ТЕКСТА И ЛИНИЙ ИЗ РАЗМЕЩЕННЫХ СЕМЕЙСТВ ТИПОВЫХ АННОТАЦИЙ
# верх_лево_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'верх_лево_магистралей' in type_annot.Name]
# верх_лево_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'верх_лево_аварийного_освещения' in type_annot.Name]
# верх_право_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'верх_право_магистралей' in type_annot.Name]
# верх_право_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'верх_право_аварийного_освещения' in type_annot.Name]
# низ_лево_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'низ_лево_магистралей' in type_annot.Name]
# низ_лево_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'низ_лево_аварийного_освещения' in type_annot.Name]
# низ_право_магистралей_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'низ_право_магистралей' in type_annot.Name]
# низ_право_аварийного_освещения_позиция = [type_annot.Location.Point for type_annot in FEC(doc).
#                                 OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType()
#                                 if 'низ_право_аварийного_освещения' in type_annot.Name]

# with DB.Transaction(doc, 'Create_text_top_bottom_level') as t:
#     t.Start()
#     # выбираем типоразмер текста, имеющийся в проекте
#     text_note_type = get_element_by_name(doc, 'BDV_Текст_черный_2.211_мм_top_bottom_level', DB.TextNoteType)
#     # Задаем опции создания текста
#     text_note_options = DB.TextNoteOptions(text_note_type.Id)

#     # ПОЛУЧАЕМ ПЛАНЫ ОСВЕЩЕНИЯ
#     # НИЗ ПОДВАЛА - ТО ЧТО НАХОИДИТСЯ В САМОМ ПОДВАЛЕ, ПРОСТО УДАЛИ НА ПЛАНЕ
#     # НЕ ПЕРЕДЕЛЫВАЙ, МОЖЕТ ПОНАДОБИТЬСЯ, ЕСЛИ ПОДВАЛ ИЗ НЕСКОЛЬКИХ УРОВНЕЙ
#     for view_plan in FEC(doc).OfClass(DB.ViewPlan):
#         # отбираем только планы, у которых шаблон BDV_E000_Освещение
#         if view_plan.ViewTemplateId.IntegerValue != -1 and 'Освещение' in doc.GetElement(view_plan.ViewTemplateId).Name:

#             верх_лево_магистралей = []
#             низ_лево_магистралей = []

#             верх_право_магистралей = []
#             низ_право_магистралей = []

#             верх_лево_аварийного_освещения = []
#             низ_лево_аварийного_освещения = []

#             верх_право_аварийного_освещения = []
#             низ_право_аварийного_освещения = []

#             # Перебираем все уровни проекта
#             for lev in FEC(doc).OfClass(DB.Level):
#                 # ФИЛЬТРАЦИЯ УРОВНЕЙ ОТНОСИТЕЛЬНО ТЕКУЩЕГО уровеня, с которым связан план
#                 # если план освещения меньше перебираемого уровня
#                 if view_plan.GenLevel.Elevation < lev.Elevation:
#                     # то это верхние тексты
#                     # ВЕРХ_ЛЕВО списки групп идущих на ВЕРХНИЕ уровни
#                     # из словаря левого стояка
#                     for elem in level_group_left_stoyak[lev.Name]:
#                         if 'А' in elem:
#                             if elem not in верх_лево_аварийного_освещения:
#                                 верх_лево_аварийного_освещения.append(elem)
#                         else:
#                             if elem not in верх_лево_магистралей:
#                                 верх_лево_магистралей.append(elem)
#                     # ВЕРХ_ПРАВО списки групп идущих на ВЕРХНИЕ уровни
#                     # из словаря правого стояка
#                     for elem in level_group_right_stoyak[lev.Name]:
#                         if 'А' in elem:
#                             if elem not in верх_право_аварийного_освещения:
#                                 верх_право_аварийного_освещения.append(elem)
#                         else:
#                             if elem not in верх_право_магистралей:
#                                 верх_право_магистралей.append(elem)
#                 else:
#                     # иначе это нижние тексты
#                     # НИЗ_ЛЕВО списки групп идущих с НИЖНИХ уровней
#                     # здесь оказывается и текущий уровень
#                     # из словаря левого стояка
#                     for elem in level_group_left_stoyak[lev.Name]:
#                         if 'А' in elem:
#                             if elem not in низ_лево_аварийного_освещения:
#                                 низ_лево_аварийного_освещения.append(elem)
#                         else:
#                             if elem not in низ_лево_магистралей:
#                                 низ_лево_магистралей.append(elem)
#                     # НИЗ_ПРАВО списки групп идущих с НИЖНИХ уровней
#                     # здесь оказывается и текущий уровень
#                     # из словаря правого стояка
#                     for elem in level_group_right_stoyak[lev.Name]:
#                         if 'А' in elem:
#                             if elem not in низ_право_аварийного_освещения:
#                                 низ_право_аварийного_освещения.append(elem)
#                         else:
#                             if elem not in низ_право_магистралей:
#                                 низ_право_магистралей.append(elem)

#             # СОРТИРОВКА СПИСКОВ
#             new_верх_лево_магистралей = my_sort(верх_лево_магистралей)
#             new_верх_лево_магистралей.append('\nна верхний этаж')
#             new_низ_лево_магистралей = my_sort(низ_лево_магистралей)
#             new_низ_лево_магистралей.append('\nс нижнего этажа')

#             new_верх_право_магистралей = my_sort(верх_право_магистралей)
#             new_верх_право_магистралей.append('\nна верхний этаж')
#             new_низ_право_магистралей = my_sort(низ_право_магистралей)
#             new_низ_право_магистралей.append('\nс нижнего этажа')

#             new_верх_лево_аварийного_освещения = my_sort(верх_лево_аварийного_освещения)
#             new_верх_лево_аварийного_освещения.append('\nна верхний этаж')
#             new_низ_лево_аварийного_освещения = my_sort(низ_лево_аварийного_освещения)
#             new_низ_лево_аварийного_освещения.append('\nс нижнего этажа')

#             new_верх_право_аварийного_освещения = my_sort(верх_право_аварийного_освещения)
#             new_верх_право_аварийного_освещения.append('\nна верхний этаж')
#             new_низ_право_аварийного_освещения = my_sort(низ_право_аварийного_освещения)
#             new_низ_право_аварийного_освещения.append('\nс нижнего этажа')

#             # ЛЕВО  HorizontalTextAlignment - Left Right Center
#             # VerticalTextAlignment - Top Bottom Middle
#             # Изменили свойство горизонтального выравнивания текста
#             text_note_options.HorizontalAlignment = DB.HorizontalTextAlignment.Right
#             # Изменили свойство вертикального выравнивания текста

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Bottom
#             # Создаем объект текста верх_лево_аварийного_освещения
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[верх_лево_аварийного_освещения_позиция[0].X + Unit(doc, -200).internal,
#                         верх_лево_аварийного_освещения_позиция[0].Y,
#                         верх_лево_аварийного_освещения_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_верх_лево_аварийного_освещения),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Top
#             # Создаем объект текста верх_лево_магистралей
#             # Создаем объект текста низ_лево_аварийного_освещения
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[низ_лево_аварийного_освещения_позиция[0].X + Unit(doc, -300).internal,
#                         низ_лево_аварийного_освещения_позиция[0].Y + Unit(doc, 385).internal,
#                         низ_лево_аварийного_освещения_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_низ_лево_аварийного_освещения),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Bottom
#             # Создаем объект текста верх_право_аварийного_освещения
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[верх_право_аварийного_освещения_позиция[0].X + Unit(doc, -200).internal,
#                         верх_право_аварийного_освещения_позиция[0].Y,
#                         верх_право_аварийного_освещения_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_верх_право_аварийного_освещения),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Top
#             # Создаем объект текста низ_право_аварийного_освещения
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[низ_право_аварийного_освещения_позиция[0].X + Unit(doc, -300).internal,
#                         низ_право_аварийного_освещения_позиция[0].Y + Unit(doc, 385).internal,
#                         низ_право_аварийного_освещения_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_низ_право_аварийного_освещения),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # ПРАВО  HorizontalTextAlignment - Left Right Center
#             # VerticalTextAlignment - Top Bottom Middle
#             # Изменили свойство горизонтального выравнивания текста
#             text_note_options.HorizontalAlignment = DB.HorizontalTextAlignment.Left

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Bottom
#             # Создаем объект текста верх_право_магистралей
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[верх_право_магистралей_позиция[0].X + Unit(doc, 200).internal,
#                         верх_право_магистралей_позиция[0].Y,
#                         верх_право_магистралей_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_верх_право_магистралей),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Top
#             # Создаем объект текста низ_право_магистралей
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[низ_право_магистралей_позиция[0].X + Unit(doc, 350).internal,
#                         низ_право_магистралей_позиция[0].Y + Unit(doc, 385).internal,
#                         низ_право_магистралей_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_низ_право_магистралей),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Bottom
#             # Создаем объект текста верх_лево_магистралей
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[верх_лево_магистралей_позиция[0].X + Unit(doc, 200).internal,
#                         верх_лево_магистралей_позиция[0].Y,
#                         верх_лево_магистралей_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_верх_лево_магистралей),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # Изменили свойство вертикального выравнивания текста
#             text_note_options.VerticalAlignment = DB.VerticalTextAlignment.Top
#             # Создаем объект текста низ_лево_магистралей
#             text_note = DB.TextNote.Create(
#                 doc,
#                 view_plan.Id,  # Id вида
#                 # точка размещения текста со смещением
#                 DB.XYZ(*[низ_лево_магистралей_позиция[0].X + Unit(doc, 350).internal,
#                         низ_лево_магистралей_позиция[0].Y + Unit(doc, 385).internal,
#                         низ_лево_магистралей_позиция[0].Z]
#                         ),
#                 Unit(doc, 3000/100).internal,  # ширина текста из мм во внутренние единицы указав 30мм в итоге на плане получим 3000мм (масшатаб 100)
#                 ', '.join(new_низ_лево_магистралей),  # вставляемый текст (преобразовали список в строку)
#                 text_note_options  # свойства выравнивания текста
#             )

#             # создаем списки кривых/линий
#             list_l = create_list_lines(верх_лево_магистралей_позиция, 5, 1, 1)
#             list_2 = create_list_lines(низ_лево_магистралей_позиция, 5, 1, -1)

#             list_3 = create_list_lines(верх_право_магистралей_позиция, 2, 1, 1)
#             list_4 = create_list_lines(низ_право_магистралей_позиция, 2, 1, -1)

#             list_5 = create_list_lines(верх_лево_аварийного_освещения_позиция, 2, -1, 1)
#             list_6 = create_list_lines(низ_лево_аварийного_освещения_позиция, 2, -1, -1)

#             list_7 = create_list_lines(верх_право_аварийного_освещения_позиция, 2, -1, 1)
#             list_8 = create_list_lines(низ_право_аварийного_освещения_позиция, 2, -1, -1)

#             curve_array = DB.CurveArray()
#             # объединили все 8 списков в один сложением
#             for curve in list_l + list_2 + list_3 + list_4 + list_5 + list_6 + list_7 + list_8:
#                 curve_array.Append(curve)

#             # создаем линии детализации на основе созданных кривых/линий
#             detail_Lines = doc.Create.NewDetailCurveArray(
#                 view_plan,  # текущий вид,
#                 curve_array
#             )
#             # катеогория линии
#             LinesCat = doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_Lines)
#             # подкатегория BDV_E000_С_top_bottom_level (выбрали существующий в проекте стиль линий)
#             top_bottom = LinesCat.SubCategories.get_Item("BDV_E000_С_top_bottom_level")
#             # получили стиль линий GraphicsStyle тип Projection (в проекции, не в разрезе)
#             BDV_E000_С_top_bottom_level = top_bottom.GetGraphicsStyle(DB.GraphicsStyleType.Projection)
#             # присваиваем созданным линиям соответствующий стиль линий
#             for detailLine in detail_Lines:
#                 detailLine.LineStyle = BDV_E000_С_top_bottom_level
#     t.Commit()




        # print('текущий уровень:  ' + view_plan.GenLevel.Name)
        # print('верх_лево_магистралей:  ')
        # bprint(sorted(верх_лево_магистралей))
        # print('верх_лево_аварийного_освещения:  ')
        # bprint(sorted(верх_лево_аварийного_освещения))
        # print('верх_право_магистралей:  ')
        # bprint(sorted(верх_право_магистралей))
        # print('верх_право_аварийного_освещения:  ')
        # bprint(sorted(верх_право_аварийного_освещения))
        # print('низ_лево_магистралей:  ')
        # bprint(sorted(низ_лево_магистралей))
        # print('низ_лево_аварийного_освещения:  ')
        # bprint(sorted(низ_лево_аварийного_освещения))
        # print('низ_право_магистралей:  ')
        # bprint(sorted(низ_право_магистралей))
        # print('низ_право_аварийного_освещения:  ')
        # bprint(sorted(низ_право_аварийного_освещения))
        # print('______________________________________________________________')

