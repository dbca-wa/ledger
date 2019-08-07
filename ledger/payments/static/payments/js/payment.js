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

    // Money Inputs
    var cfgCulture = 'en-AU';
    $.preferCulture(cfgCulture);
    $('.money').maskMoney();

    // Update Status format
    $('#invoice_status').html(formatStatus($('#invoice_status').html()));
    $('.invoice_status').each(function(){
        $(this).html(formatStatus($(this).html()));
    });
    $('#mainTabLoader').hide();

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
        $('#payment_div').hide();
        $('#mainTabLoader').show();
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
    // Refund Button
    $("#refund_btn").click(function(e){
        e.preventDefault();
        var modal = $('#refundModal');
        modal.foundation('open');
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
    function formatStatus(status){
        var parts = [];
        var res = '';
        parts = status.split('_');
        if (parts.length > 1){
            for(i=0;i < parts.length; i++){
                res += capitalizeFirstLetter(parts[i]) + ' ';
            }
        }
        else{ res = capitalizeFirstLetter(status);}
        return res
    }
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    function updateBanner() {
        var status = invoice_obj.payment_status;
        var balance = '$'+formatMoney(invoice_obj.balance);
        var amount_paid = '$'+formatMoney(invoice_obj.payment_amount);
        var refundable_amount = '$'+formatMoney(invoice_obj.refundable_amount);
        var invoice_date = invoice_obj.created;
        // Top banner
        $('#invoice_status').html(formatStatus(status));
        $('#invoice_balance').html(balance);
        $('#invoice_paid').html(amount_paid);
        $('#invoice_date').html(invoice_date);
        $('.refundable_amount').html(refundable_amount);
        // Individual Invoice
        $("strong.invoice_status[data-reference='"+invoice+"']").html(formatStatus(status));
        $("strong.invoice_balance[data-reference='"+invoice+"']").html(balance);
        $("strong.invoice_paid[data-reference='"+invoice+"']").html(amount_paid);
        if (!$success_div.hasClass('hide')) {
            setTimeout(function(){$success_div.addClass('hide');},3000);
        }
        rf.updateRefundModal();
        $('#payment_div').show();
        $('#mainTabLoader').hide();
        showRecordPayment();
        receivedPaymentsTable.ajax.reload();
    }
    function showRecordPayment(){
        if (invoice_obj.payment_status != 'paid' && invoice_obj.payment_status != 'over_paid' && !invoice_obj.voided){
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
                if (districts) {
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
        var amount = $('#other_amount').val();

        // Hide div if not hidden
        if (!$errors_div.hasClass('hide')) {
            $errors_div.addClass('hide');
        }
        if(!amount){
            formError('An amount has not been specified for the payment');
            return
        }
        // Get payload
        payload = {
            "invoice": invoice,
            "amount": $('#other_amount').val(),
            "type": 'payment',
            "source": $('#other_source').val()
        }
        // Check if the original transaction field is there and has a value
        if ($('#other_orig_txn').val()) {
            payload["orig_txn"] = invoice;
        }

        // Check if the external
        var pay_region = $('#regions').val().trim();
        if (pay_region) {
            payload['external'] = true;
            payload['region'] = $('#regions').val();
            payload['district'] = $('#districts').val();
        }
        payload['receipt'] = $('#receipt_number').val();
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
                sendCallback();
            },
            error: function(resp){
                error(resp);
            },
            complete: function(resp){
                checkInvoiceStatus();
            }
        });
    }
    function sendCallback(){
        var callback_url = $('#payment_div').data('callback');
        console.log('sending');
        var payload = {
            'invoice': invoice
        }
        $.ajax ({
            beforeSend: function(xhrObj){
              xhrObj.setRequestHeader("Content-Type","application/json");
              xhrObj.setRequestHeader("Accept","application/json");
            },
            type: "POST",
            url: callback_url,
            data: JSON.stringify(payload),
            dataType: "json",
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function(resp){
                console.log('callback sent');
            },
            error: function(resp){
                console.error(resp);
            },
        });
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
        /*if (!$location_fieldset.hasClass('hide')) {
            $location_fieldset.addClass('hide');
        }
        if (!$storedcard_fieldset.hasClass('hide')) {
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }*/
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
        /*if (!$location_fieldset.hasClass('hide')) {
            $location_fieldset.addClass('hide');
        }
        if (!$storedcard_fieldset.hasClass('hide')) {
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }*/
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
    function formError(error){
        // Show Errors
        error_html = '<div class="columns small-12"><div class="alert callout" data-closable="slide-out-right"> \
            <p class="text-center">'+error+'</p> \
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

    /*****************************
        REFUNDS
    *****************************/

    var rf = {
        refund_option: $('div[data-refund-option]'),
        refund_cards: $('div[data-refund-cards'),
        refund_manual: $('div[data-refund-manual'),
        refund_btn: $('#refund_btn'),
        radios: $('#refundable_cards_radio'),
        refund_option_select: $('#refund_option'),
        refund_loader: $("#refundLoader"),
        modal_alert: $('#modal_alert'),
        modal_alert_btn: $("#refund_alert_btn"),
        modal_alert_text: $('#modal_alert > .callout-text'),
        refund_form : document.forms.refundForm,
        cancel_refund_btn: $("#cancel_refund"),
        refund_modal : $('#refundModal'),
        init: function(){
            var form = $(document.forms.refundForm).hide(100);
            $.get('/ledger/payments/api/invoices/'+$('#invoice_selector').val()+'.json',function(resp){
                set_invoice(resp);
                rf.updateRefundModal();
                rf.refund_loader.fadeOut(100);
                rf.displayOption();
                form.fadeIn(2000);
                rf.refund_btn.on('click',function(e){
                    rf.updateRefundModal();
                });
                rf.refund_option_select.on("change",function(){
                    rf.displayOption();
                });
                rf.cancel_refund_btn.on("click",function(){
                    rf.refund_modal.foundation('close');
                });
                rf.refund_modal.on("closed.zf.reveal",function(){
                    rf.refund_form.reset();
                    rf.hide(rf.modal_alert);
                });
                rf.modal_alert_btn.on("click",function(e){
                    rf.hide(rf.modal_alert);
                });
            });
            form.submit(function(e){
                e.preventDefault();
                var amount = rf.validateAmount();
                if (amount) {
                    if (invoice_obj.refundable_cards.length > 0 && rf.refund_option_select.val() == 1){
                        rf.cardRefund(amount);
                    }
                    else{
                        if(amount <= invoice_obj.refundable_amount){
                            rf.manualRefund();
                        }else{
                            rf.displayError("The amount you are trying to refund is greater than the refundable amount.")
                        }
                    }
                }
            });
        },
        displayOption: function(){
            if (invoice_obj.refundable_cards.length > 0 && rf.refund_option_select.val() == 1){
                rf.hide(rf.refund_manual);
                rf.show(rf.refund_cards);
            }
            else{
                rf.hide(rf.refund_cards);
                rf.show(rf.refund_manual);
            }
        },
        updateRefundModal:function(){
            invoice_obj.refundable ? rf.refund_btn.removeClass('hide'): rf.refund_btn.addClass('hide');
            if(invoice_obj.refundable_cards.length > 0){
                rf.radios.html('');
                $.each(invoice_obj.refundable_cards,function(i,c){
                    var input = '<label><input type="radio" name="refund_cards" value="'+c.id+'"/>';
                    input += c.cardtype+' ending in '+c.last_digits + ' - Refundable Amount ($'+c.refundable_amount+')</label>';
                    rf.radios.append(input);
                });
                rf.show(rf.refund_option);
            }
        },
        validateAmount: function(){
            var amount = $('#refundAmount').val();
            if(!amount){
               rf.displayError("An amount has not been specified for the refund");
               return false
           }
           return amount;
        },
        cardRefund: function(amount){
            payload = {
                "amount": amount,
                "details": $("#refund_details > textarea[name='refund_details']").val()
            }
            // POST
            $.ajax ({
                beforeSend: function(xhrObj){
                  xhrObj.setRequestHeader("Content-Type","application/json");
                  xhrObj.setRequestHeader("Accept","application/json");
                },
                type: "POST",
                url: "/ledger/payments/api/bpoint/"+rf.refund_form.refund_cards.value+"/refund.json",
                data: JSON.stringify(payload),
                dataType: "json",
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                success: function(resp){
                    rf.refund_modal.foundation('close');
                    rf.refund_form.reset();
                },
                error: function(resp){
                    var str = resp.responseText.replace(/[\[\]"]/g,'');
                    str = str.replace(/[\{\}"]/g,'');
                    rf.displayError(str);
                },
                complete: function(resp){
                    checkInvoiceStatus();
                }
            });
        },
        manualRefund: function(){
            // Get payload
            payload = {
                "invoice": invoice,
                "amount": $('#refundAmount').val(),
                "details": $("#refund_details > textarea[name='refund_details']").val(),
                "type": 'refund',
                "source": 'cash'
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
                    rf.refund_form.reset();
                    $(rf.refund_modal).foundation('close');
                },
                error: function(resp){
                    var str = resp.responseText.replace(/[\[\]"]/g,'');
                    str = str.replace(/[\{\}"]/g,'');
                    rf.displayError(str);
                },
                complete: function(resp){
                    checkInvoiceStatus();
                }
            });
            console.log($('#refundAmount').val());
        },
        show:function(field){
            field.removeClass('hide',100);
        },
        hide:function(field){
            field.addClass('hide',100);
        },
        displayError:function(msg){
           rf.modal_alert.removeClass('success');
           rf.modal_alert.addClass('alert');
           rf.updateAlert(msg);
        },
        displaySuccess:function(resp){
           rf.modal_alert.removeClass('alert');
           rf.modal_alert.addClass('success');
           rf.updateAlert("Refunded successfully.");
        },
        updateAlert:function (msg) {
           rf.modal_alert_text.text(msg);
           rf.show(rf.modal_alert);
        }
    };
    rf.init();
});
