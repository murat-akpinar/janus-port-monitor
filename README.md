# Janus Port Monitor

Bu uygulama, belirli bir port üzerinde akan trafiği gerçek zamanlı olarak izlemek için bir TUI (Terminal User Interface) sunar. Aşağıdaki yönergeler, uygulamanın Debian tabanlı ve Red Hat tabanlı sistemlerde çalıştırılması için gerekli bağımlılıkları kurmanıza yardımcı olacaktır.

## Gereksinimler

- Python 3.6 veya üzeri
- `ss` komutu (trafik izleme için)
- `npyscreen` Python kütüphanesi

---

## Kurulum

### Debian Tabanlı Sistemler (Ubuntu, Debian, vb.)

1. **Python ve pip'i yükleyin:**

    ```bash
    sudo apt update
    sudo apt install -y python3 python3-pip
    ```

2. **Gerekli sistem bağımlılıklarını yükleyin:**

    ```bash
    sudo apt install -y ss python3-dev build-essential
    ```

3. **Python kütüphanelerini yükleyin:**

    ```bash
    pip3 install npyscreen
    ```

---

### Red Hat Tabanlı Sistemler (CentOS, RHEL, Fedora, vb.)

1. **Python ve pip'i yükleyin:**

    ```bash
    sudo yum install -y python3 python3-pip
    ```

2. **Gerekli sistem bağımlılıklarını yükleyin:**

    ```bash
    sudo yum install -y iproute python3-devel gcc
    ```

3. **Python kütüphanelerini yükleyin:**

    ```bash
    pip3 install npyscreen
    ```

---

## Uygulamayı Çalıştırma

1. Python dosyasını terminalde çalıştırın:

    ```bash
    python3 janus.py
    ```

2. Uygulama, belirlediğiniz port üzerindeki trafiği izleyip bir TUI ekranında gösterecektir.

---

## Sorun Giderme

- **`ss` komutu bulunamıyor:** Gerekli paketi (`iproute2` veya `iproute`) kurduğunuzdan emin olun.
- **`npyscreen` bulunamıyor:** `pip3 install npyscreen` komutuyla kütüphaneyi yükleyin.

Herhangi bir hata ile karşılaşırsanız sistem loglarını kontrol edin veya bağımlılıkların doğru yüklendiğinden emin olun.
