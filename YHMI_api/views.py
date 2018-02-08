from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from YHMI_results.models import YhmiEnrichment, FilterResult, YhmiEnrichmentTf, YhmiEnrichmentTempTable
from django.views.decorators.csrf import csrf_exempt

import copy
import json
import math
import scipy.stats

@csrf_exempt
def enrichJSON(request):
	'''
	http://cosbi4.ee.ncku.edu.tw/api/enrich
	request.POST

	argument:
	[necessary]
	InputGene: list with json
	corrected: 1.Bonferroni, 2.FDR
	cutoff: correction standard

	[option]
	setting_data: json ['fs{id}_(pro|cds)_(en|de)_value', ...]
	'''
	if ('InputGene' not in request.POST) or ('corrected' not in request.POST) or ('cutoff' not in request.POST):
		return HttpResponseBadRequest

	geneset = set(filter(None, json.loads(request.POST['InputGene'])))
	if geneset:
		enrich_db = YhmiEnrichmentTempTable()
		if 'setting_data' in request.POST:
			enrich_db.updateTable(request.POST['setting_data'])

		data = enrich_db.getData()
		# data = YhmiEnrichment.objects.all()
		data_tf = YhmiEnrichmentTf.objects.all()
		S = len(geneset)
		enrich_value = []
		enrich_value_tf = []

		for i in data:
			gene = [set(i['pro_en'].split(',')), set(i['pro_de'].split(',')), set(i['cds_en'].split(',')), set(i['cds_de'].split(','))]
			
			for g,t in zip(gene, [0, 1, 2, 3]):
				T = len(g & geneset)
				G = len(g)
				if request.POST['corrected'] == '1':
					try:
						enrich_value.append({
							'feature':i['feature'],
							'enrich_type':t, 
							'intersectOfgene':[T, S, G, 6572],
							'pvalue':Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff'])),
							'o_pvalue':Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))[0]/510
						})
					except:
						pass
				else:
					enrich_value.append([i['feature'], t, [T, S, G]])
		

		for i in data_tf:
			g = set(i.pro.split(','))
			# gene = [set(i.pro_en.split(',')), set(i.pro_de.split(',')), set(i.cod_en.split(',')), set(i.cod_de.split(','))]
			T = len(g & geneset)
			G = len(g)
			if request.POST['corrected'] == '1':
				try:
					enrich_value_tf.append({
						'feature':i.feature,
						'enrich_type':4, 
						'intersectOfgene':[T, S, G, 6572],
						'pvalue':Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff'])),
						'o_pvalue':Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))[0]/510
					})
				except:
					pass
				
			else:
				enrich_value_tf.append([i.feature, 4, [T, S, G]])
		
		# enrich_value.extend(enrich_value_tf)
		if request.POST['corrected'] == '1':
			enrich_value = [e for e in enrich_value if e['pvalue']]
		elif request.POST['corrected'] == '2':
			enrich_value = [{
				'feature':e[0],
				'enrich_type':e[1], 
				'intersectOfgene':e[2] + [6572],
				'pvalue':e[3],
				'o_pvalue':e[4]
			} for e in FDR_corrected(enrich_value, enrich_value_tf, cutoff=float(request.POST['cutoff']))]

		enrich_db.dropTable()
	else:
		print("empty gene input")
		enrich_value = []

	return JsonResponse(enrich_value,safe=False)
