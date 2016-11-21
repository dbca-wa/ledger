
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
    features:"/api/features.json"
};
