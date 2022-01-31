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

# Functions
def CreateDataFrameFrom(csvPath, csvEncoding):
    dataFrame = pd.read_csv(csvPath, encoding=csvEncoding)
    return dataFrame

def ProcessTimeSpan(df, figurePath):
    #print(df.columns)
    dfPivotSum = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.sum)
    dfPivotSum = dfPivotSum.rename(columns={"TimeSpan": "Total fixation time"})
    dfPivotSumSorted = dfPivotSum.sort_values("Total fixation time", ascending=False)

    dfPivotMean = pd.pivot_table(df, index="Category", values="TimeSpan", margins=False, aggfunc=np.mean)
    dfPivotMean = dfPivotMean.rename(columns={"TimeSpan": "Mean fixation time"})
    dfPivotMeanSorted = dfPivotMean.sort_values("Mean fixation time", ascending=False)

    currentFigSize = list(plt.rcParams["figure.figsize"])
    multiFigSize = [currentFigSize[0] * 2, currentFigSize[1] * 2]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=tuple(multiFigSize))
    dfPivotSum.plot(ax=axes[0, 0],
                 kind="bar", title="Total fixation time by categories", legend=None,
                 xlabel="Category of html elements", ylabel="Total fixation time [ms]")
    dfPivotSumSorted.plot(ax=axes[1, 0],
                 kind="bar", title="Total fixation time by categories (sorted)", legend=None,
                 xlabel="Category of html elements", ylabel="Total fixation time [ms]")
    dfPivotMean.plot(ax=axes[0, 1],
                 kind="bar", title="Mean fixation time by categories", legend=None,
                 xlabel="Category of html elements", ylabel="Mean fixation time [ms]")
    dfPivotMeanSorted.plot(ax=axes[1, 1],
                 kind="bar", title="Mean fixation time by categories (sorted)", legend=None,
                 xlabel="Category of html elements", ylabel="Mean fixation time [ms]")
    plt.savefig(figurePath)
    plt.close("all")


# Main Function
def Main(identifierString, processedCsvPath, processedCsvEncoding, outputDir, outputFormat):

    # Create dataframe
    df = CreateDataFrameFrom(processedCsvPath, processedCsvEncoding)
    dfFiltered = df.drop(["EventID", "ServerTime", "LFHF", "LFHF(Interpolated)"], axis=1)

    # Time span
    timeSpanFigurePath = outputDir + "/eta_timespan_" + identifierString + "." + outputFormat
    ProcessTimeSpan(dfFiltered, timeSpanFigurePath)


if __name__ == "__main__":
    currentDatetime = datetime.datetime.now()
    currentDatetimeString = currentDatetime.strftime("%Y%m%d%H%M%S")

    parser = argparse.ArgumentParser(description="ETA-Analyzer: CSV Processor",
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
                        help="Image size for figsize in the matplotlib \n (default: 8 6)")
    parser.add_argument("-D", "--output-dpi", type=float, default=300.0,
                        help="Image DPI \n (default: 300.0)")
    args = parser.parse_args()

    # Get output directory path
    formattedOutputDir = args.output_dir
    if args.output_dir[-1] == "/":
        formattedOutputDir = args.output_dir[0:-1]
    os.makedirs(formattedOutputDir, exist_ok=True)

    # Set pyplot configs
    plt.rcParams["figure.figsize"] = args.output_size
    plt.rcParams["figure.dpi"] = args.output_dpi
    plt.rcParams["figure.subplot.left"] = 0.08
    plt.rcParams["figure.subplot.right"] = 0.95
    plt.rcParams["figure.subplot.bottom"] = 0.15
    plt.rcParams["figure.subplot.top"] = 0.95
    plt.rcParams["figure.subplot.wspace"] = 0.15
    plt.rcParams["figure.subplot.hspace"] = 0.6

    Main(args.identifier, args.source, args.input_encoding, formattedOutputDir, args.output_format)
