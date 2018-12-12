#dbus-monitor "interface='org.freedesktop.Notifications'" | grep --line-buffered  "string"
dbus-monitor "interface='org.freedesktop.Notifications'" #| pcregrep -M "string \"\"\s*.*\s*string \"\""
