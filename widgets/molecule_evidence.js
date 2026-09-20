function esc(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
}

function number(value, digits = 2) {
  return value == null || Number.isNaN(Number(value)) ? "unknown" : Number(value).toFixed(digits);
}

function clamp(value, low, high) {
  return Math.max(low, Math.min(high, value));
}

async function unpackDepictions(packed) {
  if (!packed || packed.encoding !== "gzip+base64") throw new Error("Unsupported depiction encoding");
  const entries = await Promise.all(Object.entries(packed.items).map(async ([id, encoded]) => {
    const binary = atob(encoded);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
    return [id, await new Response(stream).text()];
  }));
  return Object.fromEntries(entries);
}

export default {
  async render({ model, el }) {
    const root = document.createElement("section");
    root.className = "mel";
    root.dataset.testid = "molecule-evidence-lens";
    el.replaceChildren(root);
    const rawData = model.get("payload");
    const data = {...rawData, depictions: await unpackDepictions(rawData.depictions)};
    const records = data.evidence_records;
    const nominations = data.nominations;
    const predictions = new Map();
    for (const row of nominations.predictions) {
      predictions.set(`${row.fit_key}|${row.molecule_id}`, row);
    }
    let animationFrame = null;
    let fitDebounce = null;
    let previousStage = (model.get("state") || {}).evidence_stage;

    const getState = () => model.get("state") || {};
    const setState = (patch) => {
      const current = getState();
      const next = {...current, ...patch, event_sequence: (current.event_sequence || 0) + 1};
      model.set("state", next);
      model.save_changes();
    };
    const stageIndex = (state) => {
      if (state.returned_to_proposal) return 8;
      if (state.caco_revealed) return 7;
      if (state.measurements_revealed) return 6;
      if (state.selection_kind === "ensemble") return 5;
      if (state.fit_explored) return 4;
      if (state.candidate_id) return 3;
      return state.seed_id ? 2 : 1;
    };
    const progress = (state) => Array.from({length: 9}, (_, index) => `<span data-done="${index < stageIndex(state)}"></span>`).join("");
    const depiction = (id) => data.depictions[id] || "";
    const candidateList = (seedId) => data.candidates.filter((candidate) => candidate.seed_id === seedId);
    const candidateRecord = (state) => state.candidate_id ? records[state.candidate_id] : null;

    function choiceCard(id, meta, selected, kind) {
      return `<button type="button" class="mel__choice" data-${kind}-id="${esc(id)}" aria-pressed="${selected}">
        <span class="mel__choice-image">${depiction(id)}</span>
        <span><strong>${esc(id)}</strong><small>${esc(meta)}</small></span>
      </button>`;
    }

    function selectionMarkup(state) {
      const seeds = data.seeds.map((seed) => choiceCard(
        seed.seed_id,
        `Measured LogD ${number(seed.measured_LogD, 1)} · KSOL ${number(seed.measured_KSOL_uM, 0)} µM`,
        state.seed_id === seed.seed_id,
        "seed",
      )).join("");
      const available = candidateList(state.seed_id);
      const first = available.slice(0, 4);
      if (state.candidate_id && !first.some((row) => row.candidate_id === state.candidate_id)) {
        first.push(available.find((row) => row.candidate_id === state.candidate_id));
      }
      const firstIds = new Set(first.filter(Boolean).map((row) => row.candidate_id));
      const cards = first.filter(Boolean).map((candidate) => choiceCard(
        candidate.candidate_id,
        `seed similarity ${number(candidate.similarity_to_seed)} · experiments unknown`,
        state.candidate_id === candidate.candidate_id,
        "candidate",
      )).join("");
      const extras = available.filter((row) => !firstIds.has(row.candidate_id));
      const extraMarkup = extras.length ? `<details class="mel__extra"><summary>Inspect ${extras.length} more recorded proposals</summary><div class="mel__cards">${extras.map((candidate) => choiceCard(candidate.candidate_id, `seed similarity ${number(candidate.similarity_to_seed)}`, state.candidate_id === candidate.candidate_id, "candidate")).join("")}</div></details>` : "";
      return `<div class="mel__selection">
        <div class="mel__panel"><p class="mel__eyebrow">Action 2 · select one measured seed</p><div class="mel__cards">${seeds}</div></div>
        <div class="mel__panel"><p class="mel__eyebrow">Action 3 · retain one cached ChemLlama proposal</p>${cards ? `<div class="mel__cards">${cards}</div>${extraMarkup}` : `<p class="mel__muted">Select a seed to see its compatible recorded proposals.</p>`}</div>
      </div>`;
    }

    function retainedMarkup(state) {
      const candidate = candidateRecord(state);
      if (!candidate) return `<div class="mel__retained"><span>No generated proposal retained yet</span><span>Choosing a card keeps that exact candidate separate from retrospective molecules.</span></div>`;
      return `<div class="mel__retained" data-testid="retained-candidate"><span>Retained proposal · <strong>${esc(candidate.molecule_id)}</strong> from seed ${esc(candidate.seed_id)}</span><span>Computed structure context only · experimental profile unknown</span></div>`;
    }

    function selectionShell(state) {
      if (!state.candidate_id) return selectionMarkup(state);
      return `<details class="mel__change"><summary>Change seed or retained proposal · current ${esc(state.candidate_id)}</summary>${selectionMarkup(state)}</details>`;
    }

    function endpointDisplay(record, stage, endpoint, index) {
      if (record.role === "generated_proposal") return {status: "missing", text: "unknown"};
      if (stage === "nomination" || stage === "prediction") {
        if (index < 2) return {status: "predicted", text: "predicted"};
        return {status: "hidden", text: "not shown"};
      }
      if (stage === "measured" && index > 1) return {status: "hidden", text: "not shown"};
      return {status: endpoint.status, text: endpoint.bound || (endpoint.value == null ? endpoint.status : `${number(endpoint.value, endpoint.value >= 100 ? 1 : 2)} ${endpoint.unit}`)};
    }

    function evidenceCard(id, state, fitKey = state.active_fit_key) {
      const record = records[id];
      if (!record) return `<div class="mel__panel"><p>Unknown record ${esc(id)}</p></div>`;
      const stage = state.returned_to_proposal ? "returned" : state.evidence_stage;
      const fitPrediction = predictions.get(`${fitKey}|${id}`);
      const ensemble = record.ensemble_prediction;
      const measurement = record.measurement_summary;
      const slots = record.endpoints.map((endpoint, index) => {
        const shown = endpointDisplay(record, stage, endpoint, index);
        return `<span class="mel__slot" data-status="${shown.status}" aria-label="${esc(endpoint.label)}: ${esc(shown.text)}">${esc(endpoint.short_label)}</span>`;
      }).join("");
      let values = "";
      if (record.role === "generated_proposal") {
        values = `<span><strong>Unknown</strong>experimental LogD</span><span><strong>Unknown</strong>experimental KSOL</span><span><strong>${esc(record.nearest_training_id)}</strong>nearest training context</span><span><strong>${number(record.nearest_training_similarity, 3)}</strong>Morgan similarity</span>`;
      } else if (stage === "nomination" && fitPrediction) {
        values = `<span><strong>${number(fitPrediction.pred_fit_LogD, 3)}</strong>fit-predicted LogD</span><span><strong>${number(fitPrediction.pred_fit_KSOL_uM, 1)} µM</strong>fit-predicted KSOL</span><span><strong>${data.nominations.inclusion_counts[id] || 0}/25</strong>fit nominations</span><span><strong>${esc(record.nearest_training_id)}</strong>training context</span>`;
      } else if (stage === "prediction" && ensemble) {
        values = `<span><strong>${number(ensemble.LogD, 3)}</strong>ensemble-predicted LogD</span><span><strong>${number(ensemble.KSOL_uM, 1)} µM</strong>ensemble-predicted KSOL</span><span><strong>${data.nominations.inclusion_counts[id] || 0}/25</strong>fit nominations</span><span><strong>${number(ensemble.score, 3)}</strong>illustrative score</span>`;
      } else if (measurement) {
        values = `<span><strong>${number(measurement.LogD, 2)}</strong>measured LogD</span><span><strong>${number(measurement.KSOL_uM, 1)} µM</strong>measured KSOL</span><span><strong>${measurement.target_pass ? "Meets" : "Misses"}</strong>two-property target</span><span><strong>${data.nominations.inclusion_counts[id] || 0}/25</strong>fit nominations</span>`;
        if (stage === "caco") {
          const papp = record.endpoints[4];
          const efflux = record.endpoints[5];
          values += `<span><strong>${papp.value == null ? esc(papp.bound || "unknown") : number(papp.value, 2)}</strong>Papp · ${esc(papp.unit)}</span><span><strong>${efflux.value == null ? esc(efflux.bound || "unknown") : number(efflux.value, 2)}</strong>efflux ratio</span>`;
        }
      }
      const badge = id === data.retrospective.unanimous_id ? "25/25 nomination—not certain success" : record.role.replaceAll("_", " ");
      return `<div class="mel__panel mel__card" data-testid="molecule-card">
        <div class="mel__structure">${depiction(id)}</div>
        <div class="mel__identity"><strong>${esc(id)}</strong><span class="mel__badge">${esc(badge)}</span></div>
        <div class="mel__strip">${slots}</div>
        <div class="mel__values">${values}</div>
        <p class="mel__muted" style="margin:10px 0 0">${esc(record.source)}</p>
      </div>`;
    }

    function trayMarkup(ids, state, stage) {
      return `<div class="mel__tray" aria-label="Committed fifty molecule tray">${ids.map((id) => {
        const record = records[id];
        const missingCaco = stage === "caco" && (record.endpoints[4].value == null || record.endpoints[5].value == null);
        const pass = stage !== "prediction" && record.measurement_summary && record.measurement_summary.target_pass;
        return `<button type="button" data-tray-id="${esc(id)}" data-pass="${Boolean(pass)}" data-missing="${missingCaco}" aria-pressed="${state.inspected_molecule_id === id}" aria-label="Inspect ${esc(id)}${missingCaco ? "; Caco-2 evidence missing or bounded" : ""}"></button>`;
      }).join("")}</div>`;
    }

    function nominationMarkup(state) {
      const fitIndex = clamp(Number(state.active_fit_index || 0), 0, nominations.fit_keys.length - 1);
      const fitKey = nominations.fit_keys[fitIndex];
      const active = new Set(nominations.nominations[fitKey]);
      const cells = nominations.union_order.map((id) => `<button type="button" class="mel__cell" data-union-id="${esc(id)}" data-nominated="${active.has(id)}" data-unanimous="${id === data.retrospective.unanimous_id}" aria-pressed="${state.inspected_molecule_id === id}" aria-label="${esc(id)}; nominated in ${data.nominations.inclusion_counts[id]} of 25 fits; ${active.has(id) ? "selected by active fit" : "not selected by active fit"}"></button>`).join("");
      const overlap = nominations.fit_to_ensemble_overlap[fitKey];
      return `<div class="mel__instrument">
        <div class="mel__panel mel__viewport">
          <div class="mel__toolbar">
            <div class="mel__fit"><div class="mel__fit-label"><strong>Action 4 · scrub the saved fits</strong><span data-fit-label>${esc(nominations.fit_metadata[fitIndex].label)}</span></div><input data-testid="fit-scrubber" type="range" min="0" max="24" step="1" value="${fitIndex}" aria-label="Saved model fit"></div>
            <div class="mel__stats"><span><strong>50</strong> nominated</span><span><strong data-overlap>${overlap}</strong> overlap ensemble</span></div>
          </div>
          <div class="mel__matrix" data-matrix aria-label="Fixed-order nomination layout of 256 molecules">${cells}</div>
          <div class="mel__legend"><span><i class="mel__swatch mel__swatch--selected"></i>active fit nomination</span><span><i class="mel__swatch"></i>not nominated</span><span><i class="mel__swatch mel__swatch--unanimous"></i>unanimous nomination</span><span>Layout order: inclusion frequency descending, ensemble score descending, ID ascending; not chemical geometry.</span></div>
          ${trayMarkup(nominations.nominations[fitKey], state, "prediction")}
          <p class="mel__muted">Across all 25 saved repeat/fold fits: <strong>256 distinct nominations</strong>, <strong>1 unanimous record</strong>. These related fits share methods and overlapping training data; disagreement is selection sensitivity, not calibrated uncertainty.</p>
          <div class="mel__action-row"><button type="button" class="mel__action" data-primary="true" data-action="commit" ${state.fit_explored ? "" : "disabled"}>Action 5 · commit the ensemble fifty</button><span class="mel__muted">The ensemble is explicit; it never becomes the last fit you touched.</span></div>
        </div>
        <div data-card-host>${evidenceCard(state.inspected_molecule_id, state, fitKey)}</div>
      </div>`;
    }

    function plotGeometry() {
      const ids = nominations.ensemble_ids;
      const xs = [];
      const ys = [];
      for (const id of ids) {
        const record = records[id];
        xs.push(record.ensemble_prediction.LogD, record.measurement_summary.LogD);
        ys.push(record.ensemble_prediction.KSOL_uM, record.measurement_summary.KSOL_uM);
      }
      const xMin = Math.floor((Math.min(...xs) - .2) * 2) / 2;
      const xMax = Math.ceil((Math.max(...xs) + .2) * 2) / 2;
      const lyMin = Math.log10(Math.min(...ys) * .8);
      const lyMax = Math.log10(Math.max(...ys) * 1.25);
      const box = {w: 720, h: 390, left: 62, right: 22, top: 20, bottom: 54};
      const x = (value) => box.left + (value - xMin) / (xMax - xMin) * (box.w - box.left - box.right);
      const y = (value) => box.top + (lyMax - Math.log10(value)) / (lyMax - lyMin) * (box.h - box.top - box.bottom);
      return {ids, xMin, xMax, lyMin, lyMax, box, x, y};
    }

    function propertyPlot(state) {
      const geometry = plotGeometry();
      const measured = state.evidence_stage !== "prediction";
      const {box, x, y} = geometry;
      const xTicks = Array.from({length: 6}, (_, index) => geometry.xMin + index * (geometry.xMax - geometry.xMin) / 5);
      const yTicks = [100, 200, 500, 1000].filter((tick) => Math.log10(tick) >= geometry.lyMin && Math.log10(tick) <= geometry.lyMax);
      const target = data.targets;
      const selected = state.inspected_molecule_id;
      const selectedRecord = records[selected];
      const connector = measured && selectedRecord ? `<line class="connector" x1="${x(selectedRecord.ensemble_prediction.LogD)}" y1="${y(selectedRecord.ensemble_prediction.KSOL_uM)}" x2="${x(selectedRecord.measurement_summary.LogD)}" y2="${y(selectedRecord.measurement_summary.KSOL_uM)}"></line>` : "";
      const points = geometry.ids.map((id) => {
        const record = records[id];
        const px = measured ? record.measurement_summary.LogD : record.ensemble_prediction.LogD;
        const py = measured ? record.measurement_summary.KSOL_uM : record.ensemble_prediction.KSOL_uM;
        return `<circle class="point" data-point-id="${esc(id)}" data-measured="${measured}" data-pass="${measured ? record.measurement_summary.target_pass : true}" data-selected="${id === selected}" cx="${x(px)}" cy="${y(py)}" r="${id === selected ? 7 : 5}" role="button" aria-label="Inspect ${esc(id)}: ${measured ? "measured" : "ensemble-predicted"} LogD ${number(px, 2)}, kinetic solubility ${number(py, 1)} micromolar"></circle>`;
      }).join("");
      return `<svg class="mel__plot" data-testid="property-plane" viewBox="0 0 ${box.w} ${box.h}" role="img" aria-label="The committed fifty in the LogD and kinetic-solubility property plane">
        <rect class="target" x="${x(target.logd_low)}" y="${box.top}" width="${x(target.logd_high) - x(target.logd_low)}" height="${y(target.ksol_min_um) - box.top}"></rect>
        ${xTicks.map((tick) => `<line class="axis" x1="${x(tick)}" y1="${box.top}" x2="${x(tick)}" y2="${box.h - box.bottom}"></line><text class="tick" x="${x(tick)}" y="${box.h - box.bottom + 18}" text-anchor="middle">${number(tick, 1)}</text>`).join("")}
        ${yTicks.map((tick) => `<line class="axis" x1="${box.left}" y1="${y(tick)}" x2="${box.w - box.right}" y2="${y(tick)}"></line><text class="tick" x="${box.left - 9}" y="${y(tick) + 4}" text-anchor="end">${tick}</text>`).join("")}
        <text class="axis-label" x="${(box.left + box.w - box.right) / 2}" y="${box.h - 13}" text-anchor="middle">${measured ? "Measured" : "Ensemble-predicted"} LogD</text>
        <text class="axis-label" transform="translate(16 ${(box.top + box.h - box.bottom) / 2}) rotate(-90)" text-anchor="middle">${measured ? "Measured" : "Ensemble-predicted"} KSOL (µM, log scale)</text>
        ${connector}${points}
      </svg>`;
    }

    function randomBand() {
      const ref = data.retrospective.random_reference;
      const x = (value) => 28 + value / 50 * 664;
      return `<svg class="mel__random" viewBox="0 0 720 52" role="img" aria-label="Random fifty 95 percent simulated range ${ref.random_low_95} to ${ref.random_high_95}; exact expected ${number(ref.random_expected_passes, 2)}; ensemble observed ${ref.selected_passes}">
        <line x1="28" y1="25" x2="692" y2="25" stroke="var(--line)"></line>
        <rect class="band" x="${x(ref.random_low_95)}" y="15" width="${x(ref.random_high_95) - x(ref.random_low_95)}" height="20" rx="5"></rect>
        <line class="expected" x1="${x(ref.random_expected_passes)}" y1="10" x2="${x(ref.random_expected_passes)}" y2="40"></line>
        <line class="observed" x1="${x(ref.selected_passes)}" y1="7" x2="${x(ref.selected_passes)}" y2="43"></line>
        <text x="28" y="50">0 passes</text><text x="692" y="50" text-anchor="end">50 passes</text>
      </svg>`;
    }

    function outcomeMarkup(state) {
      const measured = state.evidence_stage !== "prediction";
      const unanimous = records[data.retrospective.unanimous_id];
      const ref = data.retrospective.random_reference;
      return `<div class="mel__instrument">
        <div class="mel__panel mel__viewport">
          <div class="mel__toolbar"><div><p class="mel__eyebrow">${measured ? "Action 6 · measurements revealed" : "Action 5 · ensemble committed"}</p><h3>${measured ? "The same fifty, now measured" : "The ensemble fifty, before measurement"}</h3></div>${measured ? `<button type="button" class="mel__action" data-action="replay">Replay movement</button>` : ""}</div>
          <div data-plot-host>${propertyPlot(state)}</div>
          ${trayMarkup(nominations.ensemble_ids, state, state.evidence_stage)}
          ${measured ? `<div class="mel__result"><div class="mel__metric"><strong>41/50</strong>meet the measured two-property target</div><div class="mel__metric"><strong>${number(ref.random_expected_passes, 2)}</strong>exact passes expected for random fifty</div><div class="mel__metric"><strong>${number(unanimous.measurement_summary.LogD, 2)}</strong>measured LogD for the 25/25 nominee</div></div>${randomBand()}<p class="mel__muted">Shaded band: 95% of 2,000 seeded random-shortlist pass counts (${ref.random_low_95.toFixed(0)}–${ref.random_high_95.toFixed(0)}). Blue line: analytic expectation. Teal line: ensemble result. This is random-selection variation, not assay uncertainty.</p>` : `<p class="mel__muted">Target: LogD ${data.targets.logd_low}–${data.targets.logd_high}, KSOL ≥${data.targets.ksol_min_um} µM. Fifty is an illustrative attention limit. Outcomes remain hidden.</p>`}
          <div class="mel__action-row">${measured ? `<button type="button" class="mel__action" data-primary="true" data-action="caco">Action 7 · expand the ADMET question</button>` : `<button type="button" class="mel__action" data-primary="true" data-action="measure">Action 6 · reveal measurements</button>`}</div>
        </div>
        <div data-card-host>${evidenceCard(state.inspected_molecule_id, state)}</div>
      </div>`;
    }

    function cacoPlot(state) {
      const ids = nominations.ensemble_ids;
      const paired = ids.filter((id) => records[id].endpoints[4].value != null && records[id].endpoints[5].value != null);
      const papp = paired.map((id) => records[id].endpoints[4].value);
      const efflux = paired.map((id) => records[id].endpoints[5].value);
      const box = {w:720,h:390,left:64,right:22,top:22,bottom:54};
      const xMin = 0, xMax = Math.ceil(Math.max(...papp) / 5) * 5;
      const yMin = 0, yMax = Math.ceil(Math.max(...efflux));
      const x = (value) => box.left + (value - xMin) / (xMax - xMin) * (box.w - box.left - box.right);
      const y = (value) => box.top + (yMax - value) / (yMax - yMin) * (box.h - box.top - box.bottom);
      const ticks = [0,.25,.5,.75,1];
      const points = paired.map((id) => {
        const record = records[id];
        const pass = record.measurement_summary.target_pass;
        return `<circle class="point" data-caco-id="${esc(id)}" data-measured="true" data-pass="${pass}" data-selected="${id === state.inspected_molecule_id}" cx="${x(record.endpoints[4].value)}" cy="${y(record.endpoints[5].value)}" r="${id === state.inspected_molecule_id ? 7 : 5}" role="button" aria-label="Inspect ${esc(id)}: Papp ${number(record.endpoints[4].value, 2)}, efflux ${number(record.endpoints[5].value, 2)}"></circle>`;
      }).join("");
      return `<svg class="mel__plot" data-testid="caco-plane" viewBox="0 0 ${box.w} ${box.h}" role="img" aria-label="Caco-2 Papp and efflux measurements for 38 of the unchanged fifty">
        ${ticks.map((fraction) => `<line class="axis" x1="${x(fraction*xMax)}" y1="${box.top}" x2="${x(fraction*xMax)}" y2="${box.h-box.bottom}"></line><text class="tick" x="${x(fraction*xMax)}" y="${box.h-box.bottom+18}" text-anchor="middle">${number(fraction*xMax,0)}</text><line class="axis" x1="${box.left}" y1="${y(fraction*yMax)}" x2="${box.w-box.right}" y2="${y(fraction*yMax)}"></line><text class="tick" x="${box.left-9}" y="${y(fraction*yMax)+4}" text-anchor="end">${number(fraction*yMax,1)}</text>`).join("")}
        <text class="axis-label" x="${(box.left+box.w-box.right)/2}" y="${box.h-13}" text-anchor="middle">Measured Caco-2 Papp A&gt;B (10^-6 cm/s)</text>
        <text class="axis-label" transform="translate(16 ${(box.top+box.h-box.bottom)/2}) rotate(-90)" text-anchor="middle">Measured Caco-2 efflux ratio</text>${points}
      </svg>`;
    }

    function cacoMarkup(state) {
      return `<div class="mel__instrument">
        <div class="mel__panel mel__viewport">
          <div class="mel__toolbar"><div><p class="mel__eyebrow">Action 7 · a different property plane</p><h3>The first success remains visible; Caco-2 asks another question.</h3></div><div class="mel__badge">41/50 still meet LogD/KSOL target</div></div>
          ${cacoPlot(state)}
          ${trayMarkup(nominations.ensemble_ids, state, "caco")}
          <div class="mel__result"><div class="mel__metric"><strong>38/50</strong>paired numeric Caco-2 evidence</div><div class="mel__metric"><strong>33/41</strong>initial passes with paired Caco-2</div><div class="mel__metric"><strong>12</strong>remain without a paired numeric view</div></div>
          <p class="mel__muted">Hatched tray slots are missing or bounded for at least one Caco-2 measure; they are selectable and are not counted as failures. Optional contrasts: <button type="button" class="mel__action" data-inspect-example="E-0023839">broader-profile contrast E-0023839</button>.</p>
          <div class="mel__action-row"><button type="button" class="mel__action" data-primary="true" data-action="return">Action 8 · return to my proposal</button><button type="button" class="mel__action" data-action="restart">Restart retrospective</button></div>
        </div>
        <div data-card-host>${evidenceCard(state.inspected_molecule_id, state)}</div>
      </div>`;
    }

    const assayReasons = {
      "Caco-2 permeability and efflux": "Could reveal transport behavior that the original LogD/KSOL question cannot answer.",
      "Kinetic solubility": "Would replace a computed context cue with a measurement for this exact proposal.",
      "HLM intrinsic clearance": "Would add a human-microsomal metabolism question omitted by the original objective.",
    };

    function returnMarkup(state) {
      const candidate = records[state.candidate_id];
      if (!candidate) return `<div class="mel__panel"><p>The retained candidate is missing. Choose a proposal again.</p></div>`;
      const hope = data.retrospective.encouraging_ids.map((id) => {
        const record = records[id];
        return `<div class="mel__hope-card"><div class="mel__structure">${depiction(id)}</div><strong>${esc(id)}</strong><p class="mel__muted">Measured LogD ${number(record.measurement_summary.LogD,2)} · KSOL ${number(record.measurement_summary.KSOL_uM,1)} µM. Example rule: measured target pass with broader-profile evidence; not a clinical claim.</p></div>`;
      }).join("");
      const assays = Object.keys(assayReasons).map((assay) => `<button type="button" class="mel__assay" data-assay="${esc(assay)}" aria-pressed="${state.next_assay === assay}"><strong>${esc(assay)}</strong><span class="mel__muted">${esc(assayReasons[assay])}</span></button>`).join("");
      return `<div class="mel__return">
        <div>${evidenceCard(candidate.molecule_id, state)}<div class="mel__panel" style="margin-top:12px"><p class="mel__eyebrow">Action 9 · choose the next assay</p><div class="mel__assays">${assays}</div>${state.next_assay ? `<div class="mel__decision" aria-live="polite"><strong>${esc(candidate.molecule_id)}</strong> · next question: ${esc(state.next_assay)}. ${esc(assayReasons[state.next_assay])} No assay is commissioned and no result is fabricated.</div>` : ""}<div class="mel__action-row"><button type="button" class="mel__action" data-action="restart">Restart retrospective</button></div></div></div>
        <div class="mel__panel"><p class="mel__eyebrow">Measured reasons for hope</p><h3>Useful enrichment survived the surprise.</h3><p class="mel__muted">These are encouraging property profiles from the separate retrospective fifty. Their measurements never transfer to ${esc(candidate.molecule_id)}.</p><div class="mel__hope">${hope}</div></div>
      </div>`;
    }

    function bindSelection(state) {
      root.querySelectorAll("[data-seed-id]").forEach((button) => button.addEventListener("click", () => {
        setState({seed_id: button.dataset.seedId, candidate_id: null, returned_to_proposal: false, next_assay: null});
      }));
      root.querySelectorAll("[data-candidate-id]").forEach((button) => button.addEventListener("click", () => {
        setState({candidate_id: button.dataset.candidateId, returned_to_proposal: false, next_assay: null});
      }));
    }

    function bindInspection() {
      root.querySelectorAll("[data-union-id], [data-tray-id], [data-point-id], [data-caco-id], [data-inspect-example]").forEach((element) => {
        const activate = () => {
          const id = element.dataset.unionId || element.dataset.trayId || element.dataset.pointId || element.dataset.cacoId || element.dataset.inspectExample;
          setState({inspected_molecule_id: id});
        };
        element.addEventListener("click", activate);
        if (element.tagName.toLowerCase() === "circle") {
          element.setAttribute("tabindex", "0");
          element.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") { event.preventDefault(); activate(); }
          });
        }
      });
    }

    function updateFitLocal(index) {
      const fitKey = nominations.fit_keys[index];
      const active = new Set(nominations.nominations[fitKey]);
      const label = root.querySelector("[data-fit-label]");
      const overlap = root.querySelector("[data-overlap]");
      if (label) label.textContent = nominations.fit_metadata[index].label;
      if (overlap) overlap.textContent = nominations.fit_to_ensemble_overlap[fitKey];
      root.querySelectorAll("[data-union-id]").forEach((cell) => {
        const nominated = active.has(cell.dataset.unionId);
        cell.dataset.nominated = String(nominated);
        cell.setAttribute("aria-label", `${cell.dataset.unionId}; nominated in ${nominations.inclusion_counts[cell.dataset.unionId]} of 25 fits; ${nominated ? "selected by active fit" : "not selected by active fit"}`);
      });
      const tray = root.querySelector(".mel__tray");
      if (tray) tray.outerHTML = trayMarkup(nominations.nominations[fitKey], {...getState(), active_fit_index:index, active_fit_key:fitKey}, "prediction");
      const host = root.querySelector("[data-card-host]");
      if (host) host.innerHTML = evidenceCard(data.retrospective.unanimous_id, {...getState(), active_fit_index:index, active_fit_key:fitKey, inspected_molecule_id:data.retrospective.unanimous_id}, fitKey);
      root.querySelectorAll("[data-tray-id]").forEach((element) => element.addEventListener("click", () => setState({inspected_molecule_id:element.dataset.trayId})));
    }

    function bindNomination(state) {
      const slider = root.querySelector('[data-testid="fit-scrubber"]');
      if (slider) {
        slider.addEventListener("input", () => {
          const index = Number(slider.value);
          updateFitLocal(index);
          window.clearTimeout(fitDebounce);
          fitDebounce = window.setTimeout(() => setState({active_fit_index:index, active_fit_key:nominations.fit_keys[index], inspected_molecule_id:data.retrospective.unanimous_id, fit_explored:true}), 180);
        });
        slider.addEventListener("change", () => {
          window.clearTimeout(fitDebounce);
          const index = Number(slider.value);
          setState({active_fit_index:index, active_fit_key:nominations.fit_keys[index], inspected_molecule_id:data.retrospective.unanimous_id, fit_explored:true});
        });
      }
      const commit = root.querySelector('[data-action="commit"]');
      if (commit) commit.addEventListener("click", () => setState({selection_kind:"ensemble", committed_ids:[...nominations.ensemble_ids], evidence_stage:"prediction", inspected_molecule_id:data.retrospective.unanimous_id}));
    }

    function animateMeasurement(force = false) {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches && !force) return;
      const svg = root.querySelector('[data-testid="property-plane"]');
      if (!svg || getState().evidence_stage !== "measured") return;
      const geometry = plotGeometry();
      const start = performance.now();
      const duration = 850;
      const tick = (now) => {
        const t = clamp((now - start) / duration, 0, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        svg.querySelectorAll("[data-point-id]").forEach((circle) => {
          const record = records[circle.dataset.pointId];
          const px = record.ensemble_prediction.LogD + (record.measurement_summary.LogD - record.ensemble_prediction.LogD) * eased;
          const pyLog = Math.log10(record.ensemble_prediction.KSOL_uM) + (Math.log10(record.measurement_summary.KSOL_uM) - Math.log10(record.ensemble_prediction.KSOL_uM)) * eased;
          circle.setAttribute("cx", geometry.x(px));
          circle.setAttribute("cy", geometry.y(Math.pow(10, pyLog)));
        });
        if (t < 1) animationFrame = requestAnimationFrame(tick);
      };
      animationFrame = requestAnimationFrame(tick);
    }

    function bindOutcome(state, shouldAnimate) {
      const measure = root.querySelector('[data-action="measure"]');
      if (measure) measure.addEventListener("click", () => setState({evidence_stage:"measured", measurements_revealed:true, inspected_molecule_id:data.retrospective.unanimous_id}));
      const replay = root.querySelector('[data-action="replay"]');
      if (replay) replay.addEventListener("click", () => animateMeasurement(true));
      const caco = root.querySelector('[data-action="caco"]');
      if (caco) caco.addEventListener("click", () => setState({evidence_stage:"caco", caco_revealed:true}));
      if (shouldAnimate) animateMeasurement(false);
    }

    function bindCaco() {
      const back = root.querySelector('[data-action="return"]');
      if (back) back.addEventListener("click", () => {
        const state = getState();
        setState({returned_to_proposal:true, evidence_stage:"returned", inspected_molecule_id:state.candidate_id});
      });
      bindRestart();
    }

    function bindReturn() {
      root.querySelectorAll("[data-assay]").forEach((button) => button.addEventListener("click", () => setState({next_assay:button.dataset.assay})));
      bindRestart();
    }

    function bindRestart() {
      const restart = root.querySelector('[data-action="restart"]');
      if (restart) restart.addEventListener("click", () => setState({
        active_fit_index: 0,
        active_fit_key: nominations.fit_keys[0],
        inspected_molecule_id: data.retrospective.unanimous_id,
        selection_kind: null,
        committed_ids: [],
        evidence_stage: "nomination",
        measurements_revealed: false,
        caco_revealed: false,
        returned_to_proposal: false,
        next_assay: null,
        fit_explored: false,
      }));
    }

    function draw() {
      if (animationFrame !== null) cancelAnimationFrame(animationFrame);
      const state = getState();
      const shouldAnimate = previousStage !== "measured" && state.evidence_stage === "measured";
      previousStage = state.evidence_stage;
      let body = "";
      if (!state.candidate_id) {
        body = selectionMarkup(state) + retainedMarkup(state) + `<div class="mel__panel"><p class="mel__muted">Choose a proposal card to enter the separate retrospective investigation.</p></div>`;
      } else if (state.returned_to_proposal) {
        body = retainedMarkup(state) + returnMarkup(state);
      } else if (state.caco_revealed) {
        body = selectionShell(state) + retainedMarkup(state) + cacoMarkup(state);
      } else if (state.selection_kind === "ensemble") {
        body = selectionShell(state) + retainedMarkup(state) + outcomeMarkup(state);
      } else {
        body = selectionShell(state) + retainedMarkup(state) + nominationMarkup(state);
      }
      root.innerHTML = `<div class="mel__header"><div><p class="mel__eyebrow">Before You Make It · fifty experiments · twenty-five maps</p><h2>Which fifty survive a changing map?</h2><p class="mel__muted">MoleculeEvidenceLens keeps one identity anchored while the source of evidence changes.</p></div><div class="mel__progress" aria-label="${stageIndex(state)} of 9 required actions">${progress(state)}</div></div>${body}`;
      bindSelection(state);
      bindInspection();
      if (state.candidate_id && !state.returned_to_proposal && !state.caco_revealed && state.selection_kind !== "ensemble") bindNomination(state);
      if (state.selection_kind === "ensemble" && !state.caco_revealed && !state.returned_to_proposal) bindOutcome(state, shouldAnimate);
      if (state.caco_revealed && !state.returned_to_proposal) bindCaco();
      if (state.returned_to_proposal) bindReturn();
    }

    draw();
    const onState = () => draw();
    model.on("change:state", onState);
    return () => {
      if (animationFrame !== null) cancelAnimationFrame(animationFrame);
      if (fitDebounce !== null) window.clearTimeout(fitDebounce);
      model.off("change:state", onState);
    };
  },
};
