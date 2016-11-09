
module.exports = {
    status_history:function(id){
        return "/api/campgrounds/" + id + "/status_history.json?closures=True"
    },
    regions:"/api/regions.json",
    campgrounds:"/api/campgrounds.json",

};
