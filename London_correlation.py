# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 13:42:52 2019

@author: Kirsch
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import geopandas as gpd
import seaborn as sn
from tabulate import tabulate

#########################################
#Load and format the appropriate datasets
#########################################

#Load the CCG csv file
london = pd.read_csv(r'C:\Users\Kirsch\Documents\london_ccg_1.csv', error_bad_lines=False,
                  engine = 'python', sep = ';')

#Give accurate name to the columns
london.columns = ['CCG Code','Borough', 'Count', 'Population', 'LSOAs', 'City'
                  ,'PCT Cluster', 'Running Cost']
#Keep only London's CCG
london = london.loc[london["City"]=="London"]

#Format the Borough names so that its the same as for the other datasets
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

#Verify if the borough names are the same
common_b = pd.Series(list(set(london["Borough"]) & 
                        set(map_l["Borough"]))).sort_values()

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


#Merge the different datasets and reformat the new dataset
london_map = map_l.set_index('Borough').join(london.set_index('Borough'))
london_map.sort_values(by = 'Borough', inplace = True)
london_map.drop(["City of London"], inplace = True)
london_map = london_map.join(obesity.set_index('Borough'
                                )).join(depression.set_index('Borough'
                                )).join(life_e.set_index('Borough'
                                )).join(income.set_index('Borough'
                                )).join(inf_mort.set_index('Borough'))
london_map['Population'] = london_map["Population"].str.split(" "
          ).str.join("").astype(int)
london_map['Ratio'] =(london_map['Count']*100000)/london_map['Population']
london_map['Geog'] = (london_map['Count']*1000)/london_map['HECTARES']
london_map.drop(['Kensington and Chelsea'], inplace = True)

#################
#Analyse the data 
#################

#Simplify the columns names
doc = london_map["Count"]
pop1 = london_map["Population"]
obese = london_map['Obese Children (%)']
depressed = london_map["Depressive episode"]
men_le = london_map['Men']
inc = london_map["Weekly income per household"]
ratio = london_map["Ratio"]
inf = london_map['Infant mortality per 1,000 live births']
geog = london_map['Geog']
indic = [depressed,inc,obese,men_le,inf]
label = ['Number of depressed episode (per 1000 person)',
         'Weekly income per household','Percentage of obese children (%)',
         'Men life expectancy','Number of infant deaths per 1000 live births']

#Population against doctors
plt.figure()
plt.scatter(pop1,doc)
plt.ylim(bottom = 0)
plt.xlabel('Borough Population')
plt.ylabel('Number of doctors')
plt.title('Number of doctors per population size', fontsize = '16')
slope_p, intercept_p, r_value_p, p_value_p, std_err_p = stats.linregress(pop1,doc.astype(float))

#Introductory descrpitive statistics of number of doctors per 1000 hectares
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Descriptive statistics of doctor distribution in London boroughs')
sn.distplot(geog, ax = ax1)
sn.boxplot(geog, ax = ax2)
plt.figure()
plt.bar(london_map.index, geog)
plt.xticks(rotation=90)

#Plot the relationship and get the correlation and p values
correlation = [None]*5
p_value = [None]*5
for i in range(0, len(correlation)):
    plt.figure()
    plt.scatter(geog,indic[i])
    plt.ylim(bottom = 0)
    plt.ylabel(label[i])
    plt.xlabel('Number of doctors')
    plt.title(label[i] + ' \n against number of doctors', fontsize = '16', pad = 20)
    plt.savefig('{}.png'.format(label[i]),bbox_inches='tight')
    correlation[i], p_value[i] = stats.spearmanr(geog.astype(float),indic[i])


#Make a summary table of the correlations
print(tabulate([['Depressive Episodes per 1000 persons', correlation[0],p_value[0]], 
                ['Weekly income per household', correlation[1],p_value[1]],
                ['Percentage of Obese children', correlation[2],p_value[2]],
                ['Men life expectancy',correlation[3],p_value[3]],
                ['Infant mortality', correlation[4],p_value[4]]],
                headers=['Wellbeing Indicator', 'Correlation','P-value'], tablefmt='orgtbl'))