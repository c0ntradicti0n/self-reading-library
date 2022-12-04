
import pyTigerGraph as tg
hostName = "http://localhost"
graphName = "Work_Net"
secret = "phd37nvkrlh6t5t3btrnf6md4rgm80iq"
userName = "tigergraph"
password = "tigergraph"

conn = tg.TigerGraphConnection(host=hostName, username=userName, password=password,  graphname=graphName)

conn.upsertEdge("Person", "person1", "Works",  "Company","company1")
