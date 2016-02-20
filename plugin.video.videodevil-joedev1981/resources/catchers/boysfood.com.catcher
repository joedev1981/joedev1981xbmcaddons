########################################################
#                Boysfood VideoCatcher                 #
########################################################
url=%s
########################################################
target=href="([^"]+)"> mp4</a>
actions=decode(match)
extension=wmv
quality=standard
priority=1
########################################################
target=file: '(http[^']+)'
extension=wmv
quality=standard
priority=1
########################################################
target=<div id="xmoov-flv-player_va">\s+<iframe(?:[^"]+"){0,4}\s*src="([^"]+)"
priority=-1
type=redirect
########################################################
url=%s
########################################################
# pornhost
target=file: '([^']+)'
extension=wmv
quality=fallback
priority=-1
########################################################
target=link_url":"(http%3A%2F%2Fwww.pornhub.com[^"]+)"
actions=unquote(match)
priority=-2
type=forward
########################################################
target=<param name="flashvars" value="main_url=([^&]+.html)%3Fembed%3Dview&
actions=unquote(match)
priority=-2
type=redirect
########################################################
url=%s
########################################################
target=srv': '([^']+)',\s+'file': '([^']+flv)',
actions=join(/key=, match, group2)
quality=standard
########################################################
target=file': '([^']+.flv[^']+)'
actions=unquote(match)
quality=standard
########################################################
