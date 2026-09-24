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
        ? "GDB-17 is a bounded enumeration—not every possible drug-like molecule. It covers molecules with at most 17 non-hydrogen atoms drawn from a specified set of elements."
        : "At each step, one square stands for a larger counted group. The squares preserve continuity; they are not individual molecular drawings.";
      return `
        <div class="bymi-scale__question"><strong>What are you looking at?</strong> A single possibility is repeatedly grouped into larger collections so the scale remains countable as we pull back.</div>
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
        </div>
        <div class="bymi-scale__landmarks" aria-label="Scale landmarks">${landmarks.map((landmark, index) => `<span data-current="${index === Math.min(level, landmarks.length - 1)}"><strong>${formatCount(landmark.count)}</strong>${esc(landmark.label.replace(/^GDB-17:\s*/i, ""))}</span>`).join("")}</div>`;
    }

    function evidenceMarkup() {
      const data = payload();
      const seed = data.seed;
      const accounting = data.assay_accounting;
      const record = data.seed_record;
      const slots = record.endpoints.map((endpoint) => `<span class="bymi-scale__slot" data-filled="${endpoint.status === "measured"}" aria-label="${esc(endpoint.label)}: ${esc(endpoint.status)}" title="${esc(endpoint.label)}">${esc(endpoint.short_label)}</span>`).join("");
      const coverage = accounting.endpoint_columns.map((endpoint, index) => {
        const height = 100 * accounting.per_endpoint[endpoint] / accounting.records;
        return `<div><div class="bymi-scale__coverage-col" aria-label="${esc(endpoint)}: ${accounting.per_endpoint[endpoint]} numeric records"><span class="bymi-scale__coverage-fill" style="height:${height.toFixed(1)}%"></span></div><span class="bymi-scale__unit">${esc(record.endpoints[index].short_label)}</span></div>`;
      }).join("");
      const finalLandmark = data.scale_landmarks[data.scale_landmarks.length - 1];
      return `<div class="bymi-scale__recap" data-testid="scale-summary">
        <p class="bymi-scale__eyebrow">Why a shortlist is necessary</p>
        <h3>One per second would still take about ${formatCount(Math.round(finalLandmark.hypothetical_years_at_one_per_second))} years.</h3>
        <p>GDB-17 contains about 166 billion enumerated structures within a specific boundary: no more than 17 non-hydrogen atoms from its allowed elements. It is a scale reference, not the ExpansionRx dataset and not a claim about all chemical space. The one-per-second comparison is hypothetical inspection time, not a laboratory throughput estimate.</p>
        <div class="bymi-scale__landmarks" aria-label="Scale landmarks summary">${data.scale_landmarks.map((landmark) => `<span><strong>${formatCount(landmark.count)}</strong>${esc(landmark.label.replace(/^GDB-17:\s*/i, ""))}</span>`).join("")}</div>
      </div>
      <div class="bymi-scale__evidence-intro">
        <p class="bymi-scale__eyebrow">From possibilities to evidence</p>
        <h3>A structure tells us what a molecule is. Measurements tell us how it behaves.</h3>
        <p>This real training molecule has recorded assay results. <strong>LogD</strong> asks how the molecule distributes between water-like and oil-like environments under the assay conditions. <strong>Kinetic solubility</strong> asks how much can dissolve. Other assays ask about metabolism, permeability, efflux, and tissue binding.</p>
      </div>
      <div class="bymi-scale__evidence">
        <div>
          <p class="bymi-scale__eyebrow">One measured molecule</p>
          <div class="bymi-scale__molecule">${data.seed_svg}</div>
        </div>
        <div>
          <h3>${esc(seed.seed_id)} · one ExpansionRx training record</h3>
          <p>Each square below is one possible kind of evidence for this molecule. Filled squares have numeric measurements; empty squares mean the numeric evidence is unavailable here or was recorded only as a bound. Empty never means zero or failure.</p>
          <div class="bymi-scale__strip">${slots}</div>
          <details class="bymi-scale__definitions"><summary>What do the nine assay labels mean?</summary><ul>${record.endpoints.map((endpoint) => `<li><strong>${esc(endpoint.short_label)}</strong> — ${esc(endpoint.label)}</li>`).join("")}</ul></details>
          <p class="bymi-scale__collection-lead"><strong>Now expand from one record to the measured collection.</strong> The bars show how many of the 7,608 released records have a numeric value for each endpoint.</p>
          <div class="bymi-scale__coverage">${coverage}</div>
          <div class="bymi-scale__summary">
            <span><strong>${formatCount(accounting.records)}</strong>released records</span>
            <span><strong>${formatCount(accounting.recorded_values)}</strong>numeric endpoint values</span>
            <span><strong>${formatCount(accounting.missing_or_non_numeric)}</strong>missing or non-numeric slots</span>
          </div>
        </div>
      </div>
      <div class="bymi-scale__caption"><p><strong>Next question:</strong> if experimental evidence is limited, how should a model decide which fifty molecules deserve attention?</p></div>`;
    }

    function draw() {
      const complete = state().complete || level >= payload().scale_landmarks.length;
      root.innerHTML = `
        <div class="bymi-scale__header">
          <div><p class="bymi-scale__eyebrow">Why selection comes first</p><h2>How large is the space behind a shortlist?</h2><p class="bymi-scale__lede">The visual groups possibilities from one to a bounded 166-billion-molecule reference. Watch the grouping, or jump to the complete explanation; both routes end with the same scale landmarks and real measured evidence.</p></div>
          <div class="bymi-scale__controls">
            <button type="button" data-action="pull" data-primary="true">Show the scale</button>
            <button type="button" data-action="skip">Show the summary</button>
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
