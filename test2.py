import xml.etree.ElementTree as et
import pandas as pd
import gzip


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
                list_.insert(j, '[{}]'.format(','.join(list_of_lists[k+1])))
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
             'notEqual': '!=', 'and': '&', 'min': 'min', 'max': 'max'}


def fun(lol):
    if lol[0] in ['mult', 'lessThan', 'greaterThan', 'minus', 'plus',
                  'lessOrEqual', 'greaterOrEqual', 'equal', 'notEqual']:
        lol[0] = repl_dict[lol[0]]
        lol.insert(1, lol.pop(0))
        # try:
        return ' '.join(lol)
        # except TypeError:
        #     return '?'
    elif lol[0] in ['div', 'pow', 'or', 'and']:
        lol[0] = repl_dict[lol[0]]
        lol.insert(1, lol.pop(0))
        parens_1 = '({})'.format(lol[0]) if ' ' in lol[0] else lol[0]
        parens_2 = '({})'.format(lol[2]) if ' ' in lol[2] else lol[2]
        return ' '.join([parens_1, lol[1], parens_2])
    elif lol[0] in ['min', 'absval', 'sqrt', 'neg', 'max']:
        lol[0] = repl_dict[lol[0]]
        return lol[0] + '(' + ''. join(lol[1:]) + ')'
    # elif lol[0] in ['if']:
    #     # print(lol)
    #     seq = lol[1:][0][1:-1] # delete square brackets
    #     # seq = exec(lol[1:][0])
    #     print(seq)
    #     seq = seq.split(', ')
    #     return ' '.join([seq[1], lol[0], seq[0], 'else', seq[2]])
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
        # if_str = 'if {}:\n'.format(list_[2][0])
        # if_str += '\t {}={}\n'.format(variable, list_[2][1])
        # for i, l in enumerate(list_[3:], 1):
        #     if list_[1][i] == 'ifThen':
        #         if_str += 'elif {}:\n'.format(l[0])
        #         if_str += '\t {}={}\n'.format(variable, l[1])
        #     else:
        #         if_str += 'else:\n'.format(l[0])
        #         if_str += '\t {}={}\n'.format(variable, l[0])

        npwhere_str = variable + ' = '
        for i, l in enumerate(list_[2:], 0):
            if list_[1][i] == 'ifThen':
                npwhere_str += 'np.where({}, {}, '.format(l[0], l[1])
            else:  # otherwise
                npwhere_str += '{}'.format(l[0]) + ')' * (len(list_[2:]) -1) + '\n'
        return npwhere_str

xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - N-My-1.xmcdz'
# xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - Shear Rec beam Vy.xmcdz'
# xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - Torsion Rec beam-1.xmcd'
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

b_index = [i for i, e in enumerate(all_defintion) if e[0].text == 'b']
print(b_index)
python_str = 'import math\nimport numpy as np\nmm = 0.001\ncm = 10 *mm\nN = 1\nkN = 1000 * N\nMPa = N/mm**2\nm = 1000 * mm\nπ = math.pi\n'

# vars = ['N_u', 'T_u']
# df = pd.DataFrame([[-100, -200], [-400, -500]], columns=vars)
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

    # print(to_python(kupa), '\n')
    # if var in vars:
    # python_str += var + ' = ' + 'np.array({})'.format(df[var].to_list()) + '\n' + 'print("{} = ",  "{}")'.format(var, str(df[var].to_numpy())) + '\n'
    # else:
    if var:
        python_str += to_python(kupa) + '\n' + 'print("{} = ",  {})'.format(var, var) + '\n'
    else:
        python_str += to_python(kupa) + '\n'
    # pipa = eval_equ(kupa)
    # print(*pipa)

    # exprs = [el.tag[36:] for el in elem.iter()]
    # print(get_var(elem[0]))
    # print(exprs, '\n')

with open('my_file2.py', 'w', encoding='utf-8') as f:
    f.write(python_str)

import time
st = time.time()
exec(open("my_file2.py", encoding='utf-8').read())
en = time.time()
print(en-st)