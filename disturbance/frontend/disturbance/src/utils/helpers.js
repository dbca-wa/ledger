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
  apiVueResourceError: function ( resp ) {
    var error_str = '';
    if ( resp.status === 400 ) {
      var text = resp.body[ 0 ];
      try {
        obj = JSON.parse( text );
        error_str = obj.non_field_errors[ 0 ].replace( /[\[\]"]/g, '' );
      }
      catch ( e ) {
        error_str = text.replace( /[\[\]"]/g, '' );
      }
    }
    else if ( resp.status === 404 ) {
      error_str = 'The resource you are looking for does not exist.';
    }
    return error_str;
  },
  goBack: function ( vm ) {
    vm.$router.go( window.history.back() );
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
        });

    },
    initialiseActionLogs: function(vm_uid,ref,datatable_options,table){
        let vm = this;
        let actionLogId = 'actions-log-table'+vm_uid;
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
        }).on('inserted.bs.popover', function () {
            table = $('#'+actionLogId).DataTable(datatable_options);
        });
    },
};
