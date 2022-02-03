# -*- coding: utf-8-unix -*-
# Python 3.9

# ETA-Analyzer (Process Raw CSV)
# Process csv files from ETA-Browser


# Modules
import sys
import os
import argparse
import datetime


# Configs
AriaLabelCategories = {
    "00:Welcome": "ウェルカムダイアログ",
    "01:Caprese": "カプレーゼ",
    "02:Crostini": "クロスティーニ",
    "03:Panissa": "パニッサ",
    "04:Prosciutto": "プロシュット",
    "05:Arrabbiata": "アラビアータ",
    "06:Genovese": "ジェノベーゼ",
    "07:Risotto": "リゾット",
    "08:Ravioli": "ラビオリ",
    "09:AcquaPazza": "アクアパッツァ",
    "10:Ossobuco": "オッソ・ブーコ",
    "11:Cotoletta": "コトレッタ",
    "12:Piccata": "ピカタ",
    "13:Tiramisu": "ティラミス",
    "14:PannaCotta": "パンナコッタ",
    "15:Semifreddo": "セミフレッド",
    "16:Pizzelle": "ピッツェル",
    "17:Confirm": "注文"
}


# Global Variables
RawCsvColumns = {
    "EventID": 0,
    "AppTime": 0,
    "ServerTime": 0,
    "X": 0,
    "Y": 0,
    "AriaLabel": 0,
    "LFHF": 0
}

# Functions
## Filter rows
## Raw csv -> Filtered csv
def InitializeColumnsToReadFromRawCsv(headerStrings):
    for i, headerString in enumerate(headerStrings):
        if "EventID" in headerString:
            RawCsvColumns["EventID"] = i
        elif "Timestamp(App)" in headerString:
            RawCsvColumns["AppTime"] = i
        elif "Timestamp(Server)" in headerString:
            RawCsvColumns["ServerTime"] = i
        elif "X" in headerString:
            RawCsvColumns["X"] = i
        elif "Y" in headerString:
            RawCsvColumns["Y"] = i
        elif "X" in headerString:
            RawCsvColumns["X"] = i
        elif "LeafSideElem(1): aria-label"in headerString:
            RawCsvColumns["AriaLabel"] = i
        elif "LFHF" in headerString:
            RawCsvColumns["LFHF"] = i

def ProcessRowStringsFromRawCsv(rowStrings, filteredCsv):
    for rowIndex, rowString in enumerate(rowStrings):
        strippedRowString = rowString.strip()
        rowData = strippedRowString.split(",")
        filteredRowString = ""
        for i, columnIndexInOriginal in enumerate(RawCsvColumns.values()):
            if i < len(RawCsvColumns.values()) -1:
                filteredRowString = filteredRowString + rowData[columnIndexInOriginal] + ","
            else:
                filteredRowString = filteredRowString + rowData[columnIndexInOriginal] + "\n"
        filteredCsv.write(filteredRowString)

def FilterRows(rawCsvPath, rawCsvEncoding,
               filteredCsvPath, filteredCsvEncoding):
    with open(rawCsvPath, mode="r", encoding=rawCsvEncoding) as originalCsv:
        with open(filteredCsvPath, mode="w", encoding=filteredCsvEncoding) as filteredCsv:
            # Set colmuns to read from original csv
            originalHeaders = originalCsv.readline().strip()
            originalHeaderStrings = originalHeaders.split(",")
            InitializeColumnsToReadFromRawCsv(originalHeaderStrings)
            # Write headers to filtered csv
            headerString = ""
            for i, col in enumerate(RawCsvColumns.keys()):
                if i < len(RawCsvColumns.keys()) - 1:
                    headerString = headerString + col + ","
                else:
                    headerString = headerString + col + "\n"
            headerString = headerString
            filteredCsv.write(headerString)
            # Process rows
            rowStrings = originalCsv.readlines()
            ProcessRowStringsFromRawCsv(rowStrings, filteredCsv)
    print("Successfully saved: " + filteredCsvPath)

## Categorize filtered csv
## Filtered Csv -> Categorized csv
def CategorizeAriaLabel(AriaLabelCategories, string):
    for category, identifier in AriaLabelCategories.items():
        if identifier in string:
            return category
    if len(string) > 0:
        return str(len(AriaLabelCategories.items())) + ":OtherElements"
    return str(len(AriaLabelCategories.items()) + 1) + ":Unknown"

def ProcessRowStringsFromFilteredCsv(filteredCsvColumns, rowStrings, categorizedCsv, AriaLabelCategories):
    previousFixationStartedTime = 0
    previousFixationStartedCategory = ""
    for rowIndex, rowString in enumerate(rowStrings):
        rowNumber = rowIndex + 1
        strippedRowString = rowString.strip()
        rowData = strippedRowString.split(",")
        eventID = int(rowData[filteredCsvColumns.get("EventID")])
        if eventID == 0:
            # FixationStarted
            leafSideAriaLabel = rowData[filteredCsvColumns.get("AriaLabel")]
            category = CategorizeAriaLabel(AriaLabelCategories, leafSideAriaLabel)
            categorizedCsv.write(str(rowNumber) + ",FixationStarted," + category + "," + strippedRowString + ",\n")
            previousFixationStartedTime = int(rowData[filteredCsvColumns.get("AppTime")])
            previousFixationStartedCategory = category
        elif eventID == 1:
            timeSpan = int(rowData[filteredCsvColumns.get("AppTime")]) - previousFixationStartedTime
            categorizedCsv.write(str(rowNumber) + ",FixationEnded," + previousFixationStartedCategory + "," + strippedRowString + "," + str(timeSpan) + "\n")
        elif eventID == 2:
            categorizedCsv.write(str(rowNumber) + ",LFHFComputed," + "" + "," + strippedRowString + ",\n")
        else:
            categorizedCsv.write(str(rowNumber) + ",Unknown," + "" + "," + strippedRowString + ",\n")

def Categorize(filteredCsvPath, filteredCsvEncoding, filteredCsvColumns,
               categorizedCsvPath, categorizedCsvEncoding,
               AriaLabelCategories):
    with open(filteredCsvPath, mode="r", encoding=filteredCsvEncoding) as filteredCsv:
        with open(categorizedCsvPath, mode="w", encoding=categorizedCsvEncoding) as categorizedCsv:
            headers = filteredCsv.readline().strip()
            categorizedCsv.write("#,Event,Category," + headers + ",TimeSpan\n")
            rowStrings = filteredCsv.readlines()
            ProcessRowStringsFromFilteredCsv(filteredCsvColumns, rowStrings, categorizedCsv, AriaLabelCategories)
    print("Successfully saved: " + categorizedCsvPath)


## Interpolate LF/HF values
## Categorized csv -> Interpolated Csv
def ProcessRowStringsFromCategorizedCsv(categorizedCsvColumns, rowStrings, interpolatedCsv, writeLFHFComputedRows):
    hasLFHFComputedOnce = False
    previousLFHFComputedTime = 0
    previousComputedLFHF = 0.0
    fixationStartedOrEndedTimes = []
    fixationStartedOrEndedRowStrings = []
    for rowIndex, rowString in enumerate(rowStrings):
        strippedRowString = rowString.strip()
        rowData = strippedRowString.split(",")
        event = rowData[categorizedCsvColumns.get("Event")]
        if event == "FixationStarted" or event == "FixationEnded":
            if hasLFHFComputedOnce:
                fixationStartedOrEndedTimes.append(int(rowData[categorizedCsvColumns.get("AppTime")]))
                fixationStartedOrEndedRowStrings.append(strippedRowString)
            else:
                pass
        elif event == "LFHFComputed":
            lfhfComputedTime = int(rowData[categorizedCsvColumns.get("AppTime")])
            lfhf = float(rowData[categorizedCsvColumns.get("LFHF")])
            if hasLFHFComputedOnce:
                lfhfComputedTimeDelta = lfhfComputedTime - previousLFHFComputedTime
                lfhfDelta = lfhf - previousComputedLFHF
                for fixRowStr in fixationStartedOrEndedRowStrings:
                    fixRowData = fixRowStr.split(",")
                    fixRowTime = int(fixRowData[categorizedCsvColumns.get("AppTime")])
                    elapsedTime = fixRowTime - previousLFHFComputedTime
                    estimatedLFHF = previousComputedLFHF + (elapsedTime * lfhfDelta / lfhfComputedTimeDelta)
                    interpolatedCsv.write(fixRowStr + "," + f"{estimatedLFHF:.3f}" + "\n")
                if writeLFHFComputedRows:
                    interpolatedCsv.write(strippedRowString + "," + f"{lfhf:.3f}" + "\n")
            else:
                hasLFHFComputedOnce = True
                if writeLFHFComputedRows:
                    interpolatedCsv.write(strippedRowString + "," + f"{lfhf:.3f}" + "\n")
            previousLFHFComputedTime = lfhfComputedTime
            previousComputedLFHF = lfhf
            fixationStartedOrEndedTimes = []
            fixationStartedOrEndedRowStrings = []
        else:
            pass

def InterpolateLFHF(categorizedCsvPath, categorizedCsvEncoding, categorizedCsvColumns,
                    interpolatedCsvPath, interpolatedCsvEncoding,
                    writeLFHFComputedRows):
    with open(categorizedCsvPath, mode="r", encoding=categorizedCsvEncoding) as categorizedCsv:
        with open(interpolatedCsvPath, mode="w", encoding=interpolatedCsvEncoding) as interpolatedCsv:
            headers = categorizedCsv.readline().strip()
            interpolatedCsv.write(headers + ",LFHF(Interpolated)\n")
            rowStrings = categorizedCsv.readlines()
            ProcessRowStringsFromCategorizedCsv(categorizedCsvColumns, rowStrings, interpolatedCsv, writeLFHFComputedRows)
    print("Successfully saved: " + interpolatedCsvPath)


## Process interpolated LF/HF values
## Interpolated csv -> Processed csv
def ProcessRowStringsFromInterpolatedCsv(interpolatedCsvColumns, rowStrings, processedCsv):
    hasElementLFHFComputedOnce = False
    fixationStartedLFHF = 0.0
    previousElementLFHF = 0.0
    for rowIndex, rowString in enumerate(rowStrings):
        strippedRowString = rowString.strip()
        rowData = strippedRowString.split(",")
        event = rowData[interpolatedCsvColumns.get("Event")]
        if event == "FixationStarted":
            fixationStartedLFHF = float(rowData[interpolatedCsvColumns.get("InterpolatedLFHF")])
            processedCsv.write(strippedRowString + ",,\n")
        elif event == "FixationEnded":
            fixationEndedLFHF = float(rowData[interpolatedCsvColumns.get("InterpolatedLFHF")])
            elementLFHF = (fixationStartedLFHF + fixationEndedLFHF) / 2.0
            if hasElementLFHFComputedOnce:
                elementLFHFDelta = elementLFHF - previousElementLFHF
                processedCsv.write(strippedRowString + "," + f"{elementLFHF:.3f}" + "," + f"{elementLFHFDelta:.3f}" + "\n")
            else:
                processedCsv.write(strippedRowString + "," + f"{elementLFHF:.3f}" + ",\n")
                hasElementLFHFComputedOnce = True
            previousElementLFHF = elementLFHF
        else:
            processedCsv.write(strippedRowString + ",,\n")
            pass

def ProcessLFHF(interpolatedCsvPath, interpolatedCsvEncoding, interpolatedCsvColumns,
                processedCsvPath, processedCsvEncoding):
    with open(interpolatedCsvPath, mode="r", encoding=interpolatedCsvEncoding) as interpolatedCsv:
        with open(processedCsvPath, mode="w", encoding=processedCsvEncoding) as processedCsv:
            headers = interpolatedCsv.readline().strip()
            processedCsv.write(headers + ",LFHF(Element),LFHF(Element:Delta)\n")
            rowStrings = interpolatedCsv.readlines()
            ProcessRowStringsFromInterpolatedCsv(interpolatedCsvColumns, rowStrings, processedCsv)
    print("Successfully saved: " + processedCsvPath)


# Main Function
def Main(identifierString, rawCsvPath, rawCsvEncoding, outputCsvEncoding, outputDir, writeLFHFComputedRowsWhenInterpolateLFHF):
    filteredCsvPath = outputDir + identifierString + "/" + identifierString + "_step_1_filtered_rows.csv"
    filteredCsvEncoding = outputCsvEncoding
    filteredCsvColumns = {
        "EventID": 0,
        "AppTime": 1,
        "ServerTime": 2,
        "X": 3,
        "Y": 4,
        "AriaLabel": 5,
        "LFHF": 6
    }
    categorizedCsvPath = outputDir + identifierString + "/" + identifierString + "_step_2_categorized.csv"
    categorizedCsvEncoding = outputCsvEncoding
    categorizedCsvColumns = {
        "Number": 0,
        "Event": 1,
        "Category": 2,
        "EventID": 3,
        "AppTime": 4,
        "ServerTime": 5,
        "X": 6,
        "Y": 7,
        "AriaLabel": 8,
        "LFHF": 9,
        "TimeSpan": 10
    }
    interpolatedCsvPath = outputDir + identifierString + "/" + identifierString + "_step_3_interpolated_lfhf.csv"
    interpolatedCsvEncoding = outputCsvEncoding
    interpolatedCsvColumns = {
        "Number": 0,
        "Event": 1,
        "Category": 2,
        "EventID": 3,
        "AppTime": 4,
        "ServerTime": 5,
        "X": 6,
        "Y": 7,
        "AriaLabel": 8,
        "LFHF": 9,
        "TimeSpan": 10,
        "InterpolatedLFHF": 11
    }
    processedCsvPath = outputDir + identifierString + "/" + identifierString + "_step_4_processed_lfhf.csv"
    processedCsvEncoding = outputCsvEncoding

    FilterRows(rawCsvPath, rawCsvEncoding,
               filteredCsvPath, filteredCsvEncoding)
    Categorize(filteredCsvPath, filteredCsvEncoding, filteredCsvColumns,
               categorizedCsvPath, categorizedCsvEncoding,
               AriaLabelCategories)
    InterpolateLFHF(categorizedCsvPath, categorizedCsvEncoding, categorizedCsvColumns,
                    interpolatedCsvPath, interpolatedCsvEncoding,
                    writeLFHFComputedRowsWhenInterpolateLFHF)
    ProcessLFHF(interpolatedCsvPath, interpolatedCsvEncoding, interpolatedCsvColumns,
                processedCsvPath, processedCsvEncoding)


if __name__ == "__main__":
    currentDatetime = datetime.datetime.now()
    currentDatetimeString = currentDatetime.strftime("%Y%m%d%H%M%S")

    parser = argparse.ArgumentParser(description="ETA-Analyzer: CSV Processor",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source", type=str,
                        help="Raw csv file created via ETA-Browser")
    parser.add_argument("-i", "--identifier", type=str, default=currentDatetimeString,
                        help="Unique identifier for output csv files \n (default: YYYYMMDDhhmmss)")
    parser.add_argument("-e", "--input-encoding", type=str, choices=["utf_8", "shift_jis"], default="shift_jis",
                        help="Encoding of the input csv file \n (default: shift_jis)")
    parser.add_argument("-d", "--output-dir", type=str, default="csvout",
                        help="The destination directory for output csv files \n (default: csvout)")
    parser.add_argument("-E", "--output-encoding", type=str, choices=["utf_8", "shift_jis"], default="shift_jis",
                        help="Encoding of output csv files \n (default: shift_jis)")
    parser.add_argument("--write-lfhf-computed", action="store_true",
                        help="Write \"LFHFComputed\" rows on \nLF/HF interpolation")
    args = parser.parse_args()

    # Get output directory path
    formattedOutputDir = args.output_dir
    if args.output_dir[-1] != "/":
        formattedOutputDir = args.output_dir + "/"
    os.makedirs(formattedOutputDir + args.identifier, exist_ok=True)

    Main(args.identifier, args.source, args.input_encoding, args.output_encoding, formattedOutputDir, args.write_lfhf_computed)
