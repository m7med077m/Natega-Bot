from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime

def setup_admin_tools(bot_instance):
    app = bot_instance.app
    admin_list = bot_instance.admin_list
    user_student_map = bot_instance.user_student_map
    student_usage = bot_instance.student_usage
    get_student_info_by_id = bot_instance.get_student_info_by_id

    # /broadcast
    @app.on_message(filters.command("broadcast"))
    async def broadcast_command(client: Client, message: Message):
        if message.from_user.id not in admin_list:
            await message.reply("❌ الأمر ده مخصص للإدمن فقط.")
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply("❗ استخدم الأمر كده:\n/broadcast رسالتك هنا")
            return

        msg = parts[1]
        sent = 0
        failed = 0
        for uid in user_student_map.keys():
            try:
                await app.send_message(int(uid), f"📢 رسالة من الإدارة:\n\n{msg}")
                sent += 1
            except:
                failed += 1

        await message.reply(f"✅ تم الإرسال لـ {sent} مستخدم.\n❌ فشل الإرسال لـ {failed}.")

    # /stats
    @app.on_message(filters.command("stats"))
    async def stats_command(client: Client, message: Message):
        if message.from_user.id not in admin_list:
            await message.reply("❌ الأمر ده مخصص للإدمن فقط.")
            return

        total_users = len(user_student_map)
        total_lookups = sum([d.get("count", 0) for d in student_usage.values()])
        top_users = sorted(student_usage.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:5]

        text = f"📊 **إحصائيات النظام:**\n\n"
        text += f"👥 عدد المستخدمين المرتبطين: `{total_users}`\n"
        text += f"📥 عدد مرات الاستعلام الكلي: `{total_lookups}`\n"
        text += f"\n🏆 **أكثر الطلاب تم البحث عنهم:**\n"

        for sid, info in top_users:
            count = info.get("count", 0)
            name = (await get_student_info_by_id(sid)).get("name", "—")
            text += f"🔹 {name} (ID: `{sid}`) ➤ {count} مره\n"

        await message.reply(text)

    # /unlink
    @app.on_message(filters.command("unlink"))
    async def unlink_command(client: Client, message: Message):
        if message.from_user.id not in admin_list:
            await message.reply("❌ الأمر ده مخصص للإدمن فقط.")
            return

        parts = message.text.strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            await message.reply("❗ الاستخدام الصحيح:\n/unlink <telegram_user_id>")
            return

        target_id = parts[1]
        if target_id not in user_student_map:
            await message.reply("❌ لا يوجد حساب مرتبط بهذا ID.")
            return

        student_id = user_student_map.pop(target_id)
        bot_instance.save_state()

        await message.reply(
            f"✅ تم فك الربط بين:\n"
            f"👤 Telegram ID: `{target_id}`\n"
            f"🎓 Student ID: `{student_id}`"
        )

        try:
            await app.send_message(
                int(target_id),
                "⚠️ تم فك ربط حسابك برقم الطالب الخاص بك بواسطة الإدارة.\n"
                "إذا كنت تريد ربطه مرة أخرى، أرسل كود الطالب من جديد."
            )
        except:
            pass
