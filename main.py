import os
import asyncio
from playwright.async_api import async_playwright
from vision import annotate_ui_elements
from agent import AgentBrain

async def run_test():
    print("Starting browser...")
    agent = AgentBrain()
    
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
        
        # 1. PERCEPTION (Playwright -> OpenCV)
        screenshot_path = os.path.join(current_dir, "screenshot_raw.png")
        annotated_path = os.path.join(current_dir, "screenshot_annotated.png")
        
        print("\n--- STEP 1: PERCEPTION ---")
        await page.screenshot(path=screenshot_path)
        elements = annotate_ui_elements(screenshot_path, annotated_path)
        print(f"OpenCV found {len(elements)} interactable elements.")
        
        # 2. DECISION (AgentBrain / AWS Bedrock)
        print("\n--- STEP 2: DECISION ---")
        decision = agent.get_next_action("Login to the system", elements)
        print(f"Agent Decision Output: {decision}")
        
        # 3. ACTION (Playwright Execution)
        print("\n--- STEP 3: ACTION ---")
        target_el = next((el for el in elements if el['id'] == decision.get('element_id')), None)
        
        if target_el and decision.get('action') == 'type':
            # Add 10 to x,y to click inside the box instead of on the exact edge
            click_x = target_el['x'] + 10
            click_y = target_el['y'] + 10
            print(f"Executing: Typing '{decision['text']}' at screen coordinates ({click_x}, {click_y})")
            
            await page.mouse.click(click_x, click_y)
            await page.keyboard.type(decision['text'])
            
        elif target_el and decision.get('action') == 'click':
            click_x = target_el['x'] + 10
            click_y = target_el['y'] + 10
            print(f"Executing: Clicking at screen coordinates ({click_x}, {click_y})")
            await page.mouse.click(click_x, click_y)

        # Wait so we can see the result if we turn headless=False later
        await page.wait_for_timeout(2000)
        await browser.close()
        print("\nWorkflow complete! The loop successfully closed.")

if __name__ == "__main__":
    asyncio.run(run_test())
