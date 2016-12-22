<template id="modal">
    <div class="modal fade bs-example-modal-lg" tabindex="-1" role="dialog" aria-labelledby="myLargeModalLabel" @click="close" v-show="isModalOpen">
      <div class="modal-dialog modal-lg" role="document" @click.stop>
        <div class="modal-content">
            <slot></slot>
        </div>
      </div>
    </div>
</template>

<script>

module.exports = {
    name: 'modal',
    //props: ['onClose'],
    computed: {
        isModalOpen: function(){
            return this.$parent.isModalOpen;
        }
    },
    methods: {
        close: function (){
            this.$parent.close();
        },
        addCloseEvent: function (){
            document.addEventListener("keydown", (e) => {
                if (this.isModalOpen && e.keyCode == 27){
                    this.close();
                }
            });
        },

    },
    mounted: function () {
        this.addCloseEvent();
    }
};
</script>

<style>
    .modal-mask {
      position: fixed;
      z-index: 9998;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, .5);
      display: table;
      transition: opacity .3s ease;
    }

    .modal-container {
      width: 600px;
      margin: 0px auto;
      padding: 20px 30px;
      background-color: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
      transition: all .3s ease;
      font-family: Helvetica, Arial, sans-serif;
    }

    .modal-header h3 {
      margin-top: 0;
      color: #42b983;
    }

    .modal-body {
      margin: 20px 0;
    }

    .text-right {
        text-align: right;
    }

    .form-label {
        display: block;
        margin-bottom: 1em;
    }

    .form-label > .form-control {
        margin-top: 0.5em;
    }

    .form-control {
        display: block;
        width: 100%;
        padding: 0.5em 1em;
        line-height: 1.5;
        border: 1px solid #ddd;
    }

    .modal-enter, .modal-leave {
        opacity: 0;
    }

    .modal-enter .modal-container,
    .modal-leave .modal-container {
        -webkit-transform: scale(1.1);
        transform: scale(1.1);
    }
</style>
