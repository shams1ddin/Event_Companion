# bot.py
# Основной файл бота

import telebot
 
from config import BOT_TOKEN, ADMIN_PASSWORD
from database import *
from texts import get_text
from keyboards import *

# Создаём бота
bot = telebot.TeleBot(BOT_TOKEN)

# Храним временные данные пользователей
user_states = {}

# === КОМАНДЫ ===

@bot.message_handler(commands=['start'])
def start_command(message):
    """Команда /start - начало работы"""
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        # Новый пользователь - выбираем язык
        create_user(user_id)
        bot.send_message(
            message.chat.id,
            "🌍 Please choose your language | Выберите язык | Tilni tanlang:",
            reply_markup=language_keyboard()
        )
    else:
        # Пользователь уже есть - показываем главное меню
        lang = user[1]  # language column
        bot.send_message(
            message.chat.id,
            get_text(lang, 'welcome'),
            reply_markup=main_menu_keyboard(lang)
        )

# @bot.message_handler(content_types=['photo'])
# def get_id_of_photo(message):
#     """Получение ID фотографии"""
#     photo = message.photo[-1]
#     file_id = photo.file_id
#     bot.send_message(message.chat.id, f"Photo ID: {file_id}")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Команда /admin - вход в админку"""
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    if is_admin(user_id):
        # Уже админ
        bot.send_message(
            message.chat.id,
            get_text(lang, 'admin_welcome'),
            reply_markup=admin_keyboard(lang)
        )
    else:
        # Просим ввести пароль
        msg = bot.send_message(message.chat.id, get_text(lang, 'admin_login'))
        bot.register_next_step_handler(msg, check_admin_password)

def check_admin_password(message):
    """Проверка пароля администратора"""
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    if message.text == ADMIN_PASSWORD:
        set_admin(user_id)
        bot.send_message(
            message.chat.id,
            get_text(lang, 'admin_welcome'),
            reply_markup=admin_keyboard(lang)
        )
    else:
        bot.send_message(message.chat.id, get_text(lang, 'wrong_password'))

# === ОБРАБОТКА КНОПОК (Callback) ===

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def language_callback(call):
    """Выбор языка"""
    user_id = call.from_user.id
    lang = call.data.split('_')[1]
    
    update_user_language(user_id, lang)
    
    bot.edit_message_text(
        get_text(lang, 'welcome'),
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_message(
        call.message.chat.id,
        get_text(lang, 'main_menu'),
        reply_markup=main_menu_keyboard(lang)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'back_main')
def back_to_main(call):
    """Возврат в главное меню"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    bot.edit_message_text(
        get_text(lang, 'main_menu'),
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data == 'back_meetings')
def back_to_meetings(call):
    """Возврат к списку встреч"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meetings = get_all_meetings()
    if meetings:
        bot.edit_message_text(
            get_text(lang, 'select_meeting'),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=meetings_keyboard(meetings, lang)
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('meeting_') and not call.data.startswith('meeting_details'))
def meeting_callback(call):
    """Показать детали встречи"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[1])
    meeting = get_meeting(meeting_id)
    
    if meeting:
        is_following = is_participant(meeting_id, user_id)
        text = get_text(
            lang, 
            'meeting_details',
            name=meeting[1],  # name
            location=meeting[2] or 'N/A',  # location
            date=meeting[3] or 'N/A'  # date
        )
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=meeting_details_keyboard(meeting_id, lang, is_following=is_following)
        )
        try:
            bot.send_message(call.message.chat.id, " ", reply_markup=telebot.types.ReplyKeyboardRemove())
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('agenda_') and not call.data.startswith('agenda_item_') and not call.data.startswith('agenda_alert_toggle_') and not call.data.startswith('agenda_skip_desc'))
def agenda_callback(call):
    """Показать повестку дня"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[1])
    agenda_items = get_agenda(meeting_id)
    
    text = f"📋 {get_text(lang, 'agenda')}\n"
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=user_agenda_list_keyboard(meeting_id, agenda_items or [], lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('agenda_item_'))
def agenda_item_view_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[2])
    meeting_id = int(parts[3])
    items = get_agenda(meeting_id)
    item = next((i for i in items if i[0] == agenda_id), None)
    if item:
        title = item[2] or ''
        start = item[3] or ''
        end = item[4] or ''
        desc = item[5] or ''
        text = f"🕐 {start}–{end} • {title}\n" + (f"{desc}" if desc else '')
    else:
        text = get_text(lang, 'error')
    subscribed = is_agenda_alerted(agenda_id, user_id)
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=user_agenda_item_keyboard(agenda_id, meeting_id, subscribed, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('agenda_alert_toggle_'))
def agenda_alert_toggle_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[3])
    meeting_id = int(parts[4])
    if is_agenda_alerted(agenda_id, user_id):
        remove_agenda_alert(agenda_id, user_id)
        bot.answer_callback_query(call.id, get_text(lang, 'alert_off'))
    else:
        add_agenda_alert(agenda_id, user_id)
        bot.answer_callback_query(call.id, get_text(lang, 'alert_on'))
    # Refresh view
    items = get_agenda(meeting_id)
    item = next((i for i in items if i[0] == agenda_id), None)
    if item:
        title = item[2] or ''
        start = item[3] or ''
        end = item[4] or ''
        desc = item[5] or ''
        text = f"🕐 {start}–{end} • {title}\n" + (f"{desc}" if desc else '')
    else:
        text = get_text(lang, 'error')
    subscribed = is_agenda_alerted(agenda_id, user_id)
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=user_agenda_item_keyboard(agenda_id, meeting_id, subscribed, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('wifi_'))
def wifi_callback(call):
    """Показать WiFi пароль"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[1])
    meeting = get_meeting(meeting_id)
    
    if meeting and meeting[4]:  # wifi_network
        text = get_text(
            lang,
            'wifi_info',
            network=meeting[4],
            password=meeting[5] or 'N/A'
        )
    else:
        text = get_text(lang, 'no_wifi_info')
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=back_to_meeting_keyboard(meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('pdf_'))
def pdf_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[1])
    file_id = get_meeting_pdf(meeting_id)
    if file_id:
        try:
            bot.send_document(call.message.chat.id, file_id)
        except:
            pass
        bot.send_message(call.message.chat.id, get_text(lang, 'pdf_info'), reply_markup=back_to_meeting_keyboard(meeting_id, lang))
    else:
        bot.edit_message_text(get_text(lang, 'no_pdf_user'), call.message.chat.id, call.message.message_id, reply_markup=back_to_meeting_keyboard(meeting_id, lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith('qna_'))
def qna_callback(call):
    """Q&A секция"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[1])
    user_states[user_id] = {'state': 'asking_question', 'meeting_id': meeting_id}
    
    bot.edit_message_text(
        get_text(lang, 'ask_question'),
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('people_'))
def people_callback(call):
    """Список участников"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[1])
    participants = get_participants(meeting_id)
    
    text = f"👥 {get_text(lang, 'people')}\n\n"
    if participants:
        for p in participants:
            name = p[1] if p[1] else 'No name'
            phone = p[2] if p[2] else 'N/A'
            company = p[3] if p[3] else 'N/A'
            text += f"👤 {name}\n📞 {phone}\n🏢 {company}\n\n"
    else:
        text += get_text(lang, 'no_participants')
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=back_to_meeting_keyboard(meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('follow_'))
def follow_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[1])
    if not user or not user[2] or not user[3] or not user[4]:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, get_text(lang, 'fill_profile_first'), reply_markup=fill_profile_first_keyboard(lang))
        return
    add_participant(meeting_id, user_id)
    meeting = get_meeting(meeting_id)
    text = get_text(lang, 'meeting_details', name=meeting[1], location=meeting[2] or 'N/A', date=meeting[3] or 'N/A')
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=meeting_details_keyboard(meeting_id, lang, is_following=True)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('unfollow_'))
def unfollow_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[1])
    remove_participant(meeting_id, user_id)
    meeting = get_meeting(meeting_id)
    text = get_text(lang, 'meeting_details', name=meeting[1], location=meeting[2] or 'N/A', date=meeting[3] or 'N/A')
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=meeting_details_keyboard(meeting_id, lang, is_following=False)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('rate_'))
def rate_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    meeting_id = int(parts[1])
    rating = parts[2]
    add_feedback(meeting_id, user_id, rating)
    bot.edit_message_text(
        get_text(lang, 'feedback_prompt'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=yes_no_keyboard(meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('feedback_yes_'))
def feedback_yes_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    user_states[user_id] = {'state': 'meeting_feedback', 'meeting_id': meeting_id}
    bot.edit_message_text(
        get_text(lang, 'enter_feedback'),
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('feedback_no_'))
def feedback_no_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    bot.edit_message_text(
        get_text(lang, 'thank_you'),
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('photos_'))
def photos_callback(call):
    """Фотографии"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[1])
    photos = get_photos(meeting_id)
    
    if photos:
        # Отправляем фотографии
        for photo in photos:
            try:
                bot.send_photo(call.message.chat.id, photo)
            except:
                pass
        bot.send_message(
            call.message.chat.id,
            f"📸 {get_text(lang, 'photos')} ({len(photos)})",
            reply_markup=back_to_meeting_keyboard(meeting_id, lang)
        )
    else:
        text = f"📸 {get_text(lang, 'photos')}\n\n"
        text += get_text(lang, 'no_photos_user')
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_to_meeting_keyboard(meeting_id, lang)
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('map_'))
def map_callback(call):
    """Карта"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[1])
    meeting = get_meeting(meeting_id)
    
    if meeting and meeting[6] and meeting[7]:  # latitude and longitude
        # Отправляем геолокацию
        bot.send_location(call.message.chat.id, meeting[6], meeting[7])
        bot.send_message(
            call.message.chat.id,
            f"🗺 {get_text(lang, 'live_map')}",
            reply_markup=back_to_meeting_keyboard(meeting_id, lang)
        )
    else:
        text = f"🗺 {get_text(lang, 'live_map')}\n\n"
        text += get_text(lang, 'geo_not_set')
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_to_meeting_keyboard(meeting_id, lang)
        )

# === АДМИН CALLBACKS ===

@bot.callback_query_handler(func=lambda call: call.data == 'admin_add_meeting')
def admin_add_meeting_callback(call):
    """Добавление встречи"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    user_states[user_id] = {'state': 'creating_meeting', 'step': 'name'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_meeting_name'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data == 'admin_manage')
def admin_manage_callback(call):
    """Управление встречами"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meetings = get_all_meetings()
    if meetings:
        bot.edit_message_text(
            get_text(lang, 'manage_meetings'),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_meetings_keyboard(meetings, lang)
        )
    else:
        bot.answer_callback_query(call.id, get_text(lang, 'no_meetings'))

@bot.callback_query_handler(func=lambda call: call.data == 'admin_feedback_main')
def admin_feedback_main_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meetings = get_finished_meetings()
    header = get_text(lang, 'finished_meetings')
    if meetings:
        bot.edit_message_text(
            header,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_feedback_finished_meetings_keyboard(meetings, lang)
        )
    else:
        bot.edit_message_text(
            f"{header}\n\n{get_text(lang, 'no_meetings')}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_feedback_finished_meetings_keyboard([], lang)
        )

    

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_feedback_view_'))
def admin_feedback_view_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    meeting_id = int(parts[3])
    feedbacks = get_feedback_for_meeting(meeting_id)
    count_bad = sum(1 for f in feedbacks if f[1] == 'bad')
    count_good = sum(1 for f in feedbacks if f[1] == 'good')
    count_neutral = sum(1 for f in feedbacks if f[1] == 'neutral')
    text = f"💬 {get_text(lang, 'view_feedback')}\n\n"
    text += f"😡: {count_bad}  🤩: {count_good}  😐: {count_neutral}\n\n"
    detailed = [f for f in feedbacks if f[2]]
    if detailed:
        text += "📝 " + get_text(lang, 'view_feedback') + "\n"
        for f in detailed[:50]:
            text += f"• {f[2]}\n"
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_feedback_back_to_list_keyboard(lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_meeting_'))
def admin_meeting_manage_callback(call):
    """Управление конкретной встречей"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[2])
    meeting = get_meeting(meeting_id)
    
    if meeting:
        text = f"⚙️ {meeting[1]}\n\n{get_text(lang, 'choose_action')}"
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_meeting_manage_keyboard(meeting_id, lang)
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_edit_name_'))
def admin_edit_name_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'admin_edit_meeting', 'meeting_id': meeting_id, 'field': 'name'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_meeting_name'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_edit_date_'))
def admin_edit_date_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'admin_edit_meeting', 'meeting_id': meeting_id, 'field': 'date'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_date'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_edit_location_'))
def admin_edit_location_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'admin_edit_meeting', 'meeting_id': meeting_id, 'field': 'location'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_location'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_feedback_'))
def admin_feedback_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    feedbacks = get_feedback_for_meeting(meeting_id)
    count_bad = sum(1 for f in feedbacks if f[1] == 'bad')
    count_good = sum(1 for f in feedbacks if f[1] == 'good')
    count_neutral = sum(1 for f in feedbacks if f[1] == 'neutral')
    text = "💬 Отзывы\n\n"
    text += f"😡: {count_bad}  🤩: {count_good}  😐: {count_neutral}\n\n"
    detailed = [f for f in feedbacks if f[2]]
    if detailed:
        text += "📝 Детальные отзывы:\n"
        for f in detailed[:50]:
            text += f"• {f[2]}\n"
    else:
        text += "📝 Пока нет детальных отзывов"
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_feedback_keyboard(meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_questions_meeting_'))
def admin_questions_meeting_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    questions = get_questions(meeting_id)
    text = f"❓ {get_text(lang, 'view_questions')}\n\n"
    if questions:
        for q in questions:
            text += f"• {q[3]} ({q[4]})\n"
    else:
        text += get_text(lang, 'no_questions')
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_questions_back_keyboard(lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_finished_'))
def view_finished_meeting_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    meeting = get_meeting(meeting_id)
    if meeting:
        text = get_text(lang, 'meeting_details', name=meeting[1], location=meeting[2] or 'N/A', date=meeting[3] or 'N/A')
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=finished_meeting_back_to_survey_keyboard(meeting_id, lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_survey_'))
def back_survey_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    bot.edit_message_text(
        get_text(lang, 'satisfaction_prompt'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=satisfaction_keyboard(meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_finish_'))
def admin_finish_entry_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    bot.edit_message_text(
        get_text(lang, 'confirm_finish_meeting'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=finish_confirm_keyboard(meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('finish_confirm_'))
def finish_confirm_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    bot.edit_message_text(
        get_text(lang, 'confirm_finish_meeting'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=finish_confirm_keyboard(meeting_id, lang)
    )

def send_satisfaction_survey(meeting_id):
    participants = get_participant_user_ids(meeting_id)
    for uid in participants:
        try:
            user = get_user(uid)
            lang = user[1] if user else 'en'
            bot.send_message(uid, get_text(lang, 'satisfaction_prompt'), reply_markup=satisfaction_keyboard(meeting_id, lang))
        except Exception as e:
            print(f"Ошибка отправки опроса пользователю {uid}: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('finish_yes_'))
def finish_yes_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    mark_meeting_ended(meeting_id)
    send_satisfaction_survey(meeting_id)
    bot.answer_callback_query(call.id, get_text(lang, 'finish_meeting'))
    meetings = get_all_meetings()
    bot.edit_message_text(
        get_text(lang, 'manage_meetings'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_meetings_keyboard(meetings, lang)
    )

# удалены обработчики дедлайна

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_wifi_'))
def admin_wifi_view_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    meeting = get_meeting(meeting_id)
    has_wifi = bool(meeting and meeting[4])
    if has_wifi:
        text = get_text(lang, 'wifi_info', network=meeting[4], password=meeting[5] or 'N/A')
    else:
        text = get_text(lang, 'no_wifi_info')
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_wifi_view_keyboard(meeting_id, lang, has_wifi)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_wifi_edit_'))
def admin_wifi_edit_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'editing_wifi', 'meeting_id': meeting_id, 'step': 'name'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_wifi_name'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_wifi_edit_name_'))
def admin_wifi_edit_name_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[4])
    user_states[user_id] = {'state': 'editing_wifi_single', 'meeting_id': meeting_id, 'field': 'name'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_wifi_name'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_wifi_edit_password_'))
def admin_wifi_edit_password_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[4])
    user_states[user_id] = {'state': 'editing_wifi_single', 'meeting_id': meeting_id, 'field': 'password'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_wifi_password'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_wifi_clear_'))
def admin_wifi_clear_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    clear_wifi(meeting_id)
    bot.edit_message_text(
        get_text(lang, 'wifi_cleared'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_wifi_view_keyboard(meeting_id, lang, False)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_photos_') and not call.data.startswith('admin_photos_add_') and not call.data.startswith('admin_photos_clear_'))
def admin_photos_view_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    photos = get_photos(meeting_id)
    has_photos = bool(photos)
    if has_photos:
        for photo in photos:
            try:
                bot.send_photo(call.message.chat.id, photo)
            except:
                pass
        bot.send_message(
            call.message.chat.id,
            f"📸 {get_text(lang, 'photos')} ({len(photos)})",
            reply_markup=admin_photos_view_keyboard(meeting_id, lang, has_photos)
        )
    else:
        bot.edit_message_text(
            get_text(lang, 'no_photos_admin'),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_photos_view_keyboard(meeting_id, lang, False)
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_photos_add_'))
def admin_photos_add_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'adding_photos', 'meeting_id': meeting_id}
    bot.send_message(call.message.chat.id, get_text(lang, 'send_photos'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_pdf_') and not call.data.startswith('admin_pdf_add_') and not call.data.startswith('admin_pdf_edit_') and not call.data.startswith('admin_pdf_clear_') and len(call.data.split('_')) == 3)
def admin_pdf_view_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[-1])
    file_id = get_meeting_pdf(meeting_id)
    has_pdf = bool(file_id)
    if has_pdf:
        try:
            bot.send_document(call.message.chat.id, file_id)
        except:
            pass
        bot.send_message(call.message.chat.id, get_text(lang, 'pdf_info'), reply_markup=admin_pdf_view_keyboard(meeting_id, lang, True))
    else:
        bot.edit_message_text(get_text(lang, 'no_pdf_admin'), call.message.chat.id, call.message.message_id, reply_markup=admin_pdf_view_keyboard(meeting_id, lang, False))

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_pdf_add_'))
def admin_pdf_add_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'adding_pdf', 'meeting_id': meeting_id}
    bot.send_message(call.message.chat.id, get_text(lang, 'send_pdf'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_pdf_edit_'))
def admin_pdf_edit_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'editing_pdf', 'meeting_id': meeting_id}
    bot.send_message(call.message.chat.id, get_text(lang, 'send_pdf'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_pdf_clear_'))
def admin_pdf_clear_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    bot.edit_message_text(get_text(lang, 'confirm_delete_pdf'), call.message.chat.id, call.message.message_id, reply_markup=admin_pdf_delete_confirm_keyboard(meeting_id, lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_pdf_delete_confirm_yes_'))
def admin_pdf_delete_confirm_yes_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[-1])
    clear_pdf(meeting_id)
    bot.edit_message_text(get_text(lang, 'pdf_deleted'), call.message.chat.id, call.message.message_id, reply_markup=admin_pdf_view_keyboard(meeting_id, lang, False))

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_photos_clear_'))
def admin_photos_clear_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    clear_photos(meeting_id)
    bot.edit_message_text(
        get_text(lang, 'photos_cleared'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_photos_view_keyboard(meeting_id, lang, False)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_geo_') and not call.data.startswith('admin_geo_edit_') and not call.data.startswith('admin_geo_clear_'))
def admin_geo_view_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    meeting = get_meeting(meeting_id)
    has_geo = bool(meeting and meeting[6] and meeting[7])
    if has_geo:
        bot.send_location(call.message.chat.id, meeting[6], meeting[7])
        bot.send_message(
            call.message.chat.id,
            get_text(lang, 'live_map'),
            reply_markup=admin_geo_view_keyboard(meeting_id, lang, True)
        )
    else:
        bot.edit_message_text(
            get_text(lang, 'geo_not_set'),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_geo_view_keyboard(meeting_id, lang, False)
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_geo_edit_'))
def admin_geo_edit_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'adding_geo', 'meeting_id': meeting_id}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_geo_admin'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_geo_clear_'))
def admin_geo_clear_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    clear_geo(meeting_id)
    bot.edit_message_text(
        get_text(lang, 'geo_cleared'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_geo_view_keyboard(meeting_id, lang, False)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_') and not call.data.startswith('admin_agenda_add_') and not call.data.startswith('admin_agenda_clear_') and not call.data.startswith('admin_agenda_item_'))
def admin_agenda_view_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    items = get_agenda(meeting_id)
    text = f"📋 {get_text(lang, 'agenda')}\n\n"
    has_items = bool(items)
    if has_items:
        for item in items:
            title = item[2] or ''
            start = item[3] or ''
            end = item[4] or ''
            desc = item[5] or ''
            line = f"🕐 {start}–{end} • {title}".strip()
            text += line + (f"\n{desc}\n" if desc else "\n")
    else:
        text += get_text(lang, 'no_agenda_admin')
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_agenda_items_list_keyboard(meeting_id, items, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_add_'))
def admin_agenda_add_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    user_states[user_id] = {'state': 'adding_agenda', 'meeting_id': meeting_id, 'step': 'title'}
    bot.send_message(call.message.chat.id, get_text(lang, 'agenda_title'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_clear_'))
def admin_agenda_clear_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[3])
    clear_agenda(meeting_id)
    bot.edit_message_text(
        get_text(lang, 'agenda_cleared'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_agenda_items_list_keyboard(meeting_id, [], lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_delete_'))
def admin_agenda_item_delete_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[4])
    meeting_id = int(parts[5])
    bot.edit_message_text(
        get_text(lang, 'delete_agenda_confirm'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_agenda_item_delete_confirm_keyboard(agenda_id, meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_delete_confirm_'))
def admin_agenda_item_delete_confirm_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[5])
    meeting_id = int(parts[6])
    delete_agenda_item(agenda_id)
    items = get_agenda(meeting_id)
    text = f"📋 {get_text(lang, 'agenda')}\n\n{get_text(lang, 'agenda_item_deleted')}\n\n"
    if items:
        for item in items:
            title = item[2] or ''
            start = item[3] or ''
            end = item[4] or ''
            desc = item[5] or ''
            line = f"🕐 {start}–{end} • {title}".strip()
            text += line + (f"\n{desc}\n" if desc else "\n")
    else:
        text += get_text(lang, 'no_agenda_admin')
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_agenda_items_list_keyboard(meeting_id, items, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_edit_') and not call.data.startswith('admin_agenda_item_edit_title_') and not call.data.startswith('admin_agenda_item_edit_start_') and not call.data.startswith('admin_agenda_item_edit_end_') and not call.data.startswith('admin_agenda_item_edit_desc_'))
def admin_agenda_item_edit_menu_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[4])
    meeting_id = int(parts[5])
    bot.edit_message_text(
        get_text(lang, 'edit_agenda'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_agenda_item_edit_keyboard(agenda_id, meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_edit_title_'))
def admin_agenda_item_edit_title_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[5])
    meeting_id = int(parts[6])
    user_states[user_id] = {'state': 'editing_agenda_item', 'agenda_id': agenda_id, 'meeting_id': meeting_id, 'field': 'title'}
    bot.edit_message_text(get_text(lang, 'edit_agenda_title'), call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_people_'))
def admin_agenda_item_people_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[4])
    meeting_id = int(parts[5])
    rows = get_agenda_alert_users(agenda_id)
    text = f"👥 {get_text(lang, 'people')}\n\n"
    if rows:
        for p in rows:
            name = p[1] if p[1] else 'No name'
            phone = p[2] if p[2] else 'N/A'
            company = p[3] if p[3] else 'N/A'
            text += f"👤 {name}\n📞 {phone}\n🏢 {company}\n\n"
    else:
        text += get_text(lang, 'no_alert_subscribers')
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_agenda_people_back_keyboard(meeting_id, lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_edit_start_'))
def admin_agenda_item_edit_start_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[5])
    meeting_id = int(parts[6])
    user_states[user_id] = {'state': 'editing_agenda_item', 'agenda_id': agenda_id, 'meeting_id': meeting_id, 'field': 'start_time'}
    bot.edit_message_text(get_text(lang, 'edit_agenda_start'), call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_edit_end_'))
def admin_agenda_item_edit_end_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[5])
    meeting_id = int(parts[6])
    user_states[user_id] = {'state': 'editing_agenda_item', 'agenda_id': agenda_id, 'meeting_id': meeting_id, 'field': 'end_time'}
    bot.edit_message_text(get_text(lang, 'edit_agenda_end'), call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_edit_desc_'))
def admin_agenda_item_edit_desc_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[5])
    meeting_id = int(parts[6])
    user_states[user_id] = {'state': 'editing_agenda_item', 'agenda_id': agenda_id, 'meeting_id': meeting_id, 'field': 'description'}
    bot.edit_message_text(get_text(lang, 'edit_agenda_desc'), call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_agenda_item_') and not call.data.startswith('admin_agenda_item_edit_') and not call.data.startswith('admin_agenda_item_delete_'))
def admin_agenda_item_select_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    parts = call.data.split('_')
    agenda_id = int(parts[3])
    meeting_id = int(parts[4])
    bot.edit_message_text(
        get_text(lang, 'edit_agenda'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_agenda_item_actions_keyboard(agenda_id, meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'agenda_skip_desc')
def agenda_skip_desc_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    state = user_states.get(user_id) or {}
    if state.get('state') == 'adding_agenda' and state.get('step') == 'description':
        meeting_id = state.get('meeting_id')
        add_agenda_item_extended(meeting_id, state.get('title'), state.get('start_time'), state.get('end_time'), '')
        del user_states[user_id]
        bot.edit_message_text(get_text(lang, 'agenda_added'), call.message.chat.id, call.message.message_id)
        items = get_agenda(meeting_id)
        text_block = f"📋 {get_text(lang, 'agenda')}\n\n"
        if items:
            for item in items:
                title = item[2] or ''
                start = item[3] or ''
                end = item[4] or ''
                desc = item[5] or ''
                line = f"🕐 {start}–{end} • {title}".strip()
                text_block += line + (f"\n{desc}\n" if desc else "\n")
        else:
            text_block += get_text(lang, 'no_agenda_admin')
        bot.send_message(call.message.chat.id, text_block, reply_markup=admin_agenda_items_list_keyboard(meeting_id, items, lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_delete_'))
def admin_delete_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    bot.edit_message_text(
        get_text(lang, 'confirm_delete_meeting'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_delete_confirm_keyboard(meeting_id, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def admin_confirm_delete_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    delete_meeting(meeting_id)
    meetings = get_all_meetings()
    if meetings:
        bot.edit_message_text(
            get_text(lang, 'manage_meetings') + f"\n\n{get_text(lang, 'meeting_deleted')}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_meetings_keyboard(meetings, lang)
        )
    else:
        bot.edit_message_text(
            get_text(lang, 'meeting_deleted') + "\n" + get_text(lang, 'no_meetings'),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_meetings_keyboard([], lang)
        )
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_wifi_'))
def add_wifi_callback(call):
    """Добавить WiFi"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[2])
    user_states[user_id] = {'state': 'adding_wifi', 'meeting_id': meeting_id, 'step': 'name'}
    
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_wifi_name'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_photos_'))
def add_photos_callback(call):
    """Добавить фотографии"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    meeting_id = int(call.data.split('_')[2])
    user_states[user_id] = {'state': 'adding_photos', 'meeting_id': meeting_id}
    
    text = f"{get_text(lang, 'send_photos')}"
    bot.send_message(call.message.chat.id, text, reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data == 'admin_questions')
def admin_questions_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meetings = get_all_meetings()
    bot.edit_message_text(
        get_text(lang, 'view_questions'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_questions_meetings_keyboard(meetings, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'admin_notify')
def admin_notify_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meetings = get_all_meetings()
    bot.edit_message_text(
        get_text(lang, 'send_notification'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_notifications_keyboard(meetings, lang)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'notify_all')
def notify_all_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    user_states[user_id] = {'state': 'sending_notification', 'scope': 'all'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_notification'))

@bot.callback_query_handler(func=lambda call: call.data.startswith('notify_meeting_'))
def notify_meeting_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    user_states[user_id] = {'state': 'sending_notification', 'scope': 'meeting', 'meeting_id': meeting_id}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_notification'))

@bot.callback_query_handler(func=lambda call: call.data == 'notify_none')
def notify_none_callback(call):
    try:
        bot.answer_callback_query(call.id, get_text(get_user(call.from_user.id)[1] if get_user(call.from_user.id) else 'en', 'no_meetings'))
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'back_admin')
def back_to_admin(call):
    """Возврат в админ панель"""
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    bot.edit_message_text(
        get_text(lang, 'admin_welcome'),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_keyboard(lang)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'admin_exit')
def admin_exit_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    unset_admin(user_id)
    bot.edit_message_text(
        get_text(lang, 'main_menu'),
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_message(
        call.message.chat.id,
        get_text(lang, 'main_menu'),
        reply_markup=main_menu_keyboard(lang)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'edit_profile')
def edit_profile_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    bot.send_message(call.message.chat.id, get_text(lang, 'edit_profile'), reply_markup=profile_edit_options_keyboard(lang))
    try:
        bot.send_message(call.message.chat.id, " ", reply_markup=telebot.types.ReplyKeyboardRemove())
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'edit_name')
def edit_name_button_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    user_states[user_id] = {'state': 'editing_profile', 'step': 'name'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_name'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data == 'edit_phone')
def edit_phone_button_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    user_states[user_id] = {'state': 'editing_profile', 'step': 'phone'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_phone'), reply_markup=contact_request_keyboard(lang))

@bot.callback_query_handler(func=lambda call: call.data == 'edit_company')
def edit_company_button_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    user_states[user_id] = {'state': 'editing_profile', 'step': 'company'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_company'), reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data == 'fill_profile')
def fill_profile_button_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    user_states[user_id] = {'state': 'filling_profile', 'step': 'name'}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_name'), reply_markup=telebot.types.ReplyKeyboardRemove())

# === ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ===

@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    text = message.text
    
    # Проверяем состояние пользователя
    if user_id in user_states:
        state = user_states[user_id]
        
        # Задаём вопрос
        if state.get('state') == 'asking_question':
            meeting_id = state.get('meeting_id')
            add_question(meeting_id, user_id, text)
            del user_states[user_id]
            bot.send_message(message.chat.id, get_text(lang, 'question_sent'))
            return
        
        # Создание встречи
        if state.get('state') == 'creating_meeting':
            step = state.get('step')
            
            if step == 'name':
                state['name'] = text
                state['step'] = 'location'
                bot.send_message(message.chat.id, get_text(lang, 'enter_location'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            
            elif step == 'location':
                state['location'] = text
                state['step'] = 'date'
                bot.send_message(message.chat.id, get_text(lang, 'enter_date'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            
            elif step == 'date':
                state['date'] = text
                meeting_id = create_meeting(state['name'], state['location'], state['date'])
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'meeting_created'), reply_markup=main_menu_keyboard(lang))
                return
        
        # Добавление WiFi
        if state.get('state') == 'adding_wifi':
            step = state.get('step')
            meeting_id = state.get('meeting_id')
            
            if step == 'name':
                state['wifi_name'] = text
                state['step'] = 'password'
                bot.send_message(message.chat.id, get_text(lang, 'enter_wifi_password'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            
            elif step == 'password':
                update_wifi(meeting_id, state['wifi_name'], text)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'wifi_added'))
                return
        
        # Добавление фотографий: запрещаем не-фото контент
        if state.get('state') == 'adding_photos':
            bot.send_message(message.chat.id, f"{get_text(lang, 'invalid_photo_format')}\n{get_text(lang, 'send_photos')}")
            return

        if state.get('state') == 'editing_wifi':
            step = state.get('step')
            meeting_id = state.get('meeting_id')
            if step == 'name':
                state['wifi_name'] = text
                state['step'] = 'password'
                bot.send_message(message.chat.id, get_text(lang, 'enter_wifi_password'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            elif step == 'password':
                update_wifi(meeting_id, state['wifi_name'], text)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'wifi_updated'))
                return

        if state.get('state') == 'editing_wifi_single':
            meeting_id = state.get('meeting_id')
            field = state.get('field')
            meeting = get_meeting(meeting_id)
            current_name = meeting[4] if meeting else None
            current_password = meeting[5] if meeting else None
            if field == 'name':
                update_wifi(meeting_id, text, current_password or '')
            elif field == 'password':
                update_wifi(meeting_id, current_name or '', text)
            del user_states[user_id]
            bot.send_message(message.chat.id, get_text(lang, 'wifi_updated'))
            bot.send_message(message.chat.id, get_text(lang, 'admin_wifi'), reply_markup=admin_wifi_view_keyboard(meeting_id, lang, True))
            return

        # Редактирование пункта повестки
        if state.get('state') == 'editing_agenda_item':
            agenda_id = state.get('agenda_id')
            meeting_id = state.get('meeting_id')
            field = state.get('field')
            if field == 'title':
                update_agenda_title(agenda_id, text)
            elif field == 'start_time':
                update_agenda_start_time(agenda_id, text)
            elif field == 'end_time':
                update_agenda_end_time(agenda_id, text)
            elif field == 'description':
                update_agenda_description(agenda_id, text)
            del user_states[user_id]
            items = get_agenda(meeting_id)
            text_block = f"📋 {get_text(lang, 'agenda')}\n\n"
            if items:
                for item in items:
                    title = item[2] or ''
                    start = item[3] or ''
                    end = item[4] or ''
                    desc = item[5] or ''
                    line = f"🕐 {start}–{end} • {title}".strip()
                    text_block += line + (f"\n{desc}\n" if desc else "\n")
            else:
                text_block += get_text(lang, 'no_agenda_admin')
            bot.send_message(message.chat.id, text_block, reply_markup=admin_agenda_items_list_keyboard(meeting_id, items, lang))
            return

        if state.get('state') == 'adding_agenda':
            step = state.get('step')
            meeting_id = state.get('meeting_id')
            if step == 'title':
                state['title'] = text
                state['step'] = 'start_time'
                bot.send_message(message.chat.id, get_text(lang, 'agenda_start_time'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            elif step == 'start_time':
                state['start_time'] = text
                state['step'] = 'end_time'
                bot.send_message(message.chat.id, get_text(lang, 'agenda_end_time'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            elif step == 'end_time':
                state['end_time'] = text
                state['step'] = 'description'
                bot.send_message(message.chat.id, get_text(lang, 'agenda_description_optional'), reply_markup=skip_keyboard(lang))
                return
            elif step == 'description':
                add_agenda_item_extended(meeting_id, state.get('title'), state.get('start_time'), state.get('end_time'), text)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'agenda_added'))
                bot.send_message(message.chat.id, get_text(lang, 'agenda'))
                items = get_agenda(meeting_id)
                text_block = f"📋 {get_text(lang, 'agenda')}\n\n"
                if items:
                    for item in items:
                        title = item[2] or ''
                        start = item[3] or ''
                        end = item[4] or ''
                        desc = item[5] or ''
                        line = f"🕐 {start}–{end} • {title}".strip()
                        text_block += line + (f"\n{desc}\n" if desc else "\n")
                else:
                    text_block += get_text(lang, 'no_agenda_admin')
                bot.send_message(message.chat.id, text_block, reply_markup=admin_agenda_items_list_keyboard(meeting_id, items, lang))
                return
        
        # Отправка уведомления
        if state.get('state') == 'sending_notification':
            scope = state.get('scope')
            recipients = []
            if scope == 'meeting':
                meeting_id = state.get('meeting_id')
                recipients = get_participant_user_ids(meeting_id)
            else:
                users = get_all_users()
                recipients = [u[0] for u in users]
            sent_count = 0
            for uid in recipients:
                try:
                    bot.send_message(uid, f"📢 {text}")
                    sent_count += 1
                except Exception as e:
                    print(f"Ошибка отправки пользователю {uid}: {e}")
            del user_states[user_id]
            bot.send_message(message.chat.id, f"{get_text(lang, 'notification_sent')}\n✅ Отправлено: {sent_count}")
            return

        if state.get('state') == 'meeting_feedback':
            meeting_id = state.get('meeting_id')
            add_feedback(meeting_id, user_id, rating=None, feedback=text)
            del user_states[user_id]
            bot.send_message(message.chat.id, get_text(lang, 'feedback_sent'))
            return

        # Админ: редактирование полей встречи
        if state.get('state') == 'admin_edit_meeting':
            meeting_id = state.get('meeting_id')
            field = state.get('field')
            if field == 'name':
                update_meeting_name(meeting_id, text)
            elif field == 'date':
                update_meeting_date(meeting_id, text)
            elif field == 'location':
                update_meeting_location(meeting_id, text)
            del user_states[user_id]
            bot.send_message(message.chat.id, get_text(lang, 'meeting_updated'))
            meeting = get_meeting(meeting_id)
            header = f"⚙️ {meeting[1]}\n\n{get_text(lang, 'choose_action')}"
            bot.send_message(message.chat.id, header, reply_markup=admin_meeting_manage_keyboard(meeting_id, lang))
            return
        
        # Заполнение профиля
        if state.get('state') == 'filling_profile':
            step = state.get('step')
            
            if step == 'name':
                state['name'] = text
                state['step'] = 'phone'
                bot.send_message(message.chat.id, get_text(lang, 'enter_phone'), reply_markup=contact_request_keyboard(lang))
                return
            
            elif step == 'phone':
                state['phone'] = text
                state['step'] = 'company'
                bot.send_message(message.chat.id, get_text(lang, 'enter_company'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            
            elif step == 'company':
                update_user_profile(user_id, state['name'], state['phone'], text)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'profile_saved'), reply_markup=main_menu_keyboard(lang))
                return

        # Редактирование профиля (по отдельным полям)
        if state.get('state') == 'editing_profile':
            step = state.get('step')
            current = get_user(user_id)
            current_name = current[2] if current else None
            current_phone = current[3] if current else None
            current_company = current[4] if current else None
            if step == 'name':
                update_user_profile(user_id, text, current_phone, current_company)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'profile_saved'), reply_markup=main_menu_keyboard(lang))
                return
            elif step == 'phone':
                update_user_profile(user_id, current_name, text, current_company)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'profile_saved'), reply_markup=main_menu_keyboard(lang))
                return
            elif step == 'company':
                update_user_profile(user_id, current_name, current_phone, text)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'profile_saved'), reply_markup=main_menu_keyboard(lang))
                return
    
    # Обработка кнопок главного меню
    if text == get_text(lang, 'select_meeting'):
        meetings = get_all_meetings()
        if meetings:
            bot.send_message(
                message.chat.id,
                get_text(lang, 'select_meeting'),
                reply_markup=meetings_keyboard(meetings, lang)
            )
        else:
            bot.send_message(message.chat.id, get_text(lang, 'no_meetings'))
    
    elif text == get_text(lang, 'my_profile'):
        if user and user[2]:  # has name
            profile_text = get_text(
                lang,
                'your_profile',
                name=user[2] or 'N/A',
                phone=user[3] or 'N/A',
                company=user[4] or 'N/A'
            )
            bot.send_message(message.chat.id, profile_text, reply_markup=profile_actions_keyboard(lang))
        else:
            user_states[user_id] = {'state': 'filling_profile', 'step': 'name'}
            bot.send_message(message.chat.id, get_text(lang, 'enter_name'), reply_markup=telebot.types.ReplyKeyboardRemove())
    
    
    
    elif text == get_text(lang, 'change_language'):
        bot.send_message(
            message.chat.id,
            get_text(lang, 'choose_language'),
            reply_markup=language_keyboard()
        )

# === ОБРАБОТКА ГЕОЛОКАЦИИ И ФОТО ===

@bot.message_handler(content_types=['location'])
def handle_location(message):
    """Обработка геолокации"""
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    if user_id in user_states:
        state = user_states[user_id]
        
        # Добавление геолокации в админке
        if state.get('state') == 'adding_geo':
            meeting_id = state.get('meeting_id')
            update_location_geo(meeting_id, message.location.latitude, message.location.longitude)
            del user_states[user_id]
            bot.send_message(message.chat.id, get_text(lang, 'geo_added'))

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    if user_id in user_states:
        state = user_states[user_id]
        if state.get('state') in ['filling_profile', 'editing_profile'] and state.get('step') == 'phone':
            phone = message.contact.phone_number
            if state.get('state') == 'filling_profile':
                state['phone'] = phone
                state['step'] = 'company'
                bot.send_message(message.chat.id, get_text(lang, 'enter_company'), reply_markup=telebot.types.ReplyKeyboardRemove())
                return
            else:
                current = get_user(user_id)
                current_name = current[2] if current else None
                current_company = current[4] if current else None
                update_user_profile(user_id, current_name, phone, current_company)
                del user_states[user_id]
                bot.send_message(message.chat.id, get_text(lang, 'profile_saved'), reply_markup=main_menu_keyboard(lang))
                return

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Обработка фотографий"""
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    
    if user_id in user_states:
        state = user_states[user_id]
        
        # Добавление фото к встрече
        if state.get('state') == 'adding_photos':
            meeting_id = state.get('meeting_id')
            # Берём самое большое фото
            photo_id = message.photo[-1].file_id
            add_photo(meeting_id, photo_id)
            del user_states[user_id]
            bot.send_message(message.chat.id, get_text(lang, 'photo_added'))

@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    if user_id in user_states:
        state = user_states[user_id]
        if state.get('state') in ['adding_pdf', 'editing_pdf']:
            doc = message.document
            if doc and (doc.mime_type == 'application/pdf' or (doc.file_name or '').lower().endswith('.pdf')):
                meeting_id = state.get('meeting_id')
                update_pdf(meeting_id, doc.file_id)
                del user_states[user_id]
                msg_key = 'pdf_added' if state.get('state') == 'adding_pdf' else 'pdf_updated'
                bot.send_message(message.chat.id, get_text(lang, msg_key))
            else:
                bot.send_message(message.chat.id, get_text(lang, 'invalid_pdf_format'))

@bot.message_handler(content_types=['video','voice','document','audio','animation','sticker'])
def handle_non_photo_in_photo_mode(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    if user_id in user_states:
        state = user_states[user_id]
        if state.get('state') == 'adding_photos':
            bot.send_message(message.chat.id, f"{get_text(lang, 'invalid_photo_format')}\n{get_text(lang, 'send_photos')}")
            return

# === АДМИН: ДОБАВИТЬ ГЕО и УДАЛИТЬ ВСТРЕЧУ ===

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_geo_'))
def add_geo_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    user_states[user_id] = {'state': 'adding_geo', 'meeting_id': meeting_id}
    bot.send_message(call.message.chat.id, get_text(lang, 'enter_geo_admin'))

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_meeting_'))
def delete_meeting_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    lang = user[1] if user else 'en'
    meeting_id = int(call.data.split('_')[2])
    delete_meeting(meeting_id)
    meetings = get_all_meetings()
    if meetings:
        bot.edit_message_text(
            get_text(lang, 'manage_meetings') + f"\n\n{get_text(lang, 'meeting_deleted')}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_meetings_keyboard(meetings, lang)
        )
    else:
        bot.edit_message_text(
            get_text(lang, 'meeting_deleted') + "\n" + get_text(lang, 'no_meetings'),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=admin_meetings_keyboard([], lang)
        )

# === ЗАПУСК БОТА ===

if __name__ == '__main__':
    print("🤖 Бот запущен...")
    init_database()
    init_feedback_table()
    bot.infinity_polling()
