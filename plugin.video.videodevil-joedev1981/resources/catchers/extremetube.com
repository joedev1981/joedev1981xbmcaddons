########################################################
#               Extremetube VideoCatcher               #
########################################################
url=%s
header=Cookie|age_verified=1
########################################################
target=flashvars" value=".*video_url=(http[^']+[.](mp4|flv)[^&]+)
actions=unquote(match)
quality=standard
########################################################
