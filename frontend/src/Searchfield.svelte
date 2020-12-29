<script>
  import List, {Item} from '@smui/list';
  import Chip, {Set, Icon, Checkmark, Text} from '@smui/chips';
  import Textfield from '@smui/textfield';

  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { shuffle } from './Util.svelte';
  import { TernarySearchTree } from './TernarySearchTree.svelte';
  
  const t = new TernarySearchTree();
  const tickersUrl = 'http://localhost/tickers';
  let allWords = [];
  export let availableTickers = [];
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
    allWords = words;
    shuffle(words);
    words.forEach(w =>
    {
      addWordToTst(w.toLowerCase());  
    });
  });
  
  let elapsed = 0;
  let asPattern = false;
  let searchText = '';
  $: findMatches = () =>
  {
    const then = performance.now();
    const results = (asPattern ? t.patternMatch : t.prefixMatch).call(t, searchText.toLowerCase());
    elapsed = Math.round((performance.now() - then)*100)/100;
    return results.map(w => {return w.toUpperCase()});
  }
  
  let wordCount = 0;
  function addWordToTst(w)
  {
    t.addWord(w);
    wordCount = t.wordCount;
  }
  $: matchedWords = findMatches();
  $: if (searchText == '') {
      availableTickers = allWords
    } else {
      availableTickers = matchedWords.slice(0,25)
    }
  
  
  export let portfolio = ["AA", "AXP"]
  let filter = ['Shoes', 'Shirts'];
  function addTicker(ticker) {
    if (!portfolio.includes(ticker)) {
      portfolio = [ticker, ...portfolio]  
    }
    let idx = availableTickers.indexOf(ticker);
    if (idx > -1) {
      availableTickers.splice(idx, 1);
      availableTickers = availableTickers;
    }
  }
</script>

<Textfield bind:value={searchText} label="Search Ticker"/>
<div class="available-tickers">
  <pre> Available Tickers </pre>
<List>
  {#each availableTickers as ticker}
    <Chip><Icon on:click={addTicker(ticker)} class="material-icons" leading>add</Icon><Text>{ticker}</Text></Chip>
  {/each}
</List>
</div>

<style>
  .available-tickers {
    max-width: 600px;
  }
</style>