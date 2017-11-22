# hooner 
Hooner is a cross-platform audio file player and media manager, being built on Python 3.


### Concept
It is very much pre-alpha right now; we're just getting started. Planned features will include:
* A solid player, with the ability to create playlists on the fly
* A media manager and player that handles Album Artist data by default
* A media manager capabale of maintaining multiple libraries, allowing for
  * Cloud-based libraries (Amazon Music, AWS, Google Music, etc)
  * Parallel hi-def/lower-def libraries (think: home library synced with smartphone)
* Assistant for smart metatdata correction, fixing annoyances like
  * _Beastie Boys_ versus _The Beastie Boys_
  * _and_ versus _&_ versus _+_
  * Albums missing Album Artist, with multiple track artists due to guest performers
  
 ### Latest update 22 Nov 2017
 * Search box functional and labeled
 * First run creates preference file
 * First run brings up directory picker to scan for library
 * Can double-click a track to play it 
 
 ### Prerequisites/Installation
 
 Hooner is written for Python 3, so you'll need that if you don't have it. Get it [here](https://www.python.org/downloads/)
 
 For now, you'll also need two non-standard libararies, [mutagen](https://mutagen.readthedocs.io/en/latest/index.html) 
 and [pygame](http://www.pygame.org). You should be able to install them using pip:
 ```
 pip3 install mutagen
 pip3 install pygame
 ```
 
 ...or use your prefered method for installing python libraries.
 
 Once your prerequisites are installed, you can perform a git clone of the project,
 or simply download a zipfile [here](https://github.com/doglikegroove/hooner/archive/master.zip)
 
 Then simply run `python3 hooner.py`
