# -*- coding: utf-8-unix -*-
# Python 3.9

# A Verifier for ETA-Browser and ETA-Analyzer


# Modules
## Built-in
import sys
import os
import argparse
import datetime
## Additional
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

# Configs

# Global Variables
Colormaps = ["Dark2", "tab10"]

# Functions
def CreateDataFrameFrom(csvPath, csvEncoding):
    dataFrame = pd.read_csv(csvPath, encoding=csvEncoding)
    return dataFrame

def CreateDataFrameWithoutHeadersFrom(csvPath, csvEncoding):
    dataFrame = pd.read_csv(csvPath, encoding=csvEncoding, header=None)
    return dataFrame

def SetPlotMarginFor4PlotsWithXCategories():
    plt.rcParams["figure.subplot.left"] = 0.08
    plt.rcParams["figure.subplot.right"] = 0.95
    plt.rcParams["figure.subplot.bottom"] = 0.15
    plt.rcParams["figure.subplot.top"] = 0.95
    plt.rcParams["figure.subplot.wspace"] = 0.15
    plt.rcParams["figure.subplot.hspace"] = 0.6

def SetPlotMarginFor2PlotsWithXCategories():
    plt.rcParams["figure.subplot.left"] = 0.08
    plt.rcParams["figure.subplot.right"] = 0.95
    plt.rcParams["figure.subplot.bottom"] = 0.15
    plt.rcParams["figure.subplot.top"] = 0.95
    plt.rcParams["figure.subplot.wspace"] = 0.15
    plt.rcParams["figure.subplot.hspace"] = plt.rcParamsDefault["figure.subplot.hspace"]

def SetPlotMarginFor1PlotWithXTime():
    plt.rcParams["figure.subplot.left"] = 0.10
    plt.rcParams["figure.subplot.right"] = 0.95
    plt.rcParams["figure.subplot.bottom"] = plt.rcParamsDefault["figure.subplot.bottom"]
    plt.rcParams["figure.subplot.top"] = 0.93
    plt.rcParams["figure.subplot.wspace"] = plt.rcParamsDefault["figure.subplot.wspace"]
    plt.rcParams["figure.subplot.hspace"] = plt.rcParamsDefault["figure.subplot.hspace"]

def SetPlotMarginFor1PlotWithXTimeYCategories():
    plt.rcParams["figure.subplot.left"] = 0.23
    plt.rcParams["figure.subplot.right"] = 0.90
    plt.rcParams["figure.subplot.bottom"] = plt.rcParamsDefault["figure.subplot.bottom"]
    plt.rcParams["figure.subplot.top"] = 0.93
    plt.rcParams["figure.subplot.wspace"] = plt.rcParamsDefault["figure.subplot.wspace"]
    plt.rcParams["figure.subplot.hspace"] = plt.rcParamsDefault["figure.subplot.hspace"]


def MinMaxNormalizeColumns(df, columnNames):
    result = df.copy()
    for columnName in columnNames:
        maxValue = df[columnName].max()
        minValue = df[columnName].min()
        result[columnName] = (df[columnName] - minValue) / (maxValue - minValue)
    return result

def ProcessFixationTimeAndScore(identifier, df, dfInt, figurePath):
    #print(df.columns)
    dfPivotSum = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.sum).reset_index()
    dfPivotSum = dfPivotSum.rename(columns={"TimeSpan": "Total fixation time"})
    dfSumFiltered = dfPivotSum.drop([0, 17, 18, 19]).reset_index()

    dfPivotMean = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.mean).reset_index()
    dfPivotMean = dfPivotMean.rename(columns={"TimeSpan": "Mean fixation time"})
    dfMeanFiltered = dfPivotMean.drop([0, 17, 18, 19]).reset_index()

    dfSumFiltered.insert(len(dfSumFiltered.columns), "Score", dfInt[1].astype("float"))
    dfMeanFiltered.insert(len(dfMeanFiltered.columns), "Score", dfInt[1].astype("float"))

    # print(dfSumFiltered)
    # print(dfMeanFiltered)

    dfNormSumScore = MinMaxNormalizeColumns(dfSumFiltered, ["Total fixation time", "Score"]).set_index("Category")
    dfNormMeanScore = MinMaxNormalizeColumns(dfMeanFiltered, ["Mean fixation time", "Score"]).set_index("Category")

    # print(dfNormSumScore)
    # print(dfNormMeanScore)

    SetPlotMarginFor4PlotsWithXCategories()
    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0] * 2, currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=tuple(multiFigSize))
    dfNormSumScore["Total fixation time"].plot(ax=axes[0, 0],
                                               kind="bar", title="Normalized total fixation time (" + identifier + ")",
                                               xlabel="Category of elements in HTML", ylabel="Normalized total fixation time",
                                               legend=None, grid=True, colormap=Colormaps[0])
    dfNormSumScore["Score"].plot(ax=axes[1, 0],
                                 kind="bar", title="Normalized scores (" + identifier + ")",
                                 xlabel="Category of elements in HTML", ylabel="Normalized user scores from the interview",
                                 legend=None, grid=True, colormap=Colormaps[0])
    dfNormMeanScore["Mean fixation time"].plot(ax=axes[0, 1],
                                               kind="bar", title="Normalized mean fixation time (" + identifier + ")",
                                               xlabel="Category of elements in HTML", ylabel="Normalized mean fixation time",
                                               legend=None, grid=True, colormap=Colormaps[1])
    dfNormMeanScore["Score"].plot(ax=axes[1, 1],
                                  kind="bar", title="Normalized scores (" + identifier + ")",
                                  xlabel="Category of elements in HTML", ylabel="Normalized user scores from the interview",
                                  legend=None, grid=True, colormap=Colormaps[1])
    plt.savefig(figurePath)
    plt.close("all")
    print("Successfully saved: " + figurePath)

def ProcessLFHFAndScore(identifier, df, dfInt, figurePath):
    #print(df.columns)
    dfPivotDeltaSum = pd.pivot_table(df, index="Category", values="LFHF(Element:Delta)", margins=False, aggfunc=np.sum).reset_index()
    dfPivotDeltaSum = dfPivotDeltaSum.rename(columns={"LFHF(Element:Delta)": "Total LF/HF Delta"})
    dfDeltaSumFiltered = dfPivotDeltaSum.drop([0, 17, 18, 19]).reset_index()

    dfPivotMean = pd.pivot_table(df, index="Category", values="LFHF(Element)", margins=False, aggfunc=np.mean).reset_index()
    dfPivotMean = dfPivotMean.rename(columns={"LFHF(Element)": "Mean LF/HF"})
    dfMeanFiltered = dfPivotMean.drop([0, 17, 18, 19]).reset_index()

    dfDeltaSumFiltered.insert(len(dfDeltaSumFiltered.columns), "Score", dfInt[1].astype("float"))
    dfMeanFiltered.insert(len(dfMeanFiltered.columns), "Score", dfInt[1].astype("float"))

    # print(dfDeltaSumFiltered)
    # print(dfMeanFiltered)

    dfNormDeltaSumScore = MinMaxNormalizeColumns(dfDeltaSumFiltered, ["Total LF/HF Delta", "Score"]).set_index("Category")
    dfNormMeanScore = MinMaxNormalizeColumns(dfMeanFiltered, ["Mean LF/HF", "Score"]).set_index("Category")

    # print(dfNormDeltaSumScore)
    # print(dfNormMeanScore)

    SetPlotMarginFor4PlotsWithXCategories()
    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0] * 2, currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=tuple(multiFigSize))
    dfNormDeltaSumScore["Total LF/HF Delta"].plot(ax=axes[0, 0],
                                                                kind="bar", title="Normalized total LF/HF delta (" + identifier + ")",
                                                                xlabel="Category of elements in HTML", ylabel="Normalized total LF/HF delta",
                                                                legend=None, grid=True, colormap=Colormaps[0])
    dfNormDeltaSumScore["Score"].plot(ax=axes[1, 0],
                                                    kind="bar", title="Normalized scores (" + identifier + ")",
                                                    xlabel="Category of elements in HTML", ylabel="Normalized user scores from the interview",
                                                    legend=None, grid=True, colormap=Colormaps[0])
    dfNormMeanScore["Mean LF/HF"].plot(ax=axes[0, 1],
                                                     kind="bar", title="Normalized mean LF/HF (" + identifier + ")",
                                                     xlabel="Category of elements in HTML", ylabel="Normalized mean LF/HF",
                                                     legend=None, grid=True, colormap=Colormaps[1])
    dfNormMeanScore["Score"].plot(ax=axes[1, 1],
                                                kind="bar", title="Normalized scores (" + identifier + ")",
                                                xlabel="Category of elements in HTML", ylabel="Normalized user scores from the interview",
                                                legend=None, grid=True, colormap=Colormaps[1])
    plt.savefig(figurePath)
    plt.close("all")
    print("Successfully saved: " + figurePath)


# Main Function
def Main(identifierString, processedCsvPath, interviewCsvPath, inputCsvEncoding, outputDir, outputFormat):
    # Create dataframe
    df = CreateDataFrameFrom(processedCsvPath, inputCsvEncoding)
    dfFiltered = df.drop(["EventID", "ServerTime", "LFHF", "LFHF(Interpolated)"], axis=1)

    dfInt = CreateDataFrameWithoutHeadersFrom(interviewCsvPath, inputCsvEncoding)

    # Fixation time and score
    fixationTimeAndScoreFigurePath = outputDir + identifierString + "/" + identifierString + "_fixation_time_and_score." + outputFormat
    ProcessFixationTimeAndScore(identifierString, dfFiltered, dfInt, fixationTimeAndScoreFigurePath)

    # LF/HF and score
    lfhfAndScoreFigurePath = outputDir + identifierString + "/" + identifierString + "_lfhf_and_score." + outputFormat
    ProcessLFHFAndScore(identifierString, dfFiltered, dfInt, lfhfAndScoreFigurePath)


if __name__ == "__main__":
    currentDatetime = datetime.datetime.now()
    currentDatetimeString = currentDatetime.strftime("%Y%m%d%H%M%S")

    parser = argparse.ArgumentParser(description="Verifier for ETA-Browser and ETA-Analyzer",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source1", type=str,
                        help="Processed csv file created via eta_csv_processor.py")
    parser.add_argument("source2", type=str,
                        help="Processed csv file created from interview results")
    parser.add_argument("-i", "--identifier", type=str, default=currentDatetimeString,
                        help="Unique identifier for output files \n (default: YYYYMMDDhhmmss)")
    parser.add_argument("-e", "--input-encoding", type=str, choices=["utf_8", "shift_jis"], default="shift_jis",
                        help="Encoding of the input csv file \n (default: shift_jis)")
    parser.add_argument("-d", "--output-dir", type=str, default="verifyout",
                        help="The destination directory for output image files \n (default: verifyout)")
    parser.add_argument("-F", "--output-format", type=str, choices=["png", "pdf", "svg"], default="png",
                        help="File format of output image files \n (default: png)")
    parser.add_argument("-S", "--output-size", type=float, nargs=2, default=[8, 6],
                        help="Output size for figures in images \n (default: 8 6)")
    parser.add_argument("-D", "--output-dpi", type=float, default=300.0,
                        help="Output DPI \n (default: 300.0)")
    parser.add_argument("-G", "--output-grid-disable", action="store_true",
                        help="Disable grid on figures on output images")
    args = parser.parse_args()

    # Get output directory path
    formattedOutputDir = args.output_dir
    if args.output_dir[-1] != "/":
        formattedOutputDir = args.output_dir + "/"
    os.makedirs(formattedOutputDir + args.identifier, exist_ok=True)

    # Set pyplot configs
    plt.rcParams["figure.figsize"] = args.output_size
    plt.rcParams["figure.dpi"] = args.output_dpi
    if args.output_grid_disable:
        plt.rcParams["grid.alpha"] = 0.0
    else:
        plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["grid.color"] = "gray"
    plt.rcParams["grid.linestyle"] = "dotted"

    Main(args.identifier, args.source1, args.source2, args.input_encoding, formattedOutputDir, args.output_format)
