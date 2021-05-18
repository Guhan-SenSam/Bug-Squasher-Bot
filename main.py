import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from gdrive import GDrive
import random
PORT = int(os.environ.get('PORT', '443'))

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class MainMenu():
    def show_mainmenu(update,callback):
        query = update.callback_query
        query.answer()
        keyboard = [
            [
                InlineKeyboardButton("Report a bug", callback_data=str("BUGREPORT")),
                InlineKeyboardButton("Request for a feature", callback_data=str('FEATUREREPORT')),
            ],
            [
            InlineKeyboardButton("View changes", callback_data=str('VIEWCHANGES')),
            InlineKeyboardButton("Download latest APK", callback_data=str('DOWNLOAD')),
            ]
        ]
        message = '''*Report a bug* \- Click here to report a bug,mistake or a crash in the app \n
*Request for a feature* \- Click here to reuqest a new feature\. Remeber the feature must fit the stlye of the app \n
*View Changes*\- Click here to view all changes to the app over various apk releases \n
*Download Latest Apk*\- Click here to download the latest APK of this app'''
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)
        return "QUESTIONASKERS"

class BugReport():
    def ask_device(update,callback):
        query = update.callback_query
        query.answer()
        query.message.reply_text("What is the company of your device?")
        return 'DEVICECO'

    def ask_model(update,callback):
        BugReport.device_company = update.message.text
        update.message.reply_text("What model phone of "+BugReport.device_company+' do you have?')
        return 'DEVICEMODEL'

    def ask_bug_details(update,callback):
        BugReport.device_model = update.message.text
        update.message.reply_text('''Tell me about the bug or error you encountered.It would help
a lot if you could be very detailed about how you found this error or bug''')
        return 'BUGDETAILS'


    def show_bugmedia(update,callback):
        BugReport.bug_details = update.message.text
        keyboard = [
            [
                InlineKeyboardButton("Screenshot", callback_data=str("BUGPIC")),
                InlineKeyboardButton("Screen Recording", callback_data=str('BUGVIDEO')),
            ],
            [
            InlineKeyboardButton("None", callback_data=str('BUGNONE')),
            ]
        ]
        message = '''Send me a screenshot or a screenrecording of the bug.Only one image at a time.I'll ask you again if you want to add any more'''
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)
        return 'BUGMEDIA'

    def get_screenshot(update,callback):
        query = update.callback_query
        query.answer()
        query.message.reply_text('''Can you send me a screenshot of the bug.
Please send only one. I will ask again if u have another pic''')
        return 'GETSCREENSHOT'

    def save_screenshot(update,callback):
        if not update.message.text and not update.message.video and not update.message.document:
            global data_stored
            update.message.reply_text("Give me a minute while I download the file.")
            file = update.message.photo[-1].get_file()
            counter = 0
            for img in os.listdir('data/'):
                counter+=1
            new_pic_name = str(counter+1)
            sc = file.download('data/'+new_pic_name+".jpg")
            if counter == 1:# We increase one because of the delete stopper file
                MainMenu.gdrive_path = GDrive.get_current_dir()
            elif not data_stored:# In case if someone does fail to properly stop the bot this will dump all files in the root directory
                MainMenu.gdrive_path = 'root'
            GDrive.upload_picture('data/'+new_pic_name+".jpg", MainMenu.gdrive_path)

            data_stored = True
            keyboard = [
                [
                    InlineKeyboardButton("Screenshot", callback_data=str("BUGPIC")),
                    InlineKeyboardButton("Screen Recording", callback_data=str('BUGVIDEO')),
                ],
                [
                InlineKeyboardButton("None", callback_data=str('BUGNONE')),
                ]
            ]
            message = '''If you have any more pictures or videos please send them or else press none and we will move on'''
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(message, reply_markup=reply_markup)
            return 'BUGMEDIA'
        else:
            keyboard = [
                [
                    InlineKeyboardButton("Screenshot", callback_data=str("BUGPIC")),
                    InlineKeyboardButton("Screen Recording", callback_data=str('BUGVIDEO')),
                ],
                [
                InlineKeyboardButton("None", callback_data=str('BUGNONE')),
                ]
            ]
            message = '''Hey i think you sent me something else. I need a photo :)'''
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(message, reply_markup=reply_markup)
            return 'BUGMEDIA'

    def get_video(update,callback):
        query = update.callback_query
        query.answer()
        query.message.reply_text('''Send me the screenrecording of the bug.
Please try to keep the file size small as I only have limited space here :)''')
        return 'GETVIDEO'

    def save_video(update,callback):
        if not update.message.text and not update.message.photo and not update.message.document:
            global data_stored
            file = update.message.video.get_file()
            update.message.reply_text("Give me a minute while I download the file.")
            counter = 0
            for vid in os.listdir('data/'):
                counter+=1
            new_vid_name = str(counter+1)
            sc = file.download('data/'+new_vid_name+".mp4")
            if counter == 1:
                MainMenu.gdrive_path = GDrive.get_current_dir()
            elif not data_stored:
                MainMenu.gdrive_path = 'root'
            GDrive.upload_video('data/'+new_vid_name+".mp4", MainMenu.gdrive_path)

            data_stored = True
            keyboard = [
                [
                    InlineKeyboardButton("Screenshot", callback_data=str("BUGPIC")),
                    InlineKeyboardButton("Screen Recording", callback_data=str('BUGVIDEO')),
                ],
                [
                InlineKeyboardButton("None", callback_data=str('BUGNONE')),
                ]
            ]
            message = '''Attach another photo or video or press none if done'''
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(message, reply_markup=reply_markup)
            return 'BUGMEDIA'
        else:
            keyboard = [
                [
                    InlineKeyboardButton("Screenshot", callback_data=str("BUGPIC")),
                    InlineKeyboardButton("Screen Recording", callback_data=str('BUGVIDEO')),
                ],
                [
                InlineKeyboardButton("None", callback_data=str('BUGNONE')),
                ]
            ]
            message = '''Hey i think you sent me something else. I need a photo :)'''
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(message, reply_markup=reply_markup)
            return 'BUGMEDIA'



    def final_message(update,callback):
        query = update.callback_query
        query.answer()
        #Now save the text side of the bug report
        new_file = open('data/data.txt', 'w')
        lines = [str(query.message.chat.username+'\n'), BugReport.device_company+'\n', str(BugReport.device_model)+'\n',BugReport.bug_details+'\n']
        new_file.writelines(lines)
        new_file.close()
        files = os.listdir('data/')
        if len(files) == 2 and not data_stored:
            MainMenu.gdrive_path  = GDrive.get_current_dir()
        elif len(files) > 2 and data_stored:
            pass
        elif len(files) > 2 and not data_stored:
            MainMenu.gdrive_path = 'root'
        GDrive.upload_textfile('data/data.txt', MainMenu.gdrive_path, 'info.txt')
        for f in files:
            head, tail = os.path.split(f)
            if tail != 'delete_blocker.txt':
                os.remove("data/" + f)
        message = '''Thank you for your bug report. You can go back to the main menu
or exit me by just going back'''
        keyboard = [
            [
                InlineKeyboardButton("Return to Main Menu", callback_data=str("MAINMENU")),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(message, reply_markup=reply_markup)
        callback.bot.send_message(chat_id = '1335283858', text = "New bug report from user " + str(query.message.chat.username))
        callback.bot.send_message(chat_id = '1335283858', text = "Device Company:"+ BugReport.device_company)
        callback.bot.send_message(chat_id = '1335283858', text = 'Device Model:'+ BugReport.device_model)
        callback.bot.send_message(chat_id = '1335283858', text = BugReport.bug_details)
        return "MENU"

class FeatureRequest():
    def ask_feature(update,callback):
        query = update.callback_query
        query.answer()
        query.message.reply_text("""I would really like to hear of your idea for this app.
Can you please explain it to me in detail.Dont worry I wont get bored. :)""")
        return "FEATUREGET"

    def get_feature(update,callback):
        message = update.message.text
        new_file = open('feature.txt','w')
        new_file.write(message)
        new_file.close()
        id = "1ZMkn9nUg-IBXfdCoYiPQ1Ure-663m-dB"
        GDrive.upload_textfile('feature.txt', id, str(random.randint(0,250000)))
        update.message.reply_text("""Hey thanks a lot for the Idea. Let me send this to one
of the developers and let them know about your idea""")
        keyboard = [
            [
                InlineKeyboardButton("Return to Main Menu", callback_data=str("MAINMENU")),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = '''You can go back to the main menu or exit me by just going back'''
        update.message.reply_text(message, reply_markup=reply_markup)
        return "MENU"

class Download():

    def downloader(update,callback):
        query = update.callback_query
        query.answer()
        query.message.reply_text("Give me one second I am uploading the latest apk")
        file="remindy-0.1-arm64-v8a-debug.apk"
        callback.bot.send_document(update.effective_chat.id, document=open(file, 'rb'))
        keyboard = [
            [
                InlineKeyboardButton("Return to Main Menu", callback_data=str("MAINMENU")),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = '''You can go back to the main menu
or exit me by just going back'''
        query.message.reply_text(message, reply_markup=reply_markup)
        return "MENU"

class Functions():

    def start(update,callback):
        message = '''Welcome to Infinium Bug Squasher
Please select the app that you want to view options for'''

        keyboard = [
            [
                InlineKeyboardButton("Remindy-Reminder App", callback_data='MAINMENU'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)
        return "MENU"

    def stop(update,callback):
        message = "Exiting Bug squasher bot. You can now leave this page"
        update.message.reply_text(message)
        files = os.listdir('data/')
        for f in files:
            head, tail = os.path.split(f)
            if tail != 'delete_blocker.txt':
                os.remove("data/" + f)


    def inlinequery(update: Update, context: CallbackContext):
        #Display the switch to private chat option
        results = list()
        context.bot.answer_inline_query(update.inline_query.id, results = results, switch_pm_text="Switch to private chat", switch_pm_parameter='bug')

data_stored = False

class main():

    def main(self):
        self.updater = Updater("1723137577:AAFxgltlC-usPMntP8iOXqqAkDzCOI1ouys", use_context=True)
        dispatcher = self.updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', Functions.start)],
            states={
                'MENU': [
                    CallbackQueryHandler(MainMenu.show_mainmenu, pattern='^' + "MAINMENU"+ '$'),
                ],
                'QUESTIONASKERS':[
                    CallbackQueryHandler(BugReport.ask_device, pattern = '^'+"BUGREPORT"+'$'),
                    CallbackQueryHandler(Download.downloader, pattern = '^'+"DOWNLOAD"+'$'),
                    CallbackQueryHandler(FeatureRequest.ask_feature, pattern = '^'+"FEATUREREPORT"+'$')
                ],
                'DEVICECO':[
                    MessageHandler(Filters.text, BugReport.ask_model)
                ],
                'DEVICEMODEL':[
                    MessageHandler(Filters.text, BugReport.ask_bug_details)
                ],
                'BUGDETAILS':[
                    MessageHandler(Filters.text, BugReport.show_bugmedia)
                ],
                'BUGMEDIA':[
                    CallbackQueryHandler(BugReport.get_screenshot, pattern = '^'+"BUGPIC"+'$'),
                    CallbackQueryHandler(BugReport.get_video, pattern = '^'+"BUGVIDEO"+"$"),
                    CallbackQueryHandler(BugReport.final_message, pattern = '^'+"BUGNONE"+"$")
                ],
                'GETSCREENSHOT':[
                    MessageHandler(Filters.photo|Filters.text|Filters.video|Filters.document, BugReport.save_screenshot)
                ],
                "GETVIDEO":[
                    MessageHandler(Filters.video, BugReport.save_video)
                ],
                'FEATUREGET':[
                    MessageHandler(Filters.text, FeatureRequest.get_feature)
                ]
            },
            fallbacks=[CommandHandler('start', Functions.start)],
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(CommandHandler("start", Functions.start))
        dispatcher.add_handler(CommandHandler("stop", Functions.stop))
        dispatcher.add_handler(InlineQueryHandler(Functions.inlinequery))
        
                      
        self.updater.start_webhook(listen="0.0.0.0",
                      		port=PORT,
                      		url_path="1723137577:AAFxgltlC-usPMntP8iOXqqAkDzCOI1ouys",
                      		webhook_url="https://bug-squasher-bot.herokuapp.com/" + "1723137577:AAFxgltlC-usPMntP8iOXqqAkDzCOI1ouys")

        self.updater.idle()

if __name__ == '__main__':
    main().main()
