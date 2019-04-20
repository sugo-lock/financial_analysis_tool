# -*- coding: utf-8 -*-
import logging
import json
import shutil

import line_if
import xbrl_if
import s3_if

def lambda_handler(event, context):
    tmp_path = "/tmp"
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.info(event)
    logger.info(context)
    
    # REPLY_LINE
    msg = "銘柄コード:"+event['events'][0]['message']['text']+"の決算を表示します."
    user_id = event['events'][0]['source']['userId']
    replyToken = event['events'][0]['replyToken']
#    line_if.reply_msg(user_id, msg, replyToken)

    ticker = event['events'][0]['message']['text']
    logger.info(ticker)
    
    if ( ( ticker.isdigit() == True ) & ( len(ticker) == 4 ) ):
        # PUSH_LINE
        msg="銘柄コード:"+ticker+" の決算を表示します"
        line_if.push_msg(user_id, msg)
        
        # S3-KEY Confirmation
        BUCKET_NAME = 'kabu-tool'
        KEY = ticker
        url_list = s3_if.exists(BUCKET_NAME, KEY)
        
        if url_list == []:
            # DL_XBRL
            xbrl_if.download(ticker, tmp_path)

            # PARSER_XBRL
            df = xbrl_if.parse(tmp_path, ticker)
            df = df.fillna(0)
            xbrl_if.visualize(ticker, df, tmp_path+'/'+ticker)
            logger.info(df["txt"])
            logger.info(df)

            # S3_UPLOAD
            url_list = s3_if.upload(tmp_path+'/'+ticker, BUCKET_NAME, KEY)

            # RMDIR
            rmdir(tmp_path+"/"+ticker)

        # PUSH_FIG_LINE
        for fig_url in url_list:
            responce = line_if.push_fig(user_id, fig_url)

    else:
        line_if.push_msg(user_id, "4桁の銘柄コードを入力してください.")

    return {'statusCode': 200, 'body': '{}'}

def rmdir(path):
    shutil.rmtree(path)




