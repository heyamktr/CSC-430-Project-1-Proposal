from pathlib import Path
from sys import exit

import pygame

from clicker_symmetric_encryption import GAME_FILE_CONTENTS, decrypt_file, sync_all_files, sync_file
from sheet_key_store import DEFAULT_USER_ID, fetch_key

pygame.init()
pygame.display.set_caption("Clicker")

BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "fonts" / "font.ttf"
IMAGE_PATH = BASE_DIR / "graphics" / "img.png"
PLAYER_ID = DEFAULT_USER_ID

clock = pygame.time.Clock()


def load_font(size):
    if FONT_PATH.exists():
        return pygame.font.Font(str(FONT_PATH), size)
    return pygame.font.SysFont(None, size)


font = load_font(50)
small_font = load_font(18)

VP_W = 1200
VP_H = 600
MENU_W = VP_W // 3

vp = pygame.display.set_mode((VP_W, VP_H))

score = 0
click_power = 1
upgrade_cost = 20
status_message = "Connecting to Google Sheets..."
owned_keys = []
opened_file_name = ""
opened_file_text = "Buy a key, then decrypt the file to read it here."
shop_costs = {
    "file1.txt": 50,
    "file2.txt": 200,
    "file3.txt": 500,
}

files = [{"name": name, "cost": shop_costs[name]} for name in GAME_FILE_CONTENTS]

click_btn = pygame.Rect(0, 0, 0, 0)
upgrade_btn = pygame.Rect(0, 0, 0, 0)
item_btns = []
decrypt_btns = []


def set_status(message):
    global status_message
    status_message = message


def initialize_sheet_keys():
    ready_count = 0
    synced_files = sync_all_files(user_id=PLAYER_ID)

    for item in files:
        details = synced_files.get(item["name"])
        if details and details.get("uploaded_to_google_sheet"):
            item["sheet_key"] = None
            ready_count += 1
        else:
            item["sheet_key"] = None
            if details:
                set_status(details.get("upload_message", f"Could not sync {item['name']}."))
            else:
                set_status(f"Could not sync {item['name']}.")

    if ready_count == len(files):
        set_status("Files were created, encrypted, and synced to Google Sheets.")
    elif ready_count:
        set_status(f"{ready_count}/{len(files)} files were synced. Missing keys will retry on purchase.")
    else:
        set_status("Could not sync files to Google Sheets. Game still runs, but key buying is offline.")


def on_click():
    global score
    score += click_power


def on_upgrade():
    global score, click_power, upgrade_cost
    if score >= upgrade_cost:
        score -= upgrade_cost
        click_power += 1
        upgrade_cost = int(upgrade_cost * 1.5)
        set_status(f"Upgrade bought. Click power is now {click_power}.")
    else:
        set_status(f"Need {upgrade_cost} points to upgrade.")


def on_item_purchase(item):
    global score

    if score < item["cost"]:
        set_status(f"Need {item['cost']} points to buy {item['name']}.")
        return

    result, key, message = fetch_key(item["name"], user_id=PLAYER_ID)
    if result != "success":
        details = sync_file(item["name"], user_id=PLAYER_ID, force_upload=True)
        if not details.get("uploaded_to_google_sheet"):
            set_status(details.get("upload_message", f"Could not sync {item['name']}."))
            return

        result, key, message = fetch_key(item["name"], user_id=PLAYER_ID)

    if result != "success" or not key:
        set_status(message)
        return

    score -= item["cost"]
    item["sheet_key"] = key
    owned_keys.append({"name": item["name"], "key": key, "decrypted_text": None})
    files.remove(item)
    set_status(f"Bought key for {item['name']}.")
    print(f"{item['name']} key: {key}")


def on_decrypt_purchase(entry):
    global opened_file_name, opened_file_text

    try:
        decrypted_text = decrypt_file(entry["name"], entry["key"])
    except Exception as exc:
        set_status(f"Could not decrypt {entry['name']}: {exc}")
        return

    entry["decrypted_text"] = decrypted_text
    opened_file_name = entry["name"]
    opened_file_text = decrypted_text
    set_status(f"Decrypted {entry['name']}.")


def check_buttons(pos):
    if click_btn.collidepoint(pos):
        on_click()
    elif upgrade_btn.collidepoint(pos):
        on_upgrade()
    else:
        for i, btn in enumerate(decrypt_btns):
            if btn.collidepoint(pos):
                on_decrypt_purchase(owned_keys[i])
                return

        for i, btn in enumerate(item_btns):
            if btn.collidepoint(pos):
                on_item_purchase(files[i])
                break


def draw_owned_keys(start_y, margin, btn_w):
    global decrypt_btns

    title = small_font.render("Owned Keys", False, "White")
    vp.blit(title, (margin, start_y))
    current_y = start_y + title.get_height() + 8
    decrypt_btns = []

    if not owned_keys:
        empty = small_font.render("None yet", False, "Grey")
        vp.blit(empty, (margin, current_y))
        return

    for entry in owned_keys:
        name_text = small_font.render(entry["name"], False, "White")
        vp.blit(name_text, (margin, current_y))
        current_y += name_text.get_height() + 2

        key_lines = wrap_text(f"Key: {entry['key']}", btn_w)
        for line in key_lines:
            key_text = small_font.render(line, False, "Grey")
            vp.blit(key_text, (margin, current_y))
            current_y += key_text.get_height() + 2

        btn_w_small = min(140, btn_w)
        btn_h = 28
        btn_x = margin
        btn_y = current_y + 6
        btn = pygame.Rect(btn_x, btn_y, btn_w_small, btn_h)
        decrypt_btns.append(btn)
        pygame.draw.rect(vp, "Grey", btn, width=1, border_radius=6)
        btn_text = small_font.render("Decrypt File", False, "White")
        vp.blit(btn_text, (btn.x + 10, btn.y + (btn_h - btn_text.get_height()) // 2))

        current_y = btn_y + btn_h + 12


def update_menu():
    global upgrade_btn, item_btns

    panel = pygame.Surface((MENU_W, VP_H))
    panel.fill("Black")
    vp.blit(panel, (0, 0))

    margin = 10
    btn_h = 50
    btn_w = MENU_W - margin * 2

    player_text = small_font.render(f"Player: {PLAYER_ID}", False, "White")
    vp.blit(player_text, (margin, margin))

    upgrade_y = margin + player_text.get_height() + 12
    upgrade_btn = pygame.Rect(margin, upgrade_y, btn_w, btn_h)
    pygame.draw.rect(vp, "Grey", upgrade_btn, width=1, border_radius=6)
    label = small_font.render(f"Upgrade | {upgrade_cost}", False, "White")
    vp.blit(label, (upgrade_btn.x + 8, upgrade_btn.y + (btn_h - label.get_height()) // 2))

    item_btns = []
    for i, item in enumerate(files):
        iy = upgrade_y + (btn_h + margin) * (i + 1)
        btn = pygame.Rect(margin, iy, btn_w, btn_h)
        item_btns.append(btn)
        pygame.draw.rect(vp, "Grey", btn, width=1, border_radius=6)
        txt = small_font.render(f"{item['name']} | {item['cost']}", False, "White")
        vp.blit(txt, (btn.x + 8, btn.y + (btn_h - txt.get_height()) // 2))

    owned_y = upgrade_y + (btn_h + margin) * (len(files) + 1) + 12
    draw_owned_keys(owned_y, margin, btn_w)

    status_lines = [
        "Status:",
        status_message,
    ]
    status_y = VP_H - 60
    for line in status_lines:
        status_text = small_font.render(line, False, "White")
        vp.blit(status_text, (margin, status_y))
        status_y += status_text.get_height() + 4


def update_score():
    score_surf = font.render(str(score), False, "White")
    click_surf = small_font.render(f"Points per click: {click_power}", False, "White")
    game_w = VP_W - MENU_W
    tx = MENU_W + (game_w - score_surf.get_width()) / 2
    ty = (VP_H - score_surf.get_height()) / 8
    vp.blit(score_surf, (tx, ty))
    vp.blit(click_surf, (MENU_W + (game_w - click_surf.get_width()) / 2, ty + 60))


def wrap_text(text, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current_line = words[0]

    for word in words[1:]:
        candidate = f"{current_line} {word}"
        if small_font.size(candidate)[0] <= max_width:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def draw_opened_file():
    game_x = MENU_W + 20
    game_y = 4 * VP_H / 5
    game_w = VP_W - MENU_W - 40
    panel_h = 110
    panel = pygame.Rect(game_x, game_y, game_w, panel_h)

    pygame.draw.rect(vp, (35, 35, 35), panel, border_radius=8)
    pygame.draw.rect(vp, "Grey", panel, width=1, border_radius=8)

    title = small_font.render("Decrypted File", False, "White")
    vp.blit(title, (panel.x + 12, panel.y + 10))

    subtitle_text = opened_file_name if opened_file_name else "No file opened"
    subtitle = small_font.render(subtitle_text, False, "Grey")
    vp.blit(subtitle, (panel.x + 12, panel.y + 32))

    text_y = panel.y + 58
    for line in wrap_text(opened_file_text, panel.width - 24):
        rendered = small_font.render(line, False, "White")
        vp.blit(rendered, (panel.x + 12, text_y))
        text_y += rendered.get_height() + 4
        if text_y > panel.bottom - 18:
            break


def update_img():
    if IMAGE_PATH.exists():
        img = pygame.image.load(str(IMAGE_PATH)).convert_alpha()
    else:
        img = pygame.Surface((157, 200), pygame.SRCALPHA)
        pygame.draw.ellipse(img, (220, 220, 220), img.get_rect())
        pygame.draw.ellipse(img, (120, 120, 120), img.get_rect(), width=4)

    img_w, img_h = img.get_size()
    game_w = VP_W - MENU_W
    ix = MENU_W + (game_w - img_w) / 2
    iy = 3 * (VP_H - img_h) / 5
    vp.blit(img, (ix, iy))
    return pygame.Rect(ix, iy, img_w, img_h)


def update():
    vp.fill("Black")
    update_menu()
    update_score()
    click_area = update_img()
    draw_opened_file()
    return click_area


initialize_sheet_keys()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            check_buttons(event.pos)

    click_btn = update()
    pygame.display.update()
    clock.tick(60)
