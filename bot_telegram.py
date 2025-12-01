import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Import library Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Import service/logic dari aplikasi Anda
# CATATAN: Fungsi-fungsi menu CLI (app.menus.*) biasanya menggunakan 'print'. 
# Untuk bot, Anda harus memanggil fungsi yang mengembalikan DATA (dict/json), bukan yang print ke layar.
# Di sini saya import client/service-nya langsung.
from app.client.engsel import get_balance, get_tiering_info
from app.service.auth import AuthInstance

# Load environment variables
load_dotenv()

# Konfigurasi Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Ganti dengan Token Bot Father Anda
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Menampilkan Menu Utama (Profile + Tombol)
    """
    user_telegram_id = update.effective_user.id
    
    # --- LOGIC MENGAMBIL DATA USER (Diambil dari main.py Anda) ---
    active_user = AuthInstance.get_active_user()
    
    if not active_user:
        await update.message.reply_text("⚠️ Belum ada user yang login. Silakan set active user di server.")
        return

    # Ambil Balance & Tiering (Logic asli Anda)
    try:
        balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
        balance_remaining = balance.get("remaining", 0)
        balance_expired_at = balance.get("expired_at", 0)
        
        expired_at_dt = datetime.fromtimestamp(balance_expired_at).strftime("%Y-%m-%d")
        
        point_info = "Points: N/A | Tier: N/A"
        if active_user["subscription_type"] == "PREPAID":
            tiering_data = get_tiering_info(AuthInstance.api_key, active_user["tokens"])
            tier = tiering_data.get("tier", 0)
            current_point = tiering_data.get("current_point", 0)
            point_info = f"Points: {current_point} | Tier: {tier}"
            
        profile_text = (
            f"=========================================\n"
            f"👤 <b>Nomor:</b> <code>{active_user['number']}</code> | <b>Type:</b> {active_user['subscription_type']}\n"
            f"💰 <b>Pulsa:</b> Rp {balance_remaining:,}\n"
            f"📅 <b>Aktif sampai:</b> {expired_at_dt}\n"
            f"💎 <b>{point_info}</b>\n"
            f"========================================="
        )
        
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        profile_text = f"Error mengambil data akun: {str(e)}"

    # --- MEMBUAT MENU TOMBOL (INLINE KEYBOARD) ---
    # Format: [ [Tombol Baris 1], [Tombol Baris 2], ... ]
    keyboard = [
        [InlineKeyboardButton("1. Login/Ganti Akun", callback_data='menu_1')],
        [InlineKeyboardButton("2. Lihat Paket Saya", callback_data='menu_2')],
        [InlineKeyboardButton("3. Beli Paket 🔥 HOT 🔥", callback_data='menu_3')],
        [InlineKeyboardButton("4. Beli Paket 🔥 HOT-2 🔥", callback_data='menu_4')],
        [
            InlineKeyboardButton("5. Option Code", callback_data='menu_5'),
            InlineKeyboardButton("6. Family Code", callback_data='menu_6')
        ],
        [InlineKeyboardButton("7. Loop Family Code", callback_data='menu_7')],
        [InlineKeyboardButton("8. Riwayat Transaksi", callback_data='menu_8')],
        [InlineKeyboardButton("9. Family Plan/Akrab", callback_data='menu_9')],
        [InlineKeyboardButton("10. Circle", callback_data='menu_10')],
        [
            InlineKeyboardButton("11. Segments", callback_data='menu_11'),
            InlineKeyboardButton("12. Fam List", callback_data='menu_12')
        ],
        [
            InlineKeyboardButton("13. Store Pkg", callback_data='menu_13'),
            InlineKeyboardButton("14. Redeem", callback_data='menu_14')
        ],
        [
            InlineKeyboardButton("R. Register", callback_data='menu_R'),
            InlineKeyboardButton("N. Notifikasi", callback_data='menu_N')
        ],
        [InlineKeyboardButton("V. Validate MSISDN", callback_data='menu_V')],
        [InlineKeyboardButton("00. Bookmark", callback_data='menu_00')],
        [InlineKeyboardButton("🔄 Refresh Data", callback_data='refresh_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Kirim pesan (atau edit jika ini dari callback refresh)
    if update.callback_query:
        await update.callback_query.edit_message_text(text=profile_text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(text=profile_text, reply_markup=reply_markup, parse_mode='HTML')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Menghandle ketika tombol ditekan
    """
    query = update.callback_query
    await query.answer() # Memberi tahu Telegram tombol berhasil ditekan
    
    data = query.data
    
    if data == "refresh_menu":
        await start(update, context) # Panggil ulang fungsi start untuk refresh
        return

    # --- CONTOH HANDLING MENU ---
    # Di sini Anda harus menghubungkan ke logic aplikasi Anda.
    # PENTING: Jangan panggil fungsi yang ada input() atau print()-nya.
    
    if data == "menu_1":
        await query.message.reply_text("Fitur Ganti Akun belum diimplementasikan di Bot.")
        
    elif data == "menu_2":
        # Contoh logika: Panggil fetch data paket, lalu kirim teks
        # packages = fetch_my_packages_DATA_ONLY() <--- Anda perlu buat fungsi ini yg return data, bukan print
        await query.message.reply_text("📦 <b>Daftar Paket Anda:</b>\n(Fitur ini butuh modifikasi fungsi fetch_my_packages agar return string)", parse_mode='HTML')
        
    elif data == "menu_3":
        await query.message.reply_text("🔥 <b>Menu Hot</b> dipilih.", parse_mode='HTML')
        
    # ... Tambahkan elif untuk menu lainnya ...
    
    else:
        await query.message.reply_text(f"Anda memilih menu dengan data: {data}")

def main_bot():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN belum di set di .env")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handler perintah /start
    application.add_handler(CommandHandler("start", start))
    
    # Handler ketika tombol ditekan
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot sedang berjalan...")
    application.run_polling()

if __name__ == '__main__':
    main_bot()
