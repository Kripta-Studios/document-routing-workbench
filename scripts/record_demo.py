"""Record the owned-fixture browser demo in isolated, ignored runtime storage.

Requires Playwright with a local Chrome installation and the bootstrapped Mustang JARs.
The raw WebM is printed; convert it to the distributable MP4 with ffmpeg.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime" / "demo-recordings"
CHROME = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
PORT = 8771
URL = f"http://127.0.0.1:{PORT}/"


def wait_for_server(process):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError("Demo server exited before it became ready")
        try:
            with urllib.request.urlopen(URL, timeout=0.5) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.15)
    raise TimeoutError("Demo server did not become ready")


def cue(page, message, selector=None, seconds=1.5):
    if selector:
        target = page.locator(selector).first
        target.evaluate("el => el.scrollIntoView({block:'center', behavior:'smooth'})")
        page.wait_for_timeout(550)
        page.locator(".demo-focus").evaluate_all("nodes => nodes.forEach(el => el.classList.remove('demo-focus'))")
        target.evaluate("el => el.classList.add('demo-focus')")
    page.locator("#demo-caption").inner_text()
    page.evaluate("message => document.querySelector('#demo-caption').textContent = message", message)
    page.wait_for_timeout(int(seconds * 1000))


def main():
    if not CHROME.exists() or not PYTHON.exists():
        raise RuntimeError("Local Chrome and the project .venv are required")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    session = RUNTIME / stamp
    session.mkdir(parents=True)
    environment = dict(os.environ)
    environment["SOURCECHECK_DATA"] = str(session / "data")
    environment.pop("TYPESAFE_API_KEY", None)
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    server = subprocess.Popen(
        [str(PYTHON), "-m", "sourcecheck", "serve", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=ROOT, env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    try:
        wait_for_server(server)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, executable_path=str(CHROME))
            context = browser.new_context(
                viewport={"width": 1440, "height": 810},
                record_video_dir=str(session),
                record_video_size={"width": 1440, "height": 810},
                accept_downloads=True,
            )
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(URL)
            page.add_style_tag(content="""
                .demo-focus { outline: 4px solid #e56845 !important; outline-offset: 5px; }
                #demo-caption { position: fixed; z-index: 99999; left: 50%; bottom: 20px;
                    transform: translateX(-50%); width: max-content; max-width: 88vw;
                    padding: 13px 22px; border-radius: 8px; background: #12302de8;
                    color: white; font: 600 22px/1.25 Arial, sans-serif;
                    text-align: center; pointer-events: none; box-shadow: 0 8px 30px #0005; }
                #demo-card { position: fixed; z-index: 100000; inset: 0; display: grid;
                    place-content: center; gap: 20px; text-align: center; background: #112e2b;
                    color: #faf9ef; font-family: Georgia, serif; pointer-events: none; }
                #demo-card strong { font-size: 66px; letter-spacing: -.05em; }
                #demo-card span { font: 500 27px Arial, sans-serif; }
                #demo-card small { font: 500 17px Arial, sans-serif; color: #b6d2c8; }
            """)
            page.evaluate("""() => {
                const caption=document.createElement('div'); caption.id='demo-caption';
                caption.textContent='SourceCheck · local invoice evidence review'; document.body.append(caption);
                const card=document.createElement('div'); card.id='demo-card';
                card.innerHTML='<strong>SourceCheck</strong><span>Did the invoice survive import?</span><small>Owned fixture · actual Mustang importer</small>';
                document.body.append(card);
            }""")
            page.wait_for_timeout(2400)
            page.locator("#demo-card").evaluate("el => el.remove()")

            cue(page, "1 / Add the original invoice", ".create-panel", 1.1)
            page.locator('input[name="title"]').fill("Owned invoice demo")
            page.locator('input[name="source"]').set_input_files(str(ROOT / "fixtures/owned-minimal-cii.xml"))
            page.wait_for_timeout(850)
            page.get_by_role("button", name="Create case").click()
            page.locator("#case-workspace").wait_for(state="visible")

            cue(page, "2 / Run the real Mustang 2.26 importer", "#run-form", 1.1)
            page.locator('#run-form select[name="version"]').select_option("2.26.0")
            page.get_by_role("button", name="Run comparison").click()
            page.locator("#findings-list .finding-row").first.wait_for()
            cue(page, "Original XML and actual importer output, side by side", "#run-workspace", 2.0)
            page.get_by_role("button", name="Buyer order reference").click()
            cue(page, "Trace the buyer order to both exact values", "#finding-detail", 2.2)

            cue(page, "3 / Record a review decision", "#review-form", 0.8)
            page.locator('#review-form input[name="reviewer"]').fill("Demo reviewer")
            page.locator('#review-form select[name="disposition"]').select_option("accepted_transformation")
            page.locator('#review-form textarea[name="reason"]').fill("Source and importer order references agree.")
            page.get_by_role("button", name="Record decision").click()
            page.wait_for_timeout(700)
            cue(page, "Save the reviewed run as a reference", "#reference-btn", 0.8)
            page.once("dialog", lambda dialog: dialog.accept("Demo reviewer"))
            page.get_by_role("button", name="Save reviewed reference").click()
            page.wait_for_timeout(850)

            authored = session / "constructed-export.json"
            authored.write_text(json.dumps({
                "number": "SC-OWNED-001", "issue_date": "2026-09-24", "currency": "EUR",
                "lines": [{"id": "1", "name": "Review service", "quantity": "1", "price": "10.00"}],
            }), encoding="utf-8")
            cue(page, "4 / Compare a constructed upload missing the order reference", "#run-form", 1.3)
            page.locator("#mode").select_option("uploaded_json")
            page.locator('input[name="destination"]').set_input_files(str(authored))
            page.locator('textarea[name="coverage_contract"]').fill(json.dumps({
                "reviewed": True, "field_coverage": {"buyer_order": "complete"},
            }))
            page.locator("#previous-select").select_option(index=1)
            before = page.locator("#run-title").inner_text()
            page.get_by_role("button", name="Run comparison").click()
            page.wait_for_function("old => document.querySelector('#run-title')?.textContent !== old", arg=before)
            page.get_by_role("button", name="Buyer order reference").click()
            assert "missing value" in page.locator("#finding-detail").inner_text()
            cue(page, "The missing value is supported by explicit complete coverage", "#finding-detail", 2.3)
            cue(page, "5 / Export a verifiable report", "#export-btn", 0.8)
            with page.expect_download() as pending:
                page.get_by_role("button", name="Export report").click()
            pending.value.save_as(str(session / "demo-report.zip"))
            page.wait_for_timeout(1200)
            page.evaluate("""() => {
                const card=document.createElement('div'); card.id='demo-card';
                card.innerHTML='<strong>SourceCheck</strong><span>Inspect · review · rerun · export</span><small>Real Mustang run + labeled constructed export · local MVP</small>';
                document.body.append(card);
            }""")
            page.wait_for_timeout(2600)
            if errors:
                raise RuntimeError(f"Browser errors during demo: {errors}")
            raw_video = page.video.path()
            context.close()
            browser.close()
            print(json.dumps({"raw_video": raw_video, "session": str(session), "browser_errors": errors}))
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
