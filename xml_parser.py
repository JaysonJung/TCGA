import glob
import pprint
import xml.etree.ElementTree as et
import csv
import collections

def get_file_name(xml_list):
    path='/home/jayson/GDC_data/Clinical_Data/xml_data/nationwidechildrens.org_clinical.TCGA-ZN-A9VO.xml'
    xml_list.extend(glob.glob(path,recursive=True))

def extract_attribute(xml_file_name):
    xml_dict = collections.OrderedDict()
    tree=et.ElementTree(file=xml_file_name)
    root=tree.getroot()
    patient=root[1]
    print(root[1])
    for child in patient.iter():
        str_child=str(child)
        split_char1='}'
        split_char2="'"
        split_index1=str_child.find(split_char1)
        split_index2=str_child.rfind(split_char2)
        tag=str_child[split_index1+1:split_index2]

        if child.text is None:
            child.text='None'
        child.text=child.text.strip()
        #child.text='NULL'
        xml_dict[tag] = child.text
        print('TAG:',tag,'ATT:',child.text,' ')
        '''
    out_file=xml_file_name+'.csv'
    fout=csv.writer(open(out_file,'w'))
    for key, val in xml_dict.items():
        fout.writerow([key,val])
        '''

if __name__=='__main__':
    xml_list=[]

    get_file_name(xml_list)
    '''
    for i in xml_list:
        print(i)
    print(len(xml_list))
    '''
    #print(xml_list[1])
    #extract_attribute(xml_list[1])

    for xml_name in xml_list:
        extract_attribute(xml_name)

