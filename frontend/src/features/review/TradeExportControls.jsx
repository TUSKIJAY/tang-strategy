import { Download } from 'lucide-react';
import { buildTradeRecordDownloads, exportSelectionFromFilters } from './tradeRecords.js';

export function TradeExportControls({ payload, groups = [], filters = null }) {
  function downloadAll() {
    const selection = filters
      ? exportSelectionFromFilters(payload, filters)
      : payload?.export_metadata?.selection;
    const files = buildTradeRecordDownloads(payload, groups, selection);
    Object.entries(files).forEach(([filename, content]) => {
      const anchor = document.createElement('a');
      anchor.href = URL.createObjectURL(new Blob([content], { type: 'text/plain;charset=utf-8' }));
      anchor.download = filename;
      anchor.click();
      URL.revokeObjectURL(anchor.href);
    });
  }

  return (
    <button type="button" className="trade-export-button" onClick={downloadAll} disabled={!payload}>
      <Download size={13} /> Download
    </button>
  );
}
