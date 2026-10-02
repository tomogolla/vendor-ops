<script>
    import { page } from "$app/stores"
    const {vendorId, reviewId} = $page.params
</script>

<h1>Vendor review details page</h1>
<p>Vendor ID: {vendorId}</p>
<p>Review ID: {reviewId}</p>