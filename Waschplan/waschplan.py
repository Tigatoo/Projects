#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd
import weasyprint as wp
import os
import pdfkit


one_setting = [False]

#create main window
win=tk.Tk() #creating the main window and storing the window object in 'win'
win.geometry('700x300') #setting the size of the window
win.resizable(True, True)
win.wm_title('Waschplangenerator')

#global variables
nr_of_floors = 0
output = []
days_spin = []
start_radio = []
starting_day = []

lmr_strings = [[''], ['. Links', '. Rechts'], ['. Links', '. Mitte', '. Rechts']]

start = tk.IntVar(win)

def create_floors():
    try:
        nr_of_floors = int(ent1.get())

        lmr_len = len(lmr_strings[lmr.get()])

        #resize window to adjust for the changes
        width = lmr_len * nr_of_floors * 27 + 300
        height = 790
        win.geometry(f'{height}x{width}')

        #makes sure that changing from higher number of floors
        #to lower ones doesn't result in errors due to
        #the start radio button having a not well defined position
        start.set(0)

        if nr_of_floors < 0:
            raise Exception

        while(len(output) != 0):
            win.after(5, output.pop().destroy())
            win.after(5, days_spin.pop().destroy())
            win.after(5, start_radio.pop().destroy())

        if one_setting[0] == False:
            explanation = tk.Label(win, text='        Waschtag', justify='center')
            explanation.grid(row=6, column=3, sticky='W')

            radio_expl = tk.Label(win, text='Start')
            radio_expl.grid(row=6, column=2)


        for i, pos in enumerate(lmr_strings[lmr.get()]):
            label = tk.Label(win, text='P' + pos)
            label.grid(row=i + 7, sticky='W', padx=20)
            output.append(label)

            #create spinboxes
            spin = tk.Spinbox(win, from_=0, to=5, textvariable=tk.DoubleVar(value=1), command=get_starting_day)
            spin.grid(row=i+7, column=1)
            days_spin.append(spin)

            #create radio buttons to indicate the starting floor
            radio = tk.Radiobutton(win, variable = start, value=i, command=get_starting_day)
            radio.grid(row=i+7, column=2)
            start_radio.append(radio)

        
        for i in range(nr_of_floors):
            for j, pos in enumerate(lmr_strings[lmr.get()]):

                #create labels
                label = (tk.Label(win, text='%i'% (i+1) + pos))
                label.grid(row=lmr_len*(i+1)+j+7, sticky='W', padx=20)
                output.append(label)

                #create spinboxes
                spin = tk.Spinbox(win, from_=0, to=5, textvariable=tk.DoubleVar(value=1), command=get_starting_day)
                spin.grid(row=lmr_len*(i+1)+j+7, column=1)
                days_spin.append(spin)

                #create radio buttons to indicate the starting floor
                radio = tk.Radiobutton(win, variable = start, value=lmr_len*(i+1)+j, command=get_starting_day)
                radio.grid(row=lmr_len*(i+1)+j+7, column=2)
                start_radio.append(radio)

        get_starting_day()
        one_setting[0] = True

    except:
        tk.messagebox.showinfo('Error', 'Der Etagenwert muss eine positive Zahl sein!')

def get_starting_day():
    lmr_len = len(lmr_strings[lmr.get()])

    if len(starting_day) != 0:
        win.after(5, starting_day.pop().destroy())

    spin = tk.Spinbox(win, from_=0, to=days_spin[start.get()].get(), textvariable=tk.DoubleVar(value=1))
    spin.grid(row=start.get()+7, column=3)
    starting_day.append(spin)

#list of floor names and number of days
def get_floor_list():
    """
    takes no input and returns two lists [names] and [number of days]
    """
    floor_names = []
    floor_days = []

    for (spin, label) in zip(days_spin, output):
        floor_names.append(label.cget('text'))
        floor_days.append(int(spin.get()))

    return (floor_names, floor_days)

#holiday list
def holiday_list():
    """
    takes the given list of holidays and returns a pd.Series obj with the dates
    if no dates are given a pd.Series containing only '' is returned
    """
    string_list = holidays.get()
    hol_list = string_list.split(',')

    holiday_dates = pd.Series(hol_list)

    if holiday_dates[0] == '':
        return  holiday_dates

    holiday_dates = pd.to_datetime(holiday_dates, dayfirst=True)

    return holiday_dates

#list of allowed washing days
def allowed_washing():
    """
    creates and returns based on the given year, holidays and the value for sunday a
    pd.DataFrame obj labeled by the dates and indicating whether washing is
    allowed (1) or not (0)
    """

    try:
        start = pd.to_datetime('1.1.' + year.get(), dayfirst=True)
        end = pd.to_datetime('31.12.' + year.get(), dayfirst=True)

        dates = pd.date_range(start, end, freq='d')
        #initially all dates are allowed
        all_days = pd.DataFrame(np.full(len(dates), 1), index=dates)

        holiday_dates = holiday_list()

        if holiday_dates[0] != '':
            #remove holidays
            for date in holiday_dates:
                all_days.at[date, 0] = 0

        #possibly remove sundays
        if not sunday.get():
            day_of_week = dates.to_series().dt.dayofweek
            all_days[0] = all_days[0].mask(day_of_week==6, 0)

        return all_days

    except:
        tk.messagebox.showinfo('Error', 'Bitte geben Sie ein Jahr ein.')
        return [[None]]

#write html table
def generate_html(allowed_days):
    """
    takes pd.Series indexed by dates indicating who can wash
    creates an html file with the washing plan and returns its name
    """
    housename = ''.join(x for x in house.get().split('.'))

    day_dict = {0: 'Mo', 1: 'Di', 2: 'Mi', 3: 'Do', 4: 'Fr', 5: 'Sa', 6: 'So'}

    table_with_month = allowed_days.copy()
    table_with_month['month'] = table_with_month.index.month
    table_with_month['day'] = [day_dict[day] for day in table_with_month.index.day_of_week]

    file_name = housename + '.html'
    html = open(file_name, 'a', encoding='utf-8')

    html.write("""<html>
    <head>
    <meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">
      <title>Waschplan</title>

    <style>
    @page{margin:0cm}

    .table1 {
         width:800px;
         height:800px;
         margin:auto;
         font-size:14px;
         border:0px solid #000;
         border-collapse:collapse; }
     .table1 th {
         height:22px;
         margin-top:50px;
         margin-bottom: 50px
         color:#000;
         vertical-align:middle;
         text-align:center;
         border:0px solid black; }
     .table1  td {
         margin-bottom: 50px;
         color:#474747;
         vertical-align:top;
         text-align:center;
         border:0px solid #000; }

    .table2 {
         width:150px;
         height:250px;
         margin-left:50px;
         font-size:13px;
         border:0px solid black;
         border-collapse:collapse
         }
     .table2 th {
         color:#000;
         vertical-align:middle;
         text-align:center;
         border-bottom:1px solid black; }
     .table2  td {
         color:#000;
         vertical-align:middle;
         text-align:left;
         border-bottom:1px solid #000; }

    </style>
   </head>

   <body>
     <div>
       <table class="table1">
         <tr><th></th><th style="font-size:20px">""" + str(year.get()) + """</th><th></th>
         <tr style="height: 10px !important; background-color: #FFFFFF;"><td colspan="3"></td></tr>
         <tr><th>Januar</th> <th>Februar</th> <th>""" + u"M&auml;rz" + """</th></tr>
         <tr style="vertical-align:top, text-align:center">""")

    #font-size:14px
    table_titles = {3: '<tr style="height: 20px !important; background-color: #FFFFFF;"><td colspan="3"></td></tr><tr><th>April</th> <th>Mai</th> <th>Juni</th></tr>',
                    6: """<tr style="height: 20px !important; background-color: #FFFFFF;"><td colspan="3"></td></tr>
                    <tr><th>Juli</th> <th>August</th> <th>September</th></tr>""",
                    9: '<tr style="height: 20px !important; background-color: #FFFFFF;"><td colspan="3"></td></tr><tr><th>Oktober</th> <th>November</th> <th>Dezember</th></tr>'}

    for month in range(12):
        table_of_month = table_with_month.iloc[np.where(table_with_month['month'] == month + 1)[0]]

        if month in [3, 6, 9]:
            html.write('</tr>')
            html.write(table_titles[month])
            html.write('<tr style="vertical-align:top">')

        html.write("""<td>
                        <table class="table2">""")

        for count, day in enumerate(table_of_month.index):
            html.write('<tr> <td style="width:20%; font-weight: bold">' + str(count + 1) + '</td><td style="width:30%">' + str(table_of_month.loc[day]['day'])
                       + '</td><td style:"text-align:end">' + str(table_of_month.loc[day][0]) + '</td></tr>')

        html.write('</table></td>')

    html.write('</tr></table></div></body></html>')

    html.close()

    return file_name

#file generator
def generate_file():

    if one_setting[0] == False:
        create_floors()

    (floor_names, floor_days) = get_floor_list()
    #create list of floor names with right multiplicity
    floor_multip = []
    for name_num, days in enumerate(floor_days):
        for i in range(days):
            floor_multip.append(floor_names[name_num])

    allowed_days = allowed_washing()

    if allowed_days[0][0] == None:
        return None

    #generate floor names for the whole year according
    #to allowed_days
    total_days = [int(x.get()) for x in days_spin]
    count = sum(total_days[:int(start.get())]) + int(starting_day[0].get()) - 1
    mod = len(floor_multip)
    for date in allowed_days.index:
        if allowed_days.loc[date][0] == 1:
            allowed_days.at[date, 0] = floor_multip[count % mod]
            count += 1

        else:
            allowed_days.at[date, 0] = ''


    html_source = generate_html(allowed_days)

    pdf_file_name = html_source.split('.')[0] + '.pdf'

    #wp.HTML(html_source).write_pdf(pdf_file_name)
    pdfkit.from_file(html_source, pdf_file_name)

    os.remove(html_source)

#create Etagen settings
tk.Label(win, text='Etagen').grid(row=1, pady=(20,0))
ent1 = tk.Entry(win)
ent1.grid(row=1, column=1, padx=(0,20), pady=(20,0))

#house name
tk.Label(win, text='Haus').grid(row=0, padx=20, pady=20)
house = tk.Entry(win)
house.grid(row=0, column=1, padx=(0,20))

#year
tk.Label(win, text='Jahr').grid(row=0, column=3)
year = tk.Entry(win)
year.grid(row=0, column=4, padx=(0,20))

#holidays
tk.Label(win, text='Feiertage').grid(row=1, column=3)
holidays = tk.Entry(win)
holidays.grid(row=1, column=4, padx=(0,20), pady=(20,0), sticky='W')

#button using the etagen settings to change the window
button = tk.Button(text = 'Übernehmen', command = create_floors)
button.grid(row=3, column=1, sticky='W')

#button to generate file
button = tk.Button(text = 'Plan erstellen', command = generate_file)
button.grid(row=3, column=4, sticky='W')

#radio buttons for the distiction none, lr, lmr
lmr = tk.IntVar(win)
tk.Radiobutton(win, text='Einfach', variable=lmr, value=0).grid(row=0, column=7, sticky='W')
tk.Radiobutton(win, text='Links/Rechts', variable=lmr, value=1).grid(row=1, column=7, sticky='W')
tk.Radiobutton(win, text='Links/Mitte/Rechts', variable=lmr, value=2).grid(row=2, column=7, sticky='W', pady=(0,20))

#radio buttons for sunday
sunday = tk.BooleanVar(win)
tk.Radiobutton(win, text='Sonntag nicht erlaubt', variable=sunday, value=False).grid(row=3, column=7, sticky='W')
tk.Radiobutton(win, text='Sonntag erlaubt', variable=sunday, value=True).grid(row=4, column=7, sticky='W', pady=(0,20))

tk.mainloop()
