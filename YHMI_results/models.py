from __future__ import unicode_literals
from django.db import models
from django.db.models import Q

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

class YhmiInputTempTable(object):
	__temp_input_table = 'yhmi_temporary_input'
	__qualified_gene = []
	__results = ''
	__illegal = []

	def __init__(self, tableID, inputGene=None, check_illegal=True):

		self.__tableID = tableID
		try:
			con = MySQLdb.connect('localhost', 'haoping', 'a012345', 'YHMI_database')
			cursor = con.cursor()

			if inputGene:
				inputGene = list(filter(None,inputGene))
				if check_illegal:
					query = "SELECT `InputGene` FROM `const_comparison_orf`"
					cursor.execute(query)
					self.__all6572 = [g[0].upper() for g in cursor.fetchall()]
					self.__illegal = [g for g in inputGene if g.upper() not in self.__all6572]

				query = "SELECT DISTINCT `ORF` FROM `const_comparison_orf` WHERE `InputGene` IN('{}')".format("','".join(inputGene))
				cursor.execute(query)
				self.__qualified_gene = [g[0] for g in cursor.fetchall()]

				query = "DELETE FROM `{}` WHERE `tempID`='{}'".format(self.__temp_input_table, self.__tableID)
				cursor.execute(query)
				query = "INSERT INTO `{}` VALUES(NULL,'{}','{}',NULL, NULL)".format(self.__temp_input_table, self.__tableID, ",".join(self.__qualified_gene))
				cursor.execute(query)
				con.commit()
			else:
				query = "SELECT * FROM `{}` WHERE `tempID` = '{}'".format(self.__temp_input_table, self.__tableID)
				cursor.execute(query)
				res = list(cursor.fetchone())
				self.__qualified_gene = res[2].split(",")
				self.__results = res[4]

		except MySQLdb.Error as e:
			print(e)
			con.rollback()
		finally:
			con.close()

	def get_qualified(self):
		return self.__qualified_gene

	def get_illegal(self):
		return self.__illegal

	def update_results(self, results_json):
		try:
			con = MySQLdb.connect('localhost', 'haoping', 'a012345', 'YHMI_database')
			cursor = con.cursor()

			query = "UPDATE `{}` SET `results`='{}' WHERE `tempID` = '{}'".format(self.__temp_input_table, results_json, self.__tableID)
			cursor.execute(query)
			con.commit()
		except MySQLdb.Error as e:
			print(e)
			con.rollback()
		finally:
			con.close()

	def get_results(self):
		return json.loads(self.__results)
		

class YhmiEnrichmentTempTable(object):
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
				sqlCmd = 'INSERT INTO `{}` SELECT * FROM `{}` WHERE `Feature` IN (SELECT `Feature` FROM `const_comparison_feature` WHERE `Valid`)'.format(self.__temp_table + self.__tableID, self.__main_table)
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
			print("updateTable:", e)
			print(sqlCmd)

		tableDict = {}
		# {'H3_or_H4_Acetylation_mutant': [('`Data0_pro` en 1.0', 'pro_en', 'H3K4ac_set1D_on_WT_exp2', '1')]
		for r in res:
			TableID = "_"+r[3] if r[3] else ""
			for f in feature_ID[str(r[0])]:
				table_name = r[2]+TableID
				if table_name in tableDict:
					tableDict[table_name].append(("`Data{}_{}` {} {}".format(r[4], f[0], f[1], f[2]), f[0]+"_"+f[1], r[1], f[2]))
				else:
					tableDict[table_name] = [("`Data{}_{}` {} {}".format(r[4], f[0], f[1], f[2]), f[0]+"_"+f[1], r[1], f[2])]
		try:
			for table, condiction in tableDict.items():
				for c, t, feature, criteria in condiction:
					c = c.replace("en", '>=').replace('de', '<=')
					sqlCmd = "SELECT `ORF` FROM `yhmi_filter_{}` WHERE {}".format(table.lower(), c)
					# print(sqlCmd)
					cursor.execute(sqlCmd)
					update_gene = ",".join([r[0] for r in cursor.fetchall()])
					sqlCmd = "UPDATE `{}` SET `{}` = '{}',`{}_criteria`={} WHERE `Feature` = '{}'".format(
						self.__temp_table + self.__tableID, t, update_gene, t[:3], criteria, feature)
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

	def getData(self, FeatureID=None, histoneType=None, criteria=False):
		try:
			con = MySQLdb.connect(*self.__db)
			cursor = con.cursor()
			if FeatureID:
				sqlCmd = "SELECT * FROM `{}` WHERE `ID`='{}'".format(
							self.__temp_table + self.__tableID, FeatureID)
			elif criteria:
				temp_column = ['ID', 'Feature', 'Pro_en', 'Cds_en', 'HistoneType', 'Pro_criteria', 'Cds_criteria']
				sqlCmd = '''SELECT `{temp}`.`{}`, `{temp}`.`{}`, `{temp}`.`{}`, `{temp}`.`{}`, `{temp}`.`{}`, `{temp}`.`{}`, `{temp}`.`{}`, `const_comparison_feature`.`Feature_Criteria`
							FROM `{temp}`
							JOIN `const_comparison_feature`
							ON `const_comparison_feature`.`ID`=`{temp}`.`ID`
							WHERE `const_comparison_feature`.`Valid` = 1'''.format(
								*temp_column, temp=self.__temp_table+self.__tableID)
			else:
				temp_column = ['ID', 'Feature', 'Pro_en', 'Pro_de', 'Cds_en', 'Cds_de', 'HistoneType']
				sqlCmd = '''SELECT `{temp}`.`{}`,`{temp}`.`{}`,`{temp}`.`{}`,`{temp}`.`{}`,`{temp}`.`{}`,`{temp}`.`{}`,`{temp}`.`{}`,`const_comparison_feature`.`Paper`
							FROM `{temp}`
							JOIN `const_comparison_feature`
							ON `const_comparison_feature`.`ID`=`{temp}`.`ID`
							WHERE `const_comparison_feature`.`Valid` = 1'''.format(
								*temp_column, temp=self.__temp_table+self.__tableID)

			cursor.execute(sqlCmd)
			res = cursor.fetchall()
		except MySQLdb.Error as e:
			print(e)
		finally:
			con.close()

		if FeatureID:
			if histoneType:
				yield {'feature':res[0][1], 'genes':set(res[0][int(histoneType)+2].split(","))}
			else:
				yield {'feature':res[0][1], 'pro_en':res[0][2], 'pro_de':res[0][3], 'cds_en':res[0][4], 'cds_de':res[0][5]}
		elif criteria:
			for r in res:
				yield {'ID':r[0], 'feature':r[1], 'pro_en':r[2], 'cds_en':r[3], 'histoneType':r[4], 'pro_criteria':r[5], 'cds_criteria':r[6], 'feature_criteria':r[7]}
		else:
			for r in res:
				yield {'ID':r[0], 'feature':r[1], 'pro_en':r[2], 'pro_de':r[3], 'cds_en':r[4], 'cds_de':r[5], 'histoneType':r[6],'paper':r[7]}
		
class YhmiEnrichment(models.Model):
	ID = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	feature = models.CharField(db_column='Feature', primary_key=True, max_length=50)  # Field name made lowercase.
	pro_en = models.TextField(db_column='Pro_en', blank=True, null=True)  # Field name made lowercase.
	pro_de = models.TextField(db_column='Pro_de', blank=True, null=True)  # Field name made lowercase.
	cds_en = models.TextField(db_column='Cds_en', blank=True, null=True)  # Field name made lowercase.
	cds_de = models.TextField(db_column='Cds_de', blank=True, null=True)  # Field name made lowercase.
	histonetype = models.CharField(db_column='HistoneType', max_length=50)  # Field name made lowercase.

	def __str__(self):
		return self.feature
		
	class Meta:
		managed = False
		db_table = 'yhmi_enrichment'

class YhmiEnrichmentTf(models.Model):
	ID = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	feature = models.CharField(db_column='Feature', max_length=50)  # Field name made lowercase.
	pro = models.TextField(db_column='Pro', blank=True, null=True)  # Field name made lowercase.
	pro_len = models.IntegerField(db_column='Pro_len')  # Field name made lowercase.
	cds = models.TextField(db_column='Cds', blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'yhmi_enrichment_tf'

class ConstComparisonOrf(models.Model):
    inputgene = models.CharField(db_column='InputGene', primary_key=True, max_length=130)  # Field name made lowercase.
    orf = models.CharField(db_column='ORF', max_length=9, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'const_comparison_orf'

class ConstYeastName(models.Model):
    orf = models.CharField(db_column='ORF', primary_key=True, max_length=28)  # Field name made lowercase.
    standard = models.CharField(db_column='Standard', max_length=34, blank=True, null=True)  # Field name made lowercase.
    alias = models.CharField(db_column='Alias', max_length=130, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
    	return self.orf

    class Meta:
        managed = False
        db_table = 'const_yeast_name'


def histone_gene_info_server_side(histone_gene, **kwargs):
	ORDER_COLUMN_CHOICES = ['orf','standard','alias']

	draw = int(kwargs['draw'][0])
	length = int(kwargs['length'][0])
	start = int(kwargs['start'][0])
	search_value = kwargs['search[value]'][0]
	order_column = ORDER_COLUMN_CHOICES[int(kwargs['order[0][column]'][0])]
	order = kwargs['order[0][dir]'][0]

	if order == 'desc':
		order_column = '-' + order_column

	queryset = ConstYeastName.objects.filter(orf__in=histone_gene)
	total = queryset.count()

	if search_value:
		queryset = queryset.filter(
			Q(orf__icontains=search_value) |
			Q(standard__icontains=search_value) |
			Q(alias__icontains=search_value)
		)
	count = queryset.count()
	queryset = queryset.order_by(order_column).values_list()[start:start+length]
	data = {
		'draw':draw,
		'recordsTotal':total,
		'recordsFiltered':count,
		'data':list(queryset)
	}
	return data
