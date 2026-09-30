import json
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

class AgentBrain:
    def __init__(self):
        try:
            self.bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
            self.bedrock.list_foundation_models() 
            self.use_mock = False
        except Exception:
            self.use_mock = True

    def get_next_action(self, goal_prompt, ui_elements, current_params):
        prompt = f"""
        Goal: {goal_prompt}
        
        Current OpenCV Parameters:
        - Canny Low Threshold: {current_params['canny_low']}
        - Canny High Threshold: {current_params['canny_high']}
        
        Available UI Elements Detected:
        {json.dumps(ui_elements, indent=2)}
        
        INSTRUCTIONS:
        If you see the element you need, respond with a click or type action.
        CRITICAL: If the element is missing (e.g., low contrast buttons may be missed by the current OpenCV thresholds), you MUST tune the OpenCV parameters by lowering the Canny thresholds to increase sensitivity.

        Respond ONLY in valid JSON format using one of these schemas:
        1. {{"action": "tune_vision", "canny_low": 10, "canny_high": 50, "reason": "Need higher sensitivity for faint elements"}}
        2. {{"action": "type", "element_id": 1, "text": "agent@opencv.org"}}
        3. {{"action": "click", "element_id": 3}}
        """
        
        print("\n[Brain] Agent is evaluating visual data...")
        
        if self.use_mock:
            return self._mock_decision(ui_elements, current_params, goal_prompt)
            
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ]
            })
            
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=body
            )
            response_body = json.loads(response.get('body').read())
            return json.loads(response_body['content'][0]['text'])
            
        except Exception as e:
            print(f"[Brain] AWS Bedrock error: {e}")
            return self._mock_decision(ui_elements, current_params, goal_prompt)

    def _mock_decision(self, ui_elements, current_params, goal_prompt):
        import time
        time.sleep(1.5)
        
        # If the agent is looking for the "Hidden Admin Login" but Canny thresholds are high, it won't find it.
        # It intelligently decides to lower the thresholds.
        if "Admin" in goal_prompt and current_params['canny_low'] > 20:
            print("[Brain] Reason: I do not see the Hidden Admin Login. The contrast might be too low for the current edge detector settings.")
            return {
                "action": "tune_vision", 
                "canny_low": 10, 
                "canny_high": 50, 
                "reason": "Lowering Canny thresholds to detect faint UI elements."
            }
            
        # If the thresholds were lowered, it should now see more elements. We mock picking the last one.
        if "Admin" in goal_prompt and current_params['canny_low'] <= 20:
            print("[Brain] Reason: I see the new faint element that appeared after tuning OpenCV!")
            target_id = ui_elements[-1]['id'] if ui_elements else 1
            return {"action": "click", "element_id": target_id}
            
        return {"action": "done"}
