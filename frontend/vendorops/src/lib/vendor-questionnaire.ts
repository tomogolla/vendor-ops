export type Question = {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'multi-select' | 'datetime-local' | 'checkbox';
  options?: readonly string[];
  description?: string;
  max?: number;
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
