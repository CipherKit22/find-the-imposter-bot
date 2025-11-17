#!/usr/bin/env python3
"""
Find the Imposter - Telegram Bot (Burmese)
Modified: If crewmate is wrongly eliminated, remove them and CONTINUE the game:
 - remaining players are re-randomized for clue order
 - game continues only if remaining players >= 3
 - votes reset and clue-taking resumes
 - standard win checks (all imposters out -> crew win; imposters >= crewmates -> imposter win)
Requires python-telegram-bot v20+ async API
"""
import os
import sys
import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from telegram import (
    Update,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.error import InvalidToken

# ---------- CONFIG ----------
TOKEN = os.environ.get("BOT_TOKEN")  # set this in your environment
MIN_PLAYERS = 3
MAX_PLAYERS = 30
WORD_LIST = [
    "ကြက် (chicken)",
    "နို့ (milk)",
    "ကား (car)",
    "ပန်း (flower)",
    "စာအုပ် (book)",
    "တံခါး (door)",
    "မီး (fire/light)",
    "ငါး (fish)",
    "တိမ် (cloud)",
    "ဖုန် (dust)",

    # Animals
    "ကျား (tiger)",
    "ဆိတ် (goat)",
    "နွား (cow)",
    "မြင်း (horse)",
    "မြွေ (snake)",
    "ခွေး (dog)",
    "ကြောင် (cat)",
    "ဝက် (pig)",
    "ပိုးမွှား (insect)",
    "လိပ်ပြာ (butterfly)",
    "လိပ် (turtle)",
    "ဂဏန်း (crab)",
    "ပုစွန် (shrimp)",
    "ငှက် (bird)",
    "ဥ (egg)",
    "မျောက် (monkey)",
    "ပုရွက်ဆိတ် (ant)",
    "ဇီးကွက် (owl)",
    "ငါးမန်း (shark)",

    # Food
    "ထမင်း (rice)",
    "ဆန် (rice grain)",
    "ပဲ (bean)",
    "ပေါင်မုန့် (bread)",
    "ဟင်း (curry)",
    "သစ်သီး (fruit)",
    "ပန်းသီး (apple)",
    "ငှက်ပျောသီး (banana)",
    "သရက်သီး (mango)",
    "နာနတ်သီး (pineapple)",
    "ခရမ်းချဉ်သီး (tomato)",
    "အသီးခြောက် (dried fruit)",
    "ဆီ (oil)",
    "သကြား (sugar)",
    "အမှုန့် (powder)",
    "ငရုတ်ကောင်း (pepper)",
    "ဆား (salt)",
    "ရေ (water)",
    "ဟင်းသီးဟင်းရွက် (vegetables)",
    "မုန်လာဥ (carrot)",
    "အာလူး (potato)",
    "ငရုတ်သီး (chili)",
    "ကိတ်မုန့် (cake)",
    "ဒိန်ချဉ် (yogurt)",
    "ချီး (shit)",
    "သေး (piss)",

    # Places
    "အိမ် (house)",
    "ကျောင်း (school)",
    "ဆေးရုံ (hospital)",
    "ဈေး (market)",
    "ဘူတာရုံ (station)",
    "လမ်း (road)",
    "တောင် (mountain)",
    "တိုက်ခန်း (apartment)",
    "ရုံး (office)",
    "ကန် (lake)",
    "မြစ် (river)",
    "ပင်လယ် (ocean)",
    "တော (forest)",
    "ကျေးရွာ (village)",
    "မြို့ (city)",
    "အိမ်သာ (toilet)",
    "စားသောက်ဆိုင် (restaurant)",
    "ဟိုတယ် (hotel)",

    # Common objects
    "စားပွဲ (table)",
    "ခုံ (chair)",
    "ဘောပင် (pen)",
    "ခဲတံ (pencil)",
    "စာရွက် (paper)",
    "နာရီ (clock/watch)",
    "ဖုန်း (phone)",
    "ကွန်ပျူတာ (computer)",
    "အိတ် (bag)",
    "ငွေ (money)",
    "လျှပ်စစ်မီး (electricity)",
    "ရေကူးကန် (pool)",
    "သော့ (key)",
    "ဘောင်းဘီ (pants)",
    "ဖိနပ် (shoes)",
    "မှန် (mirror)",
    "ခြင်ထောင် (mosquito net)",

    # Nature & Weather
    "နေ (sun)",
    "လ (moon)",
    "ကြယ် (star)",
    "မိုး (rain)",
    "မိုးတိမ် (cloud)",
    "မုန်တိုင်း (storm)",
    "လေ (wind)",
    "မြေကြီး (soil)",
    "ကျောက်တုံး (stone)",
    "သဘာဝ (nature)",
    "အပင် (tree)",
    "အရွက် (leaf)",
    "မိုးသီး (hail)",
    "မြူ (fog)",

    # Body parts
    "ခေါင်း (head)",
    "မျက်လုံး (eye)",
    "နား (ear)",
    "နှာခေါင်း (nose)",
    "နှုတ်ခမ်း (lips)",
    "ပါး (cheek)",
    "လက် (hand)",
    "ခြေ (foot)",
    "ချိုင့် (knee)",
    "လည်ပင်း (neck)",
    "ရင်ဘတ် (chest)",
    "အသား (skin)",
    "ဆံပုံး (hair)",
    "မွေး (beard)",
    "သွား (tooth)",
    "အသည်း (liver)",
    "နှလုံး (heart)",


    # Transport
    "ရထား (train)",
    "လေယာဉ် (airplane)",
    "ဆိုင်ကယ် (motorcycle)",
    "ဘတ်စ်ကား (bus)",
    "သင်္ဘော (ship)",
    "အငှားကား (taxi)",
    "စက်ဘီး (bicycle)",

    # Misc
    "အရောင် (color)",
    "အသံ (sound)",
    "အနံ့ (smell)",
    "အလင်း (light)",
    "အမှောင် (darkness)",
    "အခန်း (room)",
    "လက်ဆောင် (gift)",
    "အသက် (life)",
    "ခြေရာ (footprint)",
    "လက်ရေး (handwriting)",
    "အကြံဉာဏ် (idea)",
    "သတင်း (news)",
    "ပျော်ရွှင်ခြင်း (happiness)",
    "မေတ္တာ (love)"
]


# Burmese messages (short keys)
B = {
    "already_game": "ဤ group တွင် လက်ရှိဂိမ်းတစ်ခု ဆော့ကစားနေပါသည် — အဲဒီဂိမ်းပြီးမှသာ /newgame လုပ်နိုင်သည်။",
    "game_created": "ဂိမ်းအသစ် ဖန်တီးပြီးပါပြီ — သင်က host ဖြစ်ပါတယ်။ /join ဖြင့် ကစားသမားများ စုဆောင်းပါ။ သင်ကိုယ်တိုင်လည်း /join ပါ။",
    "joined": "{user} သင်က ဂိမ်းထဲ ဝင်ပြီးပါပြီ။",
    "left": "{user} သင်က ဂိမ်းထဲ ထွက်ပြီးပါပြီ။",
    "not_enough_players": "ကစားသမား အနည်းဆုံး {min} ဦး လိုအပ်သည် — လက်ရှိ: {now} ဦး။",
    "host_only_cmd_used": "ဒီ command ကို host ကလွဲ၍ တခြားလူ သုံးခွင့် မရှိပါ — သင့် Host: {host}",
    "game_started": "ဂိမ်း စတင်လိုက်ပါပြီ — Bot က players အားလုံးရဲ့ DM မှာ ပို့ထားပြီးပါပြီ။",
    "dm_prefix": "သားသားချစ်တဲ့ {fullname} ခင်ဗျာ\n\n",
    "dm_imposter": "သင်က Imposter ဖြစ်ပါတယ် — သင်ဘာမှမသိလို့ သူများပြောတာကြည့်ပြီး လျှောက်ရွှီးပါ။",
    "dm_crewmate": "သင်က Crewmate ဖြစ်ပါတယ် — စကားလုံး: {word}\n\nclue များကို မသိသာအောင်ပြောပါ။",
    "order_announce": "Clue ပေးရမည့် အစီစဉ် (randomized):\n{order}",
    "not_your_turn": "ယခု သင့်အလှည့်မဟုတ်ပါ — ခင်ဗျာ။ သင့်: {expected}",
    "clue_recorded": "{user} ရဲ့ clue မှတ်တမ်းတင်ပြီးပါပြီ — \"{clue}\"",
    "vote_prompt_buttons": "အောက်က ခလုတ်ကို နှိပ်၍ မဲပေးပါ။ တစ်ယောက် တစ်ခါသာ မဲပေးနိုင်သည်။ လက်မယားပါနဲ့။",
    "already_voted": "သင်သည် ယခင်တွင် မဲပေးပြီးသား (target: {target}) — တစ်ခါထက် မပိုနိုင်ပါ။",
    "vote_recorded": "{voter} က {target} ကို မဲပေးပြီးပါပြီ။",
    "endgame_locked": "ဂိမ်းကို host က endgame လုပ်ပြီးပါပြီ — နောက်ထပ် /clue သို့မဟုတ် /vote မရပါ။",
    "result_header": "Voting result:",
    "eliminated_is": "မဲအများဆုံးပေးခံရသူ {target} — role: {role}",
    "no_elimination": "မဲတူနေသောကြောင့် ဘာမှမထူးပါ။",
    "crew_win": "Imposter ကို ထုတ်လိုက်နိုင်သည့်အတွက် Crewmates အနိုင်ရပါမည်! 🎉",
    "imposter_win": "Imposter ကို မထုတ်နိုင်သည့်အတွက် Imposter အနိုင်ရပါမည်! 😈",
    "imposter_reveal": "တကယ့် imposter :\n{list}",
    "game_finished": "ဂိမ်းပြီးဆုံးပါပြီ — အခု /newgame ပြန်လုပ်နိုင်ပါပြီ။",
    "cancelled": "ဂိမ်းကို ပယ်ဖျက်လိုက်ပါပြီ။",
    "help_text": (
        "/newgame [num_imposters] - ဂိမ်းအသစ် ဖန်တီး (creator becomes host)\n"
        "/join - ဂိမ်းထဲပါဝင်ရန်\n"
        "/leave - ဂိမ်းမှထွက်ရန်\n"
        "/startgame - Host သာစတင်နိုင်\n"
        "/clue <text> - သတ်မှတ်ထားသော စကားလုံးအရ clue ပေးရန်\n"
        "/vote - မဲပေးရန်\n"
        "/endgame - Host မှ ပွဲပြီးကြောင်းကြေညာ (clue/vote ပိတ်)\n"
        "/result - Host only — votes ဖော်ပြပြီး ရလဒ်ကြေညာ\n"
        "/cancelgame - Host only — game ပယ်ဖျက်\n"
        "/status - ဂိမ်း status ကြည့်ရန်\n"
        "/help - commands များကိုရန်"
    ),
    "dm_fail_notify": "{name} သည် Bot အား DM တွက် start မလုပ်ထားသဖြင့် စာမပို့နိုင်ပါ။ {name} အား start ပြန်လုပ်ခိုင်း၍ ဂိမ်းပွဲအသစ်စတင်ပါ။",
    "unknown_cmd": "သုံးမရသော command — သုံးလို့ရတာတွေကို /help တွင်ကြည့်ပါ။",
    "continue_round": "အမှားထုတ်ပြီး Crewmate ကို ဖယ်ထုတ်လိုက်ပါပြီ — ဂိမ်းကို ဆက်လုပ်မည် (players remaining: {n})။\nနောက်တစ်ကြိမ် clue အစီအစဉ်ကို randomize ပြန်လုပ်ပြီး စတင်ပါမည်။",
    "not_enough_to_continue": "ကျန်တဲ့ ကစားသမားအရေအတွက် {n} — ဂိမ်းကို ဆက်လုပ်ရန် အနည်းဆုံး 3 ယောက် လိုအပ်သည်။ ဂိမ်းကို ပြီးဆုံးပြီလို့ သတ်မှတ်ပြီး Imposter ကို ဖော်ထုတ်ပေးပါမည်။",
    "next_start": "clue ပြောရန်အလှည့်ကျသူ : {who} — /clue <text> ဖြင့် clue ပေးပါ။",
}

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


# Data classes
@dataclass
class Player:
    user: User
    role: str = "crewmate"  # or 'imposter'
    word: Optional[str] = None


@dataclass
class Game:
    chat_id: int
    host_id: int
    num_imposters: int = 1
    players: Dict[int, Player] = field(default_factory=dict)
    started: bool = False
    secret_word: Optional[str] = None
    order: List[int] = field(default_factory=list)  # clue order
    current_turn_index: int = 0
    locked: bool = False  # after endgame
    votes: Dict[int, int] = field(default_factory=dict)  # voter_id -> target_id

    def add_player(self, user: User) -> bool:
        if len(self.players) >= MAX_PLAYERS:
            return False
        if user.id in self.players:
            return False
        self.players[user.id] = Player(user=user)
        return True

    def remove_player(self, user_id: int) -> bool:
        if user_id in self.players:
            del self.players[user_id]
            if user_id in self.order:
                self.order.remove(user_id)
            # remove votes by or for them
            self.votes = {v: t for v, t in self.votes.items() if v != user_id and t != user_id}
            return True
        return False

    def assign_roles(self):
        ids = list(self.players.keys())
        random.shuffle(ids)
        imposters = set(ids[: self.num_imposters]) if self.num_imposters < len(ids) else set(ids[:1])
        for uid in ids:
            p = self.players[uid]
            if uid in imposters:
                p.role = "imposter"
                p.word = None
            else:
                p.role = "crewmate"
                p.word = self.secret_word
        # shuffle clue order
        self.order = list(ids)
        random.shuffle(self.order)
        self.current_turn_index = 0

    def current_player_id(self) -> Optional[int]:
        if not self.order:
            return None
        return self.order[self.current_turn_index % len(self.order)]

    def advance_turn(self):
        if not self.order:
            return
        self.current_turn_index = (self.current_turn_index + 1) % len(self.order)

    def all_voted(self) -> bool:
        return len(self.votes) >= len(self.players)


# In-memory games store: chat_id -> Game
GAMES: Dict[int, Game] = {}


# Helpers
def user_mention(u: User) -> str:
    if u.username:
        return f"@{u.username} ({u.full_name})"
    return u.full_name


# ---------- Handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Find the Imposter Burmese bot — /help ကို ကြည့်ပါ။")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(B["help_text"])


async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id in GAMES:
        await update.message.reply_text(B["already_game"])
        return
    num_imp = 1
    if context.args:
        try:
            v = int(context.args[0])
            if v >= 1:
                num_imp = v
        except Exception:
            pass
    game = Game(chat_id=chat_id, host_id=user.id, num_imposters=num_imp)
    GAMES[chat_id] = game
    await update.message.reply_text(B["game_created"])


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in GAMES:
        await update.message.reply_text("ဤ group တွင် /newgame ဖြင့် ဂိမ်းပွဲအသစ်ဖန်တီးပါ။")
        return
    game = GAMES[chat_id]
    if game.started:
        await update.message.reply_text("ဂိမ်းစတင်ပြီးသားဖြစ်သဖြင့် — /join မရသေးပါ။")
        return
    ok = game.add_player(user)
    if not ok:
        await update.message.reply_text("သင်ဟာ လက်ရှိ ကစားသူအဖြစ် ရှိနေပါသည် သို့မဟုတ် အသင်းပြည့်နေပါပြီ။")
        return
    await update.message.reply_text(B["joined"].format(user=user_mention(user)))


async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in GAMES:
        await update.message.reply_text("လက်ရှိဆော့ကစားနေသော ဂိမ်း မရှိပါ။")
        return
    game = GAMES[chat_id]
    if game.remove_player(user.id):
        await update.message.reply_text(B["left"].format(user=user_mention(user)))
    else:
        await update.message.reply_text("သင် ဂိမ်းထဲ မပါသေးပါ။")


async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in GAMES:
        await update.message.reply_text("/newgame ဖြင့် ဂိမ်းဖန်တီးပါ။")
        return
    game = GAMES[chat_id]
    if user.id != game.host_id:
        host_user = (await context.bot.get_chat_member(chat_id, game.host_id)).user
        await update.message.reply_text(B["host_only_cmd_used"].format(host=user_mention(host_user)))
        return
    if game.started:
        await update.message.reply_text("ဂိမ်းတစ်ပွဲ စတင်ထားပြီးဖြစ်ပါသည်။")
        return
    if len(game.players) < MIN_PLAYERS:
        await update.message.reply_text(B["not_enough_players"].format(min=MIN_PLAYERS, now=len(game.players)))
        return
    # pick secret and assign
    game.secret_word = random.choice(WORD_LIST)
    game.assign_roles()
    game.started = True
    # DM players
    for pid, p in game.players.items():
        try:
            prefix = B["dm_prefix"].format(fullname=p.user.full_name)
            if p.role == "imposter":
                msg = prefix + B["dm_imposter"]
            else:
                msg = prefix + B["dm_crewmate"].format(word=p.word)
            await context.bot.send_message(chat_id=pid, text=msg)
        except Exception as e:
            logger.warning("DM failed to %s: %s", pid, e)
            await update.message.reply_text(B["dm_fail_notify"].format(name=p.user.full_name))
    # announce start and order
    order_lines = []
    for i, uid in enumerate(game.order, start=1):
        u = game.players[uid].user
        order_lines.append(f"{i}. {user_mention(u)}")
    await update.message.reply_text(B["game_started"])
    await update.message.reply_text(B["order_announce"].format(order="\n".join(order_lines)))
    cur_id = game.current_player_id()
    if cur_id:
        await update.message.reply_text(f"စတင်သူ: {user_mention(game.players[cur_id].user)} — /clue <text> ဖြင့် clue ပေးပါ။")


async def clue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in GAMES:
        await update.message.reply_text("ဂိမ်း မရှိပါ။")
        return
    game = GAMES[chat_id]
    if not game.started or game.locked:
        await update.message.reply_text("ဂိမ်းမစတင်သေးပါ (သို့) endgame ဖြင့် ပိတ်ထားသည်။")
        return
    cur_id = game.current_player_id()
    if cur_id != user.id:
        expected = user_mention(game.players[cur_id].user) if cur_id in game.players else "unknown"
        await update.message.reply_text(B["not_your_turn"].format(expected=expected))
        return
    if not context.args:
        await update.message.reply_text("/clue <text> — သင့် clue ထည့်ပါ။")
        return
    clue_text = " ".join(context.args)
    await update.message.reply_text(B["clue_recorded"].format(user=user_mention(user), clue=clue_text))
    game.advance_turn()
    next_id = game.current_player_id()
    if next_id:
        await update.message.reply_text(B["next_start"].format(who=user_mention(game.players[next_id].user)))


# Build inline keyboard for voting
def build_vote_keyboard(game: Game):
    buttons = []
    row = []
    count = 0
    for uid, p in game.players.items():
        # display name (short)
        display = p.user.full_name if len(p.user.full_name) <= 20 else p.user.full_name[:17] + "..."
        row.append(InlineKeyboardButton(display, callback_data=f"vote:{game.chat_id}:{uid}"))
        count += 1
        # put 2 buttons per row
        if count % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if user typed /vote show inline buttons listing joined players
    chat = update.effective_chat
    chat_id = chat.id
    if chat_id not in GAMES:
        await update.message.reply_text("ဂိမ်း မရှိပါ — /newgame ဖြင့် စတင်ပါ။")
        return
    game = GAMES[chat_id]
    if not game.started or game.locked:
        await update.message.reply_text(B["endgame_locked"])
        return
    # show inline keyboard
    kb = build_vote_keyboard(game)
    await update.message.reply_text(B["vote_prompt_buttons"], reply_markup=kb)


# CallbackQuery handler for button taps
async def on_vote_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # acknowledge quickly (no alert)
    data = query.data  # expected like "vote:chat_id:target_id"
    user = query.from_user
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "vote":
        await query.edit_message_text("Unknown action.")
        return
    try:
        chat_id = int(parts[1])
        target_id = int(parts[2])
    except Exception:
        await query.edit_message_text("Invalid vote payload.")
        return
    if chat_id not in GAMES:
        await query.edit_message_text("ဂိမ်း မရှိတော့ပါ။")
        return
    game = GAMES[chat_id]
    if not game.started or game.locked:
        await query.edit_message_text(B["endgame_locked"])
        return
    # enforce voter is a player in this game
    if user.id not in game.players:
        # send alert to user
        await query.answer(text="သင် ဂိမ်းထဲ မပါသေးပါ — /join ဖြင့် ဝင်ပါ။", show_alert=True)
        return
    # one vote per voter
    if user.id in game.votes:
        prev = game.votes[user.id]
        await query.answer(text=f"သင် ယခင်က မဲပေးပြီးသား ဖြစ်ပါတယ်။ လက်မယားပါနဲ့။ (target: {user_mention(game.players[prev].user)})", show_alert=True)
        return
    # ensure target still in players
    if target_id not in game.players:
        await query.answer(text="ဤကစားသမားသည် ဂိမ်းထဲတွင်မရှိတော့ပါ။", show_alert=True)
        return
    # register vote
    game.votes[user.id] = target_id
    # notify in group chat (not editing original keyboard message; keep keyboard)
    try:
        await context.bot.send_message(chat_id=chat_id, text=B["vote_recorded"].format(voter=user_mention(user), target=user_mention(game.players[target_id].user)))
    except Exception:
        # permission issue; fall back to reply
        await query.edit_message_text(B["vote_recorded"].format(voter=user_mention(user), target=user_mention(game.players[target_id].user)))
    # also answer the callback to voter with a small confirmation
    await query.answer(text="မဲပေးခြင်းပြီးပါပြီ", show_alert=False)

    # optionally, auto-notify host when everyone voted
    if game.all_voted():
        host = (await context.bot.get_chat_member(chat_id, game.host_id)).user
        await context.bot.send_message(chat_id=chat_id, text=f"အကုန်လုံး မဲပေးပြီးပါပြီ — Host {user_mention(host)} က /result ဖြင့် ရလဒ်ကြေညာနိုင်သည်။")


async def endgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in GAMES:
        await update.message.reply_text("ဂိမ်း မရှိပါ။")
        return
    game = GAMES[chat_id]
    if user.id != game.host_id:
        host_user = (await context.bot.get_chat_member(chat_id, game.host_id)).user
        await update.message.reply_text(B["host_only_cmd_used"].format(host=user_mention(host_user)))
        return
    game.locked = True
    await update.message.reply_text("Host က endgame လုပ်လိုက်သည် — မဲပေးခြင်းနှင့် clue ပေးခြင်း ပိတ်ထားပါပြီ။ /result ဖြင့် ရလဒ် ကြေညာနိုင်ပါသည်။")


def count_roles(players: Dict[int, Player]):
    imposters = sum(1 for p in players.values() if p.role == "imposter")
    crewmates = sum(1 for p in players.values() if p.role == "crewmate")
    return imposters, crewmates


async def reveal_imposters_and_finish(chat_id: int, game: Game, context: ContextTypes.DEFAULT_TYPE):
    imposters = [p.user for p in game.players.values() if p.role == "imposter"]
    if imposters:
        lines = []
        for i, u in enumerate(imposters, start=1):
            lines.append(f"{i}. {user_mention(u)}")
        await context.bot.send_message(chat_id=chat_id, text=B["imposter_reveal"].format(list="\n".join(lines)))
    await context.bot.send_message(chat_id=chat_id, text=B["game_finished"])
    if chat_id in GAMES:
        del GAMES[chat_id]


async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in GAMES:
        await update.message.reply_text("ဂိမ်း မရှိပါ။")
        return
    game = GAMES[chat_id]
    if user.id != game.host_id:
        host_user = (await context.bot.get_chat_member(chat_id, game.host_id)).user
        await update.message.reply_text(B["host_only_cmd_used"].format(host=user_mention(host_user)))
        return

    # show who voted for whom
    lines = [B["result_header"]]
    if not game.votes:
        lines.append("No votes cast.")
    else:
        for voter_id, target_id in game.votes.items():
            v = game.players.get(voter_id)
            t = game.players.get(target_id)
            if v and t:
                lines.append(f"- {user_mention(v.user)} => {user_mention(t.user)}")
    await update.message.reply_text("\n".join(lines))

    # tally votes
    tally: Dict[int, int] = {}
    for t in game.votes.values():
        tally[t] = tally.get(t, 0) + 1

    if not tally:
        await update.message.reply_text(B["no_elimination"])
        # No elimination; end game (as before)
        del GAMES[chat_id]
        await update.message.reply_text(B["game_finished"])
        return

    max_votes = max(tally.values())
    top = [tid for tid, c in tally.items() if c == max_votes]
    if len(top) > 1:
        await update.message.reply_text(B["no_elimination"])
        # tied -> finish game
        del GAMES[chat_id]
        await update.message.reply_text(B["game_finished"])
        return

    eliminated_id = top[0]
    eliminated_player = game.players.get(eliminated_id)
    if not eliminated_player:
        await update.message.reply_text("Selected player not found — aborting.")
        del GAMES[chat_id]
        await update.message.reply_text(B["game_finished"])
        return

    # Announce eliminated and their role
    await update.message.reply_text(B["eliminated_is"].format(target=user_mention(eliminated_player.user), role=eliminated_player.role))

    # If eliminated was an imposter -> crew win and finish
    if eliminated_player.role == "imposter":
        await update.message.reply_text(B["crew_win"])
        # Optionally reveal imposters (others) as well
        await reveal_imposters_and_finish(chat_id, game, context)
        return

    # Else: eliminated was a crewmate -> remove them and CONTINUE if possible
    # remove player from game (but keep game object)
    game.remove_player(eliminated_id)
    # reset votes for next round
    game.votes = {}

    remaining = len(game.players)
    # If remaining players less than required to continue, end and reveal imposters
    if remaining < 3:
        await update.message.reply_text(B["not_enough_to_continue"].format(n=remaining))
        await reveal_imposters_and_finish(chat_id, game, context)
        return

    # Check win/loss immediate conditions:
    imposters_count, crewmates_count = count_roles(game.players)
    # If no imposters left -> crew win
    if imposters_count == 0:
        await update.message.reply_text(B["crew_win"])
        await reveal_imposters_and_finish(chat_id, game, context)
        return
    # If imposters are >= crewmates -> imposter win
    if imposters_count >= crewmates_count:
        await update.message.reply_text(B["imposter_win"])
        await reveal_imposters_and_finish(chat_id, game, context)
        return

    # Otherwise continue the game:
    # Re-randomize clue order among remaining players and reset turn index
    game.order = list(game.players.keys())
    random.shuffle(game.order)
    game.current_turn_index = 0
    # Announce continuation and new order (short)
    await update.message.reply_text(B["continue_round"].format(n=remaining))
    order_lines = []
    for i, uid in enumerate(game.order, start=1):
        u = game.players[uid].user
        order_lines.append(f"{i}. {user_mention(u)}")
    await update.message.reply_text(B["order_announce"].format(order="\n".join(order_lines)))
    # Announce next starter
    cur_id = game.current_player_id()
    if cur_id:
        await update.message.reply_text(B["next_start"].format(who=user_mention(game.players[cur_id].user)))
    # Game remains in GAMES and not locked; players may continue /clue and /vote as usual.


async def cancelgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in GAMES:
        await update.message.reply_text("ဂိမ်း မရှိပါ။")
        return
    game = GAMES[chat_id]
    if user.id != game.host_id:
        host_user = (await context.bot.get_chat_member(chat_id, game.host_id)).user
        await update.message.reply_text(B["host_only_cmd_used"].format(host=user_mention(host_user)))
        return
    del GAMES[chat_id]
    await update.message.reply_text(B["cancelled"])


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in GAMES:
        await update.message.reply_text("ဂိမ်း မရှိပါ။")
        return
    game = GAMES[chat_id]
    host_user = (await context.bot.get_chat_member(chat_id, game.host_id)).user
    text = f"Host: {user_mention(host_user)}\nPlayers ({len(game.players)}):\n"
    for p in game.players.values():
        text += f" - {user_mention(p.user)}\n"
    imposters_count, crewmates_count = count_roles(game.players)
    text += f"Started: {game.started}\nLocked: {game.locked}\nVotes cast: {len(game.votes)}\nImposters: {imposters_count}, Crewmates: {crewmates_count}\n"
    await update.message.reply_text(text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(B["unknown_cmd"])


# ---------- MAIN ----------
def main():
    if not TOKEN:
        print("Error: BOT_TOKEN သတ်မှတ်ထားရန်။ (environment variable)")
        sys.exit(1)

    try:
        app = ApplicationBuilder().token(TOKEN).build()
    except InvalidToken:
        logger.exception("Telegram rejected the token during ApplicationBuilder.")
        print("Invalid token — BotFather မှ token ကို ထပ်မံစစ်ပါ။")
        sys.exit(2)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("newgame", newgame))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("startgame", startgame))
    app.add_handler(CommandHandler("clue", clue))
    app.add_handler(CommandHandler("vote", vote))
    app.add_handler(CallbackQueryHandler(on_vote_button, pattern=r"^vote:"))
    app.add_handler(CommandHandler("endgame", endgame))
    app.add_handler(CommandHandler("result", result))
    app.add_handler(CommandHandler("cancelgame", cancelgame))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("Bot started...")
    try:
        app.run_polling()
    except InvalidToken:
        logger.exception("Invalid token detected while running.")
        print("Invalid token — BotFather မှ token ကို ထပ်မံစစ်ပါ။")
        sys.exit(2)


if __name__ == "__main__":
    main()
