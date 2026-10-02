import { reviews } from "$lib/reviews.js"
import { json } from "@sveltejs/kit";

export function GET() {
    return json(reviews);
}

export async function POST(requestEvent) {
    const { request } = requestEvent;
    const { text } =  await request.json();
    const newReview = {
        id: reviews.length + 1,
        text
    };
    reviews.push(newReview);
    return json(newReview, { status: 201 });
}

