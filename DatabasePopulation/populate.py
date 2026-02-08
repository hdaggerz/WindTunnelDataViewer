import numpy as np
import pandas as pd
from pathlib import Path
import re
import sqlite3
con = sqlite3.connect("WindTunnel.db")

class GroupSet:

    def __init__(self, fullFile, sheetName):
        self.fullFile = fullFile
        self.fileName = fullFile.stem
        self.sheetName = sheetName
        self.BGurney = False
        if "No" in sheetName:
            sheetName = sheetName.split("No")[0].strip()
        elif "GF" in sheetName:
            self.BGurney = True
        aFWString = re.findall(r"FW\d\d", sheetName.replace(" ", ""))
        aRWString = re.findall(r"RW\d\d", sheetName.replace(" ", ""))
        self.aRW = float(aRWString[0].split('W')[1]) if aRWString else 0.0
        self.aFW = float(aFWString[0].split('W')[1]) if aFWString else 0.0

        self._readName()
        self._readAmbients()
        self._readWheelDrag()   
        self._readTestData()

        # collate meta data
        self._collateMetaData()
        self._writeMetaData()
        # add run id
        self.testData['RunId'] = self.run_id
        self._writeTestData()


    def _readName(self):
        NRun_df = pd.read_excel(str(self.fullFile), sheet_name=self.sheetName, usecols="J", skiprows=0, nrows=1)
        NRun_df.reset_index(drop=True, inplace=True)
        self.NRun = NRun_df.iloc[0, 0] if not NRun_df.empty else None

    def _readAmbients(self):
        ambient_df = pd.read_excel(str(self.fullFile), sheet_name=self.sheetName, usecols="L:P", skiprows=1, nrows=5)
        ambient_df['Ambient Parameters'] = ambient_df['Ambient Parameters'].str.split("(").str[0].str.strip()  # Remove leading/trailing whitespace
        cols_to_drop = ambient_df.columns[1:4]  
        ambient_df.drop(columns=cols_to_drop, inplace=True)
        ambient_df = ambient_df.set_index("Ambient Parameters").T  # transpose
        ambient_df = ambient_df.apply(pd.to_numeric, errors="coerce")
        ambient_df.reset_index(drop=True, inplace=True)
        self.ambientData = ambient_df

    def _readWheelDrag(self):
        wheel_df = pd.read_excel(str(self.fullFile), sheet_name=self.sheetName, usecols="S:Y", skiprows=1, nrows=4)
        cols_to_drop = wheel_df.columns[1:6] 
        wheel_df.drop(columns=cols_to_drop, inplace=True)
        wheel_df = wheel_df.set_index("Wheel Drag measurements").T  # transpose
        wheel_df = wheel_df.apply(pd.to_numeric, errors="coerce")
        wheel_df.reset_index(drop=True, inplace=True)
        wheel_df.columns = wheel_df.columns + "Drag"
        self.wheelDragData = wheel_df

    def _readTestData(self):
        raw_df = pd.read_excel(str(self.fullFile), sheet_name=self.sheetName, usecols="B:AF", skiprows=12)
        raw_df.columns.values[0] = "FrontRideHeight"
        raw_df.columns.values[1] = "RearRideHeight"
        raw_df = raw_df.loc[:, ~raw_df.columns.str.contains("Unnamed")]
        raw_df = raw_df.loc[2:, :]
        idxMissing = raw_df['FrontRideHeight'].isna()
        firstMissingIndex = idxMissing.idxmax() if idxMissing.any() else len(raw_df)
        raw_df = raw_df.loc[:firstMissingIndex-1, :].reset_index(drop=True)
        raw_df = raw_df.apply(pd.to_numeric, errors="coerce")
        raw_df = raw_df.round(3)
        raw_df.reset_index(drop=True, inplace=True)
        raw_df.columns = raw_df.columns.str.replace(" ", "")
        raw_df.rename(columns={"L/D": "L_D"}, inplace=True)
        raw_df['FrontRideHeight'] = raw_df['FrontRideHeight'].round(1)
        raw_df['RearRideHeight'] = raw_df['RearRideHeight'].round(1)
        self.testData = raw_df

    def _collateMetaData(self):
        runMeta = pd.concat([self.ambientData, self.wheelDragData], axis=1)
        runMeta['BGurney'] = self.BGurney
        runMeta['aRW'] = round(self.aRW, 1)
        runMeta['aFW'] = round(self.aFW, 1)
        runMeta['NRun'] = self.NRun
        runMeta['FileName'] = str(self.fileName)
        runMeta['SheetName'] = self.sheetName
        runMeta.columns = runMeta.columns.str.replace(" ", "")
        self.meta = runMeta

    def _writeMetaData(self):
        self.meta.to_sql(
            "Run",
            con,
            if_exists="append",
            index=False)
        cur = con.cursor()
        self.run_id = cur.execute("SELECT last_insert_rowid()").fetchone()[0]

    def _writeTestData(self):
        self.testData.to_sql(
            "Test",
            con,
            if_exists="append",
            index=False)



ROOT = Path(__file__).resolve().parents[1]  # repo root
DATA_DIR = ROOT / "RawData"
files = list(Path(DATA_DIR).glob("*.xlsx"))
for iFile in range(0, len(files)):
    sheets = pd.ExcelFile(files[iFile]).sheet_names
    for sheet in sheets:
        sheetCleaned = sheet.replace(" ", "")
        sheetCleaned = re.sub(r"RW\d\d", "", sheetCleaned)
        sheetCleaned = re.sub(r"FW\d\d", "", sheetCleaned)
        sheetCleaned = re.sub(r"GF", "", sheetCleaned)
        sheetCleaned = re.sub(r"No", "", sheetCleaned)
        BDirty = len(sheetCleaned) > 1
        if "Repeat" not in sheet and not BDirty:
            print(f"Processing file {files[iFile].name}, sheet {sheet}")
            GroupSet(files[iFile], sheet)


print("Done")