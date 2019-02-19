<template>
  <div id="app">
    <axes></axes>
  </div>
</template>

<script>
import Axes from "./components/Axes.vue";

export default {
  name: "app",
  components: {
    Axes
  }
};
</script>

<style>
body {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  font-size: 12px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
  padding: 0;
}
</style>
