<script>
	import List, {Item, Meta} from '@smui/list';
	import Chip, {Set, Icon, Checkmark, Text} from '@smui/chips';
	import Textfield from '@smui/textfield';
	export let portfolio;
	export let availableTickers;

	let removeTicker = ticker => {
		let idx = portfolio.indexOf(ticker);
		if (idx > -1) {
			portfolio.splice(idx, 1);
			portfolio = portfolio;
		}
		availableTickers = [...availableTickers, ticker]	
	}
</script>

<div class="portfolio-list">
  <pre> Portfolio </pre>
<List>
  {#each portfolio as ticker}
    
      <Chip id={ticker}><Text>{ticker}</Text><Icon on:click={removeTicker(ticker)} class="material-icons" trailing tabindex="0">cancel</Icon></Chip>
    
  {/each}
</List>
</div>

<style type="text/css">
	.portfolio-list {
		max-width: 600px;
	}
</style>
