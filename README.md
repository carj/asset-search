# asset-search
Query Preservica v6 for assets using the search API

Generate a XLS report of all assets and folders in a Preservica system using the search API.

`usage: asset-search.py [-h] [--output OUTPUT] username password tenant server`

username:   Your Preservica username (email address)
password:   Your Preservica password
tenant:     Your Preservica system tenant name (may need to ask support for your tenant name)
server:     Your Preservica server name prefix (eu,us,ca,au).preservica.com etc

e.g.

`$./asset-search.py  test@test.com Eyhd87hfp6  TEN  eu `

will write the output to report.csv

`$./asset-search.py  test@test.com Eyhd87hfp6  TEN  eu --output assets.csv`

will write the output to data.csv

