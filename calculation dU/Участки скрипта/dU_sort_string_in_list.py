# -*- coding: utf-8 -*
# dU_sort_string_in_list

# функция преобразует в целое число цифры из строки
# для строк типа "гр.11А", "гр.5"
def int_in_string(string):
    if 'А' in string:
        return int(string[3:len(string)-1])
    if 'А' not in string:
        return int(string[3:len(string)])

lt_s = IN[0]

# сортируем список по двум критериям
# первый - по содержанию 'А' в строке
# второй - по целым числам в строке (выбрали из строки из сделали целыми числами)
OUT = sorted(lt_s, key=lambda string: ('А' in string, int_in_string(string)))


# def int_in_string(string):
#     if 'А' in string:
#         return int(string[3:len(string)-1])
#     if 'А' not in string:
#         return int(string[3:len(string)])


# lt_s = ["гр.3", "гр.1А", "гр.1", "гр.11А", "гр.5", "гр.4", "гр.17А", "гр.20", "гр.16А", "гр.22", "гр.7А", "гр.18А", "гр.22А", "гр.41"]

# # b = sorted(a, key=lambda t: (t[1], -t[0]))

# L_s = []
# for str_l in lt_s:
#        L_s.append(int_in_string(str_l))


# b = sorted(lt_s, key=lambda string: ('А' in string, int_in_string(string)))

# bprint(b)
