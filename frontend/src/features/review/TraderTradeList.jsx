import { useState } from 'react';
import { groupCardMeta, groupTimelineEvents } from './tradeRecords.js';

export function TraderTradeList({
  groups = [],
  traders = [],
  activeGroupId = '',
  onSelect,
  onEventFocus,
}) {
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
        const cardMeta = groupCardMeta(group);
        const timeline = groupTimelineEvents(group);
        return (
          <article
            key={group.trade_group_id}
            className={`trade-group-card ${directionClass} ${activeGroupId === group.trade_group_id ? 'active' : ''}`}
            data-trade-group-id={group.trade_group_id}
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
                  <em>{group.underlying}</em> · {group.trade_date}
                  {cardMeta.metaSuffix ? <> · {cardMeta.metaSuffix}</> : null}
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
              <div className="trade-legs trade-timeline" aria-label="Trade timeline">
                {timeline.length === 0 ? (
                  <div className="trade-timeline-empty">No complete-timed events.</div>
                ) : (
                  timeline.map((row) => (
                    <button
                      key={row.event_id}
                      type="button"
                      className="trade-timeline-row"
                      data-event-id={row.event_id}
                      onClick={() => onEventFocus?.(row, group)}
                    >
                      <time className="trade-timeline-time">{row.time}</time>
                      <span className={`trade-timeline-action ${row.actionLabel.toLowerCase()}`}>
                        {row.actionLabel}
                      </span>
                      <span className="trade-timeline-px">
                        {row.quantity ?? '?'} @ {row.premium ?? '?'}
                      </span>
                    </button>
                  ))
                )}
              </div>
            )}
          </article>
        );
      })}
    </section>
  );
}
