# -*- coding: UTF-8 –*-
import utilities, os


# 调用jar语音转写
command1 = u"java -jar /Users/nettech/Music/iflytek20180517.jar "

command2= u"/Users/nettech/Music/logger3/Export/9/2018/ff4e7a66-58a7-11e8-a910-acbc32d112ef/"


for output_line in utilities.run_command(command1+command2):
    print output_line
