from helper_functions import *
from my_file import calc

xml_math = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\ACI 318-14 - N-My-1.xmcdz'
xml_scia = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Caroline\output.xml'
case = 'N+M'

tables = get_xml_table_names(xml_scia)
table_name = 'Sections'

print('Analysing mathcad file...')
all_define = get_define_from_mathcad(xml_math)
df = my_xml_parse_to_df(xml_scia, table_name)
df_in, cols = input_df(df, case)
df_in['n_1'] = 2
print(df_in)
df = calc(df_in)
print(df)
for i in range(3, 20):
    if (df['Result'] == 'ok').all():
        break
    df['n_1'] = np.where(df['Result'] == 'ok', df['n_1'], i)
    df = calc(df)
print('\n', df)

max_n1 = df['n_1'].max()
max_n2 = df['n_2'].max()

df_max = df.loc[(df['n_1'] == max_n1) & (df['n_2'] == max_n2)]
df_max = df_max.sort_values(by=['Mu', 'Pu'], ascending=[False, False]).reset_index()

print(df_max)
# df_max = pd.DataFrame
int_force_in_mathcad = [col for col in df_in.columns if col not in ['Case', 'Name', 'dx']]
int_force_in_mathcad = []
mathcad_file = 'example_mathcad_file.xmcd'
print('Saving mathcad file...')

fill_in_mathcad(xml_math, int_force_in_mathcad, df_max, mathcad_file)

