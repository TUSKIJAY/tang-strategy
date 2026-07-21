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
        const direction = String(group.direction || '').toUpperCase() === 'PUT' ? 'PUT' : 'CALL';
        const directionClass = direction.toLowerCase();
        return (
          <article
            key={group.trade_group_id}
            className={`trade-group-card ${directionClass} ${activeGroupId === group.trade_group_id ? 'active' : ''}`}
          >
            <button type="button" className="trade-group-summary" onClick={() => onSelect?.(group)}>
              <span className="trade-direction-glyph" aria-hidden="true">
                <i className={`trade-direction-shape ${directionClass}`} />
              </span>
              <span className="trade-group-main">
                <span className="trade-group-title">
                  <strong className="trade-trader-name">{trader.display_name || group.trader_id}</strong>
                  <span className={`trade-direction-word ${directionClass}`}>{direction}</span>
                </span>
                <small className="trade-group-meta">
                  <em>{group.underlying}</em> · {group.trade_date} · {outcomeLabel(group)}
                </small>
              </span>
              <span className={`trade-review-badge ${group.review_status}`}>{group.review_status}</span>
            </button>
            <div className="trade-card-foot">
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
            </div>
            {isExpanded && (
              <div className="trade-legs">
                {group.legs.map((leg) => (
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
              </div>
            )}
          </article>
        );
      })}
    </section>
  );
}
