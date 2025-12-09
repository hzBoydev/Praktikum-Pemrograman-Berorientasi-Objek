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