source ./.bashrc

gadmin start all && \
gsql < ./scripts/*.gsql
#cat /home/tigergraph/.gsql_client_log/log.*
cat /home/tigergraph/.gsql_client_log/log.710351

bash