import shutil
import xml
import os
from datetime import datetime, date, time, timedelta
from math import ceil
from os import path
from random import random, randrange
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
import graphitesend


doc_path = 'C:/devel/gaz_test'
 
  

def process_file(filename):
    tree = xml.etree.ElementTree.parse(filename)
    root = tree.getroot()
 
    _data = {}
  
    _data['factory'] = root.find('HEADER').find('ID_FACTORY').text
    _data['source'] = root.find('BODY').find('SOURCE').find('ID_SOURCE').text
    _data['dt_avg'] = root.find('BODY').find('SOURCE').find('DT_AVG').text
    _data['alarm'] = root.find('BODY').find('SOURCE').find('CHEMNEY').find('ID_ALARM').text
 
    measure_ids = []
    measure_vals = []
 
    for measure in root.iter('MEASURE'):
        _id = measure.find('ID_PARAM').text
        _val = measure.find('VAL_AVG').text              
        _dim = measure.find('DIMENSION').text

        measure_ids.append(_id)
        measure_vals.append(_val)
 
    _data['measure']=list(zip(measure_ids, measure_vals))
 
    send_data('','192.168.2.194','2003')
   
def send_data(data, server_ip, port):
#    g = graphitesend.init(graphite_server=server_ip,
                            graphite_port=2003,
                            prefix='stats')
#    g.send('tester',random())
    pass
 
 
def main_loop():
    for filename in os.listdir(doc_path):
        if filename.endswith(".xml"):
            filename = os.path.join(doc_path, filename)
            process_file(filename)
 
 
 
main_loop()