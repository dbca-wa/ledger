var merge = require('webpack-merge')
var prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  PARKSTAY_URL: '"https://parkstay-ledger-uat.dpaw.aw.gov.au"'
})
