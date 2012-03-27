#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
【简介】
此脚本：
对所支持的博客提供商：
1. 百度空间
2. 网易163
支持如下功能：
1. 导出为WXR
将博客中的的帖子的全部信息，导出为WXR(WordPress eXtended RSS)文件，其中：
（1）此处所说帖子的信息，包含：标题(title)，发布时间(datetime)，内容(content)，分类(category)，标签(tags)，评论(comments)，图片(picture)等。
（2）关于帖子的内容，还可以根据设置而进行相应处理，包括下载本博客的图片(self blog picture)和别的地址的图片(other picture)，并且替换对应的图片地址为所设置的地址等。
2. 修改帖子内容
在给定用户名密码的前提下，对于每个帖子，将原先帖子内容修改为所设置的新的内容。
（1）暂时只支持修改百度空间的帖子，不支持修改网易163的博客的帖子。

【使用说明】
更多相关信息，以及详细的使用说明，请去这里：
BlogsToWordPress：将百度空间，网易163等博客搬家到WordPress
http://www.crifan.com/crifan_released_all/website/python/blogstowordpress/

【版本信息】
版本：     v3.0
作者：     crifan
联系方式： admin (at) crifan.com

【其他】
1.关于WXR：
WXR(WordPress eXtended Rss)简介
http://www.crifan.com/2012/03/23/simple_introduction_about_wxr_wordpress_extended_rss/

【TODO】
1.增加对于friendOnly类型帖子的支持。
2.支持自定义导出特定类型的帖子为public和private。
3.有机会，去实现其他博客的支持，比如新浪（sina）博客，QQ空间等。
4.支持设置导出WXR帖子时的顺序：正序和倒序。

-------------------------------------------------------------------------------
"""

#---------------------------------import---------------------------------------
import os;
import re;
import sys;
import math;
import time;
import codecs;
import pickle;
import logging;
import urllib;
import urllib2;
from BeautifulSoup import BeautifulSoup,Tag,CData;
from datetime import datetime,timedelta;
from optparse import OptionParser;
from string import Template,replace;
import xml;
from xml.sax import saxutils;
import crifanLib;
import BlogNetease;
import BlogBaidu;

#--------------------------------const values-----------------------------------
__VERSION__ = "v3.0";


gConst = {
    'generator'         : "http://www.crifan.com",
    'tailInfo'          : """

    </channel>
    </rss>""",
    'picRootPathInWP'   : "http://localhost/wordpress/wp-content/uploads",
    # also belong to ContentTypes, more info can refer: http://kenya.bokee.com/3200033.html
    # here use Tuple to avoid unexpected change
    # note: for tuple, refer item use tuple[i], not tuple(i)
    'validPicSufList'   : ('bmp', 'gif', 'jpeg', 'jpg', 'jpe', 'png', 'tiff', 'tif'),
    'othersiteDirName'  : 'other_site',
    
    'prodiverBaidu'     : 'Baidu',
    'prodiverNetease'   : 'Netease',
};

#----------------------------------global values--------------------------------
gVal = {
    'blogProvider'          : None,
    'postList'              : [],
    'catNiceDict'           : {}, # store { catName: catNiceName}
    'tagSlugDict'           : {}, # store { tagName: tagSlug}
    'postID'                : 0,
    'blogUser'              : '',
    'blogEntryUrl'          : '',
    'processedUrlList'      : [],
    'processedStUrlList'    : [],
    'replacedUrlDict'       : {},
    'exportFileName'        : '',
    'fullHeadInfo'          : '', #  include : header + category + generator
    'statInfoDict'          : {}, # store statistic info
    'errorUrlList'          : [], # store the (pic) url, which error while open
    'picSufStr'             : '', # store the pic suffix char list
    'postModifyPattern'     : '', # the string, after repalce the pattern, used for each post
};

#--------------------------configurable values---------------------------------
gCfg ={
# For defalut setting for following config value, please refer parameters.
    # where to save the downloaded pictures
    # Default (in code) set to: gConst['picRootPathInWP'] + '/' + gVal['blogUser'] + "/pic"
    'picPathInWP'       : '',
    # Default (in code) set to: gCfg['picPathInWP'] + '/' + gConst['othersiteDirName']
    'otherPicPathInWP'  : '',
    # process pictures or not
    'processPic'        : '',
    # process other site pic or not
    'processOtherPic'   : '',
    # omit process pic, which is similar before errored one
    'omitSimErrUrl'     : '',
    # do translate or not
    'googleTrans'           : '',
    # process comments or not
    'processCmt'        : '',
    # post ID prefix address
    'postPrefAddr'     : '',
    # max/limit size for output XML file
    'maxXmlSize'        : 0,
    # function execute times == max retry number + 1
    # when fail to do something: fetch page/get comment/....) 
    'funcTotalExecNum'  : 1,
    
    'username'          : '',
    'password'          : '',
    'postTypeToProcess' : '',
    'processType'       : '',
    
    # for modify post, auto jump over the post of 
    # baidu: "文章内容包含不合适内容，请检查", "文章标题包含不合适内容，请检查"
    # 163 : TODO
    'autoJumpSensitivePost' : '',
    
    'postEncoding'      : '',
};

#--------------------------functions--------------------------------------------

#------------------------------------------------------------------------------
# just print whole line
def printDelimiterLine() :
    logging.info("%s", '-'*80);
    return 

#------------------------------------------------------------------------------
# open export file name in rw mode, return file handler
def openExportFile():
    global gVal;
    # 'a+': read,write,append
    # 'w' : clear before, then write
    return codecs.open(gVal['exportFileName'], 'a+', 'utf-8');

#------------------------------------------------------------------------------
# just create output file
def createOutputFile():
    global gVal;
    gVal['exportFileName'] = "WXR_" + gVal['blogProvider'] + '_[' + gVal['blogUser'] + "]_" + datetime.now().strftime('%Y%m%d_%H%M')+ '-0' + '.xml';
    f = codecs.open(gVal['exportFileName'], 'w', 'utf-8');
    if f:
        logging.info('Created export WXR file: %s', gVal['exportFileName']);
        f.close();
    else:
        logging.error("Can not open writable exported WXR file: %s", gVal['exportFileName']);
        sys.exit(2);
    return;

#------------------------------------------------------------------------------
# add CDATA, also validate it for xml
def packageCDATA(info):
    #info = saxutils.escape('<![CDATA[' + info + ']]>');
    info = '<![CDATA[' + info + ']]>';
    return info;

#------------------------------------------------------------------------------
# 1. extract picture URL from blog content
# 2. process it:
#       remove overlapped 
#       remove processed
#       saved into the gVal['processedUrlList']
#       download
#       replace url
def processPhotos(blogContent):
    global gVal;
    global gCfg;
    global gConst;

    if gCfg['processPic'] == 'yes' :
        try :
            crifanLib.calcTimeStart("process_all_picture");
            logging.debug("Begin to process all pictures");

            processPicCfgDict = {
                'allPicUrlNoSufPat'     : r"",  # search pattern for all pic, should not include '()'
                'singlePicUrlNoSufPat'  : r"",  # search pattern for single pic, should inclde '()'
                'getFoundPicInfo'       : None, # get the found pic info after re.search
                'isSelfBlogPic'         : None, # func to check whether is self blog pic
                'genNewOtherPicName'    : None, # generate the new name for other pic
            };

            processPicCfgDict = getProcessPhotoCfg();
            #print "processPicCfgDict=",processPicCfgDict;
  
            allUalPattern = processPicCfgDict['allPicUrlNoSufPat'] + r'\.[' + gVal['picSufStr'] + r']{3,4}';
            #print "allUalPattern=",allUalPattern;

            # if matched, result for findall() is a list when no () in pattern
            matchedList = re.findall(allUalPattern, blogContent);
            if matchedList :
                nonOverlapList = crifanLib.uniqueList(matchedList); # remove processed
                # remove processed and got ones that has been processed
                (filteredPicList, existedList) = crifanLib.filterList(nonOverlapList, gVal['processedUrlList']);
                if filteredPicList :
                    logging.debug("Filtered url list to process:\n%s", filteredPicList);
                    for curUrl in filteredPicList :
                        # to check is similar, only when need check and the list it not empty
                        if ((gCfg['omitSimErrUrl'] == 'yes') and gVal['errorUrlList']):
                            (isSimilar, simSrcUrl) = crifanLib.findSimilarUrl(curUrl, gVal['errorUrlList']);
                            if isSimilar :
                                logging.warning("  Omit process %s for similar with previous error url", curUrl);
                                logging.warning("               %s", simSrcUrl);
                                continue;
                        
                        logging.debug("Now to process %s", curUrl);
                        # no matter:(1) it is pic or not, (2) follow search fail or not
                        # (3) latter fail to fetch pic or not -> still means this url is processed
                        gVal['processedUrlList'].append(curUrl);

                        # process this url
                        singleUrlPattern = processPicCfgDict['singlePicUrlNoSufPat'] + r'\.(?P<suffix>[' + gVal['picSufStr'] + r']{3,4})';
                        #print "singleUrlPattern=",singleUrlPattern;
                        
                        foundPic = re.search(singleUrlPattern, curUrl);
                        if foundPic :
                            #print "foundPic=",foundPic;
                            suffix  = foundPic.group("suffix");

                            picInfoDict = {
                                'picUrl'    : "", # the current pic url
                                'filename'  : "", # filename of pic
                                'fields'    : {}, # depend on the implemented functions, normal should contains fd1/fd2/fd3/...
                            };
                            
                            picInfoDict = processPicCfgDict['getFoundPicInfo'](foundPic);
                            #print "picInfoDict=",picInfoDict;
                            
                            filename = picInfoDict['filename'];
                            picUrl = picInfoDict['picUrl'];
                            
                            #print "picUrl=",picUrl
                            #print "filename=",filename;
                            #print "picInfoDict['fields']=",picInfoDict['fields'];
                            
                            if suffix.lower() in gConst['validPicSufList'] :
                                # indeed is pic, process it
                                (picIsValid, errReason) = crifanLib.isFileValid(curUrl);
                                if picIsValid :
                                    # 1. prepare info
                                    nameWithSuf = filename + '.' + suffix;
                                    curPath = os.getcwd();
                                    dstPathOwnPic = curPath + '\\' + gVal['blogUser'] + '\\pic';
                                    # 2. create dir for save pic
                                    if (os.path.isdir(dstPathOwnPic) == False) :
                                        os.makedirs(dstPathOwnPic); # create dir recursively
                                        logging.info("Create dir %s for save downloaded pictures of own site", dstPathOwnPic);
                                    if gCfg['processOtherPic'] == 'yes' :
                                        dstPathOtherPic = dstPathOwnPic + '\\' + gConst['othersiteDirName'];
                                        if (os.path.isdir(dstPathOtherPic) == False) :
                                            os.makedirs(dstPathOtherPic); # create dir recursively
                                            logging.info("Create dir %s for save downloaded pictures of other site", dstPathOtherPic);
                                    # 3. prepare info for follow download and save
                                    if(processPicCfgDict['isSelfBlogPic'](picInfoDict)):
                                        #print "++++ yes is self blog pic";
                                        newPicUrl = gCfg['picPathInWP'] + '/' + nameWithSuf;
                                        dstPicFile = dstPathOwnPic + '\\' + nameWithSuf;
                                    else :
                                        # is othersite pic
                                        #print "--- is other pic";
                                        if gCfg['processOtherPic'] == 'yes' :
                                            #newNameWithSuf = fd1 + '_' + fd2 + "_" + nameWithSuf;
                                            newNameWithSuf = processPicCfgDict['genNewOtherPicName'](picInfoDict) + '.' + suffix;
                                            #print "newNameWithSuf=",newNameWithSuf;
                                            newPicUrl = gCfg['otherPicPathInWP'] + '/' + newNameWithSuf;
                                            dstPicFile = dstPathOtherPic + '\\' + newNameWithSuf;
                                        else :
                                            dstPicFile = ''; # for next not download
                                            #newPicUrl = curUrl

                                    # download pic and replace url
                                    if dstPicFile and crifanLib.downloadFile(curUrl, dstPicFile) :
                                        # replace old url with new url
                                        blogContent = re.compile(curUrl).sub(newPicUrl, blogContent);
                                        # record it
                                        gVal['replacedUrlDict'][curUrl] = newPicUrl;
                                        logging.debug("Replace %s with %s", curUrl, newPicUrl);
                                        #logging.debug("After replac, new blog content:\n%s", blogContent);
                                        
                                        logging.info("    Processed picture: %s", curUrl);
                                else :
                                    logging.debug("Invalid picture: %s, reason: %s", curUrl, errReason);
                                    if (gCfg['omitSimErrUrl'] == 'yes'): # take all error pic into record
                                        # when this pic occur error, then add to list
                                        gVal['errorUrlList'].append(curUrl);
                                        logging.debug("Add invalid %s into global error url list.", curUrl);
                            else :
                                logging.debug("Omit unsupported picture %s", curUrl);
                # for that processed url, only replace the address
                if existedList :
                    for processedUrl in existedList:
                        # some pic url maybe is invalid, so not download and replace,
                        # so here only processed that downloaded and replaceed ones
                        if processedUrl in gVal['replacedUrlDict'] :
                            newPicUrl = gVal['replacedUrlDict'][processedUrl];
                            blogContent = re.compile(processedUrl).sub(newPicUrl, blogContent);
                            logging.debug("For processed url %s, not download again, only replace it with %s", processedUrl, newPicUrl);
            logging.debug("Done for process all pictures");
            gVal['statInfoDict']['processPicTime'] += crifanLib.calcTimeEnd("process_all_picture");
            logging.debug("Successfully to process all pictures");
        except :
            logging.warning('  Process picture failed.');

    return blogContent;

#------------------------------------------------------------------------------
# if input string include '%', should be converted into '%25', 25=0x25=37=ascii value for '%'
def convertToWpAddress(inputStr) :
    strInWpAddr = re.compile('%').sub('%25', inputStr);
    return strInWpAddr;

#------------------------------------------------------------------------------
# post process blog content:
# 1. download pic and replace pic url
# 2. remove invalid ascii control char
def postProcessContent(blogContent) :
    processedContent = '';
    try :
        blogContent = packageCDATA(blogContent);
        
        # 1. extract pic url, download pic, replace pic url
        afterProcessPic = processPhotos(blogContent);
        
        # 2. remove invalid ascii control char
        afterFilter = crifanLib.removeCtlChr(afterProcessPic);
        
        processedContent = afterFilter;
    except :
        logging.debug("Fail while post process for blog content");

    return processedContent;

#------------------------------------------------------------------------------
# process each feteched post info
def processSinglePost(infoDict) :
    # remove the control char in title:
    # eg;
    # http://green-waste.blog.163.com/blog/static/32677678200879111913911/
    # title contains control char:DC1, BS, DLE, DLE, DLE, DC1
    infoDict['title'] = crifanLib.removeCtlChr(infoDict['title']);
    
    # do translate here -> avoid in the end, 
    # too many translate request to google will cause "HTTPError: HTTP Error 502: Bad Gateway"
    infoDict['titleForPublish'] = generatePostName(infoDict['title']);

    if(infoDict['category']):
        gVal['catNiceDict'][infoDict['category']] = generatePostName(infoDict['category']);

    # add into global tagSlugDict
    # note: input tags should be unicode type
    if(infoDict['tags']) :
        for eachTag in infoDict['tags'] :
            if eachTag : # maybe is u'', so here should check whether is empty
                gVal['tagSlugDict'][eachTag] = generatePostName(eachTag);
                
    if(gCfg['processType'] == "exportToWxr") :    
        # do some post process for blog content
        infoDict['content'] = postProcessContent(infoDict['content']);
        
    elif (gCfg['processType'] == "modifyPost") :
        # 1. prepare new content
        newPostContentUni = gVal['postModifyPattern'];
        
        # replace permanent link in wordpress == title for publish
        newPostContentUni = newPostContentUni.replace("${titleForPublish}", infoDict['titleForPublish']);

        # replace title, infoDict['title'] must non-empty
        newPostContentUni = newPostContentUni.replace("${originalTitle}", unicode(infoDict['title']));

        titleUtf8 = infoDict['title'].encode("UTF-8");
        #quotedTitle = urllib.quote_plus(titleUtf8);
        quotedTitle = urllib.quote(titleUtf8);
        newPostContentUni = newPostContentUni.replace("${quotedTitle}", quotedTitle);

        #print "after title newPostContentUni=",newPostContentUni;

        # replace datetime, infoDict['datetime'] must non-empty
        localTime = parseDatetimeStrToLocalTime(infoDict['datetime']);
        newPostContentUni = newPostContentUni.replace("${postYear}", str.format("{0:4d}", localTime.year));
        newPostContentUni = newPostContentUni.replace("${postMonth}", str.format("{0:02d}", localTime.month));
        newPostContentUni = newPostContentUni.replace("${postDay}", str.format("{0:02d}", localTime.day));

        # replace category
        newPostContentUni = newPostContentUni.replace("${category}", infoDict['category']);
        
        # replace content
        newPostContentUni = newPostContentUni.replace("${originBlogContent}", infoDict['content']);
        
        # 2. modify to new content
        (modifyOk, errInfo) = modifySinglePost(newPostContentUni, infoDict, gCfg);
        if(modifyOk) :
            logging.debug("Modify %s successfully.", infoDict['url']);
        else:
            logging.error("Modify %s failed for %s.", infoDict['url'], errInfo);
            sys.exit(2);
    
#------------------------------------------------------------------------------
#1. open current post item
#2. save related info into post info dict
#3. return post info dict
def fetchSinglePost(url):
    global gVal;
    global gConst;
    global gCfg;

    #update post id
    gVal['postID'] += 1;

    logging.debug("----------------------------------------------------------");
    logging.info("[%04d] %s", gVal['postID'], url);

    crifanLib.calcTimeStart("fetch_page");
    for tries in range(gCfg['funcTotalExecNum']) :
        try :
            respHtml = crifanLib.getUrlRespHtml(url);
            gVal['statInfoDict']['fetchPageTime'] += crifanLib.calcTimeEnd("fetch_page");
            logging.debug("Successfully downloaded: %s", url);
            break # successfully, so break now
        except :
            if tries < (gCfg['funcTotalExecNum'] - 1) :
                logging.warning("Fetch page %s fail, do %d retry", url, (tries + 1));
                continue;
            else : # last try also failed, so exit
                logging.error("Has tried %d times to fetch page: %s, all failed!", gCfg['funcTotalExecNum'], url);
                sys.exit(2);

    # Note:
    # (1) baidu and 163 blog all use charset=gbk, but some special blog item:
    # http://chaganhu99.blog.163.com/blog/static/565262662007112245628605/
    # will messy code if use default gbk to decode it, so set GB18030 here to avoid messy code
    # (2) after BeautifulSoup process, output html content already is utf-8 encoded
    soup = BeautifulSoup(respHtml, fromEncoding=gCfg['postEncoding']);
    #prettifiedSoup = soup.prettify();
    #logging.debug("Got post html\n---------------\n%s", prettifiedSoup);
    
    infoDict = {
        'omit'          : False,
        'url'           : '',
        'postid'        : 0,
        'title'         : '',
        'nextLink'      : '',
        'type'          : '',
        'content'       : '',
        'datetime'      : '',
        'category'      : '',
        'tags'          : [],
        'comments'      : [], # each one is a dict value
        'respHtml'      : '',
        };

    infoDict['url'] = url;
    
    infoDict['postid'] = gVal['postID'];
    infoDict['respHtml'] = respHtml;
    
    # title
    infoDict['title'] =  extractTitle(soup);    
    if(not infoDict['title'] ) :
        logging.error("Can not extract post title for %s !", url);
        sys.exit(2);
    else :
        logging.debug("Extracted post title: %s", infoDict['title']);

    # extrat next (previously published) blog item link
    # here must extract next link first, for next call to use while omit=True
    infoDict['nextLink'] = findNextPermaLink(soup);
    logging.debug("Extracted post's next permanent link: %s", infoDict['nextLink']);

    isPrivate = isPrivatePost(soup);
    if(isPrivate) :
        infoDict['type'] = 'private';
        logging.debug("Post type is private.");
    else :
        # tmp not consider the "friendOnly" type
        logging.debug("Post type is public.");
        infoDict['type'] = 'publish';

    if((gCfg['postTypeToProcess'] == "privateOnly") and (not isPrivate)) :
        logging.info("  Omit process non-private post: %s", infoDict['title']);
        infoDict['omit'] = True;
    elif((gCfg['postTypeToProcess'] == "publicOnly") and isPrivate) :
        infoDict['omit'] = True;
        logging.info("  Omit process private post: %s", infoDict['title']);

    if (infoDict['omit']):
        return infoDict;
    else :
        logging.info("  Title = %s", infoDict['title']);

    # datetime
    infoDict['datetime'] = extractDatetime(soup);
    if(not infoDict['datetime'] ) :
        logging.error("Can not extract post publish datetime for %s !", url);
        sys.exit(2);
    else :
        logging.debug("Extracted post publish datetime: %s", infoDict['datetime']);

    # content
    infoDict['content'] = extractContent(soup);
    if(not infoDict['content'] ) :
        logging.error("Can not extract post content for %s !", url);
        sys.exit(2);
    # else :
        # logging.debug("Extracted post content: %s", infoDict['content']);

    # category
    infoDict['category'] = extractCategory(soup);
    logging.debug("Extracted post's category: %s", infoDict['category']);

    # if is modify post, no need: tags, comments
    if(gCfg['processType'] == "exportToWxr") :
        # tags
        infoDict['tags'] = extractTags(soup);

        # fetch comments
        if gCfg['processCmt'] == 'yes' :
            crifanLib.calcTimeStart("process_comment");
            try :
                infoDict['comments'] = fetchAndParseComments(url, soup);

                logging.debug('Total extracted comments for this blog item = %d', len(infoDict['comments']));
            except :
                logging.warning("Fail to process comments for %s", url);

            gVal['statInfoDict']['processCmtTime'] += crifanLib.calcTimeEnd("process_comment");
    
    return infoDict;

#------------------------------------------------------------------------------
# remove invalid character in url(blog's post name and category's nice name)
def removeInvalidCharInUrl(inputString):
    filterd_str = '';
    charNumerP = re.compile(r"[\w|-]");
    for c in inputString :
        if c == ' ' :
            # replace blanksplace with '_'
            filterd_str += '_';
        elif charNumerP.match(c) :
            # retain this char if is a-z,A-Z,0-9,_
            filterd_str += c;
    return filterd_str;

#------------------------------------------------------------------------------
def exportHead(dic):
    global gConst
    global gVal

    wxrT = Template("""<?xml version="1.0" encoding="UTF-8"?>
<!--
    This is a WordPress eXtended RSS file generated by ${generator} as an export of 
    your blog. It contains information about your blog's posts, comments, and 
    categories. You may use this file to transfer that content from one site to 
    another. This file is not intended to serve as a complete backup of your 
    blog.
    
    To import this information into a WordPress blog follow these steps:
    
    1.    Log into that blog as an administrator.
    2.    Go to Manage > Import in the blog's admin.
    3.    Choose "WordPress" from the list of importers.
    4.    Upload this file using the form provided on that page.
    5.    You will first be asked to map the authors in this export file to users 
        on the blog. For each author, you may choose to map an existing user on 
        the blog or to create a new user.
    6.    WordPress will then import each of the posts, comments, and categories 
        contained in this file onto your blog.
-->

<!-- generator="${generator}" created="${nowTime}"-->
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.1/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.1/"
>

<channel>
    <title>${blogTitle}</title>
    <link>http://localhost</link>
    <description>${blogDiscription}</description>
    <pubDate>${blogPubDate}</pubDate>
    <generator>${generator}</generator>
    <language>en</language>
    <wp:wxr_version>1.1</wp:wxr_version>
    <wp:base_site_url>http://localhost</wp:base_site_url>
    <wp:base_blog_url>http://localhost</wp:base_blog_url>

    <wp:author>
        <wp:author_id>1</wp:author_id>
        <wp:author_login>${blogUser}</wp:author_login>
        <wp:author_email></wp:author_email>
        <wp:author_display_name>${authorDisplayName}</wp:author_display_name>
        <wp:author_first_name>${authorFirstName}</wp:author_first_name>
        <wp:author_last_name>${authorLastName}</wp:author_last_name>
    </wp:author>

""")
#need   nowTime, blogTitle, blogDiscription, blogUser, generator
#       authorDisplayName, authorFirstName, authorLastName, blogPubDate

    catT = Template("""
    <wp:category>
        <wp:term_id>${catTermId}</wp:term_id>
        <wp:category_nicename>${catNicename}</wp:category_nicename>
        <wp:category_parent></wp:category_parent>
        <wp:cat_name>${catName}</wp:cat_name>
        <wp:category_description>${catDesc}</wp:category_description>
    </wp:category>
""")#need catTermId, catName, catNicename, catDesc

    tagT = Template("""
    <wp:tag>
        <wp:term_id>${tagNum}</wp:term_id>
        <wp:tag_slug>${tagSlug}</wp:tag_slug>
        <wp:tag_name>${tagName}</wp:tag_name>
    </wp:tag>
""")#need tagNum, tagSlug, tagName

    generatorT = Template("""
    <generator>${generator}</generator>

""")#need generator

    # Note: some field value has been set before call this func
    dic['authorDisplayName'] = packageCDATA("");
    dic['authorFirstName'] = packageCDATA("");
    dic['authorLastName'] = packageCDATA("");
    dic['blogTitle'] = saxutils.escape(dic['blogTitle']);
    dic['blogDiscription'] = saxutils.escape(dic['blogDiscription']);
    dic['generator'] = gConst['generator'];
    headerStr = wxrT.substitute(dic);

    catStr = '';
    catTermID = 1;
    for cat in gVal['catNiceDict'].keys():
        catStr += catT.substitute(
            catTermId = catTermID,
            catName = packageCDATA(cat),
            catNicename = gVal['catNiceDict'][cat],
            catDesc = packageCDATA(""),);
        catTermID += 1;

    #compose tags string
    tagsStr = '';
    tagTermID = catTermID;
    for tag in gVal['tagSlugDict'].keys():
        if tag :
            tagsStr += tagT.substitute(
                tagNum = tagTermID,
                tagSlug = gVal['tagSlugDict'][tag],
                tagName = packageCDATA(tag),);
            tagTermID += 1;

    generatorStr = generatorT.substitute(generator = gConst['generator']);

    expFile = openExportFile();
    gVal['fullHeadInfo'] = headerStr + catStr + tagsStr + generatorStr;
    expFile.write(gVal['fullHeadInfo']);
    expFile.flush();
    expFile.close();
    return;

#------------------------------------------------------------------------------
# export each post info, then add foot info
# if exceed max size, then split it
def exportPost(entry, user):
    global gVal;
    global gCfg;

    itemT = Template("""
    <item>
        <title>${entryTitle}</title>
        <!--${originalLink}-->
        <link>${entryURL}</link>
        <pubDate>${pubDate}</pubDate>
        <dc:creator>${entryAuthor}</dc:creator>
        <guid isPermaLink="false">${entryURL}</guid>
        <description></description>
        <content:encoded>${entryContent}</content:encoded>
        <excerpt:encoded>${entryExcerpt}</excerpt:encoded>
        <wp:post_id>${postId}</wp:post_id>
        <wp:post_date>${postDate}</wp:post_date>
        <wp:post_date_gmt>${postDateGMT}</wp:post_date_gmt>
        <wp:comment_status>open</wp:comment_status>
        <wp:ping_status>open</wp:ping_status>
        <wp:post_name>${entryPostName}</wp:post_name>
        <wp:status>${postStatus}</wp:status>
        <wp:post_parent>0</wp:post_parent>
        <wp:menu_order>0</wp:menu_order>
        <wp:post_type>post</wp:post_type>
        <wp:post_password></wp:post_password>
        <wp:is_sticky>0</wp:is_sticky>
        <category domain="category" nicename="${category_nicename}">${category}</category>
        ${tags}
        ${comments}
    </item>
"""); #need entryTitle, entryURL, entryAuthor, category, entryContent,
# entryExcerpt, postId, postDate, entryPostName, postStatus
# originalLink

    tagsT = Template("""
        <category domain="post_tag" nicename="${tagSlug}">${tagName}</category>"""); # tagSlug, tagName

    commentT = Template("""
        <wp:comment>
            <wp:comment_id>${commentId}</wp:comment_id>
            <wp:comment_author>${commentAuthor}</wp:comment_author>
            <wp:comment_author_email>${commentEmail}</wp:comment_author_email>
            <wp:comment_author_url>${commentURL}</wp:comment_author_url>
            <wp:comment_author_IP>${commentAuthorIP}</wp:comment_author_IP>
            <wp:comment_date>${commentDate}</wp:comment_date>
            <wp:comment_date_gmt>${commentDateGMT}</wp:comment_date_gmt>
            <wp:comment_content>${commentContent}</wp:comment_content>
            <wp:comment_approved>1</wp:comment_approved>
            <wp:comment_type></wp:comment_type>
            <wp:comment_parent>${commentParent}</wp:comment_parent>
            <wp:comment_user_id>0</wp:comment_user_id>
        </wp:comment>
"""); #need commentId, commentAuthor, commentEmail,commentURL, commentDate
     # commentDateGMT, commentContent, commentAuthorIP, commentParent

    #compose tags string
    tagsStr = '';
    for tag in entry['tags']:
        if tag:
            tagsStr += tagsT.substitute(
                tagSlug = gVal['tagSlugDict'][tag],
                tagName = packageCDATA(tag),);

    #compose comment string
    commentsStr = "";
    logging.debug("Now will export comments = %d", len(entry['comments']));
    for comment in entry['comments']:
        commentsStr += commentT.substitute(
                            commentId = comment['id'],
                            commentAuthor = comment['author'],
                            commentEmail = comment['author_email'],
                            commentURL = comment['author_url'],
                            commentAuthorIP = comment['author_IP'],
                            commentDate = comment['date'],
                            commentDateGMT = comment['date_gmt'],
                            commentContent = comment['content'],
                            commentParent = comment['parent'],);

    # parse datetime string into local time
    parsedLocalTime = parseDatetimeStrToLocalTime(entry['datetime']);
    gmt0Time = crifanLib.convertLocalToGmt(parsedLocalTime);
    entry['pubDate'] = gmt0Time.strftime('%a, %d %b %Y %H:%M:%S +0000');
    entry['postDate'] = parsedLocalTime.strftime('%Y-%m-%d %H:%M:%S');
    entry['postDateGMT'] = gmt0Time.strftime('%Y-%m-%d %H:%M:%S');
    
    itemStr = itemT.substitute(
        entryTitle = entry['title'],
        originalLink = entry['url'],
        entryURL = gCfg['postPrefAddr'] + str(entry['postid']),
        entryAuthor = user,
        category = packageCDATA(entry['category']),
        category_nicename = gVal['catNiceDict'][entry['category']],
        entryContent = entry['content'],
        entryExcerpt = packageCDATA(""),
        postId = entry['postid'],
        postDate = entry['postDate'],
        postDateGMT = entry['postDateGMT'],
        pubDate = entry['pubDate'],
        entryPostName = entry['titleForPublish'],
        tags = tagsStr,
        comments = commentsStr,
        postStatus = entry['type'],
        );

    # output item info to file
    curFileSize = os.path.getsize(gVal['exportFileName']);
    itemStrUft8 = itemStr.encode("utf-8");
    newFileSize = curFileSize + len(itemStrUft8);
    #logging.debug("itemPostId[%04d]: unicode str size = %d, utf-8 str size=%d", entry['postid'], len(itemStr), len(itemStrUft8))
    
    if gCfg['maxXmlSize'] and (newFileSize > gCfg['maxXmlSize']) : # exceed limit size, 0 means no limit
        # 1. output tail info
        curFile = openExportFile();
        curFile.write(gConst['tailInfo']);

        # 2. close old file
        curFile.flush();
        curFile.close();
        #logging.debug("Stored %s size = %d", gVal['exportFileName'], os.path.getsize(gVal['exportFileName']))

        # 3. generate new name
        # old: XXX_20111218_2213-0.xml
        # new: XXX_20111218_2213-1.xml
        oldIdx = int(gVal['exportFileName'][-5]);
        newIdx = oldIdx + 1;
        newFileName = gVal['exportFileName'][:-5] + str(newIdx) + ".xml";

        # 4. update global export file name
        gVal['exportFileName'] = newFileName;

        # 5. create new file
        newFile = codecs.open(gVal['exportFileName'], 'w', 'utf-8');
        if newFile:
            logging.info('Newly created export XML file: %s', gVal['exportFileName']);
        else:
            logging.error("Can not create new export file: %s",gVal['exportFileName']);
            sys.exit(2);

        # 6. export head info
        newFile.write(gVal['fullHeadInfo']);
        
        # 7. export current item info
        newFile.write(itemStr);
        newFile.flush();
        newFile.close();
    else : # not exceed limit size
        curFile = openExportFile();
        curFile.write(itemStr);
        curFile.flush();
        curFile.close();

    logging.debug("Export blog item '%s' done", entry['title']);
    return;

#------------------------------------------------------------------------------
def exportFoot():
    f = openExportFile();
    f.write(gConst['tailInfo']);
    f.close();
    return;

#------------------------------------------------------------------------------
# process blog header related info
def processBlogHeadInfo(blogInfoDic, username) :
    global gConst;
    global gVal;

    blogInfoDic['blogURL'] = gVal['blogEntryUrl'];
    (blogInfoDic['blogTitle'], blogInfoDic['blogDiscription']) = extractBlogTitAndDesc(gVal['blogEntryUrl']);
    logging.debug('Blog title: %s', blogInfoDic['blogTitle']);
    logging.debug('Blog description: %s', blogInfoDic['blogDiscription']);

    # if none, set to a string, avoid fail while latter processing them
    if not blogInfoDic['blogTitle'] :
        blogInfoDic['blogTitle'] = 'NoBlogTitle';
    if not blogInfoDic['blogDiscription'] :
        blogInfoDic['blogDiscription'] = 'NoBlogDescription';
    blogInfoDic['nowTime'] = datetime.now().strftime('%Y-%m-%d %H:%M');
    blogInfoDic['blogUser'] = username;
    blogInfoDic['blogPubDate'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000');
    return;

#------------------------------------------------------------------------------
# output statistic info
def outputStatisticInfo() :
    totalTime = int(gVal['statInfoDict']['totalTime']);
    if gCfg['googleTrans'] == 'yes' :
        transNameTime = int(gVal['statInfoDict']['transNameTime']);
    find1stLinkTime = int(gVal['statInfoDict']['find1stLinkTime']);
    processPostsTime = int(gVal['statInfoDict']['processPostsTime']);
    fetchPageTime = int(gVal['statInfoDict']['fetchPageTime']);
    if(gCfg['processType'] == "exportToWxr") :
        exportHeadTime = int(gVal['statInfoDict']['exportHeadTime']);
        exportPostsTime = int(gVal['statInfoDict']['exportPostsTime']);
        exportFootTime = int(gVal['statInfoDict']['exportFootTime']);
        if gCfg['processPic'] == 'yes' :
            processPicTime = int(gVal['statInfoDict']['processPicTime']);
        if gCfg['processCmt'] == 'yes' :
            processCmtTime = int(gVal['statInfoDict']['processCmtTime']);
    
    # output output statistic info
    printDelimiterLine();
    logging.info("Total Processed [%04d] posts, averagely each consume seconds=%.4f", gVal['statInfoDict']['processedPostNum'], gVal['statInfoDict']['itemAverageTime']);
    logging.info("Total Consume Time: %02d:%02d:%02d", totalTime / 3600, (totalTime % 3600)/60, totalTime % 60);
    logging.info("  Find 1stLink: %02d:%02d:%02d", find1stLinkTime/3600, (find1stLinkTime%3600)/60, find1stLinkTime%60);
    logging.info("  Process Post: %02d:%02d:%02d", processPostsTime/3600, (processPostsTime%3600)/60, processPostsTime%60);
    logging.info("      Fetch   Pages     : %02d:%02d:%02d", fetchPageTime/3600, (fetchPageTime%3600)/60, fetchPageTime%60);
    if(gCfg['processType'] == "exportToWxr") :
        if gCfg['processPic'] == 'yes' :
            logging.info("      Process Pictures  : %02d:%02d:%02d", processPicTime/3600, (processPicTime%3600)/60, processPicTime%60);
        if gCfg['processCmt'] == 'yes' :
            logging.info("      Process Comments  : %02d:%02d:%02d", processCmtTime/3600, (processCmtTime%3600)/60, processCmtTime%60);
    if gCfg['googleTrans'] == 'yes' :
        logging.info("      Translate Name    : %02d:%02d:%02d", transNameTime/3600, (transNameTime%3600)/60, transNameTime%60);
    if(gCfg['processType'] == "exportToWxr") :
        logging.info("  Export Head : %02d:%02d:%02d", exportHeadTime/3600, (exportHeadTime%3600)/60, exportHeadTime%60);
        logging.info("  Export Posts: %02d:%02d:%02d", exportPostsTime/3600, (exportPostsTime%3600)/60, exportPostsTime%60);
        logging.info("  Export Foot : %02d:%02d:%02d", exportFootTime/3600, (exportFootTime%3600)/60, exportFootTime%60);

    return;

#------------------------------------------------------------------------------
# generate the post name for original name
# post name = [translate and ] quote it
# note: input name should be unicode type
def generatePostName(unicodeName) :
    quotedName = '';

    if unicodeName :
        nameUtf8 = unicodeName.encode("utf-8");
        if gCfg['googleTrans'] == 'yes' :
            crifanLib.calcTimeStart("translate_name");
            (transOK, translatedName) = crifanLib.transZhcnToEn(nameUtf8);
            gVal['statInfoDict']['transNameTime'] += crifanLib.calcTimeEnd("translate_name");
            if transOK :
                logging.debug("Has translated [%s] to [%s].", unicodeName, translatedName);
                translatedName = removeInvalidCharInUrl(translatedName);
                logging.debug("After remove invalid char become to %s.", translatedName);
                quotedName = urllib.quote(translatedName);
                logging.debug("After quote become to %s.", quotedName);
            else :
                quotedName = urllib.quote(nameUtf8);
                logging.warning("Translate fail for [%s], roolback to use just quoted string [%s]", nameUtf8, quotedName);
        else :
            #nameUtf8 = removeInvalidCharInUrl(nameUtf8);
            quotedName = urllib.quote(nameUtf8);

    return quotedName;

#------------------------------------------------------------------------------
# generate the suffix char list according to constont picSufList
def genSufList() :
    global gConst;
    
    sufChrList = [];
    for suffix in gConst['validPicSufList'] :
        for c in suffix :
            sufChrList.append(c);
    sufChrList = crifanLib.uniqueList(sufChrList);
    sufChrList.sort();
    joinedSuf = ''.join(sufChrList);

    swapedSuf = [];
    swapedSuf = joinedSuf.swapcase();

    wholeSuf = joinedSuf + swapedSuf;

    return wholeSuf

#------------------------------------------------------------------------------
# if set username and password, then try login first
# if login OK, then will got global cookie for later usage of http request
# Note: makesure has got the extracted blog user: gVal['blogEntryUrl']
def tryLoginBlog() :
    global gCfg
    
    if gCfg['username'] and gCfg['password'] :
        loginOk = loginBlog(gCfg['username'], gCfg['password']);
        
        if (loginOk):
            logging.info("%s login successfully.", gCfg['username']);
        else :
            logging.error("%s login failed !", gCfg['username']);
            sys.exit(2);
    else :
        logging.info("Username and/or password is null, now in un-login mode.");

#------------------------------------------------------------------------------
# do some initial work:
# 1. check blog provider
# 2. extract blog user and blog entry url from input url
# 3. also init some related config values
# 4. try login blog
def initialization(inputUrl):
    logging.debug("Extracting blog user from url=%s", inputUrl);
    
    # 1. check blog provider
    checkBlogProvider(inputUrl);
    
    # 2. extract blog user and blog entry url from input url
    (extractOK, extractedBlogUser, generatedBlogEntryUrl) = extractBlogUser(inputUrl);

    if(extractOK) :
        gVal['blogUser'] = extractedBlogUser;
        gVal['blogEntryUrl'] = generatedBlogEntryUrl;
        
        logging.info("Extracted Blog user [%s] from %s", gVal['blogUser'], inputUrl);
        logging.info("Blog entry url is %s", gVal['blogEntryUrl']);
    else:
        logging.error("Can not extract blog user form input URL: %s", inputUrl);
        sys.exit(2);

    # 3. also init some related config values
    if(gCfg['processType'] == "exportToWxr") : 
        # update some related default value
        if gCfg['picPathInWP'] == '' :
            # % -> %25
            # eg: %D7%CA%C1%CF%CA%D5%BC%AF -> %25D7%25CA%25C1%25CF%25CA%25D5%25BC%25AF
            blogUsrInWpAddr = convertToWpAddress(gVal['blogUser']);
            gCfg['picPathInWP'] = gConst['picRootPathInWP'] + '/' + blogUsrInWpAddr + "/pic";
        if gCfg['otherPicPathInWP'] == '' :
            gCfg['otherPicPathInWP'] = gCfg['picPathInWP'] + '/' + gConst['othersiteDirName'];

        logging.debug("Set URL prefix for own   site picture: %s", gCfg['picPathInWP']);
        logging.debug("Set URL prefix for other site picture: %s", gCfg['otherPicPathInWP']);
        
    # 4. try login blog
    tryLoginBlog();
    
    return;

#------------------------------------------------------------------------------
def main():
    global gVal
    global gCfg

    # 0. main procedure begin
    parser = OptionParser();
    parser.add_option("-s","--srcUrl",action="store", type="string",dest="srcUrl",help=u"博客入口地址。例如: http://againinput4.blog.163.com, http://hi.baidu.com/recommend_music/。程序会自动找到你的博客的（最早发布的）第一个帖子，然后开始处理。");
    parser.add_option("-f","--startFromUrl",action="store", type="string",dest="startFromUrl",help=u"从哪个帖子（的永久链接地址）开始。例如：http://againinput4.blog.163.com/blog/static/17279949120120824544142/，http://hi.baidu.com/recommend_music/blog/item/c2896794b621ae13d31b70c3.html。如果设置此了参数，那么会自动忽略参数srcUrl");
    parser.add_option("-l","--limit",action="store",type="int",dest="limit",help=u"最多要处理的帖子的个数");
    parser.add_option("-c","--processCmt",action="store",type="string",dest="processCmt",default="yes",help=u"是否处理帖子的评论，yes或no。默认为yes");
    parser.add_option("-u","--username",action="store",type="string",default='',dest="username",help=u"博客登陆用户名");
    parser.add_option("-p","--password",action="store",type="string",default='',dest="password",help=u"博客登陆密码");
    parser.add_option("-i","--firstPostId",action="store",type="int",default=0,dest="firstPostId",help=u"导出到wordpress时候的帖子的起始ID");
    parser.add_option("-b","--processPic",action="store",type="string",default="yes",dest="processPic",help=u"是否处理（帖子内容中，属于本博客的）图片：yes或no。默认为yes。处理图片包括：下载图片，并将原图片地址替换为以wpPicPath参数的设置内容为前缀的新的地址。下载下来的图片存放在当前路径下名为用户名的文件夹中。注意，当将程序生成的WXR文件导入wordpress中之后，为了确保图片可以正确显示，不要忘了把下载下来的图片放到你的wordpress的服务器中相应的位置");
    parser.add_option("-w","--wpPicPath",action="store",type="string",dest="wpPicPath",help=u"wordpress中图片的（即，原图片所被替换的）新地址的前缀。例如：http://www.crifan.com/files/pic/recommend_music，默认设置为：http://localhost/wordpress/wp-content/uploads/BLOG_USER/pic，其中BLOG_USER是你的博客用户名。注意：此选项只有在processPic='yes'的情况下才有效");
    parser.add_option("-o","--processOtherPic",action="store",type="string",default="yes",dest="processOtherPic",help=u"是否处理（帖子内容中）其他（网站的）图片：yes或no。默认为yes。即，下载并替换对应原图片地址为参数wpOtherPicPath所设置的前缀加上原文件名。注意：此选项只有在processPic='yes'的情况下才有效");
    parser.add_option("-r","--wpOtherPicPath",action="store",type="string",dest="wpOtherPicPath",help=u"wordpress中（其他网站的）图片的（即，原其他网站的图片所被替换的）新地址的前缀。默认为 ${wpPicPath}/other_site。此选项只有在processOtherPic='yes'的情况下才有效");
    parser.add_option("-n","--omitSimErrUrl",action="store",type="string",default="yes",dest="omitSimErrUrl",help=u"是否自动忽略处理那些和之前处理过程中出错的图片地址类似的图片：yes或no。默认为yes。即，自动跳过那些图片，其中该图片的地址和之前某些已经在下载过程中出错（比如HTTP Error）的图片地址很类似。注意：此选项只有在processPic='yes'的情况下才有效");
    parser.add_option("-g","--googleTrans",action="store",type="string",default="yes",dest="googleTrans",help=u"是否执行google翻译：yes或no。通过网络调用google的api，将对应的中文翻译为英文。包括：将帖子的标题翻译为英文，用于发布帖子时的固定链接（permanent link）；将帖子的分类，标签等翻译为对应的英文，用于导出到WXR文件中");
    parser.add_option("-a","--postPrefAddr",action="store",type="string",default="http://localhost/?p=",dest="postPrefAddr",help=u"帖子导出到WXR时候的前缀，默认为http://localhost/?p=，例如可设置为：http://www.crifan.com/?p=");
    parser.add_option("-x","--maxXmlSize",action="store",type="int",default=2*1024*1024,dest="maxXmlSize",help=u"导出的单个WXR文件大小的最大值。超出此大小，则会自动分割出对应的多个WXR文件。默认为2097152（2MB=2*1024*1024）。如果设置为0，则表示无限制。");
    parser.add_option("-y","--maxFailRetryNum",action="store",type="int",default=3,dest="maxFailRetryNum",help=u"当获取网页等操作失败时的重试次数。默认为3。设置为0表示当发生错误时，不再重试。");
    parser.add_option("-v","--postTypeToProcess",action="store",type="string",default='publicOnly',dest="postTypeToProcess",help=u"要处理哪些类型的帖子：publicOnly，privateOnly，privateAndPublic。注意：当设置为非publicOnly的时候，是需要提供对应的用户名和密码的，登陆对应的博客才可以执行对应的操作，即获取对应的private等类型帖子的。");
    parser.add_option("-t","--processType",action="store",type="string",default='exportToWxr',dest="processType",help=u"对于相应类型类型的帖子，具体如何处理，即处理的类型：exportToWxr和modifyPost。exportToWxr是将帖子内容导出为WXR；modifyPost是修改帖子内容（并提交，以达到更新帖子的目的），注意需要设置相关的参数：username，password，modifyPostPatFile.");
    parser.add_option("-d","--modifyPostPatFile",action="store",type="string",dest="modifyPostPatFile",help=u"修改帖子的模板，即需要更新的帖子的新的内容。支持相关参数。注意，需要输入的配置文件是UTF-8格式的。支持的格式化参数包括： ${originBlogContent}表示原先帖子的内容；${titleForPublish}表示用于发布的帖子的标题，即翻译并编码后的标题，该标题主要用于wordpress中帖子的永久链接；${originalTitle}表示原先帖子的标题内容；${quotedTitle}表示将原标题编码后的标题；${postYear},${postMonth},${postDay}分别表示帖子发布时间的年月日，均为2位数字；${category}表示帖子的分类。");
    parser.add_option("-j","--autoJumpSensitivePost",action="store",type="string",default='yes',dest="autoJumpSensitivePost",help=u"自动跳过（即不更新处理）那些包含敏感信息的帖子：yes或no。默认为yes。比如如果去修改某些百度帖子的话，其会返回 '文章内容包含不合适内容，请检查'，'文章标题包含不合适内容，请检查',等提示，此处则可以自动跳过，不处理此类帖子。");
    parser.add_option("-e","--postEncoding",action="store",type="string",default="GB18030",dest="postEncoding",help=u"帖子的编码。默认为GB18030。当通过BeautifulSoup解析出来的帖子是乱码的时候，需要强制指定帖子的编码。如果你的博客的帖子编码是非百度，163等的中文编码，那么需要指定帖子的编码，才能正确解析帖子内容。");
    
    logging.info(u"版本信息：%s", __VERSION__);
    logging.info(u"1.如有bug，请将日志文件和bug截图等信息发至：admin(at)crifan.com");
    logging.info(u"2.如果对于此脚本使用有任何疑问，请输入-h参数以获得相应的参数说明。");
    logging.info(u"3.关于本程更多相关信息，以及详细的使用说明，请去这里：");
    logging.info(u"  BlogsToWordPress：将百度空间，网易163等博客搬家到WordPress");
    logging.info(u"  http://www.crifan.com/crifan_released_all/website/python/blogstowordpress/");
    printDelimiterLine();
        
    (options, args) = parser.parse_args();
    # 1. export all options variables
    for i in dir(options):
        exec(i + " = options." + i);

    # 2. init some settings
    gCfg['processType'] = processType;

    gCfg['username'] = username;
    gCfg['password'] = password;
    gCfg['postTypeToProcess'] = postTypeToProcess;

    if( ((not gCfg['username']) or (not gCfg['password'])) and (gCfg['postTypeToProcess'] != "publicOnly")) :
        logging.error("For no username or password, not support non-publicOnly type of post to process !");
        sys.exit(2);
    
    if(gCfg['processType'] == "modifyPost") :
        logging.info("Your process type of post is: Modify post.");
        
        # check parameter validation
        if( (not username) or (not password) ) :
            logging.error("For modify post, username and password, all should not empty !");
            sys.exit(2);
            
        # init config
        gCfg['autoJumpSensitivePost'] = autoJumpSensitivePost;
        
        # check parameter validation
        if modifyPostPatFile and os.path.isfile(modifyPostPatFile):
            patternFile = os.open(modifyPostPatFile, os.O_RDONLY);
            gVal['postModifyPattern']  = os.read(patternFile, os.path.getsize(modifyPostPatFile));
            gVal['postModifyPattern'] = unicode(gVal['postModifyPattern'], "utf-8");
            logging.debug("after convert to unicode, modify pattern =%s", gVal['postModifyPattern']);
        else :
            logging.error("For modify post, modifyPostPatFile is null or invalid !");
            sys.exit(2);

    elif(gCfg['processType'] == "exportToWxr") :
        logging.info("Your process type of post is: Export post to WXR(WordPress eXtended Rss).");

        gCfg['processPic'] = processPic;
        if gCfg['processPic'] == 'yes' :
            gVal['picSufStr'] = genSufList();
            gCfg['omitSimErrUrl'] = omitSimErrUrl;
            if wpPicPath :
                # remove last slash if user input url if including
                if (wpPicPath[-1] == '/') : wpPicPath = wpPicPath[:-1];
                gCfg['picPathInWP'] = wpPicPath;
            gCfg['processOtherPic'] = processOtherPic;
            if gCfg['processOtherPic'] and wpOtherPicPath :
                # remove last slash if user input url if including
                if (wpOtherPicPath[-1] == '/') : wpOtherPicPath = wpOtherPicPath[:-1];
                gCfg['otherPicPathInWP'] = wpOtherPicPath;

        gCfg['processCmt'] = processCmt;
        gCfg['postPrefAddr'] = postPrefAddr;
        gCfg['maxXmlSize'] = maxXmlSize;

    gCfg['googleTrans'] = googleTrans;
    gCfg['funcTotalExecNum'] = maxFailRetryNum + 1;
    gCfg['postEncoding'] = postEncoding;
    
    
    # init some global values
    
    gVal['postID'] = firstPostId;
    # prepare for statistic
    if(gCfg['processType'] == "exportToWxr") :
        gVal['statInfoDict']['processPicTime']  = 0.0;
        gVal['statInfoDict']['processCmtTime']  = 0.0;

    gVal['statInfoDict']['processedPostNum'] = 0; # also include that is omited
    gVal['statInfoDict']['transNameTime']   = 0.0;
    gVal['statInfoDict']['fetchPageTime']   = 0.0;
    gVal['statInfoDict']['find1stLinkTime'] = 0.0;

    crifanLib.calcTimeStart("total");

    # 3. connect src blog and find first permal link
    if startFromUrl :
        permalink = startFromUrl;
        logging.info("Entry URL: %s", startFromUrl);
        
        initialization(startFromUrl);
    elif srcUrl:
        logging.info("Source URL: %s", srcUrl);
        
        initialization(srcUrl);
        
        crifanLib.calcTimeStart("find_first_perma_link");
        logging.info("Now start to find the permanent link for %s", srcUrl);
        (found, retStr)= find1stPermalink();
        if(found) :
            permalink = retStr;
            logging.info("Found the first link %s ", permalink);
        else :
            logging.error("Can not find the first link for %s, error=%s", srcUrl, retStr);
            sys.exit(2);
        gVal['statInfoDict']['find1stLinkTime'] = crifanLib.calcTimeEnd("find_first_perma_link");
    else:
        logging.error("Must designate the entry URL for the first blog item !");
        sys.exit(2);
    
    # 4. main loop, fetch and process for every post
    crifanLib.calcTimeStart("process_posts");
    
    while permalink:
        infoDict = fetchSinglePost(permalink);

        if(not infoDict['omit']) :
            processSinglePost(infoDict);

            gVal['postList'].append(infoDict);

        if 'nextLink' in infoDict :
            permalink = infoDict['nextLink'];
        else :
            break;
            
        gVal['statInfoDict']['processedPostNum'] += 1;
        
        if (limit and (gVal['statInfoDict']['processedPostNum'] >= limit)) :
            break;

    gVal['statInfoDict']['processPostsTime'] = crifanLib.calcTimeEnd("process_posts");

    if(gCfg['processType'] == "exportToWxr") :
    
        # 5. output extracted info to XML file
        createOutputFile();

        # make sure the username is valid in WXR: not contains non-word(non-char and number, such as '@', '_') character
        wxrValidUsername = crifanLib.removeNonWordChar(gVal['blogUser']);
        
        # Note:
        # now have found a bug for wordpress importer:
        # if usename in WXR contains underscore, then after imported, that post's username will be omitted, become to default's admin's username
        # eg: if username is green_waste, which is valid, can be recoginzed by wordpress importer, 
        # then after imported posts into wordpress, the username of posts imported become to default admin(here is crifan), not we expected : green_waste
        # so here replace the underscore to ''
        wxrValidUsername = wxrValidUsername.replace("_", "");
        logging.info("Generated WXR safe username is %s", wxrValidUsername);

        #get blog header info
        blogInfoDic = {};
        #processBlogHeadInfo(blogInfoDic, gVal['blogUser']);
        processBlogHeadInfo(blogInfoDic, wxrValidUsername);

        # export blog header info
        logging.info('Exporting head info to file ...');
        crifanLib.calcTimeStart("export_head");
        exportHead(blogInfoDic);
        gVal['statInfoDict']['exportHeadTime'] = crifanLib.calcTimeEnd("export_head");

        # export entries
        logging.info('Exporting post items info to file ...');
        crifanLib.calcTimeStart("export_posts");
        exportedNum = 0;
        for entry in gVal['postList']:
            exportedNum += 1;
            #exportPost(entry, gVal['blogUser']);
            exportPost(entry, wxrValidUsername);
            if (exportedNum % 10) == 0 :
                logging.info("Has exported %4d blog items", exportedNum);
        gVal['statInfoDict']['exportPostsTime'] = crifanLib.calcTimeEnd("export_posts");

        # export Foot
        logging.info('Exporting tail info to file ...');
        crifanLib.calcTimeStart("export_foot");
        exportFoot();
        gVal['statInfoDict']['exportFootTime'] = crifanLib.calcTimeEnd("export_foot");

    logging.info("Process blog %s successfully", gVal['blogEntryUrl']);

    # 7. output statistic info
    gVal['statInfoDict']['totalTime'] = crifanLib.calcTimeEnd("total");
    gVal['statInfoDict']['itemAverageTime'] = gVal['statInfoDict']['totalTime'] / float(gVal['statInfoDict']['processedPostNum']);
    
    outputStatisticInfo();

############ Different Blog Provider ############
#------------------------------------------------------------------------------
#def callBlogFunc(funcToCall, **paraDict):
def callBlogFunc(funcToCall, *paraList):
    blogProvider = "";

    # paras = "";
    # for i, para in enumerate(paraDict):
        # if ( i == 0) :
            # paras += para + "=" + paraDict[para];
            # #print dir(para);
            # #paras += para.__str__;
        # else :
            # paras += " ," + para + "=" + paraDict[para];
            # #paras += " ," + para.__name__;

    # print dir(funcToCall);
    # print "funcToCall.func_name=",funcToCall.func_name;
    # #print funcToCall.__dict__;
    
    # funcCallStr = blogProvider + "." + funcToCall.func_name + "(" + paras + ")";
    # print "funcCallStr=",funcCallStr;
    
    funcName = funcToCall.func_name;
    if(blogIsNetease()):
        trueFunc = getattr(BlogNetease, funcName);
        logging.debug("Now will call netease 163 function: %s", funcName);
    elif (blogIsBaidu()) :
        trueFunc = getattr(BlogBaidu, funcName);
        logging.debug("Now will call baidu function: %s", funcName);
    else:
        logging.error("Invalid blog provider");
        sys.exit(2);
        return;

    #print "trueFunc=",trueFunc;
    paraLen = len(paraList);
    #print "paraLen=",paraLen;
    
    if(paraLen == 0):
        return trueFunc();
    elif(paraLen == 1):
        return trueFunc(paraList[0]);
    elif (paraLen == 2):
        return trueFunc(paraList[0], paraList[1]);
    elif (paraLen == 3):
        return trueFunc(paraList[0], paraList[1], paraList[2]);
    elif (paraLen == 4):
        return trueFunc(paraList[0], paraList[1], paraList[2], paraList[3]);
    elif (paraLen == 5):
        return trueFunc(paraList[0], paraList[1], paraList[2], paraList[3], paraList[4]);
    elif (paraLen == 6):
        return trueFunc(paraList[0], paraList[1], paraList[2], paraList[3], paraList[4], paraList[5]);
    elif (paraLen == 7):
        return trueFunc(paraList[0], paraList[1], paraList[2], paraList[3], paraList[4], paraList[5], paraList[6]);
    elif (paraLen == 8):
        return trueFunc(paraList[0], paraList[1], paraList[2], paraList[3], paraList[4], paraList[5], paraList[6], paraList[7]);
    else :
        logging.error("Not support function parameters exceed 8 !");
        sys.exit(2);
        return;

#------------------------------------------------------------------------------
def blogIsBaidu() :
    return (gVal['blogProvider'] == gConst['prodiverBaidu']);

#------------------------------------------------------------------------------
def blogIsNetease() :
    return (gVal['blogProvider'] == gConst['prodiverNetease']);

#------------------------------------------------------------------------------
# check the blog provider from input url:
# is baidu from http://hi.baidu.com/recommend_music/
# is netease 163 from http://againinput4.blog.163.com/
def checkBlogProvider(inputUrl) :
    if(inputUrl.find("hi.baidu.com") > 0 ) :
        gVal['blogProvider'] = gConst['prodiverBaidu'];
        logging.info("Your blog provider : Baidu Space.");
    elif (inputUrl.find("blog.163.com") > 0 ) :
        gVal['blogProvider'] = gConst['prodiverNetease'];
        logging.info("Your blog provider : Netease 163 Blog.");
    else :
        logging.error("Can not find out blog provider from %s", inputUrl);
        sys.exit(2);

################################################################################
# Common Functions for different blog provider: baidu/netease(163)
# you can implement following functions to support move additional blog provider to wordpress
################################################################################

#------------------------------------------------------------------------------
# extract title fom soup
def extractTitle(soup):
    return callBlogFunc(extractTitle, soup);

#------------------------------------------------------------------------------
# extract datetime fom soup
def extractDatetime(soup) :
    return callBlogFunc(extractDatetime, soup);

#------------------------------------------------------------------------------
# extract blog item content fom soup
def extractContent(soup) :
    return callBlogFunc(extractContent, soup);
#------------------------------------------------------------------------------
# extract category from soup
def extractCategory(soup) :
    return callBlogFunc(extractCategory, soup);
    
#------------------------------------------------------------------------------
# extract tags info from soup
def extractTags(soup) :
    return callBlogFunc(extractTags, soup);

#------------------------------------------------------------------------------
# fetch and parse comments
def fetchAndParseComments(url, soup):
    return callBlogFunc(fetchAndParseComments, url, soup);

#------------------------------------------------------------------------------
def findNextPermaLink(soup):
    return callBlogFunc(findNextPermaLink, soup);

#------------------------------------------------------------------------------
def parseDatetimeStrToLocalTime(datetimeStr):
    return callBlogFunc(parseDatetimeStrToLocalTime, datetimeStr);

#------------------------------------------------------------------------------
def getProcessPhotoCfg() :
    return callBlogFunc(getProcessPhotoCfg);

#------------------------------------------------------------------------------
# extract blog title and description
def extractBlogTitAndDesc(blogEntryUrl) :
    return callBlogFunc(extractBlogTitAndDesc, blogEntryUrl);

#------------------------------------------------------------------------------
def extractBlogUser(inputUrl):
    return callBlogFunc(extractBlogUser, inputUrl);

#------------------------------------------------------------------------------
def find1stPermalink() :
    return callBlogFunc(find1stPermalink);

####### Login Mode ######
#------------------------------------------------------------------------------
def loginBlog(username, password) :
    return callBlogFunc(loginBlog, username, password);

#------------------------------------------------------------------------------
# check whether this post is private(self only) or not
def isPrivatePost(soup) :
    return callBlogFunc(isPrivatePost, soup);

####### Modify post while in Login Mode ######
#------------------------------------------------------------------------------
# modify post content
def modifySinglePost(newPostContentUni, infoDict, inputCfg):
    return callBlogFunc(modifySinglePost, newPostContentUni, infoDict, inputCfg);


###############################################################################
if __name__=="__main__":
    # for : python xxx.py -s yyy    # -> sys.argv[0]=xxx.py
    # for : xxx.py -s yyy           # -> sys.argv[0]=D:\yyy\zzz\xxx.py
    scriptSelfName = crifanLib.extractFilename(sys.argv[0]);

    logging.basicConfig(
                    level    = logging.DEBUG,
                    format   = 'LINE %(lineno)-4d  %(levelname)-8s %(message)s',
                    datefmt  = '%m-%d %H:%M',
                    filename = scriptSelfName + ".log",
                    filemode = 'w');
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler();
    console.setLevel(logging.INFO);
    # set a format which is simpler for console use
    formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s');
    # tell the handler to use this format
    console.setFormatter(formatter);
    logging.getLogger('').addHandler(console);
    try:
        main();
    except:
        logging.exception("Unknown Error !");
        raise;