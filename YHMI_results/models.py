from __future__ import unicode_literals
from django.db import models

from collections import Counter
import json
import MySQLdb
import random
import string


# def executeSQL(sqlCmd):
#   print(sqlCmd)

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
		sqlCmd = """SELECT `ID`,`TableName`,`TableID`,`Data`
					FROM `const_comparison_feature` 
					WHERE `ID` IN({})""".format(",".join(yhmi_filter.keys()))

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
		# print(yhmi_filter)
		for r in res:
			TableID = "_"+r[2] if r[2] else ""

			for f in yhmi_filter[str(r[0])]:
				table_name = r[1]+TableID
				if table_name in tableDict:
					tableDict[table_name].append("`Data{}_{}` {} {}".format(r[3], f[0], f[1], f[2]))
				else:
					tableDict[table_name] = ["`Data{}_{}` {} {}".format(r[3], f[0], f[1], f[2])]
		
		# print(tableDict)
		sqlCmd = []
		for table,condiction in tableDict.items():
			condiction = composition.join(condiction).replace("greater", '>=').replace('less', '<=')
			sqlCmd.append("SELECT `ORF` FROM `yhmi_filter_{}` WHERE {}".format(table.lower(), condiction))

		# print(sqlCmd)
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

		# print(res)
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

class InputCheak():
	"""docstring for InputCheak"""
	def __init__(self, inputGene):
		
		db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'YHMI_database')
		cursor = db.cursor()
		query = "SELECT DISTINCT `ORF` FROM `const_comparison_orf` WHERE `InputGene` IN('{}')".format("','".join(inputGene))

		cursor.execute(query)
		self.qualified_gene = [g[0] for g in cursor.fetchall()]

class YhmiEnrichmentTempTable():
	__db = ["localhost", 'haoping', 'a012345', 'YHMI_database']
	__tableID = ''
	__main_table = 'yhmi_enrichment'
	__temp_table = 'temp_enrichment_'

	def __init__(self, tableID=None):
		def id_generator(size=20, chars=string.ascii_letters + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		
		if tableID:
			self.__tableID = tableID
		else:
			try:
				con = MySQLdb.connect(*self.__db)
				cursor = con.cursor()
				self.__tableID = id_generator()
				sqlCmd = "INSERT INTO `yhmi_temporary_table` VALUES('{}', DATE_ADD(NOW(), INTERVAL 1 DAY))".format(self.__tableID)
				cursor.execute(sqlCmd)

				sqlCmd = 'CREATE TABLE `{}` LIKE `{}`'.format(self.__temp_table + self.__tableID, self.__main_table)
				cursor.execute(sqlCmd)
				sqlCmd = 'INSERT INTO `{}` select * from `{}`;'.format(self.__temp_table + self.__tableID, self.__main_table)
				cursor.execute(sqlCmd)
				con.commit()
			except MySQLdb.Error as e:
				print(e)
				con.rollback()
			finally:
				con.close()


	@property
	def tableID(self):
		return self.__tableID
	
	def defaultTable(self):
		try:
			con = MySQLdb.connect(*self.__db)
			cursor = con.cursor()
			sqlCmd = "TRUNCATE TABLE `{}`".format(self.__temp_table + self.__tableID)
			cursor.execute(sqlCmd)
			sqlCmd = "INSERT INTO `{}` SELECT * FROM `{}`".format(
				self.__temp_table + self.__tableID, self.__main_table)
			cursor.execute(sqlCmd)
			con.commit()
		except MySQLdb.Error as e:
			print(e)
		finally:
			con.close()


	def updateTable(self, data):
		if "[" in data:
			data = json.loads(data)
			setting_data = [d.split("_") for d in data]
		else:
			setting_data = [data.split("_")]
		feature_ID = {}
		
		for d in setting_data:
			if d[0][2:] in feature_ID:
				feature_ID[d.pop(0)[2:]].append(d)
			else:
				feature_ID[d.pop(0)[2:]] = [d]

		# sqlCmd = "SELECT * FROM `const_comparison_feature` WHERE `ID` IN({})".format(",".join(feature_ID.keys()))
		sqlCmd = """SELECT `ID`,`Feature`,`TableName`,`TableID`,`Data`
					FROM `const_comparison_feature` 
					WHERE `ID` IN({})""".format(",".join(feature_ID.keys()))
		try:
			con = MySQLdb.connect(*self.__db)
			cursor = con.cursor()
			cursor.execute(sqlCmd)
			res = cursor.fetchall()
		
		except MySQLdb.Error as e:
			print(sqlCmd)
			print(e)

		tableDict = {}
		# {'H3_or_H4_Acetylation_mutant': [('`Data0_pro` en 1.0', 'pro_en', 'H3K4ac_set1D_on_WT_exp2')]
		for r in res:
			TableID = "_"+r[3] if r[3] else ""
			for f in feature_ID[str(r[0])]:
				table_name = r[2]+TableID
				if table_name in tableDict:
					tableDict[table_name].append(("`Data{}_{}` {} {}".format(r[4], f[0], f[1], f[2]), f[0]+"_"+f[1], r[1]))
				else:
					tableDict[table_name] = [("`Data{}_{}` {} {}".format(r[4], f[0], f[1], f[2]), f[0]+"_"+f[1], r[1])]

		try:
			for table, condiction in tableDict.items():
				for c, t, feature in condiction:
					c = c.replace("en", '>=').replace('de', '<=')
					sqlCmd = "SELECT `ORF` FROM `yhmi_filter_{}` WHERE {}".format(table.lower(), c)
					# print(sqlCmd)
					cursor.execute(sqlCmd)
					update_gene = ",".join([r[0] for r in cursor.fetchall()])
					sqlCmd = "UPDATE `{}` SET `{}` = '{}' WHERE `Feature` = '{}'".format(
						self.__temp_table + self.__tableID, t, update_gene, feature)
					cursor.execute(sqlCmd)
			
			con.commit()
		except MySQLdb.Error as e:
			print(e)
		finally:
			con.close()

	def dropTable(self):

		try:
			con = MySQLdb.connect(*self.__db)
			cursor = con.cursor()
			sqlCmd = "DELETE FROM `yhmi_temporary_table` WHERE `tableID` LIKE '{}'".format(self.__tableID)
			cursor.execute(sqlCmd)
			sqlCmd = 'DROP TABLE `{}`'.format(self.__temp_table + self.__tableID)
			cursor.execute(sqlCmd)
			con.commit()
		except MySQLdb.Error as e:
			print(e)
			con.rollback()
		finally:
			con.close()

	def getData(self):
		try:
			con = MySQLdb.connect(*self.__db)
			cursor = con.cursor()
			sqlCmd = '''SELECT `{temp}`.*,`const_comparison_feature`.`Paper`
						FROM `{temp}`
						LEFT JOIN `const_comparison_feature`
						ON `const_comparison_feature`.`Feature`=`{temp}`.`Feature`'''.format(
						temp=self.__temp_table + self.__tableID)

			cursor.execute(sqlCmd)
			res = cursor.fetchall()
		except MySQLdb.Error as e:
			print(e)
		finally:
			con.close()

		for r in res:
			yield {'feature':r[0], 'pro_en':r[1], 'pro_de':r[2], 'cds_en':r[3], 'cds_de':r[4], 'histoneType':r[5],'paper':r[6]}
		


class YhmiEnrichment(models.Model):
	feature = models.CharField(db_column='Feature', primary_key=True, max_length=50)  # Field name made lowercase.
	pro_en = models.TextField(db_column='Pro_en', blank=True, null=True)  # Field name made lowercase.
	pro_de = models.TextField(db_column='Pro_de', blank=True, null=True)  # Field name made lowercase.
	cds_en = models.TextField(db_column='Cds_en', blank=True, null=True)  # Field name made lowercase.
	cds_de = models.TextField(db_column='Cds_de', blank=True, null=True)  # Field name made lowercase.

	def __str__(self):
		return self.feature
		
	class Meta:
		managed = False
		db_table = 'yhmi_enrichment'

class YhmiEnrichmentTf(models.Model):
	feature = models.CharField(db_column='Feature', primary_key=True, max_length=50)  # Field name made lowercase.
	pro = models.TextField(db_column='Pro', blank=True, null=True)  # Field name made lowercase.
	cds = models.TextField(db_column='Cds', blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'yhmi_enrichment_tf'
