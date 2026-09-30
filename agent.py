import json
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

class AgentBrain:
    def __init__(self):
        # Initialize AWS Bedrock Client for the hackathon
        try:
            self.bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
            # Check if credentials are valid by querying foundation models
            self.bedrock.list_foundation_models() 
            self.use_mock = False
        except Exception:
            self.use_mock = True

    def get_next_action(self, goal_prompt, ui_elements):
        """
        Sends the available UI elements to the LLM and asks it to pick an action.
        """
        prompt = f"""
        Goal: {goal_prompt}
        
        Available UI Elements (from OpenCV Perception):
        {json.dumps(ui_elements, indent=2)}
        
        Decide the next action based on the Goal. Respond ONLY in valid JSON format:
        {{"action": "type", "element_id": 1, "text": "agent@opencv.org"}}
        or 
        {{"action": "click", "element_id": 3}}
        """
        
        print("\n[Brain] Agent is thinking...")
        
        if self.use_mock:
            print("[Brain] (No AWS credentials found. Using local mock fallback for testing)")
            return self._mock_decision(ui_elements)
            
        try:
            # Real call to Amazon Bedrock (Claude 3 Haiku)
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
            # Parse the JSON out of Claude's text response
            return json.loads(response_body['content'][0]['text'])
            
        except Exception as e:
            print(f"[Brain] AWS Bedrock error (falling back to mock): {e}")
            return self._mock_decision(ui_elements)

    def _mock_decision(self, ui_elements):
        # Simple mock logic based on our dummy UI to prove the loop works
        import time
        time.sleep(1) # Simulate thinking latency
        
        # Pick the first element to type into
        for el in ui_elements:
            if el['id'] == 1:
                return {"action": "type", "element_id": 1, "text": "demo@aws.com"}
        return {"action": "done"}
