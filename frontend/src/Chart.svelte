<script>
  import FusionCharts from 'fusioncharts';
  import Timeseries from 'fusioncharts/fusioncharts.timeseries';
  import SvelteFC, { fcRoot } from 'svelte-fusioncharts';

  fcRoot(FusionCharts, Timeseries);
  
  let promise, jsonify = res => res.json()

  export let dataFetch;
  
  let schemaFetch = fetch(
      'http://localhost/timeseries-schemas'
    ).then(jsonify);
  $: promise = Promise.all([dataFetch, schemaFetch]);

  const getChartConfig = ([data, schema]) => {
    const fusionDataStore = new FusionCharts.DataStore(),
      fusionTable = fusionDataStore.createDataTable(data, schema);

    return {
      type: 'timeseries',
      width: '100%',
      height: 450,
      renderAt: 'chart-container',
      dataSource: {
        data: fusionTable,
        caption: {
          text: 'Wealth Growth'
        },
        subcaption: {
          text: 'Grocery'
        },
        yAxis: [
          {
            plot: {
              value: 'Wealth Growth',
              type: 'line'
            },
            format: {
              suffix: 'x'
            },
            title: 'Wealth Growth'
          }
        ]
      }
    };
  };
</script>


{#await promise}
  <p>Fetching data and schema...</p>
{:then value}
  <div id="wealth-growth-chart">
  <SvelteFC
    {...getChartConfig(value)}/>
  </div>
{:catch error}
  <p>Something went wrong: {error.message}</p>
{/await}

<style type="text/css">
  #wealth-growth-chart {
    max-width: 900px;
  }
</style>