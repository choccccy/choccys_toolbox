'''
choccys_toolbox.ui
just a collection of choccy's doodads and thingies
'''


# List of characters that will be displayed, in order, by the throbber
THROBBER_GFX = ["|", "/", "-", "-", "\\"]
#THROBBER_GFX = ["◢", "◣", "◤", "◥"]


async def throbber(frame_time: float=0.15):
    '''
    prints a spinning throbber with a frame time as argument
    '''
    import asyncio

    while True:
        for x in THROBBER_GFX:
            print
            print(f" [{x}]", end="\r", flush=True) # print graphics
            await asyncio.sleep(frame_time)        # delay