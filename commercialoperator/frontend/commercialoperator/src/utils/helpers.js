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
  add_endpoint_join: function ( api_string, addition ) {
    // assumes api_string has trailing forward slash "/" character required for POST
    return api_string + addition;
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
