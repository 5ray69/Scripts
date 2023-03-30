# -*- coding: utf-8 -*
# module selections.py
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit import DB
from Autodesk.Revit.DB import FilteredElementCollector as FEC
from System.Collections.Generic import List
from Autodesk.Revit.UI import Selection as SEL  # для работы класса CategoriesSelectionFilter
from iterfunctions import to_list  # для работы класса CategoriesSelectionFilter


def get_f_symbol_by_name(doc, family, symbol_name):
    for f_symbol_id in family.GetFamilySymbolIds(): #  позволяет получить из экземпляра семейства список Id его типоразмеров
        f_symbol = doc.GetElement(f_symbol_id)
#  имя типоразмера получаем по его параметру SYMBOL_NAME_PARAM, а не по свойству Name
        if f_symbol.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM] \
                .AsString() == symbol_name:
            return f_symbol


def get_line_pattern_id(doc, name='Solid'):
    for line_pattern in FEC(doc).OfClass(DB.LinePatternElement):
        if line_pattern.Name == name:
            return line_pattern.Id
    return DB.LinePatternElement.GetSolidPatternId()


# 4.2.4
def get_view_family_type(doc, view_family, type_name=None):
    for view_family_type in FEC(doc).OfClass(DB.ViewFamilyType):
        if all(
                (
                    view_family_type.ViewFamily == view_family,
                    type_name is None or view_family_type
                    .Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM]
                    .AsString() == type_name
                )):
            return view_family_type


# 4.2.10
def get_selected_elements(uidoc):
    '''Позволяет получить список выделенных элементов в интерфейсе Revit;
    uidoc - экземпляр класса UIDocument'''
    return [uidoc.Document.GetElement(element_id)
            for element_id in uidoc.Selection.GetElementIds()]


# 4.3.9
def get_element_by_name(
        doc,
        name,
        element_class,
        family_name=None,
        return_all_elements=False):
    '''
    Получение элементов Revit по имени
    doc - документ Revit
    name - имя элемента
    element_class - класс элементов (обязательно наследник от Element)
    family_name - имя семейства
    return_all_elements - вернуть все найденные элементы
        False - возвращается лишь первый найденный элемент
        True - возвращается полный список найденных элементов
    '''
    elements = []
    for element in FEC(doc).OfClass(element_class):
        if DB.Element.Name.GetValue(element) != name:  # позволяет получать имя как экземпляра семейства, так и его типоразмера
            continue
        if family_name is not None:
            element_type = element if isinstance(element, DB.ElementType) \
                else doc.GetElement(element.GetTypeId())
            element_family_name = element_type.FamilyName if element_type \
                else None
            if element_family_name != family_name:
                continue
        elements.append(element)
    if elements:
        return elements if return_all_elements else elements[0]

# эта функция с предыдущих модулей, и имеет тоже самое название, поэтому закомментена
# def get_element_by_name(doc, name, element_type=DB.Family):
#     for item in FEC(doc).OfClass(element_type):
#         if item.Name == name:
#             return item


class CategoriesSelectionFilter(SEL.ISelectionFilter):
    def __init__(self, b_categories):
        super(CategoriesSelectionFilter, self).__init__()
        self._category_ids = [DB.ElementId(b_category)
                              for b_category in to_list(b_categories)]

    def AllowElement(self, element):
        return element.Category.Id in self._category_ids


# 4.4.7
# убрали ключ 'transforms' из функции и получаем трансформацию
# каждый раз непосредственно из экземпляра связи (он остался в # 4.4.5)
def get_link_data(doc, link_name):
    '''Получение экземпляров, типа и докумена связанного файла имени'''
    # если строка (имя) не заканчивается на .rvt
    if not link_name.endswith('.rvt'):
        # добавляем к строке .rvt
        link_name += '.rvt'
    link_type = get_element_by_name(doc, link_name, DB.RevitLinkType)
    link_instances = [doc.GetElement(link_instance_id)
                      for link_instance_id in link_type.GetDependentElements(
                      DB.ElementClassFilter(DB.RevitLinkInstance))]
    # возвращает экземляры связей, трансформации связей, типоразмер связи и документ связи
    return{
        'instances': link_instances,
        'type': link_type,
        'doc': link_instances[0].GetLinkDocument()
    }

# предусмотрены 4 разных варианта расположения точек минимума и максимума
# (избегаем ошибки пользователя и увеличиваем гибкость использования)
def BoundingBoxXyzContains(bbmin_xyz, bbmax_xyz, point_xyz):
    '''
    Проверяем содержит ли BoundingBox точку
    bbmin_xyz - точка min BoundingBoxа
    bbmax_xyz - точка max BoundingBoxа
    point_xyz - точка, которую проверяем
    '''
    # bbmin_xyz в левом нижнем ближнем углу, bbmax_xyz в правом верхнем дальнем углу
    if bbmin_xyz.X < bbmax_xyz.X and bbmin_xyz.Y < bbmax_xyz.Y:
        if bbmin_xyz.X <= point_xyz.X <= bbmax_xyz.X and \
           bbmin_xyz.Y <= point_xyz.Y <= bbmax_xyz.Y and \
           bbmin_xyz.Z <= point_xyz.Z <= bbmax_xyz.Z:
            return True
    # bbmin_xyz в правом нижнем ближнем углу, bbmax_xyz в левом верхнем дальнем углу
    if bbmin_xyz.X > bbmax_xyz.X and bbmin_xyz.Y < bbmax_xyz.Y:
        if bbmin_xyz.X >= point_xyz.X >= bbmax_xyz.X and \
           bbmin_xyz.Y <= point_xyz.Y <= bbmax_xyz.Y and \
           bbmin_xyz.Z <= point_xyz.Z <= bbmax_xyz.Z:
            return True
    # bbmin_xyz в левом нижнем дальнем углу, bbmax_xyz в правом верхнем ближнем углу
    if bbmin_xyz.X < bbmax_xyz.X and bbmin_xyz.Y > bbmax_xyz.Y:
        if bbmin_xyz.X <= point_xyz.X <= bbmax_xyz.X and \
           bbmin_xyz.Y >= point_xyz.Y >= bbmax_xyz.Y and \
           bbmin_xyz.Z <= point_xyz.Z <= bbmax_xyz.Z:
            return True
    # bbmin_xyz в правом нижнем дальнем углу, bbmax_xyz в левом верхнем ближнем углу
    if bbmin_xyz.X < bbmax_xyz.X and bbmin_xyz.Y < bbmax_xyz.Y:
        if bbmin_xyz.X >= point_xyz.X >= bbmax_xyz.X and \
           bbmin_xyz.Y >= point_xyz.Y >= bbmax_xyz.Y and \
           bbmin_xyz.Z <= point_xyz.Z <= bbmax_xyz.Z:
            return True
    return False

# # 4.4.5
# def get_link_data(doc, link_name):
#     '''Получение экземпляров, типа и докумена связанного файла имени'''
#     # если строка (имя) не заканчивается на .rvt
#     if not link_name.endswith('.rvt'):
#         # добавляем к строке .rvt
#         link_name += '.rvt'
#     link_type = get_element_by_name(doc, link_name, DB.RevitLinkType)
#     link_instances = [doc.GetElement(link_instance_id)
#                       for link_instance_id in link_type.GetDependentElements(
#                       DB.ElementClassFilter(DB.RevitLinkInstance))]
#     # возвращает экземляры связей, трансформации связей, типоразмер связи и документ связи
#     return{
#         'instances': link_instances,
#         'transforms': [instance.GetTotalTransform()
#                        for instance in link_instances],
#         'type': link_type,
#         'doc': link_instances[0].GetLinkDocument()
#     }
