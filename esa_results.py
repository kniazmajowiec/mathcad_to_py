import xml.etree.ElementTree as et
import pandas as pd
import os

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


# def get_results_from_xml(xml_path):
#     tree = et.parse(xml_path)
#     root = tree.getroot()
#     et.register_namespace('', "http://www.scia.cz")
#
#     esa_file = os.path.splitext(os.path.basename(xml_path))[0]
#     all_tables = [tab.attrib['name'] for tab in root.findall('.//{http://www.scia.cz}table')
#                   if tab.attrib['t'] == "BasicResults.10.00.EP_InternalForces1D_Shell.1"]
#     results = [esa_file]
#     for tab in all_tables:
#         df = my_xml_parse_to_df(xml_path, tab)
#         try:
#             df['UCOverall'] = df['UCOverall'].astype(float)
#         except ValueError:
#             df['UCOverall'] = df['UCOverall'].astype(str).str.replace(',', '.').astype(float)
#
#         max_UC = df['UCOverall'].max()
#         max_UC_idx = df['UCOverall'].idxmax()
#         beam_max = df.at[max_UC_idx, 'Name']
#         results.extend([tab, beam_max, max_UC])
#     return results

# xml_path = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\output2.xml'
# df = my_xml_parse_to_df(xml_path, 'Sections')
# df = my_xml_parse_to_df(xml_path, 'cross-sections')
# print(df)