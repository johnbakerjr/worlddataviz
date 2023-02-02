import pandas as pd
import numpy as np

from dataprep.clean import clean_country
import plotly.graph_objects as go

gdp_per_capita = pd.read_csv('./data/country_gdp_per_capita_worldbank.csv')
gdp_per_capita = gdp_per_capita[['Country Name', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']]

usa = pd.read_csv('./data/USAData_RenewableInvestment_2010-2020.csv').set_index('Country')

## read plotly data ##

temp_delta_plotly = pd.read_csv('./data/Annual_Surface_Temperature_Change.csv')
invest_plotly = pd.read_csv('data/Environmental_Protection_Expenditures.csv')
gdp_per_capita_plotly = gdp_per_capita.copy()

## prepare data for plotly ##

gdp_per_capita_plotly = gdp_per_capita_plotly.rename(columns={'Country Name': 'Country'})

# look up ISO3 codes for countries
gdp_per_capita_plotly = clean_country(gdp_per_capita_plotly, "Country", output_format="alpha-3").rename(columns={'Country_clean': 'ISO3'})
gdp_per_capita_plotly = gdp_per_capita_plotly[['Country', 'ISO3', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']]
gdp_per_capita_plotly = gdp_per_capita_plotly.rename(columns={'2010': 2010, '2011': 2011, '2012': 2012, '2013': 2013, '2014': 2014, '2015': 2015, '2016': 2016, '2017': 2017, '2018': 2018, '2019': 2019, '2020': 2020})

temp_delta_plotly = temp_delta_plotly[['Country', 'ISO3', 'F2010', 'F2011', 'F2012', 'F2013', 'F2014', 'F2015', 'F2016', 'F2017', 'F2018', 'F2019', 'F2020']]
temp_delta_plotly = temp_delta_plotly.rename(columns={'F2010': 2010, 'F2011': 2011, 'F2012': 2012, 'F2013': 2013, 'F2014': 2014, 'F2015': 2015, 'F2016': 2016, 'F2017': 2017, 'F2018': 2018, 'F2019': 2019, 'F2020': 2020})

usa2 = usa.copy().reset_index()
usa2['ISO3'] = 'USA'
invest_plotly = invest_plotly[invest_plotly['Unit'] == 'Percent of GDP'].fillna(int(0))
invest_plotly = invest_plotly[['Country', 'ISO3', 'F2010', 'F2011', 'F2012', 'F2013', 'F2014', 'F2015', 'F2016', 'F2017', 'F2018', 'F2019', 'F2020']].reset_index(drop=True)
invest_plotly = pd.concat([invest_plotly, usa2])
invest_plotly = invest_plotly.groupby(['ISO3']).agg('sum').reset_index()
invest_plotly = invest_plotly.rename(columns={'F2010': 2010, 'F2011': 2011, 'F2012': 2012, 'F2013': 2013, 'F2014': 2014, 'F2015': 2015, 'F2016': 2016, 'F2017': 2017, 'F2018': 2018, 'F2019': 2019, 'F2020': 2020})

temp_delta_plotly = temp_delta_plotly.melt(id_vars=['ISO3'], value_vars=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020], var_name='Year', value_name='Temp_Change')
gdp_per_capita_plotly = gdp_per_capita_plotly.melt(id_vars=['ISO3', 'Country'], value_vars=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020], var_name='Year', value_name='GDP_Per_Capita')
invest_plotly = invest_plotly.melt(id_vars=['ISO3'], value_vars=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020], var_name='Year', value_name='Investment_Percent')

plotly_data = pd.merge(temp_delta_plotly, invest_plotly, on=['ISO3', 'Year'])
plotly_data = pd.merge(gdp_per_capita_plotly, plotly_data, on=['ISO3', 'Year'])

# drop all YEMEN data, as there is missing GDP data and no temp_change data
plotly_data = plotly_data.drop(plotly_data.loc[plotly_data['ISO3']=='YEM'].index)

# drop 2010-2012 data for SOMALIA, as there is no GDP data
plotly_data = plotly_data.drop(plotly_data.loc[(plotly_data['ISO3']=='SOM') & (plotly_data['Year']<2013)].index)

new_country_data = plotly_data.copy()
new_country_data = new_country_data.groupby('Country').agg({'Temp_Change': 'mean', 'Investment_Percent': 'mean', 'GDP_Per_Capita': 'mean'})
new_country_data['Temp_Change'] = new_country_data['Temp_Change'] + .25
new_country_data = new_country_data.rename(columns={'Temp_Change': 'temp_delta_avg', 'Investment_Percent': 'renew_invest_avg', 'GDP_Per_Capita': 'gdp_per_capita_avg'})

g20 = ['Argentina', 'Australia', 'Brazil', 'Canada', 'China', 'France', 'Germany', 'India', 'Indonesia', 'Italy', 'Japan', 'Republic of Korea', 'Mexico', 'Russia', 'Saudi Arabia', 'South Africa', 'Turkey', 'United Kingdom', 'United States', 'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'Greece', 'Hungary', 'Ireland', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden']
new_country_data['g20'] = new_country_data.index.isin(g20).tolist()

g20_countries = new_country_data.loc[new_country_data['g20'] == True].index.to_list()


plotly_data['Temp_Change'] = plotly_data['Temp_Change'] + .25

p1 = (plotly_data['Investment_Percent'] > 2)
p2 = (plotly_data['Temp_Change'] < 1.5)

plotly_data['color_code'] = np.where(p1 & p2, '#46725D', "False")
plotly_data['color_code'] = np.where(p1 & ~p2, '#A46D13', plotly_data['color_code'])
plotly_data['color_code'] = np.where(~p1 & p2, '#505693', plotly_data['color_code'])
plotly_data['color_code'] = np.where(~p1 & ~p2, '#9A381D', plotly_data['color_code'])

# make plotly figure

dataset = plotly_data.copy()

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

# make figure
fig_dict = {
    "data": [],
    "layout": {},
    "frames": []
}

min_x_val = dataset['Temp_Change'].min()-.2
max_x_val = dataset['Temp_Change'].max()+.2
min_y_val = dataset['Investment_Percent'].min()-.2
max_y_val = dataset['Investment_Percent'].max()+.2

# fill in most of layout
fig_dict["layout"]["xaxis"] = {"range": [min_x_val, max_x_val], "title": f'Annual Temperature Above Pre-industrial Levels ({chr(176)}C)'}
fig_dict["layout"]["yaxis"] = {"range": [min_y_val, 4.5], "title": "Investment in Renewable Energy (% GDP)"}  # "type": "log" makes y-axis log scale
fig_dict["layout"]["hovermode"] = "closest"
fig_dict["layout"]["updatemenus"] = [
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 700, "redraw": False},
                                "fromcurrent": True, "transition": {"duration": 500,
                                                                    "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": False,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }
]

sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "Year:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 300, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": []
}

Countries = list(plotly_data['Country'].unique())
Countries = sorted(Countries)

# make data
year = 2010
for Country in g20_countries:
    dataset_by_year = dataset[dataset["Year"] == year]
    dataset_by_year_and_country = dataset_by_year[
        dataset_by_year["Country"] == Country]

    data_dict = {
        "x": list(dataset_by_year_and_country["Temp_Change"]),
        "y": list(dataset_by_year_and_country["Investment_Percent"]),
        "mode": "markers",
        "marker": {
            "sizemode": "area",
            "sizeref": 300,
            "size": list(dataset_by_year_and_country["GDP_Per_Capita"]),
            "color": dataset_by_year_and_country.loc[dataset_by_year_and_country['Country']==Country].color_code[dataset_by_year_and_country['Year']==year]
            },
            "name": Country
            }
    fig_dict["data"].append(data_dict)

# make frames
for year in years:
    frame = {"data": [], "name": str(year)}
    for Country in g20_countries:
        dataset_by_year = dataset[dataset["Year"] == int(year)]
        dataset_by_year_and_country = dataset_by_year[
            dataset_by_year["Country"] == Country]

        data_dict = {
            "x": list(dataset_by_year_and_country["Temp_Change"]),
            "y": list(dataset_by_year_and_country["Investment_Percent"]),
            "mode": "markers",
            "marker": {
                "sizemode": "area",
                "sizeref": 300,
                "size": list(dataset_by_year_and_country["GDP_Per_Capita"]),
                "color": dataset_by_year_and_country.loc[dataset_by_year_and_country['Country']==Country].color_code[dataset_by_year_and_country['Year']==year]
                },
                "name": Country
                }
        frame["data"].append(data_dict)

    fig_dict["frames"].append(frame)
    slider_step = {"args": [
        [year],
        {"frame": {"duration": 1500, "redraw": False},
         "mode": "immediate",
         "transition": {"duration": 1500}}
    ],
        "label": year,
        "method": "animate"}
    sliders_dict["steps"].append(slider_step)


fig_dict["layout"]["sliders"] = [sliders_dict]

fig = go.Figure(fig_dict)

fig.add_hline(y=2, line_dash="dash", line_color="black", annotation_text="Investment Needed to Fully Transition to Renewable Energy by 2050", annotation_position="bottom right")
fig.add_vline(x=1.5, line_dash="dash", line_color="black", annotation_text="2050 Target Temperature Increase", annotation_position="top right")
fig.add_annotation(x=3.75, y=-.35, text="Urgent Action Needed", showarrow=False, font_size=12, bordercolor='#9A381D', font=dict(color='#9A381D'), borderpad=3)
fig.add_annotation(x=3.67, y=4.1, text="Continued Progress Needed", showarrow=False, font_size=12, bordercolor='#A46D13', font=dict(color='#A46D13'), borderpad=3)
fig.add_annotation(x=0.2, y=4.1, text="Meeting 2050 Climate Goals", showarrow=False, font_size=12, bordercolor='#46725D', font=dict(color='#46725D'), borderpad=3)
fig.add_annotation(x=0.17, y=-.35, text="Investments Falling Short", showarrow=False, font_size=12, bordercolor='#505693', font=dict(color='#505693'), borderpad=3)

fig.update_layout(
    title={
        'text': "G20 Countries Have Invested Little as Temperatures Dramatically Increased Over the Last Decade",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    showlegend=False
    )

fig.write_html("index.html")