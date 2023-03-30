# module revitutils
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB



def unit_converter(
        doc,
        value,
        to_internal=False,
        unit_type=DB.SpecTypeId.Length,  # тип единиц (объект класса ForgeTypeId())
        number_of_digits=None):  # возможность округления до целого числа или десятичных знаков
    display_units = doc.GetUnits().GetFormatOptions(
        unit_type).GetUnitTypeId()  # получили объект ForgeTypeId
    method = DB.UnitUtils.ConvertToInternalUnits if to_internal \
        else DB.UnitUtils.ConvertFromInternalUnits
    if number_of_digits is None:
        return method(value, display_units)
    elif number_of_digits > 0:
        return round(method(value, display_units), number_of_digits)
    return int(round(method(value, display_units), number_of_digits))

# ConvertToInternalUnits Method (Double, ForgeTypeId)

# s = UnitUtils.ConvertFromInternalUnits(dMinYieldStress, UnitTypeId.KipsPerSquareInch) в UnitTypeId нету длины, видимо нужен какой-то другой класс

            # # module revitutils.py
            # import clr
            # clr.AddReference('RevitAPI')
            # from Autodesk.Revit import DB

            # def unit_conventer(
            #         doc,
            #         value,
            #         to_internal=False,
            #         unit_type=DB.UnitType.UT_Length,
            #         number_of_digits=None):

            #     display_units = doc.GetUnits().GetFormatOptions(unit_type).DisplayUnits
            #     method = DB.UnitUtils.ConvertToInternalUnits if to_internal \
            #         else DB.UnitUtils.ConvertFromInternalUnits
            #     if number_of_digits is None:
            #         return method(value, display_units)
            #     elif number_of_digits > 0:
            #         return round(method(value, display_units), number_of_digits)
            #     return int(round(method(value, display_units), number_of_digits))

#             var dut = new Autodesk.Revit.DB.ForgeTypeId(forgeUnit);
#             var result = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits(value, dut);

# требуется ForgeTypeId, получен параметр FormatOptions


                    # unit_type=DB.SpecTypeId.Length
                    # print unit_type
                    # display_units = doc.GetUnits().GetFormatOptions(unit_type)  
                    # print display_units

                    # Результаты:
                    # >>> 
                    # ﻿<Autodesk.Revit.DB.ForgeTypeId object at 0x0000000000000030 [Autodesk.Revit.DB.ForgeTypeId]>
                    # <Autodesk.Revit.DB.FormatOptions object at 0x0000000000000031 [Autodesk.Revit.DB.FormatOptions]>
                    # >>> 


                # unitTypeId не является идентификатором единицы. См. разделы UnitUtils.IsUnit (ForgeTypeId) и UnitUtils.GetUnitTypeId (DisplayUnitType).
