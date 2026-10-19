/* ===== Jarvis plasma orb: 3D network sphere, light beams, arcs, particles ===== */
const CONFIG = {
  // "" = same address the page was opened from (works on PC and phone). Only a file opened by double-click needs a fixed address.
  API_BASE: location.protocol.startsWith("http") ? "" : "http://localhost:8000",
  DEMO_MODE: false                    // true = preview animation without the server
};

const $ = (id) => document.getElementById(id);
const cv = $("orb"), ctx = cv.getContext("2d");
const TAU = Math.PI * 2;

const LABEL  = { idle: "Say \u201cJarvis\u201d to wake me", listening: "Listening\u2026", thinking: "Thinking\u2026", speaking: "" };
const TARGET = { idle: .1, listening: .45, thinking: .25, speaking: 1 };
const SPIN   = { idle: .5, listening: .8, thinking: 2.2, speaking: 1.1 };
const COLOR  = { idle: [235, 128, 30], listening: [255, 168, 55], thinking: [255, 105, 25], speaking: [255, 150, 40] };

let W, H, S, state = "idle";
let amp = .1, spinV = .5, ry = 0, rot = 0, t = 0, lastRipple = 0, ripples = [], col = [235, 128, 30];

function fit() {
  const d = Math.min(window.devicePixelRatio || 1, 2);   // phones: keep it smooth
  W = cv.width = innerWidth * d; H = cv.height = innerHeight * d;
  cv.style.width = innerWidth + "px"; cv.style.height = innerHeight + "px";
  S = Math.min(W, H) * .4;
}
addEventListener("resize", fit); fit();

function setState(s) { state = s; $("status").textContent = LABEL[s]; }
function showCaption(text) { $("caption").textContent = text; $("caption").classList.add("show"); }
function hideCaption() { $("caption").classList.remove("show"); }

const rgba = (a, c = col) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${Math.max(0, Math.min(1, a))})`;

/* ---------- build the 3D shapes once ---------- */
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; }; }
const R = rng(7);

const NV = 150, V = [], E = [], seen = new Set();             // network sphere
for (let i = 0; i < NV; i++) {
  const y = 1 - 2 * (i + .5) / NV, r = Math.sqrt(1 - y * y), a = i * 2.39996323;
  V.push([Math.cos(a) * r, y, Math.sin(a) * r]);
}
for (let i = 0; i < NV; i++) {
  V.map((v, j) => [j, (v[0] - V[i][0]) ** 2 + (v[1] - V[i][1]) ** 2 + (v[2] - V[i][2]) ** 2])
   .filter(x => x[0] !== i).sort((a, b) => a[1] - b[1]).slice(0, 5)
   .forEach(([j]) => { const k = i < j ? i * NV + j : j * NV + i; if (!seen.has(k)) { seen.add(k); E.push([i, j]); } });
}
const PX = new Float32Array(NV), PY = new Float32Array(NV), PZ = new Float32Array(NV);

const BEAMS = Array.from({ length: 24 }, () => {                // light beams from the core
  const z = 2 * R() - 1, a = R() * TAU, r = Math.sqrt(1 - z * z);
  return { d: [Math.cos(a) * r, z, Math.sin(a) * r], len: .9 + R() * 1.1, w: .7 + R() * 1.1, ph: R() * TAU };
});

const M = innerWidth < 700 ? 900 : 1700, PT = Array.from({ length: M }, () => {          // particle cloud
  const th = R() * TAU;
  return { th, ph: Math.acos(2 * R() - 1), rho: .58 + R() ** 2 * .6 + (Math.cos(th) < 0 ? R() * .15 : 0),
           sp: (.05 + R() * .25) * (R() < .5 ? -1 : 1), sz: .0025 + R() * .004 };
});

const ARCS = [{ r: .95, a0: 2.3, span: 1.15, spd: -.1, w: .028 }, { r: .88, a0: 5.4, span: .85, spd: .16, w: .024 }];

/* 3D rotation + simple perspective into shared P */
const P = [0, 0, 0];
let ca = 1, sa = 0, cb = 1, sb = 0;
function proj(x, y, z) {
  const x1 = x * ca + z * sa, z1 = -x * sa + z * ca;
  const y2 = y * cb - z1 * sb, z2 = y * sb + z1 * cb, p = 1 / (1 - z2 * .22);
  P[0] = x1 * p; P[1] = y2 * p; P[2] = z2;
}

/* ---------- frame ---------- */
function frame(now) {
  t += .016;
  amp += (TARGET[state] - amp) * .07;
  spinV += (SPIN[state] - spinV) * .05;
  ry += spinV * .016 * .6; rot += spinV * .016;
  const c = COLOR[state];
  for (let i = 0; i < 3; i++) col[i] += (c[i] - col[i]) * .06;

  const env = state === "speaking" ? Math.min(1, Math.abs(Math.sin(t * 9) * .55 + Math.sin(t * 5.3 + 1) * .45) + .15) : 1;
  const lift = .7 + .3 * Math.min(1, amp * 1.3);
  const Rs = .5 * S * (1 + .02 * Math.sin(t * 1.6) + .06 * amp * env);
  const tilt = .45 + .1 * Math.sin(t * .3);
  ca = Math.cos(ry); sa = Math.sin(ry); cb = Math.cos(tilt); sb = Math.sin(tilt);
  const lw = Math.max(1, S / 330);

  ctx.clearRect(0, 0, W, H);
  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.globalCompositeOperation = "lighter";
  ctx.lineCap = "round";

  // ambient glow
  const g = ctx.createRadialGradient(0, 0, 0, 0, 0, S);
  g.addColorStop(0, rgba(.28 * lift)); g.addColorStop(.55, rgba(.07 * lift)); g.addColorStop(1, rgba(0));
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, S, 0, TAU); ctx.fill();

  // thin rings
  ctx.lineWidth = lw;
  ctx.strokeStyle = rgba(.45 * lift); ctx.beginPath(); ctx.arc(0, 0, .98 * S, 0, TAU); ctx.stroke();
  ctx.strokeStyle = rgba(.22 * lift); ctx.beginPath(); ctx.arc(0, 0, .8 * S, 0, TAU); ctx.stroke();
  ctx.strokeStyle = rgba(.3 * lift); ctx.beginPath(); ctx.ellipse(0, 0, .96 * S, .42 * S, rot * .25, 0, TAU); ctx.stroke();

  // thick glowing arcs
  ctx.lineCap = "butt";
  for (const a of ARCS) {
    const s = a.a0 + rot * a.spd * 3;
    ctx.lineWidth = a.w * S * 1.9; ctx.strokeStyle = rgba(.2 * lift); ctx.beginPath(); ctx.arc(0, 0, a.r * S, s, s + a.span); ctx.stroke();
    ctx.lineWidth = a.w * S;       ctx.strokeStyle = rgba(.95 * lift); ctx.beginPath(); ctx.arc(0, 0, a.r * S, s, s + a.span); ctx.stroke();
  }
  ctx.lineCap = "round";

  // speaking ripples
  if (state === "speaking" && now - lastRipple > 520) { ripples.push({ r: .5, a: .5 }); lastRipple = now; }
  ripples = ripples.filter(p => p.a > 0);
  ctx.lineWidth = lw * 1.5;
  for (const p of ripples) { ctx.strokeStyle = rgba(p.a * lift); ctx.beginPath(); ctx.arc(0, 0, p.r * S, 0, TAU); ctx.stroke(); p.r += .006; p.a -= .0065; }

  // network sphere (vertices wobble with the voice)
  for (let i = 0; i < NV; i++) {
    const f = 1 + amp * env * .1 * Math.sin(i * 1.9 + t * 8);
    proj(V[i][0] * f, V[i][1] * f, V[i][2] * f);
    PX[i] = P[0] * Rs; PY[i] = P[1] * Rs; PZ[i] = P[2];
  }
  const eb = [new Path2D(), new Path2D(), new Path2D()];
  for (const [i, j] of E) {
    const z = (PZ[i] + PZ[j]) / 2, p = eb[z < -.3 ? 0 : z < .3 ? 1 : 2];
    p.moveTo(PX[i], PY[i]); p.lineTo(PX[j], PY[j]);
  }
  ctx.lineWidth = lw * 1.25;
  [.14, .36, .78].forEach((a, k) => { ctx.strokeStyle = rgba(a * lift); ctx.stroke(eb[k]); });
  const vf = new Path2D(), vb = new Path2D();
  for (let i = 0; i < NV; i++) {
    const front = PZ[i] > 0, p = front ? vf : vb, rr = S * (front ? .0045 : .003);
    p.moveTo(PX[i] + rr, PY[i]); p.arc(PX[i], PY[i], rr, 0, TAU);
  }
  ctx.fillStyle = rgba(.35 * lift); ctx.fill(vb);
  ctx.fillStyle = rgba(.95 * lift, [255, 170, 70]); ctx.fill(vf);

  // light beams from the core
  for (const b of BEAMS) {
    proj(b.d[0], b.d[1], b.d[2]);
    const L = Rs * b.len * (1 + .25 * amp * env * Math.sin(t * 6 + b.ph));
    const ex = P[0] * L, ey = P[1] * L, a = (.35 + .65 * (P[2] + 1) / 2) * lift;
    const gr = ctx.createLinearGradient(0, 0, ex, ey);
    gr.addColorStop(0, rgba(a, [255, 245, 215])); gr.addColorStop(.5, rgba(a * .7)); gr.addColorStop(1, rgba(0));
    ctx.strokeStyle = gr;
    ctx.lineWidth = S * .009 * b.w * (.7 + .6 * amp); ctx.globalAlpha = .35;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(ex, ey); ctx.stroke();
    ctx.lineWidth = S * .003 * b.w; ctx.globalAlpha = 1;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(ex, ey); ctx.stroke();
  }

  // particle cloud
  const pf = new Path2D(), pm = new Path2D(), pb = new Path2D();
  for (let i = 0; i < M; i++) {
    const q = PT[i];
    q.th += q.sp * .016 * (.3 + spinV);
    const rho = q.rho * (1 + .07 * amp * env * Math.sin(i * .37 + t * 10)), sp = Math.sin(q.ph);
    proj(rho * sp * Math.cos(q.th), rho * Math.cos(q.ph), rho * sp * Math.sin(q.th));
    const x = P[0] * S, y = P[1] * S, z = P[2], rr = q.sz * S * (1 + .4 * z);
    const p = z > .25 ? pf : z > -.25 ? pm : pb;
    p.moveTo(x + rr, y); p.arc(x, y, rr, 0, TAU);
  }
  ctx.fillStyle = rgba(.3 * lift); ctx.fill(pb);
  ctx.fillStyle = rgba(.55 * lift); ctx.fill(pm);
  ctx.fillStyle = rgba(.95 * lift, [255, 165, 70]); ctx.fill(pf);

  // white-hot core + flare
  const cr = Rs * (.55 + .15 * amp * env);
  const cg = ctx.createRadialGradient(0, 0, 0, 0, 0, cr);
  cg.addColorStop(0, "rgba(255,250,235,1)"); cg.addColorStop(.1, "rgba(255,236,190,.95)");
  cg.addColorStop(.3, rgba(.55 * lift)); cg.addColorStop(1, rgba(0));
  ctx.fillStyle = cg; ctx.beginPath(); ctx.arc(0, 0, cr, 0, TAU); ctx.fill();
  const fl = Rs * .4 * (1 + amp * env), fg = ctx.createLinearGradient(-fl, 0, fl, 0);
  fg.addColorStop(0, rgba(0)); fg.addColorStop(.5, "rgba(255,240,205,.8)"); fg.addColorStop(1, rgba(0));
  ctx.strokeStyle = fg; ctx.lineWidth = lw * 1.5;
  ctx.beginPath(); ctx.moveTo(-fl, 0); ctx.lineTo(fl, 0); ctx.stroke();

  ctx.restore();
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

/* ---------- follow the Jarvis server ---------- */
let offline = false;
async function poll() {
  try {
    const d = await (await fetch(CONFIG.API_BASE + "/api/state", { cache: "no-store" })).json();
    if (offline) { offline = false; setState(state); }
    if (d.state !== state) setState(d.state);
    if (d.state === "speaking" && d.text) showCaption(d.text);
    else if (d.state === "thinking" && d.heard) showCaption("\u201c" + d.heard + "\u201d");
    else hideCaption();
  } catch {
    if (!offline) { offline = true; setState("idle"); $("status").textContent = "Can't reach the Jarvis server. Start it, then refresh."; }
  }
}

if (CONFIG.DEMO_MODE) {            // preview the animation without a server
  const seq = ["idle", "listening", "thinking", "speaking"]; let i = 0;
  setInterval(() => {
    i = (i + 1) % 4; setState(seq[i]);
    seq[i] === "speaking" ? showCaption("This is how I look while speaking, Boss.") : hideCaption();
  }, 3500);
} else {
  poll(); setInterval(poll, 300);
}
setState("idle");