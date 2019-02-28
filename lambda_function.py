from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from edinet_xbrl.edinet_xbrl_downloader import EdinetXbrlDownloader
import glob, os, sys
import pandas as pd
import logging
import os
import urllib.request, urllib.parse
import json
import shutil
import matplotlib as mpl
import matplotlib.pyplot as plt
import boto3



def get_xrml(ticker, tmp_dir):
    ## init downloader
    xbrl_downloader = EdinetXbrlDownloader()

    ## set a ticker you want to download xbrl file

    #target_dir = "C:/workspace/Invest/xbrl"
    target_dir = tmp_dir
    folder_path = target_dir+"/"+ticker

    if os.path.exists(folder_path) == False:
        print("-make directry and download xbrlfiles...")
        os.mkdir(folder_path)
        xbrl_downloader.download_by_ticker(ticker, folder_path)

    ## init parser
    parser = EdinetXbrlParser()

    ## parse xbrl file and get data container
    file_list = glob.glob(folder_path+"/*")

    for filename in file_list:
        fn =filename.strip(folder_path)
        if ("asr" in filename):
            os.rename(filename, (folder_path+"/"+fn[31:35]+fn[36:44]+"-q4"+fn[55:]) )
        elif ("q1r" in filename):
            os.rename(filename, (folder_path+"/"+fn[31:35]+fn[36:44]+"-q1"+fn[55:]) )
        elif ("q2r" in filename):
            os.rename(filename, (folder_path+"/"+fn[31:35]+fn[36:44]+"-q2"+fn[55:]) )
        elif ("q3r" in filename):
            os.rename(filename, (folder_path+"/"+fn[31:35]+fn[36:44]+"-q3"+fn[55:]) )
        print(filename)


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


    print("-start...")
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
    print("-complete.")
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



def push_text(user_id, msg):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ os.environ['LINE_CHANNEL_ACCESS_TOKEN'],
    }
    body = {
        'to': user_id,
        'messages': [
            {
                "type":"text",
                "text":msg,
            }
        ]
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
    responce = urllib.request.urlopen(req)
    return responce.read()

def push_fig(user_id, fig_url):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ os.environ['LINE_CHANNEL_ACCESS_TOKEN'],
    }
    body = {
        'to': user_id,
        'messages': [
            {
                "type":"image",
                "originalContentUrl":fig_url,
                "previewImageUrl":fig_url,
            }
        ]
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
    responce = urllib.request.urlopen(req)
    return responce.read()

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(event)
    logger.info(context)
    
    #line_reply_msg
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ os.environ['LINE_CHANNEL_ACCESS_TOKEN'],
    }
    body = {
        'replyToken': event['events'][0]['replyToken'],
        'messages': [
            {
                "type":"text",
                "text":"銘柄コード:"+event['events'][0]['message']['text']+"の決算書の取得を開始します.",
            }
        ]
    }
    user_id = event['events'][0]['source']['userId']

    logger.info(headers)
    logger.info(json.dumps(body))
    
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req) as res:
            logger.info(res.read().decode("utf-8"))
    
    #analyze
    ticker = event['events'][0]['message']['text']
    logger.info(type(ticker))
    logger.info(ticker)
    
    if ( ( ticker.isdigit() == True ) & ( len(ticker) == 4 ) ):
        msg="銘柄コード:"+ticker+", 決算書を読んでいます...1分ほどお待ちください...."
        push_text(user_id, msg)

        path = "/tmp"
        df = get_xrml(ticker, path)
        df = df.fillna(0)
        
        df["txt"] = df["txt"].str.strip(path+'/'+ticker)
        df["txt"] = df["txt"].str.strip('.xbrl')
        df["txt"] = df["txt"].str[0:6]+df["txt"].str[12:15]
        logger.info(df["txt"])
        
        df = df.sort_values(by="txt")
        logger.info(df["txt"])
        
        cnt = 0
        for column in df.columns:
            if column != "txt":
                fig_name = 'fig_'+str(cnt)+'.png'
                plt.figure()
                
                push_text(user_id, "--"+column+"--")
                plt.xlabel('Quarter')
                plt.ylabel(column+'[MillionJPY]')
                
                plt.bar(df["txt"] ,df[column]/1000000)
                plt.xticks(rotation=90)
                plt.savefig(path+'/'+fig_name)
                fig = open(path+'/'+fig_name, 'rb')
                
                bucket_name = "test-gomi"
                target_dir = "abc"

                s3_client = boto3.client(service_name = 's3',
                                         aws_access_key_id = os.environ['AWS_ACCESS'],
                                         aws_secret_access_key = os.environ['AWS_SECRET_ACCESS'],
                                         region_name =os.environ['REGION_NAME']
                                         )

                result  = s3_client.put_object(Bucket=bucket_name, Key=(target_dir+"/"+fig_name), Body=fig)
                fig_url = s3_client.generate_presigned_url(ClientMethod = 'get_object',
                                                         Params = {'Bucket': bucket_name, 'Key':(target_dir+'/'+fig_name) }, 
                                                         ExpiresIn = 1000,
                                                         HttpMethod = 'GET'
                                                         )
                #line_push_msg
                responce = push_fig(user_id, fig_url)
                cnt = cnt + 1
                
        rmdir(path+"/"+ticker)
        logger.info(df)
    else:
        push_text(user_id, "4桁の銘柄コードを入力してください.")

    return {'statusCode': 200, 'body': '{}'}

def rmdir(path):
    shutil.rmtree(path)

