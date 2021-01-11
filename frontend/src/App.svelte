<svelte:head>
	 <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</svelte:head>

<script>
	import Searchfield from './Searchfield.svelte'
	import Portfolio from './Portfolio.svelte'
	import Button, {Label} from '@smui/button';
	import Chart from './Chart.svelte'
	import Textfield from '@smui/textfield';
	let portfolio = [];
	let availableTickers = [];
	let showChart = false;
	let dataFetch;
	let valueTypeDate = '';
	function fetchData(portfolio) {
		if (portfolio.length > 1) {
			showChart = true;
	    dataFetch = fetch('http://localhost/portfolio-async', {
	      method: 'POST',
	      body: JSON.stringify({"tickers": portfolio, "endDate": "2000-01-01"})
	    }).then(res => res.json())
    } else {
			alert("Add at least 2 stocks to your portfolio.")
		}
  }

  $: console.log(valueTypeDate);

</script>


<style>

	main {
	  margin: 100px;
	  padding: 5px;
	}

	h1 {
		color: #3f51b5;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}
	.margins {
	    margin: 18px 60px 24px;
	}
	.columns {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
	}

</style>

<main>
	<h1>Concord Portfolio Optimizer!</h1>
	<p>Build your portfolio and see your wealth growth.</p>

	<Searchfield 
	bind:portfolio 
	bind:availableTickers/>

	<Portfolio 
	bind:portfolio 
	bind:availableTickers/>

	<div class="columns margins">
		<div>
			<Button on:click={fetchData(portfolio)}>
			  <Label>Calculate Portfolio</Label>
			</Button>
		</div>
		<div>
			<Textfield bind:value={valueTypeDate} label="End Date" type="date" />
		</div>
	</div>

	{#if showChart}
		<Chart bind:dataFetch />
	{/if}

</main>
