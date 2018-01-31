import requests
import json
import re
import math
import pprint
import logging
import csv

data_endpt = "https://api.gdc.cancer.gov/data"
files_endpt = "https://api.gdc.cancer.gov/files"
case_endpt="https://api.gdc.cancer.gov/cases"



class GDC_api():

    def __init__(self,primary_site,filter_value):
        self.primary_site=primary_site
        self.filter_value=filter_value



    def send_query(self):
        #print('#####Send Query Function Start######')
        fields = [
            "file_id",
            "file_name",
            "cases.case_id",
            "cases.samples.submitter_id"
        ]
        fields = ",".join(fields)
        filters = {
            "op": "and",
            "content": [
                {
                    "op": "in",
                    "content": {
                        "field": "cases.project.primary_site",
                        "value": [self.primary_site]
                    }
                },
                {
                    "op": "in",
                    "content": {
                        "field": "files.data_type",
                        "value": [self.filter_value]

                    }
                },
                {
                    "op": "in",
                    "content": {
                        "field": "files.access",
                        "value": ["open"]
                    }
                }

            ]
        }
        params = {
            "filters": json.dumps(filters),
            "fields": fields,
            "format": "JSON",
            "size": "100000"
        }
        response = requests.get(files_endpt, params=params)
        file_uuid_list=[]
        case_uuid_list=[]
        file_name_tcga_id={}
        #print(len(case_uuid_list))
        for file_entry in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
            #print(file_entry['file_name'],file_entry['cases'][0]['samples'][0]['submitter_id'])
            file_uuid_list.append(file_entry['file_id'])
            case_uuid_list.append(file_entry['cases'][0]['case_id'])
            file_name_tcga_id[file_entry['file_name']]=file_entry['cases'][0]['samples'][0]['submitter_id']


        print(self.primary_site+' '+self.filter_value+' '+str(len(file_uuid_list)))
        return file_uuid_list,case_uuid_list,file_name_tcga_id

    def make_gene_expression_text_file(self,case_uuid_list,num):
        print('#####Make Text Function Start######')
        output_dict = {}
        for case_id in case_uuid_list:
            #print(case_id)
            filters = {
                "op": "and",
                "content": [
                    {
                        "op": "in",
                        "content": {
                            "field": "cases.case_id",
                            "value": [case_id]
                        }
                    },
                    {
                        "op": "in",
                        "content": {
                            "field": "files.data_type",
                            "value": ["Gene Expression Quantification"]

                        }
                    },
                    {
                        "op": "in",
                        "content": {
                            "field": "files.access",
                            "value": ["open"]
                        }
                    }

                ]
            }
            params = {
                "filters": json.dumps(filters),
                "fields": "file_name",
                "format": "JSON",
                "size": "100000"
            }
            response=requests.get(files_endpt,params=params)
            #print('id: ',case_id)
            #print(json.loads(response.content.decode("utf-8"))["data"]["hits"])
            list_tmp = []
            for file in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
                list_tmp.append(file['file_name'])

           #print(list_tmp)
            output_dict[case_id]=list_tmp
            #print(output_dict.items())

        out_file=self.primary_site+'(GeneExpresionQuantification)'+str(num)+'.csv'
        fout = csv.writer(open(out_file,"w"))
        for key, val in output_dict.items():
            fout.writerow([key,val])

        #print(output_dict.items())



    def slice_file(self,uuid_list,option):
        if option==0:
            num=0
            print('#####Slice Function Start######')
            if len(uuid_list) > 700:
                count = math.ceil(len(uuid_list) / 700)
                for i in range(count):
                    if len(uuid_list) > 700:
                        split_uuid_list = uuid_list[:700]
                        del uuid_list[:700]
                        num+=1
                        self.make_gene_expression_text_file(split_uuid_list,num)
                    else:
                        num+=1
                        self.make_gene_expression_text_file(uuid_list,num)
            else:
                num+=1
                self.make_gene_expression_text_file(uuid_list,num)
        else:
            print('#####Slice Function Start######')
            if len(uuid_list)>700:
                count=math.ceil(len(uuid_list)/700)
                for i in range(count):
                    if len(uuid_list)>700:
                        split_uuid_list=uuid_list[:700]
                        del uuid_list[:700]
                        self.download_file(split_uuid_list)
                    else:
                        self.download_file(uuid_list)
            else:
                self.download_file(uuid_list)

    def download_file(self,down_uuid_list):
        print(self.primary_site+','+self.filter_value+'#####Download Function Start######')
        logger=logging.getLogger('download_file')
        ch=logging.StreamHandler()
        ch.setLevel(logging.ERROR);
        params={"ids":down_uuid_list}
        response = requests.post(data_endpt, data=json.dumps(params), headers={"Content-Type": "application/json"})
        #print(response.headers)
        try:
            response_head_cd = response.headers["Content-Disposition"]
        except KeyError as err:
            logger.error(response.headers)
            print('KeyError')
            response = requests.post(data_endpt, data=json.dumps(params), headers={"Content-Type": "application/json"})
            response_head_cd = response.headers["Content-Disposition"]

        file_name = re.findall("filename=(.+)", response_head_cd)[0]
        out_file = "(" + self.primary_site + "," + self.filter_value + ")" + file_name
        with open(out_file, "wb")as output_file:
            output_file.write(response.content)
        print(self.primary_site+","+self.filter_value+"######download done#########")

    def tcga_id_csv_files(self,name_tcga_id):
        fout = csv.writer(open(self.primary_site+'.csv','w'))
        for key, val in name_tcga_id.items():
            fout.writerow([key,val])

#"Bone","Blood","Brain","Nervous System","Lung","Breast","Adrenal Gland", "Bile Duct","Bladder", "Bone Marrow", "Cervix", "Colorectal", "Esophagus", "Eye",
#                    "Head and Neck", "Kidney", "Liver", "Lymph Nodes", "Ovary", "Pancreas", "Pleura", "Prostate",
#                    "Skin", "Soft Tissue", "Stomach", "Testis", "Thymus", "Thyroid",
#,"Clinical Supplement",  "Masked Somatic Mutation"
if __name__=="__main__":
    primary_site = ["Bone","Blood","Brain","Nervous System","Lung","Breast","Adrenal Gland", "Bile Duct","Bladder",
                    "Bone Marrow", "Cervix", "Colorectal", "Esophagus", "Eye","Head and Neck", "Kidney", "Liver", "Lymph Nodes",
                    "Ovary", "Pancreas", "Pleura", "Prostate","Skin", "Soft Tissue", "Stomach", "Testis", "Thymus", "Thyroid","Uterus"]
    data_type_values = ["Gene Expression Quantification"]
    '''
    for primary1 in primary_site:
        for data_type1 in data_type_values:
            data = GDC_api(primary1, data_type1)
            file_uuid_list, case_uuid_list = data.send_query()
'''

    for data_type in data_type_values:
        for primary in primary_site:
            data=GDC_api(primary,data_type)
            file_uuid_list,case_uuid_list,file_name_tcga_id=data.send_query()
            data.tcga_id_csv_files(file_name_tcga_id)

            #print(case_uuid_list)

            '''
            if data_type=="Gene Expression Quantification" and len(case_uuid_list)!=0:
                print(primary + "  has " + data_type)
                data.slice_file(case_uuid_list,0)
                #data.make_gene_expression_text_file(case_uuid_list)
            else:
                print(primary + " doens't have " + data_type)
            if len(file_uuid_list)!=0:
                print(primary + "  has " + data_type)
                #data.slice_file(file_uuid_list,1)
            else:
                print(primary+" doens't have "+data_type)
            '''









