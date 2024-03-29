import pandas as pd
from geopy.exc import GeocoderTimedOut
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from dateutil.parser import parse
from plotly import express as px
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from geopy.point import Point
import folium


def preprocessing_BSCC(df):
        """
        Function: Indentify which  columns are belongs to Reporting to BSCC and change multiindex to one column name for each column
        In: dataframe
        Out: dataframe with one row in the column name part
        """ 
        covid_names = df.head(0)
        covid_names=list(df)
        first_row_index = [i[0] for i in covid_names]
        second_row_index = [i[1] for i in covid_names]
        wb_index=second_row_index.index('Reporting on website')
        temp=covid[first_row_index[0:wb_index]]#only extract county facility and time period
        temp.columns = temp.columns.droplevel(1).droplevel(1)
        bscc_index=second_row_index.index('Reporting to BSCC') 
        BSCC=covid[first_row_index[bscc_index:-2]]#only extract Reporting to BSCC
        BSCC.columns = BSCC.columns.droplevel().droplevel()
        BSCC=pd.concat([temp,BSCC], axis=1)
        for i in range(1,BSCC.shape[0]):
            for j in list(BSCC.columns):
                if pd.isna(BSCC.loc[i,j])==True:
                    BSCC.loc[i,j]=BSCC.loc[i-1,j]
            
        return BSCC


def cal_time(df):
        """
        Function: Add three more columns named as Duration, Start_Day, End_Day, and calculate time period between Start_Day and End_Day
        In: dataframe
        Out: dataframe with 3 more columns
        """
        df.insert(loc=3,column='Duration', value=0)
        df.insert(loc=4,column='Start_Day', value=0)
        df.insert(loc=5,column='End_Day', value=0)
        for i in range(0,len(df)):
            position=df["Time Period"][i].rfind(" - ")
            start=df["Time Period"][i][0:position]
            end=df["Time Period"][i][position+3:]
            df.loc[i, 'Start_Day'] = start
            df.loc[i, 'End_Day'] = end
            df.loc[i, 'Duration'] = (parse(end)-parse(start)).days
        return df


def group_concat(df1):
    """
    Function: Put Time period together and drop the duplicates
    In: dataframe
    Out: dataframe
    """
    df1['Time Period'] = ' , '.join(set(df1['Time Period']))
    return df1.drop_duplicates()


def groupby_location(df,string):
    """
    Function: Separate county and facility and get the correct time information result for each of them
    In: dataframe, string = "County" or "Facility"
    Out: dataframe
    """
    df1=df.copy()
    
    if string=="County":
        time_info=df1[[string,"Time Period"]].groupby([string],group_keys=False,sort=False).apply(group_concat)
    else:
        time_info=df1[["County","Facility","Time Period"]].groupby(["Facility"],group_keys=False,sort=False).apply(group_concat)
    cols=list(df1.columns)[6:]
    
    for i in range(len(cols)):#calcualte total days
        df1[cols[i]]=df1[cols[i]]*df1["Duration"]
    BSCC_by_location=df1.groupby([string]).sum()
    BSCC_by_location.reset_index(inplace=True)
    
    for i in range(len(cols)):#calcualte percentage
        BSCC_by_location[cols[i]]=round(BSCC_by_location[cols[i]]/BSCC_by_location["Duration"],2)
    BSCC_by_location=pd.merge(time_info,BSCC_by_location)
    
    return BSCC_by_location


def do_geocode(address, attempt=1, max_attempts=10):
    """
    Function: Use geopy to obtain the latitude and longitude of locations and maximum attempts are 10
    In: address
    Out: latitude and longitude pairs
    """

    try:
        return geo.geocode(address)
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address, attempt=attempt+1)
        raise

        
def facility_visualization(Facility):
    """
    Function: Calculate the mean of 9 columns and Use geopy to obtain the latitude and longitude of locations 
    * LOCATION is limited within California *
    In: Facility dataframe
    Out: dataframe for facility mapping
    """

    #Calculate the mean of 9 columns
    geo=Nominatim(user_agent='my-test-app')
    
    df=Facility
    df=df.drop('Duration',axis=1)
    df=df.drop('County',axis=1)
    df1=df.drop('Facility',axis=1)
    df1=df1.drop('Time Period',axis=1)
    df1=df1.astype(float)
    fac=df['Facility'].tolist()
    df['mean']=np.mean(df1,axis=1)
    
    lat=[]
    lon=[]
    geolocator = Nominatim()
    for i in fac:
        Geo=do_geocode(i)
        if Geo is None:
            lat.append(np.nan)
            lon.append(np.nan)
            continue
        if geolocator.reverse(Point(Geo.latitude, Geo.longitude)).raw.get("address").get("state")=="California":
            lat.append(Geo.latitude)
            lon.append(Geo.longitude)
        else:
            lat.append(np.nan)
            lon.append(np.nan)
    df['lat']=lat
    df['lon']=lon
    BSCC_map=df.dropna()
    
    return BSCC_map


def map_illustration_facility(BSCC_map):
    """
    Function: Use mean to make 6 divison and Map-illustration: from darkred to darkgreen, data-transparency increases
    In: Facility dataframe
    Out: facility mapping with color
    """
    
    m=[]
    for i in BSCC_map['mean']:
        if 0<=i<0.2:
            m.append('darkred')
        elif 0.2<=i<0.4:
            m.append('red')
        elif 0.4<=i<0.5:
            m.append('lightred')
        elif 0.5<=i<0.6:
            m.append('lightgreen')
        elif 0.6<=i<0.8:
            m.append('green')
        elif 0.8<=i:
            m.append('darkgreen')
    # green means good data-transparency; red means poor data-transparency
    BSCC_map['grade']=m
    BSCC_map=BSCC_map.dropna()
    fac=BSCC_map['Facility'].tolist()
    tim=BSCC_map['Time Period'].tolist()
    mea=BSCC_map['mean'].tolist()
    lat=BSCC_map['lat'].tolist()
    lon=BSCC_map['lon'].tolist()
    c=BSCC_map['grade'].tolist()
    m = folium.Map(location=[37.351002,-121.905769], zoom_start=10)
    for i in range(len(lat)):
        folium.Marker([lat[i],lon[i]], popup='【'+str(round(mea[i],2))+'】'+fac[i]+'   '+tim[i],icon=folium.Icon(color=c[i])).add_to(m)
    
    return m


def county_visualization(County):
    """
    Function: Calculate the mean of 9 columns and use mean to make 6 divison
    In: County dataframe
    Out: dataframe for County scattering
    """
    County_analysis=County.drop(["Time Period","Duration"],axis=1)
    County_analysis['mean']=np.mean(County_analysis,axis=1)
    m=[]
    
    for i in County_analysis['mean']:
        if 0<=i<0.2:
            m.append('darkred')
        elif 0.2<=i<0.4:
            m.append('red')
        elif 0.4<=i<0.5:
            m.append('lightred')
        elif 0.5<=i<0.6:
            m.append('lightgreen')
        elif 0.6<=i<0.8:
            m.append('green')
        elif 0.8<=i:
            m.append('darkgreen')
    County_analysis['grade']=m
    
    return County_analysis


def scatter_county(County_analysis):
    """
    Function: Draw the scatter graph of County
    In: County dataframe
    Out: scatter graph for County
    """
    
    fig = px.scatter(data_frame = County_analysis, # data that needs to be plotted
                 x = "County", # column name for x-axis
                 y = "mean", # column name for y-axis
                 color = "grade", # column name for color coding
                 width = 1000,
                 height = 500)
    # reduce whitespace
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # show the plot
    fig.show()


def urban_code(County_analysis):
    """
    Function: Use official region codes to show the urban-level for each county
    In: County dataframe
    Out: County dataframe with 2013 urban level
    """
    urban_code=pd.read_csv("https://raw.githubusercontent.com/kangkai20000518/Covid_In-Custody_Project_Data_sourse/main/Copy%20of%20NCHSURCodes2013.csv",error_bad_lines=False)
    v=[]
    for i in urban_code['County']:
        b=i.strip()
        v.append(b)
    urban_code['County']=v
    County_Urban= pd.merge(County_analysis,urban_code,on=['County'])
    
    return County_Urban


def correlation(County_Urban):
    """
    Function: Calculate correlation between transparency level and urban level
    In: County dataframe
    Out: correlation results
    """
    corr=County_Urban[["Active cases","Cumulative confirmed cases",	"Resolved cases in custody","Deaths","Testing","Population","Vaccinations","Frequency","History available","2013 code"]]
    for column in corr[["2013 code"]]:
        corr[column] = (corr[column] - corr[column].min()) / (corr[column].max() - corr[column].min())    
    corr=corr.corr()
    corr.fillna(value=0)
    return corr

