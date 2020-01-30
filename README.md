#pacman logs to charts

html ouput for display charts from pacman logs


#Usage

script.py "transaction started" "ALPM"
script.py "starting full system upgrade" "PACMAN"
script.py "upgraded python " "ALPM"

```
./script.py > /tmp/test.html & firefox /tmp/test.html
```
