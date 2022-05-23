"""Boilerplate for PLAXIS"""
localhostport_output = 10000
pass_word = "N+Khg1a!BE/#2rQ="
from plxscripting.easy import *
from plxscripting.plx_scripting_exceptions import PlxScriptingError
import win32com.client as win32
import tkinter as tk
import os
from tkinter.filedialog import asksaveasfile, askopenfilename


def ask_for_file_location():
    def close_window():
        tk.Tk().destroy()
        window.destroy()

    def ask_path(file_path, file_tuple):
        f_path = askopenfilename(filetypes=file_tuple)
        file_path.set(f_path)

    window = tk.Tk()
    window.title('Upload input/output file')
    window.geometry('1200x400')

    xl_file = tk.StringVar()

    lbl1 = tk.Label(window, text="Paste the directory to excel file")
    lbl1.grid(column=0, row=1, sticky="W", padx=20)
    txt1 = tk.Entry(window, width=120, textvariable=xl_file)
    txt1.grid(column=1, row=1)
    button1 = tk.Button(window, text="Find path", command=lambda: ask_path(xl_file, [("excel files", '.xlsx .xls')]))
    button1.grid(column=2, row=1, sticky="W")

    button = tk.Button(window, text="Save and next", command=close_window, height=1, width=15)
    button.grid(column=0, row=8, sticky="W", padx=20)

    window.mainloop()
    return xl_file.get()


def show_exception_and_exit(exc_type, exc_value, tb):
    """Show error without closing commnad window"""
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)


def generate_mesh(g_i, size_factor: float = 0.1):
    # generate the mesh
    g_i.gotomesh()
    # generate a fine mesh:
    g_i.mesh(size_factor)


def outputphase(g_o, inputphase):
    outputphase = get_equivalent(inputphase, g_o)
    return outputphase


def get_result(phase, doc):
    outputport = g_i.view(phase)
    s_o, g_o = new_server('localhost', outputport, password=pass_word)
    phase_o = outputphase(g_o, phase)
    U_max = max([u.value fo u in g_o.getresults(phase_o, g_o.ResultTypes.Soil.Uy, 'node')])

    ## create a path to store a picture
    pic_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'temp_MWO')
    if not os.path.exists(pic_path):
        os.makedirs(pic_path)
    pic_dir = pic_path + "//word_fig.png"

    plot = g_o.Plots[0]
    plot.DrawFrame = False
    plot.DrawLogo = False
    plot.DrawAxes = False

    g_o.set(plot.ResultType, g_o.ResultTypes.Soil.Uy)

    image_wrapper = plot.export(1600, 800)
    image_wrapper.save(pic_dir)
    put_figure(doc, pic_dir, " " + str(phase_o.Identification))

    Up_max = max([u.value for u in g_o.getresults(phase_o, g_o.ResultTypes.Soil.PUy, 'node')])

    g_o.set(plot.ResultType, g_o.ResultTypes.Soil.PUy)

    image_wrapper = plot.export(1600, 800)
    image_wrapper.save(pic_dir)
    put_figure(doc, pic_dir, " " + str(phase_o.Identification))

    return U_max, Up_max


def put_figure(doc, image, caption):
    """place image at the end of the Word doc with a caption """
    location = doc.Range()
    location.Paragraphs.Add()
    location.Collapse(0)

    figure = location.InlineShapes.AddPicture(image)
    figure.Range.InsertCaption(Label="Figure", Title=caption + '\n')
    figure.Height = 2.83 * 72
    figure.Width = 5.67 * 72


def scalling(y_coord, top_point, bottom_point, Y):
    return (top_point - y_coord) / (top_point - bottom_point) * Y


"""MAIN CODE STARTS"""
sys.excepthook = show_exception_and_exit
s_i, g_i = new_server('localhost', localhostport_output, password=pass_word)

xl_path = r"C:/Users/mwozniak/OneDrive - BESIX/Desktop/QNF/causeway/Causeway_Parametric_03052021/input_MWO.xlsx"
# xl_path = ask_for_file_location()
# print(xl_path)

# initialize excel
excel = win32.Dispatch("Excel.Application")
excel.Visible = True
wb = excel.Workbooks.Open(xl_path)
ws = wb.Worksheets('Sheet1')

soil_list = [ws.Range('D3').value, ws.Range('H3').value, ws.Range('K3').value]
i = 6
cur_cell = ws.Cells(i, 3)

param_list = []
while cur_cell.Value:
    param_list.append(ws.Range('B{}:M{}'.format(i, i)).Value[0])
    i += 1
    cur_cell = ws.Cells(i, 3)
print(param_list)
""" To remember order """
param_names = ['filename', 'seabed', 'thickness', 'phi_dep', 'c_dep', 'E_dep', 'phi_fill', 'c_fill', 'E_fill',
               'phi_armour', 'c_armour', 'E_armour']

g_i.gotostructures()

""" open word file """
word = win32.Dispatch("Word.Application")
word.Visible = True
word.Documents.Add()
doc = word.ActiveDocument

for line, params_l in enumerate(param_list, 6):
    print('/n', line, '/n')
    params = {key: params_l[i] for i, key in enumerate(param_names)}
    seabed_initial = min([p.y.value for p in g_i.Points])
    print('SEABED level', seabed_initial)
    top_intial = max([p.y.value for p in g_i.Points])  # 5.5
    print('TOP POINT', top_intial)
    Y = params['seabed'] - seabed_initial

    """ Adjusting soillayers according to seabed level """
    """Assumption Marine Deposit is first layer """
    soillayers = [(z.Top.value, z.Bottom.value, z.Thickness.value) for layer in g_i.SoilLayers for z in layer.Zones]

    for i, layer in enumerate(g_i.SoilLayers):
        for zone in layer.Zones:
            try:
                zone.Top = soillayers[i][0] + Y
            except PlxScriptingError:
                pass
            zone.Bottom = soillayers[i][1] + Y
            if i == 0:
                zone.Thickness = params['thickness']
                print(layer.Name, 'changed thickness')
            else:
                zone.Thickness = soillayers[i][2]

    """ Adjusting points of the structure according to seabed level"""
    moved_points = []
    for point in g_i.Points:
        if point.y.value < seabed_initial + 1.5:  # to account footing
            print(point.Name, 'moved')
            if point.x.value > 0:
                g_i.move(point, -4 / 3 * Y, Y)
            else:
                g_i.move(point, 4 / 3 * Y, Y)
            moved_points.append(point.Name)

    """Adjusting lines for intermediate soil fill"""
    for line in g_i.Lines:
        if (line.First.y.value == line.Second.y.value) and (line.First.y.value < top_intial - 1.9) and (
                line.First.y.value > seabed_initial + 1.5):
            points = [line.First, line.Second]
            for point in points:
                if point.Name in moved_points:
                    print(point.Name, 'has been already moved')
                else:
                    y_trans = scalling(point.y.value, top_intial, seabed_initial, Y)
                    if point.x > 0:
                        g_i.move(point, -4 / 3 * y_trans, y_trans)
                    else:
                        g_i.move(point, 4 / 3 * y_trans, y_trans)

    """ Updating soil parameter according to their name"""
    for soil in g_i.Soils:
        if soil.Material.Name in soil_list:
            if soil.Material.Name == 'MarineDeposit_SAND':
                suffix = '_dep'
            elif soil.Material.Name == 'QuarryRun':
                suffix = '_fill'
            elif soil.Material.Name == 'RockArmour':
                suffix = '_armour'
            else:
                raise UserWarning('The soil {} is not defined in the plaxis file'.format(soil.Material.Name))

            soil.Material.cref = params['c' + suffix]
            soil.Material.phi = params['phi' + suffix]
            try:
                soil.Material.Eref = params['E' + suffix] * 1000
            except PlxScriptingError:
                soil.Material.setproperties("Eref", params['E' + suffix] * 1000)
            print('I have changed {} parameters'.format(soil.Name))

    generate_mesh(g_i, 0.1)
    g_i.gotostages()
    g_i.calculate()
    """Think about saving in different location"""

    saving_name = params['filename'] + '.p2dx'
    print(type(saving_name), saving_name)
    g_i.save(saving_name)
    """Get safety factor"""
    """ASSUMPTION: I am taking safety factor from the last phase"""
    SF = g_i.Phases[-1].Reached.SumMsf.value
    print(SF)

    a1, a2 = get_result(g_i.Phases[-1], doc)
    ws.Cells(line, 14).Value = round(a1, 3) * 1000
    ws.Cells(line, 15).Value = round(a2, 3) * 1000
    ws.Cells(line, 16).Value = round(SF, 3)
    print(a1, a2)

location = doc.Range()
location.Paragraphs.Add()
location.Collapse(1)

ws.Range("A2:O{}".format(len(param_list) + 6)).Copy()
location.PasteExcelTable(False, False, False)
doc.SaveAs('figures+table.doc')

input()