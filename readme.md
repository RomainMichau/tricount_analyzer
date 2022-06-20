# Extract tricount data

Use the correct TRICOUNT_ID:
```shell
curl --location --request POST 'https://api.tricount.com/api/v1/synchronisation/tricount/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'getTricount=<tricount><id>0</id><random>TRICOUNT_ID</random><description></description><users/><expenses/><versionNumber>0</versionNumber></tricount>' 
```