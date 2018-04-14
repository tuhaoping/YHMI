from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from YHMI_results.models import (
	YhmiEnrichment, FilterResult,
	YhmiEnrichmentTf, YhmiEnrichmentTempTable,
	YhmiInputTempTable, ConstYeastName,
	ConstComparisonOrf
	)
from django.views.decorators.csrf import csrf_exempt

import csv
import copy
import json
import math
import scipy.stats

def showIntersect(request):
	if request.method == "POST":
		featureID, histoneType = request.POST['histone'].split("_")
		tableID = request.POST['tableID']
	
	else:
		featureID, histoneType = request.GET['histone'].split("_")
		tableID = request.GET['tableID']

	input_gene = YhmiInputTempTable(tableID)
	
	if histoneType != '4':
		enrich_db = YhmiEnrichmentTempTable(tableID)
		histone_data = list(enrich_db.getData(featureID, histoneType))[0]
	else:
		histone_data = YhmiEnrichmentTf.objects.get(pk=featureID)
		histone_data = {'feature':histone_data.feature, 'genes':set(histone_data.pro.split(","))}

	all_gene = [{'input':gene} for gene in sorted(input_gene.get_qualified())]
	intersect_length = len(set(input_gene.get_qualified())&histone_data['genes'])


	for i,gene in enumerate(all_gene):
		all_gene[i]['intersect'] = True if gene['input'].strip() in histone_data['genes'] else False

	all_gene.sort(key=lambda x: (~x['intersect'], x['input']))

	if request.method == "GET":
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(histone_data['feature'])

		writer = csv.writer(response)
		writer.writerow(['Input', 'Intersect of Histone Modification'])
		for gene in all_gene:
			writer.writerow([gene['input'], "V" if gene['intersect'] else "X"])

		return response

	else:
		render_dict = {
			 'all_gene': all_gene,
			 'input_length': len(input_gene.get_qualified()),
			 'intersect_length': intersect_length,
			 'histone_name': histone_data['feature']
		}
		return render(request, 'intersect_template.html', render_dict)

def showEnrich(request):
	input_gene = YhmiInputTempTable(request.POST['tableID'], json.loads(request.POST['InputGene']))

	if 'composition' in request.POST:
		yhmi_filter = list(filter(None, json.loads(request.POST['InputGene'])))
		geneset = set(FilterResult.filterGene(yhmi_filter, request.POST['composition']))
	else:
		geneset = set(filter(None, input_gene.get_qualified()))


	if geneset:
		enrich_db = YhmiEnrichmentTempTable(request.POST['tableID'])
		data_tf = YhmiEnrichmentTf.objects.all()
		data = enrich_db.getData()

		S = len(geneset)
		enrich_value = {'Acetylation':[], 'Methylation':[], 'H2A_Variant_and_H2B_Ubiquitination':[]}
		enrich_value_others = {'H2A_Variant':[], 'H2BK123_Ubiquitination':[]}
		enrich_value_tf = []

		for i in data:
			gene = [set(i['pro_en'].split(',')), set(i['pro_de'].split(',')), set(i['cds_en'].split(',')), set(i['cds_de'].split(','))]

			for g,t in zip(gene, [0, 1, 2, 3]):
				T = len(g & geneset)
				G = len(g)
				# print(i['ID'])。
				try:
					enrich_value[i['histoneType']].append({
						'enrichID':i["ID"],
						'feature':i['feature'],
						'enrich_type':t,
						'intersectOfgene':(T, S, G),
						'paper':i['paper'].replace('_', " "),
						'fold':T/S/G*6572,
						})
				except:
					enrich_value_others[i['histoneType'].replace(" ",'_')].append({
						'enrichID':i["ID"],
						'feature':i['feature'],
						'enrich_type':t,
						'intersectOfgene':(T, S, G),
						'paper':i['paper'].replace('_', " "),
						'fold':T/S/G*6572,
						})

		for i in data_tf:
			g = set(i.pro.split(','))
			T = len(g & geneset)
			G = len(g)
			enrich_value_tf.append({
				'enrichID':i.ID,
				'feature':i.feature,
				'enrich_type':4,
				'intersectOfgene':(T, S, G),
				'paper':"Venters 2011",
				'fold':T/S/G*6572
				})

		enrich_value = Hypergeometric_pvalue(enrich_value, enrich_value_tf)
		enrich_value_others = Hypergeometric_pvalue(enrich_value_others)
		temp_enrich_value = Correction(enrich_value, request.POST['corrected'], float(request.POST['cutoff']))
		temp_enrich_value_others = Correction(enrich_value_others, request.POST['corrected'], float(request.POST['cutoff']))

		data_fold = {}
		for ftype, data in temp_enrich_value.items():
			if ftype != 'TF':
				enrich_value[ftype] = {}
				enrich_value[ftype]['Promoter'] = list(filter(lambda x: x if x['enrich_type'] <= 1 else None, data))
				enrich_value[ftype]['Coding_Region'] = list(filter(lambda x: x if x['enrich_type'] >= 2 else None, data))
			else:
				enrich_value[ftype] = {}
				enrich_value[ftype]['Promoter'] = data
			data_fold[ftype] = list(
				map(lambda x:[x['feature'], x['fold'], x['pvalue'][0], x['enrich_type']], data))

		for ftype, data in temp_enrich_value_others.items():
			enrich_value_others[ftype] = {}
			enrich_value_others[ftype]['Promoter'] = list(filter(lambda x: x if x['enrich_type'] <= 1 else None, data))
			enrich_value_others[ftype]['Coding_Region'] = list(filter(lambda x: x if x['enrich_type'] >= 2 else None, data))
		
			data_fold[ftype] = list(
				map(lambda x:[x['feature'], x['fold'], x['pvalue'][0], x['enrich_type']], data))

	else:
		enrich_value_others = []
		enrich_value = []
	render_dict = {
		'inputGene_length':len(list(geneset)),
		'enrich_value': enrich_value,
		'enrich_value_others': enrich_value_others,
		'corrected': request.POST['corrected'],
		'cutoff': request.POST['cutoff'],
	}

	template = render_to_string('enrich_template.html', render_dict)
	return JsonResponse({"template":template, 'data':data_fold})


def customSetting(request, method):
	if 'tableID' in request.POST:
		enrich_db = YhmiEnrichmentTempTable(request.POST['tableID'])
	else:
		enrich_db = YhmiEnrichmentTempTable()

	if method == 'init':
		return JsonResponse({'tableID':enrich_db.tableID})

	elif method == 'update':
		enrich_db.updateTable(request.POST['setting_data'])

	elif method == 'drop':
		enrich_db.dropTable()

	elif method == 'default':
		enrich_db.defaultTable()

	return HttpResponse(status=200)


def userSpecific(request):
	geneset = json.loads(request.POST['InputGene'])
	gene_name = set(ConstComparisonOrf.objects.filter(inputgene__in=geneset).values_list('orf', flat=True))
	gene_name = ConstYeastName.objects.filter(orf__in=gene_name)
	enrich_db = YhmiEnrichmentTempTable(request.POST['tableID'])
	data = enrich_db.getData(criteria=True)
	custom_data = []
	for i in data:
		custom_data.append({
			'enrichID':i["ID"],
			'feature':i['feature'],
			'pro_len':i['pro_en'].count(',')+1,
			'cds_len':i['cds_en'].count(',')+1,
			'pro_criteria':i['pro_criteria'],
			'cds_criteria':i['cds_criteria'],
		})
	# print(request.POST['tableID'])
	# print(custom_data)
	render_dict = {
		'inputGene':gene_name,
		'inputGene_length':len(geneset),
		'corrected': request.POST['corrected'],
		'cutoff': request.POST['cutoff'],
		'custom_data':custom_data,
	}
	return render(request, 'user_specification.html', render_dict)

def Hypergeometric_pvalue(temp_enrich, enrich_value_tf=None):
	'''calculate every pvalue of each feature'''
	# T = 'intersects'         #交集數         1
	# S = 'input_gene'         #輸入 genes數   18
	# G = 'feature_gene'       #genes 樣本數   1117
	# F = 'total_feature_gene'         #總 genes數     6572

	temp = {}
	for t,temp_enrich_over in temp_enrich.items():
		temp_enrich_under = copy.deepcopy(temp_enrich_over)

		for i,data in enumerate(temp_enrich_over):
			T, S, G = data['intersectOfgene']
			F = 6572
			S_T = S-T
			G_T = G-T
			F_G_S_T = F-G-S+T

			if F_G_S_T <= 0:
				temp_enrich_over[i]['pvalue'] = (math.inf,)
				temp_enrich_under[i]['pvalue'] = (math.inf,)
			else:
				temp_enrich_over[i]['pvalue'] = [scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'greater')[1],0]
				temp_enrich_under[i]['pvalue'] = [scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'less')[1],1]
		temp[t] = temp_enrich_over + temp_enrich_under

	if enrich_value_tf:
		for i,data in enumerate(enrich_value_tf):
			T, S, G = data['intersectOfgene']
			F = 6572
			S_T = S-T
			G_T = G-T
			F_G_S_T = F-G-S+T

			if F_G_S_T <= 0:
				enrich_value_tf[i]['pvalue'] = (math.inf,)
			else:
				enrich_value_tf[i]['pvalue'] = [scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'greater')[1],2]

		temp['TF'] = enrich_value_tf
	# print(temp.keys())

	return temp


def Correction(enrich_value, method='1', cutoff=2.0):
	'''
	Correction P-value
	method:'1' Bonferroni, '2' FDR
	'''
	if method == '1':
		for ftype, fdata in enrich_value.items():
			length = len(fdata)
			# print(ftype, length)
			temp = []
			for i,data in enumerate(fdata):
				data['pvalue'][0] *= length
				if data['pvalue'][0] < 10**(-cutoff):
					temp.append(data)
			enrich_value[ftype] = temp

	elif method == '2':
		for ftype, fdata in enrich_value.items():
			fdata.sort(key=lambda x:x['pvalue'][0])
			length = len(fdata)
			pass_flag = True

			for i,t in reversed(list(enumerate(fdata, 1))):
				fdata[i-1]['pvalue'][0] = t['pvalue'][0] = t['pvalue'][0]*length/i
				if pass_flag and (t['pvalue'][0] < 10**(-cutoff)):
					pass_range = i
					pass_flag = False

			enrich_value[ftype] = fdata[:pass_range]

	return enrich_value
