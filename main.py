import flet as ft
import httpx
import asyncio
import random

# API Gateway Endpoint
API_URL = "https://tbpc3gdax9.execute-api.eu-north-1.amazonaws.com/chat"

# Colors
BG_COLOR = "#0A0A0A"
CHAT_BG = "#1E1E1E"
BUBBLE_GRAY = "#2A2A2A"
ACCENT_GREEN = "#00E676"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY = "#8A8A8A"
OFFLINE_GRAY = "#6B6B6B"
ERROR_RED = "#FF5252"

PARTNER_NAMES = ["Riya", "Arjun", "Sneha", "Rahul", "Ananya", "Aditya", "Priya", "Sourav"]


def main(page: ft.Page):
    # Page Setup
    page.title = "AI Chat"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    page.padding = 0
    page.window_width = 400
    page.window_height = 700

    # Shared state
    state = {
        "name": "",
        "age": "",
        "gender": "",
        "partner": random.choice(PARTNER_NAMES),
    }

    # Root container — screen বদলাতে শুধু এর content বদলাবো
    root = ft.Container(expand=True, bgcolor=BG_COLOR)

    # ------------------------------------------------------------------
    # SCREEN 1: User info
    # ------------------------------------------------------------------
    def show_info_screen():
        name_field = ft.TextField(
            label="Your name",
            bgcolor="#1A1A1A",
            border_color="#333333",
            focused_border_color=ACCENT_GREEN,
            color=TEXT_WHITE,
            border_radius=15,
            value=state["name"],
        )

        age_field = ft.TextField(
            label="Your age",
            bgcolor="#1A1A1A",
            border_color="#333333",
            focused_border_color=ACCENT_GREEN,
            color=TEXT_WHITE,
            border_radius=15,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=state["age"],
        )

        error_text = ft.Text("", color=ERROR_RED, size=13)

        gender_options = ["Male", "Female", "Other"]
        gender_chips = []

        def style_chips():
            for chip in gender_chips:
                selected = chip.data == state["gender"]
                chip.bgcolor = ACCENT_GREEN if selected else BUBBLE_GRAY
                chip.content.color = "#000000" if selected else TEXT_WHITE

        def select_gender(e):
            state["gender"] = e.control.data
            style_chips()
            page.update()

        for g in gender_options:
            gender_chips.append(
                ft.Container(
                    content=ft.Text(g, color=TEXT_WHITE, size=15),
                    data=g,
                    bgcolor=BUBBLE_GRAY,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    border_radius=20,
                    on_click=select_gender,
                )
            )
        style_chips()

        async def on_start(e):
            name = (name_field.value or "").strip()
            age_raw = (age_field.value or "").strip()

            if not name:
                error_text.value = "নাম দাও"
                page.update()
                return
            if not age_raw.isdigit() or not (18 <= int(age_raw) <= 99):
                error_text.value = "সঠিক বয়স দাও (18+)"
                page.update()
                return
            if not state["gender"]:
                error_text.value = "Gender select করো"
                page.update()
                return

            state["name"] = name
            state["age"] = age_raw
            state["partner"] = random.choice(PARTNER_NAMES)
            await show_search_screen()

        start_button = ft.Container(
            content=ft.Text(
                "Start", color="#000000", size=17, weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=ACCENT_GREEN,
            padding=ft.padding.symmetric(vertical=14),
            border_radius=25,
            alignment=ft.Alignment(0, 0),
            on_click=on_start,
        )

        root.content = ft.Container(
            padding=ft.padding.all(25),
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SMART_TOY, color=ACCENT_GREEN, size=60),
                    ft.Text("Welcome", size=28, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                    ft.Text("কয়েকটা তথ্য দাও, তারপর কাউকে খুঁজে দেব", size=14, color=TEXT_GRAY),
                    ft.Container(height=15),
                    name_field,
                    age_field,
                    ft.Text("Gender", size=14, color=TEXT_GRAY),
                    ft.Row(gender_chips, spacing=10, wrap=True),
                    error_text,
                    ft.Container(height=5),
                    start_button,
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )
        page.update()

    # ------------------------------------------------------------------
    # SCREEN 2: Fake search
    # ------------------------------------------------------------------
    async def show_search_screen():
        status_text = ft.Text("Searching...", size=16, color=TEXT_WHITE)

        root.content = ft.Container(
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                [
                    ft.ProgressRing(color=ACCENT_GREEN, width=60, height=60, stroke_width=5),
                    ft.Container(height=20),
                    status_text,
                    ft.Text(
                        f"{state['name']}, একটু অপেক্ষা করো",
                        size=13,
                        color=TEXT_GRAY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
        page.update()

        # Fake search messages
        steps = [
            "Searching for someone nearby...",
            "Looking for people online...",
            "Matching interests...",
            "Found someone! Connecting...",
        ]
        for step in steps:
            status_text.value = step
            page.update()
            await asyncio.sleep(random.uniform(1.0, 1.8))

        show_chat_screen()

    # ------------------------------------------------------------------
    # SCREEN 3: Chat
    # ------------------------------------------------------------------
    def show_chat_screen():
        chat_list = ft.ListView(
            expand=True,
            spacing=15,
            padding=ft.padding.all(15),
            auto_scroll=True,
        )

        # Online status widgets
        status_dot = ft.Container(
            width=12, height=12,
            bgcolor=ACCENT_GREEN,
            border_radius=6,
            border=ft.border.all(2, BG_COLOR),
            right=0, bottom=0,
        )
        status_label = ft.Text("Online", size=12, color=ACCENT_GREEN)

        def set_online(is_online: bool):
            status_dot.bgcolor = ACCENT_GREEN if is_online else OFFLINE_GRAY
            status_label.value = "Online" if is_online else "Offline"
            status_label.color = ACCENT_GREEN if is_online else OFFLINE_GRAY

        # Typing indicator
        typing_indicator = ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=8, height=8, bgcolor=ACCENT_GREEN, border_radius=4),
                    ft.Container(width=8, height=8, bgcolor=ACCENT_GREEN, border_radius=4),
                    ft.Container(width=8, height=8, bgcolor=ACCENT_GREEN, border_radius=4),
                ],
                spacing=5,
                tight=True,
            ),
            bgcolor=BUBBLE_GRAY,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border_radius=15,
            margin=ft.margin.only(right=50),
        )
        typing_row = ft.Row([typing_indicator], alignment=ft.MainAxisAlignment.START)

        # Message bubble (max_width Flet 1.0-তে নেই, তাই width নিজে হিসাব)
        def create_message_bubble(text, is_user):
            bg_color = ACCENT_GREEN if is_user else BUBBLE_GRAY
            text_color = "#000000" if is_user else TEXT_WHITE

            max_w = min(280, (page.width or 400) * 0.75)
            longest_line = max((len(line) for line in text.split("\n")), default=1)
            est_w = longest_line * 9.5 + 30
            bubble_w = min(max_w, est_w)

            return ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, color=text_color, size=16, selectable=True),
                        bgcolor=bg_color,
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        border_radius=ft.border_radius.only(
                            top_left=15, top_right=15,
                            bottom_left=15 if is_user else 0,
                            bottom_right=0 if is_user else 15,
                        ),
                        width=bubble_w,
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
            )

        # Send message
        async def send_message(e):
            user_text = (input_field.value or "").strip()
            if not user_text:
                return

            chat_list.controls.append(create_message_bubble(user_text, True))
            input_field.value = ""
            page.update()

            chat_list.controls.append(typing_row)
            page.update()

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        API_URL,
                        json={
                            "message": user_text,
                            "user": {
                                "name": state["name"],
                                "age": state["age"],
                                "gender": state["gender"],
                            },
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=30.0,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        bot_reply = data.get("reply", data.get("message", "Response format unknown."))
                        set_online(True)
                    else:
                        bot_reply = f"Error: {response.status_code} - {response.text}"
                        set_online(True)

            except Exception:
                bot_reply = "দুঃখিত, সার্ভারের সাথে সংযোগ করা যাচ্ছে না। আবার চেষ্টা করুন।"
                set_online(False)

            if typing_row in chat_list.controls:
                chat_list.controls.remove(typing_row)
            chat_list.controls.append(create_message_bubble(bot_reply, False))
            page.update()

        # Input bar
        input_field = ft.TextField(
            hint_text="Type a message...",
            bgcolor="#1A1A1A",
            border_color="#333333",
            focused_border_color=ACCENT_GREEN,
            color=TEXT_WHITE,
            expand=True,
            border_radius=25,
            on_submit=send_message,
        )

        send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color="#000000",
            bgcolor=ACCENT_GREEN,
            icon_size=20,
            on_click=send_message,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=25),
                padding=15,
            ),
        )

        input_bar = ft.Container(
            content=ft.Row(
                [input_field, send_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(10),
            bgcolor=BG_COLOR,
            border=ft.border.only(top=ft.BorderSide(1, "#2A2A2A")),
        )

        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Stack(
                        [
                            ft.CircleAvatar(
                                bgcolor=BUBBLE_GRAY,
                                content=ft.Icon(ft.Icons.PERSON, color=TEXT_WHITE),
                            ),
                            status_dot,
                        ],
                        width=44,
                        height=44,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                state["partner"], size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_WHITE,
                            ),
                            status_label,
                        ],
                        spacing=2,
                    ),
                ],
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=BG_COLOR,
            border=ft.border.only(bottom=ft.BorderSide(1, "#2A2A2A")),
        )

        # Opening message from partner
        chat_list.controls.append(
            create_message_bubble(f"Hi {state['name']}! 👋", False)
        )

        root.content = ft.Column(
            [
                header,
                ft.Container(content=chat_list, bgcolor=CHAT_BG, expand=True),
                input_bar,
            ],
            spacing=0,
            expand=True,
        )
        page.update()

    # Start
    page.add(root)
    show_info_screen()


ft.run(main)
