#%% 程式變數及套件初始化
### 程式變數及套件初始化

import os, time
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from datetime import datetime, timedelta

# 定義本程式起始路徑，若已執行過會繼承上次執行的路徑
if 'homePath' not in locals():
		homePath = os.path.dirname(os.path.abspath(__file__))

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
num_airports = len(set(df['Dep'].unique()).union(df['Arr'].unique()))

# 計算航線數量
num_routes = len(set(df['Flight'].unique()))

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
delay_time_th = timedelta(0,0,0,0,15,0)

# 轉換 Timestamp 欄位為 datetime 格式
df['STD'] = pd.to_datetime(df['STD'])
df['STA'] = pd.to_datetime(df['STA'])
df['Best Departure Time'] = pd.to_datetime(df['Best Departure Time'])
df['Best Arrival Time'] = pd.to_datetime(df['Best Arrival Time'])

print(f"全航線延誤狀況統整")

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
print(f"延誤航班數量: {num_delay_dep} ({round(100*num_delay_dep/total_flights, 2)}%)")
print(f"平均每航班延誤 {delay_dep_time_avg} 分鐘")
print(f"全月總延誤 {delay_dep_time_tot} 小時")
print(f"受影響乘客共 {delay_dep_pax_tot} 人")

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
print(f"延誤航班數量: {num_delay_arr} ({round(100*num_delay_arr/total_flights, 2)}%)")
print(f"平均每航班延誤 {delay_arr_time_avg} 分鐘")
print(f"全月總延誤 {delay_arr_time_tot} 小時")
print(f"受影響乘客共 {delay_arr_pax_tot} 人")

# 飛時有延長的航班
long_flight = df[df['Flight Time'] > df['EET']]
long_flight_time_tot = long_flight['Flight Time'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).sum() - long_flight['EET'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).sum()
long_flight_time_tot = long_flight_time_tot.total_seconds() / 3600
long_flight_time_tot = round(long_flight_time_tot, 2)
long_flight_time_avg = long_flight['Flight Time'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).mean() - long_flight['EET'].apply(lambda x: timedelta(hours=x.hour, minutes=x.minute, seconds=x.second)).mean()
long_flight_time_avg = long_flight_time_avg.total_seconds() / 60
long_flight_time_avg = round(long_flight_time_avg, 1)
num_long_flight = len(long_flight)

#print(f"\n=== 飛行時間有延長 ===")
#print(f"航班數量: {num_long_flight} ({round(100*num_long_flight/total_flights, 2)}%)")
#print(f"平均每航班延長 {long_flight_time_avg} 分鐘")
#print(f"全月總延長 {long_flight_time_tot} 小時")


#%% 航班延誤之機場觀點分析（離場部分）
### 航班延誤之機場觀點分析（離場部分）

# 初始化 delay_dep_airport_df，將所有值設為 0
all_airports_df = pd.DataFrame({'Airport': df['Dep'].unique()})
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

# 顯示結果
top_delay_dep_airport = delay_dep_airport_df.nlargest(5, 'Delay %')
print(f"離場延誤率最高的五座機場為")
print(top_delay_dep_airport[['Airport', 'Delayed Flights', 'Delay %', 'Affected PAX']])

# 輸出檔案
if 1 == 2:
    # 視窗選取儲存路徑
    default_filename = "delayed_flights_by_airport.csv"
    save_path = filedialog.asksaveasfilename(
        initialdir=os.path.abspath(homePath),
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="請選擇儲存路徑",
        initialfile=default_filename
    )
    # 如果選擇了路徑，則輸出為 .csv 檔
    if save_path:
        delay_dep_airport_df.to_csv(save_path, index=False)
        print(f"已成功儲存 CSV 檔。")
    else:
        print("未選擇儲存路徑。")


#%% 航班延誤之機場觀點分析（進場部分）
### 航班延誤之機場觀點分析（進場部分）

# 初始化 delay_arr_airport_df，將所有值設為 0
all_airports_df = pd.DataFrame({'Airport': df['Arr'].unique()})
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

# 顯示結果
top_delay_arr_airport = delay_arr_airport_df.nlargest(5, 'Delay %')
print(f"進場延誤率最高的五座機場為")
print(top_delay_arr_airport[['Airport', 'Delayed Flights', 'Delay %', 'Affected PAX']])

# 輸出檔案
if 1 == 2:
    # 視窗選取儲存路徑
    default_filename = "delayed_flights_by_airport.csv"
    save_path = filedialog.asksaveasfilename(
        initialdir=os.path.abspath(homePath),
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="請選擇儲存路徑",
        initialfile=default_filename
    )
    # 如果選擇了路徑，則輸出為 .csv 檔
    if save_path:
        delay_arr_airport_df.to_csv(save_path, index=False)
        print(f"已成功儲存 CSV 檔。")
    else:
        print("未選擇儲存路徑。")


#%% 航班延誤之航班觀點分析（未完成）
### 航班延誤之航班觀點分析

# 計算離場有延誤的航班數量前三多的航班編號及受到延誤的航班數量
delay_dep_flight = delay_dep['Flight'].value_counts()
delay_dep_airport_df = pd.DataFrame({
    'Airport': delay_dep_flight.index,
    'Delayed Flights': delay_dep['Flight'].value_counts().values
})

# 計算進場有延誤的航班數量前三多的航班編號及受到延誤的航班數量
delay_arr_flight = delay_arr['Flight'].value_counts()
delay_arr_airport_df = pd.DataFrame({
    'Airport': delay_arr_flight.index,
    'Delayed Flights': delay_arr['Flight'].value_counts().values
})

# 顯示結果
print("各航班離場延誤統計：")
print(delay_dep_airport_df)
print("\n")

print("各航班進場延誤統計：")
print(delay_arr_airport_df)


# %%
