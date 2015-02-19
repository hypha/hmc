# hmc
Hypha's media centre

Installation:

In the terminal run (Assuming you have git, otherwise, sudo apt-get install git):
		
	git clone https://github.com/hypha/hmc.git




Dependency:

1.System dependencies: python-pip, mpv, python-dev.

Install by typing 

	sudo apt-get install python-pip mpv python-dev

  Note:  mpv (only tested with latest version built from https://github.com/mpv-player/mpv-build; earlier version without eabling ffmpeg options might result in some urls not playing properly; earlier versions should exist in the repositoriy of recent versions of Linux)


2.Python libraries: IMDbPY, rottentomatoes, guessit, tabulate, pytvdbapi

   2.1.Go inside the directory where you cloned the files:
    
    cd hmc/

   2.2. Install python dependencies by typing 
   
   	sudo pip install -r requirement.txt




How to run:

Method 1: From where the file hmc.py is located in, run:
	
	python hmc.py

Method 2: create a symlink from hmc.py to any of $PATH (to check, do "echo $PATH"),e.g. 
	
	ln -s ~/hmc/hmc.py /usr/local/bin/

Then run "hmc.py" from any directory.



Command

1.to go to previous directory, type: ..

2.to go to a listed directory, type in its corresponding number

3.to play media file No. 5, enter

	play 4 ; or 4

(play is implied if one directly types in an index of a media file

4.if media file No.4 is a film, play the trailer of the film by entering
	
	trailer 4

5.play a range of media files by doing (play):
   
	1,4,5 to play file 1,4,5
   
	1-5 to play from file 1 to 5; 
   	
	1- to play from file 1 to the end 

	5- to play from 1 to 5 in reverse
	
	all to play all media files in the directory

6.add "shuffle" in front of command 5 to play a range of files in random mode

7.add "trailer" in front of command 5 to play a range of trailers of films

8.add "shuffle trailer" in front of command 5 to trailers of films in random order

9.to get information of film or Series No.3, do 
	
	info 3

Then you will see an imdb summary of the film alongside its rotten tomato scores.
