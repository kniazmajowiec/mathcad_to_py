import xml.etree.ElementTree as et
import xml.dom.minidom as md
import pandas as pd
import numpy as np
import gzip
import re

xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - N-Mz-1.xmcdz'
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
      '': "http://schemas.mathsoft.com/worksheet30",
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

for elem in all_defintion:

    if elem.tag[36:] == 'define' and elem[0].text == 'b':
        print('zmienilem')
        pupa = elem.find('.//ml:real', ns)
        pupa.text = "180"

prettyXML = md.parseString(re.sub(r'\n+\t*\s*', '', et.tostring(root, encoding='unicode'))).toprettyxml()
with open('dupa.xmcd', 'w', encoding='utf-8') as f:
    f.write(prettyXML)