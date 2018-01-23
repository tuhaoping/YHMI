from __future__ import unicode_literals
from django.db import models

from collections import Counter
import MySQLdb


# def executeSQL(sqlCmd):
# 	print(sqlCmd)

class FilterResult(object):

	@staticmethod
	def geneInfo(geneset):
		
		try:
			db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'YHMI_database')
			cursor = db.cursor()
			cursor.execute(sqlCmd)
			res = list(cursor.fetchall())
		except:
			pass
		finally:
			db.close()

		return 0

	@staticmethod
	def filterGene(yhmi_filter, composition=' AND '):
		yhmi_filter = [f.split("_") for f in yhmi_filter]

		feature_ID = {}
		for f in yhmi_filter:
			if f[0][1:] in feature_ID:
				feature_ID[f.pop(0)[1:]].append(f)
			else:
				feature_ID[f.pop(0)[1:]] = [f]
		yhmi_filter = feature_ID
		sqlCmd = "SELECT * FROM `yhmi_comparison_feature` WHERE `ID` IN({})".format(",".join(yhmi_filter.keys()))

		try:
			db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'YHMI_database')
			cursor = db.cursor()
			cursor.execute(sqlCmd)
			res = list(cursor.fetchall())
		except:
			pass
		finally:
			db.close()


		tableDict = {}
		for r in res:
			for f in yhmi_filter[str(r[0])]:
				if r[1] in tableDict:
					tableDict[r[1]+r[4]].append("`Data{}_{}` {} {}".format(r[2], f[0], f[1], f[2]))
				else:
					tableDict[r[1]+r[4]] = ["`Data{}_{}` {} {}".format(r[2], f[0], f[1], f[2])]
		
		# print(tableDict)
		sqlCmd = []
		for table,condiction in tableDict.items():
			condiction = composition.join(condiction).replace("greater", '>=').replace('less', '<=')
			sqlCmd.append("SELECT `ORF` FROM `yhmi_filter_{}` WHERE {}".format(table.lower(), condiction))

		print(sqlCmd)
		try:
			db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'YHMI_database')
			cursor = db.cursor()

			if composition == " AND ":
				data = []
				for sql in sqlCmd:
					cursor.execute(sql)
					data.append({r[0] for r in cursor.fetchall()})
				res = set.intersection(*data)
					
			else:
				sqlCmd = " UNION ".join(sqlCmd)
				cursor.execute(sqlCmd)
				res = [r[0] for r in cursor.fetchall()]

		except MySQLdb.Error as e:
			print(e)
		finally:
			db.close()

		return res;

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

class YhmiEnrichmentTf(models.Model):
    feature = models.CharField(db_column='Feature', primary_key=True, max_length=50)  # Field name made lowercase.
    pro = models.TextField(db_column='Pro', blank=True, null=True)  # Field name made lowercase.
    cod = models.TextField(db_column='Cod', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'yhmi_enrichment_tf'
