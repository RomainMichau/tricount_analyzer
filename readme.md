# run
```shell
docker build --tag tricount-analyzer-docker .    
docker run  -p 8080:8080 tricount-analyzer-docker--tricount_id <TRICOUNT_ID>
```
# Extract tricount data with curl

Use the correct TRICOUNT_ID:
```shell
curl --location --request POST 'https://api.tricount.com/api/v1/synchronisation/tricount/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'getTricount=<tricount><id>0</id><random>TRICOUNT_ID</random><description></description><users/><expenses/><versionNumber>0</versionNumber></tricount>' 
```