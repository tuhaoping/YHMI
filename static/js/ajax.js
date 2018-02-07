function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
	// crossDomain: false,
	timeout:20000,
	beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }

});

var tableID = '';
// console.log(tableID)
var rootURL = '';
var setting_data = [];
var custom_save = false;

$(document).ready(function(){
	// $.ajax({
	// 	url:"/result/init/",
	// 	type:"GET",
	// 	success:function(d){
	// 		console.log(d);
	// 	}
	// });

	$("#btn-send").click(function(){
		let jdata_gene
		let jdata_setting
		// let composition

		if($("#switch").prop('checked')){
			jdata_setting = $("tr.tr-custom-setting input[type=checkbox]:checked").map(function(){
						id = $(this).closest('tr').prop('id');
						textbox = $(this).siblings('input');
						fClass = $(this).siblings('span').text();
						console.log(id + "_" + fClass + "_" + textbox.val());
						return id + "_" + fClass + "_" + textbox.val();
					});
			jdata_setting = JSON.stringify(jdata_setting.get());
			// composition = $("#Composition-select").val();
		}

		jdata_gene = JSON.stringify($('#inputTextArea').val().split("\n"));

		$.ajax({
			url: rootURL + '/result',
			type: 'POST',
			data: {
				'tableID':tableID,
				'InputGene': jdata_gene,
				// 'composition': composition,
				'corrected': $("#div-corrected input[name=corrected]:checked").val(),
				'cutoff': $("#div-corrected input[type=text]:enabled").val(),
			},
			success:function(d){
				$(".container-fluid.container-input").hide();
				$(".container-fluid.container-results").show();
				$("#leftAccordion .nav-link").removeClass("active");
				$("#leftAccordion .nav-link").eq(2).addClass("active");

				$("#result").html(d);
				$("#Acetylation_enrich_table, \
				   #Methylation_enrich_table, \
				   #H2A_Variant_enrich_table, \
				   #H2BK123_Ubiquitination_enrich_table").DataTable({
		    			'order': [[4, "asc"], [0, 'asc']],
		    		});
				$("#TF_enrich_table").DataTable({
		    			'order': [[4, "asc"], [0, 'asc']],
		    		});

				$("#input_gene_table").DataTable();
				// $("#Acetylation_enrich_table_wrapper, #Methylation_enrich_table_wrapper, #others_enrich_table_wrapper, #TF_enrich_table_wrapper").css('padding', '10');
			}
		});
	});

});



$(document).ready(function(){
	$.ajax({
		url:rootURL + '/setting/init',
		type: 'GET',
		dataType: 'json',

		success:function(d){
			tableID = d['tableID'];
		}
	});

	$("tr.tr-custom-setting input[type=text]").change(function(){

		fClass = $(this).siblings('span').text();
		value = parseFloat($(this).val());
		if (/^-?[0-9]+(.[0-9]*)?$/.test($(this).val()) && value){
			$(this).data('prevalue', value);
			$(this).val(value);
			let id = $(this).closest('tr').prop('id');
			let setting_data = id + "_" + fClass + "_" + value;
			$.ajax({
				url:rootURL + '/setting/update',
				type:'POST',
				data: {
					'tableID':tableID,
					'setting_data': setting_data,
				}

			});
		}
		else{
			console.log('type err')
			$(this).val($(this).data('prevalue'));
		}
		// console.log($(this).defaultValue);
	});

	$("#btn-save-custom").click(function(){
		// let setting_data;
		setting_data = $("tr.tr-custom-setting input[type=checkbox]:checked").map(function(){
					id = $(this).closest('tr').prop('id');
					textbox = $(this).siblings('input');
					fClass = $(this).siblings('span').text();
					console.log(id + "_" + fClass + "_" + textbox.val());
					return id + "_" + fClass + "_" + textbox.val();
				}).get();
		console.log(setting_data);
		$.ajax({
			url:rootURL + '/setting/update',
			type: 'POST',
			data: {
				'tableID':tableID,
				'setting_data': JSON.stringify(setting_data),
			}

		});
		custom_save = true
	});

	$("#btn-reset").click(function(){
		$.ajax({
			url:rootURL + '/setting/default',
			type:"POST",
			data:{'tableID':tableID,}
		});
	});
});

window.onbeforeunload = function() {
	// console.log("leave!");
	$.ajax({
		async:false,
		url:rootURL + "/setting/drop",
		type:"POST",
		data:{'tableID':tableID,}
	});
};