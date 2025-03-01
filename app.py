# from flask import Flask, render_template, request
# import openai
# from dotenv import load_dotenv



# app = Flask(__name__)

# # Burada API anahtarınızı ayarlayın
# import os

# # .env dosyasını yükle
# load_dotenv()


# openai.api_key = os.getenv("OPENAI_API_KEY")

# @app.route("/", methods=["GET", "POST"])
# def index():
#     response_text = ""
#     user_input = ""

#     if request.method == "POST":
#         user_input = request.form.get("user_input")

#         messages = [
#             {
#                 "role": "system",
#                 "content": (
#                     "Sen Friedrich Nietzsche'sin, ünlü Alman filozof. "
#                     "Aforizmaların, keskin düşüncelerin ve güçlü metaforlarınla konuşuyorsun. "
#                     "Dilini 1800'lerin edebi tarzına uygun kullanıyorsun, sık sık kendi eserlerinden alıntılar yapıyorsun. "
#                     "Kendi kitaplarından (Böyle Buyurdu Zerdüşt, İyinin ve Kötünün Ötesinde, Ecce Homo) referans verebilirsin. "
#                     "Eğer günümüz konularına yanıt verirsen, kendi felsefi bakış açınla modern dünyayı eleştirerek konuş."
#                 )
#             },
#             {"role": "user", "content": user_input}
#         ]

#         try:
#             completion = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=messages,
#                 temperature=0.8,  # Daha yaratıcı yanıtlar için sıcaklığı artırıyoruz
#                 max_tokens=300
#             )
#             response_text = completion["choices"][0]["message"]["content"].replace("\n", "<br>")  # Yeni satırları HTML'de düzgün göstermek için
#         except Exception as e:
#             response_text = f"Hata oluştu: {e}"

#     return render_template("index.html", response_text=response_text, user_input=user_input)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))  # Render varsayılan olarak 5000 veya başka bir port atayabilir
#     app.run(host="0.0.0.0", port=port, debug=False)


from flask import Flask, render_template, request, session
import openai
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Flask session için gerekli

# OpenAI API anahtarını al
openai.api_key = os.getenv("OPENAI_API_KEY")

# Kullanılabilir karakterler
characters = {
    "nietzsche": {
        "name": "Friedrich Nietzsche",
        "description": "Ünlü Alman filozof, güç istenci ve üst insan teorisiyle bilinir.",
        "prompt": (
            "Sen Friedrich Nietzsche'sin, ünlü Alman filozof. "
            "Aforizmaların, keskin düşüncelerin ve güçlü metaforlarınla konuşuyorsun. "
            "Dilini 1800'lerin edebi tarzına uygun kullanıyorsun, sık sık kendi eserlerinden alıntılar yapıyorsun. "
            "Kendi kitaplarından (Böyle Buyurdu Zerdüşt, İyinin ve Kötünün Ötesinde, Ecce Homo) referans verebilirsin. "
            "Eğer günümüz konularına yanıt verirsen, kendi felsefi bakış açınla modern dünyayı eleştirerek konuş."
        )
    },
    "einstein": {
        "name": "Albert Einstein",
        "description": "Görelilik teorisiyle bilinen dünyaca ünlü fizikçi.",
        "prompt": (
            "Sen Albert Einstein'sın, görelilik teorisinin ve modern fiziğin babası. "
            "Sade ve anlaşılır bir dil kullanarak bilimsel kavramları açıkla. "
            "Mantık ve bilim çerçevesinde cevaplar ver, ama aynı zamanda insanlık, ahlak ve barış hakkında düşüncelerini de paylaş."
        )
    },
    "socrates": {
        "name": "Sokrates",
        "description": "Yunan filozofu, Sokratik yöntem ve ahlaki felsefesiyle ünlü.",
        "prompt": (
            "Sen Sokrates'sin, Antik Yunan'ın en büyük filozoflarından biri. "
            "Diyalog yöntemiyle (Sokratik Yöntem) cevaplar ver. "
            "Sorular sorarak insanları düşünmeye teşvik et. "
            "Eğer modern konular hakkında konuşuyorsan, eski Yunan felsefesiyle bağlantı kurarak anlat."
        )
    }
}

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", characters=characters)

@app.route("/chat/<character_id>", methods=["GET", "POST"])
def chat(character_id):
    if character_id not in characters:
        return "Böyle bir karakter bulunamadı!", 404  # Eğer karakter listesinde yoksa hata ver
    
    character = characters[character_id]  # Seçilen karakteri al

    # Sohbet geçmişini session içinde tutalım
    if "chat_history" not in session or session.get("active_character") != character_id:
        session["chat_history"] = []
        session["active_character"] = character_id  # Yeni karakter seçildiğinde geçmişi sıfırla

    response_text = ""
    user_input = ""

    if request.method == "POST":
        user_input = request.form.get("user_input")

        messages = [{"role": "system", "content": character["prompt"]}]
        messages += session["chat_history"]  # Geçmiş konuşmaları ekleyelim
        messages.append({"role": "user", "content": user_input})

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )
            response_text = completion["choices"][0]["message"]["content"].replace("\n", "<br>")

            # Yeni mesajları sohbet geçmişine ekleyelim
            session["chat_history"].append({"role": "user", "content": user_input})
            session["chat_history"].append({"role": "assistant", "content": response_text})
            session.modified = True  # Session'ı güncelle

        except Exception as e:
            response_text = f"Hata oluştu: {e}"

    return render_template("chat.html", character=character, response_text=response_text, user_input=user_input, chat_history=session["chat_history"], character_id=character_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Flask uygulaması {port} portunda çalışıyor.")
    app.run(host="0.0.0.0", port=port, debug=True)
