import yaml
import glob
import os
import re
import telegram
from telegram.ext import (
    Updater, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    Filters
)

from firewall import firewall
from models import Card


@firewall(mode="users")
def send_row(update, context):
    card = Card(context.user_data["card"], context)
    row = card.choose_one()

    context.user_data["translate"] = row.original_lang  # Storage for next iter
    custom_keyboard = [
        [telegram.InlineKeyboardButton("Translate", callback_data="translate")],
        [
            telegram.InlineKeyboardButton("↙️ Cards", callback_data="Cards"),
            telegram.InlineKeyboardButton("🥐 View", callback_data="View")
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(custom_keyboard)

    context.bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text=row.russian_lang,
        reply_markup=reply_markup
    )

    return


@firewall(mode="users")
def set_keyboard(update, context):
    cards_btn = [
        [telegram.KeyboardButton("Cards 🗃",
                                 callback_data="Cards")]
    ]
    cards_keyboard = telegram.ReplyKeyboardMarkup(
        cards_btn, resize_keyboard=True
    )

    context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="Hi 🌸\n\nI will manage your cards with translated words."
            "You need to send me *.txt* document with such format:\n\n"
            "`treu :: надежный, верный\nvorkommen :: встречаться`",
            parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup=cards_keyboard
        )

    return


@firewall(mode="users")
def callback_response(update, context):
    meow = re.match("(c___).*", update.callback_query.data)
    if meow is not None and meow.string == update.callback_query.data:
        return choose_card(update, context)

    goth = re.match("(d___).*", update.callback_query.data)
    if goth is not None and goth.string == update.callback_query.data:
        return delete_card(update, context)

    if update.callback_query.data == "Cards":
        context.bot.deleteMessage(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
        )

        return set_cards_keyboard(update, context)

    if update.callback_query.data == "View":
        return send_card_view(update, context)

    if update.callback_query.data == "next":
        context.user_data["num"] += 1
        return send_row(update, context)

    if update.callback_query.data == "translate":

        if "translate" not in context.user_data:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="Something went wrong, try again"
            )
            return

        custom_keyboard = [
            [telegram.InlineKeyboardButton("Next", callback_data="next")],
            [
                telegram.InlineKeyboardButton("↙️ Cards", callback_data="Cards"),
                telegram.InlineKeyboardButton("🥐 View", callback_data="View")
            ]
        ]
        reply_markup = telegram.InlineKeyboardMarkup(custom_keyboard)

        context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=context.user_data["translate"],
            reply_markup=reply_markup
        )


@firewall(mode="users")
def send_card_view(update, context):
    card = Card(context.user_data["card"], context)

    custom_keyboard = [[
        telegram.InlineKeyboardButton("↙️ Cards", callback_data="Cards"),
        telegram.InlineKeyboardButton("Back to card", callback_data="next"),
    ]]

    reply_markup = telegram.InlineKeyboardMarkup(custom_keyboard)

    context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=repr(card),
            reply_markup=reply_markup
        )
    
    return

@firewall(mode="users")
def set_cards_keyboard(update, context):
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)

    cards = glob.glob(f"{config['cards_path']}/{update.effective_message.chat_id}/*.txt")

    if len(cards) == 0:
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="You don't have cards yet. "
            "Send me the first one: *.txt* document with such format:\n\n"
            "`treu :: надежный, верный\nvorkommen :: встречаться`",
            parse_mode=telegram.ParseMode.MARKDOWN
        )

        return

    cards_keys = list()
    for card in cards:
        name = os.path.basename(card)[:-4]

        row = [
            telegram.InlineKeyboardButton(name, callback_data="c___"+name),
            telegram.InlineKeyboardButton("🗑", callback_data="d___"+name)
        ]

        cards_keys.append(row)

    cards_keyboard = telegram.InlineKeyboardMarkup(
        cards_keys, resize_keyboard=True
    )

    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text="Choose you card",
        reply_markup=cards_keyboard
    )

    return


@firewall(mode="users")
def choose_card(update, context):
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)

    context.user_data["card"] = config["cards_path"] + \
        "/" + str(update.effective_message.chat_id) + "/" + update.callback_query.data[4:]

    context.user_data["num"] = 0 

    return send_row(update, context)


@firewall(mode="users")
def delete_card(update, context):
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)

    os.remove(f"{config['cards_path']}/{update.effective_message.chat_id}/{update.callback_query.data[4:]}.txt")

    return set_cards_keyboard(update, context)


@firewall(mode="users")
def file_loaded(update, context):
    document = update.message.document

    file_id = document.file_id
    try:
        telegram_file = context.bot.get_file(file_id)
    except Exception as err:
        print(repr(err))

    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)

    if len(document.file_name) > 20:
        name = document.file_name[:10]+".."+document.file_name[-8:]
    else:
        name = document.file_name

    with open(f"{config['cards_path']}/{update.effective_message.chat_id}/{name}", "wb") as file:
        telegram_file.download(out=file)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="The card has been added 🦾"
    )


if __name__ == "__main__":
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)

    updater = Updater(token=config["token"], use_context=True)
    dispatcher = updater.dispatcher

    send_row_handler = CommandHandler('start', set_keyboard)
    callback_handler = CallbackQueryHandler(callback_response)
    file_loaded_handler = MessageHandler(Filters.document, file_loaded)
    cards_keyboard_handler = MessageHandler(Filters.regex("(Cards 🗃)$"),
                                            set_cards_keyboard)
    choosen_card_handler = CallbackQueryHandler(choose_card,
                                                pattern="(c___)(.)+")

    dispatcher.add_handler(send_row_handler)
    dispatcher.add_handler(callback_handler)
    dispatcher.add_handler(file_loaded_handler)
    dispatcher.add_handler(cards_keyboard_handler)
    dispatcher.add_handler(choosen_card_handler)

    updater.start_polling()
    updater.idle()
