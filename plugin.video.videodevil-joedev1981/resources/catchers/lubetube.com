########################################################
#                 Pornhub VideoCatcher                 #
########################################################
url=%s
startRE=<div id="videocontent">
#stopRE=<div class="banner-container
########################################################
target=(playlist_flow_player_flv.php\?vid\=[0-9]*)
build=http://lubetube.com/%s&bitrate=hd
type=forward
########################################################
url=%s
########################################################
target=url="([^"]+)"
quality=standard
########################################################