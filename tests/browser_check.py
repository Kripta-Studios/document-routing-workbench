"""Live local browser smoke. Requires playwright and a system Chrome installation."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sourcecheck.export import verify_export
URL="http://127.0.0.1:8770/"
CHROME=Path("C:/Program Files/Google/Chrome/Application/chrome.exe")

def inspect(page,label):
    result=page.evaluate("""() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,zoom:devicePixelRatio,clipped:[...document.querySelectorAll('button,input,select,textarea')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.left<0||r.right>innerWidth+2}).map(e=>e.id||e.name||e.textContent.slice(0,20)),overflow:[...document.querySelectorAll('*')].filter(e=>e.scrollWidth>e.clientWidth+10).slice(0,15).map(e=>({tag:e.tagName,id:e.id,class:e.className,right:Math.round(e.getBoundingClientRect().right),scroll:e.scrollWidth,client:e.clientWidth,overflow:getComputedStyle(e).overflowX}))})""")
    assert result["scroll"]<=result["width"]+2,(label,result)
    assert not result["clipped"],(label,result)
    return {"label":label,**result}

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,executable_path=str(CHROME),args=["--no-sandbox"])
    context=browser.new_context(viewport={"width":1280,"height":900},accept_downloads=True)
    page=context.new_page()
    errors=[]
    page.on("pageerror",lambda error:errors.append(str(error)))
    page.goto(URL)
    page.locator('input[name="title"]').fill("Browser owned fixture")
    page.locator('input[name="source"]').set_input_files(str(ROOT/"fixtures/owned-minimal-cii.xml"))
    page.get_by_role("button",name="Create case").click()
    page.locator("#case-workspace").wait_for(state="visible")
    page.get_by_role("button",name="Run comparison").click()
    page.locator("#findings-list .finding-row").first.wait_for()
    page.get_by_role("button",name="Buyer order reference").click()
    assert "PO-OWNED-9" in page.locator("#finding-detail").inner_text()
    page.locator('#review-form input[name="reviewer"]').fill("Browser tester")
    page.locator('#review-form select[name="disposition"]').select_option("accepted_transformation")
    page.locator('#review-form textarea[name="reason"]').fill("Original and captured order reference agree")
    page.get_by_role("button",name="Record decision").click()
    page.once("dialog",lambda dialog:dialog.accept("Browser tester"))
    page.get_by_role("button",name="Save reviewed reference").click()
    # Uploaded output without a reviewed field contract cannot establish absence.
    uploaded=ROOT/".runtime"/"browser-upload.json"
    uploaded.write_text(json.dumps({"number":"SC-OWNED-001","issue_date":"2026-09-24","currency":"EUR"}),encoding="utf-8")
    page.locator('#mode').select_option('uploaded_json')
    page.locator('input[name="destination"]').set_input_files(str(uploaded))
    page.get_by_role("button",name="Run comparison").click()
    page.wait_for_function("document.querySelector('#run-meta')?.textContent.includes('user_uploaded_unverified')")
    page.get_by_role("button",name="Buyer order reference").click()
    assert "outside complete observed coverage" in page.locator("#finding-detail").inner_text(),page.locator("#finding-detail").inner_text()
    assert "not checkable" in page.locator("#findings-list").inner_text().lower()
    page.locator('input[name="destination"]').set_input_files(str(uploaded))
    page.locator('textarea[name="coverage_contract"]').fill(json.dumps({"reviewed":True,"field_coverage":{"buyer_order":"complete"}}))
    before=page.locator('#run-title').inner_text()
    page.get_by_role("button",name="Run comparison").click()
    page.wait_for_function("old => document.querySelector('#run-title')?.textContent!==old",arg=before)
    page.get_by_role("button",name="Buyer order reference").click()
    assert "missing value" in page.locator("#finding-detail").inner_text()
    # A profile revision is visible in the next run's comparison warning.
    profile=json.loads(page.locator('#profile-json').input_value())
    profile['name']='Browser revised profile'
    page.locator('#profile-json').fill(json.dumps(profile))
    page.get_by_role("button",name="Preview changes").click()
    assert "affected check" in page.locator('#profile-preview').inner_text()
    page.get_by_role("button",name="Save new version").click()
    page.wait_for_function("document.querySelector('#notice')?.textContent.includes('Profile version 2 saved')")
    page.locator('#mode').select_option('mustang')
    page.locator('#run-form select[name="version"]').select_option("2.24.0")
    page.locator('#previous-select').select_option(index=3)
    assert page.locator('#previous-select').input_value()
    before=page.locator('#run-title').inner_text()
    page.get_by_role("button",name="Run comparison").click()
    page.wait_for_function("old => document.querySelector('#run-title')?.textContent!==old",arg=before)
    assert page.locator('#diff-panel').is_visible(),(page.locator('#notice').inner_text(),page.locator('#run-error').inner_text(),page.locator('#run-meta').inner_text())
    assert "Profile changed" in page.locator("#diff-panel").inner_text()
    with page.expect_download() as pending:
        page.get_by_role("button",name="Export report").click()
    downloaded=pending.value
    report=ROOT/".runtime"/"browser-report.zip"
    downloaded.save_as(str(report))
    assert verify_export(report)["ok"]
    page.locator("#notice").get_by_text("Export",exact=False).wait_for()
    screenshots=ROOT/".runtime"/"browser"
    screenshots.mkdir(parents=True,exist_ok=True)
    layouts=[]
    for width in (360,768,1280,1920):
        page.set_viewport_size({"width":width,"height":900})
        page.screenshot(path=str(screenshots/f"width-{width}.png"),full_page=True)
        layouts.append(inspect(page,f"width-{width}"))
    cdp=context.new_cdp_session(page)
    for factor in (1.25,2):
        cdp.send("Emulation.setDeviceMetricsOverride",{"width":round(1280/factor),"height":round(900/factor),"deviceScaleFactor":factor,"mobile":False})
        layouts.append(inspect(page,f"emulated-browser-zoom-{factor}"))
        page.screenshot(path=str(screenshots/f"zoom-{factor}.png"),full_page=True)
    cdp.send("Emulation.clearDeviceMetricsOverride")
    invalid=ROOT/".runtime"/"browser-invalid.json"
    invalid.write_text("{",encoding="utf-8")
    page.locator('#mode').select_option('uploaded_json')
    page.locator('input[name="destination"]').set_input_files(str(invalid))
    page.get_by_role("button",name="Run comparison").click()
    page.wait_for_function("document.querySelector('#run-error')?.textContent.includes('Expecting property name')")
    assert page.get_by_role("button",name="Retry as a new recorded run").is_visible()
    before=page.locator('#run-title').inner_text()
    page.get_by_role("button",name="Retry as a new recorded run").click()
    page.wait_for_function("old => document.querySelector('#run-title')?.textContent!==old",arg=before)
    assert page.locator('#run-error').is_visible()
    page.once("dialog",lambda dialog:dialog.accept())
    page.get_by_role("button",name="Delete case").click()
    page.locator("#case-workspace").wait_for(state="hidden")
    page.locator('input[name="title"]').fill("Owned hybrid PDF")
    page.locator('input[name="source"]').set_input_files(str(ROOT/"fixtures/owned-hybrid.pdf"))
    page.get_by_role("button",name="Create case").click()
    page.locator('#case-workspace').wait_for(state='visible')
    page.locator('#mode').select_option('mustang')
    page.get_by_role("button",name="Run comparison").click()
    page.locator('#source-view iframe').wait_for()
    assert 'Page 1 / 2' in page.locator('#page-indicator').inner_text()
    page.get_by_role('button',name='Next page').click()
    assert 'Page 2 / 2' in page.locator('#page-indicator').inner_text()
    page.get_by_role('button',name='Previous page').click()
    assert 'Page 1 / 2' in page.locator('#page-indicator').inner_text()
    page.once("dialog",lambda dialog:dialog.accept())
    page.get_by_role("button",name="Delete case").click()
    page.locator("#case-workspace").wait_for(state="hidden")
    page.locator('input[name="title"]').fill("Owned OCR image")
    page.locator('input[name="source"]').set_input_files(str(ROOT/"fixtures/owned-invoice.png"))
    page.get_by_role("button",name="Create case").click()
    page.locator('#case-workspace').wait_for(state='visible')
    page.locator('#mode').select_option('uploaded_json')
    page.locator('input[name="destination"]').set_input_files(str(uploaded))
    page.get_by_role("button",name="Run comparison").click()
    page.wait_for_function("document.querySelector('#run-meta')?.textContent.includes('user_uploaded_unverified')")
    page.locator('#source-view img').wait_for()
    page.wait_for_function("document.querySelector('#source-view img')?.complete")
    assert page.locator('#source-lines .source-line').count()>=4
    page.locator('#source-lines .source-line').first.click()
    assert page.locator('.ocr-box').is_visible()
    page.get_by_role('button',name='Zoom in').click()
    assert '125%' in page.locator('#zoom-label').inner_text()
    page.get_by_role('button',name='Fit').click()
    assert '100%' in page.locator('#zoom-label').inner_text()
    page.once("dialog",lambda dialog:dialog.accept())
    page.get_by_role("button",name="Delete case").click()
    page.locator("#case-workspace").wait_for(state="hidden")
    assert not errors,errors
    print(json.dumps({"workflow":"passed","layouts":layouts,"javascript_errors":errors,"screenshots":str(screenshots)},indent=2))
    browser.close()
