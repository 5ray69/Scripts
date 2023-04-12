# -*- coding: utf-8 -*
# module my_sort.py

def my_sort_group(list_af):
    my_dict = {}
    my_dict['гр.'] = []
    my_dict['гр.А'] = []

    for stri in list_af:
        if 'А' in stri:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            # если список цифр не пуст
            if let_dig:
                my_dict['гр.А'].append(int(''.join(let_dig)))
            # если в строке нет цифр, отбросили гр. и доавили в словарь
            else:
                my_dict['гр.А'].append(stri[3:])
        else:
            let_dig = []
            for let in stri:
                if let.isdigit():
                    let_dig.append(let)
            # если список цифр не пуст
            if let_dig:
                my_dict['гр.'].append(int(''.join(let_dig)))
            else:
                my_dict['гр.'].append(stri[3:])

    sort_list = []
    # если список не пуст
    if my_dict['гр.А']:
        for int_el in sorted(my_dict['гр.А']):
            sort_list.append('гр.' + str(int_el) + 'А')
    if my_dict['гр.']:
        for int_el in sorted(my_dict['гр.']):
            sort_list.append('гр.' + str(int_el))

    return sort_list
