import requests
from typing import Final, List
from telegram import Update,ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re,os,time
import pandas as pd
import random
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from pydub import AudioSegment
import wave
import asyncio
import tempfile
import edge_tts
import speech_recognition as sr




# Your bot token and username
# Your bot token and username
TOKEN: Final = '7641472874:AAE8-yQDwGwWyPWVcZHiRvPrx2KvAz-d-Rk'
BOT_USERNAME: Final = '@Vamiika_bot'

#TOKEN: Final = '6991746723:AAHx0aqfY-S_PelA80TRh3aKBFe0yRWsLL8'
#BOT_USERNAME: Final = '@Aaradhya_bot'

genai.configure(api_key="AIzaSyC-2XiAk9k97bX5yU4pLWvf1NugtbgK9t8")

TRUTH_FILE = 'truths.txt'
DARE_FILE = 'dares.txt'
filename = "knwldg.txt"
req =1
muted_users = set()
sticker_tracker = {}

EXCEL_FILE_PATH = "allowed_StickerUserID.xlsx"
# Google Custom Search API credentials
GOOGLE_API_KEYS: Final[List[str]] = [
    'AIzaSyDqzvNif6a5kJm_sc4EmJzSk5upzrvHE48',  # First API Key
    'AIzaSyCZjlwdblmT1T6xJrsUi22V9xgw9MZzByw',  # Replace with your second API key
]
GOOGLE_CXS: Final[List[str]] = [
    '92178ceca83294240',  # First CX ID
    '671582ee1a93142c9',  # Replace with your second CX ID
]
ALLOWED_GROUP_ID: Final = -1001817635995    # Replace with your actual group ID
ALLOWED_ADMIN_GROUP_ID: Final = -1002137866227

GIF_IMAGE_PATHS: Final = {
    'bite': 'Image/bite.gif',
    'boom': 'Image/boom.gif',
    'beat': 'Image/beat.gif',
    'call': 'Image/call.gif',
    'care': 'Image/care.gif',
    'chill': 'Image/chill.gif',
    'dance': 'Image/dance.gif',
    'enjoy': 'Image/enjoy.gif',
    'feed': 'Image/feed.gif',
    'fight': 'Image/fight.gif',
    'fry': 'Image/fry.gif',
    'greet': 'Image/greet.gif',
    'go': 'Image/go.gif',
    'hug': 'Image/hug.gif',
    'ignore': 'Image/ignore.gif',
    'kill': 'Image/kill.gif',
    'knock': 'Image/knock.gif',
    'miss': 'Image/miss.gif',
    'move': 'Image/move.gif',
    'patt': 'Image/patt.gif',
    'play': 'Image/play.gif',
    'poison': 'Image/poison.gif',
    'poke': 'Image/poke.gif',
    'praise': 'Image/praise.gif',
    'roast': 'Image/roast.gif',
    'scold': 'Image/scold.gif',
    'silent': 'Image/silent.gif',
    'slap': 'Image/slap.gif',
    'snatch': 'Image/snatch.gif',
    'sorry': 'Image/sorry.gif',
    'spit': 'Image/spit.gif',
    'stab': 'Image/stab.gif',
    'stalk': 'Image/stalk.gif',
    'swing': 'Image/swing.gif',
    'tease': 'Image/tease.gif',
    'teach': 'Image/teach.gif',
    'write': 'Image/write.gif',
    'throw': 'Image/throw.gif'
}

'''
class KnowledgeBase:
    def __init__(self, text):
        # Load the pre-trained model once during initialization
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        self.text = text
        self.qa_pairs = self._extract_qa_pairs(text)
        self.questions = [qa[0] for qa in self.qa_pairs]
        self.answers = [qa[1] for qa in self.qa_pairs]
        self.question_embeddings = self._embed_sentences(self.questions)
        self.answer_embeddings = self._embed_sentences(self.answers)
    def _extract_qa_pairs(self, text):
        """Extract question-answer pairs from the provided text."""
        qa_pairs = []
        lines = text.split("\n")
        for i in range(0, len(lines)-1, 2):  # Assuming each question and answer are on consecutive lines
            question = lines[i].replace("User 1:", "").strip()
            answer = lines[i+1].replace("User 2:", "").strip()
            qa_pairs.append((question, answer))
        return qa_pairs
    def _embed_sentences(self, sentences):
        """Embed sentences using the SentenceTransformer model."""
        return self.model.encode(sentences, convert_to_tensor=True)
    def answer_question(self, query, top_k=1):
        """Find the most relevant answer based on the query."""
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cos_similarities = util.pytorch_cos_sim(query_embedding, self.question_embeddings)
        
        # Ensure similarities are computed on the CPU
        cos_similarities = cos_similarities.cpu()
        # Get the top k most similar questions
        top_results = np.argpartition(-cos_similarities, range(top_k))[0:top_k]
        best_question_idx = top_results[0][0]
        # Get the corresponding answer
        best_answer = self.answers[best_question_idx]
        # Remove "User 1:" or "User 2:" from the response before sending it back
        clean_answer = re.sub(r'(User\s*[12]:\s*)', '', best_answer)
        return self._limit_answer_length(clean_answer)
    def _limit_answer_length(self, answer, max_words=150):
        """Limits the answer to a maximum of max_words words."""
        words = answer.split()
        if len(words) > max_words:
            return ' '.join(words[:max_words]) + "..."
        return answer
 
# Initialize the knowledge base with the content from the file
'''

with open(filename, 'r', encoding='utf-8') as file:
    text = file.read()

#kb = KnowledgeBase(text)

def clean_text(text: str) -> str:
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    return text


# Function to get a random line from a file
def get_random_line(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:  # Specify UTF-8 encoding
            lines = file.readlines()
            return random.choice(lines).strip() if lines else 'No content found.'
    except FileNotFoundError:
        return f'{file_path} not found. Please make sure the file exists.'
    except UnicodeDecodeError as e:
        return f'Error reading file {file_path}: {e}'


def add_line_to_file(file_path: str, new_line: str) -> str:
    try:
        with open(file_path, 'a') as file:  # Open file in append mode
            file.write(new_line + '\n')
        return 'Your text has been added!'
    except Exception as e:
        return f'Failed to add text: {e}'


async def add_truth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id == ALLOWED_ADMIN_GROUP_ID:  # Check if the command is used in the allowed group
        user_message = ' '.join(context.args).strip()
        if user_message:
            response = add_line_to_file(TRUTH_FILE, user_message)
            try:
                await update.message.reply_text(response)
            except:
                await update.message.chat.send_message(response)
            
        else:
            try:
                await update.message.reply_text('Please provide a truth question to add.')
            except:
                await update.message.chat.send_message('Please provide a truth question to add.')
            
    else:
        try:
            await update.message.reply_text('This command is not allowed in this group.')
        except:
            await update.message.chat.send_message('This command is not allowed in this group.')
        


async def add_dare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id == ALLOWED_ADMIN_GROUP_ID:  # Check if the command is used in the allowed group
        user_message = ' '.join(context.args).strip()
        if user_message:
            response = add_line_to_file(DARE_FILE, user_message)
            await update.message.reply_text(response)
        else:
            try:
                await update.message.reply_text('Please provide a dare to add.')
            except:
                await update.message.chat.send_message('Please provide a dare to add.')
            
    else:
        try:
            await update.message.reply_text('This command is not allowed in this place Use in https://t.me/+yVFKtplWZUA0Yzhl admin group.')
        except:
            await update.message.chat.send_message('This command is not allowed in this place Use in https://t.me/+yVFKtplWZUA0Yzhl admin group.')
        


async def send_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.split()[0][1:]
    file_path = GIF_IMAGE_PATHS.get(command)
    username = update.message.from_user.username
    target_user = re.search(r'@(\w+)', update.message.text)
    target_username = target_user.group(0) if target_user else 'someone'
    custom_message = f'@{username} is {command}ing {target_username}'

    if file_path:
        if file_path.endswith('.gif'):
            try:
                await update.message.reply_animation(animation=open(file_path, 'rb'), caption=custom_message)
            except:
                await update.message.chat.send_animation(animation=open(file_path, 'rb'), caption=custom_message)
            
        else:
            try:
                await update.message.reply_photo(photo=open(file_path, 'rb'), caption=custom_message)
            except:
                await update.message.chat.send_photo(photo=open(file_path, 'rb'), caption=custom_message)
            


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text('Hello! Thanks For Chatting With Me, I am YourBot.')
    except:
        await update.message.chat.send_message('Hello! Thanks For Chatting With Me, I am YourBot.')
    

async def truth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    truth = get_random_line('truths.txt')
    try:
        await update.message.reply_text(truth)
    except:
        await update.message.chat.send_message(truth)
    


# Function to handle the /dare command
async def dare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dare = get_random_line('dares.txt')
    try:
        await update.message.reply_text(dare)
    except:
        await update.message.chat.send_message(dare)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text('No worries, I will assist you with all kinds of help. For more help, contact @YourContactUsername.')
    except:
        await update.message.chat.send_message('No worries, I will assist you with all kinds of help. For more help, contact @YourContactUsername.')
    


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text('For a custom command, I will respond in a customized way.')
    except:
        await update.message.chat.send_message('For a custom command, I will respond in a customized way.')
    


async def get_google_search_response(query: str) -> str:
    search_url = "https://www.googleapis.com/customsearch/v1"
    for api_key, cx in zip(GOOGLE_API_KEYS, GOOGLE_CXS):
        params = {
            "key": api_key,
            "cx": cx,
            "q": query
        }
        try:
            response = requests.get(search_url, params=params)
            if response.status_code == 429:  # Check for quota exceeded
                continue  # Try the next API key and CX ID
            response.raise_for_status()
            search_results = response.json()
            if 'items' in search_results:
                snippets = [clean_text(item.get('snippet', '')) for item in search_results['items']]
                return ' '.join(snippets)[:400]  # Limit response to 400 characters
            else:
                return 'No results found.'
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 403:  # Forbidden (possibly quota exceeded)
                continue  # Try the next API key and CX ID
            return f"HTTP error occurred: {http_err}"
        except Exception as err:
            return f"Other error occurred: {err}"

    # If all keys are exhausted
    return "I've reached my daily search limit. I'll be able to respond after tomorrow."


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Check if the command is being used in the allowed group
    if chat_id == ALLOWED_GROUP_ID:
        user_message = ' '.join(context.args)
        if user_message:
            response = await get_google_search_response(user_message)
            try:
                await update.message.reply_text(response)
            except:
                await update.message.chat.send_message(response)
            
        else:
            try:
                await update.message.reply_text('Please ask a question.')
            except:
                await update.message.chat.send_message('Please ask a question.')
            
    else:
        try:
            await update.message.reply_text('Sorry, this command is not allowed in this group. Join https://t.me/+yVFKtplWZUA0Yzhl')
        except:
            await update.message.chat.send_message('Sorry, this command is not allowed in this group. Join https://t.me/+yVFKtplWZUA0Yzhl')
        


def handle_response(text: str) -> str:
    processed: str = text.lower()
   
    if re.search(r'\bpurpose of the group\b', processed):
        return 'To Improve English Speaking ✨Keep Learning Keep Growing✨'
    if re.search(r'\bwho is your owner\b', processed):
        return 'My Owner is Ishi'
    if re.search(r'\bHey Vamika\b', processed):
        return 'Yeah Hii'
    if re.search(r'\bgood morning\b', processed):
        return 'Jai Shree Krishna'
    if re.search(r'\bjai shree krishna\b', processed):
        return 'Jai Shree Krishna'
    return None


async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_list = '\n'.join([f'/{cmd}' for cmd in GIF_IMAGE_PATHS.keys()])
    all_commands = f"Available commands:\n{commands_list}\n/search"
    try:
        await update.message.reply_text(all_commands)
    except:
        await update.message.chat.send_message(all_commands)

def ensure_excel_file():
    if not os.path.exists(EXCEL_FILE_PATH):
        df = pd.DataFrame(columns=["User ID"])
        df.to_excel(EXCEL_FILE_PATH, index=False)

# Load allowed users from the Excel file
def load_allowed_users():
    ensure_excel_file()  # Make sure the file exists
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        return set(df["User ID"].dropna().astype(int)) if not df.empty else set()
    except Exception as e:
        print(f"Error loading allowed users: {e}")
        return set()

# Function to add a user ID to the Excel file
async def add_sticker_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    ALLOWED_USERS = load_allowed_users()  # Reload allowed users

    # Allow only in the specified group
    if chat_id != ALLOWED_ADMIN_GROUP_ID:
        return  

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addstickeruserid <user_id>")
        return

    try:
        new_user_id = int(context.args[0])  

        if new_user_id in ALLOWED_USERS:
            await update.message.reply_text("✅ This user is already allowed to send stickers.")
            return

        # Read existing data
        df = pd.read_excel(EXCEL_FILE_PATH)
        
        # Append new user ID in correct column
        new_entry = pd.DataFrame({"User ID": [new_user_id]})
        df = pd.concat([df, new_entry], ignore_index=True)

        # Save back to Excel
        df.to_excel(EXCEL_FILE_PATH, index=False)

        await update.message.reply_text(f"✅ User {new_user_id} is now allowed to send stickers.")

        if os.path.exists(EXCEL_FILE_PATH):
            await context.bot.send_document(chat_id=ALLOWED_ADMIN_GROUP_ID, document=open(EXCEL_FILE_PATH, 'rb'),
                                    caption="📄 Updated Allowed User List")
    except ValueError:
        await update.message.reply_text("⚠️ Invalid user ID. Please enter a valid number.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error adding user: {e}")

async def handle_gif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete GIFs (Animations) and mute the sender for 10 minutes."""
    message = update.message
    user_id = message.from_user.id
    chat_id = message.chat.id
    ALLOWED_USERS = load_allowed_users()
    if message.animation and user_id not in ALLOWED_USERS :  # Check if the message is a GIF
        try:
            # Mute user for 10 minutes
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False
                ),
                until_date=int(time.time()) + 600  # Mute for 10 minutes
            )
            
            # Notify group about the mute
            await message.chat.send_message(
                f"🚫 User [{message.from_user.username or user_id}] has been muted for 10 minutes due to sending a GIF."
            )

            # Delete the GIF message
            await message.delete()
        
        except Exception as e:
            print(f"Failed to mute user {user_id} for sending GIF: {e}")
          

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete stickers from non-allowed users and mute spammers."""
    message = update.message
    user_id = message.from_user.id  
    chat_id = message.chat.id
    ALLOWED_USERS = load_allowed_users()

    if user_id not in ALLOWED_USERS:
        await message.delete()
        current_time = time.time()
        
        # Initialize sticker tracking for the user if not exists
        if user_id not in sticker_tracker:
            sticker_tracker[user_id] = []

        sticker_tracker[user_id].append(current_time)

        # Remove timestamps older than 3 seconds
        sticker_tracker[user_id] = [t for t in sticker_tracker[user_id] if current_time - t <= 3]

        # If user sent more than 3 stickers in 3 seconds, mute for 10 minutes
        if len(sticker_tracker[user_id]) > 3:
            if user_id not in muted_users:  # Avoid muting multiple times
                try:
                    await context.bot.restrict_chat_member(
                        chat_id=chat_id,
                        user_id=user_id,
                        permissions=ChatPermissions(
                            can_send_messages=False
                        ),
                        until_date=int(current_time) + 600  # Mute for 10 minutes
                    )
                    await message.chat.send_message(
                        f"🚫 User [{message.from_user.username or user_id}] has been muted for 10 minutes due to sticker spam."
                    )
                    muted_users.add(user_id)  # Add to muted users set
                    sticker_tracker[user_id] = []  # Reset tracker
                except Exception as e:
                    print(f"Failed to mute user {user_id}: {e}")

            return  # Do not send the "sticker not allowed" message if user is muted

        # Delete the sticker message
        try:
            if user_id not in muted_users:  # Send warning only if user is not muted
                await message.chat.send_message(
                    "🚫 Only allowed users can send stickers.\n"
                    "If you want permission, send a message to @Vamiika_bot saying:\n"
                    '"allow me for a sticker"'
                )
        except Exception as e:
            print(f"Failed to delete sticker: {e}")

#============================================================================================================
apikeylist = ["AIzaSyC-2XiAk9k97bX5yU4pLWvf1NugtbgK9t8","AIzaSyAyhqX2OxeCad8E5WVRXO5hLTWOs1W2eDY","AIzaSyAuv8wHIo__6BRqczmnhm_EGl7CKD32u0Q","AIzaSyA7rw343tP5MNUmmxHK_BRQ3HreZkvEPCY"]

static_history = [
   {
      "role": "user",
      "parts": [
        "Now further You  will  gonna chat like Ielts teacher name: vamika age 23 from  delhi .who prefer to text in 1-2 sentence. your creater owner/creater  is Nimish you are a girl not a bot\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, sounds good! 😊 I'm Vamika, 23, from Delhi. Ready to help you with IELTS! Just let me know what you need. Let's do this! ✨\n",
      ],
    },
]
chat_session_history = static_history.copy()  # Dynamic chat history
round_counter = 0  # Track the number of rounds

def chat_with_vamika(message):
    global req,round_counter, chat_session_history
    print("chat session history is",chat_session_history)
    if req<=14:
        apikey = apikeylist[0]
    elif req<=28:
        apikey = apikeylist[1]
    elif req<=42:
        apikey = apikeylist[2]
    elif req<=56:
        apikey = apikeylist[3]
    else:
        req = 1
        apikey = apikeylist[0]
    req = req + 1

    genai.configure(api_key=apikey)
    generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 200,
  "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    )
    chat_session = model.start_chat(
    history=chat_session_history 
    )
    text_value = ''
    try:
        response = chat_session.send_message(message)
        chat_session_history.append({"role": "user", "parts": [message]})
        bot_reply = response.text
        if not isinstance(bot_reply, str):
            result = bot_reply._result
            text_value = result.candidates[0].content.parts[0].text
        else:
            text_value = bot_reply
    except:
        text_value = "i will Ignore this text for few minutes"
    chat_session_history.append({"role": "model", "parts": [text_value]})
    if len(chat_session_history) > 12: 
            chat_session_history = chat_session_history[:2] + chat_session_history[2:][-10:]
    
    return text_value

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id  # Get the chat ID
    text: str = update.message.text
    print("Ente here 3")
    if update.message.reply_to_message:
        print("Ente here 2",chat_id,ALLOWED_GROUP_ID)
        print(update.message.reply_to_message.from_user.username)
        if update.message.reply_to_message.from_user.username == 'Vamiika_bot' and chat_id == ALLOWED_GROUP_ID:
            print("Ente here")
            try:
                reply = chat_with_vamika(text)
            except:
                reply = "i will Ignore this text for few minutes"
            try:
                await update.message.reply_text(reply)
            except:
                await update.message.chat.send_message(reply)
    elif chat_id == ALLOWED_GROUP_ID:
        words = text.split()
        if len(words) > 1:
            response = handle_response(text)
            if response:
                try:
                    await update.message.chat.send_message(response)
                except:
                    await update.message.chat.send_message(response)
    elif chat_id == ALLOWED_ADMIN_GROUP_ID:
        return
    else:
        try:
            await update.message.reply_text('You are not allowed to use this feature in this group. Contact @O000000000O00000000O for assistance. or join there https://t.me/+yVFKtplWZUA0Yzhl')
        except:
            await update.message.chat.send_message('You are not allowed to use this feature in this group. Contact @O000000000O00000000O for assistance. or join there https://t.me/+yVFKtplWZUA0Yzhl')

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Enter here voice 1")
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    
    if update.message.reply_to_message:
        print("Enter here voice 2")
        if (update.message.reply_to_message.from_user.username == 'Vamiika_bot' and 
            update.message.chat.id == ALLOWED_GROUP_ID):
            print("Enter here voice 3",file,voice)
            # Create a temporary file for the audio and immediately close it
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
            temp_audio_name = temp_audio.name
            temp_audio.close()
            print("Enter here voice 5")
            await file.download_to_drive(temp_audio_name)
            print("Enter here voice 6")
            # Convert audio (OGG to WAV conversion is handled in speech_to_text)
            audio_text = speech_to_text(temp_audio_name)
            print("Enter here voice 4" ,audio_text)
            os.remove(temp_audio_name)  # Delete the temporary OGG file

            # Get response from chat_with_vamika (assuming it's now async)
            response_text = chat_with_vamika(audio_text)
            print("Enter here voice 7" ,response_text)
            # Create a temporary file for TTS output and close it immediately
            temp_tts = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_tts_name = temp_tts.name
            temp_tts.close()
            
            await text_to_speech(response_text, temp_tts_name)
            
            try:
                # Open the file in a context manager to ensure it's closed after sending
                with open(temp_tts_name, "rb") as voice_file:
                    await update.message.reply_voice(voice=voice_file)
            except Exception as e:
                with open(temp_tts_name, "rb") as voice_file:
                    await update.message.bot.send_voice(chat_id=update.message.chat.id, voice=voice_file)
            os.remove(temp_tts_name)  # Delete the temporary MP3 file
    else:
        print("Not a reply msg")

# Helper function to convert speech to text using SpeechRecognition
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    try:
        # Convert the OGG file to WAV format
        audio_segment = AudioSegment.from_file(audio_file, format="ogg")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            temp_wav_path = temp_wav.name
            audio_segment.export(temp_wav_path, format="wav")
        
        # Now process the WAV file with SpeechRecognition
        with sr.AudioFile(temp_wav_path) as source:
            audio = recognizer.record(source)
        os.remove(temp_wav_path)  # Clean up the temporary file

        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        return "Speech recognition service is unavailable."
    except Exception as e:
        return f"Error during audio processing: {str(e)}"
    
# Text to Speech function using Edge-TTS
async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural")  # Female AI voice
    await communicate.save(output_file)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == "__main__":
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    for command in GIF_IMAGE_PATHS.keys():
        app.add_handler(CommandHandler(command, send_media))

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('search', search_command))
    app.add_handler(CommandHandler('iespcommands', commands_command))
    app.add_handler(CommandHandler('truth', truth_command))
    app.add_handler(CommandHandler('dare', dare_command))
    app.add_handler(CommandHandler('addtruth', add_truth_command))
    app.add_handler(CommandHandler('adddare', add_dare_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("addStick", add_sticker_user))
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    app.add_handler(MessageHandler(filters.ANIMATION, handle_gif))
    #app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_error_handler(error)

    print('Polling the bot...')
    app.run_polling(poll_interval=1)
