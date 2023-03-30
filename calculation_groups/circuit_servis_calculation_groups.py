# module circuit_servis.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
# clr.AddReference('RevitAPIUI')
from Autodesk.Revit import DB
import math

# doc = DM.Instance.CurrentDBDocument # Получение файла документа
# uiapp = DM.Instance.CurrentUIApplication  # для Dynamo
# app = uiapp.Application  # для Dynamo
# uidoc = uiapp.ActiveUIDocument  # для Dynamo


class CircuitСontain(object):
    koef_circuit = 1.05  # коэффициент запаса
    def __init__(self, circui_t):
        self.circuit = circui_t
        self.elementId_circuit = self.get_elementId_circuit()
        self.voltage = self.get_voltage()
        self.cosf = self.get_cosf()
        self.active_power = self.get_active_power()
        self.length_up_round = self.get_length_up_round()
        self.kilovatt_on_meter = self.get_kilovatt_on_meter()
        self.dU = self.get_dU()

    def get_elementId_circuit(self):
        return self.circuit.Id

    def get_voltage(self):
        '''напряжение цепи в вольтах'''
        parameter = self.circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_VOLTAGE]
        unit = parameter.GetUnitTypeId()
        return DB.UnitUtils.ConvertFromInternalUnits(parameter.AsDouble(), unit)

    def get_cosf(self):
        '''косинус, коэффициент мощности'''
        return self.circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_POWER_FACTOR].AsDouble()

    def get_active_power(self):
        '''активная мощность в киловаттах'''
        paramete_r = self.circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_TRUE_LOAD]
        uni_t = paramete_r.GetUnitTypeId()
        return DB.UnitUtils.ConvertFromInternalUnits(paramete_r.AsDouble(), uni_t) / 1000

    def get_full_power(self):
        '''полная мощность в киловаттах'''
        paramet_er = self.circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_APPARENT_LOAD]
        uni_t = paramet_er.GetUnitTypeId()
        return DB.UnitUtils.ConvertFromInternalUnits(paramet_er.AsDouble(), uni_t) / 1000

    def get_length_up_round(self):
        '''длина цепи округленая до большего целого'''
        parame_ter = self.circuit.Parameter[DB.BuiltInParameter.RBS_ELEC_CIRCUIT_LENGTH_PARAM]
        un_it = parame_ter.GetUnitTypeId()
        le_ng = DB.UnitUtils.ConvertFromInternalUnits(parame_ter.AsDouble(), un_it)
        return math.ceil((le_ng * self.koef_circuit) / 1000)

    def get_kilovatt_on_meter(self):
        '''момент мощности киловатт на метр'''
        return self.active_power * self.length_up_round

    def get_dU(self):
        '''падение напряжения на цепи в процентах'''
        # КОЭФ ДЛЯ 220В МЕДЬ табл.12-9 Кнорринга
        koef_С = 12

        return self.kilovatt_on_meter / koef_С / float(self.circuit.LookupParameter('кабСечение').AsString())


class CircuitWithMaxMoment(object):
    def __init__(self, list_circuits):
        self.circuits = list_circuits

    def get_circuit_with_max_moment(self):
        '''из списка цепей возврвщаетает цепь c максимальным моментом'''
        return max([CircuitСontain(cir).get_kilovatt_on_meter() for cir in self.circuits])


class FullPathToPanel(object):
    def __init__(self, doc, circuit, panel_familyinstance):
        '''из цепи извлекает все цепи до панели'''
        self._doc = doc
        self.circ = circuit
        self.pan_faminst = panel_familyinstance
        self.all_circuits = self.get_all_circuits()

    def get_all_circuits(self):
        all_circuits_in_path = [self.circ]
        circuit_i = self.circ
        # цикл повторяется пока питающая панель это не выбранный щит
        while circuit_i.BaseEquipment.Id != self.pan_faminst.Id:
            # все цепи, включая цепь питания панели
            circuits_all = [circuit_all.Id for circuit_all in circuit_i.BaseEquipment.MEPModel.GetElectricalSystems()]
            # только цепи нагрузок, без цепи питания панели
            circuits_loads = [circuit_loads.Id for circuit_loads in circuit_i.BaseEquipment.MEPModel.GetAssignedElectricalSystems()]
            # Если в проекте есть группы с одинаковм названием, но не соединены в общую цепь.
            # Есть группа с таким же названием и не подключенная к выбранной панели.
            # Названия групп в проекте должны быть уникальными, не должны повторяться, но такая ошибка может быть.
            if not list(set(circuits_all) - set(circuits_loads)):
                all_circuits_in_path.append('не подключена к выбранной панели')
                break
            # ЦЕПЬ КОТОРАЯ ПИТАЕТ ПАНЕЛЬ
            circuit_i = self._doc.GetElement(list(set(circuits_all) - set(circuits_loads))[0])
            all_circuits_in_path.append(circuit_i)
        return all_circuits_in_path


class CircuitHeadBaseEquipment(object):
    def __init__(self, doc, circuit):
        self._doc = doc
        self.circ = circuit

    def get_head_panel_from_all_path(self):
        '''из цепи возврвщаетает панель, к которой подсоединен весь путь цепей'''
        base_equipment = self.circ.BaseEquipment
        check_list = [1]
        while check_list:
            # все цепи, включая цепь питания панели
            circuits_all = [circuit_all.Id for circuit_all in base_equipment.MEPModel.GetElectricalSystems()]
            # только цепи нагрузок, без цепи питания панели
            circuits_loads = [circuit_loads.Id for circuit_loads in base_equipment.MEPModel.GetAssignedElectricalSystems()]
            if not list(set(circuits_all) - set(circuits_loads)):
                return base_equipment
                break
            circuit_i = self._doc.GetElement(list(set(circuits_all) - set(circuits_loads))[0])
            base_equipment = circuit_i.BaseEquipment
            check_list = list(set(circuits_all) - set(circuits_loads))

        return base_equipment
