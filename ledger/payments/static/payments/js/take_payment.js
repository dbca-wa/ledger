var take_payment =  {
     var: { 
          row_id: 0,
          total_money: parseFloat('0.00'),
          booking_reference: '',
          booking_reference_linked: '',
          csrf_token: '',
          oracle_code_tax_status: {}
     }, 
     money_add_row: function() {
          take_payment.var.row_id = take_payment.var.row_id + 1;
          var html = "<tr id='money_row"+take_payment.var.row_id+"' >";
          html += "<td><span id='oracle-error"+take_payment.var.row_id+"'><input style='width: 200px;' class='form-control input-sm' type='text' id='money-oracle-code"+take_payment.var.row_id+"' onblur='take_payment.input_oracle_code_change(this.id)' ></span></td>";
          html += "<td><input style='width: 100%' type='text' class='form-control input-sm' id='money-line-text"+take_payment.var.row_id+"'></td>";
          html += "<td><div style='display:flex'><span class='money_sign'  style='padding-top:6px;'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='take_payment.money_update(this);' id='money-line-tax"+take_payment.var.row_id+"' disabled=true></div></td>";
          html += "<td><div style='display:flex'><span class='money_sign'  style='padding-top:6px;'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='take_payment.money_update(this);' id='money-line-amount"+take_payment.var.row_id+"'></div></td>";
          html += "<td><button type='button' class='btn btn-danger' onclick='take_payment.remove_row("+'"money_row'+take_payment.var.row_id+'"'+")' ><i class='bi bi-x-lg'></i></button></td>";
          html += "</tr>";
          $("#money-booking tbody").append(html);
     },
     remove_row: function(row_id) {
          $('#'+row_id).remove();
          take_payment.total_money();
     },
     total_money: function() {
          console.log("total_money")
          take_payment.var.total_money = parseFloat('0.00');
          $('#total_money').html('$'+take_payment.format_money(take_payment.var.total_money));
          $("#money-booking").find('input').each(function() {
               if (this.type == 'number') {
                    if (this.value > 0 ) { 
               } else {
                         this.value = '0.00'; 
                    }
                    if (this.id.substring(0,17) == 'money-line-amount') {
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
          console.log("money_update")
          var rowid_val;
          var gst_value = 0.00;
          if (item.id.substring(0,17) == 'money-line-amount') {
               rowid_val = item.id.replace('money-line-amount','')
               var oracle_code_value = $('#money-oracle-code'+rowid_val).val();                    

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
               
               $('#money-line-tax'+rowid_val).val(gst_value.toFixed(2));  
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
               if (element_id.substring(0,17) == 'money-oracle-code') {
                    rowid_val = element_id.replace('money-oracle-code','');             
                    var amount_item = document.getElementById('money-line-amount'+rowid_val);
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
          console.log("re_init")
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

          $('#take-payment').on("click", function() {
               $('.modal-backdrop').show();
               $("#take-payment").hide();
               $("#take-payment-wait").show();
               console.log('STARTING TAKE PAYMENT');
               var money_pool_array = [];
               var notification_message = "";

               $("#take-payment").show();
               $("#take-payment-wait").hide();

               $("#money-booking").find('input').each(function() {
                    input_id = this.id;
                    input = this;

                    if (this.type == 'text') {
                         idvalname = input_id.substring(0, 17);
                         rowid = input_id.replace(idvalname,"");
                         if (idvalname == 'money-oracle-code') {
                              var oracle_code = $('#money-oracle-code'+rowid).val();
                              var line_text = $('#money-line-text'+rowid).val();
                              var line_tax = $('#money-line-tax'+rowid).val();
                              var line_amount = $('#money-line-amount'+rowid).val();
                              console.log(!oracle_code)
                              if (!oracle_code) {
                                   notification_message = "Missing Oracle Code."
                              }
                              if (!line_text) {
                                   notification_message = "Missing Line Description."
                              }
                              money_pool_array.push({'oracle-code': oracle_code, 'line-text': line_text, 'line-amount': line_amount, 'line-tax': line_tax});
                         }
                    }
               });

               if (notification_message.length > 0) {
                    $('#error-message').html(notification_message);
                    $("#MessageBox").modal("show");
                    $('#notification-body').html(notification_message);
                    $('.modal-backdrop').show();
                    $('#notification-box').show();
               } else {

                    $('#LoadingPopup').modal('show');
                    $.ajax({  
                         url: "/ledger/payments/api/ledger/take-payment",
                         headers: {'X-CSRFToken' : take_payment.var.csrf_token },
                         data: {
                              csrfmiddlewaretoken: take_payment.var.csrf_token,
                              money: JSON.stringify(money_pool_array),
                              booking_reference: take_payment.var.booking_reference,
                              booking_reference_linked: take_payment.var.booking_reference_linked,
                         },

                         error: function(data) {
                              notification_message = "There was a system error, please review your submission and try again.";
                              $('#error-message').html(notification_message);
                              $('#notification-body').html("There was a system error, attempting to process your request please try again later.");
                              $("#MessageBox").modal("show");
                              $('.modal-backdrop').show();
                              $('#notification-box').show();
                              ledger_payments.load_payment_info();
                         },
                         dataType: 'json',
                         success: function(data) {
                              notification_message = "Take Payment request completed successfully. Invoice Ref: "+data.invoice+". Redirecting to Email Invoice page...";
                              $('#success-message').html(notification_message);
                              $('#notification-body-success').html("Take Payment request completed successfully.");
                              $("#SuccessMessageBox").modal("show");
                              $('.modal-backdrop').show();
                              $('#notification-box-success').show();
                              ledger_payments.load_payment_info();

                              //redirect to invoice email form
                              if (data.invoice) {
                                   setTimeout(
                                   function () {window.location.href = "/ledger/payments/invoice/email?invoice_no="+data.invoice},
                                   5000,
                                   )
                              }
                         },
                         type: 'post'
                    })

                    console.log('Take Payment Button Clicked');
               }
          });
   	}
}

document.addEventListener('DOMContentLoaded', function() {
     take_payment.init(); 
});
