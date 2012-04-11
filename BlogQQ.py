#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

For BlogsToWordpress, this file contains the functions for QQ Space.

[TODO]

"""

import os;
import re;
import sys;
import time;
import chardet;
import urllib;
import urllib2;
from datetime import datetime,timedelta;
from BeautifulSoup import BeautifulSoup,Tag,CData;
import logging;
import crifanLib;
import cookielib;
#from xml.sax import saxutils;
import json; # New in version 2.6.
import random;

#--------------------------------const values-----------------------------------
__VERSION__ = "v1.5";

gConst = {
    'spaceDomain'  : 'http://user.qzone.qq.com',
    
    'datetimePattern' : "%Y-%m-%d %H:%M:%S",
    
    'qqServer'      : {
        'blog_output_data'      : [
            'b11',  #http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=1083902439&blogid=1321000398...
            'b1',   # http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=984817619&blogid=1332499692...
        ],

        'blog_get_specialtitle' : [
            'b11',  #http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_specialtitle?uin=1083902439&blogid=1321000398...
        ],
        
        'blog_get_datenum'      : [
            'b1',   #http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_datenum?oweruin=84483423...
        ],
        
        'blog_output_titlelist2': [
            'b1',   #http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_titlelist2?uin=84483423...
        ],
        
        'blog_get_titlelist'    : [
            'b',    #http://b.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_titlelist?uin=84483423....
        ],
        
        'blog_get_countlist'    : [
            'b',    #http://b.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_countlist?type=1&uin=84483423&blogids=1317915494&blogids=1317911753
        ],
    }
}

#----------------------------------global values--------------------------------
gVal = {
    'blogUser'      : '',   # 84483423
    'blogEntryUrl'  : '',   # http://user.qzone.qq.com/84483423
    'cj'            : None, # cookiejar, to store cookies for login mode
    
    'extractedPostInfo' : {},   # the post info dict, contains what we have extracted, the key should be blogid(int type)
    
    'debugLastId'   : 0,
}

# some rules for QQ space
# 1. all blogid should be int type, not string type !!!

################################################################################
# Internal QQ Space Functions 
################################################################################

def findQQnumberFromOwnname(ownName):
    qqNumber = "";
    
    blogEntryUrl = "http://" + ownName + ".qzone.qq.com";
    
    #access http://ninaying.qzone.qq.com/, can return:
    #var g_userProfile = {"uin":+"17473070","nickname":"应应","spacename":"应应的空间","desc":"应应有点任性虚荣，幸福的生活… ","signature":"感谢大家喜欢我的空间，多谢捧场，转载请注明出处，稿件事宜联络本人qq邮箱。","avatar":"http:\/\/b86.photo.store.qq.com\/psb?\/617461363\/w3kwZLeTr1JyWZBR5Cq9lsrzNF8sjzxcfu8fqxLL23Y!\/b\/YYuySDP0LwAAYo5CSjN*LwAA","sex_type":+"0","sex":+"2","animalsign_type":+"0","animalsign":+"11","constellation_type":+"0","constellation":+"3","age_type":+"0","age":+"101","islunar":+"0","birthday_type":+"0","birthyear":+"1911","birthday":"07-16","bloodtype":+"1","address_type":+"0","country":"中国","province":"","city":"","home_type":+"0","hco":"","hp":"","hc":"","marriage":+"1","lover":"","career":"待业\/无业\/失业","company":"","compaddr_type":+"0","cco":"","cp":"","cc":"","cb":"","mailname":"","mailcellphone":"","mailaddr":""};

    # Note: html is UTF-8 format
    respHtml = crifanLib.getUrlRespHtml(blogEntryUrl);
    logging.debug("%s return html:\n%s", blogEntryUrl, respHtml);
    foundUserProfile = re.search(r'var\s+?g_userProfile\s+?=\s*?\{"uin":.+?"(?P<qqNumber>\d+)","nickname"', respHtml);
    if(foundUserProfile):
        qqNumber = foundUserProfile.group("qqNumber");

    return qqNumber;
    
    
################################################################################
# Implemented Common Functions 
################################################################################

#------------------------------------------------------------------------------
# extract blog user name:
# (1) 84483423 from: 
# http://84483423.qzone.qq.com
# http://84483423.qzone.qq.com/
# http://ninaying.qzone.qq.com/
# http://ninaying.qzone.qq.com
# (2) 84483423 from:
# http://user.qzone.qq.com/84483423
# http://user.qzone.qq.com/84483423/
# http://user.qzone.qq.com/84483423/blog/1317911753
# (3) 622007179 from:
# http://blog.qq.com/qzone/622007179/1333268691.htm
# its real address is http://user.qzone.qq.com/622007179/blog/1333268691
# (4) ninaying from :
# http://ninaying.qzone.qq.com
# http://ninaying.qzone.qq.com/
def extractBlogUser(inputUrl):
    (extractOk, extractedBlogUser, generatedBlogEntryUrl) = (False, "", "");
    logging.debug("Extracting blog user from url=%s", inputUrl);
    
    try :
        # type1, main url: 
        #http://84483423.qzone.qq.com
        #http://84483423.qzone.qq.com/
        foundMainUrl = re.search("(?P<mainUrl>http://(?P<username>\d+)\.qzone\.qq\.com).*", inputUrl);
        if(foundMainUrl) :
            extractedBlogUser = foundMainUrl.group("username");
            #generatedBlogEntryUrl = foundMainUrl.group("mainUrl");
            generatedBlogEntryUrl = gConst['spaceDomain'] + "/" + extractedBlogUser + "/blog";
            extractOk = True;
        
        # type2, main url:
        #http://user.qzone.qq.com/84483423
        #http://user.qzone.qq.com/84483423/
        #http://user.qzone.qq.com/84483423/blog/
        #http://user.qzone.qq.com/84483423/blog/1317911753
        #http://user.qzone.qq.com/815920900/blog/1307491670#!app=2&pos=1307491670
        if(not extractOk):
            foundUser = re.search("http://user\.qzone\.qq\.com/(?P<username>\d+)(/blog.*$)?", inputUrl);
            if(foundUser) :
                extractedBlogUser = foundUser.group("username");
                #generatedBlogEntryUrl = "http://" + extractedBlogUser + ".qzone.qq.com";
                generatedBlogEntryUrl = gConst['spaceDomain'] + "/" + extractedBlogUser + "/blog";
                extractOk = True;
        
        # type3:
        # (1)special single perma link:
        #http://blog.qq.com/qzone/622007179/1333268691.htm
        # (2)actual follow address is invalid even in IE/Chrome for QQ Space, but here also support it here
        #http://blog.qq.com/qzone/622007179/
        if(not extractOk):
            foundPermaLink = re.search("http://blog\.qq\.com/qzone/(?P<username>\d+)/?(\d+.htm)?$", inputUrl);
            if(foundPermaLink) :
                extractedBlogUser = foundPermaLink.group("username");
                generatedBlogEntryUrl = "http://" + extractedBlogUser + ".qzone.qq.com";
                extractOk = True;
        
        # type4: own name, not QQ number
        #http://ninaying.qzone.qq.com
        if(not extractOk):
            foundOwnname = re.search("http://(?P<username>\w+?)\.qzone\.qq\.com/?$", inputUrl);
            if(foundOwnname):
                extractedOwnname = foundOwnname.group("username");
                # from ninaying find its QQ number: 17473070
                extractedBlogUser = findQQnumberFromOwnname(extractedOwnname);
                if(extractedBlogUser) :
                    generatedBlogEntryUrl = "http://" + extractedBlogUser + ".qzone.qq.com";
                    extractOk = True;
                else :
                    extractOk = False;

    except :
        (extractOk, extractedBlogUser, generatedBlogEntryUrl) = (False, "", "");
        
    if (extractOk) :
        gVal['blogUser'] = extractedBlogUser;
        gVal['blogEntryUrl'] = generatedBlogEntryUrl;
        
    return (extractOk, extractedBlogUser, generatedBlogEntryUrl);

#------------------------------------------------------------------------------
# extract the json string from via remove __Callback:
# _Callback(
# {"data":{
# "ret":0,
# "msg":"成功",
# "totalnum":3,
# "list":[
# {"blogid":1321609592,
# "type":0,
# "pubtime":"2011-11-18 17:46",
# "replytime":1333200443,
# "replynum":3,
# "cate":"软件下载区",
# "catehex":"c8edbcfecfc2d4d8c7f8",
# "title":"下页→封爱制作空间专业软件‖【下载】",
# "effect":512,
# "effect2":524294,
# "ar":0,
# "block":0,
# "inproc":false,
# "appeal":0},
# .....}
# );

# _Callback(
# {"data":{
# "thisblog":1236072174,
# "prev_list":[{"blogid":1236591622,
# "title":"找回娇滴滴的那个你——你会撒娇吗？"}],
# "next_list":[{"blogid":1235552124,
# "title":"从贫民到百万富翁转变的心理学基础"}]
# }}
# );
def removeCallbackStr(respCallbackStr) :
    jsonStr = "";
    #foundJson = re.search("_Callback\((?P<jsonStr>.+)\);$", respCallbackStr, re.S);
    foundJson = re.search("_Callback\(\s+(?P<jsonStr>\{.+\})\s+\);$", respCallbackStr, re.S);
    logging.debug("in remove callback string, foundJson=%s", foundJson);
    if(foundJson) :
        jsonStr = foundJson.group("jsonStr");
    return jsonStr;

#------------------------------------------------------------------------------
# parse xxx in {"data":{xxx}} to dict value
# Note: input should be {"data":{xxx}} type string
def parseDataStrToInfoDict(dataJsonStr) :
    #logging.debug("before parse to info dict, input data json str %s", dataJsonStr);
    infoDict = {};

    try :
        #logging.debug("before decode and json.loads, dataJsonStr=%s", dataJsonStr);
        
        defCmtCharset = "GB18030"; # most comment use GB2312/GBK
        #defCmtCharset = "GBK";
        #defCmtCharset = "GB2312";
        #defCmtCharset = "UTF-8";
        validCharset = defCmtCharset;
        try :
            # 1. normal try decode
            dataJsonStrUni = dataJsonStr.decode(validCharset);
            logging.debug("use default charset %s do decode is OK", validCharset);
            
            dataDict = json.loads(dataJsonStrUni, encoding=validCharset);
            infoDict = dataDict['data'];
            logging.debug("use default charset %s do json.loads is OK", validCharset);
        except :
            # 2. if above decode fail, then try to (find the real charset and ) convert to unicode fisrt
            logging.debug("dataJsonStr use default charset %s to decode but occur error !!!", validCharset);

            validCharset = crifanLib.getStrPossibleCharset(dataJsonStr);
            logging.debug("Now try use the detected charset %s to decode it again", validCharset);
            
            try :
                # some comment is not GB2312, such as:
                # "ISO-8859-2" for comment startIdx=180, getNum=57 for http://user.qzone.qq.com/622007179/blog/1218912726
                dataJsonStrUni = dataJsonStr.decode(validCharset);
                logging.debug("dataJsonStr use %s decode OK", validCharset);
                #logging.debug("after use %s decode, dataJsonStrUni=%s", validCharset, dataJsonStrUni);
                
                dataDict = json.loads(dataJsonStrUni, encoding=validCharset);
                infoDict = dataDict['data'];
                logging.debug("use detected charset %s do json parse is OK", validCharset);
            except:
                #logging.debug("current not support this kind of error");
                
                # 3. if still fail, then remove the replylist if exist
                #eg:http://user.qzone.qq.com/622000169/blog/1252395085
                logging.debug("Use detected charset decode and json.loads fail, now try to remove replylist first, then retry decode and json.loads");
                
                replylistP = r'"replylist":(?P<replylist>\[?.+\])\s*\}\}$';
                replacedReplylist = '"replylist":[ ]}}';
                foundReplylist = re.search(replylistP, dataJsonStr, re.S);
                if(foundReplylist) :
                    logging.debug("Found replylist: foundReplylist=%s", foundReplylist);
                    replylistJsonStr = foundReplylist.group("replylist");
                    #logging.debug("extract out the replylist json string:\n%s", replylistJsonStr);
                    
                    logging.debug("remove replylist");
                    subP = re.compile(replylistP, re.S);
                    dataJsonStr = subP.sub(replacedReplylist, dataJsonStr);
                    
                    validCharset = "GB18030";
                    logging.debug("then use charset %s to retry decode", validCharset);
                    dataJsonStrUni = dataJsonStr.decode(validCharset);
                    
                    logging.debug("then use charset %s do json loads", validCharset);
                    dataDict = json.loads(dataJsonStrUni, encoding=validCharset);
                    infoDict = dataDict['data'];
                    logging.debug("after remove replylist then use charset %s do json parse is OK", validCharset);

    except :
        logging.debug("Error while convert to dict for data json str:\n%s", dataJsonStr);

    return infoDict;

#------------------------------------------------------------------------------
# first remove content of replylist then
# parse xxx in {"data":{xxx}} to dict value
# to avoid the parse fail if replylist contain mixed charset string
def parseDataStrToInfoDictEmptyReplylist(dataJsonStr) :
    infoDict = {};
    try :
        replylistP = r'"replylist":(?P<replylist>\[?.+\])\s*\}\}$';
        replacedString = '"replylist":[ ]}}';
        
        # 0. -> can found: foundReplylist= <_sre.SRE_Match object at 0x02E384F0>
        #foundReplylist = re.search(replylistP, dataJsonStr, re.S);
        #print "foundReplylist=",foundReplylist;
        
        # 1. -> not work
        #dataJsonStr = re.sub(replylistP, replacedString, dataJsonStr, re.S);
        
        # 2. -> not work    
        #dataJsonStr = re.compile(replylistP).sub(replacedString, dataJsonStr, re.S);
        
        # 3. -> work
        subP = re.compile(replylistP, re.S);
        dataJsonStr = subP.sub(replacedString, dataJsonStr);
        
        infoDict = parseDataStrToInfoDict(dataJsonStr);
    except :
        logging.debug("Error while convert to dict for data json str:\n%s", dataJsonStr);

    return infoDict;

#------------------------------------------------------------------------------
# parse {"error":{
# "type":"system busy",
# "msg":"服务器繁忙，请稍候再试。"
# }}
# into error reason dict
def parseErrorJsonStrToErrReasonDict(errorJsonStr) :
    errReasonDict = {};
    try :
        errorJsonStrUni = errorJsonStr.decode("GB18030");
        errorDict = json.loads(errorJsonStrUni, encoding="GB18030");
        errReasonDict = errorDict['error'];
    except:
        logging.warning("Error while convert to error reason dict for error json str:\n%s", errorJsonStr);
        
    return errReasonDict;
    
#------------------------------------------------------------------------------
# convert xxx in __Callback string:
# _Callback(
# {"data":{
# xxx
# }}
# ;
# into info dict value
#
# Note: sometime will got:
# _Callback(
# {"error":{
# "type":"system busy",
# "msg":"服务器繁忙，请稍候再试。"
# }}
# );
def callbackStrToInfoDict(respCallbackStr) :
    infoDict = {};
    try:
        #logging.debug("callbackStrToInfoDict: before call removeCallbackStr");
        remainJsonStr = removeCallbackStr(respCallbackStr);
        #logging.debug("remainJsonStr=%s", remainJsonStr);
        infoDict = parseDataStrToInfoDict(remainJsonStr);
        #print "after callbackStrToInfoDict, infoDict=",infoDict;
        if(not infoDict) :
            # maybe:
            # _Callback(
            # {"error":{
            # "type":"system busy",
            # "msg":"服务器繁忙，请稍候再试。"
            # }}
            # );
            foundErrorJsonStr = re.search('\{"error":.+', remainJsonStr, re.S);
            if(foundErrorJsonStr) :
                errReasonDict = parseErrorJsonStrToErrReasonDict(remainJsonStr);
                if(errReasonDict) :
                    errType = errReasonDict['type'];
                    errMsg = errReasonDict['msg'];
                    logging.warning("Error while convert callback string into info dict: error type = %s, error msg = %s !", errType, errMsg);
    except :
        logging.error("Unknown error while contert callback string into info dict !");
        infoDict = {};
    return infoDict;

#------------------------------------------------------------------------------
# found whether current year contains post,
# if contains, return the earliest month
def isYearContainPost(year):
    (containPost, earliestMonth, postNumInMonth) = (False, 0, 0);

    #postInYearUrl = "http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_datenum?oweruin=84483423&year="+str(year)+"&r=0.39298647226382593&g_tk=5381&ref=qzone";
    postInYearUrl = "http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_datenum";
    postInYearUrl += "?oweruin=" + gVal['blogUser'];
    postInYearUrl += "&year=" + str(year);
    postInYearUrl += "&r=" + str(random.random());
    #postInYearUrl += "&g_tk=5381";
    postInYearUrl += "&ref=qzone";
    logging.debug("postInYearUrl=%s", postInYearUrl);
    
    respCallbackStr = crifanLib.getUrlRespHtml(postInYearUrl);
    #logging.debug("postInYearUrl respCallbackStr:\n%s", respCallbackStr);
 
    # extract jsonStr
    postInfoDict = callbackStrToInfoDict(respCallbackStr);
    
    postInMonthList = postInfoDict['month_num'];
    logging.debug("postInMonthList=%s", postInMonthList);
    
    for monthIdx, postNumInMonth in enumerate(postInMonthList):
        if postNumInMonth > 0 :
            # found the first month, that contains posts
            earliestMonth = monthIdx + 1;
            containPost = True;
            logging.debug("found earliest month that that contains post: %s-%02d contain %d posts", year, earliestMonth, postNumInMonth);
            break;

    return (containPost, earliestMonth, postNumInMonth);

#------------------------------------------------------------------------------
# Note: type of startTime and endTime is datetime
# return post list
def getPostWithinPeriod(startTime, endTime, postNumInMonth):
    postList = [];
    
    try :
        startTimestamp = crifanLib.datetimeToTimestamp(startTime);
        endTimestamp = crifanLib.datetimeToTimestamp(endTime);
        logging.debug("timestamp: start=%d, end=%d", startTimestamp, endTimestamp);

        #http://1874789931.qzone.qq.com/ => 2011-05-01 -> 2011-06-01 has 170 posts
        # defaul only return 15 post
        # here should get enough/all post
        # here just need the earliest one, so here just get some of them then found the earliest is OK enough
        #max once get get max 100, so here safely just get some small value, such as (default) 15 post
        onceGetNum = 15;
        postStartNum = postNumInMonth - onceGetNum;
        postGetNum = onceGetNum;
        
        #getPostUrl = "http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_titlelist2?uin=84483423&verbose=0&catehex=&pos=0&num="+str(postGetNum)+"&sorttype=0&v=1&maxlen=68&starttime="+str(startTimestamp)+"&endtime="+str(endTimestamp)+"&bdm=b.cnc.qzone.qq.com&rand=0.14919551610282206&g_tk=5381&cate=&ref=qzone&v6=1";
        
        getPostUrl = "http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_titlelist2";
        getPostUrl += "?uin=" + gVal['blogUser'];
        
        # Note: here verbose set to 1, can get more detailed info, but currently not need this, so just set to 0
        getPostUrl += "&verbose=0";
        #getPostUrl += "&verbose=1"; 
        
        #getPostUrl += "&catehex=";
        
        getPostUrl += "&pos=" + str(postStartNum);
        getPostUrl += "&num=" + str(postGetNum);
        
        #getPostUrl += "&sorttype=0";
        #getPostUrl += "&v=1";
        #getPostUrl += "&maxlen=68";
        getPostUrl += "&starttime=" + str(startTimestamp);
        getPostUrl += "&endtime=" + str(endTimestamp);
        #getPostUrl += "&bdm=b.cnc.qzone.qq.com";
        #getPostUrl += "&rand=" + str(random.random());
        #getPostUrl += "&g_tk=5381";
        #getPostUrl += "&cate=";
        #getPostUrl += "&ref=qzone"
        #getPostUrl += "&v6=1";
        logging.debug("generated url to get post within period: %s", getPostUrl);
        
        respCallbackStr = crifanLib.getUrlRespHtml(getPostUrl);
        logging.debug("getPostWithinPeriod respCallbackStr:\n%s", respCallbackStr);
        
        # {"data":{
        # "ret":0,
        # "msg":"成功",
        # "totalnum":3,
        # "list":[{"blogid":1321610165,
        # "type":0,
        # "pubtime":"2011-11-18 17:56",
        # "replytime":1326363093,
        # "replynum":1,
        # "cate":"〖真人秀〗",
        # "catehex":"a1bcd5e6c8cbd0e3a1bd",
        # "title":"下页：封爱教做QQ真人秀...下面不要红钻qq秀",
        # "effect":512,
        # "effect2":524294,
        # "ar":0,
        # "block":0,
        # "inproc":false,
        # "appeal":0},
        # ...,...],
        # "hostflag":1
        # }}
        retInfoDict = callbackStrToInfoDict(respCallbackStr);
        if(retInfoDict['ret'] == 0 ):
            postList = retInfoDict['list'];
            logging.debug(" return post list len=%d", len(postList));
    except :
        postList = [];
        logging.debug("Error while get post from %s to %s !", str(startTime), str(endTime));
        
    return postList;

#------------------------------------------------------------------------------
# generate url of get real post info from post's blogid
# eg: 1321000398 -> http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=1083902439&blogid=1321000398&v6=1
# in which 1083902439 is blogUser
def genGetPostInfoUrl(blogid, blogOutputDataServer) :
    #http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=1083902439&blogid=1321000398&styledm=cnc.qzonestyle.gtimg.cn&imgdm=cnc.qzs.qq.com&bdm=b.cnc.qzone.qq.com&mode=2&numperpage=15&blogseed=0.000866520617759825&property=GoRE&timestamp=1333414941&dprefix=cnc.&g_tk=5381&ref=qzone&v6=1
    #getPostInfoUrl = "http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data";
    
    # Note:
    # http://user.qzone.qq.com/984817619/blog/1332499692 has changed server from b11 to b1;
    # http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=984817619&blogid=1332499692&styledm=cnc.qzonestyle.gtimg.cn&imgdm=cnc.qzs.qq.com&bdm=b.cnc.qzone.qq.com&mode=2&numperpage=15&blogseed=0.2201952870456741&property=GoRE&timestamp=1333613938&dprefix=cnc.&g_tk=5381&ref=qzone&v6=1
    
    getPostInfoUrl = "http://" + blogOutputDataServer + ".cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data";

    getPostInfoUrl += "?uin=" + gVal['blogUser'];
    getPostInfoUrl += "&blogid=" + str(blogid); #TODO
    #getPostInfoUrl += "&styledm=cnc.qzonestyle.gtimg.cn";
    #getPostInfoUrl += "&imgdm=cnc.qzs.qq.com";
    #getPostInfoUrl += "&bdm=b.cnc.qzone.qq.com";
    #getPostInfoUrl += "&mode=2"; #TODO
    #getPostInfoUrl += "&numperpage=15"; #TODO
    #getPostInfoUrl += "&blogseed=0.000866520617759825"; #TODO
    #getPostInfoUrl += "&property=GoRE";
    
    #curDatetime = datetime.now();
    #curTimestamp = crifanLib.datetimeToTimestamp(curDatetime);
    #print "curTimestamp=",curTimestamp;
    #getPostInfoUrl += "&timestamp=" + str(curTimestamp); #TODO
    
    #getPostInfoUrl += "&dprefix=cnc.";
    #getPostInfoUrl += "&g_tk=5381"; #TODO
    #getPostInfoUrl += "&ref=qzone";
    
    # should include this, otherwise return html format changed !
    getPostInfoUrl += "&v6=1";
    
    logging.debug("from blog_output_data's server=%s, generated getPostInfoUrl : %s", blogOutputDataServer, getPostInfoUrl);
    
    return getPostInfoUrl;

#------------------------------------------------------------------------------
# generate url of get post's previous and next post info from post's blogid
# eg: 1321000398 -> http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_specialtitle?uin=1083902439&blogid=1321000398&nextnum=5&prevnum=5&category=&sorttype=0&r=0.19829247597242194&g_tk=5381&ref=qzone
# in which 1083902439 is blogUser
def genGetPostPrevNextUrl(blogid) :
    #http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_specialtitle?uin=1083902439&blogid=1321000398&nextnum=5&prevnum=5&category=&sorttype=0&r=0.19829247597242194&g_tk=5381&ref=qzone
    getPostPrevNextUrl = "http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_get_specialtitle";
    
    getPostPrevNextUrl += "?uin=" + gVal['blogUser'];
    getPostPrevNextUrl += "&blogid=" + str(blogid);
    
    #getPostPrevNextUrl += "&nextnum=5";
    getPostPrevNextUrl += "&nextnum=1";
    
    #getPostPrevNextUrl += "&prevnum=5";
    getPostPrevNextUrl += "&prevnum=1";
    
    #getPostPrevNextUrl += "&category=";
    getPostPrevNextUrl += "&sorttype=0";
    #getPostPrevNextUrl += "&r=" + str(random.random());
    #getPostPrevNextUrl += "&g_tk=5381";
    #getPostPrevNextUrl += "&ref=qzone";        
        
    logging.debug("getPostPrevNextUrl=%s", getPostPrevNextUrl);
    
    return getPostPrevNextUrl;

    
#------------------------------------------------------------------------------
# extract blogid from get post info url
# eg: extract 1321000398 from http://xxx.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=1083902439&blogid=1321000398&v6=1
def extractBlogidFromGetPostInfoUrl(getPostInfoUrl) :
    extractedBlogid = 0;
    #foundBlogid = re.search("http://b11\.cnc\.qzone\.qq\.com/cgi-bin/blognew/blog_output_data\?uin=\d+.*?&blogid=(?P<blogid>\d+).*?", getPostInfoUrl);
    foundBlogid = re.search("http://\w+?\.cnc\.qzone\.qq\.com/cgi-bin/blognew/blog_output_data\?uin=\d+.*?&blogid=(?P<blogid>\d+).*?", getPostInfoUrl);
    if(foundBlogid) :
        extractedBlogid = foundBlogid.group("blogid");
        extractedBlogid = int(extractedBlogid);
    else :
        logging.error("Can't extract blogid(post id) from input get post info url %s", getPostInfoUrl);
    return extractedBlogid;

#------------------------------------------------------------------------------
# generate post permanent link from post's blogid
# eg: 1321000398 -> http://user.qzone.qq.com/1083902439/blog/1321000398
# in which 1083902439 is blogUser
# Note:
# here generated (this kind of) perma link:
# http://user.qzone.qq.com/1083902439/blog/1321000398
# return html not contain post info !!!
# -> genGetPostInfoUrl can return post info 
def genPostPermaLink(postBlogId) :
    postPermaLink = "";
        
    #gVal['blogEntryUrl']= http://622007179.qzone.qq.com
    #postPermaLink = gVal['blogEntryUrl'] + "/" + str(postBlogId);
    
    #http://user.qzone.qq.com/622007179/blog/1
    postPermaLink = gConst['spaceDomain'] + "/" + gVal['blogUser'] + "/blog/" + str(postBlogId);
    
    logging.debug("from blogid=%d generated postPermaLink=%s", postBlogId, postPermaLink);
    
    return postPermaLink;

#------------------------------------------------------------------------------
# extract blogid from permanent link
# eg:
# (1) 1321000398 from http://user.qzone.qq.com/1083902439/blog/1321000398
#                     http://user.qzone.qq.com/1083902439/blog/1321000398/
#     1307491670 from http://user.qzone.qq.com/815920900/blog/1307491670#!app=2&pos=1307491670
# (2) 1333268691 from http://blog.qq.com/qzone/622007179/1333268691.htm
# (3) 0          from http://622007179.qzone.qq.com/0
def extractBlogidFromPermaLink(permaLink) :
    extractedBlogid = 0;

    foundBlogid  = re.search("http://user\.qzone\.qq\.com/\d+/blog/(?P<blogid>\d+)/?#?!?", permaLink);
    foundBlogid2 = re.search("http://blog\.qq\.com/qzone/\d+/(?P<blogid>\d+).htm", permaLink);
    foundBlogid3 = re.search("http://\d+\.qzone\.qq\.com/(?P<blogid>\d+)/?", permaLink);
    # print "foundBlogid=",foundBlogid;
    # print "foundBlogid2=",foundBlogid2;
    # print "foundBlogid3=",foundBlogid3;

    found = None;
    if(foundBlogid) :
        found = foundBlogid;
    elif (foundBlogid2):
        found = foundBlogid2;
    elif (foundBlogid3):
        found = foundBlogid3;
    else :
        logging.error("Can't extract blogid(post id) from input permanent link %s", permaLink);
    
    if(found) :
        extractedBlogid = found.group("blogid");
        extractedBlogid = int(extractedBlogid);
        logging.debug("From perma link %s extract out blogid=%d", permaLink, extractedBlogid);

    return extractedBlogid;
        
#------------------------------------------------------------------------------
# find the first permanent link = url of the earliset published blog item
def find1stPermalink():
    (isFound, retInfo) = (False, "Unknown error!");
    
    try:
        earliestYear = 2005; 
        # 腾讯最早成立年份大概是1998年11月：http://www.tencent.com/zh-cn/index.shtml
        # QQ空间最早大概是2005年4月份：http://www.tianya.cn/publicforum/content/funinfo/1/1058230.shtml
        stillContainPost = True;
        yearToCheck = earliestYear;
        while stillContainPost:
            (containPost, earliestMonth, postNumInMonth) = isYearContainPost(yearToCheck);
            if(containPost) :
                # found the first year that has contain the earliest post
                stillContainPost = False;
            else :
                # continue to check next year
                yearToCheck += 1;
        
        firstContainPostYear = yearToCheck;
        if(earliestMonth == 12):
            nextYear = firstContainPostYear + 1;
            nextMonth = 1;
        else :
            nextYear = firstContainPostYear;
            nextMonth = earliestMonth + 1;

        logging.debug("first contain post year and month: %04d-%02d", firstContainPostYear, earliestMonth);
        logging.debug("next               year and month: %04d-%02d", nextYear, nextMonth);
        
        startTimeStr = "%04d-%02d-01 00:00"%(firstContainPostYear,earliestMonth);
        endTimeStr = "%04d-%02d-01 00:00"%(nextYear,nextMonth);
        logging.debug("generated time string: start=%s, end=%s", startTimeStr, endTimeStr);
        
        #startTime = datetime.datetime(firstContainPostYear, earliestMonth, 1);
        startTime = datetime.strptime(startTimeStr, "%Y-%m-%d %H:%M");
        endTime = datetime.strptime(endTimeStr, "%Y-%m-%d %H:%M");
        
        # after found 2006-06 has post, then :
        #http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_titlelist2?uin=84483423&verbose=0&catehex=&pos=0&num=15&sorttype=0&v=1&maxlen=68&starttime=1149091200&endtime=1151683200&bdm=b.cnc.qzone.qq.com&rand=0.14919551610282206&g_tk=5381&cate=&ref=qzone&v6=1
        #starttime: 1149091200 -> 2006-06-01 00:00:00
        #endtime  : 1151683200 -> 2006-07-01 00:00:00

        postList = getPostWithinPeriod(startTime, endTime, postNumInMonth);
        if(postList) :
            # get last one, is the earliest one
            lastPostDict = postList[-1];
            
            # {"blogid":1321000398,
            # "type":0,
            # "pubtime":"2011-11-11 16:33",
            # "replytime":1324646397,
            # "replynum":0,
            # "cate":"个人日记",
            # "catehex":"b8f6c8cbc8d5bcc7",
            # "title":"下页：空间进一次变一次做法",
            # "effect":8389120,
            # "effect2":524294,
            # "ar":0,
            # "block":0,
            # "inproc":false,
            # "appeal":0}
            earliestPostBlogId = lastPostDict['blogid'];
            logging.debug("found earliest post blogId=%d", earliestPostBlogId);
            
            isFound = True;
            # return first perma link
            retInfo = genPostPermaLink(earliestPostBlogId);
    except:
        (isFound, retInfo) = (False, "Unknown error!");
    
    return (isFound, retInfo);

#------------------------------------------------------------------------------
# exract post info dict from return html, which contain g_oBlogData and 
def extractPosInfoDict(respHtml):
    postInfoDict = {};


        # //日志信息内容
        # var g_oBlogData =  
# {"data":{
# "blogid":1321000398,
# "voteids":0,
# "pubtime":1321000398,
# "replynum":0,
# "category":"个人日记",
# "tag":"",
# "title":"下页：空间进一次变一次做法",
# "effect":8389120,
# "effect2":524294,
# "exblogtype":0,
# "sus_flag":false,
# "friendrelation":[],
# "lp_type":0,
# "lp_id":26741,
# "lp_style":101057280,
# "lp_flag":0,
# "orguin":1083902439,
# "orgblogid":1321000398,
# "ip":235433486,
# "mention_uins":[ ],
# "attach":[],
# "replylist":[]
# }}
# ;

        # g_oBlogData.data.cgiContent = '<div class=\"blog_details_20110920\"><div><font color=\"#00ff00\">&lt;% <br  />randomize <br  />Num=(int(rnd()*6)+1) <br  />Select Case Num <br  />case 1 response.redirect(\"你自己的图片地址\") <br  />case 2 response.redirect(\"你自己的图片地址\") <br  />case 3 response.redirect(\"你自己的图片地址\") <br  />case 4 response.redirect(\"你自己的图片地址\") <br  />case 5 response.redirect(\"你自己的图片地址\")<br  />case else response.redirect(\"你自己的图片地址\") <br  />end select <br  />\'response.write num <br  />%&gt; </font><br  />有什么不懂加<font color=\"#000000\">QQ1083902439</font> </div></div>';
        # //
        
        # var g_default_no_comment=0;

        # include comments:
		# var g_oBlogData =  
# {"data":{
# "blogid":1321609592,
# "voteids":0,
# "pubtime":1321609592,
# "replynum":3,
# "category":"软件下载区",
# "tag":"非主流图片|非主流闪图|ps教程|视频教程|粒子",
# "title":"下页→封爱制作空间专业软件‖【下载】",
# "effect":512,
# "effect2":524294,
# "exblogtype":0,
# "sus_flag":false,
# "friendrelation":[],
# "lp_type":0,
# "lp_id":0,
# "lp_style":0,
# "lp_flag":0,
# "orguin":1083902439,
# "orgblogid":1321609592,
# "ip":235433486,
# "mention_uins":[ ],
# "attach":[],
# "replylist":[{"replyid":1,
# "replytime":1326363116,
# "replyeffect":0,
# "replyautograph":"",
# "replycontent":" \n[ft=,2,]......[/ft] ",
# "ismyreply":0,
# "capacity":4963,
# "replyuin":739258064,
# "replynick":"心锁囚徒钥匙放在谁那里つ ",
# "responsecontent":[ ]},
# {"replyid":2,
# "replytime":1332586785,
# "replyeffect":0,
# "replyautograph":"",
# "replycontent":"可以教教我吗？ ",
# "ismyreply":0,
# "capacity":4983,
# "replyuin":781794203,
# "replynick":"_闭眼呼吸ヽ ",
# "responsecontent":[ ]},
# {"replyid":3,
# "replytime":1333200443,
# "replyeffect":0,
# "replyautograph":"",
# "replycontent":"ffffffffffff ",
# "ismyreply":0,
# "capacity":4972,
# "replyuin":734354494,
# "replynick":"ゞ莪哋圉湢呮洧沵给哋孒の ",
# "responsecontent":[ ]}]
# }}
# ;
    #logging.debug("before extract post info, input respHtml: \n%s", respHtml);
    
    #blogDataPat = r'var\s+g_oBlogData\s+=.+?(?P<dataJsonStr>\{"data":\{.+?\}\}).+?;'; 
    # in above :
    # \}\}.+?;
    # some time the content contains '}}' will cause the found string is only part of the whole g_oBlogData !!!
    # so follow use 
    # \}\}\s+;
    blogDataPat = r'var\s+g_oBlogData\s+=.+?(?P<dataJsonStr>\{"data":\{.+?\}\})\s+;';
    blogDataPat += r".+g_oBlogData\.data\.cgiContent\s+?=\s+?'(?P<cgiContent>.+?)';";
    foundBlogData = re.search(blogDataPat, respHtml, re.S);
    logging.debug("foundBlogData=%s", foundBlogData);
    if(foundBlogData) :
        dataJsonStr = foundBlogData.group("dataJsonStr");
        postInfoDict = parseDataStrToInfoDict(dataJsonStr);
        if(postInfoDict) :
            cgiContent = foundBlogData.group("cgiContent");
            cgiContentUni = cgiContent.decode("GB18030");
            postInfoDict['cgiContent'] = cgiContentUni;

        debugStr = "";
        for key in postInfoDict :
            debugStr += "[%s]=%s\n"%(key, postInfoDict[key]);
        #logging.debug("extracted post info dict:\n%s", debugStr);
    
    return postInfoDict;

#------------------------------------------------------------------------------
# store post info for latter use
def storePostInfo(postInfoDict):
    blogid = postInfoDict['blogid'];
    if(blogid not in gVal['extractedPostInfo']) :
        gVal['extractedPostInfo'][blogid] = postInfoDict;
        logging.debug("added blogid=%d post info into gVal['extractedPostInfo'].", blogid);
    else :
        logging.debug("blogid=%d post info has existed in gVal['extractedPostInfo'], so not need store it here", blogid);
    return;

#------------------------------------------------------------------------------
# get post info dict from post's blogid
def getPostInfoDictFromBlogid(blogid, blogOutputDataServer):
    postInfoDict = {};
    getPostInfoUrl = genGetPostInfoUrl(blogid, blogOutputDataServer);
    try :
        logging.debug("Now will open %s", getPostInfoUrl)
        respHtml = crifanLib.getUrlRespHtml(getPostInfoUrl);
        logging.debug("get resp html OK for %s", getPostInfoUrl);
        #logging.debug("in get post info, blogOutputDataServer=%s, blogid=%d return html: \n%s", blogOutputDataServer, blogid, respHtml);
        postInfoDict = extractPosInfoDict(respHtml);
    except :
        logging.error("Can't get post info dict from blogid %d", blogid);
    return postInfoDict;

#------------------------------------------------------------------------------
# get post info dict from url
# Note: current url means perma link
def getPostInfoDictFromUrl(url):
    logging.debug("now will get post info from url %s", url);
    
    # extract blogid from url(perma link)
    blogid = extractBlogidFromPermaLink(url);

    if(blogid in gVal['extractedPostInfo']) :
        # use post info we already got
        logging.debug("%d in gVal['extractedPostInfo']", blogid);
        postInfoDict = gVal['extractedPostInfo'][blogid];
    else :
        logging.debug("%d not in gVal['extractedPostInfo']", blogid);
        # get post info from blogid
        for blogOutputDataServer in gConst['qqServer']['blog_output_data'] :
            postInfoDict = getPostInfoDictFromBlogid(blogid, blogOutputDataServer);
            if(postInfoDict) :
                # got valid post info, so quit now
                logging.debug("Got valid post info dict from blog_output_data's server=%s", blogOutputDataServer);
            else :
                # not got valid post info, then try next server
                logging.debug("Can not got valid post info dict from blog_output_data's server=%s", blogOutputDataServer);
                continue;

        # store/update postInfoDict if necessary
        storePostInfo(postInfoDict);
    
    return postInfoDict;

#------------------------------------------------------------------------------
# extract post title
def extractTitle(url, html):
    titleUni = "";

    try :
        #logging.debug("extractTitle: input html: \n%s", html);
        
        # for QQ space, this html is un-useful
        postInfoDict = getPostInfoDictFromUrl(url);
        
        if(postInfoDict) :
            titleUni = postInfoDict['title'];
        else :
            logging.debug("Can't get post title for returned empty post info dict");
    except : 
        titleUni = "";

    return titleUni;

#------------------------------------------------------------------------------
# find next permanent link of current post
def findNextPermaLink(url, html) :
    nextLinkStr = '';
        
    try :
        nextPostTitle = "";
        
        blogid = extractBlogidFromPermaLink(url);

        getPostPrevNextUrl = genGetPostPrevNextUrl(blogid);
        respCallbackStr = crifanLib.getUrlRespHtml(getPostPrevNextUrl);
        logging.debug("findNextPermaLink: getPostPrevNextUrl respCallbackStr: \n%s", respCallbackStr);
        
        # _Callback(
        # {"data":{
        # "thisblog":1321000398,
        # "prev_list":[{"blogid":1321609592,
        # "title":"下页→封爱制作空间专业软件‖【下载】"},
        # {"blogid":1321610165,
        # "title":"下页：封爱教做QQ真人秀...下面不要红钻qq秀"},
        # {"blogid":1327667644,
        # "title":"下页：封爱〖荣誉接单〗中--非黄钻上传全屏皮肤设计--联系QQ1083902439==="},
        # {"blogid":1330699875,
        # "title":"小壕写给来访本空间的每一位好友-----来访必看"},
        # {"blogid":1333289320,
        # "title":"下页‖〖小壕〗唰钻业务介绍====来访必看==加小壕QQ1083902439"}],
        # "next_list":[]
        # }}
        # );
        
        # find the first one in prev_list if exist
        # Note: the newer (published post) than current, is the first on in prev_list !!!
        retInfoDict = callbackStrToInfoDict(respCallbackStr);
        if(retInfoDict) :
            prevList = [];
            if("prev_list" in retInfoDict) :
                prevList = retInfoDict['prev_list'];
                logging.debug("len(prevList)=%d", len(prevList));
                if(prevList):
                    #{"blogid":1321609592,
                    #"title":"下页→封爱制作空间专业软件‖【下载】"}
                    nextBlogid = prevList[0]['blogid'];
                    nextLinkStr = genPostPermaLink(nextBlogid);
                    nextPostTitle = prevList[0]['title'];

            # nextList = [];
            # if("next_list" in retInfoDict) :
                # nextList = retInfoDict['next_list'];
                # print "nextList=",nextList;

        logging.debug("Found next permanent link=%s, title=%s", nextLinkStr, nextPostTitle);
    except :
        nextLinkStr = '';
        logging.debug("Can not find next permanent link.");

    return nextLinkStr;

#------------------------------------------------------------------------------
# extract datetime fom url, html
def extractDatetime(url, html) :
    datetimeStr = '';
    try :
        postInfoDict = getPostInfoDictFromUrl(url);

        if(postInfoDict) :
            #"pubtime":1321000398,
            publishTimestamp = postInfoDict['pubtime'];
            logging.debug("publishTimestamp=%s", publishTimestamp);
            pubDatetime = crifanLib.timestampToDatetime(publishTimestamp);
            logging.debug("pubDatetime=%s", pubDatetime);
            datetimeStr = pubDatetime.strftime(gConst['datetimePattern']);
    except :
        datetimeStr = "";
        
    return datetimeStr;

#------------------------------------------------------------------------------
# extract post content
def extractContent(url, html) :
    contentUni = '';
    try :
        postInfoDict = getPostInfoDictFromUrl(url);
        if(postInfoDict) :
            contentUni = postInfoDict['cgiContent'];

        #logging.debug("extracted url=%s post content:\n%s", url, contentUni);
    except :
        contentUni = '';

    return contentUni;

#------------------------------------------------------------------------------
# extract post category
def extractCategory(url, html) :
    catUni = '';
    try :
        postInfoDict = getPostInfoDictFromUrl(url);
        
        if(postInfoDict) :
            categoryUni = postInfoDict['category'];
            logging.debug("categoryUni=%s", categoryUni);
            catUni = unicode(categoryUni);
    except :
        catUni = "";

    return catUni;

#------------------------------------------------------------------------------
# extract post tags
def extractTags(url, html) :
    tagList = [];
    try :
        postInfoDict = getPostInfoDictFromUrl(url);
        
        if(postInfoDict) :
            tagsStrUni = postInfoDict['tag'];
            logging.debug("tagsStrUni=%s", tagsStrUni);
            if(tagsStrUni):
                tagList = tagsStrUni.split("|");
    except :
        tagList = [];

    return tagList;

#------------------------------------------------------------------------------
# fill source comments dictionary into destination comments dictionary
def fillComments(destCmtDict, srcCmtDict):

# "replylist":[{"replyid":1,
# "replytime":1318227910,
# "replyeffect":4194336,
# "replyautograph":"",
# "replycontent":"[ft=,4,仿宋_GB2312]兄弟·····你可能不要疾世愤俗了····[/ft] ",
# "ismyreply":0,
# "capacity":4761,
# "replyuin":1102550638,
# "replynick":"芸芸众生之冰封世界 ",
# "responsecontent":[{"uin":"84483423","nick":"/wx礼貌 ","time":1333439231,"effect":0,"content":"[em]e128[/em] 尽量吧 [em]e113[/em]@{uin:1102550638,nick:芸芸众生之冰封世界}  "} ]},
# {"replyid":2,
# "replytime":1325505703,
# "replyeffect":4194304,
# "replyautograph":"",
# "replycontent":"[url=http://www.hlg315.com][img,177,153]http://b80.photo.store.qq.com/psb?/719a50cc-db96-4d30-a30c-7e382e97a952/7HUY*kwJGCMKRskqYWv4jgGNDqT6mXRyarwdBZWeR4Q!/b/YbJfwS8MigAAYimTsC.sigAA [/img][/url] ",
# "ismyreply":0,
# "capacity":4800,
# "replyuin":2622829178,
# "replynick":"欢乐谷性用品 ",
# "responsecontent":[ ]},
# {"replyid":3,
# "replytime":1325506832,
# "replyeffect":4194304,
# "replyautograph":"",
# "replycontent":"[url=http://www.hlg315.com][img,177,153]http://b80.photo.store.qq.com/psb?/719a50cc-db96-4d30-a30c-7e382e97a952/7HUY*kwJGCMKRskqYWv4jgGNDqT6mXRyarwdBZWeR4Q!/b/YbJfwS8MigAAYimTsC.sigAA [/img][/url] ",
# "ismyreply":0,
# "capacity":4800,
# "replyuin":2358816193,
# "replynick":"欢乐谷性用品 ",
# "responsecontent":[ ]},
# {"replyid":4,
# "replytime":1327506817,
# "replyeffect":0,
# "replyautograph":"",
# "replycontent":"如果我是玫瑰我将给你芬芳，如果我是太阳我将给你阳光；如果我是钻石我将给你永恒；如果我是你的爱我将给你我的全部。\n\n ",
# "ismyreply":0,
# "capacity":4886,
# "replyuin":2469148786,
# "replynick":"长夜难眠 ",
# "responsecontent":[ ]}]

    qqNumStr = str(srcCmtDict['replyuin']);

    if(srcCmtDict['replyid'] - gVal['debugLastId'] > 1) :
        # such as from 78 to 80, jump over 79
        logging.debug("just record some jumpped comment id: srcCmtDict['replyid']=%d, lastId=%d", srcCmtDict['replyid'], gVal['debugLastId']);

    destCmtDict['id'] = srcCmtDict['replyid'];
    logging.debug("--- comment[%d] ---", destCmtDict['id']);
    gVal['debugLastId'] = destCmtDict['id'];
    
    #logging.debug("srcCmtDict=%s", srcCmtDict);
    
    #Normal one:
    # {"replyid":2,
    # "replytime":1332944481,
    # "replyeffect":0,
    # "replyautograph":"",
    # "replycontent":"好美！ ",
    # "ismyreply":0,
    # "capacity":4990,
    # "replyuin":421380584,
    # "replynick":"故乡的原风景 ",
    # "responsecontent":[ ]}
    if("replynick" in srcCmtDict) :
        destCmtDict['author'] = srcCmtDict['replynick'];
    elif ("nickname" in srcCmtDict) :
        # http://user.qzone.qq.com/417846901/blog/1332944095 has special one:
        #{"replyid":1,
        # "replytime":1332944343,
        # "replyeffect":524288,
        # "replyautograph":"",
        # "replycontent":"梦里去过了！ ",
        # "ismyreply":0,
        # "capacity":4990,
        # "replyuin":"03037c9a5520fe5775a202f59858ec2e5dc9c1d73e346b3d",
        # "nickname":"慕寒",
        # "responsecontent":[ ]}
        destCmtDict['author'] = srcCmtDict['nickname'];
    
    #print "destCmtDict['author']=",destCmtDict['author'];
    
    qqMailAddr = qqNumStr + "@qq.com";
    destCmtDict['author_email'] = qqMailAddr;
    
    qqSpaceUrl = gConst['spaceDomain'] + "/" + qqNumStr;
    destCmtDict['author_url'] = qqSpaceUrl;
        
    localReplyTime = crifanLib.timestampToDatetime(srcCmtDict['replytime']);
    gmtReplyTime = crifanLib.convertLocalToGmt(localReplyTime);
    #print "localReplyTime=",localReplyTime;
    #print "gmtReplyTime=",gmtReplyTime;
    destCmtDict['date'] = localReplyTime.strftime("%Y-%m-%d %H:%M:%S");
    destCmtDict['date_gmt'] = gmtReplyTime.strftime("%Y-%m-%d %H:%M:%S");
    
    #print "destCmtDict['date']=",destCmtDict['date'];
    
    destCmtDict['content'] = srcCmtDict['replycontent'];
    
    destCmtDict['author_IP'] = "";
    destCmtDict['approved'] = 1;
    destCmtDict['type'] = '';
    destCmtDict['parent'] = 0;
    destCmtDict['user_id'] = 0;
    
    logging.debug("author       =%s", destCmtDict['author']);
    logging.debug("author_url   =%s", destCmtDict['author_url']);
    logging.debug("date         =%s", destCmtDict['date']);
    logging.debug("date_gmt     =%s", destCmtDict['date_gmt']);
    logging.debug("content      =%s", destCmtDict['content']);
    
    #print "fill comments %d OK"%(destCmtDict['id']);
    
    return destCmtDict;
    
#------------------------------------------------------------------------------
# fill sub comment
def fillSubComment(destCmtDict, srcRespCntDict, parentId, curSubCmtId):
    #"responsecontent":[{"uin":"84483423","nick":"/wx礼貌 ","time":1333439231,"effect":0,"content":"[em]e128[/em] 尽量吧 [em]e113[/em]@{uin:1102550638,nick:芸芸众生之冰封世界}  "} ]},
    
    #print "in fill sub comments";
    qqNumStr = str(srcRespCntDict['uin']);
    #print "qqNumStr=",qqNumStr;
    
    destCmtDict['id'] = curSubCmtId;
    logging.debug("in fill sub comments: --- comment[%d] ---", destCmtDict['id']);
    
    destCmtDict['author'] = srcRespCntDict['nick'];
    #print "destCmtDict['author']=",destCmtDict['author'];
    
    qqMailAddr = qqNumStr + "@qq.com";
    destCmtDict['author_email'] = qqMailAddr;

    qqSpaceUrl = gConst['spaceDomain'] + "/" + qqNumStr;
    destCmtDict['author_url'] = qqSpaceUrl;

    localRepTime = crifanLib.timestampToDatetime(srcRespCntDict['time']);
    gmtRepTime = crifanLib.convertLocalToGmt(localRepTime);
    #print "localRepTime=",localRepTime;
    #print "gmtRepTime=",gmtRepTime;
    destCmtDict['date'] = localRepTime.strftime("%Y-%m-%d %H:%M:%S");
    destCmtDict['date_gmt'] = gmtRepTime.strftime("%Y-%m-%d %H:%M:%S");
    
    #print "destCmtDict['date']=",destCmtDict['date'];
    
    destCmtDict['content'] = srcRespCntDict['content'];
    
    destCmtDict['parent'] = parentId;
    
    destCmtDict['author_IP'] = "";
    destCmtDict['approved'] = 1;
    destCmtDict['type'] = '';
    destCmtDict['user_id'] = 0;
    
    logging.debug("author       =%s", destCmtDict['author']);
    logging.debug("author_url   =%s", destCmtDict['author_url']);
    logging.debug("date         =%s", destCmtDict['date']);
    logging.debug("date_gmt     =%s", destCmtDict['date_gmt']);
    logging.debug("content      =%s", destCmtDict['content']);
    
    #print "fill sub comments %d OK"%(destCmtDict['id']);
    
    return ;

#------------------------------------------------------------------------------
# parse all replylist into 
def parseAllCommentsList(allReplyList, parsedCommentsList):
    # current total main comment number, used as later start number/id of sub comments
    mainCmtNum = len(allReplyList);
    
    for (cmtIdx, srcCmtDict) in enumerate(allReplyList) :
        destCmtDict = {};
        fillComments(destCmtDict, srcCmtDict);
        parsedCommentsList.append(destCmtDict);
        
        respSubCmtList = srcCmtDict['responsecontent'];
        if(respSubCmtList) :
            subCmtLen = len(respSubCmtList);
            logging.debug("comment id=%d contain %d sub comments", srcCmtDict['replyid'], subCmtLen);
            curSubCmtId = mainCmtNum + 1;
            
            for eachSubCmtDict in respSubCmtList :
                destSubCmtDict = {};
                curMainCmtId = srcCmtDict['replyid'];
                logging.debug("curMainCmtId=%d", curMainCmtId);
                fillSubComment(destSubCmtDict, eachSubCmtDict, curMainCmtId, curSubCmtId);
                parsedCommentsList.append(destSubCmtDict);
                curSubCmtId += 1;
    return;

#------------------------------------------------------------------------------
# get comments replylist
def getCmtReplyList(blogid, startIdx, getNum) :
    gotReplyList = [];

    #http://b1.qzone.qq.com/cgi-bin/blognew/blog_get_data?uin=622007179&num=15&blogid=1193481027&from=15&type=1&r=0.17835291538186426&g_tk=5381&ref=qzone

    #gen get comment url
    getCmtUrl = "http://b1.qzone.qq.com/cgi-bin/blognew/blog_get_data";
    getCmtUrl += "?uin=" + gVal['blogUser'];
    getCmtUrl += "&num=" + str(getNum);
    getCmtUrl += "&blogid=" + str(blogid);
    getCmtUrl += "&from=" + str(startIdx);
    getCmtUrl += "&type=1";
    getCmtUrl += "&r=" + str(random.random());
    getCmtUrl += "&g_tk=5381";
    getCmtUrl += "&ref=qzone";

    respCallbackStr = crifanLib.getUrlRespHtml(getCmtUrl);
    #logging.debug("get comment ret callback str:\n%s", respCallbackStr);

    postInfoDict = callbackStrToInfoDict(respCallbackStr);
    gotReplyList = postInfoDict['replylist'];
    
    return gotReplyList;

#------------------------------------------------------------------------------
# fetch and parse comments 
# return the parsed dict value
def fetchAndParseComments(url, html):
    parsedCommentsList = [];
    
    try :
        blogid = extractBlogidFromPermaLink(url);

        # seems here got replylist from extractTitle extracted postInfoDict
        # only contain the first page = 15 comments, 
        # -> not include all comments if actually contain more than 15 comments
        # so here should get all
        postInfoDict = getPostInfoDictFromUrl(url);

        alreadyGotCmtNum = 0;
        allReplyList = [];
        if(postInfoDict) :
            alreadyGotReplyList = postInfoDict['replylist'];
            #print "alreadyGotReplyList=",alreadyGotReplyList;
            alreadyGotCmtNum = len(alreadyGotReplyList);
            #print "alreadyGotCmtNum=",alreadyGotCmtNum;
            #allReplyList.add(alreadyGotReplyList); # error
            #allReplyList.append(alreadyGotReplyList); # not work
            allReplyList.extend(alreadyGotReplyList);
            #print "allReplyList=",allReplyList;

        totalCmtNum = postInfoDict['replynum'];
        remainCmtNum = totalCmtNum - alreadyGotCmtNum;
        logging.debug("totalCmtNum=%d, alreadyGotCmtNum=%d, remainCmtNum=%d", totalCmtNum, alreadyGotCmtNum, remainCmtNum);
        
        if(remainCmtNum > 0) :
            # if has more comments, then fetch them
            startIdx = alreadyGotCmtNum;
            getNum = remainCmtNum;
            #getNum = 60; # max allow once get 60, if >60, only return 15 comments
            needGetMore = True;
            
            while (needGetMore) :
                gotReplyList = getCmtReplyList(blogid, startIdx, getNum);
                gotReplyListLen = len(gotReplyList);
                logging.debug("gotReplyListLen=%d", gotReplyListLen);
                if(gotReplyListLen > 0) :
                    allReplyList.extend(gotReplyList);

                    if(gotReplyListLen < getNum) :
                        stillRemainNum = getNum - gotReplyListLen;
                        
                        startIdx = startIdx + gotReplyListLen;
                        getNum = getNum - gotReplyListLen;
                        logging.debug("still need get comment: startIdx=%d, getNum=%d", startIdx, getNum);
                    else :
                        needGetMore = False;
                        logging.debug("Now has got all relylist");
                else:
                    # means can't get more comments
                    # -> maybe replylist contain invalid char
                    # -> can't decode and do json.loads
                    # -> so remove it in parseDataStrToInfoDict
                    # -> got empty comment list here
                    # -> just quit out here
                    needGetMore = False;
                    logging.debug("    Expected get more comment:  startIdx=%d, getNum=%d, but got empty comment list", startIdx, getNum);
                    logging.warning("    Process comments failed during %d-%d comments", startIdx, startIdx+getNum);

        logging.debug("len(allReplyList)=%d", len(allReplyList));

        parseAllCommentsList(allReplyList, parsedCommentsList);
    except :
        logging.warning("Error while fetch and parse comment for %s", url);

    logging.debug("len(parsedCommentsList)=%d", len(parsedCommentsList));
    
    return parsedCommentsList;

#------------------------------------------------------------------------------
# extract blog title and description
def extractBlogTitAndDesc(blogEntryUrl) :
    (blogTitle, blogDescription) = ("", "");

    logging.debug("open %s to extract blog title and description", blogEntryUrl);
    
    respHtml = crifanLib.getUrlRespHtml(blogEntryUrl);
    
    # Note: http://user.qzone.qq.com/84483423/blog/ return html use UTF-8
    soup = BeautifulSoup(respHtml, fromEncoding="UTF-8"); #<meta charset="UTF-8" />
    #soup = BeautifulSoup(respHtml, fromEncoding="GB18030");
    
    try:
        # <title>crifan [http://84483423.qzone.qq.com]</title>
        # <meta name="keywords" content="QQ空间,黄钻,免费装扮,开心农场,QQ农场,QQ牧场" />
        # <meta name="description" content="http://www.crifan.com" />

        blogTitle = soup.title;
        blogTitle = blogTitle.string;
        blogTitle = unicode(blogTitle);
        
        foundDesc = soup.find(attrs={"name":"description"});
        if(foundDesc):
            descStr = foundDesc['content'];
            blogDescription = unicode(descStr);
    except:
        (blogTitle, blogDescription) = ("", "");
    
    return (blogTitle, blogDescription);

#------------------------------------------------------------------------------
# possible date format
def parseDatetimeStrToLocalTime(datetimeStr):
    parsedLocalTime = datetime.strptime(datetimeStr, gConst['datetimePattern']); # here is GMT+8 local time
    logging.debug("Converted datetime string %s to datetime value %s", datetimeStr, parsedLocalTime);
    return parsedLocalTime;

#------------------------------------------------------------------------------
# filter the QQ picture filename
def filterPicFilename(filename):
    filteredFilename = filename;
    
    # get YXpVdjeYnQAAYkXUdzdamAAAb0XUdzdamAAA from 
    #V10aRqIa3iFNQr/B5Xxzpeuf*GmjW9VViM6qQ1lpZHBMGwGYGIwNWmdwag!/b/YXpVdjeYnQAAYkXUdzdamAAAb0XUdzdamAAA
    filteredFilename = filteredFilename.split("/")[-1];
    #print "filteredFilename=",filteredFilename;

    # handle special patter first
    # (1) remove &amp;a=56&amp;b=18 in 
    #YcGb*SRcZAAAYjGD8iftWwAA&amp;a=62&amp;b=67
    #rurl4_b=413367b238dfafae6ef...............0d757e7e7d0bd6568f641d&amp;a=74&amp;b=74
    filteredFilename = re.sub(r"&amp;a=\d+&amp;b=\d+", "", filteredFilename);
    #print "filteredFilename=",filteredFilename;
    # (2) remove rurl4_b= in rurl4_b=fe5e6bf11e.............16c894ddfaea7&amp;a=74&amp;b=74
    # rurl2= in rurl2=3637dbbeb..........f3750968bf355760d7b6
    filteredFilename = re.sub(r"rurl\d+[_\w]*?=", "", filteredFilename);
    #print "filteredFilename=",filteredFilename;
    
    # remove non-word char in  YSb*EjvlPwAAYgALFjsxPgAA
    filteredFilename = re.sub(r"[^\w]", "", filteredFilename);
    #print "filteredFilename=",filteredFilename;
    # only got short one if it is 413367b238dfafae6efc6efabc49a7cf2fa4fee76c9ee4c3b75dec7c07e47e8504001ff861319b27f1c6510accdf52d65e585f785b93f1af0b954fb976f4b070822ecf6f593b5ad913d2072ba8771546e9c553cb
    filteredFilename = filteredFilename[-20:];
    #print "filteredFilename=",filteredFilename;
    
    return filteredFilename;
    
#------------------------------------------------------------------------------
# get the found pic info after re.search
# foundPic is MatchObject
def getFoundPicInfo(foundPic):
    # here should corresponding to singlePicUrlPat in processPicCfgDict
    picUrl  = foundPic.group(0);
    #print "picUrl=",picUrl;
    fd1     = foundPic.group("fd1"); # for QQ pic, is b74/b67/b76/...
    logging.debug("fd1=%s", fd1);
    
    filename= foundPic.group("filename");
    
    logging.debug("picture filename=%s", filename);
    
    filteredFilename = filterPicFilename(filename);
    logging.debug("filtered pic filename=%s", filteredFilename);

    #suffix  = foundPic.group("suffix");
    suffix = "";
    #print "suffix=",suffix;
    
    picInfoDict = {
        'isSupportedPic': False,
        'picUrl'        : picUrl,
        #'filename'      : filename,
        'filename'      : filteredFilename,
        'suffix'        : suffix, # empty for sina pic url: http://s14.sinaimg.cn/middle/3d55a9b7g9522d474a84d&690
        'fields'        : 
            {
                'fd1' : fd1,
                #'fd2' : fd2,
                #'fd3' : fd3,
            },
    };
    
    # if match, must be QQ pic
    picInfoDict['isSupportedPic'] = True;

    return picInfoDict;

#------------------------------------------------------------------------------
# generate the file name for other pic
# depend on following picInfoDict definition
def genNewOtherPicName(picInfoDict):
    newOtherPicName = "";
    
    filename = picInfoDict['filename'];
    
    filteredFilename = filterPicFilename(filename);
    
    fd1 = picInfoDict['fields']['fd1'];
    #fd2 = picInfoDict['fields']['fd2'];
    #fd3 = picInfoDict['fields']['fd3'];
    
    #newOtherPicName = fd1 + '_' + fd2 + "_" + filteredFilename;
    newOtherPicName = fd1 + "_" + filteredFilename;
    
    #print "newOtherPicName=",newOtherPicName;

    return newOtherPicName;

#------------------------------------------------------------------------------
# check whether is self blog pic
# depend on following picInfoDict definition
def isSelfBlogPic(picInfoDict):
    isSelfPic = False;

    # currently only support QQ space own pic, so here always True
    isSelfPic = True;

    return isSelfPic;

#------------------------------------------------------------------------------
def getProcessPhotoCfg():
    # possible own site pic link:
    
    #(1)
    #http://user.qzone.qq.com/84483423/blog/1309873770 contain:
    #http://b74.photo.store.qq.com/http_imgload.cgi?/rurl4_b=413367b238dfafae6efc6efabc49a7cf7fc6535d4858bc6a595583a7c590c7ef726230acbb8eed7adf87af87bdfdc7a503f211bedde5ae17a0459888dc94cd8ccb95d150ff972584de0d757e7e7d0bd6568f641d&a=74&b=74
    
    #----------------follow are corresponding html source code ----------------
    #<a href=\"http://b74.photo.store.qq.com/http_imgload.cgi?/rurl4_b=413367b238dfafae6efc6efabc49a7cf7fc6535d4858bc6a595583a7c590c7ef726230acbb8eed7adf87af87bdfdc7a503f211bedde5ae17a0459888dc94cd8ccb95d150ff972584de0d757e7e7d0bd6568f641d&amp;a=74&amp;b=74\" appendurl=\"1\" target=\"_blank\"><img alt=\"图片\" appendurl=\"1\" height=\"513\" src=\"http://b74.photo.store.qq.com/http_imgload.cgi?/rurl4_b=413367b238dfafae6efc6efabc49a7cf7fc6535d4858bc6a595583a7c590c7ef726230acbb8eed7adf87af87bdfdc7a503f211bedde5ae17a0459888dc94cd8ccb95d150ff972584de0d757e7e7d0bd6568f641d&amp;a=74&amp;b=74\" width=\"600\"  /></a>

    #http://user.qzone.qq.com/84483423/blog/1309614373 contain:
    #http://b74.photo.store.qq.com/http_imgload.cgi?/rurl4_b=fe5e6bf11ec39846cccc3e5c078b1d376fc431ac47c8d8a298661ac36252a6a675a92239a2601f308e5f1bd4ee6a79deb4abbeb3acaeff7da4bb12790f4973379dbd8b5fdf9c20b050212365fe016c894ddfaea7&a=74&b=74
    #http://b67.photo.store.qq.com/http_imgload.cgi?/rurl4_b=fe5e6bf11ec39846cccc3e5c078b1d377e55d302abcc69d628e673ac97d074e0fb64d5448613d84201a177c2ec8b63db328d77d2032d13a4bf8fa06b8bb07f73b2b6af5729993dcba4bd09d27e3fe3a48992af19&a=67&b=67
    
    #http://user.qzone.qq.com/84483423/blog/1308931724 contain:
    #http://b76.photo.store.qq.com/http_imgload.cgi?/rurl4_b=413367b238dfafae6efc6efabc49a7cf2fa4fee76c9ee4c3b75dec7c07e47e8504001ff861319b27f1c6510accdf52d65e585f785b93f1af0b954fb976f4b070822ecf6f593b5ad913d2072ba8771546e9c553cb&a=76&b=76
    
    #(2)
    #http://user.qzone.qq.com/622002735/blog/1331890909 contain:
    #http://b84.photo.store.qq.com/psb?/fca1b1fb-a806-4df0-9be1-230f87e73489/mnopK7Slt6bt.jWP7dT*n*X9hfyi5c6Ken.X3NdOHMs!/b/YZskHzIyYQAAYhnLJjKVXgAA
    
    #(3)
    #http://blog.qq.com/qzone/57542962/1332960840.htm contain:
    #http://b99.photo.store.qq.com/psb?/V10ppwxs00XiXU/CL128zkv*n0XyFGkEe3T1Fh6IaDOSmuX8cKEYdSM1VI!/b/YSb*EjvlPwAAYgALFjsxPgAA
    #http://b98.photo.store.qq.com/psb?/V10ppwxs00XiXU/mIRmeiilUbNG52aU3woF5mU23kF920LhGmCryE3Fl8M!/b/YZrveDoZPgAAYlTheDpfPgAA
        
    #(4)
    #84483423 签名档包含：
    #http://sz.photo.store.qq.com/rurl2=3637dbbebbffe2aac2e2b71826d10af965ed050e1f13afdb05c97e4e916c8657bb79a729eb3d7aea881b210b32076649f0e89b961b18b06c7e41846d2f1fb7991d2e68b3f48f09fb15e4f3750968bf355760d7b6
    
    #(5)
    #http://blog.qq.com/qzone/444503967/1332125975.htm contain:
    #http://b67.photo.store.qq.com/psu?/8bd0bdfe-92a6-4950-a9f1-df94885f54b3/tkMRwFhJkon8C2giO2sCXKy82i8zG4.0Dd1ggVF9pzM!/b/YcGb*SRcZAAAYjGD8iftWwAA&amp;a=62&amp;b=67
    
    #(6)
    #http://blog.qq.com/qzone/94371314/1333558347.htm contain:
    #http://b100.photo.store.qq.com/psb?/V12MguqI01wN8j/2lWCO5dvToG63r9Hj*G0.ctM0o6bPCKOLlqu85df3RM!/o/YUeirjtpJAAAYl30ozvcIwAAb83cnTsNJAAA

    # possible othersite pic url:

    picSufChars = crifanLib.getPicSufChars();
    processPicCfgDict = {
        # currently only support QQ Space self blog pic
        
        #'allPicUrlPat'     : r'http://\w+?\.photo\.store\.qq\.com/http_imgload\.cgi\?/rurl4_b=\w+[&amp;b=\d]{0,30}',
        #'singlePicUrlPat'  : r'http://(?P<fd1>\w+?)\.photo\.store\.qq\.com/http_imgload\.cgi\?/rurl4_b=(?P<filename>\w+)[&amp;b=\d]{0,30}',
        
        # 'allPicUrlPat'     : r'http://\w+?\.photo\.store\.qq\.com/[\w\.]+\?//?[\w\*\!\-\.]*rurl4_b=\w+[&amp;b=\d]{0,30}',
        # 'singlePicUrlPat'  : r'http://(?P<fd1>\w+?)\.photo\.store\.qq\.com/http_imgload\.cgi\?/rurl4_b=(?P<filename>\w+)[&amp;b=\d]{0,30}',

        # find all above (1) - (5) type pic
        'allPicUrlPat'     : r'(?!\\")http://\w+.photo\.store\.qq\.com/.*?/?[\w\*\.\!\-&;=^/]+(?=\\")',
        'singlePicUrlPat'  : r'http://(?P<fd1>\w+)\.photo\.store\.qq\.com/.*?/?(?P<filename>[\w\*\.\!\-&;=^/]+)$',
        
        # # not support (4) http://sz.photo.store.qq.com/rurl2=3637dbbeb..............50968bf355760d7b6
        # 'allPicUrlPat'     : r'(?!\\")http://\w+.photo\.store\.qq\.com/.*?/[\w\*\.\!\-&;\=^/^?]+(?=\\")',
        # 'singlePicUrlPat'  : r'http://(?P<fd1>\w+)\.photo\.store\.qq\.com/.*/(?P<filename>[^/]+)$',
        
        'getFoundPicInfo'   : getFoundPicInfo,
        'isSelfBlogPic'     : isSelfBlogPic,
        'genNewOtherPicName': genNewOtherPicName,
    };
    
    return processPicCfgDict;

####### Login Mode ######

#------------------------------------------------------------------------------
# log in Blog
def loginBlog(username, password) :
    loginOk = False;
    
    return loginOk;

#------------------------------------------------------------------------------
# check whether this post is private(self only) or not
def isPrivatePost(url, html) :
    isPrivate = False;

    return isPrivate;

#------------------------------------------------------------------------------
# modify post content
def modifySinglePost(newPostContentUni, infoDict, inputCfg):
    (modifyOk, errInfo) = (False, "Unknown error!");
    (modifyOk, errInfo) = (False, "Not support this function yet!");
    return (modifyOk, errInfo);

#------------------------------------------------------------------------------   
if __name__=="BlogQQ":
    print "Imported: %s,\t%s"%( __name__, __VERSION__);