
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
    campgroundCampsites: function(id){
        return "/api/campgrounds/" + id + "/campsites.json"
    },
    opencloseCG: function(id){
        return "/api/campgrounds/" + id + "/open_close.json"
    },
    deleteBookingRange: function (id) {
        return "/api/campground_booking_ranges/" + id + ".json"
    },
    // Campsites
    campsites:"/api/campsites.json",
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
    features:"/api/features.json"
};
