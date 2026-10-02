<script>
import { goto } from '$app/navigation';
    const handleClick = () => {
        console.log('creating a vendor')
        goto('/vendors', { replaceState: true })
    };


</script>
<a href="/applications">Applications</a>


<button onclick={handleClick}>Create vendor</button>    

<a href="/vendors">Vendors</a>

<h3>List of vendors</h3>