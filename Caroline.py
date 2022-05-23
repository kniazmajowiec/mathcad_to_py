import sys
import tkinter as tk
from tkinter.filedialog import asksaveasfile, askopenfilename
from helper_functions import *
import os
import time


def show_exception_and_exit(exc_type, exc_value, tb):
    """Show error without closing commnad window"""
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)


def ask_for_files_location():
    def close_window():
        tk.Tk().destroy()
        window.destroy()

    def ask_path(file_path, file_tuple):
        f_path = askopenfilename(filetypes=file_tuple)
        file_path.set(f_path)

    window = tk.Tk()
    window.title('Upload input files')
    window.geometry('1200x400')

    xml_math, xml_scia, case_math, max_bar = tk.StringVar(), tk.StringVar(), tk.StringVar(value='N+My'), tk.StringVar(value='10')

    file_paths = [xml_math, xml_scia, case_math, max_bar]

    lbl1 = tk.Label(window, text="Paste the directory to mathcad file")
    lbl1.grid(column=0, row=1, sticky="W", padx=20)
    txt1 = tk.Entry(window, width=120, textvariable=xml_math)
    txt1.grid(column=1, row=1)
    button1 = tk.Button(window, text="Find path", command=lambda: ask_path(xml_math, [("mathcad compressed files", '.xmcdz .xmcd')]))
    button1.grid(column=2, row=1, sticky="W")
    ent1 = tk.OptionMenu(window, case_math, 'N+My', 'N+Mz', 'Vy+Mz', 'Vz+My',  'T')
    ent1.grid(row=1, column=4, sticky="W")

    lbl2 = tk.Label(window, text="Max numer of bars in layers")
    lbl2.grid(column=0, row=2, sticky="W", padx=20)
    txt2 = tk.Entry(window, width=40, textvariable=max_bar)
    txt2.grid(column=1, row=2, sticky="W")

    lbl3 = tk.Label(window, text="Paste the path to .xml file")
    lbl3.grid(column=0, row=4, sticky="W", padx=20)
    txt3 = tk.Entry(window, width=120, textvariable=xml_scia)
    txt3.grid(column=1, row=4)
    button3 = tk.Button(window, text="Find path", command=lambda: ask_path(xml_scia, [("xml files", '.xml')]))
    button3.grid(column=2, row=4, sticky="W")

    button = tk.Button(window, text="Save and next", command=close_window, height=1, width=15)
    button.grid(column=0, row=8, sticky="W", padx=20)

    window.mainloop()
    return [f.get() for f in file_paths]


def ask_for_table_name(tables):
    def close_window():
        root.destroy()

    root = tk.Tk()
    root.title('Which results to use')
    root.geometry('800x300')

    # define variables
    table_var = tk.StringVar(root)

    tk.Label(root, text='Table name').grid(row=0, column=0)
    ent1 = tk.OptionMenu(root, table_var, *tables)
    ent1.grid(row=1, column=0, sticky='NEWS')

    closeButton = tk.Button(root, text='Close and Next', command=close_window)
    closeButton.grid(row=2, column=0, sticky='NEWS')

    root.mainloop()
    return table_var.get()


if __name__ == "__main__":
    sys.excepthook = show_exception_and_exit

    xml_math, xml_scia, case, max_bars = ask_for_files_location()
    # print(xml_math, '\n', xml_scia, '\n', case)
    tables = get_xml_table_names(xml_scia)
    table_name = ask_for_table_name(tables)

    print('Analysing mathcad file...')
    all_define = get_define_from_mathcad(xml_math)
    df = my_xml_parse_to_df(xml_scia, table_name)
    df_in, cols = input_df(df, case)
    if case == 'N+M':
        df_in['n_1'] = 2
        df_in['n_2'] = 0

    vars = df_in.columns
    # print(vars)
    python_str = 'import math\nimport numpy as np\nfrom helper_functions import moj_max, moj_min\nmm = 0.001\nN = 1\ncm = 10 *mm\n' \
                 'kN = 1000 * N\nMPa = N/mm**2\nm = 1000 * mm\nπ = math.pi\n'

    python_str += '\ndef calc(df1):\n\tdf = df1.copy()\n'

    for i, elem in enumerate(all_define):

        list_of_commands = []
        list_of_commands = make_list_of_lists(elem, list_of_commands)
        list_of_equations = make_equ(list_of_commands)

        if list_of_equations[0][0] == 'function':
            var = ''
        else:
            var = list_of_equations[0][0]

        if var in vars:
            # python_str += '\t' + var + ' = ' + 'np.array({})'.format(df_in[var].to_list()) + '\n'
            python_str += '\t' + var + ' = ' + 'df["{}"].to_numpy()'.format(var) + '\n'
            print(var, len(df_in[var].to_list()))
        elif var in cols:
            python_str += '\t' + to_python(list_of_equations) + '\n'
            python_str += '\t' + 'if isinstance({}, np.ndarray) and ({}.size == 1):\n\t\t'.format(var, var) + 'df["{}"] = {}[0]'.format(var, var) + '\n\telse: \n\t'
            python_str += '\t' + 'df["{}"] = {}'.format(var, var) + '\n'
        else:
            python_str += '\t' + to_python(list_of_equations) + '\n'

    python_str += '\treturn df' #+ ','.join(cols)
    print('Calculating all results...')

    cur_dir = os.getcwd()
    my_file1 = os.path.join(cur_dir, 'my_file.py')
    with open(my_file1, 'w', encoding='utf-8') as f:
        f.write(python_str)

    sys.path.insert(1, cur_dir)

    from my_file import calc
    df_out = calc(df_in)
    print(df_out)
    if 'Pu' in df_out.columns:  # conversion to kN and kNm
        # First row with different number of bars
        for i in range(3, int(max_bars)+1):
            if (df_out['Result'] == 'ok').all():
                break
            df_out['n_1'] = np.where(df_out['Result'] == 'ok', df_out['n_1'], i)
            df_out = calc(df_out)

        # Second row with different number of bars
        for i in range(1, int(max_bars)+1):
            if (df_out['Result'] == 'ok').all():
                break
            df_out['n_2'] = np.where(df_out['Result'] == 'ok', df_out['n_2'], i)
            df_out = calc(df_out)

        print('conversion to kN and kNm')
        df_out['Pu'] = df_out['Pu']/10**3
        df_out['Mu'] = df_out['Mu']/10**3
        df_out['Md'] = df_out['Md'].astype(float)/10**3

        max_n1 = df_out['n_1'].max()
        max_n2 = df_out['n_2'].max()

        df_max = df_out.loc[(df_out['n_1'] == max_n1) & (df_out['n_2'] == max_n2)]
        df_max = df_max.sort_values(by=['Mu', 'Pu'], ascending=[False, False])

        df[['N', 'V_y', 'V_z', 'M_x', 'M_y', 'M_z']] = df[['N', 'V_y', 'V_z', 'M_x', 'M_y', 'M_z']].astype('float64') / 1000
        df_max = df_max.merge(df.loc[df_max.index], on=['Case', 'Name', 'dx']).drop_duplicates().reset_index()

    else:
        idx_max = []
        for col in cols:
            if not df_out[col].dtypes == 'object' and df_out[col].idxmax() not in idx_max:
                idx_max.append(df_out[col].idxmax())
        print(idx_max)
        df_max = df_out.loc[idx_max]
        df[['N', 'V_y', 'V_z', 'M_x', 'M_y', 'M_z']] = df[['N', 'V_y', 'V_z', 'M_x', 'M_y', 'M_z']].astype('float64') / 1000
        df_max = df_max.merge(df.loc[idx_max], on=['Case', 'Name', 'dx']).reset_index()

    fout = asksaveasfile(title='Save excel file', mode='w', defaultextension=".xlsx")
    excel_file = fout.name
    print('Saving excel file...')
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df_out.to_excel(writer, sheet_name='all_checks', index=False)
        df_max.to_excel(writer, sheet_name='max_columns', index=False)

    int_force_in_mathcad = [col for col in df_in.columns if col not in ['Case', 'Name', 'dx']]
    fout = asksaveasfile(title='Save mathcad file', mode='w', defaultextension=".xmcd")
    mathcad_file = fout.name
    print('Saving mathcad file...')

    fill_in_mathcad(xml_math, int_force_in_mathcad, df_max, mathcad_file)
    os.remove(my_file1)