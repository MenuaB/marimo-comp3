"""Exercise the complete custom visual story in a live marimo browser session."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

from playwright.sync_api import Browser, Page, expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = json.loads((ROOT / "data" / "molab_bundle.json").read_text())


def capture(locator, output: Path, name: str) -> None:
    locator.scroll_into_view_if_needed()
    locator.screenshot(path=output / f"{name}.png")


def wait_lens(page: Page):
    lens = page.locator('[data-testid="molecule-evidence-lens"]')
    expect(lens.get_by_role("heading", name="Pick a starting point—and know what the choice changes.")).to_be_visible(
        timeout=60_000
    )
    return lens


def open_story(browser: Browser, url: str, *, reduced_motion: bool = False) -> Page:
    context = browser.new_context(
        viewport={"width": 1440, "height": 1050},
        reduced_motion="reduce" if reduced_motion else "no-preference",
    )
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    expect(
        page.get_by_role("heading", name="Before You Make It", exact=True)
    ).to_be_visible(timeout=60_000)
    expect(page.get_by_text("Imagine you can test only fifty molecules.", exact=False)).to_be_visible()
    wait_lens(page)
    return page


def exercise_main_path(page: Page, output: Path) -> tuple[list[dict[str, object]], float]:
    started = time.perf_counter()
    events: list[dict[str, object]] = []
    scale = page.locator('[data-testid="scale-journey"]')
    lens = wait_lens(page)
    page.screenshot(path=output / "00-complete-opening.png", full_page=True)

    scale.get_by_role("button", name="Show the summary").click()
    expect(scale.get_by_text("From possibilities to evidence", exact=False)).to_be_visible()
    expect(scale.get_by_text("5,260 years", exact=False)).to_be_visible()
    expect(scale.get_by_text("7,608", exact=False)).to_be_visible()
    capture(scale, output, "01-scale-and-evidence")
    events.append({"action": 1, "state": "scale skipped to real recorded evidence"})

    lens.locator('[data-seed-id="E-0015392"]').click()
    expect(lens.locator('[data-candidate-id="C-0035"]')).to_be_visible()
    events.append({"action": 2, "seed_id": "E-0015392"})

    lens.locator('[data-candidate-id="C-0035"]').click()
    expect(lens.locator('[data-testid="retained-candidate"]')).to_contain_text("C-0035")
    expect(lens.get_by_text("A separate retrospective test", exact=False)).to_be_visible()
    events.append({"action": 3, "candidate_id": "C-0035"})

    slider = lens.locator('[data-testid="fit-scrubber"]')
    for value in (4, 19, 8, 24):
        slider.evaluate(
            "(element, value) => { element.value = value; element.dispatchEvent(new Event('input', {bubbles:true})); }",
            value,
        )
    slider.evaluate(
        "element => element.dispatchEvent(new Event('change', {bubbles:true}))"
    )
    expect(lens.get_by_text("Repeat 5 · fold 5", exact=True)).to_be_visible()
    expect(lens.locator('[data-testid="molecule-card"]')).to_contain_text("E-0024329")
    expect(lens.locator('[data-testid="molecule-card"]')).to_contain_text("25/25")
    capture(lens, output, "02-fit-disagreement")
    events.append(
        {
            "action": 4,
            "fit_key": "repeat-5-fold-5",
            "focused_id": "E-0024329",
            "union": 256,
            "intersection": 1,
        }
    )

    lens.get_by_role("button", name="Choose this model’s fifty").click()
    expect(lens.locator('[data-testid="property-plane"]')).to_be_visible()
    expect(lens).to_contain_text("Outcomes remain hidden")
    assert "41/50" not in lens.inner_text()
    assert "measured LogD 0.70" not in lens.inner_text()
    events.append({"action": 5, "selection_kind": "active_fit", "fit_key": "repeat-5-fold-5", "committed_count": 50})

    lens.get_by_role("button", name="Compare with measurements").click()
    expect(lens.get_by_text("36/50", exact=True)).to_be_visible()
    expect(lens.locator('[data-testid="molecule-card"]')).to_contain_text(
        "measured LogD"
    )
    expect(lens.locator('[data-testid="molecule-card"]')).to_contain_text("0.70")
    lens.get_by_role("button", name="Replay predicted-to-measured movement").click()
    capture(lens, output, "03-measured-reveal")
    events.append(
        {
            "action": 6,
            "selected_passes": 36,
            "random_expected": 20.949074074074073,
            "unanimous_measured_logd": 0.7,
        }
    )

    lens.get_by_role("button", name="Ask about permeability and efflux").click()
    expect(lens.locator('[data-testid="caco-plane"]')).to_be_visible()
    active_ids = PAYLOAD["nominations"]["nominations"]["repeat-5-fold-5"]
    active_paired = sum(
        PAYLOAD["evidence_records"][molecule_id]["endpoints"][4]["value"] is not None
        and PAYLOAD["evidence_records"][molecule_id]["endpoints"][5]["value"] is not None
        for molecule_id in active_ids
    )
    active_paired_passes = sum(
        PAYLOAD["evidence_records"][molecule_id]["measurement_summary"]["target_pass"]
        and PAYLOAD["evidence_records"][molecule_id]["endpoints"][4]["value"] is not None
        and PAYLOAD["evidence_records"][molecule_id]["endpoints"][5]["value"] is not None
        for molecule_id in active_ids
    )
    expect(lens.get_by_text(f"{active_paired}/50", exact=True)).to_be_visible()
    expect(lens.get_by_text(f"{active_paired_passes}/36", exact=True)).to_be_visible()
    capture(lens, output, "04-caco-evidence")
    events.append({"action": 7, "caco_paired": active_paired, "paired_among_passes": active_paired_passes})

    lens.get_by_role("button", name="Apply the lesson to my proposal").click()
    expect(lens.locator('[data-testid="molecule-card"]')).to_contain_text("C-0035")
    expect(lens.locator('[data-testid="molecule-card"]')).to_contain_text(
        "experimental LogD"
    )
    events.append({"action": 8, "restored_candidate_id": "C-0035"})

    lens.locator('[data-assay="HLM intrinsic clearance"]').click()
    expect(lens.locator(".mel__decision")).to_contain_text("C-0035")
    expect(lens.locator(".mel__decision")).to_contain_text("HLM intrinsic clearance")
    bridge = page.get_by_text(re.compile(r"^Live shortlist analysis"))
    bridge.first.click()
    expect(page.get_by_text("Paired Caco-2 evidence", exact=True)).to_be_visible(timeout=10_000)
    capture(lens, output, "05-final-candidate-decision")
    events.append(
        {
            "action": 9,
            "candidate_id": "C-0035",
            "next_assay": "HLM intrinsic clearance",
        }
    )

    lens.get_by_role("button", name="Restart retrospective").click()
    expect(lens.locator('[data-testid="fit-scrubber"]')).to_be_visible()
    assert "41/50" not in lens.inner_text()
    events.append({"optional": "restart", "state": "prediction-only nomination"})

    # A second, independent route proves that the ensemble remains explicit
    # and has its own measured total rather than inheriting the active fit.
    slider = lens.locator('[data-testid="fit-scrubber"]')
    slider.evaluate("element => element.dispatchEvent(new Event('change', {bubbles:true}))")
    lens.get_by_role("button", name="Choose the averaged-model fifty").click()
    expect(lens).to_contain_text("Ensemble shortlist")
    lens.get_by_role("button", name="Compare with measurements").click()
    expect(lens.get_by_text("41/50", exact=True)).to_be_visible()
    events.append({"optional": "ensemble route", "selection_kind": "ensemble", "selected_passes": 41})

    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(300)
    overflow = lens.evaluate("element => element.scrollWidth - element.clientWidth")
    if overflow > 1:
        raise AssertionError(f"Narrow widget overflows horizontally by {overflow}px")
    capture(lens, output, "06-narrow-layout")
    events.append({"optional": "resize", "viewport": "390x844", "overflow_px": overflow})
    return events, time.perf_counter() - started


def exercise_reduced_motion(browser: Browser, url: str, output: Path) -> dict[str, object]:
    page = open_story(browser, url, reduced_motion=True)
    scale = page.locator('[data-testid="scale-journey"]')
    started = time.perf_counter()
    scale.get_by_role("button", name="Show the scale").click()
    expect(scale.get_by_text("From possibilities to evidence", exact=False)).to_be_visible(
        timeout=2_000
    )
    capture(scale, output, "07-reduced-motion")
    elapsed = time.perf_counter() - started
    page.context.close()
    return {"optional": "reduced-motion", "completed_seconds": elapsed}


def exercise_full_scale(browser: Browser, url: str, output: Path) -> dict[str, object]:
    page = open_story(browser, url)
    scale = page.locator('[data-testid="scale-journey"]')
    started = time.perf_counter()
    scale.get_by_role("button", name="Show the scale").click()
    expect(scale.get_by_text("From possibilities to evidence", exact=False)).to_be_visible(
        timeout=12_000
    )
    expect(scale.get_by_text("5,260 years", exact=False)).to_be_visible()
    capture(scale, output, "08-full-scale-route")
    elapsed = time.perf_counter() - started
    page.context.close()
    return {"optional": "full-scale-route", "completed_seconds": elapsed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/notebook_validation/custom-visual-story"),
    )
    parser.add_argument("--environment", default="native")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    browser_runtime = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "bundled")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        startup = time.perf_counter()
        page = open_story(browser, args.url)
        startup_seconds = time.perf_counter() - startup
        events, interaction_seconds = exercise_main_path(page, args.output)
        page.context.close()
        events.append(exercise_reduced_motion(browser, args.url, args.output))
        events.append(exercise_full_scale(browser, args.url, args.output))
        browser.close()

    log = {
        "status": "passed",
        "environment": args.environment,
        "url": args.url,
        "required_actions": 9,
        "startup_seconds": startup_seconds,
        "interaction_seconds": interaction_seconds,
        "browser_runtime": browser_runtime,
        "events": events,
    }
    (args.output / "interaction_log.json").write_text(
        json.dumps(log, indent=2) + "\n"
    )
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
