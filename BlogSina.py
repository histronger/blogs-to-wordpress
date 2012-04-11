#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

For BlogsToWordpress, this file contains the functions for Sina Blog.

[TODO]

【版本历史】
[v1.4]
1.支持处理评论数目超多的帖子，比如：
http://blog.sina.com.cn/s/blog_4701280b0101854o.html -> 2万多个评论
http://blog.sina.com.cn/s/blog_4701280b0102e0p3.html -> 3万多个评论

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

#--------------------------------const values-----------------------------------
__VERSION__ = "v1.4";

gConst = {
    'spaceDomain'  : 'http://blog.sina.com.cn',
}

#----------------------------------global values--------------------------------
gVal = {
    'blogUser'      : '',   # 
    'blogEntryUrl'  : '',   # 
    'cj'            : None, # cookiejar, to store cookies for login mode
}

################################################################################
# Internal Sina Blog Functions 
################################################################################

#------------------------------------------------------------------------------
# pre-process sina post html, then latter the BeautifulSoup can work normally
def beforeCallBeautifulSoup(originalHtml):
    #logging.debug("beforeCallBeautifulSoup originalHtml\n---------------\n%s", originalHtml);

    processedHtml = originalHtml;
    
    # sina post html contain string: "<!–[if lte IE 6]> xxx <![endif]–>"  ->
    # will lead to BeautifulSoup(3.0.4/3.0.6) work abnormally -> 
    # it will parse the input html to single head == 
    # use soup.findAll("head"); will got all content, not the acutual head info ->
    # so follow find(id='xxx') will not work !!!
    # so here repalce them
    processedHtml = processedHtml.replace("<!–[if lte IE 6]>", "");
    processedHtml = processedHtml.replace("<![endif]–>", "");
    
    # handle special case for http://blog.sina.com.cn/s/blog_5058502a01017j3j.html
    processedHtml = processedHtml.replace('<font COLOR="#6D4F19"><font COLOR="#7AAF5A"><font COLOR="#7AAF5A"><font COLOR="#6D4F19"><font COLOR="#7AAF5A"><font COLOR="#7AAF5A">', "");
    processedHtml = processedHtml.replace("</FONT></FONT></FONT></FONT></FONT></FONT>", "");
    
    # processedHtml = processedHtml.replace("<!--$sinatopbar-->", "");
    # processedHtml = processedHtml.replace("<!--$end sinatopbar-->", "");
    
    # processedHtml = processedHtml.replace("<!--第一列start-->", "");
    # processedHtml = processedHtml.replace("<!--$end sinatopbar-->", "");
        
    # # note here both this python file and html should be utf-8
    # processedHtml = processedHtml.replace("<!-- 正文开始 -->", "");
    # processedHtml = processedHtml.replace("<!-- 正文结束 -->", "");
    
    #logging.debug("after beforeCallBeautifulSoup html\n---------------\n%s", processedHtml);
    
    return processedHtml;
    
#------------------------------------------------------------------------------
# convert sina blog post html to soup
def htmlToSoup(html):
    soup = None;
    processedHtml = beforeCallBeautifulSoup(html);
    #logging.debug("after beforeCallBeautifulSoup sina html\n---------------\n%s", processedHtml);
    # Note:
    # (1) after BeautifulSoup process, output html content already is utf-8 encoded
    soup = BeautifulSoup(processedHtml, fromEncoding="UTF-8");
    #soup = BeautifulSoup(processedHtml);
    #prettifiedSoup = soup.prettify();
    #logging.debug("htmlToSoup prettifiedSoup\n---------------\n%s", prettifiedSoup);
    
    return soup;

################################################################################
# Implemented Common Functions 
################################################################################

#------------------------------------------------------------------------------
#extract baidu blog user name, possibility:
# (1) extract crifan2008 from url: 
# http://blog.sina.com.cn/crifan2008
# http://blog.sina.com.cn/crifan2008/
# (2) or given any blog url, such as:
# http://blog.sina.com.cn/s/blog_3d55a9b70100nyl8.html
# http://blog.sina.com.cn/s/blog_5ed55f980102e617.html?tj=1
# extract http://blog.sina.com.cn/crifan2008
# from its html code
# (3) extract 2671017827 from:
# http://blog.sina.com.cn/u/2671017827
def extractBlogUser(inputUrl):
    (extractOk, extractedBlogUser, generatedBlogEntryUrl) = (False, "", "");

    logging.debug("Extracting blog user from url=%s", inputUrl);
    
    try :
        # type1, main url: 
        #http://blog.sina.com.cn/crifan2008
        #http://blog.sina.com.cn/crifan2008/
        foundMainUrl = re.search("(?P<mainUrl>http://blog\.sina\.com\.cn/(?P<username>\w+))/?$", inputUrl);
        if(foundMainUrl) :
            extractedBlogUser = foundMainUrl.group("username");
            generatedBlogEntryUrl = foundMainUrl.group("mainUrl");
            extractOk = True;
        
        # type2, main url:
        #http://blog.sina.com.cn/u/2671017827
        #http://blog.sina.com.cn/u/2671017827/
        if(not extractOk):
            foundUnumber = re.search("(?P<urlNoSlash>http://blog\.sina\.com\.cn/u/(?P<number>\d+))/?$", inputUrl);
            if(foundUnumber) :
                extractedBlogUser = foundUnumber.group("number");
                generatedBlogEntryUrl = foundUnumber.group("urlNoSlash");
                extractOk = True;

        # type3, some post url:
        #http://blog.sina.com.cn/s/blog_3d55a9b70100nyl8.html
        #http://blog.sina.com.cn/s/blog_5ed55f980102e617.html?tj=1
        if(not extractOk):
            foundPostLink = re.search("(?P<postUrl>http://blog\.sina\.com\.cn/s/blog_\w+\.html).*?", inputUrl);
            if(foundPostLink) :
                postUrl = foundPostLink.group("postUrl");
                respHtml = crifanLib.getUrlRespHtml(postUrl);
                soup = htmlToSoup(respHtml);
                blogname = soup.find(id='blogname');
                if blogname and blogname.a :
                    href = blogname.a['href']; #http://blog.sina.com.cn/crifan2008
                    extractedMainUrl = href; 
                    splitedList = extractedMainUrl.split("/");
                    extractedBlogUser = splitedList[3];
                    generatedBlogEntryUrl = extractedMainUrl;
                    extractOk = True;

    except :
        (extractOk, extractedBlogUser, generatedBlogEntryUrl) = (False, "", "");
        
    if (extractOk) :
        gVal['blogUser'] = extractedBlogUser;
        gVal['blogEntryUrl'] = generatedBlogEntryUrl;
        
    return (extractOk, extractedBlogUser, generatedBlogEntryUrl);

#------------------------------------------------------------------------------
# find the first permanent link = url of the earliset published blog item
def find1stPermalink():
    (isFound, errInfo) = (False, "Unknown error!");
    
    try:
        # 1. open main url
        respHtml = crifanLib.getUrlRespHtml(gVal['blogEntryUrl']);

        # 2. extract:    
        #<span><a  href="http://blog.sina.com.cn/s/articlelist_1029024183_0_1.html">博文目录</a></span>
        # Note: here both sina blog use UTF-8, and here current python file is also UTF-8 => then follow can match
        foundBlogCatalog = re.search('<span><a.+?href="(?P<urlPre>http.+?)1\.html">博文目录</a></span>', respHtml);
        
        #print "foundBlogCatalog=",foundBlogCatalog;
        if(foundBlogCatalog) :
            urlPre = foundBlogCatalog.group("urlPre");
            logging.debug("urlPre=%s", urlPre);
            
            # 3. generate the oldest url:
            # http://blog.sina.com.cn/s/articlelist_1029024183_0_100000.html
            maxPageIdx = 10000;
            oldestPageUrl = urlPre + str(maxPageIdx) + ".html";
            logging.debug("oldestPageUrl=%s", oldestPageUrl);
                        
            # 4. open the last url:
            # http://blog.sina.com.cn/s/blog_3d55a9b70100b0z0.html
            respHtml = crifanLib.getUrlRespHtml(oldestPageUrl);
            #logging.debug("---sina %s html---\n%s", oldestPageUrl, respHtml);
            
            # 5. and extract the earliest url
            
            # eg1:
            #<span class="atc_title">
            #                               <a title="国内常见博客的采集办法(搜狐&nbsp;网易&nbsp;新浪&nbsp;百度空间)，免费写采集规则！" target="_blank" href="http://blog.sina.com.cn/s/blog_40e4b5660100sk8m.html">国内常见博客的采集办法(搜狐&nbsp;网易…</a></span> 
            #                            <span class="atc_ic_b"></span>
            
            #eg2:
            #<span class="atc_title">
            #                                <a title="[转载]钱云会手表视频被编辑的铁证-倒地瞬间闪现奇异" target="_blank" href="http://blog.sina.com.cn/s/blog_3d55a9b70100phmr.html">[转载]钱云会手表视频被编辑的铁证…</a></span> 
            #                            <span class="atc_ic_b"><img class="SG_icon SG_icon18" src="http://simg.sinajs.cn/blog7style/images/common/sg_trans.gif" width="15" height="15" title="此博文包含图片" align="absmiddle" /></span>
            
            soup = htmlToSoup(respHtml);
            foundUrls = soup.findAll(attrs={"class":"atc_title"});
            if(foundUrls and len(foundUrls) > 0 ) :
                lastFoundUrl = foundUrls[-1];
                fristLink = lastFoundUrl.a['href'];

                isFound = True;
                return (isFound, fristLink);
        else :
            isFound = False;
            errInfo = u"Can not found the blog catalog url !";
    except:
        (isFound, errInfo) = (False, "Unknown error!");
    
    return (isFound, errInfo);

#------------------------------------------------------------------------------
# extract title fom url, html
def extractTitle(url, html):
    titleUni = "";
    try :
        soup = htmlToSoup(html);
        
        #<h2 id="t_3d55a9b70100nyl8" class="titName SG_txta">[转载]学习笔记之三年自然灾害</h2>
        titName = soup.find(attrs={"class":"titName SG_txta"});
        if(titName) :
            titleStr = titName.string;
            titleUni = unicode(titleStr);
    except : 
        titleUni = "";
        
    return titleUni;

#------------------------------------------------------------------------------
# find next permanent link from url, html
def findNextPermaLink(url, html) :
    nextLinkStr = '';
        
    try :
        #<div><span class="SG_txtb">后一篇：</span><a href="http://blog.sina.com.cn/s/blog_3d55a9b70100iakf.html">缺点</a></div>
        match = re.search('<div><span\s+?class="SG_txtb">后一篇：</span><a href="(?P<href>.+?)">(?P<title>.+?)</a></div>', html);
        nextPostTitle = "";
        if match:
            href = match.group("href");
            nextLinkStr = href;
            
            nextPostTitle = match.group("title");

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
        #<span class="time SG_txtc">(2008-10-12 22:14:05)</span>
        match = re.search('<span\s+?class="time SG_txtc">\((?P<datetime>.+?)\)</span>', html);
        if match:
            datetimeStr = match.group("datetime");
    except :
        datetimeStr = "";
        
    return datetimeStr;

#------------------------------------------------------------------------------
# extract blog item content fom url, html
def extractContent(url, html) :
    contentStr = '';
    try :
        #logging.debug("---before extractContent html :\n%s", html);
        soup = htmlToSoup(html);
    
        #prettifiedSoup = soup.prettify();
        #logging.debug("---in extractContent prettifiedSoup :\n%s", prettifiedSoup);
        #foundContent = soup.find(attrs={"class":"articalContent"}); # not work here !!!
        foundContent = soup.find(id="sina_keyword_ad_area2");
        #logging.debug("---soup foundContent:\n%s", foundContent);
        
        # <div id="sina_keyword_ad_area2" class="articalContent  ">
        # ..................
        # </div>

        #method 1
        mappedContents = map(CData, foundContent.contents);
        #print "type(mappedContents)=",type(mappedContents); #type(mappedContents)= <type 'list'>
        contentStr = ''.join(mappedContents);
        
        # #method 2
        # originBlogContent = "";
        # logging.debug("Total %d contents for original blog contents:", len(foundContent.contents));
        # for i, content in enumerate(foundContent.contents):
            # if(content):
                # logging.debug("[%d]=%s", i, content);
                # originBlogContent += unicode(content);
            # else :
                # logging.debug("[%d] is null", i);
        
        #logging.debug("---method 1: map and join---\n%s", contentStr);
        # logging.debug("---method 2: enumerate   ---\n%s", originBlogContent);
    except :
        contentStr = '';

    return contentStr;

#------------------------------------------------------------------------------
# extract category from url, html
def extractCategory(url, html) :
    catUni = '';
    try :
        soup = htmlToSoup(html);
        # <td class="blog_class">
                                # <span class="SG_txtb">分类：</span>
            # <a target="_blank" href="http://blog.sina.com.cn/s/articlelist_1029024183_2_1.html">随写</a>
                            # </td>    

        # when no catagory:
        # <td class="blog_class">
                            # </td>
        foundClass = soup.find(attrs={"class":"blog_class"});
        if(foundClass.a) :
            classStr = foundClass.a.string;
            catUni = unicode(classStr);
    except :
        catUni = "";

    return catUni;

#------------------------------------------------------------------------------
# extract tags info from url, html
def extractTags(url, html) :
    tagList = [];
    try :
        soup = htmlToSoup(html);
        
        # <td class="blog_tag">
        # <script>
        # var $tag='转载';
        # var $tag_code='7d11115e8449fbe2e0bc2d8209f42278';
        # var $r_quote_bligid='450ffd6501000d3y';
        # var $worldcup='0';
        # var $worldcupball='0';
        # </script>
                                # <span class="SG_txtb">标签：</span>
                                                                    # <h3><a href="http://uni.sina.com.cn/c.php?t=blog&k=%D7%AA%D4%D8&ts=bpost&stype=tag" target="_blank">转载</a></h3>
                                                    # </td>
        blogTag = soup.find(attrs={"class":"blog_tag"});
        h3List = blogTag.h3;
        
        for h3 in h3List :
            tagList.append(h3.string);
    except :
        tagList = [];

    return tagList;

#------------------------------------------------------------------------------
# add fake head and tail for latter BeautifulSoup to process
def genFakeHtml(parsedHtml):
    fakeHead = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Fake Title</title>
<body>
""";

    fakeTail = """
</body>
</head>
</html>
    """;

    fakeHtml = fakeHead + parsedHtml + fakeTail;

    return fakeHtml;

#------------------------------------------------------------------------------
# parse to real html
# input is backslash style html string
def parseHtml(backslashDataStr) :
    parsedHtml = backslashDataStr;
    
    parsedHtml = parsedHtml.replace("\\t", "\t");
    parsedHtml = parsedHtml.replace("\\r\\n", "\r\n");
    parsedHtml = parsedHtml.replace("\\/", "/");
    parsedHtml = parsedHtml.replace('\\"', '"');
    #logging.debug("after html parse: \n%s", parsedHtml);

    return parsedHtml;

#------------------------------------------------------------------------------
# parse comment 'data' field string to comment dict info
def parseCmtDataStr(dataStr, startNum):
    cmtDictList = [];
    
    #logging.debug("data str in cmt json: \n%s", dataStr);
    parsedHtml = parseHtml(dataStr);
    fakeHtml = genFakeHtml(parsedHtml);
    soup = BeautifulSoup(fakeHtml);
    
    cmtList = soup.findAll(attrs={"class":"SG_revert_Cont"});
    
    for (cmtIdx, singleCmt) in enumerate(cmtList) :
        destCmtDict = {};
        
        cmtNum = cmtIdx + 1;
        cmtId = cmtNum + startNum;
        
        # init to null, log it while error
        SG_revert = None;
        SG_revert_Tit = None;
        cmtTitleUrl = "";
        cmtTitle = "";
        decoedCmtTitle = "";
        SG_revert_Time = None;
        datetimeStr = "";
        parsedLocalTime = None;
        gmtTime = None;
        SG_txtb = None;
        mappedContents = None;
        cmtContent = "";
        decodedCmtContent = "";
        
        try:
            destCmtDict['id'] = cmtId;
            
            logging.debug("--- comment[%d] ---", destCmtDict['id']);
            
            SG_revert = singleCmt.p;
            
            SG_revert_Tit = SG_revert.find(attrs={"class":"SG_revert_Tit"});
            #cmtTitleUrl = "";
            if SG_revert_Tit.a :
                SG_revert_Tit_a = SG_revert_Tit.a;
                cmtTitle = SG_revert_Tit_a.string;
                #print "a.string OK, cmtTitle=",cmtTitle;
                
                cmtTitleUrl = SG_revert_Tit_a['href'];
            else :
                cmtTitle = SG_revert_Tit.string;

            # for special:
            # the 980th in comment http://blog.sina.com.cn/s/blog_4701280b0101854o.html not contain title 
            # => SG_revert_Tit_a.string is empty
            # => follow cmtTitle.decode('unicode-escape') will fail
            # => set a fake title if is empty
            if(not cmtTitle) :
                cmtTitle = "Nobody";

            decoedCmtTitle = cmtTitle.decode('unicode-escape');
            destCmtDict['author'] = decoedCmtTitle;
            
            destCmtDict['author_url'] = cmtTitleUrl;
            
            SG_revert_Time = SG_revert.find(attrs={"class":"SG_revert_Time"});
            datetimeStr = SG_revert_Time.em.string;
            
            parsedLocalTime = datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S'); #2012-03-29 09:52:17
            gmtTime = crifanLib.convertLocalToGmt(parsedLocalTime);
            destCmtDict['date'] = parsedLocalTime.strftime("%Y-%m-%d %H:%M:%S");
            destCmtDict['date_gmt'] = gmtTime.strftime("%Y-%m-%d %H:%M:%S");
            
            SG_txtb = singleCmt.div;
            
            mappedContents = map(CData, SG_txtb.contents);
            cmtContent = ''.join(mappedContents);
            
            decodedCmtContent = cmtContent.decode('unicode-escape');
            destCmtDict['content'] = decodedCmtContent;

            destCmtDict['author_email'] = "";
            destCmtDict['author_IP'] = "";
            #destCmtDict['approved'] = 1;
            #destCmtDict['type'] = '';
            destCmtDict['parent'] = 0;
            #destCmtDict['user_id'] = 0;
            
            logging.debug("author=%s", destCmtDict['author']);
            logging.debug("author_url=%s", destCmtDict['author_url']);
            logging.debug("date=%s", destCmtDict['date']);
            logging.debug("date_gmt=%s", destCmtDict['date_gmt']);
            logging.debug("content=%s", destCmtDict['content']);
            
            cmtDictList.append(destCmtDict);
            #print "single comment parse OK: %d"%(cmtId);
        except:
            logging.debug("Error while parse single comment %d", cmtId);
            logging.debug("-------- detailed single comment info --------");
            logging.debug("SG_revert=%s", SG_revert);
            logging.debug("SG_revert_Tit=%s", SG_revert_Tit);
            logging.debug("cmtTitleUrl=%s", cmtTitleUrl);
            logging.debug("decoedCmtTitle=%s", decoedCmtTitle);
            logging.debug("SG_revert_Time=%s", SG_revert_Time);
            logging.debug("datetimeStr=%s", datetimeStr);
            logging.debug("parsedLocalTime=%s", parsedLocalTime);
            logging.debug("gmtTime=%s", gmtTime);
            logging.debug("SG_txtb=%s", SG_txtb);
            logging.debug("mappedContents=%s", mappedContents);
            logging.debug("cmtContent=%s", cmtContent);
            logging.debug("decodedCmtContent=%s", decodedCmtContent);
            logging.debug("-------- detailed single comment info --------");

            #print "%d singleCmt error"%(cmtId);
            break;

    return cmtDictList;

#------------------------------------------------------------------------------
# extract post ID
# from :
# http://blog.sina.com.cn/s/blog_56c89b680102dynu.html
# extract the 56c89b680102dynu
def extractPostId(sinaPostUrl):
    postId = "";
    foundPostId = re.search("http://blog\.sina\.com\.cn/s/blog_(?P<postId>\w+)\.html$", sinaPostUrl);
    if(foundPostId) :
        postId = foundPostId.group("postId");
    return postId;

#------------------------------------------------------------------------------
# get valid data field/string in returned in json string for comment url
def getCmtJson(cmtUrl):
    logging.debug("fetch comment from url %s", cmtUrl);
    (gotOk, cmtDataJsonStr) = (False, "");
    respJson = "";

    # sometime due to network error, fetch comment json string will fail, so here do several try
    maxRetryNum = 3;
    for tries in range(maxRetryNum) :
        try :
            #respJson = crifanLib.getUrlRespHtml(cmtUrl);
            respJson = crifanLib.getUrlRespHtml(cmtUrl, timeout=20); # add timeout to avoid dead(no response for ever) !
            logging.debug("Successfully got comment json string from %s", cmtUrl);
            break # successfully, so break now
        except :
            if tries < (maxRetryNum - 1) :
                logging.warning("    Fail to fetch comment json string from %s, do %d retry", cmtUrl, (tries + 1));
                continue;
            else : # last try also failed, so exit
                logging.warning("    All %d times failed for try to fetch comment json from %s !", maxRetryNum, cmtUrl);
                break;

    if(respJson) :
        #logging.debug("Comment url ret json: \n%s", respJson);
        # extract returned data field
        foundData = re.search('{"code":"A00006",data:"(?P<dataStr>.+)"}$', respJson);
        if (foundData) :
            dataStr = foundData.group("dataStr");
            # 1. no comments:
            #{"code":"A00006",data:"\u535a\u4e3b\u5df2\u5173\u95ed\u8bc4\u8bba"}
            if(dataStr == "\\u535a\\u4e3b\\u5df2\\u5173\\u95ed\\u8bc4\\u8bba") :
                # 博主已关闭评论
                (gotOk, cmtDataJsonStr) = (False, "");
                decodedDataStr = dataStr.decode("unicode-escape");
                logging.debug("comment url %s return %s", cmtUrl, decodedDataStr);
            elif (dataStr.find('class=\\"noCommdate\\"') > 0) :
                # 2. no more comment
                #{"code":"A00006",data:"<li><div class=\"noCommdate\">........
                (gotOk, cmtDataJsonStr) = (False, "");
                logging.debug("comment url %s return no more comments", cmtUrl);
            else :
                # contain valid comment
                gotOk = True;
                cmtDataJsonStr = dataStr;
                logging.debug("Got valid comment code json string");
        else:
            logging.debug("Found returned invalid comment code json string=%s", respJson);

    return (gotOk, cmtDataJsonStr);

#------------------------------------------------------------------------------
# fetch and parse comments 
# return the parsed dict value
def fetchAndParseComments(url, html):
    parsedCommentsList = [];
   
    # for output info use
    maxNumReportOnce = 200;
    lastRepTime = 0;
    
    try :
        postId = extractPostId(url);
        needGetMore = True;
        cmtPageNum = 1;
        
        while needGetMore :
            # from :
            # http://blog.sina.com.cn/s/blog_56c89b680102dynu.html
            # generate the comment url:
            #http://blog.sina.com.cn/s/comment_56c89b680102dynu_1.html
            cmtUrl = "http://blog.sina.com.cn/s/comment_" + postId + "_" + str(cmtPageNum) + ".html";
            #print "cmtUrl=",cmtUrl;
            (gotOK, cmtDataJsonStr) = getCmtJson(cmtUrl);
            if(gotOK) :
                cmtIdStartNum = len(parsedCommentsList);
                cmdDictList = parseCmtDataStr(cmtDataJsonStr, cmtIdStartNum);
                for eachCmtDict in cmdDictList :
                    parsedCommentsList.append(eachCmtDict);
                    
                    # report processed comments if exceed certain number
                    parsedCmtLen = len(parsedCommentsList);
                    curRepTime = parsedCmtLen/maxNumReportOnce;
                    if(curRepTime != lastRepTime) :
                        # report
                        logging.info("    Has processed comments: %5d", parsedCmtLen);
                        # update
                        lastRepTime = curRepTime;

                cmtPageNum += 1;
            else :
                needGetMore = False;

    except :
        logging.debug("Error while fetch and parse comment for %s", url);

    return parsedCommentsList;

#------------------------------------------------------------------------------
# check whether is self blog pic
# depend on following picInfoDict definition
def isSelfBlogPic(picInfoDict):
    isSelfPic = False;

    # currently only support sina own pic, so here always True
    isSelfPic = True;

    return isSelfPic;

#------------------------------------------------------------------------------
# generate the file name for other pic
# depend on following picInfoDict definition
def genNewOtherPicName(picInfoDict):
    newOtherPicName = "";
    
    filename = picInfoDict['filename'];
    fd1 = picInfoDict['fields']['fd1'];
    #fd2 = picInfoDict['fields']['fd2'];
    #fd3 = picInfoDict['fields']['fd3'];
    
    #newOtherPicName = fd1 + '_' + fd2 + "_" + filename;
    newOtherPicName = fd1 + "_" + filename;
    
    print "newOtherPicName=",newOtherPicName;

    return newOtherPicName;

#------------------------------------------------------------------------------
# get the found pic info after re.search
# foundPic is MatchObject
def getFoundPicInfo(foundPic):
    #print "In getFoundPicInfo:";
    
    # here should corresponding to singlePicUrlPat in processPicCfgDict
    picUrl  = foundPic.group(0);
    #print "picUrl=",picUrl;
    fd1     = foundPic.group("fd1"); # for sina pic, is s9/s14/i0/...
    #fd2     = foundPic.group("fd2"); # for sina pic, is sinaimg
    #fd3     = foundPic.group("fd3"); # for sina pic, is cn
    filename= foundPic.group("filename"); #3d55a9b7g9522d474a84d, not 3d55a9b7g9522d474a84d&amp;690
    #print "filename=",filename;
    #3d55a9b7g9522d474a84d&amp;690 -> 3d55a9b7g9522d474a84d_690
    #filename = filename.replace("&amp;", "_");
    #print "filename=",filename;

    #suffix  = foundPic.group("suffix");
    suffix = "";
    #print "suffix=",suffix;
    
    picInfoDict = {
        'isSupportedPic': False,
        'picUrl'        : picUrl,
        'filename'      : filename,
        'suffix'        : suffix, # empty for sina pic url: http://s14.sinaimg.cn/middle/3d55a9b7g9522d474a84d&690
        'fields'        : 
            {
                'fd1' : fd1,
                #'fd2' : fd2,
                #'fd3' : fd3,
            },
    };
    
    # if (suffix in crifanLib.getPicSufList()) :
        # picInfoDict['isSupportedPic'] = True;
    # else :
        # # for special sina pic
        # if(fd2 == "sinaimg") :
            # picInfoDict['isSupportedPic'] = True;

    # if match, must be sinaimg
    picInfoDict['isSupportedPic'] = True;
    #print "getFoundPicInfo: picInfoDict=",picInfoDict;

    return picInfoDict;

#------------------------------------------------------------------------------
def getProcessPhotoCfg():
    # possible own site pic link:
    # type1:
    # http://s13.sinaimg.cn/middle/5058502aga539c8797adc&amp;690 == http://s13.sinaimg.cn/middle/5058502aga539c8797adc&690
    # http://s8.sinaimg.cn/middle/5058502aga539ca24bca7&amp;690
    # type2:
    # http://blog.sina.com.cn/s/blog_48ace2830100aucb.html contain
    # http://s4.sinaimg.cn/bmiddle/48ace283t5925f0b45813
    # type3:
    # http://s9.sinaimg.cn/orignal/6f75ca11tbc32765138a8&690

    # tmp not support:
    # http://i0.sinaimg.cn/ent/v/m/2012-03-29/U6203P28T3D3593517F328DT20120329160927.jpg
    # 
    
    # possible othersite pic url:
    
    
    # <a href="http://photo.blog.sina.com.cn/showpic.html#blogid=3d55a9b70100n8d4&url=http://s14.sinaimg.cn/orignal/3d55a9b7g9522d474a84d" TARGET="_blank"><img src="http://simg.sinajs.cn/blog7style/images/common/sg_trans.gif" real_src ="http://s14.sinaimg.cn/middle/3d55a9b7g9522d474a84d&amp;690"  ALT="【已解决】打开word文档出错&nbsp;<wbr>/&nbsp;<wbr>如何修复损坏的word文档"  TITLE="【已解决】打开word文档出错&nbsp;<wbr>/&nbsp;<wbr>如何修复损坏的word文档" /></A>
    
    #<p ALIGN="center"><img src="http://simg.sinajs.cn/blog7style/images/common/sg_trans.gif" real_src ="http://s9.sinaimg.cn/orignal/6f75ca11tb68f63636ef8&amp;690"  ALT="京城路光影路故宫&nbsp;<wbr>（原创）"  TITLE="京城路光影路故宫&nbsp;<wbr>（原创）" /></P>
    
    picSufChars = crifanLib.getPicSufChars();
    processPicCfgDict = {
        # here only extract last pic name contain: char,digit,-,_
        #'allPicUrlPat'      : r'http://\w+\.\w+\.\w+/([\w%\-=]*/)+[\w\-\.&;^"]+'  + r'\.[' + picSufChars + r']{3,4}',
        #                                            field2     field3                                4=filename                     5=suffix
        #'singlePicUrlPat'   : r'http://\w+\.(?P<fd2>\w+)\.(?P<fd3>\w+)(\.(?P<fd4>\w+))?/[\w%\-=]*[/]?[\w\-/%=]*/(?P<filename>[\w\-\.&;]{1,100})' + r'(\.(?P<suffix>[' + picSufChars + r']{3,4}))?',

        # currently only support sina self blog middle type pic
        #'allPicUrlPat'     : r'http://\w+?\.sinaimg\.cn/middle/\w+?&amp;\d+',
        #'allPicUrlPat'     : r'http://\w+?\.sinaimg\.cn/\w*?middle/\w+[&]?[amp;]{0,4}\d{0,3}',
        'allPicUrlPat'     : r'http://\w+?\.sinaimg\.cn/\w+/\w+[&]?[amp;]{0,4}\d{0,3}',
        #                                      fd1                             filename                
        #'singlePicUrlPat'  : r'http://(?P<fd1>\w+?)\.sinaimg\.cn/middle/(?P<filename>\w+?)&amp;\d+',
        #'singlePicUrlPat'  : r'http://(?P<fd1>\w+?)\.sinaimg\.cn/\w*?middle/(?P<filename>\w+)(&amp;\d+)?',
        'singlePicUrlPat'  : r'http://(?P<fd1>\w+?)\.sinaimg\.cn/\w+/(?P<filename>\w+)(&amp;\d+)?',
        
        'getFoundPicInfo'       : getFoundPicInfo,
        'isSelfBlogPic'         : isSelfBlogPic,
        'genNewOtherPicName'    : genNewOtherPicName,
    };
    
    return processPicCfgDict;

#------------------------------------------------------------------------------
# extract blog title and description
def extractBlogTitAndDesc(blogEntryUrl) :
    (blogTitle, blogDescription) = ("", "");
    
    #print "blogEntryUrl=",blogEntryUrl;

    respHtml = crifanLib.getUrlRespHtml(blogEntryUrl);
    soup = htmlToSoup(respHtml);
    
    # <div id="blogTitle" class="blogtoparea">
    # <h1 id="blogname" class="blogtitle"><a href="http://blog.sina.com.cn/joyphotography"><span id="blognamespan">.</span></a></h1>
    # <div id="bloglink" class="bloglink"><a href="http://blog.sina.com.cn/joyphotography">http://blog.sina.com.cn/joyphotography</a>  <a onclick="return false;" class="CP_a_fuc" href="#" id="SubscribeNewRss">[<cite>订阅</cite>]</a><a class="CP_a_fuc" href="javascript:void(scope.pa_add.add('1347964970'));">[<cite>手机订阅</cite>]</a></div>
    # </div>
    
    # <div id="blogTitle" class="blogtoparea">
    # <h1 id="blogname" class="blogtitle"><a href="http://blog.sina.com.cn/crifan2008"><span id="blognamespan">crifan.com</span></a></h1>
    # <div id="bloglink" class="bloglink"><a href="http://blog.sina.com.cn/crifan2008">http://blog.sina.com.cn/crifan2008</a>  <a onclick="return false;" class="CP_a_fuc" href="#" id="SubscribeNewRss">[<cite>订阅</cite>]</a><a class="CP_a_fuc" href="javascript:void(scope.pa_add.add('1029024183'));">[<cite>手机订阅</cite>]</a></div>
    # </div>

    try:
        foundTitle = soup.find(attrs={"class":"blogtitle"}); 
        foundTitleA = foundTitle.a;
        foundTitleSpan = foundTitleA.span;
        titStr = foundTitleSpan.string;
        blogTitle = unicode(titStr);
        
        blogDescription = "";
    except:
        (blogTitle, blogDescription) = ("", "");

    return (blogTitle, blogDescription);

#------------------------------------------------------------------------------
# possible date format:
# (1) 2012-03-30 08:32:31
def parseDatetimeStrToLocalTime(datetimeStr):
    parsedLocalTime = datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S') # here is GMT+8 local time
    #print "parsedLocalTime=",parsedLocalTime;
    return parsedLocalTime;


####### Login Mode ######

#------------------------------------------------------------------------------
# log in blog
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
    
    return (modifyOk, errInfo);

#------------------------------------------------------------------------------   
if __name__=="BlogSina":
    print "Imported: %s,\t%s"%( __name__, __VERSION__);