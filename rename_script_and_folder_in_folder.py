# -*- coding: utf-8 -*
import os
import clr

# это путь к каталогу, в котором будем менять имена
# сам файл запускаем из любого другого каталога
path = r"C:\1 ИНЖИНИРИНГ\ОБЪЕКТЫ\1"
# сделали каталог текущим (изменили текущий рабочий каталог на path)
os.chdir(path)
# что меняем
search_for = "WP"

# на что меняем
reaplace_to = "ZZ"

# работает только для имен файлов и папок в корневом каталоге,
# файлы содержащиеся в этих переименованных папках переименованы не будут
for f in os.listdir(path):
    # если строка поиска для замены содержится в имени, иначе не сработает
    if search_for in f:
        # отделили имя от точки с расширением
        file_name, file_ext = os.path.splitext(f)
        # print(file_name.replace(search_for, reaplace_to))
        new_name = file_name.replace(search_for, reaplace_to)
        os.rename(f, new_name)
