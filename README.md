# FreeCAD_AppImage_downloader
This python script downloads the latest FreeCAD AppImage from @realthunder FreeCAD branch, creates symlinks and sets the symlink to executable.

# Instalation
First do a git pull
``` bash
$ git clone https://github.com/byteofsoren/FreeCAD_AppImage_downloader.git
```
Then create a coppy of the file `config.conf` and name it `config.yaml`.
``` bash
$ cp config.conf config.yaml
```

Edit the file yaml file `config.yaml` and change the `my_github_api_token` to what token you have.
Now ewerything is all set.

# How to use
To use the tool to fetch FreeCAD from the realthunder realease page just run:
``` bash
$ python get_freecad.py
```
The program creates a new directory inside the repo called downloads and then downloads the AppImage in to it.
Then it sets the exeution rights for the file and then creates a symlike with the path  `~/.local/bin/freecad`.
This makes it possible to run the freecad from a terminal with just
``` bas
$ freecad
```
