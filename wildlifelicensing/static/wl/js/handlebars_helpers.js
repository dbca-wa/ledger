define(['handlebars.runtime'], function(Handlebars) {
    Handlebars.registerHelper('isEqual', function(lvalue, rvalue, options) {
        if (arguments.length < 3)
            throw new Error("Handlebars Helper equal needs 2 parameters");
        if(lvalue != rvalue ) {
            return options.inverse(this);
        } else {
            return options.fn(this);
        }
    });

    Handlebars.registerHelper('getURLFilename', function(url) {
        return new Handlebars.SafeString(url.substr(url.lastIndexOf('/') + 1));
    });
});