# module shield.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')  # Работа с документом и транзакциями
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from RevitServices.Persistence import DocumentManager as DM  # Менеджер документа
from System.Collections.Generic import List
import math

import sys
sys.path += [
    # r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\Рабочка Варненская, 9\Скрипты",
    # путь будет вытягиваться в Dynamo нодами
    IN[0].DirectoryName  # noqa
]

from shield.user_warning import SelectShieldException, \
                                SelectedWrongItemException, \
                                ParametrGroupEmptyException
from shield.circuit_servis import CircuitСontain, FullPathToPanel

doc = DM.Instance.CurrentDBDocument # Получение файла документа
uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
app = uiapp.Application  # для Dynamo
uidoc = uiapp.ActiveUIDocument  # для Dynamo


class Shield(object):
    koef_circuit = 1.05  # коэффициент запаса
    def __init__(self, doc, uidoc):
        self._doc = doc
        self._uidoc = uidoc
        self.panel_familyinstance = self.get_selected_panel()
        self.circuit_loads = self.get_circuit_loads_from_panel()
        self.budova_group_circuit = self.get_budova_group_circuit()
        self.loads_circuit = self.get_loads_circuit()
        self.all_circuits_in_group = self.get_all_circuits_in_group()
        self.length_by_names_groups_all_circuits = self.get_length_by_names_groups_all_circuits()
        self.end_circuits = self.get_end_circuits()
        self.full_path_to_selected_panel = self.get_full_path_to_selected_panel()
        self.paths_repeat_group = {}
        self.paths_not_repeat_group = {}
        self.path_with_max_dU = self.get_path_with_max_dU()
        self.maxM_path_with_maxdU = self.get_maxM_path_with_maxdU()
        self.length_by_groups_all_circuits_without_repeating = self.get_length_by_groups_all_circuits_without_repeating()

    def get_selected_panel(self):
        '''Получили выделенную в проекте панель'''

        if not self._uidoc.Selection.GetElementIds():
            raise SelectShieldException()

        if doc.GetElement(
            list(uidoc.Selection.GetElementIds())[0]
            ).Category.Name != 'Электрооборудование':
            raise SelectedWrongItemException()

        return self._doc.GetElement(
            list(self._uidoc.Selection.GetElementIds())[0]
        )

    def get_circuit_loads_from_panel(self):
        '''Извлекает все цепи нагрузок панели'''
        return [circuit_loads for circuit_loads in self.panel_familyinstance.MEPModel.GetAssignedElectricalSystems()]

    def get_budova_group_circuit(self):
        '''Извлекает названия в виде string из БУДОВА_Группа всех цепей нагрузок панели'''
        name_group = []
        for one_circuit in self.circuit_loads:
            if not one_circuit.LookupParameter('БУДОВА_Группа').AsString():
                raise ParametrGroupEmptyException(one_circuit)
            name_group.append(one_circuit.LookupParameter('БУДОВА_Группа').AsString())
        return name_group

    def get_loads_circuit(self):
        '''Извлекает объекты familyinstans (дозы) нагрузок цепей панели'''
        loads_circuit = []
        for one_circuit in self.circuit_loads:
            for faminstan in one_circuit.Elements:
                loads_circuit.append(faminstan)
        return loads_circuit

    def get_all_circuits_in_group(self):
        '''Извлекает все цепи группы.
        Цепи дублирующихся групп здесь есть - отдели их.'''
        all_circuit = {}
        for el_circuit in FEC(doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
            for name_str in self.budova_group_circuit:
                if not el_circuit.LookupParameter('БУДОВА_Группа').AsString():
                    raise ParametrGroupEmptyException(el_circuit)
                if el_circuit.LookupParameter('БУДОВА_Группа').AsString() == name_str:
                    if name_str not in all_circuit:
                        all_circuit[name_str] = []
                    all_circuit[name_str].append(el_circuit)
        return all_circuit

    def get_length_by_names_groups_all_circuits(self):
        '''Извлекает полные длины всех одноименных цепей нагрузок панели в метрах.
        Цепи дублирующихся групп здесь есть - отдели их.'''
        sum_length_circuit = {}
        for name_str, lst_el_circuit in self.all_circuits_in_group.items():
            if name_str not in sum_length_circuit:
                sum_length_circuit[name_str] = [0]
            for el_circuit in lst_el_circuit:
                parameter = el_circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]
                unit = parameter.GetUnitTypeId()
                leng = DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)
                # округляем до большего целого каждую цепь
                leng_with_koef = math.ceil((leng * self.koef_circuit) / 1000)
                leng_sum = sum_length_circuit[name_str].pop() + leng_with_koef
                sum_length_circuit[name_str].append(leng_sum)
        return sum_length_circuit

    def get_end_circuits(self):
        '''Извлекает цепи являющиеся конечными ветками в группе.
        Цепи дублирующихся групп здесь есть - отдели их.'''
        end_circuit = {}
        for name_group_str, list_circuits_in_group in self.all_circuits_in_group.items():
            if name_group_str not in end_circuit:
                end_circuit[name_group_str] = []
            for one_circuit_from_group in list_circuits_in_group:
                # список всех цепей нагрузок имеющихся у всех панелей одной цепи
                all_circuit_loads_Equipment = []
                for family_instan in one_circuit_from_group.Elements:
                    # если это панель, а если панелей в цепи нет, то список остается пустой и
                    # выходит сразу два условия:
                    # 1.в цепи нет панелей 2.у панелей имеющихся в цепи нет отходящих линий(ниже по коду)
                    if isinstance(family_instan.MEPModel, DB.Electrical.ElectricalEquipment):
                        if family_instan.MEPModel.GetAssignedElectricalSystems():
                            for one_circuit_loads in family_instan.MEPModel.GetAssignedElectricalSystems():
                                # добавляем цепь нагрузки в список
                                all_circuit_loads_Equipment.append(one_circuit_loads)

                # если список отходящих цепей(нагрузок) пуст
                if not all_circuit_loads_Equipment:
                    # если нагрузка цепи не выключатель
                    if [family_instan.Category.Name != 'Выключатели' for family_instan in one_circuit_from_group.Elements][0]:
                        end_circuit[name_group_str].append(one_circuit_from_group)
        # конечная цепь если:
        # 1. если в элементах цепи нет панелей - словарь ключ:группа значение:[панели] - если у какой-то группы список пуст, то она конечная
        # 2. если если у всех панелей содержращихся в цепи нет цепей нагрузок - словарь ключ:группа значение:[цепи нагрузок], если хотя бы одна цепь есть в списке, то цепь не конечная
        # 3. если нагрузка цепи не выключатель путь до выключателя как до конечной цепи не нужен
        return end_circuit

    def get_full_path_to_selected_panel(self):
        '''Извлекает полный путь от конечной цепи до выбранной панели.
        Цепи дублирующихся групп здесь есть, но уже промаркированы.'''
        all_circuits_in_path = {}
        for global_group_str, list_end_circuits in self.end_circuits.items():
            if global_group_str not in all_circuits_in_path:
                all_circuits_in_path[global_group_str] = {}

            dict_one_path = {}
            i = 0
            for c_ircuit in list_end_circuits:
                i += 1
                if 'path' + str(i) not in dict_one_path:
                    dict_one_path['path' + str(i)] = []
                if len(list_end_circuits) == 1:
                    # если только одна цепь от щита и она же конечная
                    if c_ircuit.BaseEquipment.Id == self.panel_familyinstance.Id:
                        dict_one_path['path' + str(i)].append([c_ircuit])
                    if c_ircuit.BaseEquipment.Id != self.panel_familyinstance.Id:
                        dict_one_path['path' + str(i)].append(
                            FullPathToPanel(self._doc, c_ircuit, self.panel_familyinstance).get_all_circuits())
                dict_one_path['path' + str(i)].append(
                        FullPathToPanel(self._doc, c_ircuit, self.panel_familyinstance).get_all_circuits())

            all_circuits_in_path[global_group_str] = dict_one_path

        return all_circuits_in_path

    def get_path_with_max_dU(self):
        '''Извлекает путь c максимальным dU из всех других и dU пути.
        Цепей дублирующихся групп здесь нет.'''
        paths_max_dU = {}
        for glob_group_str, dict_paths_in_group in self.full_path_to_selected_panel.items():
            if glob_group_str not in paths_max_dU:
                paths_max_dU[glob_group_str] = []
            # цепи дублирующих групп (не подключенных к панели) заносим в атрибут
            self.paths_repeat_group[glob_group_str] = []
            # пути без дублирующих групп заносим в атрибут
            self.paths_not_repeat_group[glob_group_str] = {}

            keypas_maxvaluedU = {}
            keypas_valuedU = {}
            keypas_valuelist_circuits = {}
            dict_paths_not_repeat_group = {}
            for path_str, list_in_list_circuits in dict_paths_in_group.items():
                keypas_valuedU[path_str] = 0.0
                if path_str not in dict_paths_not_repeat_group:
                    dict_paths_not_repeat_group[path_str] = []

                for list_circuits in list_in_list_circuits:
                    keypas_valuelist_circuits[path_str] = list_circuits
                    # если цепь не подключена к выбранному щиту,
                    # то весь путь, со всеми цепями в нем, не учитываем
                    if 'не подключена к выбранной панели' not in list_circuits:
                        # добавляем в словарь атрибута пути без повторящихся групп
                        dict_paths_not_repeat_group[path_str].append(list_circuits)
                        for circui in list_circuits:
                            keypas_valuedU[path_str] = keypas_valuedU[path_str] + CircuitСontain(circui).get_dU()
                    else:
                        # добавляем в словарь атрибута путей повторящихся групп
                        self.paths_repeat_group[glob_group_str].append(list_circuits)
                        # удалили из словаря этот путь с цепями, не учитываем в расчетах
                        del keypas_valuedU[path_str]

                self.paths_not_repeat_group[glob_group_str] = dict_paths_not_repeat_group

            invers = [(value_dU, path_string) for path_string, value_dU in keypas_valuedU.items()]
            keypas_maxvaluedU[max(invers)[1]] = [max(invers)[0]]
            keypas_maxvaluedU[max(invers)[1]].append(keypas_valuelist_circuits[max(invers)[1]])

            paths_max_dU[glob_group_str] = keypas_maxvaluedU

        return paths_max_dU

    def get_maxM_path_with_maxdU(self):
        '''Извлекает момент пути с максимальным dU.
        Цепей дублирующихся групп здесь нет.'''
        dict_group_max_M = {}
        for k_gr, v_dU_listcircuit in self.path_with_max_dU.items():
            for value in v_dU_listcircuit.values():
                dict_group_max_M[k_gr] = math.ceil(sum(
                    [CircuitСontain(one_cir).get_length_up_round() * CircuitСontain(one_cir).get_active_power() 
                                for one_cir in value[1]]))

        return dict_group_max_M

    def get_length_by_groups_all_circuits_without_repeating(self):
        '''Извлекает полные длины всех одноименных цепей нагрузок панели в метрах.
        Цепей дублирующихся групп здесь нет.'''
        dict_length_repeat = {}
        for group, list_in_list_path in self.paths_repeat_group.items():
            if group not in dict_length_repeat:
                dict_length_repeat[group] = []

            set_circuits = set()
            for lis in list_in_list_path:
                for el_list in lis:
                    if not isinstance(el_list, str):
                        set_circuits.add(el_list.Id)
            list_length = []
            for elemId in set_circuits:
                list_length.append(CircuitСontain(self._doc.GetElement(elemId)).get_length_up_round())
            dict_length_repeat[group].append(sum(list_length))

        # вычитаем из длин всех груп подключенных, длины повторяющихся групп (одноименных в проекте)
        dict_length_without_repeating = {}
        for key_group, value_length in self.length_by_names_groups_all_circuits.items():
            dict_length_without_repeating[key_group] = value_length[0] - dict_length_repeat[key_group][0]

        return dict_length_without_repeating

    def get_data_to_excel(self):
        '''Извлекает данные для записи в эксель'''
        all_data_list = []
        # Это все пути, а не все цепи в группе, получи только цепи отходящих линий
        # от щита (первая/одна цепь).
        # В них есть и активная нагрузка и косинус, суммировать все цепи группы неправильно, 
        # потому что в каждой из цепей суммарная мощность всего последующего пути к ней приложенная
        for cir in self.circuit_loads:
            data_list = []
            data_list2 = []
            # добавляем пустой список для отделения в экселе групп
            data_list3 = []
            # ГРУППА
            data_list.append(cir.LookupParameter('БУДОВА_Группа').AsString())
            # МОЩНОСТЬ
            data_list.append(CircuitСontain(cir).get_active_power())
            # КОСИНУС
            if CircuitСontain(cir).get_full_power() == 0:
                data_list.append(0)
            else:
                data_list.append(CircuitСontain(cir).get_active_power() / CircuitСontain(cir).get_full_power())
            # ТОК (округен до большего целого, иначе при 0,3А будет округляться до нуля)
            if CircuitСontain(cir).get_full_power() == 0:
                data_list.append(0)
            else:
                data_list.append(math.ceil(
                    CircuitСontain(cir).get_active_power() / 0.22 / (CircuitСontain(cir).get_active_power() / CircuitСontain(cir).get_full_power())))
            # ДЛИНА ВСЕХ ПРОВОДОВ ГРУППЫ
            data_list.append(
                self.length_by_groups_all_circuits_without_repeating[cir.LookupParameter('БУДОВА_Группа').AsString()])

            # ПУСТАЯ СТРОКА ДЛЯ ОТСТУПА
            data_list2.append('')

            # МОМЕНТ ПУТИ С МАКСИМАЛЬНЫМ DU
            data_list2.append(self.maxM_path_with_maxdU[cir.LookupParameter('БУДОВА_Группа').AsString()])

            # DU, ДЛЯ ПУТИ ИЗ ЦЕПЕЙ С МАКСИМАЛЬНЫМ DU
            data_list2.append(round([value[0] for value in self.path_with_max_dU[cir.LookupParameter('БУДОВА_Группа').AsString()].values()][0], 2))

            # ТИП КАБЕЛЯ ИЗ КЛЮЧЕВОГО ПАРАМЕТРА ЦЕПИ
            data_list2.append(self._doc.GetElement(cir.LookupParameter('Тип кабеля').AsElementId()).Name)

            all_data_list.append(data_list)
            all_data_list.append(data_list2)
            all_data_list.append(data_list3)

        return all_data_list

    def get_Id_circuit_path_maxdU(self):
        '''Выделяет пути с maxdU'''
        element_ids = List[DB.ElementId]()
        # element_ids = []
        for lists_value in self.path_with_max_dU.values():
            for value in lists_value.values():
                for el_circuit in value[1]:
                    element_ids.Add(el_circuit.Id)


        return self._uidoc.Selection.SetElementIds(element_ids)


eq = Shield(doc, uidoc)
OUT = eq.get_selected_panel(), eq.get_data_to_excel(), eq.paths_repeat_group, eq.get_Id_circuit_path_maxdU()
