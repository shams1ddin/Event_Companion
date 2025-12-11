from telebot import types
from texts import get_text

def language_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")
    )
    return kb


def main_menu_keyboard(lang='en'):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(get_text(lang, 'select_meeting'))
    kb.row(
        get_text(lang, 'my_profile'),
        get_text(lang, 'change_language')
    )
    return kb

def profile_actions_keyboard(lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'edit_profile'), callback_data="edit_profile"),
        types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_main")
    )
    return kb

def profile_edit_options_keyboard(lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton(get_text(lang, 'edit_name_button'), callback_data="edit_name"),
        types.InlineKeyboardButton(get_text(lang, 'edit_phone_button'), callback_data="edit_phone"),
        types.InlineKeyboardButton(get_text(lang, 'edit_company_button'), callback_data="edit_company")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_main"))
    return kb

def fill_profile_first_keyboard(lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton(get_text(lang, 'fill_profile_button'), callback_data="fill_profile"),
        types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_main")
    )
    return kb

def contact_request_keyboard(lang='en'):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(types.KeyboardButton(get_text(lang, 'send_contact_button'), request_contact=True))
    return kb


def meetings_keyboard(meetings, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for m in meetings:
        kb.add(types.InlineKeyboardButton(f"{m[1]}", callback_data=f"meeting_{m[0]}"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_main"))
    return kb


def meeting_details_keyboard(meeting_id, lang='en', has_agenda=False, has_people=False, has_photos=False, has_wifi=False, has_map=False, is_following=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(get_text(lang, 'unfollow') if is_following else get_text(lang, 'follow'), callback_data=(f"unfollow_{meeting_id}" if is_following else f"follow_{meeting_id}"))
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'agenda') + (' ✅' if has_agenda else ''), callback_data=f"agenda_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'people') + (' ✅' if has_people else ''), callback_data=f"people_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'photos') + (' ✅' if has_photos else ''), callback_data=f"photos_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'wifi') + (' ✅' if has_wifi else ''), callback_data=f"wifi_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'qna'), callback_data=f"qna_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'live_map') + (' ✅' if has_map else ''), callback_data=f"map_{meeting_id}")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'pdf_info'), callback_data=f"pdf_{meeting_id}"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_meetings"))
    return kb


def back_to_meeting_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"meeting_{meeting_id}"))
    return kb

def user_agenda_list_keyboard(meeting_id, items, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for item in items:
        agenda_id = item[0]
        title = item[2] or ''
        start = item[3] or ''
        end = item[4] or ''
        label = f"🕐 {start}–{end} • {title}".strip()
        kb.add(types.InlineKeyboardButton(label, callback_data=f"agenda_item_{agenda_id}_{meeting_id}"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"meeting_{meeting_id}"))
    return kb

def user_agenda_item_keyboard(agenda_id, meeting_id, is_subscribed, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    alert_label = get_text(lang, 'alert') + (" ✅" if is_subscribed else "")
    kb.row(
        types.InlineKeyboardButton(alert_label, callback_data=f"agenda_alert_toggle_{agenda_id}_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"agenda_{meeting_id}")
    )
    return kb



def admin_keyboard(lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton(get_text(lang, 'add_meeting'), callback_data="admin_add_meeting"),
        types.InlineKeyboardButton(get_text(lang, 'manage_meetings'), callback_data="admin_manage"),
        types.InlineKeyboardButton(get_text(lang, 'view_feedback'), callback_data="admin_feedback_main"),
        types.InlineKeyboardButton(get_text(lang, 'view_questions'), callback_data="admin_questions"),
        types.InlineKeyboardButton(get_text(lang, 'send_notification'), callback_data="admin_notify")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'exit_admin'), callback_data="admin_exit"))
    return kb


def admin_meetings_keyboard(meetings, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for m in meetings:
        kb.add(types.InlineKeyboardButton(f"{m[1]}", callback_data=f"admin_meeting_{m[0]}"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_admin"))
    return kb

def admin_notifications_keyboard(meetings, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if meetings:
        for m in meetings:
            kb.add(types.InlineKeyboardButton(f"{m[1]}", callback_data=f"notify_meeting_{m[0]}"))
    else:
        kb.add(types.InlineKeyboardButton(get_text(lang, 'no_meetings'), callback_data="notify_none"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'send_all_users'), callback_data="notify_all"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_admin"))
    return kb


def admin_meeting_manage_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(get_text(lang, 'edit_meeting_name'), callback_data=f"admin_edit_name_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'edit_meeting_date'), callback_data=f"admin_edit_date_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'edit_meeting_location'), callback_data=f"admin_edit_location_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'admin_wifi'), callback_data=f"admin_wifi_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'admin_photos'), callback_data=f"admin_photos_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'admin_geo'), callback_data=f"admin_geo_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'admin_agenda'), callback_data=f"admin_agenda_{meeting_id}")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'admin_pdf'), callback_data=f"admin_pdf_{meeting_id}"))
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'admin_finish_meeting'), callback_data=f"admin_finish_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'admin_delete_meeting'), callback_data=f"admin_delete_{meeting_id}")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="admin_manage"))
    return kb

def satisfaction_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.row(
        types.InlineKeyboardButton("😡", callback_data=f"rate_{meeting_id}_bad"),
        types.InlineKeyboardButton("🤩", callback_data=f"rate_{meeting_id}_good"),
        types.InlineKeyboardButton("😐", callback_data=f"rate_{meeting_id}_neutral")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'view_meeting'), callback_data=f"view_finished_{meeting_id}"))
    return kb

def yes_no_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'yes'), callback_data=f"feedback_yes_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'no'), callback_data=f"feedback_no_{meeting_id}")
    )
    return kb

def admin_questions_meetings_keyboard(meetings, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if meetings:
        for m in meetings:
            kb.add(types.InlineKeyboardButton(f"{m[1]}", callback_data=f"admin_questions_meeting_{m[0]}"))
    else:
        kb.add(types.InlineKeyboardButton(get_text(lang, 'no_meetings'), callback_data="notify_none"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_admin"))
    return kb

def finish_meeting_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'finish_meeting'), callback_data=f"finish_confirm_{meeting_id}"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def finished_meeting_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'agenda'), callback_data=f"agenda_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'people'), callback_data=f"people_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'photos'), callback_data=f"photos_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'wifi'), callback_data=f"wifi_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'qna'), callback_data=f"qna_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'live_map'), callback_data=f"map_{meeting_id}")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_main"))
    return kb

def finished_meeting_back_to_survey_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'agenda'), callback_data=f"agenda_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'people'), callback_data=f"people_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'photos'), callback_data=f"photos_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'wifi'), callback_data=f"wifi_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'qna'), callback_data=f"qna_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'live_map'), callback_data=f"map_{meeting_id}")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"back_survey_{meeting_id}"))
    return kb

def finish_confirm_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'yes'), callback_data=f"finish_yes_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}")
    )
    return kb

def admin_feedback_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def admin_wifi_view_keyboard(meeting_id, lang='en', has_wifi=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    if has_wifi:
        edit_name_btn = types.InlineKeyboardButton(get_text(lang, 'edit_wifi_name'), callback_data=f"admin_wifi_edit_name_{meeting_id}")
        edit_pass_btn = types.InlineKeyboardButton(get_text(lang, 'edit_wifi_password'), callback_data=f"admin_wifi_edit_password_{meeting_id}")
        delete_btn = types.InlineKeyboardButton(get_text(lang, 'delete'), callback_data=f"admin_wifi_clear_{meeting_id}")
        kb.row(edit_name_btn, edit_pass_btn)
        kb.add(delete_btn)
    else:
        add_btn = types.InlineKeyboardButton(get_text(lang, 'add_wifi'), callback_data=f"add_wifi_{meeting_id}")
        kb.add(add_btn)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def admin_photos_view_keyboard(meeting_id, lang='en', has_photos=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    add_btn = types.InlineKeyboardButton(get_text(lang, 'add'), callback_data=f"admin_photos_add_{meeting_id}")
    delete_btn = types.InlineKeyboardButton(get_text(lang, 'delete'), callback_data=f"admin_photos_clear_{meeting_id}")
    if has_photos:
        kb.row(add_btn, delete_btn)
    else:
        kb.add(add_btn)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def admin_pdf_view_keyboard(meeting_id, lang='en', has_pdf=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    add_btn = types.InlineKeyboardButton(get_text(lang, 'add_pdf'), callback_data=f"admin_pdf_add_{meeting_id}")
    edit_btn = types.InlineKeyboardButton(get_text(lang, 'edit_pdf'), callback_data=f"admin_pdf_edit_{meeting_id}")
    delete_btn = types.InlineKeyboardButton(get_text(lang, 'delete'), callback_data=f"admin_pdf_clear_{meeting_id}")
    if has_pdf:
        kb.row(edit_btn, delete_btn)
    else:
        kb.add(add_btn)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def admin_pdf_delete_confirm_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'yes'), callback_data=f"admin_pdf_delete_confirm_yes_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_pdf_{meeting_id}")
    )
    return kb

def admin_geo_view_keyboard(meeting_id, lang='en', has_geo=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    edit_btn = types.InlineKeyboardButton(get_text(lang, 'edit'), callback_data=f"admin_geo_edit_{meeting_id}")
    delete_btn = types.InlineKeyboardButton(get_text(lang, 'delete'), callback_data=f"admin_geo_clear_{meeting_id}")
    if has_geo:
        kb.row(edit_btn, delete_btn)
    else:
        kb.add(edit_btn)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def admin_agenda_view_keyboard(meeting_id, lang='en', has_items=False):
    kb = types.InlineKeyboardMarkup(row_width=2)
    add_btn = types.InlineKeyboardButton(get_text(lang, 'add'), callback_data=f"admin_agenda_add_{meeting_id}")
    delete_btn = types.InlineKeyboardButton(get_text(lang, 'delete'), callback_data=f"admin_agenda_clear_{meeting_id}")
    if has_items:
        kb.row(add_btn, delete_btn)
    else:
        kb.add(add_btn)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def admin_agenda_items_list_keyboard(meeting_id, items, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'add'), callback_data=f"admin_agenda_add_{meeting_id}"))
    for item in items:
        agenda_id = item[0]
        title = item[2] or ''
        start = item[3] or ''
        end = item[4] or ''
        label = f"🕐 {start}–{end} • {title}".strip()
        kb.add(types.InlineKeyboardButton(label, callback_data=f"admin_agenda_item_{agenda_id}_{meeting_id}"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}"))
    return kb

def admin_agenda_item_delete_confirm_keyboard(agenda_id, meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'yes'), callback_data=f"admin_agenda_item_delete_confirm_{agenda_id}_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_agenda_{meeting_id}")
    )
    return kb

def admin_agenda_item_actions_keyboard(agenda_id, meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'edit_agenda'), callback_data=f"admin_agenda_item_edit_{agenda_id}_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'delete'), callback_data=f"admin_agenda_item_delete_{agenda_id}_{meeting_id}")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'people'), callback_data=f"admin_agenda_item_people_{agenda_id}_{meeting_id}"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_agenda_{meeting_id}"))
    return kb

def admin_agenda_people_back_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_agenda_{meeting_id}"))
    return kb
def admin_agenda_item_edit_keyboard(agenda_id, meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'edit_agenda_title'), callback_data=f"admin_agenda_item_edit_title_{agenda_id}_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'edit_agenda_start'), callback_data=f"admin_agenda_item_edit_start_{agenda_id}_{meeting_id}")
    )
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'edit_agenda_end'), callback_data=f"admin_agenda_item_edit_end_{agenda_id}_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'edit_agenda_desc'), callback_data=f"admin_agenda_item_edit_desc_{agenda_id}_{meeting_id}")
    )
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_agenda_{meeting_id}"))
    return kb

def skip_keyboard(lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'skip'), callback_data="agenda_skip_desc"))
    return kb

def admin_delete_confirm_keyboard(meeting_id, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton(get_text(lang, 'yes'), callback_data=f"confirm_delete_{meeting_id}"),
        types.InlineKeyboardButton(get_text(lang, 'back'), callback_data=f"admin_meeting_{meeting_id}")
    )
    return kb

def admin_feedback_finished_meetings_keyboard(meetings, lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if meetings:
        for m in meetings:
            kb.add(types.InlineKeyboardButton(f"{m[1]}", callback_data=f"admin_feedback_view_{m[0]}"))
    else:
        kb.add(types.InlineKeyboardButton(get_text(lang, 'no_meetings'), callback_data="notify_none"))
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="back_admin"))
    return kb

def admin_feedback_back_to_list_keyboard(lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="admin_feedback_main"))
    return kb

def admin_questions_back_keyboard(lang='en'):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text(lang, 'back'), callback_data="admin_questions"))
    return kb
