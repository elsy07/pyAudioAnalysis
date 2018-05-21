# -*- coding: UTF-8 –*-
import json
import sys
import uuid

import numpy

import sh

import os

import subprocess

def run_command(command):
    p = subprocess.Popen(command,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
    return iter(p.stdout.readline, b'')

def fileIndir(rootDir):
    for lists in os.listdir(rootDir):
        path = os.path.join(rootDir, lists)
        print path

def isfloat(x):
    """
    Check if argument is float
    """
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    """
    Check if argument is int
    """
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

def isNum(x):
    """
    Check if string argument is numerical
    """
    return isfloat(x) or isint(x)


def generateGUID():
    """
    生成一个GUID
    :return: GUID
    """
    guid = str(uuid.uuid1())
    return guid


def peakdet(v, delta, x = None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []

    if x is None:
        x = numpy.arange(len(v))

    v = numpy.asarray(v)

    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    if not numpy.isscalar(delta):
        sys.exit('Input argument delta must be a scalar')

    if delta <= 0:
        sys.exit('Input argument delta must be positive')

    mn, mx = numpy.Inf, -numpy.Inf
    mnpos, mxpos = numpy.NaN, numpy.NaN

    lookformax = True

    for i in numpy.arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx-delta:
                maxtab.append(mxpos)
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append(mnpos)
                mx = this
                mxpos = x[i]
                lookformax = True
 
    return numpy.array(maxtab), numpy.array(mintab)

def split(filepath):
    splits = filepath.split('/')
    path = '/'.join(splits[:-1])
    name = splits[len(splits) - 1]
    splits = name.split('.')
    filename = splits[0]
    suffix = splits[1]

    return path, filename, suffix


def cut(input_file, delimit_points):
    # 切分点加入终止点3600
    delimit_points.append(7200)

    # 记录分段起止时间
    delimit_list = []
    if len(delimit_points) <= 2:
        return
    path, name, suffix = split(input_file)
    for i in range(0, len(delimit_points) - 1, 2):
        # 切出speech段落，文件名为"开始-结束"
        delimit_list.append([str(delimit_points[i]), str(delimit_points[i + 1])])
        cmd = "ffmpeg -i " + input_file + " -acodec copy -ss " + str(delimit_points[i]) + " -to " + str(delimit_points[i + 1]) + " " + path + "/" + name + "/" + str(delimit_points[i]) + "-" + str(delimit_points[i + 1]) + "." + suffix
        sh.run(cmd)
        print delimit_list

    return delimit_list


def convert(m4a_dir):
    path, filename, suffix = split(m4a_dir)
    mp3_dir = str(path) + "/" + str(filename) + ".mp3"
    cmd = "ffmpeg -v 5 -y -i " + m4a_dir + " -acodec libmp3lame -ac 2 -ab 192k " + mp3_dir
    sh.run(cmd)

    return mp3_dir


def concat(cut_point, wav_dir, mp3_dir):
    part_0 = ""
    part_1 = ""
    size_0 = 0
    size_1 = 0
    for i in range(0, len(cut_point),2):
        part_0 += "-i " + wav_dir + "/" + str(i) + ".wav "
        size_0+=1
        if i + 1 < len(cut_point) - 1:
            part_1 += "-i " + wav_dir + "/" + str(i+1) + ".wav "
            size_1+=1

    cmd = "ffmpeg  " + part_0 + " -filter_complex '[0:0][1:0][2:0][3:0]concat=n=" + str(size_0) + ":v=0:a=1[out]' -map '[out]' " + wav_dir + "/concat_0.wav"
    sh.run(cmd)
    cmd = "ffmpeg  " + part_1 + " -filter_complex '[0:0][1:0][2:0][3:0]concat=n=" + str(size_1) + ":v=0:a=1[out]' -map '[out]' " + wav_dir + "/concat_1.wav"
    sh.run(cmd)

    # to mp3
    cmd = "ffmpeg -i " + wav_dir + "/concat_0.wav" + " -q:a 8 " + mp3_dir + "/rs_0.mp3"
    sh.run(cmd)
    cmd = "ffmpeg -i " + wav_dir + "/concat_1.wav" + " -q:a 8 " + mp3_dir + "/rs_1.mp3"
    sh.run(cmd)


def load(json_file):
    with open(json_file) as jsonfile:
        json_list = json.load(jsonfile, encoding="gb2312")
        jsonfile.close
        records_list = sorted(json_list, key=lambda k: int(k['bg']), reverse = False)
    return records_list

def feedback(jsondir, keywords):
    feedback = []

    for i in range(0, len(keywords)):
        feedback.append({"keyword": keywords[i],
                         "spot": [],
                         "num": 0})

        print i
        f_list = os.listdir(jsondir)
        for f in f_list:
            if os.path.splitext(f)[1] == ".json":
                ss = f.split("-")[0]
                records_list = load(jsondir + f)
                for j in range(0, len(records_list)):
                    if keywords[i] in records_list[j].get("onebest"):
                        secStart = int(records_list[j].get("bg")) / 1000 + int(ss)
                        timeStart = str(secStart / 3600) + ":" + str(secStart % 3600 / 60) + ":" + str(secStart % 60)
                        feedback[i]["spot"].append(timeStart)
                        feedback[i]["num"] += 1
                        print(keywords[i] + ': ' + timeStart)
                    if feedback[i]["num"] == 0:
                        print (keywords[i] + "：没说到")
                        # print feedback[i]

    return feedback


def formateFeedback(feedback):
    UserDefineFeedBackMark = ""
    for i in feedback:
        UserDefineFeedBackMark += "关键词 \"" + i["keyword"] + "\" 口播：" + str(i["num"]) + "次\n"

    return UserDefineFeedBackMark

