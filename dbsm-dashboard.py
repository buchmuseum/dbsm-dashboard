from altair.vegalite.v4.api import value
import streamlit as st
import streamlit_analytics
import pandas as pd
import altair as alt
import pydeck as pdk
import os

path = os.path.dirname(__file__)

streamlit_analytics.start_tracking()

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
Hier folgt die Bestandsbeschreibung
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

    """ rundschreiben_orte = alt.Chart(df.reset_index()).mark_bar().encode(
        alt.X('ort_name:O', title='Ort'),
        alt.Y('count(ort_name):Q', title='Anzahl Rundschreiben'),
        color='ort_name:O'
    )
    st.altair_chart(rundschreiben_orte, use_container_width=True) """

def zeitverteilung():
    st.subheader('Entstehungszeit der Objekte in der Sammlung')
    df = pd.read_csv(f'{path}/zeit.csv')
    count = pd.DataFrame(pd.value_counts(df.year))
    count = count.rename(columns={'year':'count'})
    count.index.rename('year', inplace=True)
    
    zeit = alt.Chart(count.reset_index()).mark_bar().transform_bin("year_binned", "year", bin=alt.Bin(maxbins=32, extent=[1400,2021])).encode(
        alt.X('year_binned:O', title='Entstehungsjahr', scale=alt.Scale(zero=False)),
        alt.Y('count:Q', title='Anzahl'),
        tooltip=[alt.Tooltip('year', title='Jahr'), alt.Tooltip('count', title='Anzahl')],
        color='count:Q'
    )
    return st.altair_chart(zeit, use_container_width=True)
    
def neueste():
    st.subheader('Neueste Datensätze')
    st.markdown('Derzeit sind hier viele Titel mit Bezug zur Zeit des Nationalsozialismus zu sehen. Diese Titel stammen aus der Plakatsammlung des DBSM, wo in einem Projekte Plakate aus den vom nationalsozialistischen Deutschland besetzten Ländern während des 2. Weltkriegs erschlossen werden.')
    df = pd.read_csv('erfassung.csv', index_col='idn')
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
    df = pd.read_csv('inkunabel_count.csv')
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
        get_fill_color=[33, 61, 219],
        get_line_color=[33, 61, 219],
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
        get_fill_color=[33, 219, 45],
        get_line_color=[33, 219, 45],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )
    st.pydeck_chart(pdk.Deck(
        [ink_all, ink_dbsm],
        initial_view_state=pdk.data_utils.compute_view(df[["lon", "lat"]], view_proportion=1),
        map_style=pdk.map_styles.LIGHT,
        tooltip={"html": "<b>{druckort}</b>, {dbsm_count} Exemplare"}
    ))
    st.caption('Blau sind alle bekannten Inkunabeldruckorte dargestellt, grün die Orte, aus denen sich Exemplare im DBSM befinden.')

#main
st.title('DBSM Dashboard')
rundschreiben()
zeitverteilung()
neueste()
inkunabeln()

streamlit_analytics.stop_tracking()