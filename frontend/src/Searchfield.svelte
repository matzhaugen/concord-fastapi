<script>
  import List, {Item} from '@smui/list';
  import Chip, {Set, Icon, Checkmark, Text} from '@smui/chips';
  import Textfield from '@smui/textfield';

  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { shuffle } from './Util.svelte';
  import { TernarySearchTree } from './TernarySearchTree.svelte';
  
  const t = new TernarySearchTree();
  const tickersUrl = 'http://localhost/tickerInfo';
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
    const words = await promise;
    var tickerDict = {}
    words.forEach(w => {
      tickerDict[w['ticker']] = w['name']
    })
    
    allWords = Object.keys(tickerDict);
    shuffle(words);
    words.forEach(w =>
    {
      addWordToTst(w["ticker"].toLowerCase());  
    });
  });
  
  let elapsed = 0;
  let asPattern = false;
  let searchText = '';
  $: findMatches = () =>
  {    
    const results = (asPattern ? t.patternMatch : t.prefixMatch).call(t, searchText.toLowerCase());
    return results.map(w => {return w.toUpperCase()});
  }
  
  function removePortfolioFromList(list, portfolio) {
    portfolio.forEach((ticker) => {
      let idx = list.indexOf(ticker);
      if (idx > -1) {
        list.splice(idx, 1);
        list = list;
      }
    })
    return list
  }
  let wordCount = 0;
  function addWordToTst(w)
  {
    t.addWord(w);
    wordCount = t.wordCount;
  }
  let matchedWords = []
  $: if (searchText == '') {
    availableTickers = removePortfolioFromList([...allWords], portfolio);
  } else {
    availableTickers = removePortfolioFromList(findMatches(), portfolio)
  }
  $: availableTickers = matchedWords.slice(0, 25)
    
  export let portfolio = []
  function addTicker(ticker) {
    if (!portfolio.includes(ticker)) {
      portfolio = [ticker, ...portfolio]
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