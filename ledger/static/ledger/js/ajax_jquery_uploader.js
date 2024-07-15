// configuration
var max_file_size = 52428800; //allowed file size. (1 MB = 1048576)
var allowed_file_types = ['text/plain', 'image/png', 'image/gif', 'image/jpeg', 'image/pjpeg', 'application/pdf', 'application/vnd.ms-excel', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-outlook', 'application/octet-stream']; //allowed file types
var result_output = '#output'; //ID of an element for response output
var my_form_id = '#upload_form'; //ID of an element for response output
var progress_bar_id = 'progress-wrp'; //ID of an element for response output
var total_files_allowed = 3; //Number files allowed to upload

// on form submit
function bindForm(form_id, input_id, upload_type) {
    // alert(form_id);
    $(form_id).on("click", function (event) {
        //$(form_id).on("submit", function(event) {

        console.log("Starting Upload");
        event.preventDefault();
        var proceed = true; //set proceed flag
        var error = [];	//errors
        var total_files_size = 0;
        var form_data;
        // reset progressbar
        $(progress_bar_id + " .progress-bar").css("width", "0%");
        $(progress_bar_id + " .status").text("0%");

        if (!window.File && window.FileReader && window.FileList && window.Blob) { // if browser doesn't supports File API
            error.push("Your browser does not support new File API! Please upgrade."); //push error text
        } else {
            var total_selected_files = $(form_id + '__files').prop('files').length; //number of files
            if (total_selected_files == 0) {
                error.push("Please select a file first");
                proceed = false; //set proceed flag to false
            } else {
                // limit number of files allowed
                if (total_selected_files > total_files_allowed) {
                    error.push("You have selected " + total_selected_files + " file(s), " + total_files_allowed + " is maximum!"); //push error text
                    proceed = false; //set proceed flag to false
                }
            }
            //iterate files in file input field
            $($(form_id + '__files').prop('files')).each(function (i, ifile) {
                console.log(ifile);
                if (ifile.value !== "") { //continue only if file(s) are selected
                    console.log(ifile.type);
                    //if (allowed_file_types.indexOf(ifile.type) === -1) { //check unsupported file
                    //error.push( "<b>"+ ifile.name + "</b> is unsupported file type!"); //push error text
                    //proceed = false; //set proceed flag to false
                    //}

                    total_files_size = total_files_size + ifile.size; //add file size to total size
                }
            });

            //if total file size is greater than max file size
            if (total_files_size > max_file_size) {
                error.push("You have " + total_selected_files + " file(s) with total size " + total_files_size + ", Allowed size is " + max_file_size + ", Try smaller file!"); //push error text
                proceed = false; //set proceed flag to false
            }
            console.log(input_id);
            //			var submit_btn  = $(this).find("input[name=__submit__]"); //form submit button	
            var submit_btn = $('#' + input_id + '__submit');


            //if everything looks good, proceed with jQuery Ajax
            if (proceed) {
                submit_btn.val("Please Wait...").prop("disabled", true); //disable submit button
                // var form_data = new FormData(this); //Creates new FormData object
                // var form_data;
                var form_data = new FormData();
                var post_url = $(this).attr("action"); //get action URL of form

                //jQuery Ajax to Post form data
                // form_data =  {'files': []};
                var file_array = [];
                jQuery.each(jQuery(form_id + '__files')[0].files, function (i, file) {
                    form_data.append('files', file);
                });
                console.log("FILES ATTACHED 2");
                form_data.append('csrfmiddlewaretoken', $("input[name=csrfmiddlewaretoken]").val());
                form_data.append('file_group', $("#file_group").val());
                form_data.append('file_group_ref_id', $("#file_group_ref_id").val());

                $.ajax({
                    //	url : post_url,
                    url: '/ledger-uploads/',
                    type: "POST",
                    data: form_data,
                    contentType: false,
                    cache: false,
                    processData: false,
                    xhr: function () {
                        //upload Progress
                        var xhr = $.ajaxSettings.xhr();
                        if (xhr.upload) {
                            xhr.upload.addEventListener('progress', function (event) {
                                var percent = 0;
                                var position = event.loaded || event.position;
                                var total = event.total;

                                if (event.lengthComputable) {
                                    percent = Math.ceil(position / total * 100);
                                }

                                //update progressbar
                                if (percent > 99) {
                                    $(form_id + '-progress-bar-indicator').attr('class', 'progress-bar progress-bar-success');
                                    $(form_id + '-' + progress_bar_id + " .status-text").text("success");
                                } else {
                                    $(form_id + '-progress-bar-indicator').attr('class', 'progress-bar progress-bar-warning progress-bar-striped active');
                                    $(form_id + '-' + progress_bar_id + " .status-text").text("uploading");
                                }

                                $(form_id + '-' + progress_bar_id + " .progress-bar").css("width", + percent + "%");
                                $(form_id + '-' + progress_bar_id + " .status").text(percent + "%");
                            }, true);
                        }
                        return xhr;
                    },
                    mimeType: "multipart/form-data"
                }).done(function (res) { //
                    // django_form_checks.var.form_changed = 'changed';
                    console.log('upload complete');
                    var input_array = [];

                    // $(form_id)[0].reset(); //reset form
                    // $(result_output).html(res); //output response from server
                    var obj = JSON.parse(res);
                    if (obj['status'] == 'success') {
                        var input_id_obj = $('#' + input_id + '_json').val();

                        if (upload_type == 'multiple') {

                            if (input_id_obj.length > 0) {
                                input_array = JSON.parse(input_id_obj);
                            }

                            input_array.push(obj);
                            console.log(obj['doc_id']);
                            console.log(input_id);

                        } else {
                            input_array = obj
                        }
                    } else {
                        console.log(obj['message']);
                        error.push(obj['message']);
                        $(result_output).append('<div class="error">' + obj['message'] + '</div>');
                    }
                    $('#' + input_id + '_json').val(JSON.stringify(input_array));
                    // $('#'+input_id).val(JSON.stringify(input_array));
                    submit_btn.val("Upload").prop("disabled", false); //enable submit button once ajax is done
                    ajax_loader_django.showFiles(input_id, upload_type);
                    $('#' + input_id + '__submit__files').val('');
                }).fail(function (res) { //
                    console.log('failed');

                    $(result_output).append('<div class="error">Upload to Server Error</div>');
                    $('#progress-bar-indicator').attr('class', 'progress-bar progress-bar-danger');

                    var percent = '100';
                    $(progress_bar_id + " .progress-bar").css("width", + percent + "%");
                    $(progress_bar_id + " .status").text("0%");
                    $(progress_bar_id + " .status-text").text("error");
                    submit_btn.val("Upload").prop("disabled", false);
                });


            }
        }



        $(result_output).html(""); //reset output 
        $(error).each(function (i) { //output any error to output element
            $(result_output).append('<div class="error">' + error[i] + "</div>");
            $('#progress-bar-indicator').attr('class', 'progress-bar progress-bar-danger');
            var percent = '100';
            $(progress_bar_id + " .progress-bar").css("width", + percent + "%");
            $(progress_bar_id + " .status").text("0%");
            $(progress_bar_id + " .status-text").text("error");
            submit_btn.val("Upload").prop("disabled", false);
        });

    });
}

var ajax_loader_django = {
    autoUpload: function (upload_button_id) {
        $("#" + upload_button_id).click();
    },
    openUploader: function (input_id, upload_type) {

        // Get django csrf token. 
        var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

        var htmlvalue = "";
        //           htmlvalue += '<div id="uploadModal" class="modal fade" role="dialog">';
        htmlvalue += '<div id="' + input_id + '__uploadbox">';
        htmlvalue += '<div>';
        //            htmlvalue += '<div class="modal-dialog">';

        htmlvalue += '    <div class="card">';
        htmlvalue += '      <div class="card-header">';
        htmlvalue += '        <div class="row">';
        htmlvalue += '        <div class="col-6"><h4 class="modal-title">File Uploader</h4></div>';
        htmlvalue += '        <div class="col-6 text-end"><a style="font-size: 30px; text-decoration: none; color: red;" class="close" href="javascript:void(0)" onclick="ajax_loader_django.closeUploader(\'' + input_id + '\');" >&times;</a></div>';
        htmlvalue += '        </div>';
        
        htmlvalue += '      </div>';
        htmlvalue += '      <div class="card-body" >';
        htmlvalue += '      <form action="/applications-uploads/" method="post" enctype="multipart/form-data" id="upload_form" id="' + input_id + '__uploadform" >';
        htmlvalue += '      <input type="hidden" name="csrfmiddlewaretoken" value="' + csrfmiddlewaretoken + '" />';
        htmlvalue += '      <label class="custom-file">';
        //            htmlvalue += '  <input name="__files[]" type="file" ';
        htmlvalue += '  <input name="__files[]" id="' + input_id + '__submit__files" type="file" onchange="ajax_loader_django.autoUpload(' + "'" + input_id + "__submit'" + ');" ';

        if (upload_type == 'multiple') {
            // htmlvalue += '  multiple ';
        }

        htmlvalue += '  class="custom-file-input"';
        htmlvalue += '  >';
        htmlvalue += '  <span class="custom-file-control"></span>';
        htmlvalue += '</label>';
        htmlvalue += '<input name="__submit__" type="submit" class="btn btn-primary" id="' + input_id + '__submit" value="Upload"/>';
        htmlvalue += '</form>';
        htmlvalue += '<BR><BR>';

        htmlvalue += '<div id="' + input_id + '__submit-progress-wrp" class="progress">';
        htmlvalue += '  <div id="' + input_id + '__submit-progress-bar-indicator" class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width:0%">100%';
       // htmlvalue += '    <span class="status">0%</span> Complete (<span class="status-text">success</span>) ';
        htmlvalue += '  </div> ';
        htmlvalue += '</div>';
        htmlvalue += '<BR><BR>';
        htmlvalue += '<div istyle="float:left; " id="' + input_id + '__submit-showfiles"></div>';
        //            htmlvalue += '<div id="progress-wrp"><div class="progress-bar"></div ><div class="status">0%</div></div>';
        htmlvalue += '<div id="output"><!-- error or success results --></div>';
        //            htmlvalue += '</div>';
        //            htmlvalue += '<div class="modal-footer">';
        //            htmlvalue += '<BR><BR><button name="close" type="button" class="btn btn-primary" value="Close" class="close" data-dismiss="modal" value="Close">Close</button>';
        //            htmlvalue += '</div>';
        htmlvalue += '</div>';
        htmlvalue += '</div>';
        htmlvalue += '</div>';
        htmlvalue += '</div><BR>';

        // $('#myModal').modal({
        //        show: 'false'
        // }); 
        var htmlvalue1 = '';
        htmlvalue1 = '<div>test</div>';
        $('#' + input_id + '__uploader').html(htmlvalue);
        //$('+input_id+'__uploadbox).html(htmlvalue);

        //  $('html').prepend(htmlvalue);

        // $('#uploadModal').modal({
        //        show: 'false'
        // });
        //bindForm('#'+input_id+'__uploadform',input_id,upload_type);
        bindForm('#' + input_id + '__submit', input_id, upload_type);
        // bindForm('#upload_form',input_id,upload_type);
        ajax_loader_django.showFiles(input_id, upload_type);
    },
    showFiles: function (input_id, upload_type) {
        console.log("IN" + input_id)
        var input_id_obj = $('#' + input_id + '_json').val();
        var input_array = [];
        var htmlvalue = "<BR>";
        if (input_id_obj.length > 0) {
            console.log(upload_type);
            if (upload_type == 'multiple') {
                input_array = JSON.parse(input_id_obj);

                htmlvalue += '<div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">';
                var filecount = 1;
                for (var file in input_array) {
                    htmlvalue += '<div class="col-xs-9 col-sm-9 col-md-9 col-lg-9">';

                    //htmlvalue += filecount+'. <A HREF="/media/'+input_array[file].path+'">';
                    htmlvalue += filecount + '. <A HREF="/private-media/view/' + input_array[file].doc_id + '-file' + input_array[file].extension + '" target="new_tab_' + input_array[file].doc_id + '">';
                    if (input_array[file].name.length > 2) {
                        htmlvalue += input_array[file].name;
                    } else {
                        htmlvalue += input_array[file].short_name;
                    }
                    htmlvalue += '</a></div>';
                    htmlvalue += '<div class="col-xs-3 col-sm-3 col-md-3 col-lg-3">';
                    htmlvalue += '<A onclick="ajax_loader_django.deleteFile(\'' + input_id + '\',\'' + input_array[file].doc_id + '\',\'' + upload_type + '\')" href="javascript:void(0);"><span class="glyphicon glyphicon-remove" aria-hidden="true" style="color: red"></span></A>';
                    htmlvalue += '</div>';
                    filecount++;
                }

                htmlvalue += '</div>';

            } else {
                input_array = JSON.parse(input_id_obj);

                htmlvalue += '<div class="col-xs-9 col-sm-9 col-md-9 col-lg-9">';
                //htmlvalue += '<A HREF="/media/'+input_array.path+'">';
                htmlvalue += '<A HREF="/private-media/view/' + input_array.doc_id + '-file' + input_array.extension + '" target="new_tab_' + input_array.doc_id + '">';
                if (input_array.name.length > 2) {
                    htmlvalue += input_array.name;
                } else {
                    htmlvalue += input_array.short_name;
                }

                htmlvalue += '</A>';
                htmlvalue += '</div>';
                htmlvalue += '<div class="col-xs-3 col-sm-3 col-md-3 col-lg-3">';
                htmlvalue += '<A onclick="ajax_loader_django.deleteFile(\'' + input_id + '\',\'' + input_array.doc_id + '\',\'' + upload_type + '\')" href="javascript:void(0);"><span class="glyphicon glyphicon-remove" aria-hidden="true" style="color: red"></span></A>';
                htmlvalue += '</div>';
            }

            console.log(htmlvalue);
            //                  $('#'+input_id+'-showfiles').html(htmlvalue);
            $('#' + input_id + '__showfiles').html(htmlvalue);
        } else {
            $('#showfiles').html(htmlvalue);
            $('#' + input_id + '__showfiles').html(htmlvalue);
        }
    },
    deleteFile: function (input_id, file_id, upload_type) {
        console.log(input_id + ' ' + file_id);
        var input_id_obj = $('#' + input_id + '_json').val();
        // django_form_checks.var.form_changed = 'changed';
        if (upload_type == 'multiple') {

            if (input_id_obj.length > 0) {
                input_array = JSON.parse(input_id_obj);

                for (var file in input_array) {

                    if (input_array[file].doc_id == file_id) {
                        input_array.splice(file, 1);
                        console.log('Removed');
                    }
                }

                console.log(JSON.stringify(input_array));
                if (input_array != null) {
                    $('#' + input_id + '_json').val(JSON.stringify(input_array));
                    ajax_loader_django.showFiles(input_id, upload_type);
                } else {
                    $('#' + input_id + '_json').val('');
                    ajax_loader_django.showFiles(input_id, upload_type);
                }

            }
        } else {
            $('#' + input_id + '_json').val('');
            ajax_loader_django.showFiles(input_id, upload_type);
        }

    },
    closeUploader: function (input_id) {
        $('#' + input_id + '__uploader').html('');


    },
}
