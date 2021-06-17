import streamlit as st
import streamlit_analytics
import pandas as pd
import altair as alt
import pydeck as pdk
import os

path = os.path.dirname(__file__)

streamlit_analytics.start_tracking()

def rundschreiben():
    df = pd.read_csv(f'{path}/orte_geo.csv', sep=';')
    df.dropna(
        axis=0,
        how='any',
        thresh=None,
        subset=None,
        inplace=True
    )

    df['norm']=(df['count']-df['count'].min())/(df['count'].max()-df['count'].min())

    scatter_layer = pdk.Layer(
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
        get_fill_color=[52, 133, 28],
        get_line_color=[37, 87, 47],
        line_width_min_pixels=1,
        radius_min_pixels=3,
        radius_max_pixels=10,
    )

    st.pydeck_chart(pdk.Deck(
        scatter_layer,
        initial_view_state=pdk.data_utils.compute_view(df[["lon", "lat"]], view_proportion=0.92),
        map_style=pdk.map_styles.LIGHT,
        tooltip={"html": "<b>{ort}</b><br \>{count} Rundschreiben"}
    ))

    #st.dataframe(df)
    #top diagramm
    #zeiten

def zeitverteilung():
    st.subheader('Entstehungszeit der Objekte in der Sammlung')
    df = pd.read_csv(f'{path}/zeit.csv')
    count = pd.DataFrame(pd.value_counts(df.year))
    count = count.rename(columns={'year':'count'})
    count.index.rename('year', inplace=True)
    
    zeit = alt.Chart(count.reset_index()).mark_bar().transform_bin("year_binned", "year", bin=alt.Bin(maxbins=32, extent=[1400,2021])).encode(
        alt.X('year_binned:O', title='Entstehungsjahr', scale=alt.Scale(zero=False)),
        alt.Y('count:Q', title='Anzahl'),
        tooltip=[alt.Tooltip('year', title='Jahr'), alt.Tooltip('count', title='Anzahl')]
    )
    return st.altair_chart(zeit, use_container_width=True)
    

#main
st.title('DBSM Dashboard')
rundschreiben()
zeitverteilung()

streamlit_analytics.stop_tracking()