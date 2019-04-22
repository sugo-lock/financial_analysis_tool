# -*- coding: utf-8 -*-
import glob, os, sys
import re

import shutil
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from edinet_xbrl.edinet_xbrl_downloader import EdinetXbrlDownloader


def download(ticker, dl_dir):
    print("START DOWNLODING")
    ## init downloader
    xbrl_downloader = EdinetXbrlDownloader()
    ## set a ticker you want to download xbrl file
    folder_path = dl_dir+"/"+ticker
    if os.path.exists(folder_path) == True:
        shutil.rmtree(folder_path)
        print('-- Remove Directry --')

    print("-- Makeing Directry --")
    os.mkdir(folder_path)
    print("-- Downloading xbrls --")
    xbrl_downloader.download_by_ticker(ticker, folder_path)
    rename(folder_path)
    print("FINISH DOWNLODING")


def rename(folder_path):
    file_list = glob.glob(folder_path+"/*")
    print("START RENAMING")
    # RENAME
    for filename in file_list:
        fn = filename.strip(folder_path)
        d_lst = [s for s in re.split('[-_.]', fn) if s.isdigit()]
        st = d_lst[2][2:]+d_lst[3]+d_lst[4]

        if ("asr" in filename):
            os.rename(filename, (folder_path+"/"+st+"-q4"+".xbrl") )
        elif ("q1r" in filename):
            os.rename(filename, (folder_path+"/"+st+"-q1"+".xbrl") )
        elif ("q2r" in filename):
            os.rename(filename, (folder_path+"/"+st+"-q2"+".xbrl") )
        elif ("q3r" in filename):
            os.rename(filename, (folder_path+"/"+st+"-q3"+".xbrl") )
        else:
            os.remove(filename)
        print(filename)
    print("FINISH RENAMING")

def parse(dir, ticker):
    print("START PARSING")
    folder_path = dir+"/"+ticker
    file_list = glob.glob(folder_path+"/*")
    ## init parser
    parser = EdinetXbrlParser()

    ## get value from container
    keys_dict = {
    "社名":["jpcrp_cor:CompanyNameCoverPage"],
    "文書名":["jpcrp_cor:DocumentTitleCoverPage"],
    "期間":["jpcrp_cor:QuarterlyAccountingPeriodCoverPage"],
    "Sales":["jppfs_cor:NetSales"],
    "OperatingIncome":["jppfs_cor:OperatingIncome"],
    "OrdinaryIncome":["jppfs_cor:OrdinaryIncome"],
    "CurrentAssets":["jppfs_cor:CurrentAssets"],
    "FixedAssets":["jppfs_cor:IntangibleAssets", "jppfs_cor:NoncurrentAssets"],
    "CurrentLiabilities":["jppfs_cor:CurrentLiabilities"],
    "FixedLiabilities":["jppfs_cor:LongTermLoansPayable", "jppfs_cor:NoncurrentLiabilities"],
    "SalesCF":["jppfs_cor:NetCashProvidedByUsedInOperatingActivities"],
    "InvestmentCF":["jppfs_cor:NetCashProvidedByUsedInInvestmentActivities"],
    "FinanceCF":["jppfs_cor:NetCashProvidedByUsedInFinancingActivities"]
    }

    key_list = ["Sales","OperatingIncome","OrdinaryIncome","CurrentAssets","FixedAssets","CurrentLiabilities","FixedLiabilities","SalesCF","InvestmentCF","FinanceCF"]

    context_ref=["CurrentYTDDuration",
                 "CurrentQuarterInstant",
                 "CurrentYearInstant",
                 "CurrentYearInstant_NonConsolidatedMember",
                 "CurrentYearDuration",
                 "CurrentQuarterInstant_NonConsolidatedMember", 
                 "CurrentYTDDuration_NonConsolidatedMember",
                 "CurrentYearDuration_NonConsolidatedMember"]

    #ここから
    file_list = glob.glob(folder_path+"/*") #フォルダ内のファイル名一覧を取得
    file_list.reverse()

    df = pd.DataFrame(columns = ["txt",  "Sales", "OperatingIncome", "OrdinaryIncome", "CurrentAssets", "FixedAssets", "CurrentLiabilities", "FixedLiabilities", "SalesCF", "InvestmentCF", "FinanceCF"])
    cnt=0
    for filename in file_list:
        edinet_xbrl_object = parser.parse_file(filename)
        copname=""
        doc_name=""
        term =""
        row=[]   #pandas用
        #社名
        key_copname=keys_dict["社名"][0]
        contxtref="FilingDateInstant"
        dtobj=edinet_xbrl_object.get_data_by_context_ref(key_copname, contxtref)
        if dtobj != None:
            copname = dtobj.get_value()

        #文書名
        key_docname=keys_dict["文書名"][0]
        contxtref="FilingDateInstant"
        dtobj=edinet_xbrl_object.get_data_by_context_ref(key_docname, contxtref)
        if dtobj != None:
            doc_name = dtobj.get_value()

        if ( ("四半期報告書" in doc_name) | ( "有価証券報告書" in doc_name) ):
            print("--------")
            print(filename[1:])
            row.append(filename[1:])
            key_term=keys_dict["期間"][0]
            contxtref="FilingDateInstant"
            dtobj=edinet_xbrl_object.get_data_by_context_ref(key_term, contxtref)
            if dtobj != None:
                term = dtobj.get_value()
            for key in key_list:
                flg = 0
                for i in range( len( keys_dict[key] ) ):
                    word = keys_dict[key][i]
                    for j in range( len( context_ref ) ):
                        dtobj= edinet_xbrl_object.get_data_by_context_ref(word, context_ref[j])
                        if dtobj != None:
                            val = dtobj.get_value()
                            if val ==None:
                                val = "-"
                            row.append(int(val))
                            flg = 1
                            break
                    if flg == 1:
                       break
                if flg == 0:
                     row.append(pd.np.nan)
            s = pd.Series(row, index=df.columns, name=cnt)
            df = df.append(s)
            cnt=cnt+1
    
    df["txt"] = df["txt"].str.strip(folder_path)
    df["txt"] = df["txt"].str.strip('.xbrl')
    df["txt"] = df["txt"].str.strip('\\')
    df = df.sort_values(by="txt")
    print("FINISH PARSING")
    return df
    #総資産
    #key = "jppfs_cor:Assets"
    #context_ref = "CurrentQuarterInstant"  #or CurrentQuarterInstant

    #営業CF
    #"jpcrp_cor:NetCashProvidedByUsedInOperatingActivitiesSummaryOfBusinessResults"
    #"CurrentYearDuration"
    #投資CF
    #"jpcrp_cor:NetCashProvidedByUsedInInvestingActivitiesSummaryOfBusinessResults"
    #"CurrentYearDuration"
    #財務CF
    #"jpcrp_cor:NetCashProvidedByUsedInFinancingActivitiesSummaryOfBusinessResults"
    #"CurrentYearDuration"

    #key="jpcrp040300-q1r_E33238-000:ManagementAnalysisOfFinancialPositionOperatingResultsAndCashFlowsTextBlock"
    #context_ref ="FilingDateInstant"


def visualize_individually(ticker, df, save_dir):
    i = 0
    for column in df.columns:
        if column != "txt":
            fig_name = str(i) + column+'.png'
            plt.figure()
            
#            push_text(user_id, "--"+column+"--")
            plt.xlabel('Quarter')
            plt.ylabel(column+'[MillionJPY]')
            plt.bar(df["txt"] ,df[column]/1000000)
            plt.xticks(rotation=90)
            plt.savefig(save_dir+'/'+fig_name)
            fig = open(save_dir+'/'+fig_name, 'rb')
            i = i + 1

def visualize(ticker, df, save_dir):
    df = df.set_index('txt')
    df_ = df/1000000

    h = 12
    w = 8

    plt.figure()
    fig_name = '0_Sales.png'
    df_.plot.bar(y=['Sales'], alpha=0.6, figsize=(h,w))
    plt.xlabel('Quarter')
    plt.ylabel('[MillionJPY]')
    plt.savefig(save_dir+'/'+fig_name)

    fig_name = '1_OpeIncm_OdnIncm.png'
    plt.savefig(save_dir+'/'+fig_name)
    df_.plot.bar(y=['OperatingIncome', 'OrdinaryIncome'], alpha=0.6, figsize=(h,w))
    plt.xlabel('Quarter')
    plt.ylabel('[MillionJPY]')
    plt.savefig(save_dir+'/'+fig_name)

    fig_name = '2_Assets.png'
    plt.savefig(save_dir+'/'+fig_name)
    df_.plot.bar(y=['CurrentAssets', 'FixedAssets', 'CurrentLiabilities', 'FixedLiabilities'], alpha=0.6, figsize=(h,w))
    plt.xlabel('Quarter')
    plt.ylabel('[MillionJPY]')
    plt.savefig(save_dir+'/'+fig_name)

    fig_name = '3_CF.png'
    plt.savefig(save_dir+'/'+fig_name)
    df_.plot.bar(y=['SalesCF', 'InvestmentCF', 'FinanceCF'], alpha=0.6, figsize=(h,w))
    plt.xlabel('Quarter')
    plt.ylabel('[MillionJPY]')
    plt.savefig(save_dir+'/'+fig_name)


if __name__ == '__main__':
    TICKER = "6550"
    DL_DIR = 'tmp'
    
    download(TICKER, DL_DIR)
    df = parse(DL_DIR, TICKER)
    visualize(TICKER, df, DL_DIR+'/'+TICKER)
    print(df)
