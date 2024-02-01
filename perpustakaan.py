from tkinter import *
from tkinter import messagebox
import mysql.connector
from tkinter import ttk
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class Data_perpustakaan(Tk):
    def __init__(self):
        super().__init__()
        self.title("perpustakaan")   
        self.geometry("850x600")

        # Koneksi ke database
        self.db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="registrasi"
        )

        # Membuat kursor
        self.cursor = self.db.cursor()

        # Membuat dan menampilkan GUI
        self.tampilan_gui()

    def tampilan_gui(self):
        Label(self, text="kode_buku").grid(row=0, column=0, padx=10, pady=10)
        self.kode_buku_entry = Entry(self, width=50)
        self.kode_buku_entry.grid(row=0, column=1, padx=10, pady=10)
        Label(self, text="nama").grid(row=1, column=0, padx=10, pady=10)
        self.nama_entry = Entry(self, width=50)
        self.nama_entry.grid(row=1, column=1, padx=10, pady=10)
        Label(self, text="tanggal_pinjam").grid(row=2, column=0, padx=10, pady=10)
        self.tanggal_pinjam_entry = Entry(self, width=50)
        self.tanggal_pinjam_entry.grid(row=2, column=1, padx=10, pady=10)
        Label(self, text="tanggal_pengembalian").grid(row=3, column=0, padx=10, pady=10)
        self.tanggal_pengembalian_entry = Text(self, width=37, height=1)
        self.tanggal_pengembalian_entry.grid(row=3, column=1, padx=10, pady=10)
        Button(self, text="Simpan Data",
        command=self.simpan_data).grid(row=4, column=0, columnspan=2,pady=10)
        # Menambahkan Treeview

        self.tree = ttk.Treeview(self, columns=("kode_buku", "nama", "tanggal_pinjam",
        "tanggal_pengembalian"), show="headings")
        self.tree.heading("kode_buku", text="kode_buku")
        self.tree.heading("nama", text="nama")
        self.tree.heading("tanggal_pinjam", text="tanggal_pinjam")
        self.tree.heading("tanggal_pengembalian", text="tanggal_pengembalian")
        self.tree.grid(row=5, column=0, columnspan=6, pady=10, padx=10)

        # Menambahkan tombol refresh data
        Button(self, text="Refresh Data", command=self.tampilkan_data).grid(row=6,
        column=0, columnspan=2, pady=10, padx=10)

        # Menambahkan tombol delete data
        Button(self, text="Delete Data", command=self.hapus_data).grid(row=6,
        column=1, columnspan=2, pady=10, padx=10)

        # Menambahkan tombol update data
        Button(self, text="edit Data", command=self.update_data).grid(row=6,
        column=2, columnspan=2, pady=10, padx=10)

        Button(self, text="Print Data", command=self.cetak_ke_pdf).grid(row=6,
        column=3, columnspan=3, pady=10, padx=10)

        self.tampilkan_data()

    def simpan_data(self):
        kode_buku = self.kode_buku_entry.get()
        nama = self.nama_entry.get()
        tanggal_pinjam = self.tanggal_pinjam_entry.get()
        tanggal_pengembalian = self.tanggal_pengembalian_entry.get("1.0", END)
        query = "INSERT INTO perpustakaan (kode_buku, nama, tanggal_pinjam, tanggal_pengembalian) VALUES (%s, %s,%s, %s)"
        values = (kode_buku, nama, tanggal_pinjam, tanggal_pengembalian)
        try:
            self.cursor.execute(query, values)
            self.db.commit()
            messagebox.showinfo("Sukses", "Data berhasil disimpan!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        self.kode_buku_entry.delete(0, END)
        self.nama_entry.delete(0, END)
        self.tanggal_pinjam_entry.delete(0, END)
        self.tanggal_pengembalian_entry.delete("1.0", END)

    def tampilkan_data(self):
        # Hapus data pada treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Ambil data dari database
        self.cursor.execute("SELECT * FROM perpustakaan")
        data = self.cursor.fetchall()

        # Masukkan data ke treeview
        for row in data:
            self.tree.insert("", "end", values=row)
    def hapus_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang akan dihapus.") 
            return
        
        confirmation = messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus data ini?")
        if confirmation:

            for item in selected_item:
                data = self.tree.item(item, 'values')
                kode_buku_to_delete = data[0]
                query = "DELETE FROM perpustakaan WHERE kode_buku = %s"
                values = (kode_buku_to_delete,)
        try:
            self.cursor.execute(query, values)
            self.db.commit()
            messagebox.showinfo("Sukses", "Data berhasil dihapus!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

        self.tampilkan_data()

    def update_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang akan diupdate.")
            return
    
        # Ambil data terpilih dari treeview
        data = self.tree.item(selected_item[0], 'values')

        # Tampilkan form update dengan data terpilih
        self.kode_buku_entry.insert(0, data[0])
        self.nama_entry.insert(0, data[1])
        self.tanggal_pinjam_entry.insert(0, data[2])
        self.tanggal_pengembalian_entry.insert("1.0", data[3])

        # Menambahkan tombol update di form
        Button(self, text="Update", command=lambda:
        self.proses_update(data[0])).grid(row=4, column=1, columnspan=2, pady=10)

    def proses_update(self, kode_buku_to_update):
        kode_buku = self.kode_buku_entry.get()
        nama = self.nama_entry.get()
        tanggal_pinjam = self.tanggal_pinjam_entry.get()
        tanggal_pengembalian = self.tanggal_pengembalian_entry.get("1.0", END)
        query = "UPDATE perpustakaan SET kode_buku=%s, nama=%s, tanggal_pinjam=%s, tanggal_pengembalian =%s WHERE kode_buku=%s"
        values = (kode_buku, nama, tanggal_pinjam, tanggal_pengembalian, kode_buku_to_update)
        try:
            self.cursor.execute(query, values)
            self.db.commit()
            messagebox.showinfo("Sukses", "Data berhasil diupdate!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

        # Bersihkan form setelah update
        self.kode_buku_entry.delete(0, END)
        self.nama_entry.delete(0, END)
        self.tanggal_pinjam_entry.delete(0, END)
        self.tanggal_pengembalian_entry.delete("1.0", END)

        # Tampilkan kembali data setelah diupdate
        self.tampilkan_data()

    def cetak_ke_pdf(self):
        doc = SimpleDocTemplate("data_perpustakaan.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        # Membuat data untuk tabel PDF
        data = [["NIS", "kode_buku", "Jurusan", "Alamat"]]
        for row_id in self.tree.get_children():
            row_data = [self.tree.item(row_id, 'values')[0],
                        
            self.tree.item(row_id, 'values')[1],
            self.tree.item(row_id, 'values')[2],
            self.tree.item(row_id, 'values')[3]]

            data.append(row_data)
        # Membuat tabel PDF
        table = Table(data)

        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0),
        colors.grey),

        ('TEXTCOLOR', (0, 0), (-1, 0),

        colors.whitesmoke),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

        # Menambahkan tabel ke dokumen PDF
        doc.build([table])
        messagebox.showinfo("Sukses", "Data berhasil dicetak ke PDF (data_perpustakaan.pdf).")

if __name__ == "__main__":
    app = Data_perpustakaan()
    app.mainloop()