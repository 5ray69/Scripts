# -*- coding: utf-8 -*-
# module user_warning_rename_circuit.py
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import System.Windows.Forms


class ErrorCircuitNoConect(Exception):
    def __init__(self):
        self.message = "Есть цепи неподключенные к панелям.\
                        \nCмотрите выпадающий список\
                        \nиз нода Python Script From String."
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorEnglishLetter(Exception):
    def __init__(self, name_group_str, elementId):
        self.message = "Закройте этот скрипт и запустите\
                        \nскрипт 078_09_replace_english_letter_in_equipment_and_circuit.dyn\
                        \nЕсть английские буквы вместо русских\
                        \nв именах групп электрооборудования и цепей.\
                        \nНапример, в " + name_group_str + " Id элемента: " + str(elementId.IntegerValue)
        System.Windows.Forms.MessageBox.Show(self.message)


class ErrorNumberStoyak(Exception):
    def __init__(self, equipment, elementId):
        self.message = "Параметр 'BDV_E000_Номер стояка' или не заполнен,\
                        \nили имеет значение больше двух.\
                        \nИсправьте его значение в \
                        \n" + equipment.Parameter[
                                DB.BuiltInParameter.ELEM_TYPE_PARAM].\
                                AsValueString() + ", \
                        \nс именем панели " + equipment.Name + ", \
                        \nc Id элемента: " + str(elementId.IntegerValue) + ".\
                        \nИ запустите скрипт заново."
        System.Windows.Forms.MessageBox.Show(self.message)
