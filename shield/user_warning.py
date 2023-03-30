# module user_warning.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Windows.Forms')
import System.Windows.Forms as WF


class SelectShieldException(Exception):
    def __init__(self):
        self.message = "Не выбран щит(панель). \
                        \nНужно выделить щит на плане."
        WF.MessageBox.Show(self.message)


class SelectedWrongItemException(Exception):
    def __init__(self):
        self.message = "Ошибка выбора. \
                        \nВыбранный элемент не является \
                        \nэлементом категории Электрооборудование."
        WF.MessageBox.Show(self.message)


class ParametrGroupEmptyException(Exception):
    def __init__(self, one_circuit):
        self.message = "Внимание! \
                        \nЕсть цепи с незаполненным параметром БУДОВА_Группа.\
                        Например, цепь с Id: " + str(one_circuit.Id) \
                        + "\nЗаполните c помощью скрипта rename_circuit."
                        
        WF.MessageBox.Show(self.message)
