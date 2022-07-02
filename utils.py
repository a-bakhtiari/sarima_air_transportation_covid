import os
import pandas as pd
from statsmodels.tsa.stattools import adfuller

def read_data(path):
    data_list = os.listdir(path)
    df_all = pd.DataFrame()
    for file in data_list:
        year = [int(s) for s in file.split() if s.isdigit()][0]
        if year!= 1400:
            year = int('13'+str(year))
        day = 29 # to be able to convert to gregorian
        df = pd.read_excel(path+file)
        try:
            df.columns = ['tedad_parvaz_exit', 'tedad_parvaz_entry', 'post_exit', 'post_entry',
                          'bar_exit', 'bar_entry', 'mosafer_exit', 'mosafer_entry', 'month']
        except:
            df = df.drop(['Unnamed: 7', 'Unnamed: 4'], axis=1)
            df.columns = ['tedad_parvaz_exit', 'tedad_parvaz_entry', 'post_exit', 'post_entry',
                          'bar_exit', 'bar_entry', 'mosafer_exit', 'mosafer_entry', 'month']

        df = df.dropna(axis=0)
        df['year'] = year
        df['day'] = day
        if df_all.empty:
            df_all = df.copy()
        else:
            df_all = pd.concat([df_all, df], axis=0)
    return df_all

# Jalali to gregorian. this way calculation is way easier    
def jalali_to_gregorian(jy, jm, jd):
 jy += 1595
 days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
 if (jm < 7):
  days += (jm - 1) * 31
 else:
  days += ((jm - 7) * 30) + 186
 gy = 400 * (days // 146097)
 days %= 146097
 if (days > 36524):
  days -= 1
  gy += 100 * (days // 36524)
  days %= 36524
  if (days >= 365):
   days += 1
 gy += 4 * (days // 1461)
 days %= 1461
 if (days > 365):
  gy += ((days - 1) // 365)
  days = (days - 1) % 365
 gd = days + 1
 if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
  kab = 29
 else:
  kab = 28
 sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
 gm = 0
 while (gm < 13 and gd > sal_a[gm]):
  gd -= sal_a[gm]
  gm += 1
  final_date = '-'.join([str(gy), str(gm), str(gd)])
 return final_date

def clean_data(df_all):
    # remove جمع کل
    df_all = df_all[df_all['month']!='جمع كل']

    month_list = df_all['month'].iloc[-12:].tolist() # draw up a list of jalalian months

    month_replace_list = {month_list[i]:i+1 for i in range(len(month_list))}
    df_all['month'].replace(month_replace_list, inplace=True)

    # keep a column for the jalali version of the date
    df_all['jalali_date'] = df_all['year'].astype(str)+'_'+df_all['month'].astype(str)
    df_all['date'] = df_all.apply(
    lambda row: jalali_to_gregorian(row['year'], row['month'], row['day']), axis=1
    )

    df_all['date'] = pd.to_datetime(df_all['date'])

    # old jalalian date columns
    df_all = df_all.drop(['month', 'year', 'day'], axis=1).reset_index(drop=True)
    return df_all

def preprocess_data(path):
    df = read_data(path)
    df = clean_data(df)
    return df

def perform_adf_test(series):
    results = dict()
    result_all = adfuller(series)
    results.update({'ADF Statistic':[result_all[0]]})
    results.update({'p-value':[result_all[1]]})
    return results