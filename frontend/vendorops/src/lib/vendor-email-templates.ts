export interface VendorEmailTemplate {
  id: string;
  title: string;
  subject: string;
  body: string;
}

export const vendorEmailTemplates: VendorEmailTemplate[] = [
  {
    id: "welcome",
    title: "Welcome to The Good Flea",
    subject: "Welcome to The Good Flea community! 👋",
    body: `Hi [Vendor Name],

Welcome to The Good Flea! We are thrilled that you are interested in joining our vibrant community of creators, curators, and independent businesses.

Our markets are built on celebrating unique, high-quality goods and the passionate people behind them. Whether you are an established brand or just starting out, we are here to help you connect with an enthusiastic audience and grow your business.

Over the next few days, we’ll be sending you a little more information about who we are, what we look for in our partners, and how you can officially apply to pop up with us.

If you have any immediate questions, simply reply to this email. We can't wait to learn more about your brand!

Best,

The Good Flea Team`,
  },
  {
    id: "vendor-fit",
    title: "What Kind of Vendors We Are Looking For",
    subject: "What makes a great vendor at The Good Flea? ✨",
    body: `Hi [Vendor Name],

At The Good Flea, our goal is to curate a dynamic and diverse shopping experience for our attendees. To do that, we carefully review every application to ensure a great fit for both the vendor and the market.

So, what exactly are we looking for?

- Originality & Craftsmanship: We love vintage curators, handmade artisans, and independent designers who bring something unique to the table.
- Brand Presentation: A cohesive aesthetic, whether on your social media, website, or your physical booth setup, goes a long way.
- Community Spirit: We value vendors who are enthusiastic, collaborative, and ready to engage with our amazing market-goers.

We try to limit category overlap to ensure all our vendors have a successful weekend, which means our curation process is highly competitive. However, we are always on the lookout for fresh concepts and premium quality.

Keep an eye out for our next email, where we’ll walk you through exactly how our application process works!

Best,

The Good Flea Team`,
  },
  {
    id: "application-process",
    title: "How the Application Process Works",
    subject: "Your guide to The Good Flea application process 📋",
    body: `Hi [Vendor Name],

Ready to throw your hat in the ring? We want to make sure you know exactly what to expect when applying to The Good Flea.

Here is how our application and review process works:

1. Submit Your Application: Fill out our vendor application form with your brand details, social links, and a brief description of what you sell.
2. Review Period: Our curation team reviews applications on a rolling basis. We evaluate submissions based on category availability, product quality, and overall market fit.
3. The Decision: You will hear back from us via email regarding your status. You may be accepted, waitlisted (if your category is currently full), or declined.
4. Onboarding: If accepted, we will send over an invoice, a request for your Certificate of Insurance and Business License, and our official Information Packet.

It's that simple! In our final email tomorrow, we'll send you the direct link to view our calendar and apply for your preferred dates.

Best,

The Good Flea Team`,
  },
  {
    id: "upcoming-weekends",
    title: "Apply for Upcoming Weekends",
    subject: "Applications are OPEN: Apply for our upcoming market weekends! 🎪",
    body: `Hi [Vendor Name],

The time has come! We are currently accepting applications for our upcoming market season, and we would love to see your submission.

Our spots fill up incredibly fast, so we highly recommend securing your application as soon as possible. You can review all of our available dates and submit your official vendor application using the link below:

[Insert Link to Application / Dates]

Please be sure to double-check that you have included your most up-to-date website and social media links so our team can get a complete picture of your brand.

If you have any questions or run into any issues with the form, just reply directly to this email. We are looking forward to reviewing your application!

Best,

The Good Flea Team`,
  },
];