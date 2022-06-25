# Twitter Tartı


Twitter tartı ile ağırlığını ölçtüğünüz ürünlerin Tweet atılarak bilgilendirilmesi yapılmaktadır.


 ## ÖZELLİKLER

- Ağırlık sensöründen gelen verileri okur
- Twitter'ı depo ve IOT ile bilgilendirme için kullanır
- İstenilen ürün grubunda kullanılabilir

### PROJE İÇİN GEREKLİ MALZEMELER
- Raspberry Pi 4B Model
- Yük Sensörü
- HX711 
- Breadboard
- Jumper Kablo
#### Yük Sensörü
Yük sensöründe 4 adet gerilme ölçer birbirlerine wheatstone köprüsü ile bağlantılıdır.
Gerilme ölçer telin uzunluğu değişince direnci değişen bir elemandır.Bu özellikten faydalanarak yük sensörünün bir ucu sabitlenip diğer ucuna yük konudulduğunda oluşan esnemeden faydalanarak ölçüm gerçekleşiyor.

<img src="https://github.com/SibelKilicc/TwitterTarti/blob/main/Resim1.png" width="auto">

#### HX711
Yük hücresini kuvvetlendirmek ve ADC moduülü olarak kullanılır.
HX711 ile yük sensöründeki direnç değişikliklerini okuyabilecek ve bize isteğimiz verileri verecektir.

<img src="https://github.com/SibelKilicc/TwitterTarti/blob/main/Resim3.jpg" width="auto">

### DONANIM BAĞLANTILARI
#### HX711 - Yük Sensörü Bağlantısı
Yük sensöründe bulunan kabloların renklerine göre Hx711 ile aşağıdaki şekilde bağlantısı sağlanır.
- Kırmızı: E+
- Siyah: E-
- Yeşil: A-
- Beyaz: A+

#### HX711 - Raspberry Pi Bağlantısı
HX711 üzerinde bulunan VCC,GND,DT ve SCK pinleri Raspberry Pi üzerinde bulunan pinlerle aşağıdaki şekilde bağlanır. 

- `VCC` -- Raspberry Pi Pin 2 (5V)
- `GND` -- Raspberry Pi Pin 6 (GND)
- `DT`  -- Raspberry Pi Pin 29 (GPIO 5)
- `SCK` -- Raspberry Pi Pin 31 (GPIO 6)

*SCK:Serial Clock Input, HX711'in I2C ile haberleştiği için kullanılır.
## YAZILIM

Güncellemeler için aşağıdaki paketleri kuralım.
```sh
sudo apt-get update
sudo apt-get upgrade
```
Proje dosyasına Github adresini klonlayarak ya da indirerek ulaşım sağlayarak başlıyoruz.
cd komutu ile dosyanın içine erişim sağlıyoruz.
```sh
git clone https://github.com/Sibelkilicc/TwitterTarti
Desktop/TwitterTarti
cd TwitterTarti
```
Python kütüphanesi için aşağıdaki kod ile paketi yükleyin
```sh
sudo python setup.py install
```
Gerekli bağlantılar ve kurulumlar yapıldıktan sonra programı çalıştırıyoruz
```sh
sudo python example.py
```
Program çalıştığında beklenen değeri görüntüleyemiyoruz. Bunun sebebi yük sensörünün kalibrasyon ayarının yapılmamış olmamasıdır. 
Kalibrasyon ayarlaması için ağırlığını bildiğimiz bir ürünü sensöre yerleştiriyoruz ve ölçülen değeri not alıyoruz. Ölçülen değeri beklenen gerçek değere böldüğümüzde referans değerini elde etmiş oluyoruz.

<img src="https://github.com/SibelKilicc/TwitterTarti/blob/main/Ekran%20Alıntısı.PNG" width="auto">

Terminalde kod dosyamızı açarak elde ettiğimiz referans değerini ilgili kısımda güncelliyoruz.
```sh
sudo nano example.py
```
Kod dosyasında referans kod satırı yorum satırından çıkarılarak elde edilen değer yazılır.
#hx.set_reference_unit(862)

Ctrl+ O yaparak değişikliği kaydediyoruz ve ctrl+x ile kod dosyasından çıkıyoruz.
Programı güncel hali ile çalıştırıyoruz.
```sh
sudo python example.py
```
114 gram paketi koyduğumuzda alınan ölçümler görseldeki şekilde elde edilmiştir. Sensörün hassasiyetine bağlı olarak çok ufak ölçüm farklılıkları ortaya çıkabilir.

<img src="https://github.com/SibelKilicc/TwitterTarti/blob/main/Resim13.jpg" width="auto">
<img src="https://github.com/SibelKilicc/TwitterTarti/blob/main/Resim12.png" width="auto">

**Tebrikler! Proje istenilen şekilde çalışıyor**
