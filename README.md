# HackathonJan2023

Make a Terminal UI application for plotting data from CSVs.

## Run
- Create a python environment and `pip install -r requirements.txt`
  - As of 1/10/23, rich-pixels has conflict and installs older textual. So need to also run `pip install -U textual` after.
- Run `python csv_plotter.py <root_directory>`

![screenshot](screenshot.png)

## About

- Mainly explored the capabilities of [Textual](https://textual.textualize.io)
  - Used capabilities
    - Directory tree
    - Data tables
    - Buttons
    - Key Bindings
    - CSS Layout
    - AutoComplete for inputs [textual-autocomplete](https://github.com/darrenburns/textual-autocomplete)
    - Error tracebacks from Rich
- Issues
  - Tried various plotting methods to make plots.
    - plot image using [rich-pixels](https://github.com/darrenburns/rich-pixels)
      - use any plotting library like [PlotlyExpress](https://plotly.com/graphing-libraries/) to generate plot image file first, then render the image.
      - **Con:** RichPixels is only for very low res (1 char = 1 pixel)
    - asci plotting modules
      - [plotext](https://github.com/piccolomo/plotext)
      - [plotille](https://github.com/tammoippen/plotille)
      - **Con:** not as fully featured
      - **Con:** going with fixed size for now, don't know how to autosize
      - **Con:** can't get the colors to work, I might be doing something wrong
    - Note: Textual is planning proper plotting and image support in the future but release TBD
  - DataTable can only support small CSV datasets in memory (< 1MB). Need to be efficient about it.  
- Future 
  - Support larger datasets.
  - Try adding a loading screen using these Textual capabilities.
      - Screens
      - Animation
  - Try replacing rich-pixel with [SIXEL](https://github.com/saitoha/libsixel) for higher res images.
  - Add more plotting settings/smarts.


Hey, I also just found out someone made a terminal UI for Jupyter notebooks called [euporie](https://github.com/joouha/euporie)
