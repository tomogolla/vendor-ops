export type Question = {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'multi-select' | 'datetime-local' | 'checkbox' | 'email' | 'tel' | 'url' | 'number' | 'date' | 'checkbox-group' | 'multi-date';
  options?: readonly string[];
  description?: string;
  max?: number;
  required?: boolean;
};
export type QuestionSection = { title: string; description?: string; questions: Question[] };

export const agreedWeekendOptions = [
  'October 10 & 11',
  'October 17 & 18',
  'October 24 & 25',
  'October 31 & November 1',
  'November 7 & 8',
  'November 14 & 15',
  'November 21 & 22',
  'November 28 & 29',
  'December 5 & 6',
  'December 12 & 13',
  'December 19 & 20',
  'December 26 & 27'
] as const;

export const questionnaire: QuestionSection[] = [
  {
    "title": "1. Core Brand & Contact Verification",
    "description": "Verify or update the lead’s basic contact details.",
    "questions": [
      {
        "name": "business_name",
        "label": "Brand Name",
        "type": "text",
        "max": 200,
        "required": true,
        "description": "Can you confirm your brand name?"
      },
      {
        "name": "vendor_contact_name",
        "label": "Contact Name",
        "type": "text",
        "max": 200,
        "description": "Who is the best point of contact for all market operations?"
      },
      {
        "name": "phone_number",
        "label": "Phone Number",
        "type": "tel",
        "max": 40,
        "description": "What is the best direct phone number for billing and market-day updates?"
      },
      {
        "name": "email",
        "label": "Email Address",
        "type": "email",
        "max": 254,
        "description": "What is the best email address for billing and market-day updates?"
      },
      {
        "name": "website_url",
        "label": "Website URL",
        "type": "url",
        "max": 2048,
        "description": "Where can we review your current catalog?"
      },
      {
        "name": "instagram_handle",
        "label": "Instagram Handle",
        "type": "text",
        "max": 31,
        "description": "What is your Instagram handle?"
      }
    ]
  },
  {
    "title": "2. Product & Brand Qualification",
    "questions": [
      {
        "name": "product_category",
        "label": "Product Category",
        "type": "select",
        "options": [
          "Apparel/Fashion",
          "Jewelry & Accessories",
          "Beauty & Wellness",
          "Home Goods",
          "Vintage/Thrift",
          "Art & Craft",
          "Pre-Packaged Food",
          "Other"
        ],
        "description": "How would you categorize the products you plan to sell with us?"
      },
      {
        "name": "price_point_range",
        "label": "Price Point Range",
        "type": "text",
        "max": 200,
        "description": "What is your typical product price point range (e.g., $15–$50, $50–$150)?"
      },
      {
        "name": "brand_description_aesthetic",
        "label": "Brand Description & Aesthetic",
        "type": "textarea",
        "description": "How would you describe your brand aesthetic and visual setup?"
      },
      {
        "name": "readiness_level",
        "label": "Readiness Level",
        "type": "select",
        "options": [
          "Ready Now",
          "Needs 1–2 Weeks",
          "Exploring Options"
        ],
        "description": "Do you have your booth display, point-of-sale system, and inventory fully prepared for an upcoming weekend?"
      }
    ]
  },
  {
    "title": "3. Market Logistics & Setup Needs",
    "questions": [
      {
        "name": "previous_market_experience",
        "label": "Previous Market Experience",
        "type": "select",
        "options": [
          "First-Time Vendor",
          "Experienced Pop-Up Vendor",
          "Returning Good Flea Vendor"
        ],
        "description": "Have you participated in weekend pop-up markets in Downtown NYC before, or will this be your first time?"
      },
      {
        "name": "equipment_needs",
        "label": "Equipment & Electricity Needs",
        "type": "checkbox-group",
        "options": [
          "Standard Space",
          "Table Needed",
          "Rack Space",
          "Electricity Access"
        ],
        "description": "What booth size or equipment rental will you require for your setup?"
      },
      {
        "name": "operational_placement_notes",
        "label": "Operational / Placement Notes",
        "type": "textarea",
        "description": "Do you have any unique setup requirements or neighbor positioning preferences we should record for the Market Manager?"
      }
    ]
  },
  {
    "title": "4. Commercial Terms & Date Selection",
    "questions": [
      {
        "name": "target_market_dates",
        "label": "Target Market Dates",
        "type": "multi-date",
        "description": "Which upcoming weekend dates are you looking to participate in? Add each requested calendar date. These are requests; confirmed bookings remain in Market Weekends."
      },
      {
        "name": "booking_type",
        "label": "Booking Type",
        "type": "select",
        "options": [
          "Single Weekend",
          "Multi-Weekend Package",
          "Recurring Seasonal Vendor"
        ],
        "description": "Are you open to reserving multiple weekend dates across the quarter to secure continuous vendor presence and locked-in rates?"
      },
      {
        "name": "agreed_pricing",
        "label": "Agreed Pricing ($)",
        "type": "number",
        "description": "Record the agreed rate in USD. Include discounts or per-date pricing details in Call Summary & Notes."
      },
      {
        "name": "invoice_email",
        "label": "Invoice Email",
        "type": "email",
        "max": 254,
        "description": "Based on your selected dates and footprint, we agreed on [Rate/Discount]. Should we send the Shopify invoice directly to your primary email? Record the confirmed billing email."
      }
    ]
  },
  {
    "title": "5. Expectations, Feedback & Objection Handling",
    "questions": [
      {
        "name": "primary_vendor_goal",
        "label": "Primary Vendor Goal",
        "type": "select",
        "options": [
          "High Sales Volume",
          "Brand Awareness",
          "Product Testing",
          "Content Creation"
        ],
        "description": "What is your top priority for joining The Good Flea?"
      },
      {
        "name": "objections_concerns",
        "label": "Objections / Concerns Raised",
        "type": "textarea",
        "description": "What main questions or hesitations do you have about foot traffic, load-in, or booth layout before locking in your spot?"
      },
      {
        "name": "historical_vendor_feedback",
        "label": "Historical Vendor Feedback",
        "type": "textarea",
        "description": "If returning: how was your experience during your last market with us, and is there anything operational we can adjust for your next booking?"
      }
    ]
  },
  {
    "title": "6. Representative Call Outcome & Handoff",
    "description": "Complete after the call. Pipeline selections record the representative’s assessment; invoice and payment actions remain separate.",
    "questions": [
      {
        "name": "lead_qualification",
        "label": "Lead Qualification",
        "type": "select",
        "options": [
          "Qualified & Ready",
          "Needs Follow-Up",
          "Deferred",
          "Not a Fit"
        ]
      },
      {
        "name": "vendor_pipeline_stage",
        "label": "Vendor Pipeline Stage",
        "type": "select",
        "options": [
          "Call Completed -> Pending Invoice",
          "Invoice Sent -> Awaiting Payment",
          "Booked & Paid",
          "Closed / Rejected"
        ]
      },
      {
        "name": "next_action_required",
        "label": "Next Action Required",
        "type": "select",
        "options": [
          "Send Shopify Draft Invoice",
          "Send Follow-Up Email",
          "Schedule Second Call",
          "Pass to Market Ops"
        ]
      },
      {
        "name": "next_followup_date",
        "label": "Next Follow-Up Date",
        "type": "date"
      },
      {
        "name": "notes",
        "label": "Call Summary & Notes",
        "type": "textarea",
        "description": "Capture specific promises made, agreed discounts, and operational handoff notes."
      }
    ]
  }
];

export const legacyQuestionnaire: QuestionSection[] = [
  {
    title: '1. Call Header & Lead Details',
    questions: [
      { name: 'vendor_contact_name', label: 'Vendor Contact Name', type: 'text', max: 200 },
      { name: 'call_at', label: 'Call Date & Time', type: 'datetime-local', description: 'Your local timezone.' },
      { name: 'call_outcome', label: 'Call Outcome', type: 'select', options: ['Connected', 'Left Voicemail', 'Busy', 'Rescheduled'] }
    ]
  },
  {
    title: '2. Opening & Verification',
    description: 'Hi, this is [Rep Name] / Lynnet with The Good Flea Operations. We received your vendor application and wanted to follow up quickly on a couple of details!',
    questions: [
      { name: 'identity_verified', label: 'Contact verification', description: 'Am I speaking with [Name] of [Business]?', type: 'select', options: ['Yes', 'No'] },
      { name: 'available_to_chat', label: 'Availability to chat', description: 'Do you have 5–10 minutes to chat?', type: 'select', options: ['Yes', 'Reschedule requested'] }
    ]
  },
  {
    title: '3. Discovery & Vendor Profile (Get to Know)',
    questions: [
      { name: 'business_commitment', label: 'Business Commitment', type: 'select', options: ['Full-time', 'Part-time', 'Hobbyist'] },
      { name: 'currently_does_markets', label: 'Do they currently do markets?', type: 'select', options: ['Yes', 'No'] },
      { name: 'markets_and_frequency', label: 'Which markets & how frequently?', type: 'textarea' },
      { name: 'team_details', label: 'Do you have a team / staff assisting you, or solo?', type: 'textarea' },
      { name: 'primary_goals', label: 'Goals & Primary Objectives for joining The Good Flea', type: 'textarea' },
      { name: 'registration_status', label: 'Business Registration Status', type: 'select', options: ['LLC', 'Sole Prop', 'In Progress', 'None'] },
      { name: 'insurance_status', label: 'General Liability Insurance Status', type: 'select', options: ['Have active policy', 'Need guidance', "Don't have"] }
    ]
  },
  {
    title: '4. Pain Points & Application Follow-up',
    questions: [
      { name: 'application_challenges', label: 'Post-Application Challenges', description: 'What challenges or roadblocks did you experience after submitting your application?', type: 'textarea' },
      { name: 'location_pain_points', label: 'Location / Foot-Traffic Pain Points', type: 'textarea' },
      { name: 'revenue_consistency', label: 'Revenue Consistency', description: 'Are they looking for predictable weekly revenue?', type: 'textarea' }
    ]
  },
  {
    title: '5. Pitching The Offer',
    description: 'We have an introductory vendor incentive: 2 subsequent weekends at NO charge, followed by 2 subsequent weekends at HALF charge.',
    questions: [
      { name: 'offer_interest', label: 'Vendor Reaction & Interest Level', type: 'select', options: ['1 — Very Hesitant', '2 — Hesitant', '3 — Neutral', '4 — Excited', '5 — Extremely Excited'] },
      { name: 'offer_concerns', label: 'Notes on Vendor Concerns or Objections regarding the offer', type: 'textarea' }
    ]
  },
  {
    title: '6. Long-Term Vision & Closing Checklist',
    questions: [
      { name: 'long_term_outlook', label: 'Long-Term Outlook', type: 'select', options: ['One-off', 'Seasonal', 'Long-term recurring anchor vendor'] },
      { name: 'trial_commitment', label: '1-Month Trial Commitment', type: 'select', options: ['Agreed', 'Under Consideration', 'Declined'] },
      { name: 'agreed_weekend_dates', label: 'Agreed Market Weekend Dates', description: 'Select one or more weekends.', type: 'multi-select', options: agreedWeekendOptions },
      { name: 'onboarding_dates_confirmed', label: 'Confirmed dates for onboarding', type: 'checkbox' },
      { name: 'trial_term_agreed', label: 'Agreed to 1-Month Trial Term', type: 'checkbox' },
      { name: 'insurance_setup_walked_through', label: 'Walked through Insurance setup', type: 'checkbox' },
      { name: 'information_packet_sent', label: 'Vendor Information Packet email confirmed/sent', type: 'checkbox' },
      { name: 'added_to_market_schedule', label: 'Added to market schedule', type: 'checkbox' }
    ]
  },
  {
    title: '7. Follow-Up & Next Actions',
    questions: [
      { name: 'followup_status', label: 'Status', type: 'select', options: ['Closed - Confirmed', 'Follow-up Needed', 'Unqualified', 'Lost'] }
    ]
  }
];
