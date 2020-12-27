<script>
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { shuffle } from './Util.svelte';
	import { TernarySearchTree } from './TernarySearchTree.svelte';
	
	const t = new TernarySearchTree();
	const tickersUrl = 'http://localhost/tickers';
	
	async function fetchWordsAsync()
	{
		const res = await fetch(tickersUrl);
		return await res.json();
	}	
	let promise = fetchWordsAsync();
	
	onMount(async () =>
	{
		const dictionary = await promise;
		const words = dictionary["tickers"];
		console.log(words)
		shuffle(words);
		words.forEach(w =>
		{
			addWordToTst(w);	
		});
	});
	
	let elapsed = 0;
	let asPattern = false;
	let searchText = '';
	$: findMatches = () =>
	{
		const then = performance.now();
		console.log(searchText)
		const results = (asPattern ? t.patternMatch : t.prefixMatch).call(t, searchText.toLowerCase());
		console.log(results)
		elapsed = Math.round((performance.now() - then)*100)/100;
		return results;
	}
	
	let wordCount = 0;
	function addWordToTst(w)
	{
		t.addWord(w);
		wordCount = t.wordCount;
	}
	
	$: matchedWords = findMatches();
	$: wordsToShow = matchedWords.slice(0,25);
</script>


{#await promise}
	<p>Loading words from the cloud...	</p>
{:then}
	<input type="text" placeholder="search" bind:value={searchText}/>

 <p>Total words: {wordCount} (loaded from <a href={tickersUrl}>{tickersUrl})</a></p>
	
{#if matchedWords.length}
	<p>Found {matchedWords.length} matches in {elapsed} ms (showing top {wordsToShow.length} results)</p>

	<div>
		Matches (are case insensitive):
		<ol>
			{#each wordsToShow as word}
				<li in:fly="{{ x: -300, duration: 750 }}" out:fade>{word}</li>
			{/each}
		</ol>
	</div>
{/if}

{/await}