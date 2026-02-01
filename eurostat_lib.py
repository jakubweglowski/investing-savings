import numpy as np
import pandas as pd
from datetime import datetime as dt
from warnings import filterwarnings
filterwarnings('ignore')

# EUROSTAT data
from eurostat import get_data

country_names_dict = {'Belgium': 'BE',
                    'Greece': 'EL',
                    'Lithuania': 'LT',
                    'Portugal': 'PT',
                    'Bulgaria': 'BG',
                    'Spain': 'ES',
                    'Luxembourg': 'LU',
                    'Romania': 'RO',
                    'Czechia': 'CZ',
                    'France': 'FR',
                    'Hungary': 'HU',
                    'Slovenia': 'SI',
                    'Denmark': 'DK',
                    'Croatia': 'HR',
                    'Malta': 'MT',
                    'Slovakia': 'SK',
                    'Germany': 'DE',
                    'Italy': 'IT',
                    'Netherlands': 'NL',
                    'Finland': 'FI',
                    'Estonia': 'EE',
                    'Cyprus': 'CY',
                    'Austria': 'AT',
                    'Sweden': 'SE',
                    'Ireland': 'IE',
                    'Latvia': 'LV',
                    'Poland': 'PL',
                    'Euro Zone': 'EA'}

def generategeo(countries: list) -> list:
    """Transform country names to country codes

    Args:
        countries (list): List of country names (in English)

    Returns:
        list: Eurostat country codes
    """
    geo = []
    for c in countries:
        try:
            geo.append(country_names_dict[c])
        except KeyError as e:
            print('Given country either doesn\'t exist or is not an EU member')
    return geo


def getGDP(start, end: str = dt.today().strftime("%Y-%m-%d"), countries: list = ['Poland']):

    geo = generategeo(countries)   

    raw_data = get_data('namq_10_gdp', filter_pars={
        's_adj': ['SCA'],
        'unit': ['CP_MNAC'], 
        'na_item': ['B1GQ'],
        'geo': geo
        })
    data = pd.DataFrame(raw_data[1:],
                        columns=[x if x != 'geo\\TIME_PERIOD' else 'geo' for x in raw_data[0]]).dropna(axis=1)
    y = data.select_dtypes(include=np.number).transpose()
    y.index = pd.to_datetime(y.index)
    # y = np.log(y).diff().dropna()
    y.columns = [c + '_gdp' for c in geo]
    
    return y[y.index.isin(pd.date_range(start, end))]

def getUNEMPLOYMENT(start, end: str = dt.today().strftime("%Y-%m-%d"), countries: list = ['Poland']):
    
    geo = generategeo(countries)   

    raw_data = get_data('une_rt_m', filter_pars={
        'age': ['TOTAL'],
        's_adj': ['SA'],
        'sex': ['T'],
        'unit': ['PC_ACT'],
        'geo': geo
        })
    data = pd.DataFrame(raw_data[1:],
                        columns=[x if x != 'geo\\TIME_PERIOD' else 'geo' for x in raw_data[0]]).dropna(axis=1)
    y = data.select_dtypes(include=np.number).transpose()
    y.index = pd.to_datetime(y.index)
    # y = np.log(y).diff().dropna()
    y.columns = [c  + '_unempl' for c in geo]
    
    return y[y.index.isin(pd.date_range(start, end))]

def getHICP(start: str, end: str = dt.today().strftime("%Y-%m-%d"), countries: list = ['Poland']) -> pd.DataFrame:
    
    geo = generategeo(countries)
    
    raw_data = get_data('prc_hicp_manr', filter_pars={
        'coicop': ['CP00'],
        'geo': geo
        })
    data = pd.DataFrame(raw_data[1:],
                    columns=[x if x != 'geo\\TIME_PERIOD' else 'geo' for x in raw_data[0]]).dropna(axis=1)
    
    y = data.select_dtypes(include=np.number).transpose()
    y.index = pd.to_datetime(y.index)
    y.columns = [c + '_hicp' for c in geo]
    
    return y[y.index.isin(pd.date_range(start, end))]


def getRATES(start: str, end: str = dt.today().strftime("%Y-%m-%d"), rate: str = 'M12', countries: list = ['Poland']) -> pd.DataFrame:
    """Download interest rates

    Args:
        countries (list): _description_
        start (str): _description_
        end (str): _description_
        rate (str, optional): Defaults to 'M12'. 
            Possible values:
            'DTD' for day-to-day, 
            'M1' for 1-month,
            'M3' for 3-month,
            'M6' for 6-month,
            'M12' for 12-month.

    Returns:
        pd.DataFrame: data frame with requested interest rates
    """
    geo = generategeo(countries)
    
    raw_data = get_data('irt_st_m', filter_pars={
        'int_rt': ['IRT_'+rate],
        'geo': geo
        })
    data = pd.DataFrame(raw_data[1:],
                    columns=[x if x != 'geo\\TIME_PERIOD' else 'geo' for x in raw_data[0]]).dropna(axis=1)
    y = data.select_dtypes(include=np.number).transpose()
    y.index = pd.to_datetime(y.index)
    y.columns = [c  + '_'+rate+'_rate' for c in geo]
    
    return y[y.index.isin(pd.date_range(start, end))]