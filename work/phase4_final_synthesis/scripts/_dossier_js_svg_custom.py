"""Client-side pure inline SVG generators (Part B: Exact 2-Panel EALS-030 MWC & EALS-031 IL-2 Stratification)."""
from __future__ import annotations

DOSSIER_JS_SVG_CUSTOM = """
function renderMwcSarm1Svg(){
  const xL = 52, xR = 446, W = xR - xL;
  const mapX = lg => xL + ((lg + 2.0) / 3.0) * W;
  const yAT = 54, yAB = 142, HA = yAB - yAT;
  const mapYA = mult => yAB - ((Math.log10(Math.max(0.05, Math.min(55, mult))) - Math.log10(0.05)) / (Math.log10(55) - Math.log10(0.05))) * HA;
  const yBT = 180, yBB = 264, HB = yBB - yBT;
  const mapYB = pct => yBB - ((Math.log10(Math.max(0.15, Math.min(100, pct))) - Math.log10(0.15)) / (Math.log10(100) - Math.log10(0.15))) * HB;
  const cGlue = 0.22, dLock = 6.5, binom8 = [1, 8, 28, 56, 70, 56, 28, 8, 1];
  const bexiRel = (u, L) => (Math.pow(1 + u/cGlue, 7) / (L * Math.pow(1 + 0.05*u, 8) + Math.pow(1 + u/cGlue, 8))) * (1 + L);
  const lowResPriorRel = u => { const z = Math.pow(1 + 5.154*u, 6); return 3.5 * (z / (2.5 + z)) / (1 + u); };
  const tlockAbs = (u, L) => Math.pow(1 + u/dLock, 8) / (L * Math.pow(1 + u, 8) + Math.pow(1 + u/dLock, 8));
  const heteroOctGoF = u => {
    const r = (1 + u) / (1 + u / dLock);
    let s = 0;
    for(let k=0; k<=8; k++) s += (binom8[k] / 256) / (1 + 8 * Math.pow(0.16, 8 - k) * Math.pow(r, k));
    return s;
  };
  let ptsH = [], ptsEmp = [], ptsA = [], ptsTL = [], ptsDep = [], ptsRes = [], ptsGoF = [];
  for(let i=0; i<=80; i++){
    const lg = -2.0 + (i/80)*3.0, u = Math.pow(10, lg), xp = mapX(lg).toFixed(1);
    ptsH.push(`${xp},${mapYA(bexiRel(u, 120)).toFixed(1)}`);
    ptsEmp.push(`${xp},${mapYA(lowResPriorRel(u)).toFixed(1)}`);
    ptsA.push(`${xp},${mapYA(bexiRel(u, 8)).toFixed(1)}`);
    ptsTL.push(`${xp},${mapYA(tlockAbs(u, 8)*(1+8)).toFixed(1)}`);
    ptsDep.push(`${xp},${mapYB(100*tlockAbs(u, 8)).toFixed(1)}`);
    ptsRes.push(`${xp},${mapYB(100*tlockAbs(u, 65)).toFixed(1)}`);
    ptsGoF.push(`${xp},${mapYB(100*heteroOctGoF(u)).toFixed(1)}`);
  }
  const y1x = mapYA(1.0).toFixed(1), yFlr = mapYB(1.0).toFixed(1), yGoFTop = mapYB(95.2).toFixed(1), yGoFEnd = mapYB(44.9).toFixed(1);
  const xDepCross = mapX(Math.log10(0.47)).toFixed(1), xResCross = mapX(Math.log10(0.066)).toFixed(1);
  return `<svg viewBox="0 0 460 306" class="w-full h-auto block select-none" role="img" aria-label="Modeled 8-protomer SARM1 MWC and low-reserve washout sensitivity curves">
    <text x="12" y="16" font-size="12.6" font-weight="700" fill="var(--foreground)">A. Modeled Fold vs Base: BEXi Spike (2.8x / 8-mer) vs T-Lock</text>
    <text x="${xR}" y="16" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--warning)">Sensitivity</text>
    <line x1="12" y1="31" x2="23" y2="31" stroke="var(--error)" stroke-width="1.8" stroke-dasharray="2,2"/><text x="26" y="35" font-size="12.2" fill="var(--error)">8-mer (~45x)</text>
    <line x1="112" y1="31" x2="124" y2="31" stroke="var(--primary)" stroke-width="2.1"/><text x="127" y="35" font-size="12.2" fill="var(--primary)">Low-Res (2.8x)</text>
    <line x1="226" y1="31" x2="238" y2="31" stroke="var(--warning)" stroke-width="2" stroke-dasharray="4,2"/><text x="241" y="35" font-size="12.2" fill="var(--warning)">ALS (~5x)</text>
    <line x1="314" y1="31" x2="326" y2="31" stroke="var(--success)" stroke-width="2.3"/><text x="329" y="35" font-size="12.2" fill="var(--success)">T-Lock (&le;1x)</text>
    <line x1="${xL}" y1="${yAT}" x2="${xL}" y2="${yAB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${yAB}" x2="${xR}" y2="${yAB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${y1x}" x2="${xR}" y2="${y1x}" stroke="var(--muted-foreground)" stroke-width="1" stroke-dasharray="3,3"/>
    <text x="${xL-5}" y="${mapYA(44.8).toFixed(1)}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--error)">45x</text>
    <text x="${xL-5}" y="${mapYA(2.83).toFixed(1)}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--primary)">2.8x</text>
    <text x="${xL-5}" y="${Number(y1x)+4}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--muted-foreground)">1x</text>
    <text x="${xL-5}" y="${mapYA(0.1).toFixed(1)}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--success)">0.1x</text>
    <polyline fill="none" stroke="var(--error)" stroke-width="1.6" stroke-dasharray="2,2" points="${ptsH.join(' ')}"/>
    <polyline fill="none" stroke="var(--primary)" stroke-width="2.1" points="${ptsEmp.join(' ')}"/>
    <polyline fill="none" stroke="var(--warning)" stroke-width="1.9" stroke-dasharray="5,3" points="${ptsA.join(' ')}"/>
    <polyline fill="none" stroke="var(--success)" stroke-width="2.3" points="${ptsTL.join(' ')}"/>
    <circle cx="${mapX(Math.log10(0.30)).toFixed(1)}" cy="${mapYA(0.179).toFixed(1)}" r="3.8" fill="var(--success)"/>
    <text x="${(mapX(Math.log10(0.30))+7).toFixed(1)}" y="${(mapYA(0.179)+4).toFixed(1)}" font-size="12.4" font-family="monospace" font-weight="600" fill="var(--success)">~-82% @ 0.3x Kd</text>
    <text x="12" y="165" font-size="12.4" font-weight="700" fill="var(--foreground)">B. Absolute NADase (%): Default L0=8 (Krus 1x) vs +NMNAT2 (L0=65)</text>
    <line x1="${xL}" y1="${yBT}" x2="${xL}" y2="${yBB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${yBB}" x2="${xR}" y2="${yBB}" stroke="var(--border)" stroke-width="1.2"/>
    <line x1="${xL}" y1="${yFlr}" x2="${xR}" y2="${yFlr}" stroke="var(--error)" stroke-width="1" stroke-dasharray="3,2"/>
    <text x="${xL-5}" y="${Number(yGoFTop)+4}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--warning)">95%</text>
    <text x="${xL-5}" y="${(mapYB(11.1)+4).toFixed(1)}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--foreground)">11%</text>
    <text x="${xL-5}" y="${Number(yFlr)+4}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--error)">1%</text>
    <text x="${xL-5}" y="${mapYB(0.2).toFixed(1)}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--muted-foreground)">0.2%</text>
    <polyline fill="none" stroke="var(--warning)" stroke-width="1.8" stroke-dasharray="3,2" points="${ptsGoF.join(' ')}"/>
    <text x="${xR-2}" y="${(Number(yGoFEnd)+14).toFixed(1)}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--warning)">ARM-GoF (~0.08%, &ge;36% floor)</text>
    <polyline fill="none" stroke="var(--success)" stroke-width="2.1" points="${ptsDep.join(' ')}"/>
    <polyline fill="none" stroke="var(--primary)" stroke-width="2.1" stroke-dasharray="4,2" points="${ptsRes.join(' ')}"/>
    <circle cx="${xDepCross}" cy="${yFlr}" r="3.5" fill="var(--success)"/>
    <circle cx="${xResCross}" cy="${yFlr}" r="3.5" fill="var(--primary)"/>
    <line x1="${xResCross}" y1="${Number(yFlr)-10}" x2="${xDepCross}" y2="${Number(yFlr)-10}" stroke="var(--primary)" stroke-width="1.6"/>
    <text x="${((Number(xResCross)+Number(xDepCross))/2).toFixed(1)}" y="${Number(yFlr)-17}" text-anchor="middle" font-size="12.4" font-family="monospace" font-weight="700" fill="var(--primary)">~2-7x if &alpha;&gt;0</text>
    <text x="${xR-2}" y="${(Number(yFlr)-5).toFixed(1)}" text-anchor="end" font-size="12.4" font-family="monospace" fill="var(--error)">&lt;1% floor</text>
    ${[-2,-1,0,1].map(g=>`<text x="${mapX(g).toFixed(1)}" y="${yBB+16}" text-anchor="middle" font-size="12.4" font-family="monospace" fill="var(--muted-foreground)">${Math.pow(10,g)}x</text>`).join('')}
    <text x="248" y="300" text-anchor="middle" font-size="12.4" fill="var(--muted-foreground)">Unbound CNS [Inhibitor]/Kd (Default &alpha;=0 L0=8 &middot; Conditional &alpha;&gt;0 L0=65)</text>
  </svg>`;
}

function renderIl2StratSvg(){
  const hrs = [
    {lbl:'Cov-Adj (N=220)', hr:0.32, lo:0.14, hi:0.73, col:'var(--primary)'},
    {lbl:'750-3.7k (n=154)', hr:0.52, lo:0.30, hi:0.89, col:'var(--success)'},
    {lbl:'&le;3.7k Pool (n=173)', hr:0.57, lo:0.33, hi:0.97, col:'var(--success)'},
    {lbl:'Unadj ITT (N=220)', hr:0.81, lo:0.54, hi:1.22, col:'var(--muted-foreground)'},
    {lbl:'&gt;3.7k (n=47, NS)', hr:1.37, lo:0.68, hi:2.75, col:'var(--warning)'},
  ];
  const xMap = v => 136 + ((Math.log10(v) - Math.log10(0.12)) / (Math.log10(3.0) - Math.log10(0.12))) * 94;
  const x05 = xMap(0.5).toFixed(1), x1 = xMap(1.0).toFixed(1), x2 = xMap(2.0).toFixed(1);
  const hrSvg = hrs.map((d, i) => {
    const y = 46 + i * 38;
    return `<text x="6" y="${y+4}" font-size="12.4" fill="var(--foreground)">${d.lbl}</text>
      <line x1="${xMap(d.lo).toFixed(1)}" y1="${y}" x2="${xMap(d.hi).toFixed(1)}" y2="${y}" stroke="${d.col}" stroke-width="2.1"/>
      <circle cx="${xMap(d.hr).toFixed(1)}" cy="${y}" r="4.0" fill="${d.col}"/>
      <text x="${xMap(d.hr).toFixed(1)}" y="${y-7}" text-anchor="middle" font-size="12.3" font-family="monospace" font-weight="700" fill="${d.col}">${d.hr.toFixed(2)}</text>`;
  }).join('');
  return `<svg viewBox="0 0 460 258" class="w-full h-auto block select-none" role="img" aria-label="MIROCALS survival and tryptic CSF MS NEFH vs NEFL discordance">
    <text x="6" y="18" font-size="12.8" font-weight="700" fill="var(--foreground)">A. MIROCALS 21-Mo HR</text>
    <line x1="${x05}" y1="28" x2="${x05}" y2="212" stroke="var(--card-border)" stroke-width="1" stroke-dasharray="2,3"/>
    <line x1="${x1}" y1="28" x2="${x1}" y2="212" stroke="var(--border)" stroke-width="1.3" stroke-dasharray="3,3"/>
    <line x1="${x2}" y1="28" x2="${x2}" y2="212" stroke="var(--card-border)" stroke-width="1" stroke-dasharray="2,3"/>
    <text x="${x05}" y="228" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">0.5</text>
    <text x="${x1}" y="228" text-anchor="middle" font-size="12.5" font-family="monospace" font-weight="600" fill="var(--foreground)">1.0</text>
    <text x="${x2}" y="228" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">2.0</text>
    <text x="183" y="248" text-anchor="middle" font-size="12.5" fill="var(--muted-foreground)">Hazard Ratio (Log)</text>
    ${hrSvg}
    <line x1="236" y1="10" x2="236" y2="250" stroke="var(--card-border)" stroke-width="1"/>
    <text x="244" y="18" font-size="12.8" font-weight="700" fill="var(--foreground)">B. Tryptic CSF MS (n=77)</text>
    <text x="244" y="36" font-size="12.4" fill="var(--muted-foreground)">NEFL vs NEFH r=0.278 (p=0.014)</text>
    <rect x="244" y="48" width="102" height="76" rx="6" fill="var(--background)" stroke="var(--error)" stroke-width="1.6"/>
    <text x="295" y="70" text-anchor="middle" font-size="12.5" font-weight="700" fill="var(--error)">Missed NEFL</text>
    <text x="295" y="92" text-anchor="middle" font-size="12.8" font-family="monospace" font-weight="700" fill="var(--error)">12/16 (75%)</text>
    <text x="295" y="112" text-anchor="middle" font-size="12.4" fill="var(--muted-foreground)">Hi MS NEFH</text>
    <rect x="352" y="48" width="102" height="76" rx="6" fill="var(--background)" stroke="var(--border)" stroke-width="1"/>
    <text x="403" y="78" text-anchor="middle" font-size="12.5" font-weight="600" fill="var(--foreground)">Concordant</text>
    <text x="403" y="100" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">4/16 &gt;p80</text>
    <rect x="244" y="132" width="102" height="76" rx="6" fill="var(--background)" stroke="var(--success)" stroke-width="1.5"/>
    <text x="295" y="162" text-anchor="middle" font-size="12.5" font-weight="700" fill="var(--success)">Both &le;p80</text>
    <text x="295" y="184" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">49/77 DIA</text>
    <rect x="352" y="132" width="102" height="76" rx="6" fill="var(--background)" stroke="var(--warning)" stroke-width="1.2" stroke-dasharray="3,2"/>
    <text x="403" y="162" text-anchor="middle" font-size="12.5" font-weight="600" fill="var(--warning)">Hi NEFL Only</text>
    <text x="403" y="184" text-anchor="middle" font-size="12.5" font-family="monospace" fill="var(--muted-foreground)">12/77 DIA</text>
    <text x="349" y="248" text-anchor="middle" font-size="12.4" fill="var(--muted-foreground)">31.2% tryptic MS P80 discord.</text>
  </svg>`;
}

function renderSignatureSvg(candId, sig){
  if(sig.kind === 'mwc_sarm1') return renderMwcSarm1Svg();
  if(sig.kind === 'il2_strat') return renderIl2StratSvg();
  return renderLocusSsoSvg(candId, sig);
}
"""
