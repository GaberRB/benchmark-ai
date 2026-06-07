"""
report.py — Gera relatório HTML interativo do benchmark.

Modos:
  python metrics/report.py                              # Java vs Kotlin (padrão)
  python metrics/report.py --java j.json --kotlin k.json
  python metrics/report.py --mode arch                  # comparativo de arquiteturas
  python metrics/report.py --mode arch --files a.json b.json c.json

Saída:
  metrics/reports/benchmark_report_<timestamp>.html
  metrics/reports/arch_report_<timestamp>.html
"""

import argparse, json, os, glob
from datetime import datetime, timezone

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def find_latest(language: str) -> str | None:
    pattern = os.path.join(REPORTS_DIR, f"{language}_*.json")
    files = [f for f in glob.glob(pattern) if "snapshot" not in os.path.basename(f)]
    return max(files, key=os.path.getmtime) if files else None


def load(path: str) -> dict:
    # utf-8-sig trata tanto UTF-8 puro quanto UTF-8 com BOM (gerado pelo PowerShell)
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return json.load(f)


def generate(java: dict, kotlin: dict, java_file: str, kotlin_file: str) -> str:
    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "java_file": os.path.basename(java_file),
        "kotlin_file": os.path.basename(kotlin_file),
        "java": java,
        "kotlin": kotlin,
    }
    json_str = json.dumps(data, ensure_ascii=False, indent=2).replace("</script>", "<\\/script>")
    return HTML.replace("__DATA__", json_str)


# ─────────────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Benchmark — Java vs Kotlin</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root {
  --java: #f89820;
  --kotlin: #7f52ff;
  --java-bg: rgba(248,152,32,0.7);
  --kotlin-bg: rgba(127,82,255,0.7);
  --java-dim: rgba(248,152,32,0.12);
  --kotlin-dim: rgba(127,82,255,0.12);
  --bg: #0d0f18;
  --surface: #161927;
  --surface2: #1e2236;
  --border: #272b42;
  --text: #dde3f0;
  --dim: #7a88a8;
  --green: #4caf50;
  --red: #ef5350;
  --radius: 12px;
  --shadow: 0 2px 12px rgba(0,0,0,0.4);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; line-height: 1.6; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

/* Header */
.hdr { background: linear-gradient(140deg, #12142a 0%, #1c1040 100%); border-bottom: 1px solid var(--border); padding: 40px 0 28px; }
.hdr h1 { font-size: 30px; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(90deg, var(--java) 0%, var(--kotlin) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 4px; }
.hdr-sub { color: var(--dim); font-size: 15px; margin-bottom: 18px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; padding: 4px 12px; font-size: 12px; color: var(--dim); }
.tag b { color: var(--text); }

/* Nav */
.nav { background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
.nav-inner { display: flex; overflow-x: auto; scrollbar-width: none; }
.nav-inner::-webkit-scrollbar { display: none; }
.nav-a { padding: 13px 18px; font-size: 13px; color: var(--dim); text-decoration: none; white-space: nowrap; border-bottom: 2px solid transparent; transition: all .15s; }
.nav-a:hover { color: var(--text); border-color: #4a4f78; }

/* Main layout */
.main { padding: 36px 0 60px; }
.section { margin-bottom: 52px; }
.sec-title { font-size: 17px; font-weight: 700; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }

/* Cards */
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 16px; box-shadow: var(--shadow); transition: border-color .15s; }
.card:hover { border-color: #3d4570; }
.card-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: .8px; color: var(--dim); margin-bottom: 14px; }
.card-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; font-size: 13px; }
.lang-j { background: var(--java-dim); color: var(--java); font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; }
.lang-k { background: var(--kotlin-dim); color: var(--kotlin); font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; }
.card-val { font-weight: 700; font-size: 15px; }
.badge { font-size: 10px; background: rgba(76,175,80,.15); color: var(--green); border-radius: 10px; padding: 2px 6px; font-weight: 600; }
.card-delta { font-size: 11px; color: var(--dim); margin-top: 6px; text-align: center; }

/* Charts */
.charts-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }
.ch-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); }
.ch-title { font-size: 12px; font-weight: 600; color: var(--dim); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 16px; }

/* Table */
.tbl-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow); }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead tr { background: var(--surface2); }
th { padding: 11px 14px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .7px; color: var(--dim); font-weight: 600; }
td { padding: 9px 14px; border-top: 1px solid var(--border); }
tr:hover td { background: rgba(255,255,255,.018); }
.t-cat { color: var(--text); font-weight: 600; }
.t-dim { color: var(--dim); }
.t-j { color: var(--java); font-weight: 600; }
.t-k { color: var(--kotlin); font-weight: 600; }
.t-win { text-align: center; }
.wj { color: var(--java); }
.wk { color: var(--kotlin); }
.wt { color: var(--dim); font-size: 12px; }

/* Footer */
.footer { border-top: 1px solid var(--border); padding: 20px 0; text-align: center; color: var(--dim); font-size: 12px; }

/* No CDN warning */
.no-cdn { background: rgba(239,83,80,.12); border: 1px solid rgba(239,83,80,.3); border-radius: 8px; padding: 12px 16px; color: #ef9a9a; font-size: 13px; margin-bottom: 20px; display: none; }

@media (max-width: 768px) {
  .cards { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<header class="hdr">
  <div class="container">
    <h1>AI Coding Benchmark</h1>
    <p class="hdr-sub">Task Manager REST API &mdash; Java vs Kotlin (Modo 1: Agente Sequencial)</p>
    <div class="tags" id="hdr-tags"></div>
  </div>
</header>

<nav class="nav">
  <div class="container">
    <div class="nav-inner">
      <a class="nav-a" href="#resumo">📊 Resumo</a>
      <a class="nav-a" href="#tokens">🔢 Tokens</a>
      <a class="nav-a" href="#velocidade">⚡ Velocidade</a>
      <a class="nav-a" href="#erros">🐛 Erros</a>
      <a class="nav-a" href="#qualidade">✅ Qualidade</a>
      <a class="nav-a" href="#e2e">🌐 E2E</a>
      <a class="nav-a" href="#tabela">📋 Tabela</a>
    </div>
  </div>
</nav>

<main class="main">
<div class="container">

  <div class="no-cdn" id="no-cdn">
    ⚠️ Chart.js não carregou (sem internet?). Os gráficos não aparecem, mas a tabela comparativa ainda funciona.
  </div>

  <section class="section" id="resumo">
    <h2 class="sec-title">📊 Resumo Executivo</h2>
    <div class="cards" id="cards"></div>
  </section>

  <section class="section" id="tokens">
    <h2 class="sec-title">🔢 Tokens &amp; Custo</h2>
    <div class="charts-row">
      <div class="ch-card">
        <div class="ch-title">Tokens Ativos (Input + Output)</div>
        <canvas id="ch-tok-active"></canvas>
      </div>
      <div class="ch-card">
        <div class="ch-title">Tokens de Cache</div>
        <canvas id="ch-tok-cache"></canvas>
      </div>
      <div class="ch-card">
        <div class="ch-title">Custo USD por Categoria</div>
        <canvas id="ch-cost"></canvas>
      </div>
    </div>
  </section>

  <section class="section" id="velocidade">
    <h2 class="sec-title">⚡ Velocidade &amp; Iterações</h2>
    <div class="charts-row">
      <div class="ch-card">
        <div class="ch-title">Velocidade de Entrega</div>
        <canvas id="ch-speed"></canvas>
      </div>
      <div class="ch-card">
        <div class="ch-title">Iterações da IA</div>
        <canvas id="ch-iter"></canvas>
      </div>
    </div>
  </section>

  <section class="section" id="erros">
    <h2 class="sec-title">🐛 Erros de Desenvolvimento</h2>
    <div class="charts-row" style="grid-template-columns:1fr">
      <div class="ch-card">
        <div class="ch-title">Distribuição de Erros por Tipo</div>
        <canvas id="ch-errors" style="max-height:260px"></canvas>
      </div>
    </div>
  </section>

  <section class="section" id="qualidade">
    <h2 class="sec-title">✅ Qualidade de Código</h2>
    <div class="charts-row">
      <div class="ch-card">
        <div class="ch-title">Linhas de Código (LOC)</div>
        <canvas id="ch-loc"></canvas>
      </div>
      <div class="ch-card">
        <div class="ch-title">Cobertura &amp; Proporção de Testes (%)</div>
        <canvas id="ch-coverage"></canvas>
      </div>
    </div>
  </section>

  <section class="section" id="e2e">
    <h2 class="sec-title">🌐 Testes E2E (12 Cenários)</h2>
    <div class="charts-row" style="max-width:560px">
      <div class="ch-card">
        <div class="ch-title">☕ Java</div>
        <canvas id="ch-e2e-j" style="max-height:180px"></canvas>
      </div>
      <div class="ch-card">
        <div class="ch-title">🟣 Kotlin</div>
        <canvas id="ch-e2e-k" style="max-height:180px"></canvas>
      </div>
    </div>
  </section>

  <section class="section" id="tabela">
    <h2 class="sec-title">📋 Tabela Comparativa Completa</h2>
    <div class="tbl-wrap"><table id="tbl"></table></div>
  </section>

</div>
</main>

<footer class="footer">
  <div class="container">
    Gerado por <b>metrics/report.py</b> &nbsp;&middot;&nbsp; <span id="gen-at"></span>
  </div>
</footer>

<script>
const DATA = __DATA__;
const J = DATA.java  || {};
const K = DATA.kotlin || {};

// Safe nested get with numeric default
function gv(obj, ...keys) {
  let cur = obj;
  for (const k of keys) {
    if (cur == null || typeof cur !== 'object') return 0;
    cur = cur[k];
  }
  return (cur != null && cur !== '') ? cur : 0;
}
function gs(obj, ...keys) { // string version
  let cur = obj;
  for (const k of keys) {
    if (cur == null || typeof cur !== 'object') return '—';
    cur = cur[k];
  }
  return cur != null ? String(cur) : '—';
}

// ── Header ──────────────────────────────────────────────────────────────────
document.getElementById('hdr-tags').innerHTML = [
  `<span class="tag">Modelo: <b>${gs(J,'model','primary_model')}</b></span>`,
  `<span class="tag">Claude Code: <b>${gs(J,'model','claude_code_version')}</b></span>`,
  `<span class="tag">Gerado: <b>${DATA.generated_at}</b></span>`,
  `<span class="tag">Java: <b>${DATA.java_file}</b></span>`,
  `<span class="tag">Kotlin: <b>${DATA.kotlin_file}</b></span>`,
].join('');
document.getElementById('gen-at').textContent = DATA.generated_at;

// CDN check
if (typeof Chart === 'undefined') {
  document.getElementById('no-cdn').style.display = 'block';
}

// ── Summary Cards ────────────────────────────────────────────────────────────
function pct(jV, kV) {
  if (!kV) return '';
  const d = ((jV - kV) / kV * 100).toFixed(1);
  return `Java ${d > 0 ? '+' : ''}${d}% vs Kotlin`;
}
function makeCard(lbl, jV, kV, jFmt, kFmt, lowerBetter) {
  const jWins = lowerBetter ? jV <= kV : jV >= kV;
  return `<div class="card">
    <div class="card-lbl">${lbl}</div>
    <div class="card-row"><span class="lang-j">Java</span><span class="card-val">${jFmt}</span>${jWins ? '<span class="badge">✓ melhor</span>' : ''}</div>
    <div class="card-row"><span class="lang-k">Kotlin</span><span class="card-val">${kFmt}</span>${!jWins ? '<span class="badge">✓ melhor</span>' : ''}</div>
    <div class="card-delta">${pct(jV, kV)}</div>
  </div>`;
}

const jCost = gv(J,'tokens','cost_usd'), kCost = gv(K,'tokens','cost_usd');
const jDur  = gv(J,'speed','session_duration_min'), kDur = gv(K,'speed','session_duration_min');
const jErr  = gv(J,'errors','total_errors'), kErr = gv(K,'errors','total_errors');
const jAPI  = gv(J,'tokens','api_calls_count'), kAPI = gv(K,'tokens','api_calls_count');
const jCov  = gv(J,'code_quality','test_coverage_line_pct'), kCov = gv(K,'code_quality','test_coverage_line_pct');
const jE2e  = gv(J,'e2e','passed'), kE2e = gv(K,'e2e','passed');
const jLoc  = gv(J,'code_quality','lines_of_code'), kLoc = gv(K,'code_quality','lines_of_code');

document.getElementById('cards').innerHTML = [
  makeCard('💰 Custo Total', jCost, kCost, `$${jCost.toFixed(4)}`, `$${kCost.toFixed(4)}`, true),
  makeCard('⏱ Duração (min)', jDur, kDur, `${jDur.toFixed(1)} min`, `${kDur.toFixed(1)} min`, true),
  makeCard('🐛 Total de Erros', jErr, kErr, String(jErr), String(kErr), true),
  makeCard('📡 Chamadas API', jAPI, kAPI, String(jAPI), String(kAPI), true),
  makeCard('🎯 Cobertura Linha', jCov, kCov, `${jCov}%`, `${kCov}%`, false),
  makeCard('✅ E2E Passou', jE2e, kE2e, `${jE2e}/12`, `${kE2e}/12`, false),
  makeCard('📏 LOC Produção', jLoc, kLoc, String(jLoc), String(kLoc), false),
].join('');

if (typeof Chart === 'undefined') {
  document.getElementById('gen-at').textContent = DATA.generated_at;
  // Skip charts, table still renders
} else {

// ── Chart defaults ──────────────────────────────────────────────────────────
Chart.defaults.color = '#7a88a8';
Chart.defaults.font.family = "system-ui, -apple-system, sans-serif";
Chart.defaults.font.size = 12;

const JC = '#f89820', KC = '#7f52ff';
const JBG = 'rgba(248,152,32,0.72)', KBG = 'rgba(127,82,255,0.72)';
const GRID = 'rgba(255,255,255,0.05)';

function bar(id, labels, datasets, opts={}) {
  new Chart(document.getElementById(id), {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { position: 'top', labels: { color: '#dde3f0', padding: 14, boxWidth: 12 } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const v = ctx.raw;
              if (opts.pre) return ` ${opts.pre}${typeof v==='number' ? v.toLocaleString('pt-BR',{maximumFractionDigits:4}) : v}`;
              return ` ${typeof v==='number' ? v.toLocaleString('pt-BR',{maximumFractionDigits:4}) : v}${opts.suf||''}`;
            }
          }
        }
      },
      scales: {
        x: { stacked: opts.stacked||false, grid: { color: GRID }, ticks: { color: '#7a88a8' } },
        y: {
          stacked: opts.stacked||false,
          grid: { color: GRID },
          ticks: {
            color: '#7a88a8',
            callback: v => opts.pre ? `${opts.pre}${v.toLocaleString('pt-BR')}` : `${v.toLocaleString('pt-BR')}${opts.suf||''}`
          }
        }
      }
    }
  });
}

function donut(id, labels, data, colors) {
  new Chart(document.getElementById(id), {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }] },
    options: {
      responsive: true, maintainAspectRatio: true, cutout: '68%',
      plugins: { legend: { position: 'bottom', labels: { color: '#dde3f0', padding: 12, boxWidth: 12 } } }
    }
  });
}

// Tokens activos
bar('ch-tok-active',
  ['Input Tokens', 'Output Tokens'],
  [
    { label: 'Java',   data: [gv(J,'tokens','input_tokens_total'), gv(J,'tokens','output_tokens_total')], backgroundColor: JBG, borderColor: JC, borderWidth: 1 },
    { label: 'Kotlin', data: [gv(K,'tokens','input_tokens_total'), gv(K,'tokens','output_tokens_total')], backgroundColor: KBG, borderColor: KC, borderWidth: 1 },
  ]
);

// Tokens cache
bar('ch-tok-cache',
  ['Cache Creation', 'Cache Read'],
  [
    { label: 'Java',   data: [gv(J,'tokens','cache_creation_tokens'), gv(J,'tokens','cache_read_tokens')], backgroundColor: JBG, borderColor: JC, borderWidth: 1 },
    { label: 'Kotlin', data: [gv(K,'tokens','cache_creation_tokens'), gv(K,'tokens','cache_read_tokens')], backgroundColor: KBG, borderColor: KC, borderWidth: 1 },
  ]
);

// Custo por categoria
const P = { inp: 3/1e6, out: 15/1e6, cc: 3.75/1e6, cr: 0.30/1e6 };
const jT = J.tokens||{}, kT = K.tokens||{};
bar('ch-cost',
  ['Input', 'Output', 'Cache Create', 'Cache Read'],
  [
    { label: 'Java',   data: [+(jT.input_tokens_total*P.inp).toFixed(4), +(jT.output_tokens_total*P.out).toFixed(4), +(jT.cache_creation_tokens*P.cc).toFixed(4), +(jT.cache_read_tokens*P.cr).toFixed(4)], backgroundColor: JBG, borderColor: JC, borderWidth: 1 },
    { label: 'Kotlin', data: [+(kT.input_tokens_total*P.inp).toFixed(4), +(kT.output_tokens_total*P.out).toFixed(4), +(kT.cache_creation_tokens*P.cc).toFixed(4), +(kT.cache_read_tokens*P.cr).toFixed(4)], backgroundColor: KBG, borderColor: KC, borderWidth: 1 },
  ], { pre: '$' }
);

// Velocidade
bar('ch-speed',
  ['Duração (min)', 'Tempo/Endpoint (min)', 'Throughput (ep/h)'],
  [
    { label: 'Java',   data: [gv(J,'speed','session_duration_min'), gv(J,'speed','time_per_endpoint_min'), gv(J,'speed','throughput_endpoints_per_hour')], backgroundColor: JBG, borderColor: JC, borderWidth: 1 },
    { label: 'Kotlin', data: [gv(K,'speed','session_duration_min'), gv(K,'speed','time_per_endpoint_min'), gv(K,'speed','throughput_endpoints_per_hour')], backgroundColor: KBG, borderColor: KC, borderWidth: 1 },
  ]
);

// Iterações
bar('ch-iter',
  ['Total de Turns', 'Tool Calls', 'Chamadas API'],
  [
    { label: 'Java',   data: [gv(J,'iterations','total_turns'), gv(J,'iterations','tool_calls_total'), gv(J,'tokens','api_calls_count')], backgroundColor: JBG, borderColor: JC, borderWidth: 1 },
    { label: 'Kotlin', data: [gv(K,'iterations','total_turns'), gv(K,'iterations','tool_calls_total'), gv(K,'tokens','api_calls_count')], backgroundColor: KBG, borderColor: KC, borderWidth: 1 },
  ]
);

// Erros stacked
new Chart(document.getElementById('ch-errors'), {
  type: 'bar',
  data: {
    labels: ['Java', 'Kotlin'],
    datasets: [
      { label: 'Compilação', data: [gv(J,'errors','compile_errors'), gv(K,'errors','compile_errors')], backgroundColor: 'rgba(239,83,80,.8)', borderWidth: 0 },
      { label: 'Runtime',    data: [gv(J,'errors','runtime_errors'), gv(K,'errors','runtime_errors')], backgroundColor: 'rgba(255,167,38,.8)', borderWidth: 0 },
      { label: 'Testes',     data: [gv(J,'errors','test_failures'),  gv(K,'errors','test_failures')],  backgroundColor: 'rgba(66,165,245,.8)', borderWidth: 0 },
    ]
  },
  options: {
    responsive: true, maintainAspectRatio: true,
    plugins: { legend: { position: 'top', labels: { color: '#dde3f0', padding: 14, boxWidth: 12 } } },
    scales: {
      x: { stacked: true, grid: { color: GRID } },
      y: { stacked: true, grid: { color: GRID }, ticks: { stepSize: 1, color: '#7a88a8' } }
    }
  }
});

// LOC
bar('ch-loc',
  ['Produção (LOC)', 'Testes (LOC)', 'Total (LOC)'],
  [
    { label: 'Java',   data: [gv(J,'code_quality','lines_of_code'), gv(J,'code_quality','test_lines_of_code'), gv(J,'code_quality','lines_of_code')+gv(J,'code_quality','test_lines_of_code')], backgroundColor: JBG, borderColor: JC, borderWidth: 1 },
    { label: 'Kotlin', data: [gv(K,'code_quality','lines_of_code'), gv(K,'code_quality','test_lines_of_code'), gv(K,'code_quality','lines_of_code')+gv(K,'code_quality','test_lines_of_code')], backgroundColor: KBG, borderColor: KC, borderWidth: 1 },
  ]
);

// Cobertura
bar('ch-coverage',
  ['Cobertura Linha (%)', 'Cobertura Branch (%)', 'Proporção Testes (%)'],
  [
    { label: 'Java',   data: [gv(J,'code_quality','test_coverage_line_pct'), gv(J,'code_quality','test_coverage_branch_pct'), gv(J,'code_quality','test_ratio_pct')], backgroundColor: JBG, borderColor: JC, borderWidth: 1 },
    { label: 'Kotlin', data: [gv(K,'code_quality','test_coverage_line_pct'), gv(K,'code_quality','test_coverage_branch_pct'), gv(K,'code_quality','test_ratio_pct')], backgroundColor: KBG, borderColor: KC, borderWidth: 1 },
  ], { suf: '%' }
);

// E2E doughnuts
const jP = gv(J,'e2e','passed'), jF = gv(J,'e2e','failed');
const kP = gv(K,'e2e','passed'), kF = gv(K,'e2e','failed');
donut('ch-e2e-j', [`Passou (${jP})`, `Falhou (${jF})`], [jP||0, jF||12-jP], ['rgba(76,175,80,.85)','rgba(239,83,80,.85)']);
donut('ch-e2e-k', [`Passou (${kP})`, `Falhou (${kF})`], [kP||0, kF||12-kP], ['rgba(76,175,80,.85)','rgba(239,83,80,.85)']);

} // end typeof Chart check

// ── Comparison Table ─────────────────────────────────────────────────────────
const ROWS = [
  // [cat, metric, jVal, kVal, fmt, lowerBetter, hasWinner]
  ['Modelo', 'Modelo Principal',       gs(J,'model','primary_model'),       gs(K,'model','primary_model'),       's', false, false],
  ['Modelo', 'Versão Claude Code',     gs(J,'model','claude_code_version'), gs(K,'model','claude_code_version'), 's', false, false],
  ['Modelo', 'Entrypoint',             gs(J,'model','entrypoint'),          gs(K,'model','entrypoint'),          's', false, false],
  ['Modelo', 'Stop: max_tokens (%)',   gv(J,'model','stop_reason_max_tokens_pct'), gv(K,'model','stop_reason_max_tokens_pct'), 'p', true, true],
  ['Tokens', 'Input Tokens',           gv(J,'tokens','input_tokens_total'),    gv(K,'tokens','input_tokens_total'),    'n', true,  true],
  ['Tokens', 'Output Tokens',          gv(J,'tokens','output_tokens_total'),   gv(K,'tokens','output_tokens_total'),   'n', true,  true],
  ['Tokens', 'Cache Creation',         gv(J,'tokens','cache_creation_tokens'), gv(K,'tokens','cache_creation_tokens'), 'n', true,  true],
  ['Tokens', 'Cache Read',             gv(J,'tokens','cache_read_tokens'),     gv(K,'tokens','cache_read_tokens'),     'n', true,  true],
  ['Tokens', 'Cache Hit Rate (%)',     gv(J,'tokens','cache_hit_rate_pct'),    gv(K,'tokens','cache_hit_rate_pct'),    'p', false, false],
  ['Tokens', 'Chamadas API',           gv(J,'tokens','api_calls_count'),       gv(K,'tokens','api_calls_count'),       'n', true,  true],
  ['Custo',  'Custo Total (USD)',       gv(J,'tokens','cost_usd'),              gv(K,'tokens','cost_usd'),              'u', true,  true],
  ['Custo',  'Custo/Endpoint (USD)',    gv(J,'tokens','cost_per_endpoint_usd'), gv(K,'tokens','cost_per_endpoint_usd'), 'u', true,  true],
  ['Velocidade', 'Duração (min)',       gv(J,'speed','session_duration_min'),           gv(K,'speed','session_duration_min'),           'n', true,  true],
  ['Velocidade', 'Tempo/Endpoint (min)',gv(J,'speed','time_per_endpoint_min'),          gv(K,'speed','time_per_endpoint_min'),          'n', true,  true],
  ['Velocidade', 'Throughput (ep/h)',   gv(J,'speed','throughput_endpoints_per_hour'),  gv(K,'speed','throughput_endpoints_per_hour'),  'n', false, true],
  ['Iterações', 'Total de Turns',       gv(J,'iterations','total_turns'),       gv(K,'iterations','total_turns'),       'n', true,  true],
  ['Iterações', 'Tool Calls',           gv(J,'iterations','tool_calls_total'),  gv(K,'iterations','tool_calls_total'),  'n', true,  true],
  ['Erros',  'Erros de Compilação',    gv(J,'errors','compile_errors'),        gv(K,'errors','compile_errors'),        'n', true,  true],
  ['Erros',  'Erros de Runtime',       gv(J,'errors','runtime_errors'),        gv(K,'errors','runtime_errors'),        'n', true,  true],
  ['Erros',  'Falhas de Teste',        gv(J,'errors','test_failures'),         gv(K,'errors','test_failures'),         'n', true,  true],
  ['Erros',  'Total de Erros',         gv(J,'errors','total_errors'),          gv(K,'errors','total_errors'),          'n', true,  true],
  ['Qualidade', 'LOC Produção',         gv(J,'code_quality','lines_of_code'),             gv(K,'code_quality','lines_of_code'),             'n', false, false],
  ['Qualidade', 'LOC Testes',           gv(J,'code_quality','test_lines_of_code'),        gv(K,'code_quality','test_lines_of_code'),        'n', false, false],
  ['Qualidade', 'Cobertura Linha (%)',  gv(J,'code_quality','test_coverage_line_pct'),    gv(K,'code_quality','test_coverage_line_pct'),    'p', false, true],
  ['Qualidade', 'Cobertura Branch (%)', gv(J,'code_quality','test_coverage_branch_pct'),  gv(K,'code_quality','test_coverage_branch_pct'),  'p', false, true],
  ['Qualidade', 'Proporção Testes (%)', gv(J,'code_quality','test_ratio_pct'),            gv(K,'code_quality','test_ratio_pct'),            'p', false, false],
  ['E2E',    'Cenários Passados',      gv(J,'e2e','passed'),                   gv(K,'e2e','passed'),                   'n', false, true],
  ['E2E',    'Cenários Falhados',      gv(J,'e2e','failed'),                   gv(K,'e2e','failed'),                   'n', true,  true],
];

function fmt(v, t) {
  if (t === 's') return v || '—';
  if (typeof v !== 'number') return '—';
  if (t === 'u') return `$${v.toFixed(4)}`;
  if (t === 'p') return `${v.toFixed(1)}%`;
  return v.toLocaleString('pt-BR', {maximumFractionDigits: 2});
}

function winCell(jv, kv, lower, has) {
  if (!has || typeof jv !== 'number' || typeof kv !== 'number') return '<td class="t-win"><span class="wt">—</span></td>';
  if (jv === kv) return '<td class="t-win"><span class="wt">Empate</span></td>';
  const jw = lower ? jv < kv : jv > kv;
  return jw ? '<td class="t-win"><span class="wj">☕ Java</span></td>' : '<td class="t-win"><span class="wk">🟣 Kotlin</span></td>';
}

let lastCat = null;
let html = `<thead><tr>
  <th>Categoria</th><th>Métrica</th>
  <th style="color:var(--java)">☕ Java</th>
  <th style="color:var(--kotlin)">🟣 Kotlin</th>
  <th>Vencedor</th>
</tr></thead><tbody>`;

ROWS.forEach(([cat, metric, jv, kv, t, lower, has]) => {
  const newCat = cat !== lastCat;
  if (newCat) lastCat = cat;
  html += `<tr${newCat ? ' style="border-top:2px solid var(--border)"' : ''}>
    <td class="${newCat ? 't-cat' : 't-dim'}" style="${!newCat ? 'color:transparent' : ''}">${cat}</td>
    <td class="t-dim">${metric}</td>
    <td class="t-j">${fmt(jv, t)}</td>
    <td class="t-k">${fmt(kv, t)}</td>
    ${winCell(jv, kv, lower, has)}
  </tr>`;
});
html += '</tbody>';
document.getElementById('tbl').innerHTML = html;
</script>
</body>
</html>"""
# ─────────────────────────────────────────────────────────────────────────────


def find_arch_reports() -> list[str]:
    """Localiza todos os arch-*.json excluindo snapshots."""
    pattern = os.path.join(REPORTS_DIR, "arch-*.json")
    files = [f for f in glob.glob(pattern) if "snapshot" not in os.path.basename(f)]
    files.sort(key=os.path.getmtime)
    return files


def generate_arch(datasets: list[dict], files: list[str]) -> str:
    """Gera HTML comparativo para N arquiteturas."""
    ARCH_COLORS = ["#4fc3f7", "#81c784", "#ffb74d", "#f06292", "#ce93d8", "#80cbc4"]
    ARCH_BG     = ["rgba(79,195,247,0.72)", "rgba(129,199,132,0.72)",
                   "rgba(255,183,77,0.72)", "rgba(240,98,146,0.72)",
                   "rgba(206,147,216,0.72)", "rgba(128,203,196,0.72)"]

    arch_names = []
    for d in datasets:
        # Tenta várias posições onde o nome da arquitetura pode estar
        name = (
            d.get("architecture")                          # root (hexagonal manual)
            or (d.get("meta") or {}).get("architecture")   # meta.architecture (mvc)
            or (d.get("meta") or {}).get("language", "")   # meta.language (arch-clean → clean)
            or "unknown"
        )
        # Remove prefixo "arch-" se presente (ex: "arch-clean" → "clean")
        if name.startswith("arch-"):
            name = name[5:]
        arch_names.append(name)

    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "files": [os.path.basename(f) for f in files],
        "arch_names": arch_names,
        "datasets": datasets,
        "colors": ARCH_COLORS[:len(datasets)],
        "bg_colors": ARCH_BG[:len(datasets)],
    }
    json_str = json.dumps(data, ensure_ascii=False, indent=2).replace("</script>", "<\\/script>")
    return ARCH_HTML.replace("__DATA__", json_str)


ARCH_HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Benchmark — Padrões Arquiteturais</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg: #0d0f18; --surface: #161927; --surface2: #1e2236; --border: #272b42;
  --text: #dde3f0; --dim: #7a88a8; --green: #4caf50; --red: #ef5350;
  --radius: 12px; --shadow: 0 2px 12px rgba(0,0,0,0.4);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; line-height: 1.6; }
.container { max-width: 1300px; margin: 0 auto; padding: 0 24px; }
.hdr { background: linear-gradient(140deg, #12142a 0%, #0a1a2a 100%); border-bottom: 1px solid var(--border); padding: 40px 0 28px; }
.hdr h1 { font-size: 30px; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(90deg, #4fc3f7 0%, #81c784 40%, #ffb74d 70%, #f06292 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 4px; }
.hdr-sub { color: var(--dim); font-size: 15px; margin-bottom: 18px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; padding: 4px 12px; font-size: 12px; color: var(--dim); }
.tag b { color: var(--text); }
.nav { background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
.nav-inner { display: flex; overflow-x: auto; scrollbar-width: none; }
.nav-inner::-webkit-scrollbar { display: none; }
.nav-a { padding: 13px 18px; font-size: 13px; color: var(--dim); text-decoration: none; white-space: nowrap; border-bottom: 2px solid transparent; }
.nav-a:hover { color: var(--text); }
.main { padding: 36px 0 60px; }
.section { margin-bottom: 52px; }
.sec-title { font-size: 17px; font-weight: 700; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }
.charts-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 18px; }
.ch-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); }
.ch-title { font-size: 12px; font-weight: 600; color: var(--dim); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 16px; }
.tbl-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow-x: auto; box-shadow: var(--shadow); }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead tr { background: var(--surface2); }
th { padding: 11px 14px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .7px; color: var(--dim); font-weight: 600; white-space: nowrap; }
td { padding: 9px 14px; border-top: 1px solid var(--border); }
tr:hover td { background: rgba(255,255,255,.018); }
.t-cat { color: var(--text); font-weight: 600; }
.t-dim { color: var(--dim); }
.t-best { font-weight: 700; }
.footer { border-top: 1px solid var(--border); padding: 20px 0; text-align: center; color: var(--dim); font-size: 12px; }
</style>
</head>
<body>
<header class="hdr">
  <div class="container">
    <h1>AI Benchmark — Padrões Arquiteturais</h1>
    <p class="hdr-sub">Task Manager REST API &mdash; Comparativo de Arquiteturas (Java 21, Spring Boot 3.2)</p>
    <div class="tags" id="hdr-tags"></div>
  </div>
</header>
<nav class="nav">
  <div class="container">
    <div class="nav-inner">
      <a class="nav-a" href="#custo">💰 Custo</a>
      <a class="nav-a" href="#velocidade">⚡ Velocidade</a>
      <a class="nav-a" href="#erros">🐛 Erros</a>
      <a class="nav-a" href="#qualidade">✅ Qualidade</a>
      <a class="nav-a" href="#arquitetura">🏗 Arquitetura</a>
      <a class="nav-a" href="#tabela">📋 Tabela</a>
    </div>
  </div>
</nav>
<main class="main">
<div class="container">

  <section class="section" id="custo">
    <h2 class="sec-title">💰 Custo &amp; Tokens</h2>
    <div class="charts-row">
      <div class="ch-card"><div class="ch-title">Custo Total (USD)</div><canvas id="ch-cost"></canvas></div>
      <div class="ch-card"><div class="ch-title">Output Tokens</div><canvas id="ch-out-tok"></canvas></div>
      <div class="ch-card"><div class="ch-title">Chamadas API</div><canvas id="ch-api"></canvas></div>
    </div>
  </section>

  <section class="section" id="velocidade">
    <h2 class="sec-title">⚡ Velocidade</h2>
    <div class="charts-row">
      <div class="ch-card"><div class="ch-title">Duração da Sessão (min)</div><canvas id="ch-dur"></canvas></div>
      <div class="ch-card"><div class="ch-title">Total de Turns</div><canvas id="ch-turns"></canvas></div>
    </div>
  </section>

  <section class="section" id="erros">
    <h2 class="sec-title">🐛 Erros de Desenvolvimento</h2>
    <div class="charts-row" style="grid-template-columns:1fr">
      <div class="ch-card"><div class="ch-title">Erros por Tipo</div><canvas id="ch-errors" style="max-height:280px"></canvas></div>
    </div>
  </section>

  <section class="section" id="qualidade">
    <h2 class="sec-title">✅ Qualidade de Código</h2>
    <div class="charts-row">
      <div class="ch-card"><div class="ch-title">LOC de Produção</div><canvas id="ch-loc"></canvas></div>
      <div class="ch-card"><div class="ch-title">Cobertura de Linha (%)</div><canvas id="ch-cov"></canvas></div>
    </div>
  </section>

  <section class="section" id="arquitetura">
    <h2 class="sec-title">🏗 Métricas de Arquitetura</h2>
    <div class="charts-row">
      <div class="ch-card"><div class="ch-title">Arquivos .java Criados</div><canvas id="ch-files"></canvas></div>
      <div class="ch-card"><div class="ch-title">Interfaces Criadas</div><canvas id="ch-ifaces"></canvas></div>
      <div class="ch-card"><div class="ch-title">Conformidade Arquitetural (0-10)</div><canvas id="ch-conf"></canvas></div>
    </div>
  </section>

  <section class="section" id="tabela">
    <h2 class="sec-title">📋 Tabela Comparativa</h2>
    <div class="tbl-wrap"><table id="tbl"></table></div>
  </section>

</div>
</main>
<footer class="footer">
  <div class="container">Gerado por <b>metrics/report.py --mode arch</b> &nbsp;&middot;&nbsp; <span id="gen-at"></span></div>
</footer>

<script>
const DATA = __DATA__;
const DS = DATA.datasets || [];
const NAMES = DATA.arch_names || [];
const COLORS = DATA.colors || [];
const BGS = DATA.bg_colors || [];

document.getElementById('gen-at').textContent = DATA.generated_at;
document.getElementById('hdr-tags').innerHTML = [
  `<span class="tag">Arquiteturas: <b>${NAMES.length}</b></span>`,
  `<span class="tag">Gerado: <b>${DATA.generated_at}</b></span>`,
  ...NAMES.map((n, i) => `<span class="tag" style="border-color:${COLORS[i]};color:${COLORS[i]}">${n}</span>`)
].join('');

function gv(obj, ...keys) {
  let cur = obj;
  for (const k of keys) { if (cur == null) return 0; cur = cur[k]; }
  return (cur != null && cur !== '') ? cur : 0;
}
function gs(obj, ...keys) {
  let cur = obj;
  for (const k of keys) { if (cur == null) return '—'; cur = cur[k]; }
  return cur != null ? String(cur) : '—';
}

if (typeof Chart === 'undefined') {
  document.getElementById('tbl').parentElement.insertAdjacentHTML('beforebegin',
    '<div style="background:rgba(239,83,80,.12);border:1px solid rgba(239,83,80,.3);border-radius:8px;padding:12px;color:#ef9a9a;margin-bottom:20px">⚠️ Chart.js não carregou. Tabela ainda funciona.</div>');
} else {

Chart.defaults.color = '#7a88a8';
Chart.defaults.font.family = "system-ui, -apple-system, sans-serif";
Chart.defaults.font.size = 12;
const GRID = 'rgba(255,255,255,0.05)';

function hBar(id, labels, datasets, opts={}) {
  new Chart(document.getElementById(id), {
    type: 'bar',
    data: { labels, datasets },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${typeof ctx.raw==='number' ? ctx.raw.toLocaleString('pt-BR',{maximumFractionDigits:4}) : ctx.raw}${opts.suf||''}` } }
      },
      scales: {
        x: { grid: { color: GRID }, ticks: { color: '#7a88a8', callback: v => `${v.toLocaleString('pt-BR')}${opts.suf||''}` } },
        y: { grid: { color: GRID }, ticks: { color: '#dde3f0' } }
      }
    }
  });
}

function mkDS(key_path, label_fn) {
  return DS.map((d, i) => ({
    label: NAMES[i],
    data: [key_path.reduce((o,k)=>o?o[k]:0, d) || 0],
    backgroundColor: BGS[i],
    borderColor: COLORS[i],
    borderWidth: 1
  }));
}

function multiBar(id, metric_fn, opts={}) {
  const datasets = DS.map((d, i) => ({
    label: NAMES[i],
    data: [metric_fn(d)],
    backgroundColor: BGS[i],
    borderColor: COLORS[i],
    borderWidth: 1
  }));
  new Chart(document.getElementById(id), {
    type: 'bar',
    data: { labels: [''], datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top', labels: { color: '#dde3f0', padding: 12, boxWidth: 10 } },
        tooltip: { callbacks: { label: ctx => ` ${NAMES[ctx.datasetIndex]}: ${typeof ctx.raw==='number'?ctx.raw.toLocaleString('pt-BR',{maximumFractionDigits:4}):ctx.raw}${opts.suf||''}` } }
      },
      scales: {
        x: { grid: { color: GRID } },
        y: { grid: { color: GRID }, ticks: { color: '#7a88a8', callback: v => `${v.toLocaleString('pt-BR')}${opts.suf||''}` } }
      }
    }
  });
}

multiBar('ch-cost',    d => gv(d,'tokens','cost_usd'));
multiBar('ch-out-tok', d => gv(d,'tokens','output_tokens_total'));
multiBar('ch-api',     d => gv(d,'tokens','api_calls_count'));
multiBar('ch-dur',     d => gv(d,'speed','session_duration_min'));
multiBar('ch-turns',   d => gv(d,'iterations','total_turns'));
multiBar('ch-loc',     d => gv(d,'code_quality','lines_of_code'));
multiBar('ch-cov',     d => gv(d,'code_quality','test_coverage_line_pct'), { suf: '%' });
multiBar('ch-files',   d => gv(d,'arch_metrics','file_count'));
multiBar('ch-ifaces',  d => gv(d,'arch_metrics','interface_count'));
multiBar('ch-conf',    d => gv(d,'arch_metrics','arch_conformance'));

// Erros stacked
new Chart(document.getElementById('ch-errors'), {
  type: 'bar',
  data: {
    labels: NAMES,
    datasets: [
      { label: 'Compilação', data: DS.map(d=>gv(d,'errors','compile_errors')), backgroundColor: 'rgba(239,83,80,.8)' },
      { label: 'Runtime',    data: DS.map(d=>gv(d,'errors','runtime_errors')),  backgroundColor: 'rgba(255,167,38,.8)' },
      { label: 'Testes',     data: DS.map(d=>gv(d,'errors','test_failures')),   backgroundColor: 'rgba(66,165,245,.8)' },
    ]
  },
  options: {
    responsive: true,
    plugins: { legend: { position: 'top', labels: { color: '#dde3f0', padding: 12, boxWidth: 10 } } },
    scales: {
      x: { stacked: true, grid: { color: GRID } },
      y: { stacked: true, grid: { color: GRID }, ticks: { stepSize: 1, color: '#7a88a8' } }
    }
  }
});

} // end Chart check

// ── Tabela comparativa
function fmt(v, t) {
  if (t === 's') return v != null ? String(v) : '—';
  if (typeof v !== 'number') return '—';
  if (t === 'u') return `$${v.toFixed(4)}`;
  if (t === 'p') return `${v.toFixed(1)}%`;
  return v.toLocaleString('pt-BR', { maximumFractionDigits: 2 });
}

const METRICS = [
  // [categoria, label, fn(d), tipo, lowerIsBetter]
  ['Tokens', 'Output Tokens',          d=>gv(d,'tokens','output_tokens_total'),   'n', true],
  ['Tokens', 'Cache Read',             d=>gv(d,'tokens','cache_read_tokens'),      'n', true],
  ['Tokens', 'Chamadas API',           d=>gv(d,'tokens','api_calls_count'),        'n', true],
  ['Custo',  'Custo Total',            d=>gv(d,'tokens','cost_usd'),               'u', true],
  ['Custo',  'Custo/Endpoint',         d=>gv(d,'tokens','cost_per_endpoint_usd'),  'u', true],
  ['Velocidade', 'Duração (min)',      d=>gv(d,'speed','session_duration_min'),    'n', true],
  ['Velocidade', 'Tempo/Endpoint',     d=>gv(d,'speed','time_per_endpoint_min'),   'n', true],
  ['Velocidade', 'Throughput (ep/h)',  d=>gv(d,'speed','throughput_endpoints_per_hour'), 'n', false],
  ['Iterações', 'Total de Turns',      d=>gv(d,'iterations','total_turns'),        'n', true],
  ['Iterações', 'Tool Calls',          d=>gv(d,'iterations','tool_calls_total'),   'n', true],
  ['Erros', 'Compilação',              d=>gv(d,'errors','compile_errors'),         'n', true],
  ['Erros', 'Runtime',                 d=>gv(d,'errors','runtime_errors'),         'n', true],
  ['Erros', 'Falhas de Teste',         d=>gv(d,'errors','test_failures'),          'n', true],
  ['Erros', 'Total',                   d=>gv(d,'errors','total_errors'),           'n', true],
  ['Qualidade', 'LOC Produção',        d=>gv(d,'code_quality','lines_of_code'),    'n', false],
  ['Qualidade', 'LOC Testes',          d=>gv(d,'code_quality','test_lines_of_code'), 'n', false],
  ['Qualidade', 'Cobertura Linha (%)', d=>gv(d,'code_quality','test_coverage_line_pct'), 'p', false],
  ['Qualidade', 'Cobertura Branch (%)',d=>gv(d,'code_quality','test_coverage_branch_pct'), 'p', false],
  ['E2E', 'Cenários Passou',           d=>gv(d,'e2e','passed'),                    'n', false],
  ['Arquitetura', 'Arquivos .java',    d=>gv(d,'arch_metrics','file_count'),       'n', false],
  ['Arquitetura', 'Interfaces',        d=>gv(d,'arch_metrics','interface_count'),  'n', false],
  ['Arquitetura', 'Pacotes',           d=>gv(d,'arch_metrics','package_count'),    'n', false],
  ['Arquitetura', 'Conformidade (0-10)',d=>gv(d,'arch_metrics','arch_conformance'), 'n', false],
  ['Arquitetura', 'Violações',         d=>gv(d,'arch_metrics','dependency_violations'), 'n', true],
];

let html = '<thead><tr><th>Categoria</th><th>Métrica</th>';
NAMES.forEach((n, i) => { html += `<th style="color:${COLORS[i]}">${n}</th>`; });
html += '<th>Melhor</th></tr></thead><tbody>';

let lastCat = null;
METRICS.forEach(([cat, label, fn, t, lower]) => {
  const vals = DS.map(fn);
  const nums = vals.filter(v => typeof v === 'number');
  const best = nums.length ? (lower ? Math.min(...nums) : Math.max(...nums)) : null;
  const newCat = cat !== lastCat;
  if (newCat) lastCat = cat;

  html += `<tr${newCat ? ' style="border-top:2px solid var(--border)"' : ''}>`;
  html += `<td class="${newCat ? 't-cat' : 't-dim'}" style="${!newCat ? 'color:transparent' : ''}">${cat}</td>`;
  html += `<td class="t-dim">${label}</td>`;
  vals.forEach((v, i) => {
    const isBest = best != null && typeof v === 'number' && v === best;
    html += `<td class="${isBest ? 't-best' : ''}" style="${isBest ? `color:${COLORS[i]}` : ''}">${fmt(v, t)}</td>`;
  });
  // Melhor coluna
  const bestIdx = best != null ? vals.indexOf(best) : -1;
  html += `<td style="color:${bestIdx>=0 ? COLORS[bestIdx] : 'var(--dim)'}; font-weight:600; white-space:nowrap">${bestIdx >= 0 ? NAMES[bestIdx] : '—'}</td>`;
  html += '</tr>';
});
html += '</tbody>';
document.getElementById('tbl').innerHTML = html;
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Gera relatório HTML do benchmark")
    parser.add_argument("--mode",   default="lang", choices=["lang", "arch"],
                        help="Modo: 'lang' (Java vs Kotlin) ou 'arch' (arquiteturas)")
    parser.add_argument("--java",   help="[modo lang] Caminho para JSON Java")
    parser.add_argument("--kotlin", help="[modo lang] Caminho para JSON Kotlin")
    parser.add_argument("--files",  nargs="+", help="[modo arch] Arquivos JSON das arquiteturas")
    args = parser.parse_args()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if args.mode == "arch":
        files = args.files or find_arch_reports()
        if not files:
            print("[report] ERRO: nenhum arquivo arch-*.json encontrado.")
            print(f"[report] Procurado em: {REPORTS_DIR}")
            return
        datasets = [load(f) for f in files]
        print(f"[report] Modo arch — {len(datasets)} arquitetura(s):")
        for f in files:
            print(f"  {f}")
        html = generate_arch(datasets, files)
        out = os.path.join(REPORTS_DIR, f"arch_report_{ts}.html")
    else:
        jp = args.java   or find_latest("java")
        kp = args.kotlin or find_latest("kotlin")
        if not jp:
            print("[report] ERRO: nenhum relatório java_*.json encontrado.")
            return
        if not kp:
            print("[report] ERRO: nenhum relatório kotlin_*.json encontrado.")
            return
        print(f"[report] Java:   {jp}")
        print(f"[report] Kotlin: {kp}")
        html = generate(load(jp), load(kp), jp, kp)
        out = os.path.join(REPORTS_DIR, f"benchmark_report_{ts}.html")

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[report] Relatório salvo: {out}")
    print(f"[report] Abra no browser: {out}")


if __name__ == "__main__":
    main()
