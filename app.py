# import flask related
from flask import Flask, request, abort
from urllib.parse import parse_qsl
# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage,
    VideoSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction,
    PostbackEvent, ConfirmTemplate, CarouselTemplate, CarouselColumn,
    ImageCarouselTemplate, ImageCarouselColumn, FlexSendMessage,ImageMessage
)
import json
import random
import string
import sqlite3
# create flask server
app = Flask(__name__)
line_bot_api = LineBotApi('hxxfXJjOA6fUYSSMjyCmia9gvsY1QF10B+El/yFXCzckR3vENxIOsfcQYjrU69ahU6AqIIeIo+MUnX4BU6sbrFsF9anm2uBfdJ64LFe+pj+rcEeG/LCqorcnNOd4V0azO9V5+KO11Kv/XBLjme2ZdgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('525516aa02080443145d3c92301186fc')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

#歡迎訊息(區塊一)已經在Line developer網頁那設定好了

#以下是提前設定好方程和內容#########################

def details_template(name): #這個是傳出圖片後，彈出的按鈕，給對方選擇想看這個政治人物的什麼訊息
    print('name==',name)
    template = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            # thumbnail_image_url=url_for('static', filename='images/brown_1024.jpg', _external=True),
            thumbnail_image_url='https://creazilla-store.fra1.digitaloceanspaces.com/emojis/42646/man-office-worker-emoji-clipart-md.png',
            title='想知道關於他的什麼呢？',
            text='關於'+name+'的訊息',
            actions=[
                PostbackAction(
                    label='政見',
                    display_text='我想知道'+name+'的政見',
                    data='action=顯示政見&politician_name={}'.format(name)
                ),
                PostbackAction(
                    label='資歷',
                    display_text='我想知道'+name+'的資歷',
                    data='action=顯示資歷&politician_name={}'.format(name)
                ),
                PostbackAction(
                    label='不感興趣了',
                    display_text='我不感興趣了',
                    data='action=回到首頁'
                )
            ]
        )
        )
    return template



def information(politician_name): #輸入他的名字，輸出他的資訊，剩下的靠你們了
    print('politician===',politician_name)
    con = sqlite3.connect('./data/db_text/main_v3.db')
    cur = con.cursor()
    def func_fetching( name ):
        querydata = cur.execute('''SELECT * FROM candidate WHERE `姓名` = '{}';'''.format(name))
        result_value = [ i for i in querydata ]
        result_name = (description[0] for description in querydata.description )
        result = [ dict( zip(result_name,data) ) for data in result_value ]
        print( result)
        return result
    政見=''
    資歷=''
    politi_info = func_fetching( politician_name )
    print( politi_info)
    try:
        政見=politi_info[0]['政見']
        資歷=politi_info[0]['經歷']
    except:
        print( 'error occur')
        政見=''
        資歷='' 
    return [政見,資歷]

def others_template():
    template = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            # thumbnail_image_url=url_for('static', filename='images/brown_1024.jpg', _external=True),
            thumbnail_image_url='https://creazilla-store.fra1.digitaloceanspaces.com/emojis/42646/man-office-worker-emoji-clipart-md.png',
            title='想知道關於我們的什麼呢？',
            text='其他訊息',
            actions=[
                PostbackAction(
                    label='關於作者',
                    display_text='我想知道作者的資訊',
                    data='action=顯示作者資訊'
                ),
                URIAction(
                    label='軟體網站',
                    display_text='我想知道這機器人的官方網站',
                    uri='https://www.google.com/?gws_rd=ssl'
                    ),
                PostbackAction(
                    label='不感興趣了',
                    display_text='我不感興趣了',
                    data='action=回到首頁'
                )
            ]
        )
        )
    return template

#################################################

#區塊二和三，建議從這邊開始看

#接收 所有圖片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # get user info & message
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    if event.message.type=='image': #如果訊息是圖片的話，做以下步驟
        image_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(4)) #生成圖檔名字
        image_content = line_bot_api.get_message_content(event.message.id)
        image_name = image_name.upper()+'.jpg'
        path='./static/'+image_name
        with open(path, 'wb') as fd:
            for chunk in image_content.iter_content():
                fd.write(chunk) #在這裡把圖檔存起來了，在static資料夾裡
        policitian_name='someone' #我不知道你會怎麼處理，反正就是傳政治家的名字
        messages=[]
        messages.append(TextSendMessage(text='他的名字是：'+policitian_name),)
        messages.append(details_template(policitian_name))
        line_bot_api.reply_message(event.reply_token, messages)
        #print(postback_data.get('action'))

    # get msg details
    print('img from [', user_name, '](', user_id, ') ')

# 以下為所有接收到按鈕後的集散地
@handler.add(PostbackEvent) #有注意到details_message的按鈕上有"data=action=某某某"的部分嗎，那就是拿來觸發postback的事件
def handle_postback(event):
    
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    # print(event.postback.data)
    postback_data = dict(parse_qsl(event.postback.data))
    politician_name = postback_data.get('politician_name')
    # print(postback_data.get('action', ''))
    # print(postback_data.get('item', ''))
    sticker_list=[(1070, 17839), (6362, 11087920), (11537, 52002734), (8525, 16581293)]
    info=information(politician_name)
    print('handle_postback__name = ' , politician_name)
    if postback_data.get('action')=='顯示政見':
        messages=[]
        messages.append(TextSendMessage(text=f'他的政見為:\n{info[0]}'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='顯示資歷':
        messages=[]
        messages.append(TextSendMessage(text=f'他的資歷為:\n{info[1]}'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='回到首頁':
        messages=[]
        messages.append(TextSendMessage(text='請傳給我您有興趣的政治家的照片，或者打”其他”找其他資訊'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='顯示作者資訊':
        messages=[]
        messages.append(TextSendMessage(text='我們是中央大學的學生，作者有:王本偉、田家瑋、官慶睿、林泓宇、林恩立、李恆緯'))
        line_bot_api.reply_message(event.reply_token, messages)


# 我猜應該是接收所有文字的集散地
@handler.add(MessageEvent, message=TextMessage)
def text_message(event):
    # get user info & message
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    if event.message.type=='text': #如果訊息是文字的話，做以下步驟
        receive_text=event.message.text
        if receive_text=='其他':
            messages=others_template()
            print('1')
            line_bot_api.reply_message(event.reply_token, messages)
            print('2')
        elif( '我想知道:' in receive_text ):
            messages=[]
            politicitian_name = receive_text.split(':')[-1]
            messages.append(TextSendMessage(text='他的名字是：'+politicitian_name),)
            messages.append(details_template(politicitian_name))
            line_bot_api.reply_message(event.reply_token, messages)
        else:
            messages=TextSendMessage(text='請傳給我您有興趣的政治家的照片，或者打”其他”找其他資訊')
            line_bot_api.reply_message(event.reply_token, messages)

    # get msg details
    print('img from [', user_name, '](', user_id, ') ')


# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5566)