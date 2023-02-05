#IMPORT FROM BUILT-IN LIBRARIES
import os
import asyncio

#IMPORT FROM THIRD-PARTY LIBRARIES
import openai

#IMPORT FROM PROJECT SETTINGS
from settings import OPENAI_MODEL, OPENAI_DEFAULT_TEMPERATURE, OPENAI_CUSTOM_BASE_PROMPT, get_max_tokens

class ChatGPT:

    async def ask(prompt: str = "Who was the first president of the united states?", user: str = "User", temperature: int = OPENAI_DEFAULT_TEMPERATURE) -> str:

        openai_prompt = (
                OPENAI_CUSTOM_BASE_PROMPT
                + user
                + ": "
                + prompt
                + "\nChatGPT:"
            )

        max_tokens = await get_max_tokens(openai_prompt)

        response = await openai.Completion.acreate(        
            model=OPENAI_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt=openai_prompt,
        )
        reply = response.choices[0].text.rstrip("<|im_end|>")
        return response

if __name__ == "__main__":
    asyncio.run(ChatGPT.ask())