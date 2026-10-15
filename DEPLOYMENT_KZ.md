# VERIFAI-ды GitHub және Streamlit Cloud-қа жариялау

## 1. GitHub

1. GitHub-та **New repository** басыңыз.
2. Атауы: `verifai-ai-image-detector`.
3. **Public** таңдаңыз.
4. Осы папкадағы файлдардың бәрін repository root-қа жүктеңіз.
5. `Commit changes` басыңыз.

> `models/` ішіне үлкен модель файлын салудың қажеті жоқ. Қолданба нақты pretrained ONNX моделін Hugging Face-тан **бір рет** автоматты жүктейді, SHA-256 арқылы тексереді және сервер cache-ында сақтайды. Бұл training емес.

## 2. Streamlit Community Cloud

1. `https://share.streamlit.io` сайтына GitHub арқылы кіріңіз.
2. **Create app** → **Yup, I have an app**.
3. Repository: сіздің `verifai-ai-image-detector` repository-іңіз.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Python 3.11 немесе 3.12 таңдаңыз.
7. **Deploy** басыңыз.

Алғашқы суретті талдағанда ~44 MB pretrained модель жүктеледі. Кейін ол cache-тан алынады.

## 3. Нәтиже

Сізге мына форматта ашық сілтеме беріледі:

`https://YOUR-APP-NAME.streamlit.app`

## 4. Егер бірінші рет модель ұзақ жүктелсе

Бұл қалыпты. `Community Forensics frontier detector` ONNX файлы шамамен 43.8 MB. Егер Hugging Face уақытша қолжетімсіз болса, қолданба жалған нәтиже көрсетпейді — нақты қате хабарын береді.

## 5. Жергілікті іске қосу (Windows)

`run_windows.bat` файлын екі рет басыңыз немесе:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 6. GitHub Actions

Repository-ге push жасағаннан кейін `.github/workflows/ci.yml` автоматты түрде:

- Python кодын тексереді;
- unit tests жүргізеді;
- pretrained модельді жүктеп SHA-256 тексереді;
- ONNX inference smoke-test жүргізеді.

CI жасыл болса, repository deployment-қа техникалық тұрғыда дайын.
