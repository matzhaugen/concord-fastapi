<script>
  
  import Sidebar from './Sidebar.svelte'
  import Navbar from './Navbar.svelte'
  import Chart from './Chart.svelte'
  import Autocomplete from './Autocomplete.svelte'
  let open = false
  let defaultTickers = ["AA", "AXP"]
</script>

<svelte:head>
  <link href="https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css" rel="stylesheet"/>
</svelte:head>

<style>
  .chart {
    float: right;
    width: 75%;
  }
  .portfolio {
    float: right;
    width: 75%;
  }

  .searchbox {
    float: left;
    width: 25%;
  }
</style>

<div class="searchbox">
  <Autocomplete/>
</div>

<div class="chart">
  <Chart bind:defaultTickers={defaultTickers}/>
</div>

<div class="portfolio">
{#each defaultTickers as ticker}
  <ul><li>{ticker}</li></ul>
{/each}
</div>


