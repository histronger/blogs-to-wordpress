#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

For BlogsToWordpress, this file contains the functions for Baidu space/blog.

[TODO]
1. add support for friendOnly type post detect

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
from xml.sax import saxutils;
import random;
import json; # New in version 2.6.
import binascii;

#--------------------------------const values-----------------------------------
__VERSION__ = "v1.3";

gConst = {
    'baiduSpaceDomain'  : 'http://hi.baidu.com',
}

#----------------------------------global values--------------------------------
gVal = {
    'blogUser'      : '',   # serial_story
    'quotedBlogUser': '',   # serial%5Fstory
    'blogEntryUrl'  : '',   # http://hi.baidu.com/recommend_music
    'cj'            : None, # cookiejar, to store cookies for login mode
    'spToken'       : '',
}

################################################################################
# Internal baidu space Functions 
################################################################################

def htmlToSoup(html):
    soup = None;
    # Note:
    # (1) baidu and 163 blog all use charset=gbk, but some special blog item:
    # http://chaganhu99.blog.163.com/blog/static/565262662007112245628605/
    # will messy code if use default gbk to decode it, so set GB18030 here to avoid messy code
    # (2) after BeautifulSoup process, output html content already is utf-8 encoded
    soup = BeautifulSoup(html, fromEncoding="GB18030");
    #prettifiedSoup = soup.prettify();
    #logging.debug("Got post html\n---------------\n%s", prettifiedSoup);
    return soup;

#------------------------------------------------------------------------------
# forcely convert some char into %XX, XX is hex value for the char
# eg: recommend_music -> recommend%5Fmusic
def doForceQuote(originStr) :

    quotedStr = '';
    specialList = ['_']; # currently only need to convert the '_'

    for c in originStr :
        if c in specialList :
            cHex = binascii.b2a_hex(c);
            cHexStr = '%' + str(cHex).upper();
            quotedStr += cHexStr;
        else :
            quotedStr += c;

    return quotedStr;


#------------------------------------------------------------------------------
# handle some special condition 
# to makesure the content is valid for following decode processing
def validateCmtContent(cmtContent):
    #logging.debug("[validateCmtContent]input comment content:\n%s", cmtContent)
    validCmtContent = cmtContent;
    
    if validCmtContent : # if not none
        # special cases:

        # 1. end of the comment contains odd number of backslash, eg: 'hello\\\\\'
        # -> here just simplely replace the last backslash with '[backslash]'
        if (validCmtContent[-1] == "\\") :
            validCmtContent = validCmtContent[0:-1];
            validCmtContent += '[backslash]';

    #logging.debug("[validateCmtContent]validated comment content:\n%s", validCmtContent)
    return validCmtContent;

#------------------------------------------------------------------------------
# remove some special char, for which, the wordpress not process it
def filterHtmlTag(cmtContent) :
    filteredComment = cmtContent;

    #(1)
    #from : 谢谢~<img src="http:\/\/img.baidu.com\/hi\/jx\/j_0003.gif">
    #to   : 谢谢~<img src="http://img.baidu.com/hi/jx/j_0003.gif">
    filter = re.compile(r"\\/");
    filteredComment = re.sub(filter, "/", filteredComment);

    return filteredComment;

#------------------------------------------------------------------------------
# fill source comments dictionary into destination comments dictionary
# note all converted filed in dict is Unicode, so no need do decode here !
def fillComments(destCmtDict, srcCmtDict):
    #fill all comment field
    destCmtDict['id'] = srcCmtDict['id'];
    logging.debug("--- comment[%d] ---", destCmtDict['id']);
    
    noCtrlChrUsername = crifanLib.removeCtlChr(srcCmtDict['user_name']);
    destCmtDict['author'] = noCtrlChrUsername;
    destCmtDict['author_email'] = '';

    if srcCmtDict['user_name'] :
        cmturl = 'http://hi.baidu.com/sys/checkuser/' + srcCmtDict['user_name'] + '/1';
    else :
        cmturl = '';
    destCmtDict['author_url'] = saxutils.escape(cmturl);
    destCmtDict['author_IP'] = srcCmtDict['user_ip'];

    epoch = int(srcCmtDict['create_time']);
    localTime = time.localtime(epoch);
    gmtTime = time.gmtime(epoch);
    destCmtDict['date'] = time.strftime("%Y-%m-%d %H:%M:%S", localTime);
    destCmtDict['date_gmt'] = time.strftime("%Y-%m-%d %H:%M:%S", gmtTime);

    # handle some speical condition
    srcCmtDict['content'] = validateCmtContent(srcCmtDict['content']);
    
    cmtContent = srcCmtDict['content'];
    #logging.debug("after decode, coment content:\n%s", cmtContent);
    cmtContent = filterHtmlTag(cmtContent);
    # remove invalid control char in comments content
    cmtContent = crifanLib.removeCtlChr(cmtContent);
    #logging.debug("after filtered, coment content:\n%s", cmtContent);
    destCmtDict['content'] = cmtContent;

    destCmtDict['approved'] = 1;
    destCmtDict['type'] = '';
    destCmtDict['parent'] = 0;
    destCmtDict['user_id'] = 0;

    logging.debug("author=%s", destCmtDict['author']);
    logging.debug("author_url=%s", destCmtDict['author_url']);
    logging.debug("date=%s", destCmtDict['date']);
    logging.debug("date_gmt=%s", destCmtDict['date_gmt']);
    logging.debug("content=%s", destCmtDict['content']);

    return destCmtDict;

#------------------------------------------------------------------------------
# baidu blog url like this:
#http://hi.baidu.com/recommend_music/blog/item/5fe2e923cee1f55e93580718.html
#http://hi.baidu.com/notebookrelated/blog/item/c0d090c34dda5357b219a8b0.html
# extract 5fe2e923cee1f55e93580718 c0d090c34dda5357b219a8b0 from above baidu url
def extractThreadId(baiduUrl):
    idx_last_slash = baiduUrl.rfind("/");
    start = idx_last_slash + 1; # jump the last '/'
    end = idx_last_dot = baiduUrl.rfind(".");
    return baiduUrl[start:end];

#------------------------------------------------------------------------------
# generate request comment URL from blog item URL
def genReqCmtUrl(blogItemUrl, startCmtIdx, reqCmtNum):
    threadIdEnc = extractThreadId(blogItemUrl);
    cmtReqTime = random.random();
    #http://hi.baidu.com/cmt/spcmt/get_thread?asyn=1&thread_id_enc=5fe2e923cee1f55e93580718&callback=_Space.commentOperate.viewCallBack&start=0&count=50&orderby_type=0&t=0.2307618197294
    #http://hi.baidu.com/cmt/spcmt/get_thread?asyn=1&thread_id_enc=5fe2e923cee1f55e93580718&start=0&count=1000&orderby_type=0&t=0.2307618197294

    # Note: here not use urllib.urlencode to encode para, 
    #       for the encoded result will convert some special chars($,:,{,},...) into %XX
    paraDict = {
        'asyn'          :   '1',
        'thread_id_enc' :   '',
        'start'         :   '',
        'count'         :   '',
        'orderby_type'  :   '0',
    };
    paraDict['thread_id_enc'] = str(threadIdEnc);
    paraDict['start'] = str(startCmtIdx);
    paraDict['count'] = str(reqCmtNum);
    paraDict['t'] = str(cmtReqTime);
        
    mainUrl = "http://hi.baidu.com/cmt/spcmt/get_thread";
    getCmtUrl = crifanLib.genFullUrl(mainUrl, paraDict);

    logging.debug("getCmtUrl=%s",getCmtUrl);
    return getCmtUrl;

#------------------------------------------------------------------------------
# get comments for input url of one blog item
# return the converted dict value
def getComments(url):
    onceGetNum = 100; # get 1000 comments once

    retDict = {"err_no":0,"err_msg":"", "total_count":'', "response_count":0, "err_desc":"","body":{"total_count":0, "real_ret_count":0, "data":[]}};

    try :
        # init before loop
        retDict = {"err_no":0,"err_msg":"", "total_count":'', "response_count":0, "err_desc":"","body":{"total_count":0, "real_ret_count":0, "data":[]}};
        respDict = {};
        needGetMoreCmt = True;
        startCmtIdx = 0;
        cmtRespJson = '';
    
        while needGetMoreCmt :
            cmtUrl = genReqCmtUrl(url, startCmtIdx, onceGetNum);
            
            cmtRespJson = crifanLib.getUrlRespHtml(cmtUrl);

            if cmtRespJson == '' :
                logging.warning("Can not get the %d comments for blog item: %s", startCmtIdx, url);
                break;
            else :
                # here eval and ast.literal_eval both will fail to convert the json into dict                
                #logging.debug("original comment response\n----------------------------\n%s", cmtRespJson);
                respDict = json.loads(cmtRespJson);
                #logging.debug("after convert to dict \n----------------------------\n%s", respDict);

                # validate comments response
                if respDict['err_no'] != 0:
                    # error number no 0 -> errors happened
                    needGetMoreCmt = False;
                    logging.warning("Reponse error for get %d comments for %s, error number=%d, error description=%s, now do retrt.",
                                startCmtIdx, url, respDict['err_no'], respDict['err_desc']);
                    break;
                else :
                    # merge comments
                    retDict['err_no'] = respDict['err_no'];
                    retDict['err_msg'] = respDict['err_msg'];
                    retDict['total_count'] = respDict['total_count'];
                    retDict['response_count'] += respDict['response_count'];
                    retDict['err_desc'] = respDict['err_desc'];       
                    retDict['body']['total_count'] = respDict['body']['total_count'];
                    retDict['body']['real_ret_count'] += respDict['body']['real_ret_count'];
                    retDict['body']['data'].extend(respDict['body']['data']);
                    
                    # check whether we have done for get all comments
                    if int(retDict['body']['real_ret_count']) < int(retDict['body']['total_count']) :
                        # not complete, continue next get
                        needGetMoreCmt = True;
                        startCmtIdx += onceGetNum;
                        logging.debug('Continue to get next %d comments start from %d for %s', onceGetNum, startCmtIdx, url);
                    else :
                        # complete, quit
                        needGetMoreCmt = False;
                        logging.debug('get all comments successfully for %s', url);
                        break;
            logging.debug("In get comments while loop end, startCmtIdx=%d, onceGetNum=%d, needGetMoreCmt=%s", startCmtIdx, onceGetNum, needGetMoreCmt);
    except:
        logging.debug("Error while get comments for %s", url);

    logging.debug('before return all comments done');
    
    return retDict;


#------------------------------------------------------------------------------
# generate the file name for other pic
# depend on following picInfoDict definition
def genNewOtherPicName(picInfoDict):
    newOtherPicName = "";
    
    filename = picInfoDict['filename'];
    fd1 = picInfoDict['fields']['fd1'];
    fd2 = picInfoDict['fields']['fd2'];
    fd3 = picInfoDict['fields']['fd3'];
    
    newOtherPicName = fd1 + '_' + fd2 + "_" + filename;

    return newOtherPicName;

#------------------------------------------------------------------------------
# check whether is self blog pic
# depend on following picInfoDict definition
def isSelfBlogPic(picInfoDict):
    isSelfPic = False;
    
    filename = picInfoDict['filename'];
    fd1 = picInfoDict['fields']['fd1'];
    fd2 = picInfoDict['fields']['fd2'];
    fd3 = picInfoDict['fields']['fd3'];
    
    blogUser = gVal['blogUser'];
    quotedBlogUser = gVal['quotedBlogUser'];

    if (fd1=='hiphotos') and (fd2=='baidu') and ( fd3==blogUser or fd3==quotedBlogUser) :
        isSelfPic = True;
    else :
        isSelfPic = False;
        
    logging.debug("isSelfBlogPic: %s", isSelfPic);

    return isSelfPic;

#------------------------------------------------------------------------------
# get the found pic info after re.search
# foundPic is MatchObject
def getFoundPicInfo(foundPic):
    #print "In getFoundPicInfo:";
    #print "type(foundPic)=",type(foundPic);
    
    # here should corresponding to singlePicUrlPat in processPicCfgDict
    picUrl  = foundPic.group(0);
    fd1     = foundPic.group(1);
    fd2     = foundPic.group(2);
    fd3     = foundPic.group(3); # is blogUser
    filename= foundPic.group("filename");
    suffix  = foundPic.group("suffix");
    
    picInfoDict = {
        'isSupportedPic': False,
        'picUrl'        : picUrl,
        'filename'      : filename,
        'suffix'        : suffix,
        'fields'        : 
            {
                'fd1' : fd1,
                'fd2' : fd2,
                'fd3' : fd3,
            },
    };
    
    if (suffix in crifanLib.getPicSufList()) :
        picInfoDict['isSupportedPic'] = True;

    #print "getFoundPicInfo: picInfoDict=",picInfoDict;

    return picInfoDict;

################################################################################
# Implemented Common Functions 
################################################################################

#------------------------------------------------------------------------------
# extract title fom url, html
def extractTitle(url, html):
    titXmlSafe = "";
    try :
        soup = htmlToSoup(html);
        tit = soup.findAll(attrs={"class":"tit"})[1];
        
        if(tit) :
            titStr = "";
            
            if tit.string :
                # 正常的帖子
                titStr = tit.string.strip();
            else :
                # 【转】的帖子：
                # <div class="tit"><span style="color:#E8A02B">【转】</span>各地区关于VPI/VCI值</div>        
                titStr = tit.contents[0].string + tit.contents[1].string;
                
            if(titStr) :
                titNoUniNum = crifanLib.repUniNumEntToChar(titStr);
                titXmlSafe = saxutils.escape(titNoUniNum);
    except : 
        titXmlSafe = "";
        
    return titXmlSafe;

#------------------------------------------------------------------------------
# extract datetime fom url, html
def extractDatetime(url, html) :
    datetimeStr = '';
    try :
        soup = htmlToSoup(html);
        date = soup.find(attrs={"class":"date"});
        datetimeStr = date.string.strip(); #2010-11-19 19:30, 2010年11月19日 星期五 下午 7:30, ...
    except :
        datetimeStr = "";
        
    return datetimeStr;


#------------------------------------------------------------------------------
# extract blog item content fom url, html
def extractContent(url, html) :
    contentStr = '';
    try :
        soup = htmlToSoup(html);
        blogText = soup.find(id='blog_text');
        
        #method 1
        mappedContents = map(CData, blogText.contents);
        #print "type(mappedContents)=",type(mappedContents); #type(mappedContents)= <type 'list'>
        contentStr = ''.join(mappedContents);
        
        # #method 2
        # originBlogContent = "";
        # logging.debug("Total %d contents for original blog contents:", len(blogText.contents));
        # for i, content in enumerate(blogText.contents):
            # if(content):
                # logging.debug("[%d]=%s", i, content);
                # originBlogContent += unicode(content);
            # else :
                # logging.debug("[%d] is null", i);
        
        # logging.debug("---method 1: map and join---\n%s", contentStr);
        # logging.debug("---method 2: enumerate   ---\n%s", originBlogContent);
        
        # # -->> seem that two method got same blog content
    except :
        contentStr = '';

    return contentStr;

#------------------------------------------------------------------------------
# extract category from url, html
def extractCategory(url, html) :
    catXmlSafe = '';
    try :
        soup = htmlToSoup(html);
        foundCat = soup.find(attrs={"class":"opt"}).findAll('a')[0];
        catStr = foundCat.string.strip();
        catNoUniNum = crifanLib.repUniNumEntToChar(catStr);
        
        unicodeCat = u'类别：';
        # also can use following line:
        #unicodeCat = ('类别：').decode('utf-8'); # makesure current file is UTF-8 format, then '类别：' is UTF-8, and ('类别：').decode('utf-8') can work

        catNoUniNum = catNoUniNum.replace(unicodeCat, '');        
        catXmlSafe = saxutils.escape(catNoUniNum);
    except :
        catXmlSafe = "";

    return catXmlSafe;

#------------------------------------------------------------------------------
# extract tags info from url, html
def extractTags(url, html) :
    tagList = [];
    # here baidu space not support tags
    return tagList;

#------------------------------------------------------------------------------
# fetch and parse comments 
# return the parsed dict value
def fetchAndParseComments(url, html):
    parsedCommentsList = [];

    #extract comments if exist
    cmtRespDict = getComments(url);
    
    #logging.debug("cmtRespDict=%s", cmtRespDict);
    
    try :
        if cmtRespDict :
            # got valid comments, now proess it
            cmtRealNum = int(cmtRespDict['body']['real_ret_count']);
            if cmtRealNum > 0 :
                logging.debug("Real get comments for this blog item : %d\n", cmtRealNum);
                cmtLists = cmtRespDict['body']['data'];

                idx = 0;
                for idx in range(cmtRealNum):
                    comment = {};

                    originCmtInfo = cmtLists[idx];
                    originCmtInfo['id'] = idx + 1;

                    #fill all comment field
                    #logging.debug("originCmtInfo=%s", originCmtInfo);
                    
                    comment = fillComments(comment, originCmtInfo);
                    parsedCommentsList.append(comment);

                    idx += 1;

                logging.debug('Total extracted comments for this blog item = %d', len(parsedCommentsList));
            else :
                logging.debug("No comments for this blog item: %s", url);
        
        #logging.debug("parsedCommentsList=%s", parsedCommentsList);
    except :
        logging.debug("Error while parse the returned comment response %s", cmtRespDict);

    return parsedCommentsList;

#------------------------------------------------------------------------------
# find next permanent link from url, html
def findNextPermaLink(url, html) :
    nextLinkStr = '';
        
    try :
        #soup = htmlToSoup(html);
        #prettifiedSoup = soup.prettify();
        #logging.debug("---prettifiedSoup:\n%s", prettifiedSoup);
        
        #extrat next (later published) blog item link
        #match = re.search(r"var pre = \[(.*?),.*?,.*?,'(.*?)'\]", prettifiedSoup, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        # var post = [true,'军训断章','军训断章', '\/yangsheng6810/blog/item/45706242bca812179313c6ce.html'];
        # var post = [false,'','', '\/serial_story/blog/item/.html'];
        #match = re.search(r"var post = \[(?P<boolVal>.*),\s?'.*',\s?'.*',\s?'(?P<relativeLink>.*)'\]", prettifiedSoup, re.DOTALL | re.IGNORECASE | re.MULTILINE);
        match = re.search(r"var post = \[(?P<boolVal>.*),\s?'.*',\s?'.*',\s?'(?P<relativeLink>.*)'\]", html, re.DOTALL | re.IGNORECASE | re.MULTILINE);
        if match:
            if match.group("boolVal") == "true":
                relativeLink = match.group("relativeLink")[1:];
                nextLinkStr = gConst['baiduSpaceDomain'] + relativeLink;

        logging.debug("Found next permanent link %s", nextLinkStr);
    except :
        nextLinkStr = '';
        logging.debug("Can not find next permanent link.");

    return nextLinkStr;

#------------------------------------------------------------------------------
# parse several datetime format string into local datetime
# possible date format:
# (1) 2010-11-19
# (2) 2010/11/19
# (3) 2010年11月19日
# (4) 2010年11月19日 星期五
# possible time format:
# (1) 18:50
# (2) 7:29 P.M.
# (3) 下午 7:30
# whole datetime format = date + ' ' + time, eg:
# (1) 2008-04-19 19:37
# (2) 2010-11-19 7:30 P.M.
# (3) 2010-11-19 下午 7:30
# (4) 2010/11/19 19:30
# (5) 2010/11/19 7:30 P.M.
# (6) 2010/11/19 下午 7:30
# (7) 2010-11-19 19:30:14
# (8) 2008年04月19日 6:47 P.M.
# (9) 2010年11月19日 下午 7:30
# (10)2010年11月19日 星期五 19:30
# (11)2010年11月19日 星期五 7:30 P.M.
# (12)2010年11月19日 星期五 下午 7:30
def parseDatetimeStrToLocalTime(datetimeStr):
    #                   1=year   2=month   3=day [4=星期几] [5=上午/下午] 6=hour 7=minute [8= A.M./P.M.]
    datetimeP = r"(\d{4})\D(\d{2})\D(\d{2})\D? ?(\S{0,3}) ?(\S{0,2}) (\d{1,2}):(\d{2}) ?(([A|P].M.)?)"
    foundDatetime = re.search(datetimeP, datetimeStr);

    datetimeStr = foundDatetime.group(0);
    year = foundDatetime.group(1);
    month = foundDatetime.group(2);
    day = foundDatetime.group(3);
    weekdayZhcn = foundDatetime.group(4);
    morningOrAfternoonUni = foundDatetime.group(5);
    
    hour = foundDatetime.group(6);
    minute = foundDatetime.group(7);
    amPm = foundDatetime.group(8);
    
    logging.debug("datetimeStr=%s, year=%s, month=%s, day=%s, hour=%s, minute=%s, weekdayZhcn=%s, morningOrAfternoonUni=%s, amPm=%s", 
                datetimeStr, year, month, day, hour, minute, weekdayZhcn, morningOrAfternoonUni, amPm);

    if morningOrAfternoonUni :
        unicodeAfternoon = u"下午";
        if morningOrAfternoonUni == unicodeAfternoon:
            hour = str(int(hour) + 8);

    if amPm :
        if amPm == "P.M." :
            hour = str(int(hour) + 8);

    # group parsed field -> translate to datetime value
    datetimeStr = year + "-" + month + "-" + day + " " + hour + ":" + minute
    parsedLocalTime = datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M') # here is GMT+8 local time
    
    return parsedLocalTime;

#------------------------------------------------------------------------------
def getProcessPhotoCfg():
    # possible own site pic link:
    # http://hiphotos.baidu.com/againinput_tmp/pic/item/069e0d89033b5bb53d07e9b536d3d539b400bce2.jpg
    # http://hiphotos.baidu.com/recommend_music/pic/item/221ebedfa1a34d224954039e.jpg
    # http://hiphotos.baidu.com/recommend_music/abpic/item/df5cf5ce3ff2b12bb600c88e.jpg
    # http://hiphotos.baidu.com/recommend%5Fmusic/pic/item/59743562b26681cfe6113a78.jpg
    # http://hiphotos.baidu.com/recommend%5Fmusic/abpic/item/df5cf5ce3ff2b12bb600c88e.jpg
    # http://hiphotos.baidu.com/recommend%5Fmusic/pic/item/6d7dea46b215a62a6b63e580.jpe
    # http://hiphotos.baidu.com/recommend%5Fmusic/mpic/item/6d7dea46b215a62a6b63e580.jpg

    # possible othersite pic url:
    # http://images.dsqq.cn/news/2010-09-10/20100910134306672.jpg
    # http://www.yunhepan.com/uploads/allimg/100909/1305253345-0.jpg
    # http://www.dg163.cn/tupian/adminfiles/2011-5/21/9342g9ij68de3i6haj.jpg
    # http://images.china.cn/attachement/jpg/site1000/20110408/000d87ad444e0f089c8d15.jpg
    # http://bbs.wangluodan.net/attachment/Mon_1007/3_35499_40623c813e04d94.jpg
    # http://beauty.pba.cn/uploads/allimg/c110111/1294G0I9200Z-2b3F.jpg
    # http://house.hangzhou.com.cn/lsxw/ylxw/images/attachement/jpg/site2/20100823/0023aea5a8210ddc161d36.jpg
    # http://photo.bababian.com/20061125/C90C3EDF9AC2E2E79D50F865FB4EB3B8_500.jpg
    # http://img.blog.163.com/photo/NT166ikVSUCOVvSLJfOrNQ==/3734609990997279604.jpg
    # http://a1.phobos.apple.com/r10/Music/y2005/m02/d24/h13/s05.lvnxldzq.170x170-75.jpg

    picSufChars = crifanLib.getPicSufChars();
    processPicCfgDict = {
        # here only extract last pic name contain: char,digit,-,_
        'allPicUrlPat'      : r'http://\w{1,20}\.\w{1,20}\.\w{1,10}[\.]?\w*/[\w%\-=]{0,50}[/]?[\w%\-/=]*/[\w\-\.]{1,100}' + r'\.[' + picSufChars + r']{3,4}',
        #                   1=field1    2=field2                   3=blogUser              4=fileName                       5=suffix
        'singlePicUrlPat'   : r'http://(\w{1,20})\.(\w{1,20})\.\w{1,10}[\.]?\w*/([\w%\-=]{0,50})[/]?[\w\-/%=]*/(?P<filename>[\w\-\.]{1,100})' + r'\.(?P<suffix>[' + picSufChars + r']{3,4})',
        'getFoundPicInfo'   : getFoundPicInfo,
        'isSelfBlogPic'     : isSelfBlogPic,
        'genNewOtherPicName': genNewOtherPicName,
    };
    
    return processPicCfgDict;

#------------------------------------------------------------------------------
# extract blog title and description
def extractBlogTitAndDesc(blogEntryUrl) :
    (blogTitle, blogDescription) = ("", "");
    
    mainUrl = blogEntryUrl + '/blog';
    
    respHtml = crifanLib.getUrlRespHtml(mainUrl);
    soup = htmlToSoup(respHtml);
    
    try:
        blogTitle = soup.find(attrs={"class":"titlink"}).string;
        blogDescription = soup.find(attrs={"class":"desc"}).string;
    except:
        (blogTitle, blogDescription) = ("", "");
    
    return (blogTitle, blogDescription);

#------------------------------------------------------------------------------
#extract baidu blog user name
# eg: recommend_music
# in    http://hi.baidu.com/recommend_music
# or in http://hi.baidu.com/recommend_music/blog
# or in http://hi.baidu.com/recommend_music/blog/
# or in http://hi.baidu.com/recommend_music/blog/item/f36b0
# or in http://hi.baidu.com/recommend_music/blog/item/f36b071112416ac3a6ef3f0e.html
def extractBlogUser(inputUrl):
    (extractOk, extractedBlogUser, generatedBlogEntryUrl) = (False, "", "");
    
    logging.debug("Extracting blog user from url=%s", inputUrl);
    
    try :
        splitedUrl = inputUrl.split("/");
        if splitedUrl[2] == 'hi.baidu.com' :
            extractedBlogUser = splitedUrl[3] # recommend_music
            if(not crifanLib.strIsAscii(extractedBlogUser)) :
                # if is: http://hi.baidu.com/资料收集
                # then should quote it, otherwise later output to WXR will fail !
                extractedBlogUser = urllib.quote(extractedBlogUser);
            generatedBlogEntryUrl = gConst['baiduSpaceDomain'] + "/" + extractedBlogUser;
            
            extractOk = True;
    except :
        (extractOk, extractedBlogUser, generatedBlogEntryUrl) = (False, "", "");
        
    if (extractOk) :
        gVal['blogUser'] = extractedBlogUser;
        gVal['blogEntryUrl'] = generatedBlogEntryUrl;
        
        gVal['quotedBlogUser'] = doForceQuote(gVal['blogUser']);

    return (extractOk, extractedBlogUser, generatedBlogEntryUrl);


#------------------------------------------------------------------------------
# find the first permanent link = url of the earliset published blog item
# Note: make sure the gVal['blogUser'] is valid before call this func
def find1stPermalink():
    global gConst;
    global gVal;
    
    fristLink = "";
    
    (isFound, errInfo) = (False, "Unknown error!");
    
    linkNode = '';
    
    try :
        # visit "http://hi.baidu.com/againinput_tmp/blog/index/10000"
        # will got the last page -> include 1 or more earliest blog items
        maxIdxNum = 10000;
        url = gVal['blogEntryUrl'] + '/blog/index/' + str(maxIdxNum);

        titList = [];
        logging.info("Begin to connect to %s",url);
        resp = crifanLib.getUrlResponse(url);
        
        logging.info("Connect successfully, now begin to find the first blog item");
        soup = BeautifulSoup(resp);
        #logging.debug("------prettified html page for: %s\n%s", url, soup.prettify());

        titList = soup.findAll(attrs={"class":"tit"});
        
        titListLen = len(titList);
        # here tit list contains:
        # [0]= blog main link
        # [1-N] rest are blog item relative links if exist blog items
        # so titListLen >= 1
        if titListLen > 1 :
            # here we just want the last one, which is the earliest blog item
            linkNode = titList[titListLen - 1].a;

        if linkNode :
            #linkNodeHref = url.split('com/',1)[0]+'com'+linkNode["href"];
            linkNodeHref = gConst['baiduSpaceDomain'] + linkNode["href"];
            
            isFound = True;
            fristLink = linkNodeHref;
            
            return (isFound, fristLink);
        else :
            errInfo = "Can't find the link node.";
            isFound = False;
            return (isFound, errInfo);
    except:
        (isFound, errInfo) = (False, "Unknown error!");
        return (isFound, errInfo);

####### Login Mode ######

#------------------------------------------------------------------------------
# log in baidu space
def loginBlog(username, password) :
    baiduSpaceEntryUrl = gVal['blogEntryUrl'];

    loginOk = False;
    
    #baiduSpaceEntryUrl = "http://hi.baidu.com/motionhouse";
    #baiduSpaceEntryUrl = "http://hi.baidu.com/wwwhaseecom";
    
    #http://www.darlingtree.com/wordpress/archives/242
    gVal['cj'] = cookielib.CookieJar();
    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(gVal['cj']));
    urllib2.install_opener(opener);
    resp = urllib2.urlopen(baiduSpaceEntryUrl);
       
    #soup = BeautifulSoup(resp, fromEncoding="GB18030");
    #soup = BeautifulSoup(resp);
    #logging.info('return baidu html---\r\n%s', soup);
    
    #here got cookie: BAIDUID for latter login
    # for index, cookie in enumerate(gVal['cj']):
        # print '[',index, ']';
        # print "name=",cookie.name;
                
        # # cookie.__class__,cookie.__dict__,dir(cookie)

        # print "value=",cookie.value;
        # print "domain=",cookie.domain;
        #print "expires=",cookie.expires;
        #print "path=",cookie.path;
        #print "version=",cookie.version;
        #print "port=",cookie.port;
        #print "secure=",cookie.secure;
        # print "comment=",cookie.comment;
        # print "comment_url=",cookie.comment_url;
        # print "rfc2109=",cookie.rfc2109;
        # print "port_specified=",cookie.port_specified;
        # print "domain_specified=",cookie.domain_specified;
        # print "domain_initial_dot=",cookie.domain_initial_dot;
        # print "--- not in spec --- ";
        # print "is_expired()=",cookie.is_expired();
        # print "is_expired=",cookie.is_expired;
        
    # retInfo = resp.info();    
    # retUrl = resp.geturl()
    
    # ContentType = retInfo['Content-Type'];
    # print "Content-Type=",ContentType
    
    # for key in retInfo.__dict__.keys() :
        # print "[",key,"]=",retInfo.__dict__[key]
    
    loginBaiduUrl = "https://passport.baidu.com/?login";
    #username=%D0%C4%C7%E9%C6%DC%CF%A2%B5%D8&password=xxx&mem_pass=on
    postDict = {
        'username'  : username,
        'password'  : password,
        'mem_pass'  : 'on',
        };
    resp = crifanLib.getUrlResponse(loginBaiduUrl, postDict);

    # check whether the cookie is OK
    cookieNameList = ["USERID", "PTOKEN", "STOKEN"];
    loginOk = crifanLib.checkAllCookiesExist(cookieNameList, gVal['cj']);
    if (not loginOk) :
        logging.error("Login fail for not all expected cookies exist !");
        return loginOk;

    # respInfo = resp.info();
    # # for key in respInfo.__dict__.keys() :
        # # print "[",key,"]=",respInfo.__dict__[key]

    # respSoup = BeautifulSoup(resp);
    # prettifiedSoup = respSoup.prettify();
    # logging.debug("login returned html:\r\n" + prettifiedSoup);

    baiduSpaceHomeUrl = baiduSpaceEntryUrl + "/home";
    resp = crifanLib.getUrlResponse(baiduSpaceHomeUrl);

    #respInfo = resp.info();
    #print "for: ",baiduSpaceHomeUrl;
    #print "resp.getcode()=",resp.getcode();
    #for key in respInfo.__dict__.keys() :
    #    print "[",key,"]=",respInfo.__dict__[key];
    
    respSoup = BeautifulSoup(resp, fromEncoding="GB18030");
    prettifiedSoup = respSoup.prettify();
    #logging.debug("space home returned html:\r\n%s", prettifiedSoup);    
    #spToken: '59a906953de03230cc41f75452ea2229',
    matched = re.search(r"spToken:\s*?'(?P<spToken>\w+?)',", prettifiedSoup);
    #print "matched=",matched;
    if( matched ) :
        gVal['spToken'] = matched.group("spToken");
        #print "found spToken = ",gVal['spToken'];
        logging.debug("Extrat out spToken=%s", gVal['spToken']);
    else :
        logging.error("Fail to extract out spToken for baidu splace home url %s", baiduSpaceHomeUrl);
        loginOk = False;

    if (not loginOk) :
        return loginOk;

    #isLogin: !true,
    #isLogin: true,
    foundLogin = re.search(r"isLogin:\s*?(?P<isLogin>[^\s]+?),", prettifiedSoup);
    if (foundLogin) :
        loginValue = foundLogin.group("isLogin");
        if (loginValue.lower() == "true") :
            logging.info("Login baisu space successfully.");
        else : # !true
            logging.error("Login fail for isLogin is not true !");
            loginOk = False;
    else :
        logging.error("Can not extract isLogin info !");
        loginOk = False;

    if (not loginOk) :
        return loginOk;

    #isHost: 1,
    #isHost: 0,
    #isHost: "",
    #isHost: "1",
    foundHost = re.search(r'isHost:\s*"?(?P<isHost>\d?)"?,', prettifiedSoup);
    if (foundHost) :
        hostValue = foundHost.group("isHost");
        #print "hostValue=",hostValue;
        if (hostValue == "1") :
            logging.info("You are the host of this space.");
        else : # !true, ""
            logging.error("isHost is not '1': seems that your username and password OK, but not login yourself's space.");
            loginOk = False;
    else :
        logging.error("Can not extract isHost info !");
        loginOk = False;

    if (not loginOk) :
        return loginOk;

    # #logging.debug("space home returned html:\r\n%s", resp.read());
    # # gzipedData = resp.read();
    # # print "before decompress, len=",len(gzipedData);
    # # decompressed = zlib.decompress(gzipedData, 16+zlib.MAX_WBITS);
    # # print "after decompress, len=",len(decompressed);
    
    # respSoup = BeautifulSoup(resp, fromEncoding="GB18030");
    # prettifiedSoup = respSoup.prettify();
    # logging.debug("space home returned html:\r\n" + prettifiedSoup);
    
    return loginOk;


#------------------------------------------------------------------------------
# check whether this post is private(self only) or not
def isPrivatePost(url, html) :
    isPrivate = False;
    
    try :
        soup = htmlToSoup(html);
        blogOption = soup.find(id='blogOpt');
        if blogOption and blogOption.contents :
            #print "type(blogOption.contents)=",type(blogOption.contents);
            #print "len(blogOption.contents)=",len(blogOption.contents);
            #keyDict = dict(blogOption.contents);
            #print "keyDict=",keyDict;
            #for i in range(len(blogOption.contents)) :
            for i, content in enumerate(blogOption.contents) :
                #print "[",i,"]:";
                # print "contents.string=",blogOption.contents[i].string;
                # print "contents:",blogOption.contents[i];
                #curStr = blogOption.contents[i].string;
                #curStr = blogOption.contents[i];
                #print "content=",content;
                
                #print "type(content)=",type(content);
                # type(content)= <class 'BeautifulSoup.NavigableString'>
                # type(content)= <type 'instance'>
                
                curStr = unicode(content);
                
                if(curStr == u"该文章为私有"):
                    #print "------------found:",curStr;
                    isPrivate = True;
                    break;
    except :
        isPrivate = False;
        logging.error("Error while check whether post is private");

    return isPrivate;

#------------------------------------------------------------------------------
# modify post content
# Note:
# (1) title should be unicode 
# (2) here modify post, sometime will flush out the original content,
# for example: 
# http://hi.baidu.com/goodword/blog/item/c38a9418e6d6a40634fa41c9.html
# now has empty content, for it is overwritten by this modify post.
# but after check the detail in debug info, the post data is right,
# so seems just the baidu system is abnormal, 
# which sometime will lead to missing out some content even if your modify post request is no problem !
def modifySinglePost(newPostContentUni, infoDict, inputCfg):
    (modifyOk, errInfo) = (False, "Unknown error!");
    
    url = infoDict['url'];
    
    # upload new blog content
    #logging.debug("New blog content to upload=\r\n%s", newPostContentUni);
    
    modifyUrl = gVal['blogEntryUrl'] + "/blog/submit/modifyblog";
    #logging.debug("Modify Url is %s", modifyUrl);
    
    #http://hi.baidu.com/wwwhaseecom/blog/item/79188d1b4fa36f068718bf79.html
    foundSpBlogID = re.search(r"blog/item/(?P<spBlogID>\w+?).html", url);
    if(foundSpBlogID) :
        spBlogID = foundSpBlogID.group("spBlogID");
        logging.debug("Extracted spBlogID=%s", spBlogID);
    else :
        modifyOk = False;
        errInfo = "Can't extract post spBlogID !";
        return (modifyOk, errInfo);

    newPostContentGb18030 = newPostContentUni.encode("GB18030");
    categoryGb18030 = infoDict['category'].encode("GB18030");
    titleGb18030 = infoDict['title'].encode("GB18030");
    
    postDict = {
        "bdstoken"      : gVal['spToken'],
        "ct"            : "1",
        "mms_flag"      : "0",
        "cm"            : "2",
        "spBlogID"      : spBlogID,
        "spBlogCatName_o": categoryGb18030, # old catagory
        "edithid"       : "",
        "previewImg"    : "",
        "spBlogTitle"   : titleGb18030,
        "spBlogText"    : newPostContentGb18030,
        "spBlogCatName" : categoryGb18030, # new catagory
        "spBlogPower"   : "0",
        "spIsCmtAllow"  : "1",
        "spShareNotAllow":"0",
        "spVcode"       : "",
        "spVerifyKey"   : "",
    }
            
    headerDict = {
        # 如果不添加Referer，则返回的html则会出现错误："数据添加的一般错误"
        "Referer" : gVal['blogEntryUrl'] + "/blog/modify/" + spBlogID,
        }
    #resp = crifanLib.getUrlResponse(modifyUrl, postDict, headerDict);
    respHtml = crifanLib.getUrlRespHtml(modifyUrl, postDict, headerDict);
    
    #respInfo = resp.info();
    #print "respInfo.__dict__=",respInfo.__dict__;
    
    #soup = BeautifulSoup(resp, fromEncoding="GB18030");
    soup = htmlToSoup(respHtml);
    prettifiedSoup = soup.prettify();
    #logging.debug("Modify post return html\n---------------\n%s\n", prettifiedSoup);
    
    # check whether has modify OK
    editOkUni = u"您的文章已经修改成功";
    #editOkGb18030 = editOkUni.encode("GB18030");
    editOkUft8 = editOkUni.encode("utf-8");
    editOkPat = re.compile(editOkUft8);        
    #writestr("您的文章已经修改成功。");
    # Note:
    # here for prettifiedSoup is utf-8, so should use utf-8 type str to search,
    # otherwise search can not found !
    foundEditOk = editOkPat.search(prettifiedSoup);
    if (foundEditOk) :
        modifyOk = True;
    else :
        #find error detail
        # <div id="errdetail" class="f14">
        #   您必须输入分类名称，请检查。
        # ...
        # </div>
        errDetail = soup.find(id='errdetail');
        if errDetail and errDetail.contents[0] :
            errDetailStr = errDetail.contents[0].string;
            errDetailStr = unicode(errDetailStr);
            
            if((inputCfg['autoJumpSensitivePost'] == 'yes') and (re.search(u'包含不合适内容', errDetailStr))) :
                #文章标题包含不合适内容，请检查
                #文章内容包含不合适内容，请检查
                logging.info("  Automatically omit modify this post for %s .", errDetailStr);
                #infoDict['omit'] = True;
                modifyOk = True;
            else :
                modifyOk = False;
                errInfo = "Modify blog post falied for %s !"%(errDetailStr);
                return (modifyOk, errInfo); 
        else :
            modifyOk = False;
            errInfo = "Modify blog post falied for unknown reason !";
            return (modifyOk, errInfo); 
    
    # sleep some time to avoid: 您的操作过于频繁，请稍后再试。
    sleepSeconds = 6;
    logging.info(u"  begin to sleep %s seconds to void '您的操作过于频繁，请稍后再试' ...", sleepSeconds);
    time.sleep(sleepSeconds);
    logging.info("  end sleep");

    return (modifyOk, errInfo);

#------------------------------------------------------------------------------   
if __name__=="BlogBaidu":
    print "Imported: %s,\t%s"%( __name__, __VERSION__);