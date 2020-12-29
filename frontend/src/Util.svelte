<script context="module">
	export function shuffle(arr)
	{
			arr.forEach((w, i) =>
			{
				const n = i + Math.floor(Math.random() * (arr.length-i));
				const tmp = arr[i];
				arr[i] = arr[n];
				arr[n] = tmp;
			});
	}	
</script>