function hideBanner(){
    $('#paymentBanner').addClass('hide');  
}
function showBanner(){
    $('#paymentBanner').removeClass('hide');  
}
$(function(){
    $(document).foundation();
    var $other_form = $('#other_form');
    var $card_form = $('#card_form');
    var $errors_div = $('#errors');
    var $errors_row = $('#errors_row');
    var $success_div = $('#success_div');
    var $success_row = $('#success_row');
    var $location_fieldset = $('#location_fieldset');
    var $card_fieldset = $('#card_fieldset');
    var $storedcard_fieldset = $('#storedcard_fieldset');
    var invoice = $('#invoice_selector').val(); 
    var invoice_obj = null;
    var $regions = $('#regions');
    
    
    //Datatables
    var unlinkedBPAYTable = $('#unlinkedBpayTable').DataTable({
        "ajax":{
            "url":'/ledger/payments/api/bpay/transactions.json?sorting=unmatched',
            "dataSrc":""
        },
        "processing":true,
        "columns":[
            {
                data: "crn"
            },
            {
                data: "biller_code"
            },
            {
                data: "amount"
            },
            {
                mRender: function(data,type,full){
                    return '<a href="#" data-txn_id="'+full.id+'" class="button float-right bpay_link_btn">LINK</a>';
                }
            }
        ]
    });
    
    var linkedBPAYTable = $('#linkedBpayTable').DataTable({
        "ajax":{
            "url":'/ledger/payments/api/invoices/'+invoice+'/linked_bpay.json',
            "dataSrc":""
        },
        "processing":true,
        "columns":[
            {
                data: "crn"
            },
            {
                data: "biller_code"
            },
            {
                data: "amount"
            },
            {
                mRender: function(data,type,full){
                    return '<a href="#" data-txn_id="'+full.id+'" class="button alert round float-right bpay_unlink_btn">UNLINK</a>';
                }
            }
        ]
    });
    
    var receivedPaymentsTable = $('#received_payments_table').DataTable({
        "ajax":{
            "url":'/ledger/payments/api/invoices/'+invoice+'/payments.json',
            "dataSrc":""
        },
        "processing":true,
        "columns":[
            {
                data: "date"
            },
            {
                data: "type"
            },
            {
                data: "details"
            },
            {
                data: "amount"
            },
        ]
    });
    // BPAY Buttons
    unlinkedBPAYTable.on('click','.bpay_link_btn',function(e){
        e.preventDefault();
        var txn = $(this).data('txn_id');
        bpay_payment(txn,true,function(){
            unlinkedBPAYTable.ajax.reload();
            linkedBPAYTable.ajax.reload();
        });
        
    });
    linkedBPAYTable.on('click','.bpay_unlink_btn',function(e){
        e.preventDefault();
        var txn = $(this).data('txn_id');
        bpay_payment(txn,false,function(){
            linkedBPAYTable.ajax.reload();
            unlinkedBPAYTable.ajax.reload();
        });
    });

    $('#invoice_selector').on('change',function(){
        var reference = $(this).val();
        if (reference){
            $.get('/ledger/payments/api/invoices/'+reference+'.json',function(resp){
                set_invoice(resp);
                // Received Payments
                receivedPaymentsTable.ajax.url('/ledger/payments/api/invoices/'+reference+'/payments.json');
                // Linked BPAY Payments
                linkedBPAYTable.ajax.url('/ledger/payments/api/invoices/'+reference+'/linked_bpay.json');
                linkedBPAYTable.ajax.reload();
                invoice = resp.reference;
                updateBanner();
            });
        }
    });
    // Display for the external cash payment feature
    $('#other_external').click('on',function(){
        if (this.checked) {
            $location_fieldset.removeClass('hide');
        }
        else{
            $location_fieldset.addClass('hide');
        }
    });
    // Display for the stored card feature
    $('#use_stored').click('on',function(){
        if (this.checked) {
            $storedcard_fieldset.removeClass('hide');
            $card_fieldset.addClass('hide');
        }
        else{
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }
    });
    function getCookie(name) {
        var value = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1).trim() === (name + '=')) {
                    value = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return value;
    }
    function set_invoice(invoice){
        invoice_obj = invoice; 
    }
    // Reset Forms
    function reset_forms() {
        $other_form[0].reset();
        $card_form[0].reset();
    }
    // Disable PayButtons
    function disablePayButtons() {
        $('.pay_btn').addClass('disabled');
    }
    // Check if invoice is paid
    function checkInvoiceStatus(){
        var status = '';
        var amount_paid = '';
        var redirect_url = $('#payment_div').data('redirect');
        $.get('/ledger/payments/api/invoices/'+invoice+'.json',function(resp){
            invoice_obj = resp;
            if (status === 'paid' && redirect_url) {
                window.location.replace(redirect_url);
            }
            updateBanner();
        });
    }
    function checkInvoiceStatusNoRedirect(){
        var status = '';
        var amount_paid = '';
        var redirect_url = $('#payment_div').data('redirect');
        $.get('/ledger/payments/api/invoices/'+invoice+'.json',function(resp){
            invoice_obj = resp;
            updateBanner();
        });
    }
    function redirectPage(){
        var redirect_url = $('#payment_div').data('redirect');
        window.location.replace(redirect_url);
    }
    $('.redirect_btn').click(function(e){
        e.preventDefault();
        redirectPage();
    });
    function formatMoney(n,c, d, t){
        c = isNaN(c = Math.abs(c)) ? 2 : c;
        d = d == undefined ? "." : d;
        t = t == undefined ? "," : t;
        var s = n < 0 ? "-" : "";
        var i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c)));
        var j = (j = i.length) > 3 ? j % 3 : 0;
        return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
    }
    function updateBanner() {
        var status = invoice_obj.payment_status;
        var balance = '$'+formatMoney(invoice_obj.balance);
        var amount_paid = '$'+formatMoney(invoice_obj.payment_amount);
        // Top banner
        $('#invoice_status').html(status);
        $('#invoice_balance').html(balance);
        $('#invoice_paid').html(amount_paid);
        // Individual Invoice
        $("strong.invoice_status[data-reference='"+invoice+"']").html(status);
        $("strong.invoice_balance[data-reference='"+invoice+"']").html(balance);
        $("strong.invoice_paid[data-reference='"+invoice+"']").html(amount_paid);
        if (!$success_div.hasClass('hide')) {
            setTimeout(function(){$success_div.addClass('hide');},3000);
        }
        showRecordPayment();
        receivedPaymentsTable.ajax.reload();
    }
    function showRecordPayment(){
        if (invoice_obj.payment_status != 'paid' && invoice_obj.payment_status != 'over_paid'){
            if ($other_form.hasClass('hide')){
                $other_form.removeClass('hide');
            }
        }
        else{
            $other_form.addClass('hide');
        }
    }
    /*
     * Update Region Districts
     */
    function updateDistricts(region) {
        $('#dist_wrapper').addClass('hide');
        if (!region) {
            $('#districts').html("");
        }
        else{
            $.get('/ledger/payments/api/regions/'+region+'.json',function(resp){
                var districts = resp.districts;
                $('#districts').html("");
                if (districts.length > 0) {
                    $('#districts').append('<option value="">---- Select District ----</option>');
                    $(districts).each(function(i){
                        $('#districts').append('<option value="'+districts[i].code+'">'+districts[i].name+'</option>');
                    });
                    if (districts.length === 1) {
                        $('#districts').val(districts[0].code);
                    }
                }
            });
            if ($('#dist_wrapper').hasClass('hide')) {
                $('#dist_wrapper').removeClass('hide');
            }
        }
    }
    /*
    * Make cash payments
    */
    function otherPayment(){
        var type,source,payload,ref;
        var amount, orig_txn = null;
        var external = false;
        
        // Hide div if not hidden
        if (!$errors_div.hasClass('hide')) {
            $errors_div.addClass('hide');
        }
        // Get payload
        payload = {
            "invoice": invoice,
            "type": $('#other_type').val(),
            "source": $('#other_source').val()
        }
        // Check if the amount field is there and has a value
        if ($('#other_amount').val()) {
            payload["amount"] = $('#other_amount').val();
        }
        // Check if the original transaction field is there and has a value
        if ($('#other_orig_txn').val()) {
            payload["orig_txn"] = invoice;
        }
        
        // Check if the external checkbox is selected
        if ($('#other_external').is(':checked')){
            payload['external'] = true;
            payload['region'] = $('#regions').val();
            payload['district'] = $('#districts').val();
            payload['receipt'] = $('#receipt_number').val();
        }
        
        // POST
        $.ajax ({
            beforeSend: function(xhrObj){
              xhrObj.setRequestHeader("Content-Type","application/json");
              xhrObj.setRequestHeader("Accept","application/json");
            },
            type: "POST",
            url: "/ledger/payments/api/cash.json",
            data: JSON.stringify(payload),
            dataType: "json",
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function(resp){
                success(resp,invoice,$('#other_source').val());
            },
            error: function(resp){
                error(resp);
            },
            complete: function(resp){
                checkInvoiceStatus();
            }
        });
        /*$.post("/ledger/payments/api/cash.json",payload, function(resp){
            success(resp,invoice,$('#other_source').val());
        })
        .fail(function(resp){
            error(resp);
        })
        .always(function(){
            checkInvoiceStatus()
        });*/
    }
    /*
    *  Make card payments with either stored cards or new cards
    */
    function cardPayment(){
        
        // Hide div if not hidden
        if (!$errors_div.hasClass('hide')) {
            $errors_div.addClass('hide');
        }
        // Get payload
        payload = {
            "invoice": String(invoice),
            "action": $('#card_action').val(),
            "type": "telephoneorder"
        }
        // Check if amount filed is present and has value has value
        if ($('#card_amount').val()) {
            payload["amount"] = $('#card_amount').val();
        }
        // Check if the pay by stroed cards checkbox is selected
        if ($('#use_stored').is(':checked')){
            payload['using_token'] = true;
            payload['token'] = $('input[name=card]:checked').val();
        }
        else{
            var card= {
                "number": $('#card_number').val(),
                "cvn": $('#card_cvn').val(),
                "expiry": $('#month_expiry').val()+$('#year_expiry').val(),
            }
            payload["card"] = card;
        }
        // POST
        $.ajax ({
            beforeSend: function(xhrObj){
              xhrObj.setRequestHeader("Content-Type","application/json");
              xhrObj.setRequestHeader("Accept","application/json");
            },
            type: "POST",
            url: "/ledger/payments/api/bpoint/payment",
            data: JSON.stringify(payload),
            dataType: "json",
            success: function(resp){
                success(resp,invoice,'card');
            },
            error: function(resp){
                error(resp);
            },
            complete: function(resp){
                checkInvoiceStatus();  
            }
        });
    }
    function bpay_payment(txn,link,reload_table){
        // Hide div if not hidden
        if (!$errors_div.hasClass('hide')) {
            $errors_div.addClass('hide');
        }
        // Get payload
        payload = {
            "invoice": String(invoice),
            "link": link,
            "bpay": txn
        }
        
        // POST
        $.ajax ({
            beforeSend: function(xhrObj){
              xhrObj.setRequestHeader("Content-Type","application/json");
              xhrObj.setRequestHeader("Accept","application/json");
            },
            type: "POST",
            url: "/ledger/payments/api/invoices/"+invoice+"/link.json",
            data: JSON.stringify(payload),
            dataType: "json",
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function(resp){
                if (!link) {
                    success(invoice,'This BPAY transaction has been unlinked from this invoice.');
                }
                else{
                    success(invoice,'Invoice #'+invoice+' successfully paid using '+'bpay');
                }
                reload_table();
            },
            error: function(resp){
                error(resp);
            },
            complete: function(resp){
                checkInvoiceStatusNoRedirect();  
            }
        });
    }
    /*
     * Display success message
     */
    function success(resp,reference,source){
        var success_str = '';
                         
        success_str = 'Invoice #'+reference+' successfully paid using '+source;
        
        success_html = '<div class="columns small-12"><div class="success callout" data-closable="slide-out-right"> \
            <p class="text-center">'+success_str+'</p> \
        </div></div>';
        
        $success_row.html(success_html);
        $success_div.removeClass('hide');
        if (!$location_fieldset.hasClass('hide')) {
            $location_fieldset.addClass('hide');
        }
        if (!$storedcard_fieldset.hasClass('hide')) {
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }
        reset_forms();
    }
    function success(reference,msg){
        var success_str = '';
                         
        success_str = msg;
        
        success_html = '<div class="columns small-12"><div class="success callout" data-closable="slide-out-right"> \
            <p class="text-center">'+success_str+'</p> \
        </div></div>';
        
        $success_row.html(success_html);
        $success_div.removeClass('hide');
        if (!$location_fieldset.hasClass('hide')) {
            $location_fieldset.addClass('hide');
        }
        if (!$storedcard_fieldset.hasClass('hide')) {
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }
        reset_forms();
    }
    /*
     * Display Error Message
     */
    function error(resp){
        var error_str = '';
        // Show Errors
        if (resp.status === 400) {
            try {
                obj = JSON.parse(resp.responseText);
                error_str = obj.non_field_errors[0].replace(/[\[\]"]/g,'');
            } catch(e) {
                error_str = resp.responseText.replace(/[\[\]"]/g,'');
            }
        }
        error_html = '<div class="columns small-12"><div class="alert callout" data-closable="slide-out-right"> \
            <p class="text-center">'+error_str+'</p> \
        </div></div>';
        $errors_row.html(error_html);
        $errors_div.removeClass('hide');
    }
    $other_form.submit(function(e){
        e.preventDefault();
        otherPayment();
    });
    
    $regions.change(function(){
        updateDistricts($(this).val());
    });
    // Reset all forms when page is loaded
    reset_forms();
    /*$card_form.submit(function(e){
        e.preventDefault();
        cardPayment();
    });*/
});
