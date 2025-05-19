import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
import os


# --- STİL AYARLARI ---
SUCCESS_COLOR = "#28a745"
BG_COLOR = "#f5f6fa"
PRIMARY_COLOR = "#3498db"
SECONDARY_COLOR = "#2ecc71"
DANGER_COLOR = "#e74c3c"
SUCCESS_COLOR = "#27ae60"
FONT = ("Helvetica", 10)
FONT_BOLD = ("Helvetica", 10, "bold")

categories = ["Elektronik", "Aksesuar", "Telefonlar"]
sales_history = []
# --- VERİLER ---
products = [
    {"id": 1, "name": "IPHONE 8", "desc": "White", "qty": 9, "price": 50000},
    {"id": 2, "name": "INFINIX HOT 6 PRO", "desc": "Black", "qty": 98, "price": 72000},
    {"id": 3, "name": "SAMSUNG GALAXY S21", "desc": "Blue", "qty": 25, "price": 95000},
    {"id": 4, "name": "çınar", "desc": "Blue", "qty": 25, "price": 95000},

]
sales_history = []
cart = []

# --- YARDIMCI FONKSİYONLAR ---
def create_button(parent, text, command, bg_color=PRIMARY_COLOR, fg_color="white"):
    btn = tk.Button(parent, text=text, command=command,
                    bg=bg_color, fg=fg_color, font=FONT_BOLD,
                    bd=0, padx=15, pady=5,
                    activebackground=bg_color, activeforeground=fg_color)
    btn.bind("<Enter>", lambda e: btn.config(bg="#2980b9" if bg_color == PRIMARY_COLOR else bg_color))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
    return btn

def create_entry(parent, placeholder, width=20):
    entry = ttk.Entry(parent, width=width, font=FONT)
    entry.insert(0, placeholder)
    entry.config(foreground="gray")
    
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground="black")
    
    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground="gray")
    
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return entry

def create_treeview(parent, columns):
    frame = tk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=FONT_BOLD, background=PRIMARY_COLOR, foreground="white")
    style.configure("Treeview", font=FONT, rowheight=25)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return tree, frame

# --- İŞLEVSEL FONKSİYONLAR ---
def search_products(*args):
    # Arama sadece ürün adının ilk harfine göre yapılacak
    keyword = entry_search.get().lower()
    for item in tree.get_children():
        tree.delete(item)
    
    for product in products:
        if not keyword or product["name"].lower().startswith(keyword):
            tree.insert("", "end", values=(
                product["id"], product["name"], product["desc"], product["qty"], f"{product['price']} TL"
            ))

def load_products():
    for item in tree.get_children():
        tree.delete(item)
    for product in products:
        tree.insert("", "end", values=(
            product["id"], product["name"], product["desc"], product["qty"], f"{product['price']} TL"
        ))

def add_to_cart(event):
    selected_item = tree.selection()
    if not selected_item:
        return

    product_id = tree.item(selected_item)["values"][0]
    product_name = tree.item(selected_item)["values"][1]
    product_desc = tree.item(selected_item)["values"][2]
    product_price = tree.item(selected_item)["values"][4]
    
    # Sepete ürün ekleme işlemi
    existing_item = None
    for child in cart_tree.get_children():
        item = cart_tree.item(child)["values"]
        if item[0] == product_id:
            existing_item = child
            break
    
    if existing_item:
        current_quantity = int(cart_tree.item(existing_item)["values"][2])
        current_total = float(cart_tree.item(existing_item)["values"][4].replace(" TL", ""))
        new_quantity = current_quantity + 1
        new_total = current_total + float(product_price.replace(" TL", "").replace(",", ""))
        
        cart_tree.item(existing_item, values=(
            product_id, product_name, new_quantity, product_price, f"{new_total:.2f} TL"
        ))
    else:
        cart_tree.insert("", "end", values=(
            product_id, product_name, 1, product_price, product_price
        ))
    
    update_total()

def remove_from_cart():
    selected = cart_tree.selection()
    if not selected:
        return
    
    for item in selected:
        item_values = cart_tree.item(item)["values"]
        product_id = item_values[0]
        product_name = item_values[1]
        product_qty = item_values[2]
        product_price = float(item_values[3].replace(" TL", ""))
        
        # Sepet sayısını azalt
        new_qty = product_qty - 1  # Adet bir azalacak
        
        if new_qty > 0:
            # Yeni adet ile sepeti güncelle
            cart_tree.item(item, values=(product_id, product_name, new_qty, f"{product_price} TL", f"{new_qty * product_price} TL"))
        else:
            # Sepetteki ürün tamamen çıkarılacaksa, satırı kaldır
            cart_tree.delete(item)
    
    update_total()  # Toplamı güncelle


def update_total():
    total = 0
    for child in cart_tree.get_children():
        item = cart_tree.item(child)["values"]
        total += float(item[4].replace(" TL", ""))
    lbl_total.config(text=f"{total:.2f} TL")

def purchase():
    if not cart_tree.get_children():
        messagebox.showerror("Hata", "Sepetiniz boş. Lütfen ürün ekleyin.")
        return

    # Sadece satın alma sırasında stok kontrolü
    for child in cart_tree.get_children():
        item = cart_tree.item(child)["values"]
        product_id = item[0]
        quantity_in_cart = item[2]

        for product in products:
            if product["id"] == product_id:
                if quantity_in_cart > product["qty"]:
                    messagebox.showerror("Hata", f"{product['name']} için stokta sadece {product['qty']} adet mevcut!")
                    return

    # Satış işlemi başarılı
    sales_report = ""
    total_amount = 0
    for child in cart_tree.get_children():
        item = cart_tree.item(child)["values"]
        product_id = item[0]
        product_name = item[1]
        quantity = item[2]
        price = float(item[3].replace(" TL", ""))
        total_price = quantity * price

        sales_report += f"{product_id} - {product_name} - Adet: {quantity} - Fiyat: {price} TL - Tutar: {total_price:.2f} TL\n--------------------\n"
        total_amount += total_price

        # Stok azalt
        for product in products:
            if product["id"] == product_id:
                product["qty"] -= quantity

        # Satışı geçmişe kaydet
        sales_history.append({
            "id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "total": total_price,
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    sales_report += f"Toplam: {total_amount:.2f} TL"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(os.getcwd(), f"sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    with open(file_path, "w") as file:
        file.write(sales_report)

    messagebox.showinfo("Satın Alma Başarılı", f"Satın Alma Başarıyla Gerçekleşti!\n\nSatış raporu kaydedildi: {file_path}")

    cart_tree.delete(*cart_tree.get_children())
    update_total()
    load_products()

def open_password_panel():
    try_count = [0]

    def check_password():
        password = entry_pass.get()
        if password == "2006":
            entry_pass.config(foreground="black")  # Şifre doğru ise siyah yazı
            login_window.destroy()
            open_admin_panel()
        else:
            try_count[0] += 1
            entry_pass.delete(0, tk.END)
            entry_pass.config(foreground="red")  # Hatalı şifre olduğunda kırmızı yazı
            if try_count[0] >= 3:
                messagebox.showerror("Hatalı Giriş", "3 kez hatalı giriş yapıldı. Uygulama kapanıyor.")
                root.destroy()
            else:
                messagebox.showwarning("Hatalı", f"Yanlış şifre! {3 - try_count[0]} deneme hakkınız kaldı.")
                # Şifre kutusunun etrafını kırmızı yapalım (görsel iyileştirme)
                style = ttk.Style()
                style.configure('Error.TEntry', background='pink')  # Stil tanımlaması
                entry_pass.config(style='Error.TEntry')  # Stil uygulama
                login_window.after(500, lambda: entry_pass.config(style='TEntry'))  # 500ms sonra stili geri al
            


    # Animasyonlu açılma
    def animate_fade_in(window, alpha=0.0):
        alpha += 0.05
        if alpha <= 1:
            window.attributes('-alpha', alpha)
            window.after(20, lambda: animate_fade_in(window, alpha))  # 20ms aralıklarla saydamlık artır
        else:
            window.attributes('-alpha', 1)

    # Giriş penceresini oluştur
    login_window = tk.Toplevel(root)
    login_window.title("Yönetici Girişi")
    login_window.geometry("300x200")
    login_window.resizable(False, False)
    login_window.grab_set()
    login_window.attributes('-alpha', 0.0)  # Başta saydam
    animate_fade_in(login_window)           # ✨ Animasyon başlat

    # Kapatma tuşunun işlevini ayarlama
    login_window.protocol("WM_DELETE_WINDOW", lambda: close_login_window(login_window))

    def close_login_window(window):
        window.destroy()

    tk.Label(login_window, text="Şifre:", font=FONT_BOLD).pack(pady=(20, 5))

    # Şifre giriş kutusu ve göz butonunu aynı satırda yap
    entry_frame = tk.Frame(login_window)
    entry_frame.pack(pady=5)

    entry_pass = ttk.Entry(entry_frame, show="*", font=FONT, width=22)
    entry_pass.pack(side="left", padx=(0, 0))
    entry_pass.focus_set()
    entry_pass.bind("<Return>", lambda event: check_password())  # ENTER tuşu

    # 👁 Göster / Gizle Butonu (Entry'nin yanına yerleştirilmiş)
    def toggle_password():
        if entry_pass.cget('show') == "*":
            entry_pass.config(show="")
            btn_eye.config(text="🙈")  # İsteğe göre emoji/ikon
        else:
            entry_pass.config(show="*")
            btn_eye.config(text="👁️")

    # Göz butonunu ekle
    btn_eye = tk.Button(entry_frame, text="👁️", command=toggle_password,
                        font=("Helvetica", 8), bg="white", relief="flat", padx=5)
    btn_eye.pack(side="right")

    # Giriş Yap butonu
    tk.Button(login_window, text="Giriş Yap", command=check_password,
              bg=PRIMARY_COLOR, fg="white", font=FONT_BOLD).pack(pady=5)

def open_admin_panel():
    """Yönetici panelini açar."""
    admin_window = tk.Toplevel(root)
    admin_window.title("Yönetici Paneli")
    admin_window.geometry("700x500")

    notebook = ttk.Notebook(admin_window)
    notebook.pack(fill="both", expand=True)

    create_product_management_tab(notebook)
    create_stock_status_tab(notebook)
    create_sales_reports_tab(notebook)


def create_product_management_tab(notebook):
    """Ürün yönetimi sekmesini oluşturur."""
    product_tab = tk.Frame(notebook)
    notebook.add(product_tab, text="Ürün Yönetimi")

    tk.Button(product_tab, text="Yeni Ürün Ekle", command=open_add_product_form, bg=SUCCESS_COLOR, fg="white", font=FONT_BOLD).pack(pady=10)
    tk.Button(product_tab, text="Ürün Düzenle / Sil", command=open_edit_product_form, bg=PRIMARY_COLOR, fg="white", font=FONT_BOLD).pack(pady=10)
    tk.Button(product_tab, text="Ürün Kategorileri", command=open_category_management, bg=SECONDARY_COLOR, fg="white", font=FONT_BOLD).pack(pady=10)


def create_stock_status_tab(notebook):
    """Stok durumu sekmesini oluşturur."""
    stock_tab = tk.Frame(notebook)
    notebook.add(stock_tab, text="Stok Durumu")

    global lbl_stock_report
    lbl_stock_report = tk.Label(stock_tab, text="", font=("Helvetica", 10), justify="left")
    lbl_stock_report.pack(pady=20)
    update_stock_report()


def create_sales_reports_tab(notebook):
    """Satış raporları sekmesini oluşturur."""
    report_tab = tk.Frame(notebook)
    notebook.add(report_tab, text="Satış Raporları")

    tk.Label(report_tab, text="Tarih Seçin:", font=FONT_BOLD).pack(pady=10)
    cal = DateEntry(report_tab, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    cal.pack()

    tk.Button(report_tab, text="Göster", command=lambda: show_sales(cal, report_tab), bg=SECONDARY_COLOR, fg="white").pack(pady=5)


def get_sales_for_date(selected_date):
    """Seçilen tarihe göre satışları getirir."""
    total_sales = 0
    sales_report = ""
    for sale in sales_history:
        sale_date = datetime.strptime(sale["date"], "%Y-%m-%d")
        if sale_date.date() == selected_date:
            total_sales += sale["total"]
            sales_report += f"{sale['id']} - {sale['product_name']} - Adet: {sale['quantity']} - Tutar: {sale['total']:.2f} TL\n"
    return total_sales, sales_report


def show_sales(cal, report_tab):
    """Seçilen tarihe göre satışları gösterir."""
    selected_date = cal.get_date()
    total, report = get_sales_for_date(selected_date)

    # Mevcut satış raporunu temizleriz
    for widget in report_tab.pack_slaves()[3:]:
        widget.destroy()

    # Yeni satış raporunu ekleriz
    tk.Label(report_tab, text=f"{selected_date} Satışları", font=FONT_BOLD).pack(pady=10)
    tk.Message(report_tab, text=report or "Satış yok", width=500).pack()
    tk.Label(report_tab, text=f"Toplam Satış: {total:.2f} TL", font=FONT_BOLD, fg="green").pack(pady=10)


def update_stock_report():
    """Stok raporunu günceller."""
    stock_report = ""
    for product in products:
        stock_report += f"{product['name']} - Stok: {product['qty']} adet\n"
    lbl_stock_report.config(text=stock_report)


def open_category_management():
    """Ürün kategorileri yönetimini açar."""
    category_window = tk.Toplevel(root)
    category_window.title("Ürün Kategorileri Yönetimi")
    category_window.geometry("350x300")

    def add_category():
        new_category = entry_category.get()
        if new_category:
            categories.append(new_category)
            messagebox.showinfo("Başarılı", f"{new_category} kategorisi eklendi!")
            category_window.destroy()
        else:
            messagebox.showerror("Hata", "Kategori adı boş olamaz.")

    tk.Label(category_window, text="Yeni Kategori Ekle", font=FONT_BOLD).pack(pady=10)
    entry_category = ttk.Entry(category_window, width=30)
    entry_category.pack(pady=10)

    tk.Button(category_window, text="Kategori Ekle", command=add_category, bg=SUCCESS_COLOR, fg="white").pack(pady=10)

    # Kategoriler listesi
    tk.Label(category_window, text="Mevcut Kategoriler:", font=FONT_BOLD).pack(pady=5)
    listbox = tk.Listbox(category_window, height=5, width=40)
    listbox.pack(pady=10)
    for category in categories:
        listbox.insert(tk.END, category)


def open_add_product_form():
    """Yeni ürün ekleme formunu açar."""
    def add_product():
        name = entry_name.get()
        description = entry_desc.get()
        price = entry_price.get()
        qty = entry_qty.get()

        if not name or not description or not price or not qty:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return

        try:
            price = float(price)
            qty = int(qty)
        except ValueError:
            messagebox.showerror("Hata", "Fiyat ve Stok Sayısı geçerli olmalıdır.")
            return

        new_id = products[-1]["id"] + 1 if products else 1
        new_product = {
            "id": new_id,
            "name": name,
            "desc": description,
            "qty": qty,
            "price": price
        }
        products.append(new_product)
        update_stock_report()
        add_product_window.destroy()

    add_product_window = tk.Toplevel(root)
    add_product_window.title("Yeni Ürün Ekle")
    add_product_window.geometry("300x300")

    tk.Label(add_product_window, text="Ürün Adı:").pack(pady=5)
    entry_name = ttk.Entry(add_product_window)
    entry_name.pack(pady=5)

    tk.Label(add_product_window, text="Açıklama:").pack(pady=5)
    entry_desc = ttk.Entry(add_product_window)
    entry_desc.pack(pady=5)

    tk.Label(add_product_window, text="Fiyat:").pack(pady=5)
    entry_price = ttk.Entry(add_product_window)
    entry_price.pack(pady=5)

    tk.Label(add_product_window, text="Stok Miktarı:").pack(pady=5)
    entry_qty = ttk.Entry(add_product_window)
    entry_qty.pack(pady=5)

    tk.Button(add_product_window, text="Ürün Ekle", command=add_product, bg=SUCCESS_COLOR, fg="white").pack(pady=10)


def open_edit_product_form():
    """Ürün düzenleme veya silme formunu açar."""
    if not products:
        messagebox.showinfo("Bilgi", "Düzenlenecek ürün bulunamadı.")
        return

    def update_product():
        selected = product_combo.get()
        if not selected:
            return

        selected_id = int(selected.split("-")[0].strip())
        for product in products:
            if product["id"] == selected_id:
                try:
                    product["name"] = entry_name.get()
                    product["desc"] = entry_desc.get()
                    product["price"] = float(entry_price.get())
                    product["qty"] = int(entry_qty.get())
                except ValueError:
                    messagebox.showerror("Hata", "Fiyat ve stok geçerli olmalıdır.")
                    return

                messagebox.showinfo("Başarılı", "Ürün başarıyla güncellendi.")
                update_stock_report()
                edit_window.destroy()
                break

    def delete_product():
        selected = product_combo.get()
        if not selected:
            return

        selected_id = int(selected.split("-")[0].strip())
        answer = messagebox.askyesno("Onay", f"{selected} adlı ürünü silmek istediğinize emin misiniz?")
        if answer:
            global products
            products = [p for p in products if p["id"] != selected_id]
            messagebox.showinfo("Silindi", "Ürün başarıyla silindi.")
            update_stock_report()
            edit_window.destroy()

    edit_window = tk.Toplevel(root)
    edit_window.title("Ürün Düzenle")
    edit_window.geometry("350x450")

    tk.Label(edit_window, text="Ürün Seç:").pack(pady=5)
    product_combo = ttk.Combobox(edit_window, state="readonly", width=30)
    product_combo['values'] = [f"{p['id']} - {p['name']}" for p in products]
    product_combo.pack(pady=5)

    tk.Label(edit_window, text="Yeni Ad:").pack(pady=5)
    entry_name = ttk.Entry(edit_window)
    entry_name.pack(pady=5)

    tk.Label(edit_window, text="Yeni Açıklama:").pack(pady=5)
    entry_desc = ttk.Entry(edit_window)
    entry_desc.pack(pady=5)

    tk.Label(edit_window, text="Yeni Fiyat:").pack(pady=5)
    entry_price = ttk.Entry(edit_window)
    entry_price.pack(pady=5)

    tk.Label(edit_window, text="Yeni Stok Miktarı:").pack(pady=5)
    entry_qty = ttk.Entry(edit_window)
    entry_qty.pack(pady=5)

    def fill_fields(event):
        selected = product_combo.get()
        if not selected:
            return
        selected_id = int(selected.split("-")[0].strip())
        for product in products:
            if product["id"] == selected_id:
                entry_name.delete(0, tk.END)
                entry_name.insert(0, product["name"])
                entry_desc.delete(0, tk.END)
                entry_desc.insert(0, product["desc"])
                entry_price.delete(0, tk.END)
                entry_price.insert(0, str(product["price"]))
                entry_qty.delete(0, tk.END)
                entry_qty.insert(0, str(product["qty"]))
                break

    product_combo.bind("<<ComboboxSelected>>", fill_fields)

    tk.Button(edit_window, text="Güncelle", command=update_product, bg=SECONDARY_COLOR, fg="white").pack(pady=10)
    tk.Button(edit_window, text="Ürünü Sil", command=delete_product, bg=DANGER_COLOR, fg="white").pack(pady=5)

# --- ARAYÜZ OLUŞUMU ---
root = tk.Tk()
root.title("Modern POS Sistemi")
root.geometry("1100x750")
root.config(bg=BG_COLOR)

# Başlık
header_frame = tk.Frame(root, bg=PRIMARY_COLOR, pady=10)
header_frame.pack(fill="x")
tk.Label(header_frame, text="TELEFON AKSESUAR SATIŞ SİSTEMİ",
         font=("Helvetica", 16, "bold"), bg=PRIMARY_COLOR, fg="white").pack()

# Ana içerik
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Sol Panel
left_panel = tk.Frame(main_frame, bg=BG_COLOR)
left_panel.pack(side="left", fill="both", expand=True)



# Arama
search_frame = tk.Frame(left_panel, bg=BG_COLOR)
search_frame.pack(fill="x", pady=(0, 10))
entry_search = create_entry(search_frame, "Ürün ara...", 30)
entry_search.pack(side="left", padx=(0, 10))
entry_search.bind("<KeyRelease>", search_products)

# Ürün Tablosu
product_frame = tk.LabelFrame(left_panel, text="Ürün Listesi", font=FONT_BOLD, bg=BG_COLOR)
product_frame.pack(fill="both", expand=True)
tree, tree_frame = create_treeview(product_frame, ("ID", "Ürün Adı", "Açıklama", "Stok", "Fiyat"))
tree_frame.pack(fill="both", expand=True)

# Sağ Panel
right_panel = tk.Frame(main_frame, bg=BG_COLOR)
right_panel.pack(side="right", fill="y")

# Sepet Başlığı
cart_header = tk.Frame(right_panel, bg=PRIMARY_COLOR, pady=5)
cart_header.pack(fill="x")
tk.Label(cart_header, text="ALIŞVERİŞ SEPETİ", font=FONT_BOLD, bg=PRIMARY_COLOR, fg="white").pack()

# Sepet Tablosu
cart_tree, cart_tree_frame = create_treeview(right_panel, ("ID", "Ürün", "Adet", "Fiyat", "Toplam"))
cart_tree_frame.pack(fill="x", pady=(0, 10))

# Toplam
total_frame = tk.Frame(right_panel, bg=BG_COLOR)
total_frame.pack(fill="x")
tk.Label(total_frame, text="TOPLAM:", font=FONT_BOLD, bg=BG_COLOR).pack(side="left")
lbl_total = tk.Label(total_frame, text="0.00 TL", font=("Helvetica", 12, "bold"), fg=SUCCESS_COLOR, bg=BG_COLOR)
lbl_total.pack(side="right")


# Butonlar
button_frame = tk.Frame(right_panel, bg=BG_COLOR)
button_frame.pack(fill="x", pady=10)
create_button(button_frame, "Sepetten Çıkar", remove_from_cart, DANGER_COLOR).pack(fill="x", pady=5)
create_button(button_frame, "Satın Al", purchase, SUCCESS_COLOR).pack(fill="x", pady=5)

# Alt Menü
bottom_menu = tk.Frame(root, bg=PRIMARY_COLOR, pady=10)
bottom_menu.pack(fill="x", side="bottom")
create_button(bottom_menu, "Yönetici Paneli", open_password_panel, "white", PRIMARY_COLOR).pack(side="left", padx=5)


# Ürünleri Yükle
load_products()  # Ürünleri yükle

# Sepete ürün eklemek için çift tıklama event handler'ı ekleniyor
tree.bind("<Double-1>", add_to_cart)

root.mainloop()
