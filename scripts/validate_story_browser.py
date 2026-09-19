"""Exercise the guided notebook in a real browser and retain validation evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright


def snapshot(page: Page, output: Path, name: str) -> None:
    page.screenshot(path=output / f"{name}.png", full_page=True)


def click_action(page: Page, action_text: str) -> None:
    action = page.get_by_text(action_text, exact=False).first
    expect(action).to_be_visible(timeout=30_000)
    action.click()
    page.wait_for_timeout(1_000)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/notebook_validation/story-rework-browser"),
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    checkpoints: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.goto(args.url, wait_until="domcontentloaded", timeout=60_000)
        expect(page.get_by_text("Before You Make It", exact=True)).to_be_visible(
            timeout=60_000
        )
        expect(page.get_by_text("166 billion molecules", exact=False)).to_be_visible()
        snapshot(page, args.output, "01-scale")
        checkpoints.append("opening-scale")

        expect(page.get_by_text("Start from a real training molecule", exact=False)).to_be_visible()
        expect(page.get_by_text("Candidate batch", exact=False)).to_be_visible()
        snapshot(page, args.output, "02-seed-to-candidates")
        checkpoints.append("seed-candidate-interaction")

        click_action(page, "Commit fifty retrospective choices")
        expect(page.get_by_text("Prediction-only selection", exact=False)).to_be_visible()
        snapshot(page, args.output, "03-prediction-only")
        checkpoints.append("prediction-only-choice")

        click_action(page, "Reveal what the lab already knew")
        expect(page.get_by_text("41/50", exact=False)).to_be_visible()
        snapshot(page, args.output, "04-logd-ksol-reveal")
        checkpoints.append("logd-ksol-reveal")

        click_action(page, "Reveal Caco-2 as a second experimental question")
        expect(page.get_by_text("38/50", exact=False)).to_be_visible()
        snapshot(page, args.output, "05-caco-reveal")
        checkpoints.append("caco-reveal")

        expect(page.get_by_text("Inspect a molecule in context", exact=False)).to_be_visible()
        click_action(page, "Return to the exact candidate")
        expect(page.get_by_text("Choose the next question", exact=False)).to_be_visible()
        snapshot(page, args.output, "06-assay-decision")
        checkpoints.append("inspection-to-assay-decision")

        browser.close()

    (args.output / "interaction_log.json").write_text(
        json.dumps({"status": "passed", "checkpoints": checkpoints}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
