import { useState } from 'react';

function outcomeLabel(group) {
  const reported = group.reported_outcome?.return_pct;
  const calculated = group.calculated_outcome?.return_pct;
  if (reported != null && calculated != null) return `reported ${reported}% · calculated ${calculated}%`;
  if (reported != null) return `reported ${reported}%`;
  if (calculated != null) return `calculated ${calculated}%`;
  return 'result unknown';
}

export function TraderTradeList({ groups = [], traders = [], activeGroupId = '', onSelect }) {
  const [expanded, setExpanded] = useState({});
  const registry = new Map(traders.map((trader) => [trader.trader_id, trader]));
  return (
    <section className="trade-record-list" aria-label="Normalized trade groups">
      {!groups.length && <div className="trade-record-empty">No normalized trades for this filter.</div>}
      {groups.map((group) => {
        const trader = registry.get(group.trader_id) || {};
        const isExpanded = Boolean(expanded[group.trade_group_id]);
        return (
          <article
            key={group.trade_group_id}
            className={`trade-group-card ${activeGroupId === group.trade_group_id ? 'active' : ''}`}
            style={{ '--trader-color': trader.color || '#8B9A6D' }}
          >
            <button type="button" className="trade-group-summary" onClick={() => onSelect?.(group)}>
              <span className={`trade-direction-shape ${group.direction.toLowerCase()}`} aria-hidden="true" />
              <span>
                <strong>{trader.display_name || group.trader_id} · {group.direction}</strong>
                <small>{group.underlying} {group.trade_date} · {outcomeLabel(group)}</small>
              </span>
              <span className={`trade-review-badge ${group.review_status}`}>{group.review_status}</span>
            </button>
            <button
              type="button"
              className="trade-drilldown-toggle"
              onClick={() => setExpanded((current) => ({
                ...current,
                [group.trade_group_id]: !current[group.trade_group_id],
              }))}
              aria-expanded={isExpanded}
            >
              {isExpanded ? 'Hide legs/events' : 'Show legs/events'}
            </button>
            {isExpanded && group.legs.map((leg) => (
              <div className="trade-leg" key={leg.leg_id}>
                <strong>{leg.expiry} · {leg.strike ?? '--'} {leg.option_type} · ×{leg.contract_multiplier}</strong>
                {leg.events.map((event) => (
                  <div className="trade-event" key={event.event_id}>
                    <time>{event.occurred_at?.slice(11, 16) || '--:--'}</time>
                    <span>{event.action}</span>
                    <span>{event.quantity ?? '?'} @ {event.premium ?? '?'}</span>
                    <span>fees {event.fees ?? '?'}</span>
                  </div>
                ))}
              </div>
            ))}
          </article>
        );
      })}
    </section>
  );
}
