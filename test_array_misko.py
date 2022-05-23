import xml.etree.ElementTree as et
import pandas as pd
import numpy as np
import gzip


def my_xml_parse_to_df(xml_file, table_name):
    """Assume only one table in a container, no subtable"""

    tree = et.parse(xml_file)
    root = tree.getroot()
    et.register_namespace('', "http://www.scia.cz")

    for elem in root.iter():
        if elem.tag == '{http://www.scia.cz}table' and elem.attrib['name'] == table_name:
            headers = [s.attrib['t'] for subelem in elem.findall('.//') if subelem.tag == '{http://www.scia.cz}h'
                       for s in subelem.findall('./')]
            rows = [[s.attrib['v'] for s in subelem.findall('./')] for subelem in elem.findall('.//')
                    if subelem.tag == '{http://www.scia.cz}row']
            break

    if "Overall Unity Check" in headers:
        headers.remove("Overall Unity Check")

    try:
        df = pd.DataFrame(rows, columns=headers)
    except ValueError:
        raise UserWarning('There are more than one table in the xml container')

    return df


def perf_func(elem, level=0, dupa=[]):
    if elem.tag[36:] == 'apply' and len(elem.findall('./')) == 3:
        dupa.append([elem[1].tag[36:], elem[0].tag[36:], elem[2].tag[36:]])
    for child in elem.findall('./'):
        perf_func(child, level+1)
    return dupa


def make_list_of_lists(elem, dupa=[]):
    if [el.tag[36:] for el in elem.findall('./')] and 'apply' in [el.tag[36:] for el in elem.findall('./')]:
        dupa.append([get_var(el) for el in elem.findall('./')])
    elif [el.tag[36:] for el in elem.findall('./')]:
        dupa.append([get_var(el) for el in elem.findall('./')])
    # print(elem, dupa)
    for el in elem.findall('./'):
        make_list_of_lists(el, dupa)
    return dupa


def make_equ(list_of_lists):
    list_len = len(list_of_lists)
    # if all([isinstance(list_, tuple) for list_ in list_of_lists]):
    #     return list_of_lists
    # else:
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
                # if_cond = [' '.join([list_of_lists[k + 1][1], 'if', list_of_lists[k + 1][0], 'else', list_of_lists[k + 1][2]])]
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
             'notEqual': '!=', 'and': '&', 'min': 'np.minimum', 'max': 'np.maximum'}


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
        if ''. join(lol[1:]).count(',') < 2:
            return lol[0] + '(' + ''. join(lol[1:]) + ')'
        else:
            return lol[0] +'.reduce' + '([' + ''.join(lol[1:]) + '])'
    else:
        return lol[0] + '(' + ','.join(lol[1:]) + ')' if lol[1:] else lol[0]


def to_python(list_):
    if len(list_) == 1:
        return list_[0][0] + ' = ' + list_[0][1]
    elif list_[0][0] == 'function':  # function f(x)
        if len(list_) == 2:
            variable = list_[0][1]
            def_str = 'def {}:\n'.format(variable)
            def_str += '\t return ' + fun(list_[1])
            return def_str
        else:
            variable = list_[1][0] + '(' + list_[1][1] + ')'
            list_[0][0] = list_[1][0]
            def_str = 'def {}:\n\t'.format(variable)
            list_.pop(1)
            if_str = to_python(list_).replace('\n', '\n\t')
            def_str += if_str
            def_str += 'return ' + list_[0][0]
            return def_str
    elif list_[0][1] == 'program':  # if elif else
        variable = list_[0][0]
        npwhere_str = variable + ' = '
        for i, l in enumerate(list_[2:], 0):
            if (l[0].count('>') + l[0].count('<') > 1) & (l[0].count('&') == 0):
                l[0] = l[0].split('x')
                l[0] = '(' + 'x) & (x'.join(l[0]) + ')'
            if list_[1][i] == 'ifThen':
                npwhere_str += 'np.where({}, {}, '.format(l[0], l[1])
            else:  # otherwise
                npwhere_str += '{}'.format(l[0]) + ')' * (len(list_[2:]) - 1) + '\n'
        return npwhere_str

xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - N-My-1.xmcdz'
# xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - Shear Rec beam Vy.xmcdz'
xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - Torsion Rec beam-1.xmcd'
# xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - N-My-1.xmcdz'
dupson = gzip.open(xml_path, 'r')
try:
    tree = et.parse(dupson)
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
all_comm = []
formulas = []
dupa = []
all_defintion = root.findall('.//ml:define', ns)

python_str = 'import math\nimport numpy as np\nmm = 1\ncm = 10 *mm\nN = 1\nkN = 1000 * N\nMPa = N/mm**2\nm = 1000 * mm\nπ = math.pi\n'

python_str += 'def Misko():\n'

vars = ['V_u', 'T_u']
df = pd.DataFrame([[337, 2034], [619, 838]], columns=vars)


# xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\output.xml'
# df_in = my_xml_parse_to_df(xml_path, 'Sections')
# df = my_xml_parse_to_df(xml_path, 'cross-sections')

# df = df_in[['N', 'V_y', 'V_z', 'M_x', 'M_y', 'M_z']].astype('float64')
#
# df['N_u'] = -df['N']
# df['V_u'] = df[['V_y', 'V_z']].abs().max(axis=1)
#
# df['T_u'] = df['M_x']
# print(df)
# print(df['N_u'].isnull().values.any())

# vars = ['N_u', 'V_u', 'T_u']
# df = pd.DataFrame([[1008000, 1172000000], [970000, 7390 * 10**6]], columns=vars)

# print(df)
# print(str(df['N_u'].to_numpy()))
# print(df['N_u'].to_numpy())
for i, elem in enumerate(all_defintion):

    pupa = []
    # kupa = []
    pupa = make_list_of_lists(elem, pupa)
    # print(i)
    # print(pupa)

    kupa = make_equ(pupa)
    # print(i)
    # print(*kupa, '\n')
    if kupa[0][0] == 'function':
        var = ''
    else:
        var = kupa[0][0]

    if var in vars:
        python_str += '\t' + var + ' = ' + 'np.array({})'.format(df[var].to_list()) + '\n' #+ 'print("{} = ",  "{}")'.format(var, str(df[var].to_numpy())) + '\n'
    elif var:
        python_str += '\t' + to_python(kupa) + '\n' #'\n\t' + 'print("{} = ",  {})'.format(var, var) + '\n'
    else:
        python_str += '\t' + to_python(kupa) + '\n'
    # pipa = eval_equ(kupa)
    # print(*pipa)

    # exprs = [el.tag[36:] for el in elem.iter()]
    # print(get_var(elem[0]))
    # print(exprs, '\n')

python_str += '\treturn A_l, '

with open('my_file.py', 'w', encoding='utf-8') as f:
    f.write(python_str)

# import time
# st = time.time()
# exec(open("my_file.py", encoding='utf-8').read())

from my_file import Misko
pipa = Misko()
# en = time.time()
# print(en-st)
print(pipa)
# print(np.max(pipa), np.argmax(pipa))
# print(df.at[1279, 'N_u'], df.at[1279, 'V_u'], df.at[1279, 'T_u'])
# print(df.at[200, 'N_u'], df.at[200, 'V_u'], df.at[200, 'T_u'])