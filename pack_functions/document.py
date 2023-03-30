# module document.py
# -*- coding: utf-8 -*
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC

# from os import path
# from math import atan2
# from decorators import transaction
# from selections import get_element_by_name, get_f_symbol_by_name
import os
from iterfunctions import flatten, to_list


# если False, то создается InstanceBinding, а если True = TypeBinding
def create_parameter_binding(
        doc,
        categories,
        is_type_binding=False):
    app = doc.Application
    category_set = app.Create.NewCategorySet()  # создали пустой CategorySet
    for category in to_list(categories):
        if isinstance(category, DB.BuiltInCategory):
            category = DB.Category.GetCategory(doc, category)  # получаем объект Category, соответствующий идентификатору BuiltInCategory
        category_set.Insert(category)  # добавляем в пустой CategorySet по одной категории
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
            parameter_element = doc.GetElement(internal_definition.Id)
            if isinstance(parameter_element, DB.SharedParameterElement) and \
                    parameter_element.GuidValue == external_dafinition.GUID:
                return internal_definition


def get_built_in_category(category):
    for b_category in DB.BuiltInCategory.GetValues(DB.BuiltInCategory):
        if int(b_category) == category.Id.IntegerValue:
            return b_category


# основное назначение создаваемого класса - дать понять программе,
# сохранять или нет общие координаты связанного файла при его выгрузке,
# если вдруг они были изменены.
class SaveSharedCoordinatesCallback(DB.ISaveSharedCoordinatesCallback):
    '''Класс позволяющий указать, сохранять ли общие координаты
    связи при ее выгрузке (в том случае, если они были изменены)'''
    def __init__(self, save_options):
        super(SaveSharedCoordinatesCallback, self).__init__()
        self._save_options = save_options

    def GetSaveModifiedLinksOption(self, link):
        return self._save_options


# Класс указывающий программе что делать, если мы загружаем семейство
# в проект, а оно там уже существует
    # или возвращаем обратно семейство после изменений в исходный документ Ревита
    # f_doc.LoadFamily(doc, FamilyLoadOptions())  # значения параметров перезаписываются
    # f_doc.LoadFamily(doc, FamilyLoadOptions(False))  # значения параметров не перезаписываются
class FamilyLoadOptions(DB.IFamilyLoadOptions):
    def __init__(self, overwrite_parameters=True):
        super(FamilyLoadOptions, self).__init__()
        self._overwrite_parameters = overwrite_parameters

    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues.Value = self._overwrite_parameters
        return True


# 4.5.11
def create_and_load_profile(
        doc,
        profile_curves,
        family_path,
        overwrite_existing_file=True,
        family_template_path=None):
    '''На основе переданных кривых создает семейство профиля, сохраняет его
    в указанную директорию и загружает в документ'''
    if family_template_path is None:
        root = r'C:\ProgramData\Autodesk\RVT 2022\Family Templates\Russian'
        family_template_name = 'Метрическая система, профиль.rft'
        family_template_path = os.path.join(root, family_template_name)
    f_doc = doc.Application.NewFamilyDocument(family_template_path)
    with DB.Transaction(f_doc, 'Create Profile Curves') as t:
        t.Start()
        for curve in to_list(profile_curves):
            f_doc.FamilyCreate.NewDetailCurve(
                FEC(f_doc).OfClass(DB.ViewPlan).FirstElement(),
                curve
            )
        t.Commit()
    save_as_options = DB.SaveAsOptions()
    save_as_options.OverwriteExistingFile = overwrite_existing_file
    save_as_options.PreviewViewId = FEC(f_doc).OfClass(DB.ViewPlan) \
                                              .FirstElementId()
    f_doc.SaveAs(family_path, save_as_options)
    f_doc.Close()
    family = clr.Reference[DB.Family]()
    doc.LoadFamily(
        family_path,
        FamilyLoadOptions(),
        family
    )
    for type_id in family.GetFamilySymbolIds():
        return doc.GetElement(type_id)
