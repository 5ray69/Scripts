# Подскажите, а как получить у элемента не значение 
# имени категории (element.Category.Name), а значение BuiltInCategory ?


# Такого свойства у элемента нет. Но можно написать свою функцию
# и передавать в нее объект категории:


def get_built_in_category(category):
    for b_category in DB.BuiltInCategory.GetValues(DB.BuiltInCategory):
        if int(b_category) == category.Id.IntegerValue:
            return b_category
