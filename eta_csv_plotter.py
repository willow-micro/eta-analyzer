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
import seaborn as sns

# Configs

# Global Variables
Colormaps = ["Dark2", "tab10"]

# Functions
def CreateDataFrameFrom(csvPath, csvEncoding):
    dataFrame = pd.read_csv(csvPath, encoding=csvEncoding)
    return dataFrame

def SetPlotMarginFor4PlotsWithXCategories():
    plt.rcParams["figure.subplot.left"] = 0.08
    plt.rcParams["figure.subplot.right"] = 0.95
    plt.rcParams["figure.subplot.bottom"] = 0.15
    plt.rcParams["figure.subplot.top"] = 0.95
    plt.rcParams["figure.subplot.wspace"] = 0.15
    plt.rcParams["figure.subplot.hspace"] = 0.6

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


def ProcessFixationTimeSummary(identifier, df, figurePath):
    #print(df.columns)
    dfPivotSum = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.sum)
    dfPivotSum = dfPivotSum.rename(columns={"TimeSpan": "Total fixation time"})
    dfPivotSumSorted = dfPivotSum.sort_values("Total fixation time", ascending=False)

    dfPivotMean = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.mean)
    dfPivotMean = dfPivotMean.rename(columns={"TimeSpan": "Mean fixation time"})
    dfPivotMeanSorted = dfPivotMean.sort_values("Mean fixation time", ascending=False)

    SetPlotMarginFor4PlotsWithXCategories()
    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0] * 2, currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=tuple(multiFigSize))
    dfPivotSum.plot(ax=axes[0, 0],
                    kind="bar", title="Total fixation time by categories (" + identifier + ")", legend=None, grid=True,
                    xlabel="Category of elements in HTML", ylabel="Total fixation time [ms]", colormap=Colormaps[0])
    dfPivotSumSorted.plot(ax=axes[1, 0],
                          kind="bar", title="Sorted total fixation time by categories (" + identifier + ")", legend=None, grid=True,
                          xlabel="Category of elements in HTML", ylabel="Total fixation time [ms]", colormap=Colormaps[0])
    dfPivotMean.plot(ax=axes[0, 1],
                     kind="bar", title="Mean fixation time by categories (" + identifier + ")", legend=None, grid=True,
                     xlabel="Category of elements in HTML", ylabel="Mean fixation time [ms]", colormap=Colormaps[1])
    dfPivotMeanSorted.plot(ax=axes[1, 1],
                           kind="bar", title="Sorted mean fixation time by categories (" + identifier + ")", legend=None, grid=True,
                           xlabel="Category of elements in HTML", ylabel="Mean fixation time [ms]", colormap=Colormaps[1])
    plt.savefig(figurePath)
    plt.close("all")
    print("Successfully saved: " + figurePath)

def CreateDataFrameForCategorizedPlotFrom(df):
    #print(df.columns)
    # > ["#", "Event", "Category", "AppTime", "X", "Y", "AriaLabel", "TimeSpan", "LFHF(Element)", "LFHF(Element:Delta)"]
    dfFiltered = df.drop(["#", "Event", "X", "Y", "AriaLabel", "TimeSpan", "LFHF(Element)", "LFHF(Element:Delta)"], axis=1)
    #print(dfFiltered.columns)
    # > ["Category", "AppTime"]

    dfIndexed = dfFiltered.set_index("AppTime", drop=True)
    dfIndexed = dfIndexed[~dfIndexed.index.duplicated(keep="first")]
    #print(dfIndexed.head())

    dfFilled = dfIndexed.reindex(index=range(dfIndexed.index.to_series().min(),
                                             dfIndexed.index.to_series().max(),
                                             1000),
                                 method="ffill")

    convertMillSecToSec = lambda t: round(t / 1000.0)
    dfFilled["AppTimeSec"] = dfFilled.index.to_series().apply(convertMillSecToSec)
    #print(dfFilled.head())

    return dfFilled

def ProcessFixatedCategoryTimeSeries(identifier, df, figurePath):
    dfForCategories = CreateDataFrameForCategorizedPlotFrom(df)

    SetPlotMarginFor1PlotWithXTimeYCategories()
    plt.title("Fixated categories (" + identifier + ")")
    sp = sns.stripplot(data=dfForCategories, x=dfForCategories["AppTimeSec"], y=dfForCategories["Category"],
                       order=sorted(dfForCategories["Category"].unique().tolist()),
                       marker="s", size=2.5, jitter=0.0, palette=sns.color_palette("bright"), rasterized=True)
    sp.set(xlabel="Time [s]",
           ylabel="Category of elements in HTML")
    plt.savefig(figurePath)
    plt.close("all")
    print("Successfully saved: " + figurePath)

def ProcessLFHFSummary(identifier, df, figurePath):
    #print(df.columns)
    dfPivotDeltaSum = pd.pivot_table(df, index="Category", values="LFHF(Element:Delta)", margins=False, aggfunc=np.sum)
    dfPivotDeltaSum = dfPivotDeltaSum.rename(columns={"LFHF(Element:Delta)": "Total LF/HF Delta"})
    dfPivotDeltaSumSorted = dfPivotDeltaSum.sort_values("Total LF/HF Delta", ascending=False)

    dfPivotMean = pd.pivot_table(df, index="Category", values="LFHF(Element)", margins=False, aggfunc=np.mean)
    dfPivotMean = dfPivotMean.rename(columns={"LFHF(Element)": "Mean LF/HF"})
    dfPivotMeanSorted = dfPivotMean.sort_values("Mean LF/HF", ascending=False)

    SetPlotMarginFor4PlotsWithXCategories()
    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0] * 2, currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=tuple(multiFigSize))
    dfPivotDeltaSum.plot(ax=axes[0, 0],
                         kind="bar", title="Total LF/HF delta by categories (" + identifier + ")", legend=None, grid=True,
                         xlabel="Category of elements in HTML", ylabel="Total LF/HF delta", colormap=Colormaps[0])
    dfPivotDeltaSumSorted.plot(ax=axes[1, 0],
                               kind="bar", title="Sorted total LF/HF delta by categories (" + identifier + ")", legend=None, grid=True,
                               xlabel="Category of elements in HTML", ylabel="Total LF/HF delta", colormap=Colormaps[0])
    dfPivotMean.plot(ax=axes[0, 1],
                     kind="bar", title="Mean LF/HF by categories (" + identifier + ")", legend=None, grid=True,
                     xlabel="Category of elements in HTML", ylabel="Mean LF/HF", colormap=Colormaps[1])
    dfPivotMeanSorted.plot(ax=axes[1, 1],
                           kind="bar", title="Sorted mean LF/HF by categories (" + identifier + ")", legend=None, grid=True,
                           xlabel="Category of elements in HTML", ylabel="Mean LF/HF", colormap=Colormaps[1])
    plt.savefig(figurePath)
    plt.close("all")
    print("Successfully saved: " + figurePath)

def CreateDataFrameForLFHFPlotFrom(df):
    # print(df.columns)
    # > ["#", "Event", "Category", "AppTime", "X", "Y", "AriaLabel", "TimeSpan", "LFHF(Element)", "LFHF(Element:Delta)"]
    convertMillSecToSec = lambda t: round(t / 1000.0)
    dfLFHFElement = df.drop(["#", "Event", "Category", "X", "Y", "AriaLabel", "TimeSpan", "LFHF(Element:Delta)"], axis=1)
    dfLFHFElement = dfLFHFElement.dropna(subset=["LFHF(Element)"])
    dfLFHFElement["AppTime"] = dfLFHFElement["AppTime"].apply(convertMillSecToSec)

    return dfLFHFElement

def ProcessLFHFTimeSeries(identifier, df, figurePath):
    dfForLFHF = CreateDataFrameForLFHFPlotFrom(df)

    plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
    #plt.gca().get_yaxis().set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    plt.gca().get_yaxis().set_major_formatter(mpl.ticker.FormatStrFormatter("%.1f"))
    SetPlotMarginFor1PlotWithXTime()
    dfForLFHF.plot(x="AppTime", y="LFHF(Element)",
                   kind="line", title="LF/HF ratio (" + identifier + ")", legend=None, grid=True,
                   xlabel="Time [s]", ylabel="LF/HF ratio for each element in HTML", colormap=Colormaps[0],
                   style=["o-"], ms=3, lw=1)
    plt.savefig(figurePath)
    plt.close("all")
    print("Successfully saved: " + figurePath)

def ProcessFixatedCategoryAndLFHFTimeSeries(identifier, df, figurePath):
    dfForLFHF = CreateDataFrameForLFHFPlotFrom(df)
    dfForCategories = CreateDataFrameForCategorizedPlotFrom(df)

    SetPlotMarginFor1PlotWithXTimeYCategories()
    fig, axBase = plt.subplots()
    axAlt = axBase.twinx()
    axAlt.get_yaxis().get_major_formatter().set_useOffset(False)
    #axAlt.get_yaxis().set_major_locator(mpl.ticker.MaxNLocator(integer=True))
    axAlt.get_yaxis().set_major_formatter(mpl.ticker.FormatStrFormatter("%.1f"))
    dfForLFHF.plot(ax=axAlt,
                   x="AppTime", y="LFHF(Element)",
                   kind="line", title="Fixated categories and LF/HF ratio (" + identifier + ")", legend=None, grid=True,
                   xlabel="Time [s]", ylabel="LF/HF ratio for each element in HTML", colormap=Colormaps[0],
                   style=["x-"], ms=3.5, lw=2, alpha=0.5)
    sp = sns.stripplot(ax=axBase,
                       data=dfForCategories, x=dfForCategories["AppTimeSec"], y=dfForCategories["Category"],
                       order=sorted(dfForCategories["Category"].unique().tolist()),
                       marker="s", size=2.5, jitter=0.0, palette=sns.color_palette("bright"), rasterized=True)
    sp.set(xlabel="Time [s]",
           ylabel="Category of elements in HTML")
    plt.savefig(figurePath)
    plt.close("all")
    print("Successfully saved: " + figurePath)


# Main Function
def Main(identifierString, processedCsvPath, processedCsvEncoding, outputDir, outputFormat):
    # Create dataframe
    df = CreateDataFrameFrom(processedCsvPath, processedCsvEncoding)
    dfFiltered = df.drop(["EventID", "ServerTime", "LFHF", "LFHF(Interpolated)"], axis=1)

    # Fixation time summary
    fixationTimeSummaryFigurePath = outputDir + identifierString + "/" + identifierString + "_fixation_time_summary." + outputFormat
    ProcessFixationTimeSummary(identifierString, dfFiltered, fixationTimeSummaryFigurePath)

    # Fixated category time series
    fixatedCategoryTimeSeriesFigurePath = outputDir + identifierString + "/" + identifierString + "_fixated_category_time_series." + outputFormat
    ProcessFixatedCategoryTimeSeries(identifierString, dfFiltered, fixatedCategoryTimeSeriesFigurePath)

    # LF/HF summary
    lfhfSummaryFigurePath = outputDir + identifierString + "/" + identifierString + "_lfhf_summary." + outputFormat
    ProcessLFHFSummary(identifierString, dfFiltered, lfhfSummaryFigurePath)

    # LF/HF time series
    lfhfTimeSeriesFigurePath = outputDir + identifierString + "/" + identifierString + "_lfhf_time_series." + outputFormat
    ProcessLFHFTimeSeries(identifierString, dfFiltered, lfhfTimeSeriesFigurePath)

    # Fixated category and LF/HF time series
    fixatedCategoryTimeAndLFHFSeriesFigurePath = outputDir + identifierString + "/" + identifierString + "_fixated_category_and_lfhf_time_series." + outputFormat
    ProcessFixatedCategoryAndLFHFTimeSeries(identifierString, dfFiltered, fixatedCategoryTimeAndLFHFSeriesFigurePath)


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

    Main(args.identifier, args.source, args.input_encoding, formattedOutputDir, args.output_format)
