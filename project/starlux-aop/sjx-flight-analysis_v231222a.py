#%% 程式變數及套件初始化
### 程式變數及套件初始化

import os, time
import tkinter as tk
from tkinter import filedialog
import pandas as pd

# 定義本程式起始路徑，若已執行過會繼承上次執行的路徑
if 'homePath' not in locals():
		homePath = os.path.dirname(os.path.abspath(__file__))

print("初始化完成！")


#%% 以彈出式視窗選取欲分析之航班總表
### 以彈出式視窗選取欲分析之航班總表

def open_file_dialog():
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xls;*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")],
        title="Choose a file"
    )
    
    if file_path:
        # Read the selected file into a DataFrame
        global source_df
        if file_path.endswith('.csv'):
            source_df = pd.read_csv(file_path)
        else:
            source_df = pd.read_excel(file_path)

        print("已成功讀取航班總表！")
        #print(source_df.head())

        # Close the main window
        root.destroy()

# Create the main window
root = tk.Tk()
root.withdraw()  # Hide the main window

# Open file dialog when the script is run
open_file_dialog()

# Main loop
root.mainloop()


#%% 計算獨立航班及航點數量
### 計算獨立航班及航點數量

# 扣除重複航班（Irreg State 欄為 RTR 的列）
source_df = source_df[source_df['Irreg State'] != 'RTR']

# 計算總航班數量
total_flights = len(source_df)

# 計算 TPE 離場航班數量
dep_from_tpe = len(source_df[source_df['Dep'] == 'TPE'])

# 計算 TPE 進場航班數量
arr_to_tpe = len(source_df[source_df['Arr'] == 'TPE'])

# 所有航班關聯到的機場數量
all_airports = set(source_df['Dep'].unique()).union(source_df['Arr'].unique())
num_airports = len(all_airports)

# 顯示結果
print(f"總航班數量: {total_flights}")
print(f"TPE 離場航班數量: {dep_from_tpe}")
print(f"TPE 進場航班數量: {arr_to_tpe}")
print(f"相關航點數量: {num_airports}")


# %%
