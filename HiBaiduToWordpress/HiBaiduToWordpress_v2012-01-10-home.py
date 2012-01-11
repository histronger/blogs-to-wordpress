#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
【简介】
此脚本作用是：
将百度空间中的文章/帖子的所有内容（文章内容，评论，图片（自己博客的+别的网站的）），
全部都下载下来，导出为xml文件。
此xml文件是符合RSS 2.0规范的，可以被WordPress所识别的（WordPress eXtended RSS），
可以被导入到WordPress中去。
由此实现将百度空间的所有内容搬家到WordPress中去。
因此，此脚本一般被称为：百度空间搬家（到Wordpress的）工具

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
当前脚本名称 -s http://hi.baidu.com/你的博客名称/
例如：
HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/
然后脚本就可以把你百度空间中的所有帖子，评论，图片等，都下载导出为Wordpress可识别的XML文件。
如果导出xml文件大小超过默认设置的2MB，还会帮你自动分割，省却你再用DivXML工具分割了。
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
http://b2.broom9.com/?page_id=519
写的，为了实现从微软的Live Space搬家到WordPress，最新版本在这里：
http://code.google.com/p/live-space-mover/
后来前后经过：
http://www.yhustc.com
和
tonynju.iteye.com
的修改，用于百度空间的搬家，最新版本是2011年4月左右的。
但是大概是在2011年12月份左右，当我第一次折腾从百度搬家到wordpress的时候，
由于百度空间改版，html源码改变，导致该脚本已经失效。
我是在其基础上，重写了绝大部分的内容，另外又增添了很多其他功能。
但还是要感谢前面三位的努力，否则也很难有我的这个版本的诞生。

【详细的功能列表】
1. 对于通过-s参数传入的源URL地址，支持多种格式
    例如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/blog
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/blog/
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/blog/item/f36b071112416ac3a6ef3f0e.html
    都可以自动识别，并且帮你找到你的百度空间的最早发布的那篇文章（first permenant link)，然后依次导出所有的帖子内容。

    (1) 如果你不想让程序自动去分析出，百度空间里面最早发布的那篇帖子的地址，你也可以手动用-f参数指定，例如：
    HiBaiduToWordpress.py -f http://hi.baidu.com/recommend_music/blog/item/f36b071112416ac3a6ef3f0e.html
    当然，你也可以通过-f参数指定从某篇文章开始，然后输出其本身及时间上在其之后发表的所有的文章，比如：
    HiBaiduToWordpress.py -f http://hi.baidu.com/recommend_music/blog/item/234c06cdff60ea5b0eb345ce.html
    （2）你可以通过-l参数来指定只输出多少篇文章，比如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -l 100
    可见，通过-f和-l的搭配使用，你可以自己任意指定，输出博客中的任何一部分帖子内容。

2.支持导出博客帖子的各种详细信息
    对于输出的帖子的内容，支持内容较全，包括：
    标题，链接地址，作者，发布日期，发布帖子所用的易读易记的名字(post name)，所属的分类等。

3.（默认启用）支持下载导出评论的详细信息
    支持帖子所相关的评论信息的导入，其中包括每个评论的详尽的信息：
    评论内容，评论作者，评论作者的链接，评论作者的IP，日期等。
    (1)如果你不想要下载和输出评论信息，可以指定'-c no'参数去禁止下载和导出评论信息，例如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -c no

4.（默认启用）支持图片下载和图片链接替换
    支持下载帖子中所包含的你自己百度空间的图片，并且支持自动把帖子中的地址，换为你所要的地址。
    下载下来的图片，默认是放在 当前文件夹\你的博客用户\pic 中。
    (1) 图片链接的替换规则：
    默认的是将这样的图片地址：
    http://hiphotos.baidu.com/BLOG_USER/WHICH_KIND_PIC/item/PIC_NAME.PIC_SUFFIX
    其中：
    BLOG_USER=recommend_music/recommend%5Fmusic,
    WHICH_KIND_PIC=pic/abpic/mpic,
    PIC_NAME=59743562b26681cfe6113a78/069e0d89033b5bb53d07e9b536d3d539b400bce2,
    PIC_SUFFIX=jpg/jpe/...
    替换为：
    http://localhost/wordpress/wp-content/uploads/BLOG_USER/pic/PIC_NAME.PIC_SUFFIX
    其中：
    BLOG_USER=recommend_music
    其中，对于其中你所要替换的地址：http://localhost/wordpress/wp-content/uploads/BLOG_USER/pic
    可以用-w自己指定，例如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -w http://localhost/wordpress/wp-content/uploads/pic/baidu
    当然，为了保证图片正常显示，你需要确认的是：
    A.你的wordpress中也要存在对应的目录
    B.你要手动把下载的图片拷贝到wordpress的对应的路径中去。
    (2) 你也可以通过'-p no'去禁止上述下载并替换图片的功能，例如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -p no
    (3) 在开启了上述处理图片的功能的前提下，默认会开启处理其他网站图片的功能
    对于博客中存在其他网站（包括其他百度空间的图片），可以下载对应的图片到：
    当前文件夹\你的博客用户\pic\other_site
    然后对应的地址替换为 -w指定的地址 + other_site
    例如：
    http://beauty.pba.cn/uploads/allimg/c110111/1294G0I9200Z-2b3F.jpg
    替换为：
    http://localhost/wordpress/wp-content/uploads/BLOG_USER/pic/other_site/beauty_pba_1294G0I9200Z-2b3F.jpg
    (4) 如果不需要处理替他网站的图片，可以通过 -o no 去禁止此功能，比如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -o no
    (5) 类似地-w参数可以指定要替换的对于原先自己网站的图片的地址，可以通过-r指定对于其他网站的图片所要替换的地址。
    (6) (默认开启)添加了-e参数来开启或禁止近似图片忽略功能
    对于后面处理的某个图片的url，和之前某个出了错的图片地址，如果发现相似，那么就忽略处理此图片。

5. （默认启用）支持(google)翻译功能
    将原先一些中文句子，翻译为对应的英文。
    此功能是为了方便wordpress中，直接可以使用这些已经翻译好的，易读易懂的URL固定链接，去访问对应的博客帖子。
    同时也方便了SEO优化。
    目前的翻译支持，包括博客的帖子的标题的别名(post name)和目录的别名(nice name)。
    
    举例：
    某帖子标题(title)是：                      "关于本博客的介绍"
    如果不翻译，那么帖子的别名(post name)就是："%E5%85%B3%E4%BA%8E%E6%9C%AC%E5%8D%9A%E5%AE%A2%E7%9A%84%E4%BB%8B%E7%BB%8D"
    翻译成英文变为：                           "Introduction on this blog"
    再去除非法的字符后，最终变成：             "Introduction_on_this_blog"
    （此处的非法字符指的是字母，数字，下划线，短横线之外的字符）
    对应wordpress中帖子的固定链接，就从：
    http://localhost/2008/04/19/%E5%85%B3%E4%BA%8E%E6%9C%AC%E5%8D%9A%E5%AE%A2%E7%9A%84%E4%BB%8B%E7%BB%8D/
    变为了：
    http://localhost/2008/04/19/introduction_on_this_blog/
    
    (1) 翻译功能，虽然好用，但是可能会消耗较长时间，所以，如果你不需要此功能，
    或者为了省时间暂时禁止翻，可以通过指定参数‘-t no’去禁止相应的翻译功能：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -t no

6.  支持XML文件超限自动分割
    默认所输出的XML文件，最大2MB，超过此限制，就会自动分割为多个XML文件。
    (1) 当然，你也可以通过'-x 最大字节数'来指定XML的最大限制，单位是字节，例如(200KB=200*1024=204800)：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -x 204800
    同理，如果你不想要XML自动分割功能，那么可以指定一个很大的数值，即可。

7. 支持指定帖子发布地址前缀
    默认情况下，会将帖子的链接地址设置为:
    http://localhost/?p=
    然后加上对应的postID，组成了帖子的发布地址，
    你可以通过'-a addr'的方式指定帖子发布地址的前缀，例如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -a http://www.crifan.com/?p=

8. 支持指定起始的PostID
    默认帖子的PostID是以0为开头的。
    如果有这类需求，已经用脚本将一个百度空间导出xml并导入wordpress了，该空间一共100个帖子。
    然后再去搬家另外一个百度空间，此时，可以指定postID的起始值为100，例如：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music/ -i 100
    然后生成的xml中的帖子链接地址中的postID，就会以100为起始，自动增加了。

9.  支持多种格式的帖子发布时间
    百度空间中，支持针对，帖子发布时间的格式，进行多达3x4=12中不同组合，例如：
    (1) 2008-04-19 19:37
    (2) 2010-11-19 7:30 P.M.
    (3) 2010-11-19 下午 7:30
    (4) 2010/11/19 19:30
    (5) 2010/11/19 7:30 P.M.
    (6) 2010/11/19 下午 7:30
    (7) 2010-11-19 19:30:14
    (8) 2008年04月19日 6:47 P.M.
    (9) 2010年11月19日 下午 7:30
    (10)2010年11月19日 星期五 19:30
    (11)2010年11月19日 星期五 7:30 P.M.
    (12)2010年11月19日 星期五 下午 7:30
    目前都已经支持，均可正确解析。

10. 统计信息和显示信息
    (1)支持在脚本执行的最后，显示当前脚本中每部分的处理所花费的时间
    (2)支持每处理完10个帖子，打印以后提示信息，以免执行时间太长，勿让使用者以为脚本挂了

11. 支持替换FCK_MP3_MUSIC相关部分音频播放器所支持的字符串
    (1)对于百度空间的帖子，如果插入了音乐播放器，那么就会有类似于这样的：
    <img name="FCK_MP3_MUSIC" src="xxxx" xxx rel="xxx" />
    部分的内容，此处支持将这部分的内容，替换为wordpress中所支持的音频播放形式的字符串。
    例如:
    [audio:pure_music/%b1%cb%b0%b6%bb%a8%bf%aa%b3%c9%ba%a3%a1%a1%b4%cb%b5%d8%20%bb%c4%b2%dd%b4%d4%c9%fa%a3%a8%c2%d2%ba%ec%20-%20%b3%c2%d4%c3%a3%a9.mp3|titles=彼岸花开成海　此地 荒草丛生（乱红 - 陈悦）]
    这样，替换后的字符串，就可以被wordpress中的一些音频播放器，如Audio Player所识别并播放了。
    此功能用法为：
    HiBaiduToWordpress.py -s http://hi.baidu.com/recommend_music -m replacedMusicString.txt
    其中，replacedMusicString.txt是当前文件夹下的一个文本配置文件，内容为：
    [audio:${category}/${postTitleName}.mp3|titles=${titleName}]

12. 支持处理Songtaste歌曲相关信息
    (1) 支持替换百度空间中音乐播放器相关的html源码为wordpress中音频播放器的代码。
    将形如这样的html源码：
    替换为所配置的：
    
【其他说明】
1.关于脚本执行速度
实测多个百度空间，帖子：内容+评论+图片+翻译，平均每个帖子消耗1.2秒左右。
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

【TODO】
1. 添加Python的chardet库下载安装方法


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
import cookielib

#--------------------------------const values-----------------------------------
__VERSION__ = "v2012-01-10"
null = ''

gConst = {
    'generator'         : "http://www.crifan.com",
    'baiduSpaceDomain'  : 'http://hi.baidu.com',
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
    'postID'                : 0,
    'blogUser'              : '',
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
    'omitSimErrUrl'  : '',
    # need process ST music or not
    'needProcessSt'     : '',
    # do translate or not
    'doTrans'           : '',
    # process comments or not
    'processCmt'        : '',
    # music string that we want to replace to, set to null means not replace
    'replacedMusicStr'  : '',
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
# baidu blog url like this:
#http://hi.baidu.com/recommend_music/blog/item/5fe2e923cee1f55e93580718.html
#http://hi.baidu.com/notebookrelated/blog/item/c0d090c34dda5357b219a8b0.html
# extract 5fe2e923cee1f55e93580718 c0d090c34dda5357b219a8b0 from above baidu url
def extractThreadId(baidu_url):
    idx_last_slash = baidu_url.rfind("/")
    start = idx_last_slash + 1 # jump the last '/'
    end = idx_last_dot = baidu_url.rfind(".")
    return baidu_url[start:end]

#------------------------------------------------------------------------------
# remove some special char, for which, the wordpress not process it
def filterHtmlTag(cmtContent) :
    filtered_comment = cmtContent

    #(1)
    #from : 谢谢~<img src="http:\/\/img.baidu.com\/hi\/jx\/j_0003.gif">
    #to   : 谢谢~<img src="http://img.baidu.com/hi/jx/j_0003.gif">
    filter = re.compile(r"\\/")
    filtered_comment = re.sub(filter, "/", filtered_comment)

    return filtered_comment

"""
#------------------------------------------------------------------------------
# seems need this func only when use ast.literal_eval to parse string to dict value
# note: current use eval to convert string to dict value, so not need this function now
#
# makue sure the content field in response['body']['data'][N] is valid
# -> replace possible english quote char to chinese quote char
# eg: in following:
# "content":"测试添加一个双引号，cn=“中文双引号”，en="英文双引号"，测试完毕。","reserved1":0,
# the quote char before 英文双引号 would cause the content field finish unexpected
# so replace " to “
def makesureContentdValid(contentField) :
    #logging.debug("content pos=%d", contentField.findAll("\",\"content\":\""))
    #logging.debug("resv pos=%d", contentField.findAll("\",\"reserved1\":\""))
    #startPos = contentField.find("\"content\":\"")
    #startPos += 13 #jump over -> ","content":"
    #endPos = contentField.find("\",\"reserved1\":\"")
    
    #logging.debug("content info=%s", contentField[startPos:endPos])
    contentField = contentField.replace("\\\"", "\\u201c")
    contentField = contentField.replace("\\n", "")
    
    return contentField
"""

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

    gVal['exportFileName'] = 'hibaidu_[' + gVal['blogUser'] + "]_" + datetime.now().strftime('%Y%m%d_%H%M')+ '-0' + '.xml'

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
# 
def genReqCmtUrl(blogItemUrl, startCmtIdx, reqCmtNum):
    thread_id_enc = extractThreadId(blogItemUrl)
    cmtReqTime = random.random()
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
    }
    paraDict['thread_id_enc'] = str(thread_id_enc)
    paraDict['start'] = str(startCmtIdx)
    paraDict['count'] = str(reqCmtNum)
    paraDict['t'] = str(cmtReqTime)
        
    mainUrl = "http://hi.baidu.com/cmt/spcmt/get_thread"
    getCmtUrl = genFullUrl(mainUrl, paraDict)

    logging.debug("getCmtUrl=%s",getCmtUrl)
    return getCmtUrl;

#------------------------------------------------------------------------------
# get comments for input url of one blog item
# return the converted dict value
def getComments(url):
    global gCfg
    #cmt_ret_content = ''
    onceGetNum = 100 # get 1000 comments once
    needRetry = False
    
    return_dict = {"err_no":0,"err_msg":"", "total_count":'', "response_count":0, "err_desc":"","body":{"total_count":0, "real_ret_count":0, "data":[]}}

    for tries in range(gCfg['funcTotalExecNum']) :
        try :
            # init before loop
            return_dict = {"err_no":0,"err_msg":"", "total_count":'', "response_count":0, "err_desc":"","body":{"total_count":0, "real_ret_count":0, "data":[]}}
            cmt_resp_dict = {}
            needGetMoreCmt = True
            startCmtIdx = 0
            needRetry = False

            while needGetMoreCmt :
                cmt_url = genReqCmtUrl(url, startCmtIdx, onceGetNum)
                cmt_req = urllib2.Request(cmt_url)
                cmt_ret_content = urllib2.build_opener().open(cmt_req).read()
                
                if cmt_ret_content == '' :
                    logging.warning("Can not get the %d comments for blog item: %s", startCmtIdx, url)
                    break;
                else :
                    # although eval is unsafe, not recommend to use
                    # but ast.literal_eval will cause "ValueError: malformed string"
                    # so use eval here
                    #logging.debug("before  eval or ast.literal_eval, coomment response\n----------------------------\n%s", cmt_ret_content)
                    cmt_resp_dict = eval(cmt_ret_content)
                    #cmt_resp_dict = ast.literal_eval(cmt_ret_content_filtered) # only Python 2.6+ support ast module
                    #logging.debug("after eval or ast.literal_eval\n----------------------------\n%s", cmt_resp_dict)
                    
                    # validate comments response
                    if cmt_resp_dict['err_no'] != 0:
                        # error number no 0 -> errors happened
                        needGetMoreCmt = False
                        needRetry = True
                        logging.warning("Reponse error for get %d comments for %s, error number=%d, error description=%s, now do retrt.",
                                    startCmtIdx, url, cmt_resp_dict['err_no'], cmt_resp_dict['err_desc'])
                        break;
                    else :
                        # merge comments
                        return_dict['err_no'] = cmt_resp_dict['err_no']
                        return_dict['err_msg'] = cmt_resp_dict['err_msg']
                        return_dict['total_count'] = cmt_resp_dict['total_count']
                        return_dict['response_count'] += cmt_resp_dict['response_count']
                        return_dict['err_desc'] = cmt_resp_dict['err_desc']                      
                        return_dict['body']['total_count'] = cmt_resp_dict['body']['total_count']
                        return_dict['body']['real_ret_count'] += cmt_resp_dict['body']['real_ret_count']
                        return_dict['body']['data'].extend(cmt_resp_dict['body']['data'])
                        
                        #print "return_dict['body']['real_ret_count']=",return_dict['body']['real_ret_count']
                        #print "return_dict['response_count']=",return_dict['response_count']
                        #print "int(return_dict['total_count']=",return_dict['total_count']
                        
                        # check whether we have done for get all comments
                        if int(return_dict['body']['real_ret_count']) < int(return_dict['body']['total_count']) :
                            # not complete, continue next get
                            needGetMoreCmt = True
                            startCmtIdx += onceGetNum
                            logging.debug('Continue to get next %d comments start from %d for %s', onceGetNum, startCmtIdx, url)
                        else :
                            # complete, quit
                            needGetMoreCmt = False
                            needRetry = False
                            logging.debug('get all comments successfully for %s', url)
                            break;
                logging.debug("In get comments while loop end, startCmtIdx=%d, onceGetNum=%d, needGetMoreCmt=%s, needRetry=%s", startCmtIdx, onceGetNum, needGetMoreCmt, needRetry)
            if not needRetry :
                break; # break for the for loop -> is OK, so quit here.
        except :
            if tries < (gCfg['funcTotalExecNum'] - 1) :
                logging.warning("Fetch comemnts for %s fail, do %d retry", url, (tries + 1))
                continue
            else : # last try also failed, so exit
                logging.warning("Has tried %d times to fetch comments for %s, all failed!", gCfg['funcTotalExecNum'], url)
                #sys.exit(2) # can not get comments is not big problem, so contine execute following code

    logging.debug('before return all comments done')
    
    #cmt_ret_content = BeautifulSoup(cmt_ret_content) # no need call this
    #logging.debug("original got whole response is\n******************\n%s\n******************\n",cmt_ret_content)

    #cmt_ret_content_filtered = makesureContentdValid(cmt_ret_content)
    #cmt_ret_content_filtered = cmt_ret_content
    #logging.debug("\n-------------after filter content field -------\n%s\n",cmt_ret_content_filtered)

    #return cmt_ret_content_filtered
    return return_dict

#------------------------------------------------------------------------------
# handle some special condition 
# to makesure the content is valid for following decode processing
def validateComentContent(cmtContent):
    #logging.debug("[validateComentContent]input comment content:\n%s", cmtContent)
    validCmtContent = cmtContent
    
    if validCmtContent : # if not none
        # special cases:

        # 1. end of the comment contains odd number of backslash, eg: 'hello\\\\\'
        # -> here just simplely replace the last backslash with '[backslash]'
        if (validCmtContent[-1] == "\\") :
            validCmtContent = validCmtContent[0:-1]
            validCmtContent += '[backslash]'

    #logging.debug("[validateComentContent]validated comment content:\n%s", validCmtContent)
    return validCmtContent

#------------------------------------------------------------------------------
# fill source comments dictionary into destination comments dictionary
def fillComments(dest_cmt_dict, src_cmt_dict):
    #fill all comment field
    dest_cmt_dict['id'] = src_cmt_dict['id']
    logging.debug("--- comment[%d] ---", dest_cmt_dict['id'])

    dest_cmt_dict['author'] = packageCDATA(src_cmt_dict['user_name'].decode('unicode-escape'))
    dest_cmt_dict['author_email'] = ''

    user_name_decoded = src_cmt_dict['user_name'].decode('unicode-escape')
    if user_name_decoded :
        cmturl = 'http://hi.baidu.com/sys/checkuser/' + user_name_decoded + '/1'
    else :
        cmturl = ''
    dest_cmt_dict['author_url'] = saxutils.escape(cmturl)

    dest_cmt_dict['author_IP'] = src_cmt_dict['user_ip']

    epoch = int(src_cmt_dict['create_time'])
    local_time = time.localtime(epoch)
    gmt_time = time.gmtime(epoch)
    dest_cmt_dict['date'] = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    dest_cmt_dict['date_gmt'] = time.strftime("%Y-%m-%d %H:%M:%S", gmt_time)

    # handle some speical condition
    src_cmt_dict['content'] = validateComentContent(src_cmt_dict['content'])
    #logging.debug("before decode, coment content:\n%s", src_cmt_dict['content'])
    cmt_content = src_cmt_dict['content'].decode('unicode-escape') # convert from \uXXXX to character
    #logging.debug("after decode, coment content:\n%s", cmt_content)
    cmt_content = filterHtmlTag(cmt_content)
    # remove invalid control char in comments content
    cmt_content = removeCtlChr(cmt_content)
    #logging.debug("after filtered, coment content:\n%s", cmt_content)
    dest_cmt_dict['content'] = packageCDATA(cmt_content)

    dest_cmt_dict['approved'] = 1
    dest_cmt_dict['type'] = ''
    dest_cmt_dict['parent'] = 0
    dest_cmt_dict['user_id'] = 0

    logging.debug("author=%s", dest_cmt_dict['author'])
    logging.debug("author_url=%s", dest_cmt_dict['author_url'])
    logging.debug("date=%s", dest_cmt_dict['date'])
    logging.debug("date_gmt=%s", dest_cmt_dict['date_gmt'])
    logging.debug("content=%s", dest_cmt_dict['content'])

    return dest_cmt_dict

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
# forcely convert some char into %XX, XX is hex value for the char
# eg: recommend_music -> recommend%5Fmusic
def doForceQuote(origin_str) :
    quoted_str = ''
    special_list = ['_'] # currently only need to convert the '_'

    for c in origin_str :
        if c in special_list :
            c_hex = binascii.b2a_hex(c)
            c_hex_str = '%' + str(c_hex).upper()
            quoted_str += c_hex_str
        else :
            quoted_str += c

    return quoted_str

#------------------------------------------------------------------------------
# check file validation:
# open file url to check return info is match or not
# with exception support
# note: should handle while the file url is redirect
# eg :
# http://publish.it168.com/2007/0627/images/500754.jpg ->
# http://img.publish.it168.com/2007/0627/images/500754.jpg
def isFileValid(fileUrl) :
    global gConst

    fileIsValid = False
    errReason = ''

    try :
        origFileName = fileUrl.split('/')[-1]
        retFileUrl = urllib2.urlopen(fileUrl) # note: Python 2.6 has added timeout support.
        realUrl = retFileUrl.geturl()
        newFileName = realUrl.split('/')[-1]
        urlInfo = retFileUrl.info()
        contentLen = urlInfo['Content-Length']
        # eg: Content-Type= image/gif, ContentTypes : audio/mpeg
        # more ContentTypes can refer: http://kenya.bokee.com/3200033.html
        contentType = urlInfo['Content-Type']
        # for redirect, if returned size>0 and filename is same, also should be considered valid
        if (origFileName == newFileName) and (contentLen > 0):
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

    # here type(errReason)= <class 'urllib2.HTTPError'>, so just convert it to str
    errReason = str(errReason)
    return (fileIsValid, errReason)

#------------------------------------------------------------------------------
# download from fileUrl then save to fileToSave
# with exception support
# note: the caller should make sure the fileUrl is a valid internet resource/file
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
        if fileUrl :
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
                        #                   1=field1    2=field2                   3=field3/blogUser              4=fileName                       5=suffix
                        pattern = r'http://(\w{1,20})\.(\w{1,20})\.\w{1,10}[\.]?\w*/([\w%\-=]{0,50})[/]?[\w\-/%=]*/([\w\-\.]{1,100})\.([' + gVal['picSufStr'] + r']{3,4})'
                        searched = re.search(pattern, curUrl)
                        if searched :
                            origin_url = searched.group(0)
                            fd1     = searched.group(1)
                            fd2     = searched.group(2)
                            fd3     = searched.group(3) # for baidu pic, is blogUser
                            fileName= searched.group(4)
                            suffix  = searched.group(5)
                            #print "origin_url=",origin_url
                            #print '1=',fd1,'2=',fd2,'3=',fd3,'4=',fileName,'5=',suffix
                            if suffix.lower() in gConst['validPicSufList'] :
                                # indeed is pic, process it
                                (picIsValid, errReason) = isFileValid(curUrl)
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
                                    if (fd1=='hiphotos') and (fd2=='baidu') and ((fd3==gVal['blogUser'])or(fd3==doForceQuote(gVal['blogUser']))) :
                                        # is baidu pic
                                        # from http://hiphotos.baidu.com/AAA/BBB/item/CCC.DDD
                                        # AAA=recommend_music/recommend%5Fmusic, BBB=pic/abpic/mpic, CCC=59743562b26681cfe6113a78/069e0d89033b5bb53d07e9b536d3d539b400bce2, DDD=jpg/jpe/...
                                        # to   gCfg['picPathInWP']/CCC.DDD
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
#extract baidu blog user name
# eg: recommend_music
# in    http://hi.baidu.com/recommend_music
# or in http://hi.baidu.com/recommend_music/blog
# or in http://hi.baidu.com/recommend_music/blog/
# or in http://hi.baidu.com/recommend_music/blog/item/f36b0
# or in http://hi.baidu.com/recommend_music/blog/item/f36b071112416ac3a6ef3f0e.html
def extractBlogUser(inputUrl):
    global gVal
    global gCfg
    global gConst

    logging.debug("Extracting blog user from url=%s", inputUrl)

    if gVal['blogUser'] == '' :
        splited_url = inputUrl.split("/")
        if splited_url[2] == 'hi.baidu.com' :
            gVal['blogUser'] = splited_url[3] # recommend_music
            logging.info("Extracted Blog user [%s] from %s", gVal['blogUser'], inputUrl)
        else :
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
        
        logging.debug("Extracted real addess  =%s", realAddr)
        
        # (1) process real address
        if realAddr.find('songtaste') > 0 : # is Songtaste type address
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
        
            logging.debug("Songtaste type realAddr=%s", realAddr)
        else :
            # other type address, already is real address, eg:
            # http://www.songtaste.com/song/158105/  -> http://itv.1001m.com/resources/itv/2007/12/17/70060.Mp3
            # http://www.songtaste.com/song/2407245/ -> http://224.cachefile34.rayfile.com/227b/zh-cn/download/d18c6b179f388d1bf1f1d30946802c8a/preview.mp3
            logging.debug("Other type realAddr    =%s", realAddr)

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
        logging.info("Create dir %s for save downloaded ST music files and output ST info file", gVal['stInfo']['dirName'])
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

        logging.debug("Begin to process for download ST music")
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
                        savedFileStr = fullName
                        (audioIsValid, errReason) = isFileValid(songInfoDict['realAddr'])
                        if audioIsValid :
                            dstName = gVal['stInfo']['dirName'] + '/' + fullName # here '/' is also valid in windows dir path
                            downloadOK = downloadFile(songInfoDict['realAddr'], dstName, True)
                            if downloadOK :
                                savedFileStr = "File is valid but download failed"
                        else :
                            savedFileStr = "File Invalid, reason=" + errReason

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
                        outputStInfo("Saved  Name: %s" % savedFileStr)
                        outputStInfo("Quoted Name: %s" % quotedName)
                        outputStInfo("RealAddress: %s" % songInfoDict['realAddr'])
                        outputStInfo("strUrl     : %s" % songInfoDict['strUrl'])
    return

#------------------------------------------------------------------------------
# repace music part string if necessary
# note: 
# before call this, catorgy should be [translated and] quoted
def replaceMusicPartStr(entryDict) :

    # process title name:
    # 1. remove invalid char
    # 2. remove 【歌曲推荐】
    # note: input is unicode string
    def processTitleName(titleNameUni) :
        # 1. remove invalid char
        validTitleName = ''
        invalidChrList = ['/', '\\', '<', '>', '[', ']', '|']
        for c in titleNameUni:
            if c not in invalidChrList :
                validTitleName += c
        # 2. remove 【歌曲推荐】
        recMusicUni = u'【歌曲推荐】'
        filtedTitleName = ''
        if validTitleName :
            filtedTitleName = validTitleName.replace(recMusicUni, '')
        logging.debug("Filtered title name is %s", filtedTitleName)
        return filtedTitleName
        
    # process post title name
    # here not use translated post name, just use quoted name,
    # for it's more convinienct for upload music file while retain Chinese name of music file
    # note: input is unicode string
    def processPostTitleName(filtedTitUni) :
        # from : 彼岸花开成海　此地 荒草丛生（乱红 - 陈悦）
        # to   : %b1%cb%b0%b6%bb%a8%bf%aa%b3%c9%ba%a3%a1%a1%b4%cb%b5%d8%20%bb%c4%b2%dd%b4%d4%c9%fa%a3%a8%c2%d2%ba%ec%20-%20%b3%c2%d4%c3%a3%a9
        quotedTitName = ''
        if filtedTitUni :
            # here, my PC is windows Chinese, encode is GB18030, not utf-8
            filtedTitGb18030 = filtedTitUni.encode('GB18030')
            quotedTitName = urllib.quote(filtedTitGb18030)            
            quotedTitNameLow = quotedTitName.lower()
        
            # note:
            # baidu has take some special filter for the title name
            # while display in webpage, the original title:
            # 彼岸花开成海　此地 荒草丛生（乱红 -  陈悦）
            # become to:
            # 彼岸花开成海　此地 荒草丛生（乱红 - 陈悦）
            # that is, automatically remove a blank space between '-' and "陈"
            # and corresponding quoted string is,
            # from :
            # %b1%cb%b0%b6%bb%a8%bf%aa%b3%c9%ba%a3%a1%a1%b4%cb%b5%d8%20%bb%c4%b2%dd%b4%d4%c9%fa%a3%a8%c2%d2%ba%ec%20-%20%20%b3%c2%d4%c3%a3%a9
            # become to:
            # %b1%cb%b0%b6%bb%a8%bf%aa%b3%c9%ba%a3%a1%a1%b4%cb%b5%d8%20%bb%c4%b2%dd%b4%d4%c9%fa%a3%a8%c2%d2%ba%ec%20-%20%b3%c2%d4%c3%a3%a9
            # so when the generated mp3 (quoted name address) name is invalid, you should mannual check it, to see whether is this kind of problem !!!

        logging.debug("Quoted low case title name is %s", quotedTitNameLow)
        return quotedTitNameLow

    # baidu space will automatically convert the first char into capital char
    # so here convert it back to low case
    # eg: foreign -> Foreign
    # here change Foreign back to foreign
    def processCategory(categoryUni) :
        origCat = categoryUni
        firstChar = categoryUni[0]
        if firstChar.isupper() :
            # and the rest all low case
            restStr = categoryUni[1:]
            if restStr and restStr.islower():
                firstCharLow = firstChar.lower()
                categoryUni = firstCharLow + restStr
                logging.debug("Convert the first capitalised category %s into %s", origCat, categoryUni)
        return categoryUni

    # replace the FCK_MP3_MUSIC part into configured music string if necessary
    if gCfg['replacedMusicStr']:
        variableDict = {
            'postTitleName' : '',
            'titleName'     : '',
            'category'      : '',
            }
        # init values
        for key in variableDict.keys() :
            variableDict[key] = entryDict[key]
        # process values
        variableDict['titleName'] = processTitleName(variableDict['titleName'])
        variableDict['postTitleName'] = processPostTitleName(variableDict['titleName'])
        variableDict['category'] = processCategory(variableDict['category'])

        # replace each key with value
        curMusicStr = gCfg['replacedMusicStr']
        for key in variableDict.keys() :
            variableStr = '\$\{' + key + '\}'
            variableP = re.compile(variableStr)
            keyValue = variableDict[key]
            curMusicStr = variableP.sub(keyValue, curMusicStr)
        
        # only for baidu space
        # replace these:
        # [example 1]
        # <img name="FCK_MP3_MUSIC" src="http://hi.baidu.com/fc/editor/skins/default/update/mmlogo.gif" width="400" height="95" rel="url%3Dhttp%3A%2F%2Fdc226.4shared.com%2Fimg%2F304319813%2F51da9d11%2Fdlink__2Fdownload_2FwPcnVgrN_3Ftsid_3D20100820-235837-71206df4%2Fpreview.mp3%26name%3DYou%20Will%20Never%20Be%26artist%3DJulia%20Sheer%26extra%3D%26autoPlay%3Dtrue%26loop%3Dtrue" />
        # [example 2]
        # <img name="FCK_MP3_MUSIC" width="400" height="95" rel="url%3Dhttp%3A%2F%2Fwww.nhcs.cn%2Fbuddismmedia%2FUploadFiles_6089%2F200902%2Fluanhong.mp3%26name%3D%E4%B9%B1%E7%BA%A2%26artist%3D%E9%99%88%E6%82%A6%26extra%3D%26autoPlay%3Dtrue%26loop%3Dtrue" src="http://www.crifan.com/files/pic/recommend_music/other_site/hi_baidu_mmlogo.gif" />
        # into:
        # [audio:${category}/${postTitleName}.mp3|titles=${titleName}]
        # in which, eg:
        # category = pure_music
        # postTitleName = Track_Listing_You_Will_Never_Be_-_Julia_Sheer
        # titleName = 【歌曲推荐】You Will Never Be - Julia Sheer
        mp3P = re.compile(r'<img name="FCK_MP3_MUSIC".*?rel=".*?".*?/>')
        entryDict['content'] = mp3P.sub(curMusicStr, entryDict['content'])
        logging.debug("Replace baidu FCK_MP3_MUSIC string into %s", curMusicStr)

    return 
    
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
# process blog content if necessary
def postProcessContent(entryDict) :
    global gCfg
    
    # 1. remove invalid ascii control char, 
    # for wordpress importer can not prase it
    entryDict['content'] = removeCtlChr(entryDict['content'])

    # 2. download ST music if necessary
    afterFilter = entryDict['content']
    downloadStMusic(afterFilter)

    # 3. repace music part string if necessary
    replaceMusicPartStr(entryDict)
    
    return 

#------------------------------------------------------------------------------
# extract category from soup
def extractCategory(soup) :
    global gVal
    catXmlSafe = ''
    
    try :
        foundCat = soup.find(attrs={"class":"opt"}).findAll('a')[0]
        catStr = foundCat.string.strip()
        catNoUniNum = repUniNumEntToChar(catStr)
        catNoUniNum = catNoUniNum.replace(u'类别：', '')
        #catNoUniNum = catNoUniNum.replace(unicode('类别：').encode('utf-8'), '') # this line can not exec !!!
        catXmlSafe = saxutils.escape(catNoUniNum)
        gVal['catNiceDict'][catXmlSafe] = ''

        logging.debug("Extraced catalog: %s", catXmlSafe)
    except :
        logging.debug("No catalog avaliable")

    return catXmlSafe

#------------------------------------------------------------------------------
#1. open current blog item
#2. save related info into blog entry
#3. return link of next blog item
def fetchEntry(url):
    global null
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
    soup = BeautifulSoup(page)
    #logging.debug("Got whole page content\n---------------\n%s",soup.prettify())
    #logging.debug("---------------\n")
    i = {
        'postid'            : 0,
        'nextBlogItemLink'  : '',
        'titleName'         : '',
        'postTitleName'     : '',
        'content'           : '',
        'datetime'          : '',
        'category'          : '',
        'comments'          : []
        }

    i['postid'] = gVal['postID']

    #title
    temp = soup.findAll(attrs={"class":"tit"})[1]
    try :
        # temp should not empty
        if temp.string :
            # 正常的帖子
            titStr = temp.string.strip()
            titNoUniNum = repUniNumEntToChar(titStr)
            titXmlSafe = saxutils.escape(titNoUniNum)
            i['titleName'] = titXmlSafe
        else :
            # 【转】的帖子：
            # <div class="tit"><span style="color:#E8A02B">【转】</span>各地区关于VPI/VCI值</div>        
            titStr = temp.contents[0].string + temp.contents[1].string
            titNoUniNum = repUniNumEntToChar(titStr)
            titXmlSafe = saxutils.escape(titNoUniNum)
            i['titleName'] = titXmlSafe

        logging.debug("Extrated title=%s", i['titleName'])
    except : 
        logging.error("Can not extract blog item title !")
        sys.exit(2)
    # do translate here -> avoid in the end, 
    # too many translate request to google,
    # which will cause "HTTPError: HTTP Error 502: Bad Gateway"
    if i['titleName'] :
        i['postTitleName'] = generatePostName(i['titleName'])
    logging.info("  Title = %s", i['titleName'])

    #datetime
    temp = soup.find(attrs={"class":"date"})
    try :
        i['datetime'] = temp.string.strip() #2010-11-19 19:30, 2010年11月19日 星期五 下午 7:30, ...
        logging.debug("Extracted blog publish date:%s", i['datetime'])
    except :
        logging.error("Can not extracted blog item publish date !")
        sys.exit(2)

    #category
    i['category'] = extractCategory(soup)
    if i['category'] :
        gVal['catNiceDict'][i['category']] = generatePostName(i['category'])

    #content
    temp = soup.find(id='blog_text')
    try :
        # here only one blog item content
        i['content'] = packageCDATA(''.join(map(CData,temp.contents)))
        logging.debug("Extract blog content successfully");
        #logging.debug('blog_text:\n%s', i['content'])
        
        # extract pic url, download pic, replace pic url
        i['content'] = processPhotos(i['content'])
        postProcessContent(i)
    except :
        logging.error("Can not extract blog item content !")
        sys.exit(2)

    #extrat next (later published) blog item link
    #match = re.search(r"var pre = \[(.*?),.*?,.*?,'(.*?)'\]", page, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    # var post = [true,'军训断章','军训断章', '\/yangsheng6810/blog/item/45706242bca812179313c6ce.html'];
    # var post = [false,'','', '\/serial_story/blog/item/.html'];
    match = re.search(r"var post = \[(.*),\s?'.*',\s?'.*',\s?'(.*)'\]", page, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if match:
        if match.group(1) == "true":
            relativeLink = match.group(2)[1:]
            nextLink = gConst['baiduSpaceDomain'] + relativeLink
            logging.debug("Next blog item URL: %s", nextLink)
            i['nextBlogItemLink'] = nextLink
    logging.debug("Extrated next blog item link is %s", i['nextBlogItemLink'])

    #fetch comments
    if gCfg['processCmt'] == 'yes' :
        calcTimeStart("process_comment")

        #extract comments if exist
        cmt_resp_dict = getComments(url)
        if cmt_resp_dict :
            # got valid comments, now proess it
            cmt_real_num = int(cmt_resp_dict['body']['real_ret_count'])
            if cmt_real_num > 0 :
                logging.debug("Real get comments for this blog item : %d\n", cmt_real_num)
                cmt_lists = cmt_resp_dict['body']['data']

                idx = 0
                for idx in range(cmt_real_num):
                    comment = {}

                    origin_cmt_info = cmt_lists[idx]
                    origin_cmt_info['id'] = idx + 1

                    #fill all comment field
                    comment = fillComments(comment, origin_cmt_info)
                    i['comments'].append(comment)

                    idx += 1

                logging.debug('Total extracted comments for this blog item = %d', len(i['comments']))
            else :
                logging.debug("No comments for this blog item: %s", url)
        # calc time
        gVal['statInfoDict']['processCmtTime'] += calcTimeEnd("process_comment")

    return i

#------------------------------------------------------------------------------
# find the first permanent link = url of the earliset published blog item
# Note: make sure the gVal['blogUser'] is valid before call this func
def find1stPermalink(srcURL):
    global gConst
    global gVal

    linkNode = ''

    # visit "http://hi.baidu.com/againinput_tmp/blog/index/10000"
    # will got the last page -> include 1 or more earliest blog items
    maxIdxNum = 10000
    url = gConst['baiduSpaceDomain'] + '/' + gVal['blogUser'] + '/blog/index/' + str(maxIdxNum)

    tit_list = []
    logging.info("Begin to connect to %s",url)
    page = urllib2.urlopen(url)
    logging.info("Connect successfully, now begin to find the first blog item")
    soup = BeautifulSoup(page)
    #logging.debug("------prettified html page for: %s\n%s", url, soup.prettify())

    tit_list = soup.findAll(attrs={"class":"tit"})
    len_tit_list = len(tit_list)
    # here tit list contains:
    # [0]= blog main link
    # [1-N] rest are blog item relative links if exist blog items
    # so len_tit_list >= 1
    if len_tit_list > 1 :
        # here we just want the last one, which is the earliest blog item
        linkNode = tit_list[len_tit_list - 1].a

    if linkNode :
        #linkNodeHref = url.split('com/',1)[0]+'com'+linkNode["href"]
        linkNodeHref = gConst['baiduSpaceDomain'] + linkNode["href"]
        logging.info("Found the first(earliest) blog item: %s",linkNodeHref)
        return linkNodeHref;
    else :
        logging.error("Can not find the entry of blog !")
        return False

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

    generatorStr = generatorT.substitute(generator = gConst['generator'])

    f = openExportFile()
    gVal['fullHeadInfo'] = headerStr + catStr + generatorStr
    f.write(gVal['fullHeadInfo'])
    f.flush()
    f.close()
    return

#------------------------------------------------------------------------------
# parse several datetime format into valid datetime
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
def parseEntryDatetime(entry) :
    datestr = entry['datetime']

    #                   1=year   2=month   3=day [4=星期几] [5=上午/下午] 6=hour 7=minute [8= A.M./P.M.]
    datetime_pattern = r"(\d{4})\D(\d{2})\D(\d{2})\D? ?(\S{0,3}) ?(\S{0,2}) (\d{1,2}):(\d{2}) ?(([A|P].M.)?)"
    matched_datetime = re.search(datetime_pattern, datestr)

    datetime_str = matched_datetime.group(0)
    year = matched_datetime.group(1)
    month = matched_datetime.group(2)
    day = matched_datetime.group(3)
    weekday_zhCN = matched_datetime.group(4)
    moring_afternoon_zhCN = matched_datetime.group(5)
    hour = matched_datetime.group(6)
    minute = matched_datetime.group(7)
    am_pm = matched_datetime.group(8)
    
    logging.debug("datetime_str=%s, year=%s, month=%s, day=%s, hour=%s, minute=%s, weekday_zhCN=%s, moring_afternoon_zhCN=%s, am_pm=%s", 
                datetime_str, year, month, day, hour, minute, weekday_zhCN, moring_afternoon_zhCN, am_pm)

    if moring_afternoon_zhCN :
        afternoon_zhCN_utf8 = u"下午".encode("utf-8")
        if unicode(moring_afternoon_zhCN).encode("utf-8") == afternoon_zhCN_utf8:
        #if unicode(moring_afternoon_zhCN).encode("utf-8") == unicode("下午").encode("utf-8") :  # this line can not excute!!!
            hour = str(int(hour) + 8)

    if am_pm :
        if am_pm == "P.M." :
            hour = str(int(hour) + 8)

    # group parsed field -> translate to datetime value
    datestr = year + "-" + month + "-" + day + " " + hour + ":" + minute
    #logging.debug("grouped datetime string: %s", datestr)
    parsed_gmt8Time = datetime.strptime(datestr, '%Y-%m-%d %H:%M') # here is GMT+8 local time
    #logging.debug("parsed grouped datetime: %s", parsed_gmt8Time)
    gmt0Time = parsed_gmt8Time - timedelta(hours=8)

    entry['pubDate'] = gmt0Time.strftime('%a, %d %b %Y %H:%M:00 +0000')
    entry['postDate'] = parsed_gmt8Time.strftime('%Y-%m-%d %H:%M:00')
    entry['postDateGMT'] = gmt0Time.strftime('%Y-%m-%d %H:%M:00')

#------------------------------------------------------------------------------
# export each entry info, then add foot info
# if exceed max size, then split it
def exportEntry(entry, user):
    global gVal
    global gCfg

    itemT = Template("""
    <item>
        <title>${titleName}</title>
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
        <wp:post_name>${postTitleName}</wp:post_name>
        <wp:status>publish</wp:status>
        <wp:post_parent>0</wp:post_parent>
        <wp:menu_order>0</wp:menu_order>
        <wp:post_type>post</wp:post_type>
        <wp:post_password></wp:post_password>
        <wp:is_sticky>0</wp:is_sticky>
		<category domain="category" nicename="${category_nicename}">${category}</category>
        ${comments}
    </item>
""") #need titleName, entryURL, entryAuthor, category, entryContent, entryExcerpt, postId, postDate, postTitleName

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
            <wp:comment_parent>0</wp:comment_parent>
            <wp:comment_user_id>0</wp:comment_user_id>
        </wp:comment>
""") #need commentId, commentAuthor, commentEmail, commentURL, commentDate, commentDateGMT, commentContent, commentAuthorIP

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
                            commentContent = comment['content'])
    #logging.debug(entry['category'])

    #parse and set time
    parseEntryDatetime(entry)

    itemStr = itemT.substitute(
        titleName = entry['titleName'],
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
        comments = commentsStr,
        postTitleName = entry['postTitleName'],)

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

    logging.debug("Export blog item '%s' done", entry['titleName'])
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
    
    blogInfoDic['blogURL'] = gConst['baiduSpaceDomain'] + '/' + gVal['blogUser'] + '/blog'
    url = blogInfoDic['blogURL']
    logging.info('Blog URL: %s', url)
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    #logging.debug("Prettified url: %s\n---------------\n%s\n", url, soup.prettify())
    
    #blogInfoDic['blogTitle'] = soup.find(attrs={"class":"titlink"}).string.strip()
    blogInfoDic['blogTitle'] = soup.find(attrs={"class":"titlink"}).string
    logging.debug('Blog title: %s', blogInfoDic['blogTitle'])
    #blogInfoDic['blogDiscription'] = soup.find(attrs={"class":"desc"}).string.strip()
    blogInfoDic['blogDiscription'] = soup.find(attrs={"class":"desc"}).string
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
    parser.add_option("-s","--source",action="store", type="string",dest="srcURL",help="source Baidu space address, such as: http://hi.baidu.com/recommend_music/blog")
    parser.add_option("-f","--startfrom",action="store", type="string",dest="startfromURL",help="a permalink in source Baidu space address for starting with.It should be the earliest blog item link. if this is specified, srcURL will be ignored.")
    parser.add_option("-l","--limit",action="store",type="int",dest="limit",help="limit number of transfered posts, you can use this option to test")
    parser.add_option("-c","--processCmt",action="store",type="string",dest="processCmt",default="yes",help="'yes' or 'no'. Process blog cmments or not. Set to 'no' if you not need export comments of blog items.")
    parser.add_option("-u","--userName",action="store",type="string",default='crifan',dest="user",help="Blog author")
    parser.add_option("-i","--firstPostId",action="store",type="int",default=0,dest="firstPostId",help="the start blog post id number. when you have ")
    parser.add_option("-p","--processPic",action="store",type="string",default="yes",dest="processPic",help="Process picture or not: 'yes' or 'no'. Default is 'yes' to download & replace url. The downloaded pictures can be found in a newly created dir under current dir. Note, after import the generated xml file into wordpress, before make pictures (link) in your blog can shows normally, You should mannualy copy these downloaded picture into WORDPRESS_ROOT_PATH\wp-content\uploads\YOUR_BLOG_USER\pic\ while keep the picture's name unchanged. Set to 'no' if you do not need process picture for your blog.")
    parser.add_option("-w","--wpPicPath",action="store",type="string",dest="wpPicPath",help="the path in wordpress, where you want to copy the downloaded pictures into. If you not set this parameter, default will set to http://localhost/wordpress/wp-content/uploads/YOUR_BLOG_USER/pic. Note: This option only valid when processPic='yes'.")
    parser.add_option("-o","--processOtherPic",action="store",type="string",default="yes",dest="processOtherPic",help="for other site picture url, download these pictures and replace them with address with wpOtherPicPath + a New Name. Note: This option only valid when processPic='yes'.")
    parser.add_option("-r","--wpOtherPicPath",action="store",type="string",dest="wpOtherPicPath",help="the path in wordpress, where you want to copy the downloaded other site pictures into. If you not set this parameter, default will set to ${wpPicPath}/other_site. Note: This option only valid when processOtherPic='yes'.")
    parser.add_option("-e","--omitSimErrUrl",action="store",type="string",default="yes",dest="omitSimErrUrl",help="'yes' or 'no'. For download pictures, if current pic url is similar with previously processed one, which is occur HTTP Error, then omit process this pic url. Note: This option only valid when processPic='yes'.")
    parser.add_option("-t","--translateZh2En",action="store",type="string",default="yes",dest="translateZh2En",help="'yes' or 'no' to do translate. For url SEO and more readable, translate chinese words into english for the blog title's post name and nice name of category.")
    parser.add_option("-a","--postidPrefixAddr",action="store",type="string",default="http://localhost/?p=",dest="postidPrefixAddr",help="the prefix address for postid. default is: 'http://localhost/?p='")
    parser.add_option("-x","--maxXmlSize",action="store",type="int",default=2*1024*1024,dest="maxXmlSize",help="Designate the max size in Bytes of output xml file. Default is 2MB=2*1024*1024=2097152")
    parser.add_option("-y","--maxFailRetryNum",action="store",type="int",default=3,dest="maxFailRetryNum",help="Max number of retry when fail for fetch page/get comment etc. Default is 3. Change it as you want. Set to 0 is disable this retry function.")
    parser.add_option("-m","--replMusicCfgFile",action="store",type="string",dest="replMusicCfgFile",help="Replace baidu FCK_MP3_MUSIC string into this configured string, eg: replacedMusicString.txt, while replacedMusicString.txt contain '[audio:${category}/${postTitleName}.mp3|titles=${titleName}]'. Default is none, means not replace.")
    parser.add_option("-g","--needProcessSt",action="store",type="string",default="no",dest="needProcessSt",help="Need to process songtaste music or not. Default to 'no'.")
    
    logging.info("Version: %s", __VERSION__)
    logging.info("1.If find bug, please send the log file and screen output info to green-waste(at)163.com")
    logging.info("2.If you don't know how to use this script, please give '-h' parameter to get more help info")
    printDelimiterLine()

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
    if replMusicCfgFile :
        musiCfgFile = os.open(replMusicCfgFile, os.O_RDONLY)
        replacedMusicStr = os.read(musiCfgFile, os.path.getsize(replMusicCfgFile))
        gCfg['replacedMusicStr'] = replacedMusicStr

    gCfg['needProcessSt'] = needProcessSt
    if gCfg['needProcessSt'] == 'yes' :
        initStInfo()
    
    # init some global values
    gVal['postID'] = firstPostId
    # prepare for statistic
    gVal['statInfoDict']['exportedItemIdx'] = 0
    gVal['statInfoDict']['transNameTime'] = 0.0
    gVal['statInfoDict']['processPicTime'] = 0.0
    gVal['statInfoDict']['processCmtTime'] = 0.0
    gVal['statInfoDict']['fetchPageTime'] = 0.0

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
            gVal['entries'].append(i)
            pickle.dump(i, cacheFile)
            if 'nextBlogItemLink' in i :
                permalink = i['nextBlogItemLink']
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
