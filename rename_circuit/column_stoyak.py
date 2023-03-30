# -*- coding: utf-8 -*-

import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import System.Drawing
import System.Windows.Forms


class ColumnOneStoyak(System.Windows.Forms.Form):
    def __init__(self, owner, Name_stoyak, Number_stoyak, Offset_stoyak, Number_of_levels,
                Left_Point_ComboBox, Height_Point_ComboBox, Width_Size_ComboBox, Height_Size_ComboBox,
                Label_Offset, Width_Size_Label, Height_Size_Label, Dict_from_json):
        self.name_stoyak = Name_stoyak
        self.offset_stoyak = Offset_stoyak
        self.number_of_levels = Number_of_levels + 1

        self.left_Point_ComboBox = Left_Point_ComboBox
        self.height_Point_ComboBox = Height_Point_ComboBox
        self.width_Size_ComboBox = Width_Size_ComboBox
        self.height_Size_ComboBox = Height_Size_ComboBox

        self.label_Offset = Label_Offset 
        self.width_Size_Label = Width_Size_Label
        self.height_Size_Label = Height_Size_Label
        self.dict_from_json = Dict_from_json

        self.all_combobox = []

        for namber_int in range(1, self.number_of_levels):
            owner.combbox = System.Windows.Forms.ComboBox()
            owner.combbox.Parent = self
            owner.combbox.Location = System.Drawing.Point(
                self.left_Point_ComboBox + self.offset_stoyak, self.height_Point_ComboBox + namber_int * 27)
            owner.combbox.Size = System.Drawing.Size(self.width_Size_ComboBox, self.height_Size_ComboBox)
            owner.combbox.DropDownHeight = 250  # высота выпадающего списка из Combobox
            owner.combbox.ForeColor = System.Drawing.Color.FromName('Black')
            owner.combbox.FlatStyle = System.Windows.Forms.FlatStyle.Flat  # плоский стиль, не объемный
            owner.combbox.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList  # DropDownList - пользователь не может ввести новое значение
            owner.combbox.Font = System.Drawing.Font('Arial', System.Single(10.5))
            owner.combbox.Name = 'L' + str(namber_int).rjust(2, "0") + '00'
            # добавляем строку в выпадающий список, указывая индекс,
            # под которым она должна находиться в списке
            owner.combbox.Items.Insert(0, self.dict_from_json[Number_stoyak]['L' + str(namber_int).rjust(2, "0") + '00'])
            # указываем индекс, который будет выбран и помещен в combo box
            owner.combbox.SelectedIndex = 0
            owner.Controls.Add(owner.combbox)
            self.all_combobox.append(owner.combbox)

            # LOAD DROP DOWN LIST IN COMBO BOX
            for int_namber in range(1, self.number_of_levels):
                owner.combbox.Items.Add('M' + str(int_namber))

            owner.label_to_combobox = System.Windows.Forms.Label()
            owner.label_to_combobox.Text = 'L' + str(namber_int).rjust(2, "0") + '00'
            owner.label_to_combobox.Font = System.Drawing.Font('Arial', System.Single(11))
            owner.label_to_combobox.Location = System.Drawing.Point(
                self.left_Point_ComboBox + self.offset_stoyak - self.label_Offset, self.height_Point_ComboBox + 3 + namber_int * 27)
            owner.label_to_combobox.Size = System.Drawing.Size(self.width_Size_Label, self.height_Size_Label)
            owner.Controls.Add(owner.label_to_combobox)

        owner.label_chif_stoyak = System.Windows.Forms.Label()
        owner.label_chif_stoyak.Text = self.name_stoyak
        owner.label_chif_stoyak.Font = System.Drawing.Font(
            'Arial',
            System.Single(10.5),
            System.Drawing.FontStyle.Bold,
            System.Drawing.GraphicsUnit.Point
            )
        owner.label_chif_stoyak.Location = System.Drawing.Point(
            self.left_Point_ComboBox + self.offset_stoyak - self.label_Offset, self.height_Point_ComboBox)
        owner.label_chif_stoyak.Size = System.Drawing.Size(
            owner.label_chif_stoyak.PreferredWidth, owner.label_chif_stoyak.PreferredHeight)
        owner.Controls.Add(owner.label_chif_stoyak)
        self.label_chif_stoyak = owner.label_chif_stoyak

    # нужно получить ссылку на объект Graphics из PaintEventArgs в событии Paint
    def drawBorders(self, sender, args):
        X = self.left_Point_ComboBox  + self.offset_stoyak - self.label_Offset - 3
        Y = self.height_Point_ComboBox - 3
        W = self.height_Size_ComboBox + self.height_Size_Label + 1
        H = self.number_of_levels * 27 + 5

        comboRectangle = System.Drawing.Rectangle(X, Y, W, H)
        comboPen = System.Drawing.Pen(System.Drawing.Color.FromName('DarkGray'))
        # Захыват графического объекта
        comboGraphic = args.Graphics
        # Draw the rectangle wich is the realy border
        comboGraphic.DrawRectangle(comboPen, comboRectangle)
        # чтоб увидеть нарисованый прямоугольник нужно обновиться
        self.label_chif_stoyak.Refresh()
