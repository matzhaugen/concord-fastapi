<script context="module">
class node
{
	constructor(val)
	{
		this.left = null;
		this.right = null;
		this.down = null;
		this.val = val;
		this.eow = false;
	}
}

export class TernarySearchTree
{
	constructor()
	{
		this._wordCount = 0;
		this._root = null;
		this._wild = '*';
	}

	get wordCount()
	{
		return this._wordCount;
	}

	_insert(n, word, i)
	{
		const c = word.charAt(i);
		if (n === null)
		{
			n = new node(c);
		}

		if (n.val === c)
		{
			if (i + 1 < word.length)
			{
				n.down = this._insert(n.down, word, i + 1);
			}
			else
			{
				n.eow = word;
			}
		}
		else if (c < n.val)
		{
			n.left = this._insert(n.left, word, i);
		}
		else
		{
			n.right = this._insert(n.right, word, i);
		}

		return n;
	}

	_search(n, word, i)
	{
		if (!n) return null;

		const c = word.charAt(i);
    if (c === n.val)
		{
			if (i < word.length - 1) n = this._search(n.down, word, i + 1);
		}
		else if (c < n.val)
		{
			n = this._search(n.left, word, i);
		}
		else
		{
			n = this._search(n.right, word, i);
		}

		return n;
	}

	_findWordsFrom(n, results)
	{
		if (!n) return;

		this._findWordsFrom(n.left, results);

		if (n.eow)
		{
			results.push(n.eow);
		}

		this._findWordsFrom(n.down, results);
		this._findWordsFrom(n.right, results);
	}

	prefixMatch(prefix)
	{
		const found = [];
    const searchFromNode = this._search(this._root, prefix, 0);
    if (searchFromNode)
		{
			if (searchFromNode.eow) found.push(searchFromNode.eow);
			this._findWordsFrom(this._search(this._root, prefix, 0).down, found);
		}
		return found;
	}

	_patternMatch(n, pattern, i, results)
	{
		if (!n) return;
		const c = pattern.charAt(i);
		if (c === n.val || c === this._wild)
		{
			if (i < pattern.length - 1)
			{
				this._patternMatch(n.down, pattern, i + 1, results);
			}
			else if (n.eow)
			{
				results.push(n.eow);
			}
		}

		this._patternMatch(n.left, pattern, i, results);
		this._patternMatch(n.right, pattern, i, results);
	}

	patternMatch(pattern)
	{
		const results = [];
		this._patternMatch(this._root, pattern, 0, results);
		return results;
	}

	search(word)
	{
		return this._search(this._root, word, 0);
	}

	addWord(word)
	{
		const n = this._insert(this._root, word, 0);
		if (this._root === null)
		{
			this._root = n;
		}
		this._wordCount++;
		return n;
	}
}
	
// Old code below just for reference - ignore
/*
class node
{
	constructor(val)
	{
		this.val = val;
		this.left = null;
		this.right = null;
		this.down = null;
		this.eow = false;
	}
}
	
export class TernarySearchTree
{
	constructor()
	{
		this.wild = '*';
		this.root = null;
	}
	
	addWords(words)
	{
		const self = this;
		let count = words.length-1;
		const aw = () =>
		{
			wordBeingAdded = words[count];
			self.addWord(words[count--]);
			if (count >=0)
			{
				setTimeout(aw, 1);
			}
		}
		
		aw();		
	}

	addWord(word)
	{
		if (!this.root)
    {
      this.root = new node(word.charAt(0));
    }
    
    // tracks the "linking" position (left, right, or down) once
    // a null node has been found
    let pos;
    
    // keeps track of the previous node
    let prev = null;
    
    // tracks the current node
    let curr = this.root;
    
    // tracks char position in word 
    let i = 0;
    
    // need to insert every char in word, so
    // loop as long as i isn't beyond word's length
    while (i < word.length)
    {
      prev = curr;
      let c = word.charAt(i);
      if (c === curr.val)
      {
        i++;  // next char
        curr = curr.down;  // move curr down to next child
        
        // when we've found a null node and it's time to create a new node
        // pos = 0, means it will be linked up in the "down" position
        pos = 0;
      }
      else if (c < curr.val)
      {
        curr = curr.left;  // c sorts left of current node, so move curr left
        pos = -1;          // link position is "left"
      }
      else
      {
        curr = curr.right;  // c sorts right of current node, so move curr right 
        pos = 1;            // link position is "right"
      }
      
      // if we've moved curr such that it's now null,
      // we might be done (past the end of the word), or
      // we might need to add new nodes
      if (!curr)
      {
        // if there are more chars in the word to deal with
        if (i < word.length)
        {
          // create a new node out of char at position i
          curr = new node(word.charAt(i));
          
          // determine if the new node should be linked up "down", "left", or "right"
          if (pos === -1) prev.left = curr;
          if (pos === 0) prev.down = curr;
          if (pos === 1) prev.right = curr;
        }
      }
    }
    
    // curr will be null at this point, but prev will be the node
    // representing the last char in the word. Thus, we are at
    // "eow" (end of word)
    prev.eow = true;
    
  }
  
  search(word, asPattern)
  {
    let prev = null;
    let start = null;
    let curr = this.root;
    let i = 0;
    while (i < word.length)
    {
      var c = word.charAt(i);

      if (!curr)
      {
        break;
      }
      
      prev = curr;
      if ((asPattern && c === this.wild) || curr.val === c)
      {
        start = start || curr;
        curr = curr.down;
        i++;
      }
      else if ((asPattern && c === this.wild) || c < curr.val)
      {
        curr = curr.left;
      }
      else if ((asPattern && c === this.wild) || c > curr.val)
      {
        curr = curr.right;
      }
    }
	console.log(i, word.length);
    return i === word.length && prev.eow && start;
  } 
  
  patternSearch(n, pattern, soFar, i, results)
  {
    if (!n)
    {
      return results;
    }
    
    var c = pattern.charAt(i);
    
    if (c === wild || c === n.val)
    {
      soFar.push(n.val);
      if (i+1 == pattern.length && n.eow)
      {
        results.push(soFar.join(''));
      }
      else
      {
        this.patternSearch(n.down, pattern, soFar, i+1, results);
      }
      soFar.pop();
    }
    
    
    if (c === wild || c < n.val)
    {
      this.patternSearch(n.left, pattern, soFar, i, results);
    }
    
    if (c === wild || c > n.val)
    {
      this.patternSearch(n.right, pattern, soFar, i, results);
    }
    
    return results;
  }
  
 	prefixMatch(prefix)
  {
    if (!prefix) throw 'prefix cannot be null or empty';
    let found = true;
    let prev = null;
    let curr = this.root;
    let i = 0;
    while (i < prefix.length)
    {
      if (!curr)
      {
        found = false;
        break;
      }
      
      prev = curr;
      var c = prefix.charAt(i);
      if (c === curr.val)
			{
				curr = curr.down;
				i++;
			}
      else if (c < curr.val)
      {
        curr = curr.left;
      }
      else
      {
        curr = curr.right;
      }
    }
    
    if (found)
    {
      var results = this.findWordsFrom(prev.down, [], []).map(function(el)
      {
        return prefix + el;
      });
      if (prev.eow) results.unshift(prefix);
      return results;
    }
    return [];
  }
  
  findWordsFrom(n, prefix, words)
  {
    let curr = n;
    
    if (!curr)
    {
      return words;
    }

    if (curr.left)
    {
      this.findWordsFrom(curr.left, prefix, words);
    }
    
    prefix.push(curr.val);
    
    if (curr.eow)
    {
      words.push(prefix.join(''));
    }
    
    
    if (curr.down)
    {
      this.findWordsFrom(curr.down, prefix, words);
    }
    
    prefix.pop();

    if (curr.right)
    {
      this.findWordsFrom(curr.right, prefix, words);
    }
    return words;
  }

  getAllWords()
  {
    return this.findWordsFrom(this.root, [], []);
  }
	
	get allWords()
	{
		return this.findWordsFrom(this.root, [], []);
	}
}
*/
</script>