from autogen import ConversableAgent

agent = ConversableAgent(
    name="TestAgent",
    system_message="You are a helpful assistant.",
    llm_config={
        "config_list": [
            {
                "model": "gpt-4o-mini",
                "base_url": "https://api.openai.com/v1",
                "api_key": "my_api_key_here",
                "api_type": "azure",
                "api_version": "2024-08-01-preview"
            }
        ],
        "temperature": 0
    }
)

response = agent.generate_reply(messages=[{"role": "user", "content": "What is Newton AI?"}])
print(response)
