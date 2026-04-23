var take_payment =  {
     var: { 
          row_id: 0,
          total_money: parseFloat('0.00'),
          booking_id: 0,
          newest_booking_id: 0,
          bpoint_trans_totals: {},
          cash_trans_totals: {},
          cash_on_invoices: [],
          invoices_data: [],
          oracle_code_refund_allocation_pool: '',
          api_url: '',
          cash_refund_url: '',
          cash_payment_url: '',
          booking_reference: '',
          booking_reference_linked: '',
          csrf_token: '',
          invoice_group_id: '',
          oracle_code_tax_status: {}
     }, 
     money_add_row: function() {
          take_payment.var.row_id = take_payment.var.row_id + 1;
          var html = "<tr id='money_row"+take_payment.var.row_id+"' >";
          html += "<td><span id='oracle-error"+take_payment.var.row_id+"'><input style='width: 200px;' class='form-control input-sm' type='text' id='to-money-oracle-code"+take_payment.var.row_id+"' onblur='take_payment.input_oracle_code_change(this.id)' ></span></td>";
          html += "<td><input style='width: 100%' type='text' class='form-control input-sm' id='to-money-line-text"+take_payment.var.row_id+"'></td>";
          html += "<td><div style='display:flex'><span class='money_sign'  style='padding-top:6px;'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='take_payment.money_update(this);' id='to-money-line-tax"+take_payment.var.row_id+"' disabled=true></div></td>";
          html += "<td><div style='display:flex'><span class='money_sign'  style='padding-top:6px;'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='take_payment.money_update(this);' id='to-money-line-amount"+take_payment.var.row_id+"'></div></td>";
          html += "<td><button type='button' class='btn btn-danger' onclick='take_payment.remove_row("+'"money_row'+take_payment.var.row_id+'"'+")' ><i class='bi bi-x-lg'></i></button></td>";
          html += "</tr>";
          $("#money-booking tbody").append(html);
     },
     remove_row: function(row_id) {
          $('#'+row_id).remove();
          take_payment.total_money();
     },
     total_money: function() {
          take_payment.var.total_money = parseFloat('0.00');
          $('#total_money').html('$'+take_payment.format_money(take_payment.var.total_money));
          $("#money-booking").find('input').each(function() {
               if (this.type == 'number') {
                    if (this.value > 0 ) { 
               } else {
                         this.value = '0.00'; 
                    }
                    if (this.id.substring(0,20) == 'to-money-line-amount') {
                         take_payment.var.total_money = take_payment.var.total_money + parseFloat(this.value);
                    }
                    $('#total_money').html('$'+take_payment.format_money(take_payment.var.total_money));
               }
          });
     },
     format_money: function(total, comma) {
          if (comma == null) { 
               comma = true;
          }
          if (total == null) {
               total = '0.00';
   	     }
          var neg = false;
          if(total < 0) {
               neg = true;
               total = Math.abs(total);
          }
          if (comma == true) { 
               return (neg ? "-" : '') + parseFloat(total, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString();
          } else {
               return (neg ? "-" : '') + parseFloat(total, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1").toString();
   	     } 
     },
     money_update: function(item) {
          var rowid_val;
          var gst_value = 0.00;
          if (item.id.substring(0,20) == 'to-money-line-amount') {
               rowid_val = item.id.replace('to-money-line-amount','')
          
               console.log(item.value);
               var oracle_code_value = $('#to-money-oracle-code'+rowid_val).val();                    

               if (take_payment.var.oracle_code_tax_status.hasOwnProperty(oracle_code_value) == true) {
                    if (take_payment.var.oracle_code_tax_status[oracle_code_value] == 'tax_exempt') {                                    
                         gst_value = 0.00;
                    } else {
                         gst_value = item.value / 11;
                    }
               } else {

                    if (oracle_code_value.indexOf('EXEMPT') !== -1) {
                         gst_value = 0.00;
                    } else {
                         gst_value = item.value / 11;
                    }
               }
               
               $('#to-money-line-tax'+rowid_val).val(gst_value.toFixed(2));  
          }    
 
          item.value = take_payment.format_money(item.value, false);
          take_payment.total_money();

          var unallocated_pool_refund = $('#unallocated_pool_refund').val();
          if (parseFloat(unallocated_pool_refund) > parseFloat(take_payment.var.booking_allocation_pool)) {
               $('.tooltiptext').show();
          } else {
               $('.tooltiptext').hide();
          }
   	},

     input_oracle_code_change: function(element_id) {          
          var item = $('#'+element_id); 
          console.log(item.val());         
          var code_found = take_payment.check_oracle_code(item.val()); 
          console.log(code_found);
          if (code_found == true) {   
               $('#'+element_id).css('border','');
               console.log(element_id);
               if (element_id.substring(0,22) == 'from-money-oracle-code') {
                    rowid_val = element_id.replace('from-money-oracle-code','');             
                    var amount_item = document.getElementById('from-money-line-amount'+rowid_val);
                    take_payment.money_update(amount_item);
               }
               if (element_id.substring(0,20) == 'to-money-oracle-code') {
                    
                    rowid_val = element_id.replace('to-money-oracle-code','');             
                    var amount_item = document.getElementById('to-money-line-amount'+rowid_val);
                    
                    take_payment.money_update(amount_item);
               }               
               
          } else { 
               $('#'+element_id).css('border','2px solid red');
               $('#'+element_id).css('border-radius','4px');
          }
     },
     check_oracle_code: function(oracle_code) {
          var found = false; 
          $.ajax({
               url: '/ledger/payments/api/ledger/oracle-codes-lookup?oracle_code='+oracle_code,
          data: {
               format: 'json'
          },
          async: false,
          error: function() {
               $('#info').html('<p>An error has occurred</p>');
          },
          dataType: 'json',
          success: function(data) {
               found = data.found;
               },
               type: 'GET'
          });
          return found;
     },
	re_init: function() {
          $('#money-booking tbody').html("");
          take_payment.money_add_row();
          take_payment.total_money();

          $("#take-payment").show();
          $("#take-payment-wait").hide();
	},
     init: function() {
          console.log('Take Payment Loaded');
          $('#money-booking-button').on("click", function() {
               take_payment.money_add_row();
          });
          $('.close').on("click", function() {
          $('.modal-backdrop').hide();
          $('#notification-box').hide();
     });

     $("#settlement_override").click(function() {
          var settlement_override = $('#settlement_override').prop('checked');
          if (settlement_override == true) {
               $('#div_settlement_date').show();
          } else {
               $('#div_settlement_date').hide();
          }
     });
     $('#okBtn').on("click", function() {
          $('.modal-backdrop').hide();
          $('#notification-box').hide();
     });
     $('#success-refund').on("click", function() {
          $('.modal-backdrop').hide();
          $('#notification-box-success').hide();
          window.location.href  = window.location.href;
     });

                // CREATE CASH RECORD
		$('#record-payment').on("click", function() {
                    var notification_message = "";
                    var newcashlineamount1 = $('#new-cash-line-amount1').val();   
                    var newcashlinesource1 = $('#new-cash-line-source1').val();
	            var newcashlinereceipt1 = $('#new-cash-line-receipt1').val();
	            var newcashlineinvoice1 = $('#new-cash-line-invoice1').val();

                    if (newcashlineinvoice1.length > 0) {
                    } else {
                        notification_message += "<li>Please select an invoice.</li>";
                    }

		    if (newcashlineamount1 > 0) {
		    } else {
                        notification_message += "<li>Please enter an amount greater than 0.00.</li>";
	            }

                    if (newcashlinesource1.length > 0) {
	            } else {
                        notification_message += "<li>Please select a payment source.</li>";
		    }

	            if ( newcashlinereceipt1.length > 2) { 
                       
		    } else {
                           notification_message += "<li>Please enter a receipt number.</li>";
		    }


                    if (notification_message.length > 0) {
                            $('#error-message').html(notification_message);
                            $("#MessageBox").modal("show");
                            //$('#LoadingPopup').modal('hide');
                            $('#notification-body').html(notification_message);
                            $('.modal-backdrop').show();
                            $('#notification-box').show();
                    } else {
                           $('#LoadingPopup').modal('show');

                             $.ajax({
                              beforeSend: function(xhrObj){
                                xhrObj.setRequestHeader("Content-Type","application/json");
                                xhrObj.setRequestHeader("Accept","application/json");
                             },
                             url: take_payment.var.cash_refund_url,
                             headers: {'X-CSRFToken' : take_payment.var.csrf_token },
                             data: JSON.stringify({
                                      "invoice" : newcashlineinvoice1,
                                     "amount": newcashlineamount1,
                                     "receipt": newcashlinereceipt1,
                                     "source": newcashlinesource1,
                                     "type": 'payment'}),

                             // async: false,
                             error: function(data) {
				   var error_text = "There was a system error, attempting to process your request please try again later.";
				   if ('responseText' in data) {
                                         error_text = data.responseText;
				   } else {

				   }
                                   
				   $("#MessageBox").modal("show");
                                   $('#error-message').html(error_text);
                                   setTimeout("ledger_payments.load_payment_info();",500);
                             },
                             dataType: 'json',
                             success: function(data, textStatus, xhr) {
                                   $('#new-cash-line-amount1').val("");
                                   $('#new-cash-line-source1').val("");
                                   $('#new-cash-line-receipt1').val("");
                                   $('#new-cash-line-invoice1').val("");
                                   if (xhr.status == 201) {
                                          $('#notification-body-success').html("Refund completed successfully");
                                          $('.modal-backdrop').show();
                                          $('#notification-box-success').show();
                                      setTimeout("ledger_payments.load_payment_info()",500);
                                   } else {
                                          $('#notification-body-success').html("<span style='color: red'>A refund on one or more of the transaction failed and has been moved to the unllocation pool. Please see order history to see which transaction failed. </span>");
                                          $('.modal-backdrop').show();
                                          $('#notification-box-success').show();
                                      setTimeout("ledger_payments.load_payment_info();",500);

                                   }
                             },
                                     type: 'post'
                             })


                    }

		});


                // START REFUND BOOKING BUTTON ( Esecute when button clicked )
                $('#take-payment').on("click", function() {
                    $('.modal-backdrop').show();
                    $("#take-payment").hide();
                    $("#take-payment-wait").show();
                    console.log('STARTING REFUND');
                    var from_money_pool_array = [];
                    var to_money_pool_array = [];
                    var bpoint_trans_split_array = [];
                    var notification_message = "";
                    var un_pool = $('#unallocated_pool_refund').val();
                    var un_pool_tax =  $('#unallocated_pool_refund_tax').val();
                    var trans_method = $('input[name="trans_method"]:checked').val();
                    var settlement_date_form = $('#settlement_date').val();
                    var settlement_override = $('#settlement_override').prop('checked');
                    var settlement_date = '';

			     if (trans_method == undefined) {
                         notification_message += "<li>Please select a transaction action.</li>";
		          }
                    if (settlement_override == true) {
                         settlement_date = settlement_date_form;
                         if (settlement_date.length > 0 && settlement_date.length == 10) {
                         var settlement_date_split = settlement_date.split("-");
                              if (settlement_date_split[0].length != 4) {
                                   notification_message += "<li>Settlement date year is invalid.</li>";
                              }

                              if (settlement_date_split[1].length != 2) {
                                   notification_message += "<li>Settlement date month is invalid.</li>";
                              } else {
                                   if (settlement_date_split[1] >= 1 && settlement_date_split[1] <= 12) {

                                   } else {
                                        notification_message += "<li>Settlement date month is invalid.</li>";
                                   }
                              }

                              if (settlement_date_split[2].length > 1 && settlement_date_split[2].length < 3) {
                                   if (settlement_date_split[2] >= 1 && settlement_date_split[2] <= 31) {
                                   } else {
                                        notification_message += "<li>Settlement date day is invalid.1</li>";
                                   }
                              } else {
                                   notification_message += "<li>Settlement date day is invalid.2</li>"; 
                              }				  
                         } else {
                              notification_message += "<li>Please enter a valid settlement date.</li>";
                         }
                    }

			     if (trans_method == "4") {
		          } else {

                         if (trans_method == undefined) { 
   			               notification_message += "<li>Please choose how the refund will be completed?</li>";
   			          }
                         if (trans_method == "7" ) {
				     } 
   		
                         if (un_pool > take_payment.var.booking_allocation_pool) {
   			               notification_message += "<li>Your unallocated pool from money pool total is greater than the unallocation pool available total</li>";
   			          }
                         if (trans_method == "6" || trans_method == "7" ) {
			          } 
                    }

                    if (trans_method == "1") { 
                         $("#money-bpoint-booking").find('input').each(function() {
                              input_id = this.id;
                              input = this;

                              if (this.type == 'text' || this.type=='hidden') {
                                   idvalname = input_id.substring(0, 10);
                                   rowid = input_id.replace(idvalname,"");
                                   if (idvalname == 'txn_number') {
                                        var txn_number = $('#txn_number'+rowid).val();
                                        var line_amount = $('#bp-line-amount'+rowid).val();
                                        var btt = {};
                                        for (let i = 0; i < take_payment.var.bpoint_trans_totals.length; i++) {
                                             if (take_payment.var.bpoint_trans_totals[i].txnnumber == txn_number) {
                                                  btt = take_payment.var.bpoint_trans_totals[i]                                                                                
                                             }
                                        }

                                        if (parseFloat(line_amount) > parseFloat(btt.amount)) {
                                             notification_message += "<li>Transaction '"+txn_number+"' amount '"+line_amount+"' is greater than available amount '"+btt.amount+"'</li>";
                                        }
                                   }
                              }
                         });
		          } else if (trans_method == "4") {
                               $("#take-payment").show();
                               $("#take-payment-wait").hide();
   			     } else {
                              $("#money-booking").find('input, select').each(function() {
                                   input_id = this.id;
                                   input = this;
                                   if (this.type == 'text' || this.type=='select-one') {
                                        idvalname = input_id.substring(0, 20);
                                        rowid = input_id.replace(idvalname,"");
                                        if (idvalname == 'money-to-oracle-code') {
                                             //var val = $('#'+input_id).val();
						               var val = $('#money-to-oracle-code'+rowid).val();
                                             var money_from_amount = $('#money-to-line-amount'+rowid).val();
                                             var line_text = $('#money-to-line-text'+rowid).val();
                                             if (val.length > 0) {
                                                  if (take_payment.check_oracle_code(val) == false) {
                                                       notification_message += "<li>'"+val+"' oracle code does not exist. </li>";
                                                  }
                                                  if (line_text.length < 3) {
                                                       notification_message += "<li>Please enter a suitable line description length. </li>";
                                                  }
                                             }
                                        }
                                   }
                              });
   			     }
                    if (notification_message.length > 0) {
				     $('#error-message').html(notification_message);
                         $("#MessageBox").modal("show");
                         $('#notification-body').html(notification_message);
                         $('.modal-backdrop').show();
                         $('#notification-box').show();
                         $("#take-payment").show();
                         $("#take-payment-wait").hide();
   			   } else {
				     if (trans_method == "4") {
                              $('#LoadingPopup').modal('show');
                              $("#money-cash-booking").find('input').each(function() {
                                   input_id = this.id;
                                   input = this;

                                   if (this.type == 'text' || this.type=='hidden') {
                                        idvalname = input_id.substring(0, 19);
                                        rowid = input_id.replace(idvalname,"");
                                        if (idvalname == 'cash_invoice_number') {
                                             var cash_iv = $('#cash_invoice_number'+rowid).val();
                                             var line_amount = $('#cash-line-amount'+rowid).val();
                                             $.ajax({
                                                  beforeSend: function(xhrObj){
                                                  xhrObj.setRequestHeader("Content-Type","application/json");
                                                  xhrObj.setRequestHeader("Accept","application/json");
                                                  },
                                                  url: take_payment.var.cash_refund_url,
                                                  headers: {'X-CSRFToken' : take_payment.var.csrf_token },
                                                  data: JSON.stringify({ 
                                                       "invoice" : cash_iv,
                                                       "amount": line_amount,
                                                       "details": 'refunding',
                                                       "source": 'cash',
                                                       "type": 'refund'
                                                  }),
                                                  // async: false,
                                                  error: function(data) {
                                                       $('#notification-body').html("There was a system error, attempting to process your request please try again later.");
                                                       $('.modal-backdrop').show();
                                                       $('#notification-box').show();
                                                       ledger_payments.load_payment_info();
                                                  },
                                                  dataType: 'json',
                                                  success: function(data, textStatus, xhr) {
                                                       if (xhr.status == 201) {
                                                            $('#notification-body-success').html("Refund completed successfully");
                                                            $('.modal-backdrop').show();
                                                            $('#notification-box-success').show();
                                                       setTimeout("ledger_payments.load_payment_info()",500);
                                                       } else {
                                                            $('#notification-body-success').html("<span style='color: red'>A refund on one or more of the transaction failed and has been moved to the unllocation pool. Please see order history to see which transaction failed. </span>");
                                                            $('.modal-backdrop').show();
                                                            $('#notification-box-success').show();
                                                            ledger_payments.load_payment_info();
                                                       }
                                                  },
                                                  type: 'post'
                                                  })
                                        }
                                   }
                              });


				    } else {
                                        var unallocated_text = $('#unallocated-text').val();

                                        from_money_pool_array.push({'oracle-code': take_payment.var.oracle_code_refund_allocation_pool, 'line-text': unallocated_text, 'line-amount': un_pool, 'line-tax': un_pool_tax});
    

                                        $("#money-booking").find('input').each(function() {
                                                 input_id = this.id;
                                                 input = this;

                                                 if (this.type == 'text') {
                                                      idvalname = input_id.substring(0, 20);
                                                      rowid = input_id.replace(idvalname,"");
                                                      if (idvalname == 'to-money-oracle-code') {
                                                             var oracle_code = $('#to-money-oracle-code'+rowid).val();
                                                             var line_text = $('#to-money-line-text'+rowid).val();
                                                             var line_tax = $('#to-money-line-tax'+rowid).val();
                                                             var line_amount = $('#to-money-line-amount'+rowid).val();
                                                             to_money_pool_array.push({'oracle-code': oracle_code, 'line-text': line_text, 'line-amount': line_amount, 'line-tax': line_tax});
                                                      }
                                                 }
                                        });

                                        $("#money-bpoint-booking").find('input').each(function() {
                                                 input_id = this.id;
                                                 input = this;

                                                 if (this.type == 'text' || this.type=='hidden') {
                                                      idvalname = input_id.substring(0, 10);
                                                      rowid = input_id.replace(idvalname,"");
                                                      if (idvalname == 'txn_number') {
                                                             var txn_number = $('#txn_number'+rowid).val();
                                                             var line_amount = $('#bp-line-amount'+rowid).val();
                                                             bpoint_trans_split_array.push({'txn_number': txn_number, 'line-amount': line_amount});
                                                      }
                                                 }
                                       });
				                    $('#LoadingPopup').modal('show');
                                        
				                    // $('input[name="csrfmiddlewaretoken"]').val(),
                                        $.ajax({
                                             url: take_payment.var.api_url,
                                             headers: {'X-CSRFToken' : take_payment.var.csrf_token },
                                             data: {
                                                  csrfmiddlewaretoken: take_payment.var.csrf_token,
                                                  money_from : JSON.stringify(from_money_pool_array),
                                                  money_to: JSON.stringify(to_money_pool_array),
                                                  bpoint_trans_split: JSON.stringify(bpoint_trans_split_array),
                                                  refund_method: trans_method,
                                                  booking_id: take_payment.var.booking_id,
                                                  newest_booking_id: take_payment.var.newest_booking_id,
                                                  booking_reference: take_payment.var.booking_reference,
                                                  booking_reference_linked: take_payment.var.booking_reference_linked,
                                                  settlement_date: settlement_date
                                        },
                                       // async: false,
                                       error: function(data) {
                                             $('#notification-body').html("There was a system error, attempting to process your request please try again later.");
   	                                        $('.modal-backdrop').show();
            	                              $('#notification-box').show();
                                             ledger_payments.load_payment_info();
                                       },
                                       dataType: 'json',
                                       success: function(data) {

                                             if (data.failed_refund == false) {
                                                    $('#notification-body-success').html("Refund completed successfully");
                                                    $('.modal-backdrop').show();
                                                    $('#notification-box-success').show();
				            	ledger_payments.load_payment_info();
   				             } else {
                                                    $('#notification-body-success').html("<span style='color: red'>A refund on one or more of the transaction failed and has been moved to the unllocation pool. Please see order history to see which transaction failed. </span>");
                                                    $('.modal-backdrop').show();
                                                    $('#notification-box-success').show();
				            	ledger_payments.load_payment_info();

   				             } 
                                       },
                                               type: 'post'
                                       })

			           }
   			}
   			console.log('Refund Button Clicked');
   		   });
                   // END REFUND BOOKING BUTTON ( Esecute when button clicked )


                   // Hide To Money and Bpoint until refund method selection is selected.
                   $('#money-booking-div').hide();
                   $('#money-bpoint-div').hide();
		   $('#money-cash-div').hide();
		   $('#cash-payment').hide();
                   // --

                   $("input[name='trans_method']").on( "change", function() {
		       $('#from-money-booking-div').show();
		       $('#money-booking-div').hide();
                       $('#money-bpoint-div').hide();
		       $('#money-cash-div').hide();
		       $('#cash-payment').hide();
		       $('#money-management').show();

                       if (this.value == 1) { 
                           $('#money-bpoint-div').show();
		       } else if (this.value == 4) {
                           $('#from-money-booking-div').hide();
			   $('#money-cash-div').show();
                       } else if (this.value == 5) {
			   $('#cash-payment').show();
			   $('#money-management').hide();
		       } else if (this.value == 6) {
			   $('#from-money-booking-div').show();
		       } else if (this.value == 7) {
			   $('#from-money-booking-div').hide();
			   $('#money-booking-div').show();
      		       } else {
                           $('#money-booking-div').show();
                           //$('#money-bpoint-div').hide();
                       }
                   });
                   take_payment.re_init();

                   $('.modal-backdrop').hide();

                   take_payment.money_bpoint_trans_refund();
		   take_payment.money_cash_trans_refund();
		   take_payment.money_cash_trans_payment();
   	}
   }
   document.addEventListener('DOMContentLoaded', function() {
     take_payment.init(); 
   });
