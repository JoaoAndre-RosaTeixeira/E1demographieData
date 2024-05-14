from common.api.GeographicData import GeographicData
from common.bdd.BDD import BDD



geographicData = GeographicData()
bdd = BDD()

geographicData.getDownloadCheckAndMergeData()

bdd.createBDD()

bdd.addDataInBDD()

bdd.closeSession()