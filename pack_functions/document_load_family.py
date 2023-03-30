# module document.py
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit import DB

from os import path
from math import atan2
from decorators import transaction
from selections import get_element_by_name, get_f_symbol_by_name
from iterfunctions import flatten, to_list


# @transaction('Load Family')
def load_family(doc, family_path):
    return doc.LoadFamily(family_path)


def f_instance_by_transform(
        doc,
        f_symbol,
        transform,
        structural_type=DB.Structure.StructuralType.NoneStructural):
    if not f_symbol.IsActive:
        f_symbol.Activate()
    origin = transform.Origin
    f_instance = doc.Create.NewFamilyInstance(
        origin, f_symbol, structural_type)
    basis_x = transform.basis_X
    angle = atan2(basis_x.Y, basis_x.X)
    f_instance.Location.Rotate(
        DB.Line.CreateUnbound(origin, DB.XYZ.BasisZ),
        angle
    )
    return f_instance


@transaction('Gizmo Creation')
def gizmo_by_element(
        doc,
        elements,
        gizmo_path=r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector\Gizmo_2020\Gizmo.rfa"):
    name = path.splitext(path.basename(gizmo_path))[0]
    if get_element_by_name(doc, name, DB.Family) is None:
        load_family(doc, gizmo_path)
    f_symbol = get_f_symbol_by_name(
        doc,
        get_element_by_name(doc, name, DB.Family),
        name
    )
    instances = []
    for element in flatten(elements):
        if hasattr(element, 'GetTransform'):
            instances.append(f_instance_by_transform(
                doc,
                f_symbol,
                element.GetTransform()
            ))
    return instances


def create_parameter_binding(
        doc,
        categories,
        is_type_binding=False):
    app = doc.Application
    category_set = app.Create.NewCategorySet()
    for category in to_list(categories):
        if isinstance(category, DB.BuiltInCategory):
            category = DB.Category.GetCategory(doc, category)
        category_set.Insert(category)
    if is_type_binding:
        return app.Create.NewTypeBinding(category_set)
    return app.Create.NewInstanceBinding(category_set)


def create_project_parameter(
        doc,
        external_dafinition,
        binding,
        p_group=DB.BuiltInParameterGroup.INVALID):
    if doc.ParameterBindings.Insert(external_dafinition, binding, p_group):
        iterator = doc.ParameterBindings.ForwardIterator()
        while iterator.MoveNext():
            internal_definition = iterator.Key
            if internal_definition.Name == external_dafinition.Name:
                return internal_definition
