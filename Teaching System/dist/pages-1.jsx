/* pages-1.jsx — 策略地图, 模块预览卡, 策略章节, 案例剧场 */

function HubPage({ navigate }) {
  return (
    <AppLayout activeTop="hub" activeModule={null} navigate={navigate}
      onModuleClick={(id) => navigate(`module/${id}`)}>
      <div className="p-12 max-w-[1280px] mx-auto">
        <header className="mb-8">
          <h1 className="font-['Newsreader'] text-[40px] font-semibold leading-[1.2] text-[#1A1A19] mb-2">策略地图</h1>
          <p className="font-['Work_Sans'] text-[18px] leading-[1.6] text-[#6B6B66] max-w-2xl">
            SPY 执行策略的核心模块。每个模块对应一个交易决策环节，从环境判断到出场管理。
          </p>
        </header>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {MODULES.map(m => (
            <article key={m.id} onClick={() => navigate(`module/${m.id}`)}
              className="bg-white border border-[#D8D1C3] rounded p-5 cursor-pointer hover:border-[#8B9A6D] transition-colors">
              <div className="flex justify-between items-start mb-4">
                <span className="font-['Space_Grotesk'] text-[14px] text-[#B7B09F]">{m.num}</span>
                <DataPill tone="olive">{m.tag}</DataPill>
              </div>
              <h3 className="font-['Newsreader'] text-[24px] font-medium leading-[1.4] text-[#1A1A19] mb-2">{m.name}</h3>
              <p className="font-['Work_Sans'] text-[15px] leading-[1.6] text-[#6B6B66] mb-4">{m.desc}</p>
              <div className="mb-4">
                <KlineView mode="mini" segmentId={CASES.find(c => c.module === m.id)?.segment_id || CASES[0]?.segment_id} />
              </div>
              <div className="mb-4">
                <span className="font-['Inter'] text-[11px] font-semibold text-[#6B6B66]">学习目标</span>
                <p className="font-['Work_Sans'] text-[14px] leading-[1.5] text-[#1A1A19] mt-1">{m.goal}</p>
              </div>
              <div className="flex flex-wrap gap-2 mb-6">
                {m.tags.map(t => (
                  <DataPill key={t}>{t}</DataPill>
                ))}
              </div>
              <div className="border-t border-[#D8D1C3] pt-4">
                <span className="font-['Work_Sans'] text-[16px] text-[#56623F] flex items-center justify-between">
                  进入策略章节 <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </span>
              </div>
            </article>
          ))}
        </div>

        {/* 常见执行错误 */}
        <section className="mt-12 pt-8 border-t border-[#ded7ca]">
          <h2 className="font-['Newsreader'] text-[32px] font-medium leading-[1.3] text-[#1A1A19] mb-4">常见执行错误</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {MISTAKES.slice(0, 3).map(err => (
              <a key={err.id} onClick={() => navigate(`mistake/${err.id}`)}
                className="p-4 border border-[#ffdad6]/50 bg-[#fdf8f7] rounded hover:bg-[#ffdad6]/10 transition-colors cursor-pointer group">
                <h4 className="font-['Newsreader'] text-[18px] text-[#93000a] mb-2 group-hover:underline decoration-1 underline-offset-4">{err.name}</h4>
                <p className="font-['Work_Sans'] text-[14px] text-[#494740]">{err.desc.slice(0, 40)}…</p>
              </a>
            ))}
          </div>
        </section>
      </div>
    </AppLayout>
  );
}

function ModulePage({ moduleId, navigate }) {
  const mod = MODULES.find(m => m.id === moduleId) || MODULES[0];
  const moduleCases = CASES.filter(c => c.module === mod.id);
  const moduleRules = RULES.filter(r => r.module === mod.id);
  const moduleMistakes = MISTAKES.filter(e => e.module === mod.id);
  const anchorCase = moduleCases[0] || CASES[0];

  return (
    <AppLayout activeTop="hub" activeModule={mod.id} navigate={navigate}
      onModuleClick={(id) => navigate(`module/${id}`)}>
      <div className="p-12 max-w-[960px] mx-auto">
        <button onClick={() => navigate('hub')} className="font-['Work_Sans'] text-[14px] text-[#6B6B66] hover:text-[#1A1A19] mb-6 flex items-center gap-1">
          <span className="material-symbols-outlined text-[16px]">arrow_back</span>返回策略地图
        </button>
        {/* 章节标题区 */}
        <div className="mb-8 pb-6 border-b border-[#ded7ca]">
          <span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#6B6B66] uppercase block mb-2">模块 {mod.num} · {mod.tag}</span>
          <h1 className="font-['Newsreader'] text-[40px] font-semibold leading-[1.2] mb-3">{mod.name}</h1>
          <p className="font-['Work_Sans'] text-[18px] leading-[1.6] text-[#6B6B66] max-w-2xl">{mod.desc}</p>
        </div>

        {/* 核心定义区 */}
        <section className="mb-8">
          <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">核心定义</h2>
          <div className="border border-[#ded7ca] rounded p-6 bg-white space-y-4">
            <div><span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#6B6B66] uppercase">一句话定义</span><p className="font-['Work_Sans'] text-[16px] text-[#1A1A19] mt-1">{moduleRules[0]?.one_line_definition || `${mod.desc.split('。')[0]}。`}</p></div>
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[#ded7ca]">
              <div><span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#6B6B66] uppercase">适用场景</span><p className="font-['Work_Sans'] text-[14px] text-[#6B6B66] mt-1">{moduleRules[0]?.setup || '5分钟趋势明确时'}</p></div>
              <div><span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#6B6B66] uppercase">不适用场景</span><p className="font-['Work_Sans'] text-[14px] text-[#6B6B66] mt-1">{moduleRules[0]?.invalid || '均线缠绕、无方向'}</p></div>
            </div>
          </div>
        </section>

        {/* 规则契约区 */}
        {moduleRules.length > 0 && (
          <section className="mb-8">
            <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">规则契约</h2>
            {moduleRules.map(rule => (
              <div key={rule.id} className="border border-[#ded7ca] rounded p-6 bg-white mb-4">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-['Newsreader'] text-[20px] font-medium">{rule.name}</h3>
                  <span className={`font-['Inter'] text-[12px] font-semibold tracking-[0.05em] px-2 py-1 rounded-sm border ${rule.status === '已审核' ? 'bg-[#F4F6EE] text-[#56623F] border-[#8B9A6D]/50' : 'bg-[#f1edec] text-[#6B6B66] border-[#cbc6bd]/30'}`}>{rule.status}</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">成立条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{rule.setup}</p></div>
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">触发条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{rule.trigger}</p></div>
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">过滤条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{rule.filter}</p></div>
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">失效条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{rule.invalid}</p></div>
                </div>
              </div>
            ))}
          </section>
        )}

        {/* K线证据图 */}
        <section className="mb-8">
          <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">视觉锚点</h2>
          <KlineView mode="evidence" height={300} segmentId={anchorCase?.segment_id} />
        </section>

        {/* 案例入口 */}
        <section className="mb-8">
          <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">案例入口</h2>
          {moduleCases.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {moduleCases.map(c => (
                <a key={c.id} onClick={() => navigate(`case/${c.id}`)}
                  className="p-4 border border-[#ded7ca] rounded bg-white cursor-pointer hover:shadow-[0px_4px_12px_rgba(23,22,19,0.05)] transition-shadow group">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-['Space_Grotesk'] text-[12px] text-[#7a776f]">{c.date}</span>
                    <GradePill grade={c.grade} />
                  </div>
                  <h4 className="font-['Newsreader'] text-[18px] font-medium group-hover:text-[#285fa2] transition-colors">{c.title}</h4>
                </a>
              ))}
            </div>
          ) : (
            <p className="text-[#7a776f] font-['Work_Sans'] text-[14px]">暂无案例，待补充。</p>
          )}
        </section>

        {/* 相关错误 */}
        {moduleMistakes.length > 0 && (
          <section className="mb-8">
            <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">相关错误</h2>
            <div className="space-y-3">
              {moduleMistakes.map(err => (
                <a key={err.id} onClick={() => navigate(`mistake/${err.id}`)}
                  className="flex items-center justify-between p-4 border border-[#ffdad6]/50 rounded bg-[#fdf8f7] cursor-pointer hover:bg-[#ffdad6]/10 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-[#ba1a1a]">{err.icon}</span>
                    <span className="font-['Work_Sans'] text-[16px]">{err.name}</span>
                  </div>
                  <span className="material-symbols-outlined text-[#7a776f] text-[16px]">arrow_forward</span>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* 模块训练入口 */}
        <section className="border-t border-[#ded7ca] pt-8">
          <button onClick={() => navigate(`training/${mod.id}`)}
            className="w-full bg-[#1A1A19] text-white font-['Work_Sans'] text-[18px] py-3 px-6 rounded hover:bg-[#2A2924] transition-colors flex justify-center items-center gap-2">
            进入模块训练 <span className="material-symbols-outlined text-sm">arrow_forward</span>
          </button>
        </section>
      </div>
    </AppLayout>
  );
}

function CasePage({ caseId, navigate }) {
  const c = getCase(caseId);
  const mod = MODULES.find(m => m.id === c.module);
  const segment = getCaseSegment(c);
  const checkpoints = segment?.derived?.checkpoints || [];
  const ruleNames = (c.rule_ids || []).map(id => RULES.find(r => r.id === id)?.name || id);

  // Signal Validation ↔ chart linkage: clicking a row sets selectedCpKey; a
  // second click on the same row clears. Ranges derive from checkpointToRanges.
  const [selectedCpKey, setSelectedCpKey] = React.useState(null);
  React.useEffect(() => { setSelectedCpKey(null); }, [caseId]);
  const selectedCp = selectedCpKey ? checkpoints.find(cp => cp.key === selectedCpKey) : null;
  const highlightRanges = selectedCp ? checkpointToRanges(selectedCp, segment, c) : null;

  return (
    <AppLayout activeTop="case" activeModule={c.module} navigate={navigate}
      onModuleClick={(id) => navigate(`module/${id}`)}>
      <div className="p-12 max-w-[1280px] mx-auto">
        <button onClick={() => navigate(c.module ? `module/${c.module}` : 'hub')} className="font-['Work_Sans'] text-[14px] text-[#6B6B66] hover:text-[#1A1A19] mb-6 flex items-center gap-1">
          <span className="material-symbols-outlined text-[16px]">arrow_back</span>返回{mod?.name || '策略地图'}
        </button>
        {/* Header */}
        <div className="mb-6 pb-4 border-b border-[#e6e2e0] flex justify-between items-end">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] bg-[#ebe7e6] px-2 py-1 rounded-sm uppercase">案例研究</span>
              <span className="font-['Space_Grotesk'] text-[14px] text-[#494740] flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">calendar_today</span>{c.date}
              </span>
              <GradePill grade={c.grade} />
            </div>
            <h1 className="font-['Newsreader'] text-[40px] font-semibold leading-[1.2]">{c.title}</h1>
            <p className="font-['Work_Sans'] text-[15px] leading-[1.6] text-[#6B6B66] mt-2 max-w-2xl">{c.lesson}</p>
          </div>
          <div className="flex gap-2">
            <button className="w-10 h-10 border border-[#cbc6bd] rounded flex items-center justify-center hover:bg-[#f7f3f1] transition-colors">
              <span className="material-symbols-outlined text-[#494740]">bookmark_border</span>
            </button>
            <button className="w-10 h-10 border border-[#cbc6bd] rounded flex items-center justify-center hover:bg-[#f7f3f1] transition-colors">
              <span className="material-symbols-outlined text-[#494740]">share</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* Chart + Context */}
          <div className="xl:col-span-8 space-y-4">
            <div className="bg-white border border-[#e6e2e0] rounded-[4px] p-1">
              <div className="flex justify-between items-center px-4 py-3 border-b border-[#e6e2e0]">
                <div className="flex items-center gap-4">
                  <span className="font-['Newsreader'] text-[24px] font-medium">{c.ticker}</span>
                  <span className="font-['Space_Grotesk'] text-[14px] text-[#6B6B66] bg-[#f7f3f1] px-2 py-0.5 rounded">1m / 5m Heikin-Ashi</span>
                </div>
                <div className="flex gap-4 font-['Space_Grotesk'] text-[14px] text-[#6B6B66]">
                  <span>{segment?.date}</span>
                  <span>Decision: {c.decision_bar?.time}</span>
                </div>
              </div>
              <KlineView mode="evidence" height={440} segmentId={c.segment_id} caseId={c.id} highlightRanges={highlightRanges} />
            </div>
            <div className="bg-white border border-[#e6e2e0] rounded-[4px] p-6">
              <h3 className="font-['Newsreader'] text-[24px] font-medium mb-2">技术背景</h3>
              <p className="font-['Work_Sans'] text-[16px] leading-[1.6] text-[#494740]">
                {segment?.teaching_focus || c.lesson} 当前案例关联规则：{ruleNames.join('、') || mod?.name}。右侧验证栏来自教学切片的 derived.checkpoints。
              </p>
            </div>
          </div>

          {/* Right sidebar */}
          <div className="xl:col-span-4 space-y-6">
            <div className="bg-white border border-[#e6e2e0] rounded-[4px] p-6">
              <div className="flex justify-between items-start mb-4 pb-2 border-b border-[#e6e2e0]">
                <div>
                  <h3 className="font-['Newsreader'] text-[24px] font-medium">信号验证</h3>
                  <p className="font-['Work_Sans'] text-[12px] text-[#7a776f] mt-1">点击任一项，在图表上高亮对应区域</p>
                </div>
                <span className="bg-[#8B9A6D] text-white font-['Inter'] text-[12px] font-semibold tracking-[0.05em] px-2 py-1 rounded-sm">{c.grade}</span>
              </div>
              <div className="space-y-2">
                {checkpoints.slice(0, 6).map((cp, i) => {
                  const active = cp.key === selectedCpKey;
                  const hasRange = checkpointToRanges(cp, segment, c).length > 0;
                  return (
                    <button key={i} type="button"
                      onClick={() => setSelectedCpKey(active ? null : cp.key)}
                      disabled={!hasRange}
                      className={`w-full text-left flex gap-3 items-start px-3 py-2 rounded border transition-colors ${active ? 'border-[#8B9A6D] bg-[#F4F6EE]' : hasRange ? 'border-transparent hover:border-[#D8D1C3] hover:bg-[#FAF9F5]' : 'border-transparent opacity-60 cursor-default'}`}>
                      <span className={`material-symbols-outlined text-[20px] mt-0.5 ${cp.passed ? 'text-[#8B9A6D]' : 'text-[#ba1a1a]'}`}>{cp.passed ? 'check_circle' : 'error'}</span>
                      <div className="min-w-0 flex-1">
                        <h4 className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] mb-1">{cp.label}</h4>
                        <p className="font-['Work_Sans'] text-[14px] text-[#494740] leading-tight">{cp.reason}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="bg-[#fdf8f7] border border-[#e6e2e0] rounded-[4px] p-6">
              <h3 className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase mb-4">执行指标</h3>
              <div className="grid grid-cols-2 gap-y-4 gap-x-2">
                <div><span className="block font-['Inter'] text-[10px] font-semibold text-[#7a776f] mb-1">入场价</span><span className="font-['Space_Grotesk'] text-[14px]">{c.entry}</span></div>
                <div><span className="block font-['Inter'] text-[10px] font-semibold text-[#7a776f] mb-1">止损位</span><span className="font-['Space_Grotesk'] text-[14px]">{c.stop}</span></div>
                <div><span className="block font-['Inter'] text-[10px] font-semibold text-[#7a776f] mb-1">风险回报比</span><span className="font-['Space_Grotesk'] text-[14px]">{c.rr}</span></div>
                <div><span className="block font-['Inter'] text-[10px] font-semibold text-[#7a776f] mb-1">结果</span><span className="font-['Space_Grotesk'] text-[14px] text-[#285fa2] font-medium">{c.result}</span></div>
              </div>
              <div className="mt-4 pt-3 border-t border-[#e6e2e0]">
                <button onClick={() => navigate('archives')} className="w-full border border-[#1A1A19] text-[#1A1A19] py-2 px-4 rounded font-['Inter'] text-[12px] font-semibold tracking-[0.05em] hover:bg-[#ebe7e6] transition-colors">
                  查看完整日志
                </button>
              </div>
            </div>

            <button onClick={() => navigate(`training/${c.module}`)}
              className="w-full bg-[#1A1A19] text-white font-['Work_Sans'] text-[16px] py-3 rounded hover:bg-[#2A2924] transition-colors flex justify-center items-center gap-2">
              进入回放训练 <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

Object.assign(window, { HubPage, ModulePage, CasePage });
