# module calculationGroups.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from System.Collections.Generic import List
import math


from calculation_groups.user_warning_calculation_groups import ParametrGroupEmptyException, \
                                DoubleGroupsException
                                
from calculation_groups.circuit_servis_calculation_groups import CircuitСontain, \
                                CircuitHeadBaseEquipment, FullPathToPanel


class CalculationGroups(object):
    koef_circuit = 1.05  # коэффициент запаса
    def __init__(self, doc, uidoc):
        self._doc = doc
        self._uidoc = uidoc
        self.circuits_in_groups = self.get_circuits_in_groups()
        self.end_circuits_in_group = self.get_end_circuits_in_group()
        self.head_panel = self.get_head_panel()
        self.full_path_to_head_panel = self.get_full_path_to_head_panel()
        self.list_circuits_in_path_with_max_dU = {}
        self.value_max_dU_from_path_with_max_dU = self.get_value_max_dU_from_path_with_max_dU()
        self.circuit_loads_from_panel_for_group = self.get_circuit_loads_from_panel_for_group()

    def get_circuits_in_groups(self):
        '''Извлекает все группы проекта содержащие 'гр' и цепи им принадлежащие.
        Цепи дублирующихся групп здесь есть'''
        groupStr_circuitsList = {}
        for circuit in FEC(self._doc).OfCategory(DB.BuiltInCategory.OST_ElectricalCircuit).ToElements():
            if not circuit.LookupParameter('БУДОВА_Группа').AsString():
                raise ParametrGroupEmptyException(circuit)
            else:
                if 'гр' in circuit.LookupParameter('БУДОВА_Группа').AsString():
                    if circuit.LookupParameter('БУДОВА_Группа').AsString() not in groupStr_circuitsList:
                        groupStr_circuitsList[circuit.LookupParameter('БУДОВА_Группа').AsString()] = []
                    groupStr_circuitsList[circuit.LookupParameter('БУДОВА_Группа').AsString()].append(circuit)
        return groupStr_circuitsList

    def get_end_circuits_in_group(self):
        '''Извлекает цепи являющиеся конечными ветками в группе.
        Цепи дублирующихся групп здесь есть'''
        end_circuit = {}
        for name_group_str, list_circuits_in_group in self.circuits_in_groups.items():
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

    def get_head_panel(self):
        '''получает головную панель до которой будут извлекаться все пути.
        Цепи дублирующихся групп здесь есть - предупреждение
        объеднить или переименовать их.'''
        group_headPanel = {}
        for group_str, list_circuit in self.end_circuits_in_group.items():
            if group_str not in group_headPanel:
                group_headPanel[group_str] = []

            uniqum_headPanels_in_group = set()
            for circuit in list_circuit:
                uniqum_headPanels_in_group.add((CircuitHeadBaseEquipment(self._doc, circuit).get_head_panel_from_all_path()).Id)

            if len(uniqum_headPanels_in_group) > 1:
                for elementId in uniqum_headPanels_in_group:
                    group_str += ', ' + str(elementId.IntegerValue)
                raise DoubleGroupsException(group_str)

            for element_id in uniqum_headPanels_in_group:
                group_headPanel[group_str].append(element_id)

        return group_headPanel

    def get_full_path_to_head_panel(self):
        '''Извлекает полный путь от конечной цепи до выбранной панели.
        Цепи дублирующихся групп здесь уже должны быть устранены после get_head_panel'''
        all_circuits_in_path = {}
        for global_group_str, list_end_circuits in self.end_circuits_in_group.items():
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
                    if c_ircuit.BaseEquipment.Id == self._doc.GetElement(self.head_panel[global_group_str][0]).Id:
                        dict_one_path['path' + str(i)].append([c_ircuit])
                    if c_ircuit.BaseEquipment.Id != self._doc.GetElement(self.head_panel[global_group_str][0]).Id:
                        dict_one_path['path' + str(i)].append(
                            FullPathToPanel(self._doc, c_ircuit, self._doc.GetElement(self.head_panel[global_group_str][0])).get_all_circuits())
                dict_one_path['path' + str(i)].append(
                        FullPathToPanel(self._doc, c_ircuit, self._doc.GetElement(self.head_panel[global_group_str][0])).get_all_circuits())
            all_circuits_in_path[global_group_str] = dict_one_path

        return all_circuits_in_path

    def get_value_max_dU_from_path_with_max_dU(self):
        '''Извлекает путь c максимальным dU из всех других и dU пути'''
        paths_max_dU = {}
        for glob_group_str, dict_paths_in_group in self.full_path_to_head_panel.items():
            if glob_group_str not in paths_max_dU:
                paths_max_dU[glob_group_str] = []
            self.list_circuits_in_path_with_max_dU[glob_group_str] = []

            keypas_valuedU = {}
            keypas_valuelist_circuits = {}
            for path_str, list_in_list_circuits in dict_paths_in_group.items():
                keypas_valuedU[path_str] = 0.0

                for list_circuits in list_in_list_circuits:
                    keypas_valuelist_circuits[path_str] = list_circuits
                    for circui in list_circuits:
                        keypas_valuedU[path_str] = keypas_valuedU[path_str] + CircuitСontain(circui).get_dU()
            invers = [(value_dU, path_string) for path_string, value_dU in keypas_valuedU.items()]
            paths_max_dU[glob_group_str] = max(invers)[0]
            self.list_circuits_in_path_with_max_dU[glob_group_str].append(keypas_valuelist_circuits[max(invers)[1]])

        return paths_max_dU

    def get_maxM_path_with_maxdU(self):
        '''Извлекает момент пути с максимальным dU.
        Цепей дублирующихся групп здесь нет.'''
        dict_group_max_M = {}
        for k_gr, v_dU_listcircuit in self.list_circuits_in_path_with_max_dU.items():
            for value in v_dU_listcircuit:
                dict_group_max_M[k_gr] = math.ceil(sum(
                    [CircuitСontain(one_cir).get_length_up_round() * CircuitСontain(one_cir).get_active_power() 
                                for one_cir in value]))

        return dict_group_max_M

    def get_length_by_groups_all_circuits(self):
        '''Извлекает полные длины всех одноименных цепей нагрузок панели в метрах'''
        dict_length = {}
        for group, list_circuit in self.circuits_in_groups.items():
            if group not in dict_length:
                dict_length[group] = []
            list_length = []
            for circu in list_circuit:
                list_length.append(CircuitСontain(circu).get_length_up_round())
            dict_length[group].append(sum(list_length))

        return dict_length

    def get_circuit_loads_from_panel_for_group(self):
        '''Извлекает отходящую цепь теущей группы от головной панели
        для дальнейшего извлечения мощности и косинуса'''
        dict_gorup_loadcircuit = {}
        for group_st, list_elementId_panel in self.head_panel.items():
            if group_st not in dict_gorup_loadcircuit:
                dict_gorup_loadcircuit[group_st] = []
            dict_gorup_loadcircuit[group_st].append(
                [loadcircuit for loadcircuit in self._doc.GetElement(list_elementId_panel[0]).MEPModel.GetAssignedElectricalSystems()
                if loadcircuit.LookupParameter('БУДОВА_Группа').AsString() == group_st])
        
        return dict_gorup_loadcircuit

    def get_selected_end_circuits(self):
        '''Выделяет конечные цепи'''
        element_ids = List[DB.ElementId]()
        for lists_value in self.end_circuits_in_group.values():
            for el_circuit in lists_value:
                element_ids.Add(el_circuit.Id)

        return self._uidoc.Selection.SetElementIds(element_ids)

    def get_selected_head_panel(self):
        '''Выделяет головные панели'''
        element_ids = List[DB.ElementId]()
        for lists_value in self.head_panel.values():
            for el_circuit in lists_value:
                element_ids.Add(el_circuit.Id)

        return self._uidoc.Selection.SetElementIds(element_ids)
