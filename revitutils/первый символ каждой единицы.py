# module v4.2.6_test.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

import sys
sys.path += [
    r"C:\1 ИНЖИНИРИНГ\folderVSCode\3.1.3_Filterelementcollector",
]

doc = __revit__.ActiveUIDocument.Document  # noqa

# Есть только символ единицы (symbol of the unit ) и название единицы (name of the unit).
# У некоторых единиц может быть несколько символов, например у футов ft, ' (фут, штрих)


# Вы можете получить возможные символы единиц unit symbols для каждой спецификации Spec с помощью 
# параметров формата Format options этой спецификации Spec, как показано в приведенном ниже коде:

# чтобы увидеть текст символа для каждой единицы, у которой он есть:
for unit in DB.UnitUtils.GetAllUnits():  # Получаем идентификаторы ForgeTypeId всех доступных единиц и итерируем по одному
    # print unit.TypeId  # идентификаторы ForgeTypeId - длинная строка, описывающая единицу измерения
    for symbol in DB.FormatOptions.GetValidSymbols(unit):  # Получаем идентификатор ForgeTypeId символов для данной единицы и итерируем по одному
        # print unit  # объект ForgeTypeId единиц
        # print symbol  # объект ForgeTypeId символов и там и тут объекты ForgeTypeId, но видимо чем-то разные
        if not symbol.Empty():
            if DB.LabelUtils.GetLabelForSymbol(symbol) == 'мм':
                print DB.LabelUtils.GetLabelForSymbol(symbol)  # получили краткий символ, обозначение единиц измерения (например, мм)
            # print DB.LabelUtils.GetLabelForSpec(Spec)  # получили краткий символ, обозначение единиц измерения (например, мм)
        # print '***************************************'
    # print 'end оne unit'

# Методы класса LabelUtils позволяют вам обменивать идентификатор ForgeTypeId единицы,
# символа или спецификации на понятное имя этого элемента, отображаемое в пользовательском интерфейсе

#  Все значения длины всегда хранятся в жестко заданных единицах измерения длины внутренней базы данных, которые являются британскими футами
#  Британских фут (1фут = 0,304799472 метра). Футы бывают разные. 


# Бывают разные объекты ForgeTypeId:
# ForgeTypeId идентификатор единиц unitTypeId       класс Autodesk.Revit.DB.UnitTypeId (похоже, что это системные единицы)
# ForgeTypeId идентификатор символов symbolTypeId   класс Autodesk.Revit.DB.SymbolTypeId (символы единиц, например, мм, см, дм, м)
# ForgeTypeId идентификатор спецификаций specTypeId класс Autodesk.Revit.DB.SpecTypeId (похоже, что это единицы назначенные пользователем)

# doc.GetUnits() - получаем единицы проекта


# Вы можете перебирать спецификации в классе SpectTypeId (через отражение),
# создавать FormatOptions во время каждой итерации, а затем получать символы 
# для каждого через FormatOptions.GetValidSymbols.





                        # foreach (ForgeTypeId unit in UnitUtils.GetAllUnits())
                        # {
                        #    foreach (ForgeTypeId symbol in FormatOptions.GetValidSymbols(unit))
                        #    {
                        #       if (!symbol.Empty())
                        #       {
                        #          TaskDialog.Show(unit.TypeId, LabelUtils.GetLabelForSymbol(symbol));
                        #          break;
                        #       }
                        #    }
                        # }
