#

import RPi.GPIO as GPIO
import time
import threading



class HX711:

    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck

        self.DOUT = dout

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0

        # ÖLÇEK'e bölündükten SONRA referans biriminize karşılık gelen hx711 tarafından döndürülen değer.
        
        self.REFERENCE_UNIT = 1
        self.REFERENCE_UNIT_B = 1

        self.OFFSET = 1
        self.OFFSET_B = 1
        self.lastVal = int(0)

        self.DEBUG_PRINTING = False

        self.byte_format = 'MSB'
        self.bit_format = 'MSB'

        self.set_gain(gain)

       
        time.sleep(1)

        
    def convertFromTwosComplement24bit(self, inputValue):
        return -(inputValue & 0x800000) + (inputValue & 0x7fffff)

    
    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    
    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)

        # bir dizi ham baytın okunması ve atılması
        self.readRawBytes()

        
    def get_gain(self):
        if self.GAIN == 1:
            return 128
        if self.GAIN == 3:
            return 64
        if self.GAIN == 2:
            return 32

        
        return 0
        

    def readNextBit(self):
      #Saat HX711 Dijital Seri Saat (PD_SCK). DOUT, PD_SCK yükselen kenardan 1us sonra hazır olacaktır, 
      #bu nedenle, DOUT'un kararlı olacağını bildiğimizde, PD_SCL'yi düşürdükten sonra örnekleme yaparız.
       
       GPIO.output(self.PD_SCK, True)
       GPIO.output(self.PD_SCK, False)
       value = GPIO.input(self.DOUT)

      
       return int(value)


    def readNextByte(self):
       byteValue = 0

      #Bitleri okur ve baytı MSB veya LSB bit modunda 
      #olmamıza bağlı olarak yukarıdan veya aşağıdan oluşturur.
       
       for x in range(8):
          if self.bit_format == 'MSB':
             byteValue <<= 1
             byteValue |= self.readNextBit()
          else:
             byteValue >>= 1              
             byteValue |= self.readNextBit() * 0x80

       
       return byteValue 
        

    def readRawBytes(self):
        #Bekleyin ve Okuma Kilidi'ni alır, başka bir iş parçacığı zaten varsa
        #HX711 seri arabirimini sürebilir
        self.readLock.acquire()

        # Bir örneği okumak için HX711'in hazır olmasını beklenir.
        while not self.is_ready():
           pass

        # HX711'den üç bayt veri okunur.
        firstByte  = self.readNextByte()
        secondByte = self.readNextByte()
        thirdByte  = self.readNextByte()

        #HX711 Kanal ve kazanç faktörü, 24 veri bitinden 
        #sonra okunan bit sayısı ile belirlenir.

        for i in range(self.GAIN):
           # Clock a bit out of the HX711 and throw it away.
           self.readNextBit()

        #HX711 seri arabirimini sürmeyi bitirdiğimize göre 
        #Okuma Kilidini serbest bırakılır.

        self.readLock.release()           

      
        #Nasıl yapılandırıldığımıza bağlı olarak, 
        #sıralı bir ham bayt değerleri listesi döndürür.

        if self.byte_format == 'LSB':
           return [thirdByte, secondByte, firstByte]
        else:
           return [firstByte, secondByte, thirdByte]


    def read_long(self):
        # HX711'den ham bayt biçiminde bir örnek alır.
        dataBytes = self.readRawBytes()


        if self.DEBUG_PRINTING:
            print(dataBytes,)
        
        
        twosComplementValue = ((dataBytes[0] << 16) |
                               (dataBytes[1] << 8)  |
                               dataBytes[2])

        if self.DEBUG_PRINTING:
            print("Twos: 0x%06x" % twosComplementValue)
        
        #24 bit ikinin tamamlayıcısından işaretli bir değere dönüştürür.

        signedIntValue = self.convertFromTwosComplement24bit(twosComplementValue)

        # Okuduğumuz en son numune değerini kaydeder.

        self.lastVal = signedIntValue

        #HX711'den okuduğumuz örnek değeri döndürün.
        return int(signedIntValue)

    
    def read_average(self, times=3):
        # Rasyonel miktarda numune almamızın istendiğinden emin olunur.

        if times <= 0:
            raise ValueError("HX711()::read_average(): times must >= 1!!")

       
        if times == 1:
            return self.read_long()

       
        if times < 5:
            return self.read_median(times)

        valueList = []

        for x in range(times):
            valueList += [self.read_long()]

        valueList.sort()

       
        trimAmount = int(len(valueList) * 0.2)

        valueList = valueList[trimAmount:-trimAmount]

        return sum(valueList) / len(valueList)


    # Medyan tabanlı bir okuma yöntemi, bilinmeyen veya CPU ile ilgili 
    #nedenlerle rastgele değer artışları elde ederken yardımcı olur.

    def read_median(self, times=3):
       if times <= 0:
          raise ValueError("HX711::read_median(): times must be greater than zero!")
      
       
       if times == 1:
          return self.read_long()

       valueList = []

       for x in range(times):
          valueList += [self.read_long()]

       valueList.sort()

      
       if (times & 0x1) == 0x1:
          return valueList[len(valueList) // 2]
       else:
         
          midpoint = len(valueList) / 2
          return sum(valueList[midpoint:midpoint+2]) / 2.0


    def get_value(self, times=3):
        return self.get_value_A(times)


    def get_value_A(self, times=3):
        return self.read_median(times) - self.get_offset_A()


    def get_value_B(self, times=3):
    
        g = self.get_gain()
        self.set_gain(32)
        value = self.read_median(times) - self.get_offset_B()
        self.set_gain(g)
        return value

    def get_weight(self, times=3):
        return self.get_weight_A(times)


    def get_weight_A(self, times=3):
        value = self.get_value_A(times)
        value = value / self.REFERENCE_UNIT
        return value

    def get_weight_B(self, times=3):
        value = self.get_value_B(times)
        value = value / self.REFERENCE_UNIT_B
        return value

    
    def tare(self, times=15):
        return self.tare_A(times)
    
    
    def tare_A(self, times=15):
        
        backupReferenceUnit = self.get_reference_unit_A()
        self.set_reference_unit_A(1)
        
        value = self.read_average(times)

        if self.DEBUG_PRINTING:
            print("Tare A value:", value)
        
        self.set_offset_A(value)

        
        self.set_reference_unit_A(backupReferenceUnit)

        return value


    def tare_B(self, times=15):
        
        backupReferenceUnit = self.get_reference_unit_B()
        self.set_reference_unit_B(1)

       
        backupGain = self.get_gain()
        self.set_gain(32)

        value = self.read_average(times)

        if self.DEBUG_PRINTING:
            print("Tare B value:", value)
        
        self.set_offset_B(value)

        # Kazanç/kanal/referans birimi ayarlarını geri yüklenir.
        self.set_gain(backupGain)
        self.set_reference_unit_B(backupReferenceUnit)
       
        return value


    
    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
        if byte_format == "LSB":
            self.byte_format = byte_format
        elif byte_format == "MSB":
            self.byte_format = byte_format
        else:
            raise ValueError("Unrecognised byte_format: \"%s\"" % byte_format)

        if bit_format == "LSB":
            self.bit_format = bit_format
        elif bit_format == "MSB":
            self.bit_format = bit_format
        else:
            raise ValueError("Unrecognised bitformat: \"%s\"" % bit_format)

            


    # uyumluluk nedenleriyle kanal A için ofseti ayarlanır.
    def set_offset(self, offset):
        self.set_offset_A(offset)

    def set_offset_A(self, offset):
        self.OFFSET = offset

    def set_offset_B(self, offset):
        self.OFFSET_B = offset

    def get_offset(self):
        return self.get_offset_A()

    def get_offset_A(self):
        return self.OFFSET

    def get_offset_B(self):
        return self.OFFSET_B


    
    def set_reference_unit(self, reference_unit):
        self.set_reference_unit_A(reference_unit)

        
    def set_reference_unit_A(self, reference_unit):
        # Geçersiz bir referans birimi kullanmamızın istenmediğinden emin olunur.
        if reference_unit == 0:
            raise ValueError("HX711::set_reference_unit_A() can't accept 0 as a reference unit!")
            return

        self.REFERENCE_UNIT = reference_unit

        
    def set_reference_unit_B(self, reference_unit):
        
        if reference_unit == 0:
            raise ValueError("HX711::set_reference_unit_A() can't accept 0 as a reference unit!")
            return

        self.REFERENCE_UNIT_B = reference_unit


    def get_reference_unit(self):
        return get_reference_unit_A()

        
    def get_reference_unit_A(self):
        return self.REFERENCE_UNIT

        
    def get_reference_unit_B(self):
        return self.REFERENCE_UNIT_B
        
        
    def power_down(self):
       
        self.readLock.acquire()

        #
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)

        time.sleep(0.0001)

       
        self.readLock.release()           


    def power_up(self):
       
        self.readLock.acquire()

        GPIO.output(self.PD_SCK, False)

        # Wait 100 us for the HX711 to power back up.
        time.sleep(0.0001)

        
        self.readLock.release()

       # HX711, 128 kazanç ile varsayılan olarak Kanal A'ya ayarlanacaktır. 
       #İstemci yazılımının bizden talep ettiği bu değilse, bir numune alın ve atın,
       #böylece HX711'den bir sonraki numune doğru kanaldan/kazançtan olacaktır.

        if self.get_gain() != 128:
            self.readRawBytes()


    def reset(self):
        self.power_down()
        self.power_up()


# EOF - hx711.py