export interface VendorLead {
	id: number;
    vendor_contract: boolean;
    coi: boolean;
    info_packet: boolean;
    application_decision: 'pending' | 'accepted' | 'waitlisted' | 'declined';
	instagram_handle: string;
	business_name: string;
	first_name: string;
	last_name: string;
	email: string;
	phone_number: string;
	vendor_category: string;
	lead_source: string;
	interest_level: 'hot' | 'warm' | 'cold';
	next_followup: string | null;
	notes: string;
    vendor_contact_name: string;
    call_at: string | null;
    call_outcome: string;
    identity_verified: string;
    available_to_chat: string;
    business_commitment: string;
    currently_does_markets: string;
    markets_and_frequency: string;
    team_details: string;
    primary_goals: string;
    registration_status: string;
    insurance_status: string;
    application_challenges: string;
    location_pain_points: string;
    revenue_consistency: string;
    offer_interest: number | null;
    offer_concerns: string;
    long_term_outlook: string;
    trial_commitment: string;
    agreed_weekend_dates: string;
    onboarding_dates_confirmed: boolean;
    trial_term_agreed: boolean;
    insurance_setup_walked_through: boolean;
    information_packet_sent: boolean;
    added_to_market_schedule: boolean;
    followup_status: string;
	created_at: string;
    funnel_stage: 'new_application' | 'vendor';
}

export interface LeadData {
	leads: VendorLead[];
	categories: string[];
	sources: string[];
}
