#! /usr/bin/env python
#coding=utf-8
"""
filename: miguaWXServer.py
本程序用于处理来自微信公共账号的消息，消息协议参看：
http://mp.weixin.qq.com/wiki/index.php?title=%E6%B6%88%E6%81%AF%E6%8E%A5%E5%8F%A3%E6%8C%87%E5%8D%97

消息接收流程：
用户-->微信平台-->miguaWXServer

消息发送流程：
miguaWXServer-->微信平台-->用户

微信目前只支持用户上行后回复消息，还不能主动下发
微信服务器接口配置信息：
URL:http://weixin.lidama.net
Token:coonxu
"""

from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer, utils
from twisted.python import log
from miguaCfg import setLog, ErrorCode
import sys
from xml.etree import ElementTree
from wxProcess import processPost

reload(sys)
sys.setdefaultencoding("utf-8")
        
class MiguaWXProtocol(protocol.Protocol):
    """
    something about MiguaWXProtocol
    """
    
    def __init__(self):
        self.parseBuf = ""
        self.parseContinue = False
    
    def connectionMade(self):
        """
        connectionMade
        """
        log.msg("Connected from [%s]" % (str(self.transport.client)))
    
    def dataReceived(self, data):
        """
        dataReceived
        """
        log.msg("<==[%s]:[%s]" % (str(self.transport.client), data))
        
        #do something for data
        self.dataParsed(data)
        
    def dataSended(self, data):
        """
        dataSended
        """
        log.msg("==>[%s]:[%s]" % (str(self.transport.client), data))
        self.transport.write(data)

    def resetParseBuf(self):
        #清空parseBuf，准备下次解析
        self.parseBuf = ""
        self.parseContinue = False
            

    def dataParsed(self, data):
        """
        dataParsed
        """
        log.msg("parsing [%s]" % (data))
        
        self.parseBuf = self.parseBuf + data
        
        if len(self.parseBuf) == 0:
            #buf is no data, do nothing
            return
        
        #取Http的头结束位置\r\n\r\n
        httpHeaderEndPos = self.parseBuf.find("\r\n\r\n");
        
        if httpHeaderEndPos == -1:
            #消息体中没有\r\n\r\n分隔符，直接返回客户端错误
            sendData = self.factory.errorMsg()
            self.dataSended(sendData)
            
            #清空parseBuf，准备下次解析
            self.resetParseBuf()
            return
        
        pos = self.parseBuf.find(" ")
        cmd = self.parseBuf[:pos]
        httpHeader = self.parseBuf[:httpHeaderEndPos]
        
        if cmd == "GET":
            sendData = self.factory.handleGet(httpHeader)
            self.dataSended(sendData)
            
            #清空parseBuf，准备下次解析
            self.resetParseBuf()
            return
        elif cmd == "POST":
            #取平台参数，POST /plat?....
            pos_begin = httpHeader.find("/")
            pos_end = httpHeader.find("?")
            if pos_begin == -1 or pos_end == -1:
                #没有参数，返回错误
                sendData = self.factory.handleGet(httpHeader)
                self.dataSended(sendData)
                
                #清空parseBuf，准备下次解析
                self.resetParseBuf()
                return
            
            platform = httpHeader[pos_begin+1:pos_end]
            log.msg("platform: %s" % platform)
            
            #取Http头中Content-Length的值
            Content_length = 0
            headList = httpHeader.split("\r\n")
            for head in headList:
                if head.find("Content-Length") >= 0:
                    Content_length = int(head.split(":")[1])
            
            postData = self.parseBuf[httpHeaderEndPos+4:]
            log.msg("postData: `%s`" % postData)
            
            if Content_length > len(postData):
                log.msg("---continue recv data---------")
                return
      
            #消息获取完整后，获取post的响应结果
            sendData = self.factory.handlePost(platform, postData)
            self.dataSended(sendData)
            
            #清空parseBuf，准备下次解析
            self.resetParseBuf()
            
            return
        else:
            log.msg("no [get] or [post]")
            return
            
    def connectionLost(self, reason):
        log.msg("Disconnected from [%s]" % (str(self.transport.client)))


class MiguaWXFactory(protocol.Factory):
    """
    something about MiguaWXFactory
    """
    protocol = MiguaWXProtocol
    
    def __init__(self):
        """
        init the factry
        """
        self.cmd_get = 0 
        self.cmd_post = 0
        self.errorCode = ErrorCode
    
    def errorMsg():
        return self.errorCode
    
    def handleGet(self, header):
        """
        本协议中，Get方法只用于微信接口鉴权，取出Http头中的echostr参数
        原样进行返回
        """
        returnData = self.errorCode
        pos = header.find("?")
        if pos == -1:
            #没有参数，返回错误
            return returnData
        
        header = header[pos+1:]
        pos = header.find(" ")
        if pos == -1:
            #没有参数，返回错误
            return returnData
            
        header = header[:pos]
        paramList = header.split("&")
        
        hasEchostr = False
        for param in paramList:
            itemList= param.split('=')
            if itemList[0] == "echostr":
                echostr = itemList[1]
                hasEchostr = True
        
        if hasEchostr == False:
            return returnData
        
        log.msg("echostr: [%s]" % echostr)
        
        #构建返回Get的消息
        returnData = "HTTP/1.1 200 OK\r\n"
        returnData = returnData + "Server: nginx/0.8.53\r\n"
        returnData = returnData + "Connection: close\r\n"
        returnData = returnData + "Content-Length: " + str(len(echostr)) + "\r\n"
        returnData = returnData + "\r\n"
        returnData = returnData + echostr
        
        return returnData
    
    
    def handlePost(self, platform, postData):
        """
        本协议中，Post方法用于微信交互，用户上行的都是XML格式数据，所有业务逻辑
        都在Post中实现
        其中，platform参数从POST 指定的路径读取，用于区分不同微信公共账号
        """ 
        return processPost(platform, postData)
        

def main():   
    if len(sys.argv) < 2:
        print "usage:"
        print "./MiguaWXServer.py -debug"
        print "./MiguaWXServer -log"
        sys.exit()
    
    if sys.argv[1] == "-debug":
        setLog( False )
    else:
        setLog( True )
    
    reactor.listenTCP(80, MiguaWXFactory())
    reactor.run()
    
if __name__ == '__main__':
    main()
