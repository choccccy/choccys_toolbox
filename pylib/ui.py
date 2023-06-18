'''
choccys_toolbox.ui
just a collection of choccy's doodads and thingies
'''

import asyncio

# List of characters that will be displayed, in order, by the throbber
#THROBBER_GFX = ["|", "/", "-", "-", "\\"]
THROBBER_GFX = ["◢", "◣", "◤", "◥"]


async def throbber(frame_time: float=0.15):
    '''
    prints a spinning throbber with a frame time as argument
    '''

    while True:                                        # Loop forever (until cancelled)
        for frame in THROBBER_GFX:                     # cycle next frame
            print(f" [{frame}]", end="\r", flush=True) # print frame
            await asyncio.sleep(frame_time)            # sleep for frame-time