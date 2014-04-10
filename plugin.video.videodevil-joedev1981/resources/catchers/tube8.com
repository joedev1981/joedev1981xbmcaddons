########################################################
#                 Pornhub VideoCatcher                 #
########################################################
url=%s
startRE=<div class="main-video-wrapper
stopRE=<div class="banner-container
########################################################
target="video_url":"([^"]+)"
actions=replace(match, \/, /)
dkey="video_title":"([^"]+)
quality=standard
priority=1
########################################################
target='videoUrl': '([^']+)'
quality=standard
priority=2
########################################################