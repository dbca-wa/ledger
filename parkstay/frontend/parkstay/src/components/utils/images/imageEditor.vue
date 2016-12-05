<template >
<div class="row" imageEditor>
    <div class="form-group">
        <div class="col-sm-12">
            <span class="btn btn-default btn-file">
                    <i class="fa fa-fw fa-camera"></i><input multiple ref="imagePicker" type="file" name='img' @change="readURL()" />
                </span>
            <button class="btn btn-primary" @click.prevent="clearImages">Clear All</button>
        </div>
    </div>
    <div class="form-group">
        <div class="col-sm-12">
            <div class="col-sm-12">
                <div class="upload">

                </div>
            </div>

        </div>
    </div>

</template>

<script>
import {
    $,
    slick
}
from '../../../hooks'
module.exports = {
    name: '',
    data: function() {
        let vm = this;
        return {
            slide: 0,
            images: [{
                caption: "",
                img: "data:image/jpeg;base64,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"
            }],
            slickCaro: null,
            slick_options: {
                dots: true,
                infinite: true,
                speed: 300,
                slidesToShow: 4,
                slidesToScroll: 4,
                responsive: [{
                    breakpoint: 1024,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3,
                        infinite: false,
                        dots: true
                    }
                }, {
                    breakpoint: 600,
                    settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2
                    }
                }, {
                    breakpoint: 480,
                    settings: {
                        slidesToShow: 1,
                        slidesToScroll: 1
                    }
                }]
            }
        }
    },
    components: {},
    methods: {
        clearImages: function() {
            let vm = this;
            for (var i = vm.slide; i >= 0; i--) {
                $('.upload').slick('slickRemove', i);
            }
            vm.images = [];
        },
        slick_init: function() {
            let vm = this;
            vm.slickCaro = $('.upload').slick(vm.slick_options);
        },
        readURL: function() {
            let vm = this;
            var input = vm.$refs.imagePicker;
            if (input.files && input.files[0]) {
                for (var i = 0; i < input.files.length; i++) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        vm.slide++
                            vm.images.push({
                                img: e.target.result,
                                caption: ''
                            });
                        var image =vm.images[vm.images.length-1]
                        var template = '<div class="panel panel-default"> \
                                        <div class="panel-body"> \
                                            <img src="'+image.img+'" class="img-thumbnail" alt="Responsive image" />\
                                            <div class="panel-footer">\
                                                <div class="row">\
                                                    <div class="col-lg-12">\
                                                        <div class="form-group">\
                                                            <input type="text" class="form-control" placeholder="Caption" v-model="'+image.caption+'">\
                                                        </div>\
                                                    </div>\
                                                </div>\
                                            </div>\
                                        </div>\
                                    </div>';
                        $('.upload').slick('slickAdd', template);
                        //$('.upload').slick('slickAdd', "<div><img src='" + e.target.result + "' class=\"img-thumbnail\" alt=\"Responsive image\"></div>");
                    };
                    reader.readAsDataURL(input.files[i]);
                }

            }
        }
    },
    mounted: function() {
        let vm = this;
        vm.slick_init();
    }
}

</script>

<style lang="css">
.upload .panel{
    box-shadow: 0 1px 6px 0 rgba(0, 0, 0, 0.12), 0 1px 6px 0 rgba(0, 0, 0, 0.12);
    border-radius: 2px;
    margin-right: 5px;
}
.upload img{
    height: 250px;
    width:250px;
}
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file-large{
    position: relative;
    overflow: hidden;
    width:96px;
    height:96px;
    font-size: 45px;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.slick-prev {
    left: -25px;
}
.slick-next {
    right:-25px;
}
@charset 'UTF-8';
/* Slider */
.slick-loading .slick-list
{
    background: #fff url('./ajax-loader.gif') center center no-repeat;
}

/* Arrows */
.slick-prev,
.slick-next
{
    font-size: 0;
    line-height: 0;

    position: absolute;
    top: 50%;

    display: block;

    width: 20px;
    height: 20px;
    margin-top: -10px;
    padding: 0;

    cursor: pointer;

    color: transparent;
    border: none;
    outline: none;
    background: #337ab7;
}
.slick-prev:hover,
.slick-prev:focus,
.slick-next:hover,
.slick-next:focus
{
    color: transparent;
    outline: none;
    background: #337ab7;
}
.slick-prev:hover:before,
.slick-prev:focus:before,
.slick-next:hover:before,
.slick-next:focus:before
{
    opacity: 1;
}
.slick-prev.slick-disabled:before,
.slick-next.slick-disabled:before
{
    opacity: .11;
}

.slick-prev:before,
.slick-next:before
{
    font: normal normal normal 14px/1 FontAwesome;
    text-rendering: auto;
    font-size: 20px;
    line-height: 1;

    opacity: .75;
    color: white;

    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

[dir='rtl'] .slick-prev
{
    right: -11px;
    left: auto;
}
.slick-prev:before
{
    content: '\f0a8';
}
[dir='rtl'] .slick-prev:before
{
    content: '\f0a8';
}

[dir='rtl'] .slick-next
{
    right: auto;
    left: -11px;
}
.slick-next:before
{
    content: '\f0a9';
}
[dir='rtl'] .slick-next:before
{
    content: '\f0a9';
}

/* Dots */
.slick-slider
{
    margin-bottom: 30px;
}

.slick-dots
{
    position: absolute;
    bottom: -45px;

    display: block;

    width: 100%;
    padding: 0;

    list-style: none;

    text-align: center;
}
.slick-dots li
{
    position: relative;

    display: inline-block;

    width: 20px;
    height: 20px;
    margin: 0 5px;
    padding: 0;

    cursor: pointer;
}
.slick-dots li button
{
    font-size: 0;
    line-height: 0;

    display: block;

    width: 20px;
    height: 20px;
    padding: 5px;

    cursor: pointer;

    color: transparent;
    border: 0;
    outline: none;
    background: transparent;
}
.slick-dots li button:hover,
.slick-dots li button:focus
{
    outline: none;
}
.slick-dots li button:hover:before,
.slick-dots li button:focus:before
{
    opacity: 1;
}
.slick-dots li button:before
{
    font-family: 'slick';
    font-size: 6px;
    line-height: 20px;

    position: absolute;
    top: 0;
    left: 0;

    width: 20px;
    height: 20px;

    content: '•';
    text-align: center;

    opacity: .25;
    color: black;

    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.slick-dots li.slick-active button:before
{
    opacity: .75;
    color: black;
}
</style>
