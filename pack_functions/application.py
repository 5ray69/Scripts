# module application.py
# -*- coding: utf-8 -*-
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB, UI

def get_external_definition(app, group_name, definition_name):
    return app.OpenSharedParameterFile() \
        .Groups[group_name] \
        .Definitions[definition_name]


def close_inactive_docs(uiapp, save_modified=False, close_ui_docs=False):
    '''
    Закрыть все документы Revit, кроме текущего активного.
    save_modified - сохранять изменения в файлах
    close_ui_docs - закрывать документы, открытые в пользовательском интерфейсе (close_ui_docs=True)
    то есть при close_ui_docs=True закроются все открые нами документы, кроме активного
        (по умолчанию закрываются только документы, открытые в фоновом режиме (close_ui_docs=False))
    '''
    # перебераем по очереди все открытые документы revit
    for doc in uiapp.Application.Documents:
        # если это не текущий открытый в польз интерфесе документ
        if doc != uiapp.ActiveUIDocument.Document:
            if not close_ui_docs and UI.UIDocument(doc).GetOpenUIViews():
                continue
            name = doc.Title
            doc.Close(save_modified)
            print 'Closed: {}'.format(name)
