# module sort_names_levels.py
# -*- coding: utf-8 -*-

def my_sort_names_levels(list_names_levels):
    my_dict = {}
    my_dict['LU'] = []
    my_dict['L'] = []
    my_dict['LT'] = []
    my_dict['LR'] = []

    for stri in list_names_levels:
        if 'U' in stri:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            # если список цифр не пуст
            if let_dig:
                my_dict['LU'].append(int(''.join(let_dig)))
            # если в строке нет цифр, отбросили LU и доавили в словарь
            else:
                my_dict['LU'].append(stri[2:])

        if all(y not in stri for y in ('U','T','R')):
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            # если список цифр не пуст
            if let_dig:
                my_dict['L'].append(int(''.join(let_dig)))
            # если в строке нет цифр, отбросили LU и доавили в словарь
            else:
                my_dict['L'].append(stri[2:])

        if 'T' in stri:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            # если список цифр не пуст
            if let_dig:
                my_dict['LT'].append(int(''.join(let_dig)))
            # если в строке нет цифр, отбросили LT и доавили в словарь
            else:
                my_dict['LT'].append(stri[2:])

        if 'R' in stri:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            # если список цифр не пуст
            if let_dig:
                my_dict['LR'].append(int(''.join(let_dig)))
            # если в строке нет цифр, отбросили LR и доавили в словарь
            else:
                my_dict['LR'].append(stri[2:])

    sort_list = []
    # если список не пуст
    if my_dict['LU']:
        for int_el in sorted(my_dict['LU']):
            sort_list.append('LU' + str(int_el))
        sort_list.append('')

    if my_dict['L']:
        for int_el in sorted(my_dict['L']):
            # доставляем "0", чтобы получить 4 разряда
            sort_list.append('L' + str(int_el).rjust(4, "0"))
        sort_list.append('')

    if my_dict['LT']:
        for int_el in sorted(my_dict['LT']):
            sort_list.append('LT' + str(int_el))
        sort_list.append('')

    if my_dict['LR']:
        for int_el in sorted(my_dict['LR']):
            sort_list.append('LR' + str(int_el))

    return sort_list
