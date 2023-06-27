'''
choccys_toolbox.ui
just a collection of choccy's doodads and thingies
'''

import asyncio

# List of characters that will be displayed, in order, by the throbber
#THROBBER_GFX = ["|", "/", "-", "-", "\\"]
THROBBER_GFX = ["◢", "◣", "◤", "◥"]


async def console_throbber(frame_time: float=0.15):
    '''
    Prints a spinning throbber to console with a frame time as argument
    '''
    # Loop forever (until cancelled)
    while True:
        # cycle next frame
        for frame in THROBBER_GFX:
            # print frame
            print(f" [{frame}]", end="\r", flush=True)
            # sleep for frame-time
            await asyncio.sleep(frame_time)