# -*- coding: UTF-8 –*-
#!/usr/bin/env python2
import audioSegmentation as aS
import os, datetime,time
import utilities
import audioAnalysis
import data
import jpype

if __name__ == '__main__':

    AdType = u"OA口播广告"
    RootDir = "/Users/nettech/Music/logger3/"


    # 查询到口播广告type的guid
    PlayPlanTypeGuid = data.QueryPlayPlanType(AdType)

    # 获取昨天的日期
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    print yesterday
    start = time.clock()
    playplanlist, count = data.GetPlayPlan(yesterday, PlayPlanTypeGuid)
    # program = data.SetAudioClipper(yesterday, playplanlist)
    MP3Files = data.QueryFilePath2(yesterday, count)

    for mp3 in MP3Files:
        Mp3File = RootDir + mp3["filepath"]
        print Mp3File
        # mp3转wav
        wav_audio = audioAnalysis.Mp3toWavWrapper(Mp3File, 16000, 1)
        # hmm分段，并生成segment文件
        segFileName = Mp3File.replace(".mp3", ".segment")
        [flagsInd, classesAll, acc, CM] = aS.hmmSegmentation(wav_audio, "data/hmmRadioSM", segFileName, False, '')
        print('---------------wav已分段-----------------')
        newdir = str(os.path.splitext(Mp3File)[0])
        print newdir
        os.mkdir(newdir)
        # 根据seg去除100秒以上的music、记录分段起止时间
        delimit_list = aS.segWAV(wav_audio)

        # 调用jar语音转写
        command = "java -jar /Users/nettech/Music/iflytek-Mac.jar 5af90cd2 6b047cf236ba6471aa851269eea6d779" + newdir
        for output_line in utilities.run_command(command):
            print output_line

        # 检查关键词
        keywords = mp3["keywords"].split("，")
        print keywords
        feedback = utilities.feedback(newdir, keywords)
        userdefinefeedbackmark = utilities.formateFeedback(feedback)
    elapsed = (time.clock() - start)
    print("Time used:", elapsed)








