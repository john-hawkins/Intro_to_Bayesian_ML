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
f = {'pm2.5' :['min','max','mean']  }
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

#####################################################################
# EXTRACT OUT THE LAST 90 DAYS OF MEAN PM2.5 VALUES 
# THIS WILL BE USED TO GENERATE A PLOT
temp = df_total.loc[:,['Date','pm2.5_mean']]
temp2 = temp.tail(90)
temp2.to_csv("Last_90_days.csv", header=True, index=False)
# THIS PLOT WILL BE GENERATED IN THE NOTEBOOK
# series = pd.read_csv("Last_90_days.csv", header=0, index_col=0, parse_dates=True, squeeze=True)
# series.plot()

# ##############################################################
# FORCE THE DATE COLUMN TYPE
# NOT REQUIRED ANY MORE
#def convert_date_str(incol):
#    return datetime.datetime.strptime( incol, "%Y-%M-%d")
#
#df_total['Date'] = df_total['Date'].apply( convert_date_str )


# MAKE A COPY FOR JOINING BACK WITH PREVIOUS VALUES
df_prev = df_total.copy()
df_prev['Date'] = df_prev['Date'] + datetime.timedelta(days=7)
df_prev.columns = ['Date', 'current_min', 'current_max', 'current_mean']

df_j = df_prev.merge(df_total, on=['Date' ], how='inner')

df_prev['Date'] = df_prev['Date'] + datetime.timedelta(days=7)
df_prev.columns = ['Date', 'prev_min', 'prev_max', 'prev_mean']

df_j2 = df_prev.merge(df_j, on=['Date' ], how='inner')

df_j2['pm2.5_mean_diff'] = df_j2['pm2.5_mean'] - df_j2['current_mean']
df_j2['current_diff'] = df_j2['current_mean'] - df_j2['prev_mean']
 
keep_cols = ['Date', 'prev_min', 'prev_max', 'prev_mean', 'current_diff', 'current_min',
       'current_max', 'current_mean', 'pm2.5_mean_diff']
 
df_final = df_j2.loc[:, keep_cols]

trainset = len(df_final) - 91
train_df = df_final.loc[0:trainset,:]
test_df = df_final.loc[trainset+1:,:]


# ###########################################################################################################
# WRITE OUT THE FULL UN-NORMALISED VERSION
# ###########################################################################################################
train_df.to_csv('Simple_Train_full.csv', sep=',', encoding='utf-8', index=False, header=True)
test_df.to_csv('Simple_Test_full.csv', sep=',', encoding='utf-8', index=False, header=True)


# ###########################################################################################################
#  CREATE A NORMALISATION CONFIGURATION TO 
# ###########################################################################################################
config = nzr.create_padded_normalization_config(train_df, 0.05)

# ###########################################################################################################
#  RAW TARGET NORMALISED 
# ###########################################################################################################

target_col = "pm2.5_mean_diff"
nzr.write_field_config(config, target_col, 'nzr_config.yaml')

train_df_norm = nzr.normalize(train_df, config, ['Date'] )
test_df_norm = nzr.normalize(test_df, config, ['Date'])
 
train_df_norm.to_csv('Simple_Train_norm.csv', sep=',', encoding='utf-8', index=False, header=True)
test_df_norm.to_csv('Simple_Test_norm.csv', sep=',', encoding='utf-8', index=False, header=True)

