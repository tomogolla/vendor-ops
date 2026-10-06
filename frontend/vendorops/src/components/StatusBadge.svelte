<script lang="ts">
  interface Props {
    status: string;
    size?: 'sm' | 'md' | 'lg';
  }

  let { status, size = 'md' }: Props = $props();

  const statusColors: Record<string, { bg: string; text: string }> = {
    qualified: { bg: '#d1fae5', text: '#065f46' },
    'contact_needed': { bg: '#fef3c7', text: '#92400e' },
    'discovery_scheduled': { bg: '#bfdbfe', text: '#1e40af' },
    'not_qualified': { bg: '#fee2e2', text: '#7f1d1d' },
    'unreviewed': { bg: '#f3f4f6', text: '#374151' },

    'new': { bg: '#f3f4f6', text: '#374151' },
    'under_review': { bg: '#bfdbfe', text: '#1e40af' },
    'accepted': { bg: '#d1fae5', text: '#065f46' },
    'waitlisted': { bg: '#fef3c7', text: '#92400e' },
    'declined': { bg: '#fee2e2', text: '#7f1d1d' },

    'not_invoiced': { bg: '#f3f4f6', text: '#374151' },
    'invoice_draft': { bg: '#dbeafe', text: '#0c4a6e' },
    'invoice_sent': { bg: '#fef3c7', text: '#92400e' },
    'payment_pending': { bg: '#fef3c7', text: '#92400e' },
    'partially_paid': { bg: '#fef3c7', text: '#92400e' },
    'paid': { bg: '#d1fae5', text: '#065f46' },
    'overdue': { bg: '#fee2e2', text: '#7f1d1d' },

    'not_booked': { bg: '#f3f4f6', text: '#374151' },
    'reserved': { bg: '#dbeafe', text: '#0c4a6e' },
    'confirmed': { bg: '#d1fae5', text: '#065f46' },
    'preparing': { bg: '#fef3c7', text: '#92400e' },
    'attended': { bg: '#d1fae5', text: '#065f46' },
    'no_show': { bg: '#fee2e2', text: '#7f1d1d' },
    'cancelled': { bg: '#f3f4f6', text: '#374151' },
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  const colors = statusColors[status.toLowerCase()] || statusColors['unreviewed'];
  const sizeClass = sizeClasses[size];
</script>

<span
  class={`status-badge ${sizeClass}`}
  style="background-color: {colors.bg}; color: {colors.text};"
>
  {status.replace(/_/g, ' ')}
</span>

<style>
  .status-badge {
    display: inline-block;
    border-radius: 4px;
    font-weight: 500;
    text-transform: capitalize;
    white-space: nowrap;
  }
</style>
