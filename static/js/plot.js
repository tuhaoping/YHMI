function barplot(ftype, graphtype) {
	var item = {'Promoter':{'name':[], 'fold':[], 'pvalue':[]}, 'CodingRegion':{'name':[], 'fold':[], 'pvalue':[]}};
	var fig_id = ftype + "_fig"
	var enrich_type = ['Enriched in Promoter', 'depleted in Promoter', 'Enriched in Coding Region', 'depleted in Coding Region', ''];
	var title, barcolor;

	// console.log(plot_data)
	if(ftype == 'H2A_Variant_and_H2B_Ubiquitination'){
		var item = {'name':[], 'fold':[], 'pvalue':[]};
		var plot_data = bar_data['H2A_Variant'];
		var fig_id = "H2A_Variant_fig"
		plot(plot_data, graphtype);
		
		var item = {'name':[], 'fold':[], 'pvalue':[]};
		var plot_data = bar_data['H2BK123_Ubiquitination'];
		var fig_id = "H2BK123_Ubiquitination_fig"
		plot(plot_data, graphtype);
	}
	else
		var plot_data = bar_data[ftype];
		plot(plot_data, graphtype);

	function plot(plot_data, graphtype){
		if(graphtype == 'fold'){
			plot_data.sort(function(a,b){return b[1]-a[1]})
			plot_data.forEach((e)=>{
				if(e[3]<2 || e[3]==4) histoneType = 'Promoter';
				else histoneType = 'CodingRegion';

				item[histoneType]['name'].push(e[0] + " " + enrich_type[Number(e[3])]);
				item[histoneType]['fold'].push(Math.log2(Number(e[1])));
				title = 'Fold enrichment (log2)';
				barcolor_promoter = '#66ffff';
				barcolor_cds = '#2679ff';
			});
		}
		else{
			plot_data.sort(function(a,b){return a[2]-b[2]})
			plot_data.forEach((e)=>{
				if(e[3]<2 || e[3]==4) histoneType = 'Promoter';
				else histoneType = 'CodingRegion';
				item[histoneType]['name'].push(e[0] + " " + enrich_type[Number(e[3])]);
				item[histoneType]['pvalue'].push(-Math.log10(e[2]));
				title = 'P-value (-log10)';
				barcolor_promoter = '#ffff8e';
				barcolor_cds = '#ffff00';
			});

		}

		var trace1 = {
			x:item['Promoter']['name'],
			y:item['Promoter'][graphtype],
			type: 'bar',
			name:'Promoter',
			marker:{
				color: barcolor_promoter,
				opacity: 0.7,
			}
		}
		var trace2 = {
			x:item['CodingRegion']['name'],
			y:item['CodingRegion'][graphtype],
			type: 'bar',
			name:'Coding Region',
			marker:{
				color: barcolor_cds,
				opacity: 0.7,
			}
		}

		var data = [trace1, trace2];


		var layout = {
			yaxis:{
				title: title,
			},
		}

		Plotly.newPlot(fig_id, data, layout, {displayModeBar: false});
	}
}



$(window).resize(function(){
	var ftype = $("#result .tab-content div.active.show").data('graph');

	if(ftype == 'H2A_Variant_and_H2B_Ubiquitination'){
          ftype = $("#result .tab-content div.active.show .graph_radio input[type='radio']:checked").eq(0).data('ftype');
          graphtype = $("#result .tab-content div.active.show .graph_radio input[type='radio']:checked").eq(0).data('graph');
          barplot(ftype, graphtype);
          ftype = $("#result .tab-content div.active.show .graph_radio input[type='radio']:checked").eq(1).data('ftype');
          graphtype = $("#result .tab-content div.active.show .graph_radio input[type='radio']:checked").eq(1).data('graph');
          barplot(ftype, graphtype);
        }
        else{
        	var graphtype = $("#result .tab-content div.active.show .graph_radio input[type='radio']:checked").data('graph');
        	barplot(ftype, graphtype);
        }

	// console.log('resize plot')
});