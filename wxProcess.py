#! /usr/bin/env python
#coding=utf-8
import sys
import MySQLdb
from twisted.python import log
from xml.etree import ElementTree
from miguaCfg import strHost, strDB, strUser, strPasswd, iPort
from miguaCfg import setLog, ErrorCode

#use a global conn
def dbConnect():
    global conn
    
    #connect to DB
    conn = MySQLdb.connect(host=strHost, db=strDB, user=strUser, 
                            passwd=strPasswd, port=iPort)
    #get the cursor
    cursor = conn.cursor()
    
    #set utf8
    cursor.execute("SET NAMES utf8")
    cursor.execute("SET CHARACTER_SET_CLIENT=utf8")
    cursor.execute("SET CHARACTER_SET_RESULTS=utf8")
    conn.commit()
    
    return conn

def closeDbConnect():
    global conn
    #get the cursor
    cursor = conn.cursor()    
    cursor.close()
    
def dbReConncet():
    global conn
    
    #get the cursor
    cursor = conn.cursor()    
    cursor.close()
    
    #connect to DB
    conn = MySQLdb.connect(host=strHost, db=strDB, user=strUser, 
                            passwd=strPasswd, port=iPort)    
    
    #get the cursor
    cursor = conn.cursor()
    
    #set utf8
    cursor.execute("SET NAMES utf8")
    cursor.execute("SET CHARACTER_SET_CLIENT=utf8")
    cursor.execute("SET CHARACTER_SET_RESULTS=utf8")
    conn.commit()
    
    return conn


def get_db_code_info():
    """
    从初始化指令集,返回code_info表中所有记录,并且根据rid和score倒序
    使用以下格式返回：
    [code1, code2, code3...]
    """
    #return the list for code
    codeList = [] 
    
    global conn
    #get the cursor
    cursor = conn.cursor()
    
    #取出code_info所有记录
    count = 0
    strSql = "SELECT code_content FROM code_info"
    try:
        count = cursor.execute(strSql)
    except:
        strError = "error to excute[%s]" % (strSql)
        log.msg(strError)
        dbReConncet()
    
    results = cursor.fetchall()
    for row in results:
        codeList.append(row[0])
    
    return codeList

def get_db_msg_code(plat):
    """
    从初始化指令平台对应回复记录,返回msg_code表中所有记录
    使用以下格式返回：
    {'code1':'xxxxxx', 'code2':'aaaaaaaa', 'code3':'dddddd'...}
    """
    #return the list for code to msg
    msgCodeDict = {} 
    
    global conn
    #get the cursor
    cursor = conn.cursor()
    
    #取出msg_code所有记录
    count = 0
    strSql = "SELECT code_content, msg FROM msg_code where plat = '%s'" % plat
    try:
        count = cursor.execute(strSql)
    except:
        strError = "error to excute[%s]" % (strSql)
        log.msg(strError)
        dbReConncet()
    
    results = cursor.fetchall()
    for row in results:
        msgCodeDict[row[0]] = row[1]
    
    return msgCodeDict

def get_db_cdkey_bank_nouse(source):
    """
    根据source获取一条未用的cdkey
    """
    global conn
    #get the cursor
    cursor = conn.cursor()
    
    #取出cdkey_bank中未用的1条cdkey
    count = 0
    strSql = "SELECT cdkey FROM cdkey_bank where source = '%s' and status = 0 order by id limit 1" % source
    try:
        count = cursor.execute(strSql)
    except:
        strError = "error to excute[%s]" % (strSql)
        log.msg(strError)
        dbReConncet()
    
    cdkey = ""
    results = cursor.fetchall()
    for row in results:
        cdkey = row[0]
    
    return cdkey

def get_db_cdkey_bank_byUser(username):
    """
    根据username查询玩家是否获取过cdkey
    """
    global conn
    #get the cursor
    cursor = conn.cursor()
    
    #取出cdkey_bank中未用的1条cdkey
    count = 0
    strSql = "SELECT cdkey FROM cdkey_bank where username = '%s'" % username
    try:
        count = cursor.execute(strSql)
    except:
        strError = "error to excute[%s]" % (strSql)
        log.msg(strError)
        dbReConncet()
    
    cdkey = ""
    results = cursor.fetchall()
    for row in results:
        cdkey = row[0]
    
    return cdkey
    

def set_db_cdkey_bank(cdkey, username, source):    
    #get the cursor
    global conn
    cursor = conn.cursor()
    
    #修改cdkey_bank表中指定记录，设置status = 1,usename,createtime
    #--------------------------需要做转义-------------------------------
    strSql = "UPDATE cdkey_bank SET status = 1, username = '%s', createtime = now() \
    WHERE cdkey = '%s' \
    and source = '%s'" % (username, cdkey, source)
    #--------------------------------------------------------------------
    try:
        count = cursor.execute(strSql)
    except:
        strError = "error to excute[%s]" % (strSql)
        log.msg(strError)
        dbReConncet()
    conn.commit()


    
def set_db_msg_log(sender, recver, content, msgtype, plat):
    #get the cursor
    global conn
    cursor = conn.cursor()
    
    #插入记录到msg_log表
    #--------------------------需要做转义-------------------------------
    strSql = "INSERT INTO msg_log(sender, recver, content, msgtype, \
    plat, createtime) values('%s', '%s', '%s', '%s', '%s', now())" % (sender, 
    recver, content, msgtype, plat)
    #--------------------------------------------------------------------
    try:
        count = cursor.execute(strSql)
    except:
        strError = "error to excute[%s]" % (strSql)
        log.msg(strError)
        dbReConncet()
    conn.commit()

def getTextSend(toUserName, fromUserName, createTime, content):
    #构造返回的XML消息                
    reMsgXml = ElementTree.Element('xml')
    child = ElementTree.Element('ToUserName')
    child.text = toUserName
    reMsgXml.append(child)
    child = ElementTree.Element('FromUserName')
    child.text = fromUserName
    reMsgXml.append(child)
    child = ElementTree.Element('CreateTime')
    child.text = createTime
    reMsgXml.append(child)
    child = ElementTree.Element('MsgType')
    child.text = 'text'
    reMsgXml.append(child)
    child = ElementTree.Element('Content')
    child.text = content.encode("UTF-8")
    reMsgXml.append(child)
    child = ElementTree.Element('FuncFlag')
    child.text = '0'
    reMsgXml.append(child)
    
    str_reMsgXml = ElementTree.tostring(reMsgXml)
    log.msg(str_reMsgXml)
    
    returnData = "HTTP/1.1 200 OK\r\n"
    returnData = returnData + "Server: nginx/0.8.53\r\n"
    returnData = returnData + "Connection: close\r\n"
    returnData = returnData + "Content-Length: " + str(len(str_reMsgXml)) + "\r\n"
    returnData = returnData + "\r\n"
    
    returnData = returnData + str_reMsgXml
    
    #log.msg("===========returnData:===========")
    #log.msg(returnData)
    
    return returnData
    
    
def processPost(platform, postData):
    """
    本协议中，Post方法用于微信交互，用户上行的都是XML格式数据，所有业务逻辑
    都在Post中实现
    其中，platform参数从POST 指定的路径读取，用于区分不同微信公共账号    
    """
    returnData = ErrorCode
    
    root = ElementTree.fromstring(postData)
    
    #读取XML中的各个tag
    cntParam = 0
    for child in root.getchildren():
        if child.tag == "ToUserName":
            toUserName = child.text
            cntParam = cntParam + 1
        if child.tag == "FromUserName":
            fromUserName = child.text
            cntParam = cntParam + 1
        if child.tag == "CreateTime":
            createTime = child.text
            cntParam = cntParam + 1
        if child.tag == "MsgType":
            msgType = child.text
            cntParam = cntParam + 1
        if child.tag == "Content":
            content = child.text
            cntParam = cntParam + 1
        if child.tag == "MsgId":
            msgId = child.text
            cntParam = cntParam + 1
        if child.tag == "Event":
            event = child.text
            cntParam = cntParam + 1
        if child.tag == "EventKey":
            eventKey = child.text
            cntParam = cntParam + 1
    
    if cntParam < 6:
        #参数不够，返回错误
        return returnData
    
    if msgType == "event":
        log.msg("do for msg --event...")
        
        #insert to msg log
        set_db_msg_log(fromUserName, toUserName, event, msgType, platform)
        
        #去除消息中的空格
        event = event.strip()
        #大写转换成小写
        event = event.lower()
        
        #不应该反复取-------------------------
        codeList = get_db_code_info()
        msgToCode = get_db_msg_code(platform)
        #-------------------------------------
        
        if event in codeList:
            #只对有对应指令进行反馈
            if msgToCode.has_key(event): 
                msgReturn = msgToCode[event]
            else:
                msgReturn = "need to do more"
            
            returnData = getTextSend(fromUserName, toUserName, createTime, msgReturn)
            #inset to msg log
            set_db_msg_log(toUserName, fromUserName, msgReturn, msgType, platform)
    elif msgType == "text":
        log.msg("do for msg --text...")
        
        #insert to msg log
        set_db_msg_log(fromUserName, toUserName, content, msgType, platform)
        
        #去除消息中的空格
        content = content.strip()
        
        #大写转换成小写
        content = content.lower()
        
        #不应该反复取-------------------------
        codeList = get_db_code_info()
        msgToCode = get_db_msg_code(platform)
        #-------------------------------------
        
        if content in codeList:
            #只对有对应指令进行反馈
            if msgToCode.has_key(content): 
                msgReturn = msgToCode[content]
                                
                #用户发送 pp1 or pp2 即下发激活码
                if content in ("pp1", "pp2", "uc1", "uc2", "uc3", "uc4", 
                                "m1", "m2"):
                    #根据发送消息内容获取平台信息
                    source = content
                    user = fromUserName
                    
                    #用户获取过cdkey?
                    cdkey = get_db_cdkey_bank_byUser(user)
                    if len(cdkey) == 0:
                        
                        #获取cdkey
                        cdkey = get_db_cdkey_bank_nouse(source)
                
                        #设置该cdkey的状态
                        set_db_cdkey_bank(cdkey, user, source)
            
                        msgReturn = cdkey + msgReturn 
                    else:
                        msgReturn = msgToCode["repeatActiveCode"]
                

            else:
                msgReturn = "need to do more"
            
            returnData = getTextSend(fromUserName, toUserName, createTime, msgReturn)
            #inset to msg log
            set_db_msg_log(toUserName, fromUserName, msgReturn, msgType, platform)

    return returnData

#---------------------------需要一个公共连接------------
dbConnect()
#-------------------------------------------------------

if __name__ == '__main__':
    if sys.argv[1] == "-debug":
        setLog(False)
    else:
        setLog(True)
    
    #u must coonect the DB
    dbConnect()
    
    log.msg("wxProcess....")
    
    log.msg("codeList.....")
    codeList = get_db_code_info()
    log.msg(str(codeList))
    
    log.msg("msgBank....")
    msgToCode = get_db_msg_code()
    log.msg(str(msgToCode))
