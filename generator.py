import shutil
from os import path
from datetime import datetime, date, time, timedelta
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
import xml
from random import random, randrange
from math import ceil
 
start_time = datetime(2017, 1, 1, 0, 0, 0)
end_time = datetime(2018, 1, 1, 0, 0, 0)
step = 30
doc_path = '/home/sergey/devel/eco_monitoring/xmls'
 
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = xml.etree.ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
 
def generate_name(measure_time):
    result = 'measure_529_0020_{0}.xml'.format(measure_time.strftime("%Y-%m-%d_%H-%M"))
    return result
 
def generate_file(measure_time):
 
    data = {
        'factory':'0020',
        'source':'0100',
        'time':measure_time.strftime("%d-%m-%Y %H-%M"),
        'alarm':'1',
 
        'ids' : ['41526', '41506', '41509', '41504', '41512', '41505'],
        'vals': ['0','1','2','3','4','5','6']
    }
 
    file_name = path.join(doc_path,  generate_name(measure_time))
    print (file_name)
    block = Element('BLOCK')
    header = SubElement(block, 'HEADER')
    ver = SubElement(header,'VER')
    ver.text = '1.03'
    factory_id = SubElement(header, 'ID_FACTORY')
    factory_id.text = data['factory']
 
    body = SubElement(block, 'BODY')
    source = SubElement(body, 'SOURCE')
    id_source = SubElement(source, 'ID_SOURCE')
    id_source.text = data['source']
 
    period_avg = SubElement(source, 'PERIOD_AVG')
    period_avg.text = '3'
 
    dt_avg = SubElement(source, 'DT_AVG')
    dt_avg.text = data['time']
 
    chemney = SubElement(source, 'CHEMNEY')
    id_chemney = SubElement(chemney, 'ID_CHEMNEY')
    id_chemney.text = '01'
 
    id_alarm = SubElement(chemney, 'ID_ALARM')
    id_alarm.text = data['alarm']
 
    for i in range(6):
        measure = SubElement(chemney, 'MEASURE')
        id = SubElement(measure, 'ID_PARAM')
        id.text = data['ids'][i]
        val = SubElement(measure, 'VAL_AVG')
        #val.text = data['vals'][i]
        val.text = str(round(random()*0.3,3))
        dimension = SubElement(measure, 'DIMENSION')
        dimension.text = '0'   
 
 
    f = open(file_name,'w')
    f.write(prettify(block))
    f.close()
 
 
def main():
    _time = start_time
    while(_time<end_time):
        generate_file(_time)
        _time = _time+timedelta(seconds=step)        
 
main()