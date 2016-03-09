define(['jQuery', 'handlebars', 'bootstrap'], function($, Handlebars) {
	var templates = {};
	 
	function appendTemplate(templateName, context, parentSelector) {	 
	    if (templates[templateName] === undefined) {
	      $.ajax({
	    	  url: '/static/hdb_templates/' + templateName + '.handlebars',
	    	  success: function(data) {
	    		  templates[templateName] = Handlebars.compile(data);
	    		  $(parentSelector).append(templates[templateName](context))
	    	  },
	    	  async: false
	      });
	    } else {
	    	$(parentSelector).append(templates[templateName](context))
	    }
	}

	function layoutChildren(children, childrenAnchorPointID, depth, hasMenu) {
		$.each(children, function(index, child) {
			var row = $('<div></div>').addClass('row');
			$('#' + childrenAnchorPointID).append(row);
			
			colClass = 'col-md-' + String(12-depth);
			colOffsetClass = 'col-md-offset-' + String(depth);
			col = $('<div></div>').addClass(colClass).addClass(colOffsetClass);

			// need to render childrenAnchorPointID in template, so add to context 
			if(child.childrenAnchorPointID !== undefined) {
				child.context.childrenAnchorPointID = child.childrenAnchorPointID;
				child.context.isHiddenInitially = child.children !== undefined;
			}

			appendTemplate(child.type, child.context, col);

			row.append(col);
			
			if(child.children !== undefined) {
				if(child.condition !== undefined) {
					var inputSelector = col.find('input, select');
					inputSelector.change(function(e) {
	                    if ($(this).val() === child.condition) {
	                    	$('#' + child.childrenAnchorPointID).slideDown('fast');
	                    } else {
	                    	$('#' + child.childrenAnchorPointID).hide();
	                    }
					});
				}
				layoutChildren(child.children, child.childrenAnchorPointID, depth + 1);
			}

			if(child.type === 'section' && hasMenu !== undefined && hasMenu) {
				var link = $('<a>');
				link.attr('href', '#' + child.context.id);
				link.text(child.context.label);
				$('#sectionList ul').append($('<li>').append(link));
			}
		});
	}

	return function(mainContainerSelector, formStructure) {
		appendTemplate('application_base', {
											hasMenu: formStructure.hasMenu,
											heading: formStructure.heading, 
											childrenAnchorPointID: formStructure.childrenAnchorPointID
											}, 
											mainContainerSelector);

		layoutChildren(formStructure.children, formStructure.childrenAnchorPointID, 0, formStructure.hasMenu);

		var sectionList = $('#sectionList');
		sectionList.scrollspy({ target: 'body' });
		sectionList.affix({ offset: { top: 200 }});
    };
});