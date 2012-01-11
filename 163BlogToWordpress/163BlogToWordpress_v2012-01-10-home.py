#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
【简介】
此脚本作用是：
将163博客中的文章/帖子的所有内容（文章，分类，标签，评论，图片），全部都下载下来，导出为xml文件。
此xml文件是符合RSS 2.0规范的，可以被WordPress所识别的（WordPress eXtended RSS），
可以被导入到WordPress中去。
由此实现将163博客的所有内容搬家到WordPress中去。

【使用说明】
1.安装Python 2.7.2
http://www.python.org/ftp/python/2.7.2/python-2.7.2.msi
下载后，安装即可。

2.安装BeautifulSoup
http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.0.6.py
下载后，改名为BeautifulSoup.py，再拷贝到与此脚本同目录即可。

3.安装Python的chardet库
从chardet的官网：
http://pypi.python.org/pypi/chardet#downloads
下载：chardet-1.0.1-py2.5.egg，然后改名为：chardet-1.0.1-py2.5.egg.zip
解压后，将chardet-1.0.1-py2.5.egg下面的chardet文件夹，连带其下所有文件，一起都拷贝到你的：
你的python的安装目录\Lib\site-packages下面，即可。

4.脚本使用方法：
在Windows的命令行(开始->运行->cmd->回车)中运行命令：
当前脚本名称 -s 你的博客名称地址
例如：
163BlogToWordpress.py -s http://againinput4.blog.163.com/
然后脚本就可以把你163博客中的所有帖子，评论，图片等，都下载导出为Wordpress可识别的XML文件。
如果导出xml文件大小超过2MB，还会帮你自动分割，省却你再用DivXML工具分割了。
更多高级功能，参见下面的详细功能列表。

【版本信息】
版本：     v2012-01-10
作者：     crifan
联系方式： http://www.crifan.com
           green-waste (at) 163.com

【背景说明】
1. 此脚本已在此环境下成功运行：
Win7 + Python 2.7.2 + BeautifulSoup 3.0.6 + Wordpress 3.3 zh-CN

2. 此脚本的最始版本是：
http://www.yhustc.com/exp/other/BlogMover.zip
中的163-blog-mover.py为基础，
而改写的，因为该版本是之前写的，由于163博客改版了，导致脚本失效。
我是在其基础上，重写了绝大部分的内容，另外又增添了很多其他功能。

【详细的功能列表】
1. 对于通过-s参数传入的源URL地址，支持多种格式
    例如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/
    163BlogToWordpress.py -s http://againinput4.blog.163.com/blog
    163BlogToWordpress.py -s http://againinput4.blog.163.com/blog/
    163BlogToWordpress.py -s http://againinput4.blog.163.com/blog/static/17279949120111127055419/
    都可以自动识别，并且帮你找到你的163博客的最早发布的那篇文章（first permanent link)，然后依次导出所有的帖子内容。

    (1) 如果你不想让程序自动去分析出163博客里面最早发布的那篇帖子的地址，你也可以手动用-f参数指定，例如：
    163BlogToWordpress.py -f http://againinput4.blog.163.com/blog/static/172799491201091513711591/
    当然，你也可以通过-f参数指定从某篇文章开始，然后输出其本身及时间上在其之后发表的所有的文章，比如：
    163BlogToWordpress.py -f http://againinput4.blog.163.com/blog/static/17279949120111127055419/
    （2）你可以通过-l参数来指定只输出多少篇文章，比如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -l 100
    可见，通过-f和-l的搭配使用，你可以自己任意指定，输出博客中的任何一部分帖子内容。

2.支持导出博客帖子的各种详细信息
    对于输出的帖子的内容，支持内容较全，包括：
    标题，链接地址，作者，发布日期，发布帖子所用的易读易记的名字(post name)，所属的分类，标签等。

3.（默认启用）支持下载导出评论的详细信息
    支持帖子所相关的评论信息的导入，其中包括每个评论的详尽的信息：
    评论内容，评论作者，评论作者的链接，评论作者的IP，日期等。
    (1)如果你不想要下载和输出评论信息，可以指定'-c no'参数去禁止下载和导出评论信息，例如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -c no

4.（默认启用）支持图片下载和图片链接替换
    支持下载帖子中所包含的你自己163博客的图片，并且支持自动把帖子中的地址，换为你所要的地址。
    下载下来的图片，默认是放在 当前文件夹\你的博客用户\pic 中。
    (1) 图片链接的替换规则：
    默认的是将这样的图片地址：
    http://imgAAA.BBB.126.net/CCC/DDD.EEE
    其中：AAA=None/1/3/6/7/182/..., BBB=ph/bimg, CCC=gA402SeBEI_fgrOs8HjFZA==/uCnmEQiWL40RrkIJnXKjsA==, DDD=2844867589615022702/667940119751497876, EEE=jpg
    替换为：
    gCfg['picPathInWP']/DDD.EEE
    其中gCfg['picPathInWP']可以通过后面要介绍的-w参数去配置。
    gCfg['picPathInWP']默认配置为：
    http://localhost/wordpress/wp-content/uploads/BLOG_USER/pic
    其中BLOG_USER是从你输入的地址中提取出来的博客用户名。
    2.可以用-w自己指定所要替换的图片地址
    例如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -w http://localhost/wordpress/wp-content/uploads/pic/163
    当然，为了保证图片正常显示，你需要确认的是：
    A.你的wordpress中也要存在对应的目录
    B.你要手动把下载的图片拷贝到wordpress的对应的路径中去。
    (2) 你也可以通过'-p no'去禁止上述下载并替换图片的功能，例如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -p no
    (3) 在开启了上述处理图片的功能的前提下，默认会开启处理其他网站图片的功能
    对于博客中存在其他网站（非163博客的图片），可以下载对应的图片到：
    当前文件夹\你的博客用户\pic\other_site
    然后对应的地址替换为 -w指定的地址 + other_site
    例如：
    http://beauty.pba.cn/uploads/allimg/c110111/1294G0I9200Z-2b3F.jpg
    替换为：
    http://localhost/wordpress/wp-content/uploads/BLOG_USER/pic/other_site/beauty_pba_1294G0I9200Z-2b3F.jpg
    (4) 如果不需要处理替他网站的图片，可以通过 -o no 去禁止此功能，比如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -o no
    (5) 类似地-w参数可以指定要替换的对于原先自己网站的图片的地址，可以通过-r指定对于其他网站的图片所要替换的地址。
    (6) (默认开启)添加了-e参数来开启或禁止近似图片忽略功能
    对于后面处理的某个图片的url，和之前某个出了错的图片地址，如果发现相似，那么就忽略处理此图片。

5. （默认启用）支持(google)翻译功能
    将原先一些中文句子，翻译为对应的英文。
    此功能是为了方便wordpress中，直接可以使用这些已经翻译好的，易读易懂的URL固定链接，去访问对应的博客帖子。
    同时也方便了SEO优化。
    目前的翻译支持，包括博客的帖子的标题的别名(post name)和目录的别名(nice name)。
    
    举例：
    某帖子标题(title)是：                                             “关于本博客的介绍”
    如果不翻译，那么帖子的别名(post name)就是：                       “%E5%85%B3%E4%BA%8E%E6%9C%AC%E5%8D%9A%E5%AE%A2%E7%9A%84%E4%BB%8B%E7%BB%8D”
    翻译成英文变为：                                                  ”Introduction on this blog“
    再去除（字母，数字，下划线，短横线之外的）非法的字符后，最终变成：“Introduction_on_this_blog”
    对应wordpress中帖子的固定链接，就从：
    http://localhost/2008/04/19/%E5%85%B3%E4%BA%8E%E6%9C%AC%E5%8D%9A%E5%AE%A2%E7%9A%84%E4%BB%8B%E7%BB%8D/
    变为了：
    http://localhost/2008/04/19/introduction_on_this_blog/
    
    (1) 翻译功能，虽然好用，但是可能会消耗较长时间，所以，如果你不需要此功能，
    或者为了省时间暂时禁止翻，可以通过指定参数‘-t no’去禁止相应的翻译功能：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -t no

6.  支持XML文件超限自动分割
    默认所输出的XML文件，最大2MB，超过此限制，就会自动分割为多个XML文件。
    (1) 当然，你也可以通过'-x 最大字节数'来指定XML的最大限制，单位是字节，例如(200KB=200*1024=204800)：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -x 204800
    同理，如果你不想要XML自动分割功能，那么可以指定一个很大的数值，即可。

7. 支持指定帖子发布地址前缀
    默认情况下，会将帖子的链接地址设置为:
    http://localhost/?p=
    然后加上对应的postID，组成了帖子的发布地址，
    你可以通过'-a addr'的方式指定帖子发布地址的前缀，例如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -a http://www.crifan.com/?p=

8. 支持指定起始的PostID
    默认帖子的PostID是以0为开头的。
    如果有这类需求，已经用脚本将一个163博客导出xml并导入wordpress了，该空间一共100个帖子。
    然后再去搬家另外一个163博客，此时，可以指定postID的起始值为100，例如：
    163BlogToWordpress.py -s http://againinput4.blog.163.com/ -i 100
    然后生成的xml中的帖子链接地址中的postID，就会以100为起始，自动增加了。

10. 统计信息和显示信息
    (1)支持在脚本执行的最后，显示当前脚本中每部分的处理所花费的时间
    (2)支持每处理完10个帖子，打印以后提示信息，以免执行时间太长，勿让使用者以为脚本挂了

【其他说明】
1.关于脚本执行速度
实测多个163博客，帖子：内容+评论+图片+翻译，平均每个帖子消耗1.2秒左右。
如果去掉翻译，估计会快不少，有空待添加此处的测试数据。

2.为何输出的log日志不用中文？
输出日志为中文需要至少两点：
一是，你运行脚本所用到的命令行cmd的本地语言，需要设置为（936 ANSI/OEM - 简体中文 GBK），而不能是默认的（437 OEM - 美国）。
二是，脚本里面输出GBK的话，logging系统，好像没找到可以设置编码格式的，需要手动写logging for GBK的小函数转换一下。
鉴于以上两点，一个是麻烦脚本使用者，一个是麻烦作者，所以，日志输出为英文，免去乱码的尴尬。

3.为何没有提供正序和倒序选项配置？
简单说就是，因为wordpress中，对于你所输出的博客帖子(item)的顺序，是无关的。
其自动会导入所有的帖子(item)，而不会关心item在rss文件中的顺序和位置。

4.翻译功能，可能占用较多时间
一般情况下，翻译功能可能并不会太耗时，但是在网速不太好等情况下，翻译功能可能会占用太多时间。
如果你发现执行时间太慢，可能是翻译功能占用了较多时间，此时可以考虑尝试一下'-t no'参数来禁止翻译，看看速度是否加快。

-------------------------------------------------------------------------------
"""

#---------------------------------import---------------------------------------
import os
import re
import sys
import math
import time
import random
import codecs
import pickle
import logging
import binascii
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup,Tag,CData
from datetime import datetime,timedelta
from optparse import OptionParser
from string import Template,replace
import xml
from xml.sax import saxutils
#import ast # only available in Python 2.6
#import Image
import chardet

#--------------------------------const values-----------------------------------
__VERSION__ = "v2012-01-10"

gConst = {
    'generator'         : "http://www.crifan.com",
    'blogDomain163'     : 'http://blog.163.com',
    'blogApi163'        : "http://api.blog.163.com",
    'tailInfo'          : """

    </channel>
    </rss>""",
    'picRootPathInWP'   : "http://localhost/wordpress/wp-content/uploads",
    # also belong to ContentTypes, more info can refer: http://kenya.bokee.com/3200033.html
    # here use Tuple to avoid unexpected change
    # note: for tuple, refer item use tuple[i], not tuple(i)
    'validPicSufList'   : ('bmp', 'gif', 'jpeg', 'jpg', 'jpe', 'png', 'tiff', 'tif'),
    'othersiteDirName'  : 'other_site',
}

#----------------------------------global values--------------------------------
gVal = {
    'entries'               : [],
    'catNiceDict'           : {}, # store { catName: catNiceName}
    'tagSlugDict'           : {}, # store { tagName: tagSlug}
    'postID'                : 0,
    'blogUser'              : '',
    'seflBlogMainUrl'       : '', # store main url for self blog
    'processedUrlList'      : [],
    'processedStUrlList'    : [],
    'replacedUrlDict'       : {},
    'exportFileName'        : '',
    'fullHeadInfo'          : '', #  include : header + category + generator
    'statInfoDict'          : {}, # store statistic info
    'calTimeKeyDict'        : {},
    'errorUrlList'          : [], # store the (pic) url, which error while open
    'picSufStr'             : '', # store the pic suffix char list
    'stInfo'                : {'fileName' : '', 'dirName' : '',},
}

#--------------------------configurable values---------------------------------
gCfg ={
# For defalut setting for following config value, please refer parameters.
    # where to save the downloaded pictures
    # Default (in code) set to: gVal['picRootPathInWP'] + '/' + gVal['blogUser'] + "/pic"
    'picPathInWP'       : '',
    # Default (in code) set to: gCfg['picPathInWP'] + '/' + gConst['othersiteDirName']
    'otherPicPathInWP'  : '',
    # process pictures or not
    'processPic'        : '',
    # process other site pic or not
    'processOtherPic'   : '',
    # omit process pic, which is similar before errored one
    'omitSimErrUrl'     : '',
    # need process ST music or not
    'needProcessSt'     : '',
    # do translate or not
    'doTrans'           : '',
    # process comments or not
    'processCmt'        : '',
    # post ID prefix address
    'postidPreAddr'     : '',
    # max/limit size for output XML file
    'maxXmlSize'        : 0,
    # function execute times == max retry number + 1
    # when fail to do something: fetch page/get comment/....) 
    'funcTotalExecNum'  : 1,
}

#--------------------------functions--------------------------------------------

#------------------------------------------------------------------------------
# just print whole line
def printDelimiterLine() :
    logging.info("%s", '-'*80)
    return 

#------------------------------------------------------------------------------
# check whether the strToDect is ASCII string
def isAsciiString(strToDect) :
    isAscii = False
    encInfo = chardet.detect(strToDect)
    if (encInfo['confidence'] > 0.9) and (encInfo['encoding'] == 'ascii') :
        isAscii = True
    return isAscii

#------------------------------------------------------------------------------
# open export file name in rw mode, return file handler
def openExportFile():
    global gVal
    # 'a+': read,write,append
    # 'w' : clear before, then write
    return codecs.open(gVal['exportFileName'], 'a+', 'utf-8')

#------------------------------------------------------------------------------
# just create output file
def createOutputFile():
    global gVal
    gVal['exportFileName'] = 'blog_163_[' + gVal['blogUser'] + "]_" + datetime.now().strftime('%Y%m%d_%H%M')+ '-0' + '.xml'
    f = codecs.open(gVal['exportFileName'], 'w', 'utf-8')
    if f:
        logging.info('Created export XML file: %s', gVal['exportFileName'])
        f.close()
    else:
        logging.error("Can not open writable exported file: %s",gVal['exportFileName'])
        sys.exit(2)
    return

#------------------------------------------------------------------------------
# add CDATA, also validate it for xml
def packageCDATA(info):
    #info = saxutils.escape('<![CDATA[' + info + ']]>')
    info = '<![CDATA[' + info + ']]>'
    return info

#------------------------------------------------------------------------------
# generate the full url, which include the main url plus the parameter list
def genFullUrl(mainUrl, paraDict) :
    fullUrl = ''
    fullUrl += mainUrl
    fullUrl += '?'
    for para in paraDict.keys() :
        fullUrl += '&' + str(para) + '=' + str(paraDict[para])
    return fullUrl

#------------------------------------------------------------------------------
# generate request comment URL from blog item URL
def genReqCmtUrl(soup, startCmtIdx, onceGetNum):
    global gConst
    
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
        fskClassInfo = soup.find(attrs={"class":"phide nb-init"})
        textarea_js = fskClassInfo.find(attrs={"name":"js"})
        fksStr = textarea_js.contents[0]
        matched = re.compile(r"id:'(fks_[0-9]+)',").search(fksStr)
        foundFks = matched.group(1)
        logging.debug("Found fks %s", foundFks)

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
        }
        paraDict['c0-param0'] = "string:" + str(foundFks)
        paraDict['c0-param1'] = "number:" + str(onceGetNum)
        paraDict['c0-param2'] = "number:" + str(startCmtIdx)
        
        mainUrl = gConst['blogApi163'] + '/' + gVal['blogUser'] + '/dwr/call/plaincall/BlogBeanNew.getComments.dwr'
        getCmtUrl = genFullUrl(mainUrl, paraDict)
        
        logging.debug("getCmtUrl=%s",getCmtUrl)
    except :
        logging.debug("Fail to generate comment url")
    
    return getCmtUrl;

#------------------------------------------------------------------------------
# generate get blogs URL
def genGetBlogsUrl(userId, startBlogIdx, onceGetNum):
    getBlogsUrl = ''

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
        }
        paraDict['c0-param0'] = "number:" + str(userId)
        paraDict['c0-param1'] = "number:" + str(startBlogIdx)
        paraDict['c0-param2'] = "number:" + str(onceGetNum)
        
        mainUrl = gConst['blogApi163'] + '/' + gVal['blogUser'] + '/' + 'dwr/call/plaincall/BlogBeanNew.getBlogs.dwr'
        getBlogsUrl = genFullUrl(mainUrl, paraDict)

        logging.debug("Generated get blogs url %s", getBlogsUrl)
    except :
        loggin.error("Can not generate get blog url.")

    return getBlogsUrl

#------------------------------------------------------------------------------
# convert the xxx=yyy into tuple('xxx', yyy), then return the tuple value
# [makesure input string]
# (1) is not include whitespace
# (2) include '='
# (3) last is no ';'
# [possible input string]
# blogUserName="againinput4"
# publisherEmail=""
# synchMiniBlog=false
# publishTime=1322129849397
# publisherName=null
# publisherNickname="\u957F\u5927\u662F\u70E6\u607C"
def convertToTupleVal(equationStr) :
    (key, value) = ('', None)

    try :
        # Note:
        # here should not use split with '=', for maybe input string contains string like this:
        # http://img.bimg.126.net/photo/hmZoNQaqzZALvVp0rE7faA==/0.jpg
        # so use find('=') instead
        firstEqualPos = equationStr.find("=")
        key = equationStr[0:firstEqualPos]
        valuePart = equationStr[(firstEqualPos + 1):]

        # string type
        valLen = len(valuePart)
        if valLen >= 2 :
            # maybe string
            if valuePart[0] == '"' and valuePart[-1] == '"' :
                # is string type
                value = str(valuePart[1:-1])
            elif valuePart == 'null':
                value = None
            elif (valuePart == 'false') or (valuePart == 'False') :
                value = False
            elif (valuePart == 'true') or (valuePart == 'True') :
                value = True
            else :
                # must int value
                value = int(valuePart)
        else :
            # len=1 -> must be value
            value = int(valuePart)

        #logging.debug("Convert %s to [%s]=%s", equationStr, key, value)
    except :
        logging.warning("Fail of convert the equal string %s to value", equationStr)

    return (key, value)
#------------------------------------------------------------------------------
# parse each comment response line string into a dict value
def removeEmptyInList(list) :
    newList = []
    for val in list :
        if val :
            newList.append(val)
    return newList

#------------------------------------------------------------------------------
# parse the subComments field, to get the parent idx
def parseSubComments(subComments) :
    # s0.subComments=s2
    equalSplited = subComments.split("=")
    sChild = equalSplited[1] # s2
    childIdx = int(sChild[1:]) # 2
    return childIdx

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
        cmtDict = {}
        
        # 1. handel special fields,
        # for these field may contain special char and ';',
        # so find and process them firstly
        # (1) handle special ['abstract']
        abstratP = r"s([0-9]+)\['abstract'\]=" + r'"(.*)' + r'";s[0-9]+\.blogId="'
        foundAbs = re.search(abstratP, line)
        cmtIdx = foundAbs.group(1)
        cmtDict['curCmtIdx'] = int(cmtIdx)
        cmtDict['curCmtNum'] = cmtCurNum
        cmtDict['parentCmtNum'] = 0 # default to 0, need later update if necessary
        cmtDict['abstract'] = foundAbs.group(2)
        line = line[(foundAbs.end(2) + 2):] # 2 means ";

        # (2) handle special .blogTitle
        titleP = r'";s' + str(cmtIdx) + "\.blogTitle=" + r'"(.*)' + r'";s' + str(cmtIdx) +'\.blogUserId='
        foundTitle = re.search(titleP, line)
        cmtDict['blogTitle'] = foundTitle.group(1)
        beforeTitle = line[:(foundTitle.start(0) + 2)] # include ;"
        afterTitle = line[(foundTitle.end(1) + 2):] # exclude ";
        line = beforeTitle + afterTitle

        # (3) handle special .content
        contentP = r";s" + str(cmtIdx) + "\.content=" + r'"(.*)' + r'";s' + str(cmtIdx) +'\.id="'
        foundContent = re.search(contentP, line)
        cmtDict['content'] = foundContent.group(1)
        beforeContent = line[:(foundContent.start(0) + 1)] # include ;
        afterContent = line[(foundContent.end(1) + 2):] # exclude ";
        line = beforeContent + afterContent
        
        # before use ';' to split, makesure it not contain unicode like char == &#XXX;
        # Note:
        # after test, HTMLParser.unescape can not use here, so use following :
        # replace the &shy; and &#10084; to corresponding \uXXXX
        # (1) replace string entity to number entity:   &shy; -> &#173;
        #logging.debug("---before replace string entity to number entity---\n%s", line)
        line = replaceStrEntToNumEnt(line)
        #logging.debug("---after replace string entity to number entity---\n%s", line)
        # (2) replace number entity into \uXXXX:        &#10084; -> \u2764
        line = replaceChrEntityToSlashU(line)
        #logging.debug("---after replace number entity into \uXXXX---\n%s", line)
        line = removeColonInPublisherNickname(line)
        #logging.debug("---after remove colon in PublisherNickname field ---\n%s", line)
    
        # 2. process main fields
        # (1) split
        semiSplited = line.split(";") # semicolon splited
        #logging.debug("semiSplited=\n%s",semiSplited)
        # (2) remove un-process line
        semiSplited = removeEmptyInList(semiSplited)
        subComments = semiSplited.pop(len(semiSplited) - 3)# remove subComments
        childIdx = parseSubComments(subComments)
        cmtDict['childCmtIdx'] = childIdx
        # (3) remove sN., N=0,1,2,...
        idxLen = len(str(cmtIdx))
        equationList = []
        for eachLine in semiSplited:
            eachLine = eachLine[(1 + idxLen + 1):] # omit sN. (N=0,1,2,...)
            equationList.append(eachLine)
        # (4) convert to value
        for equation in equationList :
            (key, value) = convertToTupleVal(equation)
            cmtDict[key] = value

        # notes:
        # (1) here not convert unicode-escape for later process
        # (2) most mainComId and replyComId is '-1', but some is:
        # s59.mainComId = "fks_081075082083084068082095094095085084086069083094084065080";
        # s54.replyComId = "fks_081075082080085066086086082095085084086069083094084065080";
    except :
        logging.warning("Fail to parse comment resopnse. Current comment number=%d", cmtCurNum)

    return cmtDict

#------------------------------------------------------------------------------
# check whether comment type is normal:
# s10['abstract']="...
def isNormalCmt(line) :
    foundNormal = re.search(r"s[0-9]+\['abstract'\]=.*", line)
    if foundNormal :
        return True
    else :
        return False

#------------------------------------------------------------------------------
# parse something like: s241[0]=s242;s241[1]=s243;
# into {childCommentNumber : parentCommentNumber} info
def extractParentRelation(line) :
    global gVal
    cmtParentRelation = {}
    equationList = line.split(";")
    equationList = removeEmptyInList(equationList)
    logging.debug("Parsed %s into:", line)
    for equation in equationList:
        match = re.compile(r's([0-9]+)\[([0-9]+)\]=s([0-9]+)').search(equation)
        int1 = int(match.group(1))
        int2 = int(match.group(2))
        int3 = int(match.group(3))
        # here use record its idx, so not +1
        cmtParentRelation[int3] = int1
        logging.debug("     curIdx=%d, parIdx=%d", int3, int1)
    return cmtParentRelation

#------------------------------------------------------------------------------
# parse the dwr engine line, return the number of main comments
# possbile input:
# dwr.engine._remoteHandleCallback('1','0',[s0,s1]);
# dwr.engine._remoteHandleCallback('1','0',[]);
# dwr.engine._remoteHandleCallback('1','0',[s0,s1,...,s98,s99]);
def extratMainCmtNum(dwrEngine) :
    mainCmtNum = 0
    sN = re.compile(r".*\[(.*)\]").search(dwrEngine)
    if sN and sN.group(1) :
        # parse it
        sList = sN.group(1).split(",")
        mainCmtNum = len(sList)
    else :
        mainCmtNum = 0
    return mainCmtNum

#------------------------------------------------------------------------------
# convert the old {childIdx, parentIdx} to new {childIdx : parentNum}
def updateCmtRelation(oldDict, cmtList) :
    for cmt in cmtList:
        for childIdx in oldDict.keys() :
            if cmt['childCmtIdx'] == oldDict[childIdx] :
                oldDictChildIdx = oldDict[childIdx]
                oldDict[childIdx] = cmt['curCmtNum']
                # note: here this kind of method, can change the original input oldDict[childIdx]
                logging.debug("Updated comment relation: from %d:%d to %d:%d", childIdx, oldDictChildIdx, childIdx, oldDict[childIdx])
    return oldDict

#------------------------------------------------------------------------------
# parse the returned comments response info
def parseCmtRespInfo(cmtResp, url, startCmtNum):
    retCmtDictList = []
    mainCmtNum = 0

    try :
        lines = cmtResp.split("\r\n")
        noBlankLines = removeEmptyInList(lines)
        # remove the 0,1,-1 line
        noBlankLines.pop(0) # //#DWR-INSERT
        noBlankLines.pop(0) # //#DWR-REPLY
        # eg: dwr.engine._remoteHandleCallback('1','0',[s0,s1]);
        dwrEngine = noBlankLines.pop(len(noBlankLines) - 1)
        mainCmtNum = extratMainCmtNum(dwrEngine)
        
        if noBlankLines :
            # handle first line -> remove var sN=xxx
            beginPos = noBlankLines[0].find("s0['abstract']")
            noBlankLines[0] = noBlankLines[0][beginPos:]

            cmtList = []
            relationDict = {}
            cmtCurNum = startCmtNum
            for line in noBlankLines :
                #logging.debug("%s", line)
                if isNormalCmt(line) :
                    singleCmtDict ={}
                    singleCmtDict = parseCmtRespStr(line, cmtCurNum)
                    cmtList.append(singleCmtDict)
                    
                    cmtCurNum += 1
                else :
                    # something like: s241[0]=s242;s241[1]=s243;
                    parsedRelation = extractParentRelation(line)
                    # add into whole relation dict
                    for childIdx in parsedRelation.keys() :
                        relationDict[childIdx] = parsedRelation[childIdx]
            # update the index relation
            updateCmtRelation(relationDict, cmtList)
            # update parent index info then add to list
            for cmt in cmtList :
                if cmt['curCmtIdx'] in relationDict :
                    cmt['parentCmtNum'] = relationDict[cmt['curCmtIdx']]
                    logging.debug("Updated comment parent info: curNum=%d, parentNum=%d", cmt['curCmtNum'], cmt['parentCmtNum'])
                retCmtDictList.append(cmt)

            logging.debug("Parsed %d comments", cmtCurNum - startCmtNum)
            #logging.debug("-------comment list---------")
            #for cmt in retCmtDictList :
            #    logging.debug("%s", cmt)
        else :
            logging.debug("Parsed result is no comment.")
    except :
        logging.warning("Parse number=%d comment fail for url= %s", cmtCurNum, url)

    return (retCmtDictList, mainCmtNum)

#------------------------------------------------------------------------------
# get comments for input url of one blog item
# return the converted dict value
def fetchComments(url, soup):
    cmtList = []

    # init before loop
    needGetMoreCmt = True
    startCmtIdx = 0
    startCmtNum = 1
    onceGetNum = 1000 # get 1000 comments once
    
    try :
        while needGetMoreCmt :
            cmtUrl = genReqCmtUrl(soup, startCmtIdx, onceGetNum)
            cmtReq = urllib2.Request(cmtUrl)
            cmtRetInfo = urllib2.build_opener().open(cmtReq).read()
            #logging.debug("---------got comment original response ------------\n%s", cmtRetInfo)
            (parsedCmtList, mainCmtNum) = parseCmtRespInfo(cmtRetInfo, url, startCmtNum)

            if parsedCmtList :
                # add into ret list
                cmtList.extend(parsedCmtList)
                cmtNum = len(parsedCmtList)
                logging.debug("Currently got %d comments for idx=[%d-%d]", cmtNum, startCmtIdx, startCmtIdx + onceGetNum - 1)
                if mainCmtNum < onceGetNum :
                    # only got less than we want -> already got all comments
                    needGetMoreCmt = False
                    logging.debug("Now has got all comments.")
                else :
                    needGetMoreCmt = True
                    startCmtIdx += onceGetNum
                    startCmtNum += cmtNum
            else :
                needGetMoreCmt = False
    except :
        logging.warning("Fail for fetch the comemnts(index=[%d-%d]) for %s ", startCmtIdx, startCmtIdx + onceGetNum - 1, url)

    return cmtList

#------------------------------------------------------------------------------
# check whether the input 163 blog user is other type user:
# (1) jdidi155@126     in http://blog.163.com/jdidi155@126
# (2) againinput4@yeah in http://blog.163.com/againinput4@yeah/
# note:
# for some extremly special ones:
# hi_ysj -> http://blog.163.com/hi_ysj
def isOtherTypeUser(blogUser) :
    isOthertype = False
    if blogUser and (len(blogUser) > 4 ) :
        if blogUser[-4:] == '@126' :
            isOthertype = True
        elif blogUser[-4:] == '@yeah' :
            isOthertype = True
        else :
            isOthertype = False
    return isOthertype

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
def gen163UserUrl(blogUser) :
    global gConst
    url = ''
    try :
        # http://owecn.blog.163.com/blog/static/862559512011112684224161/
        # whose comments contain 'publisherName'=None
        if blogUser :
            if isOtherTypeUser(blogUser) :
                url = gConst['blogDomain163'] + "/" + blogUser
            else : # is normal
                url = "http://" + blogUser + ".blog.163.com"
    except :
        logging.error("Can not generate blog user url for input blog user %s", blogUser)
    return url

#------------------------------------------------------------------------------
# convert local GMT8 to GMT time
# note: input should be 'datetime' type, not 'time' type
def localToGmt0(localTime) :
    return localTime - timedelta(hours=8)

#------------------------------------------------------------------------------
# fill source comments dictionary into destination comments dictionary
def fillComments(destCmtDict, srcCmtDict):
    logging.debug("--------- source comment: idx=%d, num=%d ---------",
        srcCmtDict['curCmtIdx'], srcCmtDict['curCmtNum'])
    #for item in srcCmtDict.items() :
    #    logging.debug("%s", item)
    destCmtDict['id'] = srcCmtDict['curCmtNum']

    destCmtDict['author'] = packageCDATA(srcCmtDict['publisherNickname'].decode('unicode-escape'))
    destCmtDict['author_email'] = srcCmtDict['publisherEmail']
    destCmtDict['author_url'] = saxutils.escape(gen163UserUrl(srcCmtDict['publisherName']))
    destCmtDict['author_IP'] = srcCmtDict['ip']
    
    # method 1:
    #epoch1000 = srcCmtDict['publishTime']
    #epoch = float(epoch1000) / 1000
    #localTime = time.localtime(epoch)
    #gmtTime = time.gmtime(epoch)
    # method 2:
    pubTimeStr = srcCmtDict['shortPublishDateStr'] + " " + srcCmtDict['publishTimeStr']
    localTime = datetime.strptime(pubTimeStr, "%Y-%m-%d %H:%M:%S")
    gmtTime = localToGmt0(localTime)
    destCmtDict['date'] = localTime.strftime("%Y-%m-%d %H:%M:%S")
    destCmtDict['date_gmt'] = gmtTime.strftime("%Y-%m-%d %H:%M:%S")

    # handle some speical condition
    #logging.debug("before decode, coment content:\n%s", srcCmtDict['content'])
    cmt_content = srcCmtDict['content'].decode('unicode-escape') # convert from \uXXXX to character
    #logging.debug("after decode, coment content:\n%s", cmt_content)
    # remove invalid control char in comments content
    cmt_content = removeCtlChr(cmt_content)
    destCmtDict['content'] = packageCDATA(cmt_content)

    destCmtDict['approved'] = 1
    destCmtDict['type'] = ''
    destCmtDict['parent'] = srcCmtDict['parentCmtNum']
    destCmtDict['user_id'] = 0

    logging.debug("author=%s", destCmtDict['author'])
    logging.debug("author_email=%s", destCmtDict['author_email'])
    logging.debug("author_IP=%s", destCmtDict['author_IP'])
    logging.debug("author_url=%s", destCmtDict['author_url'])
    logging.debug("date=%s", destCmtDict['date'])
    logging.debug("date_gmt=%s", destCmtDict['date_gmt'])
    logging.debug("content=%s", destCmtDict['content'])
    logging.debug("parent=%s", destCmtDict['parent'])

    return destCmtDict

#------------------------------------------------------------------------------
# remove overlapped item in the list
def uniqueList(old_list):
    newList = []
    for x in old_list:
        if x not in newList :
            newList.append(x)
    return newList

#------------------------------------------------------------------------------
# for listToFilter, remove the ones which is in listToCompare
# also return the ones which is already exist in listToCompare
def filterList(listToFilter, listToCompare) :
    filteredList = []
    existedList = []
    for singleOne in listToFilter : # remove processed
        if (not(singleOne in listToCompare)) :
            # omit the ones in listToCompare
            filteredList.append(singleOne)
        else :
            # record the already exist ones
            existedList.append(singleOne)
    return (filteredList, existedList)

#------------------------------------------------------------------------------
# check pic validation:
# open pic url to check return info is match or not
# with exception support
# note: should handle while the pic url is redirect
# eg :
# http://publish.it168.com/2007/0627/images/500754.jpg ->
# http://img.publish.it168.com/2007/0627/images/500754.jpg
def isPicValid(picUrl) :
    global gConst

    picIsValid = False
    errReason = ''

    try :
        ret_picUrl = urllib2.urlopen(picUrl) # note: Python 2.6 has added timeout support.
        realUrl = ret_picUrl.geturl()
        urlInfo = ret_picUrl.info()
        contentLen = urlInfo['Content-Length']
        # eg: Content-Type= image/gif
        # more ContentTypes can refer: http://kenya.bokee.com/3200033.html
        contentType = urlInfo['Content-Type']
        picSuffix = contentType.split("/")[1]
        #if (picSuffix in gConst['validPicSufList']) and (contentLen > 0) and (realUrl == picUrl):
        # for redirect, if returned size>0 and suffix is OK, also should be considered valid
        if (picSuffix in gConst['validPicSufList']) and (contentLen > 0):
            picIsValid = True
        else :
            picIsValid = False
            logging.waring("  Picture %s is invalid, returned info: type=%s, len=%d, realUrl=%s", contentType, contentLen, realUrl)
    except urllib2.URLError,reason :
        picIsValid = False
        errReason = reason
        logging.warning("  URLError when open %s, reason=%s", picUrl, reason)
    except urllib2.HTTPError,code :
        picIsValid = False
        errReason = code
        logging.warning("  HTTPError when open %s, code=%s", picUrl, code)
    except :
        picIsValid = False
        logging.warning("  Unknown error when open %s", picUrl)

    #errReason = str(errReason)
    return (picIsValid, errReason)

#------------------------------------------------------------------------------
# download from fileUrl then save to fileToSave
# with exception support
def downloadFile(fileUrl, fileToSave, needReport) :
    isDownOK = False
    downloadingFile = ''

    #---------------------------------------------------------------------------
    # note: totalFileSize -> may be -1 on older FTP servers which do not return a file size in response to a retrieval request
    def reportHook(copiedBlocks, blockSize, totalFileSize) :
        #global downloadingFile
        if copiedBlocks == 0 : # 1st call : once on establishment of the network connection
            logging.debug('Begin to download %s, total size=%d', downloadingFile, totalFileSize)
        else : # rest call : once after each block read thereafter
            logging.debug('Downloaded bytes: %d', blockSize * copiedBlocks)
        return
    #---------------------------------------------------------------------------

    try :
        downloadingFile = fileUrl

        calcTimeStart('download_one_file')
        logging.info("  Downloading %s", downloadingFile)
        if needReport :
            urllib.urlretrieve(fileUrl, fileToSave, reportHook)
        else :
            urllib.urlretrieve(fileUrl, fileToSave)
        downOneFileTime = calcTimeEnd('download_one_file')
        if downOneFileTime > 1.0 : # if spend too long, record it
            logging.debug("download file %s spend %.2f second", fileUrl, downOneFileTime)
        logging.debug("Saved %s to %s", fileUrl, fileToSave)
        isDownOK = True
    except urllib.ContentTooShortError(msg) :
        isDownOK = False
        logging.warning("ContentTooShortError while downloading %s, msg=%s", fileUrl, msg)
    except :
        isDownOK = False
        logging.warning("Error while downloading %s", fileUrl)

    return isDownOK

#------------------------------------------------------------------------------
# check whether two url is similar
# note: input two url both should be str type
def urlIsSimilar(url1, url2) :
    isSim = False

    url1 = str(url1)
    url2 = str(url2)

    slashList1 = url1.split('/')
    slashList2 = url2.split('/')
    lenS1 = len(slashList1)
    lenS2 = len(slashList2)

    # all should have same structure
    if lenS1 != lenS2 :
        # not same sturcture -> must not similar
        isSim = False
    else :
        sufPos1 = url1.rfind('.')
        sufPos2 = url2.rfind('.')
        suf1 = url1[(sufPos1 + 1) : ]
        suf2 = url2[(sufPos2 + 1) : ]
        # at least, suffix should same
        if (suf1 == suf2) : 
            lastSlashPos1 = url1.rfind('/')
            lastSlashPos2 = url2.rfind('/')
            exceptName1 = url1[:lastSlashPos1]
            exceptName2 = url2[:lastSlashPos2]
            # except name, all other part should same
            if (exceptName1 == exceptName2) :
                isSim = True
            else :
                # except name, other part is not same -> not similar
                isSim = False
        else :
            # suffix not same -> must not similar
            isSim = False

    return isSim

#------------------------------------------------------------------------------
# found whether the url is similar in urlList
# if found, return True, similarSrcUrl
# if not found, return False, ''
def findSimilarUrl(url, urlList) :
    (isSimilar, similarSrcUrl) = (False, '')
    for srcUrl in urlList :
        if urlIsSimilar(url, srcUrl) :
            isSimilar = True
            similarSrcUrl = srcUrl
            break
    return (isSimilar, similarSrcUrl)

#------------------------------------------------------------------------------
# check the input errInfo whether is URL Error
# return True/False
# known type:
# HTTP Error 400: Bad Request
# HTTP Error 401: Unauthorized
# HTTP Error 403: Forbidden ( The server denied the specified Uniform Resource Locator (URL). Contact the server administrator.  )
# HTTP Error 404: Not Found
# HTTP Error 500: ( The specified network name is no longer available.  )
# HTTP Error 500: Internal Server Error
# HTTP Error 504: Gateway Time-out
# HTTP Error 504: Proxy Timeout ( The connection timed out.  )
# <urlopen error [Errno 10053] >
# <urlopen error [Errno 10060] >
def isUrlError(errInfo) :
    isUrlErrorType = False
    if errInfo :
        # makesure input is string, otherwise will cause error !!!
        errStr = str(errInfo)

        pattern = re.compile(r'HTTP Error', re.IGNORECASE)
        matched = pattern.search(errStr)
        if matched :
            isUrlErrorType = True
        else :
            pattern = re.compile(r'urlopen error', re.IGNORECASE)
            matched = pattern.search(errStr)
            if matched :
                isUrlErrorType = True

    return isUrlErrorType

#------------------------------------------------------------------------------
# 1. extract picture URL from blog content
# 2. process it:
#       remove overlapped 
#       remove processed
#       saved into the gVal['processedUrlList']
#       download
#       replace url
def processPhotos(blogContent):
    global gVal
    global gCfg
    global gConst

    if gCfg['processPic'] == 'yes' :
        try :
            calcTimeStart("process_all_picture")
            logging.debug("Begin to process all pictures")

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

            # here only extract last pic name contain: char,digit,-,_
            urlPattern = r'http://\w{1,20}\.\w{1,20}\.\w{1,10}[\.]?\w*/[\w%\-=]{0,50}[/]?[\w%\-/=]*/[\w\-\.]{1,100}\.[' + gVal['picSufStr'] +']{3,4}'

            # if matched, result for findall() is a list when no () in pattern
            matchedList = re.findall(urlPattern, blogContent)
            if matchedList :
                nonOverlapList = uniqueList(matchedList) # remove processed
                # remove processed and got ones that has been processed
                (filteredPicList, existedList) = filterList(nonOverlapList, gVal['processedUrlList'])
                if filteredPicList :
                    logging.debug("Filtered url list to process:\n%s", filteredPicList)
                    for curUrl in filteredPicList :
                        # to check is similar, only when need check and the list it not empty
                        if ((gCfg['omitSimErrUrl'] == 'yes') and gVal['errorUrlList']):
                            (isSimilar, simSrcUrl) = findSimilarUrl(curUrl, gVal['errorUrlList'])
                            if isSimilar :
                                logging.warning("  Omit process %s for similar with previous error url", curUrl)
                                logging.warning("               %s", simSrcUrl)
                                continue
                        # no matter:(1) it is pic or not, (2) follow search fail or not
                        # (3) latter fail to fetch pic or not -> still means this url is processed
                        gVal['processedUrlList'].append(curUrl)

                        # process this url
                        #                              1=field1    2=field2    3=field3                                4=fileName                     5=suffix
                        pattern = r'http://\w{1,20}\.(\w{1,20})\.(\w{1,10})[\.]?(\w*)/[\w%\-=]{0,50}[/]?[\w\-/%=]*/([\w\-\.]{1,100})\.([' + gVal['picSufStr'] + r']{3,4})'
                        searched = re.search(pattern, curUrl)
                        if searched :
                            origin_url = searched.group(0)
                            fd1     = searched.group(1) # for 163 pic, is ph/bimg
                            fd2     = searched.group(2) # for 163 pic, is 126
                            fd3     = searched.group(3) # for 163 pic, is net
                            fileName= searched.group(4)
                            suffix  = searched.group(5)
                            #print "origin_url=",origin_url
                            #print '1=',fd1,'2=',fd2,'3=',fd3,'4=',fileName,'5=',suffix
                            if suffix.lower() in gConst['validPicSufList'] :
                                # indeed is pic, process it
                                (picIsValid, errReason) = isPicValid(curUrl)
                                if picIsValid :
                                    # 1. prepare info
                                    nameWithSuf = fileName + '.' + suffix
                                    curPath = os.getcwd()
                                    dstPathOwnPic = curPath + '\\' + gVal['blogUser'] + '\\pic'
                                    # 2. create dir for save pic
                                    if (os.path.isdir(dstPathOwnPic) == False) :
                                        os.makedirs(dstPathOwnPic) # create dir recursively
                                        logging.info("Create dir %s for save downloaded pictures of own site", dstPathOwnPic)
                                    if gCfg['processOtherPic'] == 'yes' :
                                        dstPathOtherPic = dstPathOwnPic + '\\' + gConst['othersiteDirName']
                                        if (os.path.isdir(dstPathOtherPic) == False) :
                                            os.makedirs(dstPathOtherPic) # create dir recursively
                                            logging.info("Create dir %s for save downloaded pictures of other site", dstPathOtherPic)
                                    # 3. prepare info for follow download and save
                                    #if ((fd1=='ph') or (fd1=='bimg')) and (fd2=='126') and (fd3=='net') :
                                    if (fd2=='126') and (fd3=='net') :
                                        # is 163 pic
                                        # from http://imgAAA.BBB.126.net/CCC/DDD.EEE
                                        # AAA=None/1/3/6/7/182/..., BBB=ph/bimg, CCC=gA402SeBEI_fgrOs8HjFZA==/uCnmEQiWL40RrkIJnXKjsA==, DDD=2844867589615022702/667940119751497876, EEE=jpg
                                        # to   gCfg['picPathInWP']/DDD.EEE
                                        newPicUrl = gCfg['picPathInWP'] + '/' + nameWithSuf
                                        dstPicFile = dstPathOwnPic + '\\' + nameWithSuf
                                    else :
                                        # is othersite pic
                                        if gCfg['processOtherPic'] == 'yes' :
                                            newNameWithSuf = fd1 + '_' + fd2 + "_" + nameWithSuf
                                            newPicUrl = gCfg['otherPicPathInWP'] + '/' + newNameWithSuf
                                            dstPicFile = dstPathOtherPic + '\\' + newNameWithSuf
                                        else :
                                            dstPicFile = '' # for next not download
                                            #newPicUrl = curUrl
                                    # download pic and replace url
                                    if dstPicFile and downloadFile(curUrl, dstPicFile, False) :
                                        # replace old url with new url
                                        blogContent = re.compile(curUrl).sub(newPicUrl, blogContent)
                                        # record it
                                        gVal['replacedUrlDict'][curUrl] = newPicUrl
                                        logging.debug("Replace %s with %s", curUrl, newPicUrl)
                                        #logging.debug("After replac, new blog content:\n%s", blogContent)
                                else :
                                    #if (gCfg['omitSimErrUrl'] == 'yes') and isUrlError(errReason) :
                                    if (gCfg['omitSimErrUrl'] == 'yes'): # take all error pic into record
                                        # when this pic occur error, then add to list
                                        gVal['errorUrlList'].append(curUrl)
                # for that processed url, only replace the address
                if existedList :
                    for processedUrl in existedList:
                        # some pic url maybe is invalid, so not download and replace,
                        # so here only processed that downloaded and replaceed ones
                        if processedUrl in gVal['replacedUrlDict'] :
                            newPicUrl = gVal['replacedUrlDict'][processedUrl]
                            blogContent = re.compile(processedUrl).sub(newPicUrl, blogContent)
                            logging.debug("For processed url %s, not download again, only replace it with %s", processedUrl, newPicUrl)
            logging.debug("Done for process all pictures")
            gVal['statInfoDict']['processPicTime'] += calcTimeEnd("process_all_picture")
            logging.debug("Successfully to process all pictures")
        except :
            logging.warning('Process picture failed.')

    return blogContent

#------------------------------------------------------------------------------
# if input string include '%', should be converted into '%25', 25=0x25=37=ascii value for '%'
def convertToWpAddress(inputStr) :
    strInWpAddr = re.compile('%').sub('%25', inputStr)
    return strInWpAddr 

#------------------------------------------------------------------------------
#extract 163 blog user name
# eg: 
# (1) againinput4       in http://againinput4.blog.163.com/xxxxxx
#     zhao.geyu         in http://zhao.geyu.blog.163.com/xxx
# (2) jdidi155@126      in http://blog.163.com/jdidi155@126/xxx
#     againinput4@yeah  in http://blog.163.com/againinput4@yeah/xxx
# (3) hi_ysj            in http://blog.163.com/hi_ysj/
def extractBlogUser(inputUrl):
    global gVal
    global gCfg
    global gConst

    logging.debug("Extracting blog user from url=%s", inputUrl)

    if gVal['blogUser'] == '' :
        try :
            blog163com = ".blog.163.com"
            lenBlog163com = len(blog163com)

            blog163Str = "http://blog.163.com/"
            lenBlog163 = len(blog163Str)
            compEnd = lenBlog163 - 1 # compare end

            slashList = inputUrl.split("/")
            mainStr = slashList[2] # againinput4.blog.163.com or blog.163.com

            if inputUrl[0 : compEnd] == blog163Str[0: compEnd] :
                # is http://blog.163.com/jdidi155@126/...
                gVal['blogUser'] = slashList[3] # jdidi155@126
                gVal['seflBlogMainUrl'] = blog163Str + gVal['blogUser']
                logging.info("Extracted Blog user [%s] from %s", gVal['blogUser'], inputUrl)
            elif mainStr[(-(lenBlog163com)):] == blog163com :
                # is http://zhao.geyu.blog.163.com/...
                gVal['blogUser'] = mainStr[0:(-(lenBlog163com))] # zhao.geyu
                gVal['seflBlogMainUrl'] = "http://" + gVal['blogUser'] + blog163com
                logging.info("Extracted Blog user [%s] from %s", gVal['blogUser'], inputUrl)
            else :
                logging.error("Can not extract blog user form input URL: %s", inputUrl)
                sys.exit(2)
        except :
            logging.error("Can not extract blog user form input URL: %s", inputUrl)
            sys.exit(2)

    # update some related default value
    if gCfg['picPathInWP'] == '' :
        # % -> %25
        # eg: %D7%CA%C1%CF%CA%D5%BC%AF -> /%25D7%25CA%25C1%25CF%25CA%25D5%25BC%25AF
        blogUsrInWpAddr = convertToWpAddress(gVal['blogUser'])
        gCfg['picPathInWP'] = gConst['picRootPathInWP'] + '/' + blogUsrInWpAddr + "/pic"
    if gCfg['otherPicPathInWP'] == '' :
        gCfg['otherPicPathInWP'] = gCfg['picPathInWP'] + '/' + gConst['othersiteDirName']

    logging.debug("Set URL prefix for own   site picture: %s", gCfg['picPathInWP'])
    logging.debug("Set URL prefix for other site picture: %s", gCfg['otherPicPathInWP'])

    return

#------------------------------------------------------------------------------
#translate strToTranslate from fromLanguage to toLanguage
# return the translated utf-8 encoded string
def translateString(strToTranslate, fromLanguage, toLanguage):
    translatedStr = strToTranslate
    transOK = False
    transErr = ''

    # some frequently used language abbrv:
    # Chinese Simplified:   zh-CN
    # Chinese Traditional:  zh-TW
    # English:              en
    # German:               de
    # Japanese:             ja
    # Korean:               ko
    # French:               fr    
    # more can be found at: 
    # http://code.google.com/intl/ru/apis/language/translate/v2/using_rest.html#language-params

    try :
        # following refer: http://python.u85.us/viewnews-335.html
        para = {'hl':'zh-CN', 'ie':'UTF-8', 'text':strToTranslate, 'langpair':"%s|%s"%(fromLanguage, toLanguage)}
        urlGoogleTrans = 'http://translate.google.cn/translate_t'
        encoded_data = urllib.urlencode(para)
        trans_req = urllib2.Request(urlGoogleTrans, encoded_data)
        # note：according to:
        # http://imtx.me/archives/650.html
        # here must use IE6, otherwise will return forbidden 403 error
        trans_req.add_header('User-Agent', "Mozilla/4.0 (compatible;MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)")
        trans_resp = urllib2.urlopen(trans_req)
    except urllib2.URLError,reason :
        transOK = False
        transErr = reason
        logging.warning("  URLError when translate %s, reason=%s", strToTranslate, reason)
    except urllib2.HTTPError,code :
        transOK = False
        transErr = code
        logging.warning("  HTTPError when translate %s, code=%s", strToTranslate, code)
    else :
        logging.debug("Translate request for %s is done", strToTranslate)

        trans_soup = BeautifulSoup(trans_resp)
        #logging.debug("response html for translate %s:\n%s", strToTranslate, trans_soup.prettify())
        resultBoxSpan = trans_soup.find(id='result_box')
        if resultBoxSpan and resultBoxSpan.span and resultBoxSpan.span.string :
            transOK = True
            translatedStr = resultBoxSpan.span.string.encode('utf-8')
            logging.debug("Successfully to extract the translated string [%s] for [%s]", translatedStr, strToTranslate)
        else :
            transOK = False
            logging.warning("For [%s], can not extract translated string from returned result", strToTranslate)

    if transOK :
        return (transOK, translatedStr)
    else :
        return (transOK, transErr)

#------------------------------------------------------------------------------
# translate the string to English char
def transToEn(strToTrans) :
    translatedStr = strToTrans
    transOK = False
    transErr = ''

    if isAsciiString(strToTrans) :
        transOK = True
        translatedStr = strToTrans
    else :
        (transOK, translatedStr) = translateString(strToTrans, "zh-CN", "en")

    return (transOK, translatedStr)

#------------------------------------------------------------------------------
# replace the &#N; (N is digit number, N > 1) to unicode char
# eg: replace "&amp;#39;" with "'" in "Creepin&#39; up on you"
def repUniNumEntToChar(text):
    unicodeP = re.compile('&#[0-9]+;')
    def transToUniChr(match): # translate the matched string to unicode char
        numStr = match.group(0)[2:-1] # remove '&#' and ';'
        num = int(numStr)
        unicodeChar = unichr(num)
        return unicodeChar
    return unicodeP.sub(transToUniChr, text)

#------------------------------------------------------------------------------
# replace the character entity references into slash + u + code point
# eg: &#10084; => \u2764 (10084=0x2764)
# more info refer: http://againinput4.blog.163.com/blog/static/1727994912011112295423982/
def replaceChrEntityToSlashU(text):
    unicodeP = re.compile('&#[0-9]+;')
    def transToSlashU(match): # translate the matched string to slash unicode
        numStr = match.group(0)[2:-1] # remove '&#' and ';'
        num = int(numStr)
        hex04x = "%04x" % num
        slasU = '\\' + 'u' + str(hex04x)
        return slasU
    return unicodeP.sub(transToSlashU, text)

#------------------------------------------------------------------------------
# remove colon in publisherNickname field
# eg:
# s8.publisherNickname="\u5FE7\u5BDE\u0026amp;\u6CA7\u6851\u72FC";s8.publisherUrl=
# s8.publisherNickname="\u5FE7\u5BDE\u0026amp\u6CA7\u6851\u72FC";s8.publisherUrl=
def removeColonInPublisherNickname(text):
    colonP = re.compile(r's([0-9]+)\.publisherNickname="(.*)";s([0-9]+)\.publisherUrl=')
    def removeColon(match): # translate the matched string to slash unicode
        fieldValue = match.group(2)
        noColon = re.compile(';').sub('', fieldValue)
        retStr = 's' + match.group(1) + '.publisherNickname="' + noColon + '";s' + match.group(3) + '.publisherUrl='
        return retStr
    return colonP.sub(removeColon, text)

#------------------------------------------------------------------------------
# convert the string entity to unicode unmber entity
# refer: http://www.htmlhelp.com/reference/html40/entities/latin1.html
def replaceStrEntToNumEnt(text) :
    strToNumEntDict = {
        # Latin-1 Entities
        "&nbsp;"	:   "&#160;",
        "&iexcl;"	:   "&#161;",
        "&cent;"    :   "&#162;",
        "&pound;"	:   "&#163;",
        "&curren;"	:   "&#164;",
        "&yen;"	    :   "&#165;",
        "&brvbar;"	:   "&#166;",
        "&sect;"	:   "&#167;",
        "&uml;"	    :   "&#168;",
        "&copy;"	:   "&#169;",
        "&ordf;"	:   "&#170;",
        "&laquo;"	:   "&#171;",
        "&not;"	    :   "&#172;",
        "&shy;"	    :   "&#173;",
        "&reg;"	    :   "&#174;",
        "&macr;"	:   "&#175;",
        "&deg;"	    :   "&#176;",
        "&plusmn;"	:   "&#177;",
        "&sup2;"	:   "&#178;",
        "&sup3;"	:   "&#179;",
        "&acute;"	:   "&#180;",
        "&micro;"	:   "&#181;",
        "&para;"	:   "&#182;",
        "&middot;"	:   "&#183;",
        "&cedil;"	:   "&#184;",
        "&sup1;"    :   "&#185;",
        "&ordm;"    :   "&#186;",
        "&raquo;"	:   "&#187;",
        "&frac14;"	:   "&#188;",
        "&frac12;"	:   "&#189;",
        "&frac34;"	:   "&#190;",
        "&iquest;"	:   "&#191;",
        "&Agrave;"	:   "&#192;",
        "&Aacute;"	:   "&#193;",
        "&Acirc;"	:   "&#194;",
        "&Atilde;"	:   "&#195;",
        "&Auml;"	:   "&#196;",
        "&Aring;"	:   "&#197;",
        "&AElig;"	:   "&#198;",
        "&Ccedil;"	:   "&#199;",
        "&Egrave;"	:   "&#200;",
        "&Eacute;"	:   "&#201;",
        "&Ecirc;"	:   "&#202;",
        "&Euml;"    :   "&#203;",
        "&Igrave;"	:   "&#204;",
        "&Iacute;"	:   "&#205;",
        "&Icirc;"	:   "&#206;",
        "&Iuml;"    :   "&#207;",
        "&ETH;"	    :   "&#208;",
        "&Ntilde;"	:   "&#209;",
        "&Ograve;"	:   "&#210;",
        "&Oacute;"	:   "&#211;",
        "&Ocirc;"	:   "&#212;",
        "&Otilde;"	:   "&#213;",
        "&Ouml;"	:   "&#214;",
        "&times;"	:   "&#215;",
        "&Oslash;"	:   "&#216;",
        "&Ugrave;"	:   "&#217;",
        "&Uacute;"	:   "&#218;",
        "&Ucirc;"	:   "&#219;",
        "&Uuml;"	:   "&#220;",
        "&Yacute;"	:   "&#221;",
        "&THORN;"	:   "&#222;",
        "&szlig;"	:   "&#223;",
        "&agrave;"	:   "&#224;",
        "&aacute;"	:   "&#225;",
        "&acirc;"	:   "&#226;",
        "&atilde;"	:   "&#227;",
        "&auml;"	:   "&#228;",
        "&aring;"	:   "&#229;",
        "&aelig;"	:   "&#230;",
        "&ccedil;"	:   "&#231;",
        "&egrave;"	:   "&#232;",
        "&eacute;"	:   "&#233;",
        "&ecirc;"	:   "&#234;",
        "&euml;"	:   "&#235;",
        "&igrave;"	:   "&#236;",
        "&iacute;"	:   "&#237;",
        "&icirc;"	:   "&#238;",
        "&iuml;"	:   "&#239;",
        "&eth;"	    :   "&#240;",
        "&ntilde;"	:   "&#241;",
        "&ograve;"	:   "&#242;",
        "&oacute;"	:   "&#243;",
        "&ocirc;"	:   "&#244;",
        "&otilde;"	:   "&#245;",
        "&ouml;" 	:   "&#246;",
        "&divide;"	:   "&#247;",
        "&oslash;"	:   "&#248;",
        "&ugrave;"	:   "&#249;",
        "&uacute;"	:   "&#250;",
        "&ucirc;"	:   "&#251;",
        "&uuml;"	:   "&#252;",
        "&yacute;"	:   "&#253;",
        "&thorn;"	:   "&#254;",
        "&yuml;"	:   "&#255;",
        # http://www.htmlhelp.com/reference/html40/entities/special.html
        # Special Entities
        "&quot;"    : "&#34;",
        "&amp;"     : "&#38;",
        "&lt;"      : "&#60;",
        "&gt;"      : "&#62;",
        "&OElig;"   : "&#338;",
        "&oelig;"   : "&#339;",
        "&Scaron;"  : "&#352;",
        "&scaron;"  : "&#353;",
        "&Yuml;"    : "&#376;",
        "&circ;"    : "&#710;",
        "&tilde;"   : "&#732;",
        "&ensp;"    : "&#8194;",
        "&emsp;"    : "&#8195;",
        "&thinsp;"  : "&#8201;",
        "&zwnj;"    : "&#8204;",
        "&zwj;"     : "&#8205;",
        "&lrm;"     : "&#8206;",
        "&rlm;"     : "&#8207;",
        "&ndash;"   : "&#8211;",
        "&mdash;"   : "&#8212;",
        "&lsquo;"   : "&#8216;",
        "&rsquo;"   : "&#8217;",
        "&sbquo;"   : "&#8218;",
        "&ldquo;"   : "&#8220;",
        "&rdquo;"   : "&#8221;",
        "&bdquo;"   : "&#8222;",
        "&dagger;"  : "&#8224;",
        "&Dagger;"  : "&#8225;",
        "&permil;"  : "&#8240;",
        "&lsaquo;"  : "&#8249;",
        "&rsaquo;"  : "&#8250;",
        "&euro;"    : "&#8364;",
        }

    replacedText = text
    for key in strToNumEntDict.keys() :
        replacedText = re.compile(key).sub(strToNumEntDict[key], replacedText)
    return replacedText

#------------------------------------------------------------------------------
# extract title fom soup
def extractTitle(soup):
    titXmlSafe = ''
    try :
        foundTitle = soup.find(attrs={"class":"tcnt"})
        # foundTitle should not empty
        # foundTitle.string is unicode type here
        titStr = foundTitle.string.strip()
        titNoUnicode = repUniNumEntToChar(titStr)
        titXmlSafe = saxutils.escape(titNoUnicode)
        logging.debug("Extrated title=%s", titXmlSafe)
    except : 
        logging.error("Can not extract blog item title !")
        sys.exit(2)

    return titXmlSafe

#------------------------------------------------------------------------------
# extract datetime fom soup
def extractDatetime(soup) :
    datetimeStr = ''
    try :
        foundDatetime = soup.find(attrs={"class":"blogsep"})
        datetimeStr = foundDatetime.string.strip() #2010-11-15 09:44:12
        logging.debug("Extracted blog publish date:%s", datetimeStr)
    except :
        logging.error("Can not extracted blog item publish date !")
        sys.exit(2)

    return datetimeStr

    
#------------------------------------------------------------------------------
# filter invalid char in content, 
# otherwise will cause wordpress importer import failed
# eg:
# http://againinput4.blog.163.com/blog/static/172799491201110111145259/
# contains some invalid ascii control chars
# http://hi.baidu.com/notebookrelated/blog/item/8bd88e351d449789a71e12c2.html
# 165th comment contains invalid control char: ETX
def removeCtlChr(inputContent) :
    validContent = ''
    for c in inputContent :
        asciiVal = ord(c)
        validChrList = [
            9, # 9=\t=tab
            10, # 10=\n=LF=Line Feed=换行
            13, # 13=\r=CR=回车
        ]
        # filter out others ASCII control character, and DEL=delete
        if (asciiVal == 0x7F) or ((asciiVal < 32) and (asciiVal not in validChrList)) :
            logging.debug("Filtered the ascii control char = %d", asciiVal)
        else : # all other is valid char
            validContent += c

    return validContent

#------------------------------------------------------------------------------
# generate ST music real time address
def genStRtAddr(strUrl, songId):
    reqStRtUrl = ''
    try :
        # Note: here not use urllib.urlencode to encode para, 
        #       for the encoded result will convert some special chars($,:,{,},...) into %XX
        paraDict = {
            'str'   :   '',
            'sid'   :   '',
        }
        paraDict['str'] = str(strUrl)
        paraDict['sid'] = str(songId)
        mainUrl = 'http://www.songtaste.com/time.php'
        reqStRtUrl = genFullUrl(mainUrl, paraDict)
        
        logging.debug("Geneated request ST song real time url=%s",reqStRtUrl)
    except :
        logging.debug("Fail to generate request ST song real time url for songID=%s", songId)
    
    return reqStRtUrl;

#------------------------------------------------------------------------------
# check file validation
def isFileValid(fileUrl) :
    global gConst

    fileIsValid = False
    errReason = ''

    try :
        ret_fileUrl = urllib2.urlopen(fileUrl) # note: Python 2.6 has added timeout support.
        realUrl = ret_fileUrl.geturl()
        print "realUrl=",realUrl
        urlInfo = ret_fileUrl.info()
        print "urlInfo=",urlInfo
        sajkgdhjkghkahk
        contentLen = urlInfo['Content-Length']
        # eg: Content-Type= image/gif
        # more ContentTypes can refer: http://kenya.bokee.com/3200033.html
        contentType = urlInfo['Content-Type']
        fileSuffix = contentType.split("/")[1]
        #if (fileSuffix in gConst['validFileSufList']) and (contentLen > 0) and (realUrl == fileUrl):
        # for redirect, if returned size>0 and suffix is OK, also should be considered valid
        if (fileSuffix in gConst['validFileSufList']) and (contentLen > 0):
            fileIsValid = True
        else :
            fileIsValid = False
            logging.waring("  File %s is invalid, returned info: type=%s, len=%d, realUrl=%s", contentType, contentLen, realUrl)
    except urllib2.URLError,reason :
        fileIsValid = False
        errReason = reason
        logging.warning("  URLError when open %s, reason=%s", fileUrl, reason)
    except urllib2.HTTPError,code :
        fileIsValid = False
        errReason = code
        logging.warning("  HTTPError when open %s, code=%s", fileUrl, code)
    except :
        fileIsValid = False
        logging.warning("  Unknown error when open %s", fileUrl)

    #errReason = str(errReason)
    return (fileIsValid, errReason)

#------------------------------------------------------------------------------
# input: http://www.songtaste.com/song/2407245/
# extract ST song real address
# return the music artist and title
def parseStUrl(stSongUrl) :
    parsedOK = False
    songInfoDict = {
        'id'        : '',
        'title'     : '',
        'artist'    : '',
        'realAddr'  : '',
        'strUrl'    : '',
        'suffix'    : '',
        'playUrl'   : '',
    }
    
    try :
        #page = urllib2.urlopen(stSongUrl)
        #soup = BeautifulSoup(page, fromEncoding="GB18030") # page is GB2312

        # 1. extract artist
        # <h1 class="h1singer">Lucky Sunday</h1>
        #foundSinger = soup.find(attrs={"class":"h1singer"})
        #songInfoDict['artist'] = foundSinger.string
        
        # 2. extrac title
        # <p class="mid_tit">Rap(Ice ice baby)Mix</p>
        #foundTitle = soup.find(attrs={"class":"mid_tit"})
        #songInfoDict['title'] = foundTitle.string

        # 3. extrat real addr
        # /playmusic.php?song_id=2407245
        # http://www.songtaste.com/playmusic.php?song_id=2407245
        songId = stSongUrl.split('/')[4]
        playmusicUrl = "http://www.songtaste.com/playmusic.php?song_id=" + songId
        songInfoDict['playUrl'] = playmusicUrl
        
        # <div class="p_songlist" id="songlist">
        # <UL id=songs>
        # <script>
        # WrtSongLine("2407245", "Rap(Ice ice baby)Mix ", "Lucky Sunday ", "0", "0", "http://224.cachefile34.rayfile.com/227b/zh-cn/download/d18c6b179f388d1bf1f1d30946802c8a/preview.mp3", "cachefile34.rayfile.com/227b/zh-cn/download/d18c6b179f388d1bf1f1d30946802c8a/preview");
        # </script>
        # </UL>
        # </DIV> 
        page = urllib2.urlopen(playmusicUrl)
        soup = BeautifulSoup(page, fromEncoding="GB18030")
        foundSonglist = soup.find(id='songlist')
        #print "foundSonglist=",foundSonglist
        #print "foundSonglist.ul=",foundSonglist.ul
        #print "foundSonglist.ul.script=",foundSonglist.ul.script
        wrtSongStr = foundSonglist.ul.script.string
        #                                      1=id     2=title  3=artist                        4=realAddr  5=strUrl
        wrtSongP = re.compile(r'WrtSongLine\("(\d+)",\s*"(.*?)",\s*"(.*?)",\s*"\d+",\s*"\d+",\s*"(.*?)",\s*"(.*?)"\);')
        # note : for rayfile address, eg:
        # -> http://www.songtaste.com/song/2407245/
        # this kind of method can extract the real address:
        # http://224.cachefile34.rayfile.com/227b/zh-cn/download/d18c6b179f388d1bf1f1d30946802c8a/preview.mp3
        # strUrl = cachefile34.rayfile.com/227b/zh-cn/download/d18c6b179f388d1bf1f1d30946802c8a/preview
        # but for : 
        # -> http://www.songtaste.com/song/2460118/
        # the extracted real address is:
        # http://m4.songtaste.com/201201092047/88601655c1388a9511c805807a6532f0/4/44/44cbec83ad2d1d4817c228cc2f2c402f.mp3
        # strUrl = 5aa9ecd9e8a48a612541c722d0d83296f3a2958a7d26c275c8464541b2e9cc4b3f3cdaa848f4efe42f1ced3fe51ffc51
        # but when click to play it, the real address will change to :
        # http://m4.songtaste.com/201201092045/cb7ca1c407a0992955264bdbd1e12250/4/44/44cbec83ad2d1d4817c228cc2f2c402f.mp3
        # http://m4.songtaste.com/201201092103/09e62bed7108ea2ee6f413a6ab53e5c5/4/44/44cbec83ad2d1d4817c228cc2f2c402f.mp3
        # in which, cb7ca1c407a0992955264bdbd1e12250 and 09e62bed7108ea2ee6f413a6ab53e5c5 is depend on time

        foundWrt = wrtSongP.search(wrtSongStr)
        id          = foundWrt.group(1)
        title       = foundWrt.group(2)
        artist      = foundWrt.group(3)
        realAddr    = foundWrt.group(4)
        strUrl      = foundWrt.group(5)

        # (1) process real address
        rayfilePos = strUrl.find('rayfile')
        if rayfilePos > 0 : # is 'rayfile' kind of addr
            logging.debug("Rayfile type realAddr=%s", realAddr)
        else :
            # is songtaste kind of addr
            # generate the url to request the real time address for this song
            reqStRtAddr = genStRtAddr(strUrl, id)
            # returned real time addr is like this:
            # http://m4.songtaste.com/201201092150/02c112717113b01e8ebeba5d16899fe0/4/44/44cbec83ad2d1d4817c228cc2f2c402f.mp3
            page = urllib2.urlopen(reqStRtAddr)
            # paraDict = {
                # 'str'   :   '',
                # 'sid'   :   '',
            # }
            # paraDict['str'] = str(strUrl)
            # paraDict['sid'] = str(id)
            # mainUrl = 'http://www.songtaste.com/time.php'
            # encodedPara = urllib.urlencode(paraDict)
            # stReq = urllib2.Request(mainUrl, encodedPara)
            # stReq.add_header('User-Agent', "Mozilla/4.0 (compatible;MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)")
            # stReq.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7")
            # stReq.add_header('Connection', "keep-alive")
            # stReq.add_header('Cache-Control', "max-age=0")
            # stReq.add_header('Host', "www.songtaste.com")
            #page = urllib2.urlopen(stReq)
            
            soup = BeautifulSoup(page)
            realAddr = unicode(soup)

            # TODO:
            # here even got real time address, but when use urllib2.urlopen to open it, will got error:
            # URLError when open http://mc.songtaste.com/201201092326/0236b1e2fa71933486a7315b487fd4b7/c/c0/c0eeecf337478a761c25f9ac9943d86d.mp3, reason=HTTP Error 403: Forbidden
            # need to fix this problem
            #isFileValid(realAddr)
            
            logging.debug("Extracted real addess  =%s", foundWrt.group(4))
            logging.debug("Songtaste type realAddr=%s", realAddr)

        # (2) process title
        title  = title.strip().rstrip()
        # (3) process artist
        artist = artist.strip().rstrip()
        # (4) process suffix
        sufPos = realAddr.rfind('.')
        suffix = realAddr[(sufPos + 1) : ]
        
        # 4. set values
        songInfoDict['id']      = id
        songInfoDict['title']   = title
        songInfoDict['artist']  = artist
        songInfoDict['realAddr']= realAddr
        songInfoDict['strUrl']  = strUrl
        songInfoDict['suffix']  = suffix

        parsedOK = True
        
        logging.debug("For ST song url %s, parsed info: id=%s, title=%s, artist=%s, realAddr=%s, strUrl=%s",
            stSongUrl, id, title, artist, realAddr, strUrl)
    except :
        parsedOK = False
        logging.debug("Fail to parse ST url %s", stSongUrl)

    return (parsedOK, songInfoDict)

#------------------------------------------------------------------------------
# create output info file for ST music
def initStInfo() :
    global gVal
    gVal['stInfo']['dirName'] = '.' + '/' + 'songtaste'
    if (os.path.isdir(gVal['stInfo']['dirName']) == False) :
        os.makedirs(gVal['stInfo']['dirName']) # create dir recursively
        logging.info("Create dir %s for save downloaded ST music file", gVal['stInfo']['dirName'])
    gVal['stInfo']['fileName'] = gVal['stInfo']['dirName'] + '/' + 'songtasteMusicInfo' + datetime.now().strftime('_%Y%m%d%H%M') + '.txt'
    infoFile = codecs.open(gVal['stInfo']['fileName'], 'w', 'utf-8')
    if infoFile:
        logging.info('Created file %s for store extracted ST info', gVal['stInfo']['fileName'])
        infoFile.close()
    else:
        logging.warning("Can not create output info file: %s", gVal['stInfo']['fileName'])
    return

#------------------------------------------------------------------------------
# output ST music info
def outputStInfo(info) :
    global gVal
    infoFile = codecs.open(gVal['stInfo']['fileName'], 'a+', 'utf-8')
    infoFile.write(info + '\n')
    infoFile.close()
    return

#------------------------------------------------------------------------------
# extract ST music url 
# download music 
def downloadStMusic(blogContent) :
    global gval
    if gCfg['needProcessSt'] == 'yes' :
        # <a href="http://www.songtaste.com/song/2407245/" target="_blank">
        # [夜店魅音Mix]ICE ICE BABY 炫音超棒Rap风[精神节拍]≈
        # </a>

        # 1. extarct the ST song urls
        stUrlP = r"http://www\.songtaste\.com/song/\d+/"
        stUrlP = re.compile(stUrlP)
        stUrlList = stUrlP.findall(blogContent)
        if stUrlList :
            uniUrlList = uniqueList(stUrlList)
            (filteredList, existedList) = filterList(uniUrlList, gVal['processedStUrlList'])
            if filteredList :
                logging.debug("Found ST song urls to process:")
                for stUrl in filteredList : logging.debug("%s", stUrl)

                for stUrl in filteredList :
                    # no matter following process is OK or not, all means processed
                    gVal['processedStUrlList'].append(stUrl)
                
                    # 2. extract the real song addr for this song url
                    (parsedOK, songInfoDict) = parseStUrl(stUrl)
                    if parsedOK :
                        # 3. download this song
                        # (1) generated the name
                        fullName = songInfoDict['title'] + ' - ' + songInfoDict['artist']
                        fullName += '.' + songInfoDict['suffix']

                        # (2) download and save it
                        dstName = gVal['stInfo']['dirName'] + '/' + fullName # here '/' is also valid in windows dir path
                        downloadFile(songInfoDict['realAddr'], dstName, False)
                        
                        # (3) output related info
                        # generated quoted name to facilicate later input music url in wordpress
                        fullNameGb18030 = fullName.encode("GB18030")
                        quotedName = urllib.quote(fullNameGb18030)
                        outputStInfo("%s ST Song Info %s" % ('-'*30, '-'*30))
                        outputStInfo("Song    URL: %s" % stUrl)
                        outputStInfo("Song     ID: %s" % songInfoDict['id'])
                        outputStInfo("Playe   URL: %s" % songInfoDict['playUrl'])
                        outputStInfo("Title      : %s" % songInfoDict['title'])
                        outputStInfo("Artist     : %s" % songInfoDict['artist'])
                        outputStInfo("Saved  Name: %s" % fullName)
                        outputStInfo("Quoted Name: %s" % quotedName)
                        outputStInfo("RealAddress: %s" % songInfoDict['realAddr'])
                        outputStInfo("strUrl     : %s" % songInfoDict['strUrl'])
    return

#------------------------------------------------------------------------------
# post process blog content:
# 1. download pic and replace pic url
# 2. remove invalid ascii control char
# 3. doanload Songtaste music
def postProcessContent(blogContent) :
    processedContent = ''
    try :
        # 1. extract pic url, download pic, replace pic url
        afterProcessPic = processPhotos(blogContent)
        
        # 2. remove invalid ascii control char
        afterFilter = removeCtlChr(afterProcessPic)
        
        # 3. download ST music if necessary
        downloadStMusic(afterFilter)
        
        processedContent = afterFilter
    except :
        logging.debug("Fail while post process for blog content")

    return processedContent

#------------------------------------------------------------------------------
# extract blog item content fom soup
def extractContent(soup) :
    contentStr = ''
    try :
        foundContent = soup.find(attrs={"class":"bct fc05 fc11 nbw-blog ztag"})

        # note: 
        # here must use BeautifulSoup-3.0.6.py
        # for CData in BeautifulSoup-3.0.4.py has bug :
        # process some kind of string will fail when use CData
        # eg: http://benbenwo1091.blog.163.com/blog/static/26634402200842202442518/
        # CData for foundContent.contents[11] will fail
        mappedContents = map(CData, foundContent.contents)
        joinedStr = ''.join(mappedContents)
        contentStr = packageCDATA(joinedStr)
        logging.debug("-----------Extract blog content successfully-------");
        #logging.debug("%s", contentStr);
        #logging.debug("---------------------------------------------------");

        # do some post process for blog content
        contentStr = postProcessContent(contentStr)
    except :
        logging.error("Can not extract blog item content !")
        sys.exit(2)

    return contentStr

#------------------------------------------------------------------------------
# extract category from soup
def extractCategory(soup) :
    global gVal

    catXmlSafe = ''
    try :
        foundCat = soup.find(attrs={"class":"fc03 m2a"})
        catStr = foundCat.string.strip()
        catNoUnicode = repUniNumEntToChar(catStr)
        catXmlSafe = saxutils.escape(catNoUnicode)
        gVal['catNiceDict'][catXmlSafe] = ''

        logging.debug("Extraced catalog: %s", catXmlSafe)
    except :
        logging.debug("No catalog avaliable")

    return catXmlSafe

#------------------------------------------------------------------------------
# extract tags info from soup
def extractTags(soup) :
    tagList = []

    try :
        # extract tags from following string:
        # blogTag:'wordpress,importer,无法识别作者,author',

        # blogUrl:'blog/static/1727994912012040341700',
        nbInit = soup.find(attrs={"class":"phide nb-init"})
        nbInitUni = unicode(nbInit)
        #nbInitStr = str(nbInit)
        blogTagP = re.compile(r"blogTag:'(.*)',\s+blogUrl:'")
        searched = blogTagP.search(nbInitUni)
        #searched = blogTagP.search(nbInitStr)
        tags = searched.group(1)
        tagList = tags.split(',')
        # note: here for list, [u''] is not empty, only [] is empty
        tagList = removeEmptyInList(tagList)
        logging.debug("Extracted tags: %s", tagList)
    except :
        logging.debug("Fail to extract tag info for current blog item !")

    return tagList

#------------------------------------------------------------------------------
# find next permanent link from soup
def findNextPermaLink(soup, curUrl) :
    (nextLinkStr, nextLinkTitleStr) = ('', '')
    try :
        foundNextLink = soup.find(attrs={"class":"pright thide"})
        nextLinkStr = foundNextLink.a['href']
        nextLinkTitleStr = foundNextLink.a.string.strip()
        logging.debug("Found next permanent link %s, title=%s", nextLinkStr, nextLinkTitleStr)
    except :
        logging.debug("Can not find next permanent link for %s", curUrl)

    return (nextLinkStr, nextLinkTitleStr)

#------------------------------------------------------------------------------
# find prev permanent link from soup
def findPrevPermaLink(soup, curUrl) :
    prevLinkStr = ''
    try :
        foundPrevLink = soup.find(attrs={"class":"pleft thide"})
        prevLinkStr = foundPrevLink.a['href']
        prevLinkTitleStr = foundPrevLink.a.string.strip()
        logging.debug("Found previous permanent link %s, title=%s", prevLinkStr, prevLinkTitleStr)
    except :
        logging.debug("Can not find previous permanent link for %s", curUrl)

    return prevLinkStr

#------------------------------------------------------------------------------
#1. open current blog item
#2. save related info into blog entry
#3. return link of next blog item
def fetchEntry(url):
    global gVal
    global gConst
    global gCfg

    #update post id
    gVal['postID'] += 1

    logging.debug("----------------------------------------------------------")
    #logging.info("Processing postID[%04d] blog item: %s", gVal['postID'], url)
    logging.info("[%04d] %s", gVal['postID'], url)

    calcTimeStart("fetch_page")
    for tries in range(gCfg['funcTotalExecNum']) :
        try :
            req = urllib2.Request(url)
            req.add_header('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.5) Gecko/20070713 Firefox/2.0.0.5')
            page = urllib2.build_opener().open(req).read()
            gVal['statInfoDict']['fetchPageTime'] += calcTimeEnd("fetch_page")
            logging.debug("Successfully downloaded: %s", url)
            break # successfully, so break now
        except :
            if tries < (gCfg['funcTotalExecNum'] - 1) :
                logging.warning("Fetch page %s fail, do %d retry", url, (tries + 1))
                continue
            else : # last try also failed, so exit
                logging.error("Has tried %d times to fetch page: %s, all failed!", gCfg['funcTotalExecNum'], url)
                sys.exit(2)

    # Note: after BeautifulSoup process, output html content already is utf-8 encoded
    #soup = BeautifulSoup(page)
    # Note:
    # 163 blog all use charset=gbk, but some special blog item:
    # http://chaganhu99.blog.163.com/blog/static/565262662007112245628605/
    # will messy code if use default gbk to decode it, so set GB18030 here to avoid messy code
    soup = BeautifulSoup(page, fromEncoding="GB18030")
    #logging.debug("Got whole page content\n---------------\n%s",soup.prettify())
    #logging.debug("---------------\n")
    entryDict = {
        'postid'        : 0,
        'nextLink'      : '',
        'nextLinkTitle' : '',
        'title'         : '',
        'content'       : '',
        'datetime'      : '',
        'category'      : '',
        'tags'          : [],
        'comments'      : [],
        }

    entryDict['postid'] = gVal['postID']

    # title
    entryDict['title'] =  extractTitle(soup)
    logging.info("  Title = %s", entryDict['title'])

    # datetime
    entryDict['datetime'] = extractDatetime(soup)

    # content
    entryDict['content'] = extractContent(soup)

    # category
    entryDict['category'] = extractCategory(soup)
    
    # tags
    entryDict['tags'] = extractTags(soup)
    # add into global tagSlugDict
    for tag in entryDict['tags'] :
        gVal['tagSlugDict'][tag] = ''

    # extrat next (previously published) blog item link
    (entryDict['nextLink'], entryDict['nextLinkTitle']) = findNextPermaLink(soup, url)

    # fetch comments
    if gCfg['processCmt'] == 'yes' :
        calcTimeStart("process_comment")
        try :        
            #extract comments if exist
            cmtRespDictList = fetchComments(url, soup)
            # got valid comments, now proess it
            for cmtDict in cmtRespDictList :
                comment = {}
                #fill all comment field
                comment = fillComments(comment, cmtDict)
                entryDict['comments'].append(comment)

            logging.debug('Total extracted comments for this blog item = %d', len(entryDict['comments']))
        except :
            logging.warning("Fail to process comments for %s", url)

        gVal['statInfoDict']['processCmtTime'] += calcTimeEnd("process_comment")

    return entryDict

#------------------------------------------------------------------------------
# extract the 'permaSerial' filed from the single response blog string
def extractPermaSerial(singleBlogStr):
    permaSerial = ''
    foundPerma = re.compile(r's[0-9]{1,10}\.permaSerial="([0-9]{1,100})";').search(singleBlogStr);
    permaSerial = foundPerma.group(1)
    logging.debug("Extracted permaSerial=%s", permaSerial)
    return permaSerial

#------------------------------------------------------------------------------
# find the real end of previous link == earliest permanent link
# Why do this:
# for some blog, if stiky some blog, which is earliest than the lastFoundPermaSerial
# then should check whether it has more previuous link or not
# if has, then find the end of previous link
# eg: http://cqyoume.blog.163.com/blog
def findRealFirstPermaLink(permaSerial) :
    endOfPrevLink = ''
    try :
        curLink = gVal['seflBlogMainUrl'] + "/blog/static/" + permaSerial
        logging.debug("Start find real first permanent link from %s", curLink)

        lastLink = curLink
        while curLink :
            # save before
            lastLink = curLink
            # open it
            page = urllib2.urlopen(curLink)
            soup = BeautifulSoup(page)
            # find previous link util the end
            curLink = findPrevPermaLink(soup, curLink)
        endOfPrevLink = lastLink
        logging.debug("Found the earliest link %s", endOfPrevLink)
    except:
        logging.debug("Can not find the earliest link for %s", permaSerial)

    return endOfPrevLink

#------------------------------------------------------------------------------
# find the first permanent link = url of the earliset published blog item
# Note: make sure the gVal['blogUser'] is valid before call this func
def find1stPermalink(srcURL):
    global gVal

    firstPermaLink = ''
    try :
        # 1. generate and open main blog url
        calcTimeStart("find_first_perma_link")
        logging.info("Begin to find the first permanent link from %s", gVal['seflBlogMainUrl'])
        logging.debug("Begin to open %s", gVal['seflBlogMainUrl'])
        page = urllib2.urlopen(gVal['seflBlogMainUrl'])
        soup = BeautifulSoup(page)
        #logging.debug("----prettified html page for: %s ----\n%s", gVal['seflBlogMainUrl'], soup.prettify())

        # 2. init
        
        # extract userId
        #UD.host = {
        #  userId:39515918
        # ,userName:'zhuchao-2006'
        # ,...........
        # };
        pageStr = str(soup)
        udHost = re.compile(r"UD\.host\s*=\s*\{\s*userId:([0-9]{1,20})\s*,").search(pageStr)
        userId = udHost.group(1)
        logging.debug("Extracted blog useId=%s", userId)

        # 3. get blogs and parse it
        needGetMoreBlogs = True
        lastFoundPermaSerial = ''
        startBlogIdx = 0
        onceGetNum = 400 # note: for get 163 blogs, one time request more than 500 will fail

        while needGetMoreBlogs :
            logging.debug("Start to get blogs: startBlogIdx=%d, onceGetNum=%d", startBlogIdx, onceGetNum)
            getBlogUrl = genGetBlogsUrl(userId, startBlogIdx, onceGetNum)
            # get blogs
            retBlogsReq = urllib2.Request(getBlogUrl)
            blogsResp = urllib2.build_opener().open(retBlogsReq).read()
            #logging.debug("---- getBlogs response startIdx=%d getNum=%d----\n%s", startBlogIdx, onceGetNum, blogsResp)

            # parse it
            lines = blogsResp.split("\r\n")
            noBlankLines = removeEmptyInList(lines)
            # remove the 0,1,-1 line
            noBlankLines.pop(0) # //#DWR-INSERT
            noBlankLines.pop(0) # //#DWR-REPLY
            # eg: dwr.engine._remoteHandleCallback('1','0',[s0,s1]);
            dwrEngine = noBlankLines.pop(len(noBlankLines) - 1)
            mainBlogsNum = extratMainCmtNum(dwrEngine)

            if (mainBlogsNum > 0)  and noBlankLines :
                # if not once get max num, 
                # then last line of the response is not contain permaSerial, like this:
                # s32[0]=8412120;s32[1]=8596165;............;s32[8]=8223049;
                while noBlankLines :
                    curLastBlogStr = noBlankLines.pop(-1)
                    if re.compile(r'\.permaSerial').search(curLastBlogStr) :
                        # only contain '.permaSerial', then goto extract it
                        lastFoundPermaSerial = extractPermaSerial(curLastBlogStr)
                        break # exit while
                
                if mainBlogsNum < onceGetNum :
                    needGetMoreBlogs = False
                    logging.debug("Has got all blogs")
                else :
                    needGetMoreBlogs = True
                    startBlogIdx += onceGetNum
            else :
                needGetMoreBlogs = False
        # out of while loop, set value
        if lastFoundPermaSerial :
            firstPermaLink = findRealFirstPermaLink(lastFoundPermaSerial)
            logging.info("Found first permanent link: %s", firstPermaLink)
        gVal['statInfoDict']['find1stLinkTime'] = calcTimeEnd("find_first_perma_link")
    except :
        logging.error("Can not find the first permanent link for %s", srcURL)
    
    return firstPermaLink

#------------------------------------------------------------------------------
# remove invalid character in url(blog's post name and category's nice name)
def removeInvalidCharInUrl(inputString):
    filterd_str = ''
    charNumerP = re.compile(r"[\w|-]")
    for c in inputString :
        if c == ' ' :
            # replace blanksplace with '_'
            filterd_str += '_'
        elif charNumerP.match(c) :
            # retain this char if is a-z,A-Z,0-9,_
            filterd_str += c
    return filterd_str

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
    dic['authorDisplayName'] = packageCDATA("")
    dic['authorFirstName'] = packageCDATA("")
    dic['authorLastName'] = packageCDATA("")
    dic['blogTitle'] = saxutils.escape(dic['blogTitle'])
    dic['blogDiscription'] = saxutils.escape(dic['blogDiscription'])
    dic['generator'] = gConst['generator']
    headerStr = wxrT.substitute(dic)

    catStr = ''
    catTermID = 1
    for cat in gVal['catNiceDict'].keys():
        catStr += catT.substitute(
            catTermId = catTermID,
            catName = packageCDATA(cat),
            catNicename = gVal['catNiceDict'][cat],
            catDesc = packageCDATA(""),)
        catTermID += 1

    #compose tags string
    tagsStr = ''
    tagTermID = catTermID
    for tag in gVal['tagSlugDict'].keys():
        if tag :
            tagsStr += tagT.substitute(
                tagNum = tagTermID,
                tagSlug = gVal['tagSlugDict'][tag],
                tagName = packageCDATA(tag),)
            tagTermID += 1

    generatorStr = generatorT.substitute(generator = gConst['generator'])

    f = openExportFile()
    gVal['fullHeadInfo'] = headerStr + catStr + tagsStr + generatorStr
    f.write(gVal['fullHeadInfo'])
    f.flush()
    f.close()
    return

#------------------------------------------------------------------------------
# parse datetime  string into local and gmt time
# possible date format:
# (1) 2011-12-26 08:46:03
def parseEntryDatetime(entry) :
    datestr = entry['datetime']

    parsedLocalTime = datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S') # here is GMT+8 local time
    gmt0Time = localToGmt0(parsedLocalTime)
    
    entry['pubDate'] = gmt0Time.strftime('%a, %d %b %Y %H:%M:%S +0000')
    entry['postDate'] = parsedLocalTime.strftime('%Y-%m-%d %H:%M:%S')
    entry['postDateGMT'] = gmt0Time.strftime('%Y-%m-%d %H:%M:%S')
    return

#------------------------------------------------------------------------------
# export each entry info, then add foot info
# if exceed max size, then split it
def exportEntry(entry, user):
    global gVal
    global gCfg

    itemT = Template("""
    <item>
        <title>${entryTitle}</title>
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
        <wp:status>publish</wp:status>
        <wp:post_parent>0</wp:post_parent>
        <wp:menu_order>0</wp:menu_order>
        <wp:post_type>post</wp:post_type>
        <wp:post_password></wp:post_password>
        <wp:is_sticky>0</wp:is_sticky>
		<category domain="category" nicename="${category_nicename}">${category}</category>
        ${tags}
        ${comments}
    </item>
""") #need entryTitle, entryURL, entryAuthor, category, entryContent, entryExcerpt, postId, postDate, entryPostName

    tagsT = Template("""
        <category domain="post_tag" nicename="${tagSlug}">${tagName}</category>""") # tagSlug, tagName

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
""") #need commentId, commentAuthor, commentEmail,commentURL, commentDate
     # commentDateGMT, commentContent, commentAuthorIP, commentParent

    #compose tags string
    tagsStr = ''
    for tag in entry['tags']:
        if tag:
            tagsStr += tagsT.substitute(
                tagSlug = gVal['tagSlugDict'][tag],
                tagName = packageCDATA(tag),)

    #compose comment string
    commentsStr = ""
    logging.debug("Now will export comments = %d", len(entry['comments']))
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
                            commentParent = comment['parent'],)

    #parse and set time
    parseEntryDatetime(entry)

    itemStr = itemT.substitute(
        entryTitle = entry['title'],
        entryURL = gCfg['postidPreAddr'] + str(entry['postid']),
        entryAuthor = user,
        category = packageCDATA(entry['category']),
        category_nicename = gVal['catNiceDict'][entry['category']],
        entryContent = entry['content'],
        entryExcerpt = packageCDATA(""),
        postId = entry['postid'],
        postDate = entry['postDate'],
        postDateGMT = entry['postDateGMT'],
        pubDate = entry['pubDate'],
        entryPostName = entry['titlePostname'],
        tags = tagsStr,
        comments = commentsStr,
        )

    # output item info to file
    curFileSize = os.path.getsize(gVal['exportFileName'])
    itemStrUft8 = itemStr.encode("utf-8")
    newFileSize = curFileSize + len(itemStrUft8)
    #logging.debug("itemPostId[%04d]: unicode str size = %d, utf-8 str size=%d", entry['postid'], len(itemStr), len(itemStrUft8))
    
    if gCfg['maxXmlSize'] and (newFileSize > gCfg['maxXmlSize']) : # exceed limit size, 0 means no limit
        # 1. output tail info
        curFile = openExportFile()
        curFile.write(gConst['tailInfo'])

        # 2. close old file
        curFile.flush()
        curFile.close()
        #logging.debug("Stored %s size = %d", gVal['exportFileName'], os.path.getsize(gVal['exportFileName']))

        # 3. generate new name
        # old: XXX_20111218_2213-0.xml
        # new: XXX_20111218_2213-1.xml
        oldIdx = int(gVal['exportFileName'][-5])
        newIdx = oldIdx + 1
        newFileName = gVal['exportFileName'][:-5] + str(newIdx) + ".xml"

        # 4. update global export file name
        gVal['exportFileName'] = newFileName

        # 5. create new file
        newFile = codecs.open(gVal['exportFileName'], 'w', 'utf-8')
        if newFile:
            logging.info('Newly created export XML file: %s', gVal['exportFileName'])
        else:
            logging.error("Can not create new export file: %s",gVal['exportFileName'])
            sys.exit(2)

        # 6. export head info
        newFile.write(gVal['fullHeadInfo'])
        
        # 7. export current item info
        newFile.write(itemStr)
        newFile.flush()
        newFile.close()
    else : # not exceed limit size
        curFile = openExportFile()
        curFile.write(itemStr)
        curFile.flush()
        curFile.close()

    logging.debug("Export blog item '%s' done", entry['title'])
    return

#------------------------------------------------------------------------------
def exportFoot():
    f = openExportFile()
    f.write(gConst['tailInfo'])
    f.close()
    return

#------------------------------------------------------------------------------
# process blog header related info
def processBlogHeadInfo(blogInfoDic, user) :
    global gConst
    global gVal

    blogInfoDic['blogURL'] = gVal['seflBlogMainUrl']
    url = blogInfoDic['blogURL']
    logging.info('Blog URL: %s', url)
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    #logging.debug("Prettified url: %s\n---------------\n%s\n", url, soup.prettify())

    titleAndDesc = soup.findAll(attrs={"class":"ztag pre"})
    blogInfoDic['blogTitle'] = titleAndDesc[0].string
    logging.debug('Blog title: %s', blogInfoDic['blogTitle'])
    blogInfoDic['blogDiscription'] = titleAndDesc[1].string
    logging.debug('Blog description: %s', blogInfoDic['blogDiscription'])
    # if none, set to a string, avoid fail while latter processing them
    if not blogInfoDic['blogTitle'] :
        blogInfoDic['blogTitle'] = 'NoBlogTitle'
    if not blogInfoDic['blogDiscription'] :
        blogInfoDic['blogDiscription'] = 'NoBlogDescription'
    blogInfoDic['nowTime'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    blogInfoDic['blogUser'] = user
    blogInfoDic['blogPubDate'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    return

#------------------------------------------------------------------------------
#init for calculate elapsed time 
def calcTimeStart(uniqueKey) :
    global gVal

    gVal['calTimeKeyDict'][uniqueKey] = time.time()
    return

#------------------------------------------------------------------------------
# to get elapsed time, before call this, should use calcTimeStart to init
def calcTimeEnd(uniqueKey) :
    global gVal

    return time.time() - gVal['calTimeKeyDict'][uniqueKey]

#------------------------------------------------------------------------------
# output statistic info
def outputStatisticInfo() :
    totalTime = int(gVal['statInfoDict']['totalTime'])
    if gCfg['doTrans'] == 'yes' :
        transNameTime = int(gVal['statInfoDict']['transNameTime'])
    find1stLinkTime = int(gVal['statInfoDict']['find1stLinkTime'])
    fetchItemsTime = int(gVal['statInfoDict']['fetchItemsTime'])
    fetchPageTime = int(gVal['statInfoDict']['fetchPageTime'])
    exportHeadTime = int(gVal['statInfoDict']['exportHeadTime'])
    exportItemsTime = int(gVal['statInfoDict']['exportItemsTime'])
    exportFootTime = int(gVal['statInfoDict']['exportFootTime'])
    if gCfg['processPic'] == 'yes' :
        processPicTime = int(gVal['statInfoDict']['processPicTime'])
    if gCfg['processCmt'] == 'yes' :
        processCmtTime = int(gVal['statInfoDict']['processCmtTime'])
    
    # output output statistic info
    printDelimiterLine()
    logging.info("Total Processed [%04d] items, averagely each consume seconds=%.4f", gVal['statInfoDict']['exportedItemIdx'], gVal['statInfoDict']['itemAverageTime'])
    logging.info("Total Consume Time: %02d:%02d:%02d", totalTime / 3600, (totalTime % 3600)/60, totalTime % 60)
    logging.info("  Find 1stLink: %02d:%02d:%02d", find1stLinkTime/3600, (find1stLinkTime%3600)/60, find1stLinkTime%60)
    logging.info("  Fetch  Items: %02d:%02d:%02d", fetchItemsTime/3600, (fetchItemsTime%3600)/60, fetchItemsTime%60)
    logging.info("      Fetch   Pages     : %02d:%02d:%02d", fetchPageTime/3600, (fetchPageTime%3600)/60, fetchPageTime%60)
    if gCfg['processPic'] == 'yes' :
        logging.info("      Process Pictures  : %02d:%02d:%02d", processPicTime/3600, (processPicTime%3600)/60, processPicTime%60)
    if gCfg['processCmt'] == 'yes' :
        logging.info("      Process Comments  : %02d:%02d:%02d", processCmtTime/3600, (processCmtTime%3600)/60, processCmtTime%60)
    if gCfg['doTrans'] == 'yes' :
        logging.info("      Translate Name    : %02d:%02d:%02d", transNameTime/3600, (transNameTime%3600)/60, transNameTime%60)
    logging.info("  Export Head : %02d:%02d:%02d", exportHeadTime/3600, (exportHeadTime%3600)/60, exportHeadTime%60)
    logging.info("  Export Items: %02d:%02d:%02d", exportItemsTime/3600, (exportItemsTime%3600)/60, exportItemsTime%60)
    logging.info("  Export Foot : %02d:%02d:%02d", exportFootTime/3600, (exportFootTime%3600)/60, exportFootTime%60)

    return

#------------------------------------------------------------------------------
# generate the post name for original name
# post name = [translate and ] quote it
# note: input name should be unicode type
def generatePostName(unicodeName) :
    quotedName = ''

    if unicodeName :
        nameUtf8 = unicodeName.encode("utf-8")
        if gCfg['doTrans'] == 'yes' :
            calcTimeStart("translate_name")
            (transOK, translatedName) = transToEn(nameUtf8)
            gVal['statInfoDict']['transNameTime'] += calcTimeEnd("translate_name")
            if transOK :
                translatedName = removeInvalidCharInUrl(translatedName)
                quotedName = urllib.quote(translatedName)
            else :
                quotedName = urllib.quote(nameUtf8)
                logging.warning("Translate fail for [%s], roolback to use just quoted string [%s]", nameUtf8, quotedName)
        else :
            #nameUtf8 = removeInvalidCharInUrl(nameUtf8)
            quotedName = urllib.quote(nameUtf8)

    return quotedName

#------------------------------------------------------------------------------
# genrate the tag slug for tags, and add into global dict
# note: input tags should be unicode type
def genTagSlug(tags) :
    for tag in tags :
        if tag :
            tagSlug = generatePostName(tag)
            gVal['tagSlugDict'][tag] = tagSlug
    return 

#------------------------------------------------------------------------------
# generate the suffix char list according to constont picSufList
def genSufList() :
    global gConst
    
    sufChrList = []
    for suffix in gConst['validPicSufList'] :
        for c in suffix :
            sufChrList.append(c)
    sufChrList = uniqueList(sufChrList)
    sufChrList.sort()
    joinedSuf = ''.join(sufChrList)

    swapedSuf = []
    swapedSuf = joinedSuf.swapcase()

    wholeSuf = joinedSuf + swapedSuf

    return wholeSuf

#------------------------------------------------------------------------------
def main():
    global gVal
    global gCfg

    # 0. main procedure begin
    parser = OptionParser()
    parser.add_option("-s","--source",action="store", type="string",dest="srcURL",help="source 163 blog address, such as: http://againinput4.blog.163.com")
    parser.add_option("-f","--startfrom",action="store", type="string",dest="startfromURL",help="a permalink in source 163 blog address for starting with.It should be the earliest blog item link. if this is specified, srcURL will be ignored.")
    parser.add_option("-l","--limit",action="store",type="int",dest="limit",help="limit number of transfered posts, you can use this option to test")
    parser.add_option("-c","--processCmt",action="store",type="string",dest="processCmt",default="yes",help="'yes' or 'no'. Process blog cmments or not. Set to 'no' if you not need export comments of blog items.")
    parser.add_option("-u","--userName",action="store",type="string",default='crifan',dest="user",help="Blog author")
    parser.add_option("-i","--firstPostId",action="store",type="int",default=0,dest="firstPostId",help="the start blog post id number. when you have ")
    parser.add_option("-p","--processPic",action="store",type="string",default="yes",dest="processPic",help="Process picture or not: 'yes' or 'no'. Default is 'yes' to download & replace url. The downloaded pictures can be found in a newly created dir under current dir. Note, after import the generated xml file into wordpress, before make pictures (link) in your blog can shows normally, You should mannualy copy these downloaded picture into WORDPRESS_ROOT_PATH\wp-content\uploads\YOUR_BLOG_USER\pic\ while keep the picture's name unchanged. Set to 'no' if you do not need process picture for your blog.")
    parser.add_option("-w","--wpPicPath",action="store",type="string",dest="wpPicPath",help="the path in wordpress, where you want to copy the downloaded pictures into. If you not set this parameter, default will set to http://localhost/wordpress/wp-content/uploads/YOUR_BLOG_USER/pic. Note: This option only valid when processPic='yes'.")
    parser.add_option("-o","--processOtherPic",action="store",type="string",default="yes",dest="processOtherPic",help="for other site picture url, download these pictures and replace them with address with wpOtherPicPath + a New Name. Note: This option only valid when processPic='yes'.")
    parser.add_option("-r","--wpOtherPicPath",action="store",type="string",dest="wpOtherPicPath",help="the path in wordpress, where you want to copy the downloaded other site pictures into. If you not set this parameter, default will set to ${wpPicPath}/other_site. Note: This option only valid when processOtherPic='yes'.")
    parser.add_option("-e","--omitSimErrUrl",action="store",type="string",default="yes",dest="omitSimErrUrl",help="'yes' or 'no'. For download pictures, if current pic url is similar with previously processed one, which is occur HTTP Error, then omit process this pic url. Note: This option only valid when processPic='yes'.")
    parser.add_option("-t","--translateZh2En",action="store",type="string",default="yes",dest="translateZh2En",help="'yes' or 'no' to do translate. For url SEO and more readable, translate chinese words into english for the blog title's post name, category nice name, and tag slug name.")
    parser.add_option("-a","--postidPrefixAddr",action="store",type="string",default="http://localhost/?p=",dest="postidPrefixAddr",help="the prefix address for postid. default is: 'http://localhost/?p='")
    parser.add_option("-x","--maxXmlSize",action="store",type="int",default=2*1024*1024,dest="maxXmlSize",help="Designate the max size in Bytes of output xml file. Default is 2MB=2*1024*1024=2097152. 0 means no limit.")
    parser.add_option("-y","--maxFailRetryNum",action="store",type="int",default=3,dest="maxFailRetryNum",help="Max number of retry when fail for fetch page/.... Default is 3. Change it as you want. Set to 0 is disable this retry function.")
    parser.add_option("-g","--needProcessSt",action="store",type="string",default="no",dest="needProcessSt",help="Need to process songtaste music or not. Default to 'no'.")

    (options, args) = parser.parse_args()
    # 1. export all options variables
    for i in dir(options):
        exec(i + " = options." + i)

    # 2. init some settings
    gCfg['processPic'] = processPic
    if gCfg['processPic'] == 'yes' :
        gVal['picSufStr'] = genSufList()
        gCfg['omitSimErrUrl'] = omitSimErrUrl
        if wpPicPath :
            # remove last slash if user input url if including
            if (wpPicPath[-1] == '/') : wpPicPath = wpPicPath[:-1]
            gCfg['picPathInWP'] = wpPicPath
        gCfg['processOtherPic'] = processOtherPic
        if gCfg['processOtherPic'] and wpOtherPicPath :
            # remove last slash if user input url if including
            if (wpOtherPicPath[-1] == '/') : wpOtherPicPath = wpOtherPicPath[:-1]
            gCfg['otherPicPathInWP'] = wpOtherPicPath

    gCfg['doTrans'] = translateZh2En
    gCfg['processCmt'] = processCmt
    gCfg['postidPreAddr'] = postidPrefixAddr
    gCfg['maxXmlSize'] = maxXmlSize
    gCfg['funcTotalExecNum'] = maxFailRetryNum + 1

    gCfg['needProcessSt'] = needProcessSt
    if gCfg['needProcessSt'] == 'yes' :
        initStInfo()

    # init some global values
    gVal['postID'] = firstPostId
    # prepare for statistic
    gVal['statInfoDict']['exportedItemIdx'] = 0
    gVal['statInfoDict']['transNameTime']   = 0.0
    gVal['statInfoDict']['processPicTime']  = 0.0
    gVal['statInfoDict']['processCmtTime']  = 0.0
    gVal['statInfoDict']['fetchPageTime']   = 0.0
    gVal['statInfoDict']['find1stLinkTime'] = 0.0

    logging.info("Version: %s", __VERSION__)
    logging.info("1.If find bug, please send the log file and screen output info to green-waste(at)163.com")
    logging.info("2.If you don't know how to use this script, please give '-h' parameter to get more help info")
    printDelimiterLine()

    calcTimeStart("total")

    # 3. connect src blog and find first permal link
    if startfromURL :
        permalink = startfromURL
        logging.info("Entry URL: %s", startfromURL)
        #extract blog user name to gVal['blogUser']
        extractBlogUser(startfromURL)
    elif srcURL:
        logging.info("Source URL: %s", srcURL)
        #extract blog user name to gVal['blogUser']
        extractBlogUser(srcURL)
        permalink = find1stPermalink(srcURL)
        if (not permalink) :
            logging.error("can not find the first link for %s ", srcURL)
            sys.exit(2)
    else:
        logging.error("must designate the entry URL for the first blog item !")
        sys.exit(2)
    
    # 4. main loop, retrieve every blog entry/item related info
    count = 0
    cacheFile = open('entries.cache','w')

    calcTimeStart("fetch_item")
    try:
        while permalink:
            i = fetchEntry(permalink)

            # do translate here -> avoid in the end, 
            # too many translate request to google will cause "HTTPError: HTTP Error 502: Bad Gateway"
            if i['title'] :
                i['titlePostname'] = generatePostName(i['title'])
            if i['category'] :
                gVal['catNiceDict'][i['category']] = generatePostName(i['category'])
            genTagSlug(i['tags'])

            gVal['entries'].append(i)
            pickle.dump(i, cacheFile)
            if 'nextLink' in i :
                permalink = i['nextLink']
            else :
                break
            count += 1
            if (limit and (count >= limit)) : break
    finally:
        cacheFile.close()
    gVal['statInfoDict']['fetchItemsTime'] = calcTimeEnd("fetch_item")

    # 5. output extracted info to XML file
    createOutputFile()

    #get blog header info
    blogInfoDic = {}
    processBlogHeadInfo(blogInfoDic, user)

    # export blog header info
    logging.info('Exporting head info to file ...')
    calcTimeStart("export_head")
    exportHead(blogInfoDic)
    gVal['statInfoDict']['exportHeadTime'] = calcTimeEnd("export_head")

    # export entries
    logging.info('Exporting blog items info to file ...')
    calcTimeStart("export_items")
    for entry in gVal['entries']:
        gVal['statInfoDict']['exportedItemIdx'] += 1
        exportEntry(entry, user)
        if (gVal['statInfoDict']['exportedItemIdx'] % 10) == 0 :
            logging.info("Has exported %4d blog items", gVal['statInfoDict']['exportedItemIdx'])
    gVal['statInfoDict']['exportItemsTime'] = calcTimeEnd("export_items")

    # export Foot
    logging.info('Exporting tail info to file ...')
    calcTimeStart("export_foot")
    exportFoot()
    gVal['statInfoDict']['exportFootTime'] = calcTimeEnd("export_foot")

    # 6. Delete cache file
    logging.info("Deleting cache file ...")
    os.remove('entries.cache')
    logging.info("blog=%s move successfully", blogInfoDic['blogURL'])

    # 7. output statistic info
    gVal['statInfoDict']['totalTime'] = calcTimeEnd("total")
    gVal['statInfoDict']['itemAverageTime'] = gVal['statInfoDict']['totalTime'] / float(gVal['statInfoDict']['exportedItemIdx'])
    outputStatisticInfo()

#------------------------------------------------------------------------------
# got python script file name itsself
def getScriptSelfFilename() :
    # got script self's name
    # for : python xxx.py -s yyy    # -> sys.argv[0]=xxx.py
    # for : xxx.py -s yyy           # -> sys.argv[0]=D:\yyy\zzz\xxx.py
    argv0List = sys.argv[0].split("\\")
    scriptName = argv0List[len(argv0List) - 1] # get script file name self
    possibleSuf = scriptName[-3:]
    if possibleSuf == ".py" :
        scriptName = scriptName[0:-3] # remove ".py"
    return scriptName

###############################################################################
if __name__=="__main__":
    logging.basicConfig(
                    level    =logging.DEBUG,
                    format   = 'LINE %(lineno)-4d  %(levelname)-8s %(message)s',
                    datefmt  = '%m-%d %H:%M',
                    filename = getScriptSelfFilename() + ".log",
                    filemode = 'w');
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    try:
        main()
    except:
        logging.exception("Unknown Error !")
        raise
