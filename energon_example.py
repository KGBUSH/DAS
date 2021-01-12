from energon.energonQL import *

query1 = """
SELECT Chiller(B)
FROM Building B
WHERE B.BuildingID = 'CP1' AND B.Source = 'LOCAL'
FILTER B.TIMESTAMP > '20190801' AND B.TIMESTAMP < '20191231'
LABEL 'cop'
"""

query2 = """
SELECT VAV(B) * (Temperature(B) + Setpoint(B))
FROM Building B
WHERE B.BuildingID = 'ecp' AND B.Source = 'LOCAL'
FILTER B.TIMESTAMP > '20190801' AND B.TIMESTAMP < '20191231'
LABEL 'epc'
"""

data, labels = energon(query2)

print(data, labels)