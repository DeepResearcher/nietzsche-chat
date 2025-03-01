from flask import Flask, render_template, request
import openai
from dotenv import load_dotenv



app = Flask(__name__)

# Burada API anahtarınızı ayarlayın
import os

# .env dosyasını yükle
load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    user_input = ""

    if request.method == "POST":
        user_input = request.form.get("user_input")

        messages = [
            {
                "role": "system",
                "content": (
                    "Sen Friedrich Nietzsche'sin, ünlü Alman filozof. "
                    "Aforizmaların, keskin düşüncelerin ve güçlü metaforlarınla konuşuyorsun. "
                    "Dilini 1800'lerin edebi tarzına uygun kullanıyorsun, sık sık kendi eserlerinden alıntılar yapıyorsun. "
                    "Kendi kitaplarından (Böyle Buyurdu Zerdüşt, İyinin ve Kötünün Ötesinde, Ecce Homo) referans verebilirsin. "
                    "Eğer günümüz konularına yanıt verirsen, kendi felsefi bakış açınla modern dünyayı eleştirerek konuş."
                )
            },
            {"role": "user", "content": user_input}
        ]

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,  # Daha yaratıcı yanıtlar için sıcaklığı artırıyoruz
                max_tokens=300
            )
            response_text = completion["choices"][0]["message"]["content"].replace("\n", "<br>")  # Yeni satırları HTML'de düzgün göstermek için
        except Exception as e:
            response_text = f"Hata oluştu: {e}"

    return render_template("index.html", response_text=response_text, user_input=user_input)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render varsayılan olarak 5000 veya başka bir port atayabilir
    app.run(host="0.0.0.0", port=port, debug=False)