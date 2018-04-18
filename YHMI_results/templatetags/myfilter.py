from django.template.defaulttags import register
import re
@register.filter
def now_type(count):
	tlist = ['Enriched in Promoter', 'Depleted in Promoter', 'Enriched in Coding Region', 'Depleted in Coding Region', '']
	return tlist[count]

@register.filter
def pvalue_type(pType):
	p = ["Over", "Under", '']
	return p[pType]

@register.filter
def calc_percent(n1, n2):
	return "{:0<.2f}%".format(n1/n2*100)

@register.filter
def format_calc_percent(n1, n2):
	return "{:06.2f}%".format(n1/n2*100)

@register.filter
def format_pvalue(pvalue):
	return "{:1.3E}".format(pvalue)

@register.filter
def format_enrichment(num):
	return "{:0<.3f}".format(num)

@register.filter
def remove_underline(s):
	return s.replace("_", " ")

@register.filter
def TF_name_transfer(s):
	return re.sub(r'(?<=_(25|37))C', '℃', s)

@register.filter
def TF_temperature(s):
	return s[-3:-1] + '℃'