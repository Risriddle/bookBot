import os
import fitz  # PyMuPDF
from pyrogram import Client, filters
from dotenv import load_dotenv
from tempfile import TemporaryDirectory

load_dotenv() 


BOT_TOKEN = os.getenv("BOT_TOKEN")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

print("bot is running============")
bot = Client("pdf_highlighter_bot", api_id=api_id, api_hash=api_hash, bot_token=BOT_TOKEN)

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

def generate_highlight_cards(pdf_path, output_path):
    with open(output_path, "w", encoding="utf-8") as f_out:
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
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
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
    return output_path

# Handler for the /start command
@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a PDF file, and I'll extract the highlighted text for you.")

# Handler for PDF file messages
@bot.on_message(filters.document)
def handle_pdf(client, message):
    if message.document.mime_type == "application/pdf":
        file_id = message.document.file_id
        file_name = message.document.file_name

        message.reply_text("Downloading your PDF file...")
        
        with TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, file_name)
            bot.download_media(file_id, file_name=pdf_path)

            message.reply_text("Extracting highlights from your PDF...")
            output_file = os.path.join(temp_dir, f"{os.path.splitext(file_name)[0]}_highlights.html")
            generate_highlight_cards(pdf_path, output_file)

            with open(output_file, "rb") as file:
                bot.send_document(message.chat.id, file)
        
        message.reply_text("Highlight extraction completed.")
    else:
        message.reply_text("Please send a PDF file.")

def main():
    bot.run()

if __name__ == '__main__':
    main()
