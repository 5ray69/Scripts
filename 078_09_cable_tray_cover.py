# module_cable_tray_coer.py
# -*- coding: utf-8 -*-
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
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo

from revitutils.unit import Unit


with DB.Transaction(doc, 'create_КРЫШЕК_лотков/деталей') as t:
    t.Start()
    # ЛОТКИ
    # Создаем словарь типоразмеров крышек лотков ключ = ширина, значение = elementId типоразмера
    type_id_dict = {}
    list_types = [type for type in FEC(doc).OfCategory(
        DB.BuiltInCategory.OST_CableTray).WhereElementIsElementType() \
        if type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() \
            .find("Крышка") != -1]
    for type in list_types:
        # имя типоразмера крышки кабельного лотка
        type_name = type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()
        start = type_name.find('м') - 3  # индекс начала среза (три разряда влево)
        stop = type_name.find('м')  # индекс конца среза
        # na_me.append(type_name[start:stop])
        if type_name[start:stop] not in type_id_dict:
            type_id_dict[type_name[start:stop]] = type.Id

    # Для каждого экземпляра кабельного лотка
    for cable_tray in FEC(doc).OfClass(DB.Electrical.CableTray).ToElements():
        # красный - запрет для создания крышки
        if cable_tray.LookupParameter('БУДОВА_Крышка').AsInteger() == 1:
            # print(cable_tray)
            width_internal = cable_tray.Parameter[DB.BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM].AsDouble()
            # ширина во внешних единицах
            width = str(int(Unit(doc, width_internal, False).display))
            # высота лотка во внутренних единицах
            height = cable_tray.Parameter[DB.BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM].AsDouble()
            # получили точки существующего лотка
            sp = cable_tray.Location.Curve.GetEndPoint(0)
            ep = cable_tray.Location.Curve.GetEndPoint(1)
            cable_tray_new = DB.Electrical.CableTray.Create(
                doc,
                type_id_dict[width],  # ElementId cabletrayType (извлекли из словаря по ключу(ширине) id типоразмера крышки)
                DB.XYZ(sp.X, sp.Y, sp.Z + height/2),  # start point
                DB.XYZ(ep.X, ep.Y, ep.Z + height/2),  # end point
                cable_tray.Parameter[DB.BuiltInParameter.RBS_START_LEVEL_PARAM].AsElementId()  # ElementId level
            )
            # новому лотку/крышке присвоили ширину сущесвтующего лотка, уменьшив на 8мм
            cable_tray_new.Parameter[DB.BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM].Set(width_internal - Unit(doc, 8).internal)
            # новому лотку/крышке присвоили минимальную (25мм) высоту лотка
            cable_tray_new.Parameter[DB.BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM].Set(Unit(doc, 25).internal)
            # включаем красный - запрет на создание крышки
            cable_tray.LookupParameter('БУДОВА_Крышка').Set(0)
            cable_tray_new.LookupParameter('БУДОВА_Крышка').Set(0)

                # 4448105 крыш100мм цинк-лам
                # 4448106 крыш200мм цинк-лам
                # 4448107 крыш300мм цинк-лам
                # 4448108 крыш600мм цинк-лам

            # Применяем параметр ключевой спецификации для созданной крышки
            if width == "100":
                cable_tray_new.LookupParameter('KL_Аналог_лотка').Set(DB.ElementId(4448105))
            if width == "200":
                cable_tray_new.LookupParameter('KL_Аналог_лотка').Set(DB.ElementId(4448106))
            if width == "300":
                cable_tray_new.LookupParameter('KL_Аналог_лотка').Set(DB.ElementId(4448107))
            if width == "600":
                cable_tray_new.LookupParameter('KL_Аналог_лотка').Set(DB.ElementId(4448108))

    # СОЕДИНИТЕЛЬНЫЕ ДЕТАЛИ
    # получаем ключевую спецификацию крышек соед деталей
    for view_schedule in FEC(doc).OfClass(DB.ViewSchedule):
        if view_schedule.Name == 'Ключи спецификация крышек соед деталей кабельных лотков':
            break
    # элементы-призраки ключевой спецификации
    elements = FEC(doc, view_schedule.Id).ToElements()

    # Создаем словарь крышек 
    # ключ = имя ключа, значение = elementId ключа
    key_krushka = {}
    # имя ключа и elementId ключа
    for elem in elements:
        if elem.Name not in key_krushka:
            key_krushka[elem.Name] = elem.Id

    # получили все типоразмеры категории Соединительные детали кабельных лотков
    fitings_type_name = [fit.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() for fit in FEC(doc).OfCategory(
        DB.BuiltInCategory.OST_CableTrayFitting).WhereElementIsElementType()]

    # из элемента получаем его имя и оно есть именем типоразмера примененного к элементу
    fitings = [fit.Name for fit in FEC(doc).OfCategory(
        DB.BuiltInCategory.OST_CableTrayFitting).WhereElementIsNotElementType() if fit.LookupParameter('БУДОВА_Крышка').AsInteger() == 1]

    # Создаем словари типоразмеров крышек лотков ключ = ширина, значение = elementId типоразмера
    # словарь углов 90 градусов
    type_id_dict_L = {}
    # словарь 
    type_id_dict_T = {}
    # словарь крестовин
    type_id_dict_X = {}
    list_types_soed_det = [type_fit for type_fit in FEC(doc).OfCategory(
        DB.BuiltInCategory.OST_CableTrayFitting).WhereElementIsElementType() \
        if type_fit.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() \
            .find("Крышка") != -1]
    # наполняем три отдельных словаря типоразмеров крышек углов, Т-ответвителей и крестовин
    for type in list_types_soed_det:
        if type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString().find("угла") != -1:
            # имя типоразмера крышки кабельного лотка
            type_name = type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()
            start = type_name.find('м') - 3  # индекс начала среза (три разряда влево)
            stop = type_name.find('м')  # индекс конца среза
            # na_me.append(type_name[start:stop])
            if type_name[start:stop] not in type_id_dict_L:
                type_id_dict_L[type_name[start:stop]] = type.Id
        if type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString().find("Т-образная") != -1:
            # имя типоразмера крышки кабельного лотка
            type_name = type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()
            start = type_name.find('м') - 3  # индекс начала среза (три разряда влево)
            stop = type_name.find('м')  # индекс конца среза
            # na_me.append(type_name[start:stop])
            if type_name[start:stop] not in type_id_dict_T:
                type_id_dict_T[type_name[start:stop]] = type.Id
        if type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString().find("Крестообразная") != -1:
            # имя типоразмера крышки кабельного лотка
            type_name = type.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()
            start = type_name.find('м') - 3  # индекс начала среза (три разряда влево)
            stop = type_name.find('м')  # индекс конца среза
            # na_me.append(type_name[start:stop])
            if type_name[start:stop] not in type_id_dict_X:
                type_id_dict_X[type_name[start:stop]] = type.Id

    fitings = [fit for fit in FEC(doc).OfCategory(
        DB.BuiltInCategory.OST_CableTrayFitting).WhereElementIsNotElementType() if fit.LookupParameter('БУДОВА_Крышка').AsInteger() == 1]
    for fit_to_copy in fitings:
        # выставляем галку на запрет создания крышки и убираем галку с БУДОВА_Крышка
        # они скопируются с ней
        # и убираем галку с БУДОВА_Крышка они скопируются с ней
        fit_to_copy.LookupParameter('БУДОВА_Крышка').Set(0)
    # высота лотка во внутренних единицах
        height = fit_to_copy.LookupParameter('Высота лотка').AsDouble()
        if fit_to_copy.Name.find("Угол") != -1:
            fit_copyed = DB.ElementTransformUtils.CopyElement(
                doc,
                fit_to_copy.Id,  # элемент Id копируемых экземпляров
                DB.XYZ(0, 0, height / 2)  # трансляция - подаем только расстояние, на которое нужно переместить (вектор/длина перемещения)
            )
            # в новых деталях меняем типоразмер на крышку
            # из словаря типоразмеров подготовленного выше
            # если нет соответствующей крышки - создавай новый типорамзер
            for new_fitId in fit_copyed:
                new_fit = doc.GetElement(new_fitId)
                # высоту лотка делаем 4мм
                new_height = new_fit.LookupParameter('Высота лотка').Set(Unit(doc, 4).internal)
                # ширина лотка во внутренних единицах
                width_fit_internal = new_fit.LookupParameter('Ширина лотка').AsDouble()
                # ширина лотка во внешних единицах и перевели в строку, int, чтоб убрать нули
                width_fit = str(int(Unit(doc, width_fit_internal, False).display))

                # крыш_L100цл.90°r100 4457255
                # крыш_L200цл.90°r100 4457256
                # крыш_L300цл.90°r100 4457257
                # крыш_L600цл.90°r100 4457258

                # Применяем параметр ключевой спецификации для созданной крышки
                if width_fit == "100":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457255))
                if width_fit == "200":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457256))
                if width_fit == "300":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457257))
                if width_fit == "600":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457258))
                
                # меняем типоразмер новой соединительной детали из словаря подав id в соответствии с шириной
                new_fit.ChangeTypeId(type_id_dict_L[width_fit])  # ElementId извлекли из словаря по ключу(ширине) id типоразмера крышки)

        if fit_to_copy.Name.find("Т-ответвитель") != -1:
            fit_copyed = DB.ElementTransformUtils.CopyElement(
                doc,
                fit_to_copy.Id,  # элемент Id копируемых экземпляров
                DB.XYZ(0, 0, height / 2)  # трансляция - подаем только расстояние, на которое нужно переместить (вектор/длина перемещения)
            )
            # в новых деталях меняем типоразмер на крышку
            # из словаря типоразмеров подготовленного выше
            # если нет соответствующей крышки - создавай новый типорамзер
            for new_fitId in fit_copyed:
                new_fit = doc.GetElement(new_fitId)
                # высоту лотка делаем 4мм
                new_height = new_fit.LookupParameter('Высота лотка').Set(Unit(doc, 4).internal)
                # ширина лотка во внутренних единицах
                width_fit_internal = new_fit.LookupParameter('Ширина лотка 1').AsDouble()
                # ширина лотка во внешних единицах и перевели в строку, int, чтоб убрать нули
                width_fit = str(int(Unit(doc, width_fit_internal, False).display))

                # крыш_T100цл.r100 4457259
                # крыш_T200цл.r100 4457260
                # крыш_T300цл.r100 4457261
                # крыш_T600цл.r100 4457262

                # Применяем параметр ключевой спецификации для созданной крышки
                if width_fit == "100":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457259))
                if width_fit == "200":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457260))
                if width_fit == "300":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457261))
                if width_fit == "600":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457262))
                
                # меняем типоразмер новой соединительной детали из словаря подав id в соответствии с шириной
                new_fit.ChangeTypeId(type_id_dict_T[width_fit])  # ElementId извлекли из словаря по ключу(ширине) id типоразмера крышки)

        if fit_to_copy.Name.find("Крестообразный") != -1:
            fit_copyed = DB.ElementTransformUtils.CopyElement(
                doc,
                fit_to_copy.Id,  # элемент Id копируемых экземпляров
                DB.XYZ(0, 0, height / 2)  # трансляция - подаем только расстояние, на которое нужно переместить (вектор/длина перемещения)
            )
            # в новых деталях меняем типоразмер на крышку
            # из словаря типоразмеров подготовленного выше
            # если нет соответствующей крышки - создавай новый типорамзер
            for new_fitId in fit_copyed:
                new_fit = doc.GetElement(new_fitId)
                # высоту лотка делаем 4мм
                new_height = new_fit.LookupParameter('Высота лотка').Set(Unit(doc, 4).internal)
                # ширина лотка во внутренних единицах
                width_fit_internal = new_fit.LookupParameter('Ширина лотка 1').AsDouble()
                # ширина лотка во внешних единицах и перевели в строку, int, чтоб убрать нули
                width_fit = str(int(Unit(doc, width_fit_internal, False).display))

                # крыш_X100цл.r100 4457263
                # крыш_X200цл.r100 4457264
                # крыш_X300цл.r100 4457265
                # крыш_X600цл.r100 4457266

                # Применяем параметр ключевой спецификации для созданной крышки
                if width_fit == "100":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457263))
                if width_fit == "200":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457264))
                if width_fit == "300":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457265))
                if width_fit == "600":
                    new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId(4457266))
                
                # меняем типоразмер новой соединительной детали из словаря подав id в соответствии с шириной
                new_fit.ChangeTypeId(type_id_dict_X[width_fit])  # ElementId извлекли из словаря по ключу(ширине) id типоразмера крышки)
    t.Commit()

                # # значение ключевого параметра для соединительных деталей, выставляем (нет)
                # new_fit.LookupParameter('KD_Аналог_соед_детали').Set(DB.ElementId.InvalidElementId)