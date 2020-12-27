<script>
	export let open = false
</script>

<button class="text-gray-500 hover:text-gray-700 cursor-pointer mr-4 border-none focus:outline-none" class:open on:click={() => open = !open}>
	<svg width=32 height=24>
		<line id="vertical" x1=16 y1=0  x2=16 y2=32/>
		<line id="horizontal" x1=0 y1=12 x2=32 y2=12/>
	</svg>
</button>

<style>
	svg {
		min-height: 24px;
		transition: transform 0.3s ease-in-out;
	}
	
	svg line {
		stroke: currentColor;
		stroke-width: 3;
		transition: transform 0.3s ease-in-out
	}
	
	button {
		z-index: 20;
	}
	
	.open svg {
		transform: scale(0.7)
	}
	
	.open #vertical {
		transform: translate(-6px, 0px) rotate(45deg)
	}
	
  .open #horizontal {
		transform: translate(-12px, 9px) rotate(-45deg)
	}
</style>