function esc(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
}

function formatCount(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

async function unpackSvg(encoded) {
  const binary = atob(encoded);
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return new Response(stream).text();
}

export default {
  async render({ model, el }) {
    const root = document.createElement("section");
    root.className = "bymi-scale";
    root.dataset.testid = "scale-journey";
    el.replaceChildren(root);
    let timer = null;
    let level = 0;

    const rawPayload = model.get("payload");
    const resolvedPayload = {...rawPayload, seed_svg: await unpackSvg(rawPayload.seed_svg_gzip_base64)};
    const payload = () => resolvedPayload;
    const state = () => model.get("state") || {};
    const sync = (patch) => {
      const next = {...state(), ...patch, event_sequence: (state().event_sequence || 0) + 1};
      model.set("state", next);
      model.save_changes();
    };
    const stop = () => {
      if (timer !== null) window.clearInterval(timer);
      timer = null;
    };
    const showLevel = (nextLevel) => {
      level = Math.max(0, Math.min(nextLevel, payload().scale_landmarks.length));
      draw();
      if (level === payload().scale_landmarks.length) {
        stop();
        sync({complete: true});
      }
    };
    const begin = (reduced = false) => {
      stop();
      const motionReduced = reduced || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      sync({started: true, complete: motionReduced, reduced_motion: motionReduced});
      if (motionReduced) {
        showLevel(payload().scale_landmarks.length);
        return;
      }
      showLevel(0);
      timer = window.setInterval(() => showLevel(level + 1), 1800);
    };

    function scaleMarkup() {
      const landmarks = payload().scale_landmarks;
      const item = landmarks[Math.min(level, landmarks.length - 1)];
      const cellCount = level === 0 ? 1 : 100;
      const cells = Array.from({length: cellCount}, (_, index) => {
        const visible = index < item.marks;
        return `<span class="bymi-scale__cell" data-empty="${!visible}"${level === 0 ? ' style="width:70px;height:70px;border-radius:12px"' : ""}></span>`;
      }).join("");
      const perMark = item.count / item.marks;
      const zoom = [1, 1.38, 1.12, .92, .75][Math.min(level, 4)];
      const gridStyle = level === 0 ? "grid-template-columns:70px;gap:0" : `transform:scale(${zoom})`;
      const source = level === 4
        ? "GDB-17 is a bounded enumeration of molecules with up to 17 atoms of C, N, O, S and halogens."
        : "Each pull-back replaces individual possibilities with deterministic counted groups.";
      return `
        <div class="bymi-scale__count">
          <span class="bymi-scale__number">${formatCount(item.count)}</span>
          <span class="bymi-scale__unit">${esc(item.label)}</span>
        </div>
        <div class="bymi-scale__field" aria-label="${formatCount(item.count)} schematic possibilities">
          <div class="bymi-scale__grid" style="${gridStyle}">${cells}</div>
        </div>
        <div class="bymi-scale__caption">
          <p><strong>One square now represents ${formatCount(perMark)} ${perMark === 1 ? "possibility" : "possibilities"}.</strong> ${source} Schematic logarithmic compression; the marks are aggregates, not rendered molecules.</p>
          <div class="bymi-scale__steps" aria-label="Scale level ${Math.min(level + 1, 5)} of 5">${landmarks.map((_, i) => `<span class="bymi-scale__step" data-active="${i <= level}"></span>`).join("")}</div>
        </div>`;
    }

    function evidenceMarkup() {
      const data = payload();
      const seed = data.seed;
      const accounting = data.assay_accounting;
      const record = data.seed_record;
      const slots = record.endpoints.map((endpoint) => `<span class="bymi-scale__slot" data-filled="${endpoint.status === "measured"}" aria-label="${esc(endpoint.label)}: ${esc(endpoint.status)}">${esc(endpoint.short_label)}</span>`).join("");
      const coverage = accounting.endpoint_columns.map((endpoint, index) => {
        const height = 100 * accounting.per_endpoint[endpoint] / accounting.records;
        return `<div><div class="bymi-scale__coverage-col" aria-label="${esc(endpoint)}: ${accounting.per_endpoint[endpoint]} numeric records"><span class="bymi-scale__coverage-fill" style="height:${height.toFixed(1)}%"></span></div><span class="bymi-scale__unit">${esc(record.endpoints[index].short_label)}</span></div>`;
      }).join("");
      return `<div class="bymi-scale__evidence">
        <div>
          <p class="bymi-scale__eyebrow">Context changes here</p>
          <div class="bymi-scale__molecule">${data.seed_svg}</div>
        </div>
        <div>
          <h3>One real ExpansionRx training record</h3>
          <p><strong>${esc(seed.seed_id)}</strong> anchors a separate measured collection. It is not presented as a member of GDB-17.</p>
          <div class="bymi-scale__strip">${slots}</div>
          <div class="bymi-scale__coverage">${coverage}</div>
          <div class="bymi-scale__summary">
            <span><strong>${formatCount(accounting.records)}</strong>released records</span>
            <span><strong>${formatCount(accounting.recorded_values)}</strong>numeric endpoint values</span>
            <span><strong>${formatCount(accounting.missing_or_non_numeric)}</strong>cells without numeric ML-ready values</span>
          </div>
        </div>
      </div>
      <div class="bymi-scale__caption"><p>Recorded values are accumulated evidence. Empty slots can mean unavailable evidence or an excluded bounded observation—not failure and never zero. Design · make · purify · measure · interpret is schematic context, not this molecule’s documented history.</p></div>`;
    }

    function draw() {
      const complete = state().complete || level >= payload().scale_landmarks.length;
      root.innerHTML = `
        <div class="bymi-scale__header">
          <div><p class="bymi-scale__eyebrow">Before you make it · action 1 of 9</p><h2>How do we choose a few molecules when even our maps disagree?</h2></div>
          <div class="bymi-scale__controls">
            <button type="button" data-action="pull" data-primary="true">Pull back</button>
            <button type="button" data-action="skip">Skip motion</button>
          </div>
        </div>
        <div class="bymi-scale__stage" aria-live="polite">${complete ? evidenceMarkup() : scaleMarkup()}</div>`;
      root.querySelector('[data-action="pull"]').addEventListener("click", () => begin(false));
      root.querySelector('[data-action="skip"]').addEventListener("click", () => begin(true));
    }

    draw();
    const onState = () => draw();
    model.on("change:state", onState);
    return () => {
      stop();
      model.off("change:state", onState);
    };
  },
};
