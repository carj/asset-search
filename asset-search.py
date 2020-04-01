#!/usr/bin/python3.6

# Example script showing how to use the Preservica API to 
# list assets within the repository.


import requests
import csv
import argparse

PAGE_SIZE = 100
accessToken = ""

folder_name_dict = {}


def write_row(w, meta, identifier, token, username, password, tenant, prefix):
    title = ""
    description = ""
    tag = ""
    document_type = ""
    parent_folder_ref = ""
    root_folder_ref = ""

    for i in meta:
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
            parent_folder_ref = j['value']
        if j['name'] == "xip.top_level_so":
            root_folder_ref = j['value'][0]

    global folder_name_dict

    parent_title = ""
    if parent_folder_ref:
        if parent_folder_ref in folder_name_dict:
            parent_title = folder_name_dict[parent_folder_ref]
        else:
            parent_title = get_folder_name(token, username, password, tenant, prefix, parent_folder_ref)
            folder_name_dict[parent_folder_ref] = parent_title

    root_title = ""
    if root_folder_ref:
        if root_folder_ref in folder_name_dict:
            root_title = folder_name_dict[root_folder_ref]
        else:
            root_title = get_folder_name(token, username, password, tenant, prefix, root_folder_ref)
            folder_name_dict[root_folder_ref] = root_title

    asset_type = "Asset"
    if document_type == "SO":
        asset_type = "Folder"

    w.writerow([identifier[7:], asset_type, title, description, tag, parent_folder_ref, parent_title,
                root_folder_ref, root_title])


def get_folder_name(token, username, password, tenant, prefix, folder_ref):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Preservica-Access-Token': token}
    so_request = requests.get(f'https://{prefix}.preservica.com/api/entity/structural-objects/{folder_ref}',
                              headers=headers)
    if so_request.status_code == 401:
        global accessToken
        accessToken = new_token(username, password, tenant, prefix)
        return get_folder_name(accessToken, username, password, tenant, prefix, folder_ref)
    elif so_request.status_code == 200:
        xml_response = str(so_request.content)
        start = xml_response.find('<xip:Title>')
        end = xml_response.find('</xip:Title>')
        return xml_response[start + len('<xip:Title>'):end]
    else:
        print(f"get_folder_name failed with error code: {so_request.status_code}")
        print(so_request.request.url)
        raise SystemExit


def new_token(user, passw, ten, prefix):
    resp = requests.post(
        f'https://{prefix}.preservica.com/api/accesstoken/login?username={user}&password={passw}&tenant={ten}')
    if resp.status_code == 200:
        return resp.json()['token']
    else:
        print(f"new_token failed with error code: {resp.status_code}")
        print(resp.request.url)
        raise SystemExit


def search(start_from, user, passw, ten, prefix, token, term):
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Preservica-Access-Token': token}
    queryterm = ('{ "q":  "%s" }' % term)
    payload = {'start': start_from, 'max': PAGE_SIZE,
               'metadata': 'xip.identifier,xip.title,xip.description,xip.security_descriptor,xip.document_type,'
                           'xip.parent_ref,xip.top_level_so',
               'q': queryterm}
    results = requests.post(f'https://{prefix}.preservica.com/api/content/search', data=payload, headers=headers)
    if results.status_code == 200:
        return results.json()
    elif results.status_code == 401:
        global accessToken
        accessToken = new_token(user, passw, ten, prefix)
        return search(start_from, user, passw, ten, prefix, accessToken, term)
    else:
        print(f"search failed with error code: {results.status_code}")
        print(results.request.url)
        raise SystemExit


def main():
    parser = argparse.ArgumentParser(description='Query Preservica for Assets and Folders')
    parser.add_argument("username", help="Preservica username (email address)")
    parser.add_argument("password", help="Preservica password")
    parser.add_argument("tenant", help="Preservica tenant name (may need to ask support for your tenant name)")
    parser.add_argument("server", help="Preservica server name prefix (eu,us,ca,au).preservica.com etc")

    parser.add_argument("--output", help="report name (e.g. report.csv)")
    parser.add_argument("--query", help="search query term")

    args = parser.parse_args()

    query = "%"
    username = args.username
    password = args.password
    tenant = args.tenant
    server = args.server

    if args.output:
        file = open(args.output, 'w', newline='', encoding='utf-8')
    else:
        file = open('report.csv', 'w', newline='', encoding='utf-8')

    if args.query:
        query = args.query
        print(f"Querying system for all assets containing:  {query} ")
    else:
        print(f"Querying system for all assets")

    global accessToken
    accessToken = new_token(username, password, tenant, server)

    start = 0

    s = search(start, username, password, tenant, server, accessToken, query)
    metadata = s['value']['metadata']
    refs = list(s['value']['objectIds'])

    hits = int(s['value']['totalHits'])
    print(f"Total Number of Results Found (Assets + Folders):  {hits} ")

    writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, delimiter=',')
    writer.writerow(
        ["Identifier", "Object Type", "Title", "Description", "Tag", "Parent collection id", "Parent collection title",
         "Root collection id", "Root collection name"])

    total = 0
    while hits > total:
        index = 0
        for m in metadata:
            write_row(writer, m, refs[index], accessToken, username, password, tenant, prefix=server)
            index = index + 1

        total = total + index
        print("{:.2f}% complete".format((total / hits) * 100))
        start = start + PAGE_SIZE
        s = search(start, username, password, tenant, server, accessToken, query)
        metadata = s['value']['metadata']
        refs = list(s['value']['objectIds'])

    print("Finished")


main()
