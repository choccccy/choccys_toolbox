'''
Advanced demo of a Discord chatbot with an LLM back end, flavored with a fictional character.

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
LLM_SUBSTYLE=ALPACA_INSTRUCT
LLM_TIMEOUT=60
```

Then to launch the bot:

```shell
python demo/alpaca_simple_qa_discord.py
```
'''

# Import standard libraries
import os
import asyncio

# Import discord.py for interaction with Discord API
import discord

# Import dotenv to load from .env file
from dotenv import load_dotenv
load_dotenv('demo/icebear.env') # eugh, presumes running from choccys_toolbox/

# Import from langchain for handling LLM management
from langchain import OpenAI

# Imports from OgbujiPT for handling LLM prompting
from ogbujipt.config import openai_emulation
from ogbujipt.async_helper import schedule_llm_call
from ogbujipt.model_style.alvic import make_prompt, sub_style

# Set up lookup table for different LLM prompting substyles
substyles = {
    'ALPACA': sub_style.ALPACA,
    'ALPACA_INSTRUCT': sub_style.ALPACA_INSTRUCT
    }

# Enable all standard intents, plus message content
# The bot app you set up on Discord will require this intent (Bot tab)
intents = discord.Intents.default()
intents.message_content = True

# Setting up a 'client' object that represents the bot
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    '''
    Print to console when bot successfully connects to Discord's API
    '''
    print(f"Ice Bear is ready. Connected to {len(client.guilds)} guild(s).\n")


async def send_llm_msg(msg, ctx):
    '''
    Schedule the LLM request
    Print prompt and response
    '''
    # Set up prompt
    prompt = 'Respond as if you are the character \'Ice Bear\' from \'We Bare Bears\''

    # Show the prompt if the user types [show_prompt] anywhere in the message
    verbose_flag = '[show_prompt]'
    if verbose_flag in msg:
        inter_msg = msg.partition(verbose_flag)
        msg = inter_msg[0] + inter_msg[2]
        await ctx.channel.send(f'`PROMPT: {prompt}`')
        await ctx.channel.send(f'`INPUT: {msg}`')

    # Format prompt for chosen substyle
    LLM_SUBSTYLE = os.getenv('LLM_SUBSTYLE')
    instru_inputs = make_prompt(
        prompt, 
        inputs=msg,
        sub=substyles[LLM_SUBSTYLE]
        )
    
    # Print prompt and user input to console
    print('=' * 80)
    print('PROMPT:')
    print(prompt)
    print('INPUT:')
    print(msg)

    # Call LLM
    response = await schedule_llm_call(llm, instru_inputs)

    # print LLM response to console
    print('' * 12, end='\r')
    print('RESPONSE FROM LLM:')
    print(response)

    # Return LLM response
    return response


async def throbber(frame_time: float=0.15):
    '''
    Prints a spinning throbber to console with specified frame time
    '''
    THROBBER_GFX = ["◢", "◣", "◤", "◥"]

    while True:                                        # Loop forever (until cancelled)
        for frame in THROBBER_GFX:                     # cycle next frame
            print(f" [{frame}]", end="\r", flush=True) # print frame
            await asyncio.sleep(frame_time)            # sleep for frame-time


@client.event
async def on_message(ctx):
    '''
    Message receipt and response
    '''
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
    inter_msg = ctx.content.partition(mention_str)
    clean_msg = inter_msg[0] + inter_msg[2]

    # Send message to discord containing throbber:
    msg = await ctx.channel.send('<a:oori_throbber:1119445227732742265>')

    # Collect task coroutines
    tasks = [
        asyncio.create_task(send_llm_msg(clean_msg, ctx)), 
        asyncio.create_task(throbber())
        ]

    # Run tasks until the first completes, or when TIMEOUT seconds occour
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT'))
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED, 
        timeout=LLM_TIMEOUT
        )

    # Cancel remaining tasks
    for tsk in pending:
        tsk.cancel()

    # Edit the discord message to be the LLM response
    if not done:
        print('LLM not responding!', end='\r')
        await msg.edit(content='`LLM not responding!`')
    else:
        response = next(iter(done)).result()
        await msg.edit(content=response)


def main():
    global llm  # Ick! Ideally should be better scope/context controlled

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