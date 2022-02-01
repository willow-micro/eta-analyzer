# -*- coding: utf-8-unix -*-
# Python 3.9

# ETA-Analyzer (Plot Processed CSV)
# Plot processed csv files via eta_csv_processor.py


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

# Configs

# Global Variables
Colormaps = ["Pastel1", "Pastel2"]

# Functions
def CreateDataFrameFrom(csvPath, csvEncoding):
    dataFrame = pd.read_csv(csvPath, encoding=csvEncoding)
    return dataFrame

def SetSubPlotMarginFor4PlotsWithCategories():
    plt.rcParams["figure.subplot.left"] = 0.08
    plt.rcParams["figure.subplot.right"] = 0.95
    plt.rcParams["figure.subplot.bottom"] = 0.15
    plt.rcParams["figure.subplot.top"] = 0.95
    plt.rcParams["figure.subplot.wspace"] = 0.15
    plt.rcParams["figure.subplot.hspace"] = 0.6

def SetSubPlotMarginFor2PlotsWithTime():
    plt.rcParams["figure.subplot.left"] = 0.12
    plt.rcParams["figure.subplot.right"] = 0.95
    plt.rcParams["figure.subplot.bottom"] = 0.1
    plt.rcParams["figure.subplot.top"] = 0.9
    plt.rcParams["figure.subplot.wspace"] = 0.0
    plt.rcParams["figure.subplot.hspace"] = 0.3

def ProcessFixationTime(identifier, df, figurePath):
    #print(df.columns)
    dfPivotSum = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.sum)
    dfPivotSum = dfPivotSum.rename(columns={"TimeSpan": "Total fixation time"})
    dfPivotSumSorted = dfPivotSum.sort_values("Total fixation time", ascending=False)

    dfPivotMean = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.mean)
    dfPivotMean = dfPivotMean.rename(columns={"TimeSpan": "Mean fixation time"})
    dfPivotMeanSorted = dfPivotMean.sort_values("Mean fixation time", ascending=False)

    SetSubPlotMarginFor4PlotsWithCategories()
    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0] * 2, currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=tuple(multiFigSize))
    dfPivotSum.plot(ax=axes[0, 0],
                    kind="bar", title="Total fixation time by categories (" + identifier + ")", legend=None, grid=True,
                    xlabel="Category of html elements", ylabel="Total fixation time [ms]", colormap=Colormaps[0])
    dfPivotSumSorted.plot(ax=axes[1, 0],
                          kind="bar", title="Sorted total fixation time by categories (" + identifier + ")", legend=None, grid=True,
                          xlabel="Category of html elements", ylabel="Total fixation time [ms]", colormap=Colormaps[0])
    dfPivotMean.plot(ax=axes[0, 1],
                     kind="bar", title="Mean fixation time by categories (" + identifier + ")", legend=None, grid=True,
                     xlabel="Category of html elements", ylabel="Mean fixation time [ms]", colormap=Colormaps[1])
    dfPivotMeanSorted.plot(ax=axes[1, 1],
                           kind="bar", title="Sorted mean fixation time by categories (" + identifier + ")", legend=None, grid=True,
                           xlabel="Category of html elements", ylabel="Mean fixation time [ms]", colormap=Colormaps[1])
    plt.savefig(figurePath)
    plt.close("all")
    print("Saved " + figurePath)

def ProcessLFHFSummary(identifier, df, figurePath):
    #print(df.columns)
    dfPivotDeltaSum = pd.pivot_table(df, index="Category", values="LFHF(Element:Delta)", margins=False, aggfunc=np.sum)
    dfPivotDeltaSum = dfPivotDeltaSum.rename(columns={"LFHF(Element:Delta)": "Total LF/HF Delta"})
    dfPivotDeltaSumSorted = dfPivotDeltaSum.sort_values("Total LF/HF Delta", ascending=False)

    dfPivotMean = pd.pivot_table(df, index="Category", values="LFHF(Element)", margins=False, aggfunc=np.mean)
    dfPivotMean = dfPivotMean.rename(columns={"LFHF(Element)": "Mean LF/HF"})
    dfPivotMeanSorted = dfPivotMean.sort_values("Mean LF/HF", ascending=False)

    SetSubPlotMarginFor4PlotsWithCategories()
    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0] * 2, currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=tuple(multiFigSize))
    dfPivotDeltaSum.plot(ax=axes[0, 0],
                         kind="bar", title="Total LF/HF delta by categories (" + identifier + ")", legend=None, grid=True,
                         xlabel="Category of html elements", ylabel="Total LF/HF delta", colormap=Colormaps[0])
    dfPivotDeltaSumSorted.plot(ax=axes[1, 0],
                               kind="bar", title="Sorted total LF/HF delta by categories (" + identifier + ")", legend=None, grid=True,
                               xlabel="Category of html elements", ylabel="Total LF/HF delta", colormap=Colormaps[0])
    dfPivotMean.plot(ax=axes[0, 1],
                     kind="bar", title="Mean LF/HF by categories (" + identifier + ")", legend=None, grid=True,
                     xlabel="Category of html elements", ylabel="Mean LF/HF", colormap=Colormaps[1])
    dfPivotMeanSorted.plot(ax=axes[1, 1],
                           kind="bar", title="Sorted mean LF/HF by categories (" + identifier + ")", legend=None, grid=True,
                           xlabel="Category of html elements", ylabel="Mean LF/HF", colormap=Colormaps[1])
    plt.savefig(figurePath)
    plt.close("all")
    print("Saved " + figurePath)

def ProcessLFHFTimeline(identifier, df, figurePath):
    # print(df.columns)
    # > ['#', 'Event', 'Category', 'AppTime', 'X', 'Y', 'AriaLabel', 'TimeSpan', 'LFHF(Element)', 'LFHF(Element:Delta)']
    convertMillSecToSec = lambda t: round(t / 1000.0)
    dfLFHFElement = df.drop(['#', 'Event', 'Category', 'X', 'Y', 'AriaLabel', 'TimeSpan', 'LFHF(Element:Delta)'], axis=1)
    dfLFHFElement = dfLFHFElement.dropna(subset=["LFHF(Element)"])
    dfLFHFElement["AppTime"] = dfLFHFElement["AppTime"].apply(convertMillSecToSec)
    dfLFHFElementDelta = df.drop(['#', 'Event', 'Category', 'X', 'Y', 'AriaLabel', 'TimeSpan', 'LFHF(Element)'], axis=1)
    dfLFHFElementDelta = dfLFHFElementDelta.dropna(subset=["LFHF(Element:Delta)"])
    dfLFHFElementDelta["AppTime"] = dfLFHFElementDelta["AppTime"].apply(convertMillSecToSec)
    # print(dfLFHFElement.columns)
    # print(dfLFHFElement.head())
    # print(dfLFHFElementDelta.columns)
    # print(dfLFHFElementDelta.head())

    SetSubPlotMarginFor2PlotsWithTime()
    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0], currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=tuple(multiFigSize))
    dfLFHFElement.plot(ax=axes[0],
                       x="AppTime", y="LFHF(Element)",
                       kind="line", title="LF/HF ratio by HTML elements (" + identifier + ")", legend=None, grid=True,
                       xlabel="Time [s]", ylabel="LF/HF ratio for each HTML elements", colormap=Colormaps[0],
                       style=["o-"])
    dfLFHFElementDelta.plot(ax=axes[1],
                            x="AppTime", y="LFHF(Element:Delta)",
                            kind="line", title="LF/HF delta by HTML elements (" + identifier + ")", legend=None, grid=True,
                            xlabel="Time [s]", ylabel="LF/HF delta for each HTML elements", colormap=Colormaps[1],
                            style=["o-"])
    plt.savefig(figurePath)
    plt.close("all")
    print("Saved " + figurePath)


# Main Function
def Main(identifierString, processedCsvPath, processedCsvEncoding, outputDir, outputFormat):

    # Create dataframe
    df = CreateDataFrameFrom(processedCsvPath, processedCsvEncoding)
    dfFiltered = df.drop(["EventID", "ServerTime", "LFHF", "LFHF(Interpolated)"], axis=1)

    # Fixation time
    fixationTimeFigurePath = outputDir + "/eta_fixation_time_" + identifierString + "." + outputFormat
    ProcessFixationTime(identifierString, dfFiltered, fixationTimeFigurePath)

    # LF/HF summary
    lfhfSummaryFigurePath = outputDir + "/eta_lfhf_summary_" + identifierString + "." + outputFormat
    ProcessLFHFSummary(identifierString, dfFiltered, lfhfSummaryFigurePath)

    # LF/HF timeline
    lfhfTimelineFigurePath = outputDir + "/eta_lfhf_timeline_" + identifierString + "." + outputFormat
    ProcessLFHFTimeline(identifierString, dfFiltered, lfhfTimelineFigurePath)


if __name__ == "__main__":
    currentDatetime = datetime.datetime.now()
    currentDatetimeString = currentDatetime.strftime("%Y%m%d%H%M%S")

    parser = argparse.ArgumentParser(description="ETA-Analyzer: CSV Plotter",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("source", type=str,
                        help="Processed csv file created via eta_csv_processor.py")
    parser.add_argument("-i", "--identifier", type=str, default=currentDatetimeString,
                        help="Unique identifier for output image files \n (default: YYYYMMDDhhmmss)")
    parser.add_argument("-e", "--input-encoding", type=str, choices=["utf_8", "shift_jis"], default="shift_jis",
                        help="Encoding of the input csv file \n (default: shift_jis)")
    parser.add_argument("-d", "--output-dir", type=str, default="plotout",
                        help="The destination directory for output image files \n (default: plotout)")
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
    if args.output_dir[-1] == "/":
        formattedOutputDir = args.output_dir[0:-1]
    os.makedirs(formattedOutputDir, exist_ok=True)

    # Set pyplot configs
    plt.rcParams["figure.figsize"] = args.output_size
    plt.rcParams["figure.dpi"] = args.output_dpi
    if args.output_grid_disable:
        plt.rcParams["grid.alpha"] = 0.0
    else:
        plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["grid.color"] = "gray"
    plt.rcParams["grid.linestyle"] = "dotted"

    Main(args.identifier, args.source, args.input_encoding, formattedOutputDir, args.output_format)
