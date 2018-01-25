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
		let jdata
		let composition

		if($("#switch").prop('checked')){
			jdata = $("tr.tr-feature input[type=checkbox]:checked").map(function(){
						id = $(this).closest('tr').prop('id');
						textbox = $(this).siblings('input');
						fClass = $(this).siblings('span').text();
						console.log(id + "_" + fClass + "_" + textbox.val());
						return id + "_" + fClass + "_" + textbox.val();
					});
			jdata = JSON.stringify(jdata.get());
			composition = $("#Composition-select").val();
		}
		else{
			jdata = JSON.stringify($('#inputTextArea').val().split("\n"));
			composition = null;
		}

		$.ajax({
			url: rootURL + '/result',
			type: 'POST',
			data: {
				'tableID':tableID,
				'InputGene': jdata,
				'composition': composition,
				'corrected': $("#div-corrected input[name=corrected]:checked").val(),
				'cutoff': $("#div-corrected input[type=text]:enabled").val(),
			},
			success:function(d){
				$(".container-fluid.container-input").hide();
				$(".container-fluid.container-results").show();
				$("#leftAccordion .nav-link").removeClass("active");
				$("#leftAccordion .nav-link").eq(2).addClass("active");

				$("#result").html(d);
				$("#enrich_table").DataTable({
		    			// 'order': [[3, "asc"]]
		    			'order': [[3, "asc"], [0, 'desc']]
		    		});

				$("#input_gene_table").DataTable();
				$("#enrich_table_wrapper").css('padding', '10');
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

	$("#btn-refresh").click(function(){
		$.ajax({
			url:rootURL + '/setting/default'
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