#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from utils import *

covid = pd.read_csv("https://raw.githubusercontent.com/kangkai20000518/Covid_In-Custody_Project_Data_sourse/main/County%20Jails%20COVID%20Data%20Tracker%20-%20Population%20Tracker.csv",header=[2,3,4],encoding="ISO-8859-1",error_bad_lines=False)

#Preprocess raw data and the Duration, Start_Day and End_day are added into the file
BSCC = BSCC_preprocessing(covid)


#Aggregate data to COUNTY/FACILITY level and calculate average
County = groupby_location(BSCC,string = "County")
Facility = groupby_location(BSCC,string = "Facility")


# DATA VISUALIZATION-For Facility
BSCC_map = facility_visualization(Facility)
map_illustration_facility(BSCC_map)

# DATA VISUALIZATION-For County
County_analysis = county_visualization(County)
scatter_county(County_analysis)

# Urban & Rural Analysis
County_Urban = urban_code(County_analysis)
correlation(County_Urban)

from google.colab import drive
drive.mount('drive')
County_Urban.to_csv('County_Urban.csv',index =False ,sep = ',')
get_ipython().system('cp County_Urban.csv "drive/My Drive/"')

