from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from YHMI_results.models import YhmiEnrichment, FilterResult, YhmiEnrichmentTf, YhmiEnrichmentTempTable
from django.views.decorators.csrf import csrf_exempt

import copy
import json
import math
import scipy.stats

def showEnrich(request):
	if request.POST['composition']:
		yhmi_filter = list(filter(None, json.loads(request.POST['InputGene'])))
		geneset = set(FilterResult.filterGene(yhmi_filter, request.POST['composition']))
	else:
		geneset = set(filter(None, json.loads(request.POST['InputGene'])))
	

	if geneset:
		enrich_db = YhmiEnrichmentTempTable(request.POST['tableID'])
		data_tf = YhmiEnrichmentTf.objects.all()
		data = enrich_db.getData()

		S = len(geneset)
		enrich_value = []
		enrich_value_tf = []

		for i in data:
			gene = [set(i['pro_en'].split(',')), set(i['pro_de'].split(',')), set(i['cds_en'].split(',')), set(i['cds_de'].split(','))]
			
			for g,t in zip(gene, [0, 1, 2, 3]):
				T = len(g & geneset)
				G = len(g)
				enrich_value.append({
					'feature':i['feature'],
					'enrich_type':t,
					'intersectOfgene':(T, S, G),
					'paper':i['paper'].replace('_', " ")
					})
		

		for i in data_tf:
			g = set(i.pro.split(','))
			T = len(g & geneset)
			G = len(g)
			enrich_value_tf.append({'feature':i.feature, 'enrich_type':4, 'intersectOfgene':(T, S, G), 'paper':"Venters 2011"})
		
		enrich_value = Hypergeometric_pvalue(enrich_value, enrich_value_tf)
		enrich_value = Correction(enrich_value, request.POST['corrected'], float(request.POST['cutoff']))

	else:
		enrich_value = []
		
	render_dict = {
		'inputGene':sorted(list(geneset)),
		'enrich_value': enrich_value,
		'corrected': request.POST['corrected'],
		'cutoff': request.POST['cutoff'],
	}
	return render(request, 'enrich_template.html', render_dict)


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
	elif method == 'drop':
		enrich_db.defaultTable()

	return HttpResponse(status=200)


def Hypergeometric_pvalue(temp_enrich_over, enrich_value_tf):
	'''calculate every pvalue of each feature'''
	# T = 'intersects'         #交集數         1
	# S = 'input_gene'         #輸入 genes數   18
	# G = 'feature_gene'       #genes 樣本數   1117
	# F = 'total_feature_gene'         #總 genes數     6572

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

	temp_enrich = {'histone':temp_enrich_over + temp_enrich_under, 'TF':enrich_value_tf}

	return temp_enrich


def Correction(enrich_value, method='1', cutoff=2.0):
	'''
	Correction P-value
	method:'1' Bonferroni, '2' FDR
	'''

	if method == '1':
		for ftype, fdata in enrich_value.items():
			length = len(fdata)
			print(ftype, length)
			temp = []
			for i,data in enumerate(fdata):
				data['pvalue'][0] *= length
				if data['pvalue'][0] < 10**(-cutoff):
					temp.append(data)
			enrich_value[ftype] = temp

	elif method == '2':
		enrich_value.sort(key=lambda x:x['pvalue'][0])
		pass_flag = True

		for i,t in reversed(list(enumerate(enrich_value, 1))):
			enrich_value[i-1]['pvalue'][0] = t['pvalue'][0] = t['pvalue'][0]*length/i
			if pass_flag and (t['pvalue'][0] < 10**(-cutoff)):
				pass_range = i
				pass_flag = False

	return enrich_value