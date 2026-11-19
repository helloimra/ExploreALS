"""Client-side pure inline SVG generators (Part B: Exact 2-Panel EALS-030 MWC & EALS-031 IL-2 Stratification)."""
from __future__ import annotations

DOSSIER_JS_SVG_CUSTOM = """
function renderMwcSarm1Svg(){
  const xL = 52, xR = 446, W = xR - xL;
  const mapX = lg => xL + ((lg + 2.0) / 3.0) * W;
  const yAT = 50, yAB = 140, HA = yAB - yAT;
  const mapYA = mult => yAB - ((Math.log10(Math.max(0.05, Math.min(55, mult))) - Math.log10(0.05)) / (Math.log10(55) - Math.log10(0.05))) * HA;
  const yBT = 178, yBB = 262, HB = yBB - yBT;
  const mapYB = pct => yBB - ((Math.log10(Math.max(0.15, Math.min(100, pct))) - Math.log10(0.15)) / (Math.log10(100) - Math.log10(0.15))) * HB;
  const cGlue = 0.22, dLock = 6.5, binom8 = [1, 8, 28, 56, 70, 56, 28, 8, 1];
  const bexiRel = (u, L) => (Math.pow(1 + u/cGlue, 7) / (L * Math.pow(1 + 0.05*u, 8) + Math.pow(1 + u/cGlue, 8))) * (1 + L);
  const tlockAbs = (u, L) => Math.pow(1 + u/dLock, 8) / (L * Math.pow(1 + u, 8) + Math.pow(1 + u/dLock, 8));
  const heteroOctGoF = u => {
    const r = (1 + u) / (1 + u / dLock);
    let s = 0;
    for(let k=0; k<=8; k++) s += (binom8[k] / 256) / (1 + 8 * Math.pow(0.16, 8 - k) * Math.pow(r, k));
    return s;
  };
  let ptsH = [], ptsA = [], ptsTL = [], ptsDep = [], ptsRes = [], ptsGoF = [];
  for(let i=0; i<=80; i++){
    const lg = -2.0 + (i/80)*3.0, u = Math.pow(10, lg), xp = mapX(lg).toFixed(1);
    ptsH.push(`${xp},${mapYA(bexiRel(u, 120)).toFixed(1)}`);
    ptsA.push(`${xp},${mapYA(bexiRel(u, 8)).toFixed(1)}`);
    ptsTL.push(`${xp},${mapYA(tlockAbs(u, 8)*(1+8)).toFixed(1)}`);
    ptsDep.push(`${xp},${mapYB(100*tlockAbs(u, 8)).toFixed(1)}`);
    ptsRes.push(`${xp},${mapYB(100*tlockAbs(u, 65)).toFixed(1)}`);
    ptsGoF.push(`${xp},${mapYB(100*heteroOctGoF(u)).toFixed(1)}`);
  }
  const y1x = mapYA(1.0).toFixed(1), yFlr = mapYB(1.0).toFixed(1), yGoFTop = mapYB(95.2).toFixed(1), yGoFEnd = mapYB(44.9).toFixed(1);
  const xDepCross = mapX(Math.log10(0.47)).toFixed(1), xResCross = mapX(Math.log10(0.066)).toFixed(1);
  return `<svg viewBox="0 0 460 304" class="w-full h-auto block select-none" role="img" aria-label="Modeled 8-protomer SARM1 MWC curves">
    <text x="12" y="16" font-size="12.8" font-weight="700" fill="var(--foreground)">A. Relative Fold vs Baseline (BEXi Spike vs T-Lock)</text>
    <text x="${xR}" y="16" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--warning)">[PRIOR]</text>
    <line x1="14" y1="30" x2="28" y2="30" stroke="var(--error)" stroke-width="2.2"/><text x="32" y="34" font-size="12.5" fill="var(--error)">8-mer Max (~45x; Emp 2.8x)</text>
    <line x1="208" y1="30" x2="222" y2="30" stroke="var(--warning)" stroke-width="2" stroke-dasharray="4,2"/><text x="226" y="34" font-size="12.5" fill="var(--warning)">ALS (~5x)</text>
    <line x1="296" y1="30" x2="310" y2="30" stroke="var(--success)" stroke-width="2.3"/><text x="314" y="34" font-size="12.5" fill="var(--success)">ARM-TIR T-Lock (0 spike)</text>
    <line x1="${xL}" y1="${yAT}" x2="${xL}" y2="${yAB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${yAB}" x2="${xR}" y2="${yAB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${y1x}" x2="${xR}" y2="${y1x}" stroke="var(--muted-foreground)" stroke-width="1" stroke-dasharray="3,3"/>
    <text x="${xL-5}" y="${mapYA(44.8).toFixed(1)}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--error)">45x</text>
    <text x="${xL-5}" y="${Number(y1x)+4}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">1x</text>
    <text x="${xL-5}" y="${mapYA(0.1).toFixed(1)}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--success)">0.1x</text>
    <polyline fill="none" stroke="var(--error)" stroke-width="2.1" points="${ptsH.join(' ')}"/>
    <polyline fill="none" stroke="var(--warning)" stroke-width="1.9" stroke-dasharray="5,3" points="${ptsA.join(' ')}"/>
    <polyline fill="none" stroke="var(--success)" stroke-width="2.3" points="${ptsTL.join(' ')}"/>
    <circle cx="${mapX(Math.log10(0.30)).toFixed(1)}" cy="${mapYA(0.179).toFixed(1)}" r="3.8" fill="var(--success)"/>
    <text x="${(mapX(Math.log10(0.30))+7).toFixed(1)}" y="${(mapYA(0.179)+4).toFixed(1)}" font-size="12.5" font-family="monospace" font-weight="600" fill="var(--success)">~-82% @ 0.3x Kd</text>
    <text x="12" y="164" font-size="12.8" font-weight="700" fill="var(--foreground)">B. Absolute NADase (% Max) &amp; +STMN2 (L_eff 8 \u2192 65) Sparing</text>
    <line x1="${xL}" y1="${yBT}" x2="${xL}" y2="${yBB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${yBB}" x2="${xR}" y2="${yBB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${yFlr}" x2="${xR}" y2="${yFlr}" stroke="var(--error)" stroke-width="1" stroke-dasharray="3,2"/>
    <text x="${xL-5}" y="${Number(yGoFTop)+4}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--warning)">95%</text>
    <text x="${xL-5}" y="${(mapYB(11.1)+4).toFixed(1)}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--foreground)">11%</text>
    <text x="${xL-5}" y="${Number(yFlr)+4}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--error)">1%</text>
    <text x="${xL-5}" y="${mapYB(0.2).toFixed(1)}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">0.2%</text>
    <polyline fill="none" stroke="var(--warning)" stroke-width="1.8" stroke-dasharray="3,2" points="${ptsGoF.join(' ')}"/>
    <text x="${xR-2}" y="${(Number(yGoFEnd)+14).toFixed(1)}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--warning)">ARM-GoF (~0.08%, &ge;36% floor)</text>
    <polyline fill="none" stroke="var(--success)" stroke-width="2.1" points="${ptsDep.join(' ')}"/>
    <polyline fill="none" stroke="var(--primary)" stroke-width="2.1" stroke-dasharray="4,2" points="${ptsRes.join(' ')}"/>
    <circle cx="${xDepCross}" cy="${yFlr}" r="3.5" fill="var(--success)"/>
    <circle cx="${xResCross}" cy="${yFlr}" r="3.5" fill="var(--primary)"/>
    <line x1="${xResCross}" y1="${Number(yFlr)-10}" x2="${xDepCross}" y2="${Number(yFlr)-10}" stroke="var(--primary)" stroke-width="1.6"/>
    <text x="${((Number(xResCross)+Number(xDepCross))/2).toFixed(1)}" y="${Number(yFlr)-17}" text-anchor="middle" font-size="12.5" font-family="monospace" font-weight="700" fill="var(--primary)">~2-7x sparing</text>
    <text x="${xR-2}" y="${(Number(yFlr)-5).toFixed(1)}" text-anchor="end" font-size="12.5" font-family="monospace" fill="var(--error)">&lt;1% floor</text>
    ${[-2,-1,0,1].map(g=>`<text x="${mapX(g).toFixed(1)}" y="${yBB+16}" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">${Math.pow(10,g)}x</text>`).join('')}
    <text x="248" y="298" text-anchor="middle" font-size="12.5" fill="var(--muted-foreground)">Unbound CNS [Inhibitor]/Kd (Solid L_eff=8 \u00b7 Dashed +STMN2 L_eff=65)</text>
  </svg>`;
}

function renderIl2StratSvg(){
  const hrs = [
    {lbl:'Cov-Adj (N=220)', hr:0.32, lo:0.14, hi:0.74, col:'var(--primary)'},
    {lbl:'750-3.7k (n=154)', hr:0.52, lo:0.30, hi:0.89, col:'var(--success)'},
    {lbl:'Unadj ITT (N=220)', hr:0.81, lo:0.54, hi:1.22, col:'var(--muted-foreground)'},
    {lbl:'&gt;3,700 pg (n=46)', hr:1.37, lo:0.68, hi:2.75, col:'var(--error)'},
  ];
  const xMap = v => 136 + ((Math.log10(v) - Math.log10(0.12)) / (Math.log10(3.0) - Math.log10(0.12))) * 94;
  const x05 = xMap(0.5).toFixed(1), x1 = xMap(1.0).toFixed(1), x2 = xMap(2.0).toFixed(1);
  const hrSvg = hrs.map((d, i) => {
    const y = 54 + i * 40;
    return `<text x="6" y="${y+4}" font-size="12.5" fill="var(--foreground)">${d.lbl}</text>
      <line x1="${xMap(d.lo).toFixed(1)}" y1="${y}" x2="${xMap(d.hi).toFixed(1)}" y2="${y}" stroke="${d.col}" stroke-width="2.1"/>
      <circle cx="${xMap(d.hr).toFixed(1)}" cy="${y}" r="4.2" fill="${d.col}"/>
      <text x="${xMap(d.hr).toFixed(1)}" y="${y-8}" text-anchor="middle" font-size="12.5" font-family="monospace" font-weight="700" fill="${d.col}">${d.hr.toFixed(2)}</text>`;
  }).join('');
  return `<svg viewBox="0 0 460 246" class="w-full h-auto block select-none" role="img" aria-label="MIROCALS survival and pNfH vs NfL discordance">
    <text x="6" y="18" font-size="12.8" font-weight="700" fill="var(--foreground)">A. MIROCALS 21-Mo HR</text>
    <line x1="${x05}" y1="30" x2="${x05}" y2="202" stroke="var(--card-border)" stroke-width="1" stroke-dasharray="2,3"/>
    <line x1="${x1}" y1="30" x2="${x1}" y2="202" stroke="var(--border)" stroke-width="1.3" stroke-dasharray="3,3"/>
    <line x1="${x2}" y1="30" x2="${x2}" y2="202" stroke="var(--card-border)" stroke-width="1" stroke-dasharray="2,3"/>
    <text x="${x05}" y="218" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">0.5</text>
    <text x="${x1}" y="218" text-anchor="middle" font-size="12.5" font-family="monospace" font-weight="600" fill="var(--foreground)">1.0</text>
    <text x="${x2}" y="218" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">2.0</text>
    <text x="183" y="236" text-anchor="middle" font-size="12.5" fill="var(--muted-foreground)">Hazard Ratio (Log)</text>
    ${hrSvg}
    <line x1="236" y1="10" x2="236" y2="238" stroke="var(--card-border)" stroke-width="1"/>
    <text x="244" y="18" font-size="12.8" font-weight="700" fill="var(--foreground)">B. Trautwig CSF Gate (n=77)</text>
    <text x="244" y="36" font-size="12.5" fill="var(--muted-foreground)">NEFL vs NEFH r=0.278 (p=0.014)</text>
    <rect x="244" y="46" width="102" height="74" rx="6" fill="var(--background)" stroke="var(--error)" stroke-width="1.6"/>
    <text x="295" y="67" text-anchor="middle" font-size="12.5" font-weight="700" fill="var(--error)">Missed NfL</text>
    <text x="295" y="88" text-anchor="middle" font-size="12.8" font-family="monospace" font-weight="700" fill="var(--error)">75% DIA</text>
    <text x="295" y="108" text-anchor="middle" font-size="12.5" fill="var(--muted-foreground)">Hi pNfH</text>
    <rect x="352" y="46" width="102" height="74" rx="6" fill="var(--background)" stroke="var(--border)" stroke-width="1"/>
    <text x="403" y="76" text-anchor="middle" font-size="12.5" font-weight="600" fill="var(--foreground)">Concordant</text>
    <text x="403" y="98" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">25% &gt;p80</text>
    <rect x="244" y="128" width="102" height="72" rx="6" fill="var(--background)" stroke="var(--success)" stroke-width="1.5"/>
    <text x="295" y="156" text-anchor="middle" font-size="12.5" font-weight="700" fill="var(--success)">Eligible</text>
    <text x="295" y="178" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">Low Both</text>
    <rect x="352" y="128" width="102" height="72" rx="6" fill="var(--background)" stroke="var(--warning)" stroke-width="1.2" stroke-dasharray="3,2"/>
    <text x="403" y="156" text-anchor="middle" font-size="12.5" font-weight="600" fill="var(--warning)">False Excl.</text>
    <text x="403" y="178" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">Hi NfL Only</text>
    <text x="349" y="236" text-anchor="middle" font-size="12.5" fill="var(--muted-foreground)">31.2% NfL gate error</text>
  </svg>`;
}

function renderSignatureSvg(candId, sig){
  if(sig.kind === 'mwc_sarm1') return renderMwcSarm1Svg();
  if(sig.kind === 'il2_strat') return renderIl2StratSvg();
  return renderLocusSsoSvg(candId, sig);
}
"""
