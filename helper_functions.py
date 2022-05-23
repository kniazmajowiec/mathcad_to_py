import xml.etree.ElementTree as et
import xml.dom.minidom as md
import pandas as pd
import numpy as np
import re
import gzip


def get_define_from_mathcad(xml_path):
    xml_ = gzip.open(xml_path, 'r')
    try:
        tree = et.parse(xml_)
    except OSError:
        tree = et.parse(xml_path)
    root = tree.getroot()

    ns = {'xmlns': "http://schemas.mathsoft.com/worksheet30",
          'xsi': "http://www.w3.org/2001/XMLSchema-instance",
          'ws': "http://schemas.mathsoft.com/worksheet30",
          'ml': "http://schemas.mathsoft.com/math30",
          'u': "http://schemas.mathsoft.com/units10",
          'p': "http://schemas.mathsoft.com/provenance10"
          }

    for prefix, uri in ns.items():
        et.register_namespace(prefix, uri)

    return root.findall('.//ml:define', ns)


def get_xml_table_names(xml_file):
    """Assume only one table in a container, no subtable"""

    tree = et.parse(xml_file)
    root = tree.getroot()
    et.register_namespace('', "http://www.scia.cz")

    tables = root.findall('.//{http://www.scia.cz}table')
    tabs = []
    [tabs.append(tab.attrib['name']) for tab in tables if tab.attrib['name'] not in tabs and
     'Nonlinear combination' not in tab.attrib['name']]
    return tabs


def my_xml_parse_to_df(xml_file, table_name):
    """Assume only one table in a container, no subtable"""

    tree = et.parse(xml_file)
    root = tree.getroot()
    et.register_namespace('', "http://www.scia.cz")

    tables = root.findall('.//{{http://www.scia.cz}}table[@name="{}"]'.format(table_name))

    df_big = pd.DataFrame()

    for elem in tables:
        headers = [s.attrib['t'] for subelem in elem.findall('.//') if subelem.tag == '{http://www.scia.cz}h'
                   for s in subelem.findall('./')]
        rows = [[s.attrib['v'] for s in subelem.findall('./')] for subelem in elem.findall('.//')
                if subelem.tag == '{http://www.scia.cz}row']

        if "Overall Unity Check" in headers:
            headers.remove("Overall Unity Check")

        df = pd.DataFrame(rows, columns=headers)
        df_big = pd.concat([df_big, df], ignore_index=True)

    return df_big


def make_list_of_lists(elem, list_of_levels=[]):
    """from mathcad xml with define returns list of lists; each sub list presents elements of the same level"""
    if [el.tag[36:] for el in elem.findall('./')] and 'apply' in [el.tag[36:] for el in elem.findall('./')]:
        list_of_levels.append([get_var(el) for el in elem.findall('./')])
    elif [el.tag[36:] for el in elem.findall('./')]:
        list_of_levels.append([get_var(el) for el in elem.findall('./')])
    for el in elem.findall('./'):
        make_list_of_lists(el, list_of_levels)
    return list_of_levels


def make_equ(list_of_lists):
    """from list of lists presenting elements of same level modifies input to get simple equations"""
    list_len = len(list_of_lists)

    for i, list_ in enumerate(list_of_lists[::-1], 1):
        k = list_len - i
        for j, something in enumerate(list_):
            if something == 'apply' or something == 'boundVars':
                list_.insert(j, fun(list_of_lists[k+1]))
                list_.remove(something)
                list_of_lists.pop(k+1)
                # print(list_of_lists)
            elif something == 'parens':
                list_.insert(j, '({})'.format(' '.join(list_of_lists[k+1])))
                list_.remove(something)
                list_of_lists.pop(k + 1)
            elif something == 'if':  # assume there is if and sequence meaning x = a if b else c

                if_cond = [' '.join(['np.where(', ', '.join(list_of_lists[k + 1]), ')'])]
                list_of_lists.insert(k, if_cond)
                list_of_lists.pop(k + 1)
                # print(list_of_lists)
            elif something == 'sequence':
                list_.insert(j, '{}'.format(','.join(list_of_lists[k+1])))
                list_.remove(something)
                list_of_lists.pop(k + 1)

    return list_of_lists


def get_var(el):
    if not el.text or not el.text.strip():
        return el.tag[36:]
    else:
        try:
            var = el.text + '_' + el.attrib['subscript']
        except KeyError:
            var = el.text
        if el.tag[36:] == 'str':
            return '"' + var + '"'
        elif el.tag[36:] == 'id':
            return var.replace('.', '_').replace('·', '*')
        else:
            return var.replace('·', '*')


repl_dict = {'define': '=', 'id': '', 'apply': '', 'mult': '*', 'real':'', 'program': '', 'ifThen': 'if',
             'lessThan': '<', 'greaterThan': '>', 'otherwise': 'else', 'parens': '', 'minus': '-', 'div': '/',
             'pow': '**', 'plus': '+', 'absval': 'abs', 'neg':'-', 'function': '', 'boundVars': '', 'lessOrEqual': '<=',
             'str': 'str', 'sequence': '', 'greaterOrEqual': '>=', 'sqrt': 'np.sqrt', 'or': '|', 'equal': '==',
             'notEqual': '!=', 'and': '&', 'min': 'moj_min', 'max': 'moj_max'}


def fun(lol):
    if lol[0] in ['mult', 'lessThan', 'greaterThan', 'minus', 'plus',
                  'lessOrEqual', 'greaterOrEqual', 'equal', 'notEqual']:
        lol[0] = repl_dict[lol[0]]
        lol.insert(1, lol.pop(0))
        return ' '.join(lol)

    elif lol[0] in ['div', 'pow', 'or', 'and']:
        lol[0] = repl_dict[lol[0]]
        lol.insert(1, lol.pop(0))
        parens_1 = '({})'.format(lol[0]) if ' ' in lol[0] else lol[0]
        parens_2 = '({})'.format(lol[2]) if ' ' in lol[2] else lol[2]
        return ' '.join([parens_1, lol[1], parens_2])

    elif lol[0] in ['min', 'absval', 'sqrt', 'neg', 'max']:
        lol[0] = repl_dict[lol[0]]
        return lol[0] + '(' + ''. join(lol[1:]) + ')'

    else:
        return lol[0] + '(' + ','.join(lol[1:]) + ')' if lol[1:] else lol[0]


def moj_max(*args):
    """take minimum from different amount of scalars and numpy arrays"""
    length = 1
    for arg in args:
        if isinstance(arg, np.ndarray) and (arg.size > length):
            length = arg.size
    arrays = []
    for arg in args:
        if isinstance(arg, float) or isinstance(arg, int):
            array = np.ones(length) * arg
            arrays.append(array)
        elif isinstance(arg, np.ndarray) and (arg.size == 1):
            array_add = np.ones(length) * arg
            arrays.append(array_add)
        elif isinstance(arg, np.ndarray) and (arg.size < length):
            array_add = np.ones(length - arg.size) * -np.inf
            array = np.append(arg, array_add)
            arrays.append(array)
        else:
            arrays.append(arg)
    else:
        return np.maximum.reduce(arrays)


def moj_min(*args):
    """take minimum from different amount of scalars and numpy arrays"""
    length = 1
    for arg in args:
        if isinstance(arg, np.ndarray) and (arg.size > length):
            length = arg.size

    arrays = []
    for arg in args:
        if isinstance(arg, float) or isinstance(arg, int): # or (isinstance(arg, np.ndarray) and (arg.shape[0] == 0)):
            array = np.ones(length) * arg
            arrays.append(array)
        elif isinstance(arg, np.ndarray) and (arg.size == 1):
            array_add = np.ones(length) * arg
            arrays.append(array_add)
        elif isinstance(arg, np.ndarray) and (arg.size < length) and (arg.size > 1):
            array_add = np.ones(length - arg.size) * np.inf
            array = np.append(arg, array_add)
            arrays.append(array)
        else:
            arrays.append(arg)
    return np.minimum.reduce(arrays)


def to_python(list_):
    if len(list_) == 1:  # standard definition A= B + 2
        return list_[0][0] + ' = ' + list_[0][1]
    elif list_[0][0] == 'function':  # function f(x)
        if len(list_) == 2:  # simple function that just returns the function for x
            variable = list_[0][1]
            def_str = 'def {}:\n'.format(variable)
            def_str += '\t return ' + fun(list_[1])
            return def_str
        else:  # function with additional cases mostly def with ifs
            variable = list_[1][0] + '(' + list_[1][1] + ')'
            list_[0][0] = list_[1][0]
            def_str = 'def {}:\n\t'.format(variable)
            list_.pop(1)
            if_str = to_python(list_).replace('\n', '\n\t')
            def_str += '\t' + if_str
            def_str += '\treturn ' + list_[0][0]
            return def_str
    elif list_[0][1] == 'program':  # if elif else
        variable = list_[0][0]
        npwhere_str = variable + ' = '
        for i, l in enumerate(list_[2:], 0):
            if (l[0].count('>') + l[0].count('<') > 1) & (l[0].count('&') == 0):
                l[0] = l[0].split(' x ')
                l[0] = '(' + 'x) & (x'.join(l[0]) + ')'
            if list_[1][i] == 'ifThen':
                npwhere_str += 'np.where({}, {}, '.format(l[0], l[1])
            else:  # otherwise
                npwhere_str += '{}'.format(l[0]) + ')' * (len(list_[2:]) - 1) + '\n'
        return npwhere_str


def input_df(df, case):
    """From input dataframe (from SCIA) changes internal forces to the desired values"""
    ### ASSUMING THAT SCIA RESULTS IN kN AND kNm
    df1 = df.copy()
    df1[['N', 'V_y', 'V_z', 'M_x', 'M_y', 'M_z']] = df1[['N', 'V_y', 'V_z', 'M_x', 'M_y', 'M_z']].astype('float64')
    df1 = df1.loc[df1['Case'].str.contains('U')]
    if case == 'N+My':
        # input in mathcad with units kN thus all input are multiplied by 1000 inside mathcad and I am replacing values
        df1['n_1'] = 2
        df1['n_2'] = 0
        df1['Pu'] = -df1['N']
        df1['Mu'] = df1['M_y'].abs()

        return df1[['Case', 'Name', 'dx', 'n_1', 'n_2', 'Pu', 'Mu']], ['Md', 'Result', 's_max', 's_min', 'As_max',
                                                                       'As_min', 'Result1', 'Result2', 'Result3',
                                                                       'Result4']
    elif case == 'N+Mz':
        # input in mathcad with units kN thus all input are multiplied by 1000 inside mathcad and I am replacing values
        df1['n_1'] = 2
        df1['n_2'] = 0
        df1['Pu'] = -df1['N']
        df1['Mu'] = df1['M_z'].abs()

        return df1[['Case', 'Name', 'dx', 'n_1', 'n_2', 'Pu', 'Mu']], ['Md', 'Result', 's_max', 's_min', 'As_max',
                                                                       'As_min', 'Result1', 'Result2', 'Result3',
                                                                       'Result4']
    elif case == 'Vy+Mz':
        df1['V_u'] = df1['V_y'].abs() / 1000
        df1['M_u'] = df1['M_z'].abs() / 1000
        return df1[['Case', 'Name', 'dx', 'V_u', 'M_u']], ['A_v', 'A_vmin', 'A_vmax']

    elif case == 'Vz+My':
        df1['V_u'] = df1['V_z'].abs() / 1000
        df1['M_u'] = df1['M_y'].abs() / 1000
        return df1[['Case', 'Name', 'dx', 'V_u', 'M_u']], ['A_v', 'A_vmin', 'A_vmax']

    elif case == 'T':
        df1['V_u'] = df1[['V_y', 'V_z']].abs().max(axis=1) / 1000
        df1['T_u'] = df1['M_x'].abs() / 1000
        return df1[['Case', 'Name', 'dx', 'V_u', 'T_u']], ['A_l', 'A_t', 'Torsion_effects']


def add_df_col(df2, col_names, col_values):
    df_out = df2.copy()
    for col, val in zip(col_names, col_values):
        try:
            df_out[col] = val
        except ValueError:
            if isinstance(val, np.ndarray) and val.size == 1:
                df_out[col] = val[0]
            else:
                print("WTF", val.size, val)
    return df_out


def fill_in_mathcad(xml_path, vars, df, mathcad_file):
    xml_ = gzip.open(xml_path, 'r')
    try:
        tree = et.parse(xml_)
    except OSError:
        tree = et.parse(xml_path)
    root = tree.getroot()

    ns = {'xmlns': "http://schemas.mathsoft.com/worksheet30",
          'xsi': "http://www.w3.org/2001/XMLSchema-instance",
          '': "http://schemas.mathsoft.com/worksheet30",
          'ml': "http://schemas.mathsoft.com/math30",
          'u': "http://schemas.mathsoft.com/units10",
          'p': "http://schemas.mathsoft.com/provenance10"
          }

    for prefix, uri in ns.items():
        et.register_namespace(prefix, uri)

    all_defintion = root.findall('.//ml:define', ns)

    for elem in all_defintion:
        if elem.tag[36:] == 'define' and elem[0].text in vars:
            var = elem[0].text
            print('changed ', var, ' to ', df.at[0, var])
            pupa = elem.find('.//ml:real', ns)
            pupa.text = "{:.0f}".format(df.at[0, var])

        else:
            try:
                if elem.tag[36:] == 'define' and elem[0].text + '_' + elem[0].attrib['subscript'] in vars:
                    var = elem[0].text + '_' + elem[0].attrib['subscript']
                    print('changed ', var, ' to ', df.at[0, var])
                    pupa = elem.find('.//ml:real', ns)
                    pupa.text = "{:.0f}".format(df.at[0, var])
            except KeyError:
                pass

    # prettyXML = md.parseString(re.sub(r'\n+\t*\s*', '', et.tostring(root, encoding='unicode'))).toprettyxml()
    prettyXML = et.tostring(root, encoding='unicode')
    with open(mathcad_file, 'w', encoding='utf-8') as f:
        f.write(prettyXML)

