import requests,bs4
import telegram
import datetime
import sys

### global var
log_path='./log.txt'

chatid=sys.argv[1]
bottoken=sys.argv[2]

bot = telegram.Bot(token=bottoken)

def post_message(message):
    requests.get("https://api.telegram.org/bot"+bottoken+"/sendMessage?chat_id="+chatid+"&text="+message)

def open_log():
    try:
        fread = open(log_path, "r")
        log=fread.read().split('\n')
        fread.close()
    except:
        log=list()
    return log

def write_log(text):
    fwrite = open(log_path, "a+")
    fwrite.write(text+"\n")
    fwrite.close()

def is_posted(index):
    log=open_log()
    if index in log:
        return True
    else:
        return False

def crawl_index():
    res=requests.get('https://www.yphs.tp.edu.tw/yphs.aspx')
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    VIEWSTATE=soup.find(id="__VIEWSTATE").get('value')
    VIEWSTATEGENERATOR=soup.find(id="__VIEWSTATEGENERATOR").get('value')
    EVENTVALIDATION=soup.find(id="__EVENTVALIDATION").get('value')
    index_table=list()
    for x in  soup.find_all('table')[1].find_all('tr')[1:-1]:
        tds=x.find_all('td')
        title,date,department=tds[2].text,tds[0].text,tds[1].text
        href=x.find('a')["href"][25:-5]
        index_table.append([title,date,department,href])
    return index_table[::-1],VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION

def crawl_info(index_table,VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION):
    message_list=list()
    for index in index_table:
        if not is_posted(index[0]):
            cookies={"AspxAutoDetectCookieSupport":"1"}
            data={"__EVENTTARGET":index[3],"__VIEWSTATE":VIEWSTATE,"__VIEWSTATEGENERATOR":VIEWSTATEGENERATOR,"__EVENTVALIDATION":EVENTVALIDATION,"DL1":"不分","DL2":"不分","DL3":"全部","__LASTFOCUS":"","__EVENTARGUMENT":""}
            res=requests.post('https://www.yphs.tp.edu.tw//yphs.aspx?AspxAutoDetectCookieSupport=1',allow_redirects=False,cookies=cookies,data=data)
            soup=bs4.BeautifulSoup(res.text,'html.parser')
            info_table=soup.find_all('table')[0].find_all('td')
            #for i in range(len(info_table)):
            #    print(i,":",info_table[i].text)
            #[title,date,author,author_title,content,attachment]
            write_log(info_table[7].text)
            message_list.append([info_table[7].text,info_table[1].text,info_table[5].text,info_table[3].text,info_table[9].text,info_table[11].text])
    return message_list

def main():
    now = datetime.datetime.now()
    if now.hour==0 and 5<now.minute<25:
        countdown=str((datetime.date(2021, 1, 23)-datetime.date(now.year,now.month,now.day)).days-1)
        countdown1=str((datetime.date(2020, 8, 3)-datetime.date(now.year,now.month,now.day)).days-1)
        countdown2=str((datetime.date(2020, 9, 3)-datetime.date(now.year,now.month,now.day)).days-1)
        countdown3=str((datetime.date(2020, 11, 2)-datetime.date(now.year,now.month,now.day)).days-1)
        countdown4=str((datetime.date(2020, 12, 15)-datetime.date(now.year,now.month,now.day)).days-1)
        #msg=bot.send_message(chat_id=chatid, text='學測{}天 模考:[{},{},{},{}]'.format(countdown,countdown1,countdown2,countdown3,countdown4))
        #bot.pin_chat_message(chat_id=chatid,message_id=str(msg.message_id))
    index_table,VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION=crawl_index()
    message_list=crawl_info(index_table,VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION)
    for message in message_list:
        post_message("[主旨:"+message[0]+"]\n"+message[4]+"\n附件:\n"+message[5]+"\n發布時間:"+message[1]+"\n發布人:"+message[2]+"\n發布身份:"+message[3])
    exit(0)


main()



