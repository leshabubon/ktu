import os
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# API для получения курсов валют (бесплатный)
EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [
            InlineKeyboardButton("💵 USD", callback_data='USD'),
            InlineKeyboardButton("💶 EUR", callback_data='EUR'),
        ],
        [
            InlineKeyboardButton("💷 GBP", callback_data='GBP'),
            InlineKeyboardButton("💴 JPY", callback_data='JPY'),
        ],
        [
            InlineKeyboardButton("🇨🇳 CNY", callback_data='CNY'),
            InlineKeyboardButton("🇹🇷 TRY", callback_data='TRY'),
        ],
        [
            InlineKeyboardButton("📊 Все курсы", callback_data='ALL'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '💱 *Бот для отслеживания курса валют*\n\n'
        'Выберите валюту для просмотра курса к RUB:\n\n'
        'Команды:\n'
        '/start - Главное меню\n'
        '/rates - Актуальные курсы\n'
        '/convert - Конвертер валют',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def get_exchange_rate(base_currency: str, target_currency: str = 'RUB'):
    """Получает курс валюты"""
    try:
        response = requests.get(f"{EXCHANGE_API}{base_currency}", timeout=10)
        data = response.json()
        
        if target_currency in data['rates']:
            rate = data['rates'][target_currency]
            date = data['date']
            return rate, date
        return None, None
    except Exception as e:
        print(f"Ошибка получения курса: {e}")
        return None, None

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    currency = query.data
    
    if currency == 'ALL':
        # Показываем все основные курсы
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'TRY']
        message = '📊 *Актуальные курсы валют к RUB:*\n\n'
        
        for curr in currencies:
            rate, date = await get_exchange_rate(curr, 'RUB')
            if rate:
                flag = {'USD': '💵', 'EUR': '💶', 'GBP': '💷', 'JPY': '💴', 'CNY': '🇨🇳', 'TRY': '🇹🇷'}
                message += f"{flag.get(curr, '💱')} *{curr}*: `{rate:.2f}` RUB\n"
        
        message += f"\n🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
    else:
        # Показываем курс выбранной валюты
        rate, date = await get_exchange_rate(currency, 'RUB')
        
        if rate:
            # Также показываем обратный курс
            reverse_rate, _ = await get_exchange_rate('RUB', currency)
            
            message = f'💱 *Курс {currency} к RUB*\n\n'
            message += f'1 {currency} = `{rate:.2f}` RUB\n'
            if reverse_rate:
                message += f'1 RUB = `{reverse_rate:.4f}` {currency}\n'
            message += f'\n🕐 Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M")}'
        else:
            message = '❌ Ошибка получения данных. Попробуйте позже.'
    
    # Кнопка "Назад"
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='BACK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("💵 USD", callback_data='USD'),
            InlineKeyboardButton("💶 EUR", callback_data='EUR'),
        ],
        [
            InlineKeyboardButton("💷 GBP", callback_data='GBP'),
            InlineKeyboardButton("💴 JPY", callback_data='JPY'),
        ],
        [
            InlineKeyboardButton("🇨🇳 CNY", callback_data='CNY'),
            InlineKeyboardButton("🇹🇷 TRY", callback_data='TRY'),
        ],
        [
            InlineKeyboardButton("📊 Все курсы", callback_data='ALL'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        '💱 *Бот для отслеживания курса валют*\n\n'
        'Выберите валюту для просмотра курса к RUB:',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def rates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /rates - показывает все курсы"""
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'TRY']
    message = '📊 *Актуальные курсы валют к RUB:*\n\n'
    
    for curr in currencies:
        rate, date = await get_exchange_rate(curr, 'RUB')
        if rate:
            flag = {'USD': '💵', 'EUR': '💶', 'GBP': '💷', 'JPY': '💴', 'CNY': '🇨🇳', 'TRY': '🇹🇷'}
            message += f"{flag.get(curr, '💱')} *{curr}*: `{rate:.2f}` RUB\n"
    
    message += f"\n🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /convert - конвертер валют"""
    if len(context.args) != 3:
        await update.message.reply_text(
            '💱 *Конвертер валют*\n\n'
            'Использование: `/convert сумма из в`\n\n'
            'Пример: `/convert 100 USD RUB`\n'
            'Пример: `/convert 5000 RUB EUR`',
            parse_mode='Markdown'
        )
        return
    
    try:
        amount = float(context.args[0])
        from_curr = context.args[1].upper()
        to_curr = context.args[2].upper()
        
        rate, date = await get_exchange_rate(from_curr, to_curr)
        
        if rate:
            result = amount * rate
            message = f'💱 *Конвертация*\n\n'
            message += f'`{amount:.2f}` {from_curr} = `{result:.2f}` {to_curr}\n\n'
            message += f'Курс: 1 {from_curr} = {rate:.4f} {to_curr}\n'
            message += f'🕐 {datetime.now().strftime("%d.%m.%Y %H:%M")}'
        else:
            message = '❌ Ошибка конвертации. Проверьте код валюты.'
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text('❌ Неверный формат суммы. Используйте числа.')

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rates", rates_command))
    application.add_handler(CommandHandler("convert", convert_command))
    
    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(back_handler, pattern='^BACK$'))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()