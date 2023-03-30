# module elements
# -*- coding: utf-8 -*
import clr
from Autodesk.Revit import DB
from iterfunctions import flatten
clr.AddReference('RevitAPI')


doc = __revit__.ActiveUIDocument.Document  # noqa


def get_type_name(element):  # получаем имя типоразмера в виде строки
    if hasattr(element, 'GetTypeId'):
        element_type = doc.GetElement(element.GetTypeId())
        return element_type.Parameter[
            DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsString()  # значение параметра "Имя типа"


def is_of_type(element, type_name):
    return type_name == get_type_name(element)


def group_by_key(elements, key_type='Type'):
    elements = flatten(elements)
    element_groups = {}
    for element in elements:
        if key_type == 'Type':
            key = type(element)
        elif key_type == 'Category':
            for key in DB.BuiltInCategory.GetValues(DB.BuiltInCategory):
                if int(key) == element.Category.Id.IntegerValue:
                    break
        else:
            key = 'Unknown Key'
        if key not in element_groups:
            element_groups[key] = []
        element_groups[key].append(element)
    return element_groups