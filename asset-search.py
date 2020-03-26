#!/usr/bin/python3.6

# Example script showing how to use the Preservica API to 
# list assets within the repository.


import sys
import os
import requests
import csv
import argparse


def writeCSVRow(writer, m, identifier):
    
    title = ""
    description = ""
    tag = ""
    document_type = ""
    parent_ref = ""
    top_level_so = ""
    
    for i in m:
        j = dict(i.items())
        if j['name'] == "xip.title":
            title = j['value']
        if j['name'] == "xip.description":
            description = j['value']
        if j['name'] == "xip.security_descriptor":
            tag = j['value'][0]
        if j['name'] == "xip.document_type":
            document_type = j['value']
        if j['name'] == "xip.parent_ref":
            parent_ref = j['value']       
        if j['name'] == "xip.top_level_so":
            top_level_so = j['value'][0]  
                  
    
    if  document_type=="SO":
        writer.writerow([identifier[7:], title, description, tag, parent_ref, "Folder", top_level_so])
    else:
        writer.writerow([identifier[7:], title, description, tag, parent_ref, "Asset", top_level_so])
    
               
def new_token(username, password, tenant, server):
    resp = requests.post(f'https://{server}.preservica.com/api/accesstoken/login?username={username}&password={password}&tenant={tenant}')
    if resp.status_code == 200:
        return resp.json()['token']
    else:
        raise SystemExit

            
def search(start, username, password, tenant, server, token):
    headers = {'Content-Type' : 'application/x-www-form-urlencoded', 'Preservica-Access-Token' : token}
    query =  '{ "q":  "%"  }'
    payload = {'start': start, 'max': PAGE_SIZE, 'metadata' : 'xip.identifier,xip.title,xip.description,xip.security_descriptor,xip.document_type,xip.parent_ref,xip.top_level_so' , 'q' : query }
    results = requests.post(f'https://{server}.preservica.com/api/content/search', data=payload, headers=headers)
    if results.status_code == 200:
        return results.json()
    elif results.status_code == 401:
        accessToken = new_token(username, password, tenant, server)
        return search(start, username, password, tenant, server, accessToken)
    else:
        raise SystemExit  



parser = argparse.ArgumentParser(description='Query Preservica for Assets and Folders')   
parser.add_argument("username", help="Your Preservica username (email address)")
parser.add_argument("password", help="Your Preservica password")
parser.add_argument("tenant",   help="Your Preservica system tenant name (may need to ask support for your tenant name)")
parser.add_argument("server",   help="Your Preservica server name prefix (eu,us,ca,au).preservica.com etc")

parser.add_argument("--output", help="report name (e.g. report.csv)")

args = parser.parse_args()


username = args.username
password = args.password
tenant = args.tenant
server = args.server

if args.output:
    file = open(args.output, 'w', newline='', encoding='utf-8')
else:
    file = open('report.csv', 'w', newline='', encoding='utf-8')

accessToken = new_token(username, password, tenant, server)

PAGE_SIZE=100
start = 0
found = 0

s = search(start, username, password, tenant, server, accessToken)
metadata = s['value']['metadata']

refs = list(s['value']['objectIds'])

hits = int(s['value']['totalHits'])
print(f"Total Number of Results Found:  {hits} ")


writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, delimiter=',')

writer.writerow(["identifier","title", "description", "tag", "parent collection", "type", "root collection"])

while (found < (hits-1)):
    index = 0;
    for m in metadata:
        writeCSVRow(writer, m, refs[index])
        index = index +1
    
    start = start + PAGE_SIZE
    if (start > hits):
        break;
    s = search((start + PAGE_SIZE - 1), username, password, tenant, server, accessToken)
    metadata = s['value']['metadata']
    refs = list(s['value']['objectIds'])
    print("{:.2f}% complete".format((start / hits)*100))
    



