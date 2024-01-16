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
import seaborn as sns

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

# 設定目標機場
base = 'TPE'

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
print(f"資料時段: {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")

# 所有航班關聯到的機場數量
all_airports = set(df['Dep'].unique()).union(df['Arr'].unique())
all_airports_df = sorted(all_airports, key=lambda x: (base not in x, x))
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

# 提取基地數據
df_base = df[df['Dep'] == base]
base_pax = df_base['PAX Total'].sum()

# 顯示結果
print(f"\n=== 所有場站資料 ===")
print(f"執飛航點數量: {num_airports}")
print(f"執飛航線數量: {num_routes}")
print(f"執飛航班數量: {total_flights}")
print(f"載運乘客總量: {total_pax}")
print(f"\n=== {base} 機場資料 ===")
print(f"{base} 離場航班數量: {len(df_base)}")
print(f"{base} 離境旅客人次: {base_pax}")


#%% 計算延誤的航班數量、平均時間和總時間
### 計算延誤的航班數量、平均時間和總時間

# 設定延誤門檻（超過即視為延誤）
delay_time_th = timedelta(0,0,0,0,15,0)		# 15 分鐘
delay_time_th_min = int(delay_time_th.total_seconds() // 60)

# 轉換 Timestamp 欄位為 datetime 格式
#df_base['STD'] = pd.to_datetime(df_base['STD'])
#df_base['Best Departure Time'] = pd.to_datetime(df_base['Best Departure Time'])

print(f"全航線延誤狀況統整")
print(f"（延誤 {delay_time_th_min} 分鐘以上者被視為延誤航班）")

# 離開有延誤的航班
delay_dep = df_base[df_base['Best Departure Time'] - df_base['STD'] > delay_time_th]
delay_dep_time_tot = (delay_dep['Best Departure Time'] - delay_dep['STD']).sum()
delay_dep_time_tot = delay_dep_time_tot.total_seconds() / 3600
delay_dep_time_tot = round(delay_dep_time_tot, 2)
delay_dep_time_avg = delay_dep['Best Departure Time'].sub(delay_dep['STD']).mean()
delay_dep_time_avg = delay_dep_time_avg.total_seconds() / 60
delay_dep_time_avg = round(delay_dep_time_avg, 1)
num_delay_dep = len(delay_dep)
delay_dep_pax_tot = delay_dep['PAX Total'].sum()

print(f"\n=== 離場航班 ===")
print(f"延誤起飛航班數量: {num_delay_dep} ({round(100*num_delay_dep/len(df_base), 2)}%)")
print(f"平均每航班延誤 {delay_dep_time_avg} 分鐘")
print(f"全月總延誤 {delay_dep_time_tot} 小時")
print(f"受影響乘客共 {delay_dep_pax_tot} 人次")


#%% 航班延誤之航線觀點
### 航班延誤之航線觀點

# 所有被考慮的航班皆為 base 出發故不列入考慮
all_airports_df = all_airports_df[~all_airports_df['Airport'].isin([base])]

# 航線延誤表單初始化
delay_airport_df = pd.DataFrame({
    'Destination': all_airports_df['Airport'],
    'Total Flights': 0,
    'Delayed Flights': 0
})

# 各航線航班數量
delay_airport = delay_dep['Arr'].value_counts()
delay_airport_df['Total Flights'] = delay_airport_df['Destination'].apply(lambda airport: df_base['Arr'].value_counts().get(airport, 0))

# 各航線延誤班次統計
delay_airport = delay_dep['Arr'].value_counts()
delay_airport_df['Delayed Flights'] = delay_airport_df['Destination'].apply(lambda airport: delay_airport.get(airport, 0))

# 各航線班次延誤百分比
delay_airport_df['Delay %'] = round(100*delay_airport_df['Delayed Flights']/delay_airport_df['Total Flights'], 2)

# 各航線總乘客數
delay_airport_df['Total PAX'] = delay_airport_df['Destination'].apply(lambda airport: df_base[df_base['Arr'] == airport]['PAX Total'].sum())

# 各航線受影響乘客數
delay_airport_df['Affected PAX'] = delay_airport_df['Destination'].apply(lambda airport: delay_dep[delay_dep['Arr'] == airport]['PAX Total'].sum())

# 各航線受影響乘客百分比
delay_airport_df['Affected %'] = round(100*delay_airport_df['Affected PAX']/delay_airport_df['Total PAX'], 2)

# 輸出延誤率最高的航線清單
if 1 == 1:
    save_path = os.path.join(outFolder, "on-time_performance_by_routes.csv")
    delay_airport_df.to_csv(save_path, index=False)
    print(f"航線延誤統計表輸出完成！")

# 印出離場延誤率最高的五座機場
top_delay_airport = delay_airport_df.nlargest(5, 'Delay %')
print(f"\n出發延誤率最高的五條航線為")
print(top_delay_airport[['Destination', 'Delayed Flights', 'Delay %', 'Affected PAX']])

# 將各機場離場航班延誤數量繪成直方圖
plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
plt.title(f"{base} On-time Performance by Routes\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
plt.xlabel("Destination")
plt.ylabel("Delay Rate (%)")
plt.ylim(0, 60)
plt.bar(delay_airport_df['Destination'], delay_airport_df['Delay %'])
plt.xticks(rotation=45)
plt.tick_params(axis='x', which='both', bottom=False, top=False)  # 隱藏 x 軸刻度
plt.tight_layout()
if 1 == 1:
    plt.savefig(os.path.join(outFolder, "on-time_performance_by_routes.jpg"))
    print(f"\n航線延誤統計圖輸出完成！")
plt.show()


#%% 航班延誤之肇因觀點（統計）
### 航班延誤之肇因觀點（統計）

# 列出所有獨立的 DLY Code
all_DLYC = set(df_base[['DLY1 Code MVT', 'DLY2 Code MVT', 'DLY3 Code MVT', 'DLY4 Code MVT']].apply(lambda x: x.str.strip()).values.flatten())
all_DLYC = {code for code in all_DLYC if pd.notna(code)}
all_DLYC_df = pd.DataFrame(sorted(all_DLYC), columns=['DLY Code'])

# 計算各 DLYC 發生的次數
melted_delay_dep = delay_dep.melt(value_vars=['DLY1 Code MVT', 'DLY2 Code MVT', 'DLY3 Code MVT', 'DLY4 Code MVT'], value_name='DLY Code')
DLYC_counts = melted_delay_dep['DLY Code'].value_counts().reset_index()
DLYC_counts.columns = ['DLY Code', 'Count']
total_DLYC_counts = DLYC_counts['Count'].sum()
DLYC_counts['Percentage'] = round((DLYC_counts['Count'] / total_DLYC_counts) * 100, 2)

# 以 DLY Code 和航點進行分組計算次數
DLYC_counts_airport = DLYC_counts
for airport in all_airports_df['Airport']:
    DLYC_counts_airport[airport] = np.nan
melted_delay_dep_dep = delay_dep.melt(id_vars=['Arr'], value_vars=['DLY1 Code MVT', 'DLY2 Code MVT', 'DLY3 Code MVT', 'DLY4 Code MVT'], value_name='DLY Code')
grouped_counts = melted_delay_dep_dep.groupby(['DLY Code', 'Arr']).size().reset_index(name='Count')

# 將計算結果填入表格
for index, row in DLYC_counts_airport.iterrows():
    dly_code = row['DLY Code']
    for airport in all_airports_df['Airport']:
        count_value = grouped_counts[(grouped_counts['DLY Code'] == dly_code) & (grouped_counts['Arr'] == airport)]['Count'].values
        if len(count_value) > 0:
            DLYC_counts_airport.at[index, airport] = count_value[0]
DLYC_counts_airport.fillna('', inplace=True)
DLYC_counts_airport = DLYC_counts_airport.sort_values(by='DLY Code')

# 輸出各航線發生延誤的原因統計表
if 1 == 1:
    save_path = os.path.join(outFolder, f"{base} on-time_performance_by_dly-code.csv")
    DLYC_counts_airport.to_csv(save_path, index=False)
    print(f"各航線發生延誤原因統計表輸出完成！")

# 新增一個欄位 'First Letter'，存放 'DLY Code' 欄位中的第一個字母
DLYC_counts_airport['DLY Code'] = DLYC_counts_airport['DLY Code'].str[0]

# 按照 'First Letter' 進行分組
DLYC_counts_airport = DLYC_counts_airport.apply(lambda x: pd.to_numeric(x, errors='coerce') if x.name != 'DLY Code' else x)
DLYC_counts_airport = DLYC_counts_airport.groupby('DLY Code').sum(min_count=1)
DLYC_counts_airport = DLYC_counts_airport.reset_index()
DLYC_counts_airport.fillna(0, inplace=True)


#%% 航班延誤之肇因觀點（直方圖）
### 航班延誤之肇因觀點（直方圖）

# 假設 DLYC_counts_aggregated 是包含 DLY Code, Count, Percentage, 以及機場名稱的 DataFrame

# 提取機場名稱
airports = DLYC_counts_airport.columns[3:]

# 使用 seaborn 的色彩搭配功能自動設定顏色
colors = sns.color_palette('husl', n_colors=len(DLYC_counts_airport['DLY Code'].unique()))

# 初始化繪圖
fig, ax = plt.subplots(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)

# 初始化每個 DLY Code 的底部位置
bottoms = np.zeros(len(airports))

# 繪製每一個 DLY Code 的方塊
for dly_code, color in zip(DLYC_counts_airport['DLY Code'].unique(), colors):
    counts = DLYC_counts_airport[DLYC_counts_airport['DLY Code'] == dly_code].iloc[0, 3:]
    ax.bar(airports, counts, bottom=bottoms, color=color, label=f'{dly_code}')
    bottoms += counts

# 加上標題及軸標籤
plt.title(f"{base} Delay Reasons by Routes\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
plt.xlabel("Destination")
plt.ylabel('Count of DLY Code')
plt.xticks(rotation=45)
plt.tick_params(axis='x', which='both', bottom=False, top=False)  # 隱藏 x 軸刻度
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Code')
plt.tight_layout()
if 1 == 1:
    plt.savefig(os.path.join(outFolder, f"{base} delay_reasons_by_routes.jpg"))
    print(f"\n各航線延誤原因統計圖輸出完成！")
plt.show()


#%% 航班延誤之肇因觀點（圓餅圖）
### 航班延誤之肇因觀點（圓餅圖）

# 提取需要的欄位
labels = [f"{code} ({percentage:.2f}%)" for code, percentage in zip(DLYC_counts_airport['DLY Code'], DLYC_counts_airport['Percentage'])]
sizes = DLYC_counts_airport['Percentage']

# 繪製餅圖
fig, ax = plt.subplots(figsize=(768/set_dpi, 768/set_dpi), dpi=set_dpi)
patches, autotexts = ax.pie(sizes, labels=labels, colors=colors, startangle=90, wedgeprops=dict(width=1, edgecolor='w'))
ax.set_facecolor('white')

# 將標記文字的顏色設定為與餅圖對應的顏色
for autotext, color in zip(autotexts, colors):
    autotext.set_color(color)

plt.title(f"{base} Delay Reasons Proportion\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
plt.tight_layout()
if 1 == 1:
    plt.savefig(os.path.join(outFolder, f"{base} delay_reasons_pie_chart.jpg"))
    print(f"\n延誤原因佔比圖輸出完成！")
plt.show()


# %%
