# Trilyzer

## Data export

Include a schedule which read data from tricount API and push them in a database  
Include a html webapp to add/remove tricounts from the DB

# Params

- DB_HOSTNAME: Hostname of the DB used to store tricount data
- DB_USER: Username used to login on the DB. (Need rw access)
- DB_PASSWORD: Password of the Username
- API_USER_PASSWORD: Arbitrary password that you will use to perform standard action on the API
- API_ADMIN_PASSWORD: Arbitrary password that you will use to perform admin action on the Webapp
- TRICOUNT_MAX_NB: Max nb of tricount that can be stored in the DB. Once the threshold is reached the webapp will refuse
  to add new tricount. (DEFAULT: 10)
- SELF_PORT: Port on which the webapp is running: (DEFAULT: 8080)
- DB_NAME: Name of the DB used to store tricount data (DEFAULT: tricount)
- REFRESH_RATE_MIN: Rate of tricount data refresh (DEFAULT: 10min)

# Prerequisite:

- Create a postgresql DB
- Run the [sql/db.sql](sql/db.sql) script on this DB

# run locally

```shell
docker build trilyzer .    
docker run -p 8080:${SELF_PORT} --rm --name trilyzer trilyzer  --db_hostname ${DB_HOSTNAME} --db_password ${DB_PASSWORD} --db_user ${DB_USER} --user_password ${API_USER_PASSWORD} --admin_password ${API_ADMIN_PASSWORD} \
  --tricount_max_nb ${TRICOUNT_MAX_NB} --self_port ${SELF_PORT} --db_name ${DB_NAME} \
  --refresh_rate ${REFRESH_RATE_MIN} 
```

# Usage:

Webapp is accessible on port 8080.  
It is using basic auth. You can authent with:

- user:${API_USER_PASSWORD} => You'll be able to add new tricount
- admin:${API_ADMIN_PASSWORD} => You'll be able to add and remove tricount

# Grafana

You can use the [grafana dashboard json](./grafana/dashboard.json) to get a basic dashbiard

You'll need to have configured the postgresql data source

# Extract tricount data with curl

Use the correct TRICOUNT_ID:

```shell
curl --location --request POST 'https://api.tricount.com/api/v1/synchronisation/tricount/' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'getTricount=<tricount><id>0</id><random>TRICOUNT_ID</random><description></description><users/><expenses/><versionNumber>0</versionNumber></tricount>' 
```