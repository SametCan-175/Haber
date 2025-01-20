import feedparser
from tkinter import *
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webview
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


# Yapay Zeka Modelleri
model_name = "sshleifer/distilbart-cnn-12-6"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# Fonksiyonlar
def default_color_button():
    for btn in buttons:
        btn.configure(bg="lightblue")

def clear_frame():
    for widget in fr_haberler.winfo_children():
        widget.destroy()

def open_url(event):
    url = event.widget.cget("text")
    webview.create_window("Haber Bağlantısı", url)
    webview.start()

def summarize_content(content):
    try:
        summary = summarizer(content, max_length=250, min_length=25, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Özetleme yapılamadı: {e}"

def add_haberler(urls):
    for url in urls:
        try:
            haberler = feedparser.parse(url)
            for i, haber in enumerate(haberler.entries):
                if i >= 2:  # Her siteden maksimum 2 haber
                    break

                # Görsel İşleme
                img_url = None
                if 'media_content' in haber and haber.media_content:
                    img_url = haber.media_content[0]['url']
                elif 'links' in haber and haber.links:
                    for link in haber.links:
                        if 'image' in link.type:
                            img_url = link.href
                            break

                if img_url:
                    try:
                        response = requests.get(img_url)
                        img_data = response.content
                        img = Image.open(BytesIO(img_data))
                        img.thumbnail((100, 100))
                        photo = ImageTk.PhotoImage(img)
                        lbl_image = Label(fr_haberler, image=photo)
                        lbl_image.image = photo
                        lbl_image.pack(side=TOP, fill="x")
                    except Exception as e:
                        print(f"Görsel yüklenemedi: {e}")

                # Başlık ve Özet
                summary = summarize_content(haber.title + " " + getattr(haber, 'summary', ""))
                Label(fr_haberler, text=haber.title, anchor='w', font=('Helvetica', 14)).pack(side=TOP, fill="x")
                Label(fr_haberler, text=f"Özet: {summary}", anchor='w', font=('Helvetica', 12), fg="darkgreen").pack(side=TOP, fill="x")

                lbl_link = Label(fr_haberler, text=haber.link, anchor='w', font=('Helvetica', 12), fg="red", cursor="hand2")
                lbl_link.pack(side=TOP, fill="x")
                lbl_link.bind("<Button-1>", open_url)
                Label(fr_haberler, text="-", anchor='c', bg="turquoise").pack(side=TOP, fill="x")

        except Exception as e:
            print(f"Hata: {e}")

def category_command(category, urls, btn):
    clear_frame()
    default_color_button()
    btn.configure(bg="green")
    add_haberler(urls)

# RSS URL'ler
rss_categories = {
    "Son Dakika": [
        "http://www.milliyet.com.tr/rss/rssNew/SonDakikaRss.xml",
        "http://www.ensonhaber.com/rss/ensonhaber.xml",
        "https://www.cnnturk.com/feed/rss/all/news",
        "https://www.sozcu.com.tr/rss/son-dakika.xml"
    ],
    "Dünya": [
        "http://www.milliyet.com.tr/rss/rssNew/dunyaRss.xml",
        "http://www.ensonhaber.com/rss/dunya.xml",
        "https://www.cnnturk.com/feed/rss/dunya/news",
        "https://www.sozcu.com.tr/feeds-rss-category-dunya"
    ],
    "Ekonomi": [
        "http://www.milliyet.com.tr/rss/rssNew/ekonomiRss.xml",
        "http://www.ensonhaber.com/rss/ekonomi.xml",
        "https://www.cnnturk.com/feed/rss/ekonomi/news",
        "https://www.sozcu.com.tr/feeds-rss-category-ekonomi"
    ],
    "Sağlık": [
        "http://www.milliyet.com.tr/rss/rssNew/saglikRss.xml",
        "http://www.ensonhaber.com/rss/saglik.xml",
        "https://www.cnnturk.com/feed/rss/saglik/news",
        "https://www.sozcu.com.tr/feeds-rss-category-saglik"
    ],
    "Spor": [
        "https://www.sabah.com.tr/rss/spor.xml",
        "https://www.ensonhaber.com/rss/kralspor.xml",
        "https://www.cnnturk.com/feed/rss/spor/news",
        "https://www.sozcu.com.tr/feeds-rss-category-spor"
    ],
}

# Tkinter Pencere Ayarları
if __name__ == "__main__":
    window = Tk()
    window.title("Haber Bot Programı")
    window.geometry("1000x600")
    window.state("zoomed")

    fr_haberler = Frame(window, height=600)
    fr_buttons = Frame(window, relief=RAISED, bg="blue", bd=2)

    # Dinamik Buton Oluşturma
    buttons = []
    for i, (category, urls) in enumerate(rss_categories.items()):
        btn = Button(fr_buttons, text=category, font=('Helvetica', 14), bg="lightblue",
                     command=lambda c=category, u=urls, b=i: category_command(c, u, buttons[b]))
        btn.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
        buttons.append(btn)

    fr_buttons.grid(row=0, column=0, sticky="ns")
    fr_haberler.grid(row=0, column=1, sticky="nsew")
    window.mainloop()