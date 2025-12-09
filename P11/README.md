# **Analisis Pelanggaran SOLID & Hasil Refactoring**

## **1. Deskripsi Singkat**

Studi kasus ini melakukan refactoring terhadap sistem validasi registrasi mata kuliah.
Kode awal (`ValidatorManagerBad`) menjadi sebuah *God Class* karena menangani terlalu banyak logika sekaligus, seperti pengecekan SKS, prasyarat, GPA, dan notifikasi dalam satu method `validate_registration()`.

Refactoring dilakukan dengan menerapkan prinsip **SRP**, **OCP**, dan **DIP**, menggunakan konsep **abstraksi (interface/kontrak)** serta **dependency injection**.

---

# **2. Analisis Pelanggaran SOLID**

## **A. Pelanggaran SRP (Single Responsibility Principle)**

### **Pelanggaran**

`ValidatorManagerBad` memiliki beberapa tanggung jawab sekaligus:

1. Validasi batas SKS
2. Validasi prasyarat mata kuliah
3. Validasi GPA
4. Menampilkan output keberhasilan/gagal
5. Mengirim notifikasi (dalam bentuk print)

Jika salah satu aturan validasi berubah (misalnya kebijakan SKS atau prasyarat), seluruh class harus ikut berubah.

### **Mengapa melanggar SRP**

Sebuah class seharusnya **hanya memiliki satu alasan untuk berubah**, tetapi class ini memiliki banyak alasan perubahan.

### **Solusi Refactor**

* Pisahkan setiap logika ke *validator class* yang berbeda:

  * `SKSValidator`
  * `PrerequisiteValidator`
  * `GPAValidator`
* Buat *Coordinator* (`RegistrationValidator`) yang hanya menangani **pengkoordinasian** validator.

---

## **B. Pelanggaran OCP (Open/Closed Principle)**

### **Pelanggaran**

Jika ingin menambah aturan validasi baru (misalnya validasi usia mahasiswa, status keaktifan, atau bayar UKT), maka:

> Programmer wajib **mengubah langsung** isi method `validate_registration()`.

Ini melanggar OCP karena class terus mengalami modifikasi setiap ada perubahan kebijakan akademik.

### **Solusi Refactor**

* Buat **kontrak abstraksi** bernama `IValidator`
* Setiap rule dibuat sebagai class baru yang mengimplementasikan kontrak tersebut
* Koordinator (`RegistrationValidator`) hanya memanggil validator yang sudah di-*inject*

Contoh pembuktian OCP:

* Menambahkan validator baru `GPAValidator`
  > Tidak mengubah *satupun baris* di `RegistrationValidator`

---

## **C. Pelanggaran DIP (Dependency Inversion Principle)**

### **Pelanggaran**

Class `ValidatorManagerBad` memiliki dependensi **langsung** pada implementasi konkrit melalui if/else:

```python
if student.current_sks + course.sks > max:
    ...
elif missing_prereqs:
    ...
elif student.gpa < 2.5:
    ...
```

Class bergantung pada *detail implementasi*, bukan pada abstraksi.

### **Solusi Refactor**

* Buat interface `IValidator` (abstraksi tingkat tinggi)
* Implementasi konkrit seperti `SKSValidator`, `PrerequisiteValidator`, dan `GPAValidator` “plug-in” ke koordinator
* `RegistrationValidator` bergantung pada **abstraksi** (list `IValidator`), bukan implementasi

---

# **3. Hasil Refactoring**

## **A. Struktur Baru**

Menggunakan konsep SOLID:

```
IValidator (interface/abstraksi)
   ├── SKSValidator
   ├── PrerequisiteValidator
   └── GPAValidator (contoh penambahan rule baru)

RegistrationValidator (Coordinator)
Student
Course
```

## **B. Alur Refactoring**

1. Memisahkan setiap validasi ke dalam kelas dengan tanggung jawab tunggal (SRP)
2. Membuat kontrak `IValidator` agar setiap validator memiliki struktur yang sama (DIP)
3. Koordinator menerima list validator melalui dependency injection (DIP)
4. Menambah rule cukup membuat class baru tanpa mengubah koordinator (OCP)

---

# **4. Pembuktian OCP**

Dengan hanya membuat class baru:

```python
class GPAValidator(IValidator):
    ...
```

Dan meng-inject:

```python
validators_with_gpa = [
    SKSValidator(24),
    PrerequisiteValidator(),
    GPAValidator(2.5)
]
coord = RegistrationValidator(validators_with_gpa)
```

Sistem otomatis mendukung rule baru **tanpa perlu memodifikasi** kode utama.

---

# **5. Keuntungan Refactoring**

| Sebelum Refactor                    | Setelah Refactor                           |
| ----------------------------------- | ------------------------------------------ |
| God class, banyak tanggung jawab    | SRP: Setiap validator punya tugas tunggal  |
| Sulit menambah aturan baru          | OCP: Tambah rule tanpa ubah class utama    |
| Bergantung pada detail implementasi | DIP: Coordinator bergantung pada abstraksi |
| Logika bercampur, sulit diuji       | Setiap validator bisa diuji terpisah       |
| Tidak fleksibel                     | Sangat modular & scalable                  |

---

# **6. Kesimpulan**

Refactoring ini berhasil:

* Memecah tanggung jawab (SRP)
* Membuat sistem dapat dikembangkan tanpa mengubah kode inti (OCP)
* Mengurangi ketergantungan pada implementasi konkret (DIP)
* Meningkatkan keterbacaan, fleksibilitas, dan maintainability kode

Sistem validasi kini **lebih bersih, mudah diuji, dan mudah dikembangkan**.
