<svelte:head>
	 <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</svelte:head>

<script>
	import Searchfield from './Searchfield.svelte'
	import Portfolio from './Portfolio.svelte'
	import Button, {Label} from '@smui/button';
	import Chart from './Chart.svelte'
	let portfolio = [];
	let availableTickers = [];
	let showChart = false;
	let dataFetch;
	$: console.log(portfolio);
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

</script>


<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
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

	<Button on:click={fetchData(portfolio)}>
	  <Label>Calculate Portfolio</Label>
	</Button>

	{#if showChart}
		<Chart bind:portfolio	bind:dataFetch />
	{/if}

</main>
