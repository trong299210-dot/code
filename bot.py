import os
import time
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from question_generator import generate_unique_question, get_seen_count

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lưu điểm người chơi
scores = {}
# Lưu mốc thời gian lần reset gần nhất (timestamp)
last_reset_time = time.time()
RESET_INTERVAL_SECONDS = 2 * 3600  # 2 tiếng (7200 giây)

DIFFICULTY_INFO = {
    "easy": {
        "name": "🟢 DỄ • BEGINNER",
        "badge": "🌱 Nhập môn",
        "color": discord.Color.from_rgb(46, 204, 113),
    },
    "medium": {
        "name": "🟡 TRUNG BÌNH • INTERMEDIATE",
        "badge": "⚡ Thử thách",
        "color": discord.Color.from_rgb(241, 196, 15),
    },
    "hard": {
        "name": "🔴 KHÓ • ADVANCED (TRICKY)",
        "badge": "🔥 Bẫy logic",
        "color": discord.Color.from_rgb(231, 76, 60),
    },
    "random": {
        "name": "🎲 NGẪU NHIÊN • ALL LEVELS",
        "badge": "✨ Hỗn hợp",
        "color": discord.Color.from_rgb(155, 89, 182),
    },
}

def get_time_until_reset():
    """Tính số phút còn lại trước lần reset điểm kế tiếp"""
    elapsed = time.time() - last_reset_time
    remaining = max(0, RESET_INTERVAL_SECONDS - elapsed)
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    return f"{hours}h {minutes}m"

# Tác vụ nền kiểm tra reset điểm mỗi 60 giây
@tasks.loop(minutes=1)
async def check_scores_reset():
    global last_reset_time, scores
    if time.time() - last_reset_time >= RESET_INTERVAL_SECONDS:
        scores.clear()
        last_reset_time = time.time()
        print("AUTO RESET: Da reset thong ke diem nguoi choi sau chu ky 2 tieng!")

def create_quiz_embed(q_data):
    diff = q_data.get("difficulty", "random")
    meta = DIFFICULTY_INFO.get(diff, DIFFICULTY_INFO["random"])
    opts = q_data["options"]

    embed = discord.Embed(
        title="✨ PYTHON CODE MASTER CHALLENGE",
        description=(
            f"**Độ khó:** `{meta['name']}`  •  **Chủ đề:** `{meta['badge']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❓ **Câu hỏi:** Đoạn mã nguồn Python dưới đây sẽ in ra kết quả gì khi chạy?"
        ),
        color=meta["color"]
    )
    embed.set_thumbnail(url="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg")

    embed.add_field(
        name="💻 MÃ NGUỒN PYTHON",
        value=f"```python\n{q_data['code']}\n```",
        inline=False
    )

    options_text = (
        f"> 🇦 **`A`** ➔ `{opts['A']}`\n"
        f"> 🇧 **`B`** ➔ `{opts['B']}`\n"
        f"> 🇨 **`C`** ➔ `{opts['C']}`\n"
        f"> 🇩 **`D`** ➔ `{opts['D']}`"
    )
    embed.add_field(
        name="🎯 CÁC LỰA CHỌN (Bấm nút bên dưới để chọn đáp án)",
        value=options_text,
        inline=False
    )

    seen = get_seen_count()
    time_left = get_time_until_reset()
    embed.set_footer(
        text=f"🛡️ Kho #{seen} câu độc nhất  •  🔄 Reset điểm sau: {time_left}  •  ⏱️ 90s",
        icon_url="https://cdn-icons-png.flaticon.com/512/2721/2721291.png"
    )
    return embed


class FollowUpView(discord.ui.View):
    def __init__(self, mode, author_id, timeout=90):
        super().__init__(timeout=timeout)
        self.mode = mode
        self.author_id = author_id

    @discord.ui.button(
        label="Chơi Câu Tiếp Theo",
        style=discord.ButtonStyle.success,
        emoji="🚀",
        custom_id="btn_continue"
    )
    async def btn_continue(self, interaction: discord.Interaction, button: discord.ui.Button):
        q_data = generate_unique_question(self.mode)
        embed = create_quiz_embed(q_data)
        quiz_view = QuizView(q_data, self.mode, author_id=interaction.user.id)
        
        await interaction.response.edit_message(embed=embed, view=quiz_view)
        quiz_view.message = interaction.message

    @discord.ui.button(
        label="Dừng & Xóa Tin Nhắn",
        style=discord.ButtonStyle.danger,
        emoji="🗑️",
        custom_id="btn_stop"
    )
    async def btn_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception:
            await interaction.response.send_message("👋 Đã kết thúc lượt thi!", ephemeral=True)

    async def on_timeout(self):
        if hasattr(self, "message") and self.message:
            try:
                await self.message.delete()
            except Exception:
                pass


class QuizView(discord.ui.View):
    def __init__(self, question_data, mode, author_id, timeout=90):
        super().__init__(timeout=timeout)
        self.question_data = question_data
        self.mode = mode
        self.author_id = author_id
        self.answered = False

    async def handle_answer(self, interaction: discord.Interaction, selected_label: str):
        user = interaction.user
        if self.answered:
            await interaction.response.send_message("⚠️ Câu hỏi này đã có người trả lời rồi!", ephemeral=True)
            return

        self.answered = True
        correct = self.question_data["correct_label"]
        correct_ans = self.question_data["correct_answer"]
        explanation = self.question_data.get("explanation", "Chạy logic theo thứ tự biểu thức của Python.")
        is_right = (selected_label == correct)

        if user.id not in scores:
            scores[user.id] = {"correct": 0, "total": 0, "name": user.display_name}
        scores[user.id]["total"] += 1
        scores[user.id]["name"] = user.display_name

        if is_right:
            scores[user.id]["correct"] += 1
            result_header = "🎉 **CHÍNH XÁC XUẤT SẮC!**"
            status_text = f"✨ {user.mention} đã chọn chính xác **Đáp án {correct}** (`{correct_ans}`)."
            color = discord.Color.from_rgb(46, 204, 113)
        else:
            result_header = "❌ **RẤT TIẾC, CHƯA CHÍNH XÁC!**"
            status_text = (
                f"💔 {user.mention} đã chọn **{selected_label}**.\n"
                f"✅ **Đáp án đúng là {correct}**: `{correct_ans}`"
            )
            color = discord.Color.from_rgb(231, 76, 60)

        acc = (scores[user.id]["correct"] / scores[user.id]["total"]) * 100

        embed = interaction.message.embeds[0]
        embed.color = color
        embed.clear_fields()
        
        # 1. Giữ nguyên đoạn code
        embed.add_field(
            name="💻 MÃ NGUỒN VỪA THỬ SỨC:",
            value=f"```python\n{self.question_data['code']}\n```",
            inline=False
        )

        # 2. PHẦN GIẢI THÍCH CHI TIẾT TẠI SAO LẠI RA ĐÁP ÁN ĐÓ
        embed.add_field(
            name="💡 TẠI SAO LẠI RA KẾT QUẢ NÀY? (GIẢI THÍCH CHI TIẾT)",
            value=f"```fix\n{explanation}\n```",
            inline=False
        )

        # 3. Kết quả & Điểm số (kèm mốc đếm ngược reset 2 tiếng)
        time_left = get_time_until_reset()
        embed.add_field(
            name=f"{result_header}",
            value=(
                f"{status_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏆 **Thống kê phiên này:** `{scores[user.id]['correct']}/{scores[user.id]['total']}` đúng  "
                f"(`{acc:.1f}%`)  •  ⏳ *Reset bảng điểm sau: {time_left}*\n"
                f"👉 *Bấm nút bên dưới để sang câu tiếp theo hoặc dừng lại.*"
            ),
            inline=False
        )

        followup_view = FollowUpView(self.mode, author_id=user.id)
        followup_view.message = interaction.message
        await interaction.response.edit_message(embed=embed, view=followup_view)

    @discord.ui.button(label="Đáp án A", style=discord.ButtonStyle.primary, emoji="🇦", custom_id="btn_A")
    async def btn_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, "A")

    @discord.ui.button(label="Đáp án B", style=discord.ButtonStyle.primary, emoji="🇧", custom_id="btn_B")
    async def btn_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, "B")

    @discord.ui.button(label="Đáp án C", style=discord.ButtonStyle.primary, emoji="🇨", custom_id="btn_C")
    async def btn_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, "C")

    @discord.ui.button(label="Đáp án D", style=discord.ButtonStyle.primary, emoji="🇩", custom_id="btn_D")
    async def btn_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, "D")

    async def on_timeout(self):
        if not self.answered and hasattr(self, "message") and self.message:
            try:
                await self.message.delete()
            except Exception:
                pass


@bot.event
async def on_ready():
    print(f"BOT READY: {bot.user} (ID: {bot.user.id})")
    if not check_scores_reset.is_running():
        check_scores_reset.start()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# ==========================================
# CÁC LỆNH PREFIX (!quiz)
# ==========================================
@bot.command(name="quiz")
async def quiz_cmd(ctx, mode: str = "random"):
    mode_clean = mode.lower()
    if mode_clean in ["de", "easy"]:
        mode_clean = "easy"
    elif mode_clean in ["trungbinh", "tb", "medium", "med"]:
        mode_clean = "medium"
    elif mode_clean in ["kho", "hard"]:
        mode_clean = "hard"
    else:
        mode_clean = "random"

    q_data = generate_unique_question(mode_clean)
    embed = create_quiz_embed(q_data)
    view = QuizView(q_data, mode_clean, author_id=ctx.author.id)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg


# ==========================================
# CÁC LỆNH SLASH (/quiz với menu chọn độ khó)
# ==========================================
@bot.tree.command(name="quiz", description="Tạo câu hỏi trắc nghiệm code Python độc nhất vô nhị")
@app_commands.describe(mode="Chọn độ khó phù hợp với trình độ của bạn")
@app_commands.choices(mode=[
    app_commands.Choice(name="🟢 Dễ (Beginner)", value="easy"),
    app_commands.Choice(name="🟡 Trung bình (Intermediate)", value="medium"),
    app_commands.Choice(name="🔴 Khó (Advanced / Tricky)", value="hard"),
    app_commands.Choice(name="🎲 Ngẫu nhiên (All Levels)", value="random"),
])
async def quiz_slash(interaction: discord.Interaction, mode: app_commands.Choice[str] = None):
    selected_mode = mode.value if mode else "random"
    q_data = generate_unique_question(selected_mode)
    embed = create_quiz_embed(q_data)
    view = QuizView(q_data, selected_mode, author_id=interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()


@bot.command(name="rank")
async def rank_cmd(ctx):
    """Bảng xếp hạng người chơi thiết kế đẹp mắt (tự động reset sau 2 tiếng)"""
    time_left = get_time_until_reset()
    if not scores:
        await ctx.send(f"📋 *Chưa có ai tham gia trong phiên này (Bảng điểm reset mỗi 2 tiếng, đợt tiếp theo: {time_left})! Gõ `!quiz` để bắt đầu.*")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: (x[1]["correct"], -x[1]["total"]), reverse=True)
    
    embed = discord.Embed(
        title="🏆 BẢNG XẾP HẠNG PHIÊN HIỆN TẠI (RESET 2 TIẾNG / LẦN)",
        description=f"⏱️ **Thời gian còn lại của phiên:** `{time_left}`\nTop các thành viên có thành tích xuất sắc nhất:",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3112/3112946.png")

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    rows = []
    for idx, (uid, data) in enumerate(sorted_scores[:10]):
        rate = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
        medal = medals[idx] if idx < len(medals) else f"#{idx+1}"
        rows.append(f"{medal} **{data['name']}** ➔ `{data['correct']}/{data['total']}` đúng (`{rate:.1f}%`)")

    embed.add_field(name="BẢNG ĐIỂM", value="\n".join(rows), inline=False)
    embed.set_footer(text=f"Tổng số câu độc nhất: {get_seen_count()} câu  •  Tự động reset sau mỗi 2 giờ")
    await ctx.send(embed=embed)


@bot.command(name="stats")
async def stats_cmd(ctx):
    """Thống kê kho câu hỏi và thời gian đếm ngược reset"""
    cnt = get_seen_count()
    time_left = get_time_until_reset()
    embed = discord.Embed(
        title="📊 THỐNG KÊ HỆ THỐNG",
        description=(
            f"⚡ **Kho câu hỏi duy nhất đã sinh:** `{cnt:,}` câu\n"
            f"🛡️ **Trùng lặp:** `0%` (Xác thực bằng SHA-256 & SQLite)\n"
            f"🎯 **Cấp độ hỗ trợ:** `Dễ` • `Trung bình` • `Khó`\n"
            f"🔄 **Chu kỳ reset điểm:** `Cứ 2 tiếng một lần`\n"
            f"⏳ **Thời gian đến lần reset tiếp:** `{time_left}`"
        ),
        color=discord.Color.teal()
    )
    await ctx.send(embed=embed)


if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Missing DISCORD_BOT_TOKEN in .env")
    else:
        bot.run(TOKEN)
