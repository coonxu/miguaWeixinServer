#! /usr/bin/env python
#coding=utf-8
"""
http://www.open-open.com/lib/view/open1329403902937.html

"""

from xml.etree import ElementTree
import sys

def print_node(node):
    '''打印结点基本信息'''
    print "=============================================="
    print "node.attrib:%s" % node.attrib
    if node.attrib.has_key("age") > 0 :
        print "node.attrib['age']:%s" % node.attrib['age']
    print "node.tag:%s" % node.tag
    print "node.text:%s" % node.text
def read_xml(text):
    '''读xml文件'''
    # 加载XML文件（2种方法,一是加载指定字符串，二是加载指定文件）    
    # root = ElementTree.parse(r"D:/test.xml")
    root = ElementTree.fromstring(text)
    
    # 获取element的方法
    # 1 通过getiterator 
    lst_node = root.getiterator("person")
    for node in lst_node:
        print_node(node)
        
    # 2通过 getchildren
    lst_node_child = lst_node[0].getchildren()[0]
    print_node(lst_node_child)
        
    # 3 .find方法
    node_find = root.find('person')
    print_node(node_find)
    
    #4. findall方法
    node_findall = root.findall("person/name")[1]
    print_node(node_findall)
    
if __name__ == '__main__':
     #read_xml(open("test.xml").read())
    testData = """<root>
 <person age="18">
    <name>hzj</name>
    <sex>man</sex>
 </person>
 <person age="19" des="hello">
    <name>kiki</name>
    <sex>female</sex>
 </person>
</root>
"""
#    print testData
#    read_xml(testData)


    root = ElementTree.Element('color')
    root.text = ('black') 
    
    child0 = ElementTree.Element('book')
    child0.text = ('here is agood')
    
    root.append(child0)
    
    tree = ElementTree.ElementTree(root)
    #tree.write(sys.stdout)
    
    print ElementTree.tostring(root)