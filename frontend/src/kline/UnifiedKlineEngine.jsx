import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef } from 'react';
import './kline-engine.js';

function normalizeAnnotation(annotation, timeframe) {
  return {
    ...annotation,
    timeframe: annotation.timeframe || timeframe,
    title: annotation.title || annotation.label || annotation.type || 'Annotation',
    body: annotation.body || annotation.label || '',
    style: annotation.style || (annotation.direction === 'PUT' ? 'red' : annotation.direction === 'CALL' ? 'green' : 'blue'),
    anchor_side: annotation.anchor_side || (annotation.direction === 'PUT' ? 'top' : 'bottom'),
    score: Object.prototype.hasOwnProperty.call(annotation, 'score') ? annotation.score : null,
  };
}

export const UnifiedKlineEngine = forwardRef(function UnifiedKlineEngine({ payload, annotations1m = [], annotations5m = [], onAnnotationClick, onBarClick, onReady, replayOnLoad = false, replayStartTime = null, engineOptions = null }, ref) {
  const containerRef = useRef(null);
  const engineRef = useRef(null);
  const onAnnotationClickRef = useRef(onAnnotationClick);
  const onBarClickRef = useRef(onBarClick);
  const onReadyRef = useRef(onReady);
  const engineOptionsRef = useRef(engineOptions);

  useEffect(() => {
    onAnnotationClickRef.current = onAnnotationClick;
    onBarClickRef.current = onBarClick;
    onReadyRef.current = onReady;
    engineOptionsRef.current = engineOptions;
  }, [onAnnotationClick, onBarClick, onReady, engineOptions]);

  const payloadWithAnnotations = useMemo(() => {
    if (!payload) return null;
    return {
      ...payload,
      annotations_1m: annotations1m.map((annotation) => normalizeAnnotation(annotation, '1m')),
      annotations_5m: annotations5m.map((annotation) => normalizeAnnotation(annotation, '5m')),
    };
  }, [payload, annotations1m, annotations5m]);

  useEffect(() => {
    if (!containerRef.current || engineRef.current || !window.KlineEngine) return undefined;
    const engine = new window.KlineEngine({ container: containerRef.current, options: engineOptionsRef.current || {} });
    engineRef.current = engine;
    // Playwright / acceptance seam: query `.unified-kline-engine` then read `__klineEngine`.
    containerRef.current.__klineEngine = engine;
    const offAnno = engine.on?.('annotation:click', (annotation) => onAnnotationClickRef.current?.(annotation));
    const offBar = engine.on?.('bar:click', (event) => onBarClickRef.current?.(event));
    onReadyRef.current?.(engine);
    return () => {
      offAnno?.();
      offBar?.();
      if (containerRef.current) {
        try { delete containerRef.current.__klineEngine; } catch (_) { /* ignore */ }
      }
      engine.destroy?.();
      engineRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!engineRef.current || !engineOptions) return;
    engineRef.current.setOptions?.(engineOptions);
  }, [engineOptions]);

  useEffect(() => {
    const engine = engineRef.current;
    if (!engine || !payloadWithAnnotations) return;
    engine.replayStartTime = replayStartTime;
    engine.loadData(payloadWithAnnotations);
    const totalBars = payloadWithAnnotations.bars_1m?.length || payloadWithAnnotations.bars_5m?.length || 0;
    if (totalBars && replayOnLoad) {
      engine.setReplayReveal?.({ enabled: true, startIndex: 0 });
    } else if (totalBars) {
      engine.setCurrentIndex?.(totalBars - 1, { follow: false });
    }
  }, [payloadWithAnnotations, replayOnLoad, replayStartTime]);

  useImperativeHandle(ref, () => ({
    get engine() { return engineRef.current; },
    play: () => engineRef.current?.play?.(),
    pause: () => engineRef.current?.pause?.(),
    togglePlayback: () => engineRef.current?.togglePlayback?.(),
    stepForward: () => engineRef.current?.stepForward?.(),
    stepBack: () => engineRef.current?.stepBack?.(),
    setTimeframe: (timeframe) => engineRef.current?.setTimeframe?.(timeframe),
    setCurrentIndex: (index, options) => engineRef.current?.setCurrentIndex?.(index, options),
    getCurrentIndex: () => engineRef.current?.getCurrentIndex?.(),
    scrollTo: (target) => engineRef.current?.scrollTo?.(target),
    fitRange: (input) => engineRef.current?.fitRange?.(input),
    setRevealCutoff: (input) => engineRef.current?.setRevealCutoff?.(input),
    setReplayReveal: (input) => engineRef.current?.setReplayReveal?.(input),
    setHighlightRanges: (input) => engineRef.current?.setHighlightRanges?.(input),
    getHighlightRanges: () => engineRef.current?.getHighlightRanges?.(),
    getViewportDebug: () => engineRef.current?.getViewportDebug?.(),
    setMAVisibility: (next) => {
      const engine = engineRef.current;
      if (!engine) return;
      engine.maVisibility = { ...engine.maVisibility, ...next };
      engine._updateToolbarState?.();
      engine.scheduleRender?.();
    },
    overview: () => engineRef.current?.overview?.(),
  }), []);

  return <div className="unified-kline-engine" ref={containerRef} />;
});
