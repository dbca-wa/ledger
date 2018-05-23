<template lang="html">
    <div class="col-md-12">
        <div class="form-group">
            <div class="row">
                <div class="embed-container">
                    <iframe :width="width" :height="height" :frameborder="frameborder" :scrolling="scrolling" :marginheight="marginheight" :marginwidth="marginwidth" :title="title" :src="src"></iframe>
                </div>

<!--
              <iframe width="1000" height="800" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" title="Apiary Sites Beekeeper's Map (WBV)" src="http://dpaw.maps.arcgis.com/apps/Embed/index.html?webmap=d89e2089045c40dcb3d56bafc60dadb3&extent=95.5777,-38.2527,149.5425,-12.3581&home=true&zoom=true&scale=true&search=true&searchextent=true&details=true&basemap_gallery=true&disable_scroll=true&theme=light">
    </iframe>
-->
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:["src", "title", "name", "width", "height", "frameborder", "scrolling", "marginheight", "marginwidth"]
}
</script>

<style lang="css">
  .embed-container {
    position: relative; padding-bottom: 80%; height: 0; max-width: 100%;

  }

  .embed-container iframe,

  .embed-container object,

  .embed-container iframe{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  }
</style>
