# asset-search

## Query Preservica v6 for assets using the search API

Generate a XLS report of all assets and folders in a Preservica system using the search API.
This is not actually a list of files, since an asset may contain multiple files in multiple representations. 

You need a python 3 runtime to run the script.

`usage: asset-search.py [-h] [--output OUTPUT] username password tenant server`

- username:   Your Preservica username (email address)
- password:   Your Preservica password
- tenant:     Your Preservica system tenant name (may need to ask support for your tenant name)
- server:     Your Preservica server name prefix (eu,us,ca,au).preservica.com etc

e.g.

`$./asset-search.py  test@test.com Eyhd87hfp6  TEN  eu `

will query the eu.preservica.com server for all assets which test@test.com has read metadata access.

will write the output to report.csv

`$./asset-search.py  test@test.com Eyhd87hfp6  TEN  eu --output assets.csv`

will write the output to assets.csv

The CSV file has the following columns:

- Asset Identifier
- Type of object, e.g. Asset or Collection
- Asset Title
- Asset Description
- Asset Security Tag
- Parent Collection Identifier
- Parent Collection Name
- Root Collection Identifier
- Root Collection Name

You can search for a particular phrase or word using the `--query` option

`$./asset-search.py  test@test.com Eyhd87hfp6  TEN  eu --output assets.csv --query Trains`

This will search Preservica for all assets or folders where the term "Trains" appears in the metadata or content





