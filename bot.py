import os
import fitz  # PyMuPDF
import telebot
from flask import Flask
from dotenv import load_dotenv

load_dotenv() 
 
# BOT_TOKEN = '6811169224:AAEknM9A2_EusaTaRMetwszkabB4fmxuZjQ'
BOT_TOKEN=os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

pdf_directory = "/home/risriddle/Downloads/Books"
output_directory = "/home/risriddle/Downloads/Jists"

def extract_highlighted_text(pdf_path):
    doc = fitz.open(pdf_path)
    highlighted_text = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        annots = page.annots()

        for annot in annots:
            if annot.type[0] == 8:  # Check if it's a highlight annotation
                rect = annot.rect  # Annotation rectangle
                highlights = page.get_text("text", clip=rect)  # Get text within the annotation's rectangle
                highlighted_text.append(highlights.strip())
    
    return highlighted_text

def generate_highlight_cards(pdf_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)
    
    filename = os.path.basename(pdf_path)
    pdf_name = os.path.splitext(filename)[0]
    output_file = os.path.join(output_directory, f"{pdf_name}_highlights.html")

    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("""
        <html>
        <head>
            <title>Highlighted Text</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; background-color: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                .card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px; box-shadow: 0 0 5px rgba(0,0,0,0.1); background-color: #f9f9f9; }
                .card h2 { margin-top: 0; }
                .share-buttons { display: flex; justify-content: flex-end; margin-top: 10px; }
                .share-button { text-decoration: none; padding: 10px 15px; margin-left: 10px; border-radius: 5px; font-size: 14px; }
                .share-whatsapp { background-color: #25D366; color: white; }
                 </style>
        </head>
        <body>
            <div class="container">
        """)

        f_out.write(f"<h1>Highlights from {pdf_name}</h1>\n")

        # Extract highlighted text
        highlights = extract_highlighted_text(pdf_path)

        # Write highlight cards
        for idx, highlight in enumerate(highlights, start=1):
            encoded_highlight = highlight.replace("\n", "%0A").replace(" ", "%20")
            f_out.write(f"""
            <div class="card">
                <h2>Highlight {idx}</h2>
                <p>{highlight}</p>
                <div class="share-buttons">
                    <a href="https://api.whatsapp.com/send?text={encoded_highlight}" target="_blank" class="share-button share-whatsapp">Share on WhatsApp</a>
                    
                </div>
            </div>
            """)

        f_out.write("""
            </div>
        </body>
        </html>
        """)

    return output_file

@bot.message_handler(commands=['start'])
def start(message):
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Please provide the PDF filename. Usage: /start <filename>")
        return

    pdf_filename = command[1]
    pdf_path = os.path.join(pdf_directory, pdf_filename)

    if not os.path.exists(pdf_path):
        bot.reply_to(message, f"File {pdf_filename} not found in the PDF directory.")
        return

    output_file = generate_highlight_cards(pdf_path, output_directory)

    with open(output_file, "rb") as file:
        bot.send_document(message.chat.id, file)

    bot.reply_to(message, f"Highlight extraction completed for {pdf_filename}. Check the output directory for the result.")

# def main():
#     bot.polling()

# if __name__ == '__main__':
#     main()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def main():
    # Start polling in a separate thread
    from threading import Thread
    Thread(target=bot.polling).start()

    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
