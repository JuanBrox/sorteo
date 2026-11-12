import json

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="¿Dónde comemos?", page_icon="🍽️", layout="centered")

OPCIONES_EJEMPLO = "Pizzería\nSushi\nHamburguesería\nMexicano\nMenú del día\nBocadillos\nIndio"
MAX_OPCIONES = 24

st.title("🍽️ ¿Dónde comemos?")
st.caption("Escribe los sitios, gira la ruleta y vais donde caiga la flecha.")

texto = st.text_area(
    "Sitios (uno por línea)",
    value=OPCIONES_EJEMPLO,
    height=190,
    key="texto_opciones",
)

# Limpia líneas vacías y duplicados, manteniendo el orden
opciones = list(dict.fromkeys(l.strip() for l in texto.splitlines() if l.strip()))

if len(opciones) > MAX_OPCIONES:
    st.warning(f"Son demasiados sitios para leer bien la ruleta. Uso los primeros {MAX_OPCIONES}.")
    opciones = opciones[:MAX_OPCIONES]

if len(opciones) < 2:
    st.info("Añade al menos dos sitios para poder girar la ruleta.")
    st.stop()

HTML = """
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&display=swap" rel="stylesheet">
<style>
  :root { --tomate:#E4472B; --tinta:#1F3A44; --crema:#FFF8E7; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Bricolage Grotesque', system-ui, sans-serif; background:transparent; }
  #box { position:relative; width:100%; max-width:480px; margin:8px auto 0; }
  #wheel { display:block; margin:0 auto; }
  #pointer {
    position:absolute; top:-4px; left:50%; transform:translateX(-50%);
    width:0; height:0; z-index:2;
    border-left:16px solid transparent; border-right:16px solid transparent;
    border-top:34px solid var(--tinta);
    filter: drop-shadow(0 2px 0 rgba(255,255,255,.9));
  }
  #panel { text-align:center; margin:18px auto 0; max-width:480px; }
  button {
    font-family:inherit; font-weight:800; font-size:20px; cursor:pointer;
    border:0; border-radius:999px; padding:14px 34px; color:#fff; background:var(--tomate);
    box-shadow:0 4px 0 #A8321B; transition:transform .08s, box-shadow .08s;
  }
  button:active { transform:translateY(3px); box-shadow:0 1px 0 #A8321B; }
  button:focus-visible { outline:3px solid var(--tinta); outline-offset:3px; }
  button:disabled { opacity:.55; cursor:default; }
  button.sec { background:var(--tinta); box-shadow:0 4px 0 #0F2229; font-size:16px; padding:10px 22px; margin-left:8px; }
  #result {
    display:none; margin:0 auto 16px; padding:16px 20px; border-radius:18px;
    background:var(--tinta); color:var(--crema);
  }
  #result small { display:block; font-weight:500; font-size:14px; opacity:.8; }
  #result strong { display:block; font-weight:800; font-size:30px; line-height:1.15; word-break:break-word; }
</style>

<div id="box">
  <div id="pointer"></div>
  <canvas id="wheel" aria-label="Ruleta de sitios para comer"></canvas>
</div>
<div id="panel">
  <div id="result" role="status" aria-live="polite"><small>Hoy se come en</small><strong id="name"></strong></div>
  <button id="spin">¡Girar!</button>
  <button id="remove" class="sec" style="display:none">Quitar y girar otra vez</button>
</div>

<script>
const ALL = __OPCIONES__;
let items = ALL.slice();
const COLORS = ['#E4472B','#F2A900','#2A9D8F','#1F3A44','#E86A92','#6C8E23','#7B5EA7','#F07B3F'];
const TAU = Math.PI * 2;
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const resultEl = document.getElementById('result');
const nameEl = document.getElementById('name');
const spinBtn = document.getElementById('spin');
const removeBtn = document.getElementById('remove');

let angle = Math.random() * TAU;
let spinning = false;
let winner = -1;
let dpr = window.devicePixelRatio || 1;

function resize() {
  const w = Math.min(document.getElementById('box').clientWidth, 480);
  canvas.style.width = w + 'px';
  canvas.style.height = w + 'px';
  canvas.width = Math.round(w * dpr);
  canvas.height = Math.round(w * dpr);
  draw();
}

function color(i) {
  // evita que el último y el primer sector tengan el mismo color
  if (items.length % COLORS.length === 1 && i === items.length - 1) return COLORS[4];
  return COLORS[i % COLORS.length];
}

function fitText(text, maxWidth, size) {
  ctx.font = '700 ' + size + 'px "Bricolage Grotesque", system-ui, sans-serif';
  while (ctx.measureText(text).width > maxWidth && size > 11 * dpr) {
    size -= 1;
    ctx.font = '700 ' + size + 'px "Bricolage Grotesque", system-ui, sans-serif';
  }
  if (ctx.measureText(text).width > maxWidth) {
    while (text.length > 1 && ctx.measureText(text + '…').width > maxWidth) text = text.slice(0, -1);
    text += '…';
  }
  return text;
}

function draw() {
  const W = canvas.width, c = W / 2, r = c - 8 * dpr;
  const n = items.length, a = TAU / n;
  ctx.clearRect(0, 0, W, W);

  for (let i = 0; i < n; i++) {
    const s = angle + i * a;
    ctx.globalAlpha = (winner >= 0 && i !== winner) ? 0.4 : 1;
    ctx.beginPath();
    ctx.moveTo(c, c);
    ctx.arc(c, c, r, s, s + a);
    ctx.closePath();
    ctx.fillStyle = color(i);
    ctx.fill();
    ctx.lineWidth = 2 * dpr;
    ctx.strokeStyle = '#FFF8E7';
    ctx.stroke();

    ctx.save();
    ctx.translate(c, c);
    ctx.rotate(s + a / 2);
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#fff';
    const base = Math.min(26 * dpr, r * 0.5 * Math.sin(Math.min(a / 2, 1.2)) * 1.1);
    const label = fitText(items[i], r * 0.66, Math.max(base, 12 * dpr));
    ctx.fillText(label, r - 18 * dpr, 0);
    ctx.restore();
  }
  ctx.globalAlpha = 1;

  // aro exterior y centro
  ctx.beginPath();
  ctx.arc(c, c, r, 0, TAU);
  ctx.lineWidth = 6 * dpr;
  ctx.strokeStyle = '#1F3A44';
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(c, c, 22 * dpr, 0, TAU);
  ctx.fillStyle = '#FFF8E7';
  ctx.fill();
  ctx.lineWidth = 5 * dpr;
  ctx.strokeStyle = '#1F3A44';
  ctx.stroke();
}

function spin() {
  if (spinning || items.length < 2) return;
  spinning = true;
  winner = -1;
  resultEl.style.display = 'none';
  removeBtn.style.display = 'none';
  spinBtn.disabled = true;

  const n = items.length, a = TAU / n;
  const win = Math.floor(Math.random() * n);
  const jitter = (Math.random() - 0.5) * a * 0.7;
  // la flecha apunta arriba (3π/2): el centro del sector ganador debe quedar ahí
  const target = 1.5 * Math.PI - (win * a + a / 2 + jitter);
  const start = angle;
  const delta = (((target - start) % TAU) + TAU) % TAU + TAU * (5 + Math.floor(Math.random() * 3));
  const dur = reduce ? 600 : 5000 + Math.random() * 1500;
  const t0 = performance.now();

  function frame(now) {
    const t = Math.min((now - t0) / dur, 1);
    const e = 1 - Math.pow(1 - t, 4);
    angle = start + delta * e;
    draw();
    if (t < 1) { requestAnimationFrame(frame); return; }
    angle = ((angle % TAU) + TAU) % TAU;
    finish(win);
  }
  requestAnimationFrame(frame);
}

function finish(win) {
  spinning = false;
  winner = win;
  draw();
  nameEl.textContent = items[win];
  resultEl.style.display = 'block';
  spinBtn.disabled = false;
  spinBtn.textContent = 'Girar de nuevo';
  if (items.length > 2) removeBtn.style.display = 'inline-block';
}

function removeWinner() {
  if (spinning || winner < 0 || items.length <= 2) return;
  items.splice(winner, 1);
  winner = -1;
  resultEl.style.display = 'none';
  removeBtn.style.display = 'none';
  draw();
  spin();
}

spinBtn.addEventListener('click', spin);
removeBtn.addEventListener('click', removeWinner);
window.addEventListener('resize', resize);
document.fonts && document.fonts.ready.then(draw);
resize();
</script>
"""

components.html(HTML.replace("__OPCIONES__", json.dumps(opciones, ensure_ascii=False)), height=760)

st.caption("Si hay empate de opiniones, manda la ruleta. 🎡")
