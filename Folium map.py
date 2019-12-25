# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 15:28:35 2019

@author: Kirsch
"""

import pandas as pd
import folium
import json
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import pybase64
from folium import IFrame

######################################
#Import and format the datasets needed
######################################

#Load the london geojson file
geo = json.load(open(r'C:\Users\Kirsch\Documents\london_boroughs_proper.geojson'))

#Load the  borough centroid dataset
latlon = pd.read_csv(r'C:\Users\Kirsch\Documents\LatLon.csv', sep = ';')
latlon['Longitude']= latlon['Longitude'].str.strip().astype(float)
latlon.drop(latlon.index[6], inplace = True)
latlon = latlon.reset_index(drop = True)

#Load london map shapefile
map_l = gpd.read_file(r'C:\Users\Kirsch\Documents\statistical-gis-boundaries-london\ESRI\London_Borough_Excluding_MHW.shp')
map_l = map_l.rename(columns = {'NAME':'Borough'})

#Load the NHS dataset and rearrange it
london = pd.read_csv(r'C:\Users\Kirsch\Documents\london_ccg_1.csv', error_bad_lines=False,
                  engine = 'python', sep = ';')
london.columns = ['CCG Code','Borough', 'Count', 'Population', 'LSOAs', 'City'
                  ,'PCT Cluster', 'Running Cost']
london = london.loc[london["City"]=="London"]
london["Borough"] = london["Borough"].str.lstrip('NHS'
      ).str.lstrip().str.rstrip('CCG').str.rstrip()
london.at[6,"Borough"] = 'Westminster'
london.at[31,"Borough"] = 'Kensington and Chelsea'
london.at[0,"Borough"] = 'Barking and Dagenham'
london.at[19,"Borough"] = 'Kingston upon Thames'
london.at[25,"Borough"] = 'Richmond upon Thames'
Hackney = pd.DataFrame(london.loc[7]).T
london = pd.concat([Hackney, london]).reset_index(drop = True)
london.at[0,"Borough"] = 'Hackney'
london.at[8,"Borough"] = 'City of London'


#Load london map shapefile
map_l = gpd.read_file(r'C:\Users\Kirsch\Documents\statistical-gis-boundaries-london\ESRI\London_Borough_Excluding_MHW.shp')
map_l = map_l.rename(columns = {'NAME':'Borough'})

#Load the obesity dataset and format it in a useful way
obesity = pd.read_csv(r'C:\Users\Kirsch\Documents\child-obesity-2.csv', error_bad_lines=False,
                  engine = 'python', sep = ',')
obesity.drop(obesity.index[0:3] , inplace = True)
obesity = obesity.reset_index(drop = True)
obesity.drop(obesity.index[32:45], inplace = True)
obesity.columns = ['Borough','2010-11',
                 'Obese Children (%)']
obesity.drop(['2010-11'], axis = 1, inplace = True)
obesity['Obese Children (%)'] = obesity['Obese Children (%)'].str.strip("%\n "
        ).astype(float)

#Load the depression dataset and rearrange it
depression = pd.read_csv(r'C:\Users\Kirsch\Documents\mental-health-common-problems-borough-per-1000-persons.csv'
                         ,error_bad_lines=False, engine = 'python', sep = ';')
depression.drop(depression.index[0], inplace = True)
depression.drop(depression.index[33:46], inplace = True)
depression = depression.drop(['ï»¿Code', 'All phobias', 'Generalised anxiety disorder',
       'Obsessive compulsive disorder', 'Panic disorder', 'Population 16-74'], axis = 1)
depression = depression.rename(columns = {'Area':'Borough'})
depression = depression.reset_index(drop = True)
depression['Any neurotic disorder'] = depression['Any neurotic disorder'].str.replace(',','.').astype(float)
depression['Depressive episode'] = depression['Depressive episode'].str.replace(',','.').astype(float)
depression['Mixed anxiety depression'] = depression['Mixed anxiety depression'].str.replace(',','.').astype(float)

#Load the life expectancy dataset and rearrange it
life_e = pd.read_csv(r'C:\Users\Kirsch\Documents\life-expectancy-birth-2012-14.csv', error_bad_lines=False,
                  engine = 'python', sep = ';')
life_e = life_e.iloc[:,[2,12,13]]
life_e.drop(life_e.index[0], inplace = True)
life_e.drop(life_e.index[32:50], inplace = True)
life_e.columns = ['Borough','Men','Women']
life_e["Men"] = life_e["Men"].str.replace(',','.').astype(float)
life_e["Women"] = life_e["Women"].str.replace(',','.').astype(float)
life_e = life_e.reset_index(drop = True)

#Load the weekly income per household dataset and rearrange it
income = pd.read_csv(r'C:\Users\Kirsch\Documents\earnings-residence-borough-2014-2018.csv', error_bad_lines=False,
                  engine = 'python', sep = ';')
income = income.iloc[:,[1,10]]
income.drop(income.index[0:2], inplace = True)
income.drop(income.index[34:48], inplace = True)
income = income.reset_index(drop = True)
income.columns = ["Borough","Weekly income per household"]
income["Weekly income per household"] = income["Weekly income per household"].str.replace(',','.').astype(float)

#Load the infant mortality dataset and rearrange it
inf_mort = pd.read_csv(r'C:\Users\Kirsch\Documents\infant-mortality-by-borough.csv', error_bad_lines=False,
                  engine = 'python', sep = ',')
inf_mort.columns = ['Borough','Infant mortality per 1,000 live births']
inf_mort.drop(inf_mort.index[0:3], inplace = True)
inf_mort.drop(inf_mort.index[34:41], inplace = True)
inf_mort.sort_values('Borough', inplace=True)
inf_mort = inf_mort.reset_index(drop = True)
inf_mort['Infant mortality per 1,000 live births'] = inf_mort['Infant mortality per 1,000 live births'].astype(float) 


#Create the dataset for the radar charts
london_rad = map_l.set_index('Borough').join(london.set_index('Borough'))
london_rad.sort_values(by = 'Borough', inplace = True)
london_rad.drop(["City of London"], inplace = True)
london_rad = london_rad.join(obesity.set_index('Borough'
                                )).join(depression.set_index('Borough'
                                )).join(life_e.set_index('Borough'
                                )).join(income.set_index('Borough'
                                )).join(inf_mort.set_index('Borough'))
london_rad['Population'] = london_rad["Population"].str.split(" "
          ).str.join("").astype(int)
london_rad['Ratio'] =(london_rad['Count']*100000)/london_rad['Population']
london_rad['Geog'] = (london_rad['Count']*1000)/london_rad['HECTARES']
#Keep only the columns needed for the radar chart
london_rad = london_rad.iloc[:,[-10,-3,-4,-6,-8]]

#Create the dataset used for the cloropeth map
folium_l = map_l.set_index('Borough').join(london.set_index('Borough'))
folium_l.sort_values(by = 'Borough', inplace = True)
folium_l.reset_index(drop = True)
folium_l.drop(["City of London"], inplace = True )
folium_l['Geog'] = (folium_l['Count']*1000)/folium_l['HECTARES']


#############################################################
#Code used to do radar charts with different axis
#From: https://datascience.stackexchange.com/questions/6084/
#how-do-i-create-a-complex-radar-chart
#############################################################

def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d-y1) / (y2-y1) 
                     * (x2 - x1) + x1)
    return sdata

class ComplexRadar():
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=6):
        angles = np.arange(0, 360, 360./len(variables))

        axes = [fig.add_axes([0.1,0.1,0.9,0.9],polar=True,
                label = "axes{}".format(i)) 
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles, 
                                         labels=variables)
        [txt.set_rotation(angle-90) for txt, angle 
             in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i], 
                               num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x,2)) 
                         for x in grid]
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1] # hack to invert grid
                          # gridlabels aren't reversed
            gridlabel[0] = "" # clean up origin
            ax.set_rgrids(grid, labels=gridlabel,
                         angle=angles[i])
            #ax.spines["polar"].set_visible(False)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]
    def plot(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], *args, **kw)
    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)


###################################
#Create the visualisation (the map)
###################################
        
#Create the folium map and center it on london 
m = folium.Map(location=[ 51.489865, -0.118092], zoom_start=11)

#Create a cloropeth map depending on the number of doctor per 1000 hectares
folium.Choropleth(
    geo_data=geo,
    name='Number of doctors per 1000 hectares',
    data=folium_l,
    columns=[folium_l.index, 'Geog'],
    key_on='feature.properties.name',
    fill_color='YlOrRd',
    nan_fill_color = 'White',
    nan_fill_opacity = '0',
    fill_opacity=0.9,
    line_opacity=0.2,
    legend_name='Number of doctors per 1000 hectares',
    show = True
    ).add_to(m)
    
#Hover popup giving the borough name
molo=folium.GeoJson(
    data=geo,
    name="Map of Ile de France",
    style_function = lambda feature: dict(color="Green", weight=0, opacity=0),
    overlay=True,
    control=False,
    show=True,
    tooltip=folium.features.GeoJsonTooltip(
            fields=['name'],
            labels=False)
    ).add_to(m)

#Instantiating useful variables for the Iframe and the radar chard
variables = ('\n       Obese', "InfMor", "Inc", 
            "LE","Dep")
resolution, width, height = 75, 4.4, 4.5
tooltip = 'Click for borough radar chart'

#Create the radar chart and the marker for each borough
for i in range (0,len(london_rad)):
    data = london_rad.iloc[i]
    ranges = [(12, 29), (2,6), (470, 770),
              (77, 84), (29, 41)]            
    fig1 = plt.figure(figsize=(4, 4))
    radar = ComplexRadar(fig1, variables, ranges)
    radar.plot(data)
    radar.fill(data, alpha=0.2)
    plt.title(london_rad.index[i], y = 1.1)
    png = 'radar_{}.png'.format(london_rad.index[i])
    fig1.savefig(png, bbox_inches='tight', dpi = resolution)
    encoded_i = pybase64.b64encode(open(png, 'rb').read())
    html = '<img src="data:image/png;base64,{}">'.format
    iframe = IFrame(html(encoded_i.decode('UTF-8')), width=(width*resolution)+20, height=(height*resolution)+20)
    popup = folium.Popup(iframe, max_width=3000)        
    icon = folium.Icon(color="red", icon="info-sign")
    marker = folium.Marker([latlon.iloc[i,1],latlon.iloc[i,2]], popup=popup, icon=icon, tooltip = tooltip)
    marker.add_to(m)

#Add layer control
folium.LayerControl().add_to(m)

# Save to html
m.save('london_layers.html')
