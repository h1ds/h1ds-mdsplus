function formatDataForPlots(data) {
    // If we have min and max signals, then we fill the area between them.
    if (($.inArray("min", data.labels) > -1) && ($.inArray("max", data.labels) > -1) && (data.labels.length == 2)) {
	var d = {"signalmin":{"data": Array(data.data[0].length)},
		 "signalmax":{"data": Array(data.data[1].length)}};

	for( i=0; i < d.signalmin.data.length; i++){
            d.signalmin.data[i]=[data.dim[i],data.data[0][i]];
            d.signalmax.data[i]=[data.dim[i],data.data[1][i]];
	}
	var dataset = [{id: 'sigmin', data:d.signalmin.data, lines:{show:true, lineWidth:0.3, fill:false, shadowSize:0}, color:"rgba(50,50,255,0.5)"},
		       {id: 'sigmax', data:d.signalmax.data, lines:{show:true, lineWidth:0.3, fill:0.5, shadowSize:0}, color:"rgba(50,50,255,0.5)", fillBetween: 'sigmin'}];
	return dataset;	
    }
    
    else {
	var d = Array(data.data.length);
	for( i=0; i < d.length; i++){
            d[i]=[data.dim[i],data.data[i]];
	}
	var dataset = [{data:d, color:"rgb(50,50,255)"}];
	return dataset;
    }
} // end formatDataForPlots

function plotSignals() {
    // TODO: there is a neater way (though perhaps not any quicker) to manipulate URL query strings...
    if (window.location.search.length) {
	var query_join_char = '&';
    } else {
	var query_join_char = '?';
    }
    var new_query = window.location.search + query_join_char + 'format=json&f999_name=resample_minmax&f999_arg1=600';
    
    $.get(
	new_query,
	function (data) {
	    var dataset = formatDataForPlots(data);
	    var options = {selection:{mode:"x"}};
	    var sigplot = $.plot($("#signal-placeholder"),  dataset, options  );
	    var overviewplot = $.plot($("#signal-overview"),  dataset , options  );
	    
	    $("#signal-placeholder").bind("plotselected", function (event, ranges) {
		// do the zooming
		var new_query = window.location.search + query_join_char + 'format=json&f980_name=dim_range&f980_arg1='+ranges.xaxis.from+'&f980_arg2='+ranges.xaxis.to+'&f990_name=resample_minmax&f990_arg1=600';
		$.get(new_query, function(newdata) {
		    var new_d = formatDataForPlots(newdata);
		    
		    sigplot = $.plot($("#signal-placeholder"), new_d, options);
		    
		});
		
		// don't fire event on the overview to prevent eternal loop
		overviewplot.setSelection(ranges, true);
	    });
	    
	    $("#signal-overview").bind("plotselected", function (event, ranges) {
		sigplot.setSelection(ranges);
	    });
	    
	    
	},
	'json'
    );
}


$(document).ready(function() {
    // Only plot signals if there is a signal placeholder
    if ($("#signal-placeholder").length) {
	data = plotSignals();
    }
});
