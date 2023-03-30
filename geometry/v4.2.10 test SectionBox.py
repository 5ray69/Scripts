# module main.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

from geometry.sectionbox import SectionBoxXYZ
from geometry.boundingbox import BoundingBoxXYZExtended
from selections import get_view_family_type, get_selected_elements
from revitutils.unit import Unit

uidoc = __revit__.ActiveUIDocument         # noqa
doc = __revit__.ActiveUIDocument.Document  # noqa

# получили объект типоразмера вида, на основе которого будет создано сечение
view_family_type = get_view_family_type(
    doc,
    DB.ViewFamily.Section,
    'Building Section'
)

# получили выделенный в проекте элемент
element = get_selected_elements(uidoc)[0]

# получаем баундингбокс по геометрии типоразмера, которая всегда не повернута
# сразу же превратим полученный ящик в объект BoundingBoxXYZExtended:
for item in element.Geometry[DB.Options()]:
    if isinstance(item, DB.GeometryInstance):
        element_b_box = BoundingBoxXYZExtended.by_bounding_box(
            item.SymbolGeometry.GetBoundingBox()
        )

# получим точку размещения сечения. А также создадим переменную offset,
# которая будет увеличивать исходный размер сечений на некоторое значение,
# чтобы все сечения были чуть больше, чем сам элемент:
origin = element.GetTransform().OfPoint(element_b_box.center)
offset = Unit(doc, 1000).internal

# Все исходные данные получены и мы можем приступить к созданию ящиков сечений.
# Для наглядности поместим их в словарь.
# Размеры сечений извлекаются из габаритного ящика элемента. Ну а направление задается
# через его свойства FacingOrientation и HandOrientation

section_boxes = {
    'longitudinal': SectionBoxXYZ(
        element_b_box.length + offset,
        element_b_box.height + offset,
        element_b_box.width / 2 + offset,
        SectionBoxXYZ.VERTICAL,
        element.FacingOrientation,
        origin
    ),
    'cross': SectionBoxXYZ(
        element_b_box.width + offset,
        element_b_box.height + offset,
        element_b_box.length / 2 + offset,
        SectionBoxXYZ.VERTICAL,
        -element.HandOrientation,
        origin
    ),
    'horizontal': SectionBoxXYZ(
        element_b_box.length + offset,
        element_b_box.width + offset,
        element_b_box.height / 2 + offset,
        SectionBoxXYZ.HORIZONTAL_DOWN,
        element.HandOrientation,
        origin
    ),
}

# поочередно перебирая значения словаря, последовательно
# создадим три необходимых сечения:
with DB.Transaction(doc, 'Family Instance Sections') as t:
    t.Start()
    for section_box in section_boxes.values():
        DB.ViewSection.CreateSection(
            doc,
            view_family_type.Id,
            section_box
        )
    t.Commit()
