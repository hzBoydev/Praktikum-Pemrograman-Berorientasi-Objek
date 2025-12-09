from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

# ----------------------------
# Contoh "KODE BURUK" (God Class)
# ----------------------------
@dataclass
class Student:
    name: str
    completed_courses: List[str]
    current_sks: int
    ipk: float

@dataclass
class Course:
    code: str
    sks: int
    prereqs: List[str]

class ValidatorManagerBad:
    """
    Class ini melanggar:
    - SRP: menampung banyak tanggung jawab (cek SKS, cek prasyarat, cek IPK, kirim notifikasi, dll.)
    - OCP: menambah rule baru harus ubah method ini
    - DIP: menggunakan pengecekan konkrit dan hard-coded
    """
    def __init__(self, max_sks=24):
        self.max_sks = max_sks

    def validate_registration(self, student: Student, course: Course) -> bool:
        print(f"[BAD] Memvalidasi pendaftaran {student.name} untuk {course.code} ...")
        # cek SKS
        if student.current_sks + course.sks > self.max_sks:
            print(" - Gagal: Melebihi batas SKS.")
            return False

        # cek prasyarat
        missing = [c for c in course.prereqs if c not in student.completed_courses]
        if missing:
            print(f" - Gagal: Prasyarat tidak terpenuhi: {missing}")
            return False

        # cek IPK (misal rule tambahan)
        if student.ipk < 2.5:
            print(" - Gagal: IPK di bawah batas minimal.")
            return False

        # notifikasi (hardcoded)
        print(f" - Sukses: {student.name} terdaftar. Mengirim notifikasi email...")
        return True

# ----------------------------
# Refactor: SRP, OCP, DIP
# ----------------------------

# --- Abstraksi: kontrak validator ---
class IValidator(ABC):
    """
    Kontrak: setiap validator harus punya method validate() yang mengembalikan (bool, pesan)
    """
    @abstractmethod
    def validate(self, student: Student, course: Course) -> (bool, str):
        pass

# --- Implementasi konkret (plug-in validators) ---
class SKSValidator(IValidator):
    def __init__(self, max_sks: int = 24):
        self.max_sks = max_sks

    def validate(self, student: Student, course: Course):
        if student.current_sks + course.sks > self.max_sks:
            return False, f"Melebihi batas SKS (max {self.max_sks})"
        return True, "SKS OK"

class PrerequisiteValidator(IValidator):
    def validate(self, student: Student, course: Course):
        missing = [c for c in course.prereqs if c not in student.completed_courses]
        if missing:
            return False, f"Prasyarat tidak terpenuhi: {missing}"
        return True, "Prasyarat OK"

# Contoh validator baru: rule tambahan untuk membuktikan OCP
class IPKValidator(IValidator):
    def __init__(self, min_ipk: float = 2.5):
        self.min_ipk = min_ipk

    def validate(self, student: Student, course: Course):
        if student.ipk < self.min_ipk:
            return False, f"IPK harus >= {self.min_ipk}"
        return True, "IPK OK"

# --- Koordinator (Coordinator) ---
class RegistrationValidator:
    """
    Tanggung jawab tunggal: mengkoordinasi sekumpulan validator.
    - Menerima dependency berupa list IValidator melalui konstruktor (Dependency Injection).
    - Tidak tahu detail implementasi tiap validator (pegang kontrak IValidator).
    """
    def __init__(self, validators: List[IValidator]):
        self.validators = validators

    def validate(self, student: Student, course: Course) -> bool:
        print(f"[REFAC] Memvalidasi pendaftaran {student.name} untuk {course.code} ...")
        all_ok = True
        for v in self.validators:
            ok, message = v.validate(student, course)
            print(f" - {v.__class__.__name__}: {message}")
            if not ok:
                all_ok = False
                # tetap lanjutkan untuk menampilkan semua pesan (atau bisa return False langsung)
        if all_ok:
            print(" - Semua validator lulus. Daftar berhasil. Mengirim notifikasi...")
            return True
        else:
            print(" - Validasi gagal. Tidak jadi mendaftar.")
            return False

# ----------------------------
# Eksekusi & Pembuktian OCP
# ----------------------------
def main():
    # Contoh Data
    siti = Student(name="Siti", completed_courses=["IF101", "MATH101"], current_sks=15, ipk=3.0)
    udin = Student(name="Udin", completed_courses=["IF101"], current_sks=22, ipk=2.0)

    advanced_ai = Course(code="AI201", sks=3, prereqs=["IF101", "MATH101"])
    networks = Course(code="NET202", sks=3, prereqs=["IF101"])

    print("\n=== Skenario 0: Menjalankan Kode Buruk (sebagai perbandingan) ===")
    bad = ValidatorManagerBad(max_sks=24)
    bad.validate_registration(siti, advanced_ai)
    bad.validate_registration(udin, networks)

    print("\n=== Skenario 1: Refactor - Inject SKS + Prerequisite Validators ===")
    validators = [SKSValidator(max_sks=24), PrerequisiteValidator()]
    coord = RegistrationValidator(validators=validators)
    coord.validate(siti, advanced_ai)  # sukses
    coord.validate(udin, networks)       # gagal karena SKS atau IPK

    print("\n=== Skenario 2: Pembuktian OCP - Tambah Validator baru (IPK) TANPA ubah RegistrationValidator ===")
    # Tambah validator baru cukup buat kelas baru dan inject ke dalam coordinator
    validators_with_ipk = [SKSValidator(24), PrerequisiteValidator(), IPKValidator(min_ipk=2.5)]
    coord2 = RegistrationValidator(validators=validators_with_ipk)
    coord2.validate(siti, advanced_ai)  # sukses
    coord2.validate(udin, networks)       # gagal karena IPK < 2.5

if __name__ == "__main__":
    main()