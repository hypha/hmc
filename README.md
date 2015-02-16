# hmc
Hypha's media centre

Installation:
run "git clone https://github.com/hypha/hmc.git" in the terminal. (Assuming you have git, otherwise, sudo apt-get install git)

Dependency:
1. System dependencies: pip, mpv, python-dev.
Install by typing "sudo install pip mpv python-dev"

Note:  mpv (only tested with latest version built from https://github.com/mpv-player/mpv-build; earlier version without eabling ffmpeg options might result in some urls not playing properly; earlier versions should exist in the repositoriy of recent versions of Linux)

2. Python libraries: IMDbPY, rottentomatoes, subliminal.
2.1. "cd hmc/" to go inside the directory where you cloned the files. 
2.2. Install python dependencies by typing "sudo pip install -r requirement.txt" 


How to:
Method 1: run "python hmc.py" from where the file hmc.py is located in.
Method 2: create a symlink from hmc.py to any of $PATH (to check, do "echo $PATH),e.g. "ln -s ~/hmc/hmc.py /usr/local/bin". Then run "hmc.py" from any directory.

Command:

1. ".." go to previous directory

2. type in "play" followed by an index to play corresponding audio/video file. "play is implied if one directly types in an index, e.g. simply type 4 to play num 4 in the list; 

3. if the file(s) is a film, use trailer index to play the trailer of the film, e.g. trailer 4

4. play a range of media files by doing (play):
   1,4,5 to play file 1,4,5;
   or 1-5 to play from file 1 to 5; 
   or 1- to play from file 1 to the end 
   or 5- to play from 1 to 5 in reverse

5. use shuffle range-of-index to play in random order

6. to play a range of trailers of films, use trailer range-of-index

7. to play a range of trailers with shuffle, add shuffle before command 6

8. to play all media files, type "play all" or simply "all". Add "shuffle" before this to play in random order

9. to play all trailers of films, type in '(play) trailer all"; add "shuffle" before to play in random order

10. to get information of a film, do info index. Then you will see an imdb summary of the film alongside its rotten tomato scores.
