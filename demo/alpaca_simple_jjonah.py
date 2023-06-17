'''
Advanced demo of a Discord chatbot with an LLM back end

Demonstrates async processing via ogbujipt.async_helper & Discord API integration.
Users can make an LLM request by @mentioning the bot by its user ID

Note: This is a simple demo, which doesn't do any client-side job management,
so for example if a request is sent, and a second comes in before it has completed,
only the latter will complete.

You need access to an OpenAI-like service. Default assumption is that you
have a self-hosted framework such as llama-cpp-python or text-generation-webui
running. Say it's at my-llm-host:8000, you can do:

Prerequisites: python-dotenv discord.py

You also need to make sure Python has root SSL certificates installed
On Mac this is via double-clicking `Install Certificates.command`

You also need to have a file, just named `.env`, in the same directory,
with contents such as:

```env
DISCORD_TOKEN={your-bot-token}
LLM_HOST=http://my-llm-host
LLM_PORT=8000
LLM_TEMP=0.5
```

Then to launch the bot:

```shell
python demo/alpaca_simple_qa_discord.py
```
'''

import os
import asyncio

import discord
from dotenv import load_dotenv

from langchain import OpenAI

from ogbujipt.config import openai_emulation
from ogbujipt.async_helper import schedule_llm_call
from ogbujipt.model_style.alpaca import prep_instru_inputs, ALPACA_PROMPT_TMPL

# Enable all standard intents, plus message content
# The bot app you set up on Discord will require this intent (Bot tab)
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"J. Jonah Jameson is ready. Connected to {len(client.guilds)} guild(s).\n")

async def send_llm_msg(prompt, msg):
    '''
    Schedule the LLM request
    '''
    
    instru_inputs = ALPACA_PROMPT_TMPL.format(
        instru_inputs=prep_instru_inputs(prompt, inputs=msg))
    print('=' * 80)
    print('PROMPT:')
    print(prompt)

    response = await schedule_llm_call(llm, instru_inputs)
    print('\nRESPONSE FROM LLM:\n', response)
    return response


def cut_out_string(input_string, string_to_cut):
    output_string = input_string.partition(string_to_cut)
    return output_string[0] + output_string[2]


# List of characters that will be displayed, in order, by the throbber
#THROBBER_GFX = ["|", "/", "-", "-", "\\"]
THROBBER_GFX = ["◢", "◣", "◤", "◥"]


async def throbber(frame_time: float=0.15):
    '''
    prints a spinning throbber with a frame time as argument
    '''
    while True:
        for x in THROBBER_GFX:
            print
            print(f" [{x}]", end="\r", flush=True) # print graphics
            await asyncio.sleep(frame_time)        # delay


@client.event
async def on_message(ctx):
    # Ignore the bot's own messages & respond only to @mentions
    # The client.user.id check creens out @everyone & @here pings
    # FIXME: Better content check—what if the bot's id is a common word?
    if ctx.author == client.user \
            or not client.user.mentioned_in(ctx) \
            or str(client.user.id) not in ctx.content:
        return

    # Assumes a single mention, for simplicity. If there are multiple,
    # All but the first will just be bundled over to the LLM
    mention_str = f'<@{client.user.id}>'
    clean_msg = cut_out_string(ctx.content, mention_str)

    prompt = 'quip as if you are the character \'J. Jonah Jameson\' from Spider-Man, then type out the edited text as requested, in quotes.'

    # Show the prompt if the user types [show_prompt] anywhere in the message
    verbose_flag = '[show_prompt]'
    if verbose_flag in clean_msg:
        clean_msg = cut_out_string(clean_msg, verbose_flag)
        await ctx.channel.send(f'`{prompt}`')

    # Send message containing throbber:
    msg = await ctx.channel.send('<a:oori_throbber:1119445227732742265>')

    tasks = [
        asyncio.create_task(send_llm_msg(prompt, clean_msg)), 
        asyncio.create_task(throbber())
        ]

    # run FIRST task until completed
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED
        )

    response = next(iter(done)).result()
    for t in pending:
        t.cancel()

    await msg.edit(content=response)


def main():
    global llm  # Ick! Ideally should be better scope/context controlled

    load_dotenv()  # From .env file
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    LLM_HOST = os.getenv('LLM_HOST')
    LLM_PORT = os.getenv('LLM_PORT')
    LLM_TEMP = os.getenv('LLM_TEMP')

    # Set up API connector
    openai_emulation(host=LLM_HOST, port=LLM_PORT)
    llm = OpenAI(temperature=LLM_TEMP)

    # launch Discord client event loop
    client.run(DISCORD_TOKEN)


if __name__ == '__main__':
    # Entry point protects against multiple launching of the overall program
    # when a child process imports this
    # viz https://docs.python.org/3/library/multiprocessing.html#multiprocessing-safe-main-import
    main()
