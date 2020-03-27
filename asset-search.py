#!/usr/bin/python3.6

# Example script showing how to use the Preservica API to 
# list assets within the repository.


import requests
import csv
import argparse

PAGE_SIZE = 100
accessToken = ""


def write_row(w, meta, identifier):
    title = ""
    description = ""
    tag = ""
    document_type = ""
    parent_ref = ""
    top_level_so = ""

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
            parent_ref = j['value']
        if j['name'] == "xip.top_level_so":
            top_level_so = j['value'][0]

    if document_type == "SO":
        w.writerow([identifier[7:], title, description, tag, parent_ref, "Folder", top_level_so])
    else:
        w.writerow([identifier[7:], title, description, tag, parent_ref, "Asset", top_level_so])


def new_token(user, passw, ten, prefix):
    resp = requests.post(
        f'https://{prefix}.preservica.com/api/accesstoken/login?username={user}&password={passw}&tenant={ten}')
    if resp.status_code == 200:
        return resp.json()['token']
    else:
        print(resp.status_code)
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
        print(results.status_code)
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
    writer.writerow(["identifier", "title", "description", "tag", "parent collection", "type", "root collection"])

    total = 0
    while hits > total:
        index = 0
        for m in metadata:
            write_row(writer, m, refs[index])
            index = index + 1

        total = total + index
        print("{:.2f}% complete".format((total / hits) * 100))
        start = start + PAGE_SIZE
        s = search(start, username, password, tenant, server, accessToken, query)
        metadata = s['value']['metadata']
        refs = list(s['value']['objectIds'])

    print("Finished")


main()
