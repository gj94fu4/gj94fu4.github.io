#%% 程式變數及套件初始化
### 程式變數及套件初始化

# 系統、時間與視窗設定
import os, time, locale
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog

# 數學運算與資料處理
import math
import numpy as np
import pandas as pd

# 圖表繪製
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import seaborn as sns

# 定義本程式的語言和時區
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

# 定義本程式起始路徑，若已執行過會繼承上次執行的路徑
if 'homePath' not in locals():
		homePath = os.path.dirname(os.path.abspath(__file__))

# 以目前日期設定輸出目錄名稱，若無則創建
outFolder = os.path.join(homePath, datetime.now().strftime('output_%y%m%d'))
if not os.path.exists(outFolder):
    os.makedirs(outFolder)

# 目標參數設定
base = 'TPE'
date_range = ['2023-01-01', '2023-12-31']

# 固定參數設定
set_dpi = 144   # 繪圖解析度
file_ID = 1     # 是否輸出表單
fig_ID = 1      # 是否輸出圖

# 執行參數設定：[全, 月, 週, 日, 時]
run_ID = [1, 1, 1, 1, 1]

# 初始化完成！
print("初始化完成！")


#%% 以彈出式視窗選取欲分析之航班總表
### 以彈出式視窗選取欲分析之航班總表

# 定義以彈出式視窗選擇讀取檔案的功能
def open_file_dialog():
    # 定義彈出式視窗內容
    file_paths = filedialog.askopenfilenames(
        initialdir=homePath,
        filetypes=[("Excel files", "*.xls;*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")],
        title="請選擇航班總表檔案"
    )
    
    if file_paths:
        # 初始化一個空的 DataFrame
        df = pd.DataFrame()

        # 逐一讀取每個檔案，並合併到 df
        for file_path in file_paths:
            if file_path.endswith('.csv'):
                temp_df = pd.read_csv(file_path)
            else:
                temp_df = pd.read_excel(file_path)
            df = pd.concat([df, temp_df], ignore_index=True)

        # 關閉彈出式視窗
        root.destroy()

        print("已成功讀取航班總表！")
        return df

# 創建彈出式視窗並提取到最上層
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', 1)

# 從彈出式視窗選擇檔案並讀取
df = open_file_dialog()

# 只取旅客航班（Service Type 為 G 或 J）
service_type = ['G', 'J']
df = df[df['Service Type'].isin(service_type)]

# 扣除重複航班及 Irreg State 欄為 RTR 的列
df = df.drop_duplicates(subset=['Flight', 'STD', 'STA'])
df = df[df['Irreg State'] != 'RTR']

# 執行主要程序
root.mainloop()

# 調整時間日期格式
df = df.copy()
df = df.sort_values(by='STD')
df['STD'] = pd.to_datetime(df['STD'])
df['LTD'] = pd.to_datetime(df['LTD'])
df['STA'] = pd.to_datetime(df['STA'])
df['LTA'] = pd.to_datetime(df['LTA'])
df['Best Departure Time'] = pd.to_datetime(df['Best Departure Time'])


#%% 計算時段內獨立航班及航點數量
### 計算時段內獨立航班及航點數量

# 定義資料時間範圍
# !!! 此處設定機場時區為 +8，未來需修改由基地（base）自動判讀。 !!!
if 'date_range' in locals():
    date_range = pd.to_datetime(date_range)
    df = df[(df['LTD'] >= date_range[0]) & (df['LTD'] < date_range[1] + timedelta(days=1))]
date_start = max(df['STD'].min() + timedelta(0,0,0,0,0,8), date_range[0])
date_end   = min(df['STD'].max() + timedelta(0,0,0,0,0,8), date_range[1] + timedelta(days=1))
print(f"資料時段: {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")

# 所有航班關聯到的機場數量
all_AP = set(df['Dep'].unique()).union(df['Arr'].unique())
all_AP_df = sorted(all_AP, key=lambda x: (base not in x, x))
all_AP_df = pd.DataFrame(all_AP_df, columns=['Airport'])
num_AP = len(all_AP)

# 時間區段內執飛航線數量
all_RTE = set(df['Flight'].unique())
all_RTE_df = pd.DataFrame(sorted(all_RTE), columns=['Flight'])
num_RTE = len(all_RTE)

# 計算總航班數量
tot_FLT = len(df)

# 計算整個月所有航線載運的總乘客量
df = df.copy()
df['PAX Total'] = df['PAX flown'].apply(lambda x: int(x.split('//')[-1]) if '//' in str(x) else 0)
tot_PAX = df['PAX Total'].sum()

# 提取基地數據
df_base = df[df['Dep'] == base]
base_PAX = df_base['PAX Total'].sum()

# 顯示結果
print(f"\n=== 所有場站資料 ===")
print(f"執飛航點數量: {num_AP}")
print(f"執飛航線數量: {num_RTE}")
print(f"執飛航班數量: {tot_FLT}")
print(f"載運乘客總量: {tot_PAX}")
print(f"\n=== {base} 機場資料 ===")
print(f"{base} 離場航班數量: {len(df_base)}")
print(f"{base} 離境旅客人次: {base_PAX}")


#%% 航班準時率分析函數定義
### 航班準時率分析函數定義

# 設定延誤門檻（超過即視為延誤）
DT_th = timedelta(0,0,0,0,15,0)		# 15 分鐘
DT_th_min = int(DT_th.total_seconds() // 60)

def otp_calc(df_intrest, otp_type):

    # 資料時間範圍
    sub_start = pd.to_datetime(df_intrest['LTD']).min()
    sub_end = pd.to_datetime(df_intrest['LTD']).max()

    # 資料篩選分類
    if otp_type == 0:
        file_key = 'Overall'
        print(f"{base} 延誤狀況統整")
        print(f"（延誤 {DT_th_min} 分鐘以上者計之）")
        print(f"\n=== 全時段 ===")
    elif otp_type == 4:
        file_key = 'Period'
        sub_start = pd.to_datetime(df_intrest['LTD']).min().hour
        #print(f"\n=== {sub_start}:00 to {sub_start + 1}:00 ===")
    elif otp_type == 3:
        file_key = 'Day'
        #print(f"\n=== {sub_start.strftime('%Y-%m-%d')} ===")
    elif otp_type == 2:
        file_key = 'Period'
        #print(f"\n=== {sub_start.strftime('%YW%U')} ===")
    elif otp_type == 1:
        file_key = 'Period'
        #print(f"\n=== {sub_start.strftime('%Y-%m')} ===")
    else:
        file_key = 'Any'
        #print(f"\n=== {sub_start.strftime('%Y-%m-%d')} to {sub_end.strftime('%Y-%m-%d')}")

    # 有延誤起飛的航班
    DLY = df_intrest[df_intrest['Best Departure Time'] - df_intrest['STD'] > DT_th]
    DLYT_ttl = (DLY['Best Departure Time'] - DLY['STD']).sum()
    DLYT_ttl = DLYT_ttl.total_seconds() / 3600
    DLYT_ttl = round(DLYT_ttl, 2)
    DLYT_avg = DLY['Best Departure Time'].sub(DLY['STD']).mean()
    DLYT_avg = DLYT_avg.total_seconds() / 60
    DLYT_avg = round(DLYT_avg, 1)
    if math.isnan(DLYT_avg):
        DLYT_avg = 0
    num_DLY = len(DLY)
    DLYP_ttl = DLY['PAX Total'].sum()

    # 顯示結果
    if otp_type == 0:
        print(f"延誤起飛航班數量: {num_DLY} ({round(100*num_DLY/len(df_intrest), 2)}%)")
        print(f"平均每航班延誤 {DLYT_avg} 分鐘")
        print(f"全日期區間總延誤 {DLYT_ttl} 小時")
        print(f"受影響乘客共 {DLYP_ttl} 人次")

    # 回傳準點率
    OTP = round(100*(1 - num_DLY/len(df_intrest)), 2)

#    return OTP
    return OTP, num_DLY, DLYP_ttl


#%% 航班時段準時率分析（全時段）
### 航班時段準時率分析（全時段）

if run_ID[0] == 1:

    # 全日期區間準時率分析
    OT_overall = pd.DataFrame({'Period': ['Overall'], 'OTP': [np.nan], 'TTL FLT': [0], 'DLY FLT': [0], 'DLY PAX': [0]})
    OT_overall.at[0, 'TTL FLT'] = round(len(df_base))
    OT_overall.at[0, 'OTP'], OT_overall.at[0, 'DLY FLT'], OT_overall.at[0, 'DLY PAX'] = otp_calc(df_base, 0)

    # 輸出準時率表單
    if file_ID == 1:
        save_path = os.path.join(outFolder, f"{base}_OTP-Overall_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.csv")
        OT_overall.to_csv(save_path, index=False)
        print(f"\n全時段準時率表單輸出完成！")

else:
     print('未執行。')

#%% 航班時段準時率分析（每時）
### 航班時段準時率分析（每時）

if run_ID[4] == 1:

    # 每小時準時率分析
    unique_hours = df['LTD'].dt.hour.unique().tolist()
    OT_hour = pd.DataFrame({'Period': list(range(24)), 'OTP': np.nan, 'TTL FLT': [0]*24, 'DLY FLT': [0]*24, 'DLY PAX': [0]*24})
    for hour in unique_hours:
        hour_str = str(hour).zfill(2)
        hour_end_str = str(hour+1).zfill(2)
        start_T = datetime.strptime(f'{hour_str}:00', '%H:%M').time()
        end_T = datetime.strptime(f'{hour_str}:59', '%H:%M').time()
        df_base_hour = df_base[(df_base['LTD'].dt.time >= start_T) & (df_base['LTD'].dt.time <= end_T)]
        OT_hour.at[hour, 'TTL FLT'] = round(len(df_base_hour))
        if len(df_base_hour) > 0:
            OT_hour.at[hour, 'OTP'], OT_hour.at[hour, 'DLY FLT'], OT_hour.at[hour, 'DLY PAX'] = otp_calc(df_base_hour, 4)

    # 篩選出有效資料
    valid_OT_hour = OT_hour[pd.notna(OT_hour['OTP'])]

    # 輸出準時率表單
    OT_hour['Period'] = OT_hour['Period'].apply(lambda x: '{:02d}H'.format(x))
    if file_ID == 1:
        save_path = os.path.join(outFolder, f"{base}_OTP-Hour_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.csv")
        OT_hour.to_csv(save_path, index=False)
        print(f"\n每小時準時率表單輸出完成！")

    # 圖面初始化
    plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
    plt.title(f"{base} On-time Performance by Hour\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")

    # 繪製直方圖
    plt.bar(valid_OT_hour['Period'], valid_OT_hour['TTL FLT'], width=0.97, align='edge', label=None)

    # 註記航班數量
    for i, row in valid_OT_hour.iterrows():
        plt.text(row['Period'] + 0.5, row['TTL FLT'] + 0.02*valid_OT_hour['TTL FLT'].max(), f"{row['OTP']:.3g}%", ha='center', va='bottom')

    # 圖面呈現設置
    plt.xlabel('Hour')
    plt.ylabel('Total Flights')
    plt.xlim([-0.1, 24.1])
    plt.ylim([0, 1.1*valid_OT_hour['TTL FLT'].max()])
    plt.xticks(np.arange(0, 25, 1))
    plt.tight_layout()
    if fig_ID == 1:
        plt.savefig(os.path.join(outFolder, f"{base}_OTP-Hour_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.jpg"))
        print(f"\n每小時準時率統計圖輸出完成！")
    plt.show()

else:
     print('未執行。')


#%% 航班時段準時率分析（每日）
### 航班時段準時率分析（每日）

if run_ID[3] == 1:

    # 每日準時率分析
    unique_dates = df['LTD'].dt.date.unique().tolist()
    OT_day = pd.DataFrame({'Period': unique_dates, 'OTP': np.nan, 'TTL FLT': [0]*len(unique_dates), 'DLY FLT': [0]*len(unique_dates), 'DLY PAX': [0]*len(unique_dates)})
    for idx, day in enumerate(unique_dates):
        df_base_day = df_base[df_base['LTD'].dt.date == day]
        OT_day.at[idx, 'TTL FLT'] = round(len(df_base_day))
        if len(df_base_day) > 0:
            OT_day.at[idx, 'OTP'], OT_day.at[idx, 'DLY FLT'], OT_day.at[idx, 'DLY PAX'] = otp_calc(df_base_day, 3)

    # 輸出準時率表單
    if file_ID == 1:
        save_path = os.path.join(outFolder, f"{base}_OTP-Day_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.csv")
        OT_day.to_csv(save_path, index=False)
        print(f"\n每日準時率表單輸出完成！")

    # 篩選出有效資料
    valid_OT_day = OT_day[pd.notna(OT_day['OTP'])]

    # 判斷是否繪圖
    x_itv = math.floor((date2num(valid_OT_day['Period'].max()) - date2num(valid_OT_day['Period'].min()))/(28*1.5))
    x_itv = max(x_itv, 1)

    if x_itv <= 1:

        # 圖面初始化
        plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
        plt.title(f"{base} On-time Performance by Day\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")

        # 繪製直方圖
        plt.bar(valid_OT_day['Period'], valid_OT_day['TTL FLT'], width=0.97, align='edge', label=None)

        # 註記準時率
        for i, row in valid_OT_day.iterrows():
            plt.text(date2num(row['Period']) + 0.5, row['TTL FLT'] - 0.02*valid_OT_day['TTL FLT'].max(), f"{row['OTP']:.3g}%", ha='center', va='top', rotation = 90)

        # 圖面呈現設置
        plt.xlabel('Date')
        plt.ylabel('Total Flights')
        plt.xlim([date2num(valid_OT_day['Period'].min()) - 0.2, date2num(valid_OT_day['Period'].max()) + 1.2])
        plt.ylim([0, 1.05*valid_OT_day['TTL FLT'].max()])
        plt.xticks(np.arange(date2num(valid_OT_day['Period'].min()), date2num(valid_OT_day['Period'].max()) + 1, 7*x_itv))
        plt.tight_layout()
        if fig_ID == 1:
            plt.savefig(os.path.join(outFolder, f"{base}_OTP-Day_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.jpg"))
            print(f"\n每日準時率統計圖輸出完成！")
        plt.show()

    else:
        print('\n資料筆數過多故不繪圖。')

else:
     print('未執行。')


#%% 航班時段準時率分析（每週）
### 航班時段準時率分析（每週）

if run_ID[2] == 1:

    # 每日準時率分析
    unique_week = df['LTD'].dt.to_period('W-SAT').unique()
    unique_week = pd.period_range(start=unique_week.min(), end=unique_week.max(), freq='W-SAT').tolist()
    OT_week = pd.DataFrame({'Period': unique_week, 'OTP': np.nan, 'TTL FLT': [0]*len(unique_week), 'DLY FLT': [0]*len(unique_week), 'DLY PAX': [0]*len(unique_week)})
    for idx, week in enumerate(unique_week):
        df_base_week = df_base[df_base['LTD'].dt.to_period('W-SAT') == week]
        OT_week.at[idx, 'TTL FLT'] = round(len(df_base_week))
        if len(df_base_week) > 0:
            OT_week.at[idx, 'OTP'], OT_week.at[idx, 'DLY FLT'], OT_week.at[idx, 'DLY PAX'] = otp_calc(df_base_week, 2)

    # 篩選出有效資料
    valid_OT_week = OT_week[pd.notna(OT_week['OTP'])]
    valid_OT_week = valid_OT_week.reset_index(drop=True)
    #valid_OT_week_str = valid_OT_week['Period'].dt.weekofyear.astype(str)
    #valid_OT_week_str = valid_OT_week['Period'].dt.strftime('%YW%U')
    valid_OT_week_str = pd.date_range(start=valid_OT_week['Period'].min().start_time, end=valid_OT_week['Period'].max().start_time, freq='W').strftime('%YW%U')
    #OT_week['Period'] = OT_week['Period'].dt.strftime('%YW%U')

    # 輸出準時率表單
    if file_ID == 1:
        save_path = os.path.join(outFolder, f"{base}_OTP-Week_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.csv")
        OT_week.assign(Period=OT_week['Period'].dt.strftime('%YW%U')).to_csv(save_path, index=False)
        print(f"\n每週準時率表單輸出完成！")

    # 判斷是否繪圖
    x_itv = math.floor((date2num(valid_OT_week['Period'].max()) - date2num(valid_OT_week['Period'].min()))/(28*2))
    x_itv = max(x_itv, 1)

    if x_itv <= 2:

        # 圖面初始化
        plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
        plt.title(f"{base} On-time Performance by Week\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")

        # 繪製折線圖
        plt.plot(date2num(OT_week['Period']), np.array(OT_week['OTP']), marker='o', label='On-time Percentage')

        # 註記準時率
        for i, row in valid_OT_week.iterrows():
            plt.text(date2num(valid_OT_week['Period'])[i], row['OTP'] + 3, f"{row['OTP']:.3g}%", ha='center', va='bottom')

        # 註記準時率
        for i, row in valid_OT_week.iterrows():
            plt.text(date2num(valid_OT_week['Period'])[i], row['OTP'] - 3, f"{int(row['TTL FLT'])}", ha='center', va='top')

        # 設定刻度
        tick_pos = np.arange(date2num(valid_OT_week['Period'].min()), date2num(valid_OT_week['Period'].max()) + 1, 7*x_itv)
        #tick_pos = date2num(valid_OT_week['Period'])[::x_itv]

        # 圖面呈現設置
        plt.xlabel('Week')
        plt.ylabel('Total Flights')
        #plt.xlim([date2num(valid_OT_week['Period'].min()) - 0.7, date2num(valid_OT_week['Period'].max()) + 7.7])
        plt.ylim([0, 110])
        plt.xticks(tick_pos, valid_OT_week_str[::x_itv])
        plt.tight_layout()
        if fig_ID == 1:
            plt.savefig(os.path.join(outFolder, f"{base}_OTP-Week_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.jpg"))
            print(f"\n每週準時率統計圖輸出完成！")
        plt.show()

    else:
        print('\n資料筆數過多故不繪圖。')

else:
     print('未執行。')


#%% 航班時段準時率分析（每月）
### 航班時段準時率分析（每月）

if run_ID[1] == 1:

    # 每日準時率分析
    unique_month = df['LTD'].dt.to_period('M').unique()
    unique_month = pd.period_range(start=unique_month.min(), end=unique_month.max(), freq='M').tolist()
    OT_month = pd.DataFrame({'Period': unique_month, 'OTP': np.nan, 'TTL FLT': [0]*len(unique_month), 'DLY FLT': [0]*len(unique_month), 'DLY PAX': [0]*len(unique_month)})
    for idx, month in enumerate(unique_month):
        df_base_month = df_base[df_base['LTD'].dt.to_period('M') == month]
        OT_month.at[idx, 'TTL FLT'] = round(len(df_base_month))
        if len(df_base_month) > 0:
            OT_month.at[idx, 'OTP'], OT_month.at[idx, 'DLY FLT'], OT_month.at[idx, 'DLY PAX'] = otp_calc(df_base_month, 1)

    # 輸出準時率表單
    if file_ID == 1:
        save_path = os.path.join(outFolder, f"{base}_OTP-Month_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.csv")
        OT_month[pd.notna(OT_month['OTP'])].to_csv(save_path, index=False)
        print(f"\n每月準時率表單輸出完成！")

    # 篩選出有效資料
    valid_OT_month = OT_month.copy()
    #valid_OT_month['OTP'] = valid_OT_month['OTP'].fillna(0)
    valid_OT_month_str = valid_OT_month['Period'].astype(str)
    #valid_OT_month_str = pd.date_range(start=valid_OT_month['Period'].min().start_time, end=valid_OT_month['Period'].max().start_time, freq='MS').strftime('%Y-%m')

    # 判斷是否繪圖
    x_itv = math.floor((date2num(valid_OT_month['Period'].max()) - date2num(valid_OT_month['Period'].min()))/(28*1))
    x_itv = max(x_itv, 1)

    if x_itv >= 4:

        # 圖面初始化
        plt.figure(figsize=(1920/set_dpi, 640/set_dpi), dpi=set_dpi)
        plt.title(f"{base} On-time Performance by Month\nFrom {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")

        # 繪製折線圖
        plt.plot(date2num(valid_OT_month['Period']), np.array(valid_OT_month['OTP']), marker='o', label='On-time Percentage')

        # 註記準時率
        for i, row in valid_OT_month.iterrows():
            if row['TTL FLT'] != 0:
                plt.text(date2num(row['Period']), row['OTP'] + 3, f"{row['OTP']:.3g}%", ha='center', va='bottom')

        # 註記航班數量
        for i, row in valid_OT_month.iterrows():
            if row['TTL FLT'] != 0:
                plt.text(date2num(row['Period']), row['OTP'] - 3, f"{int(row['TTL FLT'])}", ha='center', va='top')

        # 設定刻度
        tick_pos = date2num(valid_OT_month['Period'])

        # 圖面呈現設置
        plt.xlabel('Month')
        plt.ylabel('On-time Percentage')
        #plt.xlim([-0.1, len(date2num(valid_OT_month['Period'])) + 0.1])
        plt.ylim([0, 110])
        plt.xticks(tick_pos, valid_OT_month_str)
        plt.tight_layout()
        if fig_ID == 1:
            plt.savefig(os.path.join(outFolder, f"{base}_OTP-Month_{date_start.strftime('%Y%m%d')}-{date_end.strftime('%Y%m%d')}.jpg"))
            print(f"\n每月準時率統計圖輸出完成！")
        plt.show()

    else:
        print('\n資料筆數過少故不繪圖。')

else:
     print('未執行。')


# %%
