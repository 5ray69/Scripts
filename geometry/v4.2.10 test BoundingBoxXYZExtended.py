# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

from geometry.boundingbox import BoundingBoxXYZExtended
from geometry.align import Align

uiapp = __revit__                            # noqa
app = __revit__.Application                  # noqa
uidoc = __revit__.ActiveUIDocument           # noqa
doc = __revit__.ActiveUIDocument.Document    # noqa

# Коды тестирующие созданный класс BoundingBoxXYZExtended

b_box = BoundingBoxXYZExtended.by_bounding_box(
    DB.BoundingBoxXYZ()
)
print '{} x {} x {}'.format(b_box.length,
                            b_box.width,
                            b_box.height)
print 'Min: {}\nCenter: {}\nMax: {}\nOrigin: {}'.format(b_box.Min,
                                                        b_box.center,
                                                        b_box.Max,
                                                        b_box.origin)

# # результаты
# 200.0 x 200.0 x 200.0
# Min: (-100.000000000, -100.000000000, -100.000000000)
# Center: (0.000000000, 0.000000000, 0.000000000)
# Max: (100.000000000, 100.000000000, 100.000000000)
# Origin: (0.000000000, 0.000000000, 0.000000000)

# b_box = BoundingBoxXYZExtended(10, 5, 2)
# b_box.length = 50
# b_box.width = 25
# b_box.height = 10
# b_box.align(0, Align.START)
# b_box.align(1, Align.CENTER)
# b_box.align(2, Align.END)
# b_box.origin = DB.XYZ(5000, 2000, 1000)
# print '{} x {} x {}'.format(b_box.length,
#                             b_box.width,
#                             b_box.height)
# print 'Min: {}\nCenter: {}\nMax: {}\nOrigin: {}'.format(b_box.Min,
#                                                         b_box.center,
#                                                         b_box.Max,
#                                                         b_box.origin)
# # результаты
# 50.0 x 25.0 x 10.0
# Min: (0.000000000, -12.500000000, -10.000000000)
# Center: (25.000000000, 0.000000000, -5.000000000)
# Max: (50.000000000, 12.500000000, 0.000000000)
# Origin: (5000.000000000, 2000.000000000, 1000.000000000)


# b_box = BoundingBoxXYZExtended(10, 5, 2)
# print '{} x {} x {}'.format(b_box.length,
#                             b_box.width,
#                             b_box.height)
# print 'Min: {}\nMax: {}'.format(b_box.Min,
#                                 b_box.Max)
# # результаты
# 10.0 x 5.0 x 2.0
# Min: (-5.000000000, -2.500000000, -1.000000000)
# Max: (5.000000000, 2.500000000, 1.000000000)




# b_box = BoundingBoxXYZExtended()
# print '{} x {} x {}'.format(b_box.length,
#                             b_box.width,
#                             b_box.height)
# print 'Min: {}\nMax: {}'.format(b_box.Min,
#                                 b_box.Max)
# # результаты
# 1.0 x 1.0 x 1.0
# Min: (-0.500000000, -0.500000000, -0.500000000)
# Max: (0.500000000, 0.500000000, 0.500000000)
