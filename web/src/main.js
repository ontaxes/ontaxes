import Vue from "vue";
import App from "./App.vue";
import Toasted from "vue-toasted";
import Carousel3d from "vue-carousel-3d";
import Tabs from "vue-tabs-component";
import Loading from "vue-loading-overlay";
import VModal from "vue-js-modal";
import VueQRCode from "@chenfengyuan/vue-qrcode";

Vue.use(Toasted);
Vue.use(Carousel3d);
Vue.use(Tabs);
Vue.use(Loading);
Vue.use(VModal);

Vue.component(VueQRCode.name, VueQRCode);

Vue.config.productionTip = false;

new Vue({
  render: h => h(App)
}).$mount("#app");
