# asset-search
Query Preservica v6 for assets using the search API
You need a python 3 runtime to run the script.

Generate a XLS report of all assets and folders in a Preservica system using the search API.

`usage: asset-search.py [-h] [--output OUTPUT] username password tenant server`

o username:   Your Preservica username (email address)
o password:   Your Preservica password
o tenant:     Your Preservica system tenant name (may need to ask support for your tenant name)
o server:     Your Preservica server name prefix (eu,us,ca,au).preservica.com etc

e.g.

`$./asset-search.py  test@test.com Eyhd87hfp6  TEN  eu `

will query the eu.preservica.com server for all assets which test@test.com has read metadata access.

will write the output to report.csv

`$./asset-search.py  test@test.com Eyhd87hfp6  TEN  eu --output assets.csv`

will write the output to assets.csv

