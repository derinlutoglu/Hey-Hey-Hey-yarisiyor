import pygame
import sys
import random
import math
import json
import os
import datetime

# PYINSTALLER KAYNAK YOLU 
def resource_path(relative_path):
    """PyInstaller .app içinde veya normal çalışmada kaynak dosya yolunu döndür."""
    try:
        base_path = sys._MEIPASS  # PyInstaller geçici dizini
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

#  BAŞLANGIÇ AYARLARI 
pygame.init()
GENISLIK, YUKSEKLIK =800, 400
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("HEY HEY HEY YARIŞIYOR")
saat = pygame.time.Clock()

# RENK PALETİ 
KOYU_LACIVERT = (10,   8,  30)
KOYU_MOR      = (20,  10,  50)
MOR           = (90,  50, 160)
PARLAK_MOR    = (150, 80, 220)
PEMBE         = (230,  70, 160)
CYAN          = ( 80, 220, 210)
SARI          = (255, 220,  50)
YESIL         = ( 80, 220, 120)
BEYAZ         = (255, 255, 255)
GRI           = (140, 120, 170)
KIRMIZI       = (220,  50,  80)
ZEMIN_KOYU    = ( 30,  15,  60)
ZEMIN_IZGI    = ( 60,  30, 100)

#  SKOR TABLOSU 

_UYGULAMA_DESTEK = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ArkadaşlarMacera")
os.makedirs(_UYGULAMA_DESTEK, exist_ok=True)
SKOR_DOSYASI = os.path.join(_UYGULAMA_DESTEK, "skor_tablosu.json")

def skor_yukle():
    """Dosyadan skor listesini yükle. Yoksa boş liste döndür."""
    try:
        with open(SKOR_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def skor_kaydet(isim, skor_val):
    """Yeni skoru listeye ekle, en yüksek 10'u sakla."""
    kayitlar = skor_yukle()
    tarih    = datetime.datetime.now().strftime("%d.%m.%Y")
    kayitlar.append({"isim": isim, "skor": skor_val, "tarih": tarih})
    kayitlar.sort(key=lambda x: x["skor"], reverse=True)
    kayitlar = kayitlar[:10]                           # sadece top-10
    with open(SKOR_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False, indent=2)
    return kayitlar

#  YILDIZ SİSTEMİ 
def yildiz_olustur(adet=80):
    yildizlar = []
    for _ in range(adet):
        x   = random.randint(0, GENISLIK)
        y   = random.randint(0, 340)
        r   = random.choice([1, 1, 1, 2])
        hiz = random.uniform(0.1, 0.4)
        prl = random.randint(0, 255)
        yildizlar.append([x, y, r, hiz, prl])
    return yildizlar

def yildizlari_ciz(yildizlar, frame):
    for y in yildizlar:
        y[0] -= y[3]
        if y[0] < 0:
            y[0] = GENISLIK
            y[1] = random.randint(0, 340)
        p    = int(160 + 90 * math.sin((frame * 0.05) + y[4]))
        renk = (p, p, min(255, p + 40))
        pygame.draw.circle(ekran, renk, (int(y[0]), int(y[1])), y[2])

#  ZEMİN 
def zemin_ciz(kaydirma=0):
    pygame.draw.rect(ekran, ZEMIN_KOYU, (0, 365, GENISLIK, 35))
    aralik = 40
    for gx in range(0, GENISLIK + aralik, aralik):
        x = (gx - kaydirma % aralik)
        pygame.draw.line(ekran, ZEMIN_IZGI, (x, 365), (x - 15, 400), 1)
    pygame.draw.line(ekran, PARLAK_MOR, (0, 365), (GENISLIK, 365), 2)
    pygame.draw.line(ekran, PEMBE,      (0, 367), (GENISLIK, 367), 1)

#  METİN YARDIMCILARI 
def metin_golgeli(font, yazi, renk, x, y, golge=(0, 0, 0), golge_offset=2):
    ekran.blit(font.render(yazi, True, golge), (x + golge_offset, y + golge_offset))
    ekran.blit(font.render(yazi, True, renk),  (x, y))

def metin_ortali(font, yazi, renk, y, golge=(0, 0, 0)):
    yuzey = font.render(yazi, True, renk)
    x     = (GENISLIK - yuzey.get_width()) // 2
    metin_golgeli(font, yazi, renk, x, y, golge)

#  ENGEL SÖZLÜĞÜ 
engel_sozlugu = {
    "kahve.png"      : "Uykusuzluktan bayıldı!",
    "sarap.png"      : "Eğlenceyi dozunda bırakamadı!",
    "havalimani.png" : "Turgut geldi havalimanına gitmesi lazım!",
    "tk_logo.png"    : "TK Overdose!",
    "kalp.png"       : "Aşk acısından koşamıyor!",
}
UCUCU_ENGELLER = {"tk_logo.png", "kalp.png"}

#  BULUT SINIFI 
class Bulut:
    def __init__(self):
        self.x   = random.randint(800, 1200)
        self.y   = random.randint(30, 130)
        self.hiz = random.uniform(0.3, 1.2)

    def hareket_et(self):
        self.x -= self.hiz
        if self.x < -120:
            self.x = random.randint(800, 1000)
            self.y = random.randint(30, 130)

    def ciz(self):
        renk = (80, 50, 120)
        for ox, oy, r in [(-20, 0, 18), (0, 0, 22), (20, 0, 18), (10, -10, 15), (-10, -10, 15)]:
            pygame.draw.circle(ekran, renk, (int(self.x + ox), int(self.y + oy)), r)

# ARKADAŞ SINIFI 
ZIPLA_GUCU = 15

class Arkadas:
    def __init__(self, isim, resim_dosyasi):
        self.isim         = isim
        self.ziplama_gucu = ZIPLA_GUCU
        self.x, self.y    = 100, 300
        self.hiz_y        = 0
        self.yercekimi    = 0.8
        self.yerde_mi     = True
        self.egiliyor     = False
        try:
            ham = pygame.image.load(resource_path(resim_dosyasi))
            self.resim_normal = pygame.transform.scale(ham, (65, 65))
            self.resim_egik   = pygame.transform.scale(ham, (78, 38))
        except:
            self.resim_normal = pygame.Surface((65, 65), pygame.SRCALPHA)
            self.resim_normal.fill((150, 80, 200))
            self.resim_egik   = pygame.Surface((78, 38), pygame.SRCALPHA)
            self.resim_egik.fill((100, 50, 180))
        self.resim = self.resim_normal

    def zipla(self):
        if self.yerde_mi and not self.egiliyor:
            self.hiz_y    = -self.ziplama_gucu
            self.yerde_mi = False

    def egilme(self):
        if self.yerde_mi:
            self.egiliyor = True
            self.resim    = self.resim_egik

    def kalk(self):
        self.egiliyor = False
        self.resim    = self.resim_normal

    def hareket_et(self):
        if not self.egiliyor:
            self.hiz_y += self.yercekimi
            self.y     += self.hiz_y
        if self.y >= 300:
            self.y        = 300
            self.hiz_y    = 0
            self.yerde_mi = True

    def hitbox(self):
        if self.egiliyor:
            return pygame.Rect(self.x + 5, self.y + 27, 68, 38)
        return pygame.Rect(self.x, self.y, 60, 60)

    def ciz(self, frame=0):
        if self.egiliyor:
            glow_surf = pygame.Surface((100, 16), pygame.SRCALPHA)
            gi        = int(80 + 40 * math.sin(frame * 0.1))
            pygame.draw.ellipse(glow_surf, (80, 200, 255, gi), (0, 0, 100, 16))
            ekran.blit(glow_surf, (self.x - 10, self.y + 49))
            ekran.blit(self.resim, (self.x + 5, self.y + 27))
            f = pygame.font.SysFont("Arial", 16, bold=True)
            metin_golgeli(f, self.isim, CYAN, self.x, self.y + 10, (10, 5, 30), 2)
        else:
            glow_surf = pygame.Surface((90, 20), pygame.SRCALPHA)
            gi        = int(60 + 30 * math.sin(frame * 0.1))
            pygame.draw.ellipse(glow_surf, (180, 80, 255, gi), (0, 0, 90, 20))
            ekran.blit(glow_surf, (self.x - 12, self.y + 58))
            ekran.blit(self.resim, (self.x, self.y))
            f = pygame.font.SysFont("Arial", 16, bold=True)
            metin_golgeli(f, self.isim, CYAN, self.x, self.y - 22, (10, 5, 30), 2)

#  ENGEL SINIFI 
class Engel:
    def __init__(self, resim_adi, ucuyor=False):
        self.resim_adi = resim_adi
        self.mesaj     = engel_sozlugu[resim_adi]
        self.ucuyor    = ucuyor
        try:
            resim      = pygame.image.load(resource_path(resim_adi))
            self.resim = pygame.transform.scale(resim, (32, 32))
        except:
            self.resim = pygame.Surface((32, 32))
            self.resim.fill(KIRMIZI)
        bottom = 310 if ucuyor else 365
        self.rect = self.resim.get_rect(midbottom=(900, bottom))

    def hareket_et(self, hiz):
        self.rect.x -= hiz

    def ciz(self):
        aura_renk = (0, 200, 220, 55) if self.ucuyor else (220, 50, 80, 60)
        aura      = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.rect(aura, aura_renk, (0, 0, 44, 44), border_radius=6)
        ekran.blit(aura,       (self.rect.x - 6, self.rect.y - 6))
        ekran.blit(self.resim,  self.rect)
        if self.ucuyor:
            f  = pygame.font.SysFont("Arial", 13, bold=True)
            ok = f.render("↓ EĞİL", True, CYAN)
            ekran.blit(ok, (self.rect.x + 25 - ok.get_width() // 2, self.rect.y - 18))

# AÇILIŞ EKRANI 
def acilis_ekrani():
    font_buyuk = pygame.font.SysFont("Arial", 52, bold=True)
    font_orta  = pygame.font.SysFont("Arial", 22, bold=True)
    font_kucuk = pygame.font.SysFont("Arial", 16)
    yildizlar  = yildiz_olustur(100)
    bulutlar   = [Bulut() for _ in range(4)]

    yuklenme = 0
    while yuklenme <= 100:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        ekran.fill(KOYU_LACIVERT)
        yildizlari_ciz(yildizlar, yuklenme)
        for b in bulutlar: b.hareket_et(); b.ciz()
        metin_ortali(font_buyuk, "HEY HEY HEY YARIŞIYOR", PEMBE, 80, (80, 0, 100))
        metin_ortali(font_orta,  "~ Büyük Macera ~",   PARLAK_MOR, 145)
        bx, by, bg, bh = 200, 240, 400, 28
        pygame.draw.rect(ekran, MOR, (bx, by, bg, bh), border_radius=6)
        dolu = int(bg * yuklenme / 100)
        if dolu > 0:
            pygame.draw.rect(ekran, PEMBE, (bx, by, dolu, bh), border_radius=6)
            pygame.draw.rect(ekran, BEYAZ, (bx, by, dolu, 6),  border_radius=3)
        pygame.draw.rect(ekran, PARLAK_MOR, (bx, by, bg, bh), 2, border_radius=6)
        zemin_ciz(yuklenme * 3)
        pygame.display.flip()
        saat.tick(60)
        yuklenme += 2

    frame = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
        ekran.fill(KOYU_LACIVERT)
        yildizlari_ciz(yildizlar, frame)
        for b in bulutlar: b.hareket_et(); b.ciz()
        metin_ortali(font_buyuk, "HEY HEY HEY YARIŞIYOR", PEMBE, 75, (80, 0, 100))
        metin_ortali(font_orta,  "~ Büyük Macera ~",   PARLAK_MOR, 140)
        kr        = PEMBE if (frame // 20) % 2 == 0 else PARLAK_MOR
        btn_text  = "▶  BAŞLAMAK İÇİN ENTER"
        btn_surf  = font_orta.render(btn_text, True, kr)
        btn_w     = btn_surf.get_width() + 40
        btn_x     = (GENISLIK - btn_w) // 2
        kutu      = pygame.Rect(btn_x, 200, btn_w, 50)
        pygame.draw.rect(ekran, KOYU_MOR, kutu, border_radius=10)
        pygame.draw.rect(ekran, kr,       kutu, 3, border_radius=10)
        metin_ortali(font_orta, btn_text, kr, 214)
        metin_ortali(font_kucuk, "↑ zıpla   ↓ eğil", GRI, 295)
        zemin_ciz(frame)
        pygame.display.flip()
        saat.tick(60)
        frame += 1

# KARAKTER SEÇİM EKRANI 
def karakter_sec():
    font_baslik = pygame.font.SysFont("Arial", 38, bold=True)
    font_isim   = pygame.font.SysFont("Arial", 17, bold=True)
    font_talim  = pygame.font.SysFont("Arial", 15)
    font_esit   = pygame.font.SysFont("Arial", 13)

    yildizlar = yildiz_olustur(90)
    bulutlar  = [Bulut() for _ in range(3)]

    kadro = [
        Arkadas("Sude",   "sude.png"),
        Arkadas("Melis",  "melis.png"),
        Arkadas("Tonguç", "tonguc.png"),
        Arkadas("Sami",   "sami.png"),
        Arkadas("Derin",  "derin.png"),
    ]

    secim_index = 0
    frame       = 0

    while True:
        ekran.fill(KOYU_LACIVERT)
        yildizlari_ciz(yildizlar, frame)
        for b in bulutlar: b.hareket_et(); b.ciz()

        metin_ortali(font_baslik, "KARAKTERİNİ SEÇ", PEMBE, 20, (80, 0, 100))
        pygame.draw.line(ekran, PARLAK_MOR, (150, 68), (650, 68), 2)

        for i, kar in enumerate(kadro):
            x_pos  = 75 + i * 130
            y_pos  = 110
            secili = (i == secim_index)

            # Kart arka planı
            kart = pygame.Surface((90, 125), pygame.SRCALPHA)
            kart.fill((150, 60, 220, 80) if secili else (50, 20, 80, 60))
            ekran.blit(kart, (x_pos - 12, y_pos - 8))

            # Çerçeve
            if secili:
                pulse = int(2 + 1.5 * math.sin(frame * 0.12))
                pygame.draw.rect(ekran, PEMBE, (x_pos - 13, y_pos - 9, 92, 127), pulse, border_radius=6)
                pygame.draw.rect(ekran, SARI,  (x_pos - 13, y_pos - 9, 92, 127), 1,     border_radius=6)
            else:
                pygame.draw.rect(ekran, MOR, (x_pos - 13, y_pos - 9, 92, 127), 1, border_radius=6)

            ekran.blit(kar.resim, (x_pos, y_pos))

            # İsim
            ir   = SARI if secili else BEYAZ
            is_s = font_isim.render(kar.isim, True, ir)
            ekran.blit(is_s, (x_pos + 32 - is_s.get_width() // 2, y_pos + 72))

        # En yüksek skor
        kayitlar = skor_yukle()
        if kayitlar:
            en_yuksek = kayitlar[0]
            yk_txt = font_esit.render(
                f"🏆  {en_yuksek['isim']}  —  {en_yuksek['skor']:,}",
                True, SARI
            )
            ekran.blit(yk_txt, (GENISLIK // 2 - yk_txt.get_width() // 2, 248))

        metin_ortali(font_talim, "◄  ►  seç      ENTER  başla", GRI, 278)

        zemin_ciz(frame)
        pygame.display.flip()
        saat.tick(60)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    secim_index = (secim_index - 1) % len(kadro)
                elif event.key == pygame.K_RIGHT:
                    secim_index = (secim_index + 1) % len(kadro)
                elif event.key == pygame.K_RETURN:
                    return kadro[secim_index]

# SKOR TABLOSU EKRANI 
def skor_tablosu_ekrani(yeni_skor=None, yeni_isim=None):
    """Top-10 skor tablosunu göster. ESC/ENTER ile çık."""
    font_baslik = pygame.font.SysFont("Arial", 32, bold=True)
    font_satir  = pygame.font.SysFont("Arial", 18, bold=True)
    font_kucuk  = pygame.font.SysFont("Arial", 15)
    yildizlar   = yildiz_olustur(70)
    kayitlar    = skor_yukle()
    frame       = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_t):
                    return

        ekran.fill(KOYU_LACIVERT)
        yildizlari_ciz(yildizlar, frame)

        # Panel
        panel = pygame.Rect(100, 20, 600, 350)
        pygame.draw.rect(ekran, (20, 10, 45),  panel, border_radius=14)
        pygame.draw.rect(ekran, PARLAK_MOR,    panel, 2, border_radius=14)

        metin_ortali(font_baslik, "🏆  SKOR TABLOSU  🏆", SARI, 30, (60, 40, 0))
        pygame.draw.line(ekran, PARLAK_MOR, (130, 72), (670, 72), 1)

        # Başlık satırı
        ekran.blit(font_kucuk.render("#",     True, GRI), (120, 80))
        ekran.blit(font_kucuk.render("İSİM",  True, GRI), (160, 80))
        ekran.blit(font_kucuk.render("PUAN",  True, GRI), (360, 80))
        ekran.blit(font_kucuk.render("TARİH", True, GRI), (490, 80))
        pygame.draw.line(ekran, MOR, (120, 98), (670, 98), 1)

        if not kayitlar:
            metin_ortali(font_satir, "Henüz kayıt yok!", GRI, 180)
        else:
            for i, k in enumerate(kayitlar[:10]):
                y_satir = 108 + i * 25
                # Yeni skoru vurgula
                if yeni_isim and yeni_skor and k["isim"] == yeni_isim and k["skor"] == yeni_skor:
                    vurgu = pygame.Surface((540, 22), pygame.SRCALPHA)
                    vurgu.fill((255, 215, 50, 40))
                    ekran.blit(vurgu, (120, y_satir - 2))
                    satir_renk = SARI
                else:
                    satir_renk = BEYAZ if i < 3 else GRI

                # Madalya rengi: ilk 3'e özel
                madalya = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
                ekran.blit(font_satir.render(madalya,          True, satir_renk), (115, y_satir))
                ekran.blit(font_satir.render(k["isim"],        True, satir_renk), (155, y_satir))
                ekran.blit(font_satir.render(f"{k['skor']:,}", True, satir_renk), (355, y_satir))
                ekran.blit(font_kucuk.render(k["tarih"],       True, GRI),        (490, y_satir + 3))

        # Çıkış ipucu
        ck = CYAN if (frame // 25) % 2 == 0 else GRI
        metin_ortali(font_kucuk, "ESC  geri dön", ck, 345)

        zemin_ciz(frame)
        pygame.display.flip()
        saat.tick(60)
        frame += 1

#  OYUNU SIFIRLA 
HIZ_BASLANGIC = 3.5    # yavaş başla
HIZ_MAKS      = 18.0   # maksimum hız

def oyunu_sifirla(secili_karakter):
    secili_karakter.x, secili_karakter.y = 100, 300
    secili_karakter.hiz_y   = 0
    secili_karakter.yerde_mi = True
    secili_karakter.egiliyor = False
    secili_karakter.resim    = secili_karakter.resim_normal
    return 0, secili_karakter, [], HIZ_BASLANGIC, True, "", 0

#  ANA OYUN 
acilis_ekrani()
secili_karakter = karakter_sec()

skor, oyuncu, engeller, engel_hizi, aktif, final_mesaji, son_engel_zamani = oyunu_sifirla(secili_karakter)

skor_kaydedildi = False
bulutlar        = [Bulut() for _ in range(5)]
yildizlar       = yildiz_olustur(80)
frame_sayaci    = 0
zemin_kaydi     = 0

font_skor  = pygame.font.SysFont("Arial", 20, bold=True)
font_buyuk = pygame.font.SysFont("Arial", 26, bold=True)
font_kucuk = pygame.font.SysFont("Arial", 18)

while True:
    ekran.fill(KOYU_LACIVERT)
    yildizlari_ciz(yildizlar, frame_sayaci)
    for b in bulutlar: b.hareket_et(); b.ciz()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w) and aktif:
                oyuncu.zipla()
            if event.key in (pygame.K_DOWN, pygame.K_s) and aktif:
                oyuncu.egilme()
            if event.key == pygame.K_r and not aktif:
                secili_karakter = karakter_sec()
                skor, oyuncu, engeller, engel_hizi, aktif, final_mesaji, son_engel_zamani = oyunu_sifirla(secili_karakter)
                skor_kaydedildi = False
                frame_sayaci    = 0
                zemin_kaydi     = 0
            if event.key == pygame.K_t and not aktif:
                skor_tablosu_ekrani()
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_DOWN, pygame.K_s) and aktif:
                oyuncu.kalk()

    if aktif:
        skor         += 1
        frame_sayaci += 1
        zemin_kaydi  += engel_hizi

        #  KADEMELİ HIZ ARTIŞI 
        
        hiz_artis    = 0.0008 + (engel_hizi - HIZ_BASLANGIC) * 0.00015
        engel_hizi   = min(HIZ_MAKS, engel_hizi + hiz_artis)

        # Engel oluşturma aralığı: başta geniş, hız arttıkça daralır
        aralik_frame = max(30, int(140 - engel_hizi * 6))
        if frame_sayaci - son_engel_zamani >= aralik_frame:
            if random.randint(1, 100) <= 70:
                resim  = random.choice(list(engel_sozlugu.keys()))
                ucuyor = (resim in UCUCU_ENGELLER) and (random.randint(1, 100) <= 35)
                engeller.append(Engel(resim, ucuyor=ucuyor))
                son_engel_zamani = frame_sayaci

        oyuncu.hareket_et()
        oyuncu.ciz(frame_sayaci)

        for e in engeller[:]:
            e.hareket_et(engel_hizi)
            e.ciz()
            if e.rect.right < 0:
                engeller.remove(e)
            elif oyuncu.hitbox().colliderect(e.rect):
                aktif        = False
                final_mesaji = f"EYVAH! {oyuncu.isim} — {e.mesaj}"

        zemin_ciz(int(zemin_kaydi))

        #  HUD 
        skor_val = skor // 10
        hud_surf = pygame.Surface((165, 65), pygame.SRCALPHA)
        hud_surf.fill((20, 10, 50, 160))
        pygame.draw.rect(hud_surf, PARLAK_MOR, (0, 0, 165, 65), 1, border_radius=6)
        ekran.blit(hud_surf, (628, 10))
        ekran.blit(font_skor.render(f"{skor_val:05d}", True, SARI), (648, 16))

        # Hız çubuğu
        bar_max  = 145
        bar_dolu = int(bar_max * (engel_hizi - HIZ_BASLANGIC) / (HIZ_MAKS - HIZ_BASLANGIC))
        hiz_renk = YESIL if engel_hizi < 10 else (SARI if engel_hizi < 14 else KIRMIZI)
        pygame.draw.rect(ekran, ZEMIN_KOYU, (633, 48, bar_max, 6), border_radius=3)
        pygame.draw.rect(ekran, hiz_renk,   (633, 48, min(bar_dolu, bar_max), 6), border_radius=3)

    else:
        # OYUN SONU 
        mevcut_skor = skor // 10

        # Skoru bir kez kaydet
        if not skor_kaydedildi:
            skor_kaydet(oyuncu.isim, mevcut_skor)
            skor_kaydedildi = True

        zemin_ciz(int(zemin_kaydi))

        overlay = pygame.Surface((GENISLIK, YUKSEKLIK - 35), pygame.SRCALPHA)
        overlay.fill((10, 5, 30, 190))
        ekran.blit(overlay, (0, 0))

        kutu = pygame.Rect(50, 65, 700, 270)
        pygame.draw.rect(ekran, (30, 10, 50), kutu, border_radius=12)
        pygame.draw.rect(ekran, KIRMIZI,      kutu, 3,  border_radius=12)
        pygame.draw.rect(ekran, PEMBE,        kutu, 1,  border_radius=12)

        metin_ortali(font_buyuk, "💥  OYUN BİTTİ  💥", KIRMIZI, 78, (80, 0, 0))

        # Engel mesajı
        kelimeler = final_mesaji.split()
        satirlar, mevcut_s = [], ""
        for k in kelimeler:
            test = mevcut_s + k + " "
            if font_kucuk.size(test)[0] < 660:
                mevcut_s = test
            else:
                if mevcut_s: satirlar.append(mevcut_s)
                mevcut_s = k + " "
        if mevcut_s: satirlar.append(mevcut_s)

        y_pos = 118
        for satir in satirlar:
            metin_ortali(font_kucuk, satir.strip(), BEYAZ, y_pos)
            y_pos += 28

        pygame.draw.line(ekran, MOR, (100, y_pos + 10), (700, y_pos + 10), 1)

        # Skor
        metin_ortali(font_kucuk, f"Puan: {mevcut_skor:,}", CYAN, y_pos + 20)

        # Mini top 3
        kayitlar = skor_yukle()
        if kayitlar:
            madalyalar = ["🥇", "🥈", "🥉"]
            for j, k in enumerate(kayitlar[:3]):
                renk  = SARI if (k["isim"] == oyuncu.isim and k["skor"] == mevcut_skor) else GRI
                satirr = f"{madalyalar[j]}  {k['isim']}  {k['skor']:,}"
                metin_ortali(font_kucuk, satirr, renk, y_pos + 55 + j * 22)

        blink = SARI if (frame_sayaci // 30) % 2 == 0 else PEMBE
        metin_ortali(font_kucuk, "R  yeniden oyna       T  skor tablosu", blink, y_pos + 140)

        frame_sayaci += 1

    pygame.display.flip()
    saat.tick(60)
