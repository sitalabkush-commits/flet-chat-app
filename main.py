import flet as ft
import httpx
import asyncio

# API Gateway Endpoint
API_URL = "https://tbpc3gdax9.execute-api.eu-north-1.amazonaws.com/chat"

def main(page: ft.Page):
    # Page Setup
    page.title = "AI Chat"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0A0A0A"
    page.padding = 0
    page.window_width = 400
    page.window_height = 700

    # Colors
    BG_COLOR = "#0A0A0A"
    CHAT_BG = "#1E1E1E"
    BUBBLE_GRAY = "#2A2A2A"
    ACCENT_GREEN = "#00E676" # Emerald/Mint
    TEXT_WHITE = "#FFFFFF"

    # Chat List View
    chat_list = ft.ListView(
        expand=True,
        spacing=15,
        padding=ft.padding.all(15),
        auto_scroll=True,
    )

    # Typing Indicator (Loading state)
    typing_indicator = ft.Container(
        content=ft.Row(
            [
                ft.Container(width=8, height=8, bgcolor=ACCENT_GREEN, border_radius=4),
                ft.Container(width=8, height=8, bgcolor=ACCENT_GREEN, border_radius=4),
                ft.Container(width=8, height=8, bgcolor=ACCENT_GREEN, border_radius=4),
            ],
            spacing=5,
        ),
        bgcolor=BUBBLE_GRAY,
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        border_radius=15,
        visible=False, # Initially hidden
        margin=ft.margin.only(left=10, right=50, bottom=10)
    )

    # Message Bubbles Function
    def create_message_bubble(text, is_user):
        bg_color = ACCENT_GREEN if is_user else BUBBLE_GRAY
        text_color = "#000000" if is_user else TEXT_WHITE
        
        return ft.Row(
            [
                ft.Container(
                    content=ft.Text(text, color=text_color, size=16),
                    bgcolor=bg_color,
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    border_radius=ft.border_radius.only(
                        top_left=15, top_right=15,
                        bottom_left=15 if is_user else 0,
                        bottom_right=0 if is_user else 15
                    ),
                    max_width=280,
                )
            ],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
        )

    # Send Message Function
    async def send_message(e):
        user_text = input_field.value.strip()
        if not user_text:
            return

        # 1. Add User Message
        chat_list.controls.append(create_message_bubble(user_text, True))
        input_field.value = ""
        page.update()

        # 2. Show Typing Indicator
        typing_indicator.visible = True
        chat_list.controls.append(typing_indicator)
        page.update()

        # 3. Make API Call
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    API_URL,
                    json={"message": user_text},
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # এখানে API এর রেসপন্স ফরম্যাট অনুযায়ী 'reply' অথবা 'message' কী-টি দিতে হবে
                    bot_reply = data.get("reply", data.get("message", "Response format unknown."))
                else:
                    bot_reply = f"Error: {response.status_code} - {response.text}"
                    
        except Exception as ex:
            bot_reply = "দুঃখিত, সার্ভারের সাথে সংযোগ করা যাচ্ছে না। আবার চেষ্টা করুন।"

        # 4. Remove Typing Indicator & Add Bot Message
        typing_indicator.visible = False
        chat_list.controls.remove(typing_indicator)
        chat_list.controls.append(create_message_bubble(bot_reply, False))
        page.update()

    # Input Field & Send Button
    input_field = ft.TextField(
        hint_text="Type a message...",
        bgcolor="#1A1A1A",
        border_color="#333333",
        focused_border_color=ACCENT_GREEN,
        color=TEXT_WHITE,
        expand=True,
        border_radius=25,
        on_submit=send_message, # Enter key press
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
        )
    )

    # Bottom Input Bar
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
                            content=ft.Icon(ft.Icons.SMART_TOY, color=TEXT_WHITE),
                        ),
                        # Online Status Green Dot
                        ft.Container(
                            width=12, height=12,
                            bgcolor=ACCENT_GREEN,
                            border_radius=6,
                            border=ft.border.all(2, BG_COLOR),
                            right=0, bottom=0
                        )
                    ]
                ),
                ft.Column(
                    [
                        ft.Text("AI Assistant", size=18, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                        ft.Text("Online", size=12, color=ACCENT_GREEN),
                    ],
                    spacing=2,
                )
            ],
        ),
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        bgcolor=BG_COLOR,
        border=ft.border.only(bottom=ft.BorderSide(1, "#2A2A2A")),
    )

    # Layout Assembly
    main_layout = ft.Column(
        [
            header,
            ft.Container(content=chat_list, bgcolor=CHAT_BG, expand=True),
            input_bar,
        ],
        spacing=0,
        expand=True,
    )

    page.add(main_layout)

# Flet 1.0 এর জন্য ft.app এর বদলে ft.run ব্যবহার করতে হবে
ft.run(main)
