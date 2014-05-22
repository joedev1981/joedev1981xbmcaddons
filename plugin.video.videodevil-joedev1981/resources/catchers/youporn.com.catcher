########################################################
#                 Youporn VideoCatcher                 #
########################################################
url=%s
startRE=currentVideo
########################################################
target=video_title'\s+:\s+"([^"]+)",
actions=replace(match, &amp;, &)|unquote(match)
type=dkey
priority=0
########################################################
target=var\s+encryptedQuality720URL\s+=\s+'([^']+)';
info=720p
quality=high
priority=1
########################################################
target=var\s+encryptedQuality480URL\s+=\s+'([^']+)';
info=480p
quality=standard
priority=2
########################################################
target=var\s+encryptedQuality240URL\s+=\s+'([^']+)';
info=240p
quality=low
priority=3
########################################################