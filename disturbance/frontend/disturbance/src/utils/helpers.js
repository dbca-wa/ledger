module.exports = {
  apiError: function ( resp ) {
    var error_str = '';
    if ( resp.status === 400 ) {
      try {
        obj = JSON.parse( resp.responseText );
        error_str = obj.non_field_errors[ 0 ].replace( /[\[\]"]/g, '' );
      }
      catch ( e ) {
        error_str = resp.responseText.replace( /[\[\]"]/g, '' );
      }
    }
    else if ( resp.status === 404 ) {
      error_str = 'The resource you are looking for does not exist.';
    }
    else {
      error_str = resp.responseText.replace( /[\[\]"]/g, '' );
    }
    return error_str;
  },
    apiVueResourceError: function(resp){
        var error_str = '';
        var text = null;
        if (resp.status === 400) {
            if (Array.isArray(resp.body)){
                text = resp.body[0];
            }
            else if (typeof resp.body == 'object'){
                text = resp.body;
            }
            else{
                text = resp.body;
            }

            if (typeof text == 'object'){
                if (text.hasOwnProperty('non_field_errors')) {
                    error_str = text.non_field_errors[0].replace(/[\[\]"]/g, '');
                }
                else{
                    error_str = text;
                }
            }
            else{
                error_str = text.replace(/[\[\]"]/g,'');
                error_str = text.replace(/^['"](.*)['"]$/, '$1');
            }
        }
        else if ( resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        }
        return error_str;
    },

  goBack: function ( vm ) {
    vm.$router.go( window.history.back() );
  },
  copyObject: function(obj){
        return JSON.parse(JSON.stringify(obj));
  },
  getCookie: function ( name ) {
    var value = null;
    if ( document.cookie && document.cookie !== '' ) {
      var cookies = document.cookie.split( ';' );
      for ( var i = 0; i < cookies.length; i++ ) {
        var cookie = cookies[ i ].trim();
        if ( cookie.substring( 0, name.length + 1 )
          .trim() === ( name + '=' ) ) {
          value = decodeURIComponent( cookie.substring( name.length + 1 ) );
          break;
        }
      }
    }
    return value;
  },
  namePopover: function ( $, vmDataTable ) {
    vmDataTable.on( 'mouseover', '.name_popover', function ( e ) {
      $( this )
        .popover( 'show' );
      $( this )
        .on( 'mouseout', function () {
          $( this )
            .popover( 'hide' );
        } );
    } );
  },
  add_endpoint_json: function ( string, addition ) {
    var res = string.split( ".json" )
    return res[ 0 ] + '/' + addition + '.json';
  },
    initialiseCommLogs: function(vm_uid,ref,datatable_options,table){
        let vm = this;
        let commsLogId = 'comms-log-table'+vm_uid;
        let popover_name = 'popover-'+ vm._uid;
        $(ref).popover({
            content: function() {
                return ` 
                <table id="${commsLogId}" class="hover table table-striped table-bordered dt-responsive " cellspacing="0" width="100%">
                </table>`
            },
            html: true,
            title: 'Communications Log',
            container: 'body',
            placement: 'right',
            trigger: "click",
            template: `<div class="popover ${popover_name}" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>`,
        }).on('inserted.bs.popover', function () {
            table = $('#'+commsLogId).DataTable(datatable_options);

            // activate popover when table is drawn.
            table.on('draw.dt', function () {
                var $tablePopover = $(this).find('[data-toggle="popover"]');
                if ($tablePopover.length > 0) {
                    $tablePopover.popover();
                    // the next line prevents from scrolling up to the top after clicking on the popover.
                    $($tablePopover).on('click', function (e) {
                        e.preventDefault();
                        return true;
                    });
                }
            });
        }).on('shown.bs.popover', function () {
            var el = ref;
            var popoverheight = parseInt($('.'+popover_name).height());

            var popover_bounding_top = parseInt($('.'+popover_name)[0].getBoundingClientRect().top);
            var popover_bounding_bottom = parseInt($('.'+popover_name)[0].getBoundingClientRect().bottom);

            var el_bounding_top = parseInt($(el)[0].getBoundingClientRect().top);
            var el_bounding_bottom = parseInt($(el)[0].getBoundingClientRect().top);
            
            var diff = el_bounding_top - popover_bounding_top;

            var position = parseInt($('.'+popover_name).position().top);
            var pos2 = parseInt($(el).position().top) - 5;

            var x = diff + 5;
            $('.'+popover_name).children('.arrow').css('top', x + 'px');
        });

    },
    initialiseActionLogs: function(vm_uid,ref,datatable_options,table){
        let vm = this;
        let actionLogId = 'actions-log-table'+vm_uid;
        let popover_name = 'popover-'+ vm._uid;
        $(ref).popover({
            content: function() {
                return ` 
                <table id="${actionLogId}" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                    <thead>
                        <tr>
                            <th>Who</th>
                            <th>What</th>
                            <th>When</th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>`
            },
            html: true,
            title: 'Action Log',
            container: 'body',
            placement: 'right',
            trigger: "click",
            template: `<div class="popover ${popover_name}" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>`,
        }).on('inserted.bs.popover', function () {
            table = $('#'+actionLogId).DataTable(datatable_options);
        }).on('shown.bs.popover', function () {
            var el = ref;
            var popoverheight = parseInt($('.'+popover_name).height());

            var popover_bounding_top = parseInt($('.'+popover_name)[0].getBoundingClientRect().top);
            var popover_bounding_bottom = parseInt($('.'+popover_name)[0].getBoundingClientRect().bottom);

            var el_bounding_top = parseInt($(el)[0].getBoundingClientRect().top);
            var el_bounding_bottom = parseInt($(el)[0].getBoundingClientRect().top);
            
            var diff = el_bounding_top - popover_bounding_top;

            var position = parseInt($('.'+popover_name).position().top);
            var pos2 = parseInt($(el).position().top) - 5;

            var x = diff + 5;
            $('.'+popover_name).children('.arrow').css('top', x + 'px');
        });
    },
    dtPopover: function(value,truncate_length=30,trigger='hover'){
        var ellipsis = '...',
        truncated = _.truncate(value, {
            length: truncate_length,
            omission: ellipsis,
            separator: ' '
        }),
        result = '<span>' + truncated + '</span>',
        popTemplate = _.template('<a href="#" ' +
            'role="button" ' +
            'data-toggle="popover" ' +
            'data-trigger="'+trigger+'" ' +
            'data-placement="top auto"' +
            'data-html="true" ' +
            'data-content="<%= text %>" ' +
            '>more</a>');
        if (_.endsWith(truncated, ellipsis)) {
            result += popTemplate({
                text: value
            });
        }
        return result;
    },
    dtPopoverCellFn: function(cell){
        $(cell).find('[data-toggle="popover"]')
            .popover()
            .on('click', function (e) {
                e.preventDefault();
                return true;
            });
    } 
};
