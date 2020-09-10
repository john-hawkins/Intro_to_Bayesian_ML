import numpy as np
import pandas as pd
import sys
import datetime
import matplotlib.pyplot as plt

# CUSTOM LIBRARIES
sys.path.append('../../Dataset_Transformers')
from transform import DatasetGenerator as dg
from transform import Normalizer as nzr

df = pd.read_csv('data.csv')

# FIRST 24 RECORDS HAVE NULL PM2.5
df = df[24:].copy()

# ADD A DATE COLUMN 
df['Date'] = df.apply( lambda x : datetime.datetime(year=x['year'], month=x['month'], day=x['day']), axis=1 )

# AGGREGATE UP TO DAILY 
f = { 'Iws':['min','max','mean'], 'DEWP':['min','max','mean'], 'TEMP':['min','max','mean'], 'PRES':['min','max','mean'], 'pm2.5' :['min','max','mean']  }

df_total = df.groupby(['Date'], as_index=False).agg(f)
 
def join_sectors(input):
    if len(input[1])>1 :
        return '_'.join(input)
    else:
        return input[0]

df_total.columns = list(map(join_sectors, df_total.columns.values))

# REMOVE ROWS WITH NULL VALUES
df_temp = df_total[ np.isfinite(df_total['pm2.5_mean']) ]
df_total = df_temp

# MAKE A COPY FOR JOINING BACK WITH PREVIOUS VALUES
df_target = df_total.loc[:, ['Date', 'pm2.5_mean']].copy()
df_target['Date'] = df_target['Date'] - datetime.timedelta(days=1)
df_target.columns = ['Date', 'mean_pm2.5_tomorrow']

# LOG TRANSFORM THE TARGET
df_target['mean_pm2.5_mean_log'] = np.log(df_target['mean_pm2.5_tomorrow'])

df_j = df_total.merge(df_target, on=['Date' ], how='inner')

df_j['log_mean_pm2.5_tomorrow'] = np.log(df_j['mean_pm2.5_tomorrow'])
 
df_j.drop(['mean_pm2.5_tomorrow'], inplace=True, axis=1)

trainset = len(df_j) - 91
train_df = df_j.loc[0:trainset,:]
test_df = df_j.loc[trainset+1:,:]


# ###########################################################################################################
#  CREATE A NORMALISATION CONFIGURATION TO 
# ###########################################################################################################
config = nzr.create_padded_normalization_config(train_df, 0.05)

# ###########################################################################################################
#  RAW TARGET NORMALISED 
# ###########################################################################################################

target_col = "log_mean_pm2.5_tomorrow"

nzr.write_field_config(config, target_col, 'nzr_config_log_mean_tomoz.yaml')

train_df_norm = nzr.normalize(train_df, config, ['Date',"log_mean_pm2.5_tomorrow"] )
test_df_norm = nzr.normalize(test_df, config, ['Date',"log_mean_pm2.5_tomorrow"])
 
train_df_norm.to_csv('Train_log_mean_tomoz_norm.csv', sep=',', encoding='utf-8', index=False, header=True)
test_df_norm.to_csv('Test_log_mean_tomoz_norm.csv', sep=',', encoding='utf-8', index=False, header=True)



