<template lang="html" id="booking-dashboard">
<div class="row">
  <div class="col-lg-12">
      <div class="well">
          <div class="row">
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Campground</label>
                  <select class="form-control" name="">
                      <option value="">All</option>
                  </select>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Campground</label>
                  <select class="form-control" name="">
                      <option value="">All</option>
                  </select>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Campground</label>
                  <input type="text" class="form-control" id="" placeholder="">
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Campground</label>
                  <input type="text" class="form-control" id="" placeholder="">
                </div>
            </div>
            <div class="col-md-12">
                <button type="button" class="btn btn-primary pull-right">Add Booking</button>
            </div>
          </div>
          <div class="row">
            <div class="col-lg-12">
                <datatable id="bookings-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders"></datatable>
            </div>
          </div>
      </div>
  </div>
</div>
</template>

<script>
import datatable from '../utils/datatable.vue'
export default {
    name:'booking-dashboard',
    components:{
        datatable
    },
    data:function () {
        let vm =this;
        return {
            dtOptions:{

            },
            dtHeaders:["Campground","Region","Person","Confirmation #"," Campsite(Type)","Status","From","To","Action"]
        }
    }

}
</script>

<style lang="css">
</style>
