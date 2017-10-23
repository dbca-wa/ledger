var merge = require('webpack-merge')
var prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  PARKSTAY_URL: '"https://parkstaybookings.dbca.wa.gov.au"'
})
