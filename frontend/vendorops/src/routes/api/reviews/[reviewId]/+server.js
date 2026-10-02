import { reviews } from "$lib/reviews.js";
import { json } from "@sveltejs/kit";

export function GET(requestEvent) {
    const { params } = requestEvent;
    const { reviewId } = params;
    const review = reviews.find((r) => r.id === parseInt(reviewId));
    if (!review) {
        return new Response("Review not found", { status: 404 });
    }
    return json(review);
}

export async function PATCH(requestEvent) {
    const { params, request } = requestEvent
    const { reviewId } = params
    const { text } = await request.json()
    const review = reviews.find((r) => r.id === parseInt(reviewId))
    if (!review) {
        return new Response("Review not found", { status: 404 })
    }
    review.text = text
    return json(review)
}



export async function DELETE(requestEvent) {
    const {params } = requestEvent
    const { reviewId} = params
    const deleteReview = reviews.find((r) => r.id === parseInt(reviewId))
    if (!deleteReview) {
        return new Response("Review not found", { status: 404 })
    }
    const index = reviews.indexOf(deleteReview)
    reviews.splice(index, 1)
    return new Response(null, { status: 204 })
}