import os
import asyncio
from playwright.async_api import async_playwright
from vision import annotate_ui_elements

async def run_test():
    print("Starting browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Load our local dummy UI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = f"file://{current_dir}/dummy_ui.html"
        print(f"Loading {html_path}...")
        await page.goto(html_path)
        
        # Wait a moment for rendering
        await page.wait_for_timeout(1000)
        
        # Take a screenshot (Perception Phase)
        screenshot_path = os.path.join(current_dir, "screenshot_raw.png")
        annotated_path = os.path.join(current_dir, "screenshot_annotated.png")
        
        print("Taking screenshot...")
        await page.screenshot(path=screenshot_path)
        
        await browser.close()
        
        # Pass to OpenCV (Vision Phase)
        print("Running OpenCV 5 vision analysis...")
        elements = annotate_ui_elements(screenshot_path, annotated_path)
        
        print(f"Found {len(elements)} interactable UI elements!")
        print(f"Saved annotated screenshot to: {annotated_path}")
        
        for el in elements:
            print(f"ID: {el['id']} | Position: ({el['x']}, {el['y']}) | Size: {el['w']}x{el['h']}")

if __name__ == "__main__":
    asyncio.run(run_test())
