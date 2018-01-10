from django.template.defaulttags import register

@register.filter
def now_type(count):
	tlist = ['Enriched in Promoter', 'depleted in Promoter', 'Enriched in Coding Region', 'depleted in Coding Region', ]
	return tlist[count]

