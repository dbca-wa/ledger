
module.exports = {
    status_history:function(id){
        return "/api/campgrounds/" + id + "/status_history.json?closures=True"
    },
    regions:"/api/regions.json",
    parks:"/api/parks.json",
    // Campgrounds
    campgrounds:"/api/campgrounds.json",
    campground:function (id) {
        return "/api/campgrounds/"+id+".json";
    },
    campground_price_history: function(id){
        return "/api/campgrounds/"+ id +"/price_history.json";
    },
    addPrice: function(id){
        return "/api/campgrounds/"+ id +"/addPrice.json";
    },
    editPrice: function(id){
        return "/api/campgrounds/"+ id +"/updatePrice.json";
    },
    campgroundCampsites: function(id){
        return "/api/campgrounds/" + id + "/campsites.json"
    },
    opencloseCG: function(id){
        return "/api/campgrounds/" + id + "/open_close.json"
    },
    deleteBookingRange: function (id) {
        return "/api/campground_booking_ranges/" + id + ".json"
    },
    campground_status_history_detail: function(id){
        return "/api/campground_booking_ranges/"+ id +".json?original=true";
    },
    delete_campground_price: function(id){
        return "/api/campgrounds/" + id + "/deletePrice.json";
    },
    // Campsites
    campsites:"/api/campsites.json",
    campsites_stay_history: "/api/campsites_stay_history.json",
    campsites_stay_history_detail: function(id){
        return "/api/campsites_stay_history/"+ id +".json";
    },
    campsites_price_history: function(id){
        return "/api/campsites/"+ id +"/price_history.json";
    },
    campsites_status_history:function(id){
        return "/api/campsites/" + id + "/status_history.json?closures=True"
    },
    campsite:function (id) {
        return "/api/campsites/"+id+".json";
    },
    campsiteStayHistory: function(id){
        return "/api/campsites/" + id + "/stay_history.json"
    },
    opencloseCS: function(id){
        return "/api/campsites/" + id + "/open_close.json"
    },
    deleteCampsiteBookingRange: function (id) {
        return "/api/campsite_booking_ranges/" + id + ".json"
    },
    campsite_status_history_detail: function(id){
        return "/api/campsite_booking_ranges/"+ id +".json?original=true";
    },
    features:"/api/features.json",
    campsite_rate: "/api/campsite_rate.json",
    campsiterate_detail:function (id) {
        return "/api/campsite_rate/"+id+".json"
    },
    rates:"/api/rates.json",

    // campsite types
    campsite_classes:"/api/campsite_classes.json",
    campsite_classes_active:"/api/campsite_classes.json?active_only=true",
    campsite_class:function (id) {
        return "/api/campsite_classes/"+id+".json"
    },
    addCampsiteClassPrice: function(id){
        return "/api/campsite_classes/"+id+"/addPrice.json"
    },
    editCampsiteClassPrice(id) {
        return "/api/campsite_classes/"+id+"/updatePrice.json"
    },
    deleteCampsiteClassPrice(id) {
        return "/api/campsite_classes/"+id+"/deletePrice.json"
    },
    campsiteclass_price_history: function(id){
        return "/api/campsite_classes/"+ id +"/price_history.json";
    },
    closureReasons:function () {
        return "/api/closureReasons.json";
    },
    openReasons:function () {
        return "/api/openReasons.json";
    },
    priceReasons:function () {
        return "/api/priceReasons.json";
    },
    maxStayReasons:function () {
        return "/api/maxStayReasons.json";
    },
    bulkPricing: function(){
        return "/api/bulkPricing";
    },
    //bookings
    bookings:"/api/booking.json",
    //other
    countries:"https://restcountries.eu/rest/v1/?fullText=true"
};
