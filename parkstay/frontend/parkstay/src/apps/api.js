
module.exports = {
    status_history:function(id){
        return "/api/campgrounds/" + id + "/status_history.json?closures=True"
    },
    regions:"/api/regions.json",
    parks:"/api/parks.json",
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
        return "/api/booking_ranges/" + id + ".json"
    },
    features:"/api/features.json"
};
