import xml.etree.cElementTree as et
import gzip
import numpy as np
xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - N-My-1.xmcdz'

repl_dict = {'define': '=', 'id': '', 'apply': '', 'mult': '*', 'real':'', 'program': '', 'ifThen': 'if',
             'lessThan': '<', 'greaterThan': '>', 'otherwise': 'else', 'parens': '', 'minus': '-', 'div': '/',
             'pow': '**', 'plus': '+', 'absval': 'abs', 'neg':'-', 'function': '', 'boundVars': '', 'lessOrEqual': '<=',
             'str': 'str', 'sequence': '', 'greaterOrEqual': '>=', 'sqrt': 'np.sqrt', 'or': '|', 'equal': '==',
             'notEqual': '!=', 'and': '&'}

def get_var(el):
    if el.text:
        try:
            return el.text + '_' + el.attrib['subscript']
        except KeyError:
            return el.text
    else:
        return el.tag[36:]

dupson = gzip.open(xml_path, 'r')
tree = et.parse(dupson)
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

all_defintion = root.findall('.//ml:define', ns)
for elem in all_defintion:

    if elem[0].text == 'As' and elem[0].attrib['subscript'] == 'top':
        exprs = [{el.tag[36:]: len([ch.tag[36:] for ch in el.findall('./') if ch is not el])} for el in elem.iter()]
        print(exprs)
        form = []
        for ex in exprs:

            form.append
        exprs = [el.tag[36:] for el in elem.iter()]
        print(exprs)
        ids = [get_var(el) for el in elem.findall('.//ml:id', ns)]
        # print(ids)
        reals = [get_var(el) for el in elem.findall('.//ml:real', ns)]
        # print(reals)
        strs = [get_var(el) for el in elem.findall('.//ml:str', ns)]
        # print(strs, '\n')
        formula = []
        # form = exprs
        #
        # i = 0
        # while i < len(exprs):
        #     e = exprs[i]
        #     if e in ['define', 'mult', 'ifThen', 'lessThan', 'greaterThan', 'minus', 'div', 'pow', 'plus', 'absval', 'neg',
        #              'lessOrEqual', 'greaterOrEqual', 'sqrt', 'or', 'equal', 'notEqual', 'and']:
        #         form.insert(i+1, form.pop(i))
        #         i += 2
        #     else:
        #         i += 1
        for i, e in enumerate(exprs):
            if e == 'id':
                formula.append(ids.pop(0))
            elif e == 'real':
                formula.append(reals.pop(0))
            elif e == 'str':
                formula.append(strs.pop(0))
            else:
                formula.append(repl_dict[e])
        print(formula, '\n')

# for elem in root.iter():
#     if elem.tag =='{http://schemas.mathsoft.com/math30}define':
#         formula = []
#         for el in elem.iter():
#             if el.tag == '{http://schemas.mathsoft.com/math30}id':
#                 try:
#                     variable = el.text + '_' + el.attrib['subscript']
#                 except KeyError:
#                     variable = el.text
#                 formula.append(variable)
#             if el.tag[36:] not in all_comm:
#                 all_comm.append(el.tag[36:])
#         print(formula)
# print(all_comm, '\n', len(all_comm))