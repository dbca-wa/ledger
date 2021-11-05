var ledger_payments = {
     var: {
	'current_invoice_group_id': '',
	'current_invoice_no': '',
	'current_booking_reference': '',
        'csrf_token': '',
        'payment_info_url' : '/ledger/payments/api/ledger/payments-info',
        'payment_info': []
     },
     load_payment_info: function() {
	 data = {}
         $.ajax({
             url: ledger_payments.var.payment_info_url+"?invoice_group_id="+ledger_payments.var.current_invoice_group_id+"&invoice_no="+ledger_payments.var.current_invoice_no+"&booking_reference="+ledger_payments.var.current_booking_reference,
             method: "GET",
             headers: {'X-CSRFToken' : ledger_payments.var.csrf_token },
             //data: JSON.stringify({'payload': data,}),
             contentType: "application/json",
             success: function(data) {
		        var orderdata = "";
		        var bpointdata = "";
                        if (data.data.order.length > 0) {
                             for (let i = 0; i < data.data.order.length; i++) {
                                    var line_price_incl_tax_color = '#bb2d3b';
				    if (data.data.order[i].line_price_incl_tax > 0) {
					 line_price_incl_tax_color = '#157347';				         	   
			            }

				    orderdata+= "<tr><td>"+data.data.order[i].order_number+"</td><td>"+data.data.order[i].title+"</td><td>"+data.data.order[i].oracle_code+"</td><td style='background-color: "+line_price_incl_tax_color+"; color: #FFFFFF;'>$"+data.data.order[i].line_price_incl_tax+"</td><td>$"+data.data.order[i].rolling_total+"</td><td>"+data.data.order[i].order_date+"</td></tr>";
                                    console.log(data.data.order[i]); 
			     }

			     for (let i = 0; i < data.data.bpoint.length; i++) {
				     
                                     bpointdata+= "<tr><td>"+data.data.bpoint[i].txnnumber+"</td><td>"+data.data.bpoint[i].crn1+"</td><td>"+data.data.bpoint[i].action+"</td><td>$"+data.data.bpoint[i].amount+"</td><td>"+data.data.bpoint[i].processed+"</td></tr>";
				     console.log(data.data.bpoint[i]);

			     }

		        }

		      $('#order_list').html(orderdata);
		      $('#bpoint_tbody').html(bpointdata);
		      $('#total_payment_gateway').html('$&nbsp;'+data.data.total_gateway_amount);
		      $('#total_unallocated').html('$&nbsp;'+data.data.total_unallocated);
                      refund_booking.var.bpoint_trans_totals = data.data.bpoint;
		      refund_booking.var.unique_oracle_code_on_booking = data.data.oracle_code_totals; 
		      refund_booking.var.booking_reference = data.data.booking_reference;
		      refund_booking.var.booking_reference_linked = data.data.booking_reference_linked;
		      refund_booking.re_init();
		      $('#LoadingPopup').modal('hide');
		      // refund_booking.init();
		      console.log(data);
             },
             error: function(errMsg) {
		     $('#LoadingPopup').modal('hide');
             }
         });



     },
 


     init: function() {
       ledger_payments.load_payment_info();

     }
}
