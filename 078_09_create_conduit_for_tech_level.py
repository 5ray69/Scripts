# module create_conduit_for_tech_level.py
# -*- coding: utf-8 -*

import clr
clr.AddReference('RevitAPI')
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

# "C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Разработка Варненская, 9\Скрипты\create_conduit_for_tech_level\user_form_create_conduit.py"
from revitutils.unit import Unit
from create_conduit_for_tech_level.user_form_create_conduit import UserFormCreateConduitForLevel, ErrorMessageViewNotConnectedToLevel
from create_conduit_for_tech_level.sort_names_levels_create_conduit import my_sort_names_levels

doc = DM.Instance.CurrentDBDocument  # Получение файла документа


levels_from_project = my_sort_names_levels([lev.Name for lev in FEC(doc).OfClass(DB.Level)])
form = UserFormCreateConduitForLevel(levels_from_project)
form.ShowDialog()
# список выбора пользователя
# В список помещаем имя уровня, для которого хотим создать из эл.цепей короба
level_selected_user = []
for el in form.list_user_select:
    if el == 'Активный вид':
        # если активный вид связан с уровнем
        if isinstance(doc.ActiveView, DB.ViewPlan):
            level_selected_user.append(doc.ActiveView.GenLevel.Name)
        else:
            ErrorMessageViewNotConnectedToLevel()
    else:
        level_selected_user.append(el)


# Получаем ElementId нужного типоразмера
conduitType_elementId = [con.Id for con in FEC(doc).OfClass(DB.Electrical.ConduitType) \
                        if con.Parameter[DB.BuiltInParameter.ALL_MODEL_FAMILY_NAME].AsString() == 'Короб с соединительными деталями' \
                        and con.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == 'Короб']


with DB.Transaction(doc, 'create_conduit_for_tech_level') as t:
    t.Start()
    for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
        if doc.GetElement(el_circuit.BaseEquipment.Id).Host.Name in level_selected_user:
            # получили путь/траекторию цепи
            path = el_circuit.GetCircuitPath()
            for i in range(len(path) - 1):
                if path[i].DistanceTo(path[i + 1]) > 0.1:
                    conduit = DB.Electrical.Conduit.Create(
                        doc,
                        conduitType_elementId[0],
                        path[i],
                        path[i + 1],
                        # Id уровня дозы, к которой подключена цепь
                        doc.GetElement(el_circuit.BaseEquipment.Id).Host.Id
                    )
                    if 'гр' in el_circuit.Name:
                        # Диаметр Короба (Размер по каталогу)
                        # Присвоили коробу диаметр наружного диаметра кабеля, если его нет, то назначаем диаметр из списка каталога 9мм 
                        # если в каталоге такого диаметра нет, то все, внутренний, наружный и по каратлогу будут 9мм,
                        # если близок к имеющемуся, то будет выбран имеющийся из каталога)
                        conduit.Parameter[DB.BuiltInParameter.RBS_CONDUIT_DIAMETER_PARAM].Set(Unit(doc, 32).internal)
                        # присваиваем значение 'метрукав  32мм' ElementId 690410
                        conduit.LookupParameter('Стиль коробов').Set(DB.ElementId(690410))
                    else:
                        conduit.Parameter[DB.BuiltInParameter.RBS_CONDUIT_DIAMETER_PARAM].Set(Unit(doc, 60).internal)
                        # присваиваем значение 'метрукав  60мм' ElementId 690406
                        conduit.LookupParameter('Стиль коробов').Set(DB.ElementId(690406))


                    # Заполняем параметр БУДОВА_Группа для подсчета коробов
                    # если в имени цепи есть точка "." (для всего что не магистрали квартир)
                    if '.' in el_circuit.Name:
                        number_circuit = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
                        conduit.LookupParameter('БУДОВА_Группа').Set(number_circuit[:number_circuit.rfind('.')])
                    # # если в имени цепи есть "/" (для магистралей квартир) этот же символ есть и у вентиляторов, потому найди другой критерий
                    # if '/' in el_circuit.Name:
                    #     number_circuit = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER].AsString()
                    #     conduit.LookupParameter('БУДОВА_Группа').Set(number_circuit[:number_circuit.rfind('э')])
    t.Commit()
