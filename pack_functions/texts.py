# -*- coding: utf-8 -*
# module texts.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from System.Collections.Generic import List
from Autodesk.Revit.UI import Selection as SEL  # для работы класса CategoriesSelectionFilter
from iterfunctions import to_list  # для работы класса CategoriesSelectionFilter

def raplace_letter(strin):
    return strin.replace('ЩЭ', 'М').replace('Л', 'М').replace('ВП', 'М').replace('ВВ', 'М').replace('ВН', 'М').replace('ВЗ', 'М').replace('НХ', 'М').replace('НП', 'М').replace('НТ', 'М').replace('ГК', 'М')

def my_sort(list_af):
    my_dict = {}
    my_dict['М'] = []
    my_dict['гр.'] = []
    my_dict['гр.А'] = []

    for stri in list_af:
        if 'М' in stri:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            my_dict['М'].append(int(''.join(let_dig)))

        if 'гр.' in stri and 'А' not in stri:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            my_dict['гр.'].append(int(''.join(let_dig)))

        if 'гр.' in stri and 'А' in stri:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            my_dict['гр.А'].append(int(''.join(let_dig)))

    sort_list = []
    # если список не пуст
    if my_dict['М']:
        for int_el in sorted(my_dict['М']):
            sort_list.append('М' + str(int_el))
    if my_dict['гр.']:
        for int_el in sorted(my_dict['гр.']):
            sort_list.append('гр.' + str(int_el))
    if my_dict['гр.А']:
        for int_el in sorted(my_dict['гр.А']):
            sort_list.append('гр.' + str(int_el) + 'А')

    return sort_list

