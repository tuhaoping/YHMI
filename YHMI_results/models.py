from __future__ import unicode_literals
from django.db import models

import MySQLdb

class FilterResult(object):

	@staticmethod
	def getGeneSet(yhmi_filter, composition='Intersection'):
		yhmi_filter = [f.split("_") for f in yhmi_filter]
		feature_ID = [f.pop(0)[1:] for f in yhmi_filter]
		sqlCmd = "SELECT * FROM `yhmi_comparison_feature` WHERE `ID` IN({})".format(",".join(feature_ID))
		print(sqlCmd)
		print(yhmi_filter)

		try:
			db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'yhmi_database')
			cursor = db.cursor()
			cursor.execute(sqlCmd)
			print(list(cursor.fetchall()))
		except:
			pass
		finally:
			db.close()
		return 0;

	def enrichment_pvalue(self):
		try:
			db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'yhmi_database')
			cursor = db.cursor()
			cursor.execute("SELECT `Name_Gene`, `Name_Alias` FROM yhmi_enrichment WHERE `Name_ORF` IN ('{}')".format("','".join(self.result_gene)))
			self.result_gene = [[ORF, i[0], i[1]] for ORF, i in zip(sorted(list(self.result_gene)), cursor.fetchall())]
		except:
			pass
		finally:
			db.close()

		return self.result_gene





class YhmiEnrichment(models.Model):
    feature = models.CharField(db_column='Feature', primary_key=True, max_length=50)  # Field name made lowercase.
    pro_en = models.TextField(db_column='Pro_en', blank=True, null=True)  # Field name made lowercase.
    pro_de = models.TextField(db_column='Pro_de', blank=True, null=True)  # Field name made lowercase.
    cod_en = models.TextField(db_column='Cod_en', blank=True, null=True)  # Field name made lowercase.
    cod_de = models.TextField(db_column='Cod_de', blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
    	return self.feature
    	
    class Meta:
        managed = False
        db_table = 'yhmi_enrichment'
