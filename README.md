# hmc
Hypha's media centre

Dependency:


1. mpv (only tested with latest version built from https://github.com/mpv-player/mpv-build; earlier version without eabling ffmpeg options might result in some urls not playing properly; earlier versions should exist in the repositoriy of recent versions of Linux)

2. Need latest version of subliminal which you can get it from https://github.com/Diaoul/subliminal/tree/master/subliminal

3. Note: To install subliminal,  first git clone https://github.com/Diaoul/subliminal.git, then do "sudo python setup.py install" in the directory that it is installed.
      

How to:
Method 1: run python hmc.py from where the file is located in 
Method 2: create a symlink to $PATH from where hmc.py is located in.

Command:

1. ".." go to previous directory

2. chosse an index to play corresponding audio/video file, e.g. simply type 4 to play num 4 in the list

3. if the file(s) is a film, use trailer index to play the trailer of the film, e.g. trailer 4

4. play a range of media files by doing 
   1,4,5 to play file 1,4,5; 
   or 1-5 to play from file 1 to 5; 
   or 1- to play from file 1 to the end
   or 5- to play from 1 to 5 in reverse

5. use shuffle (range) or (range) shuffle to play in random order

6. to play a range of trailers of films, use trailer(range) or (range)trailer

7. to play a range of trailers with shuffle, add shuffle before or after command 5.

8. to get information of a film from rotten tomato, do info index.
