
module.exports = {
    status_history:function(id){
        return "/parkstay/api/campgrounds/" + id + "/status_history.json?closures=True";
    },
    regions:"/parkstay/api/regions.json",
    parks:"/parkstay/api/parks.json",
    districts:"/parkstay/api/districts.json",
    park_price_history:function (id) {
       return "/parkstay/api/parks/price_history.json";
    },
    park_add_price:function () {
       return "/parkstay/api/parks/add_price.json";
    },
    park_current_price:function (id,arrival) {
      return "/parkstay/api/parks/"+id+"/current_price.json?arrival="+arrival;
    },
    park_entry_rate:function (id) {
      return "/parkstay/api/parkentryrate/"+id+".json";
    },
    park:function (id) {
       return "/parkstay/api/parks/"+id+".json";
    },
    // Campgrounds
    campgrounds:"/parkstay/api/campgrounds.json",
    campgrounds_datatable:"/parkstay/api/campgrounds/datatable_list.json",
    bulk_close:"/parkstay/api/campgrounds/bulk_close.json",
    campground:function (id) {
        return "/parkstay/api/campgrounds/"+id+".json";
    },
    campground_price_history: function(id){
        return "/parkstay/api/campgrounds/"+ id +"/price_history.json";
    },
    campgroundStayHistory: function(id){
        return "/parkstay/api/campgrounds/" + id + "/stay_history.json"
    },
    campgroundCurrentStayHistory: function(id,start,end){
        return "/parkstay/api/campgrounds/" + id + "/stay_history.json?start="+start+"&end="+end;
    },
    campground_stay_history_detail: function(id){
        return "/parkstay/api/campground_stay_history/"+ id +".json";
    },
    available_campsite_classes:function (id,start,end) {
        return "/parkstay/api/campgrounds/" + id + "/available_campsite_classes.json?arrival="+start+"&departure="+end;
    },
    campground_stay_history: "/parkstay/api/campground_stay_history.json",
    addPrice: function(id){
        return "/parkstay/api/campgrounds/"+ id +"/addPrice.json";
    },
    editPrice: function(id){
        return "/parkstay/api/campgrounds/"+ id +"/updatePrice.json";
    },
    campgroundCampsites: function(id){
        return "/parkstay/api/campgrounds/" + id + "/campsites.json"
    },
    opencloseCG: function(id){
        return "/parkstay/api/campgrounds/" + id + "/open_close.json"
    },
    deleteBookingRange: function (id) {
        return "/parkstay/api/campground_booking_ranges/" + id + ".json"
    },
    campground_status_history_detail: function(id){
        return "/parkstay/api/campground_booking_ranges/"+ id +".json?original=true";
    },
    delete_campground_price: function(id){
        return "/parkstay/api/campgrounds/" + id + "/deletePrice.json";
    },
    // Campsites
    campsites:"/parkstay/api/campsites.json",
    campsites_stay_history: "/parkstay/api/campsites_stay_history.json",
    campsites_stay_history_detail: function(id){
        return "/parkstay/api/campsites_stay_history/"+ id +".json";
    },
    campsites_price_history: function(id){
        return "/parkstay/api/campsites/"+ id +"/price_history.json";
    },
    campsite_current_price:function (id,start,end) {
       return "/parkstay/api/campsites/"+ id +"/current_price.json?arrival="+start+"&departure="+end;
    },
    campsites_status_history:function(id){
        return "/parkstay/api/campsites/" + id + "/status_history.json?closures=True"
    },
    campsite:function (id) {
        return "/parkstay/api/campsites/"+id+".json";
    },
    campsiteStayHistory: function(id){
        return "/parkstay/api/campsites/" + id + "/stay_history.json"
    },
    opencloseCS: function(id){
        return "/parkstay/api/campsites/" + id + "/open_close.json"
    },
    deleteCampsiteBookingRange: function (id) {
        return "/parkstay/api/campsite_booking_ranges/" + id + ".json"
    },
    campsite_status_history_detail: function(id){
        return "/parkstay/api/campsite_booking_ranges/"+ id +".json?original=true";
    },
    available_campsites:function(campground,arrival,departure){
      return "/parkstay/api/campgrounds/"+campground+"/available_campsites.json?arrival="+arrival+"&departure="+departure;
    },
    features:"/parkstay/api/features.json",
    campsite_rate: "/parkstay/api/campsite_rate.json",
    campsiterate_detail:function (id) {
        return "/parkstay/api/campsite_rate/"+id+".json"
    },
    rates:"/parkstay/api/rates.json",

    // campsite types
    campsite_classes:"/parkstay/api/campsite_classes.json",
    campsite_classes_active:"/parkstay/api/campsite_classes.json?active_only=true",
    campsite_class:function (id) {
        return "/parkstay/api/campsite_classes/"+id+".json"
    },
    addCampsiteClassPrice: function(id){
        return "/parkstay/api/campsite_classes/"+id+"/addPrice.json"
    },
    editCampsiteClassPrice(id) {
        return "/parkstay/api/campsite_classes/"+id+"/updatePrice.json"
    },
    deleteCampsiteClassPrice(id) {
        return "/parkstay/api/campsite_classes/"+id+"/deletePrice.json"
    },
    campsiteclass_price_history: function(id){
        return "/parkstay/api/campsite_classes/"+ id +"/price_history.json";
    },
    closureReasons:function () {
        return "/parkstay/api/closureReasons.json";
    },
    openReasons:function () {
        return "/parkstay/api/openReasons.json";
    },
    priceReasons:function () {
        return "/parkstay/api/priceReasons.json";
    },
    maxStayReasons:function () {
        return "/parkstay/api/maxStayReasons.json";
    },
    bulkPricing: function(){
        return "/parkstay/api/bulkPricing";
    },
    //bookings
    bookings:"/parkstay/api/booking.json",
    booking: function(id){
        return "/parkstay/api/booking/"+id+".json";
    },
    //other
    countries:"https://restcountries.eu/rest/v1/?fullText=true",
    users: "/parkstay/api/users.json",
    usersLookup: function (q) {
       return  encodeURI("/parkstay/api/users.json?q="+q);
   },
   contacts:"/parkstay/api/contacts.json"
};
