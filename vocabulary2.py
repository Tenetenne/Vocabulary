# coding: utf-8

#################################################################################
#                                                                               #
#      FILE    : vocabulary2.py                                                 #
#      ABOUT   : 単語間隔反復ソフト（重要度の概念を含む）                           #
#      VERSION : 3.5                                                            #
#      DATE    : 18/10/30                                                       #
#      Author   : てねてんね                                                     #
#                                                                               #
#################################################################################

from __future__ import print_function
import argparse
from apiclient.discovery import build
import httplib2
from oauth2client import file, client, tools
from random import *
import datetime
import http
import socket
import colorama
from colorama import Fore, Back, Style
import pandas as pd


# global variance --------------------------------------------------------------
wordList = []
wordListFinish=[]
is_quit = False
is_fileOpenFirst=0
colorama.init(autoreset=True)
is_J2D=0


# constant declaration ---------------------------------------------------------
NOTNULL='1'
IMPO_Y=1
IMPO_N=2
DEFALUT_IMPORTANCE=10
SEE_FILENAME='1'
IMPORT_FILE='2'
SEE_LOG='3'
SEE_CONTENTS='4'
FIRSTTIME=1
NOTFIRSTTIME=0
LOGSSID="16Ih5mt4DUxSNcHd8K9hSE_RSrNQvWJ6-H2fJS8J-AgQ"
MSSID="1XOZWpZrq6ara0vW58FLFl2RTWzJTv9rEqlB-JdtOQRU"


# class-------------------------------------------------------------------------
class Word:
    def __init__(self, word, meaning, importance, importance1, importance2, originalNum):
        self.word = word
        self.meaning = meaning
        self.importance = importance
        self.importance1 = importance1
        self.importance2 = importance2
        self.originalNum = originalNum
    def showinfo(self):
        print("word: ",self.word,"\nmeaning: ","\nimportance: ",self.importance,\
        self.meaning,"\nimportance1: ",self.importance1,"\nimportance2: ",\
        self.importance2,"\noriginalNum: ",self.originalNum,"\n")


# input()のtry-except　---------------------------------------------------------
def inputtry(stringdata):
    try:
        ans=input(stringdata)
        return ans
    except EOFError:
        inputtry(stringdata)


# アカウントの承認 --------------------------------------------------------------
def get_credentials():
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(httplib2.Http()))
    return service


# データを読み込む --------------------------------------------------------------
def read_data(spreadId, rangeName, service):
    SPREADSHEET_ID = spreadId
    RANGE_NAME = rangeName
    response_r = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    return response_r["values"]


# データを書き込む ---------------------------------------------------------------
def write_data(spreadId, rangeName, values, service):
    SPREADSHEET_ID = spreadId
    RANGE_NAME = rangeName
    body = {
        'values': values,
    }
    service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,valueInputOption="USER_ENTERED",body=body).execute()


# データを追加する ---------------------------------------------------------------
def append_data(spreadId, rangeName, values, service):
    SPREADSHEET_ID = spreadId
    RANGE_NAME = rangeName
    body = {
        'values': values,
    }
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,valueInputOption="USER_ENTERED",body=body).execute()


# ------------------------------------------------------------------------------
def Message():
    global is_quit
    if is_quit: return
    print("\n---------------------------------------------------------------------")
    # print("- 単語を提示します。覚えていたらy、覚えていなかったらnで答えてください。")
    # print("- qを入力すると終了できます。")
    # print("- rを入力すると直前のyの処理を修正できます。")
    print("- You'll see some words. If you remember them, answer with 'y', if not, 'n'")
    print("- You can quit this program with 'q'")
    print("- If you can take back the previous answer with y, answer with 'r'")
    print("---------------------------------------------------------------------\n")


# 単語を提示する関数 -------------------------------------------------------------
def ShowWordlist(m, wordList):
    global is_quit,is_random,firstLenWordList,rateFirst,NumOfImportance9_1,NumOfImportance9_2,is_J2D
    if is_quit: return

    # print("\n～%d周目～" %m)
    if 1<=m<=3:
        list=["1st", "2nd","3rd"]
        print("***",list[m-1],"time ***")
    else:
        print("***",str(m)+"th time ***")

    if is_random:
        RandomShaffle(wordList)

    NumOfImportance9=NumOfImportance9_1 if is_J2D else NumOfImportance9_2

    counter=0
    wordListAgain=[]
    for i in range(len(wordList)):      # リスト内の単語を順番に処理する
        counter+=1
        while 1:        # ユーザから正しい反応が得られるまで繰り返す
            if wordList[i].importance<10:
                counter-=1
                break
            if m==1:
                print("%d/%d  %s" % (counter, len(wordList)-NumOfImportance9, wordList[i].word))
            else:
                print("%d/%d  %s" % (i + 1, len(wordList), wordList[i].word))
            answer = inputtry("answer : ")

            if answer =='y':
                # print("もう覚えてますね。\n")
                # print("意味：%s\n" % wordList[i].meaning)
                print("Meaning："+ColorChangeOfWord(str(wordList[i].meaning))+wordList[i].meaning+"\n")
                wordList[i].importance -= IMPO_Y
                wordListFinish.append(wordList[i])
                if (i==len(wordList)-1 and m>=2) or (counter==len(wordList)-NumOfImportance9 and m==1):
                    if inputtry('Last : ') in ['r', 'n']:
                        # print("%sの評価をyからnに変更しました。\n" % wordList[i].word)
                        print("%s's estimation was changed into 'n' from 'y'\n" % wordListFinish[-1].word)
                        wordListFinish[-1].importance += IMPO_N
                        wordListAgain.append(wordList[i])
                break
            elif answer == 'n' :
                # print("まだ覚えてないですね。\n")
                # print("意味：%s\n" % wordList[i].meaning)
                print("Meaning："+ColorChangeOfWord(str(wordList[i].meaning))+wordList[i].meaning+"\n")
                wordList[i].importance += IMPO_N
                wordListAgain.append(wordList[i])
                break
            elif answer == 'q' or is_quit:        # 強制終了
                is_quit = True
                return
            elif answer == 'r' and i > 0 and wordList[i - 1] not in wordListAgain:
                # print("%sの評価をyからnに変更しました。\n" % wordList[i - 1].word)
                print("%s's estimation was changed into 'n' from 'y'\n" % wordListFinish[-1].word)
                wordListFinish[-1].importance += IMPO_N
                wordListAgain.append(wordList[i - 1])
            else:       # 正しい答えが得られなかったとき
                # print("yかnかqかrで答えてください\n")
                print("Ansewer with 'y' 'n', 'q', or 'r'\n")

    m+=1
    if len(wordListAgain):      # 再帰処理
        rate = 100 - 100 * len(wordListAgain) / firstLenWordList
        if m==2:
            rateFirst="{0:.1f}".format(rate)
        # print("暗記率：%s %%" % "{0:.1f}".format(rate))
        print("You have already remembered：%s %%\n" % "{0:.1f}".format(rate))
        # print("まだ覚えていないのは以下の単語です\n")
        # for i in range(len(wordListAgain)):
        #     print("%s" % wordListAgain[i].word, end="")
        #     if i != len(wordListAgain) - 1:
        #         print(", ", end="")
        ShowWordlist(m, wordListAgain)
    elif m==2:
        rateFirst="100"


# ファイルを開く関数 ----------------------------------------------------------
def FileOpen():
    global is_fileOpenFirst,FILENAME
    # print("\n-------------------------")
    # print("      ファイル名入力     ")
    # print("-------------------------")
    if is_fileOpenFirst==0:
        is_fileOpenFirst==1
        print("\n-------------------------")
        print("      File name     ")
        print("-------------------------")
    FILENAME=inputtry("File name : ")
    return FILENAME


# 順番変更する関数 ---------------------------------------------------------------
def OrderChange():
    global is_random, is_quit
    if is_quit: return
    # print("\n------ 順序変更しますか？ -----")
    print("\n------ Do you want to sort data? -----")
    # sort_answer = input("（ランダムシャッフル：r, 重要度並び替え：i, デフォルト：d）  :")
    sort_answer=inputtry("(random shaffle：'r', sort by importance：'i', default：'d'）  :")
    is_random=sort_answer=="r"
    if sort_answer == "i":
        ImportanceSort()
    elif sort_answer!='r' and sort_answer!='d':
        # print("r, i, dのいずれかで答えてください")
        print("Press 'r', 'i', or 'd'")
        OrderChange()


# 単語をランダムに並び替える関数 --------------------------------------------------
def RandomShaffle(wordList):
    for i in range(len(wordList) - 1):
        j = randint(0, len(wordList) - 1)
        wordList[i], wordList[j] = wordList[j], wordList[i]


# 重要度の順にソート -------------------------------------------------------------
def ImportanceSort():
    for i in range(len(wordList)):
        for j in range(len(wordList) - 1, i, -1):
            if wordList[j].importance > wordList[j - 1].importance:
                wordList[j], wordList[j - 1] = wordList[j - 1], wordList[j]


# 単語と意味の入れ替え -----------------------------------------------------------
def ObjectChange():
    global is_quit, is_J2D
    if is_quit: return
    # if input("問題と答えを入れ替えますか？(y or n) :") == "y":
    if inputtry("Do you want to exchange questions and answers? ('y' or 'n') :") == 'y':
        is_J2D=1
        for i in range(len(wordList)):
            wordList[i].word, wordList[i].meaning = wordList[i].meaning, wordList[i].word
    for i in range(len(wordList)):
        wordList[i].importance=wordList[i].importance1 if is_J2D else wordList[i].importance2


# 指定されたファイル名のSheetをmaster sheetから探し，そのidを出力 ------------------
def idOfFname(fname):
    for response_ms_value_i in response_ms_value:
        if fname==response_ms_value_i[0]:
            return response_ms_value_i[1]


# Sheetをimportしてword listを読み出す -------------------------------------------
def ImportSheet(FILE):
    global firstLenWordList,NumOfImportance9_1,NumOfImportance9_2,is_J2D
    if idOfFname(FILE) == None:
        print("\n<No such Filename>")
        ImportSheet(FileOpen())
    else:
        print("Now loading...")
        response_r_value=read_data(idOfFname(FILE),'A1:D60',service)
        NumOfImportance9_1=0
        NumOfImportance9_2=0
        for j in range(len(response_r_value)):
            try:
                wordList.append(Word(response_r_value[j][0], response_r_value[j][1],0,
                                 int(response_r_value[j][2]),int(response_r_value[j][3]), j + 1))
            except IndexError:
                for _ in range(4-len(response_r_value[j])):
                    response_r_value[j].append(DEFALUT_IMPORTANCE)
                wordList.append(Word(response_r_value[j][0], response_r_value[j][1],0,
                                 int(response_r_value[j][2]),int(response_r_value[j][3]), j + 1))
            except ValueError:
                response_r_value[j][2]=DEFALUT_IMPORTANCE
                wordList.append(Word(response_r_value[j][0], response_r_value[j][1],0,
                                 int(response_r_value[j][2]),int(response_r_value[j][3]), j + 1))

            if int(response_r_value[j][2])<=DEFALUT_IMPORTANCE-1:
                NumOfImportance9_1+=1
            if int(response_r_value[j][3])<=DEFALUT_IMPORTANCE-1:
                NumOfImportance9_2+=1
        firstLenWordList=len(wordList)


# データのリストを描画------------------------------------------------------------
def LsData():
    print('')
    for ct, response_ms_value_i in enumerate(response_ms_value):
        if str(response_ms_value_i[2])==NOTNULL:
            print(str(response_ms_value_i[0]), '\t',end='')
            if (ct+1)%7==0:
                print('')
    print('\n')


# ログに記録する関数 -------------------------------------------------------------
def SaveLog(fileName):
    global rateFirst,is_J2D
    if inputtry("Do you want to save? ('y' or 'n') : ")=='y':
        now=str(datetime.datetime.now())
        X2X='J2D' if is_J2D else 'D2J'
        append_data(LOGSSID,'A1:D100',[[now,fileName,rateFirst,X2X]],service)


# 重要度を更新する関数------------------------------------------------------------------------------
def UpdateImportance(fileName):
    global is_J2D
    if inputtry("Do you want to update importance? ('y' or 'n') : ")=='y':
        wordListImportance=[[str(wordList[i].importance)] for i in range(len(wordList))]
        if is_J2D:
            write_data(idOfFname(fileName),'C1:100',wordListImportance,service)
        else:
            write_data(idOfFname(fileName),'D1:100',wordListImportance,service)


# ログを出力する関数 -------------------------------------------------------------
def PrintLog():
    log_value=read_data(LOGSSID,'A1:E300',service)

    timeValue=[]
    filenameValue=[]
    percentValue=[]
    J2D=[]
    times=[]
    times_filename=[]
    reset=[]

    for i in range(len(log_value)-1):
        times_filename.append(str(log_value[i][1])+str(log_value[i][3]))
        times.insert(0,times_filename.count(str(log_value[i][1])+str(log_value[i][3])))

    for i in range(len(log_value)-1,0,-1):
        if len(str(log_value[i][0]))==len("2018-09-17 2:51:41"):
            tmp1=str(log_value[i][0])
            tmp2=tmp1[:10]
            tmp3=tmp1[10:]
            log_value[i][0]=tmp2+' '+tmp3
        log_value[i][0]=log_value[i][0][5:13]

        timeValue.append(log_value[i][0])
        filenameValue.append(log_value[i][1])
        percentValue.append(log_value[i][2])
        J2D.append(log_value[i][3])
        reset.append(log_value[i][4])

    logdf=pd.DataFrame({
        str(log_value[0][0]) : timeValue,
        str(log_value[0][1]) : filenameValue,
        str(log_value[0][2]) : percentValue,
        str(log_value[0][3]) : J2D,
        "times" : times,
        str(log_value[0][4]) : reset
    })
    print(logdf)


# 重要度の更新とログの記録をする関数 ----------------------------------------------
def PrintAndUpdate(fileName):
    try:
        SaveLog(fileName)
        UpdateImportance(fileName)
    except (ConnectionAbortedError, http.client.HTTPException,\
            socket.gaierror, httplib2.ServerNotFoundError) as error:
        print("\n<Software caused connection abort>\n")
        if inputtry("Do you want to try again? : ")=='y':
            PrintAndUpdate(fileName)


# ファイルの中身を出力するだけの関数 ----------------------------------------------
def ShowContentsOfList():
    for i in range(len(wordList)):
        wordList[i].showinfo()


# wordListクラスの破棄 ----------------------------------------------------------
def Destructer():
    lenWordList=len(wordList)
    for i in range(lenWordList):
        del wordList[0]


# ------------------------------------------------------------------------------
def ColorChangeOfWord(stringdata):
    gender=stringdata[0:3]
    if gender=="der":
        return Fore.LIGHTCYAN_EX
    elif gender=="die":
        return Fore.LIGHTMAGENTA_EX
    elif gender=="das":
        return Fore.LIGHTGREEN_EX
    else:
        return ''


# ------------------------------------------------------------------------------
def Selection(is_firstTime):
    global FILENAME
    if is_firstTime:
        print("-------------------------")
        print("      vocabulary2.py     ")
        print("-------------------------")
    # print("使用可能なファイル名を表示する場合は1，")
    # ans=input("ファイルをインポートする場合は2を入力してください : ")
    print("- See available file names -> '1'")
    print("- Import a file -> '2'")
    print("- See the log -> '3'")
    ans=inputtry("- See the contents of a file -> '4' : ")
    if ans=='':
        Selection(NOTFIRSTTIME)
    elif ans==SEE_FILENAME:
        LsData()
        Selection(NOTFIRSTTIME)
    elif ans==IMPORT_FILE or any(ans[0]==x for x in ['d','e','c']) or ans=='test':
        FILENAME=FileOpen() if ans=='2' else ans
        ImportSheet(FILENAME)
        OrderChange()
        ObjectChange()
        Message()
        ShowWordlist(1, wordList)
        PrintAndUpdate(FILENAME)
    elif ans==SEE_LOG:
        PrintLog()
        Selection(NOTFIRSTTIME)
    elif ans==SEE_CONTENTS:
        FILENAME=FileOpen()
        ImportSheet(FILENAME)
        ShowContentsOfList()
        Destructer()
        Selection(NOTFIRSTTIME)
    else:
        Selection(NOTFIRSTTIME)


# ------------------------------------------------------------------------------
if __name__=='__main__':
    print('Now loading...')
    service = get_credentials()
    response_ms_value = read_data(MSSID,'A1:D300',service)
    Selection(FIRSTTIME)
