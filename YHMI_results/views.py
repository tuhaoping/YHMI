from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from YHMI_results.models import YhmiEnrichment, FilterResult, YhmiEnrichmentTf, YhmiEnrichmentTempTable, YhmiInputTempTable
from django.views.decorators.csrf import csrf_exempt

import copy
import json
import math
import scipy.stats

def showIntersect(request):
	input_gene = YhmiInputTempTable(request.POST['tableID'])
	enrich_db = YhmiEnrichmentTempTable(request.POST['tableID'])
	tlist = ['pro_en', 'pro_de', 'cds_en', 'cds_de']
	featureID, histoneType = request.POST['histone'][1:].split("_")
	# print(featureID, histoneType)
	# print("="*100)
	histone_data = list(enrich_db.getData(featureID))[0]
	# print(histone_data)
	histone_gene = set(histone_data[tlist[int(histoneType)]].split(','))
	all_gene = {gene:{} for gene in sorted(list(set(input_gene.get_qualified())|histone_gene))}
	# print(all_gene)
	for gene in all_gene.keys():
		# print(gene)
		# if gene in input_gene:
		all_gene[gene]['input'] = True if gene in input_gene.get_qualified() else False
		# if gene in histone_gene:
		all_gene[gene]['histone'] = True if gene in histone_gene else False

	# print("="*100)
	# print(histone_data['feature'])
	# print("test")
	# print(histone_data)
	# print(input_gene.get_qualified())
	render_dict = {
		 'all_gene': all_gene,
		 'input_length': len(input_gene.get_qualified()),
		 'histone_length': len(histone_gene),
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
		'inputGene':sorted(list(geneset)),
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
