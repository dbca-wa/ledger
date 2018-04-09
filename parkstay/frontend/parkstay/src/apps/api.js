
module.exports = {
    regions:process.env.PARKSTAY_URL + "/api/regions.json",
    parks:process.env.PARKSTAY_URL + "/api/parks.json",
    districts:process.env.PARKSTAY_URL + "/api/districts.json",
    park_price_history:function (id) {
       return process.env.PARKSTAY_URL + "/api/parks/price_history.json";
    },
    park_add_price:function () {
       return process.env.PARKSTAY_URL + "/api/parks/add_price.json";
    },
    park_current_price:function (id,arrival) {
      return process.env.PARKSTAY_URL + "/api/parks/"+id+"/current_price.json?arrival="+arrival;
    },
    park_entry_rate:function (id) {
      return process.env.PARKSTAY_URL + "/api/parkentryrate/"+id+".json";
    },
    park:function (id) {
       return process.env.PARKSTAY_URL + "/api/parks/"+id+".json";
    },
    // Campgrounds
    campgrounds:process.env.PARKSTAY_URL + "/api/campgrounds.json",
    campgrounds_datatable:process.env.PARKSTAY_URL + "/api/campgrounds/datatable_list.json",
    bulk_close:process.env.PARKSTAY_URL + "/api/campgrounds/bulk_close.json",
    campground:function (id) {
        return process.env.PARKSTAY_URL + "/api/campgrounds/"+id+".json";
    },
    campground_status_history: function(id){
        return process.env.PARKSTAY_URL + "/api/campgrounds/" + id + "/status_history.json?closures=True";
    },
    campground_price_history: function(id){
        return process.env.PARKSTAY_URL + "/api/campgrounds/"+ id +"/price_history.json";
    },
    campgroundStayHistory: function(id){
        return process.env.PARKSTAY_URL + "/api/campgrounds/" + id + "/stay_history.json"
    },
    campgroundCurrentStayHistory: function(id,start,end){
        return process.env.PARKSTAY_URL + "/api/campgrounds/" + id + "/stay_history.json?start="+start+"&end="+end;
    },
    campground_stay_history_detail: function(id){
        return process.env.PARKSTAY_URL + "/api/campground_stay_history/"+ id +".json";
    },
    available_campsite_classes:function (id,start,end) {
        return process.env.PARKSTAY_URL + "/api/campgrounds/" + id + "/available_campsite_classes.json?arrival="+start+"&departure="+end;
    },
    campground_stay_history: process.env.PARKSTAY_URL + "/api/campground_stay_history.json",
    addPrice: function(id){
        return process.env.PARKSTAY_URL + "/api/campgrounds/"+ id +"/addPrice.json";
    },
    editPrice: function(id){
        return process.env.PARKSTAY_URL + "/api/campgrounds/"+ id +"/updatePrice.json";
    },
    campgroundCampsites: function(id){
        return process.env.PARKSTAY_URL + "/api/campgrounds/" + id + "/campsites.json"
    },
    campground_booking_ranges: function () {
        return process.env.PARKSTAY_URL + "/api/campground_booking_ranges.json"
    },
    campground_booking_ranges_detail: function (id) {
        return process.env.PARKSTAY_URL + "/api/campground_booking_ranges/" + id + ".json"
    },
    campground_status_history_detail: function(id){
        return process.env.PARKSTAY_URL + "/api/campground_booking_ranges/"+ id +".json?original=true";
    },
    delete_campground_price: function(id){
        return process.env.PARKSTAY_URL + "/api/campgrounds/" + id + "/deletePrice.json";
    },
    // Campsites
    campsites:process.env.PARKSTAY_URL + "/api/campsites.json",
    campsites_stay_history: process.env.PARKSTAY_URL + "/api/campsites_stay_history.json",
    campsites_stay_history_detail: function(id){
        return process.env.PARKSTAY_URL + "/api/campsites_stay_history/"+ id +".json";
    },
    campsites_price_history: function(id){
        return process.env.PARKSTAY_URL + "/api/campsites/"+ id +"/price_history.json";
    },
    campsite_current_price:function (id,start,end) {
       return process.env.PARKSTAY_URL + "/api/campsites/"+ id +"/current_price.json?arrival="+start+"&departure="+end;
    },
    campsites_current_price:function () {
        return process.env.PARKSTAY_URL + "/api/campsites/current_price_list.json";
     },
    campsite_status_history:function(id){
        return process.env.PARKSTAY_URL + "/api/campsites/" + id + "/status_history.json?closures=True"
    },
    campsite:function (id) {
        return process.env.PARKSTAY_URL + "/api/campsites/"+id+".json";
    },
    campsiteStayHistory: function(id){
        return process.env.PARKSTAY_URL + "/api/campsites/" + id + "/stay_history.json"
    },
    bulk_close_campsites: function () {
        return process.env.PARKSTAY_URL + "/api/campsites/bulk_close.json"
    },
    campsite_booking_ranges: function () {
        return process.env.PARKSTAY_URL + "/api/campsite_booking_ranges.json"
    },
    campsite_booking_ranges_detail: function (id) {
        return process.env.PARKSTAY_URL + "/api/campsite_booking_ranges/" + id + ".json"
    },
    campsite_status_history_detail: function(id){
        return process.env.PARKSTAY_URL + "/api/campsite_booking_ranges/"+ id +".json?original=true";
    },
    available_campsites:function(campground,arrival,departure){
      return process.env.PARKSTAY_URL + "/api/campgrounds/"+campground+"/available_campsites.json?arrival="+arrival+"&departure="+departure;
    },
    available_campsites_booking:function(campground,arrival,departure,booking){
      return process.env.PARKSTAY_URL + "/api/campgrounds/"+campground+"/available_campsites_booking.json?arrival="+arrival+"&departure="+departure+"&booking="+booking;
    },
    features:process.env.PARKSTAY_URL + "/api/features.json",
    campsite_rate: process.env.PARKSTAY_URL + "/api/campsite_rate.json",
    campsiterate_detail:function (id) {
        return process.env.PARKSTAY_URL + "/api/campsite_rate/"+id+".json"
    },
    rates:process.env.PARKSTAY_URL + "/api/rates.json",

    // campsite types
    campsite_classes:process.env.PARKSTAY_URL + "/api/campsite_classes.json",
    campsite_classes_active:process.env.PARKSTAY_URL + "/api/campsite_classes.json?active_only=true",
    campsite_class:function (id) {
        return process.env.PARKSTAY_URL + "/api/campsite_classes/"+id+".json"
    },
    addCampsiteClassPrice: function(id){
        return process.env.PARKSTAY_URL + "/api/campsite_classes/"+id+"/addPrice.json"
    },
    editCampsiteClassPrice(id) {
        return process.env.PARKSTAY_URL + "/api/campsite_classes/"+id+"/updatePrice.json"
    },
    deleteCampsiteClassPrice(id) {
        return process.env.PARKSTAY_URL + "/api/campsite_classes/"+id+"/deletePrice.json"
    },
    campsiteclass_price_history: function(id){
        return process.env.PARKSTAY_URL + "/api/campsite_classes/"+ id +"/price_history.json";
    },
    closureReasons:function () {
        return process.env.PARKSTAY_URL + "/api/closureReasons.json";
    },
    priceReasons:function () {
        return process.env.PARKSTAY_URL + "/api/priceReasons.json";
    },
    maxStayReasons:function () {
        return process.env.PARKSTAY_URL + "/api/maxStayReasons.json";
    },
    discountReasons:function (){
        return process.env.PARKSTAY_URL + "/api/discountReasons.json";
    },
    bulkPricing: function(){
        return process.env.PARKSTAY_URL + "/api/bulkPricing";
    },
    //bookings
    bookings:process.env.PARKSTAY_URL + "/api/booking.json",
    booking: function(id){
        return process.env.PARKSTAY_URL + "/api/booking/"+id+".json";
    },
    booking_refunds:process.env.PARKSTAY_URL + "/api/reports/booking_refunds",
    //other
    countries: process.env.PARKSTAY_URL + "/api/countries.json",
    users: process.env.PARKSTAY_URL + "/api/users.json",
    usersLookup: function (q) {
       return  encodeURI(process.env.PARKSTAY_URL + "/api/users.json?q="+q);
   },
   profile: process.env.PARKSTAY_URL + "/api/profile",
   contacts:process.env.PARKSTAY_URL + "/api/contacts.json"
};
