from altair.vegalite.v4.api import value
from numpy.core.fromnumeric import sort
import streamlit as st
#import streamlit_analytics
import pandas as pd
import altair as alt
import pydeck as pdk
import os
import re
import roman

path = os.path.dirname(__file__)

@st.cache
def rundschreiben_data():
    df = pd.read_csv(f'{path}/rundschreiben_geo_neu.csv', sep=';', usecols=['idn','year', 'ort_name', 'ort_idn', 'lat', 'lon'])
    df.set_index(['year', 'ort_name'], inplace=True)
    df.sort_index(inplace=True)
    return df
    

def rundschreiben():
    st.subheader('Buchhändlerische Geschäftsrundschreiben')
    with st.beta_expander("Informationen zum Bestand"):
        st.markdown('''
Mit rund 25.000 buchhändlerischen Geschäftsrundschreiben besitzen wir die weltweit größte Sammlung dieser Textgattung. Die meist ein- oder zweiseitig gedruckten Mitteilungen (auch Zirkulare genannt) entstammen überwiegend deutschen, aber auch ausländischen Verlagen und Buchhandlungen. Zeitlich ordnen sich die Zirkulare in die Zeit von 1737 bis zur Mitte des 20. Jahrhunderts ein. Sie belegen zum Beispiel die Gründung oder das Erlöschen einer Firma, die Änderung der Inhaberschaft oder Namensänderungen. [Zur gesamten Sammlung im Katalog des DBSM](https://d-nb.info/dnbn/103243757X).
        ''')
    df = rundschreiben_data()

    filter = st.slider('Zeitraum', min_value=df.index.min()[0], max_value=df.index.max()[0], value=(1850,1900))
    
    filt_frame = df.loc[filter[0]:filter[1]].drop_duplicates(subset=['ort_idn']).dropna(how='any').reset_index()
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        filt_frame.reset_index(),
        pickable=True,
        filled=True,
        opacity=0.8,
        stroked=True,
        get_position='[lon, lat]',
        get_radius=3,
        auto_highlight=True,
        radius_units='pixels',
        get_fill_color=[52, 133, 28],
        get_line_color=[37, 87, 47],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )

    st.pydeck_chart(pdk.Deck(
        scatter_layer,
        initial_view_state=pdk.data_utils.compute_view(filt_frame[["lon", "lat"]], view_proportion=0.92),
        map_style=pdk.map_styles.LIGHT,
        tooltip={"html": "<b>{ort_name}</b>"}
    ))
    st.caption('Die Karte zeigt 92% aller Datenpunkte. Zoomen Sie weiter heraus, um alle Daten zu sehen.')
    #top diagramm
    #zeiten
    st.subheader('Anzahl der Rundschreiben pro Jahr')
    rundschreiben_zeit = alt.Chart(filt_frame.reset_index()).mark_bar().transform_bin("year_binned", "year", bin=alt.Bin(maxbins=48, extent=[1737,1971])).encode(
        alt.X('year_binned:O', title='Jahr'),
        alt.Y('count(year):Q', title='Anzahl'),
        tooltip=[alt.Tooltip('year:O', title='Jahr'), alt.Tooltip('count(year):Q', title='Anzahl')],
        color='count(year):Q'
    )
    st.altair_chart(rundschreiben_zeit, use_container_width=True)

def zeitverteilung():
    st.subheader('Entstehungszeit der Objekte in der Sammlung')
    df = pd.read_csv(f'{path}/zeit.csv')
    count = pd.DataFrame(pd.value_counts(df.year))
    count = count.rename(columns={'year':'count'})
    count.index.rename('year', inplace=True)
    
    zeit = alt.Chart(count.reset_index()).mark_bar().transform_bin("year_binned", "year", bin=alt.Bin(maxbins=32, extent=[1400,2021])).encode(
        alt.X('year_binned:N', title='Entstehungsjahr', scale=alt.Scale(zero=False)),
        alt.Y('count:Q', title='Anzahl'),
        tooltip=[alt.Tooltip('year', title='Jahr'), alt.Tooltip('count', title='Anzahl')],
        color='count:Q'
    )
    return st.altair_chart(zeit, use_container_width=True)
    
def neueste():
    st.subheader('Neueste Datensätze')
    st.markdown('Derzeit sind hier viele Titel mit Bezug zur Zeit des Nationalsozialismus zu sehen. Diese Titel stammen aus der Plakatsammlung des DBSM, wo in einem Projekte Plakate aus den vom nationalsozialistischen Deutschland besetzten Ländern während des 2. Weltkriegs erschlossen werden.')
    df = pd.read_csv(f'{path}/erfassung.csv', index_col='idn')
    df.erfassungsdatum = pd.to_datetime(df.erfassungsdatum.str.slice(5), dayfirst=True)

    col1, col2 = st.beta_columns(2)
    i = 1
    for index, row in df.nlargest(21, columns='erfassungsdatum')[1:].iterrows():
        text = f'{i}. [{row["titel"]} / {row["person"]}](https://d-nb.info/{index})'
        if i <= 10:
            with col1:
                st.write(text)
        elif i > 10:
            with col2:
                st.write(text)
        i += 1

def inkunabeln():
    st.subheader('Inkunabeldruckorte im DBSM')
    with st.beta_expander('Informationen zum Bestand'):
        st.markdown('Handschriften, Inkunabeln, Renaissancedrucke, Künstlerbücher und wertvolle Bucheinbände – diese besonderen Bestände befinden sich in den Musealen Buchsammlungen des Deutschen Buch- und Schriftmuseums. 1886 kaufte der sächsische Staat für das gerade gegründete Museum 3.000 historische Drucke des Dresdner Schneiders, Verlegers und Büchersammlers Heinrich Klemm an. Die Klemm-Sammlung bildet den Grundstock für den umfangreichen musealen Buchbestand. [zur ausführlichen Sammlungsbeschreibung](https://www.dnb.de/DE/Sammlungen/DBSM/MusealeBuchsammlungen/musealeBuchsammlungen_node.html)')
    df = pd.read_csv(f'{path}/inkunabel_count.csv')
    ink_all = pdk.Layer(
        'ScatterplotLayer',
        df.dropna(axis=1, how='any'),
        pickable=True,
        filled=True,
        opacity=0.8,
        stroked=True,
        get_position='[lon, lat]',
        get_radius=6,
        auto_highlight=True,
        radius_units='pixels',
        get_fill_color=[33, 48, 209],
        get_line_color=[16, 24, 112],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )

    ink_dbsm = pdk.Layer(
        'ScatterplotLayer',
        df[pd.notna(df['dbsm_count'])].dropna(axis=1, how='any'),
        pickable=True,
        filled=True,
        opacity=0.8,
        stroked=True,
        get_position='[lon, lat]',
        get_radius=3,
        auto_highlight=True,
        radius_units='pixels',
        get_fill_color=[62, 222, 131],
        get_line_color=[27, 94, 46],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )

    st.pydeck_chart(pdk.Deck(
        [ink_all, ink_dbsm],
        initial_view_state=pdk.data_utils.compute_view(df[["lon", "lat"]], view_proportion=1),
        map_style=pdk.map_styles.LIGHT,
        tooltip={"html": "<b>{druckort}</b>, {dbsm_count} Exemplar(e)"}
    ))

    st.caption('Blau sind alle bekannten Inkunabeldruckorte dargestellt, grün die Orte, aus denen sich Exemplare im DBSM befinden.')

def objektgattungen():
    st.subheader('Objektgattungen')
    df_gattungen = pd.read_csv(f'{path}/objektgattung.csv')
    
    gattungen = alt.Chart(df_gattungen[:20]).mark_bar().encode(
        alt.X('gattung:N', title='Gattungen', sort='-y'),
        alt.Y('n:Q', title='Anzahl'),
        alt.Color('gattung:N', legend=alt.Legend(columns=2), sort='-y', title='Objektgattungen'),
        tooltip=[alt.Tooltip('gattung:N', title='Gattung'), alt.Tooltip('n:Q', title='Anzahl')]
    )

    st.altair_chart(gattungen, use_container_width=True)

@st.cache
def herstellungsorte_data():
    return pd.read_csv(f'{path}/herstellungsorte_geo.csv', usecols=['idn', 'ort', 'lat', 'lon'], index_col='idn', sep=';')

def herstellungsorte():
    st.subheader('Herstellungsorte der Sammlungsobjekte')
    df_herstellungsorte = herstellungsorte_data()
    df_filt = df_herstellungsorte.merge(df_herstellungsorte.ort.value_counts(), left_on='ort', right_index=True).drop(['ort_x'], axis=1).rename({'ort_y':'count'}, axis=1).drop_duplicates(subset='ort').dropna(how='any').sort_values(by='count', ascending=True)

    herstellungsorte_map = pdk.Layer(
        'ScatterplotLayer',
        df_filt,
        pickable=True,
        filled=True,
        opacity=0.8,
        stroked=True,
        get_position='[lon, lat]',
        get_radius=3,
        auto_highlight=True,
        radius_units='pixels',
        get_fill_color=[36, 209, 166],
        get_line_color=[20, 117, 93],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )

    st.pydeck_chart(pdk.Deck(
        herstellungsorte_map,
        initial_view_state=pdk.data_utils.compute_view(df_filt[["lon", "lat"]], view_proportion=0.92),
        map_style=pdk.map_styles.LIGHT,
        tooltip={"html": "{count} Objekte aus {ort}"}
    ))

    st.caption('Alle Objekte mit eindeutig zuzuordnendem Entstehungsort wurden ausgewertet. Fährt man mit der Maus über den jeweiligen Punkt, sieht man, wieviele Objekte es von diesem Ort im Bestand gibt.')

@st.cache
def buchbestand_data():
    df = pd.read_csv(f'{path}/buchbestand_plus.csv', usecols=['idn','year','verlag_ort','herst_ort_name','seiten','groesse'])
    orte = pd.read_csv(f'{path}/dbsm_orte.csv')
    # zuerst werden koordinaten auf herst_ort_name gemappt, dann werden alle zeilen, in denen diese spalte NaN ist, aber verlag_ort existiert, mit verlag_ort gemappt. übrig bleibt ein df, in dem alle zeilen koordinaten haben
    return pd.concat([df[pd.notna(df['herst_ort_name'])].merge(orte, how='left', left_on='herst_ort_name', right_on='ort'),df[pd.isna(df['herst_ort_name']) & pd.notna(df['verlag_ort'])].merge(orte, how='left', left_on='verlag_ort', right_on='ort')])

def buchbestand():
    with st.beta_expander('Informationen zum Bestand'):
        st.markdown('Handschriften, Inkunabeln, Renaissancedrucke, Künstlerbücher und wertvolle Bucheinbände – diese besonderen Bestände befinden sich in den Musealen Buchsammlungen des Deutschen Buch- und Schriftmuseums. 1886 kaufte der sächsische Staat für das gerade gegründete Museum 3.000 historische Drucke des Dresdner Schneiders, Verlegers und Büchersammlers Heinrich Klemm an. Die Klemm-Sammlung bildet den Grundstock für den umfangreichen musealen Buchbestand. [zur ausführlichen Sammlungsbeschreibung](https://www.dnb.de/DE/Sammlungen/DBSM/MusealeBuchsammlungen/musealeBuchsammlungen_node.html)')


    df = buchbestand_data()
    zeitslider = st.slider('Auswertungszeitraum', min_value=int(df.year.min()), max_value=int(df.year.max()), value=(int(df.year.min()),int(df.year.max())))
    df_zeit = df[(df.year >= zeitslider[0]) & (df.year <= zeitslider[1])]
    df_karte = df_zeit.merge(df_zeit.ort.value_counts(), left_on='ort', right_index=True).drop(['ort_x', 'year'], axis=1).rename({'ort_y':'count'}, axis=1).drop_duplicates(subset='ort').dropna(how='any').sort_values(by='count', ascending=True)
    df_umfang = df_zeit.seiten.value_counts()

    herstellungsorte_map = pdk.Layer(
        'ScatterplotLayer',
        df_karte,
        pickable=True,
        filled=True,
        opacity=0.8,
        stroked=True,
        get_position='[lon, lat]',
        get_radius=3,
        auto_highlight=True,
        radius_units='pixels',
        get_fill_color=[36, 209, 166],
        get_line_color=[20, 117, 93],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )
    st.subheader('Herstellungsorte des Buchbestands')
    st.pydeck_chart(pdk.Deck(
        herstellungsorte_map,
        initial_view_state=pdk.data_utils.compute_view(df_karte[["lon", "lat"]], view_proportion=0.92),
        map_style=pdk.map_styles.LIGHT,
        tooltip={"html": "{count} Objekte aus {ort}"}
    ))

    st.subheader('Anzahl Bücher nach Erscheinungsjahr')
    count = pd.DataFrame(pd.value_counts(df_zeit.year))
    count = count.rename(columns={'year':'count'}).sort_index()
    count.index.rename('year', inplace=True)
    
    zeit = alt.Chart(count.reset_index()).mark_bar().transform_bin("year_binned", "year", bin=alt.Bin(maxbins=32, extent=[1400,2021])).encode(
        alt.X('year_binned:N', title='Entstehungsjahr', scale=alt.Scale(zero=False)),
        alt.Y('count:Q', title='Anzahl'),
        tooltip=[alt.Tooltip('year', title='Jahr'), alt.Tooltip('count', title='Anzahl')],
        color=alt.Color('count:Q')
    )
    st.altair_chart(zeit, use_container_width=True)
    df['jahrzehnt'] = (10 * (df['year'] // 10)).astype(str)

    st.subheader('Verteilung des Umfangs')
    st.write('Je älter die Bücher, desto mehr Seiten haben sie? Nicht ganz: die Wahrscheinlichkeit ist nur größer, dass ein sehr dickes, schweres Buch viele Jahrhunderte überlebt. Kleine, dünne Hefte hingegen verschwinden schneller und waren auch nicht unbedingt dafür gedacht, lange in Bibliotheken aufbewart zu werden.')
    form = alt.Chart(df.groupby('jahrzehnt').median('seiten').reset_index()).mark_line().encode(
        alt.X('jahrzehnt:O', axis=alt.Axis(title='Erscheinungsjahr', labelOverlap='greedy')),
        y = 'seiten:Q',
        tooltip=[alt.Tooltip('jahrzehnt:O', title='Jahrzehnt'), alt.Tooltip('seiten:Q', title='Median d. Seitenzahl')]
    )
    st.altair_chart(form, use_container_width=True)

    st.subheader('Verteilung der Buchgröße')
    groesse = alt.Chart(df.groupby('jahrzehnt').median('groesse').reset_index()).mark_line().encode(
        alt.X('jahrzehnt:O', axis=alt.Axis(title='Erscheinungsjahr', labelOverlap='greedy')),
        y = 'groesse:Q',
        tooltip=[alt.Tooltip('jahrzehnt:O', title='Jahrzehnt'), alt.Tooltip('groesse:Q', title='Median d. Buchgröße')]
    )
    st.altair_chart(groesse, use_container_width=True)

@st.cache
def wasserzeichen_data():
    return pd.read_csv(f'{path}/wz_geo.csv', sep=';')

def wasserzeichen():
    df = wasserzeichen_data()
    with st.beta_expander('Informationen zur Sammlunge'):
        st.markdown('''Unsere Wasserzeichensammlung ist mit mehr als 400.000 Exemplaren die weltweit größte Sammlung dieser Art. 1897 begann Karl Theodor Weiß (1872–1945) damit, nach wissenschaftlichen Gesichtspunkten Wasserzeichen zusammenzutragen. 1957 bot sein Sohn Wisso Weiß (1904–1991) diese Sammlungen zum Kauf an. Sie kamen in den Besitz des Deutschen Papiermuseums in Greiz (Thüringen). Seit 1964 sind dessen Bestände Eigentum des Deutschen Buch- und Schriftmuseums der Deutschen Nationalbibliothek.
Die Sammlungen enthalten sowohl originale Papiere als auch Reproduktionen von Wasserzeichen (Handpausen oder Kopien). Sie dienen als Grundlage für die Echtheitsprüfung sowie die Herkunfts- und Altersbestimmung von Papieren. [zur Sammlung im Katalog des DBSM](https://portal.dnb.de/opac.htm?method=simpleSearch&cqlMode=true&query=idn%3D1048061809)''')
    st.subheader('Verwendungszeitraum der Wasserzeichenbelege')
    fig_von_bis = alt.Chart(df).mark_bar().encode(
        alt.X('ab:O', axis=alt.Axis(title='Nachweiszeitraum', labelOverlap='greedy', labelAngle=-60)),
        alt.X2('bis:O'),
        alt.Y('Name:N', title='Herstellungsort'),
        tooltip=['Name', 'ab', 'bis'],
    )
    st.altair_chart(fig_von_bis, use_container_width=True)

    herstellungsorte_map = pdk.Layer(
        'ScatterplotLayer',
        df,
        pickable=True,
        filled=True,
        opacity=0.8,
        stroked=True,
        get_position='[lon, lat]',
        get_radius=3,
        auto_highlight=True,
        radius_units='pixels',
        get_fill_color=[36, 209, 166],
        get_line_color=[20, 117, 93],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )
    st.subheader('Herstellungsorte der Wasserzeichenbelege')
    st.pydeck_chart(pdk.Deck(
        herstellungsorte_map,
        initial_view_state=pdk.data_utils.compute_view(df[["lon", "lat"]], view_proportion=1),
        map_style=pdk.map_styles.LIGHT,
        tooltip={"html": "{Anzahl} Wasserzeichenbelege aus {Name} zwischen {ab} und {bis}"}
    ))

    st.markdown('Bisher ist nur ein Teil der Wasserzeichensammlung erschlossen und im elektronischen Katalog nachgewiesen. Wie man in dieser Karte sieht, handelt es sich um die Wasserzeichen der Papiermühlen aus Thüringen.')

#main

#streamlit_analytics.start_tracking()

st.title('DBSM Dashboard')

with st.beta_container():
    st.warning('Verwenden Sie einen auf Chromium basierenden Browser.')

st.sidebar.header("Sammlungsteil wählen")
sammlung = st.sidebar.selectbox(
    "Über welchen Teil der DBSM-Sammlungen möchten Sie mehr erfahren?",
    ('Sammlung allgemein', 'Buchbestand', "Geschäftsrundschreiben", "Inkunabeln", "Wasserzeichen")
)
st.sidebar.info('Auf diesem Dashboard werden einige Sammlungsteile des [Deutschen Buch- und Schriftmuseums](https://www.dnb.de/dbsm) der [Deutschen Nationalbibliothek](https://www.dnb.de) grafisch ausgewertet und aufbereitet. Wählen Sie links den Sammlungsteil, der Sie interessiert, und Sie erhalten die verfügbaren Auswertungen und Statstiken. (Stand der Daten: Juni 2021). Dieses Dashboard wurde erstellt von [ramonvoges](https://github.com/ramonvoges) und [a-wendler](https://github.com/a-wendler/).')

with st.sidebar.beta_expander("Methodik und Datenherkunft"):
        st.markdown('''
Datengrundlage ist ein Gesamtabzug der Daten des Buch- und Objektbestands des Deutschen Buch- und Schriftmuseums (DBSM).

Der Gesamtabzug liegt im OCLC-Format PICA+ vor. Die Daten werden mithilfe des Pica-Parsers [pica.rs](https://github.com/deutsche-nationalbibliothek/pica-rs) gefiltert. Dieses Tool produziert aus dem sehr großen Gesamtabzug (~ 31 GB) kleinere CSV-Dateien, die mit Python weiterverarbeitet werden.

Das Dashboard ist mit dem Python-Framework [Streamlit](https://streamlit.io/) geschrieben. Die Skripte sowie die gefilterten CSV-Rohdaten sind auf [Github](https://github.com/buchmuseum/dbsm-dashboard) zu finden. Die Diagramme wurden mit [Altair](https://altair-viz.github.io/index.html) erstellt, die Karten mit [Deck GL](https://deck.gl/) (via [Pydeck](https://deckgl.readthedocs.io/en/latest/#)).

Für grundlegende Zugriffsstatistik verwenden wir [streamlit-analytics](https://pypi.org/project/streamlit-analytics/). Dabei werden keine personenbezogenen Daten gespeichert.

Alle Skripte und Daten stehen unter CC0 Lizenz und können frei weitergenutzt werden.

Die Daten werden halbjährlich aktualisiert.
''')

allgemein = st.beta_container()
with allgemein:
    
    #allgemeine statistiken
    if sammlung == 'Sammlung allgemein':
        st.header('Sammlung allgemein')
        zeitverteilung()
        herstellungsorte()
        neueste()
        objektgattungen()
    
    elif sammlung == 'Buchbestand':
        st.header('Museale Buchbestände')
        buchbestand()
    
    elif sammlung == 'Geschäftsrundschreiben':
        st.header('Buchhändlerische Geschäftsrundschreiben')
        rundschreiben()
    
    elif sammlung == "Inkunabeln":
        st.header('Inkunabeln')
        inkunabeln()
    
    elif sammlung == 'Wasserzeichen':
        st.header('Wasserzeichen')
        wasserzeichen()


#streamlit_analytics.stop_tracking()