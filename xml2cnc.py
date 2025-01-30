"""
xml2cnc.py

Created 14 December 2020 by Michael Hess II

This script uses the music21 module to parse a musicxml file, and then converts it into G-code
to "play" on a CNC machine. The score should have 3 single-voice parts, and the resulting
G-code assumes a 3-axis CNC machine.
"""

import music21 as m21
from math import sqrt

xml_file = "Hark2.musicxml"             # musicxml file to read
nc_file = "hark2.nc"                    # Output file
speed_per_Hz = 66/440                   # Frequency-feedrate conversion factor
xmin, ymin, zmin = 0, 0, -35            # Limits of CNC axes
xmax, ymax, zmax = 250, 100, 0
xstart, ystart, zstart = xmin, ymin, zmax
tempo = 115                             # Tempo in quarter notes per minute
repeat_gap = 0.01                       # Space in seconds between repeated notes in same voice
fill_frac = 0.95                   
shortest_duration = repeat_gap/60*tempo # Default shortest duration is measured in quarter notes

def xml_to_list(xml_data):
    """Function to convert a parsed musicxml file into a list containing the notes
    in each part"""
    xml_list = []
    global shortest_duration
    print("Parsing musicxml file...\n")
    for part in xml_data.parts:
    
        part_list = []

        for note in part.flat.notesAndRests:
            start = note.offset
            duration = note.quarterLength
            if note.isNote:
                pitch = note.pitch.frequency
                if len(part_list) > 0 and pitch == part_list[-1][2]:
                    #If notes are repeated, shorten previous note and add filler note
                    #of slightly lower frequency
                    part_list[-1][1] -= repeat_gap
                    filler = [part_list[-1][0]+part_list[-1][1], repeat_gap, pitch*fill_frac]
                    part_list.append(filler)
            else: pitch = 0
            part_list.append([start, duration, pitch])
            if duration < shortest_duration: shortest_duration = duration

        xml_list.append(part_list)
                
    return xml_list

def list_to_timewise(xml_list, tempo, min_duration):
    """Convert notes and durations to frequency at each time step"""
    timewise_list = []
    
    total_time = (xml_list[0][-1][0] + xml_list[0][-1][1]) / tempo * 60
    time_step = min_duration / tempo * 60
    step_count = int(total_time/time_step)
    current_beat = 0
    print("Sorting notes...\n")
    for step in range(step_count):
        voice_list = []
        for voice in xml_list:
            if voice[0][0] + voice[0][1] <= current_beat:
                voice.pop(0)
            voice_list.append(voice[0][2])
        voices_and_time = [voice_list, time_step]
        if step > 0 and voice_list == timewise_list[-1][0]:
            timewise_list[-1][-1] += voices_and_time[1]
        else: timewise_list.append(voices_and_time)
        current_beat += min_duration

    return timewise_list
            
def timewise_to_file(timewise_list, nc_file):
    """Convert list to G-code file"""
    global speed_per_Hz
    file = open(nc_file, 'w')
    print("Creating G-code")
    file.write("G90 G21\nG0 X0 Y0 Z0\nG90\nG04 P2\n")
    x, y, z = xstart, ystart, zstart
    xdir, ydir, zdir = 1, 1, 1
    
    for item in timewise_list:
        freq_eff = sqrt(sum([x**2 for x in item[0]]))
        feedrate = round(freq_eff*speed_per_Hz, 3)
        dx = item[0][0]*speed_per_Hz*item[1]/60
        if x+dx*xdir > xmax or x+dx*xdir < xmin: xdir *= -1  #Switch directions if near limits
        x += round(dx*xdir, 3)
        dy = item[0][1]*speed_per_Hz*item[1]/60
        if y+dy*ydir > ymax or y+dy*ydir < ymin: ydir *= -1  #Switch directions if near limits
        y += round(dy*ydir, 3)
        dz = item[0][2]*speed_per_Hz*item[1]/60
        if z+dz*zdir > zmax or z+dz*zdir < zmin: zdir *= -1  #Switch directions if near limits
        z += round(dz*zdir, 3)
        if [dx, dy, dz] == [0,0,0]:
            file.write("G04 P{}\n".format(item[1]))
        #file_text = "G01 X{} Y{} Z{} F{}".format(item[0][0], item[0][1], item[0][2], feedrate)
        else:
            file.write("G01 X{} Y{} Z{} F{}\n".format(x, y, z, feedrate))
    file.write("M02")        
    file.close()
    print("G-code file created: ", nc_file, "\n")
        
        

xml_data = m21.converter.parse(xml_file).stripTies(retainContainers=False)
xml_list = xml_to_list(xml_data)
timewise_list = list_to_timewise(xml_list, tempo, shortest_duration)
timewise_to_file(timewise_list, nc_file)
