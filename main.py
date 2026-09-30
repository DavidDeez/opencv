import os
import asyncio
from playwright.async_api import async_playwright
from vision import annotate_ui_elements
from agent import AgentBrain

async def run_test():
    print("Starting Advanced Agentic Vision workflow...")
    agent = AgentBrain()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = f"file://{current_dir}/dummy_ui.html"
        print(f"Loading {html_path}...")
        await page.goto(html_path)
        await page.wait_for_timeout(1000)
        
        screenshot_path = os.path.join(current_dir, "screenshot_raw.png")
        annotated_path = os.path.join(current_dir, "screenshot_annotated.png")
        await page.screenshot(path=screenshot_path)
        
        # Initial OpenCV parameters
        cv_params = {'canny_low': 60, 'canny_high': 150}
        max_retries = 3
        goal = "Click the Hidden Admin Login button"
        
        for attempt in range(max_retries):
            print(f"\n--- LOOP ITERATION {attempt + 1} ---")
            
            # 1. PERCEPTION
            print(f"OpenCV 5: Running with parameters {cv_params}")
            elements = annotate_ui_elements(screenshot_path, annotated_path, cv_params['canny_low'], cv_params['canny_high'])
            print(f"OpenCV found {len(elements)} elements.")
            
            # 2. DECISION
            decision = agent.get_next_action(goal, elements, cv_params)
            print(f"Agent Decision Output: {decision}")
            
            # 3. ACTION / ADAPTATION
            if decision.get('action') == 'tune_vision':
                print(f"--> AGENTIC ADAPTATION: Agent is tuning OpenCV parameters! Re-running perception...")
                cv_params['canny_low'] = decision.get('canny_low', 10)
                cv_params['canny_high'] = decision.get('canny_high', 50)
                # Loop continues, re-running OpenCV on the same screenshot with new params
                continue
                
            elif decision.get('action') in ['click', 'type']:
                target_el = next((el for el in elements if el['id'] == decision.get('element_id')), None)
                if target_el:
                    click_x = target_el['x'] + 5
                    click_y = target_el['y'] + 5
                    print(f"--> ACTION: Executing Playwright interaction at ({click_x}, {click_y})")
                    await page.mouse.click(click_x, click_y)
                    if decision.get('action') == 'type':
                        await page.keyboard.type(decision.get('text', ''))
                break
            else:
                print("Agent finished or returned unknown action.")
                break

        await page.wait_for_timeout(1000)
        await browser.close()
        print("\nWorkflow complete! The loop successfully closed.")

if __name__ == "__main__":
    asyncio.run(run_test())
