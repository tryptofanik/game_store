echo "Fetching docker image"
docker run --name sql_server -d -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=SQL_server0!' -p 1433:1433 mcr.microsoft.com/mssql/server:2019-latest
docker ps
echo "Wait 60 seconds untill the container is created"
sleep 60
echo "Create Database Sales, two datbles; insert some data"
sqlcmd -S 0.0.0.0,1433 -U SA -P 'SQL_server0!' -i make_database.sql -o logs.txt
cat logs.txt
echo "Create Python virtual env"
python3 -m venv .venv
source .venv/bin/activate
echo "Install requiremnets"
pip install -r requirements.txt
source variables.env
echo "Run web app"
flask run