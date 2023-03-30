import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

from iterfunctions import flatten


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