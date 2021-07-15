import pandas as pd
from tqdm import tqdm
import re
import roman

checkliste = ['Kupfert',
              'Tit',
              'Titel',
              'Kupfertitel',
              'Titelbl',
              'Kupfertit',
              'Bildertit',
              'Frontisp',
              'Kupferfrontispiz',
              'Kupferfrontisp',
              'Porträtkupf',
              'Vort',
              'Portr.-Kupf.',
              'Frontispiz',
              'Front',
              'Port. Kupf.']

buchformate = {'gr. 2': 45, '2': 40, 'gr. 4': 35, '4': 30, 'lex. 8': 25, 'gr. 8': 22.5, '8': 18.5, 'kl. 8': 15, '16': 10}

def seiten_ermitteln(umfang):
    seiten = 0
    fehlseiten = []
    merkliste = []
    try:
        for element in umfang.split(','):
            #print(element)
            if re_find := re.search('\[?(\d+)\]?\s.*\s?(Bl|Sp|S|Faltbl|Taf|Kupf|Blätter|Seiten|Spalten).*', element.strip()):
                    if re_find.group(2) == 'Bl' or re_find.group(2) == 'Faltbl' or re_find.group(2) == 'Taf' or re_find.group(2) == 'Blätter' or re_find.group(2) == 'Kupf':
                        seiten += int(re_find.group(1)) * 2
                        #print('finde bl')
                        if len(merkliste) > 0:
                            for zahl in merkliste:
                                seiten += zahl * 2
                            merkliste = []
                    elif re_find.group(2) == 'S' or re_find.group(2) == 's' or re_find.group(2) == 'Seiten':
                        #print('finde s')
                        seiten += int(re_find.group(1))
                        if len(merkliste) > 0:
                            for zahl in merkliste:
                                seiten += zahl
                            merkliste = []
                    elif re_find.group(2) == 'Sp' or re_find.group(2) == 'Spalten':
                        seiten += int(re_find.group(1))/4
                        #print(f'{re_find.group(1)} Spalten = {str(int(re_find.group(1))/4)} Seiten')
                    else:
                        None
            elif re_find := re.search('(^(?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3}))(\s(?P<typ>S|Bl|Seiten|Blätter|Taf|Tafeln\.))?.*$', element.strip()):
                    if re_find.group('typ')  == 'S' or re_find.group('typ') == 'Seiten':
                        seiten += roman.fromRoman(re_find.group(1).strip())
                        if len(merkliste) > 0:
                            for zahl in merkliste:
                                seiten += zahl
                            merkliste = []

                    elif re_find.group('typ')  == 'Bl' or re_find.group('typ') == 'Blätter' or re_find.group('typ')== 'Taf' or re_find.group('typ') == 'Tafeln':
                        seiten += roman.fromRoman(re_find.group(1).strip()) * 2
                        if len(merkliste) > 0:
                            for zahl in merkliste:
                                seiten += zahl * 2
                            merkliste = []
                    else:
                        merkliste.append(roman.fromRoman(re_find.group(1).strip()))
            elif re_find := re.search('(?P<typ>S\.|Seiten)\s?(?P<von>\d+)\s?-\s?(?P<bis>\d+)', element.strip()):
                    seiten += int(re_find.group('bis')) - int(re_find.group('von'))
                    if len(merkliste) > 0:
                            for zahl in merkliste:
                                seiten += zahl
                            merkliste = []
            elif re_find := re.search('Bl.\s?(\d+)\s?-\s?(\d+)', element.strip()):
                    seiten += (int(re_find.group(2)) - int(re_find.group(1))) * 2
                    if len(merkliste) > 0:
                            for zahl in merkliste:
                                seiten += zahl * 2
                            merkliste = []
            elif re_find := re.search('Sp.\s?(\d+)\s?-\s?(\d+)', element.strip()):
                    seiten += (int(re_find.group(2)) - int(re_find.group(1))) / 2
                    if len(merkliste) > 0:
                            for zahl in merkliste:
                                seiten += zahl / 4
                            merkliste = []
            elif any(i in element.strip() for i in checkliste):
                    seiten += 2
            elif re_find := re.match('\[?(\d+)\]?', element.strip()):
                    merkliste.append(int(re_find.group(1)))
            else:
                fehlseiten.append(element)
    except Exception as e:
        seiten = 0
        #print(e)
    return int(seiten)#, fehlseiten

def groesse_ermitteln(format):
    if re_find := re.search(r'(\d*,?\d+)\s{1}cm', format):
        return float(re_find.group(1).replace(',','.'))
    elif re_find := re.search(r"((gr\.\s?|kl\.?\s?)?(\d{1,2}))°?", format):
        if re_find.group(1) in buchformate.keys():
            return buchformate[f'{re_find.group(1)}']
    else:
        return float("NaN")

df = pd.read_csv('buchbestand.csv')
df['seiten'] = df.umfang.map(seiten_ermitteln, na_action='ignore')
df['groesse'] = df.format.map(groesse_ermitteln, na_action='ignore')

df_filt = df[df.year.str.len() == 4]
df_filt.year = df_filt.year.str.replace('x', '0', case=False)

df.to_csv('buchbestand_formate.csv', index=None)