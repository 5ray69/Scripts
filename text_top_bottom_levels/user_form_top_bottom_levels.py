# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import System.Drawing
import System.Windows.Forms


class UserFormTopBottomLevels(System.Windows.Forms.Form):
    def __init__(self, dict_from_json):
        self.Text = "Перечислите номера групп исключаемых из стояка"
        self.BackColor = System.Drawing.Color.FromArgb(238, 238, 238)
        caption_height = System.Windows.Forms.SystemInformation.CaptionHeight
        self.MinimumSize = System.Drawing.Size(550, (800 + caption_height))
        self.CenterToScreen()

        self.dict_user_select = dict_from_json

        self._label_font = System.Drawing.Font(
                                        'Arial',
                                        System.Single(10.5),
                                        System.Drawing.FontStyle.Regular,
                                        System.Drawing.GraphicsUnit.Point)

        self._label_comment_stair = System.Windows.Forms.Label()
        self._label_comment_stair.Text = 'Укажите в строке ниже, номера групп,\
                                        \nкоторые ИДУТ ВНЕ СТОЯКА, например ПО ЛЕСТНИЦАМ.\
                                        \nЗапишите через запятую, без пробелов, в следующем виде: 1,12,1А,4,9А\
                                        \nСокращение гр. к каждой группе писать не надо, только номер.'
        self._label_comment_stair.Font = self._label_font
        self._label_comment_stair.Location = System.Drawing.Point(20, 5)
        self._label_comment_stair.Size = System.Drawing.Size(
            self._label_comment_stair.PreferredWidth, self._label_comment_stair.PreferredHeight)
        self.Controls.Add(self._label_comment_stair)

        self._text_box_stair = System.Windows.Forms.TextBox()
        self._text_box_stair.Location = System.Drawing.Point(20, 80)
        self._text_box_stair.Size = System.Drawing.Size(400, 200)
        self._text_box_stair.Font = System.Drawing.Font(self._text_box_stair.Font.FontFamily, 12)
        self.Controls.Add(self._text_box_stair)
        user_list_stair = self.dict_user_select["list_stair"]
        self._text_box_stair.Text = ','.join(user_list_stair).replace('гр.', '')

        self._label_info_stair = System.Windows.Forms.Label()
        self._label_info_stair.Text = '  Для напоминания.\
                                    \nОбычно в проектах вне стояка идут:\
                                    \nгр.1А - освещение лестничных переходов\
                                    \nгр.7А - освещение подъема на 1 этаж с подвала, СУВ\
                                    \nгр.9 - освещение входа с улицы в подвал, выключатель при входе\
                                    \nгр.9А - освещение освновной лестничной клетки\
                                    \nгр.11А - освещение освновной лестничной клетки\
                                    \nгр.15А - освещение дополнительной лестничной клетки\
                                    \nгр.16А - освещение дополнительной лестничной клетки'
        self._label_info_stair.Font = self._label_font
        self._label_info_stair.Location = System.Drawing.Point(40, 110)
        self._label_info_stair.Size = System.Drawing.Size(
            self._label_info_stair.PreferredWidth, self._label_info_stair.PreferredHeight)
        self.Controls.Add(self._label_info_stair)

        self.offset = 400

        self._label_exclude = System.Windows.Forms.Label()
        self._label_exclude.Text = 'Дополнительно, когда два стояка в здании.\
                                        \nИСКЛЮЧИТЬ ГРУППЫ ИЗ ПРАВОГО/ВТОРОГО СТОЯКА.\
                                        \nЗапишите через запятую, без пробелов, в следующем виде: 16,18\
                                        \nСокращение гр. к каждой группе писать не надо, только номер.'
        self._label_exclude.Font = self._label_font
        self._label_exclude.Location = System.Drawing.Point(20, 5 + self.offset)
        self._label_exclude.Size = System.Drawing.Size(
            self._label_exclude.PreferredWidth, self._label_exclude.PreferredHeight)
        self.Controls.Add(self._label_exclude)

        self._text_box_exclude = System.Windows.Forms.TextBox()
        self._text_box_exclude.Location = System.Drawing.Point(20, 80 + self.offset)
        self._text_box_exclude.Size = System.Drawing.Size(400,100)
        self._text_box_exclude.Font = System.Drawing.Font(self._text_box_stair.Font.FontFamily, 12)
        user_list_exclude = self.dict_user_select["delete_from_right_stoyak"]
        self._text_box_exclude.Text = ','.join(user_list_exclude).replace('гр.', '')
        self.Controls.Add(self._text_box_exclude)

        self._label_info_exclude = System.Windows.Forms.Label()
        self._label_info_exclude.Text = '  Для примера.\
                                    \nНапример, гр.16 - на первом этаже из-за сложного ветвления\
                                    \nпопала в баундингбокс, в то время как идет она в стояке,\
                                    \nкоторый вне баундингбокса'
        self._label_info_exclude.Font = self._label_font
        self._label_info_exclude.Location = System.Drawing.Point(30, 110 + self.offset)
        self._label_info_exclude.Size = System.Drawing.Size(
            self._label_info_exclude.PreferredWidth, self._label_info_exclude.PreferredHeight)
        self.Controls.Add(self._label_info_exclude)

        self.button_fonts = System.Drawing.Font(
                                'Arial',
                                System.Single(12),
                                System.Drawing.FontStyle.Bold,
                                System.Drawing.GraphicsUnit.Point)

        self._defin_button = System.Windows.Forms.Button()
        self._defin_button.Location = System.Drawing.Point(
                                        30, self.MinimumSize.Height - 120)
        self._defin_button.Size = System.Drawing.Size(230, 54)
        self._defin_button.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        self._defin_button.FlatAppearance.BorderSize = 0
        self._defin_button.Text = "Применить указанное"
        self._defin_button.Font = self.button_fonts
        self._defin_button.ForeColor = System.Drawing.Color.FromName('White')
        # цвет самой кнопки, ее заливка. Если не указывать прозрачность,
        # то он будет полностью непрозрачен
        self._defin_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
        self.button_fonts = self.button_fonts
        self._defin_button.Anchor = (
            System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)
        self.Controls.Add(self._defin_button)

        self._cancel_button = System.Windows.Forms.Button()
        self._cancel_button.Location = System.Drawing.Point(
                            self._defin_button.Location.X + 250, self.MinimumSize.Height - 120)
        self._cancel_button.Size = System.Drawing.Size(230, 54)
        self._cancel_button.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        self._cancel_button.FlatAppearance.BorderSize = 0
        self._cancel_button.Text = "Отмена"
        self._cancel_button.Font = self.button_fonts
        self._cancel_button.ForeColor = System.Drawing.Color.FromName('White')
        self._cancel_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
        self._cancel_button.Anchor = (
            System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)
        self.Controls.Add(self._cancel_button)

        # BIND EVENTS TO CONTROL
        # MouseEnter Событие, когда указатель мыши заходит в пределы элемента управления
        # MouseLeave происходит, когда указатель мыши покидает элемент управления
        self._defin_button.MouseEnter += self.define_button_mouse_enter
        self._defin_button.MouseLeave += self.define_button_mouse_leave

        self._cancel_button.MouseEnter += self.cancel_button_mouse_enter
        self._cancel_button.MouseLeave += self.cancel_button_mouse_leave

        self._defin_button.Click += self._click_on_define_button
        self._cancel_button.Click += self._click_on_cancel_button

    def _click_on_define_button(self, sender, args):
        dict_user = {}
        # удалили все пробелы из строки
        user_string_stair = self._text_box_stair.Text.replace(' ', '')
        # из строки сделали список строк и добавили в словарь
        dict_user["list_stair"] = ['гр.' + el_str for el_str in user_string_stair.split (',')]
        user_string_exclude = self._text_box_exclude.Text.replace(' ', '')
        dict_user["delete_from_right_stoyak"] = ['гр.' + elem_str for elem_str in user_string_exclude.split (',')]

        self.dict_user_select = dict_user

        self.Close()

    def _click_on_cancel_button(self, sender, args):
        self.Close()

    # DEFINE MOUSE ENTER EVENT
    def define_button_mouse_enter(self, sender, args):
        self._defin_button.ForeColor = System.Drawing.Color.FromName('White')
        self._defin_button.BackColor = System.Drawing.Color.FromArgb((int(255 * .02)), 60, 90, 100)

    def define_button_mouse_leave(self, sender, args):
        self._defin_button.ForeColor = System.Drawing.Color.FromName('White')
        self._defin_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)

    def cancel_button_mouse_enter(self, sender, args):
        self._cancel_button.ForeColor = System.Drawing.Color.FromName('White')
        self._cancel_button.BackColor = System.Drawing.Color.FromArgb((int(255 * .02)), 60, 90, 100)

    def cancel_button_mouse_leave(self, sender, args):
        self._cancel_button.ForeColor = System.Drawing.Color.FromName('White')
        self._cancel_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
