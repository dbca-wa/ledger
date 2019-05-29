var webpack = require('webpack');

var VERSION = process.env.npm_package_version;

module.exports = {
    css: {
        extract: false,
        sourceMap: false
    },

    baseUrl: undefined,
    outputDir: '../../static/availability/'+VERSION,
    assetsDir: undefined,
    runtimeCompiler: undefined,
    productionSourceMap: undefined,
    parallel: undefined,
    
    configureWebpack: function (config) {
        // expose the init function as a global 
        config.output.library = 'availabilityApp';
        config.output.libraryTarget = 'var';
        config.output.libraryExport = 'default';
        
        // if production, remove the cache-hint hash from file names
        if (process.env.NODE_ENV === 'production') {
            config.output.filename = 'js/[name].js';
            config.output.chunkFilename = 'js/[name].js';
            config.optimization.splitChunks.cacheGroups.vendors.name = 'vendor';
        }

        // make bundled jQuery available in the global namespace
        config.plugins.push(
            new webpack.ProvidePlugin({
                $: 'jquery',
                jQuery: 'jquery',
                'window.jQuery': 'jquery'
            })
        );

    },

};
