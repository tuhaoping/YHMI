function barplot(ftype, graphtype) {
	var item = {'name':[], 'fold':[], 'pvalue':[]};
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
				item['name'].push(e[0] + " " + enrich_type[Number(e[3])]);
				item['fold'].push(Math.log2(Number(e[1])));
				title = 'Fold enrichment (log2)';
				barcolor = '#66ffff';
			});
		}
		else{
			plot_data.sort(function(a,b){return a[2]-b[2]})
			plot_data.forEach((e)=>{
				item['name'].push(e[0] + " " + enrich_type[Number(e[3])]);
				item['pvalue'].push(-Math.log10(e[2]));
				title = 'P-value (-log10)';
				barcolor = '#ffff66';
			});

		}

		var data = [{
			x:item['name'],
			y:item[graphtype],
			type: 'bar',
			marker:{
				color: barcolor,
				opacity: 0.7,
			}
		}];


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