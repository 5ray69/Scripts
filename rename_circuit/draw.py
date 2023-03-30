# -*- coding: utf-8 -*-

import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import System.Drawing
import System.Windows.Forms


class DrawBorder(System.Windows.Forms.Form):
    def __init__(self, owner, Offset_stoyak, Number_of_levels,
                Left_Point_ComboBox, Height_Point_ComboBox, Height_Size_ComboBox,
                Label_Offset, Height_Size_Label):
        self.left_Point_ComboBox = Left_Point_ComboBox
        self.label_Offset = Label_Offset 
        self.height_Point_ComboBox = Height_Point_ComboBox
        self.height_Size_ComboBox = Height_Size_ComboBox
        self.height_Size_Label = Height_Size_Label
        self.number_of_levels = Number_of_levels
        self.offset_stoyak = Offset_stoyak

        '''
        DEFIND LABEL NAME STOYAK
        '''
        owner.label_chif_stoyak = System.Windows.Forms.Label()
        owner.label_chif_stoyak.Text = 'основной стояк'
        owner.label_chif_stoyak.Font = System.Drawing.Font(
            'Arial',
            System.Single(10.5),
            System.Drawing.FontStyle.Bold,
            System.Drawing.GraphicsUnit.Point
            )
        owner.label_chif_stoyak.Location = System.Drawing.Point(
            self.left_Point_ComboBox - self.label_Offset, self.height_Point_ComboBox)
        owner.label_chif_stoyak.Size = System.Drawing.Size(
            owner.label_chif_stoyak.PreferredWidth, owner.label_chif_stoyak.PreferredHeight)
        owner.Controls.Add(owner.label_chif_stoyak)
        self.label_chif_stoyak = owner.label_chif_stoyak

    '''
    DEFINE THE EVENT TO DRAW THE BORDER
    '''
    # нужно получить ссылку на объект Graphics из PaintEventArgs в событии Paint
    def drawBorders(self, sender, args):
        X = self.left_Point_ComboBox - self.label_Offset - 3
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
