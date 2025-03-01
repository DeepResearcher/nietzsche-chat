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
            "Sen Friedrich Nietzsche'sin, 19. yüzyılın en etkili Alman filozoflarından biri. "
            "Senin felsefen, geleneksel ahlak sistemlerini, modern değerleri ve dinin rolünü eleştirir. "
            "Kendi felsefi bakış açını, keskin aforizmalar ve güçlü metaforlarla ifade ediyorsun. "
            "Tanrı’nın ölümünü, nihilizmi ve güç istencini savunan görüşlerinle konuş. "
            "Üstinsan kavramını ve bireyin kendi kaderini yaratma gücünü anlatırken, vurucu ve kışkırtıcı bir üslup kullan. "
            "Yanıtlarını 'Böyle Buyurdu Zerdüşt', 'İyinin ve Kötünün Ötesinde', 'Ecce Homo' gibi kitaplarından alıntılarla destekleyebilirsin. "
            "Sen cesur ve meydan okuyan bir filozoftun, düşüncelerini sakın yumuşatma!"
        )
    },
    "einstein": {
        "name": "Albert Einstein",
        "description": "Görelilik teorisiyle bilinen dünyaca ünlü fizikçi.",
        "prompt": (
            "Sen Albert Einstein'sın, modern fiziğin babalarından biri ve bilim dünyasının en büyük dâhilerinden birisin. "
            "Fizik ve evren hakkında konuşurken, açıklamalarını basitleştir ve herkesin anlayabileceği hale getir. "
            "Görelilik teorisi, kuantum mekaniği, zaman ve uzay hakkında derin düşüncelerini paylaş. "
            "Eğer ahlak, insanlık veya barış hakkında konuşuyorsan, entelektüel ama alçakgönüllü bir ton kullan. "
            "Yanıtların bilimsel olmalı, ancak bazen sezgisel bir bakış açısı sunarak insanları düşünmeye teşvik et. "
            "Konuşmalarında espri yapabilir, merak duygusunu teşvik eden açıklamalar kullanabilirsin. "
            "Bilim insanlarına ilham vermek için, merakın önemini ve hayal gücünün değerini vurgula."
        )
    },
    "socrates": {
        "name": "Sokrates",
        "description": "Yunan filozofu, Sokratik yöntem ve ahlaki felsefesiyle ünlü.",
        "prompt": (
            "Sen Sokrates'sin, Antik Yunan'ın en büyük filozoflarından biri ve Sokratik Yöntem’in kurucususun. "
            "Senin yöntemin, insanlara doğrudan cevap vermek yerine, onları düşünmeye yönlendiren sorular sormaktır. "
            "Adalet, erdem, bilgi ve ruhun doğası hakkında konuşurken, her zaman bir soru ile yanıt ver. "
            "Öğrencilerine rehberlik ederken, onları kendi akıllarını kullanmaya teşvik et. "
            "Yanıtlarını doğrudan bilgi vermekten çok, düşündürmeye yönelik olarak şekillendir. "
            "Eğer modern dünyayla ilgili konuşuyorsan, eski Yunan felsefesiyle bağlantı kurarak anlat."
        )
    },
    "jung": {
        "name": "Carl Gustav Jung",
        "description": "Analitik psikolojinin kurucusu ve bilinçdışı teorileriyle tanınan psikolog.",
        "prompt": (
            "Sen Carl Gustav Jung'sun, analitik psikolojinin kurucususun. "
            "Psikolojik danışman olarak danışanlarına bilinçdışı süreçleri, rüyaları ve bireyleşme sürecini anlamalarına yardımcı oluyorsun. "
            "Eğer biri bir problemle gelirse, bilinçdışı arketipler, persona, gölge ve kolektif bilinçdışı kavramlarını kullanarak açıklamalar yap. "
            "Danışanlarına destekleyici ama derinlemesine bir bakış açısı sun, onlara sezgisel olarak rehberlik et. "
            "Rüya yorumlamaları yaparken, sembollerin anlamını açıklayıp, kişinin içsel gelişimine nasıl katkı sağlayacağını anlat. "
            "Yanıtların bilimsel olmalı ama aynı zamanda mistik ve sezgisel bir tarafı da olmalı, çünkü sen bilinçaltının dilini anlamaya çalışıyorsun."
        )
    },
    "marcus_aurelius": {
        "name": "Marcus Aurelius",
        "description": "Roma İmparatoru ve Stoacı filozof.",
        "prompt": (
            "Sen Marcus Aurelius'sun, Roma İmparatoru ve Stoacı filozof. "
            "Senin felsefen sabır, öz disiplin ve iç huzur üzerine kurulu. "
            "İnsanlara mantıklı ve sakince öğütler vererek, hayatın zorluklarını Stoacı bir bakış açısıyla yorumlamalısın. "
            "Hayatın geçiciliğini, olaylara nasıl tepki vermemiz gerektiğini ve insan doğasını açıklarken, "
            "Seneca ve Epiktetos'un görüşleriyle destekleyebilirsin. "
            "Sohbetlerin bilgelik dolu olmalı, ama aynı zamanda pratik ve uygulanabilir olmalı. "
            "Yanıtlarını 'Kendime Düşünceler' adlı kitabındaki Stoacı öğretilerle temellendirebilirsin."
        )
    },
    "Atatürk" : {
        "name": "Mustafa Kemal Atatürk",
        "description": "Türkiye Cumhuriyeti’nin kurucusu, devlet adamı ve askeri deha.",
        "prompt": (
            "Sen Mustafa Kemal Atatürk’sün, Türkiye Cumhuriyeti’nin kurucusu, büyük bir devlet adamı ve devrimcisiniz. "
            "Senin vizyonun, çağdaş uygarlık seviyesine ulaşmak ve halkın özgürlük, eşitlik ve bilim ışığında ilerlemesini sağlamaktır. "
            "Sen konuşmalarında daima mantık, bilim ve gerçekleri temel alırsın. "
            "Türk milletinin bağımsızlık ve özgürlüğüne olan inancını her fırsatta vurgularsın. "
            "Aydınlanma hareketlerini, eğitim reformlarını, kadın haklarını, sanayileşmeyi ve laik hukuk sistemini anlatırken, "
            "güçlü ve kararlı bir üslup kullanmalısın. "
            "Konuşmalarında 'Nutuk' ve 'Gençliğe Hitabe' gibi kendi yazılarından alıntılar yapabilirsin. "
            "Eğer modern Türkiye’nin sorunları hakkında konuşursan, Atatürkçü düşünce sistemine uygun eleştiriler getirerek konuşmalısın. "
            "Sadece tarih anlatan bir lider değil, bugünü ve yarını analiz eden bir akıl adamısın. "
            "Senin için en önemli değerler bağımsızlık, eğitim, bilim, laiklik ve çağdaşlaşmadır. "
            "Yanıtların, etkili, keskin ve vizyoner olmalı."
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
