import pandas as pd
import os
from typing import List

def load_single_excel(filepath: str, sheet_name: str = "สมุดโทรเยี่ยมผู้ป่วย") -> pd.DataFrame:
    """
    อ่านไฟล์ Excel หนึ่งไฟล์ แล้วดึงเฉพาะส่วนข้อมูลตามหัวตารางจริง
    """
    df_raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

    # หาแถวที่มีคำว่า "ลำดับ" เพื่อระบุ header
    header_row = df_raw[df_raw[0] == 'ลำดับ'].iloc[0].tolist()
    end_idx = header_row.index('หมายเหตุ')
    col = header_row[:end_idx + 1]

    # เลือกเฉพาะแถวที่เป็นข้อมูล (ลำดับเป็นตัวเลข)
    data = df_raw[df_raw[0].astype(str).str.isnumeric()]
    data = data.iloc[:, :end_idx + 1].values

    # สร้าง DataFrame
    df = pd.DataFrame(data, columns=col)

    # เพิ่มชื่อไฟล์ (กันงงเวลา merge)
    df["source_file"] = os.path.basename(filepath)

    return df


def load_folder_excels(folder_path: str, sheet_name: str = "สมุดโทรเยี่ยมผู้ป่วย") -> pd.DataFrame:
    """
    อ่านทุกไฟล์ Excel ในโฟลเดอร์ แล้วรวมเป็น DataFrame เดียว
    """
    all_files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]

    df_list: List[pd.DataFrame] = []

    for file in all_files:
        full_path = os.path.join(folder_path, file)
        try:
            df = load_single_excel(full_path, sheet_name)
            df_list.append(df)
            print(f"โหลดไฟล์สำเร็จ: {file}")
        except Exception as e:
            print(f"โหลดไฟล์ล้มเหลว: {file} | Error: {e}")

    if len(df_list) == 0:
        raise ValueError("ไม่พบไฟล์ Excel ที่โหลดสำเร็จเลยในโฟลเดอร์")

    # รวมทั้งหมด
    df_all = pd.concat(df_list, ignore_index=True)
    return df_all


if __name__ == "__main__":
    folder = "data/"  # โฟลเดอร์ที่เก็บไฟล์
    df_all = load_folder_excels(folder, )

    print("รวมไฟล์เสร็จแล้ว จำนวนทั้งหมด:", len(df_all))
    print(df_all.head())
