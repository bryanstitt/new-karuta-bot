'''

This script is used to analyze the image of a Discord message and extract the best position for a response.

Requires pytesseract and PIL (Pillow) libraries.

'''



import pytesseract
import re

from PIL import Image, ImageOps



def get_best_position() -> None:
    try:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        im = ImageOps.grayscale(Image.open('discord_image.png'))
        w, h = im.size
        im = ImageOps.invert(im)
        l_count, l_ed = get_ed_and_count(im, 157, 370, w - 882, h - 35)
        ml_count, ml_ed = get_ed_and_count(im, 430, 370, w - 617, h - 35)
        mr_count, mr_ed = get_ed_and_count(im, 700, 370, w - 338, h - 35)
        r_count, r_ed = get_ed_and_count(im, 980, 370, w - 63, h - 35)
        
        eds = [l_ed, ml_ed, mr_ed, r_ed]
        counts = [l_count, ml_count, mr_count, r_count]
        print(eds, counts)
        for i, count in enumerate(counts):
            if count == 1:
                continue
            if count < 100:
                return i, 4

        if max(eds) == 1:
            return counts.index(min(counts)), max(eds)

        return eds.index(max(eds)), max(eds)
    except:
        return 0, 0



def get_ed_and_count(im, left, top, right, bottom) -> None:
    try:
        new_im = im.crop((left, top, right, bottom))
        # new_im.show()
        text = pytesseract.image_to_string(new_im)
        # print(text)
        if text == "":
            for i in range(1, 10):
                new_im = im.crop((left+i, top, right-i, bottom))
                text = pytesseract.image_to_string(new_im)
                if text != "":
                    break
        try:
            match = re.search(r'(\d+)\D*-\D*(\d+)', text)
            if match:
                count = match.group(1)
                ed = match.group(2)[0]  # Only take the first digit
        except:
            return 1, 1
        
        count = re.findall(r'\d+', count)
        count = int(count[0])
        ed = ed.strip()

        if(ed[0].isdigit()):
            ed = int(ed[0])
        else:
            ed = 1
        
        return count, ed
    except:
        return 1, 1



def download_image_from_message(message_element, log) -> None:
    link = message_element.find_element(By.TAG_NAME, "a")
    href = link.get_attribute("href")
    log(f"Downloading image from: {href}")
    r = requests.get(href)
    with open("discord_image.png", "wb") as f:
        f.write(r.content)
    log("Image downloaded as discord_image.png")