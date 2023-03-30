# module user_warning.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Windows.Forms')
import System.Windows.Forms as WF


class ParametrGroupEmptyException(Exception):
    def __init__(self, one_circuit):
        self.message = "Внимание! \
                        \nЕсть цепи с незаполненным параметром БУДОВА_Группа.\
                        Например, цепь с Id: " + str(one_circuit.Id) \
                        + "\nЗаполните c помощью скрипта rename_circuit."
                        
        WF.MessageBox.Show(self.message)


class DoubleGroupsException(Exception):
    def __init__(self, group_str):
        self.message = "Внимание! \
                        \nЕсть две отдельные группы с одинаковым именем.\
                        \nИли соедините их в одну, или переименуйте одну из них.\
                        \nНапример, две отдельные группы с общим именем и коды \
                        \nих панелей для поиска:  "  + group_str
                        
        WF.MessageBox.Show(self.message)
