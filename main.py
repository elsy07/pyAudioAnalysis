# -*- coding: UTF-8 –*-
#!/usr/bin/env python2
import audioSegmentation as aS
import sh
import utilities

if __name__ == '__main__':


    # 输入音频文件
    audio = "/Users/nettech/Music/Logger/AM1053/20180302/08-00-00.m4a"
    keywords = [u"中科", u"虫草"]

    # 分开文件路径、文件名、后缀
    path, name, suffix = utilities.split(audio)
    print "文件路径: " + path + "\n文件名: " + name + "\n后缀: " + suffix
    print('--------------------------------')
    # m4a转换成mp3
    #mp3_audio = utilities.convert(audio)
    # 生成wav文件名和路径
    wav_audio = path + "/" + name + ".wav"
    print "wav文件路径预设为： " + wav_audio
    print('--------------------------------')
    # 批量文件路径下的mp3转wav
    #audioAnalysis.dirMp3toWavWrapper(path, 16000, 1)
    # hmm分段，并生成segment文件
    segFileName = path + "/" + name + ".segment"
    print "seg文件路径预设为： " + segFileName
    print('--------------------------------')
    #[flagsInd, classesAll, acc, CM] = aS.hmmSegmentation(wav_audio, "data/hmmRadioSM", segFileName, True, '')
    # 根据seg去除100秒以上的music
    cmd = "mkdir " + path + "/" + name
    sh.run(cmd)

    # 记录分段起止时间
    delimit_list = aS.segWAV(wav_audio)

    # 读取转写结果
    for i in (0, len(delimit_list)-1):
        records_list = utilities.load(path + "/" + name + "/" + name + "_" + delimit_list[i][0] + "-" + delimit_list[i][1] + ".json")

        # 找到关键词出现的时间
        feedback = utilities.feedback(records_list, keywords)
        print "检查结果：" + str(feedback)



