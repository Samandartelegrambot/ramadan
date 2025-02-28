from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageCantBeEdited, InlineKeyboardExpected
import re
from database import init_db
from utils import adjust_time
from translations import translations
import sqlite3
from datetime import datetime
from states import RamazanStates

init_db()

def setup_handlers(dp: Dispatcher):
    @dp.message_handler(commands=['start'], state="*")
    async def send_welcome(message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("O‘zbekcha"), types.KeyboardButton("Русский"))
        
        user_data = await state.get_data()
        last_message_id = user_data.get("last_message_id")
        
        try:
            if last_message_id:
                await dp.bot.edit_message_text(
                    text=translations["uz"]["select_language"],
                    chat_id=message.chat.id,
                    message_id=last_message_id,
                    reply_markup=None
                )
                sent_message = await message.answer(translations["uz"]["select_language"], reply_markup=keyboard)
            else:
                sent_message = await message.answer(translations["uz"]["select_language"], reply_markup=keyboard)
            await state.update_data(last_message_id=sent_message.message_id)
        except (MessageCantBeEdited, InlineKeyboardExpected):
            sent_message = await message.answer(translations["uz"]["select_language"], reply_markup=keyboard)
            await state.update_data(last_message_id=sent_message.message_id)

        current_data = await state.get_data()
        await state.update_data(
            language=current_data.get("language", "uz"),
            region=current_data.get("region", ""),
            district=current_data.get("district", ""),
            sahar_diff=current_data.get("sahar_diff", 0),
            iftor_diff=current_data.get("iftor_diff", 0)
        )
        await state.set_state(RamazanStates.START)

    @dp.message_handler(lambda message: message.text in ["O‘zbekcha", "Русский"], state=RamazanStates.START)
    async def set_language(message: types.Message, state: FSMContext):
        user_lang = "uz" if message.text == "O‘zbekcha" else "ru"
        await state.update_data(language=user_lang)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        regions = ["Qoraqolpoqiston Respublikasi", "Toshkent viloyati", "Jizzax viloyati",
                   "Andijon viloyati", "Namangan viloyati", "Farg‘ona viloyati", "Sirdaryo viloyati",
                   "Samarqand viloyati", "Qashqadaryo viloyati", "Surxondaryo viloyati", "Buxoro viloyati",
                   "Navoiy viloyati", "Xorazm viloyati"]
        for region in regions:
            keyboard.insert(types.InlineKeyboardButton(text=region, callback_data=f"region_{region}"))
        
        user_data = await state.get_data()
        lang = user_data.get("language", "uz")
        last_message_id = user_data.get("last_message_id")
        try:
            if last_message_id:
                await dp.bot.edit_message_text(
                    text=translations[lang]["welcome"],
                    chat_id=message.chat.id,
                    message_id=last_message_id,
                    reply_markup=keyboard
                )
            else:
                sent_message = await message.answer(translations[lang]["welcome"], reply_markup=keyboard)
                await state.update_data(last_message_id=sent_message.message_id)
        except (MessageCantBeEdited, InlineKeyboardExpected):
            sent_message = await message.answer(translations[lang]["welcome"], reply_markup=keyboard)
            await state.update_data(last_message_id=sent_message.message_id)

        await state.set_state(RamazanStates.REGION)

    @dp.callback_query_handler(lambda c: c.data.startswith("region_"), state=RamazanStates.REGION)
    async def process_region_selection(callback_query: types.CallbackQuery, state: FSMContext):
        region_name = callback_query.data.replace("region_", "")
        await dp.bot.answer_callback_query(callback_query.id)

        conn = sqlite3.connect("ramazan.db")
        c = conn.cursor()
        c.execute("SELECT id FROM regions WHERE name=?", (region_name,))
        region_id = c.fetchone()
        
        if not region_id:
            user_data = await state.get_data()
            lang = user_data.get("language", "uz")
            await dp.bot.send_message(callback_query.from_user.id, translations[lang]["error"])
            conn.close()
            return

        region_id = region_id[0]
        c.execute("SELECT name FROM districts WHERE region_id=?", (region_id,))
        districts = [row[0] for row in c.fetchall()]

        if not districts:
            user_data = await state.get_data()
            lang = user_data.get("language", "uz")
            await dp.bot.send_message(callback_query.from_user.id, f"{translations[lang]['error']} {region_name} uchun tumanlar topilmadi.")
            conn.close()
            return

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for district in districts:
            keyboard.insert(types.InlineKeyboardButton(text=district, callback_data=f"district_{district}"))
        
        user_data = await state.get_data()
        lang = user_data.get("language", "uz")
        keyboard.add(types.InlineKeyboardButton(text=translations[lang]["back"], callback_data="back_to_regions"))
        
        last_message_id = user_data.get("last_message_id")
        try:
            if last_message_id:
                await dp.bot.edit_message_text(
                    text=translations[lang]["select_district"].format(region_name),
                    chat_id=callback_query.message.chat.id,
                    message_id=last_message_id,
                    reply_markup=keyboard
                )
            else:
                sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["select_district"].format(region_name), reply_markup=keyboard)
                await state.update_data(last_message_id=sent_message.message_id)
        except (MessageCantBeEdited, InlineKeyboardExpected):
            sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["select_district"].format(region_name), reply_markup=keyboard)
            await state.update_data(last_message_id=sent_message.message_id)

        await state.update_data(region=region_name)
        await state.set_state(RamazanStates.DISTRICT)
        conn.close()

    @dp.callback_query_handler(lambda c: c.data.startswith("district_"), state=RamazanStates.DISTRICT)
    async def process_district_selection(callback_query: types.CallbackQuery, state: FSMContext):
        district_name = callback_query.data.replace("district_", "")
        await dp.bot.answer_callback_query(callback_query.id)

        conn = sqlite3.connect("ramazan.db")
        c = conn.cursor()
        c.execute("SELECT sahar_diff, iftor_diff FROM districts WHERE name=?", (district_name,))
        diff = c.fetchone()
        
        if not diff:
            user_data = await state.get_data()
            lang = user_data.get("language", "uz")
            await dp.bot.send_message(callback_query.from_user.id, translations[lang]["error"])
            conn.close()
            return

        sahar_diff, iftor_diff = diff

        keyboard = types.InlineKeyboardMarkup(row_width=3)
        dates = [f"{i}-mart" for i in range(1, 31)]
        for date in dates:
            keyboard.insert(types.InlineKeyboardButton(text=date, callback_data=f"date_{district_name}_{date}"))
        
        user_data = await state.get_data()
        lang = user_data.get("language", "uz")
        keyboard.add(types.InlineKeyboardButton(text=translations[lang]["back"], callback_data="back_to_districts"))
        
        last_message_id = user_data.get("last_message_id")
        try:
            if last_message_id:
                await dp.bot.edit_message_text(
                    text=translations[lang]["select_date"].format(district_name),
                    chat_id=callback_query.message.chat.id,
                    message_id=last_message_id,
                    reply_markup=keyboard
                )
            else:
                sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["select_date"].format(district_name), reply_markup=keyboard)
                await state.update_data(last_message_id=sent_message.message_id)
        except (MessageCantBeEdited, InlineKeyboardExpected):
            sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["select_date"].format(district_name), reply_markup=keyboard)
            await state.update_data(last_message_id=sent_message.message_id)

        await state.update_data(district=district_name, sahar_diff=sahar_diff, iftor_diff=iftor_diff)
        await state.set_state(RamazanStates.DATE)
        conn.close()

    @dp.callback_query_handler(lambda c: c.data.startswith("date_"), state=RamazanStates.DATE)
    async def process_date_selection(callback_query: types.CallbackQuery, state: FSMContext):
        data_parts = callback_query.data.replace("date_", "").split("_")
        district_name, date = data_parts[0], data_parts[1]
        await dp.bot.answer_callback_query(callback_query.id)

        user_data = await state.get_data()
        sahar_diff = user_data.get("sahar_diff", 0)
        iftor_diff = user_data.get("iftor_diff", 0)

        conn = sqlite3.connect("ramazan.db")
        c = conn.cursor()
        c.execute("SELECT sahar_time, iftor_time FROM ramazan_times WHERE date=?", (date,))
        toshkent_times = c.fetchone()
        
        if not toshkent_times:
            lang = user_data.get("language", "uz")
            await dp.bot.send_message(callback_query.from_user.id, translations[lang]["error"])
            conn.close()
            return

        toshkent_sahar, toshkent_iftor = toshkent_times

        sahar_time, sahar_days = adjust_time(toshkent_sahar, sahar_diff)
        iftor_time, iftor_days = adjust_time(toshkent_iftor, iftor_diff)

        try:
            match = re.match(r"(\d+)-mart", date)
            if not match:
                lang = user_data.get("language", "uz")
                await dp.bot.send_message(callback_query.from_user.id, translations[lang]["error"] + " Sana formatida xatolik.")
                conn.close()
                return

            day = int(match.group(1))
            date_obj = datetime(2025, 3, day).date()
            ramazan_start = datetime(2025, 3, 1).date()
            ramazan_end = datetime(2025, 3, 30).date()
            
            if not (ramazan_start <= date_obj <= ramazan_end):
                lang = user_data.get("language", "uz")
                keyboard = types.InlineKeyboardMarkup(row_width=3)
                dates = [f"{i}-mart" for i in range(1, 31)]
                for d in dates:
                    keyboard.insert(types.InlineKeyboardButton(text=d, callback_data=f"date_{district_name}_{d}"))
                keyboard.add(types.InlineKeyboardButton(text=translations[lang]["back"], callback_data="back_to_districts"))
                sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["outside_ramadan"], reply_markup=keyboard)
                await state.update_data(last_message_id=sent_message.message_id)
                conn.close()
                return
        except ValueError as e:
            lang = user_data.get("language", "uz")
            await dp.bot.send_message(callback_query.from_user.id, translations[lang]["error"] + f" Sana formatida xatolik: {str(e)}")
            conn.close()
            return

        final_sahar = sahar_time
        final_iftor = iftor_time
        if sahar_days != 0 or iftor_days != 0:
            day_shift = " (kun o‘zgarishi: +" if sahar_days > 0 or iftor_days > 0 else " (kun o‘zgarishi: -"
            day_shift += f"{abs(sahar_days or iftor_days)} kun)"
            final_sahar += day_shift
            final_iftor += day_shift

        lang = user_data.get("language", "uz")
        # Matnni qalin shrift bilan formatlash
        formatted_text = (
            f"**{district_name}, {date} uchun:**\n"
            f"**Saharlik: {final_sahar}**\n"
            f"**Iftor: {final_iftor}**\n\n"
            f"{translations[lang]['times']}"  # To‘g‘ridan-to‘g‘ri duolar
        )

        last_message_id = user_data.get("last_message_id")
        try:
            if last_message_id:
                await dp.bot.edit_message_text(
                    text=formatted_text,
                    chat_id=callback_query.message.chat.id,
                    message_id=last_message_id,
                    parse_mode="Markdown"
                )
            else:
                sent_message = await dp.bot.send_message(
                    callback_query.from_user.id,
                    formatted_text,
                    parse_mode="Markdown"
                )
                await state.update_data(last_message_id=sent_message.message_id)
        except (MessageCantBeEdited, InlineKeyboardExpected):
            sent_message = await dp.bot.send_message(
                callback_query.from_user.id,
                formatted_text,
                parse_mode="Markdown"
            )
            await state.update_data(last_message_id=sent_message.message_id)

        conn.close()

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text=translations[lang]["back"], callback_data="back_to_districts"))
        if last_message_id:
            try:
                await dp.bot.edit_message_reply_markup(
                    chat_id=callback_query.message.chat.id,
                    message_id=last_message_id,
                    reply_markup=keyboard
                )
            except (MessageCantBeEdited, InlineKeyboardExpected):
                await dp.bot.send_message(callback_query.from_user.id, "Qayta tanlash uchun:", reply_markup=keyboard)
        else:
            await dp.bot.send_message(callback_query.from_user.id, "Qayta tanlash uchun:", reply_markup=keyboard)

    @dp.callback_query_handler(lambda c: c.data == "back_to_districts", state=RamazanStates.DATE)
    async def back_to_districts(callback_query: types.CallbackQuery, state: FSMContext):
        await dp.bot.answer_callback_query(callback_query.id)
        user_data = await state.get_data()
        region = user_data.get("region", "")

        conn = sqlite3.connect("ramazan.db")
        c = conn.cursor()
        c.execute("SELECT id FROM regions WHERE name=?", (region,))
        region_id = c.fetchone()
        
        if region_id:
            c.execute("SELECT name FROM districts WHERE region_id=?", (region_id[0],))
            districts = [row[0] for row in c.fetchall()]

            keyboard = types.InlineKeyboardMarkup(row_width=2)
            for district in districts:
                keyboard.insert(types.InlineKeyboardButton(text=district, callback_data=f"district_{district}"))
            
            lang = user_data.get("language", "uz")
            keyboard.add(types.InlineKeyboardButton(text=translations[lang]["back"], callback_data="back_to_regions"))
            
            last_message_id = user_data.get("last_message_id")
            try:
                if last_message_id:
                    await dp.bot.edit_message_text(
                        text=translations[lang]["select_district"].format(region),
                        chat_id=callback_query.message.chat.id,
                        message_id=last_message_id,
                        reply_markup=keyboard
                    )
                else:
                    sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["select_district"].format(region), reply_markup=keyboard)
                    await state.update_data(last_message_id=sent_message.message_id)
            except (MessageCantBeEdited, InlineKeyboardExpected):
                sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["select_district"].format(region), reply_markup=keyboard)
                await state.update_data(last_message_id=sent_message.message_id)
        await state.set_state(RamazanStates.DISTRICT)
        conn.close()

    @dp.callback_query_handler(lambda c: c.data == "back_to_regions", state=[RamazanStates.DISTRICT, RamazanStates.DATE])
    async def back_to_regions(callback_query: types.CallbackQuery, state: FSMContext):
        await dp.bot.answer_callback_query(callback_query.id)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        regions = ["Qoraqolpoqiston Respublikasi", "Toshkent viloyati", "Jizzax viloyati",
                   "Andijon viloyati", "Namangan viloyati", "Farg‘ona viloyati", "Sirdaryo viloyati",
                   "Samarqand viloyati", "Qashqadaryo viloyati", "Surxondaryo viloyati", "Buxoro viloyati",
                   "Navoiy viloyati", "Xorazm viloyati"]
        
        for region in regions:
            keyboard.insert(types.InlineKeyboardButton(text=region, callback_data=f"region_{region}"))
        
        user_data = await state.get_data()
        lang = user_data.get("language", "uz")
        
        last_message_id = user_data.get("last_message_id")
        try:
            if last_message_id:
                await dp.bot.edit_message_text(
                    text=translations[lang]["welcome"],
                    chat_id=callback_query.message.chat.id,
                    message_id=last_message_id,
                    reply_markup=keyboard
                )
            else:
                sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["welcome"], reply_markup=keyboard)
                await state.update_data(last_message_id=sent_message.message_id)
        except (MessageCantBeEdited, InlineKeyboardExpected):
            sent_message = await dp.bot.send_message(callback_query.from_user.id, translations[lang]["welcome"], reply_markup=keyboard)
            await state.update_data(last_message_id=sent_message.message_id)

        await state.set_state(RamazanStates.REGION)