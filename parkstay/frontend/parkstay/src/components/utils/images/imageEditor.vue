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
            images: []
        }
    },
    components: {},
    methods: {
        clearImages:function () {
            let vm = this;
            for (var i = vm.slide; i >= 0 ;i-- ){
                $('.upload').slick('slickRemove', i);
            }
        },
        slick_init: function() {
            $('.upload').slick({
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
                    }
                    // You can unslick at a given breakpoint now by adding:
                    // settings: "unslick"
                    // instead of a settings object
                ]
            });
        },
        readURL: function() {
            let vm = this;
            var input = vm.$refs.imagePicker;
            console.log(input);
            if (input.files && input.files[0]) {
                for (var i = 0; i < input.files.length; i++) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        vm.slide++
                            $('.upload').slick('slickAdd', "<div><img src='" + e.target.result + "' class=\"img-thumbnail\" alt=\"Responsive image\"></div>");
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
