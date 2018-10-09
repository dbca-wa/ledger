var path = require('path')
var utils = require('./utils')
var config = require('../config')
var vueLoaderConfig = require('./vue-loader.conf')
var webpack = require('webpack');

function resolve (dir) {
  return path.join(__dirname, '..', dir)
}

module.exports = {
  entry: {
    "babel-polyfill": "babel-polyfill", 
    "app": "./src/main.js"
  },
  output: {
    path: config.build.assetsRoot,
    filename: '[name].js',
    publicPath: process.env.NODE_ENV === 'production'
      ? config.build.assetsPublicPath
      : config.dev.assetsPublicPath
  },
  resolve: {
    extensions: ['.js', '.vue', '.json'],
    alias: {
      'vue$': 'vue/dist/vue.esm.js',
      '@': resolve('src'),
      '@vue-utils': resolve('src/utils/vue'),
      '@common-utils': resolve('src/components/common/'),
      'datetimepicker':'eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js',
      'easing':'jquery.easing/jquery.easing.js'
    }
  },
  module: {
    rules: [
      /*{
        test: /\.(js|vue)$/,
        loader: 'eslint-loader',
        enforce: 'pre',
        include: [resolve('src'), resolve('test')],
        options: {
          formatter: require('eslint-friendly-formatter')
        }
      },*/
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: vueLoaderConfig
      },
      {
        test: /bootstrap.+\.(js)$/,
        loader: 'imports-loader?jQuery=jquery,$=jquery,this=>window'
      },
      {
          test: /jquery.easing.+\.(js)$/,
          loader: 'imports-loader?jQuery=jquery,$=jquery,this=>window'
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        include: [resolve('src'), resolve('test')]
      },
      {
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: utils.assetsPath('img/[name].[hash:7].[ext]')
        }
      },
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: utils.assetsPath('fonts/[name].[hash:7].[ext]')
        }
      },
      {
        test: /datatables\.net.*/,
        loader: 'imports-loader?define=>false,jquery=>jquery,$=>jquery'
      }  
    ]
  },
  plugins:[
        new webpack.ProvidePlugin({
           $: "jquery",
           jQuery: "jquery",
           "select2": "../node_modules/select2/dist/js/select2.full.min.js",
           moment: "moment",
           swal: 'sweetalert2',
           _: 'lodash',
           datetimepicker:"../node_modules/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js"
       })
    ]
}
