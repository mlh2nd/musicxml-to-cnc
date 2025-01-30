# musicxml-to-cnc
Convert musicxml files to g-code to play on a 3-axis CNC machine

## Usage
1. Install Python and [music21](https://www.music21.org/music21docs/). 
2. Use a music editing program to create a 3-voice score as shown. Each voice will be played by one of the motors of the CNC machine.

![Example score](Example/image.png)

3. Export your score in musicxml format.
4. In `xml2cnc.py`, change the input filename to match your musicxml file and the output filename to what you want the machine code to be saved as.
5. Run `xml2cnc.py`.
6. Run the ouput file on your CNC machine.

## Notes
* The code may require some tweaking to work properly on your machine.
* Even if it works, the `speed_per_Hz` variable may need adjustment for accurate pitch values.
* I have not tested this with all versions of music21.
