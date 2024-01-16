#%% 程式變數及套件初始化
### 程式變數及套件初始化

import os, time
import numpy as np
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 定義本程式起始路徑，若已執行過會繼承上次執行的路徑
if 'homePath' not in locals():
		homePath = os.path.dirname(os.path.abspath(__file__))

# 以目前日期設定輸出目錄名稱，若無則創建
outFolder = os.path.join(homePath, datetime.now().strftime('output_%y%m%d'))
if not os.path.exists(outFolder):
    os.makedirs(outFolder)

# 設定通用字型為思源黑體 Noto Sans CJK TC
#font_path = fm.findfont(fm.FontProperties(family='Noto Sans CJK TC'))
#font_prop = fm.FontProperties(fname=font_path)

# 設定繪圖解析度
set_dpi = 144

print("初始化完成！")


#%% 以彈出式視窗選取欲分析之航班總表
### 以彈出式視窗選取欲分析之航班總表

def open_file_dialog():
    file_path = filedialog.askopenfilename(
        initialdir=homePath,
        filetypes=[("Excel files", "*.xls;*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")],
        title="請選擇航班總表檔案"
    )
    
    if file_path:
        # Read the selected file into a DataFrame
        global df
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        print("已成功讀取航班總表！")
        #print(df.head())

        # Close the main window
        root.destroy()

# Create the main window
root = tk.Tk()
root.withdraw()  # Hide the main window
root.attributes('-topmost', 1)

# Open file dialog when the script is run
open_file_dialog()

# Main loop
root.mainloop()


#%% 計算時段內獨立航班及航點數量
### 計算時段內獨立航班及航點數量

# 扣除重複航班（Irreg State 欄為 RTR 的列）
df = df[df['Irreg State'] != 'RTR']

# 資料時間範圍
date_start = pd.to_datetime(df['STD']).min() + timedelta(0,0,0,0,0,8)
date_end = pd.to_datetime(df['STD']).max() + timedelta(0,0,0,0,0,8)

# 所有航班關聯到的機場數量
all_airports = set(df['Dep'].unique()).union(df['Arr'].unique())
all_airports_df = sorted(all_airports, key=lambda x: ('TPE' not in x, x))
all_airports_df = pd.DataFrame(all_airports_df, columns=['Airport'])
num_airports = len(all_airports)

# 計算航線數量
all_routes = set(df['Flight'].unique())
all_routes_df = pd.DataFrame(sorted(all_routes), columns=['Flight'])
num_routes = len(all_routes)

# 計算總航班數量
total_flights = len(df)

# 計算整個月所有航線載運的總乘客量
df['PAX Total'] = df['PAX flown'].apply(lambda x: int(x.split('//')[-1]) if '//' in str(x) else 0)
total_pax = df['PAX Total'].sum()

# 計算 TPE 離場航班數量
dep_from_tpe = len(df[df['Dep'] == 'TPE'])

# 計算 TPE 進場航班數量
arr_to_tpe = len(df[df['Arr'] == 'TPE'])

# 顯示結果
print(f"資料時段: {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
print(f"時段內執飛航點數量: {num_airports}")
print(f"時段內執飛航線數量: {num_routes}")
print(f"時段內執飛航班數量: {total_flights}")
print(f"時段內載運乘客總量: {total_pax}")
#print(f"TPE 離場航班數量: {dep_from_tpe}")
#print(f"TPE 進場航班數量: {arr_to_tpe}")


#%% 計算延誤以及飛時延長的航班數量、平均時間和總時間
### 計算延誤以及飛時延長的航班數量、平均時間和總時間

# 設定延誤門檻（超過即視為延誤）
delay_time_th = timedelta(0,0,0,0,15,0)		# 15 分鐘
delay_time_th_min = int(delay_time_th.total_seconds() // 60)

# 轉換 Timestamp 欄位為 datetime 格式
df['STD'] = pd.to_datetime(df['STD'])
df['STA'] = pd.to_datetime(df['STA'])
df['Best Departure Time'] = pd.to_datetime(df['Best Departure Time'])
df['Best Arrival Time'] = pd.to_datetime(df['Best Arrival Time'])

print(f"全航線延誤狀況統整")
print(f"（延誤 {delay_time_th_min} 分鐘以上者被視為延誤航班）")

# 離開有延誤的航班
delay_dep = df[df['Best Departure Time'] - df['STD'] > delay_time_th]
delay_dep_time_tot = (delay_dep['Best Departure Time'] - delay_dep['STD']).sum()
delay_dep_time_tot = delay_dep_time_tot.total_seconds() / 3600
delay_dep_time_tot = round(delay_dep_time_tot, 2)
delay_dep_time_avg = delay_dep['Best Departure Time'].sub(delay_dep['STD']).mean()
delay_dep_time_avg = delay_dep_time_avg.total_seconds() / 60
delay_dep_time_avg = round(delay_dep_time_avg, 1)
num_delay_dep = len(delay_dep)
delay_dep_pax_tot = delay_dep['PAX Total'].sum()

print(f"\n=== 離場航班 ===")
print(f"延誤起飛航班數量: {num_delay_dep} ({round(100*num_delay_dep/total_flights, 2)}%)")
print(f"平均每航班延誤 {delay_dep_time_avg} 分鐘")
print(f"全月總延誤 {delay_dep_time_tot} 小時")
print(f"受影響乘客共 {delay_dep_pax_tot} 人次")

# 抵達有延誤的航班
delay_arr = df[df['Best Arrival Time'] - df['STA'] > delay_time_th]
delay_arr_time_tot = (delay_arr['Best Arrival Time'] - delay_arr['STA']).sum()
delay_arr_time_tot = delay_arr_time_tot.total_seconds() / 3600
delay_arr_time_tot = round(delay_arr_time_tot, 2)
delay_arr_time_avg = delay_arr['Best Arrival Time'].sub(delay_arr['STA']).mean()
delay_arr_time_avg = delay_arr_time_avg.total_seconds() / 60
delay_arr_time_avg = round(delay_arr_time_avg, 1)
num_delay_arr = len(delay_arr)
delay_arr_pax_tot = delay_arr['PAX Total'].sum()

print(f"\n=== 進場航班 ===")
print(f"延誤抵達航班數量: {num_delay_arr} ({round(100*num_delay_arr/total_flights, 2)}%)")
print(f"平均每航班延誤 {delay_arr_time_avg} 分鐘")
print(f"全月總延誤 {delay_arr_time_tot} 小時")
print(f"受影響乘客共 {delay_arr_pax_tot} 人次")

# 離開或抵達有延誤的航班
delay_all = pd.concat([delay_arr, delay_dep]).drop_duplicates()
num_delay = len(delay_all)
delay_pax_tot = delay_all['PAX Total'].sum()

print(f"\n=== 總計 ===")
print(f"受延誤航班總數: {num_delay} ({round(100*num_delay/total_flights, 2)}%)")
print(f"受影響乘客共 {delay_pax_tot} 人次")

# 飛時有延長的航班
#long_flight = df[df['Flight Time'] > df['EET']]
#long_flight_time_tot = long_flight['Flight Time'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).sum() - long_flight['EET'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).sum()
#long_flight_time_tot = long_flight_time_tot.total_seconds() / 3600
#long_flight_time_tot = round(long_flight_time_tot, 2)
#long_flight_time_avg = long_flight['Flight Time'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).mean() - long_flight['EET'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).mean()
#long_flight_time_avg = long_flight_time_avg.total_seconds() / 60
#long_flight_time_avg = round(long_flight_time_avg, 1)
#num_long_flight = len(long_flight)

#print(f"\n=== 飛行時間有延長 ===")
#print(f"航班數量: {num_long_flight} ({round(100*num_long_flight/total_flights, 2)}%)")
#print(f"平均每航班延長 {long_flight_time_avg} 分鐘")
#print(f"全月總延長 {long_flight_time_tot} 小時")


#%% 航班延誤之機場觀點分析（離場部分）
### 航班延誤之機場觀點分析（離場部分）

# 機場延誤航班表單初始化
delay_dep_airport_df = pd.DataFrame({
    'Airport': all_airports_df['Airport'],
    'Total Flights': 0,
    'Delayed Flights': 0
})

# 各機場總離場航班數量
delay_dep_airport = delay_dep['Dep'].value_counts()
delay_dep_airport_df['Total Flights'] = delay_dep_airport_df['Airport'].apply(lambda airport: df['Dep'].value_counts().get(airport, 0))

# 各機場離場航班延誤數量統計
delay_dep_airport = delay_dep['Dep'].value_counts()
delay_dep_airport_df['Delayed Flights'] = delay_dep_airport_df['Airport'].apply(lambda airport: delay_dep_airport.get(airport, 0))

# 計算各機場離場航班延誤百分比

delay_dep_airport_df['Delay %'] = round(100*delay_dep_airport_df['Delayed Flights']/delay_dep_airport_df['Total Flights'], 2)

# 計算每個機場受延誤的總乘客數
delay_dep_airport_df['Total PAX'] = delay_dep_airport_df['Airport'].apply(lambda airport: df[df['Dep'] == airport]['PAX Total'].sum())

# 計算每個機場對應的受影響乘客數
delay_dep_airport_df['Affected PAX'] = delay_dep_airport_df['Airport'].apply(lambda airport: delay_dep[delay_dep['Dep'] == airport]['PAX Total'].sum())

# 計算受班機延誤影響的乘客百分比
delay_dep_airport_df['Affected %'] = round(100*delay_dep_airport_df['Affected PAX']/delay_dep_airport_df['Total PAX'], 2)

# 輸出離場延誤率最高的機場清單
if 1 == 1:
    save_path = os.path.join(outFolder, "on-time_performance_departures_by_airport.csv")
    delay_dep_airport_df.to_csv(save_path, index=False)
    print(f"機場延誤出發統計表輸出完成！")

# 印出離場延誤率最高的五座機場
top_delay_dep_airport = delay_dep_airport_df.nlargest(5, 'Delay %')
print(f"\n出發延誤率最高的五座機場為")
print(top_delay_dep_airport[['Airport', 'Delayed Flights', 'Delay %', 'Affected PAX']])

# 將各機場離場航班延誤數量繪成直方圖
plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
plt.title(f"On-time Performance of JX Departures by Airports\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
plt.xlabel("Airport (IATA Code)")
plt.ylabel("Delay Rate (%)")
plt.ylim(0, 60)
plt.bar(delay_dep_airport_df['Airport'], delay_dep_airport_df['Delay %'])
plt.xticks(rotation=45)
plt.tick_params(axis='x', which='both', bottom=False, top=False)  # 隱藏 x 軸刻度
plt.tight_layout()
if 1 == 1:
    plt.savefig(os.path.join(outFolder, "on-time_performance_departures_by_airport.jpg"))
    print(f"\n機場延誤出發統計圖輸出完成！")
plt.show()


#%% 航班延誤之機場觀點分析（進場部分）
### 航班延誤之機場觀點分析（進場部分）

# 機場延誤航班表單初始化
delay_arr_airport_df = pd.DataFrame({
    'Airport': all_airports_df['Airport'],
    'Total Flights': 0,
    'Delayed Flights': 0
})

# 各機場總離場航班數量
delay_arr_airport = delay_arr['Arr'].value_counts()
delay_arr_airport_df['Total Flights'] = delay_arr_airport_df['Airport'].apply(lambda airport: df['Arr'].value_counts().get(airport, 0))

# 各機場離場航班延誤數量統計
delay_arr_airport = delay_arr['Arr'].value_counts()
delay_arr_airport_df['Delayed Flights'] = delay_arr_airport_df['Airport'].apply(lambda airport: delay_arr_airport.get(airport, 0))

# 計算各機場離場航班延誤百分比

delay_arr_airport_df['Delay %'] = round(100*delay_arr_airport_df['Delayed Flights']/delay_arr_airport_df['Total Flights'], 2)

# 計算每個機場受延誤的總乘客數
delay_arr_airport_df['Total PAX'] = delay_arr_airport_df['Airport'].apply(lambda airport: df[df['Arr'] == airport]['PAX Total'].sum())

# 計算每個機場對應的受影響乘客數
delay_arr_airport_df['Affected PAX'] = delay_arr_airport_df['Airport'].apply(lambda airport: delay_arr[delay_arr['Arr'] == airport]['PAX Total'].sum())

# 計算受班機延誤影響的乘客百分比
delay_arr_airport_df['Affected %'] = round(100*delay_arr_airport_df['Affected PAX']/delay_arr_airport_df['Total PAX'], 2)

# 輸出進場延誤率最高的機場清單
if 1 == 1:
    save_path = os.path.join(outFolder, "on-time_performance_arrivals_by_airport.csv")
    delay_arr_airport_df.to_csv(save_path, index=False)
    print(f"機場延誤抵達統計表輸出完成！")

# 印出進場延誤率最高的五座機場
top_delay_arr_airport = delay_arr_airport_df.nlargest(5, 'Delay %')
print(f"\n抵達延誤率最高的五座機場為")
print(top_delay_arr_airport[['Airport', 'Delayed Flights', 'Delay %', 'Affected PAX']])

# 將各機場進場航班延誤數量繪成直方圖
plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
plt.title(f"On-time Performance of JX Arrivals by Airports\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
plt.xlabel("Airport (IATA Code)")
plt.ylabel("Delay Rate (%)")
plt.ylim(0, 60)
plt.bar(delay_arr_airport_df['Airport'], delay_arr_airport_df['Delay %'])
plt.xticks(rotation=45)
plt.tick_params(axis='x', which='both', bottom=False, top=False)  # 隱藏 x 軸刻度
plt.tight_layout()
if 1 == 1:
    plt.savefig(os.path.join(outFolder, "on-time_performance_arrivals_by_airport.jpg"))
    print(f"\n機場延誤抵達統計圖輸出完成！")
plt.show()


#%% 航班延誤之航班觀點分析
### 航班延誤之航班觀點分析

# 航班延誤表單初始化
delay_route_df = pd.DataFrame({
    'Flight': all_routes_df['Flight'],
    'Total Flights': 0,
    'Delayed Flights': 0
})

# 各航班執非數量
delay_route = delay_all['Flight'].value_counts()
delay_route_df['Total Flights'] = delay_route_df['Flight'].apply(lambda flight: df['Flight'].value_counts().get(flight, 0))

# 各航班延誤次數統計
delay_route = delay_all['Flight'].value_counts()
delay_route_df['Delayed Flights'] = delay_route_df['Flight'].apply(lambda flight: delay_route.get(flight, 0))

# 計算各航班延誤百分比

delay_route_df['Delay %'] = round(100*delay_route_df['Delayed Flights']/delay_route_df['Total Flights'], 2)

# 計算每個航班受延誤的總乘客數
delay_route_df['Total PAX'] = delay_route_df['Flight'].apply(lambda flight: df[df['Flight'] == flight]['PAX Total'].sum())

# 計算每個航班對應的受影響乘客數
delay_route_df['Affected PAX'] = delay_route_df['Flight'].apply(lambda flight: delay_all[delay_all['Flight'] == flight]['PAX Total'].sum())

# 計算受班機延誤影響的乘客百分比
delay_route_df['Affected %'] = round(100*delay_route_df['Affected PAX']/delay_route_df['Total PAX'], 2)

# 輸出延誤率最高的航班清單
if 1 == 1:
    save_path = os.path.join(outFolder, "on-time_performance_departures_by_flight.csv")
    delay_route_df.to_csv(save_path, index=False)
    print(f"航班延誤統計表輸出完成！")

# 印出延誤率最高的五個航班
top_delay_route = delay_route_df.nlargest(5, 'Delay %')
print(f"\n出發延誤率最高的五個航班")
print(top_delay_route[['Flight', 'Delayed Flights', 'Delay %', 'Affected PAX']])

# 將各航班延誤次數繪成直方圖
plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
plt.title(f"On-time Performance of JX Departures by Flights\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
plt.xlabel("Flight Number")
plt.ylabel("Delay Rate (%)")
plt.ylim(0, 100)
plt.bar(delay_route_df['Flight'], delay_route_df['Delay %'])
plt.xticks(rotation=90)
plt.tick_params(axis='x', which='both', bottom=False, top=False)  # 隱藏 x 軸刻度
plt.tight_layout()
if 1 == 1:
    plt.savefig(os.path.join(outFolder, "on-time_performance_departures_by_flight.jpg"))
    print(f"\n航班延誤統計圖輸出完成！")
plt.show()


#%% 航班延誤之肇因觀點分析
### 航班延誤之肇因觀點分析

# 列出所有獨立的 DLY Code
all_DLYC = set(df[['DLY1 Code MVT', 'DLY2 Code MVT', 'DLY3 Code MVT', 'DLY4 Code MVT']].apply(lambda x: x.str.strip()).values.flatten())
all_DLYC = {code for code in all_DLYC if pd.notna(code)}
all_DLYC_df = pd.DataFrame(sorted(all_DLYC), columns=['DLY Code'])

# 計算各 DLYC 發生的次數
melted_delay_all = delay_all.melt(value_vars=['DLY1 Code MVT', 'DLY2 Code MVT', 'DLY3 Code MVT', 'DLY4 Code MVT'], value_name='DLY Code')
DLYC_counts = melted_delay_all['DLY Code'].value_counts().reset_index()
DLYC_counts.columns = ['DLY Code', 'Count']
total_DLYC_counts = DLYC_counts['Count'].sum()
DLYC_counts['Percentage'] = round((DLYC_counts['Count'] / total_DLYC_counts) * 100, 2)

# 以 DLY Code 和機場進行分組計算次數
DLYC_counts_airport = DLYC_counts
for airport in all_airports_df['Airport']:
    DLYC_counts_airport[airport] = np.nan
melted_delay_all_dep = delay_all.melt(id_vars=['Dep'], value_vars=['DLY1 Code MVT', 'DLY2 Code MVT', 'DLY3 Code MVT', 'DLY4 Code MVT'], value_name='DLY Code')
grouped_counts = melted_delay_all_dep.groupby(['DLY Code', 'Dep']).size().reset_index(name='Count')

# 將計算結果填入表格
for index, row in DLYC_counts_airport.iterrows():
    dly_code = row['DLY Code']
    for airport in all_airports_df['Airport']:
        count_value = grouped_counts[(grouped_counts['DLY Code'] == dly_code) & (grouped_counts['Dep'] == airport)]['Count'].values
        if len(count_value) > 0:
            DLYC_counts_airport.at[index, airport] = round(count_value[0], 0)
DLYC_counts_airport.fillna('', inplace=True)

# 輸出各機場發生延誤的原因統計表
if 1 == 1:
    save_path = os.path.join(outFolder, "on-time_performance_airport_to_dly-code.csv")
    DLYC_counts_airport.to_csv(save_path, index=False)
    print(f"各機場發生延誤原因統計表輸出完成！")


# 列出所有航班發生各 DLYC 的次數
#DLYC_counts_flight = 


#%%

