# module decorators.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

# прочие импорты модуля

def transaction(t_name='Transaction'):
    """
    First argument of decorated function must be
    instance of Autodesk.Revit.DB.Document type
    """
    def decorator(func):
        def wrapper(doc, *args, **kwargs):
            with DB.Transaction(doc, t_name) as t:
                t.Start()
                fucn_call = func(doc, *args, **kwargs)
                t.Commit()
            return fucn_call
        return wrapper
    return decorator

# остальные функции модуля