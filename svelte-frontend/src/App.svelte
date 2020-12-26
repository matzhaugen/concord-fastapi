<script>
  import FusionCharts from 'fusioncharts';
  import Timeseries from 'fusioncharts/fusioncharts.timeseries';
  import SvelteFC, { fcRoot } from 'svelte-fusioncharts';

  fcRoot(FusionCharts, Timeseries);
  let result = null
  
  let possibleTickers = fetch("http://localhost/tickers").then(res => res.json())
  console.log(possibleTickers)
  let defaultTickers = ["AA", "AXP"]
  


  let promise,
    jsonify = res => res.json(),
    dataFetch = fetch('http://localhost/portfolio-async', {
      method: 'POST',
      body: JSON.stringify({"tickers": defaultTickers, "endDate": "2000-01-01"})
    }).then(jsonify),
    schemaFetch = fetch(
      'http://localhost/timeseries-schemas'
    ).then(jsonify);

  promise = Promise.all([dataFetch, schemaFetch]);

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
              prefix: '$'
            },
            title: 'Wealth Growth'
          }
        ]
      }
    };
  };
</script>

<p>Hi</p>
{#await promise}
  <p>Fetching data and schema...</p>
{:then value}
  <SvelteFC
    {...getChartConfig(value)}
  />
{:catch error}
  <p>Something went wrong: {error.message}</p>
{/await}