# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 16:25:32 2019

@author: Kirsch
"""

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import geopandas as gpd

#Load the CSV Doctor Dataset
doctors = pd.read_csv(r'C:\Users\Kirsch\Documents\MedicalDesert.csv', 
                  engine = 'python')

#Load the CSV Population dataset
population = pd.read_csv(r"C:\Users\Kirsch\Documents\Postcodessummary.csv", 
                 engine = 'python')

#Load the map frame
map_df = gpd.read_file(r'C:\Users\Kirsch\Documents\Distribution\Areas.shp')

#Keep only the interesting columns
geog = doctors.iloc[:,[0,1,2,3,9]]
pop = population.iloc[:,[0,2]]

#Give names to the columns
geog.columns = ["Organisation Code","Name","National Grouping",
                    "High level health geography","Postcode"]


#Separate the postcode between area (first two letters and the rest)
for i in range (0, 10):    
    geog["Postcode"] = geog["Postcode"].str.split(pat = str(i),n = 1,
             expand = True)

#Plot the distribution of doctors between the areas
#geog["Postcode"].value_counts().plot(kind='bar')

#Get the dataset as a list of number of doctors per area
geog = geog.groupby('Postcode', as_index=False).count()
geog = geog.iloc[:,[0,1]]
geog.columns = ["Postcode","Count"]

#Find the area codes common to the two series
common = pd.Series(list(set(geog["Postcode"]) & 
                        set(pop["Postcode area"]))).sort_values()

#Keep only the common areas
geog1 = geog.loc[geog["Postcode"].isin(common)]
pop1 = pop.loc[pop["Postcode area"].isin(common)]
map1 = map_df.loc[map_df["name"].isin(common)]
#Reset the indexing of the series so that they correspond
geog1 = geog1.reset_index(drop = True)
pop1 = pop1.reset_index(drop = True)
map1 = map1.reset_index(drop = True)


#Adda size row to the map1 dataset
map1['Size'] = np.zeros(shape=(111,1))

#Get the size from the geometry of each areas
selection = map1
for index, row in selection.iterrows():
    map1['Size'][index] = map1['geometry'][index].area

#Merge the two dataframes, and tidying the new dataframe up 
joine = pd.concat([geog1, pop1], axis=1)
joine = joine.iloc[:,[0,1,3]]
joine = joine.dropna()
joine = joine.reset_index(drop = True)

#New dataset with size of areas added
size = pd.concat([joine,map1], axis = 1)
size = size.iloc[:,[0,1,2,5]]

#Convert value between polygon size and squared mile from IV real size
poltomile = 6243/size.iloc[46,3]

#Convert polygon size to squared miles
for i in range(0,111) : 
    size.iloc[i,3]=size.iloc[i,3]*poltomile


#Create simplified variable names
pop = size["Population"]
c = size["Count"]
s = size["Size"]

#Plot the Number of doctors against the population for each area
plt.figure()
plt.scatter(pop,c)
plt.plot(np.unique(pop), 
         np.poly1d(np.polyfit(pop, c, 1))
         (np.unique(pop)))
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.xlabel('Number of inhabitants per postcode area')
plt.ylabel('NUmber of doctors per postcode area')
plt.title('Number of doctors per population size', fontsize = '16')
plt.savefig('Pop.png')

#Plot number of doctors against size of the area
plt.figure()
plt.scatter(s,c)
plt.xlabel('Size of each postcode area')
plt.ylabel('NUmber of doctors per postcode area')
plt.title('Number of doctors per surface area', fontsize = '16')
plt.savefig('Geo.png')

#Get the correlation coeffitient between the number of doctors and the 
#population of each area
slope, intercept, r_value, p_value, std_err = stats.linregress(pop,c)


#Create dataset with the map frame and data studied
merged = map1.set_index('name').join(joine.set_index('Postcode'))

#Create the variables which will be mapped 
variable1 = 'Size'
variable = 'Count'
vmin, vmax = 1, 640

# create figure and axes for Matplotlib
plt.figure()
fig, ax = plt.subplots(1, figsize=(10, 6))
#Number of doctors in each region
merged.plot(column=variable, cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8', legend = 'True')
plt.title('Number of doctor in each postcode area', fontsize = 16, loc = 'center')
ax.axis('off')
plt.savefig('UK_distrib.png')

#Size of area on the map
plt.figure()
fig, ax = plt.subplots(1, figsize=(10, 6))
merged.plot(column=variable1, cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')
