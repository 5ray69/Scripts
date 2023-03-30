# module geometry.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

from iterfunctions import to_list
from decorators import transaction


#  get_all_solids получение солидов без солидов вложенных семейств
def get_all_solids(element, g_options, solids=None):
    if solids is None:
        solids = []
    if hasattr(element, 'Geometry'):
        for item in element.Geometry[g_options]:
            get_all_solids(item, g_options, solids)
    elif isinstance(element, DB.GeometryInstance):
        for item in element.GetInstanceGeometry():
            get_all_solids(item, g_options, solids)
    elif isinstance(element, DB.Solid):
        solids.append(element)
    return solids

# #  get_all_solids c получением солидов вложенных семейств
# def get_all_solids(element, g_options, solids=None):
#     if solids is None:
#         solids = []
#     if hasattr(element, "Geometry"):
#         for item in element.Geometry[g_options]:
#             get_all_solids(item, g_options, solids)
#     elif isinstance(element, DB.GeometryInstance):
#         for item in element.GetInstanceGeometry():
#             get_all_solids(item, g_options, solids)
#     elif isinstance(element, DB.Solid):
#         solids.append(element)
#     if isinstance(element, DB.FamilyInstance):
#         for item in element.GetSubComponentIds(): #  получаем вложенные семейства
#             family_instance = element.Document.GetElement(item)
#             get_all_solids(family_instance, g_options, solids)
#     return solids


# 3.4.10
@transaction('Create Direct Shape')
def create_direct_shape(
        doc,
        geometry_objects,
        category_id=DB.ElementId(DB.BuiltInCategory.OST_GenericModel)):
    direct_shape = DB.DirectShape.CreateElement(
        doc, category_id)  # создали объект DirectShape, чтоб создание было полным нужно применить свойство с геометрией
    direct_shape.SetShape(to_list(
        geometry_objects, DB.GeometryObject))  # присвоение созданному объекту DirectShape корректной геометрии
    return direct_shape  # возвращает созданный объект DirectShape


# 4.4.7
def get_min_max(points):
    '''Функция извлекает из переданных в нее точек минимальное (максимальное)
    значение по каждой из трех глобальных осей координат и использует их для
    создания точек минимума и максимума'''
    pt_min = DB.XYZ(
        *(
            min(point[i] for point in points)
            for i in range(3)
        )
    )
    pt_max = DB.XYZ(
        *(
            max(point[i] for point in points)
            for i in range(3)
        )
    )
    return pt_min, pt_max


# 4.5.9
# Суть работы функции довольно проста. Исходный массив линий разбивается на первую и последующие.
# Первая добавляется в цепь (становится первым ее элементом). И далее мы перебираем все оставшиеся
# линии и проверяем, не совпадает ли начало или конец какой-либо из них с конечной точкой последнего
# элемента цепи. Если такая кривая находится, мы присоединяем ее к цепи.
# В случае, если вдруг с концом кривой совпадает другой конец, а не начало - мы создаем
# перевернутую версию линии через метод CreateReversed (тем самым меняя местами точки начала и конца кривой).
# Далее функция отправляется на следующую ветвь рекурсии и выполняется подбор следующего элемента цепи.
# Происходить это будет до тех пор, пока среди исходных кривых не перестанут находиться линии, совпадающие
# с конечным элементом цепи.
# Поскольку в нашем случае заранее известно, что контур замкнут, мы в итоге полностью "пересоберем" массив кривых,
# но только теперь все они будут располагаться в правильном порядке и конец каждой предыдущей линии
# будет совпадать с началом следующей.
def create_chain_of_curves(curves, curve_chain=None):
    '''Формирует последовательную цепочку(chain) из исходных кривых'''
    if not isinstance(curves, list):
        curves = list(curves)
    if curve_chain is None:
        curve_chain = DB.CurveArray()
        curve_chain.Append(curves.pop())
    if curves:
        for curve in curves:
            end_point = curve_chain[curve_chain.Size - 1].GetEndPoint(1)
            points_check = [curve.GetEndPoint(i).IsAlmostEqualTo(end_point)
                            for i in range(2)]
            if any(points_check):
                curves.remove(curve)
                curve = curve.CreateReversed() if points_check[1] else curve
                curve_chain.Append(curve)
                create_chain_of_curves(curves, curve_chain)
    return curve_chain


# 4.5.10
# UV координаты задаются экземпляром класса UV, у которого также, как у класса XYZ,
# есть статические свойства, возвращающие начало UV координат и базисные вектора.
# Ну а чтобы получить с помощью этих координат точку (объект XYZ) на конкретной грани,
# выполняется вызов метода Evaluate.
# Параметры u_scale и v_scale опциональны и позволяют изменить масштаб вектора, задающего
# одно из направлений UV координат. Нам это потребуется для того, чтобы понять,
# где же все-таки у нас направление U, а где V.
# Точки возвращаются в виде объектов Point, а не XYZ, поскольку именно данный тип можно
# передать в метод по созданию объектов DirectShape.
def get_face_uv_basises_as_points(face, u_scale=1, v_scale=None):
    '''
    Получает точки, показывающие направление осей U и V
    и точку начала UV координат грани. Результат возвращается
    в виде объектов класса Point.
    u_scale, v_scale - масштабы базисных векторов (по умолчанию - 1)
    '''
    if v_scale is None:
        v_scale = u_scale
    return [
        DB.Point.Create(face.Evaluate(uv))
        for uv in [DB.UV.Zero,
                   DB.UV.BasisU * u_scale,
                   DB.UV.BasisV * v_scale]
    ]


# 4.5.10
# ее назначение - определить на грани точку с минимальными значениями U и V.
# И построить сетку из объектов Point с определенным шагом UV координат
# (для плоских граней величина шага по умолчанию 1 фут как по U так и по V)
# (для криволинейных граней величина шага нормализована и мы не получим сетку,
# если не начнем указывать шаг сетки меньше единицы)
# в положительном направлении осей U и V. Таким образом мы сможем наглядно
# увидеть распределение UV координат на той или иной грани:
def get_face_uv_grid_as_points(face, u_step=1, v_step=None):
    '''Функция берет на грани точку с минимальным значением U и V
    и строит от нее сетку из объектов Point с заданным шагом UV координат.
    u_step, v_step - шаги сетки вдоль осей U и V '''
    if v_step is None:
        v_step = u_step
    # метод GetBoundingBox класса Face, возвращает особый объект BoundingBoxUV,
    # представляющий из себя как бы двумерный габаритный ящик той или иной грани
    min_max_uv = [face.GetBoundingBox().Bounds[i] for i in range(2)]
    min_u, max_u = [uv.U for uv in min_max_uv]
    min_v, max_v = [uv.V for uv in min_max_uv]
    u_values, v_values = [], []
    while min_u < max_u:
        u_values.append(min_u)
        min_u += u_step
    else:
        u_values.append(max_u)
    while min_v < max_v:
        v_values.append(min_v)
        min_v += v_step
    else:
        v_values.append(max_v)
    return [
        DB.Point.Create(face.Evaluate(DB.UV(u, v)))
        for u in u_values
        for v in v_values
    ]


# 4.5.10
# Позволяет получить геометрию нормали в той или иной точке грани.
# По умолчанию точка в середине грани и из нее нормаль.
# Нормаль грани твердого тела (солида), направлена наружу тела, а грани тела вычитания (не солида) - внутрь тела
# Возвращаемую данной функцией геометрию можно использовать для создания
# объектов DirectShape, чтобы визуально посмотреть направление нормали:
def get_face_normal_as_geometry(face, normal_uv=None, line_length=1):
    '''
    Возвращает геометрию, показывающую направление нормали грани
    в виде объектов Point (начало нормали) и Line (направление нормали).
    line_length - длина линии
    normal_uv - UV коодинаты точки на грани, из которой будет получена
    геометрия нормали. По умолчанию берется среднее значение UV между
    минимальным и максимальным для грани.
    '''
    if normal_uv is None:
        face_uv_bounds = [face.GetBoundingBox().Bounds[i] for i in range(2)]
        normal_uv = DB.UV(
            sum(uv.U for uv in face_uv_bounds) / 2,
            sum(uv.V for uv in face_uv_bounds) / 2
        )
    line_start = face.Evaluate(normal_uv)
    return DB.Point.Create(line_start), DB.Line.CreateBound(
        line_start, line_start + face.ComputeNormal(normal_uv) * line_length)


# 4.5.10
# Позволяет получить начальную или конечную грань тела выдавливания.
# Т.е. ту грань, которая совпадает по контуру с профилем выдавливания.
# На самом деле, в Revit API есть специальный класс ExtrusionAnalyzer, с помощью
# которого можно проанализировать тот или иной объект Solid на предмет того,
# является ли он телом, похожим на тело выдавливания. И в том числе попытаться получить
# начальную грань профиля выдавливания через метод GetExtrusionBase. Можно было бы, конечно,
# воспользоваться и им. Но, в данном случае, наша функция будет более универсальной, поскольку
# позволит получать не только начальную, но и конечную грань.
def get_extrusion_base_face(
        extrusion,
        index=0,
        compute_references=True):
    '''
    Получает начальную или конечную грань объекта Extrusion
    (т.е. грань, совпадающую по контуру с профилем тела выдавливания)
    extrusion - экземпляр класса Extrusion;
    index - положение грани:
        0 - начало выдавливания;
        1 - конец выдавливания;
    compute_references - указывает, можно ли получить объект Reference
    из грани, возвращаемой данной фукнцией.
    '''
    g_options = DB.Options()
    g_options.ComputeReferences = compute_references
    extrusion_direction = extrusion.Sketch.SketchPlane.GetPlane().Normal
    start_face_normal = -extrusion_direction if extrusion.IsSolid \
        else extrusion_direction
    if extrusion.EndOffset < extrusion.StartOffset:
        start_face_normal *= -1
    face_normals = [start_face_normal, -start_face_normal]
    for face in get_all_solids(extrusion, g_options)[0].Faces:
        if face.FaceNormal.IsAlmostEqualTo(face_normals[index]):
            return face
