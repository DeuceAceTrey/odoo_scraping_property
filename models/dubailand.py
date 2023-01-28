import requests
import csv
from dateutil.parser import parse

url = 'https://gateway.dubailand.gov.ae/open-data/transactions/export/csv'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','Content-type':'application/json', 'Accept':'*/*'}
body = {
    "parameters":{
        "P_FROM_DATE":"11/01/2022",
        "P_TO_DATE":"11/30/2022",
        "P_GROUP_ID":"",
        "P_IS_OFFPLAN":"",
        "P_IS_FREE_HOLD":"",
        "P_AREA_ID":"",
        "P_USAGE_ID":"",
        "P_PROP_TYPE_ID":"",
        "P_TAKE":"-1",
        "P_SKIP":"",
        "P_SORT":"TRANSACTION_NUMBER_ASC"
        },
    "command":"transactions",
    "labels":{
        "TRANSACTION_NUMBER":"Transaction Number",
        "INSTANCE_DATE":"Transaction Date",
        "PROPERTY_ID":"Property ID",
        "GROUP_EN":"Transaction Type",
        "PROCEDURE_EN":"Transaction sub type",
        "IS_OFFPLAN_EN":"Registration type",
        "IS_FREE_HOLD_EN":"Is Free Hold?",
        "USAGE_EN":"Usage",
        "AREA_EN":"Area",
        "PROP_TYPE_EN":"Property Type",
        "PROP_SB_TYPE_EN":"Property Sub Type",
        "TRANS_VALUE":"Amount",
        "PROCEDURE_AREA":"Transaction Size (sq.m)",
        "ACTUAL_AREA":"Property Size (sq.m)",
        "ROOMS_EN":"Room(s)",
        "PARKING":"Parking",
        "NEAREST_METRO_EN":"Nearest Metro",
        "NEAREST_MALL_EN":"Nearest Mall",
        "NEAREST_LANDMARK_EN":"Nearest Landmark",
        "TOTAL_BUYER":"No. of Buyer",
        "TOTAL_SELLER":"No. of Seller",
        "MASTER_PROJECT_EN":"Master Project",
        "PROJECT_EN":"Project"}
    }
r = requests.post(url = url, headers = headers,json=body)
result = r.text
rows = result.split('\n')
first_row = True
for row in rows:
    row = row.replace('\"','')
    row  = row.split(',')
    if(first_row):
        first_row = False
        continue
    result = {
        'transaction_number' : row[0],
        'transaction_date' : parse(row[1]),
        'property_id' : row[2],
        'transaction_type' : row[3],
        'transaction-sub_type' : row[4],
        'registration_type' : row[5],
        'status' : row[6],
        'usage' : row[7],
        'address' : row[8],
        'property_type' : row[9],
        'property_subtype' : row[10],
        'price' : int(row[11]),
        'transaction_size' : float(row[12]),
        'sqft' : float(row[13]),
        'bedrooms' : row[14],
        'parking' : int(row[15]),
        'nearest_metro' : row[16],
        'nearest_mall' : row[17],
        'nearest_landmark' : row[18],
        'No_of_buyer' : int(row[19]),
        'No_of_seller' : int(row[20]),
        'master_project' : row[21],
        'project' : row[22]
    }