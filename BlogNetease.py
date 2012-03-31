#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

For BlogsToWordpress, this file contains the functions for Netease 163 blog.

[TODO]
1. add support for friendOnly type post detect
2. support modify 163 post

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

#--------------------------------const values-----------------------------------
__VERSION__ = "v1.2";

gConst = {
    'blogApi163'        : "http://api.blog.163.com",
}

#----------------------------------global values--------------------------------
gVal = {
    'blogUser'      : '',
    'blogEntryUrl'  : '',  # http://againinput4.blog.163.com
    'cj'            : None, # cookiejar, to store cookies for login mode
}

################################################################################
# Internal 163 blog Functions 
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
# parse the dwr engine line, return the number of main comments
# possbile input:
# dwr.engine._remoteHandleCallback('1','0',[s0,s1]);
# dwr.engine._remoteHandleCallback('1','0',[]);
# dwr.engine._remoteHandleCallback('1','0',[s0,s1,...,s98,s99]);
def extratMainCmtNum(dwrEngine) :
    mainCmtNum = 0;
    foundSn = re.search(r".*\[(?P<sn>.*)\]", dwrEngine);
    if foundSn and foundSn.group("sn") :
        # parse it
        sList = foundSn.group("sn").split(",");
        mainCmtNum = len(sList);
    else :
        mainCmtNum = 0;
    return mainCmtNum;

#------------------------------------------------------------------------------
# generate request comment URL from blog item URL
def genReqCmtUrl(soup, startCmtIdx, onceGetNum):   
    getCmtUrl = ''

    # http://api.blog.163.com/againinput4/dwr/call/plaincall/BlogBeanNew.getComments.dwr
    # --- example ---
    # for: http://againinput4.blog.163.com/blog/static/172799491201010159650483/
    # [paras]
    # callCount=1
    # scriptSessionId=${scriptSessionId}187
    # c0-scriptName=BlogBeanNew
    # c0-methodName=getComments
    # c0-id=0
    # c0-param0=string:fks_094067082083086070082083080095085081083068093095082074085
    # c0-param1=number:1
    # c0-param2=number:0
    # batchId=728048
    # [url]
    #http://api.blog.163.com/againinput4/dwr/call/plaincall/BlogBeanNew.getComments.dwr?&callCount=1&scriptSessionId=${scriptSessionId}187&c0-scriptName=BlogBeanNew&c0-methodName=getComments&c0-id=0&c0-param0=string:fks_094067082083086070082083080095085081083068093095082074085&c0-param1=number:1&c0-param2=number:0&batchId=728048

    try :
        # extract the fks string
        fskClassInfo = soup.find(attrs={"class":"phide nb-init"});
        textareaJs = fskClassInfo.find(attrs={"name":"js"});
        fksStr = textareaJs.contents[0];
        matched = re.search(r"id:'(?P<id>fks_\d+)',", fksStr);
        foundFks = matched.group("id");
        logging.debug("Found fks %s", foundFks);

        # Note: here not use urllib.urlencode to encode para, 
        #       for the encoded result will convert some special chars($,:,{,},...) into %XX
        paraDict = {
            'callCount'     :   '1',
            'scriptSessionId':  '${scriptSessionId}187',
            'c0-scriptName' :   'BlogBeanNew',
            'c0-methodName' :   'getComments',
            'c0-id'         :   '0',
            'c0-param0'     :   '',
            'c0-param1'     :   '',
            'c0-param2'     :   '',
            'batchId'       :   '1',
        };
        paraDict['c0-param0'] = "string:" + str(foundFks);
        paraDict['c0-param1'] = "number:" + str(onceGetNum);
        paraDict['c0-param2'] = "number:" + str(startCmtIdx);
        
        mainUrl = gConst['blogApi163'] + '/' + gVal['blogUser'] + '/dwr/call/plaincall/BlogBeanNew.getComments.dwr';
        getCmtUrl = crifanLib.genFullUrl(mainUrl, paraDict);
        
        logging.debug("getCmtUrl=%s", getCmtUrl);
    except :
        getCmtUrl = "";
        logging.debug("Fail to generate comment url");
    
    return getCmtUrl;

#------------------------------------------------------------------------------
# replace the character entity references into slash + u + code point
# eg: &#10084; => \u2764 (10084=0x2764)
# more info refer: http://againinput4.blog.163.com/blog/static/1727994912011112295423982/
def replaceChrEntityToSlashU(text):
    unicodeP = re.compile(r'&#\d+;');
    def transToSlashU(match): # translate the matched string to slash unicode
        numStr = match.group(0)[2:-1]; # remove '&#' and ';'
        num = int(numStr);
        hex04x = "%04x" % num;
        slasU = '\\' + 'u' + str(hex04x);
        return slasU;
    return unicodeP.sub(transToSlashU, text);

#------------------------------------------------------------------------------
# replace '&amp;amp;' to '&amp;' in:
# s8.publisherNickname="\u5FE7\u5BDE&amp;amp;\u6CA7\u6851\u72FC";s8.publisherUrl=
# s29.replyToUserNick="\u8001\u9F20\u7687\u5E1D&amp;amp;\u9996\u5E2D\u6751\u5987";s29.shortPublishDateStr
# to makesure string is valid, then following can parse correct
def validateString(text):
    text = text.replace("&amp;amp;", "&amp;");
    return text;
    
#------------------------------------------------------------------------------
# parse the subComments field, to get the parent idx
def parseSubComments(subComments) :
    # s0.subComments=s2
    equalSplited = subComments.split("=");
    sChild = equalSplited[1]; # s2
    childIdx = int(sChild[1:]); # 2
    return childIdx;

#------------------------------------------------------------------------------
# parse each comment response line string into a dict value
def parseCmtRespStr(line, cmtCurNum) :
    # s0['abstract'] = "\u7528\u817E\u8BAF\u7684QQ\u7535\u8111\u7BA1\u5BB6\u53EF\u4EE5\u67E5\u51FA\u6765";
    # s0.blogId = "fks_094074080084085071086094085095085081083068093095082074085";
    # s0.blogPermalink = "blog/static/1727994912011390245695";
    # s0.blogTitle = "\u3010\u5DF2\u89E3\u51B3\u3011\u7F51\u9875\u65E0\u6CD5\u6253\u5F00\uFF0CIE\u8BCA\u65AD\u7ED3\u679C\u4E3A\uFF1Awindows\u65E0\u6CD5\u4F7F\u7528HTTP HTTPS\u6216\u8005FTP\u8FDE\u63A5\u5230Internet";
    # s0.blogUserId = 172799491;
    # s0.blogUserName = "againinput4";
    # s0.circleId = 0;
    # s0.circleName = null;
    # s0.circleUrlName = null;
    # s0.content = "<P>\u7528\u817E\u8BAF\u7684QQ\u7535\u8111\u7BA1\u5BB6\u53EF\u4EE5\u67E5\u51FA\u6765</P>";
    # s0.id = "fks_081068083085088067084095080095085081083068093095082074085";
    # s0.ip = "175.191.25.231";
    # s0.ipName = "\u5E7F\u4E1C \u6DF1\u5733";
    # s0.lastUpdateTime = 1322129849392;
    # s0.mainComId = "-1";
    # s0.moveFrom = null;
    # s0.popup = false;
    # s0.publishTime = 1322129849397;
    # s0.publishTimeStr = "18:17:29";
    # s0.publisherAvatar = 0;
    # s0.publisherAvatarUrl = "http://img.bimg.126.net/photo/hmZoNQaqzZALvVp0rE7faA==/0.jpg";
    # s0.publisherEmail = "";
    # s0.publisherId = 0;
    # s0.publisherName = null;
    # s0.publisherNickname = "\u957F\u5927\u662F\u70E6\u607C";
    # s0.publisherUrl = null;
    # s0.replyComId = "-1";
    # s0.replyToUserId = 172799491;
    # s0.replyToUserName = "againinput4";
    # s0.replyToUserNick = "crifan";
    # s0.shortPublishDateStr = "2011-11-24";
    # s0.spam = 0;
    # s0.subComments = s1;
    # s0.synchMiniBlog = false;
    # s0.valid = 0;

    try :
        cmtDict = {};
        
        # 1. handel special fields,
        # for these field may contain special char and ';',
        # so find and process them firstly
        # (1) handle special ['abstract']
        abstratP = r"s(?P<index>\d+)\['abstract'\]=" + r'"(?P<abstract>.*)' + r'";s[0-9]+\.blogId="';
        foundAbs = re.search(abstratP, line);
        cmtIdx = foundAbs.group("index");
        cmtDict['curCmtIdx'] = int(cmtIdx);
        cmtDict['curCmtNum'] = cmtCurNum;
        cmtDict['parentCmtNum'] = 0; # default to 0, need later update if necessary
        cmtDict['abstract'] = foundAbs.group("abstract");
        line = line[(foundAbs.end("abstract") + 2):]; # 2 means ";

        # (2) handle special .blogTitle
        titleP = r'";s' + str(cmtIdx) + "\.blogTitle=" + r'"(.*)' + r'";s' + str(cmtIdx) +'\.blogUserId=';
        foundTitle = re.search(titleP, line);
        cmtDict['blogTitle'] = foundTitle.group(1);
        beforeTitle = line[:(foundTitle.start(0) + 2)]; # include ;"
        afterTitle = line[(foundTitle.end(1) + 2):]; # exclude ";
        line = beforeTitle + afterTitle;

        # (3) handle special .content
        contentP = r";s" + str(cmtIdx) + "\.content=" + r'"(.*)' + r'";s' + str(cmtIdx) +'\.id="';
        foundContent = re.search(contentP, line);
        cmtDict['content'] = foundContent.group(1);
        beforeContent = line[:(foundContent.start(0) + 1)]; # include ;
        afterContent = line[(foundContent.end(1) + 2):]; # exclude ";
        line = beforeContent + afterContent;
                
        # TODO: nedd later use following instead of own made ones:
        # htmlentitydefs.entitydefs
        # htmlentitydefs.name2codepoint
        # htmlentitydefs.codepoint2name
        
        # before use ';' to split, makesure it not contain unicode like char == &#XXX;
        # Note:
        # after test, HTMLParser.unescape can not use here, so use following :
        # replace the &shy; and &#10084; to corresponding \uXXXX
        
        # (1) replace string entity to number entity:   &shy; -> &#173;
        originalLine = line;
        
        line = validateString(line);
        afterValidateLine = line;
    
        line = crifanLib.replaceStrEntToNumEnt(line);
        afterStrEntToNumLine = line;
        
        # (2) replace number entity into \uXXXX:        &#10084; -> \u2764
        line = replaceChrEntityToSlashU(line);
        afterChrEntToSlashULine = line;
        
        # 2. process main fields
        # (1) split
        semiSplited = line.split(";"); # semicolon splited
        #logging.debug("semiSplited=\n%s",semiSplited);
        # (2) remove un-process line
        semiSplited = crifanLib.removeEmptyInList(semiSplited);
        subComments = semiSplited.pop(len(semiSplited) - 3);# remove subComments
        childIdx = parseSubComments(subComments);
        cmtDict['childCmtIdx'] = childIdx;
        # (3) remove sN., N=0,1,2,...
        idxLen = len(str(cmtIdx));
        equationList = [];
        for eachLine in semiSplited:
            eachLine = eachLine[(1 + idxLen + 1):]; # omit sN. (N=0,1,2,...)
            equationList.append(eachLine);
        # (4) convert to value
        for equation in equationList :
            (key, value) = crifanLib.convertToTupleVal(equation);
            
            if(not key) :
                # if any error, record log info
                logging.debug("------convert equation string error, the related log info is ------");
                logging.debug("---before process, original line---\n%s", originalLine);
                logging.debug("---after validate ---\n%s", afterValidateLine);
                logging.debug("---after replace string entity to number entity---\n%s", afterStrEntToNumLine);
                logging.debug("---after replace number entity into \uXXXX---\n%s", afterChrEntToSlashULine);
            else :
                # normal, correct one
                cmtDict[key] = value;

        # notes:
        # (1) here not convert unicode-escape for later process
        # (2) most mainComId and replyComId is '-1', but some is:
        # s59.mainComId = "fks_081075082083084068082095094095085084086069083094084065080";
        # s54.replyComId = "fks_081075082080085066086086082095085084086069083094084065080";
    except :
        logging.debug("Fail to parse comment resopnse. Current comment number=%d", cmtCurNum);

    return cmtDict;

#------------------------------------------------------------------------------
# parse something like: s241[0]=s242;s241[1]=s243;
# into {childCommentNumber : parentCommentNumber} info
def extractParentRelation(line) :
    global gVal;
    
    cmtParentRelation = {};
    equationList = line.split(";");
    equationList = crifanLib.removeEmptyInList(equationList);
    logging.debug("Parsed %s into:", line);
    for equation in equationList:
        match = re.search(r's(\d+)\[(\d+)\]=s(\d+)', equation)
        int1 = int(match.group(1));
        int2 = int(match.group(2));
        int3 = int(match.group(3));
        # here use record its idx, so not +1
        cmtParentRelation[int3] = int1;
        logging.debug("     curIdx=%d, parIdx=%d", int3, int1);
    return cmtParentRelation;

#------------------------------------------------------------------------------
# convert the old {childIdx, parentIdx} to new {childIdx : parentNum}
def updateCmtRelation(oldDict, cmtList) :
    for cmt in cmtList:
        for childIdx in oldDict.keys() :
            if cmt['childCmtIdx'] == oldDict[childIdx] :
                oldDictChildIdx = oldDict[childIdx];
                oldDict[childIdx] = cmt['curCmtNum'];
                # note: here this kind of method, can change the original input oldDict[childIdx]
                logging.debug("Updated comment relation: from %d:%d to %d:%d", childIdx, oldDictChildIdx, childIdx, oldDict[childIdx]);
    return oldDict;

#------------------------------------------------------------------------------
# check whether comment type is normal:
# s10['abstract']="...
def isNormalCmt(line) :
    foundNormal = re.search(r"s\d+\['abstract'\]=.*", line);
    if foundNormal :
        return True;
    else :
        return False;

#------------------------------------------------------------------------------
# parse the returned comments response info
def parseCmtRespInfo(cmtResp, url, startCmtNum):
    retCmtDictList = [];
    mainCmtNum = 0;

    try :
        lines = cmtResp.split("\r\n");
        noBlankLines = crifanLib.removeEmptyInList(lines);
        # remove the 0,1,-1 line
        noBlankLines.pop(0); # //#DWR-INSERT
        noBlankLines.pop(0); # //#DWR-REPLY
        # eg: dwr.engine._remoteHandleCallback('1','0',[s0,s1]);
        dwrEngine = noBlankLines.pop(len(noBlankLines) - 1);
        mainCmtNum = extratMainCmtNum(dwrEngine);
        
        if noBlankLines :
            # handle first line -> remove var sN=xxx
            beginPos = noBlankLines[0].find("s0['abstract']");
            noBlankLines[0] = noBlankLines[0][beginPos:];

            cmtList = [];
            relationDict = {};
            cmtCurNum = startCmtNum;
            for line in noBlankLines :
                #logging.debug("%s", line);
                if isNormalCmt(line) :
                    singleCmtDict ={};
                    singleCmtDict = parseCmtRespStr(line, cmtCurNum);
                    cmtList.append(singleCmtDict);
                    
                    cmtCurNum += 1;
                else :
                    # something like: s241[0]=s242;s241[1]=s243;
                    parsedRelation = extractParentRelation(line);
                    # add into whole relation dict
                    for childIdx in parsedRelation.keys() :
                        relationDict[childIdx] = parsedRelation[childIdx];
            # update the index relation
            updateCmtRelation(relationDict, cmtList);
            # update parent index info then add to list
            for cmt in cmtList :
                if cmt['curCmtIdx'] in relationDict :
                    cmt['parentCmtNum'] = relationDict[cmt['curCmtIdx']];
                    logging.debug("Updated comment parent info: curNum=%d, parentNum=%d", cmt['curCmtNum'], cmt['parentCmtNum']);
                retCmtDictList.append(cmt);

            logging.debug("Parsed %d comments", cmtCurNum - startCmtNum);
            #logging.debug("-------comment list---------";
            #for cmt in retCmtDictList :
            #    logging.debug("%s", cmt);
        else :
            logging.debug("Parsed result is no comment.");
    except :
        logging.debug("Parse number=%d comment fail for url= %s", cmtCurNum, url);

    return (retCmtDictList, mainCmtNum);

#------------------------------------------------------------------------------
# get comments for input url of one blog item
# return the converted dict value
def fetchComments(url, soup):
    cmtList = [];

    # init before loop
    needGetMoreCmt = True;
    startCmtIdx = 0;
    startCmtNum = 1;
    onceGetNum = 1000; # get 1000 comments once
    
    try :
        while needGetMoreCmt :
            cmtUrl = genReqCmtUrl(soup, startCmtIdx, onceGetNum);
            cmtRetInfo = crifanLib.getUrlRespHtml(cmtUrl);
            
            #logging.debug("---------got comment original response ------------\n%s", cmtRetInfo);
            
            (parsedCmtList, mainCmtNum) = parseCmtRespInfo(cmtRetInfo, url, startCmtNum);

            if parsedCmtList :
                # add into ret list
                cmtList.extend(parsedCmtList);
                cmtNum = len(parsedCmtList);
                logging.debug("Currently got %d comments for idx=[%d-%d]", cmtNum, startCmtIdx, startCmtIdx + onceGetNum - 1);
                if mainCmtNum < onceGetNum :
                    # only got less than we want -> already got all comments
                    needGetMoreCmt = False;
                    logging.debug("Now has got all comments.");
                else :
                    needGetMoreCmt = True;
                    startCmtIdx += onceGetNum;
                    startCmtNum += cmtNum;
            else :
                needGetMoreCmt = False;
    except :
        logging.debug("Fail for fetch the comemnts(index=[%d-%d]) for %s ", startCmtIdx, startCmtIdx + onceGetNum - 1, url);

    return cmtList;

#------------------------------------------------------------------------------
# check whether the input 163 blog user is other type user:
# (1) jdidi155@126     in http://blog.163.com/jdidi155@126
# (2) againinput4@yeah in http://blog.163.com/againinput4@yeah/
# note:
# for some extremly special ones:
# hi_ysj -> http://blog.163.com/hi_ysj
def isOtherTypeUser(blogUser) :
    isOthertype = False;
    if blogUser and (len(blogUser) > 4 ) :
        if blogUser[-4:] == '@126' :
            isOthertype = True;
        elif blogUser[-4:] == '@yeah' :
            isOthertype = True;
        else :
            isOthertype = False;
    return isOthertype;

#------------------------------------------------------------------------------
# genarate the 163 blog user url from input user name
# jdidi155@126          -> http://blog.163.com/jdidi155@126
# againinput4@yeah      -> http://blog.163.com/againinput4@yeah/
# miaoyin2008.happy     -> http://miaoyin2008.happy.blog.163.com
# note:
# for some extremly special ones:
# http://blog.163.com/hi_ysj
# the generated is http://hi_ysj.blog.163.com/
# is a workable url but is redirect
def genNeteaseUserUrl(blogUser) :
    global gConst;
    
    url = '';
    try :
        # http://owecn.blog.163.com/blog/static/862559512011112684224161/
        # whose comments contain 'publisherName'=None
        if blogUser :
            if isOtherTypeUser(blogUser) :
                url = gConst['blogDomain163'] + "/" + blogUser;
            else : # is normal
                url = "http://" + blogUser + ".blog.163.com"
    except :
        logging.debug("Can not generate blog user url for input blog user %s", blogUser);
    return url;

#------------------------------------------------------------------------------
# fill source comments dictionary into destination comments dictionary
def fillComments(destCmtDict, srcCmtDict):
    logging.debug("--------- source comment: idx=%d, num=%d ---------", srcCmtDict['curCmtIdx'], srcCmtDict['curCmtNum']);
    #for item in srcCmtDict.items() :
    #    logging.debug("%s", item);
    destCmtDict['id'] = srcCmtDict['curCmtNum'];

    decodedNickname = srcCmtDict['publisherNickname'].decode('unicode-escape');
    noCtrlChrNickname = crifanLib.removeCtlChr(decodedNickname);
    destCmtDict['author'] = noCtrlChrNickname;
    destCmtDict['author_email'] = srcCmtDict['publisherEmail'];
    destCmtDict['author_url'] = saxutils.escape(genNeteaseUserUrl(srcCmtDict['publisherName']));
    destCmtDict['author_IP'] = srcCmtDict['ip'];
    
    # method 1:
    #epoch1000 = srcCmtDict['publishTime']
    #epoch = float(epoch1000) / 1000
    #localTime = time.localtime(epoch)
    #gmtTime = time.gmtime(epoch)
    # method 2:
    pubTimeStr = srcCmtDict['shortPublishDateStr'] + " " + srcCmtDict['publishTimeStr'];
    localTime = datetime.strptime(pubTimeStr, "%Y-%m-%d %H:%M:%S");
    gmtTime = crifanLib.convertLocalToGmt(localTime);
    destCmtDict['date'] = localTime.strftime("%Y-%m-%d %H:%M:%S");
    destCmtDict['date_gmt'] = gmtTime.strftime("%Y-%m-%d %H:%M:%S");

    # handle some speical condition
    #logging.debug("before decode, coment content:\n%s", srcCmtDict['content']);
    cmtContent = srcCmtDict['content'].decode('unicode-escape'); # convert from \uXXXX to character
    #logging.debug("after decode, coment content:\n%s", cmtContent);
    # remove invalid control char in comments content
    cmtContent = crifanLib.removeCtlChr(cmtContent);
    destCmtDict['content'] = cmtContent;

    destCmtDict['approved'] = 1;
    destCmtDict['type'] = '';
    destCmtDict['parent'] = srcCmtDict['parentCmtNum'];
    destCmtDict['user_id'] = 0;

    logging.debug("author=%s", destCmtDict['author']);
    logging.debug("author_email=%s", destCmtDict['author_email']);
    logging.debug("author_IP=%s", destCmtDict['author_IP']);
    logging.debug("author_url=%s", destCmtDict['author_url']);
    logging.debug("date=%s", destCmtDict['date']);
    logging.debug("date_gmt=%s", destCmtDict['date_gmt']);
    logging.debug("content=%s", destCmtDict['content']);
    logging.debug("parent=%s", destCmtDict['parent']);

    return destCmtDict;


#------------------------------------------------------------------------------
# generate get blogs URL
def genGetBlogsUrl(userId, startBlogIdx, onceGetNum):
    getBlogsUrl = '';

    try :
        # http://api.blog.163.com/againinput4/dwr/call/plaincall/BlogBeanNew.getBlogs.dwr
        # callCount=1
        # scriptSessionId=${scriptSessionId}187
        # c0-scriptName=BlogBeanNew
        # c0-methodName=getBlogs
        # c0-id=0
        # c0-param0=number:172799491
        # c0-param1=number:0
        # c0-param2=number:20
        # batchId=955290

        paraDict = {
            'callCount'     :   '1',
            'scriptSessionId':  '${scriptSessionId}187',
            'c0-scriptName' :   'BlogBeanNew',
            'c0-methodName' :   'getBlogs',
            'c0-id'         :   '0',
            'c0-param0'     :   '',
            'c0-param1'     :   '',
            'c0-param2'     :   '',
            'batchId'       :   '1',
        };
        paraDict['c0-param0'] = "number:" + str(userId);
        paraDict['c0-param1'] = "number:" + str(startBlogIdx);
        paraDict['c0-param2'] = "number:" + str(onceGetNum);
        
        mainUrl = gConst['blogApi163'] + '/' + gVal['blogUser'] + '/' + 'dwr/call/plaincall/BlogBeanNew.getBlogs.dwr';
        getBlogsUrl = crifanLib.genFullUrl(mainUrl, paraDict);

        logging.debug("Generated get blogs url %s", getBlogsUrl);
    except :
        logging.debug("Can not generate get blog url.");

    return getBlogsUrl;

#------------------------------------------------------------------------------
# extract the 'permaSerial' filed from the single response blog string
def extractPermaSerial(singleBlogStr):
    permaSerial = '';
    foundPerma = re.search(r's[0-9]{1,10}\.permaSerial="(?P<permaSerial>[0-9]{1,100})";', singleBlogStr);
    permaSerial = foundPerma.group("permaSerial");
    logging.debug("Extracted permaSerial=%s", permaSerial);
    return permaSerial;

#------------------------------------------------------------------------------
# find prev permanent link from soup
def findPrevPermaLink(soup) :
    prevLinkStr = False;
    try :
        foundPrevLink = soup.find(attrs={"class":"pleft thide"});
        prevLinkStr = foundPrevLink.a['href'];
        #prevLinkTitleStr = foundPrevLink.a.string.strip();
        logging.debug("Found previous permanent link %s", prevLinkStr);
        foundPrev = True;
    except :
        foundPrev = False;
        prevLinkStr = "";
        logging.debug("Can not find previous permanent link");

    return prevLinkStr;

#------------------------------------------------------------------------------
# find the real end of previous link == earliest permanent link
# Why do this:
# for some blog, if stiky some blog, which is earliest than the lastFoundPermaSerial
# then should check whether it has more previuous link or not
# if has, then find the end of previous link
# eg: http://cqyoume.blog.163.com/blog
def findRealFirstPermaLink(blogEntryUrl, permaSerial) :
    endOfPrevLink = '';
    try :
        curLink = blogEntryUrl + "/blog/static/" + permaSerial;
        logging.debug("Start find real first permanent link from %s", curLink);

        lastLink = curLink;
        
        while curLink :
            # save before
            lastLink = curLink;
            
            # open it
            respHtml = crifanLib.getUrlRespHtml(curLink);
            soup = BeautifulSoup(respHtml);
            
            # find previous link util the end
            curLink = findPrevPermaLink(soup);

        endOfPrevLink = lastLink;
        logging.debug("Found the earliest link %s", endOfPrevLink);
    except:
        logging.debug("Can not find the earliest link for %s", permaSerial);

    return endOfPrevLink;

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
def isSelfBlogPic(picInfoDict):
    isSelfPic = False;
    
    filename = picInfoDict['filename'];
    fd1 = picInfoDict['fields']['fd1'];
    fd2 = picInfoDict['fields']['fd2'];
    fd3 = picInfoDict['fields']['fd3'];
    
    #if ((fd1=='ph') or (fd1=='bimg')) and (fd2=='126') and (fd3=='net') :
    if (fd2=='126') and (fd3=='net') :
        #print "isSelfBlogPic: yes";
        
        # is 163 pic
        # http://imgAAA.BBB.126.net/CCC/DDD.EEE
        # AAA=None/1/3/6/7/182/..., BBB=ph/bimg, CCC=gA402SeBEI_fgrOs8HjFZA==/uCnmEQiWL40RrkIJnXKjsA==, DDD=2844867589615022702/667940119751497876, EEE=jpg

        isSelfPic = True;
    else :
        #print "isSelfBlogPic: no";
        isSelfPic = False;

    return isSelfPic;

#------------------------------------------------------------------------------
# get the found pic info after re.search
# foundPic is MatchObject
def getFoundPicInfo(foundPic):
    # here should corresponding to singlePicUrlPat in processPicCfgDict
    picUrl  = foundPic.group(0);
    fd1     = foundPic.group(1); # for 163 pic, is ph/bimg
    fd2     = foundPic.group(2); # for 163 pic, is 126
    fd3     = foundPic.group(3); # for 163 pic, is net
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

    return picInfoDict;


################################################################################
# Implemented Common Functions 
################################################################################

#------------------------------------------------------------------------------
# extract title fom html
def extractTitle(html):
    titXmlSafe = '';
    try :
        soup = htmlToSoup(html);
        foundTitle = soup.find(attrs={"class":"tcnt"});
        
        # foundTitle should not empty
        # foundTitle.string is unicode type here
        titStr = foundTitle.string.strip();
        titNoUniNum = crifanLib.repUniNumEntToChar(titStr);
        titXmlSafe = saxutils.escape(titNoUniNum);
        logging.debug("Extrated title=%s", titXmlSafe);
    except : 
        titXmlSafe = '';

    return titXmlSafe;


#------------------------------------------------------------------------------
# extract datetime fom html
def extractDatetime(html) :
    datetimeStr = '';
    try :
        soup = htmlToSoup(html);
        foundDatetime = soup.find(attrs={"class":"blogsep"});
        datetimeStr = foundDatetime.string.strip(); #2010-11-15 09:44:12
    except :
        datetimeStr = "";
        
    return datetimeStr


#------------------------------------------------------------------------------
# extract blog item content fom html
def extractContent(html) :
    contentStr = '';
    try :
        soup = htmlToSoup(html);
        foundContent = soup.find(attrs={"class":"bct fc05 fc11 nbw-blog ztag"});

        # note: 
        # here must use BeautifulSoup-3.0.6.py
        # for CData in BeautifulSoup-3.0.4.py has bug :
        # process some kind of string will fail when use CData
        # eg: http://benbenwo1091.blog.163.com/blog/static/26634402200842202442518/
        # CData for foundContent.contents[11] will fail
        mappedContents = map(CData, foundContent.contents);
        contentStr = ''.join(mappedContents);
    except :
        contentStr = '';

    return contentStr;

#------------------------------------------------------------------------------
# extract category from html
def extractCategory(html) :
    catXmlSafe = '';
    try :
        soup = htmlToSoup(html);
        foundCat = soup.find(attrs={"class":"fc03 m2a"});
        catStr = foundCat.string.strip();
        catNoUniNum = crifanLib.repUniNumEntToChar(catStr);
        catXmlSafe = saxutils.escape(catNoUniNum);
    except :
        catXmlSafe = "";

    return catXmlSafe;

#------------------------------------------------------------------------------
# extract tags info from html
def extractTags(html) :
    tagList = [];
    try :
        soup = htmlToSoup(html);
        
        # extract tags from following string:
        # blogTag:'wordpress,importer,无法识别作者,author',

        # blogUrl:'blog/static/1727994912012040341700',
        nbInit = soup.find(attrs={"class":"phide nb-init"});
        nbInitUni = unicode(nbInit);
        #nbInitStr = str(nbInit)
        blogTagP = re.compile(r"blogTag:'(?P<blogTag>.*)',\s+blogUrl:'");
        searched = blogTagP.search(nbInitUni);
        #searched = blogTagP.search(nbInitStr)
        tags = searched.group("blogTag");
        tagList = tags.split(',');
        
        # note: here for list, [u''] is not empty, only [] is empty
        tagList = crifanLib.removeEmptyInList(tagList);

    except :
        tagList = [];

    return tagList;

#------------------------------------------------------------------------------
# fetch and parse comments 
# return the parsed dict value
def fetchAndParseComments(url, html):
    cmtRespDictList = [];
    parsedCommentsList = [];

    #extract comments if exist
    soup = htmlToSoup(html);
    cmtRespDictList = fetchComments(url, soup);
    if(cmtRespDictList) :
        # got valid comments, now proess it
        for cmtDict in cmtRespDictList :
            comment = {};
            #fill all comment field
            comment = fillComments(comment, cmtDict);
            parsedCommentsList.append(comment);

    return parsedCommentsList;

#------------------------------------------------------------------------------
# find next permanent link from html
def findNextPermaLink(html) :
    nextLinkStr = '';
    try :
        soup = htmlToSoup(html);
        foundNextLink = soup.find(attrs={"class":"pright thide"});
        nextLinkStr = foundNextLink.a['href'];
        logging.debug("Found next permanent link %s", nextLinkStr);
    except :
        nextLinkStr = '';
        logging.debug("Can not find next permanent link.");

    return nextLinkStr;

#------------------------------------------------------------------------------
# possible date format:
# (1) 2011-12-26 08:46:03
def parseDatetimeStrToLocalTime(datetimeStr):
    parsedLocalTime = datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S') # here is GMT+8 local time
    return parsedLocalTime;

#------------------------------------------------------------------------------
def getProcessPhotoCfg():

    # possible own 163 pic link:
    # http://img1.bimg.126.net/photo/4OhNd7YZHKcWBijDhH_xkw==/4545539398901511141.jpg
    # http://img7.bimg.126.net/photo/6Sr67VS8U_RjyPLm5DDomw==/2315976108376294877.jpg
    # http://img.ph.126.net/L1z4EBxPAMwKj1WNRn6YTw==/3388114294667569667.jpg
    # http://img3.ph.126.net/vnCN6SMX6Kx6qM1BuEwEdg==/2837549240237180773.jpg
    # http://img5.ph.126.net/xR2T_SFlDqkzMRv2-Hwv6A==/3088061969509771535.jpg
    # http://img6.ph.126.net/mSalyXJwPfy-1agdRYLWBA==/667940119751497876.jpg
    # http://img7.ph.126.net/gA402SeBEI_fgrOs8HjFZA==/2521171366414523437.jpg
    # http://img157.ph.126.net/CrAyvqUxAjL58T1ks-n42Q==/1470988228291290473.jpg
    # http://img842.ph.126.net/kHXUQVumsubuU_-u49bC9A==/868350303154275443.jpg
    # http://img699.ph.126.net/uCnmEQiWL40RrkIJnXKjsA==/2844867589615022702.jpg
    # http://imgcdn.ph.126.net/Q0B-u3-uRIsEtozkdfTDZw==/2831356790749646754.jpg

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
        'allPicUrlPat'      : r'http://\w{1,20}\.\w{1,20}\.\w{1,10}[\.]?\w*/[\w%\-=]{0,50}[/]?[\w%\-/=]*/[\w\-\.]{1,100}'  + r'\.[' + picSufChars + r']{3,4}',
        #                              1=field1    2=field2    3=field3                                4=filename                     5=suffix
        'singlePicUrlPat'   : r'http://\w{1,20}\.(\w{1,20})\.(\w{1,10})[\.]?(\w*)/[\w%\-=]{0,50}[/]?[\w\-/%=]*/(?P<filename>[\w\-\.]{1,100})' + r'\.(?P<suffix>[' + picSufChars + r']{3,4})',
        'getFoundPicInfo'   : getFoundPicInfo,
        'isSelfBlogPic'     : isSelfBlogPic,
        'genNewOtherPicName': genNewOtherPicName,
    };
    
    return processPicCfgDict;

#------------------------------------------------------------------------------
# extract blog title and description
def extractBlogTitAndDesc(blogEntryUrl) :
    (blogTitle, blogDescription) = ("", "");
    
    respHtml = crifanLib.getUrlRespHtml(blogEntryUrl);
    soup = htmlToSoup(respHtml);
    
    try:
        titleAndDesc = soup.findAll(attrs={"class":"ztag pre"});
        blogTitle = titleAndDesc[0].string;
        blogDescription = titleAndDesc[1].string;
    except:
        (blogTitle, blogDescription) = ("", "");
    
    return (blogTitle, blogDescription);

#------------------------------------------------------------------------------
#extract 163 blog user name
# eg: 
# (1) againinput4       in http://againinput4.blog.163.com/xxxxxx
#     zhao.geyu         in http://zhao.geyu.blog.163.com/xxx
# (2) jdidi155@126      in http://blog.163.com/jdidi155@126/xxx
#     againinput4@yeah  in http://blog.163.com/againinput4@yeah/xxx
# (3) hi_ysj            in http://blog.163.com/hi_ysj/
def extractBlogUser(inputUrl):
    #print "inputUrl=",inputUrl;

    (extractOk, extractedBlogUser, generatedBlogEntryUrl) = (False, "", "");

    try :
        blog163com = ".blog.163.com";
        lenBlog163com = len(blog163com);

        blog163Str = "http://blog.163.com/";
        lenBlog163 = len(blog163Str);
        compEnd = lenBlog163 - 1; # compare end

        slashList = inputUrl.split("/");
        mainStr = slashList[2]; # againinput4.blog.163.com or blog.163.com

        if inputUrl[0 : compEnd] == blog163Str[0: compEnd] :
            # is http://blog.163.com/jdidi155@126/...
            extractedBlogUser = slashList[3]; # jdidi155@126
            generatedBlogEntryUrl = blog163Str + extractedBlogUser;
            
            extractOk = True;
        elif mainStr[(-(lenBlog163com)):] == blog163com :
            # is http://zhao.geyu.blog.163.com/...
            extractedBlogUser = mainStr[0:(-(lenBlog163com))]; # zhao.geyu
            generatedBlogEntryUrl = "http://" + extractedBlogUser + blog163com;
            
            extractOk = True;
        else :
            extractOk = False;
    except :
        extractOk = False;

    if (extractOk) :
        gVal['blogUser'] = extractedBlogUser;
        gVal['blogEntryUrl'] = generatedBlogEntryUrl;
        
    return (extractOk, extractedBlogUser, generatedBlogEntryUrl);

#------------------------------------------------------------------------------
# find the first permanent link = url of the earliset published blog item
def find1stPermalink():
    global gVal;
    
    (isFound, errInfo) = (False, "Unknown error!");
    blogEntryUrl = gVal['blogEntryUrl'];

    firstPermaLink = '';
    try :
        # 1. generate and open main blog url
        logging.debug("Begin to find the first permanent link from %s", blogEntryUrl);
        logging.debug("Begin to open %s", blogEntryUrl);
        
        respHtml = crifanLib.getUrlRespHtml(blogEntryUrl);
        
        logging.debug("Connect successfully, now begin to find the first blog item");

        # 2. init
        
        # extract userId
        #UD.host = {
        #  userId:39515918
        # ,userName:'zhuchao-2006'
        # ,...........
        # };
        udHost = re.search(r"UD\.host\s*=\s*\{\s*userId:(?P<userId>[0-9]{1,20})\s*,", respHtml);
        userId = udHost.group("userId");
        logging.debug("Extracted blog useId=%s", userId);

        # 3. get blogs and parse it
        needGetMoreBlogs = True;
        lastFoundPermaSerial = '';
        startBlogIdx = 0;
        onceGetNum = 400 # note: for get 163 blogs, one time request more than 500 will fail

        while needGetMoreBlogs :
            logging.debug("Start to get blogs: startBlogIdx=%d, onceGetNum=%d", startBlogIdx, onceGetNum);
            getBlogUrl = genGetBlogsUrl(userId, startBlogIdx, onceGetNum);
            
            # get blogs
            blogsResp = crifanLib.getUrlRespHtml(getBlogUrl);
                        
            # parse it
            lines = blogsResp.split("\r\n");
            noBlankLines = crifanLib.removeEmptyInList(lines);

            # remove the 0,1,-1 line
            noBlankLines.pop(0); # //#DWR-INSERT
            noBlankLines.pop(0); # //#DWR-REPLY
            # eg: dwr.engine._remoteHandleCallback('1','0',[s0,s1]);
            dwrEngine = noBlankLines.pop(len(noBlankLines) - 1);
            mainBlogsNum = extratMainCmtNum(dwrEngine);
 
            if (mainBlogsNum > 0)  and noBlankLines :
                # if not once get max num, 
                # then last line of the response is not contain permaSerial, like this:
                # s32[0]=8412120;s32[1]=8596165;............;s32[8]=8223049;
                while noBlankLines :
                    curLastBlogStr = noBlankLines.pop(-1);
                    if re.search(r'\.permaSerial', curLastBlogStr) :
                        # only contain '.permaSerial', then goto extract it
                        lastFoundPermaSerial = extractPermaSerial(curLastBlogStr);
                        break; # exit while
                
                if mainBlogsNum < onceGetNum :
                    needGetMoreBlogs = False;
                    logging.debug("Has got all blogs");
                else :
                    needGetMoreBlogs = True;
                    startBlogIdx += onceGetNum;
            else :
                needGetMoreBlogs = False;
        # out of while loop, set value
        if lastFoundPermaSerial :
            firstPermaLink = findRealFirstPermaLink(blogEntryUrl, lastFoundPermaSerial);
            isFound = True;
        else :
            errInfo = "Can not extract real first permanent link !";
            isFound = False;
    except :
        isFound = False;
    
    if(isFound) :
        return (isFound, firstPermaLink);
    else :
        return (isFound, errInfo);

####### Login Mode ######

#------------------------------------------------------------------------------
# login 163
# extract necessary info
# username = againinput4@163.com
def loginBlog(username, password) :
    loginOk = False;
    
    # 1. http://againinput4.blog.163.com
    gVal['cj'] = cookielib.CookieJar();
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(gVal['cj']));
    urllib2.install_opener(opener);
    resp = urllib2.urlopen(gVal['blogEntryUrl']);
    
    # for index, cookie in enumerate(gVal['cj']):
        # logging.debug('[%s]:', index);
        # logging.debug("name=%s", cookie.name);
        # # cookie.__class__,cookie.__dict__,dir(cookie);
        # logging.debug("value=%s", cookie.value);
        # logging.debug("domain=%s", cookie.domain);

    # 2. https://reg.163.com/logins.jsp
    # againinput4
    usernameNoSuf = username;
    atIdx = username.find("@");
    if( atIdx > 0) :
        usernameNoSuf = username[:atIdx];

    #http://blog.163.com/loginGate.do?username=againinput4&target=http%3A%2F%2Fagaininput4.blog.163.com%2F&blogActivation=true
    loginGateUrl = "http://blog.163.com/loginGate.do?";
    loginGateUrl += "username=" + usernameNoSuf;
    loginGateUrl += "&target=" + urllib.quote(gVal['blogEntryUrl']);
    loginGateUrl += "&blogActivation=" + "true";
    logging.debug("loginGateUrl=%s", loginGateUrl);
    
    loginUrl = "https://reg.163.com/logins.jsp";
    postDict = {
        'username'  : username,
        'password'  : password,
        'savelogin' : 'blog',
        'type'      : '1',
        'savelogin' : '0',
        'url'       : loginGateUrl,
        };
    resp = crifanLib.getUrlResponse(loginUrl, postDict);
    
    respInfo = resp.info();
    # for key in respInfo.__dict__.keys() :
        # logging.debug("[%s]=%s", key, respInfo.__dict__[key]);

    # logging.debug("--------after loginUrl -----");
    # for key in respInfo.__dict__['headers'] :
        # logging.debug(key);

    cookieNameList = ["NTES_SESS", "S_INFO", "P_INFO", "SID", "JSESSIONID"];
    loginOk = crifanLib.checkAllCookiesExist(cookieNameList, gVal['cj']);
    if (not loginOk) :
        logging.error("Login fail for not all expected cookies exist !");
        return loginOk;
        
    respHtml = crifanLib.getUrlRespHtml(gVal['blogEntryUrl']);
    #soup = BeautifulSoup(respHtml, fromEncoding="GB18030");
    #prettifiedSoup = soup.prettify();
    #logging.debug("--------after login, main url -----\n%s", prettifiedSoup);
    #logging.debug("--------after login, main url -----\n%s", respHtml);
    
    # UD.host = {
        # userId: 32677678,
        # userName: 'green-waste',
        # nickName: 'green-waste',
        # imageUpdateTime: 1258015689716,
        # baseUrl: 'http://green-waste.blog.163.com/',
        # gender: '他',
        # email: 'green-waste@163.com',
        # photo163Name: 'green-waste',
        # photo163HostName: 'green-waste',
        # TOKEN_HTMLMODULE: 'b0bda791b43853d241bb0dc738b8f971',
        # isMultiUserBlog: false,
        # isWumiUser: true,
        # sRank: -100
    # };
    # UD.visitor = {
        # userId: 32677678,
        # userName: 'green-waste',
        # nickName: 'green-waste',
        # imageUpdateTime: 1258015689716,
        # userType: [12, 26],
        # baseUrl: 'http://green-waste.blog.163.com/',
        # email: 'green-waste@163.com',
        # photo163Name: 'green-waste',
        # photo163VisitorName: 'green-waste',
        # isOnwer: true,
        # isMultiUserMember: false,
        # multiUserVisitorRank: 10000,
        # isShowFaXianTip: false,
        # isShowGuanggaoTip: false,
        # isLofterInviteTip: false,
        # isVIP: false,
        # isShowYXP: false
    # };
    
      # window.UD = {};
      # UD.host = {
          # userId:167169970
         # ,userName:'fgsink'
         # ,nickName:'Neo'
         # ,imageUpdateTime:1278587392293
         # ,baseUrl:'http://fgsink.blog.163.com/'
         # ,gender:'他'
         # ,email:'fgsink@163.com'
         # ,photo163Name:'fgsink'
         # ,photo163HostName:'fgsink'
         # ,TOKEN_HTMLMODULE:''
         # ,isMultiUserBlog:false
         # ,isWumiUser:true
         # ,sRank:-100
      # };
      # UD.visitor = {
         # userId:32677678,
         # userName:'green-waste',
         # nickName:'green-waste',
         # imageUpdateTime:1258015689716,
         # userType:[12,26],
         # baseUrl:'http://green-waste.blog.163.com/',
         # email:'green-waste@163.com'
         # ,photo163Name:'green-waste'
         # ,photo163VisitorName:'green-waste'
         # ,isOnwer:false
         # ,isMultiUserMember:false
         # ,multiUserVisitorRank:0
         # ,isShowFaXianTip:false
         # ,isShowGuanggaoTip:false
         # ,isLofterInviteTip:false
         # ,isVIP:false
         # ,isShowYXP:false
      # };
    
    matched = re.search(r"UD\.host\s*?=\s*?\{.+?email\:'(?P<email>.+?)'.+?isOnwer:(?P<isBlogOwner>\w+)\s*?,", respHtml);
    #print "matched=",matched;
    if( matched ) :
        hostMail = matched.group("email");
        if(hostMail == username) :
            logging.debug("Extrat out blog host email equal with the username = %s", username);
            loginOk = True;
            isBlogOwner = matched.group("isBlogOwner");
            if(isBlogOwner.lower() == "true") :
                loginOk = True;
                logging.debug("Indeed is blog owner.");
            else :
                loginOk = False;
                logging.error("Host email equal, but you are not blog owner !");
        else :
            logging.error("Extrat out blog host email is %s, not equal with the username %s => your are not this blog's owner !", hostMail, username);
            loginOk = False;
    else :
        logging.error("Fail to extract out blog host email => do not know whether you are the host of this blog.");
        loginOk = False;

    if (not loginOk) :
        return loginOk;
    
    # # 3. http://blog.163.com/loginGate.do?username=againinput4&target=http%3A%2F%2Fagaininput4.blog.163.com%2F&blogActivation=true
    # resp = crifanLib.getUrlResponse(gVal['blogEntryUrl']);
    # respSoup = BeautifulSoup(resp, fromEncoding="GB18030");
    # prettifiedSoup = respSoup.prettify();
    # logging.debug("163 blog entry returned html:\r\n%s", prettifiedSoup);

    return loginOk;

#------------------------------------------------------------------------------
# check whether this post is private(self only) or not
# if error while check, consider it to non-private
def isPrivatePost(html) :
    isPrivate = False;
    
    # private posts:
    #<h3 class="title pre fs1"><span class="tcnt">private 帖子2 测试</span>&nbsp;&nbsp;<span class="bgc0 fc07 fw0 fs0">私人日志</span></h3>
    #<h3 class="title pre fs1"><span class="tcnt">private post test</span>&nbsp;&nbsp;<span class="bgc0 fc07 fw0 fs0">私人日志</span></h3>
    
    # public posts:
    #<h3 class="title pre fs1"><span class="tcnt">公开 帖子 测试</span>&nbsp;&nbsp;<span class="bgc0 fc07 fw0 fs0"></span></h3>
    try :
        soup = htmlToSoup(html);
        foundBgc0 = soup.find(attrs={"class":"bgc0 fc07 fw0 fs0"});
        if foundBgc0 and foundBgc0.contents :
            for i, content in enumerate(foundBgc0.contents) :
                curStr = content;
                # here: type(curStr)= <class 'BeautifulSoup.NavigableString'>
                curStr = unicode(curStr);
                if(curStr == u"私人日志"):
                    isPrivate = True;
                    break;
    except :
        isPrivate = False;
        logging.debug("Error while check whether post is private");

    return isPrivate;

####### Modify post while in Login Mode ######

#------------------------------------------------------------------------------
# modify post content
# note: 
# (1) infoDict['title'] should be unicode
def modifySinglePost(newPostContentUni, infoDict, inputCfg):
    (modifyOk, errInfo) = (False, "Unknown error!");
    
    postRespHtml = infoDict['respHtml'];
    title = infoDict['title'];
    
    # upload new blog content
    #logging.debug("New blog content to upload=\r\n%s", newPostContentUni);
    
    # extract cls
    #<a class="fc03 m2a" href="http://againinput4.blog.163.com/blog/#m=0&t=1&c=fks_084066086082087074083094084095085081083068093095082074085" title="tmp_todo">tmp_todo</a>
        
    # extract bid
    #id:'fks_081075087094087075093094087095085081083068093095082074085',
    foundBid = re.search(r"id:'(?P<bid>fks_\d+)',", postRespHtml);
    if(foundBid) :
        bid = foundBid.group("bid");
        logging.debug("bid=%s", bid);
    else :
        modifyOk = False;
        errInfo = "Can't extract bid from post response html.";
        return (modifyOk, errInfo);
        
    #<a class="fc03 m2a" href="http://againinput4.blog.163.com/blog/#m=0&amp;t=1&amp;c=fks_084066086082085064082082085095085081083068093095082074085" title=
    #hrefP = r'class="fc03 m2a" href="http://\w+\.blog\.163\.com/blog/.+?c=(?P<classId>fks_\d+)" title=';
    hrefP = r'class="fc03 m2a" href="http://.*?blog\.163\.com.+?c=(?P<classId>fks_\d+)" title=';
    foundClassid = re.search(hrefP, postRespHtml);
    if(foundClassid) :
        classId = foundClassid.group("classId");
        logging.debug("classId=%s", classId);
    else :
        modifyOk = False;
        errInfo = "Can't extract classId from post response html.";
        return (modifyOk, errInfo);

    #extract: 
    #<span class="sep fc07">|</span><a class="noul m2a" href="http://againinput4.blog.163.com/blog/getBlog.do?bid=fks_087067093080081074087081085074072087086065083095095071093087">编辑</a>
    #from html
    foundGetblog = re.search(r'class="noul m2a" href="(?P<getBlogUrl>http://\w+?\.blog\.163\.com/blog/getBlog\.do\?bid=fks_\d+)"', postRespHtml);
    if(foundGetblog) :
        getBlogUrl = foundGetblog.group("getBlogUrl");
        logging.debug("getBlogUrl=%s", getBlogUrl);
    else :
        modifyOk = False;
        errInfo = "Can't extract getBlogUrl from post response html.";
        return (modifyOk, errInfo);

    #access:
    #http://againinput4.blog.163.com/blog/getBlog.do?bid=fks_087067093080081074087081085074072087086065083095095071093087
    #to get :
    # <input class="ytag" type="hidden" name="NETEASE_BLOG_TOKEN_EDITBLOG" value="18a51c507a2407ca8a6ee920c8f46d26"/>
    getBlogRespHtml = crifanLib.getUrlRespHtml(getBlogUrl);
    foundEditBlogToken = re.search(r'name="NETEASE_BLOG_TOKEN_EDITBLOG" value="(?P<editBlogToken>\w+)"', getBlogRespHtml);
    if(foundEditBlogToken) :
        editBlogToken = foundEditBlogToken.group("editBlogToken");
        logging.debug("editBlogToken=%s", editBlogToken);
    else :
        modifyOk = False;
        errInfo = "Can't extract NETEASE_BLOG_TOKEN_EDITBLOG from getBlogUrl response html.";
        return (modifyOk, errInfo);

    # now to modify post

    #http://api.blog.163.com/againinput4/editBlogNew.do?p=1&n=0
    modifyPostUrl = "http://api.blog.163.com/" + gVal['blogUser'] + "/editBlogNew.do?p=1&n=0";
    logging.debug("modifyPostUrl=%s", modifyPostUrl);
    
    newPostContentGb18030 = newPostContentUni.encode("GB18030");
    titleGb18030 = title.encode("GB18030");

    postDict = {
        "tag"           : "", #should find original blog tags,
        "cls"           : classId, # 新的分类 的 id, fks_084066086082085064082082085095085081083068093095082074085
        "allowview"     : "-100",
        "refurl"        : "",
        "abstract"      : "",
        "bid"           : bid, #fks_081075087094087074084084086095085081083068093095082074085
        "origClassId"   : classId, # 原先的分类的id
        "origPublishState": "1",
        "oldtitle"      : titleGb18030, #test%E6%9B%B4%E6%96%B0%E5%B8%96%E5%AD%90%E6%B5%8B%E8%AF%952
        "todayPublishedCount": "0",
        #"todayPublishedCount": "1",
        "NETEASE_BLOG_TOKEN_EDITBLOG" : editBlogToken, #e6a5766d73b0daf359a37e9361e11e46
        "title"         : titleGb18030,
        "HEContent"     : newPostContentGb18030,
        "copyPhotos"    : "",
        "suggestedSortedIds": "",
        "suggestedRecomCnt": "",
        "suggestedStyle": "0",
        "isSuggestedEachOther": "0",
        "photoBookImgUrl": "",
        "miniBlogCard"  : "0",
        "p"             : "1",
    };
    
    resp = crifanLib.getUrlResponse(modifyPostUrl, postDict);
    
    #soup = BeautifulSoup(resp, fromEncoding="GB18030");
    #prettifiedSoup = soup.prettify();
    #logging.debug("Modify blog url resp json\n---------------\n%s", prettifiedSoup);
    modifyPostRespHtml = crifanLib.getUrlRespHtml(modifyPostUrl, postDict);
    logging.debug("modify post response html=%s", modifyPostRespHtml);
    
    #return json:
    #modify OK:
    #{r:1,id:’1067120792′,sfx:’blog/static/17279949120120102415384/’}
    #modify fail when need captcha(verify code):
    #{r:-3,id:'',sfx:'/'}
    foundModifyResult = re.search(r"\{r:(?P<retVal>[\-\+\d]+?),id:'(?P<id>\d*?)',sfx:'(?P<sfx>.+?)'\}", modifyPostRespHtml);
    if(foundModifyResult) :
        retVal = foundModifyResult.group("retVal");
        
        if(retVal == "1") :
            modifyOk = True;
        elif(retVal == "-3") :
            modifyOk = False;
            errInfo = u"验证码错误！"; # captcha
        elif(retVal == "-2") :
            modifyOk = False;
            errInfo = u"Token错误！";
        elif(retVal == "-1") :
            modifyOk = False;
            errInfo = u"Referer错误！";
        else:
            modifyOk = False;
            errInfo = u"暂时无法保存日志，请稍后再试！";

        id = foundModifyResult.group("id");
        
        sfx = foundModifyResult.group("sfx");
    else :
        modifyOk = False;
        errInfo = "Can't parse the returned result of modify post.";

    return (modifyOk, errInfo);


#------------------------------------------------------------------------------
if __name__=="BlogNetease":
    print "Imported: %s, %s"%( __name__, __VERSION__);