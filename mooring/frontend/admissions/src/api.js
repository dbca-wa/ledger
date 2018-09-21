
module.exports = {
    
    park_price_history:function (id) {
       return global.parkstayUrl + "/api/admissions/price_history.json";
    },
    park_add_price:function () {
       return  global.parkstayUrl + "/api/admissions/add_price.json";
    },
    park_entry_rate:function (id) {
      return global.parkstayUrl + "/api/admissions/"+id+".json";
    },
    addPrice: function(id){
        return global.parkstayUrl + "/api/mooring-areas/"+ id +"/addPrice.json";
    },
    editPrice: function(id){
        return global.parkstayUrl + "/api/mooring-areas/"+ id +"/updatePrice.json";
    },
    addCampsiteClassPrice: function(id){
        return global.parkstayUrl + "/api/mooringsite_classes/"+id+"/addPrice.json"
    },
    editCampsiteClassPrice(id) {
        return global.parkstayUrl + "/api/admissions/"+id+"/updatePrice.json"
    },
    priceReasons:function () {
        return global.parkstayUrl + "/api/admissionsReasons.json";
    },
};
