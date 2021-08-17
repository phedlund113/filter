#------------------------------------------------------------------------------
# Name:        Filter2
# Purpose:     To scan input file, apply filter and send to output file.
#
# Author:      USPEHED
#
# Created:     27/06/2018
# Copyright:   (c) USPEHED 2018
# Licence:     <your licence>
#------------------------------------------------------------------------------

##  ------------------------------------------------------------------------
##  Imports
##  ------------------------------------------------------------------------

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import os
import sys
import subprocess
import glob
from configparser import ConfigParser
import mylib.help
# import mylib.to_log
import mylib.scrn_log
from mylib.about import *
# import simpleEd


# =============================================================================
# DONE  Add Help System
# DONE  Add Help Button
# DONE  Clear Initial input file name
# DONE  Standardize filter file format
# DONE  Add status area to gui
# DONE  When filter is run validate input file exists
# DONE  When filter is run vakudate entry box had file name
# DONE  For development add internal variable to output to console,
#       set to 0 in production program
# DONE  Fill out read.me file (help file)
# DONE  Put Filter names into combobox for selection
# DONE  Look in directory where program starts for intital filter files.
# DONE  Remove all development code that is commented out.

# DONE  Output file -- use same path as input file
# DONE  In filter file and # NAME for description
# DONE  Add Filter description to filter file

# =============================================================================

##  ------------------------------------------------------------------------
##  Constants
##  ------------------------------------------------------------------------

prog_id = {'progname': 'Filter.py',
           'title': 'Filter input to output',
           'version': '4.0',
           'date': "30 August 2018",
           'rev_date': '17 August 2021',
           'author': "Peter Hedlund",
           'description': 'To permit applying a filter to an input file\n'
           ' then send the output of the filter to another file.'}


infile = ''
outfile = ''
#  output_to_console = 0
count = 0
file_save = 0
filters = []
descrip = []
cmds = []
base_dir = os.path.dirname(sys.argv[0]) + '\\'
config_fn = os.path.dirname(sys.argv[0]) + '\\' + 'filter.ini'


##  ------------------------------------------------------------------------
##  Functions
##  ------------------------------------------------------------------------

def get_xy_pos():
    rg = root.geometry()
    xi = rg.find('+')
    yi = rg.find('+', xi+1)
    x = int(rg[xi+1:yi])
    y = int(rg[yi+1:len(rg)])
    return x, y


def default_config():
    c_pos.set(0)
    c_pos_x.set(10)
    c_pos_y.set(10)
    c_in_file.set(0)
    c_in_filename.set('')
    c_out_file.set(0)
    c_out_filename.set('')
    c_filt_sel.set(0)
    c_filt_selected.set(0)
    c_filt_opt.set(1)
    c_pcmd_sel.set(0)
    c_pcmd_selected.set(0)



def load_config():
    if os.path.exists(config_fn) == False:
        default_config()
    config = ConfigParser()
    config.read(config_fn)
    c_pos.set(config['position']['remember'])
    c_pos_x.set(config['position']['x_pos'])
    c_pos_y.set(config['position']['y_pos'])
    c_in_file.set(config['in_file']['remember'])
    c_in_filename.set(config['in_file']['filename'])
    c_out_file.set(config['out_file']['remember'])
    c_out_filename.set(config['out_file']['filename'])
    c_filt_sel.set(config['filter']['remember'])
    c_filt_selected.set(config['filter']['selected'])
    c_filt_opt.set(config['filter']['option'])
    c_pcmd_sel.set(config['pcommand']['remember'])
    c_pcmd_selected.set(config['pcommand']['selected'])
    if c_in_file.get() == 1:
        my_path.set(c_in_filename.get())
    if c_out_file.get() == 1:
        txt_save.set(c_out_filename.get())


def save_config():
    config = ConfigParser()
    x, y = get_xy_pos()
    c_pos_x.set(x)
    c_pos_y.set(y)
    if c_filt_sel.get() == 0:
        c_filt_selected.set(0)
    else:
        c_filt_selected.set(prt_sel.current())
    if c_pcmd_sel.get() == 0:
        c_pcmd_selected.set(0) 
    else:   
        c_pcmd_selected.set(cmd_sel.current())
    if c_in_file.get() == 0:
        c_in_filename.set('')
    else:    
        c_in_filename.set(my_path.get())
    if c_out_file.get() == 0: 
        c_out_filename.set('')
    else:   
        c_out_filename.set(txt_save.get())
    config['position'] = {'remember' : c_pos.get(), 
                          'x_pos' : c_pos_x.get(), 
                          'y_pos' : c_pos_y.get()}
    config['in_file'] = {'remember' : c_in_file.get(),
                         'filename' : c_in_filename.get()}
    config['out_file'] = {'remember' : c_out_file.get(),
                          'filename' : c_out_filename.get()}
    config['filter'] = {'remember' : c_filt_sel.get(),
                         'option' : output_to.get(),
                         'selected' : c_filt_selected.get()}
    config['pcommand'] = {'remember' : c_pcmd_sel.get(),
                         'selected' : c_pcmd_selected.get()}
                                               
    with open(config_fn, 'w') as configfile:
        config.write(configfile)


def my_report(wstr, color='green'):
    scrn.update = 1
    scrn.log_scrn_color(wstr, color)


def load_filter(is_reload):
    global filters
    global descrip
    filters = []
    descrip = []
    for file in glob.glob(base_dir + 'flt/*.flt'):
        filters.append(os.path.split(file)[1])
    if len(filters) == 0:
        filters.append('--NONE--')
        messagebox.showerror('FILTER ERROR', 'No Filters Found.\n Create filter then restart program.')
    else:
        filters = sorted(filters, key=str.casefold)
        for x in range(0, len(filters)):
            strx = filters[x]
            fp = open(base_dir + '//flt//' + filters[x], 'r')
            for line in fp:
                y = line.find('Purpose:')
                if y > 0 and y < 5:
                    strx = line[15:54]
                # else:
                #     strx = filters[x]
            fp.close()
            descrip.append(strx)
        if (is_reload):
            prt_sel.config(value=descrip)
            prt_sel.current(0)


def load_cmds(is_reload):
    global cmds
    global cdescrip
    cmds = []
    cdescrip = []
    for file in glob.glob(os.path.dirname(sys.argv[0]) + '\\' + 'pcmd/*.pcmd'):
        cmds.append(os.path.split(file)[1])
    if len(cmds) == 0:
        cmds.append('--NONE--')
        messagebox.showerror('COMMAND ERROR', 'No Command Found.\n Create Command then restart program.')
    else:
        cmds = sorted(cmds, key=str.casefold)
        for x in range(0, len(cmds)):
            strx = cmds[x]
            fp = open(base_dir + '//pcmd//' + cmds[x], 'r')
            for line in fp:
                y = line.find('Purpose:')
                if y > 0 and y < 5:
                    strx = line[15:54]
                # else:
                #     strx = cmds[x]
            fp.close()
            cdescrip.append(strx)

        if (is_reload):
            cmd_sel.config(value=cdescrip)
            cmd_sel.current(0)


##  ------------------------------------------------------------------------
##  Controls
##  ------------------------------------------------------------------------

def input_file():
    """Calls the askopenfilename dialog box and places the basename on the gui
        amd sets my_path to the full pathname of the input file
    """
    path = filedialog.askopenfilename(parent=mainframe, filetypes=[
        ('All', '*.*')])
    if path == '':
        return
    my_path.set(path)
    lab_if.config(text=os.path.basename(path))


def reload_filter():
    load_filter(1)


def process_file():
    """  This function sets up 3 global varable that will be read by the
    filter function called and sets up 1 global variable that the
    filter passes back.
    Input file is verified for existance
    outfile is validated to cotain some characters
    file_save indicates to filter program that there is a valid filename
    to save to count returns the number of lines processed to the output
    by the filter.
    """
    global infile
    global outfile
    global file_save
    # global output_to_console
    global count
    global output_to
    abort_filter.set(0)
    if filters[prt_sel.current()] == '--NONE--':
        scrn.log_scrn_color("NO FILTERS FOUND TO USE!!\n", 'red')
        scrn.log_scrn_color("ADD/CREATE FILTER FILE,\n", 'yellow')
        scrn.log_scrn_color("THEN RE-RUN PROGRAM!!\n", 'yellow')
        return
    if os.path.isfile(my_path.get()) == False:
        messagebox.showerror('Input File Error', 'Input File was not found')
        return
    file_save = 1
    if txt_save.get() == '':
        file_save = 0
    infile = my_path.get()
    outfile = os.path.dirname(infile) + '/' + txt_save.get()
    lab_cnt.config(text='Processing')
    root.update()
    exec(open(base_dir + 'flt/' + filters[prt_sel.current()]).read())
    lab_cnt.config(text='Count = ' + str(count))


def cmd_run():
    if cmds[cmd_sel.current()] == '--NONE--':
        scrn.log_scrn_color("NO COMMANDS FOUND TO USE!!\n", 'red')
        scrn.log_scrn_color("ADD/CREATE COmmand (.pcmd) FILE,\n", 'yellow')
        scrn.log_scrn_color("THEN RE-RUN PROGRAM!!\n", 'yellow')
        return
    exec(open(base_dir + 'pcmd/' + cmds[cmd_sel.current()]).read())


def list_cmd():
    """
    This function call the listing program passing the output file name.
    Error checking for existence of the output file as well as an empty output
    file name.
    """
    #  lister = '/bin/LTFViewr5u.exe'
    lister = '/bin/lister.exe'
    if my_path.get() == '':
        messagebox.showerror('Input File Error', 'Input File name Required')
        return

    # use this if you want to still use the calling program.
    # os.system(lister + ' ' + txt_save.get())

    # use this if you want the calling program to wait until this 
    # program terminates.
    print('myvalue=' + my_path.get() + '\n' )
    subprocess.run([base_dir + 'lister', my_path.get()])


def reload_cmds():
    load_cmds(1)


def save_log():
    """
    This function will save the log window to a file
    """
    scrn.save_scrn(mainframe)


def log2clip():
    scrn.clipboard_scrn(mainframe)
    

def clear_log():
    """
    This function will clear the log window
    """
    scrn.clear_scrn()
    lab_cnt.config(text='')


def test_edit():
    my_editor = 'NOTEPAD.exe'
    os.system(my_editor)
    # sys.argv = ['simpleEd.py','all-out.flt']
    # simpleEd.SimpleEditor()
    # execfile('text_ed2.py')


def abort_flt():
    abort_filter.set(1)


def about_cmd():
    about_box(prog_id)


def help_cmd():
    mylib.help.Dialog(mainframe, title='Scan Help', filename=None)


def quit_prog():
    save_config()
    root.destroy()


def config_quit():
    global top 
    top.destroy()


def config_save():
    global top 
    save_config()
    top.destroy()

def config():
    global top
    try:
        if top.state() == 'normal':
            top.focus()
    except:
        top = Toplevel()
        top.title('Configuration')
        x,y = get_xy_pos()
        top.geometry(f'200x210+{x+20}+{y+20}')
        # ttk.Label(top, text=' ').grid(column=0, row=0, padx=5)
        rem = ttk.Checkbutton(top, variable=c_pos, text='Remember x,y Position')
        rem.grid(column=0, row=1, sticky='w', columnspan=2, padx=5)
        rem = ttk.Checkbutton(top, variable=c_in_file, text='Remember Input Filename')
        rem.grid(column=0, row=2, sticky='w', columnspan=2, padx=5)
        rem = ttk.Checkbutton(top, variable=c_out_file, text='Remember Output Filename')
        rem.grid(column=0, row=3, sticky='w', columnspan=2, padx=5)
        rem = ttk.Checkbutton(top, variable=c_filt_sel, text='Remember Filter Selected')
        rem.grid(column=0, row=4, sticky='w', columnspan=2, padx=5)
        r1 = Radiobutton(top, text="Filter option 1", variable=c_filt_opt, value=0)
        r1.grid(column=0, row=5, sticky='w', columnspan=2, padx=5)
        r2 = Radiobutton(top, text="Filter option 2", variable=c_filt_opt, value=1)
        r2.grid(column=0, row=6, sticky='w', columnspan=2, padx=5)
        r3 = Radiobutton(top, text="Filter option 3", variable=c_filt_opt, value=2)
        r3.grid(column=0, row=7, sticky='w', columnspan=2, padx=5)
        rem = ttk.Checkbutton(top, variable=c_pcmd_sel, text='Remember PCommand Selected')
        rem.grid(column=0, row=8, sticky='w', columnspan=2, padx=5)
        qu = ttk.Button(top, text=' Cancel ', command=config_quit)
        qu.grid(column=1,row=9, pady=3)
        qu2 = ttk.Button(top, text=' SAVE ', command=config_save)
        qu2.grid(column=0,row=9, pady=3)
#------------------------------------------
#
#  MAIN GUI
#
#------------------------------------------

# valid colors : 
#    red, yellow, green, blue, cyan, white, violet, sky blue, 
#    hot pink, lightgrey, brown4

"""  Main gui starts here
    The purpose of this program is to allow the operator to create filters 
    that process an input file into an output file without having to modify 
    or create a gui each time.  The User only has to create a filter program 
    in python.  The filter has access to infile, outfile, output_to_console 
    and count.  The filter must declare count as a global so values can be 
    passed back to the gui.  See filter1.py and filter2.py for examples.
    Name your filter filter?.py where ? is a number.
    When the program starts, it scans for filter*.py and places them into 
    the combo box for selection.

"""
root = Tk()
#  prevent window resizing.
top = None
#  region Variable Area

c_pos = IntVar()
c_pos_x = IntVar()
c_pos_y = IntVar()
c_in_file = IntVar()
c_in_filename = StringVar()
c_out_file = IntVar()
c_out_filename = StringVar()
c_filt_sel = IntVar()
c_filt_selected = IntVar()
c_pcmd_sel = IntVar()
c_pcmd_selected = IntVar()
c_filt_opt = IntVar()
txt_save = StringVar()
txt_path = StringVar()
txt_load = StringVar()
my_path = StringVar()
use_srm = IntVar()
output_to = IntVar()
abort_filter = IntVar()
abort_filter.set(0)
default_config()
load_config()

#   endregion Variable Area

#  GUI Section
root.resizable(0, 0)
root.geometry('%dx%d+%d+%d' % (820, 760, c_pos_x.get(), c_pos_y.get()))
root.title(prog_id['title'])
mainframe = ttk.Frame(root, padding="3", height=760, width=820)
mainframe.grid(column=1, row=3, sticky=(N, W, E, S))
mainframe.grid_propagate(0)
mainframe.tk.call('tk', 'scaling', 1.2)

#  region Style Section
#  Style Section
s1 = ttk.Style()
s1.configure('red.TButton', background='Red', relief='sunken')
s2 = ttk.Style()
s2.configure('blue.TButton', background='Blue')
s3 = ttk.Style()
s3.configure('green.TButton', background='Green')
s4 = ttk.Style()
s4.configure('cyan.TButton', background='Cyan', relief='raised')
s5 = ttk.Style()
s5.configure('black.TLabelframe', foreground='Black')
s6 = ttk.Style()
s6.configure('black.TButton', background='Black')
s7 = ttk.Style()
s7.configure('magenta.TButton', background='Magenta')

mystyle='SUNKEN'
#  endregion Style Section

load_filter(0)

load_cmds(0)

#  region Upper Command Area
iflf = ttk.Labelframe(mainframe,text='Input File', relief=RAISED, borderwidth=4)
iflf.grid(column=0, row=0, columnspan=2)
btn_if = ttk.Button(iflf, text="InFile", command=input_file, width=15)
btn_if.grid(column=0, row=0, padx=15, pady=5)
lab_if = ttk.Label(iflf, width=15, relief='sunken')
lab_if.grid(column=1, row=0, padx=15, pady=5)
if c_in_file.get() == 1:
    lab_if.config(text=os.path.basename(c_in_filename.get()))
oflf = ttk.Labelframe(mainframe,text='Output File', relief=SUNKEN, borderwidth=4)
oflf.grid(column=2, row=0, columnspan=1)
ent_of = ttk.Entry(oflf, textvariable=txt_save, width=15)
ent_of.grid(column=0, row=0, padx=15, pady=5)
if c_out_file.get() == 1:
    txt_save.set(c_out_filename.get())
fflf = ttk.Labelframe(mainframe,text='Filter File', relief=RAISED, borderwidth=4)
fflf.grid(column=4, row=0, columnspan=3)
lab_fl = ttk.Button(fflf, text='Re-Load', command=reload_filter, width=15)
lab_fl.grid(column=2, row=0, padx=15, pady=5)
prt_sel = ttk.Combobox(fflf, state="readonly", width=35, height=20, values=descrip)
prt_sel.grid(column=0, row=0, padx=10, pady=5, columnspan=2)
prt_sel.current(c_filt_selected.get())

#  endregion Upper Command Area

# -------------------
#  Text box Widget
# -------------------
scrn = mylib.scrn_log.scrn_log(mainframe, 80, 34, 'lightgreen', 'gray15', 0, 2, 9, 20)

#  region Lower Command Area
cmlf = ttk.Labelframe(mainframe, text='Commands', borderwidth=4,style='black.TLabelframe')
cmlf.grid(column=0, row=24, columnspan=10, rowspan=2, sticky='w', padx=5)

output_to.set(c_filt_opt.get())

ctrl = (('BTN', 1, 0, 'Run Filter',    process_file, 'green.TButton'),
        ('BTN', 1, 1, 'Run CMD',       cmd_run,      'green.TButton'),
        ('BTN', 3, 0, 'Abort Filter',  abort_flt,    'green.TButton'),
        ('BTN', 1, 2, 'View Input',    list_cmd,     'blue.TButton'),
        ('BTN', 4, 1, 'Re-Load CMD',   reload_cmds,  None          ),
        ('BTN', 7, 0, 'Save Output',   save_log,     'blue.TButton'),
        ('BTN', 7, 1, 'Output 2 Clip', log2clip,     'blue.TButton'),
        ('BTN', 7, 2, 'Clear Output',  clear_log,    'blue.TButton'), 
        ('BTN', 9, 0, 'Notepad',       test_edit,    'red.TButton' ),
        ('BTN', 9, 1, 'About',         about_cmd,    'cyan.TButton'),
        ('BTN', 9, 2, 'Help',          help_cmd,     'cyan.TButton'),
        ('BTN', 9, 3, 'Quit',          quit_prog,    'red.TButton' ),
        ('RDO', 0, 1, '[ OPT 1 ]',     output_to,    0),
        ('RDO', 0, 2, '[ OPT 2 ]',     output_to,    1),
        ('RDO', 0, 3, '[ OPT 3 ]',     output_to,    2),
        ('LBL', 0, 0, 'Filter Options'),
        ('LBL', 6, 1, '   '),
        ('LBL', 8, 1, '   '),
        ('LBL',10, 1, '   '),
          )

for x in range(0, len(ctrl)):
    if ctrl[x][0] == 'BTN':
        btn_x = ttk.Button(cmlf, text=ctrl[x][3], command=ctrl[x][4], 
            width=15, style=ctrl[x][5])
        btn_x.grid(column=ctrl[x][1], row=ctrl[x][2], padx=15, pady=5)
    elif ctrl[x][0] == 'LBL':
        lbl1 = ttk.Label(cmlf, text=ctrl[x][3])
        lbl1.grid(column=ctrl[x][1], row=ctrl[x][2], padx=15, pady=5)
    elif ctrl[x][0] == 'RDO':
        r1 = Radiobutton(cmlf, text=ctrl[x][3], variable=ctrl[x][4], 
            value =ctrl[x][5])
        r1.grid(column=ctrl[x][1], row=ctrl[x][2], sticky='w')

lab_cnt = ttk.Label(cmlf,width = 15)
lab_cnt.grid(column=2, row=0, padx=15, pady=5)

cmd_sel = ttk.Combobox(cmlf, state="readonly", width=35, height=20, values=cdescrip)
cmd_sel.grid(column=2, row=1, padx=15, columnspan=2, pady=5, sticky='w')
cmd_sel.current(c_pcmd_selected.get())

conf = ttk.Button(cmlf, text='C\nO\nN\nF\nI\nG\n', command=config, width=3,style='black.TButton' )
conf.grid(column=11, row=0, rowspan=3)
#  endregion Lower Command Area

for child in cmlf.winfo_children():
    child.grid_configure(padx=0, pady=5)
root.mainloop()


